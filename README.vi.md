**Language / 语言 / Ngôn ngữ**: [中文](README.md) · [English](README.en.md) · **Tiếng Việt**

---

# LLM Wiki — Hệ thống kiến thức cá nhân chạy bằng AI

Dựa trên phương pháp luận [Karpathy llm-wiki](https://github.com/karpathy/llm-wiki), dự án này dùng AI để liên tục xây dựng và bảo trì kho kiến thức cá nhân của bạn. Hỗ trợ nhiều nguồn nguyên liệu (web, Twitter/X, WeChat, Xiaohongshu, Zhihu, YouTube, PDF, file local) và tự động tổ chức thành wiki có cấu trúc, sau đó publish qua Quartz thành site wiki tĩnh. Đồng thời gói lại năng lực llm-wiki qua `claude_agent_sdk` để gọi Claude Agent, expose API cho service bên ngoài.

Claude Agent SDK + LLM-wiki — agentic RAG mạnh nhất hiện tại. Repo này minh hoạ cách llm-wiki của mình được biến thành agentic RAG qua Claude Agent SDK, hiệu quả rất tốt. Các file lõi: `7_wiki_writer.py`, `wiki_writer_api.py`.

## 🤔 LLM-wiki là gì?

LLM Wiki: dùng mô hình ngôn ngữ lớn để tự động sắp xếp kiến thức rời rạc của bạn thành một cuốn "bách khoa toàn thư cá nhân" có cấu trúc. Cách truyền thống: mỗi lần bạn hỏi AI một câu, AI phải đọc lại toàn bộ tài liệu, tìm phần liên quan rồi trả lời (đó là RAG — retrieval-augmented generation). Giống như mỗi lần hỏi người thủ thư một câu thì họ phải lật lại toàn bộ thư viện. Karpathy nói: làm vậy quá ngu. Cách đúng là: cho AI làm "trình biên dịch tri thức" — đọc một lần toàn bộ tài liệu, sắp xếp thành cuốn bách khoa có cấu trúc, liên kết chéo rõ ràng. Sau đó bạn hỏi, AI chỉ lật cuốn bách khoa đó là xong.

Pipeline RAG truyền thống đầy đủ: ingest → chunk → index → retrieve → rerank → prompt-pack → generate → cite. Karpathy đúng là sâu sắc thật — những khái niệm AI quan trọng nhất vài năm qua đều do anh ấy tổng kết, trông đơn giản nhưng chạm đến bản chất. llm-wiki bị đánh giá thấp một cách nghiêm trọng — nó chính là cái gốc của việc làm AI. Format wiki rất quan trọng — AI dùng cấu trúc đó để tổ chức toàn bộ tri thức. Nó giải quyết trọn vẹn vấn đề RAG. Mình đã ngưng dùng RAG vì đây mới là câu trả lời. Ngoài RAG, nó còn có thể one-click sinh ra site wiki — một kho kiến thức thực sự. May là mình đã test nhiều cách và tìm ra món hay này. Dựa trên nó, có thể làm rất nhiều project mạnh — hiểu càng sâu thì sinh càng sâu. Đó là cách làm AI. Thư mục `wiki/` trong project là nơi chứa nội dung wiki; tạm thời mình để vài bài open-source của Yupi (鱼皮) để test hiệu quả.

Project tham khảo:
- https://github.com/kenneth-liao/claude-agent-sdk-intro
- https://github.com/sdyckjq-lab/llm-wiki-skill

Cảm ơn đặc biệt: https://linux.do/

## Ba năng lực cốt lõi

### 1. LLM Wiki Skill — xây dựng knowledge base

Tận dụng cơ chế Skill của Claude Code, để AI tự động thực hiện thu thập, sắp xếp, kiểm soát chất lượng và bảo trì knowledge base.

**Workflow được hỗ trợ:**

| Workflow | Mô tả |
|----------|-------|
| `init` | Khởi tạo knowledge base mới, tạo cấu trúc thư mục và cấu hình |
| `ingest` | Tiêu hoá 1 nguồn đơn (URL / file / text dán), tự động trích thực thể và chủ đề |
| `batch-ingest` | Xử lý batch nhiều file (.md / .txt / .pdf / .html) |
| `query` | Truy vấn knowledge base, trả lời tổng hợp kèm trích nguồn |
| `digest` | Report tổng hợp sâu, phân tích cross-source theo chủ đề cụ thể |
| `lint` | Health check: trang mồ côi, link gãy, chất lượng nội dung |
| `status` | Xem trạng thái: phân bố nguồn, thống kê trang, hoạt động gần đây |
| `graph` | Sinh Mermaid knowledge graph, visualize quan hệ giữa thực thể |

**Nguồn nguyên liệu hỗ trợ:**

| Loại | Cách trích xuất |
|------|----------------|
| Bài web | `baoyu-url-to-markdown` |
| X / Twitter | `baoyu-url-to-markdown` |
| WeChat | `wechat-article-to-markdown` |
| YouTube | `youtube-transcript` |
| Zhihu | `baoyu-url-to-markdown` |
| PDF | đọc trực tiếp |
| File local (.md / .txt) | đọc trực tiếp |

**Cấu trúc thư mục knowledge base:**

```
ai-wiki/
├── .wiki-schema.md      # Config và tiêu chuẩn chất lượng
├── index.md             # Index nội dung
├── log.md               # Operation log
├── overview.md          # Quick navigation
├── raw/                 # Nguyên liệu thô
│   ├── articles/        # Bài web
│   ├── tweets/          # Tweet
│   ├── wechat/          # Bài WeChat
│   ├── xiaohongshu/     # Xiaohongshu
│   ├── zhihu/           # Zhihu
│   ├── pdfs/            # PDF
│   └── notes/           # Note và text
└── wiki/                # Nội dung wiki có cấu trúc
    ├── entities/        # Trang thực thể (tool, khái niệm, người)
    ├── topics/          # Trang chủ đề (lĩnh vực nghiên cứu)
    ├── sources/         # Tóm tắt nguồn
    ├── comparisons/     # Phân tích so sánh
    └── synthesis/       # Phân tích tổng hợp
```

**Bước sử dụng chi tiết:**

❯ ai-guide là nguyên liệu thu thập về, yêu cầu là dùng llm-wiki skill để phân tích và sắp xếp thành wiki — vui lòng hoàn thành.

![](./图片1.png)

### 2. Quartz Wiki Skill — deploy site tĩnh

Publish knowledge base sinh ra thành site tĩnh đẹp qua [Quartz v4](https://quartz.jzhao.xyz/).

**Tính năng:**
- Bi-directional link và graph quan hệ
- Full-text search
- Responsive design, hỗ trợ light / dark theme
- Deploy được lên Cloudflare Pages / Vercel / GitHub Pages

**File config:** `quartz/quartz.config.ts`

```bash
# Preview local
cd quartz
npx quartz build --serve

# Build production
npx quartz build

# Deploy lên Cloudflare Pages
npx wrangler pages deploy public
```

**Cách dùng skill trong Claude Code:**

❯ Vui lòng dùng quartz-wiki skill để biến ai-wiki thành site Quartz.

URL deploy hiện tại: `http://wikilego.liangdabiao.com/`

![](./图片2.png)

### 3. Claude Agent SDK — service đối ngoại

Đóng gói năng lực knowledge base thành AI Agent gọi được bằng code, qua [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/python).

#### CLI mode (`7_wiki_writer.py`)

Agent tự nhận diện intent của user, gọi llm-wiki-skill để thao tác knowledge base (query, tiêu hoá nguyên liệu, sinh bài, v.v.).

```bash
# Gửi 1 request
.\.venv\Scripts\python.exe -B 7_wiki_writer.py -r "Viết cho mình 1 bài tổng hợp về AI Agent"

# Mode tương tác (đối thoại liên tục)
.\.venv\Scripts\python.exe -B 7_wiki_writer.py -i
```

#### API mode (`wiki_writer_api.py`)

HTTP service dựa trên FastAPI, hỗ trợ SSE streaming và sync JSON response.

```bash
# Start service
.\.venv\Scripts\python.exe -B wiki_writer_api.py

# Hoặc dùng uvicorn (hỗ trợ hot reload)
.\.venv\Scripts\uvicorn.exe wiki_writer_api:app --host 0.0.0.0 --port 8000 --reload
```

**Endpoint API:**

| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/health` | Health check |
| POST | `/api/v1/wiki/generate` | Sinh streaming (SSE) |
| POST | `/api/v1/wiki/generate/sync` | Sinh đồng bộ (JSON) |

**Ví dụ request:**

```bash
# Mode sync
curl -X POST http://localhost:8000/api/v1/wiki/generate/sync \
  -H "Content-Type: application/json" \
  -d '{"request": "Phân tích nội dung về Agent trong knowledge base"}'

# Mode streaming (SSE)
curl -X POST http://localhost:8000/api/v1/wiki/generate \
  -H "Content-Type: application/json" \
  -d '{"request": "Tiêu hoá bài này giúp mình https://example.com/article"}'
```

**Format response (sync):**

```json
{
  "success": true,
  "content": "Nội dung bài sinh ra...",
  "model": "deepseek-v4-flash",
  "request": "Phân tích nội dung về Agent trong knowledge base"
}
```

---

## Bắt đầu nhanh

### Yêu cầu môi trường

- **Python 3.13+** (bắt buộc)
- **uv** (Python package manager, [hướng dẫn cài](https://docs.astral.sh/uv/getting-started/installation/))
- **Claude Code** (`npm install -g @anthropic-ai/claude-code`)
- **Node.js** (cần cho build Quartz và API service)

### Cài đặt

```bash
# 1. Clone project
git clone <repository-url>
cd llm-wiki-skill-main

# 2. Cài Python deps (uv tự tạo .venv virtual environment)
uv sync

# 3. Cấu hình biến môi trường
cp .env.example .env
# Edit .env, điền API config của bạn
```

### Cấu hình biến môi trường

Edit file `.env`, chọn 1 trong các cấu hình sau theo API bạn dùng:

**Dùng API chính chủ Anthropic:**

```env
ANTHROPIC_AUTH_TOKEN=sk-ant-your_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com
MODEL=claude-sonnet-4-20250514
```

**Dùng DeepSeek hoặc endpoint tương thích khác:**

```env
ANTHROPIC_AUTH_TOKEN=your_deepseek_key
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
MODEL=deepseek-v4-flash
```

### Verify cài đặt

```bash
# Check Python version (bắt buộc 3.13+)
.\.venv\Scripts\python.exe --version

# Check SDK version (bắt buộc 0.1.1)
.\.venv\Scripts\python.exe -B -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"

# Test CLI mode
.\.venv\Scripts\python.exe -B 7_wiki_writer.py -r "xin chào"
```

### Dùng knowledge base

Trong Claude Code, vào thư mục project rồi dùng ngôn ngữ tự nhiên:

```
# Khởi tạo knowledge base
"Giúp mình khởi tạo 1 knowledge base về AI"

# Thêm nguyên liệu
"Tiêu hoá bài này giúp mình: https://example.com/article"

# Query knowledge base
"Knowledge base của mình có gì về RAG?"

# Health check
"Kiểm tra trạng thái knowledge base"
```

---

## Về quản lý Python version

Project yêu cầu Python 3.13+. Khuyến nghị dùng `uv`, nó tự tạo `.venv` virtual environment, không cần switch Python version thủ công:

```bash
# Tất cả lệnh chạy qua .venv (-B bỏ qua bytecode cache để start nhanh hơn)
.\.venv\Scripts\python.exe -B 7_wiki_writer.py -r "request của bạn"
.\.venv\Scripts\python.exe -B wiki_writer_api.py
```

Nếu bạn dùng **pyenv**, `.python-version` ghi là `3.13`, nhưng pyenv cần version đầy đủ:

```bash
pyenv install 3.13.7
pyenv local 3.13.7
```

> **Start chậm trên Windows?** Lần đầu chạy, package `mcp` cần compile rất nhiều bytecode (`.pyc`), trên Windows có thể mất 1-2 phút. Thêm `-B` để bỏ qua bytecode cache, start nhanh hơn rõ rệt.

---

## Vấn đề thường gặp

### SDK connect() treo không phản hồi

**Triệu chứng:** Sau khi chạy script, panel info hiện ra nhưng kẹt ở "đang phân tích request" không phản hồi.

**Nguyên nhân:** `claude-agent-sdk` version 0.1.7x có bug deadlock `anyio.to_thread.run_sync` trên môi trường Windows + Python 3.13.

**Khắc phục:** Xác nhận SDK version là `0.1.1` (đã pin trong `pyproject.toml`):

```bash
.\.venv\Scripts\python.exe -B -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"
# Phải output 0.1.1
```

Nếu version không đúng, rebuild virtual environment:

```bash
rmdir /s /q .venv
uv sync
```

### receive_response() không terminate (Python 3.11 trở xuống)

Trên Python 3.11, khi dùng endpoint bên thứ ba như DeepSeek, `receive_response()` của SDK không tự terminate. Lên Python 3.13 là tự fix.

### uv run không phản hồi

`uv run` có thể kẹt ở dependency resolution hoặc install. Dùng trực tiếp Python trong `.venv`:

```bash
.\.venv\Scripts\python.exe -B your_script.py
```

### ImportError: No module named 'fastapi'

API mode cần dep bổ sung, chạy `uv sync` để cài:

```bash
uv sync
```

---

## Cấu trúc project

```
llm-wiki-skill-main/
├── .claude/
│   └── skills/
│       ├── llm-wiki-skill/       # Skill xây knowledge base
│       │   ├── SKILL.md           # Định nghĩa skill và workflow
│       │   ├── scripts/           # Script phụ trợ
│       │   └── templates/         # Template trang
│       └── quartz-wiki/           # Skill deploy site tĩnh
│           └── SKILL.md
├── ai-wiki/                      # Data knowledge base
│   ├── raw/                     # Nguyên liệu thô
│   └── wiki/                    # Nội dung wiki có cấu trúc
├── quartz/                       # Site tĩnh Quartz
├── 7_wiki_writer.py              # Công cụ SDK CLI
├── wiki_writer_api.py            # Service SDK API
├── pyproject.toml                # Python dependencies
├── .env.example                  # Template biến môi trường
└── .gitignore
```

## Tiêu chuẩn chất lượng

Knowledge base tuân thủ tiêu chuẩn chặt chẽ:

- **Trang thực thể**: ít nhất 1500 ký tự, cấm placeholder, bắt buộc trích nguồn
- **Tóm tắt nguồn**: bắt buộc có phần "nội dung thực hành" và "trích đoạn"
- **Trang chủ đề**: ít nhất 5 điểm cốt lõi, cần có knowledge structure
- **Link nhất quán**: mọi `[[link]]` phải khớp tên file thực tế
- **Song ngữ Trung-Anh**: hỗ trợ tiếng Trung và tiếng Anh, đường dẫn file giữ nhất quán

## Tài liệu tham khảo

- [Claude Agent SDK docs](https://docs.claude.com/en/api/agent-sdk/python)
- [Claude Agent SDK tutorial](https://github.com/kenneth-liao/claude-agent-sdk-intro)
- [Quartz v4 docs](https://quartz.jzhao.xyz/)
- [Karpathy llm-wiki](https://github.com/karpathy/llm-wiki)

## 📱 Telegram bot lười — paste link là xong

`telegram_bot.py` cho phép paste link vào Telegram chat → bot tự động đẩy vào pipeline `raw-watcher.sh` → reply lại link Quartz wiki khi xử lý xong. Không đụng pipeline có sẵn.

### Setup (5 phút)

1. **Tạo bot qua [@BotFather](https://t.me/BotFather)** → copy token dạng `1234567890:AAAA...`.
2. **Chat với bot mới tạo** 1 lần (gửi bất kỳ tin nhắn nào).
3. **Lấy chat_id của bạn**:
   ```bash
   uv run python telegram_bot.py --getchatid
   ```
   Bot sẽ in `chat_id=...` rồi exit.
4. **Điền `.env`** (xem `.env.example` for template):
   ```
   TELEGRAM_BOT_TOKEN=<from BotFather>
   TELEGRAM_ALLOWED_CHAT_ID=<from step 3>
   QUARTZ_PUBLIC_BASE_URL=https://your-site.pages.dev
   ```
5. **Enable systemd user service** (auto-start cùng WSL):
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now llm-wiki-telegram-bot
   systemctl --user status llm-wiki-telegram-bot
   ```

### Sử dụng

Mở Telegram chat với bot → paste URL bài viết → đợi 1-3 phút → bot reply link wiki.

```
You: https://www.woshipm.com/pd/6384384.html
Bot: 🔄 Đã nhận URL — đang đẩy vào pipeline...
Bot: ✅ Đã ingest + deploy xong!
     Wiki source: https://your-site.pages.dev/sources/2026-05-07-...
```

Logs: `scripts/telegram_bot.log` (bot) + `scripts/watcher.log` (pipeline).

Stop / restart:
```bash
systemctl --user stop llm-wiki-telegram-bot
systemctl --user restart llm-wiki-telegram-bot
```

## ☁️ Cloud mode — chạy không cần máy local

Local mode ở trên cần WSL2 mở 24/7. Nếu muốn tắt máy mà bot vẫn xử lý link, có 2 hướng:

### Hướng 1: VPS (recommend, đơn giản nhất)

Port y nguyên local stack lên 1 VPS Ubuntu nhỏ (~$5/tháng). Code không đổi, chỉ đổi host. Setup ~10 phút.

→ Xem [`deploy/README.md`](deploy/README.md)

### Hướng 2: GitHub Actions + Cloudflare Worker (free, phức tạp hơn)

```
Telegram → Cloudflare Worker (webhook, always-on, free)
        → repository_dispatch → GitHub Actions
        → workflow chạy 7_wiki_writer.py + commit ai-wiki/ → push main
        → Cloudflare Pages auto-build từ commit → site live
        → workflow gửi Telegram reply với URL khi xong
```

### Setup

1. **GitHub Actions secrets** — repo Settings → Secrets and variables → Actions:
   - `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `MODEL`
   - `TELEGRAM_BOT_TOKEN` (cùng token với local mode)
   - `QUARTZ_PUBLIC_BASE_URL`, `CLOUDFLARE_PAGES_PROJECT`

2. **Probe trước khi tin** (Phase 1 của plan):
   ```bash
   gh workflow run probe-ingest.yml -f url='https://karpathy.bearblog.dev/llm-os/'
   ```
   Tab Actions → xem run mới, download artifact `probe-output` để check log. Nếu skill ingest chạy được → tiếp tục.

3. **Deploy Cloudflare Worker** — xem [`cloudflare-worker/README.md`](cloudflare-worker/README.md) cho các bước chi tiết (`wrangler login`, set secrets, `wrangler deploy`, `setWebhook`).

4. **Bật Cloudflare Pages auto-build từ Git** — Pages dashboard → project → Settings → Builds & deployments → Connect to Git → repo `liangdabiao/llm-wiki`, branch `main`. Build command: `cd quartz && rm -rf public .quartz-cache && npx quartz build`. Output: `quartz/public`.

5. **Test e2e**: tắt WSL hoàn toàn, gửi 1 URL Telegram → ack < 5s → 2-6 phút sau nhận URL wiki final → click load thành công.

Local mode và cloud mode KHÔNG xung đột. Có thể chạy cả hai (local nhanh hơn khi máy mở; cloud là fallback). Để tránh ingest 2 lần cùng URL: **không chạy đồng thời** `telegram_bot.py` local và webhook cloud trên cùng 1 bot token.
