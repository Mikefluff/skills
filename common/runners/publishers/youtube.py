"""YouTube publishing via the Data API v3 resumable upload.

The cleanest draft story of the seven: `privacyStatus: private` produces a real
video on the real channel that only the owner can see, editable and publishable
from YouTube Studio. So --draft here means something a user can actually act on,
unlike the 24h staging containers Meta calls drafts.

The constraint that surprises people is quota, not file size. A single
videos.insert costs 1600 units against a default daily allowance of 10,000 —
six uploads a day, and that is shared with every other call the project makes.
Preflight cannot read the remaining quota (there is no endpoint for it), so it
says so rather than implying a check happened.

Shorts are not a separate API: a vertical video under about three minutes is
classified as a Short by YouTube itself.
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
from .base import MB, IMAGE_EXTS, Post, Publisher, PublishResult, Violation, mime_for

API_ROOT = "https://www.googleapis.com/youtube/v3"
UPLOAD_ROOT = "https://www.googleapis.com/upload/youtube/v3"

TITLE_LIMIT = 100
DESCRIPTION_LIMIT = 5000
TAGS_TOTAL_LIMIT = 500  # characters across all tags
QUOTA_PER_UPLOAD = 1600
DEFAULT_DAILY_QUOTA = 10_000
UPLOAD_CHUNK = 8 * MB


class YouTubePublisher(Publisher):
    name = "youtube"
    requires_env = ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET")
    requires_oauth = True
    supports = frozenset({"video"})
    supports_draft = True
    needs_public_media_url = False
    doc_url = "https://developers.google.com/youtube/v3/docs/videos/insert"

    max_text_chars = DESCRIPTION_LIMIT
    max_title_chars = TITLE_LIMIT
    max_hashtags = 15  # YouTube only renders the first three above the title
    min_media = 1
    max_media = 1
    max_video_mb = 256_000.0

    oauth_scopes = ("https://www.googleapis.com/auth/youtube.upload",)

    # ── plumbing ────────────────────────────────────────────────────────────

    def _headers(self, token: str | None = None) -> dict[str, str]:
        return {"Authorization": f"Bearer {token or tokens.get_valid(self.name)}"}

    def _raise_for(self, resp: requests.Response) -> None:
        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            raise PublishError(self.name, resp.status_code, resp.text[:400]) from None
        error = data.get("error", {})
        message = error.get("message", resp.text[:300])
        reasons = {e.get("reason", "") for e in error.get("errors", [])}
        if "quotaExceeded" in reasons or resp.status_code == 429:
            raise RateLimitError(
                self.name,
                resp.status_code,
                f"{message} — videos.insert costs {QUOTA_PER_UPLOAD} units of the "
                f"{DEFAULT_DAILY_QUOTA}/day default allowance",
            )
        raise PublishError(self.name, resp.status_code, message)

    # ── publish ─────────────────────────────────────────────────────────────

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        self.ensure_available()
        path = post.media[0]
        size = path.stat().st_size

        metadata = {
            "snippet": {
                "title": self._derive_title(post),
                "description": post.rendered_text()[:DESCRIPTION_LIMIT],
                "tags": list(post.hashtags),
                "categoryId": os.environ.get("YOUTUBE_CATEGORY_ID", "22"),  # People & Blogs
            },
            "status": {
                "privacyStatus": "private" if draft else os.environ.get("YOUTUBE_PRIVACY", "public"),
                "selfDeclaredMadeForKids": False,
            },
        }

        session_url = self._start_session(metadata, size, mime_for(path))
        video_id = self._upload(session_url, path, size)

        return PublishResult(
            platform=self.name,
            post_id=video_id,
            state="draft" if draft else "published",
            permalink=f"https://youtu.be/{video_id}" if video_id else None,
            note=(
                "uploaded as private — publish it from YouTube Studio when ready"
                if draft
                else f"{QUOTA_PER_UPLOAD} quota units spent"
            ),
        )

    def _derive_title(self, post: Post) -> str:
        """An explicit --title always wins; otherwise fall back to the first
        non-blank line of the caption. Written out rather than chained with
        `or`, because the inline version bound as
        `(title or first_line) if text else "Untitled"` and threw away an
        explicit title whenever the caption happened to be empty."""
        if post.title.strip():
            return post.title.strip()[:TITLE_LIMIT]
        for line in post.text.splitlines():
            if line.strip():
                return line.strip()[:TITLE_LIMIT]
        return "Untitled"

    def _start_session(self, metadata: dict[str, Any], size: int, mime: str) -> str:
        headers = self._headers()
        headers.update(
            {
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Length": str(size),
                "X-Upload-Content-Type": mime,
            }
        )
        try:
            resp = requests.post(
                f"{UPLOAD_ROOT}/videos",
                params={"uploadType": "resumable", "part": "snippet,status"},
                headers=headers,
                data=json.dumps(metadata),
                timeout=120,
            )
        except requests.RequestException as exc:
            raise PublishError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code >= 400:
            self._raise_for(resp)
        session_url = resp.headers.get("Location")
        if not session_url:
            raise PublishError(self.name, None, "resumable session returned no Location header")
        return session_url

    def _upload(self, session_url: str, path: Path, size: int) -> str:
        """Push the bytes in chunks. 308 means 'keep going' and is not an error."""
        sent = 0
        with path.open("rb") as fh:
            while sent < size:
                chunk = fh.read(UPLOAD_CHUNK)
                if not chunk:
                    break
                end = sent + len(chunk) - 1
                try:
                    resp = requests.put(
                        session_url,
                        headers={
                            "Content-Length": str(len(chunk)),
                            "Content-Range": f"bytes {sent}-{end}/{size}",
                        },
                        data=chunk,
                        timeout=600,
                    )
                except requests.RequestException as exc:
                    raise PublishError(
                        self.name, None, f"upload failed at byte {sent}/{size}: {exc}"
                    ) from exc

                if resp.status_code in {200, 201}:
                    try:
                        return str(resp.json().get("id", ""))
                    except ValueError:
                        return ""
                if resp.status_code == 308:
                    sent = end + 1
                    continue
                self._raise_for(resp)
        raise PublishError(self.name, None, "upload finished without YouTube returning a video id")

    # ── preflight ───────────────────────────────────────────────────────────

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        v: list[Violation] = []

        if post.media and post.media[0].suffix.lower() in IMAGE_EXTS:
            v.append(Violation("block", "media", "YouTube takes video, not stills"))

        if not post.title:
            v.append(
                Violation(
                    "warn",
                    "title",
                    "no --title given; the first line of the caption will be used, which is "
                    "rarely a good YouTube title",
                )
            )

        tag_chars = sum(len(h) for h in post.hashtags)
        if tag_chars > TAGS_TOTAL_LIMIT:
            v.append(Violation("block", "hashtags", f"tags total {tag_chars} chars (max {TAGS_TOTAL_LIMIT})"))

        # Warned on drafts too: a private upload costs exactly the same 1600
        # units as a public one. Suppressing it there would teach people that
        # --draft is free, which is the opposite of true.
        v.append(
            Violation(
                "warn",
                "quota",
                f"this upload costs {QUOTA_PER_UPLOAD} of the {DEFAULT_DAILY_QUOTA}/day default "
                f"quota (~6 uploads/day, private ones included). There is no API to check "
                f"what is left.",
            )
        )

        return v

    # ── authorisation ───────────────────────────────────────────────────────

    def oauth_app(self):
        return oauth.get_app(self.name)

    def verify_token(self, access_token: str) -> tuple[str, str]:
        try:
            resp = requests.get(
                f"{API_ROOT}/channels",
                params={"part": "snippet", "mine": "true"},
                headers=self._headers(access_token),
                timeout=60,
            )
            items = resp.json().get("items", []) if resp.content else []
        except (requests.RequestException, ValueError) as exc:
            raise RunnerError(f"youtube: could not verify token: {exc}") from exc
        if resp.status_code >= 400:
            raise RunnerError(f"youtube: token rejected: {resp.text[:200]}")
        if not items:
            # The upload scope alone cannot read channels; not fatal.
            return "", ""
        return items[0].get("id", ""), items[0].get("snippet", {}).get("title", "")

    def finalize_auth(self, raw: dict[str, Any]):
        access = raw.get("access_token")
        if not access:
            raise RunnerError(f"youtube: token response had no access_token: {raw}")
        if not raw.get("refresh_token"):
            raise RunnerError(
                "youtube: Google returned no refresh_token. Revoke the app's access at "
                "myaccount.google.com/permissions and authorise again — Google only issues "
                "one on first consent."
            )
        account_id = label = ""
        try:
            account_id, label = self.verify_token(access)
        except RunnerError:
            pass
        return tokens.TokenEntry(
            platform=self.name,
            access_token=access,
            refresh_token=raw.get("refresh_token"),
            expires_at=time.time() + float(raw.get("expires_in", 3600)),
            scopes=list(self.oauth_scopes),
            account_id=account_id,
            account_label=label,
        )

    def refresh(self, entry: tokens.TokenEntry) -> tokens.TokenEntry:
        if not entry.refresh_token:
            raise RunnerError(
                "youtube: no refresh token stored. Google issues one only on first "
                "consent — revoke at myaccount.google.com/permissions and re-run cli.auth."
            )
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": entry.refresh_token or "",
                "client_id": os.environ.get("YOUTUBE_CLIENT_ID", ""),
                "client_secret": os.environ.get("YOUTUBE_CLIENT_SECRET", ""),
            },
            timeout=60,
        )
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400 or "access_token" not in data:
            raise RunnerError(f"youtube: refresh failed: {resp.text[:200]}")
        entry.access_token = data["access_token"]
        entry.expires_at = time.time() + float(data.get("expires_in", 3600))
        return entry


_PUBLISHER = YouTubePublisher()

oauth.register_app(
    oauth.OAuthApp(
        platform="youtube",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        scopes=_PUBLISHER.oauth_scopes,
        client_id_env="YOUTUBE_CLIENT_ID",
        client_secret_env="YOUTUBE_CLIENT_SECRET",
        # Google issues a refresh token only with these two, and only on the
        # first consent — without them the token dies in an hour, permanently.
        extra_authorize_params={"access_type": "offline", "prompt": "consent"},
        setup_url="https://console.cloud.google.com/apis/credentials",
    )
)

tokens.register_refresher("youtube", _PUBLISHER.refresh)

from ..config import register_publisher  # noqa: E402

register_publisher(_PUBLISHER)
