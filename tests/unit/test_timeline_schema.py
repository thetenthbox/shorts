import json
from pathlib import Path

import pytest

from agent.timeline_schema import validate_timeline


def test_validate_timeline_ok(tmp_path: Path):
    data = {"duration_ms": 1000, "fps": 30, "events": [{"t_ms": 0, "op": "layerShow", "target": "mcq"}]}
    validate_timeline(data)


def test_validate_timeline_rejects_unsorted():
    data = {
        "duration_ms": 1000,
        "fps": 30,
        "events": [
            {"t_ms": 10, "op": "layerShow", "target": "a"},
            {"t_ms": 0, "op": "layerShow", "target": "b"},
        ],
    }
    with pytest.raises(ValueError, match="not sorted"):
        validate_timeline(data)


def test_validate_timeline_rejects_unknown_op():
    data = {"duration_ms": 1000, "fps": 30, "events": [{"t_ms": 0, "op": "NOPE", "target": "a"}]}
    with pytest.raises(ValueError):
        validate_timeline(data)


