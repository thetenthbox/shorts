from pathlib import Path

from agent.renderer import ffmpeg_encode_cmd, ffmpeg_mux_wav_cmd


def test_ffmpeg_encode_cmd():
    cmd = ffmpeg_encode_cmd(fps=30, frame_glob="frame_%06d.png", out_mp4=Path("out.mp4"))
    assert cmd[0] == "ffmpeg"
    assert "-framerate" in cmd
    assert "30" in cmd
    assert "out.mp4" in cmd[-1]


def test_ffmpeg_mux_cmd():
    cmd = ffmpeg_mux_wav_cmd(in_mp4=Path("a.mp4"), in_wav=Path("b.wav"), out_mp4=Path("c.mp4"))
    assert cmd[0] == "ffmpeg"
    assert "a.mp4" in cmd
    assert "b.wav" in cmd
    assert cmd[-1] == "c.mp4"


