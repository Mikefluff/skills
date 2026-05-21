"""Google music provider — Lyria 3 Pro.
Gated behind LYRIA_API_ENABLED=1 while the public API surface is limited preview."""

from __future__ import annotations

import os
import time
from decimal import Decimal
from typing import Any

from ..cost import estimate
from ..errors import ProviderError, QuotaError
from ..poll import poll_until
from .base import GenerationResult, JobHandle, Provider

_OPERATIONS: dict[str, Any] = {}


def _wrap_error(name: str, exc: Exception) -> ProviderError:
    msg = str(exc)
    status: int | None = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status == 429 or "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
        return QuotaError(name, status, msg)
    return ProviderError(name, status, msg)


class _LyriaProvider(Provider):
    name = "lyria-3-pro"
    modality = "music"
    requires_env = ("GEMINI_API_KEY",)
    _model_id = "lyria-3.0-pro-preview"

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return estimate(self.name, **kwargs)

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:
        self.ensure_available()
        if os.environ.get("LYRIA_API_ENABLED") != "1":
            raise ProviderError(
                self.name,
                None,
                "Lyria 3 Pro API is in limited preview; set LYRIA_API_ENABLED=1 "
                "once your project is allowlisted to enable this provider.",
            )
        try:
            from google import genai
        except ImportError as exc:
            raise ProviderError(self.name, None, "google-genai SDK not installed") from exc

        duration_minutes = float(kwargs.get("duration_minutes", 1.0) or 1.0)
        duration_minutes = max(0.1, min(duration_minutes, 3.0))
        lyrics = kwargs.get("lyrics")
        key = kwargs.get("key")
        bpm = kwargs.get("bpm")

        config: dict[str, Any] = {"duration_seconds": int(duration_minutes * 60)}
        if lyrics:
            config["lyrics"] = str(lyrics)
        if key:
            config["key"] = str(key)
        if bpm:
            config["bpm"] = int(bpm)

        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            generate_music = getattr(client.models, "generate_music", None)
            if generate_music is None:
                raise ProviderError(
                    self.name,
                    None,
                    "installed google-genai SDK has no generate_music(); "
                    "upgrade SDK once Lyria is GA.",
                )
            operation = generate_music(model=self._model_id, prompt=prompt, config=config)
        except ProviderError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise _wrap_error(self.name, exc) from exc

        op_name = getattr(operation, "name", None) or f"lyria-{int(time.time() * 1000)}"
        _OPERATIONS[op_name] = operation
        return JobHandle(
            provider=self.name,
            job_id=op_name,
            started_at=time.time(),
            extra={"model_id": self._model_id, "duration_minutes": duration_minutes},
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
        tracks = (
            getattr(response, "generated_music", None)
            or getattr(response, "generated_audio", None)
            or []
        )
        if not tracks:
            raise ProviderError(self.name, None, "no music returned")
        track = tracks[0]
        audio = getattr(track, "audio", None) or getattr(track, "music", None)
        audio_bytes = getattr(audio, "audio_bytes", None) or getattr(audio, "data", None)
        if not audio_bytes:
            raise ProviderError(self.name, None, "audio bytes unavailable")

        _OPERATIONS.pop(handle.job_id, None)
        return GenerationResult(
            content=audio_bytes,
            mime="audio/mpeg",
            extension="mp3",
            extra={"model_id": self._model_id, "job_id": handle.job_id},
        )


from ..config import register  # noqa: E402

register(_LyriaProvider())
