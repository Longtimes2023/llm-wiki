#!/bin/bash
# Sync ai-wiki → quartz/content, build, and auto-deploy to Cloudflare Pages.
# Triggered by raw-watcher.sh after each successful ingest.
set -euo pipefail

# Derive project dir from script location (works on any host).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(dirname "$SCRIPT_DIR")}"
SRC_DIR="$PROJECT_DIR/ai-wiki/"
DST_DIR="$PROJECT_DIR/quartz/content/"
QUARTZ_DIR="$PROJECT_DIR/quartz"
LOG_FILE="$PROJECT_DIR/scripts/watcher.log"
ENV_FILE="$PROJECT_DIR/.env"

log() {
  # raw-watcher.sh invokes this script with `>> "$LOG_FILE" 2>&1`, so a plain
  # stdout echo already persists. Adding `tee -a "$LOG_FILE"` here would write
  # every line twice. Just echo.
  echo "[$(date '+%F %T')] [sync] $*"
}

if [ ! -d "$SRC_DIR" ]; then
  log "source not found: $SRC_DIR"
  exit 1
fi
if [ ! -d "$DST_DIR" ]; then
  log "destination not found: $DST_DIR"
  exit 1
fi

# Single-writer guard. Bot fail-safe and raw-watcher can both invoke this
# script; flock prevents concurrent rsync/build/deploy races. If the lock is
# already held, log and exit 0 silently — the in-flight sync covers this run.
LOCKFILE="${SYNC_LOCKFILE:-/tmp/llm-wiki-sync.lock}"
exec 200>"$LOCKFILE"
if ! flock -n 200; then
  log "skipped: another sync already holds $LOCKFILE"
  exit 0
fi

# Explicit start marker — telegram_bot.RE_SYNC_RUNNING binds this to the
# current pending and shows the user "đang sync vào Quartz". Hint is either
# the raw file basename (when invoked via raw-watcher) or "manual" (direct).
RUN_HINT="${SYNC_RUN_HINT:-manual}"
log "running: $RUN_HINT"

# Stage 0: orphan rescue — files that exist in quartz/content/ but not in ai-wiki/
# would be wiped by rsync --delete. If any future code path writes only to quartz,
# this guard rescues those files back to ai-wiki/ before the destructive rsync runs.
# Excludes _quarantine/ (intentionally one-sided).
log "scanning for orphans (quartz-only files)"
orphan_count=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  src_target="$SRC_DIR$f"
  mkdir -p "$(dirname "$src_target")"
  cp -p "$DST_DIR$f" "$src_target"
  log "WARN: orphan rescued from quartz/content/: $f"
  orphan_count=$((orphan_count+1))
done < <(comm -23 \
  <(cd "$DST_DIR" && find . -type f -name '*.md' \
      ! -path './_quarantine/*' \
      ! -path './.obsidian/*' \
      ! -path './.git/*' \
      | sed 's|^\./||' | sort) \
  <(cd "$SRC_DIR" && find . -type f -name '*.md' \
      ! -path './_quarantine/*' \
      ! -path './.obsidian/*' \
      ! -path './.git/*' \
      | sed 's|^\./||' | sort))
if [ "$orphan_count" -gt 0 ]; then
  log "orphan rescue: $orphan_count file(s) copied back to ai-wiki/"
fi

# Stage 1: rsync ai-wiki → quartz/content
log "syncing $SRC_DIR -> $DST_DIR"
rsync -a --delete \
  --exclude='.obsidian/' \
  --exclude='.git/' \
  --exclude='*.tmp' \
  --exclude='_quarantine/' \
  "$SRC_DIR" "$DST_DIR" 2>&1
log "rsync done"

# Stage 2: load Cloudflare credentials from .env (skip deploy if missing)
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source <(grep -E '^[[:space:]]*(CLOUDFLARE_|ANTHROPIC_)' "$ENV_FILE" | sed 's/^[[:space:]]*//')
  set +a
fi

if [ -z "${CLOUDFLARE_API_TOKEN:-}" ] || [ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ] || [ -z "${CLOUDFLARE_PAGES_PROJECT:-}" ]; then
  log "Cloudflare credentials missing in .env, skipping deploy"
  exit 0
fi

# Stage 3: clean Quartz cache + build static (with quarantine + retry on YAML failures)
log "building Quartz..."
cd "$QUARTZ_DIR"
rm -rf public .quartz-cache 2>/dev/null || true

# Quarantine lives source-side (ai-wiki/_quarantine/) so it's persistent across syncs.
# rsync excludes _quarantine/ both directions, so it never bounces between trees.
QUARANTINE_DIR="${SRC_DIR}_quarantine"
mkdir -p "$QUARANTINE_DIR"
QUARANTINED=()
BUILD_OK=0
for q_attempt in 1 2 3; do
  if npx quartz build > /tmp/quartz-build.log 2>&1; then
    BUILD_OK=1
    break
  fi
  # Quartz error format (verified from historic logs):
  #   Failed to process markdown `content/wiki/topics/<file>.md`: bad indentation ...
  # Path is wrapped in backticks; may contain CJK + spaces. Extract between backticks.
  # `|| true` is load-bearing: under `set -euo pipefail`, grep returning 1 (no match)
  # would kill the script silently before the "can't identify offending file" log
  # below ever runs. The conditional below handles the empty-string case.
  BAD_FILE_REL=$(grep -oE '`content/[^`]+\.md`' /tmp/quartz-build.log | head -1 | tr -d '`' || true)
  if [ -z "$BAD_FILE_REL" ] || [ ! -f "$QUARTZ_DIR/$BAD_FILE_REL" ]; then
    log "Quartz build FAILED (attempt $q_attempt) — can't identify offending file, giving up"
    tail -20 /tmp/quartz-build.log >> "$LOG_FILE"
    exit 1
  fi
  # Strip leading "content/" → relative path inside ai-wiki/ and inside _quarantine/.
  rel_inside="${BAD_FILE_REL#content/}"
  src_path="$SRC_DIR$rel_inside"
  q_target="$QUARANTINE_DIR/$rel_inside"
  log "quarantining $rel_inside (Quartz build error, attempt $q_attempt)"
  mkdir -p "$(dirname "$q_target")"
  # Prefer moving the source-side file (the actual offender). Fall back to copying from
  # quartz if source has been mutated since rsync (shouldn't happen, defensive).
  if [ -f "$src_path" ]; then
    mv "$src_path" "$q_target"
  else
    cp "$QUARTZ_DIR/$BAD_FILE_REL" "$q_target"
  fi
  # Remove the broken copy from quartz so the next build attempt succeeds.
  rm -f "$QUARTZ_DIR/$BAD_FILE_REL"
  QUARANTINED+=("$rel_inside")
done

if [ "$BUILD_OK" -ne 1 ]; then
  log "Quartz build FAILED after 3 quarantine attempts, giving up"
  exit 1
fi

if [ "${#QUARANTINED[@]}" -gt 0 ]; then
  log "quarantined ${#QUARANTINED[@]} file(s): ${QUARANTINED[*]}"
  # Append a single audit entry to ai-wiki/log.md so operator can review later.
  {
    echo ""
    echo "## $(date '+%F') quarantine | Quartz build YAML errors"
    echo ""
    for q in "${QUARANTINED[@]}"; do
      echo "- \`$q\` → moved to \`ai-wiki/_quarantine/\` (fix YAML rồi mv lại vị trí cũ để re-ingest)"
    done
    echo ""
    echo "---"
  } >> "$SRC_DIR/log.md"
fi
build_files=$(find public -type f 2>/dev/null | wc -l)
log "Quartz build OK ($build_files files emitted)"

# Stage 4: deploy to Cloudflare Pages
log "deploying to Cloudflare Pages project=$CLOUDFLARE_PAGES_PROJECT"
# Use explicit ASCII commit message — Cloudflare API rejects some unicode (e.g. → arrow,
# long multi-paragraph bodies) with "Invalid commit message, must be valid UTF-8 string"
# even when the git log message is technically valid UTF-8. Git short hash gives traceability.
DEPLOY_MSG="auto-deploy from raw-watcher ($(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown))"
if ! npx wrangler pages deploy public \
    --project-name="$CLOUDFLARE_PAGES_PROJECT" \
    --commit-dirty=true \
    --commit-message="$DEPLOY_MSG" \
    --branch=main \
    > /tmp/cf-deploy.log 2>&1; then
  log "Cloudflare deploy FAILED — see /tmp/cf-deploy.log"
  tail -10 /tmp/cf-deploy.log >> "$LOG_FILE"
  exit 1
fi

# Extract deployment URL
deploy_url=$(grep -oE 'https://[^[:space:]]*\.pages\.dev' /tmp/cf-deploy.log | tail -1 || echo "")
log "deployed: $deploy_url"
log "production URL: https://$CLOUDFLARE_PAGES_PROJECT.pages.dev/"
