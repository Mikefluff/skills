"""Google image providers — Imagen 4 family + Nano Banana Pro (Gemini 3 Pro Image).
Uses the google-genai SDK; reads GEMINI_API_KEY lazily inside generate()."""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from ..cost import estimate
from ..errors import ProviderError, QuotaError
from .base import GenerationResult, JobHandle, Provider

_IMAGEN_MODEL_IDS: dict[str, str] = {
    "imagen-4": "imagen-4.0-generate-001",
    "imagen-4-ultra": "imagen-4.0-ultra-generate-001",
    "imagen-4-fast": "imagen-4.0-fast-generate-001",
}


def _wrap_error(name: str, exc: Exception) -> ProviderError:
    msg = str(exc)
    status: int | None = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status == 429 or "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
        return QuotaError(name, status, msg)
    return ProviderError(name, status, msg)


class _ImagenProvider(Provider):
    """Imagen 4 / 4 Ultra / 4 Fast."""

    modality = "image"
    requires_env = ("GEMINI_API_KEY",)

    def __init__(self, name: str) -> None:
        self.name = name
        self._model_id = _IMAGEN_MODEL_IDS[name]

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return estimate(self.name, **kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:
        self.ensure_available()
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ProviderError(self.name, None, "google-genai SDK not installed") from exc

        variants = int(kwargs.get("variants", 1) or 1)
        aspect_ratio = str(kwargs.get("aspect_ratio", "1:1"))

        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            response = client.models.generate_images(
                model=self._model_id,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=variants,
                    aspect_ratio=aspect_ratio,
                ),
            )
        except Exception as exc:  # noqa: BLE001
            raise _wrap_error(self.name, exc) from exc

        images = getattr(response, "generated_images", None) or []
        if not images:
            raise ProviderError(self.name, None, "no images returned")
        first = images[0]
        image_bytes = first.image.image_bytes
        return GenerationResult(
            content=image_bytes,
            mime="image/png",
            extension="png",
            extra={"variants_returned": len(images), "model_id": self._model_id},
        )


class _NanoBananaProProvider(Provider):
    """Gemini 3 Pro Image (a.k.a. Nano Banana Pro)."""

    name = "nano-banana-pro"
    modality = "image"
    requires_env = ("GEMINI_API_KEY",)
    _model_id = "gemini-3-pro-image-preview"

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return estimate(self.name, **kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:  # noqa: ARG002
        self.ensure_available()
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ProviderError(self.name, None, "google-genai SDK not installed") from exc

        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            response = client.models.generate_content(
                model=self._model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                ),
            )
        except Exception as exc:  # noqa: BLE001
            raise _wrap_error(self.name, exc) from exc

        image_bytes = self._extract_image_bytes(response)
        if image_bytes is None:
            raise ProviderError(self.name, None, "no image part returned")
        return GenerationResult(
            content=image_bytes,
            mime="image/png",
            extension="png",
            extra={"model_id": self._model_id},
        )

    @staticmethod
    def _extract_image_bytes(response: Any) -> bytes | None:
        parts = getattr(response, "parts", None)
        if parts is None:
            candidates = getattr(response, "candidates", None) or []
            for cand in candidates:
                content = getattr(cand, "content", None)
                if content is not None:
                    parts = getattr(content, "parts", None)
                    if parts:
                        break
        for part in parts or []:
            inline = getattr(part, "inline_data", None)
            if inline is not None and getattr(inline, "data", None):
                return inline.data
        return None


from ..config import register  # noqa: E402

register(_ImagenProvider("imagen-4"))
register(_ImagenProvider("imagen-4-ultra"))
register(_ImagenProvider("imagen-4-fast"))
register(_NanoBananaProProvider())
