"""Analytics stays truthful across date boundaries, filters, and recovery states."""

from datetime import UTC, date, datetime

import altair as alt
import pytest

from mastery_lab import analytics as a
from mastery_lab.charts import chart_spec


def question(qid="q1", pack="p1", kind="mcq", topic="types"):
    return {
        "id": qid,
        "type": kind,
        "topic": topic,
        "topic_name": topic.title(),
        "pack_id": pack,
        "pack_title": pack,
        "difficulty": "Beginner",
        "prompt": "Explain this concept",
        "tags": [],
    }


def attempt(qid, when, correct=True):
    return {"question_id": qid, "created_at": when, "correct": int(correct)}


def test_period_filters_use_ist_and_exclude_missing_packs_and_future_days():
    lookup = {"q1": question()}
    rows = [
        attempt("q1", "2026-10-20T18:29:00Z"),
        attempt("q1", "2026-10-20T18:30:00Z"),
        attempt("q1", "2026-10-27T18:30:00Z"),
        attempt("missing", "2026-10-27T00:00:00Z"),
    ]
    selected = a.filtered_attempts(rows, lookup, today=date(2026, 10, 27), period="Last 7 days")
    assert selected == [rows[1]]
    assert a.daily_activity(selected, date(2026, 10, 27), 7)[0]["Attempts"] == 1


def test_filters_distinguish_coding_and_lecture_and_match_all_search_words():
    q = question(kind="coding")
    assert not a.content_matches(q, kind="MCQs")
    assert a.content_matches(q, kind="Coding (self-assessed)", search="q1 concept")
    assert not a.content_matches(q, search="q1 absent")
    assert not a.content_matches(q, pack="other")


def test_streaks_zero_days_and_accuracy_do_not_invent_results():
    rows = [attempt("q1", f"2026-10-{day}T00:00:00Z", day != 26) for day in (20, 21, 25, 26)]
    result = a.activity_summary(rows, date(2026, 10, 27))
    assert result["streak"] == result["best_streak"] == 2
    assert result["accuracy"] == 75
    assert result["today"] == 0
    assert a.activity_summary(rows, date(2026, 10, 28))["streak"] == 0
    daily = a.daily_activity(rows, date(2026, 10, 27), 3)
    assert [r["Attempts"] for r in daily] == [1, 1, 0]
    assert daily[-1]["Accuracy"] is None
    assert a.activity_summary([], date(2026, 10, 27))["accuracy"] is None
    assert a.activity_window(rows, date(2026, 10, 27), "All time") == 14
    assert a.activity_window(rows, date(2027, 10, 27), "All time") == 90
    assert a.activity_window(rows, date(2026, 10, 27), "Last 7 days") == 7


def test_topic_aggregation_keeps_lectures_separate():
    lookup = {"q1": question(), "q2": question("q2", "p2")}
    result = a.performance_rows(
        [attempt("q1", "2026-10-27"), attempt("q2", "2026-10-27", False)], lookup
    )
    assert len(result) == 2
    assert result[0]["Key"] == "p2:types"
    assert result[0]["Accuracy"] == 0
    assert result[1]["Accuracy"] == 100


def test_review_queues_preserve_recovered_mistakes_and_exclude_uninstalled_items():
    current = datetime(2026, 10, 27, 12, tzinfo=UTC)
    mastery = {
        "wrong": {"last_correct": 0, "total_wrong": 2, "next_due": "2026-10-26T00:00:00Z"},
        "recovered": {"last_correct": 1, "total_wrong": 1, "next_due": "2026-10-28T00:00:00Z"},
        "missing": {"last_correct": 0, "total_wrong": 8, "next_due": "2026-10-26T00:00:00Z"},
    }
    queues = a.review_queues(
        mastery, {"new", "wrong", "missing"}, {"wrong", "recovered", "new"}, current
    )
    assert queues["Needs another try"] == queues["Due now"] == {"wrong"}
    assert queues["Recovered mistakes"] == {"recovered"}
    assert queues["Bookmarked"] == {"new", "wrong"}
    assert queues["All studied"] == {"wrong", "recovered"}


def test_forecast_distinguishes_overdue_from_later_today_in_ist():
    current = datetime(2026, 10, 27, 12, tzinfo=UTC)
    mastery = {
        str(i): {"next_due": value}
        for i, value in enumerate(
            (
                "2026-10-27T11:59:00Z",
                "2026-10-27T13:00:00Z",
                "2026-10-27T18:30:00Z",
                "2026-11-10T00:00:00Z",
            )
        )
    }
    result = a.review_forecast(mastery, set(mastery), current)
    assert [r["Questions"] for r in result[:3]] == [1, 1, 1]
    assert sum(r["Questions"] for r in result) == 3


@pytest.mark.parametrize(
    "kind", ["activity", "outcomes", "topics", "difficulty", "calendar", "forecast"]
)
@pytest.mark.parametrize("dark", [False, True])
def test_chart_specs_validate_against_vega_lite_schema(kind, dark):
    values = [
        {
            "Date": "2026-10-27",
            "Week": "2026-10-26",
            "Day": "Tue",
            "Attempts": 2,
            "Correct": 1,
            "Wrong": 1,
            "Accuracy": 50,
            "Key": "p1:types",
            "Topic": "Types",
            "Lecture": "Lecture 1",
            "Difficulty": "Beginner",
            "Result": "Correct / solved",
            "Window": "Due now",
            "Questions": 1,
            "Order": 0,
        }
    ]
    alt.Chart.from_dict(chart_spec(values, kind, dark)).to_dict(validate=True)
