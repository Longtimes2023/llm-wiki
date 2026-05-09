#!/bin/bash
# llm-wiki raw/ folder watcher (v2: with proper failure detection + retry)
# Watches ai-wiki/raw/ for new markdown files (e.g. from Obsidian Web Clipper)
# and auto-triggers ingest via 7_wiki_writer.py.
set -euo pipefail

# Derive project dir from script location (works on any host).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(dirname "$SCRIPT_DIR")}"
WIKI_NAME="ai-wiki"
WATCH_DIR="$PROJECT_DIR/$WIKI_NAME/raw"
SOURCES_DIR="$PROJECT_DIR/$WIKI_NAME/wiki/sources"
LOG_FILE="$PROJECT_DIR/scripts/watcher.log"
STATE_FILE="$PROJECT_DIR/scripts/watcher.state"
FAILED_FILE="$PROJECT_DIR/scripts/watcher.failed"
DEBOUNCE_SECONDS=3
MAX_ATTEMPTS=3

log() {
  echo "[$(date '+%F %T')] $*" | tee -a "$LOG_FILE"
}

mkdir -p "$WATCH_DIR" "$SOURCES_DIR"
touch "$LOG_FILE" "$STATE_FILE" "$FAILED_FILE"

# Try ingesting one file. Returns 0 on verified success, 1 on failure.
# Failure conditions:
#   - python exit non-zero
#   - "API Error" / "status code" / "connection error" in output
#   - wiki/sources/ count did NOT grow
ingest_one_file() {
  local FILE="$1"
  local OUTPUT_TMP
  OUTPUT_TMP=$(mktemp)

  # Dedup precheck: same source_url as already-processed raw → skip without invoking agent.
  # Returns code 2 (distinct from 0=success-with-rebuild and 1=real-failure).
  local NEW_URL OLD_URL OLD_FILE
  NEW_URL=$(awk '/^source_url:/{print $2; exit}' "$FILE" 2>/dev/null)
  if [ -n "$NEW_URL" ] && [ -s "$STATE_FILE" ]; then
    while IFS= read -r OLD_FILE; do
      [ -z "$OLD_FILE" ] && continue
      [ "$OLD_FILE" = "$FILE" ] && continue
      [ -f "$OLD_FILE" ] || continue
      OLD_URL=$(awk '/^source_url:/{print $2; exit}' "$OLD_FILE" 2>/dev/null)
      if [ "$OLD_URL" = "$NEW_URL" ]; then
        log "DEDUP_SKIP: same URL as $OLD_FILE — skipping ingest, no rebuild needed"
        rm -f "$OUTPUT_TMP"
        return 2
      fi
    done < "$STATE_FILE"
  fi

  local COUNT_BEFORE
  COUNT_BEFORE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
  log "ingest start | sources count before: $COUNT_BEFORE"

  cd "$PROJECT_DIR"
  set +e
  "$PROJECT_DIR/.venv/bin/python" -B 7_wiki_writer.py \
    -r "请消化这个新素材文件，文件路径是: $FILE。请运行 llm-wiki-skill 的 ingest 工作流。" \
    > "$OUTPUT_TMP" 2>&1
  local EXIT_CODE=$?
  set -e

  cat "$OUTPUT_TMP" >> "$LOG_FILE"

  # Failure check 1: explicit error patterns in output
  if grep -qE "API Error|status code [4-5][0-9][0-9]|connection error|ETIMEDOUT|ECONNRESET" "$OUTPUT_TMP"; then
    local ERR
    ERR=$(grep -m1 -E "API Error|status code|connection" "$OUTPUT_TMP" | head -c 200)
    log "INGEST FAILED (api/connection error): $ERR"
    rm -f "$OUTPUT_TMP"
    return 1
  fi

  # Failure check 2: non-zero exit
  if [ "$EXIT_CODE" -ne 0 ]; then
    log "INGEST FAILED (exit code $EXIT_CODE)"
    rm -f "$OUTPUT_TMP"
    return 1
  fi

  # Failure check 3: wiki/sources/ did not grow → no actual ingest happened
  local COUNT_AFTER
  COUNT_AFTER=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
  if [ "$COUNT_AFTER" -le "$COUNT_BEFORE" ]; then
    log "INGEST FAILED (sources count unchanged: $COUNT_BEFORE → $COUNT_AFTER)"
    rm -f "$OUTPUT_TMP"
    return 1
  fi

  log "INGEST VERIFIED OK (sources count: $COUNT_BEFORE → $COUNT_AFTER)"
  rm -f "$OUTPUT_TMP"
  return 0
}

# Process one file with retry/backoff
process_file() {
  local FILE="$1"
  log "=== processing: $FILE ==="

  local attempt
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    log "attempt $attempt/$MAX_ATTEMPTS"

    set +e
    ingest_one_file "$FILE"
    local rc=$?
    set -e

    if [ "$rc" -eq 0 ]; then
      echo "$FILE" >> "$STATE_FILE"
      log "marked as processed in state"

      # Run sync (rsync, no AI)
      if "$PROJECT_DIR/scripts/sync-and-rebuild.sh" >> "$LOG_FILE" 2>&1; then
        log "post-ingest sync OK"
      else
        log "post-ingest sync FAILED (Quartz site may be stale)"
      fi
      return 0
    elif [ "$rc" -eq 2 ]; then
      echo "$FILE" >> "$STATE_FILE"
      log "marked as processed (dedup skip) — no rebuild"
      return 0
    fi

    # rc=1: real failure → backoff before next attempt (skip on last attempt)
    if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
      local backoff=$(( attempt * 30 ))
      log "retrying in ${backoff}s..."
      sleep "$backoff"
    fi
  done

  log "GIVING UP after $MAX_ATTEMPTS attempts: $FILE"
  echo "$FILE" >> "$FAILED_FILE"
  return 1
}

log "watcher v2 started, watching: $WATCH_DIR"

inotifywait -mqr -e close_write,moved_to --format '%w%f' "$WATCH_DIR" \
  | while read -r FILE; do
    case "$FILE" in
      *.md|*.txt) ;;
      *) continue ;;
    esac

    # skip if already verified-processed
    if grep -qxF "$FILE" "$STATE_FILE"; then
      continue
    fi

    log "detected new file: $FILE"
    sleep "$DEBOUNCE_SECONDS"

    process_file "$FILE" || true
  done
