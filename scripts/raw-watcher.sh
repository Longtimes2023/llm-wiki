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

# Tests source this file as a library to call evaluate_ingest_output() directly.
# RAW_WATCHER_LIB_ONLY=1 suppresses filesystem setup, the lock acquisition, and
# the inotifywait main loop, so the test process does not collide with the real
# watcher service or block on inotify.
if [ "${RAW_WATCHER_LIB_ONLY:-0}" != "1" ]; then
  mkdir -p "$WATCH_DIR" "$SOURCES_DIR"
  touch "$LOG_FILE" "$STATE_FILE" "$FAILED_FILE"

  exec 9>"$LOCK_FILE"
  if ! flock -n 9; then
    printf '[%s] watcher already running, exiting\n' "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
    exit 0
  fi
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

# Inspect agent output and decide ingest success/failure.
# Return codes:
#   0 = verified success (artifact produced — sources count grew + log.md grew)
#   1 = real failure (api/conn/timeout/output unchanged with concrete fetch_fail)
#   2 = dedup skip (DEDUP_SKIP marker, or raw frontmatter declares duplicate)
#   3 = deterministic config error (do not retry — burns fallback chain)
# Sourced by tests via RAW_WATCHER_LIB_ONLY=1; pure logic, side effects limited
# to log/metrics/failures append + return code. Reads OUTPUT_TMP / FILE only.
evaluate_ingest_output() {
  local OUTPUT_TMP="$1"
  local FILE="$2"
  local EXIT_CODE="$3"
  local COUNT_BEFORE="$4"
  local COUNT_AFTER="$5"
  local LOG_LINES_BEFORE="$6"
  local LOG_LINES_AFTER="$7"

  cat "$OUTPUT_TMP" >> "$LOG_FILE"

  # Persist [METRICS] line emitted by 7_wiki_writer.py to ingest_metrics.jsonl for A/B aggregation.
  # New format: [METRICS_BEGIN]<compact json>[METRICS_END] — marker-delimited, single line.
  # Fall back to legacy [METRICS] {flat} for one cycle.
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

  # Capture [FETCH_FAIL] {...} marker. Real payload → append to ingest_failures.jsonl.
  # Placeholder template (agent leaked example payload on a successful digest) →
  # log + clear FETCH_FAIL_LINE so the final count-unchanged branch doesn't treat
  # a template leak as a real source-fetch failure. This is the central bug fix.
  local FETCH_FAIL_LINE
  FETCH_FAIL_LINE=$(grep -m1 -oE '\[FETCH_FAIL\] \{[^}]*\}' "$OUTPUT_TMP" 2>/dev/null \
                    | sed 's/^\[FETCH_FAIL\] //')
  if [ -n "$FETCH_FAIL_LINE" ]; then
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
      # Placeholder = agent template leak, NOT a real fetch failure. Clearing prevents
      # the count-unchanged failure branch from misreporting it as `(source fetch)`.
      FETCH_FAIL_LINE=""
    fi
  fi

  # Config error (deterministic): exit 2 + [CONFIG_ERROR] marker. Never retry —
  # a missing/invalid provider profile fails identically on every attempt.
  if [ "$EXIT_CODE" -eq 2 ] && grep -qF '[CONFIG_ERROR]' "$OUTPUT_TMP"; then
    local CFG_ERR
    CFG_ERR=$(grep -m1 -oE '\[CONFIG_ERROR\].*' "$OUTPUT_TMP" | head -c 200)
    log "INGEST FAILED (config error): $CFG_ERR"
    return 3
  fi

  # Count growth is the only direct proof the agent produced an artifact.
  # If sources/ grew, the ingest substantively succeeded — even if the wrap-up
  # timed out (exit 124) or the SDK glued a trailing "API Error" into stdout.
  if [ "$COUNT_AFTER" -gt "$COUNT_BEFORE" ]; then
    # Half-write detection: count grew but log.md untouched.
    # Distinguish two cases:
    #   - exit 124 (timeout)/137 (SIGKILL) → agent ran out of time before step 8.
    #     Source page IS the primary artifact and exists. Retry would re-do the
    #     same expensive work and likely timeout again. Accept as partial success,
    #     trigger sync. The missing log.md changelog entry is a cosmetic gap.
    #   - any other exit (0, generic non-zero) → agent crashed mid-flow.
    #     Retry might recover.
    if [ "$LOG_LINES_AFTER" -le "$LOG_LINES_BEFORE" ]; then
      if [ "$EXIT_CODE" -eq 124 ] || [ "$EXIT_CODE" -eq 137 ]; then
        log "INGEST OK with timeout (partial: sources $COUNT_BEFORE → $COUNT_AFTER, log.md unchanged — agent timeout-killed but source page created; accepting, log.md changelog skipped)"
        return 0
      fi
      log "INGEST FAILED (partial: sources $COUNT_BEFORE → $COUNT_AFTER but log.md unchanged at $LOG_LINES_AFTER lines)"
      return 1
    fi
    if [ "$EXIT_CODE" -ne 0 ]; then
      log "INGEST OK with non-zero exit ($EXIT_CODE) — sources $COUNT_BEFORE → $COUNT_AFTER, treating as success"
    elif grep -qE "API Error|status code [4-5][0-9][0-9]|connection error|ETIMEDOUT|ECONNRESET" "$OUTPUT_TMP"; then
      log "INGEST OK with trailing API/conn error in output — sources $COUNT_BEFORE → $COUNT_AFTER, treating as success"
    else
      log "INGEST VERIFIED OK (sources count: $COUNT_BEFORE → $COUNT_AFTER)"
    fi
    return 0
  fi

  # Count unchanged → apply failure checks to distinguish the cause.
  if grep -qE "API Error|status code [4-5][0-9][0-9]|connection error|ETIMEDOUT|ECONNRESET" "$OUTPUT_TMP"; then
    local ERR
    ERR=$(grep -m1 -E "API Error|status code|connection" "$OUTPUT_TMP" | head -c 200)
    log "INGEST FAILED (api/connection error): $ERR"
    return 1
  fi

  if [ "$EXIT_CODE" -ne 0 ]; then
    if [ "$EXIT_CODE" -eq 124 ] || [ "$EXIT_CODE" -eq 137 ]; then
      log "INGEST FAILED (timeout 40m, exit $EXIT_CODE)"
    else
      log "INGEST FAILED (exit code $EXIT_CODE)"
    fi
    return 1
  fi

  if grep -q "DEDUP_SKIP:" "$OUTPUT_TMP"; then
    local DUP_LINE
    DUP_LINE=$(grep -m1 -oE 'DEDUP_SKIP: .*' "$OUTPUT_TMP" | head -c 200)
    log "INGEST SKIPPED (dedup signaled by agent): $DUP_LINE"
    return 2
  fi

  # Raw frontmatter declares this file is a known duplicate (written by telegram_bot
  # when the URL matches a previously-ingested source). Agent correctly does NOT
  # regenerate wiki pages, so count stays flat. Without this check, the watcher
  # misclassifies the no-op as a real failure and retries until GIVE UP — exactly the
  # bug behind the placeholder FETCH_FAIL incident on raw stub 2026-05-20-190434-tg-43c47a.
  if head -30 "$FILE" 2>/dev/null | grep -qE '^(duplicate_of|already_digested_source):'; then
    log "INGEST SKIPPED (raw frontmatter declares duplicate): $(basename "$FILE")"
    return 2
  fi

  # Update-only success: agent updated existing pages without adding a new source/.
  # Source page existed before this attempt (count flat), but agent still ran step 8
  # to completion — log.md grew + metrics line captured + zero exit, no fetch_fail.
  # Without this branch, the watcher marks legitimate "entity/topic updates against
  # a pre-existing source page" as failure and never triggers sync-and-rebuild, so
  # Cloudflare stays stale and the bot tracker hangs waiting for the deploy marker.
  if [ "$EXIT_CODE" -eq 0 ] \
     && [ "$LOG_LINES_AFTER" -gt "$LOG_LINES_BEFORE" ] \
     && [ -n "$METRICS_LINE" ] \
     && [ -z "$FETCH_FAIL_LINE" ]; then
    log "INGEST OK (sources flat $COUNT_BEFORE → $COUNT_AFTER, log.md $LOG_LINES_BEFORE → $LOG_LINES_AFTER + metrics captured — agent updated existing pages)"
    return 0
  fi

  if [ -n "$FETCH_FAIL_LINE" ]; then
    log "INGEST FAILED (source fetch): $FETCH_FAIL_LINE"
  else
    log "INGEST FAILED (sources count unchanged: $COUNT_BEFORE → $COUNT_AFTER)"
  fi
  return 1
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

  # Read content_type from frontmatter (set by telegram_bot for multimodal routing).
  local CONTENT_TYPE
  CONTENT_TYPE=$(awk '/^content_type:/{print $2; exit}' "$FILE" 2>/dev/null)
  CONTENT_TYPE="${CONTENT_TYPE:-text}"

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
  # Resolve effective provider for this attempt: chain override > frontmatter override > content-type-aware default.
  local EFFECTIVE_PROVIDER=""
  if [ -n "$CHAIN_PROVIDER" ]; then
    EFFECTIVE_PROVIDER="$CHAIN_PROVIDER"
    log "ingest start | provider=$EFFECTIVE_PROVIDER (fallback chain) | content_type=$CONTENT_TYPE | sources count before: $COUNT_BEFORE"
  elif [ -n "$PROVIDER" ]; then
    EFFECTIVE_PROVIDER="$PROVIDER"
    log "ingest start | provider=$EFFECTIVE_PROVIDER (frontmatter override) | content_type=$CONTENT_TYPE | sources count before: $COUNT_BEFORE"
  else
    # No explicit provider: use content_type-aware resolution via loader.resolve_for_content().
    EFFECTIVE_PROVIDER=$("$PROJECT_DIR/.venv/bin/python" -c "
from providers.loader import resolve_for_content
p = resolve_for_content('$CONTENT_TYPE')
print(p['name'])
" 2>/dev/null) || EFFECTIVE_PROVIDER=""
    if [ -n "$EFFECTIVE_PROVIDER" ]; then
      log "ingest start | provider=$EFFECTIVE_PROVIDER (content_type=$CONTENT_TYPE) | sources count before: $COUNT_BEFORE"
    else
      log "ingest start | content_type=$CONTENT_TYPE | sources count before: $COUNT_BEFORE"
    fi
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
  # Hard cap per attempt: 40m. Without this, claude_agent_sdk hangs can block the
  # entire watcher queue (raw-watcher processes files sequentially via inotify pipe).
  # Set to 40m (was 25m) so skill-heavy ingest finishes naturally and emits METRICS
  # before being killed — articles with many entity/topic updates regularly run 25-35min.
  # Exit 124 = timeout reached, 137 = SIGKILL after grace. Treated as normal failure.
  timeout --kill-after=10s 40m \
    "$PROJECT_DIR/.venv/bin/python" -B 7_wiki_writer.py $PROVIDER_FLAG \
    --raw-file "$FILE" \
    -r "请消化这个新素材文件，文件路径是: $FILE。请运行 llm-wiki-skill 的 ingest 工作流。${AB_HINT}" \
    > "$OUTPUT_TMP" 2>&1
  local EXIT_CODE=$?
  set -e

  # Post-invocation state captured BEFORE handing off to evaluate_ingest_output.
  # COUNT_AFTER + LOG_LINES_AFTER are the canonical signals the evaluator uses
  # to distinguish verified success, half-write, and count-unchanged failure.
  local COUNT_AFTER LOG_LINES_AFTER
  COUNT_AFTER=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
  LOG_LINES_AFTER=$(wc -l < "$PROJECT_DIR/$WIKI_NAME/log.md" 2>/dev/null || echo 0)

  set +e
  evaluate_ingest_output \
    "$OUTPUT_TMP" \
    "$FILE" \
    "$EXIT_CODE" \
    "$COUNT_BEFORE" \
    "$COUNT_AFTER" \
    "$LOG_LINES_BEFORE" \
    "$LOG_LINES_AFTER"
  local rc=$?
  set -e

  rm -f "$OUTPUT_TMP"
  return "$rc"
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

      # Run sync (rsync, no AI). Pass the raw filename so sync-and-rebuild.sh
      # can emit `[sync] running: <basename>` and the telegram bot binds the
      # start signal to the right pending.
      if SYNC_RUN_HINT="$(basename "$FILE")" "$PROJECT_DIR/scripts/sync-and-rebuild.sh" >> "$LOG_FILE" 2>&1; then
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

if [ "${RAW_WATCHER_LIB_ONLY:-0}" != "1" ]; then
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
fi
