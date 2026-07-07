# Quran Tracker Bot

A Telegram bot that helps groups track their daily Quran reading (الورد اليومي) with check-ins, streaks, leaderboards, and smart scheduling aligned with the Islamic (Hijri) calendar.

## Why Quran Tracker?

Managing daily Quran reading across a community can be difficult. Quran Tracker automates reading schedules, check-ins, reminders, statistics, and progress tracking so groups can stay consistent with minimal admin effort.

## Features

### 📖 Daily Reading Post
- Automatically sends today's assigned reading to the group at the configured time
- Reading plans: **1 juz/day**, **2 pages/day**, **5 pages/day**, **10 pages/day**, or custom
- Reading cycle follows the **Hijri calendar** — resets every Muharram, automatically handles carry-over when a 29-day month ends (next month starts at the missing juz)
- Optional daily verse, hadith, and dua appended to each post
- Rotating motivational text (no repeats two days in a row)

### ✅ Check-in System
- One tap to mark today's reading as done via inline button
- Streak tracking (current and longest)
- Private DM confirmation with streak badge
- Prevents duplicate check-ins

### 📊 Statistics & Reports
- **Daily report** — participation count sent automatically at configured time
- **Weekly report** — trends, averages, and encouragement
- **Monthly report** — full summary on the 1st of each month (Gregorian)
- **Personal stats** (`/me`) — streak, total check-ins, estimated juz/pages read
- **Leaderboard** (`/leaderboard`) — monthly or all-time rankings
- **Missing list** (`/missing`) — see who hasn't checked in yet (admins only)

### 🏅 Achievements & Milestones
- Badges awarded for check-in milestones (e.g., 10, 30, 100, 365 days)
- Group-wide milestone announcements configurable
- Each user can view their earned badges in their stats

### 🔔 Reminders
- Private DM reminders to members who haven't checked in yet
- Up to 3 configurable reminder times per group
- Multiple reminder messages (rotated daily)

### ⚙️ Per-Group Settings
All settings are configurable per group by admins via the settings menu:

| Setting | Description |
|---|---|
| وقت الورد (Post Time) | Time for the daily reading post (per-group timezone) |
| وقت التقرير (Report Time) | Time for the daily participation report |
| وقت التذكير (Reminder Time) | One or more reminder times (comma-separated) |
| المنطقة الزمنية (Timezone) | Group's local timezone (e.g., `Asia/Riyadh`) |
| خطة القراءة (Reading Plan) | Choose reading plan or set custom text |
| ضبط الجزء (Set Juz) | Override today's juz (auto-resets after posting) |
| التقويم الهجري (Hijri Date) | Toggle between Gregorian and Hijri date display |
| التقرير اليومي (Daily Report) | Enable/disable the daily report |
| التقرير الأسبوعي (Weekly Report) | Enable/disable the weekly report |
| الإنجازات (Milestones) | Enable/disable milestone announcements |
| الآية اليومية (Daily Verse) | Toggle verse in daily post |
| الحديث اليومي (Daily Hadith) | Toggle hadith in daily post |
| الدعاء اليومي (Daily Dua) | Toggle dua in daily post |
| التذكير (Reminder) | Enable/disable reminder DMs |
| إعلان الشارات (Badge Announcements) | Announce badges in the group |

### 🛠 Admin Commands
| Command | Description |
|---|---|
| `/settings` | Open group settings (admin only) |
| `/group` | Choose which group to manage |
| `/readingplan` | Quick-change reading plan |
| `/daily` | Preview today's reading |
| `/report` | See today's participation report |
| `/missing` | List members not checked in |
| `/force_daily` | Manually send the daily post (in settings) |
| `/skip_day` | Mark today as skipped (no post/report) |
| `/reset_month` | Reset current month's stats |
| `/reset_member` | Reset a specific member's stats |
| `/backup` / `/restore` | Database backup and restore |
| `/export` | Export group data |

### 👤 User Commands
| Command | Description |
|---|---|
| `/start` | Start the bot and get the main menu |
| `/menu` | Show the rich main menu |
| `/me` | View your personal statistics (DM) |
| `/checkin` | Check in for today's reading |
| `/leaderboard` | View the leaderboard |
| `/stats` | View group participation stats |
| `/help` | Help and command list |
| `/version` | Bot information |

## How the Reading Cycle Works

The reading cycle follows the **Hijri (Islamic) calendar**:

- **1 Muharram** → Juz 1
- Each day advances by one juz
- Muharram (30 days) covers juz 1–30
- 1 Safar → Juz 1 (normal reset after full month)
- If the previous month had **29 days** (e.g., Safar), only juz 1–29 were covered, so 1 Rabi' al-Awwal → **Juz 30** (carry-over)
- The cycle auto-resets every Hijri year (Muharram 1)

Admins can temporarily override today's juz using the "ضبط الجزء" button. The override is consumed after the daily post is sent.

## Technology Stack

- **Python 3.10+** — core language
- **python-telegram-bot v20+** — Telegram Bot API framework
- **aiosqlite** — async SQLite database
- **APScheduler** (via `python-telegram-bot` JobQueue) — per-group timezone-aware scheduling
- **pytz** — timezone handling
- **Tabular Islamic Calendar** — pure-Python Hijri date conversion (no external libraries)

## Deployment

### Environment Variables
Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | — | Telegram Bot API token (from @BotFather) |
| `DATABASE_PATH` | `data/quran_tracker.db` | Path to SQLite database file |
| `TIMEZONE` | `Africa/Cairo` | Default bot timezone |
| `DEFAULT_POST_TIME` | `08:00` | Global default reading post time |
| `REPORT_TIME` | `22:00` | Global default report time |
| `REMINDER_TIMES` | `20:00` | Default reminder time(s) |
| `ENABLE_REMINDERS` | `false` | Enable reminder system |
| `ENABLE_WEEKLY_REPORT` | `true` | Enable weekly reports |
| `ENABLE_BADGES` | `false` | Enable badge system |
| `ANNOUNCE_BADGES` | `false` | Announce badges in group |
| `ENABLE_MILESTONES` | `true` | Enable milestone announcements |
| `NOTIFY_ACHIEVEMENTS` | `false` | Notify on achievements |
| `WEEKLY_REPORT_DAY` | `4` | Day of week for weekly report (0=Mon, 6=Sun) |
| `BACKUP_TIME` | `03:00` | Auto-backup time |
| `BACKUP_DIR` | `backups` | Backup directory |
| `BACKUP_RETAIN` | `14` | Days to keep backups |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_MAX_MB` | `10` | Max log file size in MB |
| `LOG_BACKUP_COUNT` | `5` | Number of log files to keep |

### Railway
The bot is designed for **Railway** deployment:
1. Fork/clone the repo
2. Create a Railway project from the repo
3. Add a **Volume** mounted at `/data` for persistent storage
4. Set `DATABASE_PATH=/data/quran_tracker.db`
5. Add all required environment variables
6. Railway auto-deploys from the `main` branch

## License

MIT License — see [LICENSE](LICENSE) for details.
