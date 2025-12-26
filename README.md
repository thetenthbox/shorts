# 1learner Shorts (HTML Animation System)

This repo is a lightweight workflow for producing YouTube Shorts using **HTML/CSS/JS** animations (no video editor required).

## What’s in here

- `docs/PRODUCTION_GUIDE.md`: end-to-end pipeline (audio script → video script → HTML scene → MP4 recording)
- `docs/ANIMATION_LIBRARY.md`: reusable animation patterns (`fadeUp`, `popIn`, `zoomOut`, `panRight`, `swipe-out`, etc.)
- `docs/COMPONENT_LIBRARY.md`: reusable UI blocks (bullets, MCQ cards, spreadsheets, callouts, controls)

## Folder structure

- `audio_scripts/`: raw voiceover scripts (input)
- `scripts/`: video scripts (timed animation + VO mapping)
  - `scripts/video_script1.md`: built from `audio_scripts/audio_script1.md`
- `scenes/`: runnable HTML scenes
  - `scenes/scene1.html`: original prototype scene
  - `scenes/ib_model_critique.html`: expanded build from `scripts/video_script1.md`
- `templates/`: starting points for new work
  - `templates/base.html`: boilerplate scene template (controls, nav, common styles)
  - `templates/script-template.md`: script template
- `assets/`: copy/paste components and style snippets (plus background, Excel tables, MCQ, callouts)
- `image.png`: example Wall Street background (used by scenes)

## How to run a scene

Open any file in `scenes/` in your browser (Chrome recommended).

- Use **▶ Play All** to run the full timeline
- Use the **1x / 3x** toggle to preview faster
- Use the right-side buttons to jump to sections

## How to export an MP4 (Mac)

1. Open the scene in Chrome
2. Set speed to **1x**
3. QuickTime Player → File → New Screen Recording
4. Select the animation area (1080×1920 container) and record
5. Press **▶ Play All**
6. Stop recording → Export 1080p

## Suggested workflow

1. Write voiceover in `audio_scripts/`
2. Convert to timed video plan in `scripts/`
3. Implement scene in `scenes/` by copying `templates/base.html` or an existing scene
4. Record MP4

## Create a GitHub repo + push

This folder is already initialized as a git repo. To publish it:

```bash
cd Shorts
git add .
git commit -m "Initial Shorts animation system"

# Create an empty GitHub repo, then:
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```


