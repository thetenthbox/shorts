import os
import pytest

from agent.openrouter_client import OpenRouterClient
from agent.config import OPENROUTER_SCRIPT_MODEL


@pytest.mark.live
def test_openrouter_live_minimal():
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY not set")

    client = OpenRouterClient(api_key=api_key)
    resp = client.chat(
        model=OPENROUTER_SCRIPT_MODEL,
        messages=[
            {"role": "system", "content": "Return valid JSON only."},
            {"role": "user", "content": "Return a JSON object with keys: ok (boolean), model (string)."},
        ],
        temperature=0.0,
        max_tokens=50,
        response_format={"type": "json_object"},
    )
    assert "choices" in resp
    assert resp["choices"]


