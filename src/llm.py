from __future__ import annotations

"""Shared OpenAI client cho enrichment (M5)."""

import os, sys, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, GENERATION_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        # SDK tự retry 429/5xx/timeout với backoff → không cần vòng retry riêng.
        _client = OpenAI(api_key=OPENAI_API_KEY, max_retries=6, timeout=60)
    return _client


def chat(messages: list[dict], json_mode: bool = False) -> str | None:
    """Gọi chat completion. Trả về None nếu không có key; raise nếu SDK hết retry."""
    if not OPENAI_API_KEY:
        return None
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    resp = _get_client().chat.completions.create(model=GENERATION_MODEL, messages=messages, **kwargs)
    return (resp.choices[0].message.content or "").strip()


def parse_json(raw: str | None) -> dict:
    """Parse JSON từ output LLM (chịu được ```json fences). Trả về {} nếu hỏng."""
    import json
    if not raw:
        return {}
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            return {}
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
    return data if isinstance(data, dict) else {}
