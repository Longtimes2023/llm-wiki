# Cloudflare Worker — Telegram webhook receiver

Webhook nhận message Telegram → trigger `repository_dispatch` qua GitHub API → workflow `ingest-url.yml` chạy ingest pipeline.

Worker này là phần **always-on** thay cho `telegram_bot.py` long-poll. Không cần WSL local mở.

## Một lần setup

### 1. Cài wrangler + login

```bash
cd cloudflare-worker
npm install -g wrangler          # hoặc: npx wrangler ...
wrangler login
```

### 2. Set secrets

Cần chuẩn bị trước:

| Secret | Lấy ở đâu |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather (`/newbot` hoặc dùng bot có sẵn) |
| `ALLOWED_CHAT_ID` | Chat ID của user duy nhất được phép. Lấy bằng cách chat với bot rồi xem `https://api.telegram.org/bot<TOKEN>/getUpdates`, hoặc dùng `python telegram_bot.py --getchatid` ở local. |
| `WEBHOOK_SECRET` | Bạn tự tạo random string 32+ ký tự. Telegram sẽ đính kèm header này khi gọi worker — dùng để chặn request giả mạo. `python -c 'import secrets; print(secrets.token_urlsafe(32))'` |
| `GITHUB_DISPATCH_TOKEN` | GitHub Personal Access Token (Classic, scope `repo`) hoặc Fine-grained PAT với `Contents: read+write` + `Actions: read+write` cho repo `liangdabiao/llm-wiki`. |
| `GITHUB_REPO` | `liangdabiao/llm-wiki` |

Set lần lượt:

```bash
wrangler secret put TELEGRAM_BOT_TOKEN
wrangler secret put ALLOWED_CHAT_ID
wrangler secret put WEBHOOK_SECRET
wrangler secret put GITHUB_DISPATCH_TOKEN
wrangler secret put GITHUB_REPO
```

### 3. Deploy worker

```bash
wrangler deploy
```

Sẽ in ra URL dạng `https://llm-wiki-tg-webhook.<your-subdomain>.workers.dev`. Note URL này.

### 4. Đăng ký webhook với Telegram

Thay `<TOKEN>`, `<WORKER_URL>`, `<WEBHOOK_SECRET>`:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=<WORKER_URL>/tg" \
  -d "secret_token=<WEBHOOK_SECRET>" \
  -d "allowed_updates=[\"message\"]"
```

Verify:

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

`url` phải khớp `<WORKER_URL>/tg`, `last_error_message` phải rỗng.

### 5. GitHub Actions secrets

Vào `Settings → Secrets and variables → Actions` của repo, thêm:

| Secret | Giá trị |
|---|---|
| `ANTHROPIC_AUTH_TOKEN` | Anthropic key (hoặc DeepSeek key nếu dùng compat endpoint) |
| `ANTHROPIC_BASE_URL` | `https://api.anthropic.com` (hoặc DeepSeek endpoint) |
| `MODEL` | `claude-sonnet-4-20250514` (hoặc model bạn đang dùng) |
| `TELEGRAM_BOT_TOKEN` | Cùng token với worker |
| `QUARTZ_PUBLIC_BASE_URL` | URL Cloudflare Pages, vd `https://llm-wiki-ai.pages.dev` |
| `CLOUDFLARE_PAGES_PROJECT` | (optional) Tên project Pages, dùng để compute URL fallback |

### 6. Bật Cloudflare Pages auto-build từ Git

Pages dashboard → project hiện có → Settings → Builds & deployments → Connect to Git → chọn repo `liangdabiao/llm-wiki` branch `main`.

Build settings:
- Framework: **None**
- Build command: `cd quartz && rm -rf public .quartz-cache && npx quartz build`
- Build output: `quartz/public`
- Root directory: (empty)

## Test

1. Gửi 1 URL bất kỳ vào chat bot trên Telegram.
2. Worker reply ngay "🔄 Đã nhận..." (< 2s).
3. Mở GitHub repo → tab Actions → thấy run `Ingest URL` mới.
4. Sau 2-6 phút workflow xong, push commit `ingest: <url>` lên main.
5. Cloudflare Pages tự build (xem Pages dashboard).
6. Bot reply final với link wiki.

## Troubleshooting

- **403 từ worker**: header `X-Telegram-Bot-Api-Secret-Token` không khớp `WEBHOOK_SECRET`. Re-run `setWebhook` với đúng secret.
- **GitHub dispatch 401**: PAT hết hạn hoặc không đủ scope. Tạo PAT mới với scope `repo` hoặc fine-grained `Contents: write` + `Actions: write`.
- **Workflow chạy nhưng `ANTHROPIC_AUTH_TOKEN` rỗng**: chưa set secret ở GitHub Actions (khác với secret của worker).
- **Worker logs**: `wrangler tail` để xem real-time.

## Local dev

Chỉ cần test logic worker:

```bash
wrangler dev
# expose qua ngrok / cloudflared tunnel để Telegram gọi vào, rồi setWebhook tạm về tunnel URL
```
