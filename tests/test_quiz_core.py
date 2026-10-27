"""Run from project root: python -m pytest -q"""

import json
import tempfile
from pathlib import Path

import quiz_core as c


def questions():
    packs = c.load_packs()
    return next(iter(packs.values()))["questions"]


def test_bank_has_full_topic_coverage():
    p = next(iter(c.load_packs().values()))
    c.validate_pack(p)
    assert len(p["topics"]) == 14
    assert len(p["questions"]) >= 200
    assert len(p["challenges"]) >= 25
    ids = [q["id"] for q in p["questions"] + p["challenges"]]
    assert len(ids) == len(set(ids))
    assert {"Beginner", "Intermediate", "Advanced"} == {q["difficulty"] for q in p["questions"]}
    assert {"notes", "extension"} == {q["source"] for q in p["questions"]}
    for topic in p["topics"]:
        assert any(q["topic"] == topic["id"] for q in p["questions"])


def test_resume_wrong_review_and_subsequent_correct():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "scores.sqlite3"
        c.init_db(path)
        q = questions()[0]
        profile = "Student"
        s = c.new_session(profile, "mcq", [q["id"]], {"mode": "All"}, path)
        assert c.get_session(profile, s, path)["position"] == 0
        wrong = (q["answer"] + 1) % 4
        assert c.save_answer(profile, s, q, wrong, path)
        assert not c.save_answer(profile, s, q, wrong, path)  # Cannot double count
        assert c.get_answer(profile, s, q["id"], path)["correct"] == 0
        assert c.mastery_map(profile, path)[q["id"]]["last_correct"] == 0
        assert q["id"] in c.select_questions([q], profile, 10, "Missed", database=path)
        assert q["id"] in c.select_questions([q], profile, 10, "Due", database=path)
        c.save_note(profile, q["id"], "Remember this.", path)
        c.bookmark(profile, q["id"], True, path)
        c.change_position(profile, s, 1, path)
        assert c.get_session(profile, s, path)["completed_at"] is not None
        assert c.get_session(profile, s, path)["queue"] == [q["id"]]
        # New session, correct on retry; prior bad answer and explanatory note remain.
        s2 = c.new_session(profile, "mcq", [q["id"]], {"mode": "Missed"}, path)
        assert c.save_answer(profile, s2, q, q["answer"], path)
        assert c.mastery_map(profile, path)[q["id"]]["last_correct"] == 1
        assert c.mastery_map(profile, path)[q["id"]]["total_wrong"] == 1
        assert c.mastery_map(profile, path)[q["id"]]["total_correct"] == 1
        assert not c.select_questions([q], profile, 10, "Missed", database=path)
        assert c.get_note(profile, q["id"], path) == "Remember this."
        assert q["id"] in c.bookmarked_ids(profile, path)
        assert len(c.attempt_history(profile, database=path)) == 2
        assert c.profile_metrics(profile, path)["attempts"] == 2
        assert c.profile_metrics("Other learner", path)["attempts"] == 0


def test_coding_drafts_and_manual_grades():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "scores.sqlite3"
        c.init_db(path)
        ch = next(iter(c.load_packs().values()))["challenges"][0]
        c.save_draft("Student", ch["id"], "print(123)", path)
        assert c.get_draft("Student", ch["id"], path) == "print(123)"
        c.grade_code("Student", ch, False, "print(1)", path)
        c.grade_code("Student", ch, True, 'print("Hello World")', path)
        assert len(c.attempt_history("Student", database=path)) == 2
        assert c.get_draft("Student", ch["id"], path) == 'print("Hello World")'
        assert c.mastery_map("Student", path)[ch["id"]]["last_correct"] == 1


def test_rejects_malformed_pack():
    pack = next(iter(c.load_packs().values()))
    bad = json.loads(json.dumps(pack, default=str))
    bad["questions"][0]["options"] = ["same"] * 4
    try:
        c.validate_pack(bad)
    except ValueError as ex:
        assert "unique" in str(ex)
    else:
        raise AssertionError("Malformed pack accepted")
