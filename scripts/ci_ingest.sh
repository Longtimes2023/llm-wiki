#!/bin/bash
# CI ingest wrapper — port of raw-watcher.sh's ingest_one_file logic for GitHub Actions.
# Verifies success by checking ai-wiki/wiki/sources/ count grew (same gate as raw-watcher.sh).
#
# Usage: scripts/ci_ingest.sh "<url>"
# Env (set by workflow):
#   ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL, MODEL
#
# Exit codes:
#   0  ingest verified (sources count grew)
#   1  ingest failed (api error / non-zero exit / sources unchanged)

set -euo pipefail

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "usage: $0 <url>" >&2
  exit 2
fi

PROJECT_DIR="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
SOURCES_DIR="$PROJECT_DIR/ai-wiki/wiki/sources"
RAW_DIR="$PROJECT_DIR/ai-wiki/raw/articles"
LOG_FILE="${CI_INGEST_LOG:-$PROJECT_DIR/scripts/ci_ingest.log}"

mkdir -p "$SOURCES_DIR" "$RAW_DIR"

log() {
  echo "[$(date '+%F %T')] [ci_ingest] $*" | tee -a "$LOG_FILE"
}

count_sources() {
  find "$SOURCES_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l
}

# Drop a raw stub file matching telegram_bot.py's format so the skill has a
# canonical entry point. 7_wiki_writer.py via skill will fetch + process.
write_raw_stub() {
  local ts short path
  ts=$(date +%Y-%m-%d-%H%M%S)
  short=$(printf '%s' "$URL:$RANDOM" | sha1sum | cut -c1-6)
  path="$RAW_DIR/${ts}-ci-${short}.md"
  cat > "$path" <<EOF
---
source_url: $URL
captured_at: $(date -Iseconds)
captured_via: github_actions
---

# Source URL

$URL

(GitHub Actions ingest — please fetch this URL and process it as a normal article source.)
EOF
  echo "$path"
}

COUNT_BEFORE=$(count_sources)
log "ingest start | url=$URL | sources count before: $COUNT_BEFORE"

RAW_FILE=$(write_raw_stub)
log "wrote raw stub: $RAW_FILE"

cd "$PROJECT_DIR"

OUTPUT_TMP=$(mktemp)
trap 'rm -f "$OUTPUT_TMP"' EXIT

set +e
uv run python 7_wiki_writer.py \
  -r "请消化这个新素材文件，文件路径是: $RAW_FILE。请运行 llm-wiki-skill 的 ingest 工作流。" \
  > "$OUTPUT_TMP" 2>&1
EXIT_CODE=$?
set -e

cat "$OUTPUT_TMP" | tee -a "$LOG_FILE"

if grep -qE "API Error|status code [4-5][0-9][0-9]|connection error|ETIMEDOUT|ECONNRESET" "$OUTPUT_TMP"; then
  ERR=$(grep -m1 -E "API Error|status code|connection" "$OUTPUT_TMP" | head -c 200)
  log "INGEST FAILED (api/connection error): $ERR"
  exit 1
fi

if [ "$EXIT_CODE" -ne 0 ]; then
  log "INGEST FAILED (exit code $EXIT_CODE)"
  exit 1
fi

COUNT_AFTER=$(count_sources)
if [ "$COUNT_AFTER" -le "$COUNT_BEFORE" ]; then
  log "INGEST FAILED (sources count unchanged: $COUNT_BEFORE -> $COUNT_AFTER)"
  exit 1
fi

# Find the new source file and emit it for downstream steps.
NEW_SOURCE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.md" -newer "$RAW_FILE" 2>/dev/null | head -1)
if [ -n "$NEW_SOURCE" ]; then
  STEM=$(basename "$NEW_SOURCE" .md)
  log "INGEST VERIFIED OK (sources count: $COUNT_BEFORE -> $COUNT_AFTER) | new source: $STEM"
  if [ -n "${GITHUB_OUTPUT:-}" ]; then
    {
      echo "new_source_stem=$STEM"
      echo "raw_file=$(basename "$RAW_FILE")"
    } >> "$GITHUB_OUTPUT"
  fi
else
  log "INGEST VERIFIED OK (sources count: $COUNT_BEFORE -> $COUNT_AFTER) | new source: <unknown>"
fi
