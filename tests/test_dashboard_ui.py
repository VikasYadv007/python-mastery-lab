"""Exercise analytics and revision using real Streamlit with isolated progress."""

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def dashboard(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    for name in ("app.py", "quiz_core.py", "ui_style.py"):
        shutil.copy2(root / name, tmp_path / name)
    shutil.copytree(root / "packs", tmp_path / "packs")
    spec = importlib.util.spec_from_file_location("quiz_core", tmp_path / "quiz_core.py")
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    monkeypatch.setitem(sys.modules, "quiz_core", core)
    core.init_db()
    pack = next(iter(core.load_packs().values()))
    recovered, missed, bookmarked = pack["questions"][:3]
    coding = pack["challenges"][0]
    profile = "My Python practice"
    for q, correct in ((recovered, False), (recovered, True), (missed, False), (missed, False)):
        sid = core.new_session(profile, "mcq", [q["id"]])
        core.save_answer(profile, sid, q, q["answer"] if correct else (q["answer"] + 1) % 4)
    core.grade_code(profile, coding, False, "# draft")
    core.bookmark(profile, bookmarked["id"], True)
    # Cold chart imports can exceed 15 seconds on Windows; keep integration runs
    # bounded without making them dependent on an already-warm module cache.
    app = AppTest.from_file(str(tmp_path / "app.py"), default_timeout=45)
    return app, core, {"recovered": recovered, "missed": missed, "coding": coding}


def test_progress_filters_and_review_link(dashboard):
    app, core, bank = dashboard
    app.query_params["page"] = "progress"
    app.run()
    assert not app.exception
    assert next(m for m in app.metric if m.label == "Attempts in range").value == "5"
    app.number_input(key="daily_goal_My Python practice").set_value(15).run()
    app.selectbox(key="progress_kind").select("Coding (self-assessed)").run()
    assert not app.exception
    assert next(m for m in app.metric if m.label == "Attempts in range").value == "1"
    assert app.selectbox(key="progress_spotlight").value
    app.button(key="progress_review_link").click().run()
    assert not app.exception
    assert app.selectbox(key="review_kind").value == "Coding (self-assessed)"
    assert app.selectbox(key="review_inspect").value == bank["coding"]["id"]
    app.button(key="review_open_code").click().run()
    assert not app.exception
    assert app.selectbox(key="challenge_picker").value == bank["coding"]["id"]
    assert len(core.attempt_history("My Python practice", None)) == 5
    app.button(key="top_nav_progress").click().run()
    assert app.number_input(key="daily_goal_My Python practice").value == 15


def test_recovered_history_and_due_forecast_navigate_to_queue(dashboard):
    app, core, bank = dashboard
    app.query_params["page"] = "review"
    app.run()
    assert not app.exception
    app.selectbox(key="review_queue").select("Recovered mistakes").run()
    assert app.selectbox(key="review_inspect").value == bank["recovered"]["id"]
    app.session_state["review_tabs"] = "Mistake history"
    app.run()
    app.selectbox(key="review_history_item").select(bank["recovered"]["id"]).run()
    app.button(key="review_history_open").click().run()
    assert not app.exception
    assert app.session_state["review_tabs"] == "Practice queue"
    assert app.selectbox(key="review_inspect").value == bank["recovered"]["id"]
    app.session_state["review_tabs"] = "Review forecast"
    app.run()
    app.button(key="review_due_focus").click().run()
    assert not app.exception
    assert app.session_state["review_tabs"] == "Practice queue"
    assert app.selectbox(key="review_queue").value == "Due now"
    assert len(core.attempt_history("My Python practice", None)) == 5


def test_priority_revision_retries_only_matching_mcqs(dashboard):
    app, core, bank = dashboard
    app.query_params["page"] = "review"
    app.run()
    app.selectbox(key="review_kind").select("MCQs").run()
    assert app.selectbox(key="review_inspect").value == bank["missed"]["id"]
    app.button(key="review_start_batch").click().run()
    assert not app.exception
    sid = app.session_state["active_session_id"]
    session = core.get_session("My Python practice", sid)
    assert session["queue"] == [bank["missed"]["id"]]
    assert app.session_state["current_page"] == "quiz"


def test_bookmark_queue_accepts_unseen_questions_and_search_can_be_empty(dashboard):
    app, _, _ = dashboard
    app.query_params["page"] = "review"
    app.run()
    app.selectbox(key="review_queue").select("Bookmarked").run()
    assert not app.exception
    assert app.selectbox(key="review_inspect").value
    app.text_input(key="review_search").set_value("nothing-matches-this-search").run()
    assert not app.exception
    assert not any(s.key == "review_inspect" for s in app.selectbox)


def test_topic_spotlight_starts_a_quiz_with_only_that_topic(dashboard):
    app, core, bank = dashboard
    app.query_params["page"] = "progress"
    app.run()
    app.session_state["progress_tabs"] = "Topics & difficulty"
    app.run()
    q = bank["recovered"]
    key = f"{q['pack_id']}:{q['topic']}"
    app.selectbox(key="progress_spotlight").select(key).run()
    app.button(key="progress_topic_practice").click().run()
    assert not app.exception
    session = core.get_session("My Python practice", app.session_state["active_session_id"])
    lookup = {q["id"]: q for p in core.load_packs().values() for q in p["questions"]}
    assert 0 < len(session["queue"]) <= 10
    assert all(
        f"{lookup[qid]['pack_id']}:{lookup[qid]['topic']}" == key for qid in session["queue"]
    )


def test_overview_topic_launchpad_opens_the_matching_coding_challenge(dashboard):
    app, core, bank = dashboard
    app.run()
    assert not app.exception
    q = bank["coding"]
    app.selectbox(key="overview_topic").select(f"{q['pack_id']}:{q['topic']}").run()
    app.button(key="home_topic_code").click().run()
    assert not app.exception
    assert app.selectbox(key="challenge_picker").value == q["id"]
    assert len(core.attempt_history("My Python practice", None)) == 5


def test_overview_due_mission_opens_the_due_queue(dashboard):
    app, core, _ = dashboard
    app.run()
    app.button(key="home_due").click().run()
    assert not app.exception
    assert app.selectbox(key="review_queue").value == "Due now"
    assert app.selectbox(key="review_topic").value == "All topics"
    assert len(core.attempt_history("My Python practice", None)) == 5


def test_overview_topic_practice_stays_inside_the_selected_topic(dashboard):
    app, core, bank = dashboard
    app.run()
    q = bank["recovered"]
    key = f"{q['pack_id']}:{q['topic']}"
    app.selectbox(key="overview_topic").select(key).run()
    app.button(key="home_topic_practice").click().run()
    assert not app.exception
    session = core.get_session("My Python practice", app.session_state["active_session_id"])
    lookup = {q["id"]: q for p in core.load_packs().values() for q in p["questions"]}
    assert 0 < len(session["queue"]) <= 10
    assert all(
        f"{lookup[qid]['pack_id']}:{lookup[qid]['topic']}" == key for qid in session["queue"]
    )


def test_empty_overview_links_to_the_library(dashboard, monkeypatch):
    app, core, _ = dashboard
    monkeypatch.setattr(core, "load_packs", lambda: {})
    app.run()
    assert not app.exception
    assert next(b for b in app.button if b.label == "15-question Smart Mix").disabled
    app.button(key="home_empty_library").click().run()
    assert app.session_state["current_page"] == "packs"
