"""Preflight rules — one function per thing that can be wrong with a post.

`Publisher.preflight()` used to be a hundred-line method that checked ten
unrelated things in sequence. Every new platform quirk made it longer, and no
single rule could be tested without constructing a whole publisher.

Each rule here is a plain function with the same shape:

    (publisher, post, draft) -> list[Violation]

so they compose, they can be reordered, a platform can opt out of one, and each
can be tested against a stub. `GENERIC_RULES` is the sequence every platform
runs before its own `_extra_preflight()`.

Rules must not perform I/O beyond stat()ing the media the caller already named.
Anything that needs the network belongs in a platform's own preflight, where it
can be gated on credentials being present.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from .base import IMAGE_EXTS, MB, VIDEO_EXTS, Post, Violation

if TYPE_CHECKING:
    from .base import Publisher

Rule = Callable[["Publisher", Post, bool], list[Violation]]


def check_kind(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    if post.kind in pub.supports:
        return []
    return [
        Violation(
            "block",
            "kind",
            f"{pub.name} does not support {post.kind} posts "
            f"(supported: {', '.join(sorted(pub.supports))})",
        )
    ]


def check_text_length(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    limit = pub.text_limit_for(post)
    if limit is None:
        return []
    # Measured on the rendered text, hashtags included, because that is what
    # the platform receives — not on the body the author typed. The unit is the
    # platform's: YouTube states its description budget in bytes.
    text = post.rendered_text()
    size = pub.measure_text(text)
    if size <= limit:
        return []
    unit = pub.text_unit
    over = f"(over by {size - limit})"
    if unit == "bytes":
        over = f"(over by {size - limit}; {len(text)} characters)"
    return [
        Violation("block", "text", f"{size} {unit} exceeds the {limit}-{unit.rstrip('s')} limit {over}")
    ]


def check_title_length(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    if pub.max_title_chars is None or len(post.title) <= pub.max_title_chars:
        return []
    return [
        Violation(
            "block", "title", f"{len(post.title)} chars exceeds the {pub.max_title_chars}-char limit"
        )
    ]


def check_hashtag_count(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    if pub.max_hashtags is None or len(post.hashtags) <= pub.max_hashtags:
        return []
    return [
        Violation(
            "warn",
            "hashtags",
            f"{len(post.hashtags)} hashtags; {pub.name} tolerates about "
            f"{pub.max_hashtags} before it reads as spam",
        )
    ]


def check_media_count(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    n = len(post.media)
    out = []
    if n < pub.min_media:
        out.append(Violation("block", "media", f"needs at least {pub.min_media} file(s), got {n}"))
    if n > pub.max_media:
        out.append(Violation("block", "media", f"accepts at most {pub.max_media} file(s), got {n}"))
    return out


def check_media_files(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    out: list[Violation] = []
    for path in post.media:
        out.extend(_check_one_file(pub, path))
    return out


def _check_one_file(pub: "Publisher", path: Path) -> list[Violation]:
    if not path.is_file():
        return [Violation("block", "media", f"file not found: {path}")]

    size_bytes = path.stat().st_size
    if size_bytes == 0:
        return [Violation("block", "media", f"file is empty: {path.name}")]

    ext = path.suffix.lower()
    size_mb = size_bytes / MB

    if ext in IMAGE_EXTS:
        limit = pub.max_image_mb
        label = "images"
    elif ext in VIDEO_EXTS:
        limit = pub.max_video_mb
        label = "video"
    else:
        return [
            Violation(
                "block",
                "media",
                f"unrecognised media type '{ext}' ({path.name}); "
                f"expected one of {', '.join(sorted(IMAGE_EXTS | VIDEO_EXTS))}",
            )
        ]

    if limit and size_mb > limit:
        return [
            Violation(
                "block",
                "media",
                f"{path.name} is {size_mb:.1f} MB; {pub.name} caps {label} at {limit} MB",
            )
        ]
    return []


def check_alt_text(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    if not post.media:
        return []
    if not post.alt_texts:
        return [Violation("warn", "alt_texts", "no alt text — hurts reach and accessibility")]
    if len(post.alt_texts) >= len(post.media):
        return []
    # Partial alt text is the likelier mistake than none at all: --alt is
    # repeated per file, so describing the first two slides and forgetting the
    # rest is easy. Naming the gap beats a generic nudge.
    first_missing = len(post.alt_texts) + 1
    total = len(post.media)
    span = f"file {first_missing}" if first_missing == total else f"files {first_missing}-{total}"
    return [
        Violation(
            "warn",
            "alt_texts",
            f"{len(post.alt_texts)} alt texts for {total} files — {span} will go without",
        )
    ]


def check_media_hosting(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    if not pub.needs_public_media_url or not post.media:
        return []
    from ..storage import s3

    if s3.s3_configured():
        return []
    return [
        Violation(
            "block",
            "media",
            f"{pub.name} fetches media by URL and cannot accept raw bytes. "
            f"Set S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY in ~/.skills.env. "
            f"(--draft does not avoid this: staging the container is what "
            f"needs the URL. Without a bucket, post it by hand — see "
            f"references/browser-fallback.md.)",
        )
    ]


def check_article_shape(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    """An article needs a headline, a body, and somewhere to point home.

    The canonical warning is the one that matters. Syndicating without it is
    worse than not syndicating: search engines see the same text on several
    domains, pick one, and it is rarely the author's.
    """
    if post.kind != "article":
        return []

    out: list[Violation] = []
    if not post.title.strip():
        out.append(Violation("block", "title", "an article needs a title"))
    if not post.text.strip():
        out.append(Violation("block", "text", "an article needs a body"))
    if not post.canonical_url:
        out.append(
            Violation(
                "warn",
                "canonical_url",
                "no canonical URL — this platform becomes the original. Pass "
                "--canonical <your-url> to keep the ranking signal on your own domain",
            )
        )
    elif not post.canonical_url.startswith(("http://", "https://")):
        out.append(
            Violation("block", "canonical_url", f"not an absolute URL: {post.canonical_url}")
        )
    return out


def check_draft_support(pub: "Publisher", post: Post, draft: bool) -> list[Violation]:
    if draft and not pub.supports_draft:
        return [Violation("block", "draft", f"{pub.name} has no draft concept")]
    return []


# Order matters only for readability of the output: cheap structural checks
# first, then per-file work, then the ones that consult configuration.
GENERIC_RULES: tuple[Rule, ...] = (
    check_kind,
    check_text_length,
    check_title_length,
    check_hashtag_count,
    check_media_count,
    check_media_files,
    check_alt_text,
    check_media_hosting,
    check_article_shape,
    check_draft_support,
)
