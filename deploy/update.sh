#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKDIR=$(dirname $(dirname $(readlink -f "$0")))
DB_PATH="$WORKDIR/data/quran_tracker.db"
BACKUP_DIR="$WORKDIR/data/backups"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}     Quran Tracker Bot - Update Script    ${NC}"
echo -e "${BLUE}==========================================${NC}"

# 1. Pre-update Backup
echo -e "${BLUE}[INFO]${NC} Creating pre-update backup..."
mkdir -p "$BACKUP_DIR"
if [ -f "$DB_PATH" ]; then
    BACKUP_FILE="$BACKUP_DIR/update_backup_$(date +%Y%m%d_%H%M%S).db"
    cp "$DB_PATH" "$BACKUP_FILE"
    echo -e "${GREEN}[OK]${NC} Database backed up to $BACKUP_FILE"
else
    echo -e "${YELLOW}[WARN]${NC} No active database found to backup. Skipping."
fi

# 2. Pull Latest Code
echo -e "${BLUE}[INFO]${NC} Pulling latest changes from Git..."
cd "$WORKDIR"
git pull origin main || echo -e "${YELLOW}[WARN]${NC} Git pull failed or not a git repository. Proceeding anyway..."

# 3. Update Dependencies
echo -e "${BLUE}[INFO]${NC} Updating Python dependencies..."
if [ -d "$WORKDIR/.venv" ]; then
    "$WORKDIR/.venv/bin/pip" install -r requirements.txt --upgrade
    echo -e "${GREEN}[OK]${NC} Dependencies updated."
else
    echo -e "${RED}[ERROR]${NC} Virtual environment not found. Run setup.sh."
    exit 1
fi

# 4. Restart Service
echo -e "${BLUE}[INFO]${NC} Restarting service..."
if systemctl is-active --quiet quran-bot.service || systemctl is-failed --quiet quran-bot.service; then
    sudo systemctl restart quran-bot.service
    sleep 2
    if systemctl is-active --quiet quran-bot.service; then
        echo -e "${GREEN}[OK]${NC} Bot updated and restarted successfully."
    else
        echo -e "${RED}[ERROR]${NC} Bot failed to start after update. Check logs."
    fi
else
    echo -e "${YELLOW}[WARN]${NC} quran-bot.service not found. Was deploy.sh run?"
fi
