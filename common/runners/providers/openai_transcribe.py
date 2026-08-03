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
from ..errors import ProviderError
from . import _http
from .base import GenerationResult, Provider

FORMATS = ("srt", "vtt", "json", "text", "verbose_json")
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # Whisper API limit


def _decode(resp: requests.Response, response_format: str) -> tuple[bytes, str, str]:
    """(content, mime, extension). SRT/VTT/text arrive as a text body, JSON as JSON."""
    if response_format in ("json", "verbose_json"):
        return resp.content, "application/json", "json"
    extension = response_format if response_format != "text" else "txt"
    return resp.text.encode("utf-8"), "text/plain", extension


class WhisperTranscribeProvider(Provider):
    name = "whisper-1"
    modality = "audio"
    requires_env = ("OPENAI_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        duration_min = kwargs.get("duration_minutes")
        if duration_min is None:
            return None
        return cost.estimate(self.name, duration_minutes=float(duration_min), variants=1)

    def _resolve_input(self, kwargs: dict[str, Any]) -> Path:
        """Fail before the upload rather than after — a 25 MB POST is not free."""
        file_path = kwargs.get("file_path") or kwargs.get("input")
        if not file_path:
            raise ProviderError(self.name, None, "missing required kwarg 'file_path'")
        path = Path(file_path)
        if not path.is_file():
            raise ProviderError(self.name, None, f"input file not found: {file_path}")
        if path.stat().st_size > MAX_UPLOAD_BYTES:
            raise ProviderError(
                self.name, None,
                "file >25 MB — Whisper API limit. Split with ffmpeg or compress audio.",
            )
        return path

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:  # noqa: ARG002 — prompt unused
        self.ensure_available()
        path = self._resolve_input(kwargs)

        response_format: str = kwargs.get("response_format", "srt")
        if response_format not in FORMATS:
            raise ProviderError(self.name, None, f"unsupported response_format: {response_format}")

        language: str | None = kwargs.get("language")
        headers = {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}
        data = {
            "model": "whisper-1",
            "response_format": response_format,
            "temperature": str(float(kwargs.get("temperature", 0.0))),
        }
        if language:
            data["language"] = language

        with path.open("rb") as fh:
            resp = _http.post(
                self.name,
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                data=data,
                files={"file": (path.name, fh, "application/octet-stream")},
                timeout=300,
            )

        content, mime, extension = _decode(resp, response_format)
        return GenerationResult(
            content=content,
            mime=mime,
            extension=extension,
            extra={"language": language, "format": response_format},
        )


from ..config import register

register(WhisperTranscribeProvider())
