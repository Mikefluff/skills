"""Ideogram image providers, v4 and v3.

The two generate endpoints differ in one field name and nothing else that matters
here: v3 takes `prompt`, v4 takes `text_prompt` (and a `json_prompt` alternative
this does not use yet — teaching the layout skills to emit structured prompts is
its own change, not a slug).

Verified against developer.ideogram.ai on 2026-08-08:
`POST /v1/ideogram-v4/generate`, `rendering_speed` ∈ {TURBO, DEFAULT, QUALITY}.
FLASH is documented as "coming soon" for v4 and returns 400 today, so the flash
tier stays on v3.
"""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from .. import cost
from ..errors import ProviderError
from . import _http
from .base import GenerationResult, Provider


class _IdeogramBase(Provider):
    modality = "image"
    requires_env = ("IDEOGRAM_API_KEY",)
    rendering_speed: str = "DEFAULT"
    endpoint: str = "https://api.ideogram.ai/v1/ideogram-v3/generate"
    prompt_field: str = "prompt"

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return cost.estimate(self.name, variants=kwargs.get("num_images", kwargs.get("variants", 1)))

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        self.ensure_available()
        api_key = os.environ["IDEOGRAM_API_KEY"]

        num_images = int(kwargs.get("num_images", kwargs.get("variants", 1)))
        aspect_ratio: str = kwargs.get("aspect_ratio", "16x9")

        body: dict[str, Any] = {
            self.prompt_field: prompt,
            "rendering_speed": self.rendering_speed,
            "num_images": num_images,
            "aspect_ratio": aspect_ratio,
        }
        resp = _http.post(
            self.name,
            self.endpoint,
            json=body,
            headers={"Api-Key": api_key, "Content-Type": "application/json"},
            timeout=120,
        )

        payload = resp.json()
        data = payload.get("data") or []
        if not data:
            raise ProviderError(self.name, resp.status_code, "no images in response")

        image_url = data[0].get("url")
        if not image_url:
            raise ProviderError(self.name, resp.status_code, "missing url in response")

        return GenerationResult(
            content=_http.download(self.name, image_url, timeout=120),
            mime="image/png",
            extension="png",
            extra={
                "rendering_speed": self.rendering_speed,
                "num_images": num_images,
                "aspect_ratio": aspect_ratio,
            },
        )


class _IdeogramV4Base(_IdeogramBase):
    endpoint = "https://api.ideogram.ai/v1/ideogram-v4/generate"
    prompt_field = "text_prompt"


class Ideogram4TurboProvider(_IdeogramV4Base):
    name = "ideogram-4-turbo"
    rendering_speed = "TURBO"


class Ideogram4DefaultProvider(_IdeogramV4Base):
    name = "ideogram-4"
    rendering_speed = "DEFAULT"


class Ideogram4QualityProvider(_IdeogramV4Base):
    name = "ideogram-4-quality"
    rendering_speed = "QUALITY"


class IdeogramFlashProvider(_IdeogramBase):
    """Cheapest v3 tier. Priced at TURBO's rate — FLASH bills lower, never higher."""

    name = "ideogram-3-flash"
    rendering_speed = "FLASH"


class IdeogramTurboProvider(_IdeogramBase):
    name = "ideogram-3-turbo"
    rendering_speed = "TURBO"


class IdeogramDefaultProvider(_IdeogramBase):
    name = "ideogram-3"
    rendering_speed = "DEFAULT"


class IdeogramQualityProvider(_IdeogramBase):
    name = "ideogram-3-quality"
    rendering_speed = "QUALITY"


from ..config import register

register(Ideogram4TurboProvider())
register(Ideogram4DefaultProvider())
register(Ideogram4QualityProvider())
register(IdeogramFlashProvider())
register(IdeogramTurboProvider())
register(IdeogramDefaultProvider())
register(IdeogramQualityProvider())
