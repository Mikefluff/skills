"""Seedance through OpenRouter's video API — same model, OpenRouter billing.
Vendor: OpenRouter (https://openrouter.ai/api/v1/videos), routed to BytePlus Seedance.

For when BytePlus itself cannot be paid (it refuses some cards) but the model is
still wanted. OpenRouter forwards references in order and, for Seedance 2 and
newer, honours audio references — so @Image1 / @Audio1 in the prompt keep their
meaning and lip-sync to the supplied take still works.

Takes the same kwargs as the BytePlus providers in `seedance.py`, plus one:

  media_host  "litterbox" — where local audio and video references are put up
              first (`audio_host` is the older name and still works).

OpenRouter takes a reference image inline but refuses inline audio and video
("Only HTTPS URLs are allowed"), so a local take or previs clip has to be
public for the length of the render. That can be the user's voice on a public
URL, so it never happens by default: without a host, a local audio or video
reference is an error. Litterbox deletes the file after an hour, which outlives the render.
The take goes up as MP3, a fifth of the WAV.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import cost
from ..errors import ProviderError
from ..poll import poll_until
from . import _http
from .base import GenerationResult, JobHandle, Provider
from .seedance import _refs, ark_tokens, as_url

_BASE = "https://openrouter.ai/api/v1/videos"
_LITTERBOX = "https://litterbox.catbox.moe/resources/internals/api.php"
_NAME = "openrouter-seedance-2-5"


def _litterbox(path: Path) -> str:
    with path.open("rb") as fh:
        resp = _http.post(_NAME, _LITTERBOX, data={"reqtype": "fileupload", "time": "1h"},
                          files={"fileToUpload": (path.name, fh)}, timeout=120)
    url = resp.text.strip()
    if not url.startswith("https://"):
        raise ProviderError(_NAME, resp.status_code, f"litterbox upload failed: {url[:200]}")
    return url


def _video_url(ref: str, host: str | None) -> str:
    """A URL as-is; a local clip (a previs, a camera reference) on `host`."""
    if ref.startswith("https://"):
        return ref
    path = Path(ref)
    if not path.is_file():
        raise ProviderError(_NAME, None, f"reference not found: {ref}")
    if host != "litterbox":
        raise ProviderError(_NAME, None, "OpenRouter takes video references only as public HTTPS URLs; "
                                         "pass a URL or set media_host='litterbox'")
    return _litterbox(path)


def _audio_url(ref: str, host: str | None) -> str:
    """A URL as-is; a local file as MP3 on `host`, or an error without one."""
    if ref.startswith("https://"):
        return ref
    path = Path(ref)
    if not path.is_file():
        raise ProviderError(_NAME, None, f"reference not found: {ref}")
    if host != "litterbox":
        raise ProviderError(
            _NAME, None,
            "OpenRouter takes audio references only as public HTTPS URLs; "
            "pass a URL or set media_host='litterbox' to upload the take for an hour",
        )
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / f"{path.stem}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-b:a", "192k", str(mp3)],
            check=True, capture_output=True,
        )
        return _litterbox(mp3)


class OpenRouterSeedance25Provider(Provider):
    name = _NAME
    modality = "video"
    requires_env = ("OPENROUTER_API_KEY",)
    model_id = "bytedance/seedance-2.5"

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        # OpenRouter passes BytePlus's token price through (≈$0.231/s at 720p).
        tokens = ark_tokens(
            float(kwargs.get("duration_seconds", 5)),
            str(kwargs.get("resolution") or "720p"),
            str(kwargs.get("aspect_ratio") or "9:16"),
        )
        return cost.estimate(self.name, tokens=tokens, variants=kwargs.get("variants", 1))

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"}

    @staticmethod
    def _references(kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        """Images, then videos, then audio — the order that makes @Image1.., @Video1.., @Audio1.."""
        host = kwargs.get("media_host") or kwargs.get("audio_host")
        kinds = (("reference_images", "image_url", as_url),
                 ("reference_videos", "video_url", lambda r: _video_url(r, host)),
                 ("reference_audio", "audio_url", lambda r: _audio_url(r, host)))
        return [{"type": wire, wire: {"url": encode(r)}} for key, wire, encode in kinds for r in _refs(kwargs, key)]

    def build_body(self, prompt: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        refs = self._references(kwargs)
        body: dict[str, Any] = {
            "model": kwargs.get("model_id") or self.model_id,
            "prompt": prompt,
            "duration": int(kwargs.get("duration_seconds", 5)),
            "generate_audio": bool(kwargs.get("generate_audio", True)),
        }
        if refs:
            body["input_references"] = refs
        # frame_images switches the request to image-to-video and drops every
        # reference, so it is sent only when asked for and never with references.
        frames = [
            {"type": "image_url", "image_url": {"url": as_url(kwargs[role])}, "frame_type": role}
            for role in ("first_frame", "last_frame") if kwargs.get(role)
        ]
        if frames and refs:
            raise ProviderError(self.name, None, "first/last frames and references cannot be combined on OpenRouter")
        if frames:
            body["frame_images"] = frames
        for key, wire in (("aspect_ratio", "aspect_ratio"), ("resolution", "resolution"), ("seed", "seed")):
            if kwargs.get(key) is not None:
                body[wire] = kwargs[key]
        return body

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        resp = _http.post(self.name, _BASE, json=self.build_body(prompt, kwargs), headers=self._headers(), timeout=120)
        job = resp.json()
        if not job.get("id"):
            raise ProviderError(self.name, resp.status_code, "no job id in response")
        return JobHandle(
            provider=self.name,
            job_id=str(job["id"]),
            started_at=time.time(),
            poll_url=job.get("polling_url") or f"{_BASE}/{job['id']}",
        )

    def _status(self, handle: JobHandle) -> dict[str, Any] | None:
        data = _http.poll_get(self.name, handle.poll_url, headers=self._headers()).json()
        status = (data.get("status") or "").lower()
        if status in {"failed", "cancelled", "expired"}:
            raise ProviderError(self.name, None, f"job {handle.job_id} {status}: {data.get('error')}")
        return data if status == "completed" else None

    def poll(self, handle: JobHandle, timeout: float = 900.0) -> GenerationResult:
        final = poll_until(lambda: self._status(handle), provider=self.name, timeout=timeout)
        content = _http.download(self.name, f"{_BASE}/{handle.job_id}/content?index=0", headers=self._headers())
        return GenerationResult(
            content=content,
            mime="video/mp4",
            extension="mp4",
            extra={"model_id": self.model_id, "cost_usd": (final.get("usage") or {}).get("cost")},
        )


from ..config import register

register(OpenRouterSeedance25Provider())
