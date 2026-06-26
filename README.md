# 📖 Quran Tracker Bot

A production-ready Telegram bot that helps Islamic groups maintain a daily Quran reading habit. The bot sends daily reading reminders, tracks participation, celebrates streaks, generates beautiful reports — all in Arabic.

---

## Features

- **Daily Quran post** — automated reminder with today's reading portion; message text rotates daily from a pool of motivational templates (never repeats two days in a row)
- **One-tap check-in** — members tap ✅ to confirm they completed their reading
- **Enhanced personal statistics** — streaks, monthly/yearly totals, estimated juz & pages read, average completions per week, best month, join date, and all earned badges
- **Daily report** — evening summary of participation (never publicly shames anyone)
- **Weekly report** — every Friday: participation trend vs the previous week, positive encouragement, never names who missed
- **Monthly report** — full summary with leaderboard, sent on the 1st of each month
- **Reading plans** — 1 juz/day, 2/5/10 pages/day, or fully custom
- **Admin panel** — admins control schedule, plan, timezone, and more via inline buttons
- **Achievement system** — 🌱 First Day · 🔥 7-day streak · 🌙 30 days · ⭐ 100 days · 💎 365 days · 📖 First full month · 🏅 One year in the group · 📚 50/100/200/365 total check-ins. Private DM on unlock, optional group announcement
- **Group milestones** — celebrate collective achievements: 100/500/1000/2500/5000 total check-ins, 10/50/100 complete khatmahs
- **Reminder system** — private DM reminders to members who haven't checked in, configurable times, multiple per day supported
- **Automatic backups** — daily backup with configurable retention
- **Full export** — CSV export of all check-in data
- **All text in one file** — edit `messages.py` to customise every Arabic string

---

## Requirements

- Python 3.11 or higher
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- Linux (tested on Ubuntu 22.04 / Linux Mint 21+)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/youruser/quran_tracker_bot.git
cd quran_tracker_bot
```

### 2. Create a Telegram bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. *Quran Tracker*)
4. Choose a username ending in `bot` (e.g. `quran_tracker_mygroup_bot`)
5. Copy the **token** BotFather gives you

### 3. Run setup

```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Check your Python version (3.11+)
- Create a virtual environment (`.venv/`)
- Install all dependencies
- Create `data/` and `logs/` directories
- Copy `.env.example` → `.env`
- Initialise the SQLite database (creates all tables including new v2 tables)
- Verify all modules import cleanly

### 4. Configure

Edit `.env`:

```ini
BOT_TOKEN=your_actual_token_here
TIMEZONE=Africa/Cairo
DEFAULT_POST_TIME=08:00
REPORT_TIME=22:00
ENABLE_WEEKLY_REPORT=true
ENABLE_BADGES=true
ENABLE_MILESTONES=true
ENABLE_REMINDERS=false
REMINDER_TIMES=20:00,21:30
```

### 5. Run locally

```bash
source .venv/bin/activate
python bot.py
```

---

## Configuration

All settings live in `.env`. See `.env.example` for full documentation.

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | *(required)* | BotFather token |
| `TIMEZONE` | `Africa/Cairo` | pytz timezone string |
| `DEFAULT_POST_TIME` | `08:00` | Time to send daily reminder |
| `REPORT_TIME` | `22:00` | Time to send evening report |
| `BACKUP_TIME` | `03:00` | Time to run automatic backup |
| `WEEKLY_REPORT_DAY` | `4` | Day weekly report fires (0=Mon … 4=Fri … 6=Sun) |
| `ENABLE_WEEKLY_REPORT` | `true` | Send weekly summary report |
| `ENABLE_BADGES` | `true` | Personal achievement notifications |
| `ANNOUNCE_BADGES` | `true` | Also announce badge unlocks in the group |
| `ENABLE_MILESTONES` | `true` | Group milestone announcements |
| `ENABLE_REMINDERS` | `false` | Private reminders to members who haven't checked in |
| `REMINDER_TIMES` | `20:00` | Comma-separated HH:MM reminder times |
| `ENABLE_RANDOM_VERSES` | `true` | Include a Quran verse in each daily post |
| `ENABLE_RANDOM_HADITH` | `false` | Include a hadith in each daily post |
| `ENABLE_RANDOM_DUA` | `false` | Include a dua in each daily post |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `BACKUP_RETAIN` | `7` | Number of backups to keep |

Per-group settings (post time, timezone, reading plan, reminder toggle) can be changed by group admins via `/settings` without editing `.env`.

---

## Commands

### General (everyone)

| Command | Description |
|---|---|
| `/start` | Start the bot / register the group |
| `/help` | Show help and command list |
| `/me` | Your enhanced personal statistics |
| `/stats` | Today's group participation |
| `/daily` | Post today's reading reminder now |
| `/report` | Show today's completion report |

### Admin only

| Command | Description |
|---|---|
| `/settings` | Open the settings panel |
| `/readingplan` | Change the reading plan |
| `/missing` | See who hasn't checked in (sent privately) |
| `/backup` | Create and download a database backup |
| `/restore` | Restore from a backup file |
| `/export` | Export all check-ins as CSV |
| `/reset_member @user` | Clear a member's history |
| `/reset_month` | Clear this month's check-ins |
| `/version` | Show bot version and stats |

---

## Achievement System

Achievements are evaluated automatically after every check-in. When unlocked:
1. The user receives a private DM congratulating them.
2. If `ANNOUNCE_BADGES=true` (or the per-group setting is on), an announcement is also sent in the group.

| Key | Badge | Condition |
|---|---|---|
| `first_day` | 🌱 اليوم الأول | First ever check-in |
| `streak_7` | 🔥 7 أيام | 7-day streak |
| `streak_30` | 🌙 30 يوماً | 30-day streak |
| `streak_100` | ⭐ 100 يوم | 100-day streak |
| `streak_365` | 💎 سنة كاملة | 365-day streak |
| `first_full_month` | 📖 أول شهر كامل | Complete every day of a calendar month |
| `one_year_member` | 🏅 سنة في المجموعة | 365 days since joining the group |
| `checkins_50` | 📚 50 ورداً | 50 total check-ins |
| `checkins_100` | 🎖️ 100 ورد | 100 total check-ins |
| `checkins_200` | 🏆 200 ورد | 200 total check-ins |
| `checkins_365` | 👑 365 ورداً | 365 total check-ins |

Adding new achievements only requires adding an entry to `ACHIEVEMENT_DEFINITIONS` in `messages.py` and a condition in `achievements.py:evaluate_user_achievements()`.

---

## Group Milestones

Collective milestones are announced in the group automatically.

| Milestone | Trigger |
|---|---|
| 🌱 100 total check-ins | Group reaches 100 combined check-ins |
| ⭐ 500 total check-ins | — |
| 🏆 1 000 total check-ins | — |
| 💎 2 500 total check-ins | — |
| 👑 5 000 total check-ins | — |
| 📖 10 khatmahs | Estimated 10 full Quran completions |
| 🌙 50 khatmahs | — |
| 🌟 100 khatmahs | — |

---

## Weekly Report

Sent automatically on the day configured by `WEEKLY_REPORT_DAY` (default: Friday). Includes:
- Active member count
- Total check-ins for the week
- Average daily participation percentage
- Trend vs the previous week (↑ improved / ↓ dipped / → stable)
- A rotating motivational message

Never names members who missed.

---

## Reminder System

When `ENABLE_REMINDERS=true`, the bot sends a private DM to any member who has **not** checked in by each time listed in `REMINDER_TIMES`. Multiple times can be set:

```ini
ENABLE_REMINDERS=true
REMINDER_TIMES=20:00,21:30
```

Each time slot uses a different reminder template from `messages.py` to avoid feeling repetitive. Reminders are silently skipped if the user has already checked in before the time fires.

---

## Dynamic Daily Posts

The daily message footer rotates through 10 motivational templates stored in `DAILY_MOTIVATION_TEMPLATES` in `messages.py`. The bot ensures the same template is never used two days in a row. The last-used index is stored per group in the database.

---

## Reading Plans

| Key | Arabic label | Description |
|---|---|---|
| `1_juz_day` | جزء يومياً | 1 juz per day (30-day Quran cycle) |
| `2_pages_day` | صفحتان يومياً | 2 pages per day |
| `5_pages_day` | 5 صفحات يومياً | 5 pages per day |
| `10_pages_day` | 10 صفحات يومياً | 10 pages per day |
| `custom` | مخصص | Admin sets a custom text |

---

## Customising Arabic Text

All Arabic strings are in `messages.py`. No other file contains Arabic text. Customisable pools:
- `DAILY_MOTIVATION_TEMPLATES` — daily post footer (10 entries)
- `WEEKLY_ENCOURAGEMENT_MESSAGES` — weekly report closer (7 entries)
- `REMINDER_TEMPLATES` — reminder DM text (5 entries)
- `QURAN_VERSES` — verse pool for daily posts (20 entries)
- `QURAN_HADITHS` — hadith pool (10 entries)
- `DAILY_DUAS` — dua pool (8 entries)
- `ACHIEVEMENT_DEFINITIONS` — badge names and descriptions
- `GROUP_MILESTONE_DEFINITIONS` — milestone thresholds and messages

---

## Database

SQLite database at `data/quran_tracker.db`.

### Tables

| Table | Purpose |
|---|---|
| `groups` | Registered groups |
| `users` | Users per group |
| `daily_checkins` | Each check-in event |
| `streaks` | Current and longest streak per user |
| `settings` | Per-group configuration (now includes reminder fields) |
| `reading_plans` | Available plan types |
| `daily_reports` | Evening report snapshots |
| `skipped_days` | Days marked as skipped by admins |
| `achievements` | User achievement records |
| `group_milestones` | Group milestone records |
| `last_motivation` | Last daily motivation index per group |

### Upgrading from v1

Run `./setup.sh` again — it applies safe `ALTER TABLE` migrations for the new `settings` columns and creates the three new tables without touching existing data.

---

## Deployment

### Option A: systemd (Ubuntu VPS)

```bash
sudo cp quran_bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/quran_bot.service  # set User= and WorkingDirectory=
sudo systemctl daemon-reload
sudo systemctl enable quran_bot
sudo systemctl start quran_bot
sudo journalctl -u quran_bot -f   # live logs
```

### Option B: Docker

```bash
docker compose up -d
docker compose logs -f
```

### Option C: Railway / Render

Push to GitHub, create a Background Worker, set environment variables from `.env`, set start command to `python bot.py`.

---

## Updating

```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt   # pick up any new deps
./setup.sh                         # runs migrations safely
sudo systemctl restart quran_bot
```

---

## Project Structure

```
quran_tracker_bot/
├── bot.py              Entry point — wires everything together
├── config.py           Loads and validates .env settings (feature flags)
├── database.py         Async SQLite layer — all SQL lives here
├── handlers.py         Telegram command & callback handlers
├── keyboards.py        Inline keyboard builders and CB constants
├── messages.py         ALL Arabic text, template pools, badge definitions
├── scheduler.py        Automated daily/weekly/monthly/reminder/backup jobs
├── achievements.py     Achievement & milestone engine (reusable)
├── utils.py            Statistics engine, date helpers, backup utilities
├── requirements.txt
├── setup.sh            One-command setup + migration script
├── .env.example        Configuration template (fully documented)
├── .gitignore
├── README.md
├── data/               SQLite DB + backups
└── logs/               Rotating log files
```

---

## Troubleshooting

**Reminders not arriving** — ensure the user has started a private conversation with the bot (Telegram requires this for DMs). Members can type `/start` to the bot privately.

**Achievements not announced** — check `ANNOUNCE_BADGES=true` in `.env` and that the per-group `announce_badges` setting is `1`.

**Weekly report not sent** — verify `ENABLE_WEEKLY_REPORT=true` and `WEEKLY_REPORT_DAY` matches the expected weekday integer. The job runs daily at 23:45 but only acts on the correct day.

**"Bot was blocked by the user" in logs** — normal when a user has blocked the bot for DMs; reminders and private achievement notifications are silently skipped for that user.

**Database locked error after crash**
```bash
rm data/quran_tracker.db-wal data/quran_tracker.db-shm
```

---

*بارك الله فيكم وجعلكم من أهل القرآن* 🤲
