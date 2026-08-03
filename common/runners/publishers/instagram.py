"""Instagram publishing via the Instagram API with Instagram Login.

Two routes exist to publish on Instagram. This module takes the newer one —
`graph.instagram.com` with Instagram Login — because the older route
(`graph.facebook.com` with Facebook Login for Business) additionally requires
the account to be linked to a Facebook Page, which is a setup step most people
publishing their own content do not want and do not need.

Still required, and there is no way around it: a Business or Creator account.
Instagram does not publish to personal accounts through any API. If that is a
blocker, the browser path in the skill's references/browser-fallback.md is the
honest alternative — not a different endpoint.

Three constraints shape the code:

  · Media is fetched by Instagram from a URL. Local bytes are never accepted,
    so S3 staging is mandatory and preflight blocks without it.
  · Video is Reels. There is no "video feed post" any more; media_type=REELS
    is the only video container that publishes.
  · 25 published posts per rolling 24h. The account can be asked how much of
    that it has spent, so it is asked before publishing rather than after.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import oauth, tokens
from ..errors import RunnerError
from .base import IMAGE_EXTS, Post, PublishResult, Violation
from ._meta import MetaPublisher

API_ROOT = "https://graph.instagram.com"

CAPTION_LIMIT = 2200
HASHTAG_LIMIT = 30
CAROUSEL_MIN = 2
CAROUSEL_MAX = 10

# 100, not the 25 this was first written with. Meta raised the API publishing
# cap and the old figure would have blocked three quarters of a legitimate day.
# Verified 2026-08-03 against developers.facebook.com/docs/instagram-platform/
# content-publishing — "limited to 100 API-published posts within a 24-hour
# moving period".
DAILY_POST_CAP = 100

# Reels cap at 300 MB and 15 minutes; 1 GB was wrong.
REELS_MAX_MB = 300.0
REELS_MAX_SECONDS = 15 * 60
REELS_MIN_SECONDS = 3


class InstagramPublisher(MetaPublisher):
    name = "instagram"
    requires_env = ("INSTAGRAM_APP_ID", "INSTAGRAM_APP_SECRET")
    supports = frozenset({"image", "carousel", "video"})  # no text-only posts
    doc_url = "https://developers.facebook.com/docs/instagram-platform/content-publishing"

    api_root = API_ROOT
    api_version_env = "INSTAGRAM_API_VERSION"
    default_api_version = "v25.0"
    container_path = "media"
    publish_path = "media_publish"
    status_field = "status_code"
    text_param = "caption"
    user_id_env = "INSTAGRAM_USER_ID"
    secret_env = "INSTAGRAM_APP_SECRET"

    max_text_chars = CAPTION_LIMIT
    max_hashtags = HASHTAG_LIMIT
    min_media = 1
    max_media = CAROUSEL_MAX
    max_image_mb = 8.0
    max_video_mb = REELS_MAX_MB

    oauth_scopes = ("instagram_business_basic", "instagram_business_content_publish")
    exchange_url = f"{API_ROOT}/access_token"
    exchange_grant = "ig_exchange_token"
    refresh_url = f"{API_ROOT}/refresh_access_token"
    refresh_grant = "ig_refresh_token"

    def _media_params(self, path: Path, url: str) -> dict[str, Any]:
        if path.suffix.lower() in IMAGE_EXTS:
            return {"image_url": url}
        # Video only publishes as a Reel; a plain video container is rejected.
        return {"media_type": "REELS", "video_url": url}

    # ── posting cap ─────────────────────────────────────────────────────────

    def quota_used(self) -> int | None:
        """Posts spent from the rolling 24h allowance, or None if unavailable."""
        try:
            data = self._call(
                "GET",
                f"{self.user_id()}/content_publishing_limit",
                params={"fields": "config,quota_usage"},
            )
        except RunnerError:
            return None
        rows = data.get("data") or []
        if not rows:
            return None
        return int(rows[0].get("quota_usage", 0))

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        # Asked before the work, not after: staging a Reel to S3 and waiting a
        # minute for Meta to ingest it, only to be refused at the last step,
        # wastes the upload and leaves an orphan container.
        used = self.quota_used()
        if used is not None and used >= DAILY_POST_CAP:
            from ..errors import RateLimitError

            raise RateLimitError(
                self.name,
                None,
                f"{used}/{DAILY_POST_CAP} posts used in the last 24h — Instagram will refuse this one",
            )
        result = super().publish(post, draft=draft)
        if used is not None and result.state == "published":
            result.note = f"{used + 1}/{DAILY_POST_CAP} of the 24h posting allowance used"
        return result

    # ── preflight ───────────────────────────────────────────────────────────

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        v = super()._extra_preflight(post, draft=draft)

        if post.kind == "carousel" and len(post.media) > CAROUSEL_MAX:
            v.append(Violation("block", "media", f"an Instagram carousel holds at most {CAROUSEL_MAX} items"))

        if post.kind == "video":
            v.append(
                Violation(
                    "warn",
                    "media",
                    "video publishes as a Reel — there is no plain video feed post via the API",
                )
            )

        used = None
        if self.available() and self.token_ready():
            used = self.quota_used()
        if used is not None and used >= DAILY_POST_CAP:
            v.append(
                Violation("block", "quota", f"{used}/{DAILY_POST_CAP} posts used in the last 24h")
            )
        elif used is not None and used >= DAILY_POST_CAP - 3:
            v.append(
                Violation("warn", "quota", f"{used}/{DAILY_POST_CAP} posts used in the last 24h")
            )

        return v


_PUBLISHER = InstagramPublisher()

oauth.register_app(
    oauth.OAuthApp(
        platform="instagram",
        authorize_url="https://www.instagram.com/oauth/authorize",
        token_url="https://api.instagram.com/oauth/access_token",
        scopes=_PUBLISHER.oauth_scopes,
        client_id_env="INSTAGRAM_APP_ID",
        client_secret_env="INSTAGRAM_APP_SECRET",
        scope_sep=",",
        setup_url="https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login",
    )
)

tokens.register_refresher("instagram", _PUBLISHER.refresh)

from ..config import register_publisher  # noqa: E402

register_publisher(_PUBLISHER)
