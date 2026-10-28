"""Deterministic analytics and revision queues; no UI or database side effects."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
PERIODS = {"All time": None, "Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
QUEUE_HELP = {
    "Needs another try": "Your most recent attempt was incorrect. Older mistakes remain in history after you improve.",
    "Due now": "Previously studied questions whose scheduled review time has arrived. A wrong answer is immediately due.",
    "Bookmarked": "Questions you saved for later, whether or not you have attempted them.",
    "Recovered mistakes": "Previously missed questions whose latest attempt is correct. Revisit them to make the learning stick.",
    "All studied": "Every installed question you have attempted, including self-assessed coding tasks.",
}


def parse_time(value: str | None) -> datetime | None:
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt
    except (ValueError, TypeError):
        return None


def content_matches(
    q: dict,
    *,
    kind="All practice",
    pack="All lectures",
    topic="All topics",
    difficulty="Any difficulty",
    search="",
) -> bool:
    if kind == "MCQs" and q["type"] != "mcq":
        return False
    if kind == "Coding (self-assessed)" and q["type"] != "coding":
        return False
    if pack != "All lectures" and q["pack_id"] != pack:
        return False
    if topic != "All topics" and q["topic_name"] != topic:
        return False
    if difficulty != "Any difficulty" and q["difficulty"] != difficulty:
        return False
    words = f"{q['id']} {q.get('title', '')} {q['prompt']} {q['topic_name']} {' '.join(q.get('tags', []))}".casefold()
    return all(word in words for word in search.casefold().split())


def filtered_attempts(
    records: list[dict], lookup: dict[str, dict], *, today: date, period="All time", **filters
) -> list[dict]:
    days = PERIODS[period]
    start = today - timedelta(days=days - 1) if days else None
    result = []
    for row in records:
        q = lookup.get(row["question_id"])
        dt = parse_time(row["created_at"])
        if (
            q
            and dt
            and dt.astimezone(IST).date() <= today
            and (start is None or dt.astimezone(IST).date() >= start)
            and content_matches(q, **filters)
        ):
            result.append(row)
    return result


def activity_summary(records: list[dict], today: date) -> dict:
    counts = Counter()
    for row in records:
        dt = parse_time(row["created_at"])
        if dt:
            counts[dt.astimezone(IST).date()] += 1
    days = sorted(counts)
    best = running = 0
    previous = None
    for day in days:
        running = running + 1 if previous and day == previous + timedelta(days=1) else 1
        best = max(best, running)
        previous = day
    cursor = today if today in counts else today - timedelta(days=1)
    streak = 0
    while cursor in counts:
        streak += 1
        cursor -= timedelta(days=1)
    correct = sum(bool(r["correct"]) for r in records)
    return {
        "attempts": len(records),
        "correct": correct,
        "accuracy": round(correct * 100 / len(records), 1) if records else None,
        "studied": len({r["question_id"] for r in records}),
        "active_days": len(days),
        "best_streak": best,
        "streak": streak,
        "today": counts[today],
    }


def daily_activity(records: list[dict], today: date, days=30) -> list[dict]:
    counts = defaultdict(lambda: [0, 0])
    for row in records:
        dt = parse_time(row["created_at"])
        if dt:
            day = dt.astimezone(IST).date()
            counts[day][0] += 1
            counts[day][1] += bool(row["correct"])
    result = []
    for i in range(days):
        day = today - timedelta(days=days - i - 1)
        n, right = counts[day]
        result.append(
            {
                "Date": day.isoformat(),
                "Attempts": n,
                "Correct": right,
                "Accuracy": round(100 * right / n, 1) if n else None,
                "Week": (day - timedelta(days=day.weekday())).isoformat(),
                "Day": day.strftime("%a"),
            }
        )
    return result


def activity_window(records: list[dict], today: date, period: str) -> int:
    """Avoid months of leading empty bars for learners with a short history."""
    if PERIODS[period] is not None:
        return PERIODS[period]
    dates = [dt.astimezone(IST).date() for row in records if (dt := parse_time(row["created_at"]))]
    return min(90, max(14, (today - min(dates)).days + 1)) if dates else 14


def performance_rows(records: list[dict], lookup: dict[str, dict], by="topic") -> list[dict]:
    groups = {}
    for row in records:
        q = lookup.get(row["question_id"])
        if not q:
            continue
        key = f"{q['pack_id']}:{q['topic']}" if by == "topic" else q["difficulty"]
        group = groups.setdefault(
            key,
            {
                "Key": key,
                "Topic": q["topic_name"],
                "Lecture": q["pack_title"],
                "Difficulty": q["difficulty"],
                "Attempts": 0,
                "Correct": 0,
            },
        )
        group["Attempts"] += 1
        group["Correct"] += bool(row["correct"])
    for group in groups.values():
        group["Wrong"] = group["Attempts"] - group["Correct"]
        group["Accuracy"] = round(100 * group["Correct"] / group["Attempts"], 1)
    return sorted(groups.values(), key=lambda r: (r["Accuracy"], -r["Attempts"], r["Key"]))


def review_queues(
    mastery: dict, marks: set[str], installed: set[str], current: datetime
) -> dict[str, set[str]]:
    missed, due, recovered = set(), set(), set()
    for qid, state in mastery.items():
        if qid not in installed:
            continue
        if not state["last_correct"]:
            missed.add(qid)
        elif state["total_wrong"]:
            recovered.add(qid)
        dt = parse_time(state["next_due"])
        if dt and dt <= current:
            due.add(qid)
    return {
        "Needs another try": missed,
        "Due now": due,
        "Bookmarked": marks & installed,
        "Recovered mistakes": recovered,
        "All studied": set(mastery) & installed,
    }


def sort_review(items: list[dict], mastery: dict, order: str) -> list[dict]:
    def priority(q):
        m = mastery.get(q["id"], {})
        if order == "Oldest review first":
            return (m.get("next_due", "9999"), q["id"])
        if order == "Topic A–Z":
            return (q["topic_name"], q["id"])
        return (-m.get("total_wrong", 0), m.get("next_due", "9999"), q["id"])

    return sorted(items, key=priority)


def review_forecast(mastery: dict, installed: set[str], current: datetime) -> list[dict]:
    today = current.astimezone(IST).date()
    result = [
        {"Window": "Due now", "Questions": 0, "Order": 0},
        {"Window": "Later today", "Questions": 0, "Order": 1},
    ]
    result += [
        {"Window": (today + timedelta(days=i)).strftime("%d %b"), "Questions": 0, "Order": i + 1}
        for i in range(1, 8)
    ]
    for qid, state in mastery.items():
        dt = parse_time(state["next_due"])
        if qid not in installed or dt is None:
            continue
        offset = (dt.astimezone(IST).date() - today).days
        if dt <= current:
            result[0]["Questions"] += 1
        elif 0 <= offset <= 7:
            result[offset + 1]["Questions"] += 1
    return result
