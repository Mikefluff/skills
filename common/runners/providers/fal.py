"""fal.ai providers — image, video, music routed through fal queue API.
Vendor: fal.ai serverless functions (https://queue.fal.run).
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
from .base import Companion, GenerationResult, JobHandle, Provider

_QUEUE_BASE = "https://queue.fal.run"


class _FalBase(Provider):
    requires_env = ("FAL_KEY",)
    default_model: str = ""
    output_key: str = ""  # "images" | "video" | "audio"
    output_extension: str = ""
    output_mime: str = ""

    # A layerize call bills per layer produced, and produces up to 17. Estimating
    # it as one image would quote $0.05 against a possible $0.57 — under, which
    # is the direction this table is not allowed to be wrong in. There is no way
    # to know the count before the call, so quote the ceiling and let the receipt
    # come in lower.
    _SET_MODEL_MARKERS = ("layerize", "layer-decomposition")
    _MAX_LAYERS = 17

    def _model_multiplier(self, kwargs: dict[str, Any]) -> int:
        model_id = str(self._model_id(kwargs) or "").lower()
        return self._MAX_LAYERS if any(m in model_id for m in self._SET_MODEL_MARKERS) else 1

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        variants = int(kwargs.get("variants") or 1) * self._model_multiplier(kwargs)
        if self.modality == "image":
            return cost.estimate("fal/any", variants=variants)
        duration = float(kwargs.get("duration_seconds", 5))
        return cost.estimate("fal/any", duration_seconds=duration, variants=variants)

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

        resp = _http.post(
            self.name,
            f"{_QUEUE_BASE}/{model_id}",
            json=body,
            headers=self._headers(),
        )

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

    def _status(self, handle: JobHandle, status_url: str, headers: dict[str, str]) -> dict[str, Any] | None:
        """One poll tick: None means still queued or running, a dict means done."""
        data = _http.poll_get(self.name, status_url, headers=headers).json()
        status = (data.get("status") or "").upper()
        if status in {"FAILED", "ERROR", "CANCELED"}:
            raise ProviderError(self.name, None, f"job {handle.job_id} {status}")
        if status == "COMPLETED":
            return data
        return None

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        headers = self._headers()
        status_url = handle.poll_url
        response_url = handle.extra.get("response_url")

        poll_until(
            lambda: self._status(handle, status_url, headers),
            provider=self.name,
            timeout=timeout,
        )

        # fal's queue separates "is it done" from "what did it produce": the
        # status endpoint never carries the result, so fetch it once at the end.
        payload = _http.get(
            self.name, response_url, headers=headers, what="network error fetching response"
        ).json()

        assets = self._asset_set(payload)
        if assets:
            return self._download_set(assets, handle)

        url = self._extract_url(payload)
        if not url:
            raise ProviderError(self.name, None, f"completed job missing {self.output_key} url")

        return GenerationResult(
            content=_http.download(self.name, url),
            mime=self.output_mime,
            extension=self.output_extension,
            extra={"model_id": handle.extra.get("model_id")},
        )

    # fal hosts models whose whole output is a set. `seedream/v5/pro/layerize`
    # decomposes an image into 2-17 transparent PNGs — background, subject, each
    # text block — and bills $0.03375 for every one of them. Returning the first
    # and dropping the rest would charge for seventeen and deliver one, with
    # nothing in the output saying so.
    _ASSET_SET_KEYS = ("layers", "outputs", "files")

    def _asset_set(self, payload: dict[str, Any]) -> list[dict[str, Any]] | None:
        """The list a set-returning model produced, or None for ordinary models."""
        for key in self._ASSET_SET_KEYS:
            node = payload.get(key)
            if isinstance(node, list) and len(node) > 1 and all(isinstance(x, dict) for x in node):
                # z_index is the stacking order; without it the caller has to
                # guess which transparent PNG goes underneath which.
                return sorted(node, key=lambda a: a.get("z_index", 0))
        return None

    def _download_set(self, assets: list[dict[str, Any]], handle: JobHandle) -> GenerationResult:
        downloaded = []
        for asset in assets:
            url = asset.get("url")
            if not url:
                raise ProviderError(self.name, None, "asset in set has no url")
            downloaded.append((asset, _http.download(self.name, url)))

        first_meta, first_bytes = downloaded[0]
        return GenerationResult(
            content=first_bytes,
            mime=self.output_mime,
            extension=self.output_extension,
            extra={
                "model_id": handle.extra.get("model_id"),
                "asset_count": len(downloaded),
                "primary_layer": first_meta.get("name") or first_meta.get("label"),
            },
            companions=tuple(
                Companion(
                    content=content,
                    mime=self.output_mime,
                    extension=self.output_extension,
                    name=str(meta.get("name") or meta.get("label") or ""),
                    meta={
                        k: meta[k]
                        for k in ("z_index", "bbox", "bounding_box", "description")
                        if k in meta
                    },
                )
                for meta, content in downloaded[1:]
            ),
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
