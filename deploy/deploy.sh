#!/usr/bin/env bash
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}      Quran Tracker Bot - Deployment      ${NC}"
echo -e "${BLUE}==========================================${NC}"

# 1. Environment Validation
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[ERROR] Please run this script with sudo or as root.${NC}"
    exit 1
fi

WORKDIR=$(dirname $(dirname $(readlink -f "$0")))
CURRENT_USER=${SUDO_USER:-$(whoami)}
CURRENT_GROUP=$(id -gn $CURRENT_USER)

echo -e "${GREEN}[OK]${NC} Detected Workspace: $WORKDIR"
echo -e "${GREEN}[OK]${NC} Detected User: $CURRENT_USER:$CURRENT_GROUP"

# 2. Check for .venv
if [ ! -d "$WORKDIR/.venv" ]; then
    echo -e "${RED}[ERROR] Virtual environment not found. Please run setup.sh first.${NC}"
    exit 1
fi

# 3. Check for .env
if [ ! -f "$WORKDIR/.env" ]; then
    echo -e "${RED}[ERROR] .env file not found. Please create it and set your config.${NC}"
    exit 1
fi

# 4. Generate Systemd Service
echo -e "${BLUE}[INFO]${NC} Generating systemd service file..."
SERVICE_FILE="/etc/systemd/system/quran-bot.service"
sed -e "s|__USER__|$CURRENT_USER|g" \
    -e "s|__GROUP__|$CURRENT_GROUP|g" \
    -e "s|__WORKDIR__|$WORKDIR|g" \
    "$WORKDIR/deploy/quran-bot.service.template" > "$SERVICE_FILE"

echo -e "${GREEN}[OK]${NC} Service file created at $SERVICE_FILE"

# 5. Logrotate Configuration
echo -e "${BLUE}[INFO]${NC} Setting up log rotation..."
LOGROTATE_CONF="/etc/logrotate.d/quran-bot"
sed -e "s|__WORKDIR__|$WORKDIR|g" "$WORKDIR/deploy/logrotate.conf" > "$LOGROTATE_CONF"
echo -e "${GREEN}[OK]${NC} Log rotation configured."

# 6. Enable and Start Service
echo -e "${BLUE}[INFO]${NC} Reloading systemd daemon..."
systemctl daemon-reload

echo -e "${BLUE}[INFO]${NC} Enabling and starting quran-bot service..."
systemctl enable quran-bot.service
systemctl restart quran-bot.service

# 7. Final Healthcheck
sleep 2
if systemctl is-active --quiet quran-bot.service; then
    echo -e "${GREEN}[OK]${NC} Deployment successful! The bot is running."
    echo -e "Use ${YELLOW}sudo systemctl status quran-bot${NC} to check the status."
    echo -e "Use ${YELLOW}journalctl -u quran-bot -f${NC} to view live system logs."
else
    echo -e "${RED}[ERROR]${NC} Service failed to start. Check logs with 'systemctl status quran-bot'."
    exit 1
fi
