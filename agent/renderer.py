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
    """Capture frames from HTML animation using Playwright.
    
    Returns the number of frames captured.
    """
    from playwright.sync_api import sync_playwright
    
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    frame_interval_ms = 1000 / fps
    total_frames = int((duration_ms / 1000) * fps) + 1
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        
        # Load HTML file
        page.goto(f"file://{html_path.resolve()}")
        page.wait_for_load_state("networkidle")
        
        # Start animation via __shortsPlayAll if it exists
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
            # Many scenes visually scale the container for desktop preview (e.g., transform: scale(0.4)).
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

        # Capture frames
        for i in range(total_frames):
            frame_path = frames_dir / f"frame_{i:06d}.png"
            if use_locator:
                locator.first.screenshot(path=str(frame_path))
            else:
                page.screenshot(path=str(frame_path))
            time.sleep(frame_interval_ms / 1000)
        
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


