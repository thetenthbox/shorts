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
1. A DETAILED video_script in markdown with EXACT voiceover timing
2. A precise timeline JSON with animation events synced to voiceover

## CRITICAL: VOICEOVER-DRIVEN TIMING
The video MUST be driven by the voiceover. Every animation should be triggered by specific words being spoken.

Assume speaking rate: ~150 words per minute (~2.5 words/second, ~400ms per word)

## VIDEO SCRIPT REQUIREMENTS
The video_script_md MUST include for EACH scene:

### 1. EXACT TRANSCRIPT with word-level timing estimates
Break down the voiceover into phrases, estimating when each phrase starts/ends.

### 2. ANIMATION TRIGGERS tied to specific words
Specify which word triggers each animation.

### 3. ON-SCREEN TEXT that matches voiceover
Any text shown should reinforce what's being said.

## EXAMPLE FORMAT:

```markdown
## SCENE 1: HOOK (0.0s - 6.5s)

### Voiceover Transcript:
| Time | Words |
|------|-------|
| 0.0s - 1.2s | "Let's say you're working" |
| 1.2s - 2.8s | "at a bulge bracket investment bank" |
| 2.8s - 4.0s | "on Wall Street." |
| 4.0s - 5.2s | "Your senior associate" |
| 5.2s - 6.5s | "is ripping your model apart." |

### Animation Triggers:
| Trigger Word | Time | Animation |
|--------------|------|-----------|
| "Let's" | 0.0s | wallstreetContainer → layerShow + panRight |
| "Wall Street" | 2.8s | Text "WALL STREET" → fadeUp |
| "associate" | 4.5s | wallstreetContainer → slideOutDown |
| "ripping" | 5.5s | spreadsheet → layerShow + popIn |

### Visual Elements:
- Wall Street cityscape image (zoomed 130%, panning right)
- Text overlay: "WALL STREET" (white, 72px, appears at 2.8s)
- Spreadsheet with red highlights (appears at 5.5s)

### On-Screen Text:
- (2.8s) "WALL STREET" - centered, white, 72px
- (5.5s) Spreadsheet cells highlighted in red
```

## SCENE STRUCTURE
Each scene should cover ONE logical unit of the script:
1. **HOOK** (0-6s): Grab attention, establish context
2. **PROBLEM** (6-12s): Present the conflict/question
3. **OPTIONS** (12-18s): Show choices (MCQ format works well)
4. **INSIGHT** (18-30s): Reveal the answer/strategy
5. **STEPS** (30-45s): Actionable takeaways
6. **CTA** (45-50s): Call to action, branding

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
  "voiceover_segments": [
    {"start_ms": 0, "end_ms": 1200, "text": "Let's say you're working"},
    {"start_ms": 1200, "end_ms": 2800, "text": "at a bulge bracket investment bank"},
    {"start_ms": 2800, "end_ms": 4000, "text": "on Wall Street."}
  ],
  "events": [
    {"t_ms": 0, "op": "layerShow", "target": "wallstreetContainer", "trigger": "Let's"},
    {"t_ms": 0, "op": "classAdd", "target": "wallstreetImg", "value": "panRight"},
    {"t_ms": 2800, "op": "textSet", "target": "titleText", "value": "WALL STREET", "trigger": "Wall Street"},
    {"t_ms": 2800, "op": "classAdd", "target": "titleText", "value": "fadeUp"},
    {"t_ms": 4500, "op": "classAdd", "target": "wallstreetContainer", "value": "slideOutDown", "trigger": "associate"},
    {"t_ms": 5100, "op": "layerHide", "target": "wallstreetContainer"},
    {"t_ms": 5500, "op": "layerShow", "target": "spreadsheet", "trigger": "ripping"},
    {"t_ms": 5500, "op": "classAdd", "target": "spreadsheet", "value": "popIn"}
  ]
}

### Event Fields:
- t_ms: Timestamp in milliseconds
- op: Operation (classAdd, classRemove, layerShow, layerHide, textSet)
- target: Element ID
- value: CSS class name OR text content (for textSet)
- trigger: (optional) The spoken word that triggers this animation

### Operations:
- classAdd: Add CSS animation class
- classRemove: Remove CSS class
- layerShow: Show element (display: block)
- layerHide: Hide element (display: none)
- textSet: Set element's innerHTML

## RULES
1. EVERY animation must be tied to a word in the voiceover (use "trigger" field)
2. voiceover_segments must cover the ENTIRE audio script, split into logical phrases
3. Timeline events must be in chronological order (t_ms ascending)
4. Show layers BEFORE animating them
5. Hide layers AFTER exit animations complete (~600ms later)
6. On-screen text should MATCH or reinforce the voiceover
7. Estimate ~400ms per word for timing

## OUTPUT
Respond with a JSON object containing:
- "video_script_md": string (detailed markdown with voiceover tables)
- "timeline": object (timeline JSON with voiceover_segments and events)
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


@dataclass
class DetailResult:
    detailed_script_md: str
    refined_timeline: Dict[str, Any]


def stage_detail_pass(
    *,
    client: OpenRouterClient,
    video_script: str,
    timeline: Dict[str, Any],
) -> DetailResult:
    """Stage B2: Polish video script with detailed visual descriptions."""
    
    system_prompt = """You are an infographic animator specifying motion graphics for a short vertical video (1080x1920).

Style: Clean infographic/motion graphics on a WHITE background with subtle grey plus-sign pattern.

## YOUR TASK
For each scene, specify exactly what appears and how it animates. Keep it simple and clean.

## EXAMPLE OUTPUT:

```markdown
## SCENE 1: HOOK (0.0s - 4.0s)

### Elements:
1. **Header text** "THE IB STRESS TEST"
   - Position: top 15%, centered
   - Font: CMU Serif, 56px, dark grey (#1f2937)
   - Animation: fadeUp at 0.0s (500ms)

2. **Bullet 1** "You're at a bulge bracket firm"
   - Position: top 35%, left-aligned with 80px padding
   - Font: CMU Serif, 42px, #1f2937
   - Animation: fadeUp at 1.0s (400ms)

3. **Bullet 2** "An Associate is shredding your model"
   - Position: top 45%, left-aligned
   - Animation: fadeUp at 2.0s (400ms)

### Transition: All elements swipe-out left at 3.5s

---

## SCENE 2: SPREADSHEET (4.0s - 8.0s)

### Elements:
1. **DCF Table** (centered)
   - White cells, light grey borders
   - 6 columns × 5 rows
   - Animation: popIn at 4.0s (300ms)

2. **Callout badges** zoom out from cells:
   - "WACC" at 5.0s
   - "Exit Multiple" at 5.5s
   - "Growth Rate" at 6.0s
   - Each: blue pill (#1e40af), white text, zoomOut animation

### Transition: Table fades out at 7.5s
```

## RULES
1. Background is ALWAYS white (#ffffff) with grey plus-pattern
2. Use simple animations: fadeUp, popIn, zoomOut, swipe-out
3. Text in CMU Serif or system-ui
4. Colors: dark grey text (#1f2937), blue accents (#1e40af), white cards
5. Keep descriptions SHORT and actionable

## OUTPUT
Return JSON with:
- "detailed_script_md": concise markdown listing elements + animations per scene
- "refined_timeline": timeline with added "description" field on each event
"""

    user_prompt = f"""Video Script:

{video_script}

Timeline:
```json
{json.dumps(timeline, indent=2)}
```

Add precise visual specifications to every element. Return valid JSON only."""

    resp = client.chat(
        model=OPENROUTER_MODEL_SCRIPT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=8000,
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
    
    return DetailResult(
        detailed_script_md=data.get("detailed_script_md", ""),
        refined_timeline=data.get("refined_timeline", timeline),
    )


def stage_scene_builder(
    *,
    client: OpenRouterClient,
    timeline: Dict[str, Any],
    base_html: str,
    animation_library: str,
    component_library: str,
    detailed_script: str = "",
) -> SceneBuildResult:
    """Stage C: Build HTML scene from timeline using Sonnet 4.5."""
    
    system_prompt = """You are an HTML animation builder for short-form vertical videos (1080x1920).

Given:
1. A timeline JSON with animation events
2. A base HTML template
3. Animation CSS library
4. Component library
5. (Optional) A detailed visual script with exact specifications

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

    detailed_section = ""
    if detailed_script:
        detailed_section = f"""
Detailed Visual Script (follow these specifications exactly):
```markdown
{detailed_script}
```

"""

    user_prompt = f"""Timeline:
```json
{json.dumps(timeline, indent=2)}
```
{detailed_section}
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

Generate the complete HTML with __shortsPlayAll() function. Follow the detailed visual script specifications exactly for colors, sizes, positions, and animations. Return valid JSON only."""

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

