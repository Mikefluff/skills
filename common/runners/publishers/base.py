"""Publisher ABC + shared dataclasses.

Sibling of `providers/base.py`, deliberately NOT a subclass of it. A provider
turns a prompt into bytes and can be retried for free. A publisher takes bytes
that already exist and does something irreversible and outward-facing with
them. Different contract, different failure modes:

  provider   generate(prompt, **kwargs) -> bytes      · costs money · retryable
  publisher  publish(post, draft=...)   -> permalink  · costs nothing · NOT retryable

So there is no `estimate_cost()` here. Instead there is `preflight()`, which
every caller must run before `publish()`, and a `supports_draft` flag so the
CLI can offer the safe path where a platform has one.
"""

from __future__ import annotations

import hashlib
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from ..errors import KeyMissingError

PostKind = Literal["text", "image", "carousel", "video"]
PostState = Literal["published", "draft", "pending_review"]
Severity = Literal["block", "warn"]

# Extensions we recognise. Anything else gets flagged by preflight rather than
# being silently POSTed with a wrong Content-Type.
IMAGE_EXTS = frozenset({".jpg", ".jpeg", ".png", ".webp"})
VIDEO_EXTS = frozenset({".mp4", ".mov", ".m4v", ".webm"})

MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".m4v": "video/x-m4v",
    ".webm": "video/webm",
}

MB = 1024 * 1024


def mime_for(path: Path) -> str:
    return MIME_BY_EXT.get(path.suffix.lower(), "application/octet-stream")


@dataclass
class Violation:
    """One preflight finding.

    `block` means publish() must not be called. `warn` means the post will go
    through but something is off (truncation, unusual aspect, missing alt text).
    """

    severity: Severity
    field: str
    message: str

    def __str__(self) -> str:
        mark = "BLOCK" if self.severity == "block" else "warn "
        return f"{mark} {self.field}: {self.message}"


@dataclass
class Post:
    """Platform-neutral envelope. One Post can be sent to several publishers.

    `text` is the caption/body as authored. `hashtags` stay separate so that
    preflight can count them and each platform can place them where it belongs
    (Instagram: in the caption; YouTube: in the description; TikTok: in title).
    """

    kind: PostKind
    text: str = ""
    media: tuple[Path, ...] = ()
    alt_texts: tuple[str, ...] = ()
    title: str = ""  # YouTube video title, LinkedIn article title
    link: str | None = None
    thread: tuple[str, ...] = ()  # X threads / Threads reply chains
    hashtags: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Accept lists/strings/Paths from callers and normalise once, so every
        # publisher downstream can assume tuples of Path.
        if isinstance(self.media, (str, Path)):
            self.media = (Path(self.media),)
        else:
            self.media = tuple(Path(m) for m in self.media)
        self.alt_texts = tuple(self.alt_texts)
        self.thread = tuple(self.thread)
        self.hashtags = tuple(h.lstrip("#") for h in self.hashtags if h.strip())

    def rendered_text(self, *, hashtag_sep: str = "\n\n") -> str:
        """Caption with hashtags appended. What most platforms actually receive."""
        body = self.text.strip()
        if not self.hashtags:
            return body
        tags = " ".join(f"#{h}" for h in self.hashtags)
        return f"{body}{hashtag_sep}{tags}" if body else tags

    def alt_for(self, index: int) -> str:
        return self.alt_texts[index] if index < len(self.alt_texts) else ""

    def content_hash(self) -> str:
        """Stable fingerprint used for the duplicate-post receipt check.

        Media is fingerprinted by (name, size) rather than by bytes — hashing a
        1 GB video on every dry-run would be absurd, and a same-name same-size
        file in the same output dir is the case we actually need to catch
        (re-running the same publish command twice).
        """
        h = hashlib.sha256()
        h.update(self.kind.encode())
        h.update(b"\x00")
        h.update(self.text.strip().encode())
        h.update(b"\x00")
        h.update(self.title.strip().encode())
        h.update(b"\x00")
        h.update(" ".join(self.hashtags).encode())
        for m in self.media:
            h.update(b"\x00")
            h.update(m.name.encode())
            try:
                h.update(str(m.stat().st_size).encode())
            except OSError:
                h.update(b"missing")
        return h.hexdigest()[:16]


@dataclass
class PublishResult:
    platform: str
    post_id: str
    state: PostState
    permalink: str | None = None
    note: str = ""  # e.g. "landed in TikTok inbox — finish in the app"
    extra: dict[str, Any] = field(default_factory=dict)

    def display(self) -> str:
        head = f"{self.platform}: {self.state}"
        if self.permalink:
            head += f" → {self.permalink}"
        elif self.post_id:
            head += f" (id {self.post_id})"
        return f"{head}\n  {self.note}" if self.note else head


class Publisher(ABC):
    """Platform adapter — subclass and implement publish()."""

    name: str  # canonical slug: "telegram", "instagram", ...
    requires_env: tuple[str, ...] = ()  # app-level creds from ~/.skills.env
    requires_oauth: bool = False  # user token from ~/.skills-tokens.json
    supports: frozenset[PostKind] = frozenset()
    supports_draft: bool = False
    needs_public_media_url: bool = False  # platform fetches media itself (Meta)
    doc_url: str = ""

    # Generic limits — subclasses override with real numbers. None = no limit.
    max_text_chars: int | None = None
    max_title_chars: int | None = None
    max_hashtags: int | None = None
    min_media: int = 0
    max_media: int = 1
    max_image_mb: float | None = None
    max_video_mb: float | None = None

    # ── availability ────────────────────────────────────────────────────────

    def available(self) -> bool:
        """True when app creds are present. OAuth token presence is checked
        separately by `token_ready()` — a platform can be configured but not
        yet authorised, and the two need distinct messages."""
        return all(os.environ.get(k) for k in self.requires_env)

    def missing_env(self) -> list[str]:
        return [k for k in self.requires_env if not os.environ.get(k)]

    def ensure_available(self) -> None:
        if not self.available():
            raise KeyMissingError(self.name, self.missing_env(), kind="platform")

    def token_ready(self) -> bool:
        """Whether a usable OAuth token exists. Non-OAuth platforms are always ready."""
        if not self.requires_oauth:
            return True
        from .. import tokens

        return tokens.has_usable(self.name)

    # ── authorisation hooks (overridden by OAuth platforms) ─────────────────

    def oauth_app(self) -> Any | None:
        """Return this platform's OAuthApp, or None if it needs no OAuth flow."""
        return None

    def finalize_auth(self, raw: dict[str, Any]) -> Any:
        """Turn a raw token response into a TokenEntry.

        Kept per-platform because the responses barely agree on anything: some
        return `expires_in`, some an absolute `expires_at`, some neither; the
        account identifier may need a second call to fetch.
        """
        raise NotImplementedError(f"{self.name} does not implement finalize_auth()")

    def verify_token(self, access_token: str) -> tuple[str, str]:
        """Confirm a token works and return (account_id, account_label).

        Used both after the OAuth flow and by `--paste-token`, so that a bad
        paste fails here rather than at 2 a.m. mid-publish.
        """
        raise NotImplementedError(f"{self.name} does not implement verify_token()")

    # ── preflight ───────────────────────────────────────────────────────────

    def preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        """Generic checks every platform needs, plus the subclass hook.

        Concrete rather than abstract on purpose: a subclass that forgets to
        call super() would skip the file-exists check and fail mid-upload with
        a confusing vendor error. Subclasses extend via `_extra_preflight()`.

        `draft` is passed through because it can change what is valid, not just
        what happens afterwards — TikTok's audit caveat applies to a direct post
        and is noise on a draft.
        """
        v: list[Violation] = []

        if post.kind not in self.supports:
            v.append(
                Violation(
                    "block",
                    "kind",
                    f"{self.name} does not support {post.kind} posts "
                    f"(supported: {', '.join(sorted(self.supports))})",
                )
            )

        text = post.rendered_text()
        if self.max_text_chars is not None and len(text) > self.max_text_chars:
            v.append(
                Violation(
                    "block",
                    "text",
                    f"{len(text)} chars exceeds the {self.max_text_chars}-char limit "
                    f"(over by {len(text) - self.max_text_chars})",
                )
            )

        if self.max_title_chars is not None and len(post.title) > self.max_title_chars:
            v.append(
                Violation(
                    "block",
                    "title",
                    f"{len(post.title)} chars exceeds the {self.max_title_chars}-char limit",
                )
            )

        if self.max_hashtags is not None and len(post.hashtags) > self.max_hashtags:
            v.append(
                Violation(
                    "warn",
                    "hashtags",
                    f"{len(post.hashtags)} hashtags; {self.name} tolerates about "
                    f"{self.max_hashtags} before it reads as spam",
                )
            )

        n = len(post.media)
        if n < self.min_media:
            v.append(Violation("block", "media", f"needs at least {self.min_media} file(s), got {n}"))
        if n > self.max_media:
            v.append(Violation("block", "media", f"accepts at most {self.max_media} file(s), got {n}"))

        for m in post.media:
            v.extend(self._check_file(m))

        if post.media and not post.alt_texts:
            v.append(Violation("warn", "alt_texts", "no alt text — hurts reach and accessibility"))
        elif post.media and len(post.alt_texts) < len(post.media):
            # Partial alt text is the likelier mistake than none at all: --alt is
            # repeated per file, so it is easy to describe the first two slides
            # and forget the rest. Naming the gap beats a generic nudge.
            first_missing = len(post.alt_texts) + 1
            v.append(
                Violation(
                    "warn",
                    "alt_texts",
                    f"{len(post.alt_texts)} alt texts for {len(post.media)} files — "
                    f"{'file' if first_missing == len(post.media) else 'files'} "
                    f"{first_missing}"
                    f"{'' if first_missing == len(post.media) else f'-{len(post.media)}'} "
                    f"will go without",
                )
            )

        if self.needs_public_media_url and post.media:
            from ..storage import s3

            if not s3.s3_configured():
                v.append(
                    Violation(
                        "block",
                        "media",
                        f"{self.name} fetches media by URL and cannot accept raw bytes. "
                        f"Set S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY in ~/.skills.env. "
                        f"(--draft does not avoid this: staging the container is what "
                        f"needs the URL. Without a bucket, post it by hand — see "
                        f"references/browser-fallback.md.)",
                    )
                )

        if draft and not self.supports_draft:
            v.append(Violation("block", "draft", f"{self.name} has no draft concept"))

        v.extend(self._extra_preflight(post, draft=draft))
        return v

    def _check_file(self, path: Path) -> list[Violation]:
        v: list[Violation] = []
        if not path.is_file():
            v.append(Violation("block", "media", f"file not found: {path}"))
            return v

        ext = path.suffix.lower()
        size_bytes = path.stat().st_size
        if size_bytes == 0:
            v.append(Violation("block", "media", f"file is empty: {path.name}"))
            return v
        size_mb = size_bytes / MB

        if ext in IMAGE_EXTS:
            if self.max_image_mb and size_mb > self.max_image_mb:
                v.append(
                    Violation(
                        "block",
                        "media",
                        f"{path.name} is {size_mb:.1f} MB; {self.name} caps images at {self.max_image_mb} MB",
                    )
                )
        elif ext in VIDEO_EXTS:
            if self.max_video_mb and size_mb > self.max_video_mb:
                v.append(
                    Violation(
                        "block",
                        "media",
                        f"{path.name} is {size_mb:.1f} MB; {self.name} caps video at {self.max_video_mb} MB",
                    )
                )
        else:
            v.append(
                Violation(
                    "block",
                    "media",
                    f"unrecognised media type '{ext}' ({path.name}); "
                    f"expected one of {', '.join(sorted(IMAGE_EXTS | VIDEO_EXTS))}",
                )
            )
        return v

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:  # noqa: ARG002
        """Platform-specific rules. Override; default is no extra rules."""
        return []

    # ── publish ─────────────────────────────────────────────────────────────

    @abstractmethod
    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        """Send it. Callers must have run preflight() and confirmed with the user."""

    def info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "requires_env": list(self.requires_env),
            "requires_oauth": self.requires_oauth,
            "supports": sorted(self.supports),
            "supports_draft": self.supports_draft,
            "available": self.available(),
            "token_ready": self.token_ready(),
        }
