import asyncio
import hashlib
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

async def generate_checksum(filepath: Path) -> str:
    """Generate SHA256 checksum for a file."""
    loop = asyncio.get_event_loop()
    def _hash():
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    return await loop.run_in_executor(None, _hash)

def _sync_create_backup(db_path: Path, backup_dir: Path, retain_daily: int = 7, retain_weekly: int = 4, is_weekly: bool = False) -> tuple[Path, str]:
    """Sync backup logic to be run in executor."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    prefix = "quran_tracker_weekly" if is_weekly else "quran_tracker_daily"
    backup_path = backup_dir / f"{prefix}_{timestamp}.db"

    # Safely lock and copy if it were active sqlite3 connection, but since aiosqlite is used,
    # shutil.copy2 on WAL mode is generally ok, though `.backup()` API is safer.
    # We will use shutil.copy2 for now as it was the existing logic, to preserve backward compat.
    shutil.copy2(db_path, backup_path)
    logger.info("Backup created: %s", backup_path)
    
    # Generate checksum
    sha256_hash = hashlib.sha256()
    with open(backup_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    checksum = sha256_hash.hexdigest()
    
    # Write checksum file
    checksum_path = backup_path.with_suffix('.db.sha256')
    with open(checksum_path, "w") as f:
        f.write(checksum)

    # Prune old backups (Daily)
    daily_existing = sorted(
        backup_dir.glob("quran_tracker_daily_*.db"),
        key=lambda p: p.stat().st_mtime,
    )
    while len(daily_existing) > retain_daily:
        oldest = daily_existing.pop(0)
        oldest.unlink(missing_ok=True)
        oldest.with_suffix('.db.sha256').unlink(missing_ok=True)
        logger.info("Pruned old daily backup: %s", oldest)

    # Prune old backups (Weekly)
    weekly_existing = sorted(
        backup_dir.glob("quran_tracker_weekly_*.db"),
        key=lambda p: p.stat().st_mtime,
    )
    while len(weekly_existing) > retain_weekly:
        oldest = weekly_existing.pop(0)
        oldest.unlink(missing_ok=True)
        oldest.with_suffix('.db.sha256').unlink(missing_ok=True)
        logger.info("Pruned old weekly backup: %s", oldest)

    return backup_path, checksum

async def async_create_backup(db_path: Path, backup_dir: Path, retain_daily: int = 7, retain_weekly: int = 4, is_weekly: bool = False) -> tuple[Path, str]:
    """Async wrapper around sync backup creation."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _sync_create_backup, db_path, backup_dir, retain_daily, retain_weekly, is_weekly
    )
