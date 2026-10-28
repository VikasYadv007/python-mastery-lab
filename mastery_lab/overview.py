"""Overview presentation data and a locally authored, self-contained visual scene."""

from __future__ import annotations

import base64
import hashlib
import html
import json
from pathlib import Path

from ui_style import THEMES, python_mark

ASSETS = Path(__file__).with_name("assets")


def topic_summaries(packs: dict, mastery: dict) -> list[dict]:
    """Keep topic coverage separate from accuracy and from full-library totals."""
    result = []
    for pack in packs.values():
        items = pack.get("questions", []) + pack.get("challenges", [])
        for topic in pack["topics"]:
            matching = [q for q in items if q["topic"] == topic["id"]]
            states = [mastery[q["id"]] for q in matching if q["id"] in mastery]
            correct = sum(m["total_correct"] for m in states)
            wrong = sum(m["total_wrong"] for m in states)
            result.append(
                {
                    "key": f"{pack['pack_id']}:{topic['id']}",
                    "name": topic["name"],
                    "pack_id": pack["pack_id"],
                    "lecture": pack["title"],
                    "questions": len(matching),
                    "mcqs": len([q for q in matching if q["type"] == "mcq"]),
                    "coding": len([q for q in matching if q["type"] == "coding"]),
                    "studied": len(states),
                    "mastered": sum(m["streak"] >= 3 for m in states),
                    "missed": sum(not m["last_correct"] for m in states),
                    "accuracy": round(correct * 100 / (correct + wrong))
                    if correct + wrong
                    else None,
                }
            )
    return result


def observatory_html(summary: dict, topics: list[dict], *, dark: bool) -> str:
    """Only static, authored JavaScript executes. Learner content stays inert data.

    JSON is escaped into an HTML attribute, never interpolated into JavaScript.
    The client uses textContent for topic names. No question code is executed.
    """
    payload = html.escape(
        json.dumps({"summary": summary, "topics": topics}, ensure_ascii=False), quote=True
    )
    # st.html uses an HTML-only sanitizer. Keep the local vector intact as an
    # image instead of relying on inline SVG surviving that sanitizer.
    logo = base64.b64encode(python_mark(62).encode()).decode()
    script = ASSETS.joinpath("overview.js").read_text(encoding="utf-8")
    # Give authored HTML the shared tokens directly so it does not depend on
    # stylesheet inheritance across Streamlit's rendering boundaries.
    tokens = ";".join(
        f"{key}:{value}" for key, value in THEMES["dark" if dark else "light"].items()
    )
    return (
        ASSETS.joinpath("overview.html")
        .read_text(encoding="utf-8")
        .replace("__OV_THEME__", "dark" if dark else "light")
        .replace("__OV_THEME_VARS__", html.escape(tokens, quote=True))
        .replace("__OV_VERSION__", hashlib.sha256(script.encode()).hexdigest()[:12])
        .replace(
            "__OV_LOGO__",
            f'<img width="62" height="62" src="data:image/svg+xml;base64,{logo}" alt="">',
        )
        .replace("__OV_QUESTIONS__", str(int(summary["mcqs"])))
        .replace("__OV_CODING__", str(int(summary["coding"])))
        .replace("__OV_TOPICS__", str(len(topics)))
        .replace("__OV_EXPLORED__", str(int(summary["studied"])))
        .replace(
            "__OV_ACCURACY__", "—" if summary["accuracy"] is None else f"{summary['accuracy']:g}%"
        )
        .replace("__OV_STREAK__", str(int(summary["streak"])))
        .replace("__OV_DUE__", str(int(summary["due"])))
        .replace("__OV_SCRIPT__", script)
        .replace("__OV_DATA__", payload)
    )
