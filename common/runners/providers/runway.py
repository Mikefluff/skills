"""Runway providers — gen-4, gen-4-turbo (I2V), aleph (V2V).
Vendor: Runway ML developer API (https://api.dev.runwayml.com).
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

_API_BASE = "https://api.dev.runwayml.com/v1"
_API_VERSION = "2024-11-06"


class _RunwayBase(Provider):
    modality = "video"
    requires_env = ("RUNWAY_API_KEY",)
    model_id: str = ""
    default_duration: int = 5
    endpoint_path: str = ""  # "image_to_video" or "video_to_video"

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        duration = float(kwargs.get("duration", self.default_duration))
        return cost.estimate(self.name, duration_seconds=duration, variants=kwargs.get("variants", 1))

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {os.environ['RUNWAY_API_KEY']}",
            "Content-Type": "application/json",
            "X-Runway-Version": _API_VERSION,
        }

    def _build_body(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        body = self._build_body(prompt, **kwargs)
        url = f"{_API_BASE}/{self.endpoint_path}"

        try:
            resp = requests.post(url, json=body, headers=self._headers(), timeout=60)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            raise QuotaError(self.name, 429, resp.text[:500])
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.status_code, resp.text[:500])

        payload = resp.json()
        task_id = payload.get("id") or payload.get("task_id")
        if not task_id:
            raise ProviderError(self.name, resp.status_code, "no task id in response")

        return JobHandle(
            provider=self.name,
            job_id=str(task_id),
            started_at=time.time(),
            poll_url=f"{_API_BASE}/tasks/{task_id}",
            extra={"duration": body.get("duration", self.default_duration)},
        )

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
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
            status = (data.get("status") or "").upper()
            if status in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
                raise ProviderError(self.name, None, f"task {handle.job_id} {status}: {data.get('failure', '')}")
            if status == "SUCCEEDED":
                return data
            return None

        final = poll_until(_check, provider=self.name, timeout=timeout)

        output = final.get("output")
        url = None
        if isinstance(output, list) and output:
            url = output[0] if isinstance(output[0], str) else output[0].get("url")
        elif isinstance(output, str):
            url = output
        elif isinstance(output, dict):
            url = output.get("url")

        if not url:
            raise ProviderError(self.name, None, "completed task has no output URL")

        try:
            asset = requests.get(url, timeout=180)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"download failed: {exc}") from exc
        if asset.status_code >= 400:
            raise ProviderError(self.name, asset.status_code, "asset download failed")

        return GenerationResult(
            content=asset.content,
            mime="video/mp4",
            extension="mp4",
            extra=handle.extra,
        )


class _RunwayI2V(_RunwayBase):
    endpoint_path = "image_to_video"

    def _build_body(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        image_url = kwargs.get("image_url") or kwargs.get("promptImage")
        if not image_url:
            raise ProviderError(self.name, None, "image_url is required for image-to-video")
        duration = int(kwargs.get("duration", self.default_duration))
        ratio = kwargs.get("ratio", "1280:720")
        return {
            "model": self.model_id,
            "promptText": prompt,
            "promptImage": image_url,
            "duration": duration,
            "ratio": ratio,
        }


class Gen4Provider(_RunwayI2V):
    name = "gen-4"
    model_id = "gen4"
    default_duration = 5


class Gen4TurboProvider(_RunwayI2V):
    name = "gen-4-turbo"
    model_id = "gen4_turbo"
    default_duration = 5


class AlephProvider(_RunwayBase):
    name = "aleph"
    model_id = "aleph"
    endpoint_path = "video_to_video"
    default_duration = 5

    def _build_body(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        video_url = kwargs.get("video_url") or kwargs.get("videoUri")
        if not video_url:
            raise ProviderError(self.name, None, "video_url is required for video-to-video")
        duration = int(kwargs.get("duration", self.default_duration))
        body: dict[str, Any] = {
            "model": self.model_id,
            "videoUri": video_url,
            "promptText": prompt,
            "duration": duration,
        }
        if "ratio" in kwargs:
            body["ratio"] = kwargs["ratio"]
        return body


from ..config import register

register(Gen4Provider())
register(Gen4TurboProvider())
register(AlephProvider())
