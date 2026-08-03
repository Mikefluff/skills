"""Style validation — is a style file usable, and if not, why.

Split out of styles.py, which had grown past the module-size gate. styles.py
answers "load me a style"; this answers "is this one well-formed". The
dependency runs one way: this imports Style, styles.py does not import this.

The issue strings are user-facing. Styles are hand-written — users are invited
to add their own under ~/.claude/style-library/ — and this is the only place
that tells an author what is wrong with one. A rule that silently stops firing
turns a broken style into a confusing render three steps later.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from .styles import Style

# ---------------------------------------------------------------------------
# Schema + validation
# ---------------------------------------------------------------------------

REQUIRED_FRONTMATTER: dict[str, set[str]] = {
    "carousel": {"id", "modality", "display", "mood", "tags", "text_friendly", "photoreal"},
    "video":    {"id", "modality", "display", "mood", "tags", "pacing", "dialogue_friendly"},
    "music":    {"id", "modality", "display", "mood", "tags", "bpm_range", "energy", "two_box", "vocal_friendly"},
}

REQUIRED_BODY_FIELDS: dict[str, list[str]] = {
    "carousel": [
        "Vibe",
        "Palette",
        "Typography",
        "Medium",
        "Composition",
        "Style anchor (carousel)",
        "Style anchor (text-in-image mode)",
        "Best for",
        "Avoid for",
        "Suggested models",
        "Caption tone",
    ],
    "video": [
        "Inspired by",
        "Cinematography anchor",
        "Color palette",
        "Lens & framing",
        "Lighting",
        "Motion language",
        "Editing rhythm",
        "Shot anchor (per-shot prompt fragment)",
        "Action vocabulary",
        "Sound design implications",
        "Best for",
        "Avoid for",
        "Suggested duration",
        "Suggested music style",
    ],
    "music": [
        "Vibe",
        "Era & lineage",
        "Tempo",
        "Core sonic signature",
        "Suno Style box (paste-ready, ≤200 chars)",
        "Suno meta-tag stacks (by section)",
        "Udio prompt",
        "Lyria 3 Pro field-driven",
        "ElevenLabs Music prompt",
        "Lyrics conventions for this genre",
        "Caption tone (for paired carousel post or reel CTA)",
        "Best for",
        "Avoid for",
        "Suggested duration",
    ],
}

# Music meta-tag stack regex — used by the music validator to nudge users
# toward the canonical taxonomy. Not a hard error if mismatched.
_KEBAB_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,40}$")
_BPM_RANGE_RE = re.compile(r"^\d{2,3}-\d{2,3}$")
_VALID_ENERGY = {"calm", "warm", "driving", "aggressive"}
_VALID_PACING = {"slow", "medium", "snap", "kinetic"}


ANCHOR_FIELD: dict[str, str] = {
    "carousel": "Style anchor (carousel)",
    "video": "Shot anchor (per-shot prompt fragment)",
    "music": "Suno Style box (paste-ready, ≤200 chars)",
}

MIN_ANCHOR_CHARS = 40


def _bool_issues(meta: dict[str, Any], names: Iterable[str]) -> list[str]:
    """Absent is fine; present-but-not-a-bool is not."""
    out: list[str] = []
    for name in names:
        value = meta.get(name)
        if value is not None and not isinstance(value, bool):
            out.append(f"'{name}' must be true/false")
    return out


def _identity_issues(style: Style) -> list[str]:
    """Is this style who it says it is, and does it declare what it must?"""
    issues: list[str] = []
    meta = style.meta

    missing = [k for k in REQUIRED_FRONTMATTER[style.modality] if k not in meta]
    if missing:
        issues.append(f"frontmatter missing required field(s): {', '.join(sorted(missing))}")

    sid = str(meta.get("id") or "")
    if not _KEBAB_ID_RE.fullmatch(sid):
        issues.append(f"id '{sid}' must match ^[a-z][a-z0-9-]{{1,40}}$ (kebab-case)")
    # The filename is how every caller refers to a style, so a mismatch means
    # --style <id> silently resolves to something else.
    if sid != style.id:
        issues.append(f"frontmatter id '{sid}' must match filename stem '{style.id}'")

    meta_modality = str(meta.get("modality") or "")
    if meta_modality != style.modality:
        issues.append(f"frontmatter modality '{meta_modality}' must equal '{style.modality}'")

    return issues


def _shared_shape_issues(meta: dict[str, Any]) -> list[str]:
    """Types of the fields every modality declares."""
    issues: list[str] = []

    for list_field in ("mood", "tags"):
        val = meta.get(list_field)
        if val is not None and not isinstance(val, list):
            issues.append(f"'{list_field}' must be a list (got {type(val).__name__})")
        elif isinstance(val, list) and not all(isinstance(x, str) for x in val):
            issues.append(f"'{list_field}' entries must all be strings")

    display = meta.get("display")
    if display is not None and not isinstance(display, str):
        issues.append(f"'display' must be a string (got {type(display).__name__})")

    return issues


def _carousel_meta_issues(meta: dict[str, Any]) -> list[str]:
    return _bool_issues(meta, ("text_friendly", "photoreal"))


def _video_meta_issues(meta: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    pacing = meta.get("pacing")
    if pacing is not None and pacing not in _VALID_PACING:
        issues.append(f"'pacing' must be one of {sorted(_VALID_PACING)} (got {pacing!r})")
    return issues + _bool_issues(meta, ("dialogue_friendly",))


def _music_meta_issues(meta: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    bpm = meta.get("bpm_range")
    if bpm is not None and not (isinstance(bpm, str) and _BPM_RANGE_RE.fullmatch(bpm.strip())):
        issues.append(f"'bpm_range' must be 'NN-NN' string (got {bpm!r})")
    energy = meta.get("energy")
    if energy is not None and energy not in _VALID_ENERGY:
        issues.append(f"'energy' must be one of {sorted(_VALID_ENERGY)} (got {energy!r})")
    return issues + _bool_issues(meta, ("two_box", "vocal_friendly"))


_MODALITY_META_VALIDATORS = {
    "carousel": _carousel_meta_issues,
    "video": _video_meta_issues,
    "music": _music_meta_issues,
}


def _body_issues(style: Style) -> list[str]:
    """Required fields must be present, and the anchor must say something."""
    issues = [
        f"body missing field: '{field}' (expected line starting with '**{field}**:')"
        for field in REQUIRED_BODY_FIELDS.get(style.modality, [])
        if f"**{field}**:" not in style.body
    ]

    # The anchor is injected into every generated prompt. A stub one produces
    # styleless output rather than an error, so it is checked for length.
    anchor_field = ANCHOR_FIELD[style.modality]
    anchor_text = style.anchor(anchor_field)
    if not anchor_text or len(anchor_text) < MIN_ANCHOR_CHARS:
        issues.append(
            f"'{anchor_field}' is empty or too short (need ≥{MIN_ANCHOR_CHARS} chars)"
        )
    return issues


def validate_style(style: Style) -> list[str]:
    """Return a list of issue strings. Empty list = valid.

    Every issue found is reported, not just the first — a user fixing a
    hand-written style wants the whole list, not one round trip per mistake.
    """
    if style.modality not in REQUIRED_FRONTMATTER:
        return [
            f"unknown modality '{style.modality}' "
            f"(expected one of {sorted(REQUIRED_FRONTMATTER)})"
        ]

    per_modality = _MODALITY_META_VALIDATORS[style.modality]
    return (
        _identity_issues(style)
        + _shared_shape_issues(style.meta)
        + per_modality(style.meta)
        + _body_issues(style)
    )
