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
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Audio Script   │ -> │  Storyboard     │ -> │  Scene Builder  │ -> │  TTS            │ -> │  Render         │
│  (markdown)     │    │  (GPT-5)        │    │  (Sonnet 4.5)   │    │  (Cartesia)     │    │  (Playwright)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
     input              timeline.json         scene.html              voiceover.wav         final.mp4
```

### Pipeline Stages

| Stage | Model/Tool | Input | Output |
|-------|------------|-------|--------|
| **B: Storyboard** | OpenRouter (GPT-5) | audio_script.md | timeline.json, video_script.md |
| **C: Scene Builder** | OpenRouter (Sonnet 4.5) | timeline.json + templates | scene.html |
| **D: TTS** | Cartesia Sonic 3 | audio_script text | voiceover.wav |
| **E: Render** | Playwright + ffmpeg | scene.html + wav | final.mp4 |

---

## CLI Reference

```bash
shorts --id <run_id> --audio <path> [options]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `--id` | Unique identifier for this run (used for output filenames) |
| `--audio` | Path to audio script markdown file |

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--duration` | 60 | Target video duration in seconds |
| `--skip-tts` | false | Skip voiceover generation |
| `--skip-render` | false | Skip Playwright/ffmpeg rendering |

### Examples

```bash
# Full pipeline (20 second video)
shorts --id demo --audio audio_scripts/audio_script1.md --duration 20

# Generate scripts + HTML only (no TTS, no render)
shorts --id demo --audio audio_scripts/audio_script1.md --skip-tts --skip-render

# Generate scripts + HTML + TTS (no render)
shorts --id demo --audio audio_scripts/audio_script1.md --skip-render
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
├── scripts/                  # Video scripts (timed animation plans)
│   └── video_script1.md
│
├── scenes/                   # Runnable HTML scenes (manual builds)
│   ├── scene1.html
│   └── ib_model_critique.html
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
│       ├── audio_script.md
│       ├── timeline.json
│       ├── video_script.md
│       ├── scene.html
│       ├── scene_spec.json
│       ├── frames/
│       ├── video.mp4
│       └── final.mp4
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

Create `scripts/my_script.md` with timed animation events.

### 3. Build HTML Scene

Copy `templates/base.html` to `scenes/my_scene.html` and add your content.

### 4. Preview in Browser

Open `scenes/my_scene.html` in Chrome:
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

### Fix timing in scene.html (re-render only)

```python
from pathlib import Path
from agent.renderer import render_mp4

render_mp4(
    html_path=Path('runs/my_run/scene.html'),
    output_dir=Path('runs/my_run_fixed'),
    duration_ms=20000,
    fps=30,
    wav_path=Path('renders/my_run.wav'),
)
```

### Regenerate scene from edited timeline.json

```python
import json
from pathlib import Path
from agent.openrouter_client import OpenRouterClient
from agent.config import get_openrouter_api_key
from agent.stages import stage_scene_builder, load_base_html, load_animation_library, load_component_library

shorts = Path('.')
timeline = json.loads((shorts / 'runs/my_run/timeline.json').read_text())
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

## Animation Library

Available CSS animations (see `docs/ANIMATION_LIBRARY.md`):

| Animation | Effect |
|-----------|--------|
| `fadeUp` | Fade in from below |
| `popIn` | Pop/scale in |
| `zoomOut` | Zoom out effect |
| `slideOutDown` | Slide down and exit |
| `slideOutRight` | Slide right and exit |
| `panRight` | Ken Burns pan effect |
| `swipe-out` | Swipe left and fade |

---

## Timeline JSON Format

The pipeline generates `timeline.json` with this structure:

```json
{
  "duration_ms": 20000,
  "fps": 30,
  "events": [
    {"t_ms": 0, "op": "layerShow", "target": "intro"},
    {"t_ms": 0, "op": "classAdd", "target": "title", "value": "fadeUp"},
    {"t_ms": 2000, "op": "textSet", "target": "subtitle", "value": "New text"},
    {"t_ms": 5000, "op": "layerHide", "target": "intro"}
  ]
}
```

### Operations

| Op | Description |
|----|-------------|
| `classAdd` | Add CSS class to element |
| `classRemove` | Remove CSS class from element |
| `layerShow` | Show element (display: block) |
| `layerHide` | Hide element (display: none) |
| `textSet` | Set element's text content |

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
