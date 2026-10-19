"""OpenAI image provider — gpt-image-2 and later (gpt-image-2.5-sunburst / -flare via model_id).
Vendor: OpenAI Images API. With reference_images it calls the edits endpoint, so a
portrait or a storyboard frame is drawn from the faces it is given, not invented.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
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

        size: str = kwargs.get("size") or _size(kwargs.get("aspect_ratio"), kwargs.get("image_size"))
        quality: Literal["low", "medium", "high"] = kwargs.get("quality", "medium")
        variants: int = int(kwargs.get("variants", 1))
        output_format: str = kwargs.get("output_format", "png")

        body = {
            "model": kwargs.get("model_id") or "gpt-image-2",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": variants,
            "output_format": output_format,
        }
        resp = self._post(body, [str(r) for r in kwargs.get("reference_images") or []], api_key)
        b64 = self._b64(resp)
        content = base64.b64decode(b64)
        mime = "image/png" if output_format == "png" else f"image/{output_format}"
        return GenerationResult(
            content=content,
            mime=mime,
            extension=output_format,
            extra={"variants": variants, "size": size, "quality": quality, "model_id": body["model"],
                   "cost_usd": float(self.estimate_cost(quality=quality, variants=variants) or 0)},
        )

    def _post(self, body: dict[str, Any], refs: list[str], api_key: str):
        """The edits endpoint when there are references to draw from, else generations."""
        auth = {"Authorization": f"Bearer {api_key}"}
        # Synchronous endpoint — it renders before answering, so it needs far
        # longer than a job submission would.
        if refs:
            files = [("image[]", (Path(r).name, Path(r).read_bytes(), _mime(r))) for r in refs]
            return _http.post(self.name, "https://api.openai.com/v1/images/edits",
                              data={k: str(v) for k, v in body.items()}, files=files, headers=auth, timeout=600)
        return _http.post(self.name, "https://api.openai.com/v1/images/generations", json=body,
                          headers={**auth, "Content-Type": "application/json"}, timeout=300)

    def _b64(self, resp: Any) -> str:
        """The first image's base64, or a ProviderError saying what is missing."""
        data = resp.json().get("data") or []
        if not data:
            raise ProviderError(self.name, resp.status_code, "no images in response")
        b64 = data[0].get("b64_json")
        if not b64:
            raise ProviderError(self.name, resp.status_code, "missing b64_json in response")
        return b64


# Long edge per tier; both sides multiples of 16, as the API requires.
_EDGE = {"1K": 1024, "2K": 2048, "4K": 3840}


def _size(aspect: str | None, tier: str | None) -> str:
    """"16:9" at 2K → "2048x1152"; no aspect → the square default."""
    if not aspect:
        return "1024x1024"
    w, h = (int(v) for v in aspect.split(":"))
    edge = _EDGE.get(tier or "2K", 2048) if w >= h else 1536
    long_, short = edge, round(edge * min(w, h) / max(w, h) / 16) * 16
    return f"{long_}x{short}" if w >= h else f"{short}x{long_}"


def _mime(path: str) -> str:
    return "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"


from ..config import register

register(GptImage2Provider())
