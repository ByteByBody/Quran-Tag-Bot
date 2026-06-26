#!/usr/bin/env bash
# ===========================================================================
# setup.sh — Quran Tracker Bot Setup Script
#
# Usage:  chmod +x setup.sh && ./setup.sh
# ===========================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'   # No colour

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Quran Tracker Bot — Setup Script v2   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Check Python version (≥ 3.11)
# ---------------------------------------------------------------------------
info "Checking Python version …"
PYTHON_CMD=""
for cmd in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    error "Python 3.11 or higher is required but was not found."
    error "Install it with: sudo apt install python3.11 python3.11-venv"
    exit 1
fi
success "Found Python $VER at $(which $PYTHON_CMD)"

# ---------------------------------------------------------------------------
# Step 2: Create virtual environment
# ---------------------------------------------------------------------------
VENV_DIR=".venv"
if [ -d "$VENV_DIR" ]; then
    warn "Virtual environment already exists at .venv — skipping creation."
else
    info "Creating virtual environment in .venv …"
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    success "Virtual environment created."
fi

# Activate
source "$VENV_DIR/bin/activate"
success "Virtual environment activated."

# ---------------------------------------------------------------------------
# Step 3: Upgrade pip and install requirements
# ---------------------------------------------------------------------------
info "Upgrading pip …"
pip install --quiet --upgrade pip

info "Installing Python packages from requirements.txt …"
pip install --quiet -r requirements.txt
success "All packages installed."

# ---------------------------------------------------------------------------
# Step 4: Create required directories
# ---------------------------------------------------------------------------
info "Creating data/ and logs/ directories …"
mkdir -p data/backups logs
success "Directories ready."

# ---------------------------------------------------------------------------
# Step 5: Copy .env.example → .env  (only if .env doesn't exist)
# ---------------------------------------------------------------------------
if [ -f ".env" ]; then
    warn ".env already exists — not overwriting."
else
    cp .env.example .env
    success "Copied .env.example → .env"
fi

# ---------------------------------------------------------------------------
# Step 6: Initialise the database
# ---------------------------------------------------------------------------
info "Initialising SQLite database …"
python - <<'PYEOF'
import asyncio, sys, pathlib
sys.path.insert(0, ".")
from database import Database
async def init():
    db = Database("data/quran_tracker.db")
    await db.init()
    await db.close()
asyncio.run(init())
PYEOF
success "Database initialised at data/quran_tracker.db"

# ---------------------------------------------------------------------------
# Step 6b: Verify all core modules import cleanly
# ---------------------------------------------------------------------------
info "Verifying module imports …"
python - <<'PYEOF'
import sys
sys.path.insert(0, ".")
errors = []
for mod in ["messages", "keyboards", "utils", "achievements"]:
    try:
        __import__(mod)
    except Exception as e:
        errors.append(f"{mod}: {e}")
if errors:
    for e in errors:
        print(f"  FAIL: {e}")
    sys.exit(1)
PYEOF
success "All modules import cleanly."

# ---------------------------------------------------------------------------
# Step 7: Verify .env has a real token
# ---------------------------------------------------------------------------
if grep -q "your_bot_token_here" .env; then
    warn "BOT_TOKEN is still the placeholder in .env"
    warn "Edit .env and set your real BotFather token before running the bot."
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║             ✅  Setup complete!                          ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Next steps:                                            ║"
echo "║                                                          ║"
echo "║  1. Edit .env and set your BOT_TOKEN                    ║"
echo "║     (get one from @BotFather on Telegram)               ║"
echo "║                                                          ║"
echo "║  2. Optionally adjust TIMEZONE, DEFAULT_POST_TIME, etc. ║"
echo "║                                                          ║"
echo "║  3. Activate the virtual environment:                   ║"
echo "║     source .venv/bin/activate                           ║"
echo "║                                                          ║"
echo "║  4. Run the bot:                                        ║"
echo "║     python bot.py                                       ║"
echo "║                                                          ║"
echo "║  5. Add the bot to your Telegram group and enjoy!       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
