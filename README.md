# 1learner Shorts

**Automated HTML animation → MP4 pipeline for YouTube Shorts.**

Turn an audio script into a fully rendered vertical video (1080×1920) with voiceover — no video editor required.

---

## Quick Start

```bash
cd Shorts

# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e '.[dev]'
playwright install chromium

# 3. Set up API keys
cat > .env << 'EOF'
OPENROUTER_API_KEY=your_openrouter_key
CARTESIA_API_KEY=your_cartesia_key
CARTESIA_VOICE_ID=0ad65e7f-006c-47cf-bd31-52279d487913
EOF

# 4. Run the pipeline
source .env && export OPENROUTER_API_KEY CARTESIA_API_KEY CARTESIA_VOICE_ID
shorts --id my_first_short --audio audio_scripts/audio_script1.md --duration 30
```

**Outputs:**
- `renders/my_first_short.mp4` — final video with audio
- `renders/my_first_short.wav` — voiceover audio
- `runs/my_first_short/` — all intermediate files

---

## How It Works

```
Audio Script ─┬─► Stage B: Storyboard (GPT-5)
              │       ├── video_script.md      (voiceover timing tables)
              │       └── timeline.json        (animation events)
              │
              ├─► Stage B2: Detail Pass (GPT-5)
              │       ├── detailed_script.md   (natural language descriptions)
              │       └── refined_timeline.json
              │
              ├─► Stage C: Scene Builder (Sonnet 4.5)
              │       └── scene.html           (runnable animation)
              │
              ├─► Stage D: TTS (Cartesia Sonic 3)
              │       └── voiceover.wav
              │
              └─► Stage E: Render (Playwright + ffmpeg)
                      └── final.mp4
```

### Pipeline Stages

| Stage | Model | What It Does | Output |
|-------|-------|--------------|--------|
| **D0: TTS + Timestamps (first)** | Cartesia Sonic 3 | Synthesizes voiceover audio AND word timestamps. We convert these to `voiceover_segments` which become the authoritative timing for the rest of the pipeline. | `renders/<id>.wav`, `runs/<id>/tts_words.json`, `runs/<id>/voiceover_segments.json` |
| **B: Storyboard (timestamp-driven)** | GPT-5 | Builds `timeline.json` using the authoritative `voiceover_segments` timestamps (no guesswork). | `video_script.md`, `timeline.json` |
| **B2: Detail Pass (visual-only)** | GPT-5 | Adds detailed visual descriptions/specs. **Must not change timing** (no changes to `t_ms` or segment times). | `detailed_script.md`, `refined_timeline.json` |
| **C: Scene Builder** | Sonnet 4.5 | Generates complete HTML/CSS/JS from timeline + detailed script. | `scene.html`, `scene_spec.json` |
| **E: Render** | Playwright + ffmpeg | Captures frames from the HTML animation using headless Chromium. Encodes to MP4 and muxes with audio. | `video.mp4`, `final.mp4` |

### Key Concept: Voiceover-Driven Timing

The entire animation is synced to the voiceover. Stage B produces timing tables like:

```markdown
| Time | Words |
|------|-------|
| 0.0s - 1.2s | "Let's say you're working" |
| 1.2s - 2.8s | "at a bulge bracket investment bank" |
| 2.8s - 4.0s | "on Wall Street." |
```

And animation triggers tied to specific words:

```json
{"t_ms": 2800, "op": "textSet", "target": "titleText", "value": "WALL STREET", "trigger": "Wall Street"}
```

Stage B2 then describes exactly what happens visually:

> "At 2.8s, when the voiceover says 'on Wall Street,' bold centered text 'WALL STREET' fades up smoothly from 20px below to rest at screen center (duration 500ms, ease-out). The font is CMU Serif, 56px, dark grey (#1f2937)..."

---

## CLI Reference

```bash
shorts --id <run_id> --audio <path> [options]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `--id` | Unique identifier for this run (used for output filenames) |
| `--audio` | Path to audio script markdown file (not needed with `--render-only`) |

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--duration` | 60 | Target video duration in seconds |
| `--skip-tts` | false | Skip voiceover generation |
| `--no-tts-first` | false | Disable timestamp-driven timing (use estimated timings) |
| `--skip-render` | false | Skip Playwright/ffmpeg rendering |
| `--render-only` | false | Only render MP4 from existing `runs/<id>/scene.html` |
| `--rebuild-html` | false | Rebuild `runs/<id>/scene.html` from existing `detailed_script.md` + timeline |
| `--debug` | false | Add debug overlay (timer + current script line) |

### Examples

```bash
# Full pipeline (20 second video)
shorts --id demo --audio audio_scripts/audio_script1.md --duration 20

# Generate scripts + HTML only (no TTS, no render)
shorts --id demo --audio audio_scripts/audio_script1.md --skip-tts --skip-render

# Generate scripts + HTML + TTS (no render)
shorts --id demo --audio audio_scripts/audio_script1.md --skip-render

# Re-render after editing scene.html manually
shorts --id demo --render-only

# Rebuild HTML (from detailed_script + timeline) and render
shorts --id demo --rebuild-html

# Rebuild HTML with debug overlay (no render)
shorts --id demo --rebuild-html --skip-render --debug
```

---

## Project Structure

```
Shorts/
├── agent/                    # Python pipeline code
│   ├── cli.py                # CLI entry point
│   ├── stages.py             # LLM stages (storyboard, scene builder)
│   ├── renderer.py           # Playwright frame capture + ffmpeg
│   ├── cartesia_tts.py       # Cartesia TTS client
│   ├── openrouter_client.py  # OpenRouter LLM client
│   ├── config.py             # Configuration + env vars
│   ├── timeline_schema.py    # Timeline JSON validation
│   └── qa.py                 # QA checks
│
├── audio_scripts/            # Input: voiceover scripts
│   └── audio_script1.md
│
├── templates/                # Starting points for new scenes
│   ├── base.html             # Boilerplate HTML template
│   └── script-template.md
│
├── assets/                   # Reusable components
│   ├── backgrounds/
│   ├── components/
│   └── excel/
│
├── docs/                     # Documentation
│   ├── PRODUCTION_GUIDE.md
│   ├── ANIMATION_LIBRARY.md
│   └── COMPONENT_LIBRARY.md
│
├── runs/                     # Pipeline run outputs (gitignored)
│   └── <run_id>/
│       ├── audio_script.md       # Input script (copied)
│       ├── video_script.md       # Stage B: voiceover timing tables
│       ├── timeline.json         # Stage B: animation events
│       ├── detailed_script.md    # Stage B2: natural language descriptions
│       ├── refined_timeline.json # Stage B2: refined events
│       ├── scene.html            # Stage C: runnable animation
│       ├── scene_spec.json       # Stage C: element specs
│       ├── frames/               # Stage E: captured PNGs
│       ├── video.mp4             # Stage E: video only
│       └── final.mp4             # Stage E: video + audio
│
├── renders/                  # Final outputs (gitignored)
│   ├── <run_id>.mp4
│   └── <run_id>.wav
│
├── tests/                    # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env                      # API keys (gitignored)
├── pyproject.toml            # Python package config
└── README.md
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...
CARTESIA_API_KEY=sk_car_...

# Optional (defaults shown)
CARTESIA_VOICE_ID=0ad65e7f-006c-47cf-bd31-52279d487913
```

### Models Used

| Purpose | Provider | Model ID |
|---------|----------|----------|
| Script writing / Storyboard | OpenRouter | `openai/gpt-5-chat` |
| HTML scene building | OpenRouter | `anthropic/claude-sonnet-4.5` |
| Text-to-speech | Cartesia | Sonic 3 |

---

## Manual Workflow (No API Keys)

You can also create shorts manually without the automated pipeline:

### 1. Write Audio Script

Create `audio_scripts/my_script.md`:

```markdown
Let's say you're working at a bank...
[pause]
What do you do?
```

### 2. Create Video Script

Create a rough video plan (timing + what appears) in any markdown file. The pipeline will generate `runs/<id>/video_script.md` and `runs/<id>/timeline.json` automatically when you run it with API keys.

### 3. Build HTML Scene

Copy `templates/base.html` to `runs/my_manual/scene.html` and add your content.

### 4. Preview in Browser

Open `runs/my_manual/scene.html` in Chrome:
- **▶ Play All** — run full timeline
- **1x / 3x** — toggle speed
- Side buttons — jump to sections

### 5. Record MP4

**Mac (QuickTime):**
1. QuickTime Player → File → New Screen Recording
2. Select the 1080×1920 container
3. Click Play All, record, stop
4. Export 1080p

---

## Modifying Pipeline Outputs

### Edit scene.html and re-render

1. Open `runs/<id>/scene.html` in your editor
2. Modify animations, timing, or content
3. Re-render:

```bash
shorts --id <id> --render-only
```

### Regenerate scene from edited timeline

If you modify `runs/<id>/timeline.json` or `refined_timeline.json`:

```python
import json
from pathlib import Path
from agent.openrouter_client import OpenRouterClient
from agent.config import get_openrouter_api_key
from agent.stages import stage_scene_builder, load_base_html, load_animation_library, load_component_library

shorts = Path('.')
timeline = json.loads((shorts / 'runs/my_run/refined_timeline.json').read_text())
client = OpenRouterClient(api_key=get_openrouter_api_key())

result = stage_scene_builder(
    client=client,
    timeline=timeline,
    base_html=load_base_html(shorts),
    animation_library=load_animation_library(shorts),
    component_library=load_component_library(shorts),
)
(shorts / 'runs/my_run/scene_v2.html').write_text(result.html)
```

### Preview without rendering

Open `runs/<id>/scene.html` directly in Chrome to preview animations:
- Click **▶ Play All** to run the full timeline
- Use **1x / 3x** button to toggle speed
- Side buttons jump to specific sections

---

## Testing

```bash
# Activate environment
source .venv/bin/activate

# Unit tests only (fast, no API calls)
pytest

# Live API tests (costs money)
pytest -m live

# Render tests (requires ffmpeg + Playwright)
pytest -m render

# Full e2e test
pytest -m e2e

# All tests
pytest -m "live or render or e2e"
```

---

## Visual Style

All animations use a clean **infographic style**:

- **Background**: White (#ffffff) with subtle grey plus-sign pattern
- **Text**: CMU Serif for body, system-ui for badges
- **Colors**: Dark grey text (#1f2937), blue accents (#1e40af), white cards
- **Animations**: Simple, professional motion graphics

This is NOT cinematic/movie-style — think educational explainer video.

---

## Animation Library

Available CSS animations (see `docs/ANIMATION_LIBRARY.md`):

| Animation | Effect | Duration |
|-----------|--------|----------|
| `fadeUp` | Fade in + rise from below | 500ms |
| `popIn` | Scale from 80% to 100% with bounce | 300ms |
| `zoomOut` | Zoom out magnify effect | 400ms |
| `slideOutDown` | Slide down and exit | 600ms |
| `slideOutRight` | Slide right and exit | 600ms |
| `panRight` | Ken Burns slow pan | 2500ms |
| `swipe-out` | Swipe left and fade | 500ms |

---

## Timeline JSON Format

The pipeline generates `timeline.json` with this structure:

```json
{
  "duration_ms": 20000,
  "fps": 30,
  "voiceover_segments": [
    {"start_ms": 0, "end_ms": 1200, "text": "Let's say you're working"},
    {"start_ms": 1200, "end_ms": 2800, "text": "at a bulge bracket investment bank"},
    {"start_ms": 2800, "end_ms": 4000, "text": "on Wall Street."}
  ],
  "events": [
    {"t_ms": 0, "op": "layerShow", "target": "intro", "trigger": "Let's"},
    {"t_ms": 0, "op": "classAdd", "target": "title", "value": "fadeUp"},
    {"t_ms": 2800, "op": "textSet", "target": "subtitle", "value": "WALL STREET", "trigger": "Wall Street"},
    {"t_ms": 5000, "op": "layerHide", "target": "intro"}
  ]
}
```

### Event Fields

| Field | Description |
|-------|-------------|
| `t_ms` | Timestamp in milliseconds |
| `op` | Operation to perform |
| `target` | Element ID |
| `value` | CSS class or text content |
| `trigger` | (optional) Spoken word that triggers this animation |

### Operations

| Op | Description |
|----|-------------|
| `classAdd` | Add CSS class to element |
| `classRemove` | Remove CSS class from element |
| `layerShow` | Show element (display: block) |
| `layerHide` | Hide element (display: none) |
| `textSet` | Set element's innerHTML |

### Voiceover Segments

The `voiceover_segments` array maps the audio script to precise timestamps, allowing animations to sync with specific phrases.

---

## Requirements

- **Python 3.10+**
- **ffmpeg** (for video encoding)
- **Playwright Chromium** (for frame capture)
- **OpenRouter API key** (for LLM stages)
- **Cartesia API key** (for TTS)

### Install ffmpeg (Mac)

```bash
brew install ffmpeg
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'agent'"

Reinstall the package:
```bash
pip install -e '.[dev]'
```

### "OPENROUTER_API_KEY not set"

Load your .env file:
```bash
set -a && source .env && set +a
```

### Empty or broken scene.html

Check `runs/<id>/timeline.json` for valid JSON. The LLM sometimes returns malformed output — re-run the pipeline or manually fix the timeline.

### ffmpeg not found

Install ffmpeg:
```bash
brew install ffmpeg  # Mac
sudo apt install ffmpeg  # Ubuntu
```

---

## License

MIT
