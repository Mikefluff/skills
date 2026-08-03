"""LinkedIn publishing via the Posts API.

Scope note, because it decides whether this works at all: `w_member_social`
posts as the authenticated person and is available through ordinary OAuth.
Posting as a company page needs the Community Management API, which is
partner-gated — LinkedIn reviews the application and most are declined. This
module therefore targets member posts, and preflight says so rather than
letting someone discover it from a 403.

LinkedIn versions its API by a monthly `LinkedIn-Version` header rather than a
URL path, and rejects versions older than about a year. It is env-overridable
(LINKEDIN_API_VERSION) because that value ages out on a schedule no pinned
default can survive.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

from .. import oauth, tokens
from ..errors import PublishError, RateLimitError, RunnerError
from .base import IMAGE_EXTS, Post, Publisher, PublishResult, Violation, mime_for

API_ROOT = "https://api.linkedin.com"
DEFAULT_VERSION = "202401"

TEXT_LIMIT = 3000


class LinkedInPublisher(Publisher):
    name = "linkedin"
    requires_env = ("LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET")
    requires_oauth = True
    supports = frozenset({"text", "image", "carousel", "video"})
    supports_draft = False
    needs_public_media_url = False
    doc_url = "https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api"

    max_text_chars = TEXT_LIMIT
    max_hashtags = 5  # LinkedIn's own guidance; more actively suppresses reach
    min_media = 0
    max_media = 20
    max_image_mb = 10.0
    max_video_mb = 500.0

    oauth_scopes = ("w_member_social", "openid", "profile")

    def api_version(self) -> str:
        return os.environ.get("LINKEDIN_API_VERSION", DEFAULT_VERSION)

    # ── plumbing ────────────────────────────────────────────────────────────

    def _headers(self, token: str | None = None) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token or tokens.get_valid(self.name)}",
            "LinkedIn-Version": self.api_version(),
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def _request(self, method: str, path: str, *, token: str | None = None, **kwargs) -> dict[str, Any]:
        url = path if path.startswith("http") else f"{API_ROOT}{path}"
        headers = kwargs.pop("headers", {})
        headers.update(self._headers(token))
        kwargs.setdefault("timeout", 120)
        try:
            resp = requests.request(method, url, headers=headers, **kwargs)
        except requests.RequestException as exc:
            raise PublishError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            raise RateLimitError(self.name, 429, "rate limited")
        if resp.status_code >= 400:
            detail = resp.text[:300]
            if resp.status_code == 403:
                detail += (
                    " — if this is a company page, it needs the partner-gated "
                    "Community Management API; member posts need only w_member_social"
                )
            raise PublishError(self.name, resp.status_code, detail)

        # A created post returns its URN in a header, with an empty body.
        created = resp.headers.get("x-restli-id") or resp.headers.get("x-linkedin-id")
        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            data = {}
        if created:
            data.setdefault("id", created)
        return data

    def author_urn(self) -> str:
        override = os.environ.get("LINKEDIN_AUTHOR_URN")
        if override:
            return override
        entry = tokens.read(self.name)
        if entry is None or not entry.account_id:
            raise RunnerError("linkedin: no member id stored — re-run cli.auth")
        return f"urn:li:person:{entry.account_id}"

    # ── media ───────────────────────────────────────────────────────────────

    def _upload_media(self, path: Path) -> str:
        is_image = path.suffix.lower() in IMAGE_EXTS
        resource = "images" if is_image else "videos"
        init = self._request(
            "POST",
            f"/rest/{resource}?action=initializeUpload",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"initializeUploadRequest": {"owner": self.author_urn()}}),
        )
        value = init.get("value", {})
        upload_url = value.get("uploadUrl") or (value.get("uploadInstructions") or [{}])[0].get("uploadUrl")
        urn = value.get("image") or value.get("video")
        if not upload_url or not urn:
            raise PublishError(self.name, None, f"upload init returned no url/urn: {init}")

        try:
            resp = requests.put(
                upload_url,
                data=path.read_bytes(),
                headers={"Content-Type": mime_for(path)},
                timeout=600,
            )
        except requests.RequestException as exc:
            raise PublishError(self.name, None, f"media upload failed: {exc}") from exc
        if resp.status_code >= 400:
            raise PublishError(self.name, resp.status_code, f"media upload rejected: {resp.text[:200]}")
        return urn

    # ── publish ─────────────────────────────────────────────────────────────

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        if draft:
            raise PublishError(self.name, None, "LinkedIn has no draft API for member posts")
        self.ensure_available()

        body: dict[str, Any] = {
            "author": self.author_urn(),
            "commentary": post.rendered_text(),
            "visibility": os.environ.get("LINKEDIN_VISIBILITY", "PUBLIC"),
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }

        if len(post.media) == 1:
            urn = self._upload_media(post.media[0])
            body["content"] = {"media": {"id": urn, "altText": post.alt_for(0)}}
        elif len(post.media) > 1:
            elements = []
            for i, path in enumerate(post.media):
                elements.append({"id": self._upload_media(path), "altText": post.alt_for(i)})
            body["content"] = {"multiImage": {"images": elements}}

        data = self._request(
            "POST", "/rest/posts", headers={"Content-Type": "application/json"}, data=json.dumps(body)
        )
        post_id = str(data.get("id", ""))
        permalink = (
            f"https://www.linkedin.com/feed/update/{post_id}" if post_id.startswith("urn:") else None
        )
        return PublishResult(
            platform=self.name, post_id=post_id, state="published", permalink=permalink
        )

    # ── preflight ───────────────────────────────────────────────────────────

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        v: list[Violation] = []
        if post.kind == "text" and not post.text.strip():
            v.append(Violation("block", "text", "a text post needs text"))
        if os.environ.get("LINKEDIN_AUTHOR_URN", "").startswith("urn:li:organization"):
            v.append(
                Violation(
                    "warn",
                    "author",
                    "posting as an organisation needs the partner-gated Community Management "
                    "API; expect 403 unless the app was approved for it",
                )
            )
        videos = [p for p in post.media if p.suffix.lower() not in IMAGE_EXTS]
        if videos and len(post.media) > 1:
            v.append(Violation("block", "media", "LinkedIn takes one video, or several images — not both"))
        return v

    # ── authorisation ───────────────────────────────────────────────────────

    def oauth_app(self):
        return oauth.get_app(self.name)

    def verify_token(self, access_token: str) -> tuple[str, str]:
        try:
            resp = requests.get(
                f"{API_ROOT}/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=60,
            )
            data = resp.json() if resp.content else {}
        except (requests.RequestException, ValueError) as exc:
            raise RunnerError(f"linkedin: could not verify token: {exc}") from exc
        if resp.status_code >= 400:
            raise RunnerError(f"linkedin: token rejected: {resp.text[:200]}")
        return str(data.get("sub", "")), str(data.get("name", ""))

    def finalize_auth(self, raw: dict[str, Any]):
        access = raw.get("access_token")
        if not access:
            raise RunnerError(f"linkedin: token response had no access_token: {raw}")
        account_id = label = ""
        try:
            account_id, label = self.verify_token(access)
        except RunnerError:
            pass
        return tokens.TokenEntry(
            platform=self.name,
            access_token=access,
            refresh_token=raw.get("refresh_token"),
            expires_at=time.time() + float(raw.get("expires_in", 5_184_000)),  # 60 days
            scopes=list(self.oauth_scopes),
            account_id=account_id,
            account_label=label,
        )

    def refresh(self, entry: tokens.TokenEntry) -> tokens.TokenEntry:
        if not entry.refresh_token:
            raise RunnerError(
                "linkedin: no refresh token — refresh tokens are only issued to apps "
                "approved for them. Re-run cli.auth to get a fresh 60-day token."
            )
        resp = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "refresh_token",
                "refresh_token": entry.refresh_token,
                "client_id": os.environ.get("LINKEDIN_CLIENT_ID", ""),
                "client_secret": os.environ.get("LINKEDIN_CLIENT_SECRET", ""),
            },
            timeout=60,
        )
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400 or "access_token" not in data:
            raise RunnerError(f"linkedin: refresh failed: {resp.text[:200]}")
        entry.access_token = data["access_token"]
        entry.refresh_token = data.get("refresh_token", entry.refresh_token)
        entry.expires_at = time.time() + float(data.get("expires_in", 5_184_000))
        return entry


_PUBLISHER = LinkedInPublisher()

oauth.register_app(
    oauth.OAuthApp(
        platform="linkedin",
        authorize_url="https://www.linkedin.com/oauth/v2/authorization",
        token_url="https://www.linkedin.com/oauth/v2/accessToken",
        scopes=_PUBLISHER.oauth_scopes,
        client_id_env="LINKEDIN_CLIENT_ID",
        client_secret_env="LINKEDIN_CLIENT_SECRET",
        setup_url="https://www.linkedin.com/developers/apps",
    )
)

tokens.register_refresher("linkedin", _PUBLISHER.refresh)

from ..config import register_publisher  # noqa: E402

register_publisher(_PUBLISHER)
