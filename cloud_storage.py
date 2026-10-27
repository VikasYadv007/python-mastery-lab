"""Database backend selection: SQLite for offline practice, PostgreSQL for cloud.

Uses server-side PostgreSQL credentials only. No Supabase REST endpoint or keys
are exposed to a browser. Connection URL comes from Streamlit secrets or env.
"""

from __future__ import annotations

import atexit
import os
import threading
from contextlib import contextmanager

from mastery_lab.schema import PG_SCHEMA as PG_SCHEMA

_POSTGRES_URL: str | None = None
_pool = None
_lock = threading.RLock()


def configure(url: str | None) -> None:
    """Call before first DB operation; don't change URL while app is serving."""
    global _POSTGRES_URL, _pool
    url = (url or "").strip()
    with _lock:
        if _pool is not None and url != _POSTGRES_URL:
            _pool.close()
            _pool = None
        _POSTGRES_URL = url or None


def is_cloud() -> bool:
    return bool(_database_url())


def _database_url() -> str:
    return (_POSTGRES_URL or os.environ.get("DATABASE_URL") or "").strip()


def close_pool() -> None:
    """Release connection workers on shutdown; safe to call repeatedly."""
    global _pool
    with _lock:
        if _pool is not None:
            _pool.close()
            _pool = None


atexit.register(close_pool)


def _get_pool():
    global _pool
    with _lock:
        url = _database_url()
        if not url:
            raise RuntimeError("PostgreSQL requires a nonempty DATABASE_URL.")
        if _pool is None:
            try:
                from psycopg.rows import dict_row
                from psycopg_pool import ConnectionPool
            except ImportError as exc:
                raise RuntimeError(
                    "PostgreSQL support requires pip install -r requirements.txt"
                ) from exc
            # Session pooler (:5432) recommended. prepare_threshold=None also
            # supports transaction pooler (:6543) without server-side prepares.
            _pool = ConnectionPool(
                conninfo=url,
                min_size=0,
                max_size=5,
                kwargs={
                    "row_factory": dict_row,
                    "prepare_threshold": None,
                    "connect_timeout": 10,
                    "sslmode": "require",
                },
                open=True,
                timeout=15,
            )
        return _pool


class PostgresConnection:
    """Tiny placeholder compatibility layer for quiz_core's DB-API queries."""

    def __init__(self, connection):
        self._con = connection

    def execute(self, query: str, params=()):
        return self._con.execute(query.replace("?", "%s"), params)

    def executescript(self, script: str):
        # Only used for our own fixed schema, never user supplied SQL.
        for statement in script.split(";"):
            if statement.strip():
                self._con.execute(statement)


@contextmanager
def connection():
    pool = _get_pool()
    with pool.connection() as con:
        yield PostgresConnection(con)
