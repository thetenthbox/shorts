import os
import wave
from pathlib import Path

import pytest

from agent.cartesia_tts import CartesiaTTS


@pytest.mark.live
def test_cartesia_live_wav(tmp_path: Path):
    api_key = os.getenv("CARTESIA_API_KEY", "").strip()
    voice_id = os.getenv("CARTESIA_VOICE_ID", "").strip()
    base_url = os.getenv("CARTESIA_BASE_URL", "https://api.cartesia.ai").strip()
    if not api_key:
        pytest.skip("CARTESIA_API_KEY not set")
    if not voice_id:
        pytest.skip("CARTESIA_VOICE_ID not set")

    out = tmp_path / "out.wav"
    tts = CartesiaTTS(api_key=api_key, base_url=base_url)
    tts.synthesize_wav(text="Test.", voice_id=voice_id, out_wav_path=out)

    assert out.exists()
    assert out.stat().st_size > 1000

    with wave.open(str(out), "rb") as wf:
        assert wf.getnframes() > 0
        assert wf.getframerate() > 0

