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
LOCK_FILE="$PROJECT_DIR/scripts/raw-watcher.lock"
DEBOUNCE_SECONDS=3
MAX_ATTEMPTS=3

mkdir -p "$WATCH_DIR" "$SOURCES_DIR"
touch "$LOG_FILE" "$STATE_FILE" "$FAILED_FILE"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  printf '[%s] watcher already running, exiting\n' "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
  exit 0
fi

remove_from_failed() {
  local FILE="$1"
  [ -f "$FAILED_FILE" ] || return 0
  local TMP
  TMP=$(mktemp)
  grep -vxF "$FILE" "$FAILED_FILE" > "$TMP" || true
  mv "$TMP" "$FAILED_FILE"
}

log() {
  # systemd unit redirects stdout/stderr to $LOG_FILE via StandardOutput=append.
  # Echo once to stdout; do not also tee to LOG_FILE or every line lands twice.
  echo "[$(date '+%F %T')] $*"
}

# Try ingesting one file. Returns 0 on verified success, 1 on failure, 2 on dedup-skip, 3 on config error.
# Failure conditions:
#   - python exit non-zero
#   - "API Error" / "status code" / "connection error" in output
#   - wiki/sources/ count did NOT grow
# Args:
#   $1 = raw file path
#   $2 = optional provider override (from fallback chain). Supersedes frontmatter `provider:` for the
#        actual --provider flag but does NOT add the A/B filename suffix (that's only for user-explicit overrides).
ingest_one_file() {
  local FILE="$1"
  local CHAIN_PROVIDER="${2:-}"
  local OUTPUT_TMP
  OUTPUT_TMP=$(mktemp)

  # Read optional provider override from raw frontmatter (set by telegram_bot when
  # user sends `URL @<provider>`). Bypasses dedup precheck — intentional re-test.
  local PROVIDER
  PROVIDER=$(awk '/^provider:/{print $2; exit}' "$FILE" 2>/dev/null)

  # Dedup precheck: same source_url as already-processed raw → skip without invoking agent.
  # Skipped when PROVIDER override present (A/B re-test).
  # Returns code 2 (distinct from 0=success-with-rebuild and 1=real-failure).
  local NEW_URL OLD_URL OLD_FILE
  NEW_URL=$(awk '/^source_url:/{print $2; exit}' "$FILE" 2>/dev/null)
  if [ -z "$PROVIDER" ] && [ -n "$NEW_URL" ] && [ -s "$STATE_FILE" ]; then
    while IFS= read -r OLD_FILE; do
      [ -z "$OLD_FILE" ] && continue
      [ "$OLD_FILE" = "$FILE" ] && continue
      [ -f "$OLD_FILE" ] || continue
      OLD_URL=$(awk '/^source_url:/{print $2; exit}' "$OLD_FILE" 2>/dev/null)
      if [ "$OLD_URL" = "$NEW_URL" ]; then
        log "DEDUP_SKIP: $FILE same URL as $OLD_FILE — skipping ingest, no rebuild needed"
        rm -f "$OUTPUT_TMP"
        return 2
      fi
    done < "$STATE_FILE"
  fi

  local COUNT_BEFORE
  COUNT_BEFORE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
  # Half-write tripwire: skill workflow step 8 ALWAYS appends to ai-wiki/log.md when ingest
  # is complete. If sources/ grew but log.md did not, the agent crashed mid-flow after writing
  # the source page but before updating log.md / entities / topics. We reject that and retry.
  local LOG_LINES_BEFORE
  LOG_LINES_BEFORE=$(wc -l < "$PROJECT_DIR/$WIKI_NAME/log.md" 2>/dev/null || echo 0)
  # Resolve effective provider for this attempt: chain override > frontmatter override > none (loader picks .active).
  local EFFECTIVE_PROVIDER=""
  if [ -n "$CHAIN_PROVIDER" ]; then
    EFFECTIVE_PROVIDER="$CHAIN_PROVIDER"
    log "ingest start | provider=$EFFECTIVE_PROVIDER (fallback chain) | sources count before: $COUNT_BEFORE"
  elif [ -n "$PROVIDER" ]; then
    EFFECTIVE_PROVIDER="$PROVIDER"
    log "ingest start | provider=$EFFECTIVE_PROVIDER (frontmatter override) | sources count before: $COUNT_BEFORE"
  else
    log "ingest start | sources count before: $COUNT_BEFORE"
  fi

  cd "$PROJECT_DIR"
  set +e
  # Build provider flag + A/B suffix instruction. A/B suffix only fires for user-explicit
  # frontmatter overrides — fallback-chain attempts overwrite (no suffix) because they're
  # recovery attempts for the same logical ingest, not A/B comparisons.
  local PROVIDER_FLAG=""
  local AB_HINT=""
  if [ -n "$EFFECTIVE_PROVIDER" ]; then
    PROVIDER_FLAG="--provider $EFFECTIVE_PROVIDER"
  fi
  if [ -n "$PROVIDER" ] && [ -z "$CHAIN_PROVIDER" ]; then
    AB_HINT="注意：素材摘要页文件名末尾追加 -$PROVIDER 后缀（用于 A/B 测试，避免覆盖之前用其他模型生成的版本）。"
  fi
  # Hard cap per attempt: 25m. Without this, claude_agent_sdk hangs can block the
  # entire watcher queue (raw-watcher processes files sequentially via inotify pipe).
  # Exit 124 = timeout reached, 137 = SIGKILL after grace. Treated as normal failure.
  timeout --kill-after=10s 25m \
    "$PROJECT_DIR/.venv/bin/python" -B 7_wiki_writer.py $PROVIDER_FLAG \
    --raw-file "$FILE" \
    -r "请消化这个新素材文件，文件路径是: $FILE。请运行 llm-wiki-skill 的 ingest 工作流。${AB_HINT}" \
    > "$OUTPUT_TMP" 2>&1
  local EXIT_CODE=$?
  set -e

  cat "$OUTPUT_TMP" >> "$LOG_FILE"

  # Persist [METRICS] line emitted by 7_wiki_writer.py to ingest_metrics.jsonl for A/B aggregation.
  # New format: [METRICS_BEGIN]<compact json>[METRICS_END] — single line, marker-delimited,
  # survives terminal wrapping and SDK-error glue. Fall back to legacy [METRICS] {flat} for
  # one cycle in case an in-flight writer process still emits the old format.
  local METRICS_LINE
  METRICS_LINE=$(grep -m1 -oE '\[METRICS_BEGIN\].*\[METRICS_END\]' "$OUTPUT_TMP" 2>/dev/null \
                 | sed 's/^\[METRICS_BEGIN\]//; s/\[METRICS_END\]$//')
  if [ -z "$METRICS_LINE" ]; then
    METRICS_LINE=$(grep -m1 -oE '\[METRICS\] \{[^}]*\}' "$OUTPUT_TMP" 2>/dev/null | sed 's/^\[METRICS\] //')
  fi
  if [ -n "$METRICS_LINE" ]; then
    echo "$METRICS_LINE" >> "$PROJECT_DIR/scripts/ingest_metrics.jsonl"
    log "metrics: $METRICS_LINE"
  fi

  # Capture [FETCH_FAIL] {...} line emitted by the skill when all source-fetch paths
  # (WebFetch, baoyu, youtube-transcript, manual fallback) have given up. Persisted to
  # ingest_failures.jsonl so telegram_bot can surface the reason to the user.
  local FETCH_FAIL_LINE
  FETCH_FAIL_LINE=$(grep -m1 -oE '\[FETCH_FAIL\] \{[^}]*\}' "$OUTPUT_TMP" 2>/dev/null \
                    | sed 's/^\[FETCH_FAIL\] //')
  if [ -n "$FETCH_FAIL_LINE" ]; then
    # Inject raw_file so the bot can correlate without parsing the source_id.
    local RAW_BASENAME
    RAW_BASENAME=$(basename "$FILE")
    local ENRICHED
    ENRICHED=$(echo "$FETCH_FAIL_LINE" | sed "s|}\$|,\"raw_file\":\"$RAW_BASENAME\"}|")
    if python3 - <<'PY' "$ENRICHED"
import json
import sys

obj = json.loads(sys.argv[1])
placeholders = {
    "source_id": {"<id>", "<source_id>", "真实来源ID"},
    "url": {"<url>", "https://example.com/post", "真实原始URL"},
    "reason": {"<一句话原因>", "<reason>", "真实一句话原因"},
    "status": {"403|paywall|empty|timeout|runtime_failed", "<status>", "真实单一状态值"},
}
for key, invalid_values in placeholders.items():
    value = obj.get(key)
    if isinstance(value, str) and value.strip() in invalid_values:
        raise SystemExit(1)
PY
    then
      echo "$ENRICHED" >> "$PROJECT_DIR/scripts/ingest_failures.jsonl"
      log "fetch_fail: $ENRICHED"
    else
      log "fetch_fail skipped placeholder payload for $(basename "$FILE"): $FETCH_FAIL_LINE"
    fi
  fi

  # Config error (deterministic): exit 2 + [CONFIG_ERROR] marker in output. Never retry —
  # a missing/invalid provider profile fails identically on every attempt, so burning the
  # fallback chain on it just wastes time. Marker check (not just exit code 2) avoids
  # confusion with argparse's default exit code 2 for bad args.
  if [ "$EXIT_CODE" -eq 2 ] && grep -qF '[CONFIG_ERROR]' "$OUTPUT_TMP"; then
    local CFG_ERR
    CFG_ERR=$(grep -m1 -oE '\[CONFIG_ERROR\].*' "$OUTPUT_TMP" | head -c 200)
    log "INGEST FAILED (config error): $CFG_ERR"
    rm -f "$OUTPUT_TMP"
    return 3
  fi

  # Count growth is the only direct proof the agent produced an artifact.
  # If sources/ grew, the ingest substantively succeeded — even if the final
  # wrap-up timed out (exit 124) or the SDK glued a trailing "API Error" into
  # stdout. Indirect signals (exit code, log grep) have produced false negatives
  # in this exact case, leaving artifacts on disk but watcher.state empty and
  # sync-and-rebuild un-triggered.
  local COUNT_AFTER
  COUNT_AFTER=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
  if [ "$COUNT_AFTER" -gt "$COUNT_BEFORE" ]; then
    # Half-write detection: count grew but log.md untouched → agent crashed before completing
    # workflow step 8. Treat as failure so the attempt can be retried with the next provider.
    local LOG_LINES_AFTER
    LOG_LINES_AFTER=$(wc -l < "$PROJECT_DIR/$WIKI_NAME/log.md" 2>/dev/null || echo 0)
    if [ "$LOG_LINES_AFTER" -le "$LOG_LINES_BEFORE" ]; then
      log "INGEST FAILED (partial: sources $COUNT_BEFORE → $COUNT_AFTER but log.md unchanged at $LOG_LINES_AFTER lines)"
      rm -f "$OUTPUT_TMP"
      return 1
    fi
    if [ "$EXIT_CODE" -ne 0 ]; then
      log "INGEST OK with non-zero exit ($EXIT_CODE) — sources $COUNT_BEFORE → $COUNT_AFTER, treating as success"
    elif grep -qE "API Error|status code [4-5][0-9][0-9]|connection error|ETIMEDOUT|ECONNRESET" "$OUTPUT_TMP"; then
      log "INGEST OK with trailing API/conn error in output — sources $COUNT_BEFORE → $COUNT_AFTER, treating as success"
    else
      log "INGEST VERIFIED OK (sources count: $COUNT_BEFORE → $COUNT_AFTER)"
    fi
    rm -f "$OUTPUT_TMP"
    return 0
  fi

  # Count unchanged → apply original failure checks to distinguish the cause.
  # Failure check 1: explicit error patterns in output
  if grep -qE "API Error|status code [4-5][0-9][0-9]|connection error|ETIMEDOUT|ECONNRESET" "$OUTPUT_TMP"; then
    local ERR
    ERR=$(grep -m1 -E "API Error|status code|connection" "$OUTPUT_TMP" | head -c 200)
    log "INGEST FAILED (api/connection error): $ERR"
    rm -f "$OUTPUT_TMP"
    return 1
  fi

  # Failure check 2: non-zero exit (incl. 124=timeout, 137=SIGKILL)
  if [ "$EXIT_CODE" -ne 0 ]; then
    if [ "$EXIT_CODE" -eq 124 ] || [ "$EXIT_CODE" -eq 137 ]; then
      log "INGEST FAILED (timeout 25m, exit $EXIT_CODE)"
    else
      log "INGEST FAILED (exit code $EXIT_CODE)"
    fi
    rm -f "$OUTPUT_TMP"
    return 1
  fi

  # Failure check 3: wiki/sources/ did not grow → no actual ingest happened
  # If the agent explicitly said this was a duplicate/skip, keep it out of failed state.
  if grep -q "DEDUP_SKIP:" "$OUTPUT_TMP"; then
    local DUP_LINE
    DUP_LINE=$(grep -m1 -oE 'DEDUP_SKIP: .*' "$OUTPUT_TMP" | head -c 200)
    log "INGEST SKIPPED (dedup signaled by agent): $DUP_LINE"
    rm -f "$OUTPUT_TMP"
    return 2
  fi
  if [ -n "$FETCH_FAIL_LINE" ]; then
    log "INGEST FAILED (source fetch): $FETCH_FAIL_LINE"
  else
    log "INGEST FAILED (sources count unchanged: $COUNT_BEFORE → $COUNT_AFTER)"
  fi
  rm -f "$OUTPUT_TMP"
  return 1
}

# Process one file with retry/backoff
process_file() {
  local FILE="$1"
  log "=== processing: $FILE ==="

  # Read explicit per-file override from frontmatter — if set, user is doing an A/B test
  # on a specific provider, so we do NOT walk the fallback chain (every attempt uses the
  # frontmatter provider, retry-as-is).
  local FRONT_PROVIDER
  FRONT_PROVIDER=$(awk '/^provider:/{print $2; exit}' "$FILE" 2>/dev/null)

  # Load fallback chain only when no explicit frontmatter override.
  # Format: providers/.fallback_chain = "deepseek,doubao,claude-opus,gemini" (one line).
  # attempt 1 uses .active (no flag), attempt 2..N walk CHAIN[0..].
  local FALLBACK_CHAIN_FILE="$PROJECT_DIR/providers/.fallback_chain"
  local -a CHAIN=()
  if [ -z "$FRONT_PROVIDER" ] && [ -f "$FALLBACK_CHAIN_FILE" ]; then
    local CHAIN_RAW
    CHAIN_RAW=$(tr -d '\n' < "$FALLBACK_CHAIN_FILE" | tr -d '[:space:]')
    if [ -n "$CHAIN_RAW" ]; then
      IFS=',' read -ra CHAIN <<< "$CHAIN_RAW"
    fi
  fi

  local attempt
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    # Per-attempt provider selection:
    #   attempt 1 → empty (loader uses .active or frontmatter PROVIDER inside ingest_one_file)
    #   attempt 2..N → CHAIN[attempt-2] if chain has enough entries, else last entry of chain.
    # If FRONT_PROVIDER is set, CHAIN is empty so this stays "" for all attempts (retry-as-is).
    local PROVIDER_FOR_ATTEMPT=""
    if [ "$attempt" -ge 2 ] && [ "${#CHAIN[@]}" -gt 0 ]; then
      local idx=$(( attempt - 2 ))
      if [ "$idx" -ge "${#CHAIN[@]}" ]; then
        idx=$(( ${#CHAIN[@]} - 1 ))
      fi
      PROVIDER_FOR_ATTEMPT="${CHAIN[$idx]}"
    fi

    if [ -n "$PROVIDER_FOR_ATTEMPT" ]; then
      log "attempt $attempt/$MAX_ATTEMPTS | provider=$PROVIDER_FOR_ATTEMPT (fallback chain)"
    else
      log "attempt $attempt/$MAX_ATTEMPTS"
    fi

    set +e
    ingest_one_file "$FILE" "$PROVIDER_FOR_ATTEMPT"
    local rc=$?
    set -e

    if [ "$rc" -eq 0 ]; then
      remove_from_failed "$FILE"
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
      remove_from_failed "$FILE"
      echo "$FILE" >> "$STATE_FILE"
      log "marked as processed (dedup skip) — no rebuild"
      return 0
    elif [ "$rc" -eq 3 ]; then
      # Config error — deterministic, do NOT retry / walk fallback chain.
      log "GIVING UP (config error, not retrying): $FILE"
      echo "$FILE" >> "$FAILED_FILE"
      return 1
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

    # Defense-in-depth: never process files under any */cancelled/* subpath
    case "$FILE" in
      */cancelled/*) continue ;;
    esac

    # skip if already verified-processed
    if grep -qxF "$FILE" "$STATE_FILE"; then
      continue
    fi

    log "detected new file: $FILE"
    sleep "$DEBOUNCE_SECONDS"

    process_file "$FILE" || true
  done
