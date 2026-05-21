"""OpenAI TTS provider — gpt-4o-mini-tts.
Vendor: OpenAI Audio Speech API.
"""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

import requests

from .. import cost
from ..errors import ProviderError, QuotaError
from .base import GenerationResult, Provider

CHARS_PER_MINUTE = 150


class GptMiniTtsProvider(Provider):
    name = "gpt-4o-mini-tts"
    modality = "audio"
    requires_env = ("OPENAI_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        prompt_text: str = kwargs.get("prompt") or kwargs.get("input") or ""
        char_count = len(prompt_text)
        minutes = max(char_count / CHARS_PER_MINUTE, 0.01)
        return cost.estimate(self.name, duration_minutes=minutes, variants=kwargs.get("variants", 1))

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        self.ensure_available()
        api_key = os.environ["OPENAI_API_KEY"]

        voice: str = kwargs.get("voice", "alloy")
        response_format: str = kwargs.get("response_format", "mp3")

        body = {
            "model": "gpt-4o-mini-tts",
            "voice": voice,
            "input": prompt,
            "response_format": response_format,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(
                "https://api.openai.com/v1/audio/speech",
                json=body,
                headers=headers,
                timeout=120,
            )
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            raise QuotaError(self.name, 429, resp.text[:500])
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.status_code, resp.text[:500])

        return GenerationResult(
            content=resp.content,
            mime="audio/mpeg" if response_format == "mp3" else f"audio/{response_format}",
            extension=response_format,
            extra={"voice": voice, "char_count": len(prompt)},
        )


from ..config import register

register(GptMiniTtsProvider())
