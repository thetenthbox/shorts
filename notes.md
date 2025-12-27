## Edge Cases & Failure Modes

### 1. **Audio-Visual Sync Issues**

| Issue | Cause | Example |
|-------|-------|---------|
| Animation fires too early | TTS speaks faster than estimated 400ms/word | Text appears before narrator says it |
| Animation fires too late | TTS speaks slower, pauses between sentences | Viewer waits on blank screen |
| Word boundaries mismatch | Cartesia splits words differently than expected | "Wall Street" as 1 word vs 2 |
| Silence gaps | TTS adds natural pauses we didn't account for | 500ms gaps between sentences |
| Speaking rate varies | Emphasis on certain words changes timing | "YOU" stretched to 800ms |

### 2. **HTML/CSS Animation Issues**

| Issue | Cause | Example |
|-------|-------|---------|
| Animation overlap | Two elements animate at same position | Text appears behind spreadsheet |
| Z-index wars | Layers stack incorrectly | Exit animation shows under new layer |
| Animation not visible | Element hidden before animation starts | `layerShow` missing before `classAdd` |
| Animation stuck | CSS animation doesn't reset | Replaying causes no motion |
| Easing feels wrong | Wrong curve for the motion type | Slam effect uses `ease-in-out` instead of `ease-out` |
| Jank/stuttering | Too many simultaneous animations | 5 elements animate at once |
| Font not loaded | Web font fails to load in time | CMU Serif shows as Arial |
| Image not loaded | Image URL 404s or slow CDN | Blank white rectangle |

### 3. **Layout/Positioning Issues**

| Issue | Cause | Example |
|-------|-------|---------|
| Text overflow | Long text doesn't fit container | "Investment Banking" wraps mid-word |
| Text clipping | Container too small | Bottom of letters cut off |
| Mobile aspect ratio | 1080x1920 renders differently | Elements off-screen on some devices |
| Absolute positioning drift | Different font metrics | Text 10px lower than expected |
| Element collision | Two elements occupy same space | Option cards overlap |

### 4. **Timeline/Sequencing Issues**

| Issue | Cause | Example |
|-------|-------|---------|
| Events out of order | LLM generates non-chronological `t_ms` | Hide before show |
| Missing hide events | Layer never hidden after exit | Old content still visible |
| Orphan elements | Element ID in timeline doesn't exist in HTML | `target: "bullet3"` but no `#bullet3` |
| Duration mismatch | Timeline `duration_ms` doesn't match actual video | Video cuts off or has dead time |
| Gap between scenes | Transition timing leaves blank frames | 200ms of nothing |

### 5. **LLM Generation Issues**

| Issue | Cause | Example |
|-------|-------|---------|
| Invalid JSON | Unterminated strings, missing commas | Parser crash |
| Missing required fields | LLM omits `t_ms` or `target` | Runtime error |
| Hallucinated element IDs | LLM invents `#heroSection` | Element not found |
| Inconsistent specs | Stage B2 says "72px" but Stage C uses 48px | Visual mismatch |
| Wrong animation name | LLM uses `fadeIn` instead of `fadeUp` | No animation plays |
| Token limit truncation | Long script gets cut off | Last scenes missing |
| Markdown in JSON | LLM wraps JSON in ```json``` | Parser fails |

### 6. **TTS Issues**

| Issue | Cause | Example |
|-------|-------|---------|
| Pronunciation errors | Abbreviations, numbers, names | "IB" pronounced "ib" |
| Unnatural pacing | No control over emphasis | Monotone delivery |
| Audio clipping | Volume spikes | Distortion on loud words |
| Wrong voice | Voice ID invalid or deprecated | Different character |
| Sample rate mismatch | 44100 vs 48000 Hz | Audio pitch shift |
| Timestamp drift | Cumulative timing errors | 2 second drift by end |

### 7. **Rendering Issues**

| Issue | Cause | Example |
|-------|-------|---------|
| Frame drops | Playwright can't keep up | Choppy motion |
| Wrong resolution | Canvas not exactly 1080x1920 | Blurry output |
| Color space mismatch | RGB vs sRGB vs BT.709 | Washed out colors |
| FFmpeg encoding artifacts | Wrong codec settings | Blocking in dark areas |
| Audio desync after mux | Video/audio different durations | Drift over time |
| Black frames | Animation hasn't started yet | First 100ms blank |

### 8. **Content/Creative Issues**

| Issue | Cause | Example |
|-------|-------|---------|
| Visuals don't match voiceover | Semantic mismatch | Saying "spreadsheet" showing MCQ |
| Wrong emphasis | Animation on wrong word | "WALL" emphasized, not "Street" |
| Too much happening | Cognitive overload | 3 things animate simultaneously |
| Boring visuals | Not enough motion | Static text for 5 seconds |
| Inconsistent style | Mixed fonts, colors | Scene 1 blue, Scene 2 purple |
| Jarring transitions | Abrupt scene changes | Hard cut with no transition |

---

## Suggested Fixes / Safeguards

1. **Use actual TTS timestamps** — Generate audio FIRST, then use Cartesia's word timestamps to drive animation timing
2. **Validation layer** — Check all element IDs in timeline exist in HTML
3. **Schema enforcement** — Validate timeline JSON against strict schema
4. **Preview mode** — Browser-based preview with audio before rendering
5. **Retry logic** — Re-prompt LLM on invalid JSON
6. **Timing buffer** — Add 200ms padding between events
7. **Fallback animations** — Default fade if specified animation missing
8. **Font preloading** — Load fonts before first frame capture