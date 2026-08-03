"""Static cost table + interactive confirmation."""

from __future__ import annotations

import os
import sys
from decimal import Decimal
from typing import Any

from .errors import CostConfirmationDeclined

# Per-unit USD pricing as of 2026-08-03. Source: vendor pricing pages (snapshotted).
# Values are conservative — actual cost may be slightly lower; never higher.
#
# A `_4k` suffix is the same unit charged at 4K output, which several vendors now
# bill separately. estimate() picks it only when the caller passes resolution="4k";
# the bare key is the price at every resolution below that.
PRICE_TABLE: dict[str, dict[str, Decimal]] = {
    # OpenAI
    "gpt-image-2": {"low": Decimal("0.02"), "medium": Decimal("0.05"), "high": Decimal("0.10")},
    "gpt-4o-mini-tts": {"per_minute": Decimal("0.015")},
    "whisper-1": {"per_minute": Decimal("0.006")},
    "gpt-4o-transcribe": {"per_minute": Decimal("0.006")},
    "gpt-4o-mini-transcribe": {"per_minute": Decimal("0.003")},
    # Retired from the API on 2026-09-24 along with the whole Videos API.
    "sora-2": {"per_second": Decimal("0.10")},
    "sora-2-pro": {"per_second": Decimal("0.50")},
    # Google — Gemini image family ("Nano Banana"). Imagen 4 shut down 2026-06-30.
    "nano-banana-pro": {"per_image": Decimal("0.134"), "per_image_4k": Decimal("0.24")},
    "nano-banana-2": {"per_image": Decimal("0.101"), "per_image_4k": Decimal("0.151")},
    "nano-banana-2-lite": {"per_image": Decimal("0.034")},
    "veo-3-1": {"per_second": Decimal("0.40"), "per_second_4k": Decimal("0.60")},
    "veo-3-1-fast": {"per_second": Decimal("0.12"), "per_second_4k": Decimal("0.30")},
    "veo-3-1-lite": {"per_second": Decimal("0.08")},
    "lyria-3-pro": {"per_minute": Decimal("0.10")},
    "lyria-3-clip": {"per_minute": Decimal("0.10")},
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
    "gen-4-5": {"per_second": Decimal("0.12")},
    "aleph": {"per_second": Decimal("0.18")},
    # Kling — standard runs $0.084/sec, Pro with video input up to $0.168.
    "kling-3": {"per_second": Decimal("0.12")},
    # Suno
    "suno-v5-5": {"per_song": Decimal("0.10")},
    # ElevenLabs
    "eleven-music": {"per_minute": Decimal("0.20")},
    "eleven-tts": {"per_1k_chars": Decimal("0.12")},
    # Ideogram. Ideogram 4.0 shipped 2026-06-03 at $0.03/$0.06/$0.10, but the public
    # API still exposes only the v3 generate endpoint — priced here when we can call it.
    "ideogram-3-flash": {"per_image": Decimal("0.02")},
    "ideogram-3-turbo": {"per_image": Decimal("0.02")},
    "ideogram-3": {"per_image": Decimal("0.04")},
    "ideogram-3-quality": {"per_image": Decimal("0.08")},
}

CONFIRMATION_THRESHOLD = Decimal("0.10")

_4K_ALIASES = {"4k", "4K", "3840", "4096", "2160p", "uhd"}


def _wants_4k(kwargs: dict[str, Any]) -> bool:
    """True when the caller asked for 4K output, under any of the spellings callers use."""
    for key in ("resolution", "image_size", "size", "quality"):
        value = kwargs.get(key)
        if value is not None and str(value).strip().lower() in {a.lower() for a in _4K_ALIASES}:
            return True
    return False


def estimate(provider: str, **kwargs: Any) -> Decimal | None:
    """Return USD estimate for a single generation. None = unknown."""
    entry = PRICE_TABLE.get(provider)
    if entry is None:
        return None

    variants = int(kwargs.get("variants", 1) or 1)

    def unit(key: str) -> Decimal:
        """Price for `key`, upgraded to its 4K tier when the caller asked for 4K."""
        if _wants_4k(kwargs) and f"{key}_4k" in entry:
            return entry[f"{key}_4k"]
        return entry[key]

    if "per_image" in entry:
        return unit("per_image") * variants
    if "per_edit" in entry:
        return entry["per_edit"] * variants
    if "per_song" in entry:
        return entry["per_song"] * variants
    if "per_second" in entry:
        duration = float(kwargs.get("duration_seconds", 8))
        return unit("per_second") * Decimal(str(duration)) * variants
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


# ---------------------------------------------------------------------------
# Batch-aware confirmation (carousel-builder, reel-builder)
# ---------------------------------------------------------------------------

_DEFAULT_BUDGETS: dict[str, Decimal] = {
    "carousel": Decimal("1.50"),    # 8 slides × ~$0.18 typical
    "reel": Decimal("4.00"),         # 3 shots × ~$1.20 + music ~$0.30
    "research": Decimal("0.00"),     # WebSearch/WebFetch — usually free
}

_BUDGET_ENV_OVERRIDE = {
    "carousel": "SKILLS_CAROUSEL_BUDGET",
    "reel": "SKILLS_REEL_BUDGET",
    "research": "SKILLS_RESEARCH_BUDGET",
}


def batch_budget(modality: str) -> Decimal | None:
    """Read a per-modality budget cap from env override or default table."""
    env_key = _BUDGET_ENV_OVERRIDE.get(modality)
    if env_key:
        raw = os.environ.get(env_key)
        if raw:
            try:
                return Decimal(raw)
            except Exception:  # noqa: BLE001
                pass
    return _DEFAULT_BUDGETS.get(modality)


def confirm_batch(
    estimated_total: Decimal | None,
    *,
    n_items: int,
    modality: str,
    yes: bool = False,
) -> None:
    """Confirm the AGGREGATE cost for a batch of N items.

    Threshold: max(per-call CONFIRMATION_THRESHOLD, batch budget).
    Asks once before the batch starts — not per item.
    """
    if estimated_total is None or yes:
        return
    if estimated_total < CONFIRMATION_THRESHOLD:
        return
    budget = batch_budget(modality)
    over_budget = budget is not None and estimated_total > budget
    sys.stderr.write(
        f"\nBatch: {n_items} {modality} items, total estimated cost ${estimated_total:.4f} USD"
    )
    if over_budget and budget is not None:
        sys.stderr.write(
            f"\n  WARNING: exceeds default {modality} budget (${budget:.2f}). "
            f"Override via {_BUDGET_ENV_OVERRIDE[modality]}=X."
        )
    sys.stderr.write(". Proceed? [y/N] ")
    sys.stderr.flush()
    answer = sys.stdin.readline().strip().lower()
    if answer not in {"y", "yes"}:
        raise CostConfirmationDeclined(float(estimated_total))
