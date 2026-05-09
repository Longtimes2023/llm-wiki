"""Telegram sendMessage helper for GitHub Actions ingest workflow.

Called at the end (success and failure paths) of .github/workflows/ingest-url.yml
to reply back to the user who sent the URL via the Cloudflare Worker webhook.

Usage:
  python scripts/notify_telegram.py --status ok \
      --chat-id "$CHAT_ID" --reply-to "$MSG_ID" \
      --url "https://wiki.example/wiki/sources/foo"

  python scripts/notify_telegram.py --status fail \
      --chat-id "$CHAT_ID" --reply-to "$MSG_ID" \
      --reason "ingest exit 1, see workflow run"

Env:
  TELEGRAM_BOT_TOKEN  required
  GITHUB_RUN_URL      optional, link to the workflow run (added to fail message)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request


API = "https://api.telegram.org/bot{token}/sendMessage"


def send(token: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API.format(token=token),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--status", choices=["ok", "fail"], required=True)
    p.add_argument("--chat-id", required=True)
    p.add_argument("--reply-to", default="")
    p.add_argument("--url", default="")
    p.add_argument("--reason", default="")
    p.add_argument("--site", default="", help="Optional site root URL to append")
    args = p.parse_args()

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("TELEGRAM_BOT_TOKEN missing in env", file=sys.stderr)
        return 2

    run_url = os.environ.get("GITHUB_RUN_URL", "").strip()

    if args.status == "ok":
        lines = ["✅ Đã ingest + deploy xong!"]
        if args.url:
            lines.append(f"Wiki: {args.url}")
        if args.site:
            lines.append(f"(Site: {args.site})")
        text = "\n".join(lines)
    else:
        lines = ["❌ Pipeline thất bại."]
        if args.reason:
            lines.append(f"Lý do: {args.reason}")
        if run_url:
            lines.append(f"Workflow: {run_url}")
        text = "\n".join(lines)

    payload: dict = {
        "chat_id": args.chat_id,
        "text": text,
        "disable_web_page_preview": False,
    }
    if args.reply_to:
        try:
            payload["reply_to_message_id"] = int(args.reply_to)
        except ValueError:
            pass

    try:
        result = send(token, payload)
    except Exception as e:
        print(f"sendMessage failed: {e}", file=sys.stderr)
        return 1

    if not result.get("ok"):
        print(f"Telegram API error: {json.dumps(result)}", file=sys.stderr)
        return 1

    print(f"sent: {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
