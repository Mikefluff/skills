"""Tripo — text-to-3D and image-to-3D, the collection's first `model` provider.

Verified against developers.tripo3d.ai/en/docs/quick-start on 2026-08-08:

    POST https://openapi.tripo3d.ai/v3/generation/text-to-model
    GET  https://openapi.tripo3d.ai/v3/tasks/{task_id}
    Authorization: Bearer <TRIPO_API_KEY>
    status ∈ {success, failed, cancelled, banned}
    finished file at output.model_url

The one thing that makes this different from every other async provider here:
**a finished model URL expires five minutes after the task succeeds.** Handing
the URL back and downloading later — which is what a video provider can get away
with — loses an asset the user has already been billed for. So `poll` downloads
inside the same call that observes success, and the URL never leaves this module.
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

BASE = "https://openapi.tripo3d.ai/v3"

# Pinned. The model string is dated by the vendor, which is the good kind of
# version pin: a silent upgrade would change geometry and price under a caller
# who asked for neither.
DEFAULT_MODEL = "v3.1-20260211"

_TERMINAL_FAILURES = {"failed", "cancelled", "banned"}


class TripoProvider(Provider):
    name = "tripo-v3"
    modality = "model"
    requires_env = ("TRIPO_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return cost.estimate(self.name, variants=int(kwargs.get("variants", 1) or 1))

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {os.environ['TRIPO_API_KEY']}",
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()

        image_url = kwargs.get("image_url")
        path = "/generation/image-to-model" if image_url else "/generation/text-to-model"

        body: dict[str, Any] = {"model": kwargs.get("model_version") or DEFAULT_MODEL}
        if image_url:
            body["image_url"] = image_url
            if prompt:
                body["prompt"] = prompt
        else:
            body["prompt"] = prompt

        for key in ("texture", "pbr", "texture_quality", "face_limit", "style"):
            if kwargs.get(key) is not None:
                body[key] = kwargs[key]

        resp = _http.post(self.name, f"{BASE}{path}", json=body, headers=self._headers())
        payload = resp.json()
        task_id = (payload.get("data") or {}).get("task_id") or payload.get("task_id")
        if not task_id:
            raise ProviderError(self.name, resp.status_code, f"no task_id in response: {payload}")

        return JobHandle(
            provider=self.name,
            job_id=str(task_id),
            started_at=time.time(),
            poll_url=f"{BASE}/tasks/{task_id}",
            extra={"model_version": body["model"], "textured": bool(body.get("texture", True))},
        )

    def _status(self, handle: JobHandle) -> dict[str, Any] | None:
        """One poll tick. None means still running; a dict means finished."""
        payload = _http.poll_get(self.name, handle.poll_url, headers=self._headers()).json()
        data = payload.get("data") or payload
        status = str(data.get("status") or "").lower()
        if status in _TERMINAL_FAILURES:
            reason = data.get("message") or data.get("error") or status
            raise ProviderError(self.name, None, f"task {handle.job_id} {status}: {reason}")
        if status == "success":
            return data
        return None

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        data = poll_until(
            lambda: self._status(handle),
            provider=self.name,
            timeout=timeout,
        )

        output = (data or {}).get("output") or {}
        url = output.get("model_url") or output.get("model")
        if not url:
            raise ProviderError(self.name, None, f"task {handle.job_id} succeeded with no model_url")

        # Download now. The URL is valid for five minutes, and the asset is
        # already paid for — returning a link that expires is losing it.
        content = _http.download(self.name, url)
        extension = _extension_for(url)

        return GenerationResult(
            content=content,
            mime={"glb": "model/gltf-binary", "usdz": "model/vnd.usdz+zip"}.get(
                extension, "application/octet-stream"
            ),
            extension=extension,
            extra={
                "task_id": handle.job_id,
                "model_version": handle.extra.get("model_version"),
                "consumed_credit": data.get("consumed_credit"),
            },
        )


def _extension_for(url: str) -> str:
    """Tripo serves glb by default; honour whatever the URL actually ends in."""
    tail = url.split("?", 1)[0].rsplit(".", 1)
    if len(tail) == 2 and 2 <= len(tail[1]) <= 5:
        return tail[1].lower()
    return "glb"


from ..config import register  # noqa: E402

register(TripoProvider())
