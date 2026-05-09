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
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiofiles
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
from providers.loader import list_providers, get_active, set_active

# ---------- Config ----------
PROJECT_DIR = Path(__file__).resolve().parent
WIKI_DIR = PROJECT_DIR / "ai-wiki"
RAW_ARTICLES_DIR = WIKI_DIR / "raw" / "articles"
SOURCES_DIR = WIKI_DIR / "wiki" / "sources"
WATCHER_LOG = PROJECT_DIR / "scripts" / "watcher.log"
STATE_FILE = PROJECT_DIR / "scripts" / "telegram_bot.state"
METRICS_FILE = PROJECT_DIR / "scripts" / "ingest_metrics.jsonl"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_ALLOWED_CHAT_ID = os.getenv("TELEGRAM_ALLOWED_CHAT_ID", "").strip()
QUARTZ_PUBLIC_BASE_URL = os.getenv(
    "QUARTZ_PUBLIC_BASE_URL", "https://llm-wiki-ai.pages.dev"
).rstrip("/")

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
    if not url:
        await msg.reply_text("❌ Không tìm thấy URL hợp lệ. Gửi 1 link http(s) nhé.")
        return

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
            src_url = (
                quartz_url_for_source(src_name) if src_name
                else f"{QUARTZ_PUBLIC_BASE_URL}/"
            )
            log.info("dedup: url already ingested via raw=%s, source=%s", existing.name, src_name)
            await msg.reply_text(
                f"♻️ URL này đã ingest trước đó.\n"
                f"Wiki: {src_url}\n"
                f"<i>Raw: {existing.name}</i>\n\n"
                f"Để A/B test với provider khác, gửi: <code>{url} @&lt;provider&gt;</code>",
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
        avail_str = ", ".join(available) if available else "(no profiles in providers/)"
        await msg.reply_text(
            f"<b>Active provider:</b> {active}\n"
            f"<b>Available:</b> {avail_str}\n\n"
            f"Switch: <code>/provider &lt;name&gt;</code>\n"
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
            try:
                await bot.send_message(
                    chat_id=p.chat_id,
                    reply_to_message_id=p.msg_id,
                    text=(
                        f"❌ Pipeline thất bại sau nhiều lần thử cho file "
                        f"<code>{filename}</code>.\nXem <code>scripts/watcher.log</code>."
                    ),
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
    while True:
        try:
            now = time.time()
            for p in await tracker.all():
                if now - p.created_ts > PENDING_TIMEOUT_SECONDS:
                    log.warning("timeout for pending %s (status=%s)", p.raw_file, p.status)
                    try:
                        await bot.send_message(
                            chat_id=p.chat_id,
                            reply_to_message_id=p.msg_id,
                            text=(
                                f"⏱️ Quá {PENDING_TIMEOUT_SECONDS // 60} phút mà pipeline "
                                f"chưa xong cho <code>{p.raw_file}</code>.\n"
                                f"Last status: <b>{p.status}</b>. "
                                f"Xem <code>scripts/watcher.log</code> để debug."
                            ),
                            parse_mode="HTML",
                        )
                    finally:
                        await tracker.remove(p.raw_file)
        except Exception as e:
            log.exception("sweeper error: %s", e)
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)


# ---------- App lifecycle ----------
async def _post_init(application: Application) -> None:
    application.bot_data["tracker"] = PendingTracker()
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
