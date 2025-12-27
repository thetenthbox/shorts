"""Pipeline stages for Shorts generation."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import OPENROUTER_MODEL_SCRIPT, OPENROUTER_MODEL_HTML
from .openrouter_client import OpenRouterClient


@dataclass
class StoryboardResult:
    video_script_md: str
    timeline: Dict[str, Any]


@dataclass
class SceneBuildResult:
    html: str
    scene_spec: Dict[str, Any]


def stage_storyboard(
    *,
    client: OpenRouterClient,
    audio_script: str,
    duration_hint_s: int = 60,
) -> StoryboardResult:
    """Stage B: Convert audio script to video script + timeline.json using GPT-5."""
    
    system_prompt = """You are a video storyboard agent for short-form vertical videos (1080x1920).

Given an audio script, produce:
1. A video_script in markdown with scene breakdowns
2. A timeline JSON with precise animation events

Available animation classes (from ANIMATION_LIBRARY):
- fadeUp: fade in from below
- popIn: pop/scale in
- zoomOut: zoom out effect
- slideOutDown: slide down and exit
- slideOutRight: slide right and exit
- swipe-out: swipe left and fade
- animate-pan: pan effect
- animate-exit: exit animation

Available layers/components:
- wallstreetContainer, bluePanel: intro layers
- bullet1, bullet2: text bullets
- spreadsheet: DCF table
- callout1, callout2, callout3: parameter callouts
- mcqContainer, mcqQuestion, optionA, optionB, optionC: MCQ section
- realityLayer: context cards
- goalLayer: win/align badges
- playbookLayer: 4-step checklist
- wrapLayer: summary + CTA

Timeline JSON format:
{
  "duration_ms": <total duration>,
  "fps": 30,
  "events": [
    {"t_ms": 0, "op": "classAdd", "target": "elementId", "value": "animationClass"},
    {"t_ms": 1000, "op": "classRemove", "target": "elementId", "value": "animationClass"},
    {"t_ms": 2000, "op": "layerShow", "target": "layerId"},
    {"t_ms": 3000, "op": "layerHide", "target": "layerId"},
    {"t_ms": 4000, "op": "textSet", "target": "elementId", "value": "New text content"}
  ]
}

Respond with a JSON object containing:
- "video_script_md": string (markdown)
- "timeline": object (the timeline JSON)
"""

    user_prompt = f"""Audio script:

{audio_script}

Target duration: ~{duration_hint_s} seconds

Generate the video_script_md and timeline JSON. Return valid JSON only."""

    resp = client.chat(
        model=OPENROUTER_MODEL_SCRIPT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    content = resp["choices"][0]["message"]["content"]
    
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        first_newline = content.find("\n")
        if first_newline != -1:
            content = content[first_newline + 1:]
        if content.endswith("```"):
            content = content[:-3].strip()
    
    data = json.loads(content)
    
    return StoryboardResult(
        video_script_md=data.get("video_script_md", ""),
        timeline=data.get("timeline", {}),
    )


def stage_scene_builder(
    *,
    client: OpenRouterClient,
    timeline: Dict[str, Any],
    base_html: str,
    animation_library: str,
    component_library: str,
) -> SceneBuildResult:
    """Stage C: Build HTML scene from timeline using Sonnet 4.5."""
    
    system_prompt = """You are an HTML animation builder for short-form vertical videos (1080x1920).

Given:
1. A timeline JSON with animation events
2. A base HTML template
3. Animation CSS library
4. Component library

Your job:
1. Modify the base HTML to include all required elements referenced in the timeline
2. Ensure all element IDs from the timeline exist in the HTML
3. Add a `window.__shortsPlayAll()` function that executes the timeline events
4. The function should use setTimeout to trigger events at the specified times

The __shortsPlayAll function should:
- Reset all elements to initial state
- Execute each event at its t_ms time using setTimeout
- Support ops: classAdd, classRemove, layerShow, layerHide, textSet

Return a JSON object with:
- "html": the complete HTML string
- "scene_spec": {"element_ids": [...], "duration_ms": ..., "event_count": ...}
"""

    user_prompt = f"""Timeline:
```json
{json.dumps(timeline, indent=2)}
```

Base HTML:
```html
{base_html}
```

Animation Library (CSS):
```
{animation_library}
```

Component Library:
```
{component_library}
```

Generate the complete HTML with __shortsPlayAll() function. Return valid JSON only."""

    resp = client.chat(
        model=OPENROUTER_MODEL_HTML,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=16000,
        response_format={"type": "json_object"},
    )

    content = resp["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise ValueError(f"Empty response from LLM. Full response: {resp}")
    
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = content.find("\n")
        if first_newline != -1:
            content = content[first_newline + 1:]
        # Remove closing fence
        if content.endswith("```"):
            content = content[:-3].strip()
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}\nContent: {content[:500]}...")
    
    return SceneBuildResult(
        html=data.get("html", ""),
        scene_spec=data.get("scene_spec", {}),
    )


def load_audio_script(path: Path) -> str:
    """Load audio script from markdown file."""
    return path.read_text(encoding="utf-8")


def load_base_html(shorts_dir: Path) -> str:
    """Load base HTML template."""
    # Prefer templates/base.html, fallback to scenes/scene1.html
    base = shorts_dir / "templates" / "base.html"
    if base.exists():
        return base.read_text(encoding="utf-8")
    
    scene1 = shorts_dir / "scenes" / "scene1.html"
    if scene1.exists():
        return scene1.read_text(encoding="utf-8")
    
    raise FileNotFoundError("No base HTML template found")


def load_animation_library(shorts_dir: Path) -> str:
    """Load animation library docs."""
    lib = shorts_dir / "docs" / "ANIMATION_LIBRARY.md"
    if lib.exists():
        return lib.read_text(encoding="utf-8")
    return ""


def load_component_library(shorts_dir: Path) -> str:
    """Load component library docs."""
    lib = shorts_dir / "docs" / "COMPONENT_LIBRARY.md"
    if lib.exists():
        return lib.read_text(encoding="utf-8")
    return ""

