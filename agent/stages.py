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
    
    system_prompt = """You are a professional video storyboard agent for short-form vertical videos (1080x1920).

Given an audio script, produce:
1. A DETAILED video_script in markdown
2. A precise timeline JSON with animation events

## VIDEO SCRIPT REQUIREMENTS
The video_script_md MUST include for EACH scene:
- **Timestamp range** (e.g., "0.0s - 2.5s")
- **Voiceover text** (exact words being spoken during this scene)
- **Visual elements**: What appears on screen (exact text, images, components)
- **Animation sequence**: Step-by-step animations with timing offsets
- **Transition**: How this scene exits/next scene enters

Example format:
```
## SCENE 1: HOOK (0.0s - 3.0s)

**Voiceover:**
> "Let's say you're working at a bulge bracket investment bank..."

**Visual:**
- Wall Street image fills screen (zoomed 130%)
- Text overlay: "WALL STREET" (white, 72px, centered)

**Animation sequence:**
1. (0.0s) Image starts panning right with `panRight`
2. (1.5s) Text fades up with `fadeUp`
3. (2.5s) Image slides down with `slideOutDown`

**Transition:** Slide down reveals blue panel
```

## AVAILABLE ANIMATIONS
- fadeUp: fade in from below (0.5s)
- popIn: pop/scale in (0.25s)
- zoomOut: zoom out magnify effect (0.5s)
- slideOutDown: slide down and exit (0.6s)
- slideOutRight: slide right and exit (0.6s)
- swipe-out: swipe left and fade (0.5s)
- panRight: Ken Burns pan effect (2.5s)
- animate-exit: generic exit

## AVAILABLE COMPONENTS
- wallstreetContainer, bluePanel: intro layers
- bullet1, bullet2: text bullets (CMU Serif, 48px)
- spreadsheet: DCF table with callouts
- callout1, callout2, callout3: parameter badges
- mcqContainer, mcqQuestion, optionA, optionB, optionC: multiple choice
- realityLayer: context/conflict cards
- goalLayer: goal badges ("ALIGN FAST", "SHIP CLEAN")
- playbookLayer: step-by-step checklist
- wrapLayer: summary + CTA

## TIMELINE JSON FORMAT
{
  "duration_ms": <total duration in milliseconds>,
  "fps": 30,
  "events": [
    {"t_ms": 0, "op": "layerShow", "target": "wallstreetContainer"},
    {"t_ms": 0, "op": "classAdd", "target": "wallstreetImg", "value": "panRight"},
    {"t_ms": 2500, "op": "classAdd", "target": "wallstreetContainer", "value": "slideOutDown"},
    {"t_ms": 3100, "op": "layerHide", "target": "wallstreetContainer"},
    {"t_ms": 3100, "op": "layerShow", "target": "bluePanel"},
    {"t_ms": 4000, "op": "textSet", "target": "bullet1", "value": "Your exact text here"}
  ]
}

Operations:
- classAdd: Add CSS animation class
- classRemove: Remove CSS class
- layerShow: Show element (display: block)
- layerHide: Hide element (display: none)
- textSet: Set element's innerHTML

## RULES
1. Every scene must have EXACT voiceover text from the audio script
2. Timeline events must be in chronological order (t_ms ascending)
3. Show layers BEFORE animating them
4. Hide layers AFTER exit animations complete (~600ms later)
5. Text content must be specified via textSet operations

Respond with a JSON object:
- "video_script_md": string (detailed markdown per format above)
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

