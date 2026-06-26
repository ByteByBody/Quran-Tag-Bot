import asyncio
import logging
import psutil
import sqlite3
from datetime import datetime
from pathlib import Path
from config import settings

logger = logging.getLogger(__name__)

async def run_health_checks() -> dict:
    """Run comprehensive health checks on the bot's environment."""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "unknown",
        "disk_space": "unknown",
        "memory_usage": "unknown",
        "cpu_usage": "unknown",
        "errors": []
    }

    # 1. Check Database Integrity
    try:
        if settings.database_path.exists():
            loop = asyncio.get_event_loop()
            def _check_db():
                with sqlite3.connect(settings.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA integrity_check;")
                    return cursor.fetchone()[0]
            
            result = await loop.run_in_executor(None, _check_db)
            if result == "ok":
                status["database"] = "healthy"
            else:
                status["database"] = f"corrupt ({result})"
                status["status"] = "degraded"
                status["errors"].append("Database integrity check failed.")
        else:
            status["database"] = "missing"
            status["status"] = "critical"
            status["errors"].append("Database file is missing.")
    except Exception as e:
        status["database"] = "error"
        status["status"] = "critical"
        status["errors"].append(f"DB Check Error: {e}")

    # 2. Check Disk Space (Warn if < 500MB free)
    try:
        disk = psutil.disk_usage('/')
        free_mb = disk.free / (1024 * 1024)
        status["disk_space"] = f"{free_mb:.2f} MB free"
        if free_mb < 500:
            status["status"] = "degraded"
            status["errors"].append(f"Low disk space: {free_mb:.2f} MB left.")
    except Exception as e:
        status["errors"].append(f"Disk check error: {e}")

    # 3. Process Memory & CPU
    try:
        process = psutil.Process()
        mem_mb = process.memory_info().rss / (1024 * 1024)
        cpu = process.cpu_percent(interval=0.1)
        status["memory_usage"] = f"{mem_mb:.2f} MB"
        status["cpu_usage"] = f"{cpu}%"
        
        # Arbitrary thresholds: warn if RAM > 500MB for a simple bot
        if mem_mb > 500:
            status["status"] = "degraded"
            status["errors"].append(f"High memory usage: {mem_mb:.2f} MB.")
    except Exception as e:
        status["errors"].append(f"Process check error: {e}")

    return status

async def monitoring_job(context) -> None:
    """Scheduled job to run health checks and alert admins if degraded."""
    try:
        status = await run_health_checks()
        if status["status"] != "healthy":
            alert_text = (
                "⚠️ *تنبيه النظام (Monitoring Alert)* ⚠️\n\n"
                f"الحالة: {status['status']}\n"
                f"قاعدة البيانات: {status['database']}\n"
                f"الذاكرة: {status['memory_usage']}\n\n"
                "*الأخطاء:*\n- " + "\n- ".join(status["errors"])
            )
            for admin_id in settings.bot_admins:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=alert_text,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.error("Failed to send alert to admin %s: %s", admin_id, e)
    except Exception as e:
        logger.error("Monitoring job failed: %s", e)
