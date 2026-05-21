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

import requests

from .. import cost
from ..errors import ProviderError, QuotaError
from ..poll import poll_until
from .base import GenerationResult, JobHandle, Provider


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


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

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()

        image_url = kwargs.get("image_url")
        if not image_url:
            raise ProviderError(self.name, None, "image_url is required for Kling image-to-video")

        duration = str(int(kwargs.get("duration", self.default_duration)))
        mode = kwargs.get("mode", "std")
        model_name = kwargs.get("model_name", "kling-v3")

        body: dict[str, Any] = {
            "model_name": model_name,
            "image": image_url,
            "prompt": prompt,
            "duration": duration,
            "mode": mode,
        }
        if "negative_prompt" in kwargs:
            body["negative_prompt"] = kwargs["negative_prompt"]
        if "cfg_scale" in kwargs:
            body["cfg_scale"] = kwargs["cfg_scale"]

        host = self._host()
        url = f"{host}/v1/videos/image2video"

        try:
            resp = requests.post(url, json=body, headers=self._headers(), timeout=60)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            raise QuotaError(self.name, 429, resp.text[:500])
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.status_code, resp.text[:500])

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
            extra={"duration": int(duration), "mode": mode, "model_name": model_name},
        )

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        def _check() -> dict[str, Any] | None:
            # JWT short-lived; refresh headers per poll.
            try:
                r = requests.get(handle.poll_url, headers=self._headers(), timeout=30)
            except requests.RequestException as exc:
                raise ProviderError(self.name, None, f"network error during poll: {exc}") from exc
            if r.status_code == 429:
                raise QuotaError(self.name, 429, r.text[:500])
            if r.status_code >= 400:
                raise ProviderError(self.name, r.status_code, r.text[:500])
            body = r.json()
            data = body.get("data") or {}
            status = (data.get("task_status") or body.get("status") or "").lower()
            if status in {"failed", "error"}:
                msg = data.get("task_status_msg") or body.get("message") or "failed"
                raise ProviderError(self.name, None, f"task {handle.job_id} failed: {msg}")
            if status in {"succeed", "succeeded", "completed"}:
                return data
            return None

        final = poll_until(_check, provider=self.name, timeout=timeout)

        videos = (final.get("task_result") or {}).get("videos") or []
        if not videos:
            raise ProviderError(self.name, None, "completed task has no videos array")
        video_url = videos[0].get("url")
        if not video_url:
            raise ProviderError(self.name, None, "video entry missing url")

        try:
            asset = requests.get(video_url, timeout=180)
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


from ..config import register

register(Kling3Provider())
