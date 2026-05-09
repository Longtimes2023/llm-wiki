# Multi-Provider Setup

Mỗi file `<name>.env` trong thư mục này là 1 provider profile. Bot/CLI/API resolve provider theo thứ tự ưu tiên (cao xuống thấp):

1. CLI flag `--provider X` (per-call)
2. Telegram message có `@X` token (per-URL)
3. `providers/.active` sentinel (sticky default, set bởi `/provider X` command)
4. `ACTIVE_PROVIDER=X` trong `.env` chính (bootstrap fallback)
5. `ANTHROPIC_*` trong `.env` chính (legacy, vẫn work)

Nếu không có gì → dùng giá trị `ANTHROPIC_*` trong main `.env`.

## Thêm provider mới

```bash
cp providers/anthropic.env.example providers/myprovider.env
# Edit providers/myprovider.env, điền AUTH_TOKEN + BASE_URL + MODEL
# Optional: thêm INPUT_PRICE_PER_M, OUTPUT_PRICE_PER_M để track cost trong A/B
```

## Switch sticky provider

Trong Telegram chat:
```
/provider                 # show active + list available
/provider deepseek        # switch sticky
```

Hoặc:
```bash
echo deepseek > providers/.active
```

Switch instant — không kill ingest đang chạy. Ingest tiếp theo sẽ pick provider mới.

## A/B test 1 URL với nhiều provider

```
URL @deepseek      # one-off override, không đổi sticky, dedup bypass
URL @anthropic     # ingest lại cùng URL với anthropic
```

Source page sẽ có suffix `-<provider>` để cùng tồn tại side-by-side. Metrics (time + tokens + cost) ghi vào `scripts/ingest_metrics.jsonl`.

## Profile field reference

Required:
- `ANTHROPIC_AUTH_TOKEN` — API key
- `ANTHROPIC_BASE_URL` — endpoint (e.g. `https://api.anthropic.com`, `https://api.deepseek.com/anthropic`)
- `MODEL` — model id (e.g. `claude-sonnet-4-20250514`, `deepseek-v4-flash`)

Optional (for cost reporting):
- `INPUT_PRICE_PER_M` — USD per 1M input tokens
- `OUTPUT_PRICE_PER_M` — USD per 1M output tokens

Profile có giá → cost tự tính; không có → fallback `total_cost_usd` từ SDK (chỉ chính xác với Anthropic native).

## Gitignore

`providers/*.env` và `providers/.active` đều gitignored. Chỉ `.env.example` được track. Đừng commit creds.
