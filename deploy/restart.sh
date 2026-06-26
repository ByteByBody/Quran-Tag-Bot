#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}[INFO]${NC} Restarting Quran Tracker Bot..."
sudo systemctl restart quran-bot.service

sleep 2

if systemctl is-active --quiet quran-bot.service; then
    echo -e "${GREEN}[OK]${NC} Bot restarted successfully!"
else
    echo -e "${RED}[ERROR]${NC} Bot failed to start. Check status:"
    sudo systemctl status quran-bot.service
fi
