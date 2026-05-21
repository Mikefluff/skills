"""Output writer — local FS always, optional S3 mirror."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .storage import s3_configured, write_local, write_s3

Modality = Literal["image", "video", "music", "audio"]

_MIME_BY_EXT = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "svg": "image/svg+xml",
    "mp4": "video/mp4",
    "webm": "video/webm",
    "mov": "video/quicktime",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
    "txt": "text/plain; charset=utf-8",
}


@dataclass
class SavedAsset:
    local_path: Path
    s3_url: str | None = None

    def display(self) -> str:
        if self.s3_url:
            return f"{self.local_path}  (also at {self.s3_url})"
        return str(self.local_path)


def _slugify(s: str | None, max_len: int = 40) -> str:
    if not s:
        return "asset"
    s = re.sub(r"[^A-Za-z0-9-]+", "-", s.strip()).strip("-").lower()
    return s[:max_len] or "asset"


def save(
    content: bytes,
    modality: Modality,
    extension: str,
    *,
    slug: str | None = None,
    output_dir: Path | None = None,
    mime: str | None = None,
) -> SavedAsset:
    """Write content to ./generated/<modality>/<timestamp>-<slug>.<ext>.

    If S3 env vars are set, also uploads and returns the URL.
    """
    ext = extension.lstrip(".").lower()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{_slugify(slug)}.{ext}"

    base = output_dir or Path("./generated") / modality
    local_path = base / filename
    write_local(content, local_path)

    s3_url: str | None = None
    if s3_configured():
        content_type = mime or _MIME_BY_EXT.get(ext, "application/octet-stream")
        s3_url = write_s3(content, f"{modality}/{filename}", content_type)

    return SavedAsset(local_path=local_path, s3_url=s3_url)


def save_prompt_only(
    prompt: str,
    modality: Modality,
    *,
    slug: str | None = None,
    output_dir: Path | None = None,
    reason: str = "",
) -> SavedAsset:
    """Fallback when execution fails: persist the prompt text so work isn't lost."""
    body = prompt
    if reason:
        body = f"# Prompt-only fallback\n# Reason: {reason}\n\n{prompt}"
    return save(body.encode("utf-8"), modality, "txt", slug=slug or "prompt-only", output_dir=output_dir)
