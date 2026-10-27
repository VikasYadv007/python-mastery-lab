"""Question-pack schema validation shared by imports, backups, and the engine."""

from __future__ import annotations

import re
from typing import Any


def validate_pack(pack: Any) -> None:
    """Fail early on malformed imported question packs."""
    if (
        not isinstance(pack, dict)
        or type(pack.get("schema_version")) is not int
        or pack["schema_version"] != 1
    ):
        raise ValueError("Pack must be a JSON object with schema_version = 1.")
    if not isinstance(pack.get("pack_id"), str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", pack["pack_id"]
    ):
        raise ValueError("pack_id needs 1–80 letters/digits/hyphens/underscores.")
    if not isinstance(pack.get("title"), str) or not pack["title"].strip():
        raise ValueError("title must be a nonempty string.")
    topics = pack.get("topics")
    if not isinstance(topics, list) or not topics:
        raise ValueError("topics needs a nonempty list.")
    topic_ids = set()
    for topic in topics:
        if (
            not isinstance(topic, dict)
            or not isinstance(topic.get("id"), str)
            or not isinstance(topic.get("name"), str)
        ):
            raise ValueError("Every topic requires id and name strings.")
        if not topic["id"].strip() or not topic["name"].strip():
            raise ValueError("Topic id and name must not be blank.")
        if topic["id"] in topic_ids:
            raise ValueError("Duplicate topic id.")
        topic_ids.add(topic["id"])
    ids = set()
    for kind, items in [("mcq", pack.get("questions", [])), ("coding", pack.get("challenges", []))]:
        if not isinstance(items, list):
            raise ValueError(f"{kind} items must be a list.")
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                raise ValueError(f"Every {kind} needs a string id.")
            if item["id"] in ids:
                raise ValueError(f"Duplicate question/challenge ID: {item['id']}")
            ids.add(item["id"])
            if not isinstance(item.get("topic"), str) or item["topic"] not in topic_ids:
                raise ValueError(f"Unknown topic in {item['id']}")
            if item.get("difficulty") not in ("Beginner", "Intermediate", "Advanced"):
                raise ValueError(f"Unsupported difficulty in {item['id']}")
            if item.get("source") not in ("notes", "extension"):
                raise ValueError(f"Invalid source tag in {item['id']}")
            if not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
                raise ValueError(f"Missing prompt in {item['id']}")
            if "code" in item and not isinstance(item["code"], str):
                raise ValueError(f"{item['id']}: code must be a string.")
            if "pages" in item and (
                not isinstance(item["pages"], list)
                or any(type(p) is not int or p < 1 for p in item["pages"])
            ):
                raise ValueError(f"{item['id']}: pages must be positive integers.")
            if "tags" in item and (
                not isinstance(item["tags"], list)
                or any(not isinstance(tag, str) for tag in item["tags"])
            ):
                raise ValueError(f"{item['id']}: tags must be strings.")
            if kind == "mcq":
                opts = item.get("options")
                if (
                    not isinstance(opts, list)
                    or len(opts) != 4
                    or not all(isinstance(x, str) and x.strip() for x in opts)
                    or len({x.strip() for x in opts}) != 4
                ):
                    raise ValueError(f"{item['id']}: need four unique answer options.")
                if type(item.get("answer")) is not int or not 0 <= item["answer"] < 4:
                    raise ValueError(f"{item['id']}: answer must be an index 0–3.")
                if not isinstance(item.get("explanation"), str) or not item["explanation"].strip():
                    raise ValueError(f"{item['id']}: missing explanation.")
            else:
                if not all(
                    isinstance(item.get(field), str) and item[field].strip()
                    for field in ("title", "rubric")
                ):
                    raise ValueError(f"{item['id']}: coding item requires a title and rubric.")
                if not all(
                    isinstance(item.get(field), str) for field in ("solution", "starter", "hint")
                ):
                    raise ValueError(f"{item['id']}: coding item missing solution/starter/hint.")
                if not isinstance(item.get("samples"), list):
                    raise ValueError(f"{item['id']}: samples must be a list.")
                for sample in item["samples"]:
                    if not isinstance(sample, dict) or not all(
                        isinstance(sample.get(field), str) for field in ("input", "output")
                    ):
                        raise ValueError(
                            f"{item['id']}: every sample needs input and output strings."
                        )
