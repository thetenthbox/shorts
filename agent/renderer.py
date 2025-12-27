from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class RenderPaths:
    frames_dir: Path
    mp4_path: Path


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


