"""X (Twitter) publishing via API v2.

The distinguishing feature here is the thread. X is the only platform in this
set where the natural unit is a chain rather than a post, so `Post.thread`
gets used: the first item is the root, each subsequent one replies to the id
returned by the previous call. That also means a thread cannot be rolled back
halfway — if post 4 of 6 fails, posts 1-3 are already public. The result
records how far it got instead of pretending the whole thing failed.

Rate limiting is a real constraint rather than a footnote. The documented
ceilings on POST /2/tweets are 10,000 per 24h per app and 100 per 15 minutes
per user (verified 2026-08-03 against docs.x.com/x-api/fundamentals/rate-limits).
What an account may actually spend on top of that depends on the plan, and X
has moved to pay-per-usage pricing — check current pricing before budgeting a
posting cadence around this. An earlier draft of this file asserted a "17 posts
per 24h free tier" from memory; it was not in the docs and is not repeated here.

Media upload runs through POST /2/media/upload with INIT/APPEND/FINALIZE/STATUS
and a Bearer user token — not the legacy upload.twitter.com host. That endpoint
has moved before, so it stays env-overridable via X_UPLOAD_URL.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import requests

from .. import oauth, tokens
from ..errors import PublishError, RateLimitError, RunnerError
from ._oauth import OAuthPublisher
from .base import MB, IMAGE_EXTS, Post, PublishResult, Violation, mime_for

API_ROOT = "https://api.x.com/2"
DEFAULT_UPLOAD_URL = f"{API_ROOT}/media/upload"

TEXT_LIMIT = 280
CHUNK_SIZE = 4 * MB
PROCESSING_TIMEOUT = 180.0


class XPublisher(OAuthPublisher):
    name = "x"
    requires_env = ("X_CLIENT_ID", "X_CLIENT_SECRET")
    supports = frozenset({"text", "image", "carousel", "video"})
    supports_draft = False
    needs_public_media_url = False
    doc_url = "https://docs.x.com/x-api/posts/creation-of-a-post"

    max_text_chars = TEXT_LIMIT
    max_hashtags = 3  # more than this on X reads as spam and suppresses reach
    min_media = 0
    max_media = 4  # X allows at most 4 images, or 1 video, per post
    max_image_mb = 5.0
    max_video_mb = 512.0

    oauth_scopes = ("tweet.read", "tweet.write", "users.read", "offline.access")
    default_token_ttl = 7200.0
    refresh_url = f"{API_ROOT}/oauth2/token"
    refresh_missing_message = (
        "x: no refresh token stored — the app was authorised without the "
        "offline.access scope. Re-run cli.auth after adding it."
    )

    def upload_url(self) -> str:
        return os.environ.get("X_UPLOAD_URL", DEFAULT_UPLOAD_URL)

    # ── plumbing ────────────────────────────────────────────────────────────

    def _headers(self, token: str | None = None) -> dict[str, str]:
        return {"Authorization": f"Bearer {token or tokens.get_valid(self.name)}"}

    def _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        kwargs.setdefault("timeout", 120)
        headers = kwargs.pop("headers", {})
        headers.update(self._headers(kwargs.pop("token", None)))
        try:
            resp = requests.request(method, url, headers=headers, **kwargs)
        except requests.RequestException as exc:
            raise PublishError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            reset = resp.headers.get("x-rate-limit-reset", "")
            hint = f" (limit resets at epoch {reset})" if reset else ""
            raise RateLimitError(self.name, 429, f"rate limited{hint}")

        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            raise PublishError(self.name, resp.status_code, resp.text[:400]) from None

        if resp.status_code >= 400:
            detail = data.get("detail") or data.get("title") or resp.text[:300]
            raise PublishError(self.name, resp.status_code, detail)
        return data

    # ── media ───────────────────────────────────────────────────────────────

    def _upload_media(self, path: Path) -> str:
        size = path.stat().st_size
        is_video = path.suffix.lower() not in IMAGE_EXTS
        category = "tweet_video" if is_video else "tweet_image"

        init = self._request(
            "POST",
            self.upload_url(),
            data={
                "command": "INIT",
                "total_bytes": size,
                "media_type": mime_for(path),
                "media_category": category,
            },
        )
        media_id = str((init.get("data") or init).get("id") or (init.get("data") or init).get("media_id"))
        if not media_id or media_id == "None":
            raise PublishError(self.name, None, f"media INIT returned no id: {init}")

        with path.open("rb") as fh:
            index = 0
            while True:
                chunk = fh.read(CHUNK_SIZE)
                if not chunk:
                    break
                self._request(
                    "POST",
                    self.upload_url(),
                    data={"command": "APPEND", "media_id": media_id, "segment_index": index},
                    files={"media": (path.name, chunk, mime_for(path))},
                )
                index += 1

        finalize = self._request(
            "POST", self.upload_url(), data={"command": "FINALIZE", "media_id": media_id}
        )
        self._await_processing(media_id, finalize)
        return media_id

    def _await_processing(self, media_id: str, finalize: dict[str, Any]) -> None:
        """Video needs server-side transcoding. Posting before it finishes
        fails with an error that does not mention processing."""
        info = (finalize.get("data") or finalize).get("processing_info")
        deadline = time.time() + PROCESSING_TIMEOUT
        while info and time.time() < deadline:
            state = info.get("state")
            if state == "succeeded":
                return
            if state == "failed":
                raise PublishError(self.name, None, f"media processing failed: {info.get('error')}")
            time.sleep(max(1, int(info.get("check_after_secs", 5))))
            status = self._request(
                "GET", self.upload_url(), params={"command": "STATUS", "media_id": media_id}
            )
            info = (status.get("data") or status).get("processing_info")

    # ── publish ─────────────────────────────────────────────────────────────

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        if draft:
            raise PublishError(self.name, None, "X has no draft API — post it or don't")
        self.ensure_available()

        media_ids = [self._upload_media(p) for p in post.media]

        body: dict[str, Any] = {"text": post.rendered_text()}
        if media_ids:
            body["media"] = {"media_ids": media_ids}

        root = self._request("POST", f"{API_ROOT}/tweets", json=body)
        root_id = str((root.get("data") or {}).get("id", ""))

        posted = 1
        parent = root_id
        try:
            for follow_up in post.thread:
                data = self._request(
                    "POST",
                    f"{API_ROOT}/tweets",
                    json={"text": follow_up, "reply": {"in_reply_to_tweet_id": parent}},
                )
                parent = str((data.get("data") or {}).get("id", ""))
                posted += 1
        except (PublishError, RunnerError) as exc:
            # The root is already public. Reporting a clean failure would be a
            # lie and would make --force the only way forward.
            total = len(post.thread) + 1
            return PublishResult(
                platform=self.name,
                post_id=root_id,
                state="published",
                permalink=self._permalink(root_id),
                note=f"PARTIAL: {posted}/{total} posts published, then failed — {exc}",
            )

        note = f"thread of {posted} posts" if posted > 1 else ""
        return PublishResult(
            platform=self.name,
            post_id=root_id,
            state="published",
            permalink=self._permalink(root_id),
            note=note,
        )

    def _permalink(self, post_id: str) -> str | None:
        if not post_id:
            return None
        entry = tokens.read(self.name)
        handle = (entry.account_label if entry else "").lstrip("@") or "i"
        return f"https://x.com/{handle}/status/{post_id}"

    # ── preflight ───────────────────────────────────────────────────────────

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        v: list[Violation] = []

        videos = [p for p in post.media if p.suffix.lower() not in IMAGE_EXTS]
        if videos and len(post.media) > 1:
            v.append(Violation("block", "media", "X takes either one video or up to four images"))

        for i, part in enumerate(post.thread, start=2):
            if len(part) > TEXT_LIMIT:
                v.append(
                    Violation("block", "thread", f"post {i} of the thread is {len(part)} chars (max {TEXT_LIMIT})")
                )
            if not part.strip():
                v.append(Violation("block", "thread", f"post {i} of the thread is empty"))

        if post.kind == "text" and not post.text.strip():
            v.append(Violation("block", "text", "a text post needs text"))

        return v

    # ── authorisation ───────────────────────────────────────────────────────

    def verify_token(self, access_token: str) -> tuple[str, str]:
        data = self._request("GET", f"{API_ROOT}/users/me", token=access_token).get("data", {})
        username = data.get("username", "")
        return str(data.get("id", "")), (f"@{username}" if username else "")

    def _refresh_payload(self, entry: tokens.TokenEntry) -> dict[str, Any]:
        return {
            "grant_type": "refresh_token",
            "refresh_token": entry.refresh_token or "",
            "client_id": os.environ.get("X_CLIENT_ID", ""),
        }

    def _post_form(self, url: str, payload: dict[str, Any], **kwargs) -> dict[str, Any]:
        # X wants the client credentials as HTTP Basic on the token endpoint.
        return super()._post_form(
            url,
            payload,
            auth=(os.environ.get("X_CLIENT_ID", ""), os.environ.get("X_CLIENT_SECRET", "")),
            **kwargs,
        )


_PUBLISHER = XPublisher()

oauth.register_app(
    oauth.OAuthApp(
        platform="x",
        authorize_url="https://x.com/i/oauth2/authorize",
        token_url="https://api.x.com/2/oauth2/token",
        scopes=_PUBLISHER.oauth_scopes,
        client_id_env="X_CLIENT_ID",
        client_secret_env="X_CLIENT_SECRET",
        use_pkce=True,  # X requires PKCE for OAuth 2.0 user-context tokens
        setup_url="https://developer.x.com/en/portal/dashboard",
    )
)

tokens.register_refresher("x", _PUBLISHER.refresh)

from ..config import register_publisher  # noqa: E402

register_publisher(_PUBLISHER)
