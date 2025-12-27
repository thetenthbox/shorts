# 1learner Animation Library

A catalog of CSS animations for Shorts production.

---

## ⚠️ CRITICAL: Transform Conflicts

**CSS `transform` is NOT additive — it completely REPLACES any existing transform.**

If an element uses `transform: translateX(-50%)` for horizontal centering, applying a standard animation will BREAK the centering:

```css
/* ❌ BAD - This breaks centering! */
.centered-element {
  left: 50%;
  transform: translateX(-50%);  /* Centering */
}

@keyframes fadeUp {
  0% { transform: translateY(20px); }   /* Overwrites translateX(-50%)! */
  100% { transform: translateY(0); }    /* Element jumps to left edge */
}
```

**Solution: Use CENTERED variants that preserve the centering transform:**

```css
/* ✅ GOOD - Preserves centering */
@keyframes fadeUpCenteredX {
  0% { opacity: 0; transform: translateX(-50%) translateY(20px); }
  100% { opacity: 1; transform: translateX(-50%) translateY(0); }
}

@keyframes fadeUpCentered {
  0% { opacity: 0; transform: translate(-50%, -50%) translateY(20px); }
  100% { opacity: 1; transform: translate(-50%, -50%) translateY(0); }
}

@keyframes popInCenteredX {
  0% { opacity: 0; transform: translateX(-50%) scale(0.8); }
  100% { opacity: 1; transform: translateX(-50%) scale(1); }
}

@keyframes popInCentered {
  0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}
```

### When to use which variant:

| Element Centering | Use Animation |
|-------------------|---------------|
| No transform centering | `fadeUp`, `popIn` (standard) |
| `transform: translateX(-50%)` | `fadeUpCenteredX`, `popInCenteredX` |
| `transform: translate(-50%, -50%)` | `fadeUpCentered`, `popInCentered` |

---

## Reset & Display Rules

### Resetting Elements

```javascript
// ❌ BAD - 'none' blocks future animations
el.style.animation = 'none';

// ✅ GOOD - Empty string allows new animations
el.style.animation = '';
el.style.transform = '';  // Also clear inline transform
```

### Show Before Animate

```javascript
// ❌ BAD - Animation runs while element is hidden
el.style.animation = 'fadeUp 0.4s ease-out forwards';

// ✅ GOOD - Show first, then animate
el.style.display = 'block';
el.style.animation = 'fadeUp 0.4s ease-out forwards';
```

### Hide After FadeOut

```javascript
// ❌ BAD - Instant hide causes flash
el.style.display = 'none';

// ✅ GOOD - Animate out, then hide
el.style.animation = 'fadeOut 0.4s ease-out forwards';
setTimeout(() => {
  el.style.display = 'none';
}, 400);  // Wait for animation to complete
```

---

## Quick Reference

| Animation | Effect | Duration | Use Case |
|-----------|--------|----------|----------|
| `fadeUp` | Rise + fade in | 0.4-0.5s | Text, cards, general elements |
| `fadeUpCenteredX` | Rise + fade (preserves X centering) | 0.4-0.5s | Centered titles, subtitles |
| `fadeUpCentered` | Rise + fade (preserves XY centering) | 0.4-0.5s | Centered overlays, modals |
| `popIn` | Scale bounce | 0.25s | MCQ options, buttons |
| `popInCenteredX` | Scale bounce (preserves X centering) | 0.25s | Centered badges |
| `popInCentered` | Scale bounce (preserves XY centering) | 0.25s | Centered cards |
| `zoomOut` | Magnify from small | 0.5s | Callout cells, highlights |
| `slideOutDown` | Exit downward | 0.6s | Image/panel reveals |
| `slideOutRight` | Exit rightward | 0.6s | Panel transitions |
| `panRight` | Ken Burns pan | 2.5s | Background images |
| `swipe-out` | Slide left + fade | 0.5s | Clear screen transitions |
| `fadeOut` | Fade to invisible | 0.3-0.4s | Exit animations |

---

## Animation Definitions

### fadeUp

Elements rise from below while fading in. The most versatile animation.

```css
@keyframes fadeUp {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Usage:**
```css
.element {
  opacity: 0;
  transform: translateY(20px);
}

.element.animate {
  animation: fadeUp 0.5s ease-out forwards;
}
```

**Best for:** Bullets, paragraphs, cards, spreadsheets

---

### popIn

Scale bounce effect for interactive elements.

```css
@keyframes popIn {
  0% {
    opacity: 0;
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
```

**Usage:**
```css
.element {
  opacity: 0;
  transform: scale(0.95);
}

.element.animate {
  animation: popIn 0.25s ease-out forwards;
}
```

**Best for:** MCQ options, buttons, badges

---

### zoomOut

Magnifying glass effect—element zooms from small to full size with bounce.

```css
@keyframes zoomOut {
  0% {
    opacity: 0;
    transform: scale(0.5);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
```

**Usage:**
```css
.callout {
  opacity: 0;
  transform: scale(0.5);
  transform-origin: left center;
}

.callout.animate {
  animation: zoomOut 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
```

**Best for:** Callout cells, highlighted values, zoom reveals

**Note:** The `cubic-bezier(0.34, 1.56, 0.64, 1)` easing adds a slight overshoot/bounce.

---

### slideOutDown

Panel slides down to reveal content beneath.

```css
@keyframes slideOutDown {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(100%);
  }
}
```

**Usage:**
```css
.panel.animate-exit {
  animation: slideOutDown 0.6s ease-in-out forwards;
}
```

**Best for:** Image reveals, layer transitions

---

### slideOutRight

Panel slides right to reveal content beneath.

```css
@keyframes slideOutRight {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(100%);
  }
}
```

**Usage:**
```css
.panel.animate-exit {
  animation: slideOutRight 0.6s ease-in-out forwards;
}
```

**Best for:** Blue panel transitions, horizontal reveals

---

### panRight (Ken Burns)

Slow pan and zoom for background images.

```css
@keyframes panRight {
  0% {
    transform: scale(1.3) translateX(0);
  }
  100% {
    transform: scale(1.4) translateX(-15%);
  }
}
```

**Usage:**
```css
.background-img {
  width: 200%; /* Extra width for pan room */
  transform: scale(1.3);
  filter: brightness(0.8);
}

.background-img.animate-pan {
  animation: panRight 2.5s ease-in-out forwards;
}
```

**Best for:** Opening shots, cinematic backgrounds

**Note:** Image needs to be wider than container (200%) to allow pan room.

---

### fadeOut

Simple fade to invisible for exit animations.

```css
@keyframes fadeOut {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
```

**Usage:**
```javascript
el.style.animation = 'fadeOut 0.4s ease-out forwards';
setTimeout(() => {
  el.style.display = 'none';
}, 400);
```

**Best for:** Smooth exits before hiding elements

---

### Centered Animation Variants

For elements using `transform` for centering:

```css
/* For elements with transform: translateX(-50%) */
@keyframes fadeUpCenteredX {
  0% { opacity: 0; transform: translateX(-50%) translateY(20px); }
  100% { opacity: 1; transform: translateX(-50%) translateY(0); }
}

@keyframes popInCenteredX {
  0% { opacity: 0; transform: translateX(-50%) scale(0.8); }
  100% { opacity: 1; transform: translateX(-50%) scale(1); }
}

/* For elements with transform: translate(-50%, -50%) */
@keyframes fadeUpCentered {
  0% { opacity: 0; transform: translate(-50%, calc(-50% + 20px)); }
  100% { opacity: 1; transform: translate(-50%, -50%); }
}

@keyframes popInCentered {
  0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

@keyframes shakeContainerCentered {
  0%, 100% { transform: translate(-50%, -50%); }
  25% { transform: translate(calc(-50% - 5px), -50%); }
  75% { transform: translate(calc(-50% + 5px), -50%); }
}
```

---

### swipe-out (Transition Class)

Not a keyframe—uses CSS transition for smoother control.

```css
.element {
  transition: transform 0.5s ease-in-out, opacity 0.5s ease-in-out;
}

.element.swipe-out {
  transform: translateX(-100%);
  opacity: 0;
}
```

**Usage:**
```javascript
element.classList.add('swipe-out');
```

**Best for:** Clearing screen before new section, mass element removal

---

## Easing Reference

| Easing | Value | Effect |
|--------|-------|--------|
| Standard | `ease-out` | Fast start, slow end |
| Smooth | `ease-in-out` | Slow start and end |
| Bounce | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Overshoot and settle |

---

## Timing Guidelines

| Element Type | Recommended Duration |
|--------------|---------------------|
| Text appearing | 0.4-0.5s |
| Cards/options | 0.25-0.3s |
| Panel transitions | 0.5-0.6s |
| Background pans | 2-3s |
| Stagger between items | 0.2-0.5s |

---

## Stagger Pattern

For sequential element reveals:

```javascript
// Elements appear 400ms apart
setTimeout(() => el1.classList.add('animate'), 0);
setTimeout(() => el2.classList.add('animate'), 400);
setTimeout(() => el3.classList.add('animate'), 800);
```

Or use CSS animation-delay:

```css
.item:nth-child(1) { animation-delay: 0s; }
.item:nth-child(2) { animation-delay: 0.2s; }
.item:nth-child(3) { animation-delay: 0.4s; }
```

