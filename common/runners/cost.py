"""Static cost table + interactive confirmation."""

from __future__ import annotations

import sys
from decimal import Decimal
from typing import Any

from .errors import CostConfirmationDeclined

# Per-unit USD pricing as of 2026-05. Source: vendor pricing pages (snapshotted).
# Values are conservative — actual cost may be slightly lower; never higher.
PRICE_TABLE: dict[str, dict[str, Decimal]] = {
    # OpenAI
    "gpt-image-2": {"low": Decimal("0.02"), "medium": Decimal("0.05"), "high": Decimal("0.10")},
    "gpt-4o-mini-tts": {"per_minute": Decimal("0.015")},
    "sora-2": {"per_second": Decimal("0.10")},
    "sora-2-pro": {"per_second": Decimal("0.30")},
    # Google
    "imagen-4": {"per_image": Decimal("0.04")},
    "imagen-4-ultra": {"per_image": Decimal("0.06")},
    "imagen-4-fast": {"per_image": Decimal("0.02")},
    "nano-banana-pro": {"per_image": Decimal("0.05")},
    "veo-3-1": {"per_second": Decimal("0.40")},
    "veo-3-1-fast": {"per_second": Decimal("0.15")},
    "lyria-3-pro": {"per_minute": Decimal("0.10")},
    # BFL
    "flux-1-1-pro": {"per_image": Decimal("0.04")},
    "flux-2-pro": {"per_image": Decimal("0.06")},
    "flux-kontext": {"per_edit": Decimal("0.05")},
    "flux-schnell": {"per_image": Decimal("0.003")},
    # fal.ai (routed; cost varies by hosted model — we estimate the median)
    "fal/any": {"per_image": Decimal("0.05"), "per_second": Decimal("0.15")},
    # Replicate
    "replicate/any": {"per_image": Decimal("0.03"), "per_second": Decimal("0.10")},
    # Runway
    "gen-4": {"per_second": Decimal("0.10")},
    "gen-4-turbo": {"per_second": Decimal("0.05")},
    "aleph": {"per_second": Decimal("0.18")},
    # Kling
    "kling-3": {"per_second": Decimal("0.10")},
    # Suno
    "suno-v5-5": {"per_song": Decimal("0.10")},
    # ElevenLabs
    "eleven-music": {"per_minute": Decimal("0.30")},
    "eleven-tts": {"per_1k_chars": Decimal("0.15")},
    # Ideogram
    "ideogram-3-turbo": {"per_image": Decimal("0.02")},
    "ideogram-3": {"per_image": Decimal("0.04")},
    "ideogram-3-quality": {"per_image": Decimal("0.08")},
}

CONFIRMATION_THRESHOLD = Decimal("0.10")


def estimate(provider: str, **kwargs: Any) -> Decimal | None:
    """Return USD estimate for a single generation. None = unknown."""
    entry = PRICE_TABLE.get(provider)
    if entry is None:
        return None

    variants = int(kwargs.get("variants", 1) or 1)

    if "per_image" in entry:
        return entry["per_image"] * variants
    if "per_edit" in entry:
        return entry["per_edit"] * variants
    if "per_song" in entry:
        return entry["per_song"] * variants
    if "per_second" in entry:
        duration = float(kwargs.get("duration_seconds", 8))
        return entry["per_second"] * Decimal(str(duration)) * variants
    if "per_minute" in entry:
        minutes = float(kwargs.get("duration_minutes", 1))
        return entry["per_minute"] * Decimal(str(minutes)) * variants
    if "per_1k_chars" in entry:
        chars = int(kwargs.get("char_count", 0))
        return entry["per_1k_chars"] * Decimal(str(chars / 1000)) * variants
    # quality tier (gpt-image-2)
    quality = kwargs.get("quality", "medium")
    if quality in entry:
        return entry[quality] * variants
    return None


def confirm(estimated_usd: Decimal | None, yes: bool = False) -> None:
    """Block on stdin if cost is over threshold and --yes was not passed.

    Raises CostConfirmationDeclined if user says no.
    """
    if estimated_usd is None or estimated_usd < CONFIRMATION_THRESHOLD or yes:
        return
    sys.stderr.write(
        f"\nEstimated cost: ${estimated_usd:.4f} USD. Proceed? [y/N] "
    )
    sys.stderr.flush()
    answer = sys.stdin.readline().strip().lower()
    if answer not in {"y", "yes"}:
        raise CostConfirmationDeclined(float(estimated_usd))


def format_cost(estimated_usd: Decimal | None) -> str:
    if estimated_usd is None:
        return "unknown"
    return f"${estimated_usd:.4f}"
