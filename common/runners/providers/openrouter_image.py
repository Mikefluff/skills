"""Images and image judgement through OpenRouter's chat API — Nano Banana Pro and a Gemini critic.
Vendor: OpenRouter (https://openrouter.ai/api/v1/chat/completions), routed to Google.

The same Google models as `google_image.py`, billed to the OpenRouter balance —
for when the Gemini project itself cannot be billed. A film's storyboard needs
several references per frame (the character, the previous frame for the
space), which this route takes as an ordered list.

`judge()` is the other half of a storyboard: a vision model reading a frame
against the shot it was meant to be, returning a score and what to fix.
"""

from __future__ import annotations

import base64
import json
import os
import re
from decimal import Decimal
from typing import Any

from .. import cost
from ..errors import ProviderError
from . import _http
from .base import GenerationResult, Provider
from .seedance import _refs, as_url

_CHAT = "https://openrouter.ai/api/v1/chat/completions"
JUDGE_MODEL = "google/gemini-3.5-flash"


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"}


def _images(refs: list[str]) -> list[dict[str, Any]]:
    return [{"type": "image_url", "image_url": {"url": as_url(r)}} for r in refs]


class OpenRouterNanoBananaProProvider(Provider):
    name = "openrouter-nano-banana-pro"
    modality = "image"
    requires_env = ("OPENROUTER_API_KEY",)
    model_id = "google/gemini-3-pro-image"

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return cost.estimate(self.name, variants=kwargs.get("variants", 1))

    def build_body(self, prompt: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        refs = _refs(kwargs, "reference_images")
        body: dict[str, Any] = {
            "model": kwargs.get("model_id") or self.model_id,
            "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": [*_images(refs), {"type": "text", "text": prompt}]}],
        }
        if kwargs.get("aspect_ratio"):
            body["image_config"] = {"aspect_ratio": kwargs["aspect_ratio"]}
        return body

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        self.ensure_available()
        data = _http.post(self.name, _CHAT, json=self.build_body(prompt, kwargs), headers=_headers(), timeout=300).json()
        message = ((data.get("choices") or [{}])[0]).get("message") or {}
        images = message.get("images") or []
        if not images:
            raise ProviderError(self.name, None, f"no image returned: {(message.get('content') or '')[:200]}")
        url = images[0]["image_url"]["url"]
        return GenerationResult(
            content=base64.b64decode(url.split(",", 1)[1]),
            mime="image/png",
            extension="png",
            extra={"model_id": self.model_id, "cost_usd": (data.get("usage") or {}).get("cost")},
        )


def judge(prompt: str, images: list[str], *, model: str = JUDGE_MODEL) -> dict[str, Any]:
    """Ask a vision model for a JSON verdict on `images`; returns the parsed object."""
    body = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": [*_images(images), {"type": "text", "text": prompt}]}],
    }
    data = _http.post("openrouter-judge", _CHAT, json=body, headers=_headers(), timeout=180).json()
    text = (((data.get("choices") or [{}])[0]).get("message") or {}).get("content") or ""
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ProviderError("openrouter-judge", None, f"no JSON verdict: {text[:200]}")
    verdict = json.loads(match.group(0))
    verdict["cost_usd"] = (data.get("usage") or {}).get("cost")
    return verdict


from ..config import register

register(OpenRouterNanoBananaProProvider())
