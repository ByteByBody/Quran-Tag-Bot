#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

WORKDIR=$(dirname $(dirname $(readlink -f "$0")))
DB_PATH="$WORKDIR/data/quran_tracker.db"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}    Quran Tracker Bot - Health Check      ${NC}"
echo -e "${BLUE}==========================================${NC}"

# 1. Check Systemd Service Status
echo -n "Service Status: "
if systemctl is-active --quiet quran-bot.service; then
    echo -e "${GREEN}Running (Active)${NC}"
else
    echo -e "${RED}Not Running (Inactive/Failed)${NC}"
    exit 1
fi

# 2. Process Info (RAM & CPU)
MAIN_PID=$(systemctl show -p MainPID quran-bot.service | cut -d= -f2)
if [ "$MAIN_PID" -gt 0 ]; then
    echo -e "Main PID:       ${GREEN}$MAIN_PID${NC}"
    MEM_USAGE=$(ps -o rss= -p "$MAIN_PID" | awk '{print $1/1024 " MB"}')
    CPU_USAGE=$(ps -o %cpu= -p "$MAIN_PID")
    echo -e "RAM Usage:      ${GREEN}$MEM_USAGE${NC}"
    echo -e "CPU Usage:      ${GREEN}$CPU_USAGE%${NC}"
else
    echo -e "${RED}Process ID not found.${NC}"
fi

# 3. Database Check
echo -n "Database State: "
if [ -f "$DB_PATH" ]; then
    DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo -e "${GREEN}OK ($DB_SIZE)${NC}"
else
    echo -e "${RED}Missing at $DB_PATH${NC}"
fi

# 4. Check for Recent Errors in Logs
LOG_FILE="$WORKDIR/logs/bot.log"
if [ -f "$LOG_FILE" ]; then
    ERRORS_TODAY=$(grep "$(date +%Y-%m-%d)" "$LOG_FILE" | grep -c "ERROR" || true)
    if [ "$ERRORS_TODAY" -eq 0 ]; then
        echo -e "Errors Today:   ${GREEN}0${NC}"
    else
        echo -e "Errors Today:   ${RED}$ERRORS_TODAY${NC} (Check logs/bot.log)"
    fi
else
    echo -e "Errors Today:   ${YELLOW}Log file not found${NC}"
fi

echo -e "${BLUE}==========================================${NC}"
