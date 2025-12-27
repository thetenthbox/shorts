# 1learner Component Library

Reusable HTML/CSS components for Shorts production.

---

## ⚠️ Centering Best Practices

**Problem**: Using `transform` for centering conflicts with animations (see ANIMATION_LIBRARY.md).

### Option 1: Flexbox Centering (RECOMMENDED)

No transform conflicts — works with all standard animations:

```css
.centered-container {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.centered-content {
  /* Can use fadeUp, popIn directly */
  animation: fadeUp 0.4s ease-out forwards;
}
```

### Option 2: Transform Centering (use with CENTERED animations)

If you must use transform centering, use matching animation variants:

```css
/* Element with translateX(-50%) centering */
.title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}
/* Use: fadeUpCenteredX, popInCenteredX */

/* Element with translate(-50%, -50%) centering */
.modal {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
}
/* Use: fadeUpCentered, popInCentered */
```

### Centering Reference Table

| Centering Method | Animation to Use |
|------------------|------------------|
| Flexbox (`display: flex`) | Standard: `fadeUp`, `popIn` |
| `transform: translateX(-50%)` | `fadeUpCenteredX`, `popInCenteredX` |
| `transform: translate(-50%, -50%)` | `fadeUpCentered`, `popInCentered` |

---

## Brand Colors

```css
/* 1learner Brand */
--blue-primary: #1e3a5f;    /* Dark blue - panels, buttons */
--blue-accent: #1e40af;     /* Bright blue - callouts, highlights */
--text-dark: #1f2937;       /* Headings */
--text-muted: #374151;      /* Body text */
--text-light: #9ca3af;      /* Secondary text */
--bg-white: #ffffff;        /* Main backdrop */
--border-light: #d1d5db;    /* Borders, dividers */
```

---

## Fonts

```css
@import url('https://fonts.cdnfonts.com/css/cmu-serif');

/* Primary - Body text, bullets */
font-family: 'CMU Serif', Georgia, serif;

/* Secondary - UI elements */
font-family: system-ui, -apple-system, sans-serif;

/* Monospace - Data, code, Excel */
font-family: 'Consolas', 'Courier New', monospace;
```

---

## Layouts

### Shorts Container

The base wrapper for all content. 1080x1920 (9:16 aspect ratio), scaled to 40% for preview.

```html
<div class="shorts-container">
  <!-- Content layers go here -->
</div>
```

```css
.shorts-container {
  width: 1080px;
  height: 1920px;
  position: relative;
  overflow: hidden;
  transform: scale(0.4);
  transform-origin: center center;
}
```

---

### White Backdrop with Plus Pattern

Clean white background with subtle grid pattern.

```html
<div class="white-backdrop">
  <div class="plus-pattern"></div>
  <!-- Content here -->
</div>
```

```css
.white-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fff;
  z-index: 1;
}

.plus-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(#d1d5db 1px, transparent 1px),
    linear-gradient(90deg, #d1d5db 1px, transparent 1px);
  background-size: 80px 80px;
  opacity: 0.5;
}

.plus-pattern::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(circle, #9ca3af 3px, transparent 3px);
  background-size: 80px 80px;
  background-position: 40px 40px;
}
```

---

### Blue Panel Overlay

Full-screen blue panel for titles/transitions.

```html
<div class="blue-panel" id="bluePanel">
  <div class="title">YOUR TITLE</div>
</div>
```

```css
.blue-panel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #1e3a5f;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
}

.title {
  font-size: 140px;
  font-weight: 800;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 10px;
}

.blue-panel.animate-exit {
  animation: slideOutRight 0.6s ease-in-out forwards;
}
```

---

## Text Components

### Bullet Points

CMU Serif styled bullet list.

```html
<div class="text-content">
  <div class="bullet" id="bullet1">
    <span class="bullet-dot">•</span>
    <span class="bullet-text">Your text here.</span>
  </div>
  <div class="bullet" id="bullet2">
    <span class="bullet-dot">•</span>
    <span class="bullet-text">Another point with <span class="quote-text">"quoted text"</span>.</span>
  </div>
</div>
```

```css
.text-content {
  position: absolute;
  top: 120px;
  left: 80px;
  right: 80px;
  z-index: 2;
  font-family: 'CMU Serif', Georgia, serif;
  transition: transform 0.5s ease-in-out, opacity 0.5s ease-in-out;
}

.bullet {
  display: flex;
  gap: 24px;
  margin-bottom: 50px;
  opacity: 0;
  transform: translateY(20px);
}

.bullet.animate {
  animation: fadeUp 0.5s ease-out forwards;
}

.bullet-dot {
  font-size: 48px;
  color: #374151;
  line-height: 1.4;
}

.bullet-text {
  font-size: 48px;
  color: #1f2937;
  line-height: 1.4;
}

.quote-text {
  font-style: italic;
}

.text-content.swipe-out {
  transform: translateX(-100%);
  opacity: 0;
}
```

---

## Data Visualizations

### DCF Spreadsheet

Excel-style table for financial data.

```html
<div class="excel-container" id="spreadsheet">
  <table class="spreadsheet">
    <tr>
      <td class="header"></td>
      <td class="header">2024</td>
      <td class="header">2025</td>
      <td class="header">2026</td>
      <td class="header">2027</td>
      <td class="header">2028</td>
    </tr>
    <tr>
      <td class="label-col">Revenue</td>
      <td class="dash">—</td>
      <td class="dash">—</td>
      <td class="dash">—</td>
      <td class="dash">—</td>
      <td class="dash">—</td>
    </tr>
    <!-- More rows... -->
  </table>
</div>
```

```css
.excel-container {
  position: absolute;
  top: 680px;
  left: 40px;
  right: 40px;
  z-index: 2;
  opacity: 0;
  transform: translateY(20px);
  transition: transform 0.5s ease-in-out, opacity 0.5s ease-in-out;
}

.excel-container.animate {
  animation: fadeUp 0.5s ease-out forwards;
}

.spreadsheet {
  background: #fff;
  border: 2px solid #6b7280;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 22px;
  border-collapse: collapse;
  width: 100%;
}

.spreadsheet td {
  border: 1px solid #d1d5db;
  padding: 12px 16px;
  color: #374151;
  text-align: right;
  min-width: 90px;
}

.spreadsheet td.label-col {
  text-align: left;
  background: #f9fafb;
  font-weight: 500;
  min-width: 200px;
}

.spreadsheet td.header {
  background: #e5e7eb;
  font-weight: 600;
  text-align: center;
}

.spreadsheet td.dash {
  color: #9ca3af;
}

.excel-container.swipe-out {
  transform: translateX(-100%) !important;
  opacity: 0 !important;
}
```

---

### Callout Cells

Zoom-out callout for highlighting values.

```html
<div class="callout-container">
  <div class="callout callout-1" id="callout1">
    <div class="callout-label">WACC</div>
    <div class="callout-value">9.5%</div>
  </div>
  <div class="callout callout-2" id="callout2">
    <div class="callout-label">Exit Multiple</div>
    <div class="callout-value">8.0x</div>
  </div>
  <div class="callout callout-3" id="callout3">
    <div class="callout-label">Growth Rate</div>
    <div class="callout-value">3.0%</div>
  </div>
</div>
```

```css
.callout-container {
  position: absolute;
  top: 680px;
  left: 40px;
  right: 40px;
  z-index: 3;
  pointer-events: none;
  transition: transform 0.5s ease-in-out, opacity 0.5s ease-in-out;
}

.callout {
  position: absolute;
  display: flex;
  background: #fff;
  border: 3px solid #1e40af;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.2);
  opacity: 0;
  transform: scale(0.5);
  transform-origin: left center;
}

.callout.animate {
  animation: zoomOut 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

.callout-label {
  background: #1e40af;
  color: #fff;
  padding: 20px 28px;
  font-family: 'Consolas', monospace;
  font-size: 36px;
  font-weight: 600;
}

.callout-value {
  background: #fff;
  color: #1e40af;
  padding: 20px 28px;
  font-family: 'Consolas', monospace;
  font-size: 36px;
  font-weight: 700;
}

/* Position variants */
.callout-1 { top: 60px; left: 50px; }
.callout-2 { top: 200px; left: 120px; }
.callout-3 { top: 340px; left: 80px; }

.callout-container.swipe-out {
  transform: translateX(-100%);
  opacity: 0;
}
```

---

## Interactive Elements

### MCQ Question + Options

Multiple choice question layout.

```html
<div class="mcq-container" id="mcqContainer">
  <div class="mcq-question" id="mcqQuestion">
    Your question text here?
  </div>
  <div class="mcq-options">
    <div class="mcq-option" id="optionA">
      <span class="mcq-label">A)</span>
      <span>First option text.</span>
    </div>
    <div class="mcq-option" id="optionB">
      <span class="mcq-label">B)</span>
      <span>Second option text.</span>
    </div>
    <div class="mcq-option" id="optionC">
      <span class="mcq-label">C)</span>
      <span>Third option text.</span>
    </div>
    <div class="mcq-option" id="optionD">
      <span class="mcq-label">D)</span>
      <span>Fourth option text.</span>
    </div>
  </div>
</div>
```

```css
.mcq-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
  z-index: 4;
  opacity: 0;
  pointer-events: none;
}

.mcq-container.active {
  opacity: 1;
  pointer-events: auto;
}

.mcq-question {
  font-family: 'CMU Serif', Georgia, serif;
  font-size: 52px;
  color: #1f2937;
  text-align: center;
  max-width: 900px;
  margin-bottom: 80px;
  line-height: 1.3;
  opacity: 0;
  transform: translateY(8px);
}

.mcq-question.animate {
  animation: fadeUp 0.4s ease-out forwards;
}

.mcq-options {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: 900px;
}

.mcq-option {
  background: #fff;
  border: 2px solid #d1d5db;
  border-radius: 12px;
  padding: 28px 36px;
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 36px;
  color: #374151;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  opacity: 0;
  transform: scale(0.95);
  cursor: pointer;
  transition: all 0.2s;
}

.mcq-option:hover {
  border-color: #1e40af;
  box-shadow: 0 4px 12px rgba(30,64,175,0.15);
}

.mcq-option.animate {
  animation: popIn 0.25s ease-out forwards;
}

.mcq-label {
  font-weight: 700;
  color: #1e40af;
  margin-right: 12px;
}
```

---

## Controls

### Bottom Control Bar

```html
<div class="controls">
  <button class="btn" onclick="replay()">▶ Play All</button>
  <button class="btn" id="speedBtn" onclick="toggleSpeed()">1x</button>
</div>
```

```css
.controls {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  z-index: 100;
}

.btn {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  background: #1e3a5f;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.btn:hover {
  transform: scale(1.05);
}
```

---

### Side Navigation

```html
<div class="side-nav">
  <button class="side-btn" onclick="jumpTo(1)">1. Section Name</button>
  <button class="side-btn" onclick="jumpTo(2)">2. Section Name</button>
  <!-- More sections... -->
</div>
```

```css
.side-nav {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 100;
}

.side-btn {
  width: 140px;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  background: #374151;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s;
}

.side-btn:hover {
  background: #1e3a5f;
}

.side-btn.active {
  background: #1e40af;
}
```

---

## Image Components

### Ken Burns Background Image

```html
<div class="wallstreet-container" id="wallstreetContainer">
  <img src="image.png" alt="Background" class="wallstreet-img" id="wallstreetImg">
</div>
```

```css
.wallstreet-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 10;
}

.wallstreet-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 200%;
  height: 100%;
  object-fit: cover;
  object-position: left center;
  transform: scale(1.3);
  transform-origin: center center;
  filter: brightness(0.8);
}

.wallstreet-img.animate-pan {
  animation: panRight 2.5s ease-in-out forwards;
}

.wallstreet-container.animate-exit {
  animation: slideOutDown 0.6s ease-in-out forwards;
}
```

