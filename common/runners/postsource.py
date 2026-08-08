"""Turning a generated output directory into a Post.

Domain logic, deliberately not in the CLI. Working out that a directory of
`slide-*.png` plus a `captions.md` is a carousel with a particular caption has
nothing to do with argparse, and keeping it here means it can be tested without
one — which is what the discovery and caption-extraction tests do.

The two jobs:

  discover_media()   what kind of post do these files describe?
  extract_caption()  which part of a captions.md is the post body?

Both are tolerant by design. `captions.md` is written by an agent following a
convention, not by a runner emitting a schema, so the parser takes its best
guess and the CLI shows the result in the dry-run preview. A wrong guess that
is visible beats a strict parser that refuses a file someone hand-edited.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .errors import RunnerError
from .publishers.base import IMAGE_EXTS, VIDEO_EXTS, Post, PostKind

CAPTION_FILE = "captions.md"

# Headings under which carousel-builder / reel-builder put the main post body.
_MAIN_HEADING = re.compile(
    r"^#{1,6}\s*(main post|post caption|caption|post copy|основной пост|подпись)\b.*$",
    re.IGNORECASE,
)
_ANY_HEADING = re.compile(r"^#{1,6}\s+")


# ── captions ────────────────────────────────────────────────────────────────


def extract_caption(text: str) -> str:
    """Pull the main post body out of a captions.md, or fall back to the lot."""
    lines = text.splitlines()
    start = _find_main_heading(lines)

    if start is None:
        # No recognised heading — use everything, minus heading lines. Better to
        # over-include than to silently post an empty caption.
        return "\n".join(ln for ln in lines if not _ANY_HEADING.match(ln)).strip()

    collected = []
    for line in lines[start:]:
        if _ANY_HEADING.match(line.strip()):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def _find_main_heading(lines: list[str]) -> int | None:
    for i, line in enumerate(lines):
        if _MAIN_HEADING.match(line.strip()):
            return i + 1
    return None


def read_caption(source_dir: Path) -> str:
    path = source_dir / CAPTION_FILE
    if not path.is_file():
        return ""
    return extract_caption(path.read_text(encoding="utf-8"))


# ── media ───────────────────────────────────────────────────────────────────


def sort_media(paths: list[Path]) -> list[Path]:
    """Numeric-aware sort so slide-2 precedes slide-10."""

    def key(p: Path):
        return ([int(n) for n in re.findall(r"\d+", p.stem)], p.name)

    return sorted(paths, key=key)


def kind_for_file(path: Path) -> PostKind:
    ext = path.suffix.lower()
    if ext in VIDEO_EXTS:
        return "video"
    if ext in IMAGE_EXTS:
        return "image"
    raise RunnerError(f"unsupported file type: {path.name}")


def discover_media(source: Path) -> tuple[list[Path], PostKind]:
    """Work out what a generated output directory is holding."""
    if source.is_file():
        return [source], kind_for_file(source)
    return _discover_in_dir(source)


def _discover_in_dir(source: Path) -> tuple[list[Path], PostKind]:
    # A stitched reel wins over its own component frames.
    final = source / "final.mp4"
    if final.is_file():
        return [final], "video"

    videos = sort_media([p for p in source.glob("*") if p.suffix.lower() in VIDEO_EXTS])
    if videos:
        return ([videos[0]], "video") if len(videos) == 1 else (videos, "carousel")

    images = sort_media([p for p in source.glob("*") if p.suffix.lower() in IMAGE_EXTS])
    if len(images) > 1:
        return images, "carousel"
    if images:
        return images, "image"

    return [], "text"


# ── assembly ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PostOverrides:
    """What the caller supplies on top of what the directory already says.

    A dataclass rather than seven keyword arguments: the fields travel together
    from the CLI to the Post, and a signature that long invites callers to pass
    them positionally in the wrong order.

    `caption=None` means "read it from the source directory"; `caption=""`
    means the caller deliberately wants an empty one.
    """

    caption: str | None = None
    kind: PostKind | None = None
    title: str = ""
    hashtags: tuple[str, ...] = ()
    alt_texts: tuple[str, ...] = ()
    link: str | None = None
    # Article-only. Ignored by the social publishers, which never read them.
    canonical_url: str | None = None
    description: str = ""
    series: str | None = None
    extra: dict[str, object] = field(default_factory=dict)


def build_post(
    source: str | None, overrides: PostOverrides | None = None
) -> tuple[Post, Path | None]:
    """Assemble a Post. Returns it plus the directory that should hold posted.json."""
    spec = overrides or PostOverrides()
    media, detected, receipt_dir = _resolve_source(source)

    caption = spec.caption
    if caption is None:
        caption = read_caption(receipt_dir) if receipt_dir else ""

    post = Post(
        kind=spec.kind or detected,
        text=caption,
        media=tuple(media),
        alt_texts=spec.alt_texts,
        title=spec.title,
        link=spec.link,
        hashtags=spec.hashtags,
        canonical_url=spec.canonical_url,
        description=spec.description,
        series=spec.series,
        extra=dict(spec.extra),
    )
    return post, receipt_dir


def _resolve_source(source: str | None) -> tuple[list[Path], PostKind, Path | None]:
    if not source:
        return [], "text", None
    path = Path(source).expanduser()
    if not path.exists():
        raise RunnerError(f"source not found: {path}")
    media, kind = discover_media(path)
    return media, kind, (path if path.is_dir() else path.parent)
