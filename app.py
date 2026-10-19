"""Python Mastery Lab — polished, responsive Streamlit experience.

Run: python -m streamlit run app.py
Database, question IDs and pack schema are unchanged from the original app.
"""
from __future__ import annotations

import html
import json
import csv
import io
import sqlite3
import tempfile
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict
from pathlib import Path

import streamlit as st
import quiz_core as core
from ui_style import svg_icon, style

st.set_page_config(
    page_title="Python Mastery Lab · Study Workspace",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Your local, persistent Python practice workspace."},
)
core.init_db()
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
    ("quiz", "Quiz arena"),
    ("coding", "Coding dojo"),
    ("review", "Review lab"),
    ("progress", "My progress"),
    ("packs", "Lecture library"),
]

# Store the appearance in the URL as well as Streamlit session state.
# This keeps it consistent after a browser refresh, without altering question progress.
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = str(st.query_params.get("theme", "light")).lower() == "dark"


def persist_theme() -> None:
    st.query_params["theme"] = "dark" if st.session_state["dark_mode"] else "light"


st.markdown(style("dark" if st.session_state["dark_mode"] else "light"), unsafe_allow_html=True)


IST = ZoneInfo("Asia/Kolkata")


def as_ist(value: str | None, *, date_only: bool = False) -> str:
    """Convert UTC/offset-aware old stored times for display, never for DB comparisons."""
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:  # Older database rows used UTC without an offset.
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime("%d %b %Y" if date_only else "%d %b %Y, %I:%M %p IST")
    except (ValueError, TypeError, OverflowError):
        return "Unknown time"


def rich_table(rows: list[dict], fields: list[str] | None = None, code_fields: tuple[str, ...] = ()) -> None:
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
    st.markdown(f'<div class="table-scroll" role="region" aria-label="Study data" tabindex="0"><table class="ui-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>', unsafe_allow_html=True)


def consistent_db_backup() -> bytes:
    """Take an SQLite online backup, safe even if Streamlit is writing in WAL mode."""
    source = core.DEFAULT_DB
    if not source.exists():
        return b""
    with tempfile.TemporaryDirectory() as tmpdir:
        copy = Path(tmpdir) / "progress.sqlite3"
        with sqlite3.connect(str(source)) as source_db:
            with sqlite3.connect(str(copy)) as backup_db:
                source_db.backup(backup_db)
        return copy.read_bytes()


def attempts_export_ist(profile: str) -> bytes:
    """Keep original UTC column for exact ordering, add a human-friendly IST column."""
    rows = core.attempt_history(profile, 100000)
    out = io.StringIO()
    names = ["saved_at_ist", "created_at", "question_id", "kind", "answer_index", "correct", "response_text", "session_id"]
    writer = csv.DictWriter(out, fieldnames=names)
    writer.writeheader()
    for row in rows:
        writer.writerow({**{k: row.get(k) for k in names}, "saved_at_ist": as_ist(row.get("created_at"))})
    return out.getvalue().encode("utf-8-sig")



def esc(value) -> str:
    return html.escape(str(value), quote=True)


def chip(text: str, kind: str = "") -> str:
    return f'<span class="num-chip {kind}">{esc(text)}</span>'


def hero(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{esc(eyebrow)}</div>'
        f'<h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def section(title: str, caption: str = "") -> None:
    st.markdown(f'<div class="section-title">{esc(title)}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-sub">{esc(caption)}</div>', unsafe_allow_html=True)


def go_to(page: str) -> None:
    st.session_state["current_page"] = page
    st.query_params["page"] = page
    st.rerun()


def start_session(profile: str, qs: list[dict], mode: str, size: int, filters: dict | None = None) -> bool:
    ids = core.select_questions(qs, profile, min(size, len(qs)), mode)
    if not ids:
        st.warning(f"No questions are available for '{mode}' in this selection. Try All or Smart Mix.")
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
        chip(q["difficulty"], "chip-teal" if q["difficulty"] == "Beginner" else "chip-amber" if q["difficulty"] == "Advanced" else "")
        + chip(q["topic_name"], "chip-muted")
        + chip(source + (f" · p. {page}" if page else ""), "chip-muted"),
        unsafe_allow_html=True,
    )


def bookmark_control(profile: str, q: dict) -> None:
    marked = q["id"] in core.bookmarked_ids(profile)
    if st.button("Bookmarked" if marked else "Bookmark", key="mark_" + q["id"], use_container_width=True,
                 help="Keep this question in your Bookmarked review queue"):
        core.bookmark(profile, q["id"], not marked)
        st.rerun()


def personal_note(profile: str, q: dict) -> None:
    with st.expander("Personal revision note"):
        field_key = "note_" + q["id"]
        if field_key not in st.session_state:
            st.session_state[field_key] = core.get_note(profile, q["id"])
        st.text_area("Explain the idea in your own words", key=field_key, height=118,
                     placeholder="What makes this question tricky? How will you recognize it next time?")
        if st.button("Save note", key="save_note_" + q["id"]):
            core.save_note(profile, q["id"], st.session_state[field_key])
            st.toast("Revision note saved", icon="✅")


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
        hero("Session finished · Saved to your history", "Nice work — session complete!", "Your attempts, explanations and revision schedule are saved on this computer.")
        x, y, z = st.columns(3)
        x.metric("Questions answered", f"{answered}/{len(queue)}")
        y.metric("Correct responses", right)
        z.metric("Accuracy", f"{right / answered:.0%}" if answered else "—")
        missed = [Q_LOOKUP[qid] for qid, ans in zip(queue, answers) if ans and not ans["correct"] and qid in Q_LOOKUP]
        if missed:
            section("Worth revisiting", "These questions stay in your learning history.")
            for q in missed[:12]:
                st.markdown(f'<div class="review-item"><b>{esc(q["prompt"])}</b><p>{esc(q["topic_name"])} · {esc(q["id"])}</p></div>', unsafe_allow_html=True)
        first, second = st.columns(2)
        with first:
            if st.button("Back to overview", type="primary", use_container_width=True):
                st.session_state.pop("active_session_id", None)
                go_to("home")
        with second:
            if st.button("Browse answered questions", use_container_width=True):
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
            f'<div class="question-topline">{esc(q["topic_name"])} · All answers saved locally</div>',
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("Save & leave", key="leave_session", use_container_width=True):
            st.session_state.pop("active_session_id", None)
            go_to("quiz")
    st.progress(index / len(queue))
    left, right = st.columns([3, 1.25], vertical_alignment="bottom")
    with left:
        st.markdown(f'<div class="question-heading">{esc(q["prompt"])}</div>', unsafe_allow_html=True)
    with right:
        bookmark_control(profile, q)
    item_meta(q)
    st.caption(f"Question ID: {q['id']}")
    if q.get("code"):
        st.code(q["code"], language="python")

    if previous is None:
        with st.form(f"answer_form_{sid}_{q['id']}", clear_on_submit=False):
            st.markdown("**Choose one answer**")
            choice = st.radio(
                "Answer options", range(4), index=None,
                format_func=lambda j: f'{"ABCD"[j]}.  {q["options"][j]}',
                key=f"choice_{sid}_{q['id']}", label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Check my answer", type="primary", use_container_width=True)
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
            suffix = " · Correct answer" if i == correct else " · Your selection" if i == selected else ""
            st.markdown(
                f'<div class="option-card {cls}"><span class="option-letter">{"ABCD"[i]}</span>'
                f'<span>{esc(option)}<strong>{esc(suffix)}</strong></span></div>',
                unsafe_allow_html=True,
            )
        successful = bool(previous["correct"])
        title = "Correct — keep building momentum" if successful else "Let's learn from this one"
        st.markdown(
            f'<div class="feedback {"" if successful else "feedback-bad"}">'
            f'<strong>{esc(title)}</strong>'
            f'<p>{esc("This question is scheduled for spaced revision." if successful else "Saved to your mistake history and due-review queue.")}</p>'
            f'<p><b>Why:</b> {esc(q["explanation"])}</p></div>',
            unsafe_allow_html=True,
        )
        if q.get("tags"):
            st.caption("Related concepts: " + ", ".join(q["tags"]))
    personal_note(profile, q)
    st.divider()
    back, next_btn = st.columns([1, 2])
    with back:
        if st.button("Previous", disabled=index == 0, use_container_width=True):
            core.change_position(profile, sid, index - 1)
            st.rerun()
    with next_btn:
        label = "Finish session" if index + 1 == len(queue) else "Next question"
        if st.button(label, type="primary", disabled=previous is None, use_container_width=True):
            core.change_position(profile, sid, index + 1)
            st.rerun()


def quiz_page(profile: str) -> None:
    active = st.session_state.get("active_session_id")
    if active and core.get_session(profile, active):
        quiz_session(profile, active)
        return
    hero("MCQ / Learn · Test · Repeat", "Build your next practice session", "Focused questions, immediate explanations, and revision queues that remember every mistake.")
    sessions = core.recent_sessions(profile, limit=40, unfinished=True)
    if sessions:
        section("Pick up where you left off", "Your earlier attempts and selected questions are intact.")
        # A saved session with an already-completed position is not displayed here.
        choices = {s["id"]: f'{as_ist(s["created_at"])}  ·  {s["position"]}/{len(s["queue"])} questions  ·  {s["configuration"].get("mode", "Practice")}' for s in sessions}
        a, b = st.columns([3, 1], vertical_alignment="bottom")
        with a:
            selected_sid = st.selectbox("Unfinished sessions", list(choices), format_func=lambda k: choices[k], label_visibility="collapsed")
        with b:
            if st.button("Resume session", type="primary", use_container_width=True):
                st.session_state["active_session_id"] = selected_sid
                st.rerun()

    section("Create a new quiz", "Choose your practice mode, then refine the questions if you want to focus on a specific concept.")
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
        base = ALL_MCQ if name == "All lectures" else [q for q in ALL_MCQ if q["pack_id"] == packs[name]]
        with b:
            topic_name = st.selectbox("Topic", ["All topics"] + sorted({q["topic_name"] for q in base}), key="quiz_topic")
        if topic_name != "All topics":
            base = [q for q in base if q["topic_name"] == topic_name]
        a2, b2 = st.columns(2)
        with a2:
            levels = st.multiselect("Difficulty", ["Beginner", "Intermediate", "Advanced"],
                                    default=["Beginner", "Intermediate", "Advanced"], key="quiz_levels")
        with b2:
            source = st.selectbox("Source", ["Lecture + tricky extensions", "Lecture PDF only", "Tricky extensions only"], key="quiz_source")
        base = [q for q in base if q["difficulty"] in levels]
        if source == "Lecture PDF only":
            base = [q for q in base if q["source"] == "notes"]
        elif source == "Tricky extensions only":
            base = [q for q in base if q["source"] == "extension"]

    mastered = core.mastery_map(profile)
    marks = core.bookmarked_ids(profile)
    due_now = core.now()
    pool = [q for q in base if (
        mode in ("All", "Smart Mix") or
        (mode == "Unseen" and q["id"] not in mastered) or
        (mode == "Missed" and q["id"] in mastered and not mastered[q["id"]]["last_correct"]) or
        (mode == "Due" and q["id"] in mastered and mastered[q["id"]]["next_due"] <= due_now) or
        (mode == "Bookmarked" and q["id"] in marks)
    )]
    left, right = st.columns([2, 1], vertical_alignment="bottom")
    with left:
        st.markdown(
            f'<div class="lead-strip"><div><strong>{len(pool)} questions ready for {esc(mode.lower())}</strong><br>'
            f'<span>{len(base)} questions match the lecture and topic filters</span></div>'
            f'{chip("Saved automatically", "chip-teal")}</div>', unsafe_allow_html=True,
        )
    with right:
        count = st.number_input("Questions per session", min_value=1, max_value=max(1, len(pool)),
                                value=min(15, max(1, len(pool))), step=1)
    if st.button("Start practicing", type="primary", use_container_width=True, disabled=not pool):
        start_session(profile, base, mode, int(count), {"topic": topic_name, "source": source})
    if not pool:
        st.info("Nothing matches this mode yet. Try Smart Mix, All, or broaden your filters.")


def overview_page(profile: str) -> None:
    hero("Your personal study workspace", "Master Python, one question at a time.",
         "From the lecture basics to tricky interview questions. Explore, practice, track progress, and turn mistakes into strengths.")
    met = core.profile_metrics(profile)
    a, b, c, d = st.columns(4)
    a.metric("Questions available", len(ALL_MCQ))
    b.metric("Coding challenges", len(ALL_CODE))
    c.metric("Your accuracy", f'{met["accuracy"]}%')
    d.metric("Need revision", met["missed"])

    sessions = core.recent_sessions(profile, limit=10, unfinished=True)
    if sessions:
        most_recent = sessions[0]
        st.markdown(
            f'<div class="lead-strip"><div><strong>Continue your learning streak</strong><br>'
            f'<span>Saved session · question {most_recent["position"] + 1} of {len(most_recent["queue"])}</span></div>'
            f'{chip(most_recent["configuration"].get("mode", "Practice"), "chip-teal")}</div>',
            unsafe_allow_html=True,
        )
        if st.button("Continue saved session", type="primary", use_container_width=True):
            st.session_state["active_session_id"] = most_recent["id"]
            go_to("quiz")

    section("What would you like to do?", "Everything you need for deliberate Python practice, in one place.")
    cards = [
        ("quiz", "Practice questions", "Mix all topics or drill a single concept, from beginner to interview-level traps.", "Open quiz arena", "quiz"),
        ("coding", "Solve coding tasks", "Work in VS Code, compare examples and save drafts for your next session.", "Open coding dojo", "coding"),
        ("review", "Review mistakes", "Revisit missed, due, and bookmarked questions with full explanations.", "Open revision lab", "review"),
    ]
    cols = st.columns(3)
    for col, (icon, title, descr, button, page) in zip(cols, cards):
        with col:
            with st.container(border=True, key="feature_" + page):
                st.markdown(f'<div class="feature-icon">{svg_icon(icon, 24)}</div><div class="feature-title">{esc(title)}</div>'
                            f'<div class="feature-description">{esc(descr)}</div>', unsafe_allow_html=True)
                if st.button(button, key="card_" + page, use_container_width=True):
                    go_to(page)

    section("Instant practice", "One click to train your recall or revisit an earlier mistake.")
    left, right = st.columns(2)
    with left:
        if st.button("Start a 15-question Smart Mix", type="primary", use_container_width=True, disabled=not ALL_MCQ):
            start_session(profile, ALL_MCQ, "Smart Mix", 15)
    with right:
        missed = {qid for qid, x in core.mastery_map(profile).items() if not x["last_correct"]}
        candidates = [q for q in ALL_MCQ if q["id"] in missed]
        if st.button("Practice previous mistakes", use_container_width=True, disabled=not candidates):
            start_session(profile, candidates, "All", 15)

    section("Your lecture shelf", "Click a lecture to see the concepts inside it.")
    for pack in PACKS.values():
        with st.expander(f'{pack["title"]}   ·   {len(pack.get("questions", []))} MCQs   ·   {len(pack.get("challenges", []))} coding tasks'):
            counts = Counter(q["topic"] for q in pack.get("questions", []))
            pills = "".join(f'<span class="topic-pill">{esc(t["name"])} · {counts[t["id"]]}</span>' for t in pack["topics"])
            st.markdown(pills, unsafe_allow_html=True)
            st.caption("Questions tagged ‘PDF material’ come from the lecture. ‘Advanced extension’ adds related tricks.")


def coding_page(profile: str) -> None:
    hero("Hands-on / VS Code companion", "Coding dojo", "Solve real programming problems in VS Code, save working drafts, and check your solution when you're ready.")
    if not ALL_CODE:
        st.info("No coding challenges are installed yet.")
        return
    a, b, c = st.columns(3)
    with a:
        pack_filter = st.selectbox("Lecture", ["All lectures"] + [p["title"] for p in PACKS.values()], key="code_pack")
    with b:
        level_filter = st.selectbox("Difficulty", ["Any difficulty", "Beginner", "Intermediate", "Advanced"], key="code_level")
    with c:
        status = st.selectbox("Progress", ["All tasks", "Unseen", "Needs practice", "Previously solved"], key="code_status")
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
    titles = {q["id"]: f'{q["title"]}  ·  {q["difficulty"]}' for q in available}
    qid = st.selectbox("Select a challenge", list(titles), format_func=lambda id_: titles[id_], key="challenge_picker")
    q = Q_LOOKUP[qid]
    section(q["title"])
    item_meta(q)
    st.markdown(q["prompt"])
    section("Example test cases", "Run the examples yourself in VS Code; inputs are supplied one line at a time.")
    rich_table([{"Input": x["input"], "Expected output": x["output"]} for x in q["samples"]],
               code_fields=("Input", "Expected output"))
    helper, hint = st.columns(2)
    with helper:
        with st.expander("Starter code"):
            st.code(q["starter"] or "# Write your Python code here", language="python")
    with hint:
        with st.expander("Reveal a hint"):
            st.write(q["hint"])
    section("Your working solution", "Drafts save to your profile; this app never executes code. Run and test it in VS Code first.")
    draft_key = "draft_" + qid
    if draft_key not in st.session_state:
        st.session_state[draft_key] = core.get_draft(profile, qid) or q["starter"]
    st.text_area("Your Python code", key=draft_key, height=260, label_visibility="collapsed",
                 placeholder="# Paste your tested VS Code solution here")
    save_col, reveal_col = st.columns(2)
    with save_col:
        if st.button("Save my draft", use_container_width=True, key="save_draft_" + qid):
            core.save_draft(profile, qid, st.session_state[draft_key])
            st.toast("Draft saved locally", icon="✅")
    with reveal_col:
        if st.button("Reveal reference solution", use_container_width=True, key="reveal_code_" + qid):
            st.session_state["revealed_" + qid] = True
    if st.session_state.get("revealed_" + qid):
        section("Reference solution", "Read and understand it before grading your attempt.")
        st.code(q["solution"], language="python")
        st.info(q["rubric"])
        yes, no = st.columns(2)
        with yes:
            if st.button("Solved independently", type="primary", use_container_width=True, key="grade_yes_" + qid):
                core.grade_code(profile, q, True, st.session_state[draft_key])
                st.toast("Recorded as solved", icon="✅")
        with no:
            if st.button("Need more practice", use_container_width=True, key="grade_no_" + qid):
                core.grade_code(profile, q, False, st.session_state[draft_key])
                st.toast("Added to your practice queue", icon="🔁")
    personal_note(profile, q)


def review_list(profile: str, ids: set[str], title: str) -> None:
    questions = [q for q in ALL_MCQ if q["id"] in ids]
    code = [q for q in ALL_CODE if q["id"] in ids]
    st.markdown(f'<div class="section-sub">{len(questions)} MCQs · {len(code)} coding tasks in this queue</div>', unsafe_allow_html=True)
    if questions:
        for q in questions[:12]:
            st.markdown(
                f'<div class="review-item"><b>{esc(q["prompt"][:220])}</b>'
                f'<p>{esc(q["topic_name"])} · {esc(q["difficulty"])} · {esc(q["id"])}</p></div>', unsafe_allow_html=True,
            )
        if len(questions) > 12:
            st.caption(f"Showing 12 of {len(questions)} questions. The practice session pulls from the full queue.")
        if st.button(f"Start {title.lower()} practice", type="primary", use_container_width=True, key="review_start_" + title):
            start_session(profile, questions, "All", 20, {"queue": title})
    if code:
        with st.expander(f"{len(code)} coding challenges in this queue"):
            for q in code[:18]:
                st.markdown(f'**{q["title"]}**  ·  {q["difficulty"]}')
    if not questions and not code:
        st.markdown('<div class="empty">Your queue is empty. Great time to explore new questions!</div>', unsafe_allow_html=True)


def review_page(profile: str) -> None:
    hero("Learning / Repetition", "Revision lab", "Everything you got wrong stays in your attempt history. Use these queues to turn weak spots into reliable skills.")
    mastery = core.mastery_map(profile)
    now_ = core.now()
    missed = {k for k, v in mastery.items() if not v["last_correct"]}
    due = {k for k, v in mastery.items() if v["next_due"] <= now_}
    marks = core.bookmarked_ids(profile)
    a, b, c = st.columns(3)
    a.metric("Need another try", len(missed))
    b.metric("Due for review", len(due))
    c.metric("Bookmarked", len(marks))
    section("Choose a revision queue")
    tabs = st.tabs([f"Missed ({len(missed)})", f"Due ({len(due)})", f"Bookmarks ({len(marks)})"])
    for tab, ids, title in zip(tabs, (missed, due, marks), ("Missed", "Due", "Bookmarked")):
        with tab:
            review_list(profile, ids, title)

    section("Your earlier incorrect answers", "Review what you selected, the correct choice, and why it works.")
    attempts = [a for a in core.attempt_history(profile, 400) if a["kind"] == "mcq" and not a["correct"] and a["question_id"] in Q_LOOKUP]
    if not attempts:
        st.info("No wrong MCQ attempts recorded. Your history will appear here as you practice.")
    else:
        record = st.selectbox("Choose an earlier mistake", range(len(attempts)),
                              format_func=lambda i: f'{as_ist(attempts[i]["created_at"])} · {Q_LOOKUP[attempts[i]["question_id"]]["prompt"][:88]}')
        attempt = attempts[record]
        q = Q_LOOKUP[attempt["question_id"]]
        st.markdown(f'**{q["prompt"]}**')
        if q.get("code"):
            st.code(q["code"], language="python")
        st.error("You chose: " + q["options"][attempt["answer_index"]])
        st.success("Correct choice: " + q["options"][q["answer"]])
        st.markdown(f'<div class="feedback"><strong>Explanation</strong><p>{esc(q["explanation"])}</p></div>', unsafe_allow_html=True)
        personal_note(profile, q)


def progress_page(profile: str) -> None:
    hero("Growth / Analytics", "Your learning progress", "Understand your strong topics, find where you lose marks, and keep your practice history safe.")
    metric = core.profile_metrics(profile)
    a, b, c, d = st.columns(4)
    a.metric("Total attempts", metric["attempts"])
    b.metric("Accuracy", f'{metric["accuracy"]}%')
    c.metric("Unique questions", metric["studied"])
    d.metric("Mastered · 3+ streak", metric["mastered"])
    records = core.attempt_history(profile, 100000)
    stats = defaultdict(lambda: [0, 0])
    for entry in records:
        q = Q_LOOKUP.get(entry["question_id"])
        if q:
            stats[q["topic_name"]][0] += 1
            stats[q["topic_name"]][1] += int(entry["correct"])
    section("Strength by topic", "Performance across MCQs and self-assessed coding tasks.")
    if stats:
        rows = [{"Topic": key, "Attempts": n, "Correct": right, "Accuracy %": round(100 * right / n)}
                for key, (n, right) in sorted(stats.items())]
        for row in sorted(rows, key=lambda r: (-r["Attempts"], r["Topic"])):
            pct = max(0, min(100, row["Accuracy %"]))
            st.markdown(
                f'<div class="topic-row"><span class="topic-label">{esc(row["Topic"])}</span>'
                f'<div class="topic-track" role="meter" aria-label="{esc(row["Topic"])} accuracy" '
                f'aria-valuemin="0" aria-valuemax="100" aria-valuenow="{pct}">'
                f'<div class="topic-fill" style="width:{pct}%"></div></div>'
                f'<span class="topic-rate">{pct}%</span></div>', unsafe_allow_html=True,
            )
        with st.expander("View the detailed topic table"):
            rich_table(rows)
    else:
        st.info("Answer your first questions to unlock topic analytics.")
    section("Recent sessions")
    sessions = core.recent_sessions(profile, limit=30)
    if sessions:
        rich_table([{"Saved at (IST)": as_ist(s["created_at"]),
                    "Mode": s["configuration"].get("mode", "All"),
                    "Progress": f'{s["position"]}/{len(s["queue"])}',
                    "Status": "Finished" if s["completed_at"] else "In progress"} for s in sessions])
    else:
        st.caption("No saved sessions yet.")
    section("Export & backup", "Keep your history when moving computers or replacing app files.")
    left, right = st.columns(2)
    with left:
        st.download_button("Export attempts (CSV)", data=attempts_export_ist(profile),
                           file_name=f'python_attempts_{profile.replace(" ", "_")}.csv',
                           mime="text/csv", use_container_width=True)
    with right:
        dbfile = core.DEFAULT_DB
        if dbfile.exists():
            st.download_button("Download progress database", data=consistent_db_backup(),
                               file_name="python_mastery_progress.sqlite3",
                               mime="application/octet-stream", use_container_width=True)
    st.caption("All times shown in this app use Indian Standard Time (IST, UTC+05:30). The database keeps UTC timestamps for accurate scheduling. Keep data/progress.sqlite3 when updating.")


def packs_page(profile: str) -> None:
    hero("Library / Expand your knowledge", "Your lecture library", "All lecture packs in one learning workspace. Add new topics without resetting your progress.")
    for pack in PACKS.values():
        with st.container(border=True, key="pack_" + pack["pack_id"]):
            st.markdown(f'### {pack["title"]}')
            st.caption(pack.get("description", ""))
            a, b, c = st.columns(3)
            a.metric("Multiple-choice", len(pack.get("questions", [])))
            b.metric("Coding tasks", len(pack.get("challenges", [])))
            c.metric("Topics", len(pack["topics"]))
            st.markdown("".join(f'<span class="topic-pill">{esc(t["name"])}</span>' for t in pack["topics"]), unsafe_allow_html=True)
    section("Import your next lecture", "The app accepts validated JSON question packs, not raw PDFs. Send your PDF to create a compatible pack first.")
    uploaded = st.file_uploader("Select a JSON question pack", type=["json"])
    if uploaded is not None:
        if st.button("Validate & import lecture", type="primary"):
            try:
                dest = core.import_pack(uploaded.getvalue())
                st.success(f"Imported {Path(dest).name}. Your earlier progress remains intact.")
                st.rerun()
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                st.error(str(exc))
    with st.expander("See the pack format and question ID rules"):
        st.code('''{
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
}''', language="json")
        st.caption("Use a different pack_id and globally unique question IDs for every lecture.")


def sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><span class="brand-symbol">' + svg_icon("coding", 25, "#fff") + '</span>'
            '<div><div class="brand-name">Python Mastery Lab</div>'
            '<div class="brand-caption">YOUR STUDY WORKSPACE</div></div></div>',
            unsafe_allow_html=True,
        )
        profile = st.text_input(
            "Learner profile", value="My Python practice", max_chars=60,
            help="Use the same profile name to reopen your saved questions and history.",
        ).strip() or "My Python practice"
        st.markdown('<div class="brand-caption" style="margin:19px 0 11px">EXPLORE</div>', unsafe_allow_html=True)
        if st.session_state.get("current_page") not in {id_ for id_, _ in PAGES}:
            requested = str(st.query_params.get("page", "home"))
            st.session_state["current_page"] = requested if requested in {id_ for id_, _ in PAGES} else "home"
        for id_, title in PAGES:
            if st.button(title, key="nav_" + id_,
                         type="primary" if id_ == st.session_state["current_page"] else "secondary",
                         use_container_width=True):
                go_to(id_)
        st.divider()
        brief = core.profile_metrics(profile)
        st.markdown(
            f'<div class="side-stats"><span>LEARNING SNAPSHOT</span>'
            f'<div style="margin-top:9px"><strong>{brief["correct"]}</strong> correct / '
            f'<strong>{brief["attempts"]}</strong> attempts</div>'
            f'<div style="margin-top:7px"><span>{brief["due"]} due · {brief["missed"]} need practice</span></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sidebar-small" style="margin-top:16px">'
                    'Your answers and notes stay on this computer. The native sidebar arrow in the top header can close or reopen this panel.</div>',
                    unsafe_allow_html=True)
    return profile, st.session_state["current_page"]


def top_toolbar() -> None:
    """Navigation remains usable after the native sidebar has been closed."""
    left, center, right = st.columns([1.15, 3, 1.55], vertical_alignment="center", gap="small")
    with left:
        with st.popover("Menu"):
            st.caption("Jump to a section — works even when the sidebar is closed")
            for page_id, title in PAGES:
                if st.button(title, use_container_width=True, key="top_nav_" + page_id,
                             type="primary" if page_id == st.session_state["current_page"] else "secondary"):
                    go_to(page_id)
    with center:
        current_label = next((label for key, label in PAGES if key == st.session_state["current_page"]), "Workspace")
        st.markdown(
            '<div class="topbar"><span class="topbar-overline">Python mastery lab</span>'
            f'<span class="topbar-title">{esc(current_label)}</span></div>', unsafe_allow_html=True,
        )
    with right:
        st.toggle("Dark mode", key="dark_mode", on_change=persist_theme,
                  help="Switch the complete interface between light and dark mode. Your choice stays in the page URL after refresh.")


profile, page = sidebar()
top_toolbar()
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
