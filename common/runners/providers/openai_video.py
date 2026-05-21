"""OpenAI video providers — sora-2 and sora-2-pro.
Vendor: OpenAI Sora 2 API (gated behind OPENAI_SORA_API_ENABLED=1).
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


class _SoraBase(Provider):
    modality = "video"
    requires_env = ("OPENAI_API_KEY",)
    default_duration: int = 8
    default_resolution: str = "720p"
    model_id: str = ""

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        duration = float(kwargs.get("duration_seconds", self.default_duration))
        return cost.estimate(self.name, duration_seconds=duration, variants=kwargs.get("variants", 1))

    def _gate(self) -> None:
        if os.environ.get("OPENAI_SORA_API_ENABLED") != "1":
            raise ProviderError(
                self.name,
                None,
                "Sora 2 API access is currently gated. Set OPENAI_SORA_API_ENABLED=1 once your account has Sora API access.",
            )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        self._gate()

        duration_seconds = int(kwargs.get("duration_seconds", self.default_duration))
        resolution = kwargs.get("resolution", self.default_resolution)

        body = {
            "model": self.model_id,
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "resolution": resolution,
        }

        try:
            resp = requests.post(
                "https://api.openai.com/v1/videos",
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

        payload = resp.json()
        job_id = payload.get("id") or payload.get("video_id")
        if not job_id:
            raise ProviderError(self.name, resp.status_code, "no job id in response")

        return JobHandle(
            provider=self.name,
            job_id=str(job_id),
            started_at=time.time(),
            poll_url=f"https://api.openai.com/v1/videos/{job_id}",
            extra={"duration_seconds": duration_seconds, "resolution": resolution},
        )

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        self._gate()
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
                raise ProviderError(self.name, None, f"job {handle.job_id} {status}: {data.get('error', '')}")
            if status in {"completed", "succeeded", "ready"}:
                return data
            return None

        final = poll_until(_check, provider=self.name, timeout=timeout)

        video_url = (
            final.get("video_url")
            or final.get("output_url")
            or (final.get("output") or {}).get("url")
        )
        if not video_url:
            raise ProviderError(self.name, None, "completed job missing video_url")

        try:
            download = requests.get(video_url, timeout=180)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"download failed: {exc}") from exc
        if download.status_code >= 400:
            raise ProviderError(self.name, download.status_code, "download failed")

        return GenerationResult(
            content=download.content,
            mime="video/mp4",
            extension="mp4",
            extra=handle.extra,
        )


class Sora2Provider(_SoraBase):
    name = "sora-2"
    model_id = "sora-2"
    default_duration = 8
    default_resolution = "720p"


class Sora2ProProvider(_SoraBase):
    name = "sora-2-pro"
    model_id = "sora-2-pro"
    default_duration = 12
    default_resolution = "1024p"


from ..config import register

register(Sora2Provider())
register(Sora2ProProvider())
