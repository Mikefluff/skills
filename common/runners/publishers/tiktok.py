"""TikTok publishing via the Content Posting API.

The one platform where the default is deliberately NOT to publish.

TikTok gates direct publishing behind an app audit. An unaudited app can call
the direct-post endpoint, but everything it posts is forced to SELF_ONLY — the
call succeeds, the post exists, and nobody can see it. That failure mode is
invisible from the API response, which makes it exactly the kind of thing this
layer should refuse to walk into quietly.

So the mapping is inverted compared to the other platforms:

    --draft  (default advice)  → /inbox/video/init/   lands in the app's inbox,
                                 creator finishes and publishes by hand.
                                 No audit needed. Always works.
    no --draft                 → /video/init/         real direct post. Requires
                                 an audited app; preflight says so loudly.

Video uses FILE_UPLOAD, so bytes go straight from disk — no S3 needed. Photo
carousels are the exception: TikTok only accepts photos via PULL_FROM_URL, and
that URL's domain must be verified in the developer portal. Preflight flags it
rather than letting the upload fail three steps later.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

import requests

from .. import oauth, tokens
from ..errors import PublishError, RateLimitError, RunnerError
from . import _tiktok_payload
from ._oauth import OAuthPublisher
from .base import IMAGE_EXTS, MB, Post, PublishResult, Violation, mime_for

API_ROOT = "https://open.tiktokapis.com/v2"

# Video and photos are separate endpoints with separate budgets — the field
# tables for both, and why they differ, live in _tiktok_payload.py.
TITLE_LIMIT = _tiktok_payload.VIDEO_TITLE_LIMIT
CAROUSEL_MAX = 35

# TikTok requires chunks between 5 MB and 64 MB, with the final chunk allowed
# to run up to 128 MB. Anything under the minimum must go as a single chunk.
MIN_CHUNK = 5 * MB
MAX_CHUNK = 64 * MB
CHUNK_SIZE = 20 * MB

STATUS_TIMEOUT = 600.0
STATUS_POLL_INTERVAL = 5.0
MEDIA_URL_TTL = 3600


class TikTokPublisher(OAuthPublisher):
    name = "tiktok"
    requires_env = ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET")
    supports = frozenset({"video", "carousel", "image"})
    supports_draft = True
    needs_public_media_url = False  # video uploads bytes; photos are checked separately
    doc_url = "https://developers.tiktok.com/doc/content-posting-api-get-started"

    max_text_chars = TITLE_LIMIT
    max_hashtags = 10
    min_media = 1
    max_media = CAROUSEL_MAX
    max_video_mb = 4096.0
    max_image_mb = 20.0

    oauth_scopes = ("video.upload", "video.publish")
    scope_delimiter = ","
    default_token_ttl = 86400.0  # TikTok access tokens live 24h
    refresh_url = f"{API_ROOT}/oauth/token/"
    refresh_missing_message = (
        "tiktok: no refresh token stored — re-run cli.auth. TikTok access tokens "
        "last 24h, so this connection cannot be renewed without one."
    )

    # ── plumbing ────────────────────────────────────────────────────────────

    def _post(self, path: str, body: dict[str, Any], *, timeout: float = 120.0) -> dict[str, Any]:
        token = tokens.get_valid(self.name)
        try:
            resp = requests.post(
                f"{API_ROOT}/{path.lstrip('/')}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json; charset=UTF-8",
                },
                data=json.dumps(body),
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise PublishError(self.name, None, f"network error: {exc}") from exc

        try:
            payload = resp.json()
        except ValueError:
            raise PublishError(self.name, resp.status_code, resp.text[:400]) from None

        error = payload.get("error") or {}
        code = error.get("code", "ok")
        if code not in {"ok", "", None}:
            message = error.get("message") or code
            if "rate_limit" in str(code) or resp.status_code == 429:
                raise RateLimitError(self.name, resp.status_code, message)
            raise PublishError(self.name, resp.status_code, f"{code}: {message}")
        if resp.status_code >= 400:
            raise PublishError(self.name, resp.status_code, resp.text[:400])
        return payload.get("data", payload)

    def creator_info(self) -> dict[str, Any]:
        """Mandatory before posting. TikTok requires the app to have fetched the
        creator's current options (privacy levels, whether comments are off,
        max duration) so the UI it shows the user is not stale. Also the
        cheapest way to confirm the token is good before uploading anything."""
        return self._post("post/publish/creator_info/query/", {})

    # ── upload ──────────────────────────────────────────────────────────────

    def _chunk_plan(self, size: int) -> tuple[int, int]:
        """Pick (chunk_size, total_chunk_count) for the init call.

        TikTok validates the declared plan against the real file, and rejects a
        chunk_size larger than video_size. So anything that fits in a single
        chunk must declare chunk_size == video_size — declaring the nominal
        20 MB for a 6 MB file is a rejection, not a rounding detail.

        A lone chunk is also the final chunk, and the final chunk may run to
        128 MB, so everything up to MAX_CHUNK goes in one piece.
        """
        if size <= MAX_CHUNK:
            return size, 1
        chunk = min(max(CHUNK_SIZE, MIN_CHUNK), MAX_CHUNK)
        count = int(size // chunk)
        if count <= 1:
            return size, 1
        return chunk, count

    def _upload(self, upload_url: str, path: Path, chunk: int, count: int) -> None:
        size = path.stat().st_size
        mime = mime_for(path)
        with path.open("rb") as fh:
            for index in range(count):
                start = index * chunk
                # The final chunk absorbs the remainder rather than adding a
                # short chunk TikTok would reject.
                end = size - 1 if index == count - 1 else start + chunk - 1
                fh.seek(start)
                data = fh.read(end - start + 1)
                try:
                    resp = requests.put(
                        upload_url,
                        headers={
                            "Content-Range": f"bytes {start}-{end}/{size}",
                            "Content-Type": mime,
                            "Content-Length": str(len(data)),
                        },
                        data=data,
                        timeout=600,
                    )
                except requests.RequestException as exc:
                    raise PublishError(self.name, None, f"chunk {index + 1}/{count} failed: {exc}") from exc
                if resp.status_code >= 400:
                    raise PublishError(
                        self.name, resp.status_code, f"chunk {index + 1}/{count}: {resp.text[:200]}"
                    )

    def _wait_for(self, publish_id: str) -> dict[str, Any]:
        deadline = time.time() + STATUS_TIMEOUT
        last = "UNKNOWN"
        while time.time() < deadline:
            data = self._post("post/publish/status/fetch/", {"publish_id": publish_id})
            last = str(data.get("status", "UNKNOWN")).upper()
            if last in {"PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"}:
                return data
            if last == "FAILED":
                reason = data.get("fail_reason", "no reason given")
                raise PublishError(self.name, None, f"publish failed: {reason}")
            time.sleep(STATUS_POLL_INTERVAL)
        raise PublishError(
            self.name, None, f"still {last} after {STATUS_TIMEOUT:.0f}s — check the TikTok app"
        )

    # ── publish ─────────────────────────────────────────────────────────────

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        self.ensure_available()
        info = self.creator_info()
        username = info.get("creator_username", "")

        if post.kind in {"image", "carousel"}:
            return self._publish_photos(post, draft=draft, info=info, username=username)
        return self._publish_video(post, draft=draft, info=info, username=username)

    def _publish_video(
        self, post: Post, *, draft: bool, info: dict[str, Any], username: str
    ) -> PublishResult:
        path = post.media[0]
        size = path.stat().st_size
        chunk, count = self._chunk_plan(size)
        source = {
            "source": "FILE_UPLOAD",
            "video_size": size,
            "chunk_size": chunk,
            "total_chunk_count": count,
        }

        if draft:
            data = self._post("post/publish/inbox/video/init/", {"source_info": source})
        else:
            data = self._post(
                "post/publish/video/init/",
                {
                    "post_info": self._post_info(post, info),
                    "source_info": source,
                },
            )

        publish_id = data.get("publish_id", "")
        upload_url = data.get("upload_url")
        if not upload_url:
            raise PublishError(self.name, None, f"init returned no upload_url: {data}")

        self._upload(upload_url, path, chunk, count)
        self._wait_for(publish_id)
        return self._result(publish_id, draft=draft, username=username)

    def _publish_photos(
        self, post: Post, *, draft: bool, info: dict[str, Any], username: str
    ) -> PublishResult:
        from ..storage import s3

        if not s3.s3_configured():
            raise PublishError(
                self.name,
                None,
                "photo posts are accepted only via PULL_FROM_URL — set S3_* in ~/.skills.env, "
                "and verify that domain in the TikTok developer portal",
            )
        urls = []
        for path in post.media:
            key = f"publish/tiktok/{uuid.uuid4().hex[:12]}/{path.name}"
            urls.append(s3.stage_for_fetch(path, key, mime_for(path), ttl=MEDIA_URL_TTL))

        data = self._post(
            "post/publish/content/init/",
            {
                "post_info": self._post_info(post, info),
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "photo_cover_index": 0,
                    "photo_images": urls,
                },
                "post_mode": "MEDIA_UPLOAD" if draft else "DIRECT_POST",
                "media_type": "PHOTO",
            },
        )
        publish_id = data.get("publish_id", "")
        self._wait_for(publish_id)
        return self._result(publish_id, draft=draft, username=username)

    def _post_info(self, post: Post, info: dict[str, Any]) -> dict[str, Any]:
        return _tiktok_payload.post_info(post, info)

    def text_limit_for(self, post: Post) -> int | None:
        return _tiktok_payload.text_limit_for(post)

    def _result(self, publish_id: str, *, draft: bool, username: str) -> PublishResult:
        if draft:
            return PublishResult(
                platform=self.name,
                post_id=publish_id,
                state="draft",
                note="landed in the TikTok app inbox — open the app to caption and publish it",
            )
        permalink = f"https://www.tiktok.com/@{username}" if username else None
        return PublishResult(
            platform=self.name,
            post_id=publish_id,
            state="published",
            permalink=permalink,
            note="if the post is visible only to you, the app is not audited for direct publishing",
        )

    # ── preflight ───────────────────────────────────────────────────────────

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        v: list[Violation] = []

        if not draft:
            # Surfaced on every direct TikTok post, because the failure it
            # describes is silent: the API reports success and the post is
            # invisible. Irrelevant for a draft, which always works.
            v.append(
                Violation(
                    "warn",
                    "audit",
                    "direct publishing requires an audited TikTok app. Unaudited apps have "
                    "every post forced to SELF_ONLY — it looks published and nobody sees it. "
                    "Use --draft to land it in the app inbox instead, which always works.",
                )
            )

        if post.kind in {"image", "carousel"}:
            from ..storage import s3

            if not s3.s3_configured():
                v.append(
                    Violation(
                        "block",
                        "media",
                        "photo posts upload only via PULL_FROM_URL — needs S3_* configured",
                    )
                )
            else:
                v.append(
                    Violation(
                        "warn",
                        "media",
                        "photo posts pull from a URL whose domain must be verified in the "
                        "TikTok developer portal, or the fetch is rejected",
                    )
                )

        if post.kind == "video" and post.media:
            size_mb = post.media[0].stat().st_size / MB if post.media[0].is_file() else 0
            if size_mb > 1024:
                v.append(
                    Violation("warn", "media", f"{size_mb:.0f} MB will take a while to chunk-upload")
                )

        for path in post.media:
            if post.kind == "video" and path.suffix.lower() in IMAGE_EXTS:
                v.append(Violation("block", "media", f"{path.name} is an image in a video post"))

        return v

    # ── authorisation ───────────────────────────────────────────────────────

    def verify_token(self, access_token: str) -> tuple[str, str]:
        try:
            resp = requests.post(
                f"{API_ROOT}/post/publish/creator_info/query/",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=60,
            )
            data = resp.json().get("data", {})
        except (requests.RequestException, ValueError) as exc:
            raise RunnerError(f"tiktok: could not verify token: {exc}") from exc
        username = data.get("creator_username", "")
        return username, (f"@{username}" if username else "")

    def _refresh_payload(self, entry: tokens.TokenEntry) -> dict[str, Any]:
        return {
            "client_key": os.environ.get("TIKTOK_CLIENT_KEY", ""),
            "client_secret": os.environ.get("TIKTOK_CLIENT_SECRET", ""),
            "grant_type": "refresh_token",
            "refresh_token": entry.refresh_token or "",
        }


_PUBLISHER = TikTokPublisher()

oauth.register_app(
    oauth.OAuthApp(
        platform="tiktok",
        authorize_url="https://www.tiktok.com/v2/auth/authorize/",
        token_url=f"{API_ROOT}/oauth/token/",
        scopes=_PUBLISHER.oauth_scopes,
        client_id_env="TIKTOK_CLIENT_KEY",
        client_secret_env="TIKTOK_CLIENT_SECRET",
        use_pkce=True,
        scope_sep=",",
        # TikTok rejects the standard client_id/client_secret parameter names.
        client_id_param="client_key",
        setup_url="https://developers.tiktok.com/doc/content-posting-api-get-started",
    )
)

tokens.register_refresher("tiktok", _PUBLISHER.refresh)

from ..config import register_publisher  # noqa: E402

register_publisher(_PUBLISHER)
