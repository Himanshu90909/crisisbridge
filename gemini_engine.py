"""Optional Gemini integration for CrisisBridge.

Uses the current ``google-genai`` SDK. The app remains runnable without a key
or package and falls back to source-bounded deterministic responses.
"""
from __future__ import annotations

import os
from typing import Any

SYSTEM_PROMPT = """You are CrisisBridge Sentinel, a careful emergency-intelligence analyst.
Answer only from the supplied context and attached evidence. Separate observed
facts, source-reported figures, forecasts, estimates, and unknowns. Never infer or invent deaths, injuries, affected people, locations, or response actions.
If a requested fact is missing, say 'Not reported by the connected source'.
Return concise but complete Markdown with these sections: Direct answer,
Situation, Affected people, Casualties, Resources, Responders, Evidence and
sources, Uncertainty, and Recommended verification. Do not issue autonomous
orders and do not replace local emergency authorities.
"""


def _api_key(override: str | None = None) -> str | None:
    return override or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def gemini_package_available() -> bool:
    try:
        from google import genai  # noqa: F401
        return True
    except ModuleNotFoundError:
        return False


def gemini_available(override: str | None = None) -> bool:
    return bool(_api_key(override)) and gemini_package_available()


def gemini_status(override: str | None = None) -> str:
    if not gemini_package_available():
        return "package missing; redeploy after installing google-genai from requirements.txt"
    if not _api_key(override):
        return "key not configured; deterministic fallback active"
    return "configured"


def ask_gemini(
    question: str,
    context: dict[str, Any],
    *,
    image_bytes: bytes | None = None,
    audio_bytes: bytes | None = None,
    document_bytes: bytes | None = None,
    document_mime: str | None = None,
    api_key: str | None = None,
) -> str | None:
    """Call Gemini when configured; return None for a safe local fallback."""
    key = _api_key(api_key)
    if not key or not gemini_package_available():
        return None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)
        prompt = f"""{SYSTEM_PROMPT}

User question: {question}

Dynamic CrisisBridge context:
{context}

Use the context timestamp and source status in your answer. If the context is
synthetic or stale, say so explicitly. Ask for a more precise location or date
when the question cannot be answered reliably.
"""
        parts: list[Any] = [prompt]
        if image_bytes:
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
        if audio_bytes:
            parts.append(types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"))
        if document_bytes:
            parts.append(types.Part.from_bytes(data=document_bytes, mime_type=document_mime or "application/octet-stream"))
        response = client.models.generate_content(model="gemini-2.0-flash", contents=parts)
        return getattr(response, "text", None) or "Gemini returned no text response."
    except Exception:
        # Do not expose provider internals or raw exception text to visitors.
        return None
