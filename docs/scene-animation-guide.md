# Scene.html Animation Guide

A comprehensive guide to creating synchronized, polished animations for Shorts.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Core Concepts](#core-concepts)
3. [Timing System](#timing-system)
4. [Working with Audio Timestamps](#working-with-audio-timestamps)
5. [Animation Patterns](#animation-patterns)
6. [CSS Best Practices](#css-best-practices)
7. [Common Pitfalls](#common-pitfalls)
8. [Checklist](#checklist)

---

## Project Structure

```
runs/{short_id}/
├── scene.html          # Main animation file
├── tts_words.json      # Word-level timestamps from TTS
├── timeline.json       # High-level scene timeline
└── refined_timeline.json # Detailed animation cues

templates/
├── scene_playground.html  # Animation catalog/reference
└── assets_*.html          # Asset showcases by category

assets/
├── components/         # UI components (MCQ, toast, etc.)
├── excel/              # Spreadsheet/table assets
├── finance/            # Org charts, tombstones, etc.
├── icons/              # Arrows, emojis, status icons
├── logos/              # Bank logos (PNG)
├── text/               # Title, typewriter, bullets
└── backgrounds/        # Patterns, gradients
```

---

## Core Concepts

### The Animation Container

Every scene uses a fixed 1080×1920 container (9:16 vertical video):

```html
<div class="shorts-container">
  <div class="white-backdrop">
    <!-- All animated elements go here -->
  </div>
</div>
```

```css
.shorts-container {
  width: 1080px;
  height: 1920px;
  position: relative;
  overflow: hidden;
  transform: scale(0.4);  /* Scale down for preview */
  transform-origin: center center;
}
```

### Element States

Every animated element follows this pattern:

1. **Hidden by default** — `opacity: 0` or `display: none`
2. **Shown via JS** — Add `.show` or `.animate` class
3. **Hidden again** — Add `.hide` class or remove element

```css
.my-element {
  opacity: 0;
  transform: translateY(20px);
}
.my-element.show {
  animation: fadeUp 0.4s ease-out forwards;
}
.my-element.hide {
  animation: fadeOut 0.3s ease-out forwards;
}
```

---

## Timing System

### The `at()` and `addDelay()` Pattern

This is the core timing mechanism. It lets you write animations in sequence without manually calculating cumulative offsets.

```javascript
let globalOffset = 0;

function at(ms) {
  return ms + globalOffset;
}

function addDelay(ms) {
  globalOffset += ms;
}
```

### How It Works

```javascript
// Scene 1: Logo appears at 0ms, stays for 3000ms
setTimeout(() => showEl('logo'), at(0));
setTimeout(() => hideEl('logo'), at(3000));
addDelay(3500);  // Move timeline forward (3000 + 500ms gap)

// Scene 2: Now starts at 3500ms automatically
setTimeout(() => showEl('title'), at(0));  // Actually fires at 3500ms
setTimeout(() => hideEl('title'), at(2000));  // Fires at 5500ms
addDelay(2500);

// Scene 3: Starts at 6000ms...
```

### Why This Pattern?

1. **Easy reordering** — Move entire scenes without recalculating times
2. **Easy spacing** — `addDelay()` controls gaps between scenes
3. **Easy debugging** — Each scene's internal timing is relative to 0

---

## Working with Audio Timestamps

### The `tts_words.json` File

TTS generates word-level timing data:

```json
[
  { "word": "Welcome", "start_ms": 0, "end_ms": 320 },
  { "word": "to", "start_ms": 320, "end_ms": 410 },
  { "word": "investment", "start_ms": 410, "end_ms": 890 },
  { "word": "banking", "start_ms": 890, "end_ms": 1350 }
]
```

### Timing Strategy: When to Trigger Animations

| Scenario | Use | Example |
|----------|-----|---------|
| Element appears **as word is spoken** | `start_ms` | Logo pops when "Goldman" starts |
| Element appears **after word finishes** | `end_ms` | MCQ option after "defend?" ends |
| Element appears **before word** (anticipation) | `start_ms - 200` | Build tension |
| Element disappears | Find the word that signals transition | Hide logos when moving to next topic |

### Example: Syncing MCQ Options

```javascript
// From tts_words.json:
// { "word": "apologize", "start_ms": 15557 }
// { "word": "defend", "end_ms": 21625 }
// { "word": "walk", "start_ms": 28832 }

setTimeout(() => showEl('optionA'), at(15557));  // "apologize"
setTimeout(() => showEl('optionB'), at(21625));  // after "defend"
setTimeout(() => showEl('optionC'), at(28832));  // "walk"
```

### Pro Tips

1. **Find trigger words** — Scan the transcript for natural cue points
2. **Use `end_ms` for questions** — Let the question finish before showing the answer
3. **Add breathing room** — Don't stack animations too close; 200-500ms gaps feel natural
4. **Watch for fast speech** — Some words are < 100ms; combine with neighbors

---

## Animation Patterns

### Pattern 1: Pop In (Scale)

Best for: badges, icons, buttons, emphasis

```css
@keyframes popIn {
  0% { opacity: 0; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1); }
}
```

### Pattern 2: Fade Up (Translate Y)

Best for: text blocks, cards, general content

```css
@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
```

### Pattern 3: Slide In (Translate X)

Best for: lists, sequential items, comparison boxes

```css
@keyframes slideInLeft {
  0% { opacity: 0; transform: translateX(-50px); }
  100% { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
  0% { opacity: 0; transform: translateX(50px); }
  100% { opacity: 1; transform: translateX(0); }
}
```

### Pattern 4: Staggered Entrance

Best for: lists, grids, multiple items

```javascript
// Items appear 150ms apart
setTimeout(() => animateEl('item1'), at(0));
setTimeout(() => animateEl('item2'), at(150));
setTimeout(() => animateEl('item3'), at(300));
setTimeout(() => animateEl('item4'), at(450));
```

### Pattern 5: Transform + Move

Best for: element that appears, then repositions

```css
.reality-card {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.6s ease-out;
}

.reality-card.moved-up {
  top: 15%;
  transform: translate(-50%, 0) scale(0.8);
}
```

```javascript
// Card pops in centered, then moves up to make room
setTimeout(() => showEl('realityCard'), at(0));
setTimeout(() => document.getElementById('realityCard').classList.add('moved-up'), at(2000));
```

### Pattern 6: Cross-Out / Strike

Best for: dismissing wrong options, crossing out mistakes

```javascript
function crossOutTable(tableId, crossId) {
  const cross = document.getElementById(crossId);
  cross.style.opacity = '1';
  cross.style.width = '140%';  // Animate from 0 to 140%
}
```

```css
.cross-line {
  position: absolute;
  height: 8px;
  background: #dc2626;
  width: 0;
  transition: width 0.3s ease-out;
  transform: rotate(-15deg);
}
```

---

## CSS Best Practices

### 1. Centering Elements

**Problem:** Animation transforms override centering transforms.

**Solution:** Use keyframes that preserve the centering:

```css
/* BAD - breaks centering */
@keyframes fadeUp {
  0% { transform: translateY(30px); }
  100% { transform: translateY(0); }  /* Lost the -50% */
}

/* GOOD - preserves centering */
@keyframes fadeUpCentered {
  0% { opacity: 0; transform: translate(-50%, -40%); }
  100% { opacity: 1; transform: translate(-50%, -50%); }
}
```

Or wrap in an inner div:

```html
<div id="container" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
  <div id="inner" class="animate-me">Content</div>
</div>
```

### 2. Z-Index Layering

Establish a clear z-index hierarchy:

```css
.background { z-index: 0; }
.content { z-index: 1; }
.overlays { z-index: 2; }
.callouts { z-index: 3; }
.modals { z-index: 10; }
.section-labels { z-index: 100; }
```

### 3. Font Sizing for Video

Text must be **large** for mobile viewing:

| Element | Minimum Size |
|---------|--------------|
| Main title | 60-80px |
| Subtitle | 32-42px |
| Body text | 28-36px |
| Labels | 20-24px |

### 4. Animation Timing Functions

```css
/* Snappy entrance */
animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;

/* Smooth slide */
animation: slideIn 0.4s ease-out forwards;

/* Gentle fade */
animation: fadeIn 0.5s ease-in-out forwards;
```

---

## Common Pitfalls

### 1. Orphaned Elements

**Problem:** Elements shown but never hidden, cluttering the screen.

**Fix:** Every `showEl()` needs a corresponding `hideEl()`:

```javascript
setTimeout(() => showEl('badge'), at(0));
setTimeout(() => hideEl('badge'), at(3000));  // Don't forget this!
```

### 2. Timing Collisions

**Problem:** Two elements animate at the same time, fighting for attention.

**Fix:** Stagger by 200-500ms or use `addDelay()`:

```javascript
// BAD
setTimeout(() => showEl('a'), at(1000));
setTimeout(() => showEl('b'), at(1000));

// GOOD
setTimeout(() => showEl('a'), at(1000));
setTimeout(() => showEl('b'), at(1300));
```

### 3. Fast Animations Getting Clipped

**Problem:** At 30fps rendering, quick animations (< 200ms) can be missed.

**Fix:** Minimum 250ms for important animations. For render, use 60fps:

```bash
shorts --id my_short --render-only --fps 60
```

### 4. Inline Styles Not Reset

**Problem:** On replay, elements have stale inline styles.

**Fix:** Reset in your `__shortsPlayAll()` or reset function:

```javascript
function resetAll() {
  document.querySelectorAll('.animate, .show, .hide').forEach(el => {
    el.classList.remove('animate', 'show', 'hide');
    el.style.cssText = '';  // Clear inline styles
  });
  globalOffset = 0;
}
```

### 5. Transform Conflicts

**Problem:** CSS `transform` property can only have one value; later ones override.

**Fix:** Combine transforms or use wrapper divs:

```css
/* BAD */
.element {
  transform: translate(-50%, -50%);
}
.element.animate {
  transform: scale(1.2);  /* Loses the translate! */
}

/* GOOD */
.element {
  transform: translate(-50%, -50%) scale(1);
}
.element.animate {
  transform: translate(-50%, -50%) scale(1.2);
}
```

---

## Checklist

### Before Starting

- [ ] Audio file exists and is final
- [ ] `tts_words.json` generated with word timestamps
- [ ] Script/transcript reviewed for animation cues
- [ ] Assets identified from `assets/` folder

### During Development

- [ ] All elements hidden by default (opacity: 0)
- [ ] Every `showEl` has a matching `hideEl`
- [ ] Using `at()` / `addDelay()` for timing
- [ ] Animations synced to audio keywords
- [ ] Minimum 250ms between adjacent animations
- [ ] Text large enough (28px+ body, 48px+ titles)
- [ ] Z-index hierarchy clear

### Before Render

- [ ] Test in browser with audio playing
- [ ] Check all elements appear/disappear correctly
- [ ] No overlapping/fighting animations
- [ ] Reset function clears all state
- [ ] Duration matches audio length

### Render Settings

```bash
# Preview (fast)
shorts --id my_short --render-only --fps 30 --duration 30

# Final (quality)
shorts --id my_short --render-only --fps 60
```

---

## Quick Reference

### Helper Functions

```javascript
let globalOffset = 0;
function at(ms) { return ms + globalOffset; }
function addDelay(ms) { globalOffset += ms; }
function showEl(id) { document.getElementById(id).classList.add('show'); }
function hideEl(id) { 
  const el = document.getElementById(id);
  el.classList.remove('show');
  el.classList.add('hide');
}
function animateEl(id, cls = 'animate') { 
  document.getElementById(id).classList.add(cls); 
}
```

### Essential Keyframes

```css
@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes fadeUpCentered {
  0% { opacity: 0; transform: translate(-50%, -40%); }
  100% { opacity: 1; transform: translate(-50%, -50%); }
}

@keyframes popIn {
  0% { opacity: 0; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1); }
}

@keyframes fadeOut {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

@keyframes slideInLeft {
  0% { opacity: 0; transform: translateX(-50px); }
  100% { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
  0% { opacity: 0; transform: translateX(50px); }
  100% { opacity: 1; transform: translateX(0); }
}
```

---

## Example Timeline

```javascript
// ===== SCENE 1: INTRO (0-3s) =====
setTimeout(() => showEl('logo'), at(0));
setTimeout(() => showEl('title'), at(500));
setTimeout(() => hideEl('logo'), at(2500));
setTimeout(() => hideEl('title'), at(3000));
addDelay(3500);

// ===== SCENE 2: QUESTION (3.5s-8s) =====
setTimeout(() => showEl('questionCard'), at(0));
setTimeout(() => animateEl('optionA'), at(1000));
setTimeout(() => animateEl('optionB'), at(1500));
setTimeout(() => animateEl('optionC'), at(2000));
setTimeout(() => hideEl('questionCard'), at(4500));
addDelay(5000);

// ===== SCENE 3: ANSWER (8.5s-12s) =====
// ... continue pattern
```

---

*Last updated: December 2024*

