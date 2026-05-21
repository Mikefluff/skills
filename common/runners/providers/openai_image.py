"""OpenAI image provider — gpt-image-2.
Vendor: OpenAI Images API.
"""

from __future__ import annotations

import base64
import os
from decimal import Decimal
from typing import Any, Literal

import requests

from .. import cost
from ..errors import ProviderError, QuotaError
from .base import GenerationResult, Provider


class GptImage2Provider(Provider):
    name = "gpt-image-2"
    modality = "image"
    requires_env = ("OPENAI_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return cost.estimate(self.name, **kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        self.ensure_available()
        api_key = os.environ["OPENAI_API_KEY"]

        size: str = kwargs.get("size", "1024x1024")
        quality: Literal["low", "medium", "high"] = kwargs.get("quality", "medium")
        variants: int = int(kwargs.get("variants", 1))
        output_format: str = kwargs.get("output_format", "png")

        body = {
            "model": "gpt-image-2",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": variants,
            "output_format": output_format,
            "response_format": "b64_json",
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(
                "https://api.openai.com/v1/images/generations",
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

        payload = resp.json()
        data = payload.get("data") or []
        if not data:
            raise ProviderError(self.name, resp.status_code, "no images in response")

        b64 = data[0].get("b64_json")
        if not b64:
            raise ProviderError(self.name, resp.status_code, "missing b64_json in response")

        content = base64.b64decode(b64)
        mime = "image/png" if output_format == "png" else f"image/{output_format}"
        return GenerationResult(
            content=content,
            mime=mime,
            extension=output_format,
            extra={"variants": variants, "size": size, "quality": quality},
        )


from ..config import register

register(GptImage2Provider())
