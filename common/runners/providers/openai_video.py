"""OpenAI video providers — sora-2 and sora-2-pro.
Vendor: OpenAI Sora 2 API (gated behind OPENAI_SORA_API_ENABLED=1).
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

        body: dict[str, Any] = {
            "model": self.model_id,
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "resolution": resolution,
        }

        # Image-to-video — accept cross-provider aliases. The Sora 2 API
        # documents image input via `input_reference` (URL or data URI).
        # If your account requires multipart/form-data upload, swap this
        # branch for the multipart variant — the gate (OPENAI_SORA_API_ENABLED)
        # already restricts who hits this code path.
        image_ref = kwargs.get("image_url") or kwargs.get("input_image")
        if image_ref:
            body["input_reference"] = image_ref

        resp = _http.post(
            self.name,
            "https://api.openai.com/v1/videos",
            json=body,
            headers=self._headers(),
        )

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

    def _status(self, handle: JobHandle, headers: dict[str, str]) -> dict[str, Any] | None:
        """One poll tick: None means still running, a dict means done."""
        data = _http.poll_get(self.name, handle.poll_url, headers=headers).json()
        status = (data.get("status") or "").lower()
        if status in {"failed", "error", "canceled"}:
            raise ProviderError(
                self.name, None, f"job {handle.job_id} {status}: {data.get('error', '')}"
            )
        if status in {"completed", "succeeded", "ready"}:
            return data
        return None

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        self._gate()
        headers = self._headers()

        final = poll_until(
            lambda: self._status(handle, headers), provider=self.name, timeout=timeout
        )

        video_url = (
            final.get("video_url")
            or final.get("output_url")
            or (final.get("output") or {}).get("url")
        )
        if not video_url:
            raise ProviderError(self.name, None, "completed job missing video_url")

        return GenerationResult(
            content=_http.download(self.name, video_url),
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
