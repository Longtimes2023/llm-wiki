# Deploy lên VPS

Chạy `telegram_bot.py` + `raw-watcher.sh` + `sync-and-rebuild.sh` trên 1 VPS Ubuntu nhỏ. Tắt máy local, bot vẫn xử lý URL.

## Yêu cầu VPS

- Ubuntu **22.04 hoặc 24.04** LTS, x86_64 hoặc ARM64.
- ≥ **1 vCPU, 1GB RAM, 10GB disk**. (Khuyến nghị 2GB RAM cho buffer khi build Quartz.)
- Có user thường (không phải root) với quyền `sudo`. Nếu chỉ có root, tạo user mới trước:
  ```bash
  adduser llmwiki
  usermod -aG sudo llmwiki
  su - llmwiki
  ```

VPS đề xuất: **Hetzner CX22** (~€4/tháng), **Contabo VPS S** (~$5/tháng), **Oracle Cloud Free Tier** (free vĩnh viễn nếu được approve).

## Setup (1 lần, ~5 phút)

### 1. SSH vào VPS, clone repo

```bash
cd ~
git clone https://github.com/<your-username>/llm-wiki.git
cd llm-wiki
```

### 2. Chạy installer

```bash
bash deploy/vps-setup.sh
```

Lần đầu sẽ:
- Cài system deps (`inotify-tools`, `rsync`, `python3.13`, …)
- Cài `uv`, Node.js 22, `@anthropic-ai/claude-code` CLI
- Chạy `uv sync`
- Tạo file `.env` từ `.env.example` rồi **DỪNG** để user điền giá trị

### 3. Điền `.env`

```bash
nano .env
```

Bắt buộc:
- `ANTHROPIC_AUTH_TOKEN` — Claude API key (hoặc DeepSeek key nếu dùng compat)
- `ANTHROPIC_BASE_URL` — `https://api.anthropic.com` (hoặc DeepSeek)
- `MODEL` — `claude-sonnet-4-20250514` (hoặc model đang dùng)
- `TELEGRAM_BOT_TOKEN` — token từ BotFather
- `TELEGRAM_ALLOWED_CHAT_ID` — chat_id của bạn (xem step 4 nếu chưa biết)
- `QUARTZ_PUBLIC_BASE_URL` — URL Cloudflare Pages, vd `https://llm-wiki-ai.pages.dev`

Optional (nếu muốn VPS tự deploy Quartz lên Cloudflare Pages mỗi lần ingest):
- `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_PAGES_PROJECT`

Nếu **đã setup Cloudflare Pages auto-build từ Git** thì 3 var Cloudflare ở trên KHÔNG cần — VPS chỉ cần `git push`, Pages tự build.

### 4. Lấy `TELEGRAM_ALLOWED_CHAT_ID` (skip nếu đã có)

```bash
uv run python telegram_bot.py --getchatid
```

Mở Telegram → chat với bot → script in `chat_id=...` rồi exit. Copy số đó vào `.env`.

### 5. Chạy lại installer

```bash
bash deploy/vps-setup.sh
```

Lần này sẽ render systemd units, bật lingering (services chạy 24/7 không cần login), start cả 2 services.

Kết thúc sẽ hiển thị status. Cả 2 đều phải `active (running)`.

## Test

Mở Telegram chat với bot, gửi 1 URL bất kỳ:

```
You:  https://karpathy.bearblog.dev/llm-os/
Bot:  🔄 Đã nhận URL — đang đẩy vào pipeline...
       (1-3 phút)
Bot:  ✅ Đã ingest + deploy xong!
       Wiki: https://your-site.pages.dev/wiki/sources/...
```

## Quản lý service

```bash
# Status
systemctl --user status llm-wiki-telegram-bot
systemctl --user status llm-wiki-watcher

# Restart
systemctl --user restart llm-wiki-telegram-bot
systemctl --user restart llm-wiki-watcher

# Stop
systemctl --user stop llm-wiki-telegram-bot llm-wiki-watcher

# Disable (không auto-start nữa)
systemctl --user disable llm-wiki-telegram-bot llm-wiki-watcher

# Logs realtime
journalctl --user -u llm-wiki-telegram-bot -f
journalctl --user -u llm-wiki-watcher -f

# Hoặc tail file log
tail -f scripts/telegram_bot.log
tail -f scripts/watcher.log
```

## Update code từ GitHub

```bash
cd ~/llm-wiki
git pull
uv sync   # nếu deps thay đổi
systemctl --user restart llm-wiki-telegram-bot llm-wiki-watcher
```

## Troubleshooting

### Service `failed` ngay sau start

```bash
journalctl --user -u llm-wiki-telegram-bot -n 50 --no-pager
```

Lỗi thường gặp:
- `TELEGRAM_BOT_TOKEN missing in .env` → chưa điền `.env` hoặc sai path.
- `ModuleNotFoundError: claude_agent_sdk` → `uv sync` chưa chạy thành công, chạy lại trong `~/llm-wiki`.
- `Claude Code not found` → `claude` CLI chưa cài hoặc không trong `PATH` của service. Edit `~/.config/systemd/user/llm-wiki-watcher.service`, kiểm tra dòng `Environment=PATH=...` có chứa `~/.npm-global/bin` không.

### Bot không reply gì

- Verify token: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Verify chat_id đúng (gửi message từ đúng account đã allowlist).
- Tail bot log: `tail -f scripts/telegram_bot.log`.

### Pipeline ingest fail

Tail watcher log: `tail -f scripts/watcher.log`. Tìm dòng `INGEST FAILED ...` để xem nguyên nhân (API error, exit code, sources count unchanged…).

### Out of memory khi Quartz build

VPS 1GB RAM có thể không đủ. 2 cách:
- Upgrade lên VPS 2GB RAM.
- Bỏ Quartz build trên VPS, dùng Cloudflare Pages auto-build từ Git: comment phần `npx quartz build` + `wrangler deploy` trong `scripts/sync-and-rebuild.sh`, chỉ giữ rsync + git push.

### Disk full

```bash
du -sh ~/llm-wiki/quartz/.quartz-cache ~/llm-wiki/quartz/public
rm -rf ~/llm-wiki/quartz/.quartz-cache  # safe, sẽ tự rebuild
```

## So sánh với các mode khác

| | Local WSL | VPS (mode này) | GitHub Actions + Cloudflare |
|---|---|---|---|
| Cần máy tắt được | ❌ | ✅ | ✅ |
| Setup time | nhanh | ~10 phút | ~30 phút (nhiều secrets) |
| Chi phí | $0 | $5/tháng | $0 |
| Latency ack | < 1s | < 1s | < 1s (qua Worker) |
| Phụ thuộc | WSL2 | VPS provider | Cloudflare + GitHub |
| Code path | giống local | giống local | khác (workflow YAML) |

VPS = trade-off đơn giản nhất sau local: y chang code đang chạy, chỉ đổi host.
