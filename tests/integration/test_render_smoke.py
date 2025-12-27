import shutil
import subprocess
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from agent.renderer import ffmpeg_encode_cmd, ffmpeg_mux_wav_cmd, ffprobe_resolution


@pytest.mark.render
def test_render_smoke(tmp_path: Path):
    # Hard requirement (per your preference)
    assert shutil.which("ffmpeg"), "ffmpeg not found on PATH"
    assert shutil.which("ffprobe"), "ffprobe not found on PATH"

    scene_path = Path(__file__).resolve().parents[2] / "scenes" / "scene1.html"
    assert scene_path.exists()

    frames_dir = tmp_path / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    fps = 10
    n_frames = 10

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(scene_path.as_uri())
        page.wait_for_timeout(500)
        for i in range(n_frames):
            page.screenshot(path=str(frames_dir / f"frame_{i:06d}.png"))
        browser.close()

    out_mp4 = tmp_path / "out.mp4"
    cmd = ffmpeg_encode_cmd(fps=fps, frame_glob=str(frames_dir / "frame_%06d.png"), out_mp4=out_mp4)
    subprocess.check_call(cmd)

    assert out_mp4.exists()
    assert ffprobe_resolution(mp4_path=out_mp4) == "1080x1920"


