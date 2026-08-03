"""Kling video provider — kling-3 (image-to-video) via Kuaishou Kling API.
Vendor: Kuaishou Kling (https://api.klingai.com), JWT HS256 auth.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from decimal import Decimal
from typing import Any

from .. import cost
from ..errors import ProviderError
from ..poll import poll_until
from . import _http
from .base import GenerationResult, JobHandle, Provider


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _image_payload(ref: str) -> str:
    """Kling accepts a URL or a base64 string. Local paths are read + base64-encoded."""
    if ref.startswith(("http://", "https://")):
        return ref
    from pathlib import Path

    p = Path(ref)
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return ref


def _make_jwt(access_key_id: str, access_key_secret: str, ttl_seconds: int = 1800) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "iss": access_key_id,
        "exp": now + ttl_seconds,
        "nbf": now - 5,
    }
    header_b64 = _b64url(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    msg = f"{header_b64}.{payload_b64}"
    sig = _b64url(hmac.new(access_key_secret.encode(), msg.encode(), hashlib.sha256).digest())
    return f"{msg}.{sig}"


class Kling3Provider(Provider):
    name = "kling-3"
    modality = "video"
    requires_env = ("KLING_ACCESS_KEY_ID", "KLING_ACCESS_KEY_SECRET")
    default_duration: int = 5

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        duration = float(kwargs.get("duration", self.default_duration))
        return cost.estimate(self.name, duration_seconds=duration, variants=kwargs.get("variants", 1))

    def _host(self) -> str:
        return os.environ.get("KLING_API_HOST", "https://api.klingai.com").rstrip("/")

    def _headers(self) -> dict[str, str]:
        token = _make_jwt(
            os.environ["KLING_ACCESS_KEY_ID"],
            os.environ["KLING_ACCESS_KEY_SECRET"],
        )
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _body(self, prompt: str, image_url: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model_name": kwargs.get("model_name", "kling-v3"),
            "image": _image_payload(image_url),
            "prompt": prompt,
            "duration": str(int(kwargs.get("duration", self.default_duration))),
            "mode": kwargs.get("mode", "std"),
        }
        if "negative_prompt" in kwargs:
            body["negative_prompt"] = kwargs["negative_prompt"]
        if "cfg_scale" in kwargs:
            body["cfg_scale"] = kwargs["cfg_scale"]
        # Last-frame bookend — Kling's native drift lock (`image_tail`). Mirrors the
        # google_video.py kwarg contract: explicit image_tail / last_frame wins;
        # lock_first_last=True bookends with the first frame (start == end), which
        # collapses overlay-text drift the same way Veo's last_frame does.
        tail_ref = kwargs.get("image_tail") or kwargs.get("last_frame") or kwargs.get("last_frame_image")
        if tail_ref is None and kwargs.get("lock_first_last"):
            tail_ref = image_url
        if tail_ref:
            body["image_tail"] = _image_payload(tail_ref)
        return body

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()

        image_url = kwargs.get("image_url")
        if not image_url:
            raise ProviderError(self.name, None, "image_url is required for Kling image-to-video")

        body = self._body(prompt, image_url, kwargs)
        host = self._host()
        resp = _http.post(
            self.name,
            f"{host}/v1/videos/image2video",
            json=body,
            headers=self._headers(),
        )

        payload = resp.json()
        data = payload.get("data") or {}
        task_id = data.get("task_id") or payload.get("task_id")
        if not task_id:
            raise ProviderError(self.name, resp.status_code, "no task_id in response")

        return JobHandle(
            provider=self.name,
            job_id=str(task_id),
            started_at=time.time(),
            poll_url=f"{host}/v1/videos/image2video/{task_id}",
            extra={
                "duration": int(body["duration"]),
                "mode": body["mode"],
                "model_name": body["model_name"],
            },
        )

    def _status(self, handle: JobHandle) -> dict[str, Any] | None:
        """One poll tick: None means still running, a dict means done."""
        # JWT is short-lived, so headers are rebuilt on every tick.
        payload = _http.poll_get(self.name, handle.poll_url, headers=self._headers()).json()
        data = payload.get("data") or {}
        status = (data.get("task_status") or payload.get("status") or "").lower()
        if status in {"failed", "error"}:
            msg = data.get("task_status_msg") or payload.get("message") or "failed"
            raise ProviderError(self.name, None, f"task {handle.job_id} failed: {msg}")
        if status in {"succeed", "succeeded", "completed"}:
            return data
        return None

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        final = poll_until(lambda: self._status(handle), provider=self.name, timeout=timeout)

        videos = (final.get("task_result") or {}).get("videos") or []
        if not videos:
            raise ProviderError(self.name, None, "completed task has no videos array")
        video_url = videos[0].get("url")
        if not video_url:
            raise ProviderError(self.name, None, "video entry missing url")

        return GenerationResult(
            content=_http.download(self.name, video_url),
            mime="video/mp4",
            extension="mp4",
            extra=handle.extra,
        )


from ..config import register

register(Kling3Provider())
