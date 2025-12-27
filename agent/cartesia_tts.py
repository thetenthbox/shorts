from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx


@dataclass
class WordTimestamp:
    word: str
    start_ms: int
    end_ms: int


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

    def synthesize_with_timestamps(
        self,
        *,
        text: str,
        voice_id: str,
        out_wav_path: Path,
        model: str = "sonic-3",
        sample_rate_hz: int = 44100,
    ) -> List[WordTimestamp]:
        """Synthesize audio and return word-level timestamps.
        
        Uses the SSE endpoint with add_timestamps=true.
        Returns list of WordTimestamp objects.
        """
        out_wav_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"{self.base_url}/tts/sse"
        headers = {
            "Cartesia-Version": "2025-04-16",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model_id": model,
            "transcript": text,
            "voice": {"mode": "id", "id": voice_id},
            "output_format": {
                "container": "raw",
                "encoding": "pcm_s16le",
                "sample_rate": sample_rate_hz,
            },
            "add_timestamps": True,
            "generation_config": {"speed": 1, "volume": 1},
        }

        audio_chunks: List[bytes] = []
        timestamps: List[WordTimestamp] = []

        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if not data_str:
                        continue
                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    
                    # Audio chunk
                    if "data" in event:
                        import base64
                        audio_chunks.append(base64.b64decode(event["data"]))
                    
                    # Timestamp event (parallel arrays: words, start, end)
                    if "word_timestamps" in event:
                        wt = event["word_timestamps"]
                        words = wt.get("words", [])
                        starts = wt.get("start", [])
                        ends = wt.get("end", [])
                        for i, word in enumerate(words):
                            timestamps.append(WordTimestamp(
                                word=word,
                                start_ms=int(starts[i] * 1000) if i < len(starts) else 0,
                                end_ms=int(ends[i] * 1000) if i < len(ends) else 0,
                            ))

        # Write WAV file
        audio_data = b"".join(audio_chunks)
        self._write_wav(out_wav_path, audio_data, sample_rate_hz)

        return timestamps

    def _write_wav(self, path: Path, pcm_data: bytes, sample_rate: int) -> None:
        """Write raw PCM data to WAV file."""
        import struct
        
        num_channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        data_size = len(pcm_data)
        
        with open(path, "wb") as f:
            # RIFF header
            f.write(b"RIFF")
            f.write(struct.pack("<I", 36 + data_size))
            f.write(b"WAVE")
            # fmt chunk
            f.write(b"fmt ")
            f.write(struct.pack("<I", 16))  # chunk size
            f.write(struct.pack("<H", 1))   # PCM format
            f.write(struct.pack("<H", num_channels))
            f.write(struct.pack("<I", sample_rate))
            f.write(struct.pack("<I", byte_rate))
            f.write(struct.pack("<H", block_align))
            f.write(struct.pack("<H", bits_per_sample))
            # data chunk
            f.write(b"data")
            f.write(struct.pack("<I", data_size))
            f.write(pcm_data)


