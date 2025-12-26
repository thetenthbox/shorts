# 1learner Short Script: The IB Stress Test

**Topic:** Managing Arguments (How to handle aggressive critique in banking)  
**Duration:** ~12 seconds (current build)  
**Status:** Complete - Scene 1 + MCQ implemented

---

## SCENE 1: THE HOOK (0-9.6s)

### Section 1: Wall Street Pan (0-2.5s)

**Visual:**
- Wall Street image fills screen, zoomed to 130% scale
- Slow pan right (Ken Burns effect) - zooms to 140% while translating left
- Dark overlay (brightness 0.8) for cinematic feel

**Animation sequence:**
1. (0.0s) Image starts panning with `panRight 2.5s ease-in-out`

---

### Section 2: IB Clinic Reveal (2.5-4.0s)

**Visual:**
- Wall Street image slides DOWN
- Reveals blue backdrop (#1e3a5f)
- White text centered: **"IB CLINIC"** (140px, 800 weight, uppercase)

**Animation sequence:**
1. (2.5s) Image container `slideOutDown 0.6s ease-in-out`

---

### Section 3: White Backdrop + Bullets (4.0-6.4s)

**Visual:**
- Blue panel slides RIGHT
- Reveals white backdrop with grey plus/grid pattern
- Two bullet points animate in (CMU Serif font, 48px)

**Animation sequence:**
1. (4.0s) Blue panel `slideOutRight 0.6s ease-in-out`
2. (4.8s) Bullet 1 `fadeUp 0.5s ease-out`
3. (5.6s) Bullet 2 `fadeUp 0.5s ease-out`

**Bullet 1:**
> • You're at a Bulge Bracket firm. An Associate is aggressively shredding your valuation.

**Bullet 2:**
> • He says "The model is completely wrong."

---

### Section 4: DCF Spreadsheet (6.4s)

**Visual:**
- Excel-style DCF table fades in
- 6 rows × 6 columns (headers: 2024-2028)
- Row labels: Revenue, EBITDA, FCF, Discount Factor, PV of FCF, Terminal Value
- All data cells show "—" (dashes)

**Animation sequence:**
1. (6.4s) Spreadsheet `fadeUp 0.5s ease-out`

---

### Section 5: Parameter Callouts (7.2-8.8s)

**Visual:**
- Three callout cells zoom out (magnifying glass effect)
- Blue styling (#1e40af) with box shadow

**Animation sequence:**
1. (7.2s) WACC | 9.5% - `zoomOut 0.5s cubic-bezier`
2. (8.0s) Exit Multiple | 8.0x - `zoomOut 0.5s cubic-bezier`
3. (8.8s) Growth Rate | 3.0% - `zoomOut 0.5s cubic-bezier`

---

## SCENE 2: MCQ DECISION MOMENT (9.6-12s)

### Transition (9.6s)

**Visual:**
- All content swipes left and fades out
- Clean white backdrop with plus pattern remains

**Animation sequence:**
1. (9.6s) Text content, spreadsheet, callouts all `swipe-out` (translateX -100%, opacity 0)

---

### Question (10.2s)

**Visual:**
- Question text fades up (CMU Serif, 52px, #1f2937)

**Animation sequence:**
1. (10.2s) Question `fadeUp 0.4s ease-out`

**Question:**
> What would you do if you were pressed by a more senior colleague?

---

### Options (10.6-11.2s)

**Visual:**
- Four MCQ cards stack vertically
- White cards with light grey border, subtle shadow
- Options pop in with stagger

**Animation sequence:**
1. (10.6s) Option A `popIn 0.25s ease-out`
2. (10.8s) Option B `popIn 0.25s ease-out`
3. (11.0s) Option C `popIn 0.25s ease-out`
4. (11.2s) Option D `popIn 0.25s ease-out`

**Options:**
- **A)** Apologize and agree immediately to end the tension.
- **B)** Defend every assumption at once (talk faster, talk louder).
- **C)** Pause, isolate the exact critique, then walk through the logic calmly.
- **D)** Deflect: "That's just how the template works" and move on.

---

## TECHNICAL SPECS

| Element | Specification |
|---------|---------------|
| Dimensions | 1080 x 1920 (9:16) |
| Preview scale | 0.4x |
| Background colors | #1e3a5f (blue panel), #fff (white backdrop) |
| Fonts | CMU Serif (bullets, question), Consolas (spreadsheet), System UI (options) |
| Accent color | #1e40af (callouts, option labels) |

---

## TIMELINE SUMMARY

| Time | Event |
|------|-------|
| 0.0s | Wall Street pan starts |
| 2.5s | Image slides down → blue panel |
| 4.0s | Blue panel slides right → white backdrop |
| 4.8s | Bullet 1 appears |
| 5.6s | Bullet 2 appears |
| 6.4s | Spreadsheet fades in |
| 7.2s | WACC callout zooms |
| 8.0s | Exit Multiple callout zooms |
| 8.8s | Growth Rate callout zooms |
| 9.6s | Content swipes out |
| 10.2s | MCQ question appears |
| 10.6s | Option A pops in |
| 10.8s | Option B pops in |
| 11.0s | Option C pops in |
| 11.2s | Option D pops in |

---

## FULL VOICEOVER SCRIPT

> You're at a Bulge Bracket firm. An Associate is aggressively shredding your valuation. He says "The model is completely wrong." What would you do if you were pressed by a more senior colleague?

---

## NOTES

- Answer: C is correct (Pause, isolate, walk through logic)
- Scene file: `scenes/scene1.html`
- Image asset: `image.png` (Wall Street background)
- Speed toggle available for preview (1x/3x)
- Side navigation buttons for section jumping

