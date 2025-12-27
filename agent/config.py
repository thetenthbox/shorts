from __future__ import annotations

import os
from dataclasses import dataclass


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_SCRIPT_MODEL = "openai/gpt-5-chat"
OPENROUTER_HTML_MODEL = "anthropic/claude-sonnet-4.5"

CARTESIA_VOICE_ID_DEFAULT = "0ad65e7f-006c-47cf-bd31-52279d487913"


@dataclass(frozen=True)
class Config:
    openrouter_api_key: str
    cartesia_api_key: str
    cartesia_voice_id: str = CARTESIA_VOICE_ID_DEFAULT
    openrouter_base_url: str = OPENROUTER_BASE_URL

    @staticmethod
    def from_env() -> "Config":
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        cartesia_api_key = os.getenv("CARTESIA_API_KEY", "").strip()
        cartesia_voice_id = os.getenv("CARTESIA_VOICE_ID", CARTESIA_VOICE_ID_DEFAULT).strip()

        if not openrouter_api_key:
            raise ValueError("Missing OPENROUTER_API_KEY")
        if not cartesia_api_key:
            raise ValueError("Missing CARTESIA_API_KEY")
        if not cartesia_voice_id:
            raise ValueError("Missing CARTESIA_VOICE_ID")

        return Config(
            openrouter_api_key=openrouter_api_key,
            cartesia_api_key=cartesia_api_key,
            cartesia_voice_id=cartesia_voice_id,
        )


