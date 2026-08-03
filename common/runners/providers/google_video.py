"""Google video providers — Veo 3.1 (standard + fast).
Async long-running operation pattern via google-genai client.operations.get()."""

from __future__ import annotations

import os
import sys
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


_LAST_FRAME_REFUSALS = ("last_frame", "400", "invalid_argument", "not supported", "use case")


def _is_last_frame_refusal(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(key in msg for key in _LAST_FRAME_REFUSALS)


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

    @staticmethod
    def _as_image(types_mod: Any, ref: str) -> Any:
        image_bytes, mime = _read_image_bytes_and_mime(ref)
        return types_mod.Image(image_bytes=image_bytes, mime_type=mime)

    def _frames(self, types_mod: Any, kwargs: dict[str, Any]) -> tuple[Any, Any]:
        """(first frame, last frame); either may be None. Aliases accepted.

        Pinning the last frame is Veo's only documented lever against drift in
        image-to-video: setting last_frame == image forces start == end, which
        is what collapses overlay-text wobble. `lock_first_last=True` asks for
        exactly that without naming the same file twice.
        """
        image_ref = kwargs.get("image_url") or kwargs.get("input_image")
        last_ref = kwargs.get("last_frame") or kwargs.get("last_frame_image")
        if last_ref is None and kwargs.get("lock_first_last") and image_ref:
            last_ref = image_ref
        return (
            self._as_image(types_mod, image_ref) if image_ref else None,
            self._as_image(types_mod, last_ref) if last_ref else None,
        )

    def _submit(self, client: Any, types_mod: Any, gen_kwargs: dict, config_kwargs: dict) -> Any:
        """Submit the job, retrying once without last_frame if it is refused."""
        try:
            return client.models.generate_videos(**gen_kwargs)
        except Exception as exc:  # noqa: BLE001
            # Some preview model IDs (notably veo-3.1-fast-generate-preview) reject
            # last_frame with a 400 whose wording varies — "use case is currently
            # not supported", "Parameter Not Supported". Matching the message is a
            # losing game, so retry on any error while last_frame is set: the shot
            # still ships, with the drift-lock weakened but negative_prompt and
            # prompt-side discipline still in force.
            if "last_frame" not in config_kwargs or not _is_last_frame_refusal(exc):
                raise
            config_kwargs.pop("last_frame", None)
            gen_kwargs["config"] = types_mod.GenerateVideosConfig(**config_kwargs)
            print(
                f"  ⚠ {self.name}: last_frame rejected, retrying without it "
                f"(text-lock weakened; negative_prompt + prompt-side discipline still active)",
                file=sys.stderr,
            )
            return client.models.generate_videos(**gen_kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:
        self.ensure_available()
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ProviderError(self.name, None, "google-genai SDK not installed") from exc

        image_part, last_frame_part = self._frames(types, kwargs)

        config_kwargs: dict[str, Any] = dict(
            number_of_videos=int(kwargs.get("variants", 1) or 1),
            aspect_ratio=str(kwargs.get("aspect_ratio", "16:9")),
            duration_seconds=str(int(kwargs.get("duration_seconds", 8) or 8)),
        )
        # Comma-separated phrase list; the text-stability default comes from the
        # Veo text-preservation field guide.
        if kwargs.get("negative_prompt"):
            config_kwargs["negative_prompt"] = kwargs["negative_prompt"]
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
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            operation = self._submit(client, types, gen_kwargs, config_kwargs)
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
