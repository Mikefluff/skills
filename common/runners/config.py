"""Provider registry + env-key resolution.

Providers self-register on import. The CLI looks up by name and asks each
provider whether all its required env vars are set before attempting a call.

Pattern (simplified) from the author's earlier production key-resolution layer.
No company-DB layer — single-user CLI reads from os.environ only.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .providers.base import Modality, Provider

_REGISTRY: dict[str, "Provider"] = {}


def register(provider: "Provider") -> None:
    _REGISTRY[provider.name] = provider


def get_provider(name: str) -> "Provider":
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(sorted(_REGISTRY)) or "(none registered yet)"
        raise KeyError(f"unknown provider '{name}'. Known: {known}") from exc


def all_providers(modality: "Modality | None" = None) -> list["Provider"]:
    items = list(_REGISTRY.values())
    if modality is not None:
        items = [p for p in items if p.modality == modality]
    items.sort(key=lambda p: (p.modality, p.name))
    return items


def available_providers(modality: "Modality | None" = None) -> list["Provider"]:
    return [p for p in all_providers(modality) if p.available()]


def resolve_env(*names: str) -> dict[str, str]:
    """Return a dict of present env vars only. Empty values are treated as missing."""
    out: dict[str, str] = {}
    for n in names:
        val = os.environ.get(n)
        if val:
            out[n] = val
    return out


def load_all_providers() -> None:
    """Force-import every provider module so they self-register.

    Called lazily from CLI entry points so import errors don't crash --check / --list.
    Also pulls ~/.skills.env (if present) into os.environ — file entries lose
    to existing shell exports.
    """
    # Load ~/.skills.env into os.environ (no override of existing values).
    try:
        from . import keysfile
        keysfile.load_into_env(override=False)
    except Exception:  # noqa: BLE001 — never break runners over keysfile errors
        pass
    from .providers import (  # noqa: F401
        bfl,
        elevenlabs,
        fal,
        google_image,
        google_music,
        google_video,
        ideogram,
        kling,
        openai_audio,
        openai_image,
        openai_transcribe,
        openai_video,
        replicate,
        runway,
        suno,
    )
