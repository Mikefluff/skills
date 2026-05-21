"""Style library loader — reads style frontmatter from bundled and user dirs.

Layout:
  <repo>/common/style-library/<modality>/<id>.md     (bundled)
  ~/.claude/style-library/<modality>/<id>.md          (user override — priority)

Each style is a markdown file with YAML-ish frontmatter (regex-parsed; no PyYAML dep)
and free-form body. The loader returns a Style object exposing:

  - meta: frontmatter dict (id, display, mood, tags, ...)
  - body: full markdown body after frontmatter
  - anchor(name): extract a named anchor block ("Style anchor (carousel)" etc.)

Callers (carousel-builder / reel-builder / music-prompt) decide which anchor to
inject into per-item prompts.

Also exposes:
  - REQUIRED_FRONTMATTER per modality + REQUIRED_BODY_FIELDS per modality
  - validate_style(style) -> list[str] of issues
  - copy_template(modality, new_id, user_dir=None) -> Path of newly created file
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

Modality = Literal["carousel", "video", "music"]

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)
_LIST_RE = re.compile(r"^\[(.*)\]$")
_KV_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")


@dataclass
class Style:
    id: str
    modality: Modality
    meta: dict[str, Any]
    body: str
    source_path: Path

    @property
    def display(self) -> str:
        return str(self.meta.get("display") or self.id)

    @property
    def mood(self) -> list[str]:
        v = self.meta.get("mood") or []
        return list(v) if isinstance(v, list) else [str(v)]

    @property
    def tags(self) -> list[str]:
        v = self.meta.get("tags") or []
        return list(v) if isinstance(v, list) else [str(v)]

    def anchor(self, name: str) -> str | None:
        """Extract the prose block following a `**<name>**:` line in the body.

        Body convention is:
          **Style anchor (carousel)**:
          > one or more paragraphs...

          **Next field**: ...

        We return the paragraph(s) under the `**name**:` marker until the next
        blank line + `**` marker, with the leading `> ` blockquote markers stripped.
        Returns None if no such anchor exists.
        """
        marker = f"**{name}**:"
        idx = self.body.find(marker)
        if idx < 0:
            return None
        rest = self.body[idx + len(marker):]
        # Find the next top-level marker (`**Word`...`**:` or `## ` heading) that begins a new field.
        # We strip leading whitespace/newlines, then walk lines until we hit a new field marker.
        lines: list[str] = []
        for raw in rest.lstrip("\n").splitlines():
            line = raw.rstrip()
            if line.startswith("**") and line.endswith(":"):
                break
            if line.startswith("## "):
                break
            lines.append(line)
        # Strip trailing blank lines
        while lines and not lines[-1].strip():
            lines.pop()
        # Strip leading blank lines
        while lines and not lines[0].strip():
            lines.pop(0)
        # Strip `> ` blockquote prefix from each line
        cleaned = [re.sub(r"^> ?", "", ln) for ln in lines]
        text = " ".join(ln.strip() for ln in cleaned if ln.strip())
        return text or None

    def section(self, heading: str) -> str | None:
        """Return the prose block under a `**heading**:` field, preserving newlines.

        Works for fields like 'Vibe', 'Palette', 'Best for', 'Action vocabulary'.
        Returns None if the field is missing.
        """
        marker = f"**{heading}**:"
        idx = self.body.find(marker)
        if idx < 0:
            return None
        rest = self.body[idx + len(marker):]
        lines: list[str] = []
        for raw in rest.lstrip().splitlines():
            line = raw.rstrip()
            if line.startswith("**") and line.endswith(":"):
                break
            if line.startswith("## "):
                break
            lines.append(line)
        while lines and not lines[-1].strip():
            lines.pop()
        return "\n".join(lines).strip() or None


@dataclass
class StyleLibrary:
    bundled_dir: Path
    user_dir: Path | None = None
    _cache: dict[tuple[str, str], Style] = field(default_factory=dict)

    def _candidates(self, modality: Modality, style_id: str) -> Iterable[Path]:
        # User override first
        if self.user_dir is not None:
            yield self.user_dir / modality / f"{style_id}.md"
        yield self.bundled_dir / modality / f"{style_id}.md"

    def load(self, style_id: str, modality: Modality) -> Style:
        cache_key = (modality, style_id)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        for path in self._candidates(modality, style_id):
            if path.is_file():
                style = _parse_file(path, modality, style_id)
                self._cache[cache_key] = style
                return style
        raise FileNotFoundError(
            f"style '{style_id}' not found for modality '{modality}'. "
            f"Looked in: {', '.join(str(p) for p in self._candidates(modality, style_id))}"
        )

    def list(self, modality: Modality) -> list[Style]:
        """Return all styles available for a modality (bundled + user overrides merged)."""
        seen: dict[str, Style] = {}
        dirs: list[Path] = []
        if self.user_dir is not None:
            dirs.append(self.user_dir / modality)
        dirs.append(self.bundled_dir / modality)
        for d in dirs:
            if not d.is_dir():
                continue
            for path in sorted(d.glob("*.md")):
                if path.name.startswith("_") or path.name.lower() == "readme.md":
                    continue
                style_id = path.stem
                if style_id in seen:
                    continue  # user override already loaded
                try:
                    seen[style_id] = _parse_file(path, modality, style_id)
                except (ValueError, OSError):
                    continue
        return sorted(seen.values(), key=lambda s: s.id)

    def find_by_tags(self, tags: list[str], modality: Modality) -> list[Style]:
        wanted = {t.lower().strip() for t in tags if t.strip()}
        if not wanted:
            return []
        matches: list[tuple[int, Style]] = []
        for style in self.list(modality):
            haystack = {t.lower() for t in style.tags + style.mood}
            score = len(wanted & haystack)
            if score > 0:
                matches.append((score, style))
        matches.sort(key=lambda pair: (-pair[0], pair[1].id))
        return [s for _, s in matches]


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        return ""
    # Quoted string
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    # Inline list
    m = _LIST_RE.match(raw)
    if m:
        inner = m.group(1)
        if not inner.strip():
            return []
        parts = [p.strip().strip('"').strip("'") for p in _split_csv(inner)]
        return [p for p in parts if p]
    # Bool
    low = raw.lower()
    if low in {"true", "yes"}:
        return True
    if low in {"false", "no"}:
        return False
    # Number
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    return raw


def _split_csv(s: str) -> list[str]:
    """Split a list-body on commas, respecting quoted items."""
    out: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in s:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in {'"', "'"}:
            quote = ch
            buf.append(ch)
            continue
        if ch == ",":
            out.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    head, body = m.group(1), m.group(2)
    meta: dict[str, Any] = {}
    for raw_line in head.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        kv = _KV_RE.match(line)
        if not kv:
            continue
        key, value = kv.group(1), kv.group(2)
        meta[key] = _parse_value(value)
    return meta, body


def _parse_file(path: Path, modality: Modality, style_id: str) -> Style:
    text = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)
    # Confidence: meta.id should match filename stem; fall back gracefully
    style_id_in_meta = str(meta.get("id") or style_id)
    if style_id_in_meta != style_id:
        # Trust filename over meta on mismatch (filename is what callers ask for)
        style_id_in_meta = style_id
    return Style(
        id=style_id_in_meta,
        modality=modality,
        meta=meta,
        body=body,
        source_path=path,
    )


# Default library — resolved relative to this file's location.
# `common/runners/styles.py` → `common/style-library/`
_BUNDLED_DIR = Path(__file__).resolve().parent.parent / "style-library"
_USER_DIR = Path.home() / ".claude" / "style-library"

_default_library = StyleLibrary(
    bundled_dir=_BUNDLED_DIR,
    user_dir=_USER_DIR if _USER_DIR.is_dir() else None,
)


def load_style(style_id: str, modality: Modality) -> Style:
    return _default_library.load(style_id, modality)


def list_styles(modality: Modality) -> list[Style]:
    return _default_library.list(modality)


def find_by_tags(tags: list[str], modality: Modality) -> list[Style]:
    return _default_library.find_by_tags(tags, modality)


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


def validate_style(style: Style) -> list[str]:
    """Return a list of issue strings. Empty list = valid."""
    issues: list[str] = []
    mod = style.modality

    # --- frontmatter ---
    required = REQUIRED_FRONTMATTER.get(mod)
    if required is None:
        return [f"unknown modality '{mod}' (expected one of {sorted(REQUIRED_FRONTMATTER)})"]

    missing = [k for k in required if k not in style.meta]
    if missing:
        issues.append(f"frontmatter missing required field(s): {', '.join(sorted(missing))}")

    # id format
    sid = str(style.meta.get("id") or "")
    if not _KEBAB_ID_RE.fullmatch(sid):
        issues.append(f"id '{sid}' must match ^[a-z][a-z0-9-]{{1,40}}$ (kebab-case)")
    if sid != style.id:
        issues.append(f"frontmatter id '{sid}' must match filename stem '{style.id}'")

    # modality field
    meta_modality = str(style.meta.get("modality") or "")
    if meta_modality != mod:
        issues.append(f"frontmatter modality '{meta_modality}' must equal '{mod}'")

    # mood + tags must be lists
    for list_field in ("mood", "tags"):
        val = style.meta.get(list_field)
        if val is not None and not isinstance(val, list):
            issues.append(f"'{list_field}' must be a list (got {type(val).__name__})")
        elif isinstance(val, list) and not all(isinstance(x, str) for x in val):
            issues.append(f"'{list_field}' entries must all be strings")

    # display must be a string
    display = style.meta.get("display")
    if display is not None and not isinstance(display, str):
        issues.append(f"'display' must be a string (got {type(display).__name__})")

    # Per-modality field shape
    if mod == "carousel":
        for bool_field in ("text_friendly", "photoreal"):
            v = style.meta.get(bool_field)
            if v is not None and not isinstance(v, bool):
                issues.append(f"'{bool_field}' must be true/false")
    elif mod == "video":
        pacing = style.meta.get("pacing")
        if pacing is not None and pacing not in _VALID_PACING:
            issues.append(f"'pacing' must be one of {sorted(_VALID_PACING)} (got {pacing!r})")
        df = style.meta.get("dialogue_friendly")
        if df is not None and not isinstance(df, bool):
            issues.append("'dialogue_friendly' must be true/false")
    elif mod == "music":
        bpm = style.meta.get("bpm_range")
        if bpm is not None and not (isinstance(bpm, str) and _BPM_RANGE_RE.fullmatch(bpm.strip())):
            issues.append(f"'bpm_range' must be 'NN-NN' string (got {bpm!r})")
        energy = style.meta.get("energy")
        if energy is not None and energy not in _VALID_ENERGY:
            issues.append(f"'energy' must be one of {sorted(_VALID_ENERGY)} (got {energy!r})")
        for bool_field in ("two_box", "vocal_friendly"):
            v = style.meta.get(bool_field)
            if v is not None and not isinstance(v, bool):
                issues.append(f"'{bool_field}' must be true/false")

    # --- body ---
    for field in REQUIRED_BODY_FIELDS.get(mod, []):
        marker = f"**{field}**:"
        if marker not in style.body:
            issues.append(f"body missing field: '{field}' (expected line starting with '{marker}')")

    # Anchors should not be empty
    anchor_field = {
        "carousel": "Style anchor (carousel)",
        "video": "Shot anchor (per-shot prompt fragment)",
        "music": "Suno Style box (paste-ready, ≤200 chars)",
    }[mod]
    anchor_text = style.anchor(anchor_field)
    if not anchor_text or len(anchor_text) < 40:
        issues.append(f"'{anchor_field}' is empty or too short (need ≥40 chars)")

    return issues


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def template_path(modality: Modality, *, library_root: Path | None = None) -> Path:
    """Path to the bundled _template.md for a modality."""
    root = library_root or _BUNDLED_DIR
    return root / modality / "_template.md"


def copy_template(
    modality: Modality,
    new_id: str,
    *,
    user_dir: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Copy `<modality>/_template.md` to `<user_dir>/<modality>/<new_id>.md`,
    replacing the `<ID>` and `<modality>` placeholders.

    Returns the path of the newly created user-override file.
    Raises FileExistsError if the target exists and overwrite=False.
    Raises FileNotFoundError if the template doesn't exist.
    Raises ValueError if new_id isn't kebab-case.
    """
    if not _KEBAB_ID_RE.fullmatch(new_id):
        raise ValueError(f"id '{new_id}' must match ^[a-z][a-z0-9-]{{1,40}}$ (kebab-case)")

    tpl = template_path(modality)
    if not tpl.is_file():
        raise FileNotFoundError(f"no template for modality '{modality}' at {tpl}")

    user_root = user_dir or (Path.home() / ".claude" / "style-library")
    target = user_root / modality / f"{new_id}.md"

    if target.exists() and not overwrite:
        raise FileExistsError(f"style already exists at {target} (use overwrite=True to replace)")

    target.parent.mkdir(parents=True, exist_ok=True)
    body = tpl.read_text(encoding="utf-8")
    body = body.replace("<ID>", new_id).replace("<MODALITY>", modality)
    target.write_text(body, encoding="utf-8")
    return target


def copy_existing(
    source_id: str,
    new_id: str,
    modality: Modality,
    *,
    user_dir: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Copy an existing bundled style as a starting point for a new user style.

    Frontmatter `id` is rewritten to `new_id`. Display name gets a TODO suffix.
    """
    if not _KEBAB_ID_RE.fullmatch(new_id):
        raise ValueError(f"id '{new_id}' must match ^[a-z][a-z0-9-]{{1,40}}$ (kebab-case)")

    source = _default_library.load(source_id, modality)

    user_root = user_dir or (Path.home() / ".claude" / "style-library")
    target = user_root / modality / f"{new_id}.md"
    if target.exists() and not overwrite:
        raise FileExistsError(f"style already exists at {target} (use overwrite=True to replace)")

    text = source.source_path.read_text(encoding="utf-8")
    text = re.sub(r"^id:\s*.*$", f"id: {new_id}", text, count=1, flags=re.MULTILINE)
    text = re.sub(
        r'^display:\s*"(.+)"$',
        lambda m: f'display: "{m.group(1)} (custom)"',
        text,
        count=1,
        flags=re.MULTILINE,
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def resolution_status(style_id: str, modality: Modality) -> str:
    """Return one of: 'user-only' / 'override' / 'bundled' / 'missing'.

    - user-only: exists ONLY in user dir
    - override:  exists in both (user dir shadows bundled)
    - bundled:   exists ONLY in bundled
    - missing:   nowhere
    """
    user_path = _USER_DIR / modality / f"{style_id}.md"
    bundled_path = _BUNDLED_DIR / modality / f"{style_id}.md"
    user_exists = user_path.is_file()
    bundled_exists = bundled_path.is_file()
    if user_exists and bundled_exists:
        return "override"
    if user_exists:
        return "user-only"
    if bundled_exists:
        return "bundled"
    return "missing"


def resolved_path(style_id: str, modality: Modality) -> Path | None:
    """Return the actual file path the loader will use (user wins over bundled)."""
    user_path = _USER_DIR / modality / f"{style_id}.md"
    if user_path.is_file():
        return user_path
    bundled = _BUNDLED_DIR / modality / f"{style_id}.md"
    return bundled if bundled.is_file() else None


def bundled_dir() -> Path:
    return _BUNDLED_DIR


def user_dir() -> Path:
    return _USER_DIR
