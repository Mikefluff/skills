"""Google video providers — Veo 3.1 (standard + fast).
Async long-running operation pattern via google-genai client.operations.get()."""

from __future__ import annotations

import os
import time
from decimal import Decimal
from typing import Any

from ..cost import estimate
from ..errors import ProviderError, QuotaError
from ..poll import poll_until
from .base import GenerationResult, JobHandle, Provider
from .google_image import _read_image_bytes_and_mime

_VEO_MODEL_IDS: dict[str, str] = {
    "veo-3-1": "veo-3.1-generate-preview",
    "veo-3-1-fast": "veo-3.1-fast-generate-preview",
}

# Module-level cache of in-flight operations keyed by operation.name so poll()
# can recover the original operation object (the SDK refreshes it via .get()).
_OPERATIONS: dict[str, Any] = {}


def _wrap_error(name: str, exc: Exception) -> ProviderError:
    msg = str(exc)
    status: int | None = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status == 429 or "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
        return QuotaError(name, status, msg)
    return ProviderError(name, status, msg)


class _VeoProvider(Provider):
    modality = "video"
    requires_env = ("GEMINI_API_KEY",)

    def __init__(self, name: str) -> None:
        self.name = name
        self._model_id = _VEO_MODEL_IDS[name]

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return estimate(self.name, **kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:
        self.ensure_available()
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ProviderError(self.name, None, "google-genai SDK not installed") from exc

        duration_seconds = int(kwargs.get("duration_seconds", 8) or 8)
        aspect_ratio = str(kwargs.get("aspect_ratio", "16:9"))
        variants = int(kwargs.get("variants", 1) or 1)

        # Optional first-frame image (image-to-video) — accept cross-provider aliases
        image_ref = kwargs.get("image_url") or kwargs.get("input_image")
        image_part = None
        if image_ref:
            image_bytes, image_mime = _read_image_bytes_and_mime(image_ref)
            image_part = types.Image(image_bytes=image_bytes, mime_type=image_mime)

        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            gen_kwargs: dict[str, Any] = dict(
                model=self._model_id,
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    number_of_videos=variants,
                    aspect_ratio=aspect_ratio,
                    duration_seconds=str(duration_seconds),
                ),
            )
            if image_part is not None:
                gen_kwargs["image"] = image_part
            operation = client.models.generate_videos(**gen_kwargs)
        except Exception as exc:  # noqa: BLE001
            raise _wrap_error(self.name, exc) from exc

        op_name = getattr(operation, "name", None) or f"veo-{int(time.time() * 1000)}"
        _OPERATIONS[op_name] = operation
        return JobHandle(
            provider=self.name,
            job_id=op_name,
            started_at=time.time(),
            extra={"model_id": self._model_id},
        )

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        try:
            from google import genai
        except ImportError as exc:
            raise ProviderError(self.name, None, "google-genai SDK not installed") from exc

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        operation = _OPERATIONS.get(handle.job_id)
        if operation is None:
            raise ProviderError(self.name, None, f"operation {handle.job_id} not cached locally")

        def _check() -> Any | None:
            nonlocal operation
            try:
                operation = client.operations.get(operation)
            except Exception as exc:  # noqa: BLE001
                raise _wrap_error(self.name, exc) from exc
            _OPERATIONS[handle.job_id] = operation
            if getattr(operation, "done", False):
                return operation
            return None

        done_op = poll_until(_check, provider=self.name, timeout=timeout)

        response = getattr(done_op, "response", None)
        videos = getattr(response, "generated_videos", None) or []
        if not videos:
            raise ProviderError(self.name, None, "no videos returned")
        video = videos[0].video

        video_bytes = getattr(video, "video_bytes", None)
        if not video_bytes:
            try:
                client.files.download(file=video)
                video_bytes = getattr(video, "video_bytes", None)
            except Exception as exc:  # noqa: BLE001
                raise _wrap_error(self.name, exc) from exc
        if not video_bytes:
            raise ProviderError(self.name, None, "video bytes unavailable after download")

        _OPERATIONS.pop(handle.job_id, None)
        return GenerationResult(
            content=video_bytes,
            mime="video/mp4",
            extension="mp4",
            extra={"model_id": self._model_id, "job_id": handle.job_id},
        )


from ..config import register  # noqa: E402

register(_VeoProvider("veo-3-1"))
register(_VeoProvider("veo-3-1-fast"))
