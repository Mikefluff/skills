"""OpenAI image provider — gpt-image-2.
Vendor: OpenAI Images API.
"""

from __future__ import annotations

import base64
import os
from decimal import Decimal
from typing import Any, Literal

from .. import cost
from ..errors import ProviderError
from . import _http
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
        }
        # Synchronous endpoint — it renders before answering, so it needs far
        # longer than a job submission would.
        resp = _http.post(
            self.name,
            "https://api.openai.com/v1/images/generations",
            json=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=300,
        )

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
