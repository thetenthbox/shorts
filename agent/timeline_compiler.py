from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .timeline_schema import validate_timeline


@dataclass(frozen=True)
class CompiledTimeline:
    duration_ms: int
    fps: int
    schedule: Dict[int, List[Dict[str, Any]]]


def compile_timeline(timeline: Dict[str, Any]) -> CompiledTimeline:
    validate_timeline(timeline)

    schedule: Dict[int, List[Dict[str, Any]]] = {}
    for ev in timeline["events"]:
        t = int(ev["t_ms"])
        schedule.setdefault(t, []).append(ev)

    return CompiledTimeline(
        duration_ms=int(timeline["duration_ms"]),
        fps=int(timeline["fps"]),
        schedule=schedule,
    )


