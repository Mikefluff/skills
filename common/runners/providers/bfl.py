"""Black Forest Labs Flux providers — 1.1 Pro, 2 Pro, Kontext, Schnell.
Direct REST via requests; async pattern with polling_url returned by submit."""

from __future__ import annotations

import base64
import os
import time
from decimal import Decimal
from typing import Any

import requests

from ..cost import estimate
from ..errors import ProviderError, QuotaError
from ..poll import poll_until
from .base import GenerationResult, JobHandle, Provider

_BFL_BASE = "https://api.bfl.ai"
_BFL_ENDPOINTS: dict[str, str] = {
    "flux-1-1-pro": "/v1/flux-pro-1.1",
    "flux-2-pro": "/v1/flux-2-pro",
    "flux-kontext": "/v1/flux-kontext-pro",
    "flux-schnell": "/v1/flux-pro-1.1",  # fallback — schnell endpoint not in OpenAPI spec
}

_POLLING_URLS: dict[str, str] = {}


def _wrap_status(name: str, response: requests.Response) -> ProviderError:
    status = response.status_code
    try:
        message = response.json().get("detail") or response.text
    except ValueError:
        message = response.text
    if status == 429:
        return QuotaError(name, status, str(message))
    return ProviderError(name, status, str(message))


def _encode_input_image(value: str | bytes) -> str:
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if value.startswith(("http://", "https://")):
        resp = requests.get(value, timeout=30)
        if not resp.ok:
            raise ProviderError("flux-kontext", resp.status_code, "failed to fetch input_image URL")
        return base64.b64encode(resp.content).decode("ascii")
    if value.startswith("data:"):
        return value.split(",", 1)[-1]
    with open(value, "rb") as fh:
        return base64.b64encode(fh.read()).decode("ascii")


class _FluxProvider(Provider):
    modality = "image"
    requires_env = ("BFL_API_KEY",)

    def __init__(self, name: str) -> None:
        self.name = name
        self._endpoint = _BFL_ENDPOINTS[name]

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return estimate(self.name, **kwargs)

    def _build_body(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        body: dict[str, Any] = {
            "prompt": prompt,
            "output_format": str(kwargs.get("output_format", "png")),
        }
        seed = kwargs.get("seed")
        if seed is not None:
            body["seed"] = int(seed)
        if self.name == "flux-kontext":
            aspect_ratio = kwargs.get("aspect_ratio")
            if aspect_ratio:
                body["aspect_ratio"] = str(aspect_ratio)
            input_image = kwargs.get("input_image")
            if input_image is None:
                raise ProviderError(self.name, None, "flux-kontext requires input_image")
            body["input_image"] = _encode_input_image(input_image)
        else:
            body["width"] = int(kwargs.get("width", 1024))
            body["height"] = int(kwargs.get("height", 1024))
        return body

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:
        self.ensure_available()
        body = self._build_body(prompt, **kwargs)
        url = _BFL_BASE + self._endpoint
        try:
            resp = requests.post(
                url,
                json=body,
                headers={"x-key": os.environ["BFL_API_KEY"], "Content-Type": "application/json"},
                timeout=60,
            )
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"network error: {exc}") from exc

        if not resp.ok:
            raise _wrap_status(self.name, resp)

        data = resp.json()
        job_id = data.get("id")
        polling_url = data.get("polling_url") or f"{_BFL_BASE}/v1/get_result?id={job_id}"
        if not job_id:
            raise ProviderError(self.name, None, "no id in response")
        _POLLING_URLS[job_id] = polling_url
        return JobHandle(
            provider=self.name,
            job_id=job_id,
            started_at=time.time(),
            poll_url=polling_url,
            extra={"endpoint": self._endpoint},
        )

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        polling_url = handle.poll_url or _POLLING_URLS.get(handle.job_id)
        if polling_url is None:
            polling_url = f"{_BFL_BASE}/v1/get_result?id={handle.job_id}"
        headers = {"x-key": os.environ["BFL_API_KEY"]}

        def _check() -> dict[str, Any] | None:
            try:
                r = requests.get(polling_url, headers=headers, timeout=30)
            except requests.RequestException as exc:
                raise ProviderError(self.name, None, f"network error: {exc}") from exc
            if not r.ok:
                raise _wrap_status(self.name, r)
            payload = r.json()
            status = str(payload.get("status", "")).lower()
            if status == "ready":
                return payload
            if status in {"error", "failed", "content_moderated", "request_moderated"}:
                raise ProviderError(self.name, None, f"BFL status={status}")
            return None

        payload = poll_until(_check, provider=self.name, timeout=timeout)
        result = payload.get("result") or {}
        sample = result.get("sample")
        if not sample:
            raise ProviderError(self.name, None, "no sample URL in result")

        try:
            img_resp = requests.get(sample, timeout=60)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"sample download failed: {exc}") from exc
        if not img_resp.ok:
            raise _wrap_status(self.name, img_resp)

        ext = str(payload.get("result", {}).get("output_format", "png")).lower()
        mime = f"image/{'jpeg' if ext == 'jpg' else ext}"
        _POLLING_URLS.pop(handle.job_id, None)
        return GenerationResult(
            content=img_resp.content,
            mime=mime,
            extension=ext if ext in {"png", "jpg", "jpeg", "webp"} else "png",
            extra={"job_id": handle.job_id, "endpoint": self._endpoint},
        )


from ..config import register  # noqa: E402

register(_FluxProvider("flux-1-1-pro"))
register(_FluxProvider("flux-2-pro"))
register(_FluxProvider("flux-kontext"))
register(_FluxProvider("flux-schnell"))
