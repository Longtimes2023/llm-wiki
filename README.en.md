**Language / 语言 / Ngôn ngữ**: [中文](README.md) · **English** · [Tiếng Việt](README.vi.md)

---

# LLM Wiki — Personal AI Knowledge Base

Built on the [Karpathy llm-wiki](https://github.com/karpathy/llm-wiki) methodology, this project uses AI to continuously build and maintain your personal knowledge base. It automatically organizes content from multiple source types (web pages, Twitter, WeChat articles, Xiaohongshu, Zhihu, YouTube, PDFs, local files) into a structured wiki, and publishes it as a static knowledge-base site through Quartz. It also exposes the LLM-wiki capabilities through the Claude Agent SDK with an HTTP API for external service.

Claude Agent SDK + LLM-wiki — the most powerful agentic RAG you can build today. This repo demonstrates how the LLM-wiki I built becomes agentic RAG via the Claude Agent SDK, with excellent results. Core files: `7_wiki_writer.py`, `wiki_writer_api.py`.

## 🤔 What is LLM-wiki?

LLM Wiki: use large language models to automatically organize your scattered knowledge into a structured "personal encyclopedia". The traditional way: every time you ask AI a question, the AI re-reads all your raw material, finds the relevant parts, then answers (this is RAG — retrieval-augmented generation). It's like asking a librarian a question and forcing them to re-shelf every book in the library each time. Karpathy says this is silly. The right approach: let the AI act as a "knowledge compiler" — read all your material once, organize it into a clear, cross-linked encyclopedia. Then when you ask questions, the AI just flips through that encyclopedia.

The full pipeline of a traditional RAG system is: ingest → chunk → index → retrieve → rerank → prompt-pack → generate → cite. Karpathy is genuinely profound — the most important AI concepts of the last few years all trace back to him, all looking simple but reaching the essence. llm-wiki is massively underrated; it's the root of building AI. The wiki format is the key insight — AI uses that structure to organize all knowledge. It dissolves the entire RAG problem in one go. I've stopped using RAG; this is the answer. Beyond RAG, it can one-click generate a wiki site, a real knowledge base. After testing many approaches, I found this gem. Built on top of this, I can build many powerful projects — the deeper the understanding, the deeper the generation. That's how you build AI. The current `wiki/` folder is where the wiki content lives; for now I've put some open-source articles by Yupi (鱼皮) in there to test the result.

Referenced projects:
- https://github.com/kenneth-liao/claude-agent-sdk-intro
- https://github.com/sdyckjq-lab/llm-wiki-skill

Special thanks to: https://linux.do/

## Three Core Capabilities

### 1. LLM Wiki Skill — Knowledge Base Construction

Using Claude Code's Skill mechanism, AI handles knowledge-base capture, organization, quality control, and maintenance automatically.

**Supported workflows:**

| Workflow | Description |
|----------|-------------|
| `init` | Initialize a new knowledge base, create directory structure and config |
| `ingest` | Digest a single source (URL / file / pasted text), auto-extract entities and topics |
| `batch-ingest` | Batch-process multiple files (.md / .txt / .pdf / .html) |
| `query` | Query the knowledge base, return synthesized answers with citations |
| `digest` | Deep synthesis report, cross-source analysis of a specific topic |
| `lint` | Health check: orphan pages, broken links, content quality |
| `status` | View knowledge base status: source distribution, page stats, recent activity |
| `graph` | Generate a Mermaid knowledge graph to visualize entity relationships |

**Supported source types:**

| Type | Extraction method |
|------|-------------------|
| Web articles | `baoyu-url-to-markdown` |
| X / Twitter | `baoyu-url-to-markdown` |
| WeChat articles | `wechat-article-to-markdown` |
| YouTube | `youtube-transcript` |
| Zhihu | `baoyu-url-to-markdown` |
| PDF | direct read |
| Local files (.md / .txt) | direct read |

**Knowledge base directory layout:**

```
ai-wiki/
├── .wiki-schema.md      # Knowledge base config and quality standards
├── index.md             # Content index
├── log.md               # Operation log
├── overview.md          # Quick navigation
├── raw/                 # Raw source material
│   ├── articles/        # Web articles
│   ├── tweets/          # Tweets
│   ├── wechat/          # WeChat articles
│   ├── xiaohongshu/     # Xiaohongshu content
│   ├── zhihu/           # Zhihu content
│   ├── pdfs/            # PDFs
│   └── notes/           # Notes and text
└── wiki/                # Structured wiki content
    ├── entities/        # Entity pages (tools, concepts, people)
    ├── topics/          # Topic pages (research areas)
    ├── sources/         # Source summaries
    ├── comparisons/     # Comparative analyses
    └── synthesis/       # Synthesis analyses
```

**Detailed usage:**

❯ ai-guide is the collected material; the task is to use llm-wiki skill to analyze and organize it into a wiki — please complete it.

![](./图片1.png)

### 2. Quartz Wiki Skill — Static Site Deployment

Publish the generated knowledge base as a beautiful static site via [Quartz v4](https://quartz.jzhao.xyz/).

**Features:**
- Bi-directional links and relationship graph
- Full-text search
- Responsive design with light/dark themes
- Deployable to Cloudflare Pages / Vercel / GitHub Pages

**Config file:** `quartz/quartz.config.ts`

```bash
# Local preview
cd quartz
npx quartz build --serve

# Production build
npx quartz build

# Deploy to Cloudflare Pages
npx wrangler pages deploy public
```

**Using the skill inside Claude Code:**

❯ Please use quartz-wiki skill to turn ai-wiki into a Quartz site.

Current deployment: `http://wikilego.liangdabiao.com/`

![](./图片2.png)

### 3. Claude Agent SDK — External Service

Wrap the knowledge-base capability into a programmable AI agent via the [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/python).

#### CLI mode (`7_wiki_writer.py`)

The agent automatically recognizes user intent and invokes llm-wiki-skill to perform knowledge-base operations (query, digest, generate articles, etc).

```bash
# Single request
.\.venv\Scripts\python.exe -B 7_wiki_writer.py -r "Write me a synthesis article about AI agents"

# Interactive mode (continuous conversation)
.\.venv\Scripts\python.exe -B 7_wiki_writer.py -i
```

#### API mode (`wiki_writer_api.py`)

FastAPI-based HTTP service supporting SSE streaming and synchronous JSON responses.

```bash
# Start the service
.\.venv\Scripts\python.exe -B wiki_writer_api.py

# Or via uvicorn (hot-reload supported)
.\.venv\Scripts\uvicorn.exe wiki_writer_api:app --host 0.0.0.0 --port 8000 --reload
```

**API endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/wiki/generate` | Streaming generation (SSE) |
| POST | `/api/v1/wiki/generate/sync` | Synchronous generation (JSON) |

**Request examples:**

```bash
# Sync mode
curl -X POST http://localhost:8000/api/v1/wiki/generate/sync \
  -H "Content-Type: application/json" \
  -d '{"request": "Analyze what the knowledge base contains about Agents"}'

# Streaming mode (SSE)
curl -X POST http://localhost:8000/api/v1/wiki/generate \
  -H "Content-Type: application/json" \
  -d '{"request": "Digest this article https://example.com/article"}'
```

**Response format (sync):**

```json
{
  "success": true,
  "content": "Generated article content...",
  "model": "deepseek-v4-flash",
  "request": "Analyze what the knowledge base contains about Agents"
}
```

---

## Quick Start

### Requirements

- **Python 3.13+** (required)
- **uv** (Python package manager, [install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Claude Code** (`npm install -g @anthropic-ai/claude-code`)
- **Node.js** (needed for Quartz build and API service)

### Install

```bash
# 1. Clone the repo
git clone <repository-url>
cd llm-wiki-skill-main

# 2. Install Python deps (uv auto-creates the .venv virtual environment)
uv sync

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your API config
```

### Environment variables

Edit `.env` and pick one of the following based on the API you use:

**Using the official Anthropic API:**

```env
ANTHROPIC_AUTH_TOKEN=sk-ant-your_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com
MODEL=claude-sonnet-4-20250514
```

**Using DeepSeek or another compatible endpoint:**

```env
ANTHROPIC_AUTH_TOKEN=your_deepseek_key
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
MODEL=deepseek-v4-flash
```

### Verify install

```bash
# Check Python version (must be 3.13+)
.\.venv\Scripts\python.exe --version

# Check SDK version (must be 0.1.1)
.\.venv\Scripts\python.exe -B -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"

# Test CLI mode
.\.venv\Scripts\python.exe -B 7_wiki_writer.py -r "hello"
```

### Using the knowledge base

Inside Claude Code, enter the project directory and just speak natural language:

```
# Initialize the knowledge base
"Help me initialize an AI-themed knowledge base"

# Add material
"Digest this article for me: https://example.com/article"

# Query the knowledge base
"What does my knowledge base have on RAG?"

# Health check
"Check the knowledge base health"
```

---

## On Python version management

The project requires Python 3.13+. Recommended: use `uv`, which auto-creates the `.venv` virtual environment so you don't have to switch Python versions manually:

```bash
# Run all commands through .venv (-B skips bytecode cache for faster startup)
.\.venv\Scripts\python.exe -B 7_wiki_writer.py -r "your request"
.\.venv\Scripts\python.exe -B wiki_writer_api.py
```

If you use **pyenv**, `.python-version` says `3.13`, but pyenv needs the full version:

```bash
pyenv install 3.13.7
pyenv local 3.13.7
```

> **Slow startup on Windows?** On the first run, the `mcp` package compiles a lot of bytecode (`.pyc`), which can take 1-2 minutes on Windows. Adding `-B` skips the bytecode cache and significantly speeds up startup.

---

## Troubleshooting

### SDK connect() hangs

**Symptom:** The script shows the panel info but stays stuck at "analyzing request" with no response.

**Cause:** `claude-agent-sdk` versions 0.1.7x have an `anyio.to_thread.run_sync` deadlock bug on Windows + Python 3.13.

**Fix:** Confirm the SDK version is `0.1.1` (locked in `pyproject.toml`):

```bash
.\.venv\Scripts\python.exe -B -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"
# Must output 0.1.1
```

If the version is wrong, rebuild the virtual environment:

```bash
rmdir /s /q .venv
uv sync
```

### receive_response() doesn't terminate (Python 3.11 or below)

On Python 3.11, when using third-party endpoints like DeepSeek, the SDK's `receive_response()` won't terminate automatically. Upgrading to Python 3.13 resolves this.

### uv run unresponsive

`uv run` may hang on dependency resolution or installation. Use the `.venv` Python directly:

```bash
.\.venv\Scripts\python.exe -B your_script.py
```

### ImportError: No module named 'fastapi'

API mode needs extra dependencies — run `uv sync`:

```bash
uv sync
```

---

## Project structure

```
llm-wiki-skill-main/
├── .claude/
│   └── skills/
│       ├── llm-wiki-skill/       # Knowledge-base construction skill
│       │   ├── SKILL.md           # Skill definition and workflows
│       │   ├── scripts/           # Helper scripts
│       │   └── templates/         # Page templates
│       └── quartz-wiki/           # Static site deployment skill
│           └── SKILL.md
├── ai-wiki/                      # Knowledge-base data
│   ├── raw/                     # Raw source material
│   └── wiki/                    # Structured wiki content
├── quartz/                       # Quartz static site
├── 7_wiki_writer.py              # SDK CLI tool
├── wiki_writer_api.py            # SDK API service
├── pyproject.toml                # Python dependencies
├── .env.example                  # Environment variable template
└── .gitignore
```

## Quality standards

The knowledge base follows strict rules:

- **Entity pages**: at least 1500 characters, no placeholder text, must cite sources
- **Source summaries**: must contain "practical content" and "excerpts" sections
- **Topic pages**: at least 5 key points, must include knowledge structure
- **Link consistency**: every `[[link]]` must match the actual filename
- **Bilingual support**: both Chinese and English are supported with consistent file paths

## References

- [Claude Agent SDK docs](https://docs.claude.com/en/api/agent-sdk/python)
- [Claude Agent SDK tutorial](https://github.com/kenneth-liao/claude-agent-sdk-intro)
- [Quartz v4 docs](https://quartz.jzhao.xyz/)
- [Karpathy llm-wiki](https://github.com/karpathy/llm-wiki)

## 📱 Telegram bot — lazy-ingest

`telegram_bot.py` lets you paste a link into the Telegram chat → the bot automatically pushes it into the `raw-watcher.sh` pipeline → replies with the Quartz wiki link when done. It doesn't touch the existing pipeline.

### Setup (5 minutes)

1. **Create a bot via [@BotFather](https://t.me/BotFather)** → copy the token in the form `1234567890:AAAA...`.
2. **Send a message** to your new bot once (any content).
3. **Get your chat_id**:
   ```bash
   uv run python telegram_bot.py --getchatid
   ```
   The bot prints `chat_id=...` and exits.
4. **Fill in `.env`** (template in `.env.example`):
   ```
   TELEGRAM_BOT_TOKEN=<from BotFather>
   TELEGRAM_ALLOWED_CHAT_ID=<from step 3>
   QUARTZ_PUBLIC_BASE_URL=https://your-site.pages.dev
   ```
5. **Enable the systemd user service** (auto-starts with WSL):
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now llm-wiki-telegram-bot
   systemctl --user status llm-wiki-telegram-bot
   ```

### Usage

Open the Telegram chat with the bot → paste an article URL → wait 1-3 minutes → the bot replies with the wiki link.

```
You: https://www.woshipm.com/pd/6384384.html
Bot: 🔄 URL received — pushing into pipeline...
Bot: ✅ Ingest + deploy complete!
     Wiki source: https://your-site.pages.dev/sources/2026-05-07-...
```

Logs: `scripts/telegram_bot.log` (bot) + `scripts/watcher.log` (pipeline).

Stop / restart:
```bash
systemctl --user stop llm-wiki-telegram-bot
systemctl --user restart llm-wiki-telegram-bot
```

## ☁️ Cloud mode — run without keeping your local machine on

The Local mode above needs WSL2 running 24/7. If you want the bot to keep processing links while your machine is off, there are two options:

### Option 1: VPS (recommended, simplest)

Port the local stack as-is to a small Ubuntu VPS (~$5/month). No code changes, just a different host. ~10 minutes to set up.

→ See [`deploy/README.md`](deploy/README.md)

### Option 2: GitHub Actions + Cloudflare Worker (free, more complex)

```
Telegram → Cloudflare Worker (webhook, always-on, free)
        → repository_dispatch → GitHub Actions
        → workflow runs 7_wiki_writer.py + commits ai-wiki/ → pushes main
        → Cloudflare Pages auto-builds from commit → site live
        → workflow sends a Telegram reply with the URL on completion
```

### Setup

1. **GitHub Actions secrets** — repo Settings → Secrets and variables → Actions:
   - `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `MODEL`
   - `TELEGRAM_BOT_TOKEN` (same token as local mode)
   - `QUARTZ_PUBLIC_BASE_URL`, `CLOUDFLARE_PAGES_PROJECT`

2. **Probe first** (Phase 1):
   ```bash
   gh workflow run probe-ingest.yml -f url='https://karpathy.bearblog.dev/llm-os/'
   ```
   Actions tab → check the new run, download the `probe-output` artifact to inspect logs. If skill ingest runs → proceed.

3. **Deploy the Cloudflare Worker** — see [`cloudflare-worker/README.md`](cloudflare-worker/README.md) for step-by-step (`wrangler login`, set secrets, `wrangler deploy`, `setWebhook`).

4. **Enable Cloudflare Pages auto-build from Git** — Pages dashboard → project → Settings → Builds & deployments → Connect to Git → repo `liangdabiao/llm-wiki`, branch `main`. Build command: `cd quartz && rm -rf public .quartz-cache && npx quartz build`. Output: `quartz/public`.

5. **End-to-end test**: shut down WSL entirely, send a Telegram URL → ack in < 5s → 2-6 minutes later you receive the final wiki URL → click and it loads successfully.

Local and Cloud modes do not conflict. You can run both (local is faster while the machine is on; cloud is the fallback). To avoid ingesting the same URL twice: **do not run** `telegram_bot.py` (local) and the webhook (cloud) simultaneously on the same bot token.
