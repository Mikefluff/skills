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
