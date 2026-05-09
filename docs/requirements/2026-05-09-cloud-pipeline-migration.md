# Requirement: Migrate llm-wiki ingest pipeline to GitHub Actions

- **Date**: 2026-05-09
- **Owner**: Steven
- **Stop target this run**: `phase_cleanup` (vibe-do)
- **Status**: frozen
- **Linked plan**: `.claude/plans/polished-booping-rabin.md`
- **Predecessor requirement**: `docs/requirements/2026-05-07-telegram-bot-llm-wiki.md`

## 1. Goal

Tách phụ thuộc của workflow ingest khỏi máy local: hiện tại `telegram_bot.py` long-poll + `raw-watcher.sh` (systemd user unit) + `sync-and-rebuild.sh` đều cần WSL2 mở 24/7. Mục tiêu: tắt máy, gửi link Telegram, link wiki vẫn xuất hiện trên `*.pages.dev` sau vài phút.

## 2. Deliverable

- `cloudflare-worker/` — Worker nhận webhook Telegram, dispatch sang GitHub.
- `.github/workflows/probe-ingest.yml` — manual probe cho Phase 1 (validate skill chạy được trên runner).
- `.github/workflows/ingest-url.yml` — workflow chính, triggered qua `repository_dispatch`.
- `scripts/ci_ingest.sh` — wrapper port từ `raw-watcher.sh` để chạy trên Actions runner.
- `scripts/notify_telegram.py` — gửi sendMessage final khi workflow xong/fail.
- Cập nhật `.env.example` phân tách rõ LOCAL vs CLOUD vars.
- README section mới hướng dẫn setup cloud mode.

## 3. Constraints

| ID | Constraint | Source |
|---|---|---|
| C1 | Không xoá / không đổi behavior local stack (`telegram_bot.py`, `raw-watcher.sh`, `sync-and-rebuild.sh`, `setup-wsl-autostart.ps1`, `7_wiki_writer.py`) | giảm blast radius |
| C2 | Single-user allowlist như requirement cũ (C2 doc 2026-05-07) | UX không đổi |
| C3 | Reply final phải là Quartz public URL `https://*.pages.dev/...` | đồng bộ với A3 cũ |
| C4 | Secrets không hardcode; phải qua GitHub Actions secrets + Cloudflare Worker secrets | security baseline |
| C5 | Cloudflare Pages build từ Git push, KHÔNG dùng `wrangler pages deploy` trong CI | đơn giản, không cần CLOUDFLARE_API_TOKEN trong Actions |
| C6 | Worker phải verify `X-Telegram-Bot-Api-Secret-Token` header | chống request giả mạo |
| C7 | Workflow phải `concurrency.cancel-in-progress: false` để 2 link liên tiếp không bị mất | match A6 cũ |

## 4. Acceptance criteria

### 4.1 Functional acceptance (must pass)

- **A1**: Tắt WSL hoàn toàn. Gửi 1 URL từ Telegram → bot ack reply trong < 5s.
- **A2**: GitHub Actions tab thấy workflow `Ingest URL` chạy với client_payload đúng URL.
- **A3**: Workflow exit 0, `git log origin/main` thấy commit `ingest: <url>` của `llm-wiki-bot`.
- **A4**: Cloudflare Pages dashboard thấy deployment mới được trigger từ commit đó (không phải `wrangler deploy`).
- **A5**: Telegram nhận reply final với URL `https://<project>.pages.dev/wiki/sources/<stem>`. URL load thật (HTTP 200).
- **A6**: Gửi URL từ chat_id không trong allowlist → worker ignore, không trigger workflow.
- **A7**: Gửi message không có URL → bot reply "❌ Không tìm thấy URL hợp lệ", không dispatch.
- **A8**: Force fail (gửi URL 404) → workflow fail → Telegram nhận "❌ Pipeline thất bại" + link workflow run.
- **A9**: Gửi 2 URL trong 5s → cả 2 workflow chạy lần lượt (concurrency group `ingest`), không lost.

### 4.2 Product acceptance (the laziness check)

- **P1**: Trên điện thoại, máy bàn tắt, copy link → paste Telegram → reply final với URL clickable. Không cần mở máy.
- **P2**: Từ ack đến final reply ≤ 6 phút cho URL blog đơn giản.

### 4.3 Manual spot checks

- M1: Blog tĩnh (Substack / Bear / Medium) → wiki có entry đúng nội dung.
- M2: YouTube link → tận dụng `youtube-transcript`, wiki có summary.
- M3: WeChat MP link → có thể fail nếu skill cần Chrome MCP; cần xác nhận từ Phase 1 probe.
- M4: Force PAT expire → worker dispatch fail, user nhận error message rõ ràng (không treo).
- M5: Restart Cloudflare Worker (re-deploy) trong lúc không có message → không mất state (worker stateless).

### 4.4 Completion language policy

Không dùng "done", "production-ready", "fully working" cho đến khi:
- A1-A9 chạy thực ít nhất 1 lần.
- Đã verify với WSL **tắt hoàn toàn** (kill WSL distro, không chỉ stop systemd unit).
- 1 message → 1 commit → 1 Pages deploy → 1 URL clickable, có screenshot.

Trước đó, status là "implemented" / "smoke-tested local" / "probe pending".

### 4.5 Delivery truth contract

- "Cloud pipeline live" = `wrangler deployments list` thấy worker active + GitHub Actions tab thấy ≥1 successful run của `ingest-url` từ `repository_dispatch` event.
- "Bot reply được" = screenshot Telegram chat thật.
- "Pipeline e2e" = commit `ingest: <url>` trên `origin/main` + Pages deploy trong dashboard với cùng commit SHA + URL trong reply Telegram load HTTP 200.

## 5. Non-goals

- **N1**: Không xoá `telegram_bot.py` long-poll mode — vẫn dùng được local.
- **N2**: Không xoá `raw-watcher.sh` / systemd unit / autostart task — local dev path còn nguyên.
- **N3**: Không multi-tenant (single chat_id allowlist).
- **N4**: Không support media (chỉ URL).
- **N5**: Không build dashboard / `/status` command.
- **N6**: Không thay `7_wiki_writer.py` hoặc skill nội dung — chỉ thay môi trường chạy.
- **N7**: Không bật Cloudflare Pages cho preview branches — chỉ `main`.
- **N8**: Không setup GitHub App; PAT đủ.

## 6. Autonomy mode

- `interactive_governed` — vibe stop target = `phase_cleanup`. User tự handle các bước có touch hệ thống bên ngoài (set secrets, deploy worker, kết nối Pages với Git, register webhook), code/docs là Claude làm.

## 7. Inferred assumptions (need flag if wrong)

- **I1**: GitHub Actions Ubuntu runner đủ để chạy `7_wiki_writer.py` cho ít nhất loại URL blog tĩnh đơn giản. **Cần Phase 1 probe để verify.**
- **I2**: Skill `llm-wiki` có code path không cần browser MCP cho ít nhất 1 loại URL. Nếu mọi loại đều cần Chrome interactive → escalate (cài chromium trong runner, hoặc dùng `claude-code` MCP server với puppeteer adapter).
- **I3**: PAT classic scope `repo` đủ cho `repository_dispatch` + `git push`. Fine-grained PAT cũng được nhưng cần quyền `Contents: write` + `Actions: write` cụ thể cho repo này.
- **I4**: Cloudflare Pages auto-build từ Git có thể `cd quartz && npx quartz build` mà không cần rsync vì workflow đã commit `quartz/content/` cùng `ai-wiki/`.
- **I5**: Cloudflare Worker free plan đủ — load thực tế ~10 request/ngày, mỗi request 2 fetch.
- **I6**: User đã có 1 bot Telegram active từ requirement cũ và 1 Cloudflare Pages project active từ deploy hiện tại — không cần tạo mới.

Nếu sai bất kỳ giả định nào, flag trước khi bắt đầu test thực.

## 8. Out-of-scope (parking lot)

- Worker dùng KV để dedupe message_id (Telegram retry sometimes).
- Tự động re-register webhook nếu detect 401/error.
- Worker custom domain thay `*.workers.dev`.
- Multi-URL trong 1 message (regex hiện chỉ lấy URL đầu tiên).
- Cancel button trong reply ack để abort workflow.
- Status command `/last` qua bot xem run gần nhất.
