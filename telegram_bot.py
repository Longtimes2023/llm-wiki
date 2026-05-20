"""
Telegram bot for llm-wiki ingest.

Workflow (per docs/requirements/2026-05-07-telegram-bot-llm-wiki.md):
  1. User sends URL → bot writes file to ai-wiki/raw/articles/
  2. Existing raw-watcher.sh (systemd user unit) picks it up
  3. Bot tails scripts/watcher.log for "INGEST VERIFIED OK" + "deployed: <url>"
  4. Bot replies with Quartz public URL

Run modes:
  python telegram_bot.py               → full bot (long-poll)
  python telegram_bot.py --getchatid   → helper: print chat_id of next message and exit
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import re
import signal
import subprocess
import time
from collections import deque
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiofiles
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv(override=True)

# Allow `from providers.loader import ...` regardless of cwd
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers.loader import (
    list_providers, get_active, set_active,
    get_active_chat, set_active_chat,
)

# ---------- Config ----------
PROJECT_DIR = Path(__file__).resolve().parent
WIKI_DIR = PROJECT_DIR / "ai-wiki"
RAW_ARTICLES_DIR = WIKI_DIR / "raw" / "articles"
SOURCES_DIR = WIKI_DIR / "wiki" / "sources"
WATCHER_LOG = PROJECT_DIR / "scripts" / "watcher.log"
STATE_FILE = PROJECT_DIR / "scripts" / "telegram_bot.state"
METRICS_FILE = PROJECT_DIR / "scripts" / "ingest_metrics.jsonl"
FAILURES_FILE = PROJECT_DIR / "scripts" / "ingest_failures.jsonl"
WATCHER_FAILED_FILE = PROJECT_DIR / "scripts" / "watcher.failed"
# Outside the inotify watch tree (raw/) so moves here don't re-trigger ingest.
CANCELLED_DIR = WIKI_DIR / "cancelled"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_ALLOWED_CHAT_ID = os.getenv("TELEGRAM_ALLOWED_CHAT_ID", "").strip()
QUARTZ_PUBLIC_BASE_URL = os.getenv(
    "QUARTZ_PUBLIC_BASE_URL", "https://llm-wiki-ai.pages.dev"
).rstrip("/")

# Q&A backend (wiki_writer_api.py)
WIKI_API_BASE = os.getenv("WIKI_API_BASE", "http://localhost:8000").rstrip("/")
WIKI_API_SYNC_URL = f"{WIKI_API_BASE}/api/v1/wiki/generate/sync"
WIKI_API_TIMEOUT_S = int(os.getenv("WIKI_API_TIMEOUT_S", "300"))
TELEGRAM_MAX_MSG = 4000  # 4096 hard cap minus margin for Telegram entity overhead

PENDING_TIMEOUT_SECONDS = 1800
SWEEP_INTERVAL_SECONDS = 30
LOG_POLL_INTERVAL_SECONDS = 1.0
SOURCES_POLL_INTERVAL_SECONDS = 15

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
RE_SOURCE_URL = re.compile(r"^source_url:\s*(\S+)\s*$", re.MULTILINE)
RE_SOURCE_PATH = re.compile(r"^source_path:\s*raw/articles/(\S+\.md)\s*$", re.MULTILINE)
RE_PROVIDER_TOKEN = re.compile(r"@([a-z0-9_-]+)\b", re.IGNORECASE)

# Markers emitted by raw-watcher.sh + sync-and-rebuild.sh
RE_DETECTED = re.compile(r"detected new file:\s*(\S+\.md)")
RE_INGEST_OK = re.compile(r"INGEST VERIFIED OK")
RE_INGEST_FAIL = re.compile(r"GIVING UP after \d+ attempts:\s*(\S+\.md)")
RE_DEPLOYED = re.compile(r"deployed:\s*(https?://\S+)")

logging.basicConfig(
    format="%(asctime)s [telegram_bot] %(levelname)s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("telegram_bot")
# Quiet down noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


# ---------- Pending tracker ----------
@dataclass
class Pending:
    raw_file: str
    chat_id: int
    msg_id: int
    ack_msg_id: Optional[int]
    created_ts: float
    status: str = "queued"
    last_ingest_event: Optional[str] = None
    last_deploy_url: Optional[str] = None
    sources_snapshot: list[str] = field(default_factory=list)
    new_source_file: Optional[str] = None  # detected after ingest_ok via diff


class PendingTracker:
    def __init__(self) -> None:
        self._items: dict[str, Pending] = {}
        self._lock = asyncio.Lock()

    async def add(self, p: Pending) -> None:
        async with self._lock:
            self._items[p.raw_file] = p
        await self._persist(p)

    async def get(self, raw_file: str) -> Optional[Pending]:
        async with self._lock:
            return self._items.get(raw_file)

    async def update(self, raw_file: str, **fields) -> Optional[Pending]:
        async with self._lock:
            p = self._items.get(raw_file)
            if not p:
                return None
            for k, v in fields.items():
                setattr(p, k, v)
            await self._persist(p)
            return p

    async def remove(self, raw_file: str) -> Optional[Pending]:
        async with self._lock:
            return self._items.pop(raw_file, None)

    async def all(self) -> list[Pending]:
        async with self._lock:
            return list(self._items.values())

    async def _persist(self, p: Pending) -> None:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(asdict(p), ensure_ascii=False)
        async with aiofiles.open(STATE_FILE, "a") as f:
            await f.write(line + "\n")


# ---------- URL + raw file ----------
def extract_url(text: str) -> Optional[str]:
    if not text:
        return None
    m = URL_RE.search(text)
    return m.group(0) if m else None


def extract_url_and_provider(text: str) -> tuple[Optional[str], Optional[str]]:
    """Returns (url, provider_override). Provider is the @<name> token if present.

    Examples:
      "https://example.com"            -> ("https://example.com", None)
      "https://example.com @deepseek"  -> ("https://example.com", "deepseek")
      "@anthropic https://example.com" -> ("https://example.com", "anthropic")
    """
    if not text:
        return None, None
    url = extract_url(text)
    pm = RE_PROVIDER_TOKEN.search(text)
    return url, (pm.group(1).lower() if pm else None)


def _norm_url(url: str) -> str:
    return url.rstrip("/").lower()


def find_existing_raw_for_url(url: str) -> Optional[Path]:
    """Scan ai-wiki/raw/articles/ for a raw file with matching source_url frontmatter."""
    if not RAW_ARTICLES_DIR.exists():
        return None
    target = _norm_url(url)
    for raw in RAW_ARTICLES_DIR.glob("*.md"):
        try:
            head = raw.read_text(encoding="utf-8", errors="ignore")[:500]
        except OSError:
            continue
        m = RE_SOURCE_URL.search(head)
        if m and _norm_url(m.group(1)) == target:
            return raw
    return None


def find_source_page_for_raw(raw_filename: str) -> Optional[str]:
    """Find wiki/sources/*.md whose frontmatter source_path: points to this raw."""
    if not SOURCES_DIR.exists():
        return None
    for src in SOURCES_DIR.glob("*.md"):
        try:
            head = src.read_text(encoding="utf-8", errors="ignore")[:1500]
        except OSError:
            continue
        m = RE_SOURCE_PATH.search(head)
        if m and m.group(1) == raw_filename:
            return src.name
    return None


def find_metrics_for_raw(raw_filename: str) -> Optional[dict]:
    """Read the latest metrics line for this raw_file from ingest_metrics.jsonl."""
    if not METRICS_FILE.exists():
        return None
    try:
        last = None
        with METRICS_FILE.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("raw_file") == raw_filename:
                    last = obj
        return last
    except OSError:
        return None


def find_fetch_fail_for_raw(raw_filename: str) -> Optional[dict]:
    """Latest [FETCH_FAIL] entry for this raw_file from ingest_failures.jsonl.
    Returns dict with {source_id, url, status, reason, raw_file} or None."""
    if not FAILURES_FILE.exists():
        return None
    try:
        last = None
        with FAILURES_FILE.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("raw_file") == raw_filename:
                    last = obj
        return last
    except OSError:
        return None


def format_metrics_line(metrics: dict) -> str:
    """One-liner for Telegram deploy reply: '⏱ 14.5min · 🔢 12,345/6,789 · 💰 $0.052 (model)'."""
    dur_s = metrics.get("duration_s") or 0
    mins = dur_s / 60
    in_tok = metrics.get("input_tokens") or 0
    out_tok = metrics.get("output_tokens") or 0
    cache = metrics.get("cache_read_tokens") or 0
    cost = metrics.get("cost_usd")
    model = metrics.get("model") or metrics.get("provider") or "?"
    parts = [f"⏱ {mins:.1f}min", f"🔢 {in_tok:,} in / {out_tok:,} out"]
    if cache:
        parts[-1] += f" ({cache:,} cached)"
    if cost is not None:
        parts.append(f"💰 ${cost:.4f}")
    parts.append(f"<code>{model}</code>")
    return " · ".join(parts)


def write_raw_file(
    url: str,
    chat_id: int,
    msg_id: int,
    provider: Optional[str] = None,
) -> Path:
    RAW_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    short = hashlib.sha1(f"{url}:{msg_id}:{time.time()}".encode()).hexdigest()[:6]
    path = RAW_ARTICLES_DIR / f"{ts}-tg-{short}.md"
    provider_line = f"provider: {provider}\n" if provider else ""
    body = (
        f"---\n"
        f"source_url: {url}\n"
        f"captured_at: {datetime.now().isoformat(timespec='seconds')}\n"
        f"captured_via: telegram_bot\n"
        f"telegram_chat_id: {chat_id}\n"
        f"telegram_msg_id: {msg_id}\n"
        f"{provider_line}"
        f"---\n\n"
        f"# Source URL\n\n"
        f"{url}\n\n"
        f"(Telegram bot ingest — please fetch this URL and process it as a normal article source.)\n"
    )
    path.write_text(body, encoding="utf-8")
    return path


def snapshot_sources() -> list[str]:
    """Return sorted list of .md filenames currently in wiki/sources/."""
    if not SOURCES_DIR.exists():
        return []
    return sorted(p.name for p in SOURCES_DIR.glob("*.md"))


def diff_new_sources(before: list[str]) -> list[str]:
    """Files now in wiki/sources/ but not in `before` snapshot."""
    before_set = set(before)
    return [name for name in snapshot_sources() if name not in before_set]


def quartz_url_for_source(source_filename: str) -> str:
    """Build Quartz URL for a wiki/sources/<filename>.md page."""
    if not source_filename:
        return f"{QUARTZ_PUBLIC_BASE_URL}/"
    stem = Path(source_filename).stem
    return f"{QUARTZ_PUBLIC_BASE_URL}/wiki/sources/{stem}"


# ---------- Process / state helpers (for /retry, /cancel) ----------
def _find_pid_for_raw(raw_filename: str) -> Optional[int]:
    """Return PID of running 7_wiki_writer.py for this raw, or None.

    Matches `--raw-file ...<raw_filename>` in the command line via pgrep.
    """
    try:
        r = subprocess.run(
            ["pgrep", "-f", f"7_wiki_writer.py.*{re.escape(raw_filename)}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return int(r.stdout.strip().splitlines()[0])
    except ValueError:
        return None


def _kill_pid(pid: int, grace_s: float = 5.0) -> bool:
    """SIGTERM, wait up to grace_s, then SIGKILL. Returns True if process gone."""
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return True
    except PermissionError:
        log.warning("no permission to signal pid=%s", pid)
        return False

    deadline = time.time() + grace_s
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.2)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return True


def _resolve_raw_target(
    arg: Optional[str],
    tracker_items: list[Pending],
    recent_timeouts: Optional[deque] = None,
) -> Optional[Path]:
    """Resolve `/retry` or `/cancel` argument to a raw file Path.

    - With arg: substring match in raw/articles/*.md (trailing punctuation tolerated).
    - No arg, recent_timeouts non-empty: newest entry there (file the sweeper just
      complained about — what users usually mean when they type "/retry" right
      after a timeout warning).
    - No arg, tracker non-empty: newest entry by created_ts.
    - No arg, watcher.failed non-empty: last line.
    """
    if arg:
        # Tolerate stray punctuation users sometimes paste (e.g. "filename.md.")
        arg_s = arg.strip().lstrip("/").rstrip(".,;:!?\"'`")
        if not RAW_ARTICLES_DIR.exists():
            return None
        matches = [p for p in RAW_ARTICLES_DIR.glob("*.md") if arg_s in p.name]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            # Prefer exact filename match if present
            exact = [p for p in matches if p.name == arg_s]
            if len(exact) == 1:
                return exact[0]
            return None
        return None

    if recent_timeouts:
        # Most recent timeout victim wins
        for raw_name in reversed(recent_timeouts):
            path = RAW_ARTICLES_DIR / raw_name
            if path.exists():
                return path

    if tracker_items:
        newest = max(tracker_items, key=lambda p: p.created_ts)
        path = RAW_ARTICLES_DIR / newest.raw_file
        if path.exists():
            return path

    if WATCHER_FAILED_FILE.exists():
        try:
            lines = [
                ln.strip() for ln in WATCHER_FAILED_FILE.read_text().splitlines() if ln.strip()
            ]
        except OSError:
            return None
        if lines:
            last = Path(lines[-1])
            if last.exists():
                return last
    return None


def _remove_from_watcher_failed(raw_filename: str) -> bool:
    """Remove any line in watcher.failed whose path basename matches raw_filename."""
    if not WATCHER_FAILED_FILE.exists():
        return False
    try:
        lines = WATCHER_FAILED_FILE.read_text().splitlines()
    except OSError:
        return False
    kept = [ln for ln in lines if Path(ln.strip()).name != raw_filename]
    if len(kept) == len(lines):
        return False
    WATCHER_FAILED_FILE.write_text("\n".join(kept) + ("\n" if kept else ""))
    return True


def _atomic_retrigger(path: Path) -> None:
    """Atomic rename to fire an inotify moved_to event on raw-watcher."""
    tmp = path.with_suffix(path.suffix + ".retry.tmp")
    path.rename(tmp)
    tmp.rename(path)


# ---------- Log tailer ----------
async def tail_watcher_log(emit) -> None:
    """Tail scripts/watcher.log forever; call emit(event_type, payload) per match.

    event_type ∈ {"ingest_ok", "ingest_fail", "deployed"}
    payload: dict with at least one of: filename, url
    """
    if not WATCHER_LOG.exists():
        log.warning("watcher.log not found yet at %s — will wait", WATCHER_LOG)

    last_inode: Optional[int] = None
    fp = None
    last_seen_filename: Optional[str] = None  # bind ingest_ok to most recent "detected" line

    while True:
        try:
            if not WATCHER_LOG.exists():
                await asyncio.sleep(LOG_POLL_INTERVAL_SECONDS)
                continue

            st = WATCHER_LOG.stat()
            if fp is None or st.st_ino != last_inode:
                if fp is not None:
                    fp.close()
                fp = WATCHER_LOG.open("r", encoding="utf-8", errors="replace")
                fp.seek(0, os.SEEK_END)
                last_inode = st.st_ino
                log.info("LogTailer attached to %s (inode=%s)", WATCHER_LOG, last_inode)

            line = fp.readline()
            if not line:
                await asyncio.sleep(LOG_POLL_INTERVAL_SECONDS)
                continue

            line = line.rstrip("\n")

            m = RE_DETECTED.search(line)
            if m:
                last_seen_filename = Path(m.group(1)).name
                continue

            if RE_INGEST_OK.search(line) and last_seen_filename:
                await emit("ingest_ok", {"filename": last_seen_filename})
                continue

            m = RE_INGEST_FAIL.search(line)
            if m:
                await emit("ingest_fail", {"filename": Path(m.group(1)).name})
                continue

            m = RE_DEPLOYED.search(line)
            if m and last_seen_filename:
                await emit(
                    "deployed",
                    {"filename": last_seen_filename, "url": m.group(1)},
                )
                continue
        except Exception as e:
            log.exception("LogTailer error, sleeping then retrying: %s", e)
            await asyncio.sleep(5)


# ---------- Q&A intent + backend ----------
# Phrases that flip an URL-bearing message from Q&A (default) to ingest.
# Naked URL (no surrounding prose) still defaults to ingest for backwards compat.
INGEST_KEYWORDS = (
    # vi
    "thêm vào wiki", "cập nhật wiki", "lưu vào wiki", "lưu link", "lưu bài",
    "vào wiki", "add wiki", "ingest",
    # zh
    "消化", "存进wiki", "存进 wiki", "保存到wiki", "保存到 wiki",
    "更新wiki", "更新 wiki", "加入wiki", "加入 wiki", "记一下", "收藏到wiki",
    # en
    "save to wiki", "save this", "add to wiki", "add this", "ingest this",
    "remember this", "store this",
)


def is_ingest_request(text: str, url: Optional[str]) -> bool:
    """True if message asks to ingest; False → Q&A path."""
    if not url:
        return False
    stripped = text.strip()
    # Naked URL (optionally with @provider tag) → ingest (legacy behavior)
    bare = URL_RE.sub("", stripped).strip()
    bare = RE_PROVIDER_TOKEN.sub("", bare).strip()
    if not bare:
        return True
    lower = stripped.lower()
    return any(kw in lower for kw in INGEST_KEYWORDS)


QUERY_PROMPT_PREFIX = (
    "你是知识库问答助手。当前目录是 ai-wiki/。知识库在 wiki/ 下：\n"
    "- wiki/entities/  实体页（人物、产品、概念）\n"
    "- wiki/topics/    主题页（领域综合）\n"
    "- wiki/sources/   素材摘要\n"
    "- wiki/synthesis/ 跨素材综合分析\n\n"
    "请使用 Glob/Grep/Read 工具查找相关页面。\n\n"
    "**语言规则（重要）**：先判断用户问题的主要语言，然后整条回答只用这一种语言。\n"
    "- 用户用越南语问 → 整条回答只用越南语（包括标题、表格、列表项）。专有名词/产品名可保留原文。\n"
    "- 用户用中文问 → 整条回答只用中文。\n"
    "- 用户用英语问 → 整条回答只用英语。\n"
    "- 问题混合多种语言时，按字数最多的那种语言回答，不要混合输出。\n"
    "- 知识库内容是中文也要翻译成用户的语言；不要原样照搬中文短语夹进越南语/英语回答里。\n\n"
    "如果知识库里找不到相关内容，直接用用户的语言说\"知识库里还没有这个主题\"（越南语：\"Wiki chưa có chủ đề này\"；英语：\"Wiki doesn't have this topic yet\"）。"
    "不要修改任何文件，不要执行 ingest。\n\n"
    "用户问题: "
)


async def ask_wiki(question: str) -> str:
    """Q&A via wiki_writer_api (read-only agent)."""
    payload = {
        "request": QUERY_PROMPT_PREFIX + question,
        "read_only": True,
        "stream": False,
    }
    chat_provider = get_active_chat()
    if chat_provider:
        payload["provider"] = chat_provider
    try:
        async with httpx.AsyncClient(timeout=WIKI_API_TIMEOUT_S) as client:
            r = await client.post(WIKI_API_SYNC_URL, json=payload)
        r.raise_for_status()
        data = r.json()
    except httpx.ConnectError:
        return (
            "⚠️ wiki_writer_api không phản hồi. Kiểm tra:\n"
            "<code>systemctl --user status llm-wiki-api</code>"
        )
    except httpx.HTTPStatusError as e:
        return f"⚠️ API trả lỗi {e.response.status_code}: {e.response.text[:300]}"
    except httpx.TimeoutException:
        return f"⚠️ Q&A timeout sau {WIKI_API_TIMEOUT_S}s — câu hỏi nặng quá, thử rút gọn."
    except Exception as e:
        log.exception("ask_wiki error")
        return f"⚠️ Lỗi gọi API: {e}"

    if not data.get("success"):
        return f"⚠️ Agent trả về lỗi:\n<code>{json.dumps(data, ensure_ascii=False)[:500]}</code>"
    content = (data.get("content") or "").strip()
    return content or "⚠️ Agent không trả nội dung nào (có thể model rỗng response)."


async def _send_long(msg, text: str) -> None:
    """Split > Telegram limit and reply each chunk. Markdown→plain fallback per chunk."""
    if not text:
        await msg.reply_text("(empty)")
        return
    chunks = [text[i:i + TELEGRAM_MAX_MSG] for i in range(0, len(text), TELEGRAM_MAX_MSG)]
    for chunk in chunks:
        try:
            await msg.reply_text(chunk, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception:
            # Unmatched markdown char (_, *, [) — fall back to plain text
            try:
                await msg.reply_text(chunk, disable_web_page_preview=True)
            except Exception as e:
                log.exception("send_long final fallback failed: %s", e)


async def _typing_loop(bot, chat_id: int) -> None:
    """Keep the Telegram typing indicator alive while ask_wiki is in flight."""
    try:
        while True:
            try:
                await bot.send_chat_action(chat_id=chat_id, action="typing")
            except Exception:
                pass
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        return


# ---------- Bot handlers ----------
def _is_allowed(chat_id: int) -> bool:
    if not TELEGRAM_ALLOWED_CHAT_ID:
        return False
    try:
        return int(TELEGRAM_ALLOWED_CHAT_ID) == int(chat_id)
    except ValueError:
        return False


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg or not msg.text:
        return
    chat_id = msg.chat_id

    if not _is_allowed(chat_id):
        log.warning("ignoring message from non-allowlisted chat_id=%s", chat_id)
        return

    url, provider_override = extract_url_and_provider(msg.text)

    # Branch: ingest intent vs Q&A.
    # Naked URL (or URL + ingest keyword) → ingest (legacy). Anything else → Q&A.
    if not is_ingest_request(msg.text, url):
        question = msg.text.strip()
        if not question:
            return
        log.info("Q&A request from chat=%s: %r", chat_id, question[:120])
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        except Exception:
            pass
        ack = await msg.reply_text("🤔 Đang tra cứu wiki...")
        typing_task = asyncio.create_task(_typing_loop(context.bot, chat_id))
        try:
            answer = await ask_wiki(question)
        finally:
            typing_task.cancel()
        try:
            await ack.delete()
        except Exception:
            pass
        await _send_long(msg, answer)
        return

    # Ingest path (existing flow).
    # Validate provider override (if any) against profiles BEFORE writing raw
    if provider_override:
        if provider_override not in list_providers():
            available = ", ".join(list_providers()) or "(no profiles)"
            await msg.reply_text(
                f"❌ Provider <b>{provider_override}</b> không có. Available: {available}",
                parse_mode="HTML",
            )
            return

    # Pre-flight dedup — skip when @provider override is present (intentional re-test)
    if not provider_override:
        existing = find_existing_raw_for_url(url)
        if existing:
            src_name = find_source_page_for_raw(existing.name)
            if src_name:
                src_url = quartz_url_for_source(src_name)
                log.info("dedup: url already ingested via raw=%s, source=%s", existing.name, src_name)
                await msg.reply_text(
                    f"♻️ URL này đã ingest trước đó.\n"
                    f"Wiki: {src_url}\n"
                    f"<i>Raw: {existing.name}</i>\n\n"
                    f"Để A/B test với provider khác, gửi: <code>{url} @&lt;provider&gt;</code>",
                    parse_mode="HTML",
                )
            else:
                # Raw exists but no source page yet → in-flight, failed, or hung
                log.info(
                    "dedup: raw exists but no source page yet for url=%s raw=%s",
                    url, existing.name,
                )
                await msg.reply_text(
                    f"⏳ URL này đang được xử lý (chưa có source page).\n"
                    f"<i>Raw: {existing.name}</i>\n\n"
                    f"• Khởi động lại: <code>/retry {existing.name}</code>\n"
                    f"• Hủy hẳn: <code>/cancel {existing.name}</code>\n"
                    f"• A/B với provider khác: <code>{url} @&lt;provider&gt;</code>",
                    parse_mode="HTML",
                )
            return

    raw_path = write_raw_file(url, chat_id, msg.message_id, provider=provider_override)
    log.info(
        "wrote raw file %s for url=%s provider=%s",
        raw_path, url, provider_override or "(default)",
    )

    sources_before = snapshot_sources()
    log.info("snapshot sources before ingest: %d files", len(sources_before))

    ack_lines = [f"🔄 Đã nhận URL — đang đẩy vào pipeline:", url]
    if provider_override:
        ack_lines.append(f"\n<b>Provider override:</b> {provider_override} (one-off, dedup bypass)")
    ack_lines.append(f"\nFile: <code>{raw_path.name}</code>")
    ack_lines.append("Sẽ reply link wiki khi pipeline xong (thường 1–5 phút).")
    ack = await msg.reply_text("\n".join(ack_lines), parse_mode="HTML")

    tracker: PendingTracker = context.application.bot_data["tracker"]
    await tracker.add(
        Pending(
            raw_file=raw_path.name,
            chat_id=chat_id,
            msg_id=msg.message_id,
            ack_msg_id=ack.message_id if ack else None,
            created_ts=time.time(),
            status="queued",
            sources_snapshot=sources_before,
        )
    )


async def on_provider_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """`/provider` shows active + list. `/provider <name>` switches sticky default."""
    msg = update.effective_message
    if not msg:
        return
    chat_id = msg.chat_id
    if not _is_allowed(chat_id):
        log.warning("ignoring /provider from non-allowlisted chat_id=%s", chat_id)
        return

    args = context.args or []
    available = list_providers()
    if not args:
        active = get_active() or "(none — using .env default)"
        chat_active = get_active_chat() or "(none — same as ingest provider)"
        avail_str = ", ".join(available) if available else "(no profiles in providers/)"
        await msg.reply_text(
            f"<b>Ingest provider:</b> {active}\n"
            f"<b>Chat provider:</b> {chat_active}\n"
            f"<b>Available:</b> {avail_str}\n\n"
            f"Switch ingest: <code>/provider &lt;name&gt;</code>\n"
            f"Switch chat:   <code>/chatprovider &lt;name&gt;</code>\n"
            f"Per-URL override: send <code>URL @&lt;name&gt;</code> (one-off, bypasses dedup)",
            parse_mode="HTML",
        )
        return

    name = args[0].strip().lower()
    try:
        prev = get_active()
        set_active(name)
        log.info("provider switched: %s -> %s by chat=%s", prev, name, chat_id)
        await msg.reply_text(
            f"✅ Active provider: <b>{name}</b>\n"
            f"<i>(was: {prev or 'default'})</i>\n\n"
            f"Ingest đang chạy KHÔNG bị ảnh hưởng — vẫn dùng provider cũ tới khi xong.\n"
            f"URL tiếp theo sẽ dùng <b>{name}</b>.",
            parse_mode="HTML",
        )
    except ValueError as e:
        await msg.reply_text(f"❌ {e}")


async def on_chatprovider_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """`/chatprovider` shows active chat provider + list.
    `/chatprovider <name>` switches sticky chat (Q&A) provider.

    Independent from `/provider` (ingest). Empty/unset → Q&A falls back to
    ingest provider, preserving backward compat.
    """
    msg = update.effective_message
    if not msg:
        return
    chat_id = msg.chat_id
    if not _is_allowed(chat_id):
        log.warning("ignoring /chatprovider from non-allowlisted chat_id=%s", chat_id)
        return

    args = context.args or []
    available = list_providers()
    if not args:
        active = get_active_chat() or "(none — falls back to ingest provider)"
        avail_str = ", ".join(available) if available else "(no profiles in providers/)"
        await msg.reply_text(
            f"<b>Chat (Q&A) provider:</b> {active}\n"
            f"<b>Available:</b> {avail_str}\n\n"
            f"Switch: <code>/chatprovider &lt;name&gt;</code>",
            parse_mode="HTML",
        )
        return

    name = args[0].strip().lower()
    try:
        prev = get_active_chat()
        set_active_chat(name)
        log.info("chat provider switched: %s -> %s by chat=%s", prev, name, chat_id)
        await msg.reply_text(
            f"✅ Chat provider: <b>{name}</b>\n"
            f"<i>(was: {prev or 'fallback to ingest'})</i>\n\n"
            f"Câu hỏi tiếp theo sẽ chạy qua <b>{name}</b>.",
            parse_mode="HTML",
        )
    except ValueError as e:
        await msg.reply_text(f"❌ {e}")


async def on_retry_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """`/retry` re-triggers the newest pending/failed raw file.
    `/retry <substr>` re-triggers a specific file by filename substring.

    Kills any live 7_wiki_writer.py for that file (avoids two processes racing
    on the same raw + state files), removes any watcher.failed entry, then
    atomically renames the raw file so inotify fires moved_to.
    """
    msg = update.effective_message
    if not msg:
        return
    chat_id = msg.chat_id
    if not _is_allowed(chat_id):
        log.warning("ignoring /retry from non-allowlisted chat_id=%s", chat_id)
        return

    tracker: PendingTracker = context.application.bot_data["tracker"]
    recent_timeouts: deque = context.application.bot_data.get("recent_timeouts") or deque()
    arg = context.args[0] if context.args else None
    target = _resolve_raw_target(arg, await tracker.all(), recent_timeouts)
    if target is None:
        await msg.reply_text(
            "❌ Không tìm thấy raw file để retry.\n"
            "Cú pháp: <code>/retry &lt;phần-tên-file&gt;</code> "
            "(hoặc <code>/retry</code> để retry file mới nhất).",
            parse_mode="HTML",
        )
        return

    raw_name = target.name

    # Kill old process first to avoid races on watcher.state / metrics jsonl
    pid = _find_pid_for_raw(raw_name)
    killed = False
    if pid:
        killed = _kill_pid(pid)
        log.info("/retry killed pid=%s for %s (success=%s)", pid, raw_name, killed)

    # Clean state
    removed_from_failed = _remove_from_watcher_failed(raw_name)
    # Drop any in-memory pending so a fresh tracker entry can be added
    await tracker.remove(raw_name)
    # Forget the timeout victim if we just acted on it
    try:
        while raw_name in recent_timeouts:
            recent_timeouts.remove(raw_name)
    except ValueError:
        pass

    # Read source_url for the new Pending; refresh sources snapshot
    try:
        _atomic_retrigger(target)
    except OSError as e:
        log.exception("/retry atomic rename failed for %s: %s", target, e)
        await msg.reply_text(f"❌ Rename thất bại: {e}")
        return

    sources_before = snapshot_sources()
    ack = await msg.reply_text(
        f"🔁 Đã retry <code>{raw_name}</code>.\n"
        + (f"Killed PID <code>{pid}</code>.\n" if pid else "")
        + (f"Removed from <code>watcher.failed</code>.\n" if removed_from_failed else "")
        + "Sẽ báo khi pipeline xong (thường 1–5 phút).",
        parse_mode="HTML",
    )

    await tracker.add(
        Pending(
            raw_file=raw_name,
            chat_id=chat_id,
            msg_id=msg.message_id,
            ack_msg_id=ack.message_id if ack else None,
            created_ts=time.time(),
            status="queued",
            sources_snapshot=sources_before,
        )
    )


async def on_cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """`/cancel [<substr>]` kills the in-flight ingest and moves the raw to
    `raw/articles/cancelled/` so the watcher won't pick it up again.
    """
    msg = update.effective_message
    if not msg:
        return
    chat_id = msg.chat_id
    if not _is_allowed(chat_id):
        log.warning("ignoring /cancel from non-allowlisted chat_id=%s", chat_id)
        return

    tracker: PendingTracker = context.application.bot_data["tracker"]
    recent_timeouts: deque = context.application.bot_data.get("recent_timeouts") or deque()
    arg = context.args[0] if context.args else None
    target = _resolve_raw_target(arg, await tracker.all(), recent_timeouts)
    if target is None:
        await msg.reply_text(
            "❌ Không tìm thấy raw file để cancel.\n"
            "Cú pháp: <code>/cancel &lt;phần-tên-file&gt;</code>",
            parse_mode="HTML",
        )
        return

    raw_name = target.name
    pid = _find_pid_for_raw(raw_name)
    killed = False
    if pid:
        killed = _kill_pid(pid)
        log.info("/cancel killed pid=%s for %s (success=%s)", pid, raw_name, killed)

    _remove_from_watcher_failed(raw_name)
    await tracker.remove(raw_name)
    try:
        while raw_name in recent_timeouts:
            recent_timeouts.remove(raw_name)
    except ValueError:
        pass

    CANCELLED_DIR.mkdir(parents=True, exist_ok=True)
    dest = CANCELLED_DIR / raw_name
    try:
        target.rename(dest)
    except OSError as e:
        log.exception("/cancel move failed for %s: %s", target, e)
        await msg.reply_text(f"❌ Move thất bại: {e}")
        return

    await msg.reply_text(
        f"🛑 Đã hủy <code>{raw_name}</code>.\n"
        + (f"Killed PID <code>{pid}</code>.\n" if pid else "(không có process đang chạy)\n")
        + f"Raw moved → <code>{dest.relative_to(PROJECT_DIR)}</code>.",
        parse_mode="HTML",
    )


# ---------- Bridge: log events → telegram replies ----------
async def make_emitter(application: Application):
    bot = application.bot
    tracker: PendingTracker = application.bot_data["tracker"]

    async def emit(event_type: str, payload: dict) -> None:
        filename = payload.get("filename")
        if not filename:
            return
        p = await tracker.get(filename)
        if not p:
            return  # not ours, ignore

        if event_type == "ingest_ok":
            new_sources = diff_new_sources(p.sources_snapshot)
            new_src = new_sources[0] if new_sources else None
            await tracker.update(
                filename,
                status="ingested",
                last_ingest_event="ok",
                new_source_file=new_src,
            )
            log.info(
                "ingest_ok matched pending %s; new source=%s (total new: %d)",
                filename, new_src, len(new_sources),
            )
        elif event_type == "ingest_fail":
            # Trust the filesystem poller over watcher.log's pessimism. If we already
            # detected the new source file via polling, ignore watcher's GIVING UP —
            # claude may have crashed mid-write but the file still landed.
            if p.status != "queued":
                log.info(
                    "ignoring ingest_fail for %s (status=%s, poller already saw success)",
                    filename, p.status,
                )
                return
            await tracker.update(filename, status="failed", last_ingest_event="fail")
            # Surface structured fetch-fail reason if the skill emitted one; otherwise
            # fall back to the generic "see watcher.log" message.
            fail_info = find_fetch_fail_for_raw(filename)
            if fail_info:
                reason = fail_info.get("reason") or fail_info.get("status") or "unknown"
                url = fail_info.get("url") or ""
                status_label = fail_info.get("status") or ""
                url_line = f"\nURL: <code>{url}</code>" if url else ""
                text = (
                    f"❌ Lấy nội dung thất bại ({status_label}) cho file "
                    f"<code>{filename}</code>:\n{reason}{url_line}"
                )
            else:
                text = (
                    f"❌ Pipeline thất bại sau nhiều lần thử cho file "
                    f"<code>{filename}</code>.\nXem <code>scripts/watcher.log</code>."
                )
            try:
                await bot.send_message(
                    chat_id=p.chat_id,
                    reply_to_message_id=p.msg_id,
                    text=text,
                    parse_mode="HTML",
                )
            finally:
                await tracker.remove(filename)
        elif event_type == "deployed":
            # Prefer the new source file detected after ingest_ok; fallback to root
            url = (
                quartz_url_for_source(p.new_source_file)
                if p.new_source_file
                else f"{QUARTZ_PUBLIC_BASE_URL}/"
            )
            await tracker.update(filename, status="deployed", last_deploy_url=url)
            try:
                src_label = (
                    f"\nSource: <code>{p.new_source_file}</code>"
                    if p.new_source_file else ""
                )
                # Append per-ingest metrics if available (time, tokens, cost)
                metrics = find_metrics_for_raw(filename)
                metrics_label = f"\n{format_metrics_line(metrics)}" if metrics else ""
                await bot.send_message(
                    chat_id=p.chat_id,
                    reply_to_message_id=p.msg_id,
                    text=(
                        f"✅ Đã ingest + deploy xong!\n"
                        f"Wiki: {url}{src_label}{metrics_label}\n"
                        f"(Site: {QUARTZ_PUBLIC_BASE_URL}/)"
                    ),
                    parse_mode="HTML",
                    disable_web_page_preview=False,
                )
            finally:
                await tracker.remove(filename)

    return emit


# ---------- Source filesystem poller (Option D) ----------
# Authoritative ingest detector. Watches wiki/sources/ for new files matching
# each pending's snapshot. More reliable than watcher.log markers — works even
# when Claude SDK crashes mid-write or watcher.sh's heuristic fails.
async def poll_sources(application: Application) -> None:
    tracker: PendingTracker = application.bot_data["tracker"]
    while True:
        try:
            for p in await tracker.all():
                if p.status != "queued":
                    continue
                new_sources = diff_new_sources(p.sources_snapshot)
                if new_sources:
                    new_src = new_sources[0]
                    await tracker.update(
                        p.raw_file,
                        status="ingested",
                        new_source_file=new_src,
                        last_ingest_event="ok_via_poll",
                    )
                    log.info(
                        "source poll detected ingest: %s → new_source=%s",
                        p.raw_file, new_src,
                    )
        except Exception as e:
            log.exception("poll_sources error: %s", e)
        await asyncio.sleep(SOURCES_POLL_INTERVAL_SECONDS)


# ---------- Timeout sweeper ----------
async def sweep_pending(application: Application) -> None:
    bot = application.bot
    tracker: PendingTracker = application.bot_data["tracker"]
    recent_timeouts: deque = application.bot_data["recent_timeouts"]
    while True:
        try:
            now = time.time()
            for p in await tracker.all():
                if now - p.created_ts > PENDING_TIMEOUT_SECONDS:
                    log.warning("timeout for pending %s (status=%s)", p.raw_file, p.status)
                    minutes = PENDING_TIMEOUT_SECONDS // 60
                    # Tailor wording to actual status. "ingested" means the ingest
                    # itself succeeded and a source page exists — only the
                    # `deployed:` marker never came back, which usually means
                    # rsync/Quartz lagged or bot was restarted mid-tail.
                    if p.status in ("ingested", "deployed"):
                        src_label = (
                            f"\nSource page: <code>{p.new_source_file}</code>"
                            if p.new_source_file else ""
                        )
                        msg_text = (
                            f"⏱️ Quá {minutes} phút đợi marker deploy cho "
                            f"<code>{p.raw_file}</code>.\n"
                            f"Status hiện tại: <b>{p.status}</b> — ingest đã xong, "
                            f"chỉ deploy không phản hồi.{src_label}\n\n"
                            f"Có thể wiki đã update rồi, kiểm tra: "
                            f"{QUARTZ_PUBLIC_BASE_URL}/\n"
                            f"Nếu cần ép chạy lại: <code>/retry {p.raw_file}</code>"
                        )
                    else:
                        msg_text = (
                            f"⏱️ Quá {minutes} phút mà pipeline chưa xong cho "
                            f"<code>{p.raw_file}</code>.\n"
                            f"Last status: <b>{p.status}</b>. "
                            f"Xem <code>scripts/watcher.log</code>.\n\n"
                            f"Lệnh nhanh:\n"
                            f"• Chạy lại: <code>/retry {p.raw_file}</code>\n"
                            f"• Hủy hẳn: <code>/cancel {p.raw_file}</code>"
                        )
                    try:
                        await bot.send_message(
                            chat_id=p.chat_id,
                            reply_to_message_id=p.msg_id,
                            text=msg_text,
                            parse_mode="HTML",
                        )
                    finally:
                        recent_timeouts.append(p.raw_file)
                        await tracker.remove(p.raw_file)
        except Exception as e:
            log.exception("sweeper error: %s", e)
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)


# ---------- App lifecycle ----------
async def _post_init(application: Application) -> None:
    application.bot_data["tracker"] = PendingTracker()
    # Files the sweep just timed out — `/retry` no-args picks from here first.
    application.bot_data["recent_timeouts"] = deque(maxlen=16)
    emit = await make_emitter(application)
    loop = asyncio.get_running_loop()
    application.bot_data["tail_task"] = loop.create_task(tail_watcher_log(emit))
    application.bot_data["poll_task"] = loop.create_task(poll_sources(application))
    application.bot_data["sweep_task"] = loop.create_task(sweep_pending(application))
    log.info("post_init: tracker + tail + poll + sweep started")


async def _post_shutdown(application: Application) -> None:
    for key in ("tail_task", "poll_task", "sweep_task"):
        t = application.bot_data.get(key)
        if t:
            t.cancel()
    log.info("post_shutdown: background tasks cancelled")


def build_app() -> Application:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN missing in .env. See .env.example."
        )
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(_post_init)
        .post_shutdown(_post_shutdown)
        .build()
    )
    app.add_handler(CommandHandler("provider", on_provider_cmd))
    app.add_handler(CommandHandler("chatprovider", on_chatprovider_cmd))
    app.add_handler(CommandHandler("retry", on_retry_cmd))
    app.add_handler(CommandHandler("cancel", on_cancel_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    return app


# ---------- --getchatid mode ----------
def run_getchatid() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN missing in .env.")

    print("Send any message to your bot from the account you want to allowlist...")
    print("(Ctrl-C to abort)")

    async def _grab(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id if update.effective_chat else None
        user = update.effective_user.username if update.effective_user else "?"
        print(f"\n=== chat_id={chat_id}  username=@{user} ===")
        print(f"Add to .env:\n  TELEGRAM_ALLOWED_CHAT_ID={chat_id}")
        os._exit(0)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, _grab))
    app.run_polling(allowed_updates=["message"])


# ---------- Entry ----------
def main() -> None:
    parser = argparse.ArgumentParser(description="Telegram bot for llm-wiki ingest")
    parser.add_argument(
        "--getchatid",
        action="store_true",
        help="Helper: print chat_id of next message and exit",
    )
    args = parser.parse_args()

    if args.getchatid:
        run_getchatid()
        return

    log.info("Starting telegram bot (allowlist chat_id=%s)", TELEGRAM_ALLOWED_CHAT_ID)
    app = build_app()
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
