# 1learner Shorts Production Guide

## Overview

This guide outlines the 4-stage pipeline for creating animated YouTube Shorts for 1learner.

---

## Pipeline Stages

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. AUDIO       │ -> │  2. VIDEO       │ -> │  3. HTML        │ -> │  4. RECORDING   │
│     SCRIPT      │    │     SCRIPT      │    │     SCENE       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
     Topic/idea         Shot-by-shot          Animated HTML          Final MP4
     Voiceover text     Timing + visuals      Using components       Screen capture
```

---

## Stage 1: Audio Script

**Input:** Topic or concept  
**Output:** Raw voiceover text with timing estimates

### Format
```markdown
# [Topic Title]

## Voiceover Script

[Opening hook - 3-5 seconds]
"Attention-grabbing statement or question."

[Setup - 5-8 seconds]
"Context and problem statement."

[Main content - 20-30 seconds]
"Step-by-step explanation or narrative."

[CTA - 3-5 seconds]
"Call to action with 1learner mention."

## Estimated Duration: XX seconds
```

### Tips
- Keep total duration under 60 seconds (ideal: 40-50s)
- Front-load the hook in first 3 seconds
- Write conversationally—this will be spoken
- Include natural pauses for visual beats

---

## Stage 2: Video Script

**Input:** Audio script  
**Output:** Shot-by-shot breakdown with animations, timing markers, visual descriptions

### Format
Use the template at `templates/script-template.md`

### Key Elements

1. **Scene Headers** - Include timing range
   ```markdown
   ## SCENE 2: THE QUESTION (6-8s)
   ```

2. **Visual Description** - What appears on screen
   ```markdown
   ### Visual
   - **Background:** White backdrop with plus pattern
   - **Elements:** Two bullet points, CMU Serif font
   ```

3. **Animation Sequence** - Numbered steps with timestamps
   ```markdown
   ### Animation sequence:
   1. (4.8s) First bullet fades up
   2. (5.6s) Second bullet fades up
   3. (6.4s) Spreadsheet appears
   ```

4. **Voiceover Sync** - Quote the audio with timing
   ```markdown
   ### Voiceover
   > "You're at a Bulge Bracket firm..."
   ```

---

## Stage 3: HTML Implementation

**Input:** Video script  
**Output:** Animated HTML file using component library

### Process

1. **Copy base template**
   ```bash
   cp templates/base.html scenes/scene-[name].html
   ```

2. **Add content layers** - Reference `docs/COMPONENT_LIBRARY.md`
   - Background patterns
   - Text content
   - Data visualizations
   - Interactive elements

3. **Wire up animations** - Reference `docs/ANIMATION_LIBRARY.md`
   - Add `.animate` classes
   - Set up timeline in `animate()` function
   - Configure `jumpTo()` sections

4. **Test with controls**
   - Use side nav to jump between sections
   - Use speed toggle for quick preview
   - Verify timing matches script

### File Naming
```
scenes/
├── scene1-ib-stress-test.html
├── scene2-dcf-basics.html
└── scene3-lbo-walkthrough.html
```

---

## Stage 4: Recording

**Input:** Completed HTML scene  
**Output:** MP4 video file

### QuickTime Method (Mac)

1. Open HTML file in Chrome
2. Click speed toggle to **1x** (normal speed)
3. Open **QuickTime Player** → File → New Screen Recording
4. Click dropdown → select recording area (draw around white container)
5. Start recording
6. Click **▶ Play All** in browser
7. Wait for animation to complete
8. Stop recording
9. File → Export → 1080p

### Tips
- Record at 1x speed for final output
- Use 3x speed only for previewing
- Ensure no browser UI is captured
- Export at highest quality

---

## Quality Checklist

Before recording, verify:

- [ ] All animations play smoothly
- [ ] Text is readable (check font sizes)
- [ ] Timing matches voiceover script
- [ ] No elements cut off at edges
- [ ] Speed toggle set to 1x
- [ ] Side nav hidden or cropped out

---

## Directory Structure

```
Shorts/
├── docs/
│   ├── PRODUCTION_GUIDE.md      # This file
│   ├── ANIMATION_LIBRARY.md     # CSS animations catalog
│   └── COMPONENT_LIBRARY.md     # Reusable HTML/CSS
├── templates/
│   ├── base.html                # Starting template
│   └── script-template.md       # Script format
├── assets/
│   ├── backgrounds/             # SVG patterns
│   ├── excel/                   # Table components
│   └── components/              # Reusable snippets
├── scripts/
│   └── script1.md               # Video scripts
└── scenes/
    └── scene1.html              # Built scenes
```

