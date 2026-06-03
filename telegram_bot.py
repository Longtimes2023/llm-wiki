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
from html import escape
from pathlib import Path
from types import SimpleNamespace
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
PENDING_HARD_TIMEOUT_SECONDS = 7200
SWEEP_INTERVAL_SECONDS = 30
LOG_POLL_INTERVAL_SECONDS = 1.0
SOURCES_POLL_INTERVAL_SECONDS = 15
HEARTBEAT_INTERVAL_SECONDS = 60
# Cap for bot_data["recent_resolved"]: parked entries from hard-timed-out pendings
# so a late-arriving deploy marker can still notify the user even after the
# tracker entry has been removed. In-memory only (bot restart loses entries).
RECENT_RESOLVED_MAXLEN = 32
# Poller fail-safe: when the bot's filesystem poller has flipped a pending to
# `status=ingested` and no sync_start marker has landed for this many seconds,
# the bot itself fires sync-and-rebuild.sh as a backstop. Protects the user
# from the watcher misclassifying the ingest result (e.g. update-only or
# already-ingested cases the heuristic misses) and never calling sync.
POLLER_SYNC_FAILSAFE_SECONDS = 120

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
RE_SOURCE_URL = re.compile(r"^source_url:\s*(\S+)\s*$", re.MULTILINE)
RE_SOURCE_PATH = re.compile(r"^source_path:\s*raw/articles/(\S+\.md)\s*$", re.MULTILINE)
# Matches both `source_url: https://…` (stub raws) and `source: "https://…"` (post-fetch raws).
RE_RAW_URL_ANY = re.compile(
    r"""^(?:source_url|source)\s*:\s*["']?(https?://[^\s"']+)["']?\s*$""",
    re.MULTILINE,
)
RE_PROVIDER_TOKEN = re.compile(r"@([a-z0-9_-]+)\b", re.IGNORECASE)

# Markers emitted by raw-watcher.sh + sync-and-rebuild.sh
RE_DETECTED = re.compile(r"detected new file:\s*(\S+\.md)")
RE_INGEST_OK = re.compile(r"INGEST VERIFIED OK")
RE_INGEST_FAIL = re.compile(r"GIVING UP after \d+ attempts:\s*(\S+\.md)")
RE_DEDUP_SKIP = re.compile(r"DEDUP_SKIP:\s*(\S+\.md)\s+same URL as\s+(\S+\.md)\s+— skipping ingest, no rebuild needed")
RE_DEPLOYED = re.compile(r"deployed:\s*(https?://\S+)")
# Progress milestones — surfaced to user as ack edits (not new replies).
RE_INGEST_START = re.compile(r"ingest start \|")
RE_INGEST_ATTEMPT = re.compile(r"attempt (\d+)/(\d+)(?:\s*\|\s*provider=(\S+))?")
RE_SYNC_OK = re.compile(r"post-ingest sync OK")
RE_INGEST_RETRY_FAIL = re.compile(r"INGEST FAILED \((.+?)\)")
# Sync+deploy phase markers from sync-and-rebuild.sh. RE_SYNC_RUNNING matches
# the explicit `[sync] running:` start marker; RE_REBUILD_OK fires after
# `Quartz build OK (NNN files emitted)`; RE_SYNC_FAILED catches both Quartz
# build failures and Cloudflare deploy failures so the user gets a single
# error notification instead of silent watcher.log mutation.
RE_SYNC_RUNNING = re.compile(r"\[sync\] running(?::\s*(\S+))?")
RE_REBUILD_OK = re.compile(r"\[sync\] Quartz build OK \((\d+) files emitted\)")
RE_SYNC_FAILED = re.compile(r"\[sync\] (Quartz build FAILED[^\n]*|Cloudflare deploy FAILED[^\n]*)")

# ---------- Content type detection ----------
# Maps URL patterns to content_type for multimodal provider routing.
# Returns "text" for general URLs; "video" / "image" / "audio" for known media hosts.
_YT_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"}
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".avif"}
_AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".wma"}
_VIDEO_EXTS = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".flv"}
_MEDIA_HOSTS_VIDEO = {"vimeo.com", "www.vimeo.com", "dailymotion.com", "www.dailymotion.com",
                       "tiktok.com", "www.tiktok.com", "twitch.tv", "www.twitch.tv",
                       "bilibili.com", "www.bilibili.com"}


def detect_content_type(url: str) -> str:
    """Classify URL as text / video / image / audio.

    Priority:
      1. Known video hosts (YouTube, Vimeo, TikTok, …) → "video"
      2. File extension match → corresponding type
      3. Default → "text"
    """
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
    except Exception:
        return "text"

    host = parsed.hostname or ""
    path_lower = parsed.path.lower()

    # YouTube / known video hosts
    if host in _YT_HOSTS or host in _MEDIA_HOSTS_VIDEO:
        return "video"

    # Extension-based detection (strip query string)
    ext = Path(path_lower).suffix
    if ext in _IMAGE_EXTS:
        return "image"
    if ext in _AUDIO_EXTS:
        return "audio"
    if ext in _VIDEO_EXTS:
        return "video"

    return "text"


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
    timeout_notified_ts: Optional[float] = None
    # Progress tracking — populated by tail_watcher_log milestones + heartbeat loop.
    phase: str = "queued"  # queued / fetching / attempt_1..N / verifying / syncing
    attempt: int = 0
    max_attempts: int = 3
    ack_base_text: Optional[str] = None  # initial ack text, used as heartbeat prefix
    # Idempotent milestone flags. Each phase ("ingested", "deployed", "failed") is
    # appended exactly once so that the filesystem poller (poll_sources) and the
    # watcher.log tail (tail_watcher_log) can each independently call
    # notify_milestone without double-messaging the user.
    notified_phases: list[str] = field(default_factory=list)
    # When poller or watcher first flips status to "ingested". The poller
    # fail-safe uses (now - ingested_ts) > POLLER_SYNC_FAILSAFE_SECONDS to
    # decide whether to trigger sync-and-rebuild.sh as backstop.
    ingested_ts: Optional[float] = None
    sync_failsafe_fired: bool = False
    # Set when the watcher actually starts processing this file (ingest_start
    # or first ingest_attempt event). Used by sweep_pending to skip timeout
    # for entries still waiting in the watcher queue.
    started_ts: Optional[float] = None
    # Content type detected from URL (text/video/image/audio). Used for
    # multimodal provider routing and display in notifications.
    content_type: str = "text"


class PendingTracker:
    def __init__(self) -> None:
        self._items: dict[str, Pending] = {}
        self._lock = asyncio.Lock()

    async def add(self, p: Pending) -> None:
        async with self._lock:
            self._items[p.raw_file] = p
        await self._persist()

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
            await self._persist()
            return p

    async def remove(self, raw_file: str) -> Optional[Pending]:
        async with self._lock:
            p = self._items.pop(raw_file, None)
        if p is not None:
            await self._persist()
        return p

    async def all(self) -> list[Pending]:
        async with self._lock:
            return list(self._items.values())

    async def _persist(self) -> None:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        async with self._lock:
            items = list(self._items.values())
        data = [asdict(p) for p in items]
        tmp = STATE_FILE.with_suffix(".tmp")
        async with aiofiles.open(tmp, "w") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
        tmp.rename(STATE_FILE)

    async def restore(self) -> int:
        """Restore pending entries from STATE_FILE after restart."""
        if not STATE_FILE.exists():
            return 0
        try:
            raw = STATE_FILE.read_text(encoding="utf-8").strip()
            if not raw:
                return 0
            data = json.loads(raw)
            if not isinstance(data, list):
                return 0
            restored = 0
            async with self._lock:
                for d in data:
                    if not isinstance(d, dict) or "raw_file" not in d:
                        continue
                    # Only restore non-terminal entries
                    if d.get("status") in ("deployed", "failed"):
                        continue
                    p = Pending(**{k: v for k, v in d.items() if k in Pending.__dataclass_fields__})
                    self._items[p.raw_file] = p
                    restored += 1
            if restored:
                log.info("restored %d pending entries from state file", restored)
            return restored
        except Exception as e:
            log.warning("failed to restore state file: %s", e)
            return 0


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


def _read_raw_url(raw_path: Path) -> Optional[str]:
    """Pull `source_url:` or `source: "…"` from a raw file's frontmatter."""
    try:
        head = raw_path.read_text(encoding="utf-8", errors="ignore")[:2500]
    except OSError:
        return None
    m = RE_RAW_URL_ANY.search(head)
    return m.group(1) if m else None


def find_source_page_for_url(url: str) -> Optional[str]:
    """Find a wiki/sources/*.md that backs `url`, even if the raw was renamed.

    Walks each source page → reads its source_path: → reads that raw's
    source/source_url frontmatter → matches against `url`. Handles the case
    where ingest renamed the raw, breaking the filename-based lookup.
    """
    if not SOURCES_DIR.exists():
        return None
    target = _norm_url(url)
    for src in SOURCES_DIR.glob("*.md"):
        try:
            head = src.read_text(encoding="utf-8", errors="ignore")[:1500]
        except OSError:
            continue
        m = RE_SOURCE_PATH.search(head)
        if not m:
            continue
        raw_path = RAW_ARTICLES_DIR / m.group(1)
        raw_url = _read_raw_url(raw_path)
        if raw_url and _norm_url(raw_url) == target:
            return src.name
    return None


def source_page_matches_pending(src_name: str, pending: Pending) -> bool:
    src_path = SOURCES_DIR / src_name
    try:
        head = src_path.read_text(encoding="utf-8", errors="ignore")[:1500]
    except OSError:
        return False

    m = RE_SOURCE_PATH.search(head)
    if m and m.group(1) == pending.raw_file:
        return True

    pending_url = _read_raw_url(RAW_ARTICLES_DIR / pending.raw_file)
    if not pending_url:
        return False

    source_url = None
    raw_url = None
    raw_path = RAW_ARTICLES_DIR / m.group(1) if m else None
    if raw_path:
        raw_url = _read_raw_url(raw_path)

    url_match = RE_RAW_URL_ANY.search(head)
    if url_match:
        source_url = url_match.group(1)

    target = _norm_url(pending_url)
    return any(_norm_url(url) == target for url in (source_url, raw_url) if url)


def find_matching_new_source_for_pending(pending: Pending) -> Optional[str]:
    for src_name in diff_new_sources(pending.sources_snapshot):
        if source_page_matches_pending(src_name, pending):
            return src_name
    return None


def find_metrics_for_raw(raw_filename: str) -> Optional[dict]:
    """Read the latest metrics line for this raw_file from ingest_metrics.jsonl.

    Prefer the most recent entry with input_tokens > 0 (an attempt that actually
    reached the model). Falls back to the last entry if every attempt failed,
    so callers can still surface the failure for debugging.
    """
    if not METRICS_FILE.exists():
        return None
    try:
        last = None
        last_success = None
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
                    if (obj.get("input_tokens") or 0) > 0:
                        last_success = obj
        return last_success or last
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


def _is_placeholder_value(value: object) -> bool:
    if not isinstance(value, str):
        return False
    s = value.strip()
    return s in {
        "<id>",
        "<url>",
        "<一句话原因>",
        "403|paywall|empty|timeout|runtime_failed",
        "<source_id>",
        "<reason>",
        "<status>",
        "真实来源ID",
        "真实原始URL",
        "真实单一状态值",
        "真实一句话原因",
    }


def _clean_fetch_fail_info(fail_info: dict) -> tuple[Optional[str], Optional[str], Optional[str]]:
    status = fail_info.get("status")
    reason = fail_info.get("reason")
    url = fail_info.get("url")

    status_text = None if _is_placeholder_value(status) else str(status).strip() or None
    reason_text = None if _is_placeholder_value(reason) else str(reason).strip() or None
    url_text = None if _is_placeholder_value(url) else str(url).strip() or None
    return status_text, reason_text, url_text


def find_watcher_status_for_raw(raw_filename: str) -> Optional[dict]:
    if not WATCHER_LOG.exists():
        return None

    status: dict = {
        "attempt": None,
        "max_attempts": None,
        "provider": None,
        "failures": [],
        "final_give_up": False,
        "started": False,
    }
    in_section = False

    try:
        with WATCHER_LOG.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                detected = RE_DETECTED.search(line)
                if detected:
                    in_section = Path(detected.group(1)).name == raw_filename
                    if in_section:
                        status = {
                            "attempt": None,
                            "max_attempts": None,
                            "provider": None,
                            "failures": [],
                            "final_give_up": False,
                            "started": False,
                        }
                    continue

                give_up = RE_INGEST_FAIL.search(line)
                if give_up and Path(give_up.group(1)).name == raw_filename:
                    status["final_give_up"] = True
                    in_section = False
                    continue

                if not in_section:
                    continue

                if RE_INGEST_START.search(line):
                    status["started"] = True
                    continue

                attempt = RE_INGEST_ATTEMPT.search(line)
                if attempt:
                    status["attempt"] = int(attempt.group(1))
                    status["max_attempts"] = int(attempt.group(2))
                    status["provider"] = attempt.group(3)
                    continue

                failure = RE_INGEST_RETRY_FAIL.search(line)
                if failure:
                    status["failures"].append(failure.group(1))
    except OSError:
        return None

    if status["started"] or status["attempt"] or status["failures"] or status["final_give_up"]:
        return status
    return None


def _format_failure_reason_text(reason: str) -> str:
    reason = reason.strip()
    if reason.startswith("timeout 25m"):
        return "một attempt đã chạm hard timeout 25 phút"
    if reason.startswith("partial:"):
        return f"attempt cuối ghi dở: {reason}"
    if reason.startswith("api/connection error"):
        return f"lỗi API/kết nối: {reason}"
    if reason.startswith("exit code"):
        return f"agent thoát lỗi: {reason}"
    if reason.startswith("sources count unchanged"):
        return f"không tạo thêm source page: {reason}"
    return reason


def _format_watcher_status_reason(status: dict) -> Optional[str]:
    parts = []
    failures = status.get("failures") or []
    if failures:
        summarized = [_format_failure_reason_text(reason) for reason in failures[-2:]]
        parts.append("; ".join(summarized))

    attempt = status.get("attempt")
    max_attempts = status.get("max_attempts")
    if status.get("final_give_up"):
        if attempt and max_attempts:
            parts.append(f"watcher đã dừng sau {attempt}/{max_attempts} attempts")
        else:
            parts.append("watcher đã dừng sau nhiều lần thử")
    elif attempt and max_attempts:
        provider = status.get("provider")
        provider_text = f" bằng provider {provider}" if provider else ""
        parts.append(f"watcher đang/đã chạy attempt {attempt}/{max_attempts}{provider_text}")
    elif status.get("started"):
        parts.append("watcher đã bắt đầu xử lý file này")

    if not parts:
        return None
    return "; ".join(parts) + "."


def format_pipeline_reason(pending: Pending) -> str:
    fail_info = find_fetch_fail_for_raw(pending.raw_file)
    if fail_info:
        status_label, reason, url = _clean_fetch_fail_info(fail_info)
        details = []
        if status_label:
            details.append(f"status: {status_label}")
        if reason:
            details.append(reason)
        if url:
            details.append(f"URL: {url}")
        if details:
            return "; ".join(details) + "."

    watcher_status = find_watcher_status_for_raw(pending.raw_file)
    watcher_reason = _format_watcher_status_reason(watcher_status) if watcher_status else None
    if watcher_reason:
        return watcher_reason

    live_parts = []
    if pending.attempt and pending.max_attempts:
        live_parts.append(f"watcher đang/đã chạy attempt {pending.attempt}/{pending.max_attempts}")
    if pending.phase and pending.phase != "queued":
        live_parts.append(f"phase hiện tại: {pending.phase}")
    if live_parts:
        return "; ".join(live_parts) + "."

    return "Chưa thấy marker kết thúc từ watcher; attempt hiện tại có thể vẫn đang chạy hoặc bị kẹt."



def _lookup_source_page_for_raw(pending: Pending) -> Optional[str]:
    if pending.new_source_file:
        return pending.new_source_file
    direct = find_source_page_for_raw(pending.raw_file)
    if direct:
        return direct
    # Fallback: raw may have been renamed by ingest. Try URL-based lookup.
    raw_url = _read_raw_url(RAW_ARTICLES_DIR / pending.raw_file)
    if raw_url:
        return find_source_page_for_url(raw_url)
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
    content_type: str = "text",
) -> Path:
    RAW_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    short = hashlib.sha1(f"{url}:{msg_id}:{time.time()}".encode()).hexdigest()[:6]
    path = RAW_ARTICLES_DIR / f"{ts}-tg-{short}.md"
    provider_line = f"provider: {provider}\n" if provider else ""
    body = (
        f"---\n"
        f"source_url: {url}\n"
        f"content_type: {content_type}\n"
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

    event_type ∈ {
      "ingest_ok", "ingest_fail", "dedup_skip", "deployed",
      "ingest_start", "ingest_attempt", "ingest_retry_fail", "sync_ok",
    }
    payload: dict with at least one of: filename, url
    """
    if not WATCHER_LOG.exists():
        log.warning("watcher.log not found yet at %s — will wait", WATCHER_LOG)

    last_inode: Optional[int] = None
    fp = None
    last_seen_filename: Optional[str] = None  # bind ingest_ok to most recent "detected" line
    _sync_hint_filename: Optional[str] = None  # from [sync] running: <hint> — more accurate for deploy binding

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

            # Progress milestones — only emit if bound to a known pending filename.
            if last_seen_filename:
                if RE_INGEST_START.search(line):
                    await emit("ingest_start", {"filename": last_seen_filename})
                    continue
                m = RE_INGEST_ATTEMPT.search(line)
                if m:
                    await emit("ingest_attempt", {
                        "filename": last_seen_filename,
                        "attempt": int(m.group(1)),
                        "max_attempts": int(m.group(2)),
                        "provider": m.group(3),
                    })
                    continue
                # `INGEST FAILED (...)` is a per-attempt failure; bot stays in retry mode
                # until either `INGEST VERIFIED OK` or `GIVING UP after N attempts` lands.
                m = RE_INGEST_RETRY_FAIL.search(line)
                if m:
                    await emit("ingest_retry_fail", {
                        "filename": last_seen_filename,
                        "reason": m.group(1),
                    })
                    continue
                if RE_SYNC_OK.search(line):
                    await emit("sync_ok", {"filename": _sync_hint_filename or last_seen_filename})
                    continue
                m = RE_SYNC_RUNNING.search(line)
                if m:
                    hint = m.group(1)  # e.g. "bot-failsafe:raw.md", "raw.md", or "manual"
                    if hint and hint != "manual":
                        # bot-failsafe:<raw>.md → strip prefix; <raw>.md → keep
                        _sync_hint_filename = hint.removeprefix("bot-failsafe:")
                    await emit("sync_start", {"filename": last_seen_filename})
                    continue
                m = RE_REBUILD_OK.search(line)
                if m:
                    await emit("rebuild_ok", {
                        "filename": _sync_hint_filename or last_seen_filename,
                        "files_emitted": int(m.group(1)),
                    })
                    continue
                m = RE_SYNC_FAILED.search(line)
                if m:
                    await emit("sync_fail", {
                        "filename": _sync_hint_filename or last_seen_filename,
                        "reason": m.group(1),
                    })
                    continue

            if RE_INGEST_OK.search(line) and last_seen_filename:
                await emit("ingest_ok", {"filename": last_seen_filename})
                continue

            m = RE_INGEST_FAIL.search(line)
            if m:
                await emit("ingest_fail", {"filename": Path(m.group(1)).name})
                continue

            m = RE_DEDUP_SKIP.search(line)
            if m:
                await emit("dedup_skip", {"filename": Path(m.group(1)).name})
                continue

            m = RE_DEPLOYED.search(line)
            deploy_filename = _sync_hint_filename or last_seen_filename
            if m and deploy_filename:
                log.debug(
                    "deploy event: filename=%s url=%s (hint=%s last=%s)",
                    deploy_filename, m.group(1), _sync_hint_filename, last_seen_filename,
                )
                await emit(
                    "deployed",
                    {"filename": deploy_filename, "url": m.group(1)},
                )
                _sync_hint_filename = None  # one-shot: each sync deploy uses its own hint
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


async def _send_long(msg, text: str, *, prefer_plain: bool = False) -> None:
    """Split > Telegram limit and reply each chunk. Markdown→plain fallback per chunk."""
    if not text:
        await msg.reply_text("(empty)")
        return
    chunks = [text[i:i + TELEGRAM_MAX_MSG] for i in range(0, len(text), TELEGRAM_MAX_MSG)]
    for chunk in chunks:
        if prefer_plain:
            try:
                await msg.reply_text(chunk, disable_web_page_preview=True)
            except Exception as e:
                log.exception("send_long plain-text send failed: %s", e)
            continue
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


def _command_parts(text: str) -> list[str]:
    if not text:
        return []
    parts = text.strip().split()
    if not parts or not parts[0].startswith("/"):
        return []
    head = parts[0][1:].split("@", 1)[0].lower()
    return [head, *parts[1:]]


def _command_args(update: Update, context: ContextTypes.DEFAULT_TYPE) -> list[str]:
    if context.args:
        return context.args
    msg = update.effective_message
    return _command_parts(msg.text)[1:] if msg and msg.text else []


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg or not msg.text:
        return
    chat_id = msg.chat_id

    if not _is_allowed(chat_id):
        log.warning("ignoring message from non-allowlisted chat_id=%s", chat_id)
        return

    cmd_parts = _command_parts(msg.text)
    if cmd_parts:
        cmd = cmd_parts[0]
        if cmd == "provider":
            await on_provider_cmd(update, context)
            return
        if cmd == "chatprovider":
            await on_chatprovider_cmd(update, context)
            return
        if cmd == "retry":
            await on_retry_cmd(update, context)
            return
        if cmd == "cancel":
            await on_cancel_cmd(update, context)
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
            # Try filename-based source lookup first, then fall back to URL-based
            # (handles raws renamed by ingest — e.g. stub → slugified filename).
            src_name = find_source_page_for_raw(existing.name) or find_source_page_for_url(url)
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

    content_type = detect_content_type(url)
    raw_path = write_raw_file(url, chat_id, msg.message_id, provider=provider_override, content_type=content_type)
    log.info(
        "wrote raw file %s for url=%s provider=%s content_type=%s",
        raw_path, url, provider_override or "(default)", content_type,
    )

    sources_before = snapshot_sources()
    log.info("snapshot sources before ingest: %d files", len(sources_before))

    ack_lines = [f"🔄 Đã nhận URL — đang đẩy vào pipeline:", url]
    if content_type != "text":
        ack_lines.append(f"\n<b>Content type:</b> {content_type} → multimodal provider")
    if provider_override:
        ack_lines.append(f"\n<b>Provider override:</b> {provider_override} (one-off, dedup bypass)")
    ack_lines.append(f"\nFile: <code>{raw_path.name}</code>")
    ack_lines.append("Sẽ reply link wiki khi pipeline xong (thường 1–5 phút).")
    ack_text = "\n".join(ack_lines)
    ack = await msg.reply_text(ack_text, parse_mode="HTML")

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
            ack_base_text=ack_text,
            content_type=content_type,
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

    args = _command_args(update, context)
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

    args = _command_args(update, context)
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
    args = _command_args(update, context)
    arg = args[0] if args else None
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
    # Read content_type from existing raw file frontmatter (set during original ingest).
    retry_content_type = "text"
    try:
        raw_text = target.read_text(encoding="utf-8", errors="replace")
        m_ct = re.search(r"^content_type:\s*(\S+)", raw_text, re.MULTILINE)
        if m_ct:
            retry_content_type = m_ct.group(1)
    except OSError:
        pass
    ack_text = (
        f"🔁 Đã retry <code>{raw_name}</code>.\n"
        + (f"Killed PID <code>{pid}</code>.\n" if pid else "")
        + (f"Removed from <code>watcher.failed</code>.\n" if removed_from_failed else "")
        + "Sẽ báo khi pipeline xong (thường 1–5 phút)."
    )
    ack = await msg.reply_text(ack_text, parse_mode="HTML")

    await tracker.add(
        Pending(
            raw_file=raw_name,
            chat_id=chat_id,
            msg_id=msg.message_id,
            ack_msg_id=ack.message_id if ack else None,
            created_ts=time.time(),
            status="queued",
            sources_snapshot=sources_before,
            ack_base_text=ack_text,
            content_type=retry_content_type,
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
    args = _command_args(update, context)
    arg = args[0] if args else None
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


# ---------- Progress ack helpers ----------
def _format_progress_line(p: Pending, now: float) -> str:
    elapsed_s = max(0, int(now - p.created_ts))
    if elapsed_s < 60:
        elapsed = f"{elapsed_s}s"
    else:
        elapsed = f"{elapsed_s / 60:.1f}m"
    parts = [f"⏳ {elapsed}"]
    # Once the poller (or watcher) has flipped to ingested, the watcher's
    # `attempt N/M` and stale failure phase text become misleading — the
    # pipeline has already crossed into sync/deploy. Override the display
    # with a sync/deploy-derived label so the user sees forward motion.
    sync_phases = {"syncing", "synced", "deploying", "sync_failed"}
    if p.status == "ingested":
        derived = p.phase if p.phase in sync_phases else "sync/deploy"
        parts.append(f"phase: {derived}")
    else:
        if p.attempt > 0:
            parts.append(f"attempt {p.attempt}/{p.max_attempts}")
        if p.phase and p.phase != "queued":
            parts.append(f"phase: {p.phase}")
    return " · ".join(parts)


async def _edit_ack_progress(bot, p: Pending) -> None:
    """Re-render the ack with an appended progress line. Silent on Telegram no-op."""
    if not p.ack_msg_id or not p.ack_base_text:
        return
    progress = _format_progress_line(p, time.time())
    text = f"{p.ack_base_text}\n\n{progress}"
    try:
        await bot.edit_message_text(
            chat_id=p.chat_id,
            message_id=p.ack_msg_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        # "Message is not modified" → benign; everything else → log and move on.
        if "not modified" in str(e).lower():
            return
        log.debug("edit_message_text failed for %s: %s", p.raw_file, e)


async def notify_milestone(
    bot,
    p: Pending,
    phase: str,
    tracker: PendingTracker,
    extra: Optional[dict] = None,
) -> bool:
    """Send a one-time user message for a pipeline milestone.

    Idempotent on `phase` — repeated calls for the same (raw_file, phase) are no-ops,
    so the filesystem poller (poll_sources) and the watcher.log tail
    (tail_watcher_log) can each independently call this without double-messaging.

    Returns True if the message was sent this call, False if skipped (already notified
    or unrecognized phase).
    """
    if phase in (p.notified_phases or []):
        return False

    extra = extra or {}
    text: Optional[str] = None
    if phase == "ingested":
        src = p.new_source_file or extra.get("new_source") or "?"
        text = (
            f"✓ Đã ingest xong cho <code>{escape(p.raw_file)}</code>.\n"
            f"Source: <code>{escape(src)}</code>\n"
            f"Đang sync + deploy lên Cloudflare Pages..."
        )
    elif phase == "deployed":
        url = extra.get("url") or p.last_deploy_url or ""
        src_label = (
            f"\nSource: <code>{escape(p.new_source_file)}</code>"
            if p.new_source_file else ""
        )
        metrics = find_metrics_for_raw(p.raw_file)
        metrics_label = f"\n{format_metrics_line(metrics)}" if metrics else ""
        text = (
            f"✅ Đã ingest + deploy xong!\n"
            f"Wiki: {escape(url)}{src_label}{metrics_label}\n"
            f"(Site: {escape(QUARTZ_PUBLIC_BASE_URL)}/)"
        )
    elif phase == "sync_failed":
        # Surfaced when watcher.log shows `[sync] Quartz build FAILED` or
        # `[sync] Cloudflare deploy FAILED`. The reason is the matched substring
        # from RE_SYNC_FAILED — short enough to inline, truncated for safety.
        reason = (extra.get("reason") or "unknown").strip()[:200]
        src_label = (
            f"\nSource: <code>{escape(p.new_source_file)}</code>"
            if p.new_source_file else ""
        )
        text = (
            f"⚠️ Sync/build thất bại cho <code>{escape(p.raw_file)}</code>.\n"
            f"Lý do: {escape(reason)}{src_label}\n"
            f"Wiki có thể đang stale. Thử lại: <code>/retry {escape(p.raw_file)}</code>"
        )

    if text is None:
        return False

    try:
        await bot.send_message(
            chat_id=p.chat_id,
            reply_to_message_id=p.msg_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=(phase != "deployed"),
        )
    except Exception as e:
        log.exception("notify_milestone(%s) send failed for %s: %s", phase, p.raw_file, e)
        return False

    new_phases = list(p.notified_phases or [])
    new_phases.append(phase)
    await tracker.update(p.raw_file, notified_phases=new_phases)
    return True


# ---------- Bridge: log events → telegram replies ----------
def park_pending_for_late_marker(
    p: "Pending",
    recent_resolved: dict,
    now: float,
    maxlen: int = RECENT_RESOLVED_MAXLEN,
) -> bool:
    """Park a pending entry so a deploy marker arriving AFTER hard-removal
    can still notify the user. FIFO-evicts at `maxlen`.

    Returns False (and does nothing) when parking would serve no purpose —
    entry already deployed, or status not in queued/ingested.
    """
    if p.status not in ("queued", "ingested") or p.last_deploy_url:
        return False
    recent_resolved[p.raw_file] = {
        "raw_file": p.raw_file,
        "chat_id": p.chat_id,
        "msg_id": p.msg_id,
        "new_source_file": p.new_source_file,
        "created_ts": p.created_ts,
        "parked_ts": now,
    }
    while len(recent_resolved) > maxlen:
        recent_resolved.pop(next(iter(recent_resolved)))
    return True


async def make_emitter(application: Application):
    bot = application.bot
    tracker: PendingTracker = application.bot_data["tracker"]

    async def emit(event_type: str, payload: dict) -> None:
        filename = payload.get("filename")
        if event_type == "dedup_skip" and not filename:
            filename = next((item.raw_file for item in await tracker.all() if item.status == "queued"), None)
        if not filename and event_type != "deployed":
            return

        if event_type == "deployed":
            # 3-tier lookup for deployed: tail_watcher_log binds `[sync] deployed:` lines
            # to `last_seen_filename`, which can drift to the WRONG raw_file when a
            # second `detected new file:` arrives between this raw's ingest and its
            # deploy marker — or be entirely irrelevant when sync-and-rebuild.sh is
            # invoked manually. Without the fallback, the deploy marker is silently
            # dropped (telegram_bot.log entry: "ignoring ... no tracker entry").
            p = await tracker.get(filename) if filename else None
            if not p:
                # Tier 2a: exact filename match among ALL pending entries.
                # When the tail reader falls behind, last_seen_filename can
                # drift to a different file, causing Tier 1 to miss.  But the
                # _sync_hint_filename (used for `filename`) is correct, so a
                # direct scan finds the right entry.
                all_pending = await tracker.all()
                if filename:
                    for cp in all_pending:
                        if cp.raw_file == filename:
                            p = cp
                            break
                # Tier 2b: oldest ingested without deploy_url (best-effort).
                if not p:
                    candidates = [
                        cp for cp in all_pending
                        if cp.status == "ingested" and not cp.last_deploy_url
                    ]
                    if candidates:
                        p = min(candidates, key=lambda x: x.created_ts)
                        log.warning(
                            "deployed event filename=%s has no exact tracker match; "
                            "fallback to oldest pending without deploy_url: %s",
                            filename, p.raw_file,
                        )
                        filename = p.raw_file
            if not p:
                # 3rd tier: late deploy marker landing AFTER sweep_pending
                # hard-removed the tracker entry. Reconstruct a local Pending
                # from recent_resolved so notify_milestone can still reply to
                # the original Telegram message. Not re-inserted into tracker
                # because the entry is terminal — drained one-shot.
                recent_resolved: dict = application.bot_data.get("recent_resolved") or {}
                parked = recent_resolved.get(filename) if filename else None
                if not parked and recent_resolved:
                    parked = recent_resolved[next(reversed(recent_resolved))]
                if parked:
                    p = Pending(
                        raw_file=parked["raw_file"],
                        chat_id=parked["chat_id"],
                        msg_id=parked["msg_id"],
                        ack_msg_id=None,
                        created_ts=parked["created_ts"],
                        new_source_file=parked.get("new_source_file"),
                        status="ingested",
                        notified_phases=[],
                    )
                    filename = p.raw_file
                    recent_resolved.pop(p.raw_file, None)
                    log.warning(
                        "deployed event matched parked recent_resolved entry %s "
                        "(tracker had already hard-removed it)", p.raw_file,
                    )
            if not p:
                log.info(
                    "deployed event filename=%s but no eligible pending entry "
                    "(already cleared or never tracked)", filename,
                )
                return
        else:
            p = await tracker.get(filename)
            if not p:
                return  # not ours, ignore

        if event_type == "ingest_ok":
            new_sources = diff_new_sources(p.sources_snapshot)
            new_src = new_sources[0] if new_sources else None
            matched_source = new_src or _lookup_source_page_for_raw(p)
            p2 = await tracker.update(
                filename,
                status="ingested",
                last_ingest_event="ok",
                new_source_file=matched_source,
                phase="ingested",
                ingested_ts=time.time() if p.ingested_ts is None else p.ingested_ts,
            )
            log.info(
                "ingest_ok matched pending %s; new source=%s (total new: %d)",
                filename, matched_source, len(new_sources),
            )
            if p2:
                await _edit_ack_progress(bot, p2)
                # Idempotent — poller may already have fired this for the same raw.
                await notify_milestone(bot, p2, "ingested", tracker)
        elif event_type == "ingest_start":
            fields = {"phase": "fetching", "last_ingest_event": "start"}
            if not p.started_ts:
                fields["started_ts"] = time.time()
            await tracker.update(filename, **fields)
            p2 = await tracker.get(filename)
            if p2:
                await _edit_ack_progress(bot, p2)
        elif event_type == "ingest_attempt":
            attempt = int(payload.get("attempt") or 0)
            max_attempts = int(payload.get("max_attempts") or 3)
            fields = {
                "attempt": attempt,
                "max_attempts": max_attempts,
                "phase": "starting",
                "last_ingest_event": "attempt",
            }
            if not p.started_ts:
                fields["started_ts"] = time.time()
            await tracker.update(filename, **fields)
            p2 = await tracker.get(filename)
            if p2:
                await _edit_ack_progress(bot, p2)
        elif event_type == "ingest_retry_fail":
            reason = payload.get("reason") or ""
            await tracker.update(
                filename,
                phase=f"retry ({reason[:40]})" if reason else "retrying",
                last_ingest_event="retry_fail",
            )
            p2 = await tracker.get(filename)
            if p2:
                await _edit_ack_progress(bot, p2)
        elif event_type == "sync_ok":
            await tracker.update(filename, phase="synced", last_ingest_event="sync_ok")
            p2 = await tracker.get(filename)
            if p2:
                await _edit_ack_progress(bot, p2)
        elif event_type == "sync_start":
            # First `[sync] running:` marker from sync-and-rebuild.sh. Ack edit
            # only — the user already received the "Đang sync + deploy..."
            # message via notify_milestone("ingested"). This just keeps the
            # heartbeat phase accurate so it doesn't show stale watcher attempts.
            await tracker.update(filename, phase="syncing", last_ingest_event="sync_start")
            p2 = await tracker.get(filename)
            if p2:
                await _edit_ack_progress(bot, p2)
        elif event_type == "rebuild_ok":
            # Quartz build finished; Cloudflare deploy is the next step. Ack edit
            # so heartbeat shows "deploying" rather than "syncing".
            await tracker.update(filename, phase="deploying", last_ingest_event="rebuild_ok")
            p2 = await tracker.get(filename)
            if p2:
                await _edit_ack_progress(bot, p2)
        elif event_type == "sync_fail":
            reason = payload.get("reason") or "unknown"
            p2 = await tracker.update(
                filename,
                phase="sync_failed",
                last_ingest_event="sync_fail",
            )
            target = p2 or p
            sent = await notify_milestone(
                bot, target, "sync_failed", tracker, extra={"reason": reason}
            )
            if not sent:
                log.info(
                    "sync_fail milestone for %s already notified (or no-op), "
                    "skipping resend", filename,
                )
            # Don't tracker.remove — user may /retry. Leave entry until deploy
            # or hard timeout.
        elif event_type == "dedup_skip":
            await tracker.update(filename, status="dedup_skipped", last_ingest_event="dedup_skip")
            try:
                await bot.send_message(
                    chat_id=p.chat_id,
                    reply_to_message_id=p.msg_id,
                    text=(
                        f"♻️ URL này là nội dung trùng, pipeline đã bỏ qua chứ không phải lỗi.\n"
                        f"Raw: <code>{escape(filename)}</code>"
                    ),
                    parse_mode="HTML",
                )
            except Exception as e:
                log.exception("failed to send dedup notification for %s: %s", filename, e)
            finally:
                await tracker.remove(filename)
            return
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
            # derive a concise watcher/progress reason for the user.
            fail_info = find_fetch_fail_for_raw(filename)
            if fail_info:
                status_label, reason, url = _clean_fetch_fail_info(fail_info)
                status_text = f" (status: {status_label})" if status_label else ""
                details = []
                if reason:
                    details.append(reason)
                if url:
                    details.append(f"URL: {url}")
                if details:
                    text = (
                        f"❌ Lấy nội dung thất bại cho file {filename}{status_text}.\n"
                        + "\n".join(details)
                    )
                else:
                    text = (
                        f"❌ Lấy nội dung thất bại cho file {filename}.\n"
                        f"Lý do: {format_pipeline_reason(p)}"
                    )
            else:
                reason = format_pipeline_reason(p)
                text = (
                    f"❌ Pipeline thất bại sau nhiều lần thử cho file "
                    f"{filename}.\nLý do: {reason}"
                )
            try:
                await _send_long(
                    SimpleNamespace(reply_text=lambda *args, **kwargs: bot.send_message(
                        chat_id=p.chat_id,
                        reply_to_message_id=p.msg_id,
                        text=args[0],
                        **kwargs,
                    )),
                    text,
                    prefer_plain=True,
                )
            except Exception as e:
                log.exception("failed to send ingest_fail notification for %s: %s", filename, e)
            finally:
                await tracker.remove(filename)
        elif event_type == "deployed":
            # Prefer the new source file detected after ingest_ok; fallback to root.
            # `url` payload comes from the [sync] deployed: line directly; we ignore
            # it in favor of quartz_url_for_source when we have a source_file so the
            # message lands on the specific page rather than the homepage.
            payload_url = payload.get("url", "")
            url = (
                quartz_url_for_source(p.new_source_file)
                if p.new_source_file
                else (payload_url or f"{QUARTZ_PUBLIC_BASE_URL}/")
            )
            p2 = await tracker.update(filename, status="deployed", last_deploy_url=url)
            target = p2 or p
            # Guard: skip deployed notification when metrics are not yet available.
            # The bot-failsafe deploy often fires BEFORE the watcher writes the
            # metrics line (ingest_metrics.jsonl).  Sending now would produce a
            # message without ⏱/🔢/💰, and marking "deployed" as notified would
            # prevent the watcher's later deploy from resending WITH metrics.
            # By skipping (and NOT marking notified), we let the watcher deploy
            # send the complete message.
            if not find_metrics_for_raw(filename):
                log.info(
                    "deployed event for %s: metrics not yet available, deferring "
                    "notification to next deploy marker (likely watcher sync)",
                    filename,
                )
            else:
                sent = await notify_milestone(bot, target, "deployed", tracker, extra={"url": url})
                if not sent:
                    log.info(
                        "deployed milestone for %s already notified (or no-op), skipping resend",
                        filename,
                    )
                await tracker.remove(filename)
            # else: deferred (metrics not yet available) — entry stays in tracker
            # so the watcher's deploy marker can find it and send WITH metrics.

    return emit


# ---------- Heartbeat: nudge ack with elapsed time every HEARTBEAT_INTERVAL_SECONDS ----------
async def heartbeat_loop(application: Application) -> None:
    """Edit each in-flight pending's ack message every HEARTBEAT_INTERVAL_SECONDS so
    the user sees forward motion even when watcher.log is silent (e.g. mid-LLM call).
    Terminal statuses are skipped — they're handled by make_emitter.
    """
    bot = application.bot
    tracker: PendingTracker = application.bot_data["tracker"]
    while True:
        try:
            for p in await tracker.all():
                # Tick during queued AND ingested — for ingested entries the
                # heartbeat keeps elapsed time visible while sync+deploy runs,
                # and _format_progress_line overrides the stale watcher phase.
                if p.status not in ("queued", "ingested"):
                    continue
                if not p.ack_msg_id or not p.ack_base_text:
                    continue
                await _edit_ack_progress(bot, p)
        except Exception as e:
            log.exception("heartbeat_loop error: %s", e)
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)


# ---------- Source filesystem poller (Option D) ----------
# Authoritative ingest detector. Watches wiki/sources/ for new files matching
# each pending's snapshot. More reliable than watcher.log markers — works even
# when Claude SDK crashes mid-write or watcher.sh's heuristic fails.
def should_fire_sync_failsafe(p: "Pending", now: float) -> bool:
    """Decide if poll_sources should fire sync-and-rebuild.sh as a backstop.

    The bot's poller has authoritative knowledge of "source page exists for
    this raw_file". When the watcher misclassifies the ingest and never calls
    sync (e.g. agent returned no-op for an already-ingested URL but the file
    still exists), the user would wait indefinitely. The fail-safe trips when
    we've been in `status=ingested` for POLLER_SYNC_FAILSAFE_SECONDS without
    a sync_start marker. Once fired, sync_failsafe_fired prevents repeats.
    """
    if p.status != "ingested":
        return False
    if p.sync_failsafe_fired:
        return False
    if p.last_deploy_url:
        return False
    if p.ingested_ts is None:
        return False
    if now - p.ingested_ts <= POLLER_SYNC_FAILSAFE_SECONDS:
        return False
    # last_ingest_event in ("ok", "ok_via_poll") means we never saw sync_start.
    # sync_start updates last_ingest_event to "sync_start"; rebuild_ok / sync_ok
    # advance further. Block the failsafe once the pipeline has moved past ingest.
    if p.last_ingest_event not in (None, "", "ok", "ok_via_poll"):
        return False
    return True


async def poll_sources(application: Application) -> None:
    tracker: PendingTracker = application.bot_data["tracker"]
    bot = application.bot
    while True:
        try:
            for p in await tracker.all():
                if p.status == "queued":
                    matched_source = find_matching_new_source_for_pending(p)
                    if matched_source:
                        now = time.time()
                        p2 = await tracker.update(
                            p.raw_file,
                            status="ingested",
                            new_source_file=matched_source,
                            last_ingest_event="ok_via_poll",
                            # Anticipating sync — _format_progress_line maps
                            # "syncing" to a friendly label and ignores stale
                            # watcher phase wording.
                            phase="syncing",
                            ingested_ts=now,
                        )
                        log.info(
                            "source poll detected ingest: %s → new_source=%s",
                            p.raw_file, matched_source,
                        )
                        # Proactively tell the user immediately, instead of waiting for
                        # watcher.log to emit INGEST VERIFIED OK (can be 7+ min on retry
                        # chains). notify_milestone is idempotent; if the watcher tail
                        # later fires ingest_ok for the same raw, it's a no-op.
                        if p2:
                            await notify_milestone(bot, p2, "ingested", tracker)
                elif should_fire_sync_failsafe(p, time.time()):
                    # Bot-side fail-safe: source exists but no sync_start observed
                    # for >120s. Watcher probably misclassified; fire sync-and-rebuild
                    # ourselves. The script is flock-protected so concurrent calls
                    # from a delayed watcher invocation are no-ops.
                    await tracker.update(p.raw_file, sync_failsafe_fired=True)
                    log.warning(
                        "poller fail-safe firing sync-and-rebuild for %s "
                        "(ingested for %.1fs with no sync_start)",
                        p.raw_file,
                        time.time() - (p.ingested_ts or time.time()),
                    )
                    try:
                        log_path = str(WATCHER_LOG)
                        log_fh = open(log_path, "ab")
                        subprocess.Popen(
                            [
                                "bash",
                                str(PROJECT_DIR / "scripts" / "sync-and-rebuild.sh"),
                            ],
                            stdout=log_fh,
                            stderr=log_fh,
                            cwd=str(PROJECT_DIR),
                            env={
                                **os.environ,
                                "SYNC_RUN_HINT": f"bot-failsafe:{p.raw_file}",
                            },
                            start_new_session=True,
                        )
                        log_fh.close()
                    except Exception as spawn_err:
                        log.exception(
                            "poller failsafe failed to spawn sync-and-rebuild: %s",
                            spawn_err,
                        )
        except Exception as e:
            log.exception("poll_sources error: %s", e)
        await asyncio.sleep(SOURCES_POLL_INTERVAL_SECONDS)


# ---------- Timeout sweeper ----------
async def sweep_pending(application: Application) -> None:
    bot = application.bot
    tracker: PendingTracker = application.bot_data["tracker"]
    recent_timeouts: deque = application.bot_data["recent_timeouts"]
    recent_resolved: dict = application.bot_data.setdefault("recent_resolved", {})
    while True:
        try:
            now = time.time()
            for p in await tracker.all():
                # Skip timeout for entries still waiting in the watcher queue.
                # The watcher processes files sequentially; counting from
                # created_ts would penalise entries behind a long-running file.
                if not p.started_ts:
                    continue
                age = now - p.started_ts
                if age <= PENDING_TIMEOUT_SECONDS:
                    continue

                if age > PENDING_HARD_TIMEOUT_SECONDS:
                    log.warning("hard timeout for pending %s (status=%s)", p.raw_file, p.status)
                    # Park so a late `[sync] deployed:` marker can still notify
                    # via the bridge's 3rd-tier lookup. In-memory only — bot
                    # restart drops parked entries (acceptable since the user
                    # has already received the "đang deploy" early-ack).
                    park_pending_for_late_marker(p, recent_resolved, now)
                    await tracker.remove(p.raw_file)
                    continue

                if p.timeout_notified_ts:
                    continue

                log.warning("timeout for pending %s (status=%s)", p.raw_file, p.status)
                minutes = PENDING_TIMEOUT_SECONDS // 60
                if p.status in ("ingested", "deployed"):
                    src_label = (
                        f"\nSource page: <code>{escape(p.new_source_file)}</code>"
                        if p.new_source_file else ""
                    )
                    msg_text = (
                        f"⏱️ Quá {minutes} phút đợi marker deploy cho "
                        f"<code>{escape(p.raw_file)}</code>.\n"
                        f"Status hiện tại: <b>{escape(p.status)}</b> — ingest đã xong, "
                        f"chỉ deploy không phản hồi.{src_label}\n\n"
                        f"Có thể wiki đã update rồi, kiểm tra: "
                        f"{escape(QUARTZ_PUBLIC_BASE_URL)}/\n"
                        f"Nếu cần ép chạy lại: <code>/retry {escape(p.raw_file)}</code>"
                    )
                else:
                    reason = format_pipeline_reason(p)
                    msg_text = (
                        f"⏱️ Quá {minutes} phút mà pipeline chưa xong cho "
                        f"<code>{escape(p.raw_file)}</code>.\n"
                        f"Last status: <b>{escape(p.status)}</b>.\n"
                        f"Lý do hiện tại: {escape(reason)}\n\n"
                        f"Bot sẽ tiếp tục nghe watcher để báo kết quả cuối.\n"
                        f"Lệnh nhanh:\n"
                        f"• Chạy lại: <code>/retry {escape(p.raw_file)}</code>\n"
                        f"• Hủy hẳn: <code>/cancel {escape(p.raw_file)}</code>"
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
                    await tracker.update(p.raw_file, timeout_notified_ts=now)
        except Exception as e:
            log.exception("sweeper error: %s", e)
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)


# ---------- App lifecycle ----------
async def _post_init(application: Application) -> None:
    application.bot_data["tracker"] = PendingTracker()
    # Restore pending entries from previous run (survives OOM kill / restart)
    await application.bot_data["tracker"].restore()
    # Files the sweep just timed out — `/retry` no-args picks from here first.
    application.bot_data["recent_timeouts"] = deque(maxlen=16)
    # Parking lot for raw_files whose tracker entry was hard-removed by
    # sweep_pending; a late `[sync] deployed:` marker can still notify the
    # user via the bridge's 3rd-tier lookup. FIFO-bounded at
    # RECENT_RESOLVED_MAXLEN, in-memory only (lost on restart by design).
    application.bot_data["recent_resolved"] = {}
    emit = await make_emitter(application)
    loop = asyncio.get_running_loop()
    application.bot_data["tail_task"] = loop.create_task(tail_watcher_log(emit))
    application.bot_data["poll_task"] = loop.create_task(poll_sources(application))
    application.bot_data["sweep_task"] = loop.create_task(sweep_pending(application))
    application.bot_data["heartbeat_task"] = loop.create_task(heartbeat_loop(application))
    log.info("post_init: tracker + tail + poll + sweep + heartbeat started")


async def _post_shutdown(application: Application) -> None:
    for key in ("tail_task", "poll_task", "sweep_task", "heartbeat_task"):
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
