"""Threads publishing via the official Threads API.

The gentler half of the Meta pair, and the right one to connect first:

  · a text-only post needs no media, so no S3 bucket and no staging;
  · a personal Threads account is enough — no business conversion, no linked
    Facebook Page;
  · the posting cap (250/day) is high enough that you will not meet it.

The 500-character limit is the thing that actually bites. viral-text already
knows it (skills/viral-text/references/platforms.md), so a post drafted for Threads
usually fits; a caption written for Instagram never does, which is why
preflight measures the rendered text including hashtags.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import oauth, tokens
from .base import IMAGE_EXTS, Post, Violation
from ._meta import MetaPublisher

API_ROOT = "https://graph.threads.net"

TEXT_LIMIT = 500
CAROUSEL_MIN = 2
CAROUSEL_MAX = 20
DAILY_POST_CAP = 250


class ThreadsPublisher(MetaPublisher):
    name = "threads"
    requires_env = ("THREADS_APP_ID", "THREADS_APP_SECRET")
    supports = frozenset({"text", "image", "carousel", "video"})
    doc_url = "https://developers.facebook.com/docs/threads"

    api_root = API_ROOT
    api_version_env = "THREADS_API_VERSION"
    default_api_version = "v1.0"
    container_path = "threads"
    publish_path = "threads_publish"
    status_field = "status"
    text_param = "text"
    user_id_env = "THREADS_USER_ID"
    secret_env = "THREADS_APP_SECRET"

    max_text_chars = TEXT_LIMIT
    max_hashtags = 5  # Threads surfaces one topic tag; a wall of them reads as spam
    min_media = 0
    max_media = CAROUSEL_MAX
    max_image_mb = 8.0
    max_video_mb = 1024.0

    oauth_scopes = ("threads_basic", "threads_content_publish")
    exchange_url = f"{API_ROOT}/access_token"
    exchange_grant = "th_exchange_token"
    refresh_url = f"{API_ROOT}/refresh_access_token"
    refresh_grant = "th_refresh_token"

    def _media_params(self, path: Path, url: str) -> dict[str, Any]:
        if path.suffix.lower() in IMAGE_EXTS:
            return {"media_type": "IMAGE", "image_url": url}
        return {"media_type": "VIDEO", "video_url": url}

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        v = super()._extra_preflight(post, draft=draft)
        if post.kind == "carousel" and len(post.media) > CAROUSEL_MAX:
            v.append(Violation("block", "media", f"a Threads carousel holds at most {CAROUSEL_MAX} items"))
        if post.kind == "text" and not post.text.strip():
            v.append(Violation("block", "text", "a text post needs text"))
        return v


_PUBLISHER = ThreadsPublisher()

oauth.register_app(
    oauth.OAuthApp(
        platform="threads",
        authorize_url="https://threads.net/oauth/authorize",
        token_url=f"{API_ROOT}/oauth/access_token",
        scopes=_PUBLISHER.oauth_scopes,
        client_id_env="THREADS_APP_ID",
        client_secret_env="THREADS_APP_SECRET",
        scope_sep=",",
        setup_url="https://developers.facebook.com/docs/threads/get-started",
    )
)

tokens.register_refresher("threads", _PUBLISHER.refresh)

from ..config import register_publisher  # noqa: E402

register_publisher(_PUBLISHER)
