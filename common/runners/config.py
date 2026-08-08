"""Provider registry + env-key resolution.

Providers self-register on import. The CLI looks up by name and asks each
provider whether all its required env vars are set before attempting a call.

Pattern (simplified) from the author's earlier production key-resolution layer.
No company-DB layer — single-user CLI reads from os.environ only.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .providers.base import Modality, Provider
    from .publishers.base import Publisher

_REGISTRY: dict[str, "Provider"] = {}
_PUBLISHERS: dict[str, "Publisher"] = {}

# Retired slugs → (successor slug, why). A vendor shutting a model down does not
# get to break a user's script: the old name keeps resolving, prints one line to
# stderr, and routes upward. Mirrors the "Deprecations" tables the model-picker
# references already publish.
_DEPRECATED: dict[str, tuple[str, str]] = {}


def register(provider: "Provider") -> None:
    _REGISTRY[provider.name] = provider


def register_deprecated(old: str, new: str, reason: str) -> None:
    """Alias a retired provider slug onto its successor."""
    _DEPRECATED[old] = (new, reason)


def deprecations() -> dict[str, tuple[str, str]]:
    return dict(_DEPRECATED)


def get_provider(name: str) -> "Provider":
    if name in _DEPRECATED and name not in _REGISTRY:
        successor, reason = _DEPRECATED[name]
        sys.stderr.write(f"warning: '{name}' is retired ({reason}). Routing to '{successor}'.\n")
        name = successor
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


# ───────────────────────────────────────────────────────────────────────────
# Publisher registry — same self-registration pattern, separate namespace.
# A publisher named "instagram" must not collide with a provider slug.
# ───────────────────────────────────────────────────────────────────────────


def register_publisher(publisher: "Publisher") -> None:
    _PUBLISHERS[publisher.name] = publisher


def get_publisher(name: str) -> "Publisher":
    try:
        return _PUBLISHERS[name]
    except KeyError as exc:
        known = ", ".join(sorted(_PUBLISHERS)) or "(none registered yet)"
        raise KeyError(f"unknown platform '{name}'. Known: {known}") from exc


def all_publishers() -> list["Publisher"]:
    return sorted(_PUBLISHERS.values(), key=lambda p: p.name)


def load_all_publishers() -> None:
    """Force-import every publisher module so they self-register.

    Mirrors load_all_providers(), including the ~/.skills.env pull — app-level
    creds (META_APP_ID, TELEGRAM_BOT_TOKEN, ...) live there alongside the
    generation keys. Short-lived user tokens live in ~/.skills-tokens.json and
    are read on demand by the tokens module, not loaded into os.environ.
    """
    try:
        from . import keysfile

        keysfile.load_into_env(override=False)
    except Exception:  # noqa: BLE001 — never break runners over keysfile errors
        pass
    from .publishers import (  # noqa: F401
        devto,
        hashnode,
        instagram,
        linkedin,
        micropub,
        qiita,
        telegram,
        telegraph,
        threads,
        tiktok,
        tumblr,
        x,
        youtube,
    )
