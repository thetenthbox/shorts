from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL_SCRIPT = "openai/gpt-5-chat"
OPENROUTER_MODEL_HTML = "anthropic/claude-sonnet-4.5"

# Aliases for backward compat
OPENROUTER_SCRIPT_MODEL = OPENROUTER_MODEL_SCRIPT
OPENROUTER_HTML_MODEL = OPENROUTER_MODEL_HTML

CARTESIA_VOICE_ID = "0ad65e7f-006c-47cf-bd31-52279d487913"
CARTESIA_VOICE_ID_DEFAULT = CARTESIA_VOICE_ID


def get_openrouter_api_key() -> Optional[str]:
    """Get OpenRouter API key from environment."""
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    return key if key else None


def get_cartesia_api_key() -> Optional[str]:
    """Get Cartesia API key from environment."""
    key = os.getenv("CARTESIA_API_KEY", "").strip()
    return key if key else None


def get_cartesia_voice_id() -> str:
    """Get Cartesia voice ID from environment or default."""
    return os.getenv("CARTESIA_VOICE_ID", CARTESIA_VOICE_ID).strip()


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


