"""ElevenLabs providers — eleven-music (async) and eleven-tts (sync).
Vendor: ElevenLabs Music + Text-to-Speech APIs.
"""

from __future__ import annotations

import os
import time
from decimal import Decimal
from typing import Any

import requests

from .. import cost
from ..errors import ProviderError, QuotaError
from ..poll import poll_until
from .base import GenerationResult, JobHandle, Provider

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # "Rachel" — ElevenLabs default preset.


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

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()

        duration_seconds = int(kwargs.get("duration_seconds", 30))
        lyrics: str | None = kwargs.get("lyrics")
        composition_plan: dict | None = kwargs.get("composition_plan")

        body: dict[str, Any] = {
            "prompt": prompt,
            "duration_seconds": duration_seconds,
        }
        if lyrics is not None:
            body["lyrics"] = lyrics
        if composition_plan is not None:
            body["composition_plan"] = composition_plan

        try:
            resp = requests.post(
                "https://api.elevenlabs.io/v1/music",
                json=body,
                headers=self._headers(),
                timeout=60,
            )
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            raise QuotaError(self.name, 429, resp.text[:500])
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.status_code, resp.text[:500])

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

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        if handle.job_id == "inline":
            return GenerationResult(
                content=handle.extra["inline_bytes"],
                mime="audio/mpeg",
                extension="mp3",
                extra={"duration_seconds": handle.extra.get("duration_seconds")},
            )

        headers = self._headers()

        def _check() -> dict[str, Any] | None:
            try:
                r = requests.get(handle.poll_url, headers=headers, timeout=30)
            except requests.RequestException as exc:
                raise ProviderError(self.name, None, f"network error during poll: {exc}") from exc
            if r.status_code == 429:
                raise QuotaError(self.name, 429, r.text[:500])
            if r.status_code >= 400:
                raise ProviderError(self.name, r.status_code, r.text[:500])
            data = r.json()
            status = (data.get("status") or "").lower()
            if status in {"failed", "error", "canceled"}:
                raise ProviderError(self.name, None, f"job {handle.job_id} {status}")
            if status in {"completed", "succeeded", "ready", "done"}:
                return data
            return None

        final = poll_until(_check, provider=self.name, timeout=timeout)
        audio_url = final.get("audio_url") or final.get("output_url") or final.get("url")
        if not audio_url:
            raise ProviderError(self.name, None, "completed job missing audio_url")

        try:
            download = requests.get(audio_url, timeout=180)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"download failed: {exc}") from exc
        if download.status_code >= 400:
            raise ProviderError(self.name, download.status_code, "download failed")

        return GenerationResult(
            content=download.content,
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

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        self.ensure_available()
        voice_id: str = kwargs.get("voice_id", DEFAULT_VOICE_ID)
        model_id: str = kwargs.get("model_id", "eleven_multilingual_v2")
        body = {
            "text": prompt,
            "model_id": model_id,
            "voice_settings": {
                "stability": float(kwargs.get("stability", 0.5)),
                "similarity_boost": float(kwargs.get("similarity_boost", 0.75)),
            },
        }
        headers = {
            "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        try:
            resp = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                json=body,
                headers=headers,
                timeout=120,
            )
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            raise QuotaError(self.name, 429, resp.text[:500])
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.status_code, resp.text[:500])

        return GenerationResult(
            content=resp.content,
            mime="audio/mpeg",
            extension="mp3",
            extra={"voice_id": voice_id, "model_id": model_id, "char_count": len(prompt)},
        )


from ..config import register

register(ElevenMusicProvider())
register(ElevenTtsProvider())
