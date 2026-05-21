"""OpenAI Whisper transcription provider — transcribes audio/video to SRT/VTT/JSON.

Vendor: OpenAI Audio Transcriptions API.

Different from typical providers: input is a media file (not a prompt). We pass
the file path via kwargs["file_path"]; the response format is chosen via
kwargs["response_format"] ∈ {"srt", "vtt", "json", "text"}.

Returns GenerationResult.content as bytes of the chosen format.
"""

from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from typing import Any

import requests

from .. import cost
from ..errors import ProviderError, QuotaError
from .base import GenerationResult, Provider


class WhisperTranscribeProvider(Provider):
    name = "whisper-1"
    modality = "audio"
    requires_env = ("OPENAI_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        duration_min = kwargs.get("duration_minutes")
        if duration_min is None:
            return None
        return cost.estimate(self.name, duration_minutes=float(duration_min), variants=1)

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:  # noqa: ARG002 — prompt unused
        self.ensure_available()
        api_key = os.environ["OPENAI_API_KEY"]

        file_path: str | None = kwargs.get("file_path") or kwargs.get("input")
        if not file_path:
            raise ProviderError(self.name, None, "missing required kwarg 'file_path'")
        path = Path(file_path)
        if not path.is_file():
            raise ProviderError(self.name, None, f"input file not found: {file_path}")

        response_format: str = kwargs.get("response_format", "srt")
        if response_format not in ("srt", "vtt", "json", "text", "verbose_json"):
            raise ProviderError(self.name, None, f"unsupported response_format: {response_format}")

        language: str | None = kwargs.get("language")
        temperature: float = float(kwargs.get("temperature", 0.0))

        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "model": "whisper-1",
            "response_format": response_format,
            "temperature": str(temperature),
        }
        if language:
            data["language"] = language

        # OpenAI requires multipart upload; we read the file into memory (Whisper API limit is 25 MB).
        if path.stat().st_size > 25 * 1024 * 1024:
            raise ProviderError(
                self.name, None,
                "file >25 MB — Whisper API limit. Split with ffmpeg or compress audio.",
            )

        try:
            with path.open("rb") as fh:
                files = {"file": (path.name, fh, "application/octet-stream")}
                resp = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300,
                )
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            raise QuotaError(self.name, 429, resp.text[:500])
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.status_code, resp.text[:500])

        # SRT/VTT/text come back as text body; JSON comes as JSON
        if response_format in ("json", "verbose_json"):
            content_bytes = resp.content
            mime = "application/json"
            extension = "json"
        else:
            content_bytes = resp.text.encode("utf-8")
            mime = "text/plain"
            extension = response_format if response_format != "text" else "txt"

        return GenerationResult(
            content=content_bytes,
            mime=mime,
            extension=extension,
            extra={"language": language, "format": response_format},
        )


from ..config import register

register(WhisperTranscribeProvider())
