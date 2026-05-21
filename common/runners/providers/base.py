"""Provider ABC + shared dataclasses."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Literal

from ..errors import KeyMissingError

Modality = Literal["image", "video", "music", "audio"]


@dataclass
class JobHandle:
    """Returned by async providers (video, music). Polled to completion."""

    provider: str
    job_id: str
    started_at: float
    poll_url: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Returned by generate() or poll() once an asset is ready."""

    content: bytes
    mime: str
    extension: str  # "png", "mp4", "mp3", ...
    extra: dict[str, Any] = field(default_factory=dict)


class Provider(ABC):
    """Provider adapter — must subclass and implement generate()."""

    name: str  # canonical slug, e.g. "gpt-image-2"
    modality: Modality
    requires_env: tuple[str, ...]  # all must be set for available() to be True

    def available(self) -> bool:
        return all(os.environ.get(k) for k in self.requires_env)

    def ensure_available(self) -> None:
        if not self.available():
            missing = [k for k in self.requires_env if not os.environ.get(k)]
            raise KeyMissingError(self.name, missing)

    def estimate_cost(self, **kwargs: Any) -> Decimal | None:  # noqa: ARG002
        """USD cost estimate. None = unknown (don't gate the confirmation)."""
        return None

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult | JobHandle:
        """Sync providers return GenerationResult; async return JobHandle."""

    def poll(self, handle: JobHandle, timeout: float = 600.0) -> GenerationResult:  # noqa: ARG002
        """Default impl raises — async providers override."""
        raise NotImplementedError(f"{self.name} returned a JobHandle but did not override poll()")

    def info(self) -> dict[str, Any]:
        """Short metadata block printed by --list-providers / --check."""
        return {
            "name": self.name,
            "modality": self.modality,
            "requires_env": list(self.requires_env),
            "available": self.available(),
        }
