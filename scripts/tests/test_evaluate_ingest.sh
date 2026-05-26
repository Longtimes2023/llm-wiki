#!/bin/bash
# Regression tests for evaluate_ingest_output() in scripts/raw-watcher.sh.
# Covers the placeholder [FETCH_FAIL] leak bug: agent sometimes emits the
# template payload {"source_id":"真实来源ID",...} even on successful digests;
# without proper handling the watcher mistakes it for a real source-fetch
# failure and retries until GIVE UP.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PASS=0
FAIL=0
FAILURES=()

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    PASS=$(( PASS + 1 ))
    echo "  PASS: $label"
  else
    FAIL=$(( FAIL + 1 ))
    FAILURES+=("$label: expected=[$expected] actual=[$actual]")
    echo "  FAIL: $label — expected=[$expected] actual=[$actual]"
  fi
}

# Isolated project tree per test so sourcing raw-watcher.sh does not clobber
# the user's real watcher state (locks, log, state, failed list).
make_tmp_project() {
  local TMPDIR
  TMPDIR=$(mktemp -d)
  mkdir -p "$TMPDIR/scripts" \
           "$TMPDIR/ai-wiki/raw/articles" \
           "$TMPDIR/ai-wiki/wiki/sources"
  : > "$TMPDIR/ai-wiki/log.md"
  echo "$TMPDIR"
}

# Source raw-watcher.sh into the current shell with the main inotify loop
# suppressed, so we can call evaluate_ingest_output() directly with synthetic
# arguments. The watcher must honor RAW_WATCHER_LIB_ONLY=1 for this hook.
source_watcher_as_lib() {
  local PROJ="$1"
  PROJECT_DIR="$PROJ" RAW_WATCHER_LIB_ONLY=1 source "$REPO_ROOT/scripts/raw-watcher.sh"
}

run_case() {
  local NAME="$1"
  local RAW_FILE="$2"
  local OUTPUT_TMP="$3"
  local EXIT_CODE="$4"
  local COUNT_BEFORE="$5"
  local COUNT_AFTER="$6"
  local LOG_LINES_BEFORE="$7"
  local LOG_LINES_AFTER="$8"
  local EXPECTED_RC="$9"
  local EXPECTED_FAILURES_APPENDED="${10}"

  echo "::: $NAME"

  # Side-effect target: writer appends one line per real fetch fail to this file.
  : > "$PROJECT_DIR/scripts/ingest_failures.jsonl"

  set +e
  evaluate_ingest_output \
    "$OUTPUT_TMP" \
    "$RAW_FILE" \
    "$EXIT_CODE" \
    "$COUNT_BEFORE" \
    "$COUNT_AFTER" \
    "$LOG_LINES_BEFORE" \
    "$LOG_LINES_AFTER" \
    > /dev/null
  local RC=$?
  set -e

  assert_eq "$NAME: return code" "$EXPECTED_RC" "$RC"

  local APPENDED_LINES
  APPENDED_LINES=$(wc -l < "$PROJECT_DIR/scripts/ingest_failures.jsonl" | tr -d ' ')
  assert_eq "$NAME: ingest_failures.jsonl lines appended" \
            "$EXPECTED_FAILURES_APPENDED" "$APPENDED_LINES"
}

# ---------------------------------------------------------------------------
# Test 1 — Placeholder FETCH_FAIL + raw file marked duplicate_of in frontmatter.
# Sources count unchanged is the EXPECTED outcome (agent correctly skipped a
# known-duplicate raw stub). Watcher must return 2 (dedup), not 1 (failure),
# so the dispatcher does not retry and Telegram does not get a false failure.
# ---------------------------------------------------------------------------
TC1_PROJ=$(make_tmp_project)
PROJECT_DIR="$TC1_PROJ"
source_watcher_as_lib "$TC1_PROJ"

TC1_RAW="$TC1_PROJ/ai-wiki/raw/articles/dup.md"
cat > "$TC1_RAW" <<'RAW'
---
source_url: https://example.com/dup
duplicate_of: raw/articles/example.com/dup.md
already_digested_source: wiki/sources/2026-05-20-example.md
---
# stub
RAW

TC1_OUT=$(mktemp)
cat > "$TC1_OUT" <<'OUT'
... agent narrative ...
[FETCH_FAIL] {"source_id":"真实来源ID","url":"真实原始URL","status":"真实单一状态值","reason":"真实一句话原因"}

[METRICS_BEGIN]{"provider":"sonnet","raw_file":"dup.md","cost_usd":0.005}[METRICS_END]
OUT

run_case "placeholder + duplicate_of frontmatter -> dedup skip" \
  "$TC1_RAW" "$TC1_OUT" 0 5 5 10 10 2 0

# ---------------------------------------------------------------------------
# Test 2 — Real FETCH_FAIL with concrete payload + no duplicate_of frontmatter.
# Watcher MUST keep returning 1 (retry) AND append one line to ingest_failures.
# This guards against the fix being overzealous.
# ---------------------------------------------------------------------------
TC2_PROJ=$(make_tmp_project)
PROJECT_DIR="$TC2_PROJ"
source_watcher_as_lib "$TC2_PROJ"

TC2_RAW="$TC2_PROJ/ai-wiki/raw/articles/real.md"
cat > "$TC2_RAW" <<'RAW'
---
source_url: https://www.woshipm.com/pmd/9999.html
captured_via: telegram_bot
---
# pending fetch
RAW

TC2_OUT=$(mktemp)
cat > "$TC2_OUT" <<'OUT'
... agent narrative ...
[FETCH_FAIL] {"source_id":"woshipm.com/pmd/9999","url":"https://www.woshipm.com/pmd/9999.html","status":"403","reason":"paywall blocks fetch"}

[METRICS_BEGIN]{"provider":"sonnet","raw_file":"real.md","cost_usd":0.005}[METRICS_END]
OUT

run_case "real fetch_fail payload -> retry" \
  "$TC2_RAW" "$TC2_OUT" 0 5 5 10 10 1 1

# ---------------------------------------------------------------------------
# Test 3 — Placeholder FETCH_FAIL but no duplicate_of frontmatter and sources
# count unchanged. This is ambiguous: agent leaked the template but did not
# produce wiki output. Watcher should still treat as failure (return 1) but
# MUST NOT append the placeholder to ingest_failures.jsonl.
# ---------------------------------------------------------------------------
TC3_PROJ=$(make_tmp_project)
PROJECT_DIR="$TC3_PROJ"
source_watcher_as_lib "$TC3_PROJ"

TC3_RAW="$TC3_PROJ/ai-wiki/raw/articles/ambig.md"
cat > "$TC3_RAW" <<'RAW'
---
source_url: https://example.com/new
captured_via: telegram_bot
---
# fresh article
RAW

TC3_OUT=$(mktemp)
cat > "$TC3_OUT" <<'OUT'
... agent narrative ...
[FETCH_FAIL] {"source_id":"真实来源ID","url":"真实原始URL","status":"真实单一状态值","reason":"真实一句话原因"}

[METRICS_BEGIN]{"provider":"sonnet","raw_file":"ambig.md","cost_usd":0.005}[METRICS_END]
OUT

run_case "placeholder without duplicate frontmatter -> retry but no failures.jsonl append" \
  "$TC3_RAW" "$TC3_OUT" 0 5 5 10 10 1 0

# ---------------------------------------------------------------------------
# Test 4 — Update-only success: source page existed before the run (count flat),
# but agent ran step 8 to completion: log.md grew, metrics captured, exit 0, no
# fetch_fail. Watcher MUST return 0 so the dispatcher triggers sync-and-rebuild
# and the deploy marker reaches the bot. This is the bug for raw stub
# 2026-05-26-081646-tg-8891da.md: agent updated existing pages, watcher kept
# misclassifying it as failure → sync never ran → Cloudflare stale → bot timed
# out after 30 minutes waiting on a marker that was never going to arrive.
# ---------------------------------------------------------------------------
TC4_PROJ=$(make_tmp_project)
PROJECT_DIR="$TC4_PROJ"
source_watcher_as_lib "$TC4_PROJ"

TC4_RAW="$TC4_PROJ/ai-wiki/raw/articles/update-only.md"
cat > "$TC4_RAW" <<'RAW'
---
source_url: https://example.com/existing
captured_via: telegram_bot
---
# stub for previously-ingested URL
RAW

TC4_OUT=$(mktemp)
cat > "$TC4_OUT" <<'OUT'
... agent narrative: source page already exists, updating related entities ...
[METRICS_BEGIN]{"provider":"sonnet","raw_file":"update-only.md","cost_usd":0.18}[METRICS_END]
OUT

run_case "update-only success: log.md grew, metrics present, no fetch_fail -> rc=0" \
  "$TC4_RAW" "$TC4_OUT" 0 75 75 100 110 0 0

# ---------------------------------------------------------------------------
# Test 5 — Defense in depth: log.md grew but agent exited non-zero. Must still
# return 1 (the non-zero-exit branch wins; we do NOT promote a half-completed
# crash to a success just because step 8 happened to flush).
# ---------------------------------------------------------------------------
TC5_PROJ=$(make_tmp_project)
PROJECT_DIR="$TC5_PROJ"
source_watcher_as_lib "$TC5_PROJ"

TC5_RAW="$TC5_PROJ/ai-wiki/raw/articles/half-crash.md"
cat > "$TC5_RAW" <<'RAW'
---
source_url: https://example.com/half
captured_via: telegram_bot
---
RAW

TC5_OUT=$(mktemp)
cat > "$TC5_OUT" <<'OUT'
... agent narrative ...
[METRICS_BEGIN]{"provider":"sonnet","raw_file":"half-crash.md"}[METRICS_END]
OUT

run_case "non-zero exit overrides log.md growth -> rc=1" \
  "$TC5_RAW" "$TC5_OUT" 1 75 75 100 110 1 0

# ---------------------------------------------------------------------------
# Test 6 — Defense in depth: log.md grew, exit 0, but METRICS_LINE missing.
# Agent never reached its epilogue print → treat as failure so retry can happen.
# ---------------------------------------------------------------------------
TC6_PROJ=$(make_tmp_project)
PROJECT_DIR="$TC6_PROJ"
source_watcher_as_lib "$TC6_PROJ"

TC6_RAW="$TC6_PROJ/ai-wiki/raw/articles/no-metrics.md"
cat > "$TC6_RAW" <<'RAW'
---
source_url: https://example.com/no-metrics
captured_via: telegram_bot
---
RAW

TC6_OUT=$(mktemp)
cat > "$TC6_OUT" <<'OUT'
... agent narrative, never printed METRICS epilogue ...
OUT

run_case "no metrics line -> rc=1 even if log.md grew" \
  "$TC6_RAW" "$TC6_OUT" 0 75 75 100 110 1 0

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo
echo "================================"
echo "PASS=$PASS  FAIL=$FAIL"
if [ "$FAIL" -gt 0 ]; then
  echo "FAILURES:"
  for f in "${FAILURES[@]}"; do echo "  - $f"; done
  exit 1
fi
echo "ALL GREEN"
