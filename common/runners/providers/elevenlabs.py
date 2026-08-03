"""ElevenLabs providers — eleven-music (async) and eleven-tts (sync).
Vendor: ElevenLabs Music + Text-to-Speech APIs.
"""

from __future__ import annotations

import os
import time
from decimal import Decimal
from typing import Any

from .. import cost
from ..errors import ProviderError
from ..poll import poll_until
from . import _http
from .base import GenerationResult, JobHandle, Provider

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # "Rachel" — ElevenLabs default preset.

# eleven_v3 is the current flagship: 70+ languages, far wider emotional range.
# Pass model_id="eleven_multilingual_v2" to fall back to the previous default,
# or "eleven_flash_v2_5" when latency matters more than expressiveness.
DEFAULT_TTS_MODEL = "eleven_v3"

# music_v2 is the current Eleven Music model; the API still defaults to music_v1.
DEFAULT_MUSIC_MODEL = "music_v2"


def _with_lyrics(prompt: str, lyrics: str | None) -> str:
    """Fold lyrics into the prompt — Eleven Music has no separate lyrics field.

    The old code sent a top-level `lyrics` key, which is not in the request schema
    and was dropped on the floor, so every "song with these words" run came back
    as an instrumental or with invented words.
    """
    if not lyrics:
        return prompt
    return f"{prompt}\n\nLyrics:\n{lyrics}"


class ElevenMusicProvider(Provider):
    name = "eleven-music"
    modality = "music"
    requires_env = ("ELEVENLABS_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        duration_seconds = float(kwargs.get("duration_seconds", 30))
        minutes = max(duration_seconds / 60.0, 0.01)
        return cost.estimate(self.name, duration_minutes=minutes, variants=kwargs.get("variants", 1))

    def _headers(self) -> dict[str, str]:
        return {
            "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
            "Content-Type": "application/json",
        }

    @staticmethod
    def _build_body(prompt: str, duration_seconds: int, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Request body for POST /v1/music."""
        body: dict[str, Any] = {"model_id": kwargs.get("model_id", DEFAULT_MUSIC_MODEL)}

        composition_plan: dict | None = kwargs.get("composition_plan")
        if composition_plan is not None:
            # The API rejects prompt and composition_plan together — the plan wins,
            # since it carries strictly more structure than the sentence would.
            body["composition_plan"] = composition_plan
        else:
            body["prompt"] = _with_lyrics(prompt, kwargs.get("lyrics"))
            # Wire field is milliseconds, clamped by the vendor to 3s-10min. Sending
            # `duration_seconds` here silently produced default-length tracks.
            body["music_length_ms"] = max(3_000, min(duration_seconds * 1000, 600_000))

        if kwargs.get("force_instrumental"):
            body["force_instrumental"] = True
        return body

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()

        duration_seconds = int(kwargs.get("duration_seconds", 30))
        body = self._build_body(prompt, duration_seconds, kwargs)

        resp = _http.post(
            self.name,
            "https://api.elevenlabs.io/v1/music",
            json=body,
            headers=self._headers(),
        )

        # If response is audio bytes directly (small/quick gen), wrap as completed handle.
        content_type = resp.headers.get("Content-Type", "")
        if "audio" in content_type:
            return JobHandle(
                provider=self.name,
                job_id="inline",
                started_at=time.time(),
                poll_url=None,
                extra={"inline_bytes": resp.content, "duration_seconds": duration_seconds},
            )

        payload = resp.json()
        job_id = payload.get("id") or payload.get("job_id") or payload.get("generation_id")
        if not job_id:
            raise ProviderError(self.name, resp.status_code, "no job id in response")

        return JobHandle(
            provider=self.name,
            job_id=str(job_id),
            started_at=time.time(),
            poll_url=f"https://api.elevenlabs.io/v1/music/{job_id}",
            extra={"duration_seconds": duration_seconds},
        )

    def _status(self, handle: JobHandle, headers: dict[str, str]) -> dict[str, Any] | None:
        """One poll tick: None means still running, a dict means done."""
        data = _http.poll_get(self.name, handle.poll_url, headers=headers).json()
        status = (data.get("status") or "").lower()
        if status in {"failed", "error", "canceled"}:
            raise ProviderError(self.name, None, f"job {handle.job_id} {status}")
        if status in {"completed", "succeeded", "ready", "done"}:
            return data
        return None

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        if handle.job_id == "inline":
            return GenerationResult(
                content=handle.extra["inline_bytes"],
                mime="audio/mpeg",
                extension="mp3",
                extra={"duration_seconds": handle.extra.get("duration_seconds")},
            )

        headers = self._headers()
        final = poll_until(
            lambda: self._status(handle, headers), provider=self.name, timeout=timeout
        )

        audio_url = final.get("audio_url") or final.get("output_url") or final.get("url")
        if not audio_url:
            raise ProviderError(self.name, None, "completed job missing audio_url")

        return GenerationResult(
            content=_http.download(self.name, audio_url),
            mime="audio/mpeg",
            extension="mp3",
            extra=handle.extra,
        )


class ElevenTtsProvider(Provider):
    name = "eleven-tts"
    modality = "audio"
    requires_env = ("ELEVENLABS_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        text: str = kwargs.get("prompt") or kwargs.get("text") or ""
        return cost.estimate(self.name, char_count=len(text), variants=kwargs.get("variants", 1))

    @staticmethod
    def _voice_settings(model_id: str, kwargs: dict[str, Any]) -> dict[str, float]:
        """v3 rejects the v2 similarity_boost knob, so only send what the model takes.

        Both families accept an explicit stability; nothing is sent unless asked for,
        which lets the vendor's own per-voice defaults stand.
        """
        settings: dict[str, float] = {}
        if "stability" in kwargs:
            settings["stability"] = float(kwargs["stability"])
        if model_id.startswith("eleven_v3"):
            return settings
        settings.setdefault("stability", 0.5)
        settings["similarity_boost"] = float(kwargs.get("similarity_boost", 0.75))
        return settings

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        self.ensure_available()
        # Accept either --voice-id (explicit) or --voice (generic, also used by
        # gpt-4o-mini-tts). voice_id wins if both set.
        voice_id: str = kwargs.get("voice_id") or kwargs.get("voice") or DEFAULT_VOICE_ID
        model_id: str = kwargs.get("model_id", DEFAULT_TTS_MODEL)
        body: dict[str, Any] = {"text": prompt, "model_id": model_id}
        voice_settings = self._voice_settings(model_id, kwargs)
        if voice_settings:
            body["voice_settings"] = voice_settings
        headers = {
            "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        # TTS is synchronous and returns the audio inline, so it gets a longer
        # timeout than a job submission.
        resp = _http.post(
            self.name,
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            json=body,
            headers=headers,
            timeout=120,
        )

        return GenerationResult(
            content=resp.content,
            mime="audio/mpeg",
            extension="mp3",
            extra={"voice_id": voice_id, "model_id": model_id, "char_count": len(prompt)},
        )


from ..config import register

register(ElevenMusicProvider())
register(ElevenTtsProvider())
