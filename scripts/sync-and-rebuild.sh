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
  echo "[$(date '+%F %T')] [sync] $*" | tee -a "$LOG_FILE"
}

if [ ! -d "$SRC_DIR" ]; then
  log "source not found: $SRC_DIR"
  exit 1
fi
if [ ! -d "$DST_DIR" ]; then
  log "destination not found: $DST_DIR"
  exit 1
fi

# Stage 1: rsync ai-wiki → quartz/content
log "syncing $SRC_DIR -> $DST_DIR"
rsync -a --delete \
  --exclude='.obsidian/' \
  --exclude='.git/' \
  --exclude='*.tmp' \
  "$SRC_DIR" "$DST_DIR" 2>&1 | tee -a "$LOG_FILE"
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

# Stage 3: clean Quartz cache + build static
log "building Quartz..."
cd "$QUARTZ_DIR"
rm -rf public .quartz-cache 2>/dev/null || true
if ! npx quartz build > /tmp/quartz-build.log 2>&1; then
  log "Quartz build FAILED — see /tmp/quartz-build.log"
  tail -20 /tmp/quartz-build.log >> "$LOG_FILE"
  exit 1
fi
build_files=$(find public -type f 2>/dev/null | wc -l)
log "Quartz build OK ($build_files files emitted)"

# Stage 4: deploy to Cloudflare Pages
log "deploying to Cloudflare Pages project=$CLOUDFLARE_PAGES_PROJECT"
if ! npx wrangler pages deploy public \
    --project-name="$CLOUDFLARE_PAGES_PROJECT" \
    --commit-dirty=true \
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
