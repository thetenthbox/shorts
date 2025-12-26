# 1learner Video Script: IB Model Critique (Full Walkthrough)

**Source audio:** `audio_scripts/audio_script1.md`  
**Target duration:** ~45–55s  
**Backdrop style:** White + grey plus pattern (from `assets/backgrounds/plus-pattern.css`)  
**Animation primitives:** `fadeUp`, `popIn`, `zoomOut`, `slideOutDown`, `slideOutRight`, `panRight`, `swipe-out` (see `docs/ANIMATION_LIBRARY.md`)  

---

## SCENE 1: WALL STREET SETUP (0.0–6.5s)

### Voiceover (audio L1)
> “Let's say you're working at a bulge bracket investment bank on Wall Street… you're not exactly clear what went wrong.”

### Visual
- Start with Wall Street image pan (Ken Burns), then reveal blue panel “IB CLINIC”, then slide to white plus-pattern.

### Animation sequence
1. (0.0s) **Wall Street image** pans right (`panRight`, 2.5s).
2. (2.5s) **Image slides down** to reveal blue panel (`slideOutDown`, 0.6s).
3. (3.2s) Blue panel shows centered title: **IB CLINIC** (already present).
4. (4.0s) **Blue panel slides right** to reveal white plus-pattern (`slideOutRight`, 0.6s).
5. (4.8s) Bullet appears (CMU Serif, 48px):  
   - “• Bulge bracket on Wall Street.” (`fadeUp`, 0.5s)
6. (5.6s) Bullet appears:  
   - “• Senior associate is ripping your model apart.” (`fadeUp`, 0.5s)

---

## SCENE 2: MCQ — “SO WHAT DO YOU DO?” (6.5–15.5s)

### Voiceover (audio L5 + L11 + L15 + L19)
> “So, what do you do? Do you leave it be and apologize… or do you defend your model… or do you try to walk through their logic…”

### Visual
- Clear prior bullets/spreadsheet; show MCQ question + 3 options (A/B/C).

### Animation sequence
1. (6.5s) **Swipe away** prior content (`swipe-out`, 0.5s).
2. (7.1s) Question appears (CMU Serif, 52px):  
   - “So, what do you do?” (`fadeUp`, 0.4s)
3. (7.8s) Option A card pops in (`popIn`, 0.25s):  
   - **A)** Apologize + keep your head down (protect offer)
4. (8.1s) Option B card pops in (`popIn`, 0.25s):  
   - **B)** Defend the model (you’re right)
5. (8.4s) Option C card pops in (`popIn`, 0.25s):  
   - **C)** Walk through their logic (even under time pressure)
6. (9.2s–15.5s) Hold while VO completes.

---

## SCENE 3: REALITY CHECK (15.5–24.0s)

### Voiceover (audio L23 + L25 + L27)
> “Now, let's get something straight… This kind of conflict is going to happen all the time in IB. People are busy, stressed… you're passing work between like 6 different people.”

### Visual
- Same white plus-pattern.
- Replace MCQ with “context cards” showing why conflict happens.
- Minimal, clean: 3 small cards or icons.

### Animation sequence
1. (15.5s) MCQ swipes away (`swipe-out`, 0.5s).
2. (16.2s) Title line fades up (CMU Serif, 52px):  
   - “This conflict is normal in IB.” (`fadeUp`, 0.4s)
3. (16.9s) 3 cards pop in (System UI, 34px) with small labels:
   - “Busy”
   - “Stressed”
   - “Missing context” (`popIn` stagger 0.2s)
4. (18.0s) Add a small “handoff chain” under cards: **6 dots connected by arrows** draws left→right (simple line/arrow animation).

---

## SCENE 4: THE GOAL (24.0–30.0s)

### Voiceover (audio L29–L32)
> “So your goal isn't to ‘win’ the argument. Your goal is to get aligned fast… and ship clean work.”

### Visual
- Big contrast: “WIN” crossed out, replaced by “ALIGN FAST” and “SHIP CLEAN”.

### Animation sequence
1. (24.0s) Context cards slide down + fade out (quick `swipe-out` or `fadeUp` reversed).
2. (24.5s) Word card appears: **WIN** (large, 120px). (`popIn`)
3. (25.1s) Red strike-through line draws across WIN.
4. (25.6s) Two pill badges pop in beneath:
   - “ALIGN FAST”
   - “SHIP CLEAN” (`popIn` stagger 0.2s)

---

## SCENE 5: THE PLAYBOOK — 4 STEPS (30.0–52.0s)

### Voiceover (audio L33–L48)
> “Here's how you wade through it… Ask for the one thing… Then repeat it back… Then you commit to a timeline… And after? Send a quick recap…”

### Visual
- A vertical “checklist” of 4 steps.
- Each step shows a sample quote inside a small rounded rectangle.

### Animation sequence
1. (30.0s) Scene clears to white plus-pattern.
2. (30.3s) Step 1 card slides in (`fadeUp`):
   - **1) Ask for the one thing**
   - Quote bubble: “What’s the biggest issue if we fix it right now?”
3. (35.0s) Step 2 card slides in (`fadeUp`):
   - **2) Repeat it back**
   - Quote bubble: “Got it — so the concern is X, because Y?”
4. (39.5s) Step 3 card slides in (`fadeUp`):
   - **3) Commit to a timeline**
   - Quote bubble: “I’ll fix this, resend, and flag anything else that still looks off.”
5. (45.0s) Step 4 card slides in (`fadeUp`):
   - **4) Send a recap**
   - Subtext: “What changed / why / confirm”

**Optional micro-visuals (to match IB theme):**
- Behind Step 1–2: small “noise” scribbles fade out when “clarity” appears.
- Behind Step 3: a mini timeline bar fills 0→100%.
- Behind Step 4: an “email” icon with 3 bullet lines.

---

## SCENE 6: WRAP + CTA (52.0–58.0s)

### Voiceover (audio L49–L51)
> “Sometimes all it takes is a bit of ego stroking… That's how you handle pressure in IB without getting walked over…”

### Visual
- Summary card with 3 tags + CTA.

### Animation sequence
1. (52.0s) Checklist compresses slightly (scale 0.95) and fades.
2. (52.5s) Summary pops in:
   - “Ask for the one thing.”
   - “Repeat it back.”
   - “Ship clean work.” (`popIn` stagger)
3. (55.0s) CTA line fades up:
   - “Practice IB stress-tests at 1learner.com” (`fadeUp`)
---

## IMPLEMENTATION NOTES (for HTML)

- Use the existing scene structure from `scenes/scene1.html` as a base and extend it.
- Reuse:
  - Plus-pattern backdrop
  - MCQ component (`assets/components/mcq-card.html`)
  - Swipe-out transitions
  - Speed toggle + side nav system
- Add new components as needed:
  - 3 “context cards” row
  - “WIN” crossed out card
  - 4-step playbook checklist

