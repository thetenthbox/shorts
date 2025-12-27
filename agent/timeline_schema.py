from __future__ import annotations

from typing import Any, Dict

from jsonschema import Draft202012Validator


TIMELINE_SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["duration_ms", "fps", "events"],
    "properties": {
        "duration_ms": {"type": "integer", "minimum": 1},
        "fps": {"type": "integer", "minimum": 1, "maximum": 120},
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["t_ms", "op", "target"],
                "properties": {
                    "t_ms": {"type": "integer", "minimum": 0},
                    "op": {
                        "type": "string",
                        "enum": ["classAdd", "classRemove", "textSet", "layerShow", "layerHide"],
                    },
                    "target": {"type": "string", "minLength": 1},
                    "value": {},
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}


_validator = Draft202012Validator(TIMELINE_SCHEMA)


def validate_timeline(data: Dict[str, Any]) -> None:
    errors = sorted(_validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        msg = "; ".join([f"{list(e.path)}: {e.message}" for e in errors[:5]])
        raise ValueError(f"Invalid timeline.json: {msg}")

    # Extra rule: events should be non-decreasing by t_ms
    prev = -1
    for ev in data["events"]:
        t = ev["t_ms"]
        if t < prev:
            raise ValueError("Invalid timeline.json: events not sorted by t_ms")
        prev = t


