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
    """Lyria 3. Model ids verified against ai.google.dev on 2026-08-03.

    Google's newer surface for these models is the Interactions API. The legacy
    generate_music() path is what the SDK exposes today, so that is what we call;
    switch when the SDK grows interactions.create().
    """

    modality = "music"
    requires_env = ("GEMINI_API_KEY",)
    max_minutes: float = 3.0

    def __init__(self, name: str, model_id: str, max_minutes: float) -> None:
        self.name = name
        self._model_id = model_id
        self.max_minutes = max_minutes

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return estimate(self.name, **kwargs)

    def _require_preview_access(self) -> None:
        if os.environ.get("LYRIA_API_ENABLED") != "1":
            raise ProviderError(
                self.name,
                None,
                "Lyria 3 is in paid preview; set LYRIA_API_ENABLED=1 "
                "once your project is allowlisted to enable this provider.",
            )

    def _config(self, kwargs: dict[str, Any]) -> tuple[dict[str, Any], float]:
        """(SDK config, clamped minutes). Pro caps at 3 minutes, Clip at 30 seconds."""
        minutes = max(0.1, min(float(kwargs.get("duration_minutes", 1.0) or 1.0), self.max_minutes))
        config: dict[str, Any] = {"duration_seconds": int(minutes * 60)}
        if kwargs.get("lyrics"):
            config["lyrics"] = str(kwargs["lyrics"])
        if kwargs.get("key"):
            config["key"] = str(kwargs["key"])
        if kwargs.get("bpm"):
            config["bpm"] = int(kwargs["bpm"])
        return config, minutes

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:
        self.ensure_available()
        self._require_preview_access()
        try:
            from google import genai
        except ImportError as exc:
            raise ProviderError(self.name, None, "google-genai SDK not installed") from exc

        config, duration_minutes = self._config(kwargs)

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

register(_LyriaProvider("lyria-3-pro", "lyria-3-pro-preview", max_minutes=3.0))
register(_LyriaProvider("lyria-3-clip", "lyria-3-clip-preview", max_minutes=0.5))
