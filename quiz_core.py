"""Persistent engine for Python Mastery Lab. Requires only the Python standard library."""

from __future__ import annotations

import csv
import io
import json
import random
import sqlite3
import uuid
import zipfile
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import cloud_storage as cloud
from mastery_lab.schema import SQLITE_SCHEMA
from mastery_lab.security import (
    make_password_hash as make_password_hash,
)
from mastery_lab.security import (
    normalize_username as normalize_username,
)
from mastery_lab.security import (
    verify_password as verify_password,
)
from mastery_lab.validation import validate_pack as validate_pack

ROOT = Path(__file__).resolve().parent
PACK_DIR = ROOT / "packs"
DEFAULT_DB = ROOT / "data" / "progress.sqlite3"


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def load_packs() -> dict[str, dict]:
    """Read bundled and persisted packs, requiring unique IDs across all lectures."""
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    loaded = {}
    ids = set()
    files = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(PACK_DIR.glob("*.json"))]
    for pack in files:
        validate_pack(pack)
    if cloud.is_cloud():
        with db() as con:
            hosted = [
                json.loads(row["body"])
                for row in con.execute(
                    "SELECT body FROM uploaded_packs ORDER BY pack_id"
                ).fetchall()
            ]
        installed = {pack["pack_id"]: pack for pack in files}
        for pack in hosted:
            validate_pack(pack)
            original = installed.get(pack["pack_id"])
            if original is not None:
                # If an uploaded pack was later committed to GitHub with the same
                # contents, use its Git copy and don't double-register the lecture.
                if json.dumps(original, sort_keys=True) != json.dumps(pack, sort_keys=True):
                    raise ValueError(
                        f"Cloud pack {pack['pack_id']} conflicts with the bundled pack. Keep a single definition."
                    )
                continue
            files.append(pack)
    for pack in files:
        validate_pack(pack)
        if pack["pack_id"] in loaded:
            raise ValueError(f"Duplicate pack_id: {pack['pack_id']}")
        item_types = {
            q["id"]: kind
            for kind, items in (
                ("mcq", pack.get("questions", [])),
                ("coding", pack.get("challenges", [])),
            )
            for q in items
        }
        for q in pack.get("questions", []) + pack.get("challenges", []):
            if q["id"] in ids:
                raise ValueError(f"Question ID {q['id']} exists in multiple packs.")
            ids.add(q["id"])
            # Older valid packs omitted this optional display field. The list
            # containing an item is the schema's authoritative question kind.
            q["type"] = item_types[q["id"]]
            q["pack_id"] = pack["pack_id"]
            q["pack_title"] = pack["title"]
            q["topic_name"] = next(t["name"] for t in pack["topics"] if t["id"] == q["topic"])
        loaded[pack["pack_id"]] = pack
    return loaded


def import_pack(raw: bytes) -> str:
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError("Pack too large (8 MB maximum).")
    pack = json.loads(raw.decode("utf-8"))
    validate_pack(pack)
    existing = load_packs()
    if pack["pack_id"] in existing:
        raise ValueError("This pack ID already exists. Give the new PDF a unique pack_id.")
    old_ids = {
        q["id"]
        for old in existing.values()
        for q in old.get("questions", []) + old.get("challenges", [])
    }
    new_ids = {q["id"] for q in pack.get("questions", []) + pack.get("challenges", [])}
    duplicated = old_ids.intersection(new_ids)
    if duplicated:
        raise ValueError(
            "Question IDs must be unique across lectures: " + ", ".join(sorted(duplicated)[:5])
        )
    if cloud.is_cloud():
        with db() as con:
            con.execute(
                "INSERT INTO uploaded_packs (pack_id,body,created_at) VALUES (?,?,?)",
                (pack["pack_id"], raw.decode("utf-8"), now()),
            )
        return "Cloud library: " + pack["pack_id"]
    target = PACK_DIR / ("import_" + pack["pack_id"] + ".json")
    try:
        with target.open("x", encoding="utf-8") as output:
            output.write(json.dumps(pack, ensure_ascii=False, indent=2) + "\n")
    except FileExistsError as exc:
        raise ValueError(
            "This lecture file already exists. Refresh the library before importing again."
        ) from exc
    return str(target)


@contextmanager
def db(database: Path | str = DEFAULT_DB):
    if database == DEFAULT_DB and cloud.is_cloud():
        with cloud.connection() as con:
            yield con
        return
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=30000")
    try:
        yield con
        con.commit()
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()


def init_db(database: Path | str = DEFAULT_DB) -> None:
    """Idempotently initialize the schema without replacing existing progress."""
    schema = cloud.PG_SCHEMA if database == DEFAULT_DB and cloud.is_cloud() else SQLITE_SCHEMA
    with db(database) as con:
        con.executescript(schema)
        con.execute(
            "INSERT INTO schema_migrations(version,applied_at) VALUES (?,?) ON CONFLICT(version) DO NOTHING",
            (1, now()),
        )


def new_session(
    profile: str,
    kind: str,
    queue: list[str],
    configuration: dict | None = None,
    database: Path | str = DEFAULT_DB,
) -> str:
    if not queue:
        raise ValueError("Cannot start a session with no questions.")
    if (
        kind != "mcq"
        or any(not isinstance(qid, str) or not qid for qid in queue)
        or len(queue) != len(set(queue))
    ):
        raise ValueError("A quiz session needs unique question IDs and kind mcq.")
    sid = str(uuid.uuid4())
    with db(database) as con:
        con.execute(
            "INSERT INTO sessions (id,profile,kind,configuration,queue,position,created_at) VALUES (?,?,?,?,?,?,?)",
            (sid, profile, kind, json.dumps(configuration or {}), json.dumps(queue), 0, now()),
        )
    return sid


def get_session(profile: str, sid: str, database: Path | str = DEFAULT_DB) -> dict | None:
    with db(database) as con:
        row = con.execute(
            "SELECT * FROM sessions WHERE profile=? AND id=?", (profile, sid)
        ).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["queue"] = json.loads(result["queue"])
    result["configuration"] = json.loads(result["configuration"])
    return result


def recent_sessions(
    profile: str, limit=12, unfinished=False, database: Path | str = DEFAULT_DB
) -> list[dict]:
    sql = "SELECT * FROM sessions WHERE profile=? AND kind='mcq'"
    if unfinished:
        sql += " AND completed_at IS NULL"
    sql += " ORDER BY created_at DESC LIMIT ?"
    with db(database) as con:
        rows = con.execute(sql, (profile, limit)).fetchall()
    res = []
    for row in rows:
        item = dict(row)
        item["queue"] = json.loads(item["queue"])
        item["configuration"] = json.loads(item["configuration"])
        res.append(item)
    return res


def change_position(
    profile: str, sid: str, position: int, database: Path | str = DEFAULT_DB
) -> None:
    sess = get_session(profile, sid, database)
    if sess is None:
        raise ValueError("Unknown session.")
    position = max(0, min(len(sess["queue"]), position))
    done = now() if position >= len(sess["queue"]) else None
    with db(database) as con:
        con.execute(
            "UPDATE sessions SET position=?,completed_at=COALESCE(completed_at,?) WHERE id=? AND profile=?",
            (position, done, sid, profile),
        )


def get_answer(profile: str, sid: str, qid: str, database: Path | str = DEFAULT_DB) -> dict | None:
    with db(database) as con:
        row = con.execute(
            "SELECT * FROM attempts WHERE profile=? AND session_id=? AND question_id=?",
            (profile, sid, qid),
        ).fetchone()
    return dict(row) if row else None


def update_mastery(con, profile: str, qid: str, correct: bool) -> None:
    old = con.execute(
        "SELECT * FROM mastery WHERE profile=? AND question_id=?", (profile, qid)
    ).fetchone()
    streak = (old["streak"] if old else 0) + 1 if correct else 0
    delays = [1, 3, 7, 14, 30, 60, 90]
    next_due = (
        datetime.now(UTC) + timedelta(days=delays[min(streak - 1, len(delays) - 1)])
        if correct
        else datetime.now(UTC)
    )
    con.execute(
        """INSERT INTO mastery (profile,question_id,streak,total_correct,total_wrong,last_correct,next_due,updated_at)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(profile,question_id) DO UPDATE SET
        streak=excluded.streak,total_correct=excluded.total_correct,total_wrong=excluded.total_wrong,
        last_correct=excluded.last_correct,next_due=excluded.next_due,updated_at=excluded.updated_at""",
        (
            profile,
            qid,
            streak,
            (old["total_correct"] if old else 0) + int(correct),
            (old["total_wrong"] if old else 0) + int(not correct),
            int(correct),
            next_due.isoformat(timespec="seconds"),
            now(),
        ),
    )


def save_answer(
    profile: str, sid: str, question: dict, answer_index: int, database: Path | str = DEFAULT_DB
) -> bool:
    if type(answer_index) is not int or answer_index not in range(4):
        raise ValueError("Answer must be 0, 1, 2 or 3.")
    sess = get_session(profile, sid, database)
    if not sess or question["id"] not in sess["queue"] or sess["kind"] != "mcq":
        raise ValueError("Question not in this MCQ session.")
    if get_answer(profile, sid, question["id"], database) is not None:
        return False
    correct = answer_index == question["answer"]
    with db(database) as con:
        cur = con.execute(
            """INSERT INTO attempts
           (profile,session_id,question_id,kind,answer_index,correct,created_at)
           VALUES (?,?,?,?,?,?,?) ON CONFLICT(profile,session_id,question_id) DO NOTHING""",
            (profile, sid, question["id"], "mcq", answer_index, int(correct), now()),
        )
        if cur.rowcount:
            update_mastery(con, profile, question["id"], correct)
            return True
        return False


def grade_code(
    profile: str, question: dict, solved: bool, code: str, database: Path | str = DEFAULT_DB
) -> None:
    with db(database) as con:
        con.execute(
            """INSERT INTO attempts(profile,session_id,question_id,kind,answer_index,correct,response_text,created_at)
             VALUES (?,?,?,?,?,?,?,?)""",
            (profile, str(uuid.uuid4()), question["id"], "coding", None, int(solved), code, now()),
        )
        update_mastery(con, profile, question["id"], solved)
        con.execute(
            """INSERT INTO code_drafts(profile,question_id,code,updated_at) VALUES (?,?,?,?)
            ON CONFLICT(profile,question_id) DO UPDATE SET code=excluded.code,updated_at=excluded.updated_at""",
            (profile, question["id"], code, now()),
        )


def mastery_map(profile: str, database: Path | str = DEFAULT_DB) -> dict[str, dict]:
    with db(database) as con:
        rows = con.execute("SELECT * FROM mastery WHERE profile=?", (profile,)).fetchall()
    return {row["question_id"]: dict(row) for row in rows}


def bookmarked_ids(profile: str, database: Path | str = DEFAULT_DB) -> set[str]:
    with db(database) as con:
        rows = con.execute(
            "SELECT question_id FROM bookmarks WHERE profile=?", (profile,)
        ).fetchall()
    return {row["question_id"] for row in rows}


def bookmark(profile: str, qid: str, save: bool, database: Path | str = DEFAULT_DB) -> None:
    with db(database) as con:
        if save:
            con.execute(
                "INSERT INTO bookmarks (profile,question_id,created_at) VALUES (?,?,?) ON CONFLICT(profile,question_id) DO NOTHING",
                (profile, qid, now()),
            )
        else:
            con.execute("DELETE FROM bookmarks WHERE profile=? AND question_id=?", (profile, qid))


def get_note(profile: str, qid: str, database: Path | str = DEFAULT_DB) -> str:
    with db(database) as con:
        row = con.execute(
            "SELECT note FROM personal_notes WHERE profile=? AND question_id=?", (profile, qid)
        ).fetchone()
    return row["note"] if row else ""


def save_note(profile: str, qid: str, note: str, database: Path | str = DEFAULT_DB) -> None:
    with db(database) as con:
        con.execute(
            """INSERT INTO personal_notes(profile,question_id,note,updated_at) VALUES (?,?,?,?)
            ON CONFLICT(profile,question_id) DO UPDATE SET note=excluded.note,updated_at=excluded.updated_at""",
            (profile, qid, note, now()),
        )


def get_draft(profile: str, qid: str, database: Path | str = DEFAULT_DB) -> str | None:
    with db(database) as con:
        row = con.execute(
            "SELECT code FROM code_drafts WHERE profile=? AND question_id=?", (profile, qid)
        ).fetchone()
    return row["code"] if row else None


def save_draft(profile: str, qid: str, code: str, database: Path | str = DEFAULT_DB) -> None:
    with db(database) as con:
        con.execute(
            """INSERT INTO code_drafts(profile,question_id,code,updated_at) VALUES (?,?,?,?)
            ON CONFLICT(profile,question_id) DO UPDATE SET code=excluded.code,updated_at=excluded.updated_at""",
            (profile, qid, code, now()),
        )


def select_questions(
    all_questions: list[dict],
    profile: str,
    quantity: int,
    mode: str = "Smart Mix",
    seed: int | None = None,
    database: Path | str = DEFAULT_DB,
) -> list[str]:
    """Create a mixed queue, including wrong and due questions first; no duplicates."""
    if type(quantity) is not int or quantity < 1:
        raise ValueError("Question quantity must be a positive integer.")
    if mode not in ("Smart Mix", "All", "Unseen", "Missed", "Due", "Bookmarked"):
        raise ValueError("Unknown practice mode.")
    mastery = mastery_map(profile, database)
    bookmarks = bookmarked_ids(profile, database)
    current = now()
    filtered = []
    seen = set()
    for q in all_questions:
        if q["id"] in seen:
            continue
        seen.add(q["id"])
        m = mastery.get(q["id"])
        due = bool(m and m["next_due"] <= current)
        missed = bool(m and m["last_correct"] == 0)
        if mode == "Unseen" and m:
            continue
        if mode == "Missed" and not missed:
            continue
        if mode == "Due" and not due:
            continue
        if mode == "Bookmarked" and q["id"] not in bookmarks:
            continue
        filtered.append(q)
    rng = random.Random(seed)
    rng.shuffle(filtered)
    if mode == "Smart Mix":

        def priority(q):
            m = mastery.get(q["id"])
            if m and m["last_correct"] == 0:
                return 0
            if m and m["next_due"] <= current:
                return 1
            if not m:
                return 2
            return 3

        filtered.sort(key=priority)
    return [q["id"] for q in filtered[:quantity]]


def profile_metrics(profile: str, database: Path | str = DEFAULT_DB) -> dict:
    m = mastery_map(profile, database)
    current = now()
    with db(database) as con:
        row = con.execute(
            "SELECT COUNT(*) n, COALESCE(SUM(correct),0) right_count FROM attempts WHERE profile=?",
            (profile,),
        ).fetchone()
    return {
        "attempts": row["n"],
        "correct": row["right_count"],
        "accuracy": round(row["right_count"] * 100 / row["n"]) if row["n"] else 0,
        "studied": len(m),
        "missed": sum(x["last_correct"] == 0 for x in m.values()),
        "due": sum(x["next_due"] <= current for x in m.values()),
        "mastered": sum(x["streak"] >= 3 for x in m.values()),
    }


def attempt_history(
    profile: str, limit: int | None = 200, database: Path | str = DEFAULT_DB
) -> list[dict]:
    """Read a bounded history, or the full history with limit=None, for this profile."""
    query = "SELECT * FROM attempts WHERE profile=? ORDER BY created_at DESC, id DESC"
    params = (profile,)
    if limit is not None:
        if type(limit) is not int or limit < 1:
            raise ValueError("History limit must be a positive integer or None.")
        query += " LIMIT ?"
        params = (profile, limit)
    with db(database) as con:
        rows = con.execute(query, params).fetchall()
    return [dict(x) for x in rows]


def attempts_csv(profile: str, database: Path | str = DEFAULT_DB) -> bytes:
    rows = attempt_history(profile, None, database)
    f = io.StringIO()
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "id",
            "created_at",
            "question_id",
            "kind",
            "answer_index",
            "correct",
            "response_text",
            "session_id",
        ],
    )
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r.get(k) for k in writer.fieldnames})
    return f.getvalue().encode("utf-8-sig")


# ---------------- Cloud user accounts and full history export -----------------
EXPORT_TABLES = ("sessions", "attempts", "mastery", "bookmarks", "personal_notes", "code_drafts")


def register_user(username: str, password: str, database: Path | str = DEFAULT_DB) -> str:
    username = normalize_username(username)
    password_hash = make_password_hash(password)
    with db(database) as con:
        result = con.execute(
            "INSERT INTO users (username,password_hash,created_at) VALUES (?,?,?) ON CONFLICT(username) DO NOTHING",
            (username, password_hash, now()),
        )
    if not result.rowcount:
        raise ValueError("This username is already registered.")
    return username


def authenticate_user(
    username: str, password: str, database: Path | str = DEFAULT_DB
) -> str | None:
    try:
        username = normalize_username(username)
    except ValueError:
        return None
    with db(database) as con:
        row = con.execute(
            "SELECT password_hash FROM users WHERE username=?", (username,)
        ).fetchone()
    # Same expensive hash operation for absent users to reduce username enumeration.
    if row is None:
        make_password_hash("dummy-password-not-reused")
        return None
    return username if verify_password(password, row["password_hash"]) else None


def reset_user_password(username: str, password: str, database: Path | str = DEFAULT_DB) -> None:
    username = normalize_username(username)
    hashed = make_password_hash(password)
    with db(database) as con:
        cur = con.execute("UPDATE users SET password_hash=? WHERE username=?", (hashed, username))
        if not cur.rowcount:
            raise ValueError("User does not exist.")


def user_exists(username: str, database: Path | str = DEFAULT_DB) -> bool:
    username = normalize_username(username)
    with db(database) as con:
        return (
            con.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone() is not None
        )


def export_all_progress(profile: str, database: Path | str = DEFAULT_DB) -> bytes:
    """Complete per-user backup, including notes, drafts, mastery, and sessions.

    Do not expose this ZIP to other users: its content is sensitive study history.
    """
    payload = {
        "format": "python_mastery_backup_v1",
        "user": profile,
        "exported_at_utc": now(),
        "tables": {},
    }
    with db(database) as con:
        for table in EXPORT_TABLES:  # constants, not untrusted SQL identifiers
            rows = con.execute(f"SELECT * FROM {table} WHERE profile=?", (profile,)).fetchall()
            payload["tables"][table] = [dict(row) for row in rows]
    if database == DEFAULT_DB and cloud.is_cloud():
        with db() as con:
            payload["uploaded_packs"] = [
                dict(row)
                for row in con.execute(
                    "SELECT pack_id,body,created_at FROM uploaded_packs"
                ).fetchall()
            ]
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("my_progress.json", json.dumps(payload, indent=2, ensure_ascii=False))
    return output.getvalue()
