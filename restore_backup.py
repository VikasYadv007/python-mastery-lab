"""Recovery tool for per-user ZIP downloads. Does not delete or overwrite rows.

Run locally as project owner, with DATABASE_URL environment secret set:
  python restore_backup.py my_progress_backup.zip --to-user student
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import zipfile
from pathlib import Path

import cloud_storage as cloud
import quiz_core as core
from mastery_lab.transfer import insert_progress


def pack_body(pack: dict) -> dict:
    """Compare original pack content without loader-added display metadata."""
    result = copy.deepcopy(pack)
    for question in result.get("questions", []) + result.get("challenges", []):
        for field in ("pack_id", "pack_title", "topic_name"):
            question.pop(field, None)
    return result


def restore(backup: Path, username: str) -> dict[str, int]:
    username = core.normalize_username(username)
    if not cloud.is_cloud():
        raise RuntimeError("Recovery requires PostgreSQL DATABASE_URL.")
    core.init_db()
    if not core.user_exists(username):
        raise ValueError("Create the target account before restoring its data.")
    if backup.stat().st_size > 150_000_000:
        raise ValueError("Backup ZIP unexpectedly large; refuse to open.")
    with zipfile.ZipFile(backup) as archive:
        info = archive.getinfo("my_progress.json")
        if info.file_size > 150_000_000:
            raise ValueError("Uncompressed backup too large.")
        payload = json.loads(archive.read(info))
    if (
        not isinstance(payload, dict)
        or payload.get("format") != "python_mastery_backup_v1"
        or not isinstance(payload.get("tables"), dict)
    ):
        raise ValueError("Not a Python Mastery Lab progress backup.")
    installed = core.load_packs()
    known_questions = {
        q["id"]
        for pack in installed.values()
        for q in pack.get("questions", []) + pack.get("challenges", [])
    }
    with core.db() as target:
        result = insert_progress(target, payload["tables"], username)
        restored_packs = 0
        for p in payload.get("uploaded_packs", []):
            pack = json.loads(p["body"])
            core.validate_pack(pack)
            if p["pack_id"] != pack["pack_id"]:
                raise ValueError("Backup pack ID does not match its contents.")
            if p["pack_id"] in installed:
                if pack_body(installed[p["pack_id"]]) != pack_body(pack):
                    raise ValueError("Backup lecture conflicts with an installed pack.")
                continue
            ids = {q["id"] for q in pack.get("questions", []) + pack.get("challenges", [])}
            if ids.intersection(known_questions):
                raise ValueError("Backup question IDs conflict with an installed pack.")
            installed[p["pack_id"]] = pack
            known_questions.update(ids)
            restored_packs += max(
                0,
                target.execute(
                    "INSERT INTO uploaded_packs(pack_id,body,created_at) VALUES (?,?,?) ON CONFLICT(pack_id) DO NOTHING",
                    (p["pack_id"], p["body"], p["created_at"]),
                ).rowcount,
            )
        result["uploaded_packs"] = restored_packs
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Restore one user history into a live Supabase project (insert missing only)"
    )
    parser.add_argument("backup", type=Path)
    parser.add_argument("--to-user", required=True)
    args = parser.parse_args()
    if not os.environ.get("DATABASE_URL"):
        parser.error("Set DATABASE_URL in your terminal first")
    cloud.configure(os.environ["DATABASE_URL"])
    print("Restored new rows:", restore(args.backup, args.to_user))
    print("Existing cloud data was never deleted or overwritten.")


if __name__ == "__main__":
    main()
