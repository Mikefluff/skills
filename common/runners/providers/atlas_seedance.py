"""Seedance 2.5 reference-to-video through Atlas Cloud — the route that takes the cast's faces.
Vendor: Atlas Cloud (https://api.atlascloud.ai/api/v1/model/generateVideo), routed to ByteDance Seedance.

Seedance refuses a photoreal face in a reference unless it sits in a portrait asset library
(`asset://<id>`); OpenRouter forwards no such thing, so its Seedance sees our generated cast as real
people and fails the shot (`PrivacyInformation`). Atlas registers every reference image as an asset
itself, so the same request carries the cast's portraits, the place, the storyboard frame and the clay
previs as one generation. Local files go inline as base64 data URIs: nothing is put on a public host.

Takes the kwargs of the other Seedance providers: reference_images, reference_videos, reference_audio,
duration_seconds, resolution, aspect_ratio, generate_audio. With first_frame (and last_frame) the shot goes to
Seedance 2.5 image-to-video instead: a transition drawn from one shot's last frame to the next one's first.
"""

from __future__ import annotations

import base64
import mimetypes
import os
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import cost
from ..errors import ProviderError
from ..poll import poll_until
from . import _http
from .base import GenerationResult, JobHandle, Provider

_BASE = "https://api.atlascloud.ai/api/v1/model"
_NAME = "atlas-seedance-2-5"
_I2V = "bytedance/seedance-2.5/image-to-video"  # `image` = first frame, `last_image` = last frame, 4-30 s


def _inline(ref: str) -> str:
    """A URL as-is; a local file as a data URI."""
    if ref.startswith(("https://", "http://", "data:", "asset://")):
        return ref
    path = Path(ref)
    if not path.is_file():
        raise ProviderError(_NAME, None, f"reference not found: {ref}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    data = path.read_bytes()
    if mime.startswith("image/"):
        # A 2K PNG portrait is 1.6 MB, a quarter of a request that then timed out on submit (Atlas registers and
        # reviews each image while it accepts the job). A 1600 px JPEG carries the same face at a sixth.
        from io import BytesIO

        from PIL import Image

        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((1600, 1600))
            buf = BytesIO()
            im.save(buf, "JPEG", quality=90)
        data, mime = buf.getvalue(), "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


class AtlasSeedance25Provider(Provider):
    name = _NAME
    modality = "video"
    requires_env = ("ATLASCLOUD_API_KEY",)
    model_id = "bytedance/seedance-2.5/reference-to-video"

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return cost.estimate(self.name, duration_seconds=kwargs.get("duration_seconds", 5),
                             variants=kwargs.get("variants", 1))

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {os.environ['ATLASCLOUD_API_KEY']}", "Content-Type": "application/json"}

    def build_body(self, prompt: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        if kwargs.get("first_frame"):
            # A shot pinned at both ends (a transition the generation draws: the last frame of one shot to the
            # first of the next) goes to image-to-video, whose first and last frames are inputs.
            body = {"model": _I2V, "prompt": prompt, "image": _inline(str(kwargs["first_frame"])),
                    "duration": int(kwargs.get("duration_seconds", 5)), "resolution": kwargs.get("resolution") or "480p",
                    # the vendor takes the ratio from the first frame and refuses any other value
                    "ratio": "adaptive", "generate_audio": bool(kwargs.get("generate_audio", True))}
            if kwargs.get("last_frame"):
                body["last_image"] = _inline(str(kwargs["last_frame"]))
            return body
        body: dict[str, Any] = {
            "model": self.model_id,
            "prompt": prompt,
            "duration": int(kwargs.get("duration_seconds", 5)),
            "resolution": kwargs.get("resolution") or "480p",
            "ratio": kwargs.get("aspect_ratio") or "16:9",
            "generate_audio": bool(kwargs.get("generate_audio", True)),
        }
        for key, wire in (("reference_images", "reference_images"), ("reference_videos", "reference_videos"),
                          ("reference_audio", "reference_audios")):
            refs = kwargs.get(key) or []
            if refs:
                body[wire] = [_inline(str(r)) for r in refs]
        return body

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        resp = _http.post(self.name, f"{_BASE}/generateVideo", json=self.build_body(prompt, kwargs),
                          headers=self._headers(), timeout=600)
        data = resp.json().get("data") or {}
        if not data.get("id"):
            raise ProviderError(self.name, resp.status_code, f"no prediction id: {resp.text[:300]}")
        return JobHandle(provider=self.name, job_id=str(data["id"]), started_at=time.time(),
                         poll_url=f"{_BASE}/prediction/{data['id']}")

    def _status(self, handle: JobHandle) -> dict[str, Any] | None:
        data = _http.poll_get(self.name, handle.poll_url, headers=self._headers()).json().get("data") or {}
        status = (data.get("status") or "").lower()
        if status == "failed":
            raise ProviderError(self.name, None, f"prediction {handle.job_id} failed: {data.get('error')}")
        return data if status in ("completed", "succeeded") else None

    def poll(self, handle: JobHandle, timeout: float = 900.0) -> GenerationResult:
        final = poll_until(lambda: self._status(handle), provider=self.name, timeout=timeout)
        outputs = final.get("outputs") or []
        url = outputs[0] if outputs and isinstance(outputs[0], str) else (outputs[0] or {}).get("url") if outputs else None
        if not url:
            raise ProviderError(self.name, None, f"prediction {handle.job_id} finished without a video: {final}")
        return GenerationResult(content=_http.download(self.name, url), mime="video/mp4", extension="mp4",
                                extra={"model_id": self.model_id, "prediction": handle.job_id})


from ..config import register

register(AtlasSeedance25Provider())
