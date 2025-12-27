import os
import pytest

from agent.config import (
    CARTESIA_VOICE_ID_DEFAULT,
    OPENROUTER_HTML_MODEL,
    OPENROUTER_SCRIPT_MODEL,
    Config,
)


def test_models_fixed():
    assert OPENROUTER_SCRIPT_MODEL == "openai/gpt-5-chat"
    assert OPENROUTER_HTML_MODEL == "anthropic/claude-sonnet-4.5"


def test_config_from_env_requires_keys(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("CARTESIA_API_KEY", raising=False)
    with pytest.raises(ValueError):
        Config.from_env()


def test_config_from_env_loads(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "ok")
    monkeypatch.setenv("CARTESIA_API_KEY", "ok2")
    monkeypatch.delenv("CARTESIA_VOICE_ID", raising=False)
    cfg = Config.from_env()
    assert cfg.cartesia_voice_id == CARTESIA_VOICE_ID_DEFAULT


