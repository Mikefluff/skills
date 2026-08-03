"""Replicate providers — image, video, music routed through Replicate predictions API.
Vendor: Replicate (https://api.replicate.com).
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

_API_BASE = "https://api.replicate.com/v1"


class _ReplicateBase(Provider):
    requires_env = ("REPLICATE_API_TOKEN",)
    default_model: str = ""  # "owner/model" or "owner/model:version"
    output_extension: str = ""
    output_mime: str = ""

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        if self.modality == "image":
            return cost.estimate("replicate/any", variants=kwargs.get("variants", 1))
        duration = float(kwargs.get("duration_seconds", 5))
        return cost.estimate("replicate/any", duration_seconds=duration, variants=kwargs.get("variants", 1))

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {os.environ['REPLICATE_API_TOKEN']}",
            "Content-Type": "application/json",
        }

    def _model_id(self, kwargs: dict[str, Any]) -> str:
        return kwargs.get("replicate_model") or self.default_model

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        model_id = self._model_id(kwargs)

        input_payload: dict[str, Any] = {"prompt": prompt}
        for k, v in kwargs.items():
            if k in {"replicate_model", "variants"} or v is None:
                continue
            input_payload[k] = v

        if ":" in model_id:
            # version-pinned form
            _, version = model_id.split(":", 1)
            url = f"{_API_BASE}/predictions"
            body: dict[str, Any] = {"version": version, "input": input_payload}
        else:
            url = f"{_API_BASE}/models/{model_id}/predictions"
            body = {"input": input_payload}

        resp = _http.post(self.name, url, json=body, headers=self._headers())

        payload = resp.json()
        prediction_id = payload.get("id")
        urls = payload.get("urls") or {}
        get_url = urls.get("get") or f"{_API_BASE}/predictions/{prediction_id}"
        if not prediction_id:
            raise ProviderError(self.name, resp.status_code, "no prediction id in response")

        return JobHandle(
            provider=self.name,
            job_id=str(prediction_id),
            started_at=time.time(),
            poll_url=get_url,
            extra={"model_id": model_id},
        )

    def _status(self, handle: JobHandle, headers: dict[str, str]) -> dict[str, Any] | None:
        """One poll tick: None means still running, a dict means done."""
        data = _http.poll_get(self.name, handle.poll_url, headers=headers).json()
        status = (data.get("status") or "").lower()
        if status in {"failed", "canceled"}:
            raise ProviderError(
                self.name, None, f"job {handle.job_id} {status}: {data.get('error', '')}"
            )
        if status == "succeeded":
            return data
        return None

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        headers = self._headers()
        final = poll_until(
            lambda: self._status(handle, headers), provider=self.name, timeout=timeout
        )

        url = self._extract_url(final.get("output"))
        if not url:
            raise ProviderError(self.name, None, "completed prediction has no output URL")

        return GenerationResult(
            content=_http.download(self.name, url),
            mime=self.output_mime,
            extension=self.output_extension,
            extra={"model_id": handle.extra.get("model_id")},
        )

    def _extract_url(self, output: Any) -> str | None:
        if isinstance(output, str):
            return output
        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return first.get("url")
        if isinstance(output, dict):
            return output.get("url") or output.get("audio") or output.get("video")
        return None


class ReplicateImageProvider(_ReplicateBase):
    name = "replicate-image"
    modality = "image"
    default_model = "black-forest-labs/flux-1.1-pro"
    output_extension = "png"
    output_mime = "image/png"


class ReplicateVideoProvider(_ReplicateBase):
    name = "replicate-video"
    modality = "video"
    default_model = "kwaivgi/kling-v1.6-pro"
    output_extension = "mp4"
    output_mime = "video/mp4"


class ReplicateMusicProvider(_ReplicateBase):
    name = "replicate-music"
    modality = "music"
    default_model = "meta/musicgen"
    output_extension = "mp3"
    output_mime = "audio/mpeg"


from ..config import register

register(ReplicateImageProvider())
register(ReplicateVideoProvider())
register(ReplicateMusicProvider())
