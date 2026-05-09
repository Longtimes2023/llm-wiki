#!/bin/bash
# llm-wiki VPS setup — chạy trên Ubuntu 22.04+ tươi mới (root hoặc user có sudo).
#
# Usage:
#   git clone <your-fork-url> ~/llm-wiki
#   cd ~/llm-wiki
#   bash deploy/vps-setup.sh
#
# Idempotent: chạy lại nhiều lần OK. Sẽ skip step nào đã xong.

set -euo pipefail

# ---------- Resolve paths ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

# ---------- Colors ----------
RED=$'\033[0;31m'
GRN=$'\033[0;32m'
YLW=$'\033[1;33m'
NC=$'\033[0m'

ok() { echo "${GRN}[OK]${NC} $*"; }
info() { echo "${YLW}[..]${NC} $*"; }
err() { echo "${RED}[ERR]${NC} $*" >&2; }

# ---------- Sanity ----------
if [ "$EUID" -eq 0 ]; then
  err "Không chạy script này với root. Dùng user thường có sudo."
  err "  adduser llmwiki && usermod -aG sudo llmwiki && su - llmwiki"
  exit 1
fi

if ! command -v sudo >/dev/null; then
  err "sudo chưa cài. Trên VPS root: 'apt install -y sudo'"
  exit 1
fi

if [ ! -f "$PROJECT_DIR/pyproject.toml" ] || [ ! -f "$PROJECT_DIR/7_wiki_writer.py" ]; then
  err "Project không đúng. Expected pyproject.toml + 7_wiki_writer.py ở $PROJECT_DIR"
  exit 1
fi

info "Project dir: $PROJECT_DIR"
info "User: $USER  HOME: $HOME"

# ---------- Step 1: System packages ----------
info "[1/8] Cài system deps (apt)"
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
  git curl ca-certificates \
  build-essential pkg-config \
  inotify-tools rsync \
  python3 python3-venv python3-pip \
  >/dev/null
ok "apt deps installed"

# ---------- Step 2: uv (Python package manager) ----------
if ! command -v uv >/dev/null && [ ! -x "$HOME/.local/bin/uv" ]; then
  info "[2/8] Cài uv"
  curl -fsSL https://astral.sh/uv/install.sh | sh
else
  ok "[2/8] uv đã có"
fi
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || { err "uv install fail. Check ~/.local/bin trong PATH."; exit 1; }
uv --version

# ---------- Step 3: Node.js 22 (for Quartz + claude-code) ----------
NEED_NODE=1
if command -v node >/dev/null; then
  NODE_MAJOR=$(node -p "process.versions.node.split('.')[0]")
  if [ "$NODE_MAJOR" -ge 22 ]; then
    NEED_NODE=0
    ok "[3/8] Node v$NODE_MAJOR đã có (>=22)"
  fi
fi

if [ "$NEED_NODE" = "1" ]; then
  info "[3/8] Cài Node.js 22 (NodeSource)"
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - >/dev/null
  sudo apt-get install -y nodejs >/dev/null
  ok "node $(node --version)"
fi

NODE_BIN_DIR="$(dirname "$(command -v node)")"
NPM_GLOBAL_DIR="$HOME/.npm-global"

# Configure npm to install global packages without sudo.
if [ ! -d "$NPM_GLOBAL_DIR" ]; then
  mkdir -p "$NPM_GLOBAL_DIR"
  npm config set prefix "$NPM_GLOBAL_DIR"
fi
export PATH="$NPM_GLOBAL_DIR/bin:$PATH"

# ---------- Step 4: Claude Code CLI ----------
if ! command -v claude >/dev/null; then
  info "[4/8] Cài @anthropic-ai/claude-code"
  npm install -g @anthropic-ai/claude-code >/dev/null
  ok "claude $(claude --version 2>/dev/null || echo '?')"
else
  ok "[4/8] claude CLI đã có"
fi

# ---------- Step 5: Python venv + deps ----------
info "[5/8] uv sync (Python deps)"
cd "$PROJECT_DIR"
uv sync
ok "venv tại .venv/, deps installed"

# ---------- Step 6: .env ----------
ENV_FILE="$PROJECT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
  info "[6/8] Tạo .env từ .env.example (cần điền sau)"
  cp "$PROJECT_DIR/.env.example" "$ENV_FILE"
  echo
  echo "${YLW}>>> CHƯA xong: edit $ENV_FILE và điền các giá trị cần thiết:${NC}"
  echo "    - ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL, MODEL"
  echo "    - TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHAT_ID, QUARTZ_PUBLIC_BASE_URL"
  echo "    - (optional, nếu muốn auto-deploy Quartz từ VPS): CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_PAGES_PROJECT"
  echo
  echo "Xong rồi chạy lại: bash deploy/vps-setup.sh"
  exit 0
fi
ok "[6/8] .env đã có"

# Sanity: required vars present
set +e
. <(grep -E '^(ANTHROPIC_AUTH_TOKEN|TELEGRAM_BOT_TOKEN|TELEGRAM_ALLOWED_CHAT_ID)=' "$ENV_FILE" | sed 's/^/export /')
set -e

MISSING=()
[ -z "${ANTHROPIC_AUTH_TOKEN:-}" ] && MISSING+=("ANTHROPIC_AUTH_TOKEN")
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && MISSING+=("TELEGRAM_BOT_TOKEN")
[ -z "${TELEGRAM_ALLOWED_CHAT_ID:-}" ] && MISSING+=("TELEGRAM_ALLOWED_CHAT_ID")
if [ ${#MISSING[@]} -gt 0 ]; then
  err ".env thiếu: ${MISSING[*]}"
  err "Edit $ENV_FILE rồi chạy lại."
  exit 1
fi
ok ".env có đủ vars chính"

# ---------- Step 7: Render systemd units ----------
info "[7/8] Render systemd units → $SYSTEMD_USER_DIR"
mkdir -p "$SYSTEMD_USER_DIR"

render_unit() {
  local src="$1" dst="$2"
  sed -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
      -e "s|__HOME__|$HOME|g" \
      -e "s|__NODE_PATH__|$NPM_GLOBAL_DIR/bin:$NODE_BIN_DIR|g" \
      "$src" > "$dst"
  ok "wrote $dst"
}

render_unit \
  "$PROJECT_DIR/deploy/systemd/llm-wiki-telegram-bot.service.template" \
  "$SYSTEMD_USER_DIR/llm-wiki-telegram-bot.service"

render_unit \
  "$PROJECT_DIR/deploy/systemd/llm-wiki-watcher.service.template" \
  "$SYSTEMD_USER_DIR/llm-wiki-watcher.service"

systemctl --user daemon-reload

# ---------- Step 8: Enable lingering + start services ----------
info "[8/8] Bật lingering (services chạy không cần login)"
sudo loginctl enable-linger "$USER"

systemctl --user enable --now llm-wiki-watcher.service
systemctl --user enable --now llm-wiki-telegram-bot.service

sleep 2

echo
echo "─────────────────────────────────────────────"
ok "Xong! Status:"
systemctl --user status llm-wiki-watcher.service --no-pager -n 3 || true
echo
systemctl --user status llm-wiki-telegram-bot.service --no-pager -n 3 || true
echo
echo "─────────────────────────────────────────────"
echo "Logs realtime:"
echo "  journalctl --user -u llm-wiki-telegram-bot.service -f"
echo "  journalctl --user -u llm-wiki-watcher.service -f"
echo
echo "Hoặc tail file:"
echo "  tail -f $PROJECT_DIR/scripts/telegram_bot.log"
echo "  tail -f $PROJECT_DIR/scripts/watcher.log"
echo
echo "Test bằng cách gửi 1 URL từ Telegram tới bot."
