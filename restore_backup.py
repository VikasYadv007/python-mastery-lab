"""Recovery tool for per-user ZIP downloads. Does not delete or overwrite rows.

Run locally as project owner, with DATABASE_URL environment secret set:
  python restore_backup.py my_progress_backup.zip --to-user student
"""
from __future__ import annotations

import argparse
import json
import os
import zipfile
from pathlib import Path

import cloud_storage as cloud
import quiz_core as core
from migrate_progress import TABLE_FIELDS


def restore(backup: Path, username: str) -> dict[str, int]:
    username = core.normalize_username(username)
    if not cloud.is_cloud():
        raise RuntimeError('Recovery requires PostgreSQL DATABASE_URL.')
    core.init_db()
    if not core.user_exists(username):
        raise ValueError('Create the target account before restoring its data.')
    if backup.stat().st_size > 150_000_000:
        raise ValueError('Backup ZIP unexpectedly large; refuse to open.')
    with zipfile.ZipFile(backup) as archive:
        info = archive.getinfo('my_progress.json')
        if info.file_size > 150_000_000:
            raise ValueError('Uncompressed backup too large.')
        payload = json.loads(archive.read(info))
    if payload.get('format') != 'python_mastery_backup_v1' or not isinstance(payload.get('tables'), dict):
        raise ValueError('Not a Python Mastery Lab progress backup.')
    result = {}
    with core.db() as target:
        # Ensure all-or-nothing even when a row is malformed.
        for table, columns in TABLE_FIELDS.items():
            imported = 0
            for row in payload['tables'].get(table, []):
                cols = ','.join(columns)
                placeholders = ','.join('?' for _ in columns)
                conflict = '(id)' if table == 'sessions' else '(profile,session_id,question_id)' if table == 'attempts' else '(profile,question_id)'
                sql = f'INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT{conflict} DO NOTHING'
                values = [username if field == 'profile' else row[field] for field in columns]
                imported += max(0, target.execute(sql, tuple(values)).rowcount)
            result[table] = imported
        restored_packs = 0
        bundled_ids = {json.loads(path.read_text(encoding='utf-8'))['pack_id'] for path in core.PACK_DIR.glob('*.json')}
        for p in payload.get('uploaded_packs', []):
            pack = json.loads(p['body'])
            core.validate_pack(pack)
            if p['pack_id'] in bundled_ids:
                continue  # Already preserved in Git, no cloud duplicate needed.
            restored_packs += max(0, target.execute(
                'INSERT INTO uploaded_packs(pack_id,body,created_at) VALUES (?,?,?) ON CONFLICT(pack_id) DO NOTHING',
                (p['pack_id'], p['body'], p['created_at'])).rowcount)
        result['uploaded_packs'] = restored_packs
    return result


def main():
    parser = argparse.ArgumentParser(description='Restore one user history into a live Supabase project (insert missing only)')
    parser.add_argument('backup', type=Path)
    parser.add_argument('--to-user', required=True)
    args = parser.parse_args()
    if not os.environ.get('DATABASE_URL'):
        parser.error('Set DATABASE_URL in your terminal first')
    cloud.configure(os.environ['DATABASE_URL'])
    print('Restored new rows:', restore(args.backup, args.to_user))
    print('Existing cloud data was never deleted or overwritten.')


if __name__ == '__main__':
    main()
