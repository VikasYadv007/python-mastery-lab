"""Vega-Lite specifications styled for Python Glass, without remote assets."""

from __future__ import annotations

from collections import Counter

from ui_style import THEMES


def chart_spec(values: list[dict], kind: str, dark: bool) -> dict:
    t = THEMES["dark" if dark else "light"]
    # Amber has enough contrast on light glass; luminous Python gold suits dark glass.
    blue, gold = t["--accent"], t["--gold"] if dark else "#a67811"
    result = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": values},
        "height": 260,
        "background": "transparent",
        "config": {
            "view": {"stroke": None},
            "font": "Segoe UI",
            "axis": {
                "labelColor": t["--muted"],
                "titleColor": t["--muted"],
                "gridColor": t["--border"],
                "domain": False,
                "tickColor": t["--border"],
                "labelFontSize": 11,
                "titleFontSize": 11,
                "titlePadding": 12,
            },
            "legend": {"labelColor": t["--muted"], "titleColor": t["--text"], "orient": "bottom"},
        },
    }
    if kind == "activity":
        result.update(
            {
                "encoding": {
                    "x": {
                        "field": "Date",
                        "type": "temporal",
                        "scale": {"type": "utc"},
                        "axis": {"title": None, "format": "%d %b", "tickCount": 5},
                    },
                    "tooltip": [
                        {"field": "Date", "type": "nominal", "title": "Date (IST)"},
                        {"field": "Attempts"},
                        {"field": "Correct"},
                        {"field": "Accuracy", "title": "Accuracy (%)"},
                    ],
                },
                "layer": [
                    {
                        "mark": {
                            "type": "bar",
                            "color": blue,
                            "opacity": 0.65,
                            "cornerRadiusTopLeft": 3,
                            "cornerRadiusTopRight": 3,
                        },
                        "encoding": {
                            "y": {
                                "field": "Attempts",
                                "type": "quantitative",
                                "axis": {"tickMinStep": 1},
                            }
                        },
                    },
                    {
                        "transform": [{"filter": "datum.Accuracy != null"}],
                        "mark": {
                            "type": "line",
                            "color": gold,
                            "point": {"filled": True, "size": 38},
                        },
                        "encoding": {
                            "y": {
                                "field": "Accuracy",
                                "type": "quantitative",
                                "scale": {"domain": [0, 100]},
                                "axis": {"title": "Accuracy (%)", "grid": False, "orient": "right"},
                            }
                        },
                    },
                ],
                "resolve": {"scale": {"y": "independent"}},
            }
        )
    elif kind == "outcomes":
        result.update(
            {
                "mark": {
                    "type": "arc",
                    "innerRadius": {"expr": "min(width, height) * 0.26"},
                    "outerRadius": {"expr": "min(width, height) * 0.43"},
                    "cornerRadius": 4,
                    "padAngle": 0.035,
                },
                "encoding": {
                    "theta": {"field": "Attempts", "type": "quantitative"},
                    "color": {
                        "field": "Result",
                        "type": "nominal",
                        "scale": {
                            "domain": ["Correct / solved", "Incorrect / practice"],
                            "range": [blue, gold],
                        },
                        "legend": {"title": None, "columns": 1, "labelLimit": 150},
                    },
                    "tooltip": [{"field": "Result"}, {"field": "Attempts", "type": "quantitative"}],
                },
            }
        )
    elif kind == "topics":
        stacked = []
        names = Counter(r["Topic"] for r in values)
        labels = {
            r["Key"]: r["Topic"] if names[r["Topic"]] == 1 else f"{r['Topic']} · {r['Lecture']}"
            for r in values
        }
        for r in values:
            for status, field in (
                ("Correct / solved", "Correct"),
                ("Incorrect / practice", "Wrong"),
            ):
                stacked.append(
                    {**r, "Label": labels[r["Key"]], "Result": status, "Count": r[field]}
                )
        result["data"]["values"] = stacked
        result.update(
            {
                "height": max(180, min(650, len(values) * 40)),
                "mark": {"type": "bar", "cornerRadiusEnd": 4, "cursor": "pointer"},
                "params": [
                    {
                        "name": "topic_pick",
                        "select": {"type": "point", "fields": ["Key"], "toggle": False},
                    }
                ],
                "encoding": {
                    "y": {
                        "field": "Label",
                        "type": "nominal",
                        "sort": [labels[r["Key"]] for r in values],
                        "axis": {
                            "title": None,
                            "labelLimit": 140,
                        },
                    },
                    "x": {
                        "field": "Count",
                        "type": "quantitative",
                        "stack": "zero",
                        "title": "Attempts",
                        "axis": {"tickMinStep": 1},
                    },
                    "color": {
                        "field": "Result",
                        "scale": {
                            "domain": ["Correct / solved", "Incorrect / practice"],
                            "range": [blue, gold],
                        },
                        "legend": {"title": None},
                    },
                    "opacity": {"condition": {"param": "topic_pick", "value": 1}, "value": 0.35},
                    "tooltip": [
                        {"field": "Topic"},
                        {"field": "Lecture"},
                        {"field": "Attempts"},
                        {"field": "Accuracy", "title": "Accuracy (%)"},
                    ],
                },
            }
        )
    elif kind == "difficulty":
        result.update(
            {
                "mark": {"type": "bar", "color": blue, "cornerRadiusEnd": 6},
                "encoding": {
                    "x": {
                        "field": "Difficulty",
                        "type": "nominal",
                        "sort": ["Beginner", "Intermediate", "Advanced"],
                        "axis": {"labelAngle": 0, "title": None},
                    },
                    "y": {
                        "field": "Accuracy",
                        "type": "quantitative",
                        "scale": {"domain": [0, 100]},
                        "title": "Accuracy (%)",
                    },
                    "tooltip": [
                        {"field": "Difficulty"},
                        {"field": "Attempts"},
                        {"field": "Accuracy", "title": "Accuracy (%)"},
                    ],
                },
            }
        )
    elif kind == "calendar":
        result.update(
            {
                "height": 170,
                "mark": {"type": "rect", "cornerRadius": 4, "stroke": t["--bg"], "strokeWidth": 3},
                "encoding": {
                    "x": {
                        "field": "Week",
                        "type": "ordinal",
                        "axis": {
                            "title": None,
                            "labelExpr": "substring(datum.label, 5)",
                            "labelAngle": 0,
                            "labelOverlap": True,
                        },
                    },
                    "y": {
                        "field": "Day",
                        "type": "ordinal",
                        "sort": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                        "axis": {"title": None},
                    },
                    "color": {
                        "field": "Attempts",
                        "type": "quantitative",
                        "scale": {"range": [t["--code-bg"], blue]},
                        "legend": {"title": "Daily attempts", "direction": "horizontal"},
                    },
                    "tooltip": [
                        {"field": "Date", "type": "nominal", "title": "Date (IST)"},
                        {"field": "Attempts"},
                    ],
                },
            }
        )
    elif kind == "forecast":
        result.update(
            {
                "mark": {"type": "bar", "cornerRadiusEnd": 5},
                "encoding": {
                    "x": {
                        "field": "Window",
                        "type": "ordinal",
                        "sort": [r["Window"] for r in values],
                        "axis": {"title": None, "labelAngle": -35},
                    },
                    "y": {"field": "Questions", "type": "quantitative", "axis": {"tickMinStep": 1}},
                    "color": {
                        "condition": {"test": "datum.Order == 0", "value": gold},
                        "value": blue,
                    },
                    "tooltip": [{"field": "Window"}, {"field": "Questions"}],
                },
            }
        )
    else:
        raise ValueError(f"Unknown chart: {kind}")
    return result
