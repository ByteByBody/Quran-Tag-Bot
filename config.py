"""
config.py — Central configuration loader for Quran Tracker Bot.

Reads environment variables (via .env) and exposes a single Settings
dataclass consumed by all other modules.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

import pytz
from dotenv import load_dotenv

# Load .env file at import time so all os.getenv calls find the values.
load_dotenv()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require(key: str) -> str:
    """Return the value of a required env var or raise a clear error."""
    value = os.getenv(key, "").strip()
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            "Please copy .env.example to .env and fill in all required values."
        )
    return value


def _optional(key: str, default: str = "") -> str:
    """Return an optional env var or its default."""
    return os.getenv(key, default).strip()


def _bool(key: str, default: bool = False) -> bool:
    """Parse a boolean env var ('true'/'1'/'yes' → True)."""
    raw = os.getenv(key, str(default)).strip().lower()
    return raw in ("true", "1", "yes")


def _int(key: str, default: int = 0) -> int:
    """Parse an integer env var."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def _list(key: str, default: str = "") -> list[str]:
    """Parse a comma-separated env var into a list of stripped strings."""
    raw = os.getenv(key, default).strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Settings dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Settings:
    """Immutable application settings resolved from environment variables."""

    # Core
    bot_token: str
    bot_version: str

    # Database
    database_path: Path

    # Scheduling
    timezone: pytz.BaseTzInfo
    timezone_str: str
    default_post_time: str      # "HH:MM"
    report_time: str             # "HH:MM"
    backup_time: str             # "HH:MM"
    weekly_report_day: int       # 0=Monday … 6=Sunday (4 = Friday)

    # Logging
    log_level: str
    log_max_mb: int
    log_backup_count: int

    # Content toggles
    include_daily_verse: bool
    include_daily_hadith: bool
    include_daily_dua: bool

    # Backups
    backup_dir: Path
    backup_retain: int

    # Feature flags (new)
    enable_weekly_report: bool
    enable_badges: bool
    enable_milestones: bool
    enable_reminders: bool
    announce_badges: bool          # Global default; per-group can override
    notify_achievements: bool      # Send private DM when badge earned (false = silent until /me)
    enable_random_verses: bool
    enable_random_hadith: bool
    enable_random_dua: bool
    reminder_times: list[str]      # e.g. ["20:00", "21:30"]
    bot_admins: set[int]           # Global admin user IDs

    # Derived convenience fields
    log_dir: Path = field(init=False)
    data_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        # Bypass frozen=True to set derived fields.
        object.__setattr__(self, "log_dir", Path("logs"))
        object.__setattr__(self, "data_dir", Path("data"))


def _validate_time(value: str, key: str) -> str:
    """Ensure HH:MM format is valid."""
    try:
        parts = value.split(":")
        assert len(parts) == 2
        h, m = int(parts[0]), int(parts[1])
        assert 0 <= h <= 23 and 0 <= m <= 59
    except (ValueError, AssertionError):
        raise ValueError(
            f"Environment variable '{key}' must be in HH:MM format (got '{value}')."
        )
    return value


def _validate_reminder_times(times: list[str]) -> list[str]:
    """Validate each reminder time string."""
    valid = []
    for t in times:
        try:
            _validate_time(t, "REMINDER_TIMES")
            valid.append(t)
        except ValueError:
            logging.getLogger(__name__).warning("Ignoring invalid reminder time: %r", t)
    return valid


def load_settings() -> Settings:
    """Build and return the Settings singleton."""
    bot_token = _require("BOT_TOKEN")
    if bot_token == "your_bot_token_here":
        raise EnvironmentError(
            "BOT_TOKEN is still the placeholder value. "
            "Please set it to your actual Telegram bot token."
        )

    timezone_str = _optional("TIMEZONE", "Africa/Cairo")
    try:
        tz = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValueError(
            f"Unknown timezone '{timezone_str}'. "
            "Use a valid pytz timezone, e.g. 'Asia/Riyadh' or 'Africa/Cairo'."
        )

    raw_reminder_times = _list("REMINDER_TIMES", "20:00")
    reminder_times = _validate_reminder_times(raw_reminder_times) or ["20:00"]

    return Settings(
        bot_token=bot_token,
        bot_version=_optional("BOT_VERSION", "2.0.0"),
        database_path=Path(_optional("DATABASE_PATH", "data/quran_tracker.db")),
        timezone=tz,
        timezone_str=timezone_str,
        default_post_time=_validate_time(
            _optional("DEFAULT_POST_TIME", "08:00"), "DEFAULT_POST_TIME"
        ),
        report_time=_validate_time(
            _optional("REPORT_TIME", "22:00"), "REPORT_TIME"
        ),
        backup_time=_validate_time(
            _optional("BACKUP_TIME", "03:00"), "BACKUP_TIME"
        ),
        weekly_report_day=_int("WEEKLY_REPORT_DAY", 4),   # 4 = Friday
        log_level=_optional("LOG_LEVEL", "INFO").upper(),
        log_max_mb=_int("LOG_MAX_MB", 5),
        log_backup_count=_int("LOG_BACKUP_COUNT", 5),
        # Legacy aliases kept for compatibility
        include_daily_verse=_bool("INCLUDE_DAILY_VERSE", True),
        include_daily_hadith=_bool("INCLUDE_DAILY_HADITH", False),
        include_daily_dua=_bool("INCLUDE_DAILY_DUA", False),
        backup_dir=Path(_optional("BACKUP_DIR", "data/backups")),
        backup_retain=_int("BACKUP_RETAIN", 7),
        # New feature flags
        enable_weekly_report=_bool("ENABLE_WEEKLY_REPORT", True),
        enable_badges=_bool("ENABLE_BADGES", True),
        enable_milestones=_bool("ENABLE_MILESTONES", True),
        enable_reminders=_bool("ENABLE_REMINDERS", False),
        announce_badges=_bool("ANNOUNCE_BADGES", True),
        notify_achievements=_bool("NOTIFY_ACHIEVEMENTS", True),
        enable_random_verses=_bool("ENABLE_RANDOM_VERSES", True),
        enable_random_hadith=_bool("ENABLE_RANDOM_HADITH", False),
        enable_random_dua=_bool("ENABLE_RANDOM_DUA", False),
        reminder_times=reminder_times,
        bot_admins={int(x.strip()) for x in _optional("BOT_ADMINS", "").split(",") if x.strip().isdigit()},
    )


# ---------------------------------------------------------------------------
# Module-level singleton — import and use `settings` everywhere.
# ---------------------------------------------------------------------------
try:
    settings: Settings = load_settings()
except EnvironmentError:
    # Allow importing during setup/test without crashing.
    settings = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)
