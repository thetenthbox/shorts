# 1learner Shorts

**Simple HTML animation → MP4 pipeline for YouTube Shorts.**

Create vertical videos (1080×1920) with synchronized voiceover. You write the HTML animations, the tool handles TTS and rendering.

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

# 3. Set up API key
echo "CARTESIA_API_KEY=your_cartesia_key" > .env

# 4. Generate TTS
set -a && source .env && set +a
shorts tts --id my_short --audio audio_scripts/my_script.md

# 5. Create scene.html manually (with timestamps from tts_words.json)
# ... edit runs/my_short/scene.html ...

# 6. Render MP4
shorts render --id my_short
```

**Outputs:**
- `renders/my_short.mp4` — final video with audio
- `renders/my_short.wav` — voiceover audio
- `runs/my_short/tts_words.json` — word-level timestamps

---

## Workflow

```
┌─────────────────┐     ┌───────────────┐     ┌─────────────────┐
│ audio_script.md │────▶│  shorts tts   │────▶│  tts_words.json │
└─────────────────┘     └───────────────┘     │  + WAV file     │
                                              └─────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐                           ┌─────────────────┐
│  scene.html     │◀──────── You create ──────│  Use timestamps │
│  (animations)   │         manually          │  for timing     │
└─────────────────┘                           └─────────────────┘
        │
        ▼
┌───────────────┐     ┌─────────────────┐
│ shorts render │────▶│  final.mp4      │
└───────────────┘     └─────────────────┘
```

1. **Write audio script** — what the voiceover will say
2. **Run TTS** — get WAV audio + word-level timestamps
3. **Create scene.html** — build animations using the timestamps for sync
4. **Render** — capture frames and encode to MP4 with audio

---

## CLI Reference

### Generate TTS

```bash
shorts tts --id <run_id> --audio <path>
```

Generates voiceover audio and word-level timestamps.

**Outputs:**
- `renders/<run_id>.wav` — audio file
- `runs/<run_id>/tts_words.json` — word timestamps
- `runs/<run_id>/audio_script.md` — copy of input script

### Render MP4

```bash
shorts render --id <run_id> [options]
```

Renders `scene.html` to MP4, optionally muxing with audio.

| Option | Default | Description |
|--------|---------|-------------|
| `--duration` | 60 | Minimum duration in seconds |
| `--fps` | 30 | Frames per second |
| `--debug` | on | Show timer + current word overlay |
| `--no-debug` | — | Disable debug overlay |

**Requires:**
- `runs/<run_id>/scene.html` — your animation file
- `renders/<run_id>.wav` — audio (optional, for muxing)

**Outputs:**
- `renders/<run_id>.mp4` — final video
- `runs/<run_id>/frames/` — captured PNGs

### Full Pipeline

```bash
shorts run --id <run_id> --audio <path> [options]
```

Runs TTS first, then render (if scene.html exists).

---

## Project Structure

```
Shorts/
├── agent/                    # Python pipeline code
│   ├── cli.py                # CLI entry point
│   ├── cartesia_tts.py       # Cartesia TTS client
│   ├── renderer.py           # Playwright + ffmpeg
│   └── debug_overlay.py      # Debug overlay injection
│
├── audio_scripts/            # Input: voiceover scripts
│   └── my_script.md
│
├── templates/                # Starting points
│   └── base.html             # Boilerplate HTML template
│
├── assets/                   # Reusable components
│   ├── backgrounds/
│   ├── components/
│   └── excel/
│
├── docs/                     # Documentation
│   ├── ANIMATION_LIBRARY.md
│   └── COMPONENT_LIBRARY.md
│
├── runs/                     # Run outputs (gitignored)
│   └── <run_id>/
│       ├── audio_script.md   # Input (copied)
│       ├── tts_words.json    # Word timestamps
│       ├── scene.html        # YOUR animation (create manually)
│       ├── frames/           # Captured PNGs
│       └── final.mp4         # Video + audio
│
├── renders/                  # Final outputs (gitignored)
│   ├── <run_id>.mp4
│   └── <run_id>.wav
│
├── .env                      # API keys (gitignored)
├── pyproject.toml
└── README.md
```

---

## Word Timestamps Format

The `tts_words.json` file contains word-level timing:

```json
[
  {"word": "Let's", "start_ms": 0, "end_ms": 180},
  {"word": "say", "start_ms": 180, "end_ms": 340},
  {"word": "you're", "start_ms": 340, "end_ms": 520},
  {"word": "working", "start_ms": 520, "end_ms": 780},
  {"word": "at", "start_ms": 820, "end_ms": 920},
  {"word": "a", "start_ms": 920, "end_ms": 980},
  {"word": "bank.", "start_ms": 980, "end_ms": 1200}
]
```

Use these timestamps to sync your animations in `scene.html`:

```javascript
// Show title when "working" is spoken (520ms)
setTimeout(() => {
  document.getElementById('title').classList.add('fadeUp');
}, 520);

// Show next element when "bank" is spoken (980ms)
setTimeout(() => {
  document.getElementById('subtitle').classList.add('popIn');
}, 980);
```

---

## Scene HTML Structure

Your `scene.html` should follow this pattern:

```html
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=1080, height=1920">
  <style>
    .shorts-container {
      width: 1080px;
      height: 1920px;
      position: relative;
      background: #fff;
    }
    /* Your animations */
    .fadeUp { animation: fadeUp 0.5s ease-out forwards; }
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="shorts-container">
    <!-- Your content here -->
    <h1 id="title" style="opacity:0;">Title</h1>
  </div>
  
  <script>
    window.__shortsPlayAll = function() {
      // Trigger animations based on tts_words.json timestamps
      setTimeout(() => {
        document.getElementById('title').classList.add('fadeUp');
      }, 520); // "working" starts at 520ms
    };
  </script>
</body>
</html>
```

**Key requirements:**
- Container class: `.shorts-container` (1080×1920)
- Play function: `window.__shortsPlayAll()` — called by renderer to start animation
- Use `setTimeout` with timestamps from `tts_words.json`

---

## Animation Library

Common CSS animations (copy into your scene.html):

| Animation | Effect | Duration |
|-----------|--------|----------|
| `fadeUp` | Fade in + rise from below | 500ms |
| `popIn` | Scale from 80% with bounce | 300ms |
| `slideOutDown` | Slide down and exit | 600ms |
| `swipe-out` | Swipe left and fade | 500ms |

See `docs/ANIMATION_LIBRARY.md` for full list with CSS code.

---

## Configuration

### Environment Variables

Create `.env` in project root:

```bash
CARTESIA_API_KEY=sk_car_...
```

### Voice ID

Default voice: `0ad65e7f-006c-47cf-bd31-52279d487913`

To use a different voice, modify `CARTESIA_VOICE_ID` in `agent/cli.py`.

---

## Requirements

- **Python 3.10+**
- **ffmpeg** — for video encoding
- **Playwright Chromium** — for frame capture
- **Cartesia API key** — for TTS

### Install ffmpeg

```bash
brew install ffmpeg      # Mac
sudo apt install ffmpeg  # Ubuntu
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'agent'"

```bash
pip install -e '.[dev]'
```

### "CARTESIA_API_KEY not set"

```bash
set -a && source .env && set +a
```

### Animation timing is off

Check that your `setTimeout` delays match the timestamps in `tts_words.json`.

### ffmpeg not found

```bash
brew install ffmpeg
```

---

## License

MIT
