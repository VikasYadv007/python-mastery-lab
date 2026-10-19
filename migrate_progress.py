"""Idempotent SQLite -> PostgreSQL progress import (password accounts must exist).

Run in a trusted local terminal, never hosted/public:
  python migrate_progress.py --from-profile "My Python practice" --to-user student

Data belonging to one legacy profile is mapped to one cloud username. Rows are
copied in a transaction; any existing cloud records win on conflict.
"""
import argparse
import os
import sqlite3
from pathlib import Path

import cloud_storage as cloud
import quiz_core as core

TABLE_FIELDS = {
    'sessions': ('id', 'profile', 'kind', 'configuration', 'queue', 'position', 'created_at', 'completed_at'),
    'attempts': ('profile', 'session_id', 'question_id', 'kind', 'answer_index', 'correct', 'response_text', 'created_at'),
    'mastery': ('profile', 'question_id', 'streak', 'total_correct', 'total_wrong', 'last_correct', 'next_due', 'updated_at'),
    'bookmarks': ('profile', 'question_id', 'created_at'),
    'personal_notes': ('profile', 'question_id', 'note', 'updated_at'),
    'code_drafts': ('profile', 'question_id', 'code', 'updated_at'),
}


def legacy_profiles(file: Path) -> list[str]:
    if not file.is_file():
        raise FileNotFoundError(file)
    with sqlite3.connect(f'file:{file.resolve()}?mode=ro', uri=True) as con:
        return sorted({row[0] for table in TABLE_FIELDS for row in con.execute(f'SELECT DISTINCT profile FROM {table}')})


def migrate(source: Path, old_profile: str, destination: str) -> dict[str, int]:
    """Transactionally copy one user; skipping duplicates prevents double counting."""
    destination = core.normalize_username(destination)
    if not cloud.is_cloud():
        raise RuntimeError('DATABASE_URL is required. Migration must target PostgreSQL.')
    core.init_db()
    if not core.user_exists(destination):
        raise ValueError('Create the destination user in the app first.')
    if not source.is_file():
        raise FileNotFoundError(source)
    results = {}
    with sqlite3.connect(f'file:{source.resolve()}?mode=ro', uri=True) as old:
        old.row_factory = sqlite3.Row
        # One PostgreSQL transaction across ALL tables. Failures roll back.
        with core.db() as target:
            for table, columns in TABLE_FIELDS.items():
                rows = old.execute(f'SELECT * FROM {table} WHERE profile=?', (old_profile,)).fetchall()
                if not rows:
                    results[table] = 0
                    continue
                cols = ','.join(columns)
                placeholders = ','.join('?' for _ in columns)
                if table == 'sessions':
                    conflict = '(id)'
                elif table == 'attempts':
                    conflict = '(profile,session_id,question_id)'
                else:
                    conflict = '(profile,question_id)'
                sql = f'INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT{conflict} DO NOTHING'
                copied = 0
                for row in rows:
                    values = [destination if col == 'profile' else row[col] for col in columns]
                    copied += max(target.execute(sql, tuple(values)).rowcount, 0)
                results[table] = copied
    return results


def main():
    p = argparse.ArgumentParser(description='Transfer an existing SQLite learner profile to your PostgreSQL user')
    p.add_argument('--sqlite', type=Path, default=core.DEFAULT_DB, help='Old data/progress.sqlite3 path')
    p.add_argument('--list-profiles', action='store_true')
    p.add_argument('--from-profile', help='Exact old learner name as shown in app')
    p.add_argument('--to-user', help='Registered cloud account username')
    args = p.parse_args()
    if args.list_profiles:
        for profile in legacy_profiles(args.sqlite):
            print(profile)
        return
    if not (args.from_profile and args.to_user):
        p.error('Provide both --from-profile and --to-user, or use --list-profiles')
    if not os.environ.get('DATABASE_URL'):
        p.error('Set DATABASE_URL in your local terminal (do NOT put it in Git)')
    cloud.configure(os.environ['DATABASE_URL'])
    results = migrate(args.sqlite, args.from_profile, args.to_user)
    print('Imported new rows:', results)
    print('Re-running is safe: already-imported records are left unchanged.')


if __name__ == '__main__':
    main()
