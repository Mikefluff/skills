"""Suno music provider — suno-v5-5 via official or gateway Suno API.
Vendor: Suno (https://api.suno.com), gated behind SUNO_API_ENABLED=1.
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


class SunoV55Provider(Provider):
    name = "suno-v5-5"
    modality = "music"
    requires_env = ("SUNO_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return cost.estimate(self.name, variants=kwargs.get("variants", 1))

    def _gate(self) -> None:
        if os.environ.get("SUNO_API_ENABLED") != "1":
            raise ProviderError(
                self.name,
                None,
                "Suno API surface varies between official and third-party gateways. "
                "Set SUNO_API_ENABLED=1 and (optionally) SUNO_API_URL to opt in.",
            )

    def _base_url(self) -> str:
        return os.environ.get("SUNO_API_URL", "https://api.suno.com/v1").rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {os.environ['SUNO_API_KEY']}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _job_id(payload: Any) -> str | None:
        """Official Suno and the gateways each name the job differently."""
        if isinstance(payload, list):
            return payload[0].get("id") if payload else None
        return (
            payload.get("id")
            or payload.get("task_id")
            or (payload.get("data") or {}).get("id")
        )

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        self._gate()

        instrumental = bool(kwargs.get("instrumental", False))
        body: dict[str, Any] = {
            "prompt": prompt,
            "make_instrumental": instrumental,
            "model_version": kwargs.get("model_version", "v5.5"),
        }
        if kwargs.get("lyrics"):
            body["lyrics"] = kwargs["lyrics"]
        for optional in ("title", "tags"):
            if optional in kwargs:
                body[optional] = kwargs[optional]

        base = self._base_url()
        resp = _http.post(self.name, f"{base}/generate", json=body, headers=self._headers())

        job_id = self._job_id(resp.json())
        if not job_id:
            raise ProviderError(self.name, resp.status_code, "no job id in response")

        return JobHandle(
            provider=self.name,
            job_id=str(job_id),
            started_at=time.time(),
            poll_url=f"{base}/generate/{job_id}",
            extra={"instrumental": instrumental},
        )

    def _status(self, handle: JobHandle, headers: dict[str, str]) -> dict[str, Any] | None:
        """One poll tick: None means still running, a dict means done."""
        data = _http.poll_get(self.name, handle.poll_url, headers=headers).json()
        node = data.get("data") if isinstance(data.get("data"), dict) else data
        status = (node.get("status") or "").lower()
        if status in {"failed", "error"}:
            raise ProviderError(
                self.name, None, f"job {handle.job_id} failed: {node.get('error', '')}"
            )
        if status in {"complete", "completed", "succeeded", "done"}:
            return node
        # Some gateways never set a terminal status and just start serving audio.
        if node.get("audio_url") or node.get("audio"):
            return node
        return None

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        self._gate()
        headers = self._headers()

        final = poll_until(
            lambda: self._status(handle, headers), provider=self.name, timeout=timeout
        )

        audio_url = (
            final.get("audio_url")
            or final.get("audio")
            or (final.get("output") or {}).get("audio_url")
        )
        if not audio_url:
            raise ProviderError(self.name, None, "completed job missing audio_url")

        return GenerationResult(
            content=_http.download(self.name, audio_url),
            mime="audio/mpeg",
            extension="mp3",
            extra=handle.extra,
        )


from ..config import register

register(SunoV55Provider())
