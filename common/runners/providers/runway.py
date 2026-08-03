"""Runway providers — gen-4, gen-4-turbo (I2V), aleph (V2V).
Vendor: Runway ML developer API (https://api.dev.runwayml.com).
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

_API_BASE = "https://api.dev.runwayml.com/v1"
_API_VERSION = "2024-11-06"

_MIME_BY_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def _to_uri(ref: str) -> str:
    """Runway wants an http(s) URL or a data URI. Local paths become data URIs."""
    if ref.startswith(("http://", "https://", "data:")):
        return ref
    from base64 import b64encode
    from pathlib import Path

    p = Path(ref)
    if p.exists():
        mime = _MIME_BY_EXT.get(p.suffix.lower(), "image/png")
        return f"data:{mime};base64,{b64encode(p.read_bytes()).decode()}"
    return ref


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
        resp = _http.post(
            self.name,
            f"{_API_BASE}/{self.endpoint_path}",
            json=body,
            headers=self._headers(),
        )

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

    def _status(self, handle: JobHandle, headers: dict[str, str]) -> dict[str, Any] | None:
        """One poll tick: None means still running, a dict means done."""
        data = _http.poll_get(self.name, handle.poll_url, headers=headers).json()
        status = (data.get("status") or "").upper()
        if status in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
            raise ProviderError(
                self.name, None, f"task {handle.job_id} {status}: {data.get('failure', '')}"
            )
        if status == "SUCCEEDED":
            return data
        return None

    @staticmethod
    def _output_url(output: Any) -> str | None:
        """Runway has returned all three of these shapes across API revisions."""
        if isinstance(output, list) and output:
            return output[0] if isinstance(output[0], str) else output[0].get("url")
        if isinstance(output, str):
            return output
        if isinstance(output, dict):
            return output.get("url")
        return None

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        headers = self._headers()
        final = poll_until(
            lambda: self._status(handle, headers), provider=self.name, timeout=timeout
        )

        url = self._output_url(final.get("output"))
        if not url:
            raise ProviderError(self.name, None, "completed task has no output URL")

        return GenerationResult(
            content=_http.download(self.name, url),
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
        body: dict[str, Any] = {
            "model": self.model_id,
            "promptText": prompt,
            "duration": duration,
            "ratio": ratio,
        }
        # First/Last-Image mode — Runway's native drift lock. Mirrors the
        # google_video.py / kling.py kwarg contract: explicit last_frame wins;
        # lock_first_last=True bookends start == end, collapsing overlay-text drift.
        # (Runway has no negative_prompt parameter — that kwarg is intentionally ignored.)
        tail_ref = kwargs.get("last_frame") or kwargs.get("last_frame_image")
        if tail_ref is None and kwargs.get("lock_first_last"):
            tail_ref = image_url
        if tail_ref:
            body["promptImage"] = [
                {"uri": _to_uri(image_url), "position": "first"},
                {"uri": _to_uri(tail_ref), "position": "last"},
            ]
        else:
            body["promptImage"] = _to_uri(image_url)
        return body


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
