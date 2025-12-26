# 1learner Animation Library

A catalog of CSS animations for Shorts production.

---

## Quick Reference

| Animation | Effect | Duration | Use Case |
|-----------|--------|----------|----------|
| `fadeUp` | Rise + fade in | 0.4-0.5s | Text, cards, general elements |
| `popIn` | Scale bounce | 0.25s | MCQ options, buttons |
| `zoomOut` | Magnify from small | 0.5s | Callout cells, highlights |
| `slideOutDown` | Exit downward | 0.6s | Image/panel reveals |
| `slideOutRight` | Exit rightward | 0.6s | Panel transitions |
| `panRight` | Ken Burns pan | 2.5s | Background images |
| `swipe-out` | Slide left + fade | 0.5s | Clear screen transitions |

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

