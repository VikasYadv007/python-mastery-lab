"""Regression tests for validation, authentication, and safe progress transfers."""

import copy
import json
import sqlite3
from contextlib import closing

import pytest

import quiz_core as core
from mastery_lab.presentation import sqlite_backup
from mastery_lab.security import make_password_hash, verify_password
from mastery_lab.transfer import insert_progress
from migrate_progress import legacy_profiles


@pytest.fixture
def bank():
    return copy.deepcopy(next(iter(core.load_packs().values())))


@pytest.mark.parametrize(
    "field,value",
    [("title", None), ("rubric", ""), ("samples", [{}]), ("tags", 7), ("pages", [True])],
)
def test_coding_pack_rejects_fields_that_break_ui(bank, field, value):
    bank["challenges"][0][field] = value
    with pytest.raises(ValueError):
        core.validate_pack(bank)


def test_cloud_load_validates_bundled_pack_before_indexing(tmp_path, monkeypatch):
    (tmp_path / "bad.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(core, "PACK_DIR", tmp_path)
    monkeypatch.setattr(core.cloud, "is_cloud", lambda: True)
    with pytest.raises(ValueError, match="schema_version"):
        core.load_packs()


def test_import_cannot_overwrite_existing_pack_file(tmp_path, monkeypatch, bank):
    monkeypatch.setattr(core, "PACK_DIR", tmp_path)
    raw = json.dumps(bank).encode()
    core.import_pack(raw)
    with pytest.raises(ValueError, match="already exists"):
        core.import_pack(raw)
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_password_hashes_and_malformed_inputs():
    encoded = make_password_hash("a-long-password")
    assert verify_password("a-long-password", encoded)
    assert not verify_password("incorrect-password", encoded)
    assert encoded != make_password_hash("a-long-password")
    for malformed in ("garbage", "scrypt$16384$8$1$!!!$!!!", "scrypt$999999$8$1$a$b"):
        assert not verify_password("a-long-password", malformed)
    assert not verify_password("x" * 201, encoded)


def test_accounts_and_export_are_profile_scoped(tmp_path):
    path = tmp_path / "progress.sqlite3"
    core.init_db(path)
    assert core.register_user(" Alice ", "a-long-password", path) == "alice"
    assert core.authenticate_user("ALICE", "a-long-password", path) == "alice"
    assert core.authenticate_user("alice", "wrong-password", path) is None
    with pytest.raises(ValueError, match="already registered"):
        core.register_user("alice", "another-password", path)
    core.reset_user_password("alice", "replacement-password", path)
    assert core.authenticate_user("alice", "replacement-password", path) == "alice"
    core.save_note("alice", "q1", "Alice note", path)
    core.save_note("bob", "q1", "Bob note", path)
    import io
    import zipfile

    with zipfile.ZipFile(io.BytesIO(core.export_all_progress("alice", path))) as archive:
        payload = json.loads(archive.read("my_progress.json"))
    assert payload["tables"]["personal_notes"][0]["note"] == "Alice note"
    assert all(row["profile"] == "alice" for rows in payload["tables"].values() for row in rows)


def test_transfer_is_idempotent_and_rolls_back_cross_profile_session(tmp_path):
    path = tmp_path / "progress.sqlite3"
    core.init_db(path)
    sid = core.new_session("alice", "mcq", ["q1"], database=path)
    session = core.get_session("alice", sid, path)
    session["queue"] = json.dumps(session["queue"])
    session["configuration"] = json.dumps(session["configuration"])
    with core.db(path) as target:
        assert insert_progress(target, {"sessions": [session]}, "alice")["sessions"] == 0
    other = dict(session, id="new-id")
    with pytest.raises(ValueError, match="another learner"):
        with core.db(path) as target:
            insert_progress(target, {"sessions": [other, session]}, "bob")
    assert core.get_session("bob", "new-id", path) is None
    with pytest.raises(ValueError, match="required fields"):
        with core.db(path) as target:
            insert_progress(target, {"code_drafts": [{}]}, "bob")


def test_backup_and_profile_listing_release_windows_file_handles(tmp_path):
    path = tmp_path / "progress #1.sqlite3"
    core.init_db(path)
    core.save_note("alice", "q1", "keep this", path)
    assert legacy_profiles(path) == ["alice"]
    backup = tmp_path / "backup.sqlite3"
    backup.write_bytes(sqlite_backup(path))
    with closing(sqlite3.connect(backup)) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT note FROM personal_notes").fetchone()[0] == "keep this"
    path.rename(tmp_path / "renamed.sqlite3")


@pytest.mark.parametrize("quantity,mode", [(0, "All"), (-1, "All"), (True, "All"), (1, "Invalid")])
def test_question_selection_rejects_invalid_requests(quantity, mode):
    with pytest.raises(ValueError):
        core.select_questions([], "alice", quantity, mode)


def test_selection_deduplicates_input(tmp_path, bank):
    path = tmp_path / "progress.sqlite3"
    core.init_db(path)
    question = bank["questions"][0]
    assert core.select_questions([question, question], "alice", 10, "All", database=path) == [
        question["id"]
    ]


def test_database_initialization_preserves_existing_rows(tmp_path):
    path = tmp_path / "progress.sqlite3"
    core.init_db(path)
    core.save_draft("alice", "q1", "print(1)", path)
    core.init_db(path)
    assert core.get_draft("alice", "q1", path) == "print(1)"
    with core.db(path) as con:
        assert con.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 1


def test_cloud_configuration_and_pool_cleanup(monkeypatch):
    from unittest.mock import Mock

    import cloud_storage as cloud

    monkeypatch.setenv("DATABASE_URL", "  ")
    assert not cloud.is_cloud()
    with pytest.raises(RuntimeError, match="nonempty"):
        cloud._get_pool()
    pool = Mock()
    monkeypatch.setattr(cloud, "_pool", pool)
    cloud.close_pool()
    cloud.close_pool()
    pool.close.assert_called_once()


@pytest.mark.parametrize("queue", [["q1", "q1"], [{}], ["q1", None]])
def test_session_rejects_invalid_question_ids(queue):
    with pytest.raises(ValueError, match="unique"):
        core.new_session("alice", "mcq", queue)


def test_restore_pack_conflict_rolls_back_progress(tmp_path, monkeypatch, bank):
    import io
    import zipfile

    import restore_backup

    path = tmp_path / "progress.sqlite3"
    core.init_db(path)
    real_db = core.db
    monkeypatch.setattr(core, "db", lambda: real_db(path))
    monkeypatch.setattr(core, "init_db", lambda: None)
    monkeypatch.setattr(core, "user_exists", lambda username: True)
    monkeypatch.setattr(core.cloud, "is_cloud", lambda: True)
    monkeypatch.setattr(core, "load_packs", lambda: {bank["pack_id"]: bank})
    modified = copy.deepcopy(bank)
    modified["title"] = "Different content with the same ID"
    payload = {
        "format": "python_mastery_backup_v1",
        "tables": {
            "personal_notes": [
                {
                    "profile": "old",
                    "question_id": "q1",
                    "note": "rollback",
                    "updated_at": core.now(),
                }
            ]
        },
        "uploaded_packs": [
            {"pack_id": bank["pack_id"], "body": json.dumps(modified), "created_at": core.now()}
        ],
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("my_progress.json", json.dumps(payload))
    backup = tmp_path / "backup.zip"
    backup.write_bytes(output.getvalue())
    with pytest.raises(ValueError, match="conflicts"):
        restore_backup.restore(backup, "alice")
    with real_db(path) as con:
        assert con.execute("SELECT COUNT(*) FROM personal_notes").fetchone()[0] == 0


def test_legacy_packs_without_type_support_analytics_and_restore(tmp_path, monkeypatch, bank):
    from restore_backup import pack_body

    legacy = copy.deepcopy(bank)
    for q in legacy["questions"] + legacy["challenges"]:
        q.pop("type", None)
    monkeypatch.setattr(core, "PACK_DIR", tmp_path)
    (tmp_path / "legacy.json").write_text(json.dumps(legacy), encoding="utf-8")
    loaded = next(iter(core.load_packs().values()))
    assert all(q["type"] == "mcq" for q in loaded["questions"])
    assert all(q["type"] == "coding" for q in loaded["challenges"])
    assert pack_body(legacy) == pack_body(loaded)


def test_complete_history_is_profile_scoped_and_not_limited_to_200(tmp_path):
    path = tmp_path / "history.sqlite3"
    core.init_db(path)
    with core.db(path) as con:
        for index in range(205):
            con.execute(
                "INSERT INTO attempts(profile,session_id,question_id,kind,correct,created_at) VALUES (?,?,?,?,?,?)",
                ("alice", str(index), "q1", "mcq", 1, core.now()),
            )
    assert len(core.attempt_history("alice", database=path)) == 200
    assert len(core.attempt_history("alice", None, path)) == 205
    assert not core.attempt_history("bob", None, path)
    with pytest.raises(ValueError):
        core.attempt_history("alice", -1, path)
