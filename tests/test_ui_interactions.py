"""Real Streamlit reruns against an isolated SQLite database."""

import importlib.util
import shutil
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_navigation_editors_and_quiz(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    for name in ("app.py", "quiz_core.py", "ui_style.py"):
        shutil.copy2(root / name, tmp_path / name)
    shutil.copytree(root / "packs", tmp_path / "packs")
    spec = importlib.util.spec_from_file_location("quiz_core", tmp_path / "quiz_core.py")
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    monkeypatch.setitem(sys.modules, "quiz_core", core)
    app = AppTest.from_file(str(tmp_path / "app.py")).run()
    assert not app.exception
    for page in ("quiz", "review", "progress", "packs", "coding"):
        app.button(key="top_nav_" + page).click().run()
        assert not app.exception
    qid = app.selectbox(key="challenge_picker").value
    key = f"draft_My Python practice_{qid}"
    app.text_area(key=key).set_value('print("saved")').run()
    assert core.get_draft("My Python practice", qid) == 'print("saved")'
    app.text_input(key="offline_profile").set_value("Another learner").run()
    assert app.text_area(key=f"draft_Another learner_{qid}").value != 'print("saved")'
    app.button(key="theme_circle").click().run()
    assert app.session_state["dark_mode"] is True
    app.button(key="top_nav_home").click().run()
    next(b for b in app.button if b.label == "15-question Smart Mix").click().run()
    assert not app.exception
    assert app.radio[0].value is None
    next(b for b in app.button if b.label == "Check my answer").click().run()
    assert app.warning
    app.radio[0].set_value(0)
    next(b for b in app.button if b.label == "Check my answer").click().run()
    assert not app.exception
    next(b for b in app.button if b.label == "Next question").click().run()
    assert not app.exception
    assert (
        core.get_session("Another learner", app.session_state["active_session_id"])["position"] == 1
    )
