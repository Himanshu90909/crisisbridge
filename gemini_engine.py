"""Optional Gemini integration for CrisisBridge.

The app remains runnable without a key. When GEMINI_API_KEY is configured in
Streamlit secrets or the environment, this module sends a tailored prompt and
optional camera/audio evidence to Gemini. Unknown facts are never fabricated.
"""

from __future__ import annotations

import os
from typing import Any


SYSTEM_PROMPT = """You are CrisisBridge Sentinel, a careful emergency-intelligence analyst.
Answer only from the supplied context and attached evidence. Separate observed
facts, source-reported figures, forecasts, estimates, and unknowns. Never infer
or invent deaths, injuries, affected people, locations, or response actions.
If a requested fact is missing, say 'Not reported by the connected source'.
Return concise but complete Markdown with these sections: Direct answer,
Situation, Affected people, Casualties, Resources, Responders, Evidence and
sources, Uncertainty, and Recommended verification. Do not issue autonomous
orders and do not replace local emergency authorities.
"""


def _api_key(override: str | None = None) -> str | None:
    return override or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def gemini_available(override: str | None = None) -> bool:
    return bool(_api_key(override))


def ask_gemini(
    question: str,
    context: dict[str, Any],
    *,
    image_bytes: bytes | None = None,
    audio_bytes: bytes | None = None,
    api_key: str | None = None,
) -> str | None:
    """Call Gemini when configured; otherwise return None for safe fallback."""
    key = _api_key(api_key)
    if not key:
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
        prompt = f"""User question: {question}

Dynamic CrisisBridge context:
{context}

Use the context timestamp and source status in your answer. If the context is
synthetic or stale, say so explicitly. Ask for a more precise location or date
when the question cannot be answered reliably.
"""
        parts: list[Any] = [prompt]
        if image_bytes:
            parts.append({"mime_type": "image/jpeg", "data": image_bytes})
        if audio_bytes:
            parts.append({"mime_type": "audio/wav", "data": audio_bytes})
        response = model.generate_content(parts)
        return getattr(response, "text", None) or "Gemini returned no text response."
    except Exception as exc:  # graceful fallback keeps the public demo healthy
        return f"Gemini is temporarily unavailable: {exc.__class__.__name__}. Use the source-backed CrisisBridge response below."
