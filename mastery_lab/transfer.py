"""Shared insert-only progress transfer used by migration and ZIP recovery.

Call inside a database transaction so a malformed row rolls back the transfer.
SQL identifiers are constants; values always use parameterized queries.
"""

from __future__ import annotations

from collections.abc import Mapping

TABLE_FIELDS = {
    "sessions": (
        "id",
        "profile",
        "kind",
        "configuration",
        "queue",
        "position",
        "created_at",
        "completed_at",
    ),
    "attempts": (
        "profile",
        "session_id",
        "question_id",
        "kind",
        "answer_index",
        "correct",
        "response_text",
        "created_at",
    ),
    "mastery": (
        "profile",
        "question_id",
        "streak",
        "total_correct",
        "total_wrong",
        "last_correct",
        "next_due",
        "updated_at",
    ),
    "bookmarks": ("profile", "question_id", "created_at"),
    "personal_notes": ("profile", "question_id", "note", "updated_at"),
    "code_drafts": ("profile", "question_id", "code", "updated_at"),
}


def insert_progress(target, tables: Mapping, username: str) -> dict[str, int]:
    """Copy missing rows without linking a user's attempts to another's session."""
    results = {}
    for table, columns in TABLE_FIELDS.items():
        rows = tables.get(table, [])
        if not isinstance(rows, list):
            raise ValueError(f"{table}: expected a list of rows.")
        conflict = (
            "(id)"
            if table == "sessions"
            else "(profile,session_id,question_id)"
            if table == "attempts"
            else "(profile,question_id)"
        )
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) ON CONFLICT{conflict} DO NOTHING"
        copied = 0
        for row in rows:
            if not isinstance(row, Mapping) or any(field not in row for field in columns):
                raise ValueError(f"{table}: row is missing required fields.")
            sid = (
                row.get("id")
                if table == "sessions"
                else row.get("session_id")
                if table == "attempts"
                else None
            )
            if sid is not None:
                owner = target.execute("SELECT profile FROM sessions WHERE id=?", (sid,)).fetchone()
                if owner and owner["profile"] != username:
                    raise ValueError("A session ID belongs to another learner. Transfer cancelled.")
            values = tuple(username if field == "profile" else row[field] for field in columns)
            copied += max(0, target.execute(sql, values).rowcount)
        results[table] = copied
    return results
