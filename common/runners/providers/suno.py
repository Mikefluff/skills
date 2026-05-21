"""Suno music provider — suno-v5-5 via official or gateway Suno API.
Vendor: Suno (https://api.suno.com), gated behind SUNO_API_ENABLED=1.
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


class SunoV55Provider(Provider):
    name = "suno-v5-5"
    modality = "music"
    requires_env = ("SUNO_API_KEY",)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:
        return cost.estimate(self.name, variants=kwargs.get("variants", 1))

    def _gate(self) -> None:
        if os.environ.get("SUNO_API_ENABLED") != "1":
            raise ProviderError(
                self.name,
                None,
                "Suno API surface varies between official and third-party gateways. "
                "Set SUNO_API_ENABLED=1 and (optionally) SUNO_API_URL to opt in.",
            )

    def _base_url(self) -> str:
        return os.environ.get("SUNO_API_URL", "https://api.suno.com/v1").rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {os.environ['SUNO_API_KEY']}",
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str, **kwargs: Any) -> JobHandle:
        self.ensure_available()
        self._gate()

        lyrics: str | None = kwargs.get("lyrics")
        instrumental: bool = bool(kwargs.get("instrumental", False))

        body: dict[str, Any] = {
            "prompt": prompt,
            "make_instrumental": instrumental,
            "model_version": kwargs.get("model_version", "v5.5"),
        }
        if lyrics:
            body["lyrics"] = lyrics
        if "title" in kwargs:
            body["title"] = kwargs["title"]
        if "tags" in kwargs:
            body["tags"] = kwargs["tags"]

        base = self._base_url()
        try:
            resp = requests.post(
                f"{base}/generate",
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
        # Handle multiple known response shapes (official + gateways).
        job_id = (
            payload.get("id")
            or payload.get("task_id")
            or (payload.get("data") or {}).get("id")
        )
        if not job_id and isinstance(payload, list) and payload:
            job_id = payload[0].get("id")
        if not job_id:
            raise ProviderError(self.name, resp.status_code, "no job id in response")

        return JobHandle(
            provider=self.name,
            job_id=str(job_id),
            started_at=time.time(),
            poll_url=f"{base}/generate/{job_id}",
            extra={"instrumental": instrumental},
        )

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:
        self._gate()
        headers = self._headers()

        def _check() -> dict[str, Any] | None:
            try:
                r = requests.get(handle.poll_url, headers=headers, timeout=30)
            except requests.RequestException as exc:
                raise ProviderError(self.name, None, f"network error during poll: {exc}") from exc
            if r.status_code == 429:
                raise QuotaError(self.name, 429, r.text[:500])
            if r.status_code >= 400:
                raise ProviderError(self.name, r.status_code, r.text[:500])
            data = r.json()
            node = data.get("data") if isinstance(data.get("data"), dict) else data
            status = (node.get("status") or "").lower()
            if status in {"failed", "error"}:
                raise ProviderError(self.name, None, f"job {handle.job_id} failed: {node.get('error', '')}")
            if status in {"complete", "completed", "succeeded", "done"}:
                return node
            audio_url = node.get("audio_url") or node.get("audio")
            if audio_url:
                return node
            return None

        final = poll_until(_check, provider=self.name, timeout=timeout)

        audio_url = (
            final.get("audio_url")
            or final.get("audio")
            or (final.get("output") or {}).get("audio_url")
        )
        if not audio_url:
            raise ProviderError(self.name, None, "completed job missing audio_url")

        try:
            asset = requests.get(audio_url, timeout=180)
        except requests.RequestException as exc:
            raise ProviderError(self.name, None, f"download failed: {exc}") from exc
        if asset.status_code >= 400:
            raise ProviderError(self.name, asset.status_code, "asset download failed")

        return GenerationResult(
            content=asset.content,
            mime="audio/mpeg",
            extension="mp3",
            extra=handle.extra,
        )


from ..config import register

register(SunoV55Provider())
