from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class RenderPaths:
    frames_dir: Path
    mp4_path: Path


@dataclass(frozen=True)
class RenderResult:
    frames_dir: Path
    frame_count: int
    mp4_path: Path
    final_mp4_path: Optional[Path]  # After audio mux


def ffmpeg_encode_cmd(*, fps: int, frame_glob: str, out_mp4: Path) -> List[str]:
    return [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        frame_glob,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(out_mp4),
    ]


def ffmpeg_mux_wav_cmd(*, in_mp4: Path, in_wav: Path, out_mp4: Path) -> List[str]:
    return [
        "ffmpeg",
        "-y",
        "-i",
        str(in_mp4),
        "-i",
        str(in_wav),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(out_mp4),
    ]


def ffprobe_resolution(*, mp4_path: Path) -> str:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=p=0:s=x",
        str(mp4_path),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return out


def capture_frames_playwright(
    *,
    html_path: Path,
    frames_dir: Path,
    duration_ms: int,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920,
    selector: str = ".shorts-container",
) -> int:
    """Capture frames from HTML animation using Playwright with deterministic timing.
    
    Uses Web Animations API to pause and seek all animations to exact timestamps,
    ensuring frame-perfect capture regardless of browser speed.
    
    Returns the number of frames captured.
    """
    from playwright.sync_api import sync_playwright
    
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    frame_interval_ms = 1000 / fps
    total_frames = int((duration_ms / 1000) * fps) + 1
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        
        # Set render mode flag BEFORE page scripts run (prevents auto-play on load)
        page.add_init_script("window.__RENDER_MODE__ = true;")
        
        # Load HTML file
        page.goto(f"file://{html_path.resolve()}")
        page.wait_for_load_state("networkidle")
        
        # Inject frame-stepping controller that works with CSS animations, setTimeout, AND requestAnimationFrame
        page.evaluate("""
            // Virtual time state
            window.__virtualTime = 0;
            window.__lastSeekTime = 0;
            window.__timers = [];
            window.__timerIdCounter = 1;
            window.__rafCallbacks = new Map();
            window.__rafIdCounter = 1;
            
            // Override setTimeout to use virtual time
            const __originalSetTimeout = window.setTimeout;
            window.setTimeout = (callback, delay, ...args) => {
                const id = window.__timerIdCounter++;
                window.__timers.push({
                    id,
                    callback,
                    triggerTime: window.__virtualTime + (delay || 0),
                    args
                });
                return id;
            };
            
            // Override clearTimeout
            const __originalClearTimeout = window.clearTimeout;
            window.clearTimeout = (id) => {
                window.__timers = window.__timers.filter(t => t.id !== id);
            };
            
            // Override requestAnimationFrame
            const __originalRAF = window.requestAnimationFrame;
            window.requestAnimationFrame = (callback) => {
                const id = window.__rafIdCounter++;
                window.__rafCallbacks.set(id, callback);
                return id;
            };
            
            // Override cancelAnimationFrame
            const __originalCAF = window.cancelAnimationFrame;
            window.cancelAnimationFrame = (id) => {
                window.__rafCallbacks.delete(id);
            };
            
            // Override Date.now and performance.now
            const __originalDateNow = Date.now;
            const __originalPerfNow = performance.now.bind(performance);
            Date.now = () => window.__virtualTime;
            performance.now = () => window.__virtualTime;
            
            // Function to seek to exact time
            window.__seekToTime = (targetMs) => {
                // Process time in small steps to fire timers in order
                const stepSize = 1; // 1ms steps for accuracy
                
                while (window.__virtualTime < targetMs) {
                    const nextTime = Math.min(window.__virtualTime + stepSize, targetMs);
                    window.__virtualTime = nextTime;
                    
                    // Fire all timers that should have triggered
                    const dueTimers = window.__timers.filter(t => t.triggerTime <= nextTime);
                    window.__timers = window.__timers.filter(t => t.triggerTime > nextTime);
                    dueTimers.sort((a, b) => a.triggerTime - b.triggerTime);
                    dueTimers.forEach(t => {
                        try { t.callback(...t.args); } catch(e) { console.error(e); }
                    });
                }
                
                // Fire RAF callbacks once per seek (simulating one frame)
                const rafCbs = Array.from(window.__rafCallbacks.values());
                window.__rafCallbacks.clear();
                rafCbs.forEach(cb => {
                    try { cb(window.__virtualTime); } catch(e) { console.error(e); }
                });
                
                // Seek all CSS animations using Web Animations API
                document.getAnimations().forEach(anim => {
                    try {
                        // Only seek if animation is in a seekable state
                        if (anim.playState !== 'idle') {
                            anim.currentTime = targetMs;
                        }
                    } catch(e) {
                        // Some animations can't be seeked (e.g., not yet started) - skip them
                    }
                });
                
                window.__lastSeekTime = targetMs;
            };
        """)
        
        # Start animation via __shortsPlayAll if it exists
        # This triggers the setTimeout chain that shows/hides elements
        has_play_fn = page.evaluate("typeof window.__shortsPlayAll === 'function'")
        if has_play_fn:
            page.evaluate("window.__shortsPlayAll()")
        else:
            # Fallback: try clicking Play All button
            play_btn = page.locator("text=Play All")
            if play_btn.count() > 0:
                play_btn.first.click()
        
        # Prefer capturing only the animation container (not the whole DOM/page UI).
        # Fall back to full-page screenshots if selector isn't found.
        locator = page.locator(selector)
        use_locator = locator.count() > 0
        if use_locator:
            # Ensure stable bounding box (wait for it to exist)
            locator.first.wait_for(state="visible", timeout=10_000)
            # Ensure the container is captured at the true 1080x1920 size.
            page.evaluate(
                """
                (sel) => {
                  const el = document.querySelector(sel);
                  if (!el) return;
                  el.style.transform = 'none';
                  el.style.transformOrigin = 'top left';
                }
                """,
                selector,
            )

        # Capture frames by stepping through time
        # We advance virtual time (for setTimeout/RAF) and let CSS animations run in real-time
        last_virtual_time = 0
        for i in range(total_frames):
            frame_path = frames_dir / f"frame_{i:06d}.png"
            target_time_ms = i * frame_interval_ms
            
            # Advance virtual time to fire setTimeout callbacks (which add animation classes)
            page.evaluate(f"window.__seekToTime({target_time_ms})")
            
            # Let CSS animations catch up by sleeping the delta in real-time
            # This ensures CSS transitions/animations progress correctly
            delta_ms = target_time_ms - last_virtual_time
            if delta_ms > 0:
                time.sleep(delta_ms / 1000)
            last_virtual_time = target_time_ms
            
            if use_locator:
                locator.first.screenshot(path=str(frame_path))
            else:
                page.screenshot(path=str(frame_path))
        
        browser.close()
    
    return total_frames


def render_mp4(
    *,
    html_path: Path,
    output_dir: Path,
    duration_ms: int,
    fps: int = 30,
    wav_path: Optional[Path] = None,
) -> RenderResult:
    """Full render pipeline: capture frames -> encode MP4 -> optionally mux audio."""
    
    frames_dir = output_dir / "frames"
    mp4_path = output_dir / "video.mp4"
    
    # Step 1: Capture frames
    frame_count = capture_frames_playwright(
        html_path=html_path,
        frames_dir=frames_dir,
        duration_ms=duration_ms,
        fps=fps,
    )
    
    # Step 2: Encode MP4
    frame_glob = str(frames_dir / "frame_%06d.png")
    encode_cmd = ffmpeg_encode_cmd(fps=fps, frame_glob=frame_glob, out_mp4=mp4_path)
    subprocess.run(encode_cmd, check=True, capture_output=True)
    
    # Step 3: Mux audio if provided
    final_mp4_path: Optional[Path] = None
    if wav_path and wav_path.exists():
        final_mp4_path = output_dir / "final.mp4"
        mux_cmd = ffmpeg_mux_wav_cmd(in_mp4=mp4_path, in_wav=wav_path, out_mp4=final_mp4_path)
        subprocess.run(mux_cmd, check=True, capture_output=True)
    
    return RenderResult(
        frames_dir=frames_dir,
        frame_count=frame_count,
        mp4_path=mp4_path,
        final_mp4_path=final_mp4_path,
    )


