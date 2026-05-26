"""Stdlib unittest coverage for the Telegram bot milestone notifier and
late-marker recovery — closes the Phase-2 silent-wait gap after Cloudflare
deploys (see /home/steven/.claude/plans/melodic-fluttering-aurora.md).

Run directly:
    uv run python scripts/tests/test_telegram_milestone.py -v

Or via discovery:
    uv run python -m unittest discover -s scripts/tests -p 'test_*.py' -v
"""
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import telegram_bot  # noqa: E402
from telegram_bot import (  # noqa: E402
    Pending,
    PendingTracker,
    RECENT_RESOLVED_MAXLEN,
    notify_milestone,
    park_pending_for_late_marker,
)


def _make_pending(raw_file: str = "2026-05-26-test.md", **overrides) -> Pending:
    fields = dict(
        raw_file=raw_file,
        chat_id=12345,
        msg_id=67890,
        ack_msg_id=None,
        created_ts=time.time(),
    )
    fields.update(overrides)
    return Pending(**fields)


class _StateFilePatchMixin:
    """Per-test redirect of telegram_bot.STATE_FILE so PendingTracker._persist
    writes to a throwaway path instead of scripts/telegram_bot.state."""

    def setUp(self) -> None:  # type: ignore[override]
        super().setUp()
        self._tmpdir = tempfile.TemporaryDirectory()
        self._state_patcher = patch.object(
            telegram_bot,
            "STATE_FILE",
            Path(self._tmpdir.name) / "telegram_bot.state",
        )
        self._state_patcher.start()

    def tearDown(self) -> None:  # type: ignore[override]
        self._state_patcher.stop()
        self._tmpdir.cleanup()
        super().tearDown()


class MilestoneNotifierTests(_StateFilePatchMixin, unittest.IsolatedAsyncioTestCase):
    """TC-A, TC-B, TC-E — direct notify_milestone behavior."""

    async def _tracker_with(self, p: Pending) -> PendingTracker:
        t = PendingTracker()
        await t.add(p)
        return t

    async def test_a_first_ingested_notify_sends(self) -> None:
        p = _make_pending(new_source_file="wiki/sources/foo.md")
        tracker = await self._tracker_with(p)
        bot = AsyncMock()

        sent = await notify_milestone(bot, p, "ingested", tracker)

        self.assertTrue(sent)
        bot.send_message.assert_awaited_once()
        kwargs = bot.send_message.await_args.kwargs
        self.assertEqual(kwargs["chat_id"], 12345)
        self.assertEqual(kwargs["reply_to_message_id"], 67890)
        self.assertIn("Đã ingest xong", kwargs["text"])
        self.assertIn("wiki/sources/foo.md", kwargs["text"])
        p2 = await tracker.get(p.raw_file)
        self.assertEqual(p2.notified_phases, ["ingested"])

    async def test_b_double_ingested_is_idempotent(self) -> None:
        # Pre-seed notified_phases — simulates poller having already notified.
        p = _make_pending(
            new_source_file="wiki/sources/foo.md",
            notified_phases=["ingested"],
        )
        tracker = await self._tracker_with(p)
        bot = AsyncMock()

        sent = await notify_milestone(bot, p, "ingested", tracker)

        self.assertFalse(sent)
        bot.send_message.assert_not_awaited()
        p2 = await tracker.get(p.raw_file)
        self.assertEqual(p2.notified_phases, ["ingested"])

    async def test_e_unknown_phase_is_safe_no_op(self) -> None:
        p = _make_pending()
        tracker = await self._tracker_with(p)
        bot = AsyncMock()

        sent = await notify_milestone(bot, p, "frobnicated", tracker)

        self.assertFalse(sent)
        bot.send_message.assert_not_awaited()
        p2 = await tracker.get(p.raw_file)
        self.assertEqual(p2.notified_phases, [])

    async def test_g_sync_failed_message_includes_reason(self) -> None:
        p = _make_pending(new_source_file="wiki/sources/foo.md", status="ingested")
        tracker = await self._tracker_with(p)
        bot = AsyncMock()

        sent = await notify_milestone(
            bot, p, "sync_failed", tracker,
            extra={"reason": "Quartz build FAILED after 3 quarantine attempts"},
        )

        self.assertTrue(sent)
        bot.send_message.assert_awaited_once()
        text = bot.send_message.await_args.kwargs["text"]
        self.assertIn("Sync", text)
        self.assertIn("thất bại", text)
        self.assertIn("Quartz build FAILED", text)
        p2 = await tracker.get(p.raw_file)
        self.assertEqual(p2.notified_phases, ["sync_failed"])

    async def test_h_double_sync_failed_is_idempotent(self) -> None:
        p = _make_pending(status="ingested", notified_phases=["sync_failed"])
        tracker = await self._tracker_with(p)
        bot = AsyncMock()

        sent = await notify_milestone(
            bot, p, "sync_failed", tracker, extra={"reason": "..."}
        )

        self.assertFalse(sent)
        bot.send_message.assert_not_awaited()


class HeartbeatPhaseTests(unittest.TestCase):
    """TC-J — _format_progress_line must NOT show stale watcher "retry"
    phase when poller has already flipped status to ingested. Attempt
    counter must also be hidden because the watcher loop is no longer
    authoritative for an ingested entry."""

    def test_j_progress_line_overrides_stale_retry_phase_when_ingested(self) -> None:
        from telegram_bot import _format_progress_line
        p = _make_pending(
            status="ingested",
            phase="retry (api/connection error: API Error 400)",
            attempt=3,
            max_attempts=3,
            new_source_file="wiki/sources/foo.md",
        )
        line = _format_progress_line(p, p.created_ts + 5820)  # 97 minutes
        # The stale watcher attempt/phase must NOT appear.
        self.assertNotIn("retry", line.lower())
        self.assertNotIn("api error", line.lower())
        self.assertNotIn("attempt 3/3", line)
        # Some sync/deploy progress wording must appear instead.
        self.assertTrue(
            any(token in line.lower() for token in ("sync", "deploy")),
            f"expected sync/deploy progress in ingested line, got: {line!r}",
        )
        # Elapsed time still shown.
        self.assertIn("⏳", line)

    def test_j2_queued_status_keeps_watcher_phase(self) -> None:
        from telegram_bot import _format_progress_line
        p = _make_pending(
            status="queued",
            phase="retry (api/connection error)",
            attempt=2,
            max_attempts=3,
        )
        line = _format_progress_line(p, p.created_ts + 100)
        # For queued status, watcher phase + attempt remain authoritative.
        self.assertIn("attempt 2/3", line)
        self.assertIn("retry", line.lower())


class PollerFailsafeTests(unittest.TestCase):
    """TC-K, TC-L — should_fire_sync_failsafe controls when the bot's poller
    auto-triggers sync-and-rebuild.sh in case the watcher misclassified the
    ingest and never called sync."""

    def test_k_fires_when_ingested_120s_with_no_sync_start(self) -> None:
        from telegram_bot import should_fire_sync_failsafe, POLLER_SYNC_FAILSAFE_SECONDS
        now = 10_000.0
        p = _make_pending(
            status="ingested",
            ingested_ts=now - (POLLER_SYNC_FAILSAFE_SECONDS + 10),
            last_ingest_event="ok_via_poll",
            sync_failsafe_fired=False,
            last_deploy_url=None,
        )
        self.assertTrue(should_fire_sync_failsafe(p, now))

    def test_l_does_not_fire_when_already_fired(self) -> None:
        from telegram_bot import should_fire_sync_failsafe, POLLER_SYNC_FAILSAFE_SECONDS
        now = 10_000.0
        p = _make_pending(
            status="ingested",
            ingested_ts=now - (POLLER_SYNC_FAILSAFE_SECONDS + 10),
            last_ingest_event="ok_via_poll",
            sync_failsafe_fired=True,
            last_deploy_url=None,
        )
        self.assertFalse(should_fire_sync_failsafe(p, now))

    def test_l2_does_not_fire_when_too_soon(self) -> None:
        from telegram_bot import should_fire_sync_failsafe, POLLER_SYNC_FAILSAFE_SECONDS
        now = 10_000.0
        p = _make_pending(
            status="ingested",
            ingested_ts=now - 30,  # only 30s
            last_ingest_event="ok_via_poll",
            sync_failsafe_fired=False,
            last_deploy_url=None,
        )
        self.assertFalse(should_fire_sync_failsafe(p, now))

    def test_l3_does_not_fire_when_sync_started(self) -> None:
        from telegram_bot import should_fire_sync_failsafe, POLLER_SYNC_FAILSAFE_SECONDS
        now = 10_000.0
        p = _make_pending(
            status="ingested",
            ingested_ts=now - (POLLER_SYNC_FAILSAFE_SECONDS + 10),
            last_ingest_event="sync_start",
            sync_failsafe_fired=False,
            last_deploy_url=None,
        )
        self.assertFalse(should_fire_sync_failsafe(p, now))

    def test_l4_does_not_fire_when_deployed(self) -> None:
        from telegram_bot import should_fire_sync_failsafe, POLLER_SYNC_FAILSAFE_SECONDS
        now = 10_000.0
        p = _make_pending(
            status="ingested",
            ingested_ts=now - (POLLER_SYNC_FAILSAFE_SECONDS + 10),
            last_ingest_event="ok_via_poll",
            sync_failsafe_fired=False,
            last_deploy_url="https://x.pages.dev",
        )
        self.assertFalse(should_fire_sync_failsafe(p, now))

    def test_l5_does_not_fire_when_status_queued(self) -> None:
        from telegram_bot import should_fire_sync_failsafe, POLLER_SYNC_FAILSAFE_SECONDS
        now = 10_000.0
        p = _make_pending(
            status="queued",
            ingested_ts=None,
            last_ingest_event=None,
            sync_failsafe_fired=False,
        )
        self.assertFalse(should_fire_sync_failsafe(p, now))


class ParkingHelperTests(unittest.TestCase):
    """TC-C, TC-F — park_pending_for_late_marker contract + FIFO eviction.
    Synchronous; the helper does not touch the tracker."""

    def test_c_park_populates_dict_with_expected_fields(self) -> None:
        p = _make_pending(
            raw_file="2026-05-26-tg-test.md",
            status="ingested",
            new_source_file="wiki/sources/abc.md",
        )
        recent_resolved: dict = {}
        now = time.time()

        parked = park_pending_for_late_marker(p, recent_resolved, now)

        self.assertTrue(parked)
        entry = recent_resolved[p.raw_file]
        self.assertEqual(entry["raw_file"], p.raw_file)
        self.assertEqual(entry["chat_id"], p.chat_id)
        self.assertEqual(entry["msg_id"], p.msg_id)
        self.assertEqual(entry["new_source_file"], "wiki/sources/abc.md")
        self.assertEqual(entry["created_ts"], p.created_ts)
        self.assertEqual(entry["parked_ts"], now)

    def test_c2_park_refuses_already_deployed(self) -> None:
        p = _make_pending(status="deployed", last_deploy_url="https://x.pages.dev")
        recent_resolved: dict = {}

        parked = park_pending_for_late_marker(p, recent_resolved, time.time())

        self.assertFalse(parked)
        self.assertEqual(recent_resolved, {})

    def test_f_park_fifo_evicts_at_maxlen(self) -> None:
        recent_resolved: dict = {}
        now = time.time()
        # Fill MAXLEN + 5 entries; first 5 should be evicted in insertion order.
        for i in range(RECENT_RESOLVED_MAXLEN + 5):
            p = _make_pending(raw_file=f"raw-{i:04d}.md", status="ingested")
            park_pending_for_late_marker(p, recent_resolved, now + i)

        self.assertEqual(len(recent_resolved), RECENT_RESOLVED_MAXLEN)
        for i in range(5):
            self.assertNotIn(f"raw-{i:04d}.md", recent_resolved)
        for i in range(5, RECENT_RESOLVED_MAXLEN + 5):
            self.assertIn(f"raw-{i:04d}.md", recent_resolved)


class LateMarkerRecoveryTests(_StateFilePatchMixin, unittest.IsolatedAsyncioTestCase):
    """TC-D — full round trip mimicking the bridge's 3rd-tier lookup:
    park → tracker drains → reconstruct Pending → notify deployed."""

    async def test_d_late_deployed_uses_parked_entry(self) -> None:
        original = _make_pending(
            raw_file="2026-05-26-late.md",
            status="ingested",
            new_source_file="wiki/sources/late.md",
        )

        # 1. Hard-timeout park step
        recent_resolved: dict = {}
        park_pending_for_late_marker(original, recent_resolved, time.time())
        self.assertIn(original.raw_file, recent_resolved)

        # 2. Bridge's 3rd-tier reconstruction (mirrors make_emitter deployed branch)
        parked = recent_resolved[original.raw_file]
        reconstructed = Pending(
            raw_file=parked["raw_file"],
            chat_id=parked["chat_id"],
            msg_id=parked["msg_id"],
            ack_msg_id=None,
            created_ts=parked["created_ts"],
            new_source_file=parked.get("new_source_file"),
            status="ingested",
            notified_phases=[],
        )

        # 3. notify_milestone called against an empty tracker — tracker.update
        # returns None silently, but the user-facing send_message still fires.
        tracker = PendingTracker()
        bot = AsyncMock()
        sent = await notify_milestone(
            bot, reconstructed, "deployed", tracker,
            extra={"url": "https://x.pages.dev"},
        )

        self.assertTrue(sent)
        bot.send_message.assert_awaited_once()
        kwargs = bot.send_message.await_args.kwargs
        self.assertEqual(kwargs["chat_id"], 12345)
        self.assertEqual(kwargs["reply_to_message_id"], 67890)
        self.assertIn("Đã ingest + deploy xong", kwargs["text"])
        self.assertIn("https://x.pages.dev", kwargs["text"])
        self.assertIn("wiki/sources/late.md", kwargs["text"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
