"""
bot.py — Entry point for the Quran Tracker Bot.

Responsibilities:
  • Configure logging
  • Initialise the database
  • Register all Telegram handlers
  • Register scheduled jobs
  • Start polling

Run with:
    python bot.py
"""

from __future__ import annotations

import asyncio
import logging
import logging.handlers
import sys
from pathlib import Path

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import settings
from database import Database
from handlers import (
    cmd_backup,
    cmd_checkin,
    cmd_daily,
    cmd_export,
    cmd_help,
    cmd_leaderboard,
    cmd_me,
    cmd_menu,
    cmd_missing,
    cmd_readingplan,
    cmd_report,
    cmd_reset_member,
    cmd_reset_month,
    cmd_restore,
    cmd_settings,
    cmd_start,
    cmd_stats,
    cmd_version,
    handle_callback,
    handle_left_member,
    handle_new_member,
    handle_restore_document,
    handle_text_message,
)
from scheduler import register_jobs


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def configure_logging() -> None:
    """Set up rotating file + console logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_level = getattr(logging, settings.log_level, logging.INFO)
    max_bytes = settings.log_max_mb * 1024 * 1024

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    root_logger.addHandler(console)

    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "bot.log",
        maxBytes=max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
        )
    )
    root_logger.addHandler(file_handler)

    # Silence overly verbose third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# Bot command menu
# ---------------------------------------------------------------------------

BOT_COMMANDS = [
    BotCommand("start",        "تشغيل البوت"),
    BotCommand("menu",         "القائمة الرئيسية"),
    BotCommand("help",         "المساعدة وقائمة الأوامر"),
    BotCommand("me",           "إحصائياتك الشخصية"),
    BotCommand("checkin",      "تسجيل ورد اليوم"),
    BotCommand("leaderboard",  "لوحة الشرف"),
    BotCommand("stats",        "إحصائيات المجموعة"),
    BotCommand("daily",        "إرسال ورد اليوم"),
    BotCommand("report",       "تقرير اليوم"),
    BotCommand("missing",      "من لم يُكمل الورد (مشرفون)"),
    BotCommand("settings",     "إعدادات المجموعة (مشرفون)"),
    BotCommand("readingplan",  "تغيير خطة القراءة (مشرفون)"),
    BotCommand("backup",       "نسخة احتياطية (مشرفون)"),
    BotCommand("restore",      "استعادة نسخة (مشرفون)"),
    BotCommand("export",       "تصدير البيانات (مشرفون)"),
    BotCommand("reset_member", "إعادة ضبط عضو (مشرفون)"),
    BotCommand("reset_month",  "إعادة ضبط الشهر (مشرفون)"),
    BotCommand("version",      "معلومات البوت"),
]


# ---------------------------------------------------------------------------
# Post-init hook
# ---------------------------------------------------------------------------

async def post_init(app: Application) -> None:
    """Initialise shared resources after the Application is built."""
    # Database
    db = Database(settings.database_path)
    await db.init()
    app.bot_data["db"] = db

    # Register bot commands with Telegram
    await app.bot.set_my_commands(BOT_COMMANDS)
    logging.getLogger(__name__).info("Bot commands registered.")


async def post_shutdown(app: Application) -> None:
    """Clean up on shutdown."""
    db: Database = app.bot_data.get("db")
    if db:
        await db.close()
    logging.getLogger(__name__).info("Bot shut down cleanly.")


# ---------------------------------------------------------------------------
# Handler registration
# ---------------------------------------------------------------------------

def register_handlers(app: Application) -> None:
    """Attach all handlers to the Application."""

    # --- Commands ---
    app.add_handler(CommandHandler("start",        cmd_start))
    app.add_handler(CommandHandler("menu",         cmd_menu))
    app.add_handler(CommandHandler("help",         cmd_help))
    app.add_handler(CommandHandler("me",           cmd_me))
    app.add_handler(CommandHandler("checkin",      cmd_checkin))
    app.add_handler(CommandHandler("leaderboard",  cmd_leaderboard))
    app.add_handler(CommandHandler("stats",        cmd_stats))
    app.add_handler(CommandHandler("daily",        cmd_daily))
    app.add_handler(CommandHandler("report",       cmd_report))
    app.add_handler(CommandHandler("missing",      cmd_missing))
    app.add_handler(CommandHandler("settings",     cmd_settings))
    app.add_handler(CommandHandler("readingplan",  cmd_readingplan))
    app.add_handler(CommandHandler("backup",       cmd_backup))
    app.add_handler(CommandHandler("restore",      cmd_restore))
    app.add_handler(CommandHandler("export",       cmd_export))
    app.add_handler(CommandHandler("reset_member", cmd_reset_member))
    app.add_handler(CommandHandler("reset_month",  cmd_reset_month))
    app.add_handler(CommandHandler("version",      cmd_version))

    # --- Inline keyboard callbacks ---
    app.add_handler(CallbackQueryHandler(handle_callback))

    # --- Group membership changes ---
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member)
    )
    app.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_left_member)
    )

    # --- Document messages (for /restore) ---
    app.add_handler(
        MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_restore_document)
    )

    # --- Plain text (for capturing setting values) ---
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    )


# ---------------------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------------------

async def error_handler(update: object, context) -> None:
    """Log all unhandled exceptions."""
    logger = logging.getLogger(__name__)
    logger.error("Unhandled exception for update %s", update, exc_info=context.error)

    # Attempt to notify the user if we have an update
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("⚠️ حدث خطأ غير متوقع.")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Build and run the bot."""
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Quran Tracker Bot v%s …", settings.bot_version)

    if settings is None:
        logger.critical("Settings could not be loaded. Check your .env file.")
        sys.exit(1)

    app = (
        Application.builder()
        .token(settings.bot_token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    register_handlers(app)
    app.add_error_handler(error_handler)
    register_jobs(app)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
