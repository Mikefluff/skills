"""Google image providers — the Gemini image family, marketed as "Nano Banana".

Uses the google-genai SDK; reads GEMINI_API_KEY lazily inside generate().

The Imagen 4 family that used to live here was shut down by Google on
2026-06-30. Its slugs still resolve — see the deprecation aliases at the bottom
of this file — but they route to the Gemini replacements Google names in its own
migration table, because the Imagen endpoints no longer answer.
"""

from __future__ import annotations

import mimetypes
import os
from decimal import Decimal
from pathlib import Path
from typing import Any

import requests

from ..cost import estimate
from ..errors import ProviderError, QuotaError
from .base import GenerationResult, JobHandle, Provider


def _read_image_bytes_and_mime(value: str | bytes) -> tuple[bytes, str]:
    """Resolve an image reference (path / URL / raw bytes) → (bytes, mime).

    Used to embed a reference image as a multimodal Part.
    """
    if isinstance(value, bytes):
        return value, "image/png"
    if value.startswith(("http://", "https://")):
        resp = requests.get(value, timeout=30)
        if not resp.ok:
            raise ProviderError(
                "nano-banana-pro", resp.status_code, f"failed to fetch image URL: {value}",
            )
        mime = resp.headers.get("Content-Type", "image/png").split(";")[0]
        return resp.content, mime
    # local file path
    path = Path(value)
    if not path.is_file():
        raise ProviderError("nano-banana-pro", None, f"image file not found: {value}")
    mime, _ = mimetypes.guess_type(str(path))
    return path.read_bytes(), mime or "image/png"


def _wrap_error(name: str, exc: Exception) -> ProviderError:
    msg = str(exc)
    status: int | None = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status == 429 or "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
        return QuotaError(name, status, msg)
    return ProviderError(name, status, msg)


class _GeminiImageProvider(Provider):
    """One Gemini image model. Tiers differ by model id and price, not by call shape."""

    modality = "image"
    requires_env = ("GEMINI_API_KEY",)

    def __init__(self, name: str, model_id: str) -> None:
        self.name = name
        self._model_id = model_id

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return estimate(self.name, **kwargs)

    def _image_config(self, types: Any, kwargs: dict[str, Any]) -> Any | None:
        """Build ImageConfig if this SDK version has it; otherwise skip it.

        Pinning the SDK is not our call — an older google-genai simply ignores
        aspect ratio rather than crashing on an unknown kwarg.
        """
        image_config_cls = getattr(types, "ImageConfig", None)
        if image_config_cls is None:
            return None
        fields: dict[str, Any] = {"aspect_ratio": str(kwargs.get("aspect_ratio", "1:1"))}
        resolution = kwargs.get("resolution")
        if resolution:
            fields["image_size"] = str(resolution).upper()
        try:
            return image_config_cls(**fields)
        except TypeError:
            # Field names drifted between SDK versions — aspect ratio alone is safer.
            try:
                return image_config_cls(aspect_ratio=fields["aspect_ratio"])
            except TypeError:
                return None

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:
        self.ensure_available()
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ProviderError(self.name, None, "google-genai SDK not installed") from exc

        # Accept reference image via either kwarg name — `image_url` is the cross-provider
        # alias; `input_image` is the BFL native key. Either resolves to bytes + mime.
        image_ref = kwargs.get("image_url") or kwargs.get("input_image")
        contents: Any = prompt
        if image_ref:
            image_bytes, image_mime = _read_image_bytes_and_mime(image_ref)
            contents = [
                types.Part.from_bytes(data=image_bytes, mime_type=image_mime),
                prompt,
            ]

        config_fields: dict[str, Any] = {"response_modalities": ["TEXT", "IMAGE"]}
        image_config = self._image_config(types, kwargs)
        if image_config is not None:
            config_fields["image_config"] = image_config

        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            response = client.models.generate_content(
                model=self._model_id,
                contents=contents,
                config=types.GenerateContentConfig(**config_fields),
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
            extra={
                "model_id": self._model_id,
                "had_input_image": image_ref is not None,
                "resolution": kwargs.get("resolution"),
            },
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


from ..config import register, register_deprecated  # noqa: E402

# Model ids verified against ai.google.dev/gemini-api/docs/nanobanana on 2026-08-03.
register(_GeminiImageProvider("nano-banana-pro", "gemini-3-pro-image"))
register(_GeminiImageProvider("nano-banana-2", "gemini-3.1-flash-image"))
register(_GeminiImageProvider("nano-banana-2-lite", "gemini-3.1-flash-lite-image"))

_IMAGEN_SHUTDOWN = "Google shut the Imagen 4 endpoints down on 2026-06-30"
register_deprecated("imagen-4", "nano-banana-2", _IMAGEN_SHUTDOWN)
register_deprecated("imagen-4-ultra", "nano-banana-pro", _IMAGEN_SHUTDOWN)
register_deprecated("imagen-4-fast", "nano-banana-2-lite", _IMAGEN_SHUTDOWN)
