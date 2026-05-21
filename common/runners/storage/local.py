"""Local filesystem sink."""

from __future__ import annotations

from pathlib import Path


def write_local(content: bytes, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path
