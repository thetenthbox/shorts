from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import httpx


@dataclass(frozen=True)
class CartesiaTTS:
    """Cartesia TTS client.

    Note: Cartesia API details can vary by version. We keep base_url configurable.
    """

    api_key: str
    base_url: str = "https://api.cartesia.ai"

    def synthesize_wav(
        self,
        *,
        text: str,
        voice_id: str,
        out_wav_path: Path,
        model: str = "sonic-3",
        sample_rate_hz: int = 44100,
    ) -> Path:
        out_wav_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"{self.base_url}/tts/bytes"
        headers = {
            "Cartesia-Version": "2025-04-16",
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model_id": model,
            "transcript": text,
            "voice": {"mode": "id", "id": voice_id},
            "output_format": {
                "container": "wav",
                "encoding": "pcm_s16le",
                "sample_rate": sample_rate_hz,
            },
            "speed": "normal",
            "generation_config": {"speed": 1, "volume": 1},
        }

        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            out_wav_path.write_bytes(resp.content)

        return out_wav_path


