#!/bin/bash
# TC-D-lock: verify that sync-and-rebuild.sh refuses to run concurrently when
# its flock guard is held. Protects against bot fail-safe + raw-watcher race.
#
# Run: bash scripts/tests/test_sync_lock.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SYNC_SCRIPT="$PROJECT_DIR/scripts/sync-and-rebuild.sh"

if [ ! -x "$SYNC_SCRIPT" ] && [ ! -f "$SYNC_SCRIPT" ]; then
  echo "FAIL: sync-and-rebuild.sh not found at $SYNC_SCRIPT"
  exit 2
fi

PASS=0; FAIL=0
pass() { PASS=$((PASS+1)); echo "  PASS: $*"; }
fail() { FAIL=$((FAIL+1)); echo "  FAIL: $*"; }

LOCKFILE="$(mktemp -u /tmp/llm-wiki-sync-test-XXXXXX.lock)"
trap 'rm -f "$LOCKFILE"' EXIT

# Hold the lock in a background process for 5s. Second invocation must
# exit 0 quickly (the "skipped" branch). Without the flock guard, the second
# call would proceed and the test takes much longer / produces both runs.
( exec 200>"$LOCKFILE"; flock 200; sleep 5 ) &
HOLDER_PID=$!
sleep 0.3  # let the holder grab the lock

echo "::: concurrent invocation should exit 0 silently within 2s"
START=$(date +%s%N)
OUT="$(SYNC_LOCKFILE="$LOCKFILE" bash "$SYNC_SCRIPT" 2>&1)" || true
END=$(date +%s%N)
ELAPSED_MS=$(( (END - START) / 1000000 ))

if [ "$ELAPSED_MS" -lt 2000 ]; then
  pass "concurrent invocation returned in ${ELAPSED_MS}ms (< 2000ms)"
else
  fail "concurrent invocation took ${ELAPSED_MS}ms (expected < 2000ms — lock not working?)"
fi

if echo "$OUT" | grep -q "skipped: another sync already holds"; then
  pass "skip marker logged: another sync already holds"
else
  fail "skip marker not found in output; got:
$OUT"
fi

wait "$HOLDER_PID" 2>/dev/null || true

echo ""
echo "================================"
echo "PASS=$PASS  FAIL=$FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "ALL GREEN"
  exit 0
else
  exit 1
fi
