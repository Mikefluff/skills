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

    # What `max_text_chars` counts. Every platform but YouTube documents a
    # character budget; YouTube's snippet.description is "a maximum length of
    # 5000 bytes", which is half as much text in Cyrillic and less than that
    # in CJK.
    text_unit: str = "chars"

    def measure_text(self, text: str) -> int:
        """Length of `text` in whatever unit this platform's limit is stated in."""
        return len(text.encode("utf-8")) if self.text_unit == "bytes" else len(text)

    def text_limit_for(self, post: "Post") -> int | None:
        """The caption budget for this particular post.

        One number per platform is the usual case. TikTok is not: photos and
        video are separate endpoints with separate budgets, so the limit
        depends on what is being posted rather than on where.
        """
        return self.max_text_chars

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
        """Run every generic rule, then the platform's own.

        Concrete rather than abstract on purpose: a subclass that forgot to call
        super() would skip the file-exists check and fail mid-upload with a
        confusing vendor error. Subclasses extend via `_extra_preflight()`, and
        `check-code-quality.py` fails the build if one overrides this instead.

        `draft` is passed through because it can change what is valid, not just
        what happens afterwards — TikTok's audit caveat applies to a direct post
        and is noise on a draft.
        """
        from .rules import GENERIC_RULES

        found: list[Violation] = []
        for rule in GENERIC_RULES:
            found.extend(rule(self, post, draft))
        found.extend(self._extra_preflight(post, draft=draft))
        return found

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
