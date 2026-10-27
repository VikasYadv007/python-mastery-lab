"""Date formatting and database downloads, independent of the UI framework."""

from __future__ import annotations

import sqlite3
import tempfile
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def as_ist(value: str | None, *, date_only: bool = False) -> str:
    """Display UTC/offset timestamps in IST; legacy naive timestamps are UTC."""
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(IST).strftime("%d %b %Y" if date_only else "%d %b %Y, %I:%M %p IST")
    except (ValueError, TypeError, OverflowError):
        return "Unknown time"


def sqlite_backup(source: Path) -> bytes:
    """Use SQLite's online backup API and close handles before Windows cleanup."""
    if not source.is_file():
        return b""
    with tempfile.TemporaryDirectory() as tmpdir:
        copy = Path(tmpdir) / "progress.sqlite3"
        with closing(
            sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)
        ) as source_db:
            with closing(sqlite3.connect(str(copy))) as backup_db:
                source_db.backup(backup_db)
        return copy.read_bytes()
