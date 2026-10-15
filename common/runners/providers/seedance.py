"""Seedance video providers — ByteDance Seedance 2.x, native (BytePlus ModelArk) and via fal.
Vendor: BytePlus ModelArk (https://ark.ap-southeast.bytepluses.com/api/v3) and fal.ai.

Seedance is the one video model here that takes an audio reference and lip-syncs
a character to it, which is what a voiced film needs: the ElevenLabs take goes
in as @Audio1, the character photo as @Image1, and the prompt addresses both by
those names. 2.5 renders 4-30 s in one generation, so a 30-second film has no
seams at all; 2.0 stops at 15 s.

All three providers take the same kwargs, so a plan does not change when the
route does:

  reference_images  list of paths/URLs  → @Image1, @Image2, ... in this order
  reference_videos  list of paths/URLs  → @Video1, ...
  reference_audio   list of paths/URLs  → @Audio1, ...
  first_frame / last_frame              BytePlus only; fal's reference route has none
  duration_seconds  int, model range
  aspect_ratio      "9:16" etc.
  resolution        "480p" | "720p" | "1080p"
  generate_audio    bool (default True — lip-sync output carries the speech)
  seed              int (BytePlus; fal 2.5 only)

Local files go up inline as base64 data URIs. Both routes accept them, which
spares the pipeline an upload bucket for a 30-second voice track.
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
from .fal import FalVideoProvider

_ARK_BASE = "https://ark.ap-southeast.bytepluses.com/api/v3"


def as_url(ref: str) -> str:
    """A URL stays a URL; a local file becomes a data URI."""
    if ref.startswith(("http://", "https://", "data:", "asset://")):
        return ref
    path = Path(ref)
    if not path.is_file():
        raise ProviderError("seedance", None, f"reference not found: {ref}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def _refs(kwargs: dict[str, Any], key: str) -> list[str]:
    value = kwargs.get(key) or []
    return [value] if isinstance(value, str) else list(value)


class _SeedancePricing:
    name: str

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        duration = float(kwargs.get("duration_seconds", 5))
        return cost.estimate(self.name, duration_seconds=duration, variants=kwargs.get("variants", 1))


# Short side in pixels per resolution tier; the long side follows the aspect.
_SHORT_SIDE = {"480p": 480, "720p": 720, "1080p": 1080}
_FPS = 24


def ark_tokens(duration: float, resolution: str = "720p", aspect: str = "9:16") -> int:
    """BytePlus's billing unit: seconds × width × height × fps / 1024."""
    short = _SHORT_SIDE.get(resolution, 720)
    a, b = (float(x) for x in (aspect if ":" in aspect else "16:9").split(":"))
    long_side = round(short * max(a, b) / min(a, b))
    return int(duration * short * long_side * _FPS / 1024)


class _ArkSeedance(Provider):
    modality = "video"
    requires_env = ("ARK_API_KEY",)
    model_id: str = ""

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        tokens = ark_tokens(
            float(kwargs.get("duration_seconds", 5)),
            str(kwargs.get("resolution") or "720p"),
            str(kwargs.get("aspect_ratio") or "9:16"),
        )
        return cost.estimate(self.name, tokens=tokens, variants=kwargs.get("variants", 1))

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {os.environ['ARK_API_KEY']}",
            "Content-Type": "application/json",
        }

    def _content(self, prompt: str, kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for role in ("first_frame", "last_frame"):
            if kwargs.get(role):
                content.append({"type": "image_url", "image_url": {"url": as_url(kwargs[role])}, "role": role})
        # Order is the numbering: the third reference_image is @Image3.
        for ref in _refs(kwargs, "reference_images"):
            content.append({"type": "image_url", "image_url": {"url": as_url(ref)}, "role": "reference_image"})
        for ref in _refs(kwargs, "reference_videos"):
            content.append({"type": "video_url", "video_url": {"url": as_url(ref)}, "role": "reference_video"})
        for ref in _refs(kwargs, "reference_audio"):
            content.append({"type": "audio_url", "audio_url": {"url": as_url(ref)}, "role": "reference_audio"})
        return content

    def build_body(self, prompt: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": kwargs.get("model_id") or self.model_id,
            "content": self._content(prompt, kwargs),
            "duration": int(kwargs.get("duration_seconds", 5)),
            "generate_audio": bool(kwargs.get("generate_audio", True)),
            "watermark": False,
        }
        # With a first frame the vendor only takes "adaptive"; sending 9:16 is a 400.
        if kwargs.get("first_frame"):
            body["ratio"] = "adaptive"
        elif kwargs.get("aspect_ratio"):
            body["ratio"] = kwargs["aspect_ratio"]
        for key in ("resolution", "seed"):
            if kwargs.get(key) is not None:
                body[key] = kwargs[key]
        return body

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        resp = _http.post(
            self.name,
            f"{_ARK_BASE}/contents/generations/tasks",
            json=self.build_body(prompt, kwargs),
            headers=self._headers(),
        )
        task_id = resp.json().get("id")
        if not task_id:
            raise ProviderError(self.name, resp.status_code, "no task id in response")
        return JobHandle(
            provider=self.name,
            job_id=str(task_id),
            started_at=time.time(),
            poll_url=f"{_ARK_BASE}/contents/generations/tasks/{task_id}",
        )

    def _status(self, handle: JobHandle) -> dict[str, Any] | None:
        data = _http.poll_get(self.name, handle.poll_url, headers=self._headers()).json()
        status = (data.get("status") or "").lower()
        if status in {"failed", "cancelled", "expired"}:
            err = data.get("error") or {}
            raise ProviderError(self.name, None, f"task {handle.job_id} {status}: {err.get('message') or err}")
        return data if status == "succeeded" else None

    def poll(self, handle: JobHandle, timeout: float = 900.0) -> GenerationResult:
        final = poll_until(lambda: self._status(handle), provider=self.name, timeout=timeout)
        url = (final.get("content") or {}).get("video_url")
        if not url:
            raise ProviderError(self.name, None, "succeeded task has no content.video_url")
        # The URL expires in about a day, so the bytes are fetched now, not recorded.
        return GenerationResult(
            content=_http.download(self.name, url),
            mime="video/mp4",
            extension="mp4",
            extra={"model_id": self.model_id, "seed": final.get("seed")},
        )


class Seedance25Provider(_ArkSeedance):
    name = "seedance-2-5"
    model_id = "dreamina-seedance-2-5-260628"


class Seedance20Provider(_ArkSeedance):
    name = "seedance-2-0"
    model_id = "dreamina-seedance-2-0-260128"


class FalSeedance25Provider(_SeedancePricing, FalVideoProvider):
    """Same model through fal's reference-to-video route, for a FAL_KEY-only setup."""

    name = "fal-seedance-2-5"
    default_model = "bytedance/seedance-2.5/reference-to-video"
    model_id = default_model

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        if kwargs.get("first_frame") or kwargs.get("last_frame"):
            raise ProviderError(
                self.name, None,
                "fal's reference route has no first/last frame; pass the frame as a reference image",
            )
        body: dict[str, Any] = {
            "image_urls": [as_url(r) for r in _refs(kwargs, "reference_images")] or None,
            "video_urls": [as_url(r) for r in _refs(kwargs, "reference_videos")] or None,
            "audio_urls": [as_url(r) for r in _refs(kwargs, "reference_audio")] or None,
            "duration": int(kwargs.get("duration_seconds", 5)),
            "aspect_ratio": kwargs.get("aspect_ratio"),
            "resolution": kwargs.get("resolution"),
            "generate_audio": bool(kwargs.get("generate_audio", True)),
            "seed": kwargs.get("seed"),
        }
        # _FalBase drops None values, so absent options stay absent on the wire.
        return super().generate(prompt, **body)


from ..config import register

register(Seedance25Provider())
register(Seedance20Provider())
register(FalSeedance25Provider())
