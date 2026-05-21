"""fal.ai providers — image, video, music routed through fal queue API.
Vendor: fal.ai serverless functions (https://queue.fal.run).
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

_QUEUE_BASE = "https://queue.fal.run"


class _FalBase(Provider):
    requires_env = ("FAL_KEY",)
    default_model: str = ""
    output_key: str = ""  # "images" | "video" | "audio"
    output_extension: str = ""
    output_mime: str = ""

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        if self.modality == "image":
            return cost.estimate("fal/any", variants=kwargs.get("variants", 1))
        duration = float(kwargs.get("duration_seconds", 5))
        return cost.estimate("fal/any", duration_seconds=duration, variants=kwargs.get("variants", 1))

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Key {os.environ['FAL_KEY']}",
            "Content-Type": "application/json",
        }

    def _model_id(self, kwargs: dict[str, Any]) -> str:
        return kwargs.get("fal_model") or self.default_model

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        model_id = self._model_id(kwargs)

        body: dict[str, Any] = {"prompt": prompt}
        for k, v in kwargs.items():
            if k in {"fal_model", "variants"} or v is None:
                continue
            body[k] = v

        try:
            resp = requests.post(
                f"{_QUEUE_BASE}/{model_id}",
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
        request_id = payload.get("request_id") or payload.get("requestId")
        if not request_id:
            raise ProviderError(self.name, resp.status_code, "no request_id in response")

        status_url = payload.get("status_url") or f"{_QUEUE_BASE}/{model_id}/requests/{request_id}/status"
        response_url = payload.get("response_url") or f"{_QUEUE_BASE}/{model_id}/requests/{request_id}"

        return JobHandle(
            provider=self.name,
            job_id=str(request_id),
            started_at=time.time(),
            poll_url=status_url,
            extra={"model_id": model_id, "response_url": response_url},
        )

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        headers = self._headers()
        status_url = handle.poll_url
        response_url = handle.extra.get("response_url")

        def _check() -> dict[str, Any] | None:
            try:
                r = requests.get(status_url, headers=headers, timeout=30)
            except requests.RequestException as exc:
                raise ProviderError(self.name, None, f"network error during poll: {exc}") from exc
            if r.status_code == 429:
                raise QuotaError(self.name, 429, r.text[:500])
            if r.status_code >= 400:
                raise ProviderError(self.name, r.status_code, r.text[:500])
            data = r.json()
            status = (data.get("status") or "").upper()
            if status in {"FAILED", "ERROR", "CANCELED"}:
                raise ProviderError(self.name, None, f"job {handle.job_id} {status}")
            if status == "COMPLETED":
                return data
            return None

        poll_until(_check, provider=self.name, timeout=timeout)

        try:
            final = requests.get(response_url, headers=headers, timeout=60)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"network error fetching response: {exc}") from exc
        if final.status_code >= 400:
            raise ProviderError(self.name, final.status_code, final.text[:500])
        payload = final.json()

        url = self._extract_url(payload)
        if not url:
            raise ProviderError(self.name, None, f"completed job missing {self.output_key} url")

        try:
            asset = requests.get(url, timeout=180)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"download failed: {exc}") from exc
        if asset.status_code >= 400:
            raise ProviderError(self.name, asset.status_code, "asset download failed")

        return GenerationResult(
            content=asset.content,
            mime=self.output_mime,
            extension=self.output_extension,
            extra={"model_id": handle.extra.get("model_id")},
        )

    def _extract_url(self, payload: dict[str, Any]) -> str | None:
        node = payload.get(self.output_key)
        if isinstance(node, list) and node:
            first = node[0]
            return first.get("url") if isinstance(first, dict) else None
        if isinstance(node, dict):
            return node.get("url")
        return None


class FalImageProvider(_FalBase):
    name = "fal-image"
    modality = "image"
    default_model = "fal-ai/flux/pro/v1.1"
    output_key = "images"
    output_extension = "png"
    output_mime = "image/png"


class FalVideoProvider(_FalBase):
    name = "fal-video"
    modality = "video"
    default_model = "fal-ai/kling-video/v1.6/pro/text-to-video"
    output_key = "video"
    output_extension = "mp4"
    output_mime = "video/mp4"


class FalMusicProvider(_FalBase):
    name = "fal-music"
    modality = "music"
    default_model = "fal-ai/cassetteai/music-generator"
    output_key = "audio"
    output_extension = "mp3"
    output_mime = "audio/mpeg"


from ..config import register

register(FalImageProvider())
register(FalVideoProvider())
register(FalMusicProvider())
