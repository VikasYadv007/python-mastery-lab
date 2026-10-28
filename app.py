"""Python Mastery Lab — Python Glass learning workspace.

Run: python -m streamlit run app.py
Database, question IDs and pack schema are unchanged from the original app.
"""

from __future__ import annotations

import csv
import hmac
import html
import io
import json
import os
from collections import Counter
from datetime import UTC, datetime

import streamlit as st

import cloud_storage as cloud
import quiz_core as core
from mastery_lab import analytics
from mastery_lab.charts import chart_spec
from mastery_lab.overview import observatory_html, topic_summaries
from mastery_lab.presentation import as_ist as as_ist
from mastery_lab.presentation import sqlite_backup
from ui_style import python_mark, style, svg_icon

st.set_page_config(
    page_title="Python Mastery Lab · Study Workspace",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "Python Mastery Lab: local practice or password-protected cloud progress."
    },
)


def secret_value(key: str) -> str:
    """Read Streamlit cloud/local secret or environment without exposing it."""
    try:
        return str(st.secrets.get(key) or os.environ.get(key) or "")
    except (FileNotFoundError, AttributeError, KeyError):
        return str(os.environ.get(key, ""))


cloud.configure(secret_value("DATABASE_URL"))
try:
    core.init_db()
except Exception:
    st.error(
        "Cannot connect to your progress database. Check the DATABASE_URL secret, database status, and connection settings."
    )
    st.stop()
try:
    PACKS = core.load_packs()
except (ValueError, OSError, json.JSONDecodeError) as exc:
    st.error(f"Cannot load question packs: {exc}")
    st.stop()

ALL_MCQ = [q for p in PACKS.values() for q in p.get("questions", [])]
ALL_CODE = [q for p in PACKS.values() for q in p.get("challenges", [])]
Q_LOOKUP = {q["id"]: q for q in ALL_MCQ + ALL_CODE}
PAGES = [
    ("home", "Overview"),
    ("quiz", "Quiz Arena"),
    ("coding", "Coding"),
    ("review", "Review"),
    ("progress", "Progress"),
    ("packs", "Lectures"),
]

# Store the appearance in the URL as well as Streamlit session state.
# This keeps it consistent after a browser refresh, without altering question progress.
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = str(st.query_params.get("theme", "light")).lower() == "dark"


def persist_theme() -> None:
    st.query_params["theme"] = "dark" if st.session_state["dark_mode"] else "light"


st.markdown(style("dark" if st.session_state["dark_mode"] else "light"), unsafe_allow_html=True)


def rich_table(
    rows: list[dict], fields: list[str] | None = None, code_fields: tuple[str, ...] = ()
) -> None:
    """Accessible horizontally scrollable table styled for BOTH appearance modes."""
    if not rows:
        st.caption("Nothing to display yet.")
        return
    fields = fields or list(rows[0])
    head = "".join(f"<th scope='col'>{esc(k)}</th>" for k in fields)
    body = ""
    for row in rows:
        cells = ""
        for k in fields:
            value = esc(row.get(k, ""))
            if k in code_fields:
                value = f"<pre>{value}</pre>"
            cells += f"<td>{value}</td>"
        body += f"<tr>{cells}</tr>"
    st.markdown(
        f'<div class="table-scroll" role="region" aria-label="Study data" tabindex="0"><table class="ui-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def consistent_db_backup() -> bytes:
    return sqlite_backup(core.DEFAULT_DB)


def attempts_export_ist(profile: str, rows: list[dict] | None = None) -> bytes:
    """Keep original UTC column for exact ordering, add a human-friendly IST column."""
    rows = core.attempt_history(profile, None) if rows is None else rows
    out = io.StringIO()
    names = [
        "saved_at_ist",
        "created_at",
        "question_id",
        "kind",
        "answer_index",
        "correct",
        "response_text",
        "session_id",
    ]
    writer = csv.DictWriter(out, fieldnames=names)
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {**{k: row.get(k) for k in names}, "saved_at_ist": as_ist(row.get("created_at"))}
        )
    return out.getvalue().encode("utf-8-sig")


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def chip(text: str, kind: str = "") -> str:
    return f'<span class="num-chip {kind}">{esc(text)}</span>'


def hero(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><div class="hero-copy"><div class="eyebrow">{esc(eyebrow)}</div>'
        f"<h1>{esc(title)}</h1><p>{esc(subtitle)}</p>"
        '<div class="hero-signature"><span class="status-dot"></span> A little practice. A lot of possibility.</div></div>'
        '<div class="hero-code" aria-hidden="true"><div class="editor-bar"><span></span><span></span><span></span>'
        '<small>your_next_chapter.py</small></div><div class="editor-body">'
        '<div><i>01</i><span class="syntax-comment"># Small steps. Real progress.</span></div>'
        '<div><i>02</i>skills = [<span class="syntax-string">"learn"</span>, <span class="syntax-string">"build"</span>]</div>'
        '<div><i>03</i><span class="syntax-keyword">for</span> step <span class="syntax-keyword">in</span> skills:</div>'
        '<div><i>04</i>&nbsp;&nbsp;&nbsp;&nbsp;<span class="syntax-function">print</span>(step)</div></div>'
        f'<div class="editor-footer">{python_mark(18)} Python · Made for curious minds</div></div></div>',
        unsafe_allow_html=True,
    )


def section(title: str, caption: str = "") -> None:
    st.markdown(f'<h2 class="section-title">{esc(title)}</h2>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-sub">{esc(caption)}</div>', unsafe_allow_html=True)


def go_to(page: str) -> None:
    st.session_state["current_page"] = page
    st.query_params["page"] = page
    st.rerun()


def cloud_login() -> str:
    """Require a password per new browser session; retain theme controls on sign-in."""
    if not cloud.is_cloud():
        return ""
    username = st.session_state.get("cloud_username")
    if username:
        return username

    # The same header and circular theme control appear on the sign-in screen.
    site_header(None)

    hero(
        "Your progress, protected",
        "Welcome back",
        "Sign in to continue your practice, saved quizzes, notes, and revision plan. Your progress stays with your account.",
    )
    outer_left, middle, outer_right = st.columns([1, 2.1, 1])
    with middle:
        tab_login, tab_create = st.tabs(["Sign in", "Create an account"])
        with tab_login:
            with st.form("cloud_signin", clear_on_submit=True):
                user = st.text_input("Username", key="signin_username", max_chars=30)
                password = st.text_input("Password", type="password", key="signin_password")
                submitted = st.form_submit_button(
                    "Sign in", type="primary", use_container_width=False
                )
            if submitted:
                if core.authenticate_user(user, password):
                    st.session_state["cloud_username"] = core.normalize_username(user)
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
        with tab_create:
            if not secret_value("REGISTRATION_CODE"):
                st.info("New accounts are invite-only. Ask the app owner to create your account.")
            else:
                with st.form("cloud_signup", clear_on_submit=True):
                    new_user = st.text_input("Choose a username (3–30 characters)")
                    new_password = st.text_input(
                        "New password (at least 10 characters)", type="password"
                    )
                    repeated = st.text_input("Confirm password", type="password")
                    invite = st.text_input("Private invitation code", type="password")
                    sign_up = st.form_submit_button(
                        "Create account", type="primary", use_container_width=False
                    )
                if sign_up:
                    if not hmac.compare_digest(invite, secret_value("REGISTRATION_CODE")):
                        st.error("Invalid invitation code.")
                    elif new_password != repeated:
                        st.error("Passwords don't match.")
                    else:
                        try:
                            st.session_state["cloud_username"] = core.register_user(
                                new_user, new_password
                            )
                            st.success("Account created. Opening your workspace.")
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))
        st.caption(
            "Passwords are hashed before storage. You'll sign in again after a full browser refresh."
        )
    st.stop()


def start_session(
    profile: str, qs: list[dict], mode: str, size: int, filters: dict | None = None
) -> bool:
    if not qs:
        st.info("No questions match this practice session. Try different filters.")
        return False
    ids = core.select_questions(qs, profile, min(size, len(qs)), mode)
    if not ids:
        st.warning(
            f"No questions are available for '{mode}' in this selection. Try All or Smart Mix."
        )
        return False
    st.session_state["active_session_id"] = core.new_session(
        profile, "mcq", ids, {"mode": mode, "filters": filters or {}}
    )
    go_to("quiz")
    return True


def item_meta(q: dict) -> None:
    source = "PDF material" if q["source"] == "notes" else "Advanced extension"
    page = ", ".join(str(p) for p in q.get("pages", []))
    st.markdown(
        chip(
            q["difficulty"],
            "chip-teal"
            if q["difficulty"] == "Beginner"
            else "chip-amber"
            if q["difficulty"] == "Advanced"
            else "",
        )
        + chip(q["topic_name"], "chip-muted")
        + chip(source + (f" · p. {page}" if page else ""), "chip-muted"),
        unsafe_allow_html=True,
    )


def bookmark_control(profile: str, q: dict) -> None:
    marked = q["id"] in core.bookmarked_ids(profile)
    if st.button(
        "Bookmarked" if marked else "Bookmark",
        key="mark_" + q["id"],
        use_container_width=False,
        help="Keep this question in your Bookmarked review queue",
    ):
        core.bookmark(profile, q["id"], not marked)
        st.rerun()


def save_editor(profile: str, qid: str, key: str, kind: str) -> None:
    """Persist committed editor changes before navigation removes the widget."""
    save = core.save_draft if kind == "draft" else core.save_note
    save(profile, qid, st.session_state[key])


def personal_note(profile: str, q: dict) -> None:
    with st.expander("Personal revision note"):
        field_key = f"note_{profile}_{q['id']}"
        if field_key not in st.session_state:
            st.session_state[field_key] = core.get_note(profile, q["id"])
        st.text_area(
            "Explain the idea in your own words",
            key=field_key,
            height=118,
            on_change=save_editor,
            args=(profile, q["id"], field_key, "note"),
            placeholder="What makes this question tricky? How will you recognize it next time?",
        )
        if st.button("Save note", key="save_note_" + q["id"]):
            core.save_note(profile, q["id"], st.session_state[field_key])
            st.toast("Revision note saved", icon="✅")
        st.caption("Changes save when you leave the text field. Use Save note to save immediately.")


def quiz_session(profile: str, sid: str) -> None:
    session = core.get_session(profile, sid)
    if session is None:
        st.session_state.pop("active_session_id", None)
        st.error("This session is no longer available for this learner profile.")
        return
    queue, index = session["queue"], session["position"]
    if index >= len(queue):
        answers = [core.get_answer(profile, sid, qid) for qid in queue]
        answered = sum(a is not None for a in answers)
        right = sum(bool(a and a["correct"]) for a in answers)
        hero(
            "Session finished · Saved to your history",
            "Nice work — session complete!",
            "Your attempts, explanations and revision schedule are saved to your account.",
        )
        x, y, z = st.columns(3)
        x.metric("Questions answered", f"{answered}/{len(queue)}")
        y.metric("Correct responses", right)
        z.metric("Accuracy", f"{right / answered:.0%}" if answered else "—")
        missed = [
            Q_LOOKUP[qid]
            for qid, ans in zip(queue, answers)
            if ans and not ans["correct"] and qid in Q_LOOKUP
        ]
        if missed:
            section("Worth revisiting", "These questions stay in your learning history.")
            for q in missed[:12]:
                st.markdown(
                    f'<div class="review-item"><b>{esc(q["prompt"])}</b><p>{esc(q["topic_name"])} · {esc(q["id"])}</p></div>',
                    unsafe_allow_html=True,
                )
            if st.button("Practice these mistakes again", key="retry_session_mistakes"):
                start_session(profile, missed, "All", len(missed))
        with st.container(key="completed_actions"):
            first, second = st.columns(2, gap="small")
            with first:
                if st.button("Back to overview", type="primary", use_container_width=False):
                    st.session_state.pop("active_session_id", None)
                    go_to("home")
            with second:
                if st.button("Browse answered questions", use_container_width=False):
                    core.change_position(profile, sid, 0)
                    st.rerun()
        return

    q = Q_LOOKUP.get(queue[index])
    if q is None:
        st.error("Question missing. Restore its JSON question pack to resume the saved session.")
        return
    previous = core.get_answer(profile, sid, q["id"])
    top_left, top_right = st.columns([2.7, 1.3], vertical_alignment="center")
    with top_left:
        st.markdown(
            f'<div class="question-label">Practice session · Question {index + 1} of {len(queue)}</div>'
            f'<div class="question-topline">{esc(q["topic_name"])} · '
            f"{'Saved to your cloud account' if cloud.is_cloud() else 'Saved on this computer'}</div>",
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("Save & leave", key="leave_session", use_container_width=False):
            st.session_state.pop("active_session_id", None)
            go_to("quiz")
    st.progress((index + int(previous is not None)) / len(queue))
    with st.container(border=True, key="question_intro"):
        left, right = st.columns([3, 1.25], vertical_alignment="bottom")
        with left:
            st.markdown(
                f'<div class="question-heading">{esc(q["prompt"])}</div>', unsafe_allow_html=True
            )
        with right:
            bookmark_control(profile, q)
        item_meta(q)
        st.caption(f"Question ID: {q['id']}")
        if q.get("code"):
            st.code(q["code"], language="python")

    if previous is None:
        with st.form(f"answer_form_{sid}_{q['id']}", clear_on_submit=False):
            st.markdown(
                '<div class="option-title">Select the best answer</div>', unsafe_allow_html=True
            )
            choice = st.radio(
                "Answer options",
                range(4),
                index=None,
                format_func=lambda j: f"{'ABCD'[j]}.  {q['options'][j]}",
                key=f"choice_{sid}_{q['id']}",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button(
                "Check my answer", type="primary", use_container_width=False
            )
            if submitted:
                if choice is None:
                    st.warning("Select an option first.")
                else:
                    core.save_answer(profile, sid, q, choice)
                    st.rerun()
    else:
        selected = previous["answer_index"]
        correct = q["answer"]
        for i, option in enumerate(q["options"]):
            cls = "option-correct" if i == correct else "option-wrong" if i == selected else ""
            suffix = (
                " · Correct answer"
                if i == correct
                else " · Your selection"
                if i == selected
                else ""
            )
            st.markdown(
                f'<div class="option-card {cls}"><span class="option-letter">{"ABCD"[i]}</span>'
                f"<span>{esc(option)}<strong>{esc(suffix)}</strong></span></div>",
                unsafe_allow_html=True,
            )
        successful = bool(previous["correct"])
        title = "Correct — keep building momentum" if successful else "Let's learn from this one"
        st.markdown(
            f'<div class="feedback {"" if successful else "feedback-bad"}">'
            f"<strong>{esc(title)}</strong>"
            f"<p>{esc('This question is scheduled for spaced revision.' if successful else 'Saved to your mistake history and due-review queue.')}</p>"
            f"<p><b>Why:</b> {esc(q['explanation'])}</p></div>",
            unsafe_allow_html=True,
        )
        if q.get("tags"):
            st.caption("Related concepts: " + ", ".join(q["tags"]))
    personal_note(profile, q)
    st.divider()
    with st.container(key="question_actions"):
        back, next_btn = st.columns(2, gap="small")
        with back:
            if st.button("Previous", disabled=index == 0, use_container_width=False):
                core.change_position(profile, sid, index - 1)
                st.rerun()
        with next_btn:
            label = "Finish session" if index + 1 == len(queue) else "Next question"
            if st.button(
                label, type="primary", disabled=previous is None, use_container_width=False
            ):
                core.change_position(profile, sid, index + 1)
                st.rerun()


def quiz_page(profile: str) -> None:
    active = st.session_state.get("active_session_id")
    if active and core.get_session(profile, active):
        quiz_session(profile, active)
        return
    hero(
        "MCQ / Learn · Test · Repeat",
        "Build your next practice session",
        "Focused questions, immediate explanations, and revision queues that remember every mistake.",
    )
    sessions = core.recent_sessions(profile, limit=40, unfinished=True)
    if sessions:
        section(
            "Pick up where you left off", "Your earlier attempts and selected questions are intact."
        )
        # A saved session with an already-completed position is not displayed here.
        choices = {
            s[
                "id"
            ]: f"{as_ist(s['created_at'])}  ·  {s['position']}/{len(s['queue'])} questions  ·  {s['configuration'].get('mode', 'Practice')}"
            for s in sessions
        }
        a, b = st.columns([3, 1], vertical_alignment="bottom")
        with a:
            selected_sid = st.selectbox(
                "Unfinished sessions",
                list(choices),
                format_func=lambda k: choices[k],
                label_visibility="collapsed",
            )
        with b:
            if st.button("Resume session", type="primary", use_container_width=False):
                st.session_state["active_session_id"] = selected_sid
                st.rerun()

    section(
        "Create a new quiz",
        "Choose your practice mode, then refine the questions if you want to focus on a specific concept.",
    )
    modes = {
        "Smart Mix": "Recommended · missed first, then due and unseen",
        "All": "Any question from the selected topics",
        "Unseen": "Questions you haven't attempted yet",
        "Missed": "Retry mistakes from earlier sessions",
        "Due": "Questions ready for spaced revision",
        "Bookmarked": "Your saved favorites",
    }
    mode = st.selectbox("Practice mode", list(modes), format_func=lambda k: f"{k} — {modes[k]}")
    with st.expander("Refine topics, lecture and difficulty", expanded=True):
        a, b = st.columns(2)
        packs = {p["title"]: p["pack_id"] for p in PACKS.values()}
        with a:
            name = st.selectbox("Lecture pack", ["All lectures"] + list(packs), key="quiz_pack")
        base = (
            ALL_MCQ
            if name == "All lectures"
            else [q for q in ALL_MCQ if q["pack_id"] == packs[name]]
        )
        with b:
            topic_name = st.selectbox(
                "Topic", ["All topics"] + sorted({q["topic_name"] for q in base}), key="quiz_topic"
            )
        if topic_name != "All topics":
            base = [q for q in base if q["topic_name"] == topic_name]
        a2, b2 = st.columns(2)
        with a2:
            levels = st.multiselect(
                "Difficulty",
                ["Beginner", "Intermediate", "Advanced"],
                default=["Beginner", "Intermediate", "Advanced"],
                key="quiz_levels",
            )
        with b2:
            source = st.selectbox(
                "Source",
                ["Lecture + tricky extensions", "Lecture PDF only", "Tricky extensions only"],
                key="quiz_source",
            )
        base = [q for q in base if q["difficulty"] in levels]
        if source == "Lecture PDF only":
            base = [q for q in base if q["source"] == "notes"]
        elif source == "Tricky extensions only":
            base = [q for q in base if q["source"] == "extension"]

    mastered = core.mastery_map(profile)
    marks = core.bookmarked_ids(profile)
    due_now = core.now()
    pool = [
        q
        for q in base
        if (
            mode in ("All", "Smart Mix")
            or (mode == "Unseen" and q["id"] not in mastered)
            or (mode == "Missed" and q["id"] in mastered and not mastered[q["id"]]["last_correct"])
            or (mode == "Due" and q["id"] in mastered and mastered[q["id"]]["next_due"] <= due_now)
            or (mode == "Bookmarked" and q["id"] in marks)
        )
    ]
    left, right = st.columns([2, 1], vertical_alignment="bottom")
    with left:
        st.markdown(
            f'<div class="lead-strip"><div><strong>{len(pool)} questions ready for {esc(mode.lower())}</strong><br>'
            f"<span>{len(base)} questions match the lecture and topic filters</span></div>"
            f"{chip('Saved automatically', 'chip-teal')}</div>",
            unsafe_allow_html=True,
        )
    with right:
        count = st.number_input(
            "Questions per session",
            min_value=1,
            max_value=max(1, len(pool)),
            value=min(15, max(1, len(pool))),
            step=1,
        )
    if st.button("Start practicing", type="primary", use_container_width=False, disabled=not pool):
        start_session(profile, base, mode, int(count), {"topic": topic_name, "source": source})
    if not pool:
        st.info("Nothing matches this mode yet. Try Smart Mix, All, or broaden your filters.")


def overview_page(profile: str) -> None:
    current = datetime.now(UTC)
    mastery = core.mastery_map(profile)
    records = analytics.filtered_attempts(
        core.attempt_history(profile, None),
        Q_LOOKUP,
        today=current.astimezone(analytics.IST).date(),
    )
    activity = analytics.activity_summary(records, current.astimezone(analytics.IST).date())
    topics = topic_summaries(PACKS, mastery)
    queues = analytics.review_queues(mastery, set(), set(Q_LOOKUP), current)
    known = set(mastery) & set(Q_LOOKUP)
    summary = {
        "mcqs": len(ALL_MCQ),
        "coding": len(ALL_CODE),
        "total": len(Q_LOOKUP),
        "studied": len(known),
        "mastered": sum(mastery[qid]["streak"] >= 3 for qid in known),
        "accuracy": activity["accuracy"],
        "attempts": len(records),
        "streak": activity["streak"],
        "due": len(queues["Due now"]),
    }
    with st.container(key="overview_scene"):
        # The executable source is authored in assets/overview.js. Imported pack
        # text is escaped into inert data and is never inserted into that source.
        st.html(
            observatory_html(summary, topics, dark=st.session_state["dark_mode"]),
            unsafe_allow_javascript=True,
        )

    section(
        "Your next small step",
        "Build a little momentum. Your progress takes care of the bigger picture.",
    )
    with st.container(border=True, key="home_mission"):
        left, right = st.columns([2, 1], vertical_alignment="center")
        with left:
            if summary["due"]:
                st.markdown(
                    f'<div class="eyebrow">YOUR PERSONAL FLIGHT PLAN</div><div class="feature-title">{summary["due"]} ideas are ready for another look.</div><div class="feature-description">A short revision session can turn a familiar mistake into a reliable skill.</div>',
                    unsafe_allow_html=True,
                )
            elif activity["today"]:
                st.markdown(
                    f'<div class="eyebrow">YOU SHOWED UP TODAY</div><div class="feature-title">{activity["today"]} attempts. One step further.</div><div class="feature-description">Keep exploring, or give the ideas a little time to settle.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="eyebrow">BEGIN ANYWHERE</div><div class="feature-title">Your next good idea starts with a question.</div><div class="feature-description">Try a quick Smart Mix or pick a concept in the topic launchpad below.</div>',
                    unsafe_allow_html=True,
                )
        with right:
            if summary["due"]:
                if st.button("Review what’s due", key="home_due", type="primary"):
                    st.session_state["review_queue"] = "Due now"
                    st.session_state["review_kind"] = "All practice"
                    st.session_state["review_pack"] = "All lectures"
                    st.session_state["review_topic"] = "All topics"
                    st.session_state["review_level"] = "Any difficulty"
                    st.session_state["review_search"] = ""
                    go_to("review")
            elif st.button("See your learning pulse", key="home_pulse"):
                go_to("progress")
        with st.container(key="quick_actions"):
            quick_start, quick_review = st.columns(2, gap="small")
            with quick_start:
                if st.button(
                    "15-question Smart Mix",
                    type="primary",
                    use_container_width=False,
                    disabled=not ALL_MCQ,
                ):
                    start_session(profile, ALL_MCQ, "Smart Mix", 15)
            with quick_review:
                candidates = [q for q in ALL_MCQ if q["id"] in queues["Needs another try"]]
                if st.button(
                    "Retry previous mistakes", use_container_width=False, disabled=not candidates
                ):
                    start_session(profile, candidates, "All", 15)

    sessions = core.recent_sessions(profile, limit=10, unfinished=True)
    if sessions:
        most_recent = sessions[0]
        with st.container(border=True, key="home_resume"):
            left, right = st.columns([2, 1], vertical_alignment="center")
            with left:
                st.markdown(
                    f'<div class="eyebrow">YOUR PLACE IS SAVED</div><div class="feature-title">Pick up your last orbit.</div><div class="feature-description">Question {most_recent["position"] + 1} of {len(most_recent["queue"])} · {esc(most_recent["configuration"].get("mode", "Practice"))}</div>',
                    unsafe_allow_html=True,
                )
            with right:
                if st.button("Continue saved session", type="primary", use_container_width=False):
                    st.session_state["active_session_id"] = most_recent["id"]
                    go_to("quiz")

    section(
        "Choose your constellation",
        "The animation is a playground. This launchpad connects real topics to your next practice session.",
    )
    if topics:
        topic_map = {t["key"]: t for t in topics}
        with st.container(border=True, key="home_topic_launchpad"):
            selected = select_choice(
                "Choose a topic to practise",
                list(topic_map),
                "overview_topic",
                format_func=lambda k: f"{topic_map[k]['name']} · {topic_map[k]['lecture']}",
            )
            topic = topic_map[selected]
            percentage = (
                round(topic["studied"] * 100 / topic["questions"]) if topic["questions"] else 0
            )
            left, right = st.columns([1, 2], vertical_alignment="center")
            with left:
                st.markdown(
                    f'<div class="home-coverage" role="meter" aria-label="Questions explored in {esc(topic["name"])}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{percentage}"><svg viewBox="0 0 140 140" aria-hidden="true"><circle class="home-ring-track" cx="70" cy="70" r="54"/><circle class="home-ring-fill" cx="70" cy="70" r="54" style="--ring-offset:{339.3 * (1 - percentage / 100):.2f}"/></svg><div><strong>{percentage}%</strong><span>explored</span></div></div>',
                    unsafe_allow_html=True,
                )
            with right:
                accuracy = f"{topic['accuracy']}%" if topic["accuracy"] is not None else "—"
                st.markdown(
                    f'<div class="eyebrow">TOPIC SPOTLIGHT</div><h3 class="chart-title">{esc(topic["name"])}</h3><div class="home-topic-chips">{chip(str(topic["mcqs"]) + " MCQs")}{chip(str(topic["coding"]) + " coding tasks", "chip-amber")}</div><div class="home-topic-facts"><span><b>{topic["studied"]}/{topic["questions"]}</b> explored</span><span><b>{accuracy}</b> accuracy</span><span><b>{topic["mastered"]}</b> mastered</span></div>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    "Coverage counts first attempts. Accuracy includes self-assessed coding results; mastered means three correct attempts in a row."
                )
            candidates = [
                q for q in Q_LOOKUP.values() if f"{q['pack_id']}:{q['topic']}" == selected
            ]
            mcqs = [q for q in candidates if q["type"] == "mcq"]
            codes = [q for q in candidates if q["type"] == "coding"]
            with st.container(key="home_topic_actions"):
                a, b, c = st.columns(3, gap="small")
                with a:
                    if st.button(
                        "Practice this topic",
                        key="home_topic_practice",
                        type="primary",
                        disabled=not mcqs,
                    ):
                        start_session(
                            profile,
                            mcqs,
                            "Smart Mix",
                            min(10, len(mcqs)),
                            {"topic": topic["name"], "source": "Overview constellation"},
                        )
                with b:
                    if st.button(
                        "Open a coding challenge", key="home_topic_code", disabled=not codes
                    ):
                        open_coding_question(codes[0]["id"])
                with c:
                    if st.button(
                        "Review this topic", key="home_topic_review", disabled=not topic["studied"]
                    ):
                        st.session_state["review_pack"] = topic["pack_id"]
                        st.session_state["review_topic"] = topic["name"]
                        st.session_state["review_kind"] = "All practice"
                        st.session_state["review_level"] = "Any difficulty"
                        st.session_state["review_search"] = ""
                        st.session_state["review_queue"] = (
                            "Needs another try" if topic["missed"] else "All studied"
                        )
                        go_to("review")
    else:
        st.info("Your learning universe is empty. Import a lecture pack to start exploring.")
        if st.button("Open the lecture library", key="home_empty_library"):
            go_to("packs")

    section(
        "Three ways to move forward",
        "A question, a working program, or a second look. Pick the kind of progress you need.",
    )
    cards = [
        (
            "quiz",
            "01 / THINK IT THROUGH",
            "Practice questions",
            "A focused topic or an unexpected mix. Test the idea, then understand why.",
            "Open quiz arena",
        ),
        (
            "coding",
            "02 / MAKE IT REAL",
            "Build something small",
            "Turn a concept into a working program. Keep your drafts and test your ideas.",
            "Open coding dojo",
        ),
        (
            "review",
            "03 / CONNECT THE DOTS",
            "Make it stick",
            "Return to your mistakes, follow your revision plan, and see what has clicked.",
            "Open revision lab",
        ),
    ]
    for col, (page, kicker, title, desc, button) in zip(st.columns(3), cards):
        with col:
            with st.container(border=True, key="feature_" + page):
                st.markdown(
                    f'<div class="home-feature-kicker">{esc(kicker)}</div><div class="feature-icon">{svg_icon(page, 24)}</div><div class="feature-title">{esc(title)}</div><div class="feature-description">{esc(desc)}</div>',
                    unsafe_allow_html=True,
                )
                if st.button(button, key="card_" + page, use_container_width=False):
                    go_to(page)

    section("Your lecture shelf", "Open a lecture to see its concepts and question coverage.")
    for pack in PACKS.values():
        with st.expander(
            f"{pack['title']} · {len(pack.get('questions', []))} MCQs · {len(pack.get('challenges', []))} coding tasks"
        ):
            counts = Counter(q["topic"] for q in pack.get("questions", []))
            st.markdown(
                "".join(
                    f'<span class="topic-pill">{esc(t["name"])} · {counts[t["id"]]}</span>'
                    for t in pack["topics"]
                ),
                unsafe_allow_html=True,
            )
            st.caption(
                "PDF material follows the lecture; advanced extensions explore related tricks. Use the topic launchpad to focus your practice."
            )


def coding_page(profile: str) -> None:
    hero(
        "Hands-on / VS Code companion",
        "Coding dojo",
        "Solve real programming problems in VS Code, save working drafts, and check your solution when you're ready.",
    )
    if not ALL_CODE:
        st.info("No coding challenges are installed yet.")
        return
    a, b, c = st.columns(3)
    with a:
        pack_filter = st.selectbox(
            "Lecture", ["All lectures"] + [p["title"] for p in PACKS.values()], key="code_pack"
        )
    with b:
        level_filter = st.selectbox(
            "Difficulty",
            ["Any difficulty", "Beginner", "Intermediate", "Advanced"],
            key="code_level",
        )
    with c:
        status = st.selectbox(
            "Progress",
            ["All tasks", "Unseen", "Needs practice", "Previously solved"],
            key="code_status",
        )
    available = ALL_CODE[:]
    if pack_filter != "All lectures":
        available = [q for q in available if q["pack_title"] == pack_filter]
    if level_filter != "Any difficulty":
        available = [q for q in available if q["difficulty"] == level_filter]
    map_ = core.mastery_map(profile)
    if status == "Unseen":
        available = [q for q in available if q["id"] not in map_]
    elif status == "Needs practice":
        available = [q for q in available if q["id"] in map_ and not map_[q["id"]]["last_correct"]]
    elif status == "Previously solved":
        available = [q for q in available if q["id"] in map_ and map_[q["id"]]["last_correct"]]
    if not available:
        st.info("No challenges match these filters.")
        return
    titles = {q["id"]: f"{q['title']}  ·  {q['difficulty']}" for q in available}
    qid = st.selectbox(
        "Select a challenge",
        list(titles),
        format_func=lambda id_: titles[id_],
        key="challenge_picker",
    )
    q = Q_LOOKUP[qid]
    section(q["title"])
    item_meta(q)
    st.markdown(q["prompt"])
    section(
        "Example test cases",
        "Run the examples yourself in VS Code; inputs are supplied one line at a time.",
    )
    rich_table(
        [{"Input": x["input"], "Expected output": x["output"]} for x in q["samples"]],
        code_fields=("Input", "Expected output"),
    )
    helper, hint = st.columns(2)
    with helper:
        with st.expander("Starter code"):
            st.code(q["starter"] or "# Write your Python code here", language="python")
    with hint:
        with st.expander("Reveal a hint"):
            st.write(q["hint"])
    section(
        "Your working solution",
        "Drafts save to your profile; this app never executes code. Run and test it in VS Code first.",
    )
    draft_key = f"draft_{profile}_{qid}"
    if draft_key not in st.session_state:
        saved_draft = core.get_draft(profile, qid)
        st.session_state[draft_key] = q["starter"] if saved_draft is None else saved_draft
    st.text_area(
        "Your Python code",
        key=draft_key,
        height=260,
        label_visibility="collapsed",
        on_change=save_editor,
        args=(profile, qid, draft_key, "draft"),
        placeholder="# Paste your tested VS Code solution here",
    )
    st.caption("Changes save when you leave the editor. Run your code in VS Code to test it.")
    with st.container(key="code_actions"):
        save_col, reveal_col = st.columns(2, gap="small")
        with save_col:
            if st.button("Save my draft", use_container_width=False, key="save_draft_" + qid):
                core.save_draft(profile, qid, st.session_state[draft_key])
                st.toast(
                    "Draft saved to your cloud account"
                    if cloud.is_cloud()
                    else "Draft saved on this computer",
                    icon="✅",
                )
        with reveal_col:
            if st.button(
                "Reveal reference solution", use_container_width=False, key="reveal_code_" + qid
            ):
                st.session_state[f"revealed_{profile}_{qid}"] = True
    st.download_button(
        "Download Python file",
        st.session_state[draft_key],
        file_name=f"{qid}.py",
        mime="text/x-python",
        key="download_code_" + qid,
    )
    if st.session_state.get(f"revealed_{profile}_{qid}"):
        section("Reference solution", "Read and understand it before grading your attempt.")
        st.code(q["solution"], language="python")
        st.info(q["rubric"])
        with st.container(key="grading_actions"):
            yes, no = st.columns(2, gap="small")
            with yes:
                if st.button(
                    "Solved independently",
                    type="primary",
                    use_container_width=False,
                    key="grade_yes_" + qid,
                ):
                    core.grade_code(profile, q, True, st.session_state[draft_key])
                    st.toast("Recorded as solved", icon="✅")
            with no:
                if st.button(
                    "Need more practice", use_container_width=False, key="grade_no_" + qid
                ):
                    core.grade_code(profile, q, False, st.session_state[draft_key])
                    st.toast("Added to your practice queue", icon="🔁")
    personal_note(profile, q)


def select_choice(label: str, options: list, key: str, **kwargs):
    """Keep dependent filters valid when a parent filter changes."""
    if key in st.session_state and st.session_state[key] not in options:
        st.session_state[key] = options[0]
    return st.selectbox(label, options, key=key, **kwargs)


def content_filters(prefix: str) -> dict:
    kind_col, pack_col, topic_col = st.columns(3)
    with kind_col:
        kind = select_choice(
            "Practice type", ["All practice", "MCQs", "Coding (self-assessed)"], prefix + "_kind"
        )
    with pack_col:
        pack = select_choice(
            "Lecture",
            ["All lectures"] + list(PACKS),
            prefix + "_pack",
            format_func=lambda k: PACKS[k]["title"] if k in PACKS else k,
        )
    topics = sorted(
        {
            q["topic_name"]
            for q in Q_LOOKUP.values()
            if analytics.content_matches(q, kind=kind, pack=pack)
        }
    )
    with topic_col:
        topic = select_choice("Topic", ["All topics"] + topics, prefix + "_topic")
    return {"kind": kind, "pack": pack, "topic": topic}


def draw_chart(
    values: list[dict], kind: str, title: str, caption: str, key: str, *, selectable=False
):
    with st.container(border=True, key="chart_" + key):
        st.markdown(
            f'<h3 class="chart-title">{esc(title)}</h3><p class="chart-caption">{esc(caption)}</p>',
            unsafe_allow_html=True,
        )
        return st.vega_lite_chart(
            spec=chart_spec(values, kind, st.session_state["dark_mode"]),
            theme=None,
            width="stretch",
            key=key,
            on_select="rerun" if selectable else "ignore",
            selection_mode="topic_pick" if selectable else None,
            alt=title + ". " + caption,
        )


def open_coding_question(qid: str) -> None:
    st.session_state["code_pack"] = "All lectures"
    st.session_state["code_level"] = "Any difficulty"
    st.session_state["code_status"] = "All tasks"
    st.session_state["challenge_picker"] = qid
    go_to("coding")


def set_review_item(qid: str) -> None:
    st.session_state["review_inspect"] = qid


def remember_daily_goal(profile: str) -> None:
    # Store outside the widget key so Streamlit's page cleanup does not erase it.
    st.session_state["daily_target_" + profile] = st.session_state["daily_goal_" + profile]


def review_inspector(profile: str, q: dict, records: list[dict], mastery: dict) -> None:
    history = [r for r in records if r["question_id"] == q["id"]]
    m = mastery.get(q["id"], {})
    with st.container(border=True, key="review_inspector"):
        st.markdown(
            f'<div class="eyebrow">QUESTION SPOTLIGHT · {esc(q["id"])}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="question-heading">{esc(q.get("title", q["prompt"]))}</div>',
            unsafe_allow_html=True,
        )
        if q["type"] == "coding":
            st.write(q["prompt"])
        item_meta(q)
        if q.get("code"):
            st.code(q["code"], language="python")
        st.caption(
            f"Attempts: {len(history)} · Mistakes: {m.get('total_wrong', 0)} · Correct streak: {m.get('streak', 0)}"
            + (f" · Next review: {as_ist(m.get('next_due'))}" if m else " · Not attempted yet")
        )
        action, saved = st.columns([2, 1])
        with action:
            if q["type"] == "mcq":
                if st.button("Try this question again", type="primary", key="review_retry_one"):
                    start_session(profile, [q], "All", 1, {"source": "Review spotlight"})
            elif st.button("Open this coding challenge", type="primary", key="review_open_code"):
                open_coding_question(q["id"])
        with saved:
            bookmark_control(profile, q)
        if q["type"] == "mcq":
            if history:
                latest = history[0]
                selected = latest.get("answer_index")
                if type(selected) is int and 0 <= selected < len(q["options"]):
                    st.caption(
                        f"Latest choice: {q['options'][selected]} · {'Correct' if latest['correct'] else 'Incorrect'} · {as_ist(latest['created_at'])}"
                    )
            with st.expander("Reveal answer & reasoning"):
                st.success("Correct answer: " + q["options"][q["answer"]])
                st.write(q["explanation"])
        else:
            st.caption(
                "Coding attempts are self-assessed. Test your code before marking it solved."
            )
        with st.expander(f"Attempt timeline ({len(history)})"):
            rich_table(
                [
                    {
                        "When (IST)": as_ist(r["created_at"]),
                        "Result": "Correct / solved" if r["correct"] else "Incorrect / practice",
                        "Your answer": q["options"][r["answer_index"]]
                        if q["type"] == "mcq"
                        and type(r.get("answer_index")) is int
                        and 0 <= r["answer_index"] < 4
                        else "Self-assessed coding",
                    }
                    for r in history[:20]
                ]
            )
            if len(history) > 20:
                st.caption(
                    "Showing the latest 20 attempts. Complete history is included in exports."
                )
        personal_note(profile, q)


def review_page(profile: str) -> None:
    hero(
        "Practice / Recover / Remember",
        "Your revision studio",
        "Turn mistakes into progress. Find what needs attention, retry with purpose, and plan your next review.",
    )
    if st.session_state.get("review_pending_queue"):
        st.session_state["review_queue"] = st.session_state.pop("review_pending_queue")
        st.session_state["review_tabs"] = "Practice queue"
    if st.session_state.get("review_pending"):
        st.session_state["review_queue"] = "All studied"
        st.session_state["review_inspect"] = st.session_state.pop("review_pending")
        st.session_state["review_tabs"] = "Practice queue"
    mastery = core.mastery_map(profile)
    records = core.attempt_history(profile, None)
    current = datetime.now(UTC)
    queues = analytics.review_queues(mastery, core.bookmarked_ids(profile), set(Q_LOOKUP), current)
    cols = st.columns(4)
    for col, label in zip(
        cols, ("Needs another try", "Due now", "Bookmarked", "Recovered mistakes")
    ):
        col.metric(label, len(queues[label]))
    st.caption(
        "Current status across installed lectures. Queues overlap: a missed question can also be due and bookmarked."
    )
    with st.container(border=True, key="review_filters"):
        filters = content_filters("review")
        a, b = st.columns(2)
        with a:
            filters["difficulty"] = select_choice(
                "Difficulty",
                ["Any difficulty", "Beginner", "Intermediate", "Advanced"],
                "review_level",
            )
        with b:
            filters["search"] = st.text_input(
                "Search questions",
                key="review_search",
                placeholder="A concept, question ID, or keyword…",
            )
    content = [q for q in Q_LOOKUP.values() if analytics.content_matches(q, **filters)]
    content_ids = {q["id"] for q in content}
    queue_tab, history_tab, forecast_tab = st.tabs(
        ["Practice queue", "Mistake history", "Review forecast"],
        key="review_tabs",
        on_change="rerun",
    )
    with queue_tab:
        a, b = st.columns(2)
        with a:
            queue = select_choice("Revision queue", list(analytics.QUEUE_HELP), "review_queue")
        with b:
            order = select_choice(
                "Priority",
                ["Most mistakes first", "Oldest review first", "Topic A–Z"],
                "review_order",
            )
        st.caption(analytics.QUEUE_HELP[queue])
        items = analytics.sort_review(
            [q for q in content if q["id"] in queues[queue]], mastery, order
        )
        mcqs = [q for q in items if q["type"] == "mcq"]
        codes = [q for q in items if q["type"] == "coding"]
        st.markdown(
            f'<div class="lead-strip"><div><strong>{len(items)} questions in your focus queue</strong><br><span>{len(mcqs)} MCQs · {len(codes)} coding challenges · sorted by {esc(order.lower())}</span></div>{chip(queue, "chip-amber")}</div>',
            unsafe_allow_html=True,
        )
        if mcqs:
            a, b = st.columns([1, 2], vertical_alignment="bottom")
            with a:
                size_key = "review_batch_size"
                if size_key in st.session_state:
                    st.session_state[size_key] = min(max(1, st.session_state[size_key]), len(mcqs))
                size = st.number_input(
                    "Questions to retry",
                    min_value=1,
                    max_value=len(mcqs),
                    value=min(10, len(mcqs)),
                    step=1,
                    key=size_key,
                )
            with b:
                if st.button("Start focused revision", type="primary", key="review_start_batch"):
                    start_session(
                        profile, mcqs[: int(size)], "All", int(size), {"queue": queue, **filters}
                    )
            st.caption(
                "Uses the highest-priority matching MCQs. Coding challenges open separately from the spotlight below."
            )
        if items:
            ids = [q["id"] for q in items]
            selected = select_choice(
                "Question to inspect",
                ids,
                "review_inspect",
                format_func=lambda k: (
                    f"{Q_LOOKUP[k]['id']} · {Q_LOOKUP[k].get('title', Q_LOOKUP[k]['prompt'])[:110]}"
                ),
            )
            index = ids.index(selected)
            with st.container(key="question_actions_review"):
                left, middle, right = st.columns([1, 2, 1], vertical_alignment="center")
                with left:
                    st.button(
                        "Previous item",
                        disabled=index == 0,
                        key="review_prev",
                        on_click=set_review_item,
                        args=(ids[max(0, index - 1)],),
                    )
                with middle:
                    st.caption(f"Inspecting {index + 1} of {len(ids)} matching questions")
                with right:
                    st.button(
                        "Next item",
                        disabled=index + 1 == len(ids),
                        key="review_next",
                        on_click=set_review_item,
                        args=(ids[min(len(ids) - 1, index + 1)],),
                    )
            review_inspector(profile, Q_LOOKUP[selected], records, mastery)
            with st.expander("Queue summary · compare all matching questions"):
                rich_table(
                    [
                        {
                            "Question": q.get("title", q["prompt"])[:130],
                            "Topic": q["topic_name"],
                            "Mistakes": mastery.get(q["id"], {}).get("total_wrong", 0),
                            "Correct streak": mastery.get(q["id"], {}).get("streak", 0),
                            "Due (IST)": as_ist(mastery.get(q["id"], {}).get("next_due")),
                        }
                        for q in items[:100]
                    ]
                )
                if len(items) > 100:
                    st.caption(
                        "Table shows the first 100. The inspector and practice queue include every match."
                    )
        else:
            st.info(
                "No questions in this queue match your filters. Try another queue, clear your search, or practice new questions."
            )
            if st.button("Explore the quiz arena", key="review_explore"):
                go_to("quiz")
    with history_tab:
        wrong = [r for r in records if not r["correct"] and r["question_id"] in content_ids]
        section(
            "Every mistake has a story",
            "This history keeps incorrect attempts even after you recover. Content filters apply; the practice-queue selector does not.",
        )
        if wrong:
            wrong_ids = list(dict.fromkeys(r["question_id"] for r in wrong))
            st.caption(
                f"{len(wrong)} incorrect attempts across {len(wrong_ids)} questions. Coding results are self-assessed."
            )
            selected_history = select_choice(
                "Revisit a past mistake",
                wrong_ids,
                "review_history_item",
                format_func=lambda k: (
                    f"{k} · {Q_LOOKUP[k].get('title', Q_LOOKUP[k]['prompt'])[:100]}"
                ),
            )
            if st.button("Inspect this mistake", key="review_history_open"):
                st.session_state["review_pending"] = selected_history
                st.rerun()
            rich_table(
                [
                    {
                        "When (IST)": as_ist(r["created_at"]),
                        "Question": r["question_id"],
                        "Topic": Q_LOOKUP[r["question_id"]]["topic_name"],
                        "Current status": "Recovered"
                        if mastery.get(r["question_id"], {}).get("last_correct")
                        else "Needs practice",
                    }
                    for r in wrong[:50]
                ]
            )
            st.caption("Latest 50 attempts shown; the download includes every matching mistake.")
            st.download_button(
                "Export matching mistakes (CSV)",
                attempts_export_ist(profile, wrong),
                file_name="revision_mistakes.csv",
                mime="text/csv",
                key="review_export",
            )
        else:
            st.info(
                "No incorrect attempts match these filters. Your mistake history will appear here as you practice."
            )
    with forecast_tab:
        draw_chart(
            analytics.review_forecast(mastery, content_ids, current),
            "forecast",
            "Your next seven days",
            "Due now includes overdue items. Future reviews use IST. Wrong answers become due immediately.",
            "review_forecast",
        )
        st.caption(
            "The forecast respects content filters. It is a snapshot of the current schedule, which changes as you answer."
        )
        if st.button("Focus on questions due now", key="review_due_focus"):
            # Apply on the next rerun, before the queue widget is instantiated.
            st.session_state["review_pending_queue"] = "Due now"
            st.rerun()


def progress_page(profile: str) -> None:
    hero(
        "Your learning / In perspective",
        "See your progress take shape.",
        "Explore your practice rhythm, spot patterns, and turn your next session into a step forward.",
    )
    current = datetime.now(UTC)
    today = current.astimezone(analytics.IST).date()
    all_records = core.attempt_history(profile, None)
    mastery = core.mastery_map(profile)
    with st.container(border=True, key="progress_filters"):
        filters = content_filters("progress")
        period = select_choice("Time range", list(analytics.PERIODS), "progress_period")
    records = analytics.filtered_attempts(
        all_records, Q_LOOKUP, today=today, period=period, **filters
    )
    summary = analytics.activity_summary(records, today)
    a, b, c, d = st.columns(4)
    a.metric("Attempts in range", summary["attempts"])
    b.metric("Accuracy", f"{summary['accuracy']:g}%" if records else "—")
    c.metric("Questions practiced", summary["studied"])
    d.metric("Active days", summary["active_days"])
    st.caption(
        f"{period} · {filters['kind']} · IST dates. MCQs are graded automatically; coding attempts use your self-assessment."
    )
    missing = sum(r["question_id"] not in Q_LOOKUP for r in all_records)
    if missing:
        st.caption(
            f"{missing} attempts reference unavailable lectures and are excluded from charts. Full exports retain them."
        )
    if not records:
        st.info(
            "No practice matches these filters yet. Broaden the time range or start a session to build your dashboard."
        )
    content = [q for q in Q_LOOKUP.values() if analytics.content_matches(q, **filters)]
    content_ids = {q["id"] for q in content}
    known = content_ids & set(mastery)
    mastered = sum(mastery[qid]["streak"] >= 3 for qid in known)
    queues = analytics.review_queues(mastery, core.bookmarked_ids(profile), content_ids, current)
    overview, topics_tab, history = st.tabs(
        ["Learning pulse", "Topics & difficulty", "History & exports"],
        key="progress_tabs",
        on_change="rerun",
    )
    with overview:
        with st.container(border=True, key="practice_goal"):
            a, b = st.columns([2, 1], vertical_alignment="center")
            with a:
                st.markdown(
                    f'<div class="eyebrow">TODAY’S MOMENTUM</div><h3 class="chart-title">{summary["today"]} attempts today · {summary["streak"]}-day streak</h3>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"Best streak in the selected range: {summary['best_streak']} days. A streak stays active through yesterday."
                )
            with b:
                goal = st.number_input(
                    "Daily attempt target",
                    min_value=1,
                    max_value=500,
                    value=st.session_state.get("daily_target_" + profile, 10),
                    step=1,
                    key="daily_goal_" + profile,
                    on_change=remember_daily_goal,
                    args=(profile,),
                )
            st.progress(
                min(1.0, summary["today"] / goal),
                text=f"{min(summary['today'], goal)}/{goal} toward today's target",
            )
            st.caption(
                "Target is remembered for this browser session. Counts respect the selected content filters."
            )
        days = analytics.activity_window(records, today, period)
        activity = analytics.daily_activity(records, today, days)
        left, right = st.columns([1.7, 1])
        with left:
            draw_chart(
                activity,
                "activity",
                "Activity meets accuracy",
                "Blue bars: daily attempts. Gold line: accuracy on days practiced. Hover for details.",
                "progress_activity",
            )
        with right:
            if records:
                draw_chart(
                    [
                        {"Result": "Correct / solved", "Attempts": summary["correct"]},
                        {
                            "Result": "Incorrect / practice",
                            "Attempts": len(records) - summary["correct"],
                        },
                    ],
                    "outcomes",
                    "Every attempt counts",
                    "Results within your selected filters.",
                    "progress_outcomes",
                )
            else:
                st.info("Your results breakdown appears after your first attempt.")
        st.caption(
            "The activity graph shows up to 90 days and adapts to shorter histories. Summary metrics and exports cover the full selected range."
        )
        draw_chart(
            analytics.daily_activity(records, today, min(analytics.PERIODS[period] or 84, 84)),
            "calendar",
            "Your practice calendar",
            "Each square is an IST day. Stronger colour means more attempts. Hover to explore.",
            "progress_calendar",
        )
        with st.container(border=True, key="mastery_snapshot"):
            section(
                "Your library, in motion",
                "Current status for the selected content, independent of the time range. Mastered means a streak of at least three correct attempts.",
            )
            a, b, c = st.columns(3)
            a.metric("Mastered", mastered)
            b.metric("Still building", len(known) - mastered)
            c.metric("Not started", len(content) - len(known))
            st.progress(
                len(known) / len(content) if content else 0,
                text=f"{len(known)} of {len(content)} questions explored",
            )
            if st.button(
                f"Open revision studio · {len(queues['Needs another try'])} need another try",
                key="progress_review_link",
            ):
                st.session_state["review_kind"] = filters["kind"]
                st.session_state["review_pack"] = filters["pack"]
                st.session_state["review_topic"] = filters["topic"]
                st.session_state["review_queue"] = "Needs another try"
                st.session_state["review_level"] = "Any difficulty"
                st.session_state["review_search"] = ""
                go_to("review")
    with topics_tab:
        topics = analytics.performance_rows(records, Q_LOOKUP)
        if topics:
            event = draw_chart(
                topics,
                "topics",
                "Where your practice is going",
                "Sorted by accuracy, lowest first. Click a bar to explore that topic below; double-click to clear the selection.",
                "progress_topics",
                selectable=True,
            )
            topic_map = {r["Key"]: r for r in topics}
            selection = (
                event.get("selection", {}).get("topic_pick", []) if isinstance(event, dict) else []
            )
            picked = selection[0].get("Key") if selection else None
            if picked in topic_map and picked != st.session_state.get("last_chart_topic"):
                st.session_state["progress_spotlight"] = picked
            st.session_state["last_chart_topic"] = picked
            spotlight = select_choice(
                "Topic spotlight",
                list(topic_map),
                "progress_spotlight",
                format_func=lambda k: f"{topic_map[k]['Topic']} · {topic_map[k]['Lecture']}",
            )
            row = topic_map[spotlight]
            with st.container(border=True, key="topic_spotlight"):
                section(
                    row["Topic"],
                    f"{row['Attempts']} attempts · {row['Accuracy']:g}% accuracy · {row['Wrong']} incorrect / needs-practice results",
                )
                if row["Attempts"] < 5:
                    st.caption(
                        "A small sample: practice more before treating this accuracy as a reliable strength or weakness."
                    )
                candidates = [q for q in content if f"{q['pack_id']}:{q['topic']}" == spotlight]
                mcqs = [q for q in candidates if q["type"] == "mcq"]
                if mcqs and st.button(
                    "Practice this topic", type="primary", key="progress_topic_practice"
                ):
                    start_session(
                        profile,
                        mcqs,
                        "Smart Mix",
                        min(10, len(mcqs)),
                        {"topic": row["Topic"], "source": "Progress spotlight"},
                    )
                codes = [q for q in candidates if q["type"] == "coding"]
                if codes and st.button("Open a coding challenge", key="progress_topic_code"):
                    open_coding_question(codes[0]["id"])
            draw_chart(
                analytics.performance_rows(records, Q_LOOKUP, "difficulty"),
                "difficulty",
                "Challenge yourself at every level",
                "Hover to compare accuracy and sample size by difficulty. Includes only attempted levels.",
                "progress_difficulty",
            )
            with st.expander("Detailed topic data"):
                rich_table(
                    [
                        {
                            k: r[k]
                            for k in (
                                "Topic",
                                "Lecture",
                                "Attempts",
                                "Correct",
                                "Wrong",
                                "Accuracy",
                            )
                        }
                        for r in topics
                    ]
                )
        else:
            st.info("Topic and difficulty charts appear after practice matches your filters.")
    with history:
        section(
            "Your attempt journal",
            "The latest 100 attempts matching the dashboard filters. Download the full filtered set below.",
        )
        rich_table(
            [
                {
                    "When (IST)": as_ist(r["created_at"]),
                    "Question": r["question_id"],
                    "Topic": Q_LOOKUP[r["question_id"]]["topic_name"],
                    "Type": "MCQ" if r["kind"] == "mcq" else "Coding · self-assessed",
                    "Result": "Correct / solved" if r["correct"] else "Incorrect / practice",
                }
                for r in records[:100]
            ]
        )
        st.download_button(
            "Export filtered attempts (CSV)",
            attempts_export_ist(profile, records),
            file_name="python_filtered_attempts.csv",
            mime="text/csv",
            key="progress_filtered_export",
            disabled=not records,
        )
        sessions = core.recent_sessions(profile, limit=30)
        section(
            "Pick up a saved session",
            "The latest 30 profile sessions, independent of chart filters.",
        )
        if sessions:
            unfinished = [s for s in sessions if not s["completed_at"]]
            if unfinished:
                session_map = {s["id"]: s for s in unfinished}
                sid = select_choice(
                    "Saved quiz",
                    list(session_map),
                    "progress_resume_picker",
                    format_func=lambda k: (
                        f"{as_ist(session_map[k]['created_at'])} · Question {session_map[k]['position'] + 1} of {len(session_map[k]['queue'])}"
                    ),
                )
                if st.button("Resume this quiz", key="progress_resume"):
                    st.session_state["active_session_id"] = sid
                    go_to("quiz")
            rich_table(
                [
                    {
                        "Saved at (IST)": as_ist(s["created_at"]),
                        "Mode": s["configuration"].get("mode", "All"),
                        "Position": f"{min(s['position'] + 1, len(s['queue']))}/{len(s['queue'])}",
                        "Status": "Finished" if s["completed_at"] else "In progress",
                    }
                    for s in sessions
                ]
            )
        else:
            st.caption("No saved sessions yet.")
        progress_backups(profile)


def progress_backups(profile: str) -> None:
    section(
        "Export & backup", "These full-profile exports are independent of the dashboard filters."
    )
    with st.container(key="export_actions"):
        left, right = st.columns(2, gap="small")
        with left:
            st.download_button(
                "Export all attempts (CSV)",
                data=attempts_export_ist(profile),
                file_name="python_all_attempts.csv",
                mime="text/csv",
                use_container_width=False,
            )
        with right:
            if cloud.is_cloud():
                st.download_button(
                    "Download full progress backup (ZIP)",
                    data=core.export_all_progress(profile),
                    file_name=f"python_mastery_{profile}_backup.zip",
                    mime="application/zip",
                    use_container_width=False,
                )
            elif core.DEFAULT_DB.exists():
                st.download_button(
                    "Download progress database",
                    data=consistent_db_backup(),
                    file_name="python_mastery_progress.sqlite3",
                    mime="application/octet-stream",
                    use_container_width=False,
                )
    st.caption(
        "Cloud backups include your profile and imported lecture packs."
        if cloud.is_cloud()
        else "The SQLite database backup includes all learner profiles on this computer."
    )


def packs_page(profile: str) -> None:
    hero(
        "Library / Expand your knowledge",
        "Your lecture library",
        "All lecture packs in one learning workspace. Add new topics without resetting your progress.",
    )
    if not PACKS:
        st.info("Your library is empty. Import a JSON lecture pack below to begin practicing.")
    for pack in PACKS.values():
        with st.container(border=True, key="pack_" + pack["pack_id"]):
            st.markdown(f"### {pack['title']}")
            st.caption(pack.get("description", ""))
            a, b, c = st.columns(3)
            a.metric("Multiple-choice", len(pack.get("questions", [])))
            b.metric("Coding tasks", len(pack.get("challenges", [])))
            c.metric("Topics", len(pack["topics"]))
            st.markdown(
                "".join(
                    f'<span class="topic-pill">{esc(t["name"])}</span>' for t in pack["topics"]
                ),
                unsafe_allow_html=True,
            )
    section(
        "Import your next lecture",
        "The app accepts validated JSON question packs, not raw PDFs. Send your PDF to create a compatible pack first.",
    )
    uploaded = st.file_uploader("Select a JSON question pack", type=["json"])
    if uploaded is not None:
        if st.button("Validate & import lecture", type="primary"):
            try:
                dest = core.import_pack(uploaded.getvalue())
                st.success(f"Imported {dest}. Your earlier progress remains intact.")
                st.rerun()
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                st.error(str(exc))
    with st.expander("See the pack format and question ID rules"):
        st.code(
            """{
  "schema_version": 1,
  "pack_id": "lecture-2",
  "title": "Python Basics — Lecture 2",
  "topics": [{"id": "loops", "name": "Loops", "first_page": 1}],
  "questions": [{
    "id": "L2-M001", "type": "mcq", "topic": "loops",
    "difficulty": "Beginner", "source": "notes", "pages": [1],
    "prompt": "Which keyword starts a for loop?", "code": "",
    "options": ["for", "loop", "repeat", "iterate"], "answer": 0,
    "explanation": "Python uses for to begin iteration."
  }],
  "challenges": []
}""",
            language="json",
        )
        st.caption("Use a different pack_id and globally unique question IDs for every lecture.")


def site_header(profile: str | None) -> None:
    """Sidebar-free, consistently sized top navigation and theme button.

    Buttons are native Streamlit controls; all navigation works without custom JS.
    The active section and appearance survive reruns and browser refreshes via URL.
    """
    with st.container(key="site_header"):
        brand_col, theme_col, account_col = st.columns(
            [5.5, 0.55, 1.9], gap="small", vertical_alignment="center"
        )
        with brand_col:
            st.markdown(
                '<div class="site-brand">'
                f'<span class="site-brand-icon">{python_mark(38)}</span>'
                '<span class="site-brand-text"><b>Python Mastery Lab</b>'
                "<small>YOUR PYTHON WORKSPACE</small></span></div>",
                unsafe_allow_html=True,
            )
        with theme_col:
            next_theme = "light" if st.session_state["dark_mode"] else "dark"
            if st.button(
                f"Switch to {next_theme} mode",
                key="theme_circle",
                use_container_width=False,
                help=f"Switch to {next_theme} appearance",
            ):
                st.session_state["dark_mode"] = not st.session_state["dark_mode"]
                persist_theme()
                st.rerun()

        with account_col:
            if profile is not None:
                with st.popover(
                    f"{profile[:21]}",
                    use_container_width=True,
                    help="Account and sign-out options",
                ):
                    st.markdown(
                        f'<div class="account-popover-title">Signed in as <b>{esc(profile)}</b></div>',
                        unsafe_allow_html=True,
                    )
                    if cloud.is_cloud():
                        if st.button("Sign out", key="header_signout", use_container_width=False):
                            current_theme = st.session_state.get("dark_mode", False)
                            for k in list(st.session_state.keys()):
                                del st.session_state[k]
                            st.session_state["dark_mode"] = current_theme
                            st.rerun()
                    else:
                        st.text_input(
                            "Learner profile",
                            key="offline_profile",
                            max_chars=60,
                            help="Local SQLite learner name. Add DATABASE_URL for secure cloud accounts.",
                        )
                        st.caption("Offline SQLite storage")
            else:
                st.markdown(
                    '<span class="visitor-note">Personal workspace</span>', unsafe_allow_html=True
                )

        if profile is not None:
            with st.container(key="top_navigation"):
                nav_columns = st.columns(len(PAGES), gap="small")
                for col, (page_id, title) in zip(nav_columns, PAGES):
                    with col:
                        if st.button(
                            title,
                            key="top_nav_" + page_id,
                            type="primary"
                            if page_id == st.session_state["current_page"]
                            else "secondary",
                            use_container_width=False,
                        ):
                            go_to(page_id)


def selected_page() -> str:
    valid = {page for page, _ in PAGES}
    if "current_page" not in st.session_state:
        requested = str(st.query_params.get("page", "home"))
        st.session_state["current_page"] = requested if requested in valid else "home"
    if st.session_state["current_page"] not in valid:
        st.session_state["current_page"] = "home"
    return st.session_state["current_page"]


if cloud.is_cloud():
    cloud_login()
    profile = st.session_state["cloud_username"]
else:
    if "offline_profile" not in st.session_state:
        st.session_state["offline_profile"] = "My Python practice"
    profile = st.session_state["offline_profile"].strip() or "My Python practice"

page = selected_page()
if st.session_state.get("workspace_profile", profile) != profile:
    st.session_state.pop("active_session_id", None)
st.session_state["workspace_profile"] = profile
site_header(profile)
if page == "home":
    overview_page(profile)
elif page == "quiz":
    quiz_page(profile)
elif page == "coding":
    coding_page(profile)
elif page == "review":
    review_page(profile)
elif page == "progress":
    progress_page(profile)
else:
    packs_page(profile)
