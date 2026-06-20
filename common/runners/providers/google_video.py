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

        # Optional last-frame image — Veo's only documented mechanism for constraining
        # drift in i2v. Setting image == last_frame forces start=end, which dramatically
        # reduces overlay text wobble. Accept "last_frame" / "last_frame_image" / a magic
        # "same-as-first" sentinel via kwargs.get("lock_first_last") == True.
        last_frame_ref = kwargs.get("last_frame") or kwargs.get("last_frame_image")
        if last_frame_ref is None and kwargs.get("lock_first_last") and image_ref:
            last_frame_ref = image_ref
        last_frame_part = None
        if last_frame_ref:
            lf_bytes, lf_mime = _read_image_bytes_and_mime(last_frame_ref)
            last_frame_part = types.Image(image_bytes=lf_bytes, mime_type=lf_mime)

        # Optional negative prompt — comma-separated phrase list for Veo. The text-stability
        # default below comes from the Veo text-preservation field guide; callers can pass
        # their own via kwargs["negative_prompt"] or extend via kwargs["negative_prompt_extra"].
        negative_prompt = kwargs.get("negative_prompt")

        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            config_kwargs: dict[str, Any] = dict(
                number_of_videos=variants,
                aspect_ratio=aspect_ratio,
                duration_seconds=str(duration_seconds),
            )
            if negative_prompt:
                config_kwargs["negative_prompt"] = negative_prompt
            if last_frame_part is not None:
                config_kwargs["last_frame"] = last_frame_part
            gen_kwargs: dict[str, Any] = dict(
                model=self._model_id,
                prompt=prompt,
                config=types.GenerateVideosConfig(**config_kwargs),
            )
            if image_part is not None:
                gen_kwargs["image"] = image_part
            try:
                operation = client.models.generate_videos(**gen_kwargs)
            except Exception as exc:  # noqa: BLE001
                # Some preview model IDs (notably veo-3.1-fast-generate-preview) reject
                # last_frame with a 400 "use case is currently not supported" or
                # "Parameter Not Supported". The error message format varies, so trigger
                # the fallback on any error when last_frame is set. Retry without
                # last_frame so the shot still ships; other levers (negative_prompt,
                # prompt-side discipline) still apply. Surface a stderr note so callers
                # know the drift-lock didn't activate.
                msg = str(exc).lower()
                fallback_keys = ("last_frame", "400", "invalid_argument", "not supported", "use case")
                if last_frame_part is not None and any(k in msg for k in fallback_keys):
                    config_kwargs.pop("last_frame", None)
                    gen_kwargs["config"] = types.GenerateVideosConfig(**config_kwargs)
                    print(
                        f"  ⚠ {self.name}: last_frame rejected, retrying without it "
                        f"(text-lock weakened; negative_prompt + prompt-side discipline still active)",
                        file=__import__("sys").stderr,
                    )
                    operation = client.models.generate_videos(**gen_kwargs)
                else:
                    raise
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
