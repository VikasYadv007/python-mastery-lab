"""Idempotent SQLite -> PostgreSQL progress import (password accounts must exist).

Run in a trusted local terminal, never hosted/public:
  python migrate_progress.py --from-profile "My Python practice" --to-user student

Data belonging to one legacy profile is mapped to one cloud username. Rows are
copied in a transaction; any existing cloud records win on conflict.
"""

import argparse
import os
import sqlite3
from contextlib import closing
from pathlib import Path

import cloud_storage as cloud
import quiz_core as core
from mastery_lab.transfer import TABLE_FIELDS, insert_progress


def legacy_profiles(file: Path) -> list[str]:
    if not file.is_file():
        raise FileNotFoundError(file)
    with closing(sqlite3.connect(file.resolve().as_uri() + "?mode=ro", uri=True)) as con:
        return sorted(
            {
                row[0]
                for table in TABLE_FIELDS
                for row in con.execute(f"SELECT DISTINCT profile FROM {table}")
            }
        )


def migrate(source: Path, old_profile: str, destination: str) -> dict[str, int]:
    """Transactionally copy one user; skipping duplicates prevents double counting."""
    destination = core.normalize_username(destination)
    if not cloud.is_cloud():
        raise RuntimeError("DATABASE_URL is required. Migration must target PostgreSQL.")
    core.init_db()
    if not core.user_exists(destination):
        raise ValueError("Create the destination user in the app first.")
    if not source.is_file():
        raise FileNotFoundError(source)
    results = {}
    with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as old:
        old.row_factory = sqlite3.Row
        # One PostgreSQL transaction across ALL tables. Failures roll back.
        with core.db() as target:
            tables = {
                table: [
                    dict(row)
                    for row in old.execute(
                        f"SELECT * FROM {table} WHERE profile=?", (old_profile,)
                    ).fetchall()
                ]
                for table in TABLE_FIELDS
            }
            results = insert_progress(target, tables, destination)
    return results


def main():
    p = argparse.ArgumentParser(
        description="Transfer an existing SQLite learner profile to your PostgreSQL user"
    )
    p.add_argument(
        "--sqlite", type=Path, default=core.DEFAULT_DB, help="Old data/progress.sqlite3 path"
    )
    p.add_argument("--list-profiles", action="store_true")
    p.add_argument("--from-profile", help="Exact old learner name as shown in app")
    p.add_argument("--to-user", help="Registered cloud account username")
    args = p.parse_args()
    if args.list_profiles:
        for profile in legacy_profiles(args.sqlite):
            print(profile)
        return
    if not (args.from_profile and args.to_user):
        p.error("Provide both --from-profile and --to-user, or use --list-profiles")
    if not os.environ.get("DATABASE_URL"):
        p.error("Set DATABASE_URL in your local terminal (do NOT put it in Git)")
    cloud.configure(os.environ["DATABASE_URL"])
    results = migrate(args.sqlite, args.from_profile, args.to_user)
    print("Imported new rows:", results)
    print("Re-running is safe: already-imported records are left unchanged.")


if __name__ == "__main__":
    main()
