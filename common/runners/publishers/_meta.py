"""Shared machinery for Meta's two own-login publishing APIs.

Threads (graph.threads.net) and Instagram (graph.instagram.com) are separate
products with separate app credentials, but since Meta shipped Instagram Login
they publish through an identical three-step shape:

    1. create a media container         POST /{user-id}/{container_path}
    2. wait for it to finish processing GET  /{container-id}?fields=<status>
    3. publish it                       POST /{user-id}/{publish_path}

They also share the awkward part: neither accepts bytes. You hand them a URL
and they fetch it themselves, which is why S3 staging is mandatory for
anything with media, and why preflight blocks early rather than letting the
upload get halfway.

Step 2 is not optional even for images. Publishing a container that is still
IN_PROGRESS fails with an error that does not say so.

API versions are env-overridable (THREADS_API_VERSION / INSTAGRAM_API_VERSION)
so a version bump does not need a code change — Meta deprecates versions on a
schedule this repo cannot track.
"""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any

import requests

from .. import oauth, tokens
from ..errors import PublishError, RateLimitError, RunnerError, TokenError
from .base import IMAGE_EXTS, Post, Publisher, PublishResult, Violation, mime_for

# How long to wait for Meta to ingest a video before giving up. Reels routinely
# take 30-60s; images are near-instant.
CONTAINER_TIMEOUT = 300.0
CONTAINER_POLL_INTERVAL = 3.0

# Presigned links must outlive Meta's fetch, which happens within seconds but
# retries on their side. An hour is generous and still self-expiring.
MEDIA_URL_TTL = 3600


class MetaPublisher(Publisher):
    """Base for the container → publish flow. Subclasses set the nouns."""

    api_root: str
    api_version_env: str
    default_api_version: str
    container_path: str  # "threads" | "media"
    publish_path: str  # "threads_publish" | "media_publish"
    status_field: str  # "status" | "status_code"
    text_param: str  # "text" | "caption"
    user_id_env: str  # optional override for the account id
    requires_oauth = True
    supports_draft = True
    needs_public_media_url = True

    # ── plumbing ────────────────────────────────────────────────────────────

    def api_version(self) -> str:
        return os.environ.get(self.api_version_env, self.default_api_version)

    def base_url(self) -> str:
        return f"{self.api_root}/{self.api_version()}"

    def user_id(self) -> str:
        """Account id, from the stored token unless explicitly overridden."""
        override = os.environ.get(self.user_id_env)
        if override:
            return override
        entry = tokens.read(self.name)
        if entry is None or not entry.account_id:
            raise TokenError(self.name, "no account id stored")
        return entry.account_id

    def _call(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        token: str | None = None,
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        url = path if path.startswith("http") else f"{self.base_url()}/{path.lstrip('/')}"
        payload = dict(params or {})
        payload["access_token"] = token or tokens.get_valid(self.name)

        try:
            if method == "GET":
                resp = requests.get(url, params=payload, timeout=timeout)
            else:
                resp = requests.post(url, data=payload, timeout=timeout)
        except requests.RequestException as exc:
            raise PublishError(self.name, None, f"network error: {exc}") from exc

        try:
            data = resp.json()
        except ValueError:
            raise PublishError(self.name, resp.status_code, resp.text[:400]) from None

        self._raise_for(resp, data)
        return data

    # Meta's throttling family. 9 is publishing-limit-reached, which is a cap
    # rather than a bug and deserves the same "wait" framing as a 429.
    THROTTLE_CODES = frozenset({4, 9, 17, 32, 613})

    def _raise_for(self, resp: requests.Response, data: dict[str, Any]) -> None:
        """Meta reports failure inside a 200 body as often as through a status
        code, so both paths converge here rather than being checked twice."""
        error = data.get("error")
        if error:
            message = error.get("error_user_msg") or error.get("message") or str(error)
            if error.get("code") in self.THROTTLE_CODES or resp.status_code == 429:
                raise RateLimitError(self.name, resp.status_code, message)
            raise PublishError(self.name, resp.status_code, message)
        if resp.status_code >= 400:
            raise PublishError(self.name, resp.status_code, resp.text[:400])

    # ── media staging ───────────────────────────────────────────────────────

    def _stage(self, path: Path) -> str:
        from ..storage import s3

        if not s3.s3_configured():
            raise PublishError(
                self.name,
                None,
                "media staging needs S3 (S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY) — "
                f"{self.name} fetches media by URL and cannot take raw bytes",
            )
        key = f"publish/{self.name}/{uuid.uuid4().hex[:12]}/{path.name}"
        return s3.stage_for_fetch(path, key, mime_for(path), ttl=MEDIA_URL_TTL)

    # ── container lifecycle ─────────────────────────────────────────────────

    def _media_params(self, path: Path, url: str) -> dict[str, Any]:
        """Subclass hook: how this platform names an image vs a video."""
        raise NotImplementedError

    def _create_container(self, params: dict[str, Any]) -> str:
        data = self._call("POST", f"{self.user_id()}/{self.container_path}", params=params)
        container_id = data.get("id")
        if not container_id:
            raise PublishError(self.name, None, f"container creation returned no id: {data}")
        return str(container_id)

    def _wait_for(self, container_id: str) -> None:
        """Poll until the container is ready. Skipping this is the single most
        common way a Reels publish fails with an unhelpful error."""
        deadline = time.time() + CONTAINER_TIMEOUT
        last = "UNKNOWN"
        # Threads reports progress in `status`, Instagram in `status_code`, and
        # asking for both keeps one code path. dict.fromkeys dedupes so Threads
        # does not request "status,status".
        fields = ",".join(dict.fromkeys([self.status_field, "status"]))
        while time.time() < deadline:
            data = self._call("GET", container_id, params={"fields": fields})
            last = str(data.get(self.status_field) or data.get("status") or "UNKNOWN").upper()
            if last in {"FINISHED", "PUBLISHED"}:
                return
            if last in {"ERROR", "EXPIRED"}:
                detail = data.get("status") or data.get("error_message") or ""
                raise PublishError(self.name, None, f"container {container_id} is {last}. {detail}")
            time.sleep(CONTAINER_POLL_INTERVAL)
        raise PublishError(
            self.name,
            None,
            f"container {container_id} still {last} after {CONTAINER_TIMEOUT:.0f}s — "
            f"Meta may still finish it; check the account before retrying",
        )

    def publish_container(self, container_id: str) -> PublishResult:
        """Publish a container created earlier by a --draft run."""
        data = self._call(
            "POST", f"{self.user_id()}/{self.publish_path}", params={"creation_id": container_id}
        )
        media_id = str(data.get("id", ""))
        return PublishResult(
            platform=self.name,
            post_id=media_id,
            state="published",
            permalink=self._permalink(media_id),
        )

    def _permalink(self, media_id: str) -> str | None:
        if not media_id:
            return None
        try:
            return self._call("GET", media_id, params={"fields": "permalink"}).get("permalink")
        except RunnerError:
            # A missing permalink is cosmetic — the post is already live, and
            # failing here would wrongly report the publish as failed.
            return None

    # ── publish ─────────────────────────────────────────────────────────────

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        self.ensure_available()
        text = post.rendered_text()

        if post.kind == "carousel":
            children = []
            for path in post.media:
                url = self._stage(path)
                params = self._media_params(path, url)
                params["is_carousel_item"] = "true"
                child = self._create_container(params)
                self._wait_for(child)
                children.append(child)
            container_id = self._create_container(
                {"media_type": "CAROUSEL", "children": ",".join(children), self.text_param: text}
            )
        elif post.media:
            params = self._media_params(post.media[0], self._stage(post.media[0]))
            params[self.text_param] = text
            container_id = self._create_container(params)
        else:
            container_id = self._create_container({"media_type": "TEXT", self.text_param: text})

        self._wait_for(container_id)

        if draft:
            return PublishResult(
                platform=self.name,
                post_id=container_id,
                state="draft",
                note=(
                    f"container staged and processed, NOT posted. It expires in 24h. "
                    f"Publish it with: --platform {self.name} --publish-container {container_id}"
                ),
                extra={"container_id": container_id},
            )

        return self.publish_container(container_id)

    # ── authorisation ───────────────────────────────────────────────────────

    def oauth_app(self):
        return oauth.get_app(self.name)

    def verify_token(self, access_token: str) -> tuple[str, str]:
        data = self._call("GET", "me", params={"fields": "id,username"}, token=access_token)
        username = data.get("username", "")
        return str(data.get("id", "")), (f"@{username}" if username else "")

    def finalize_auth(self, raw: dict[str, Any]):
        short_lived = raw.get("access_token")
        if not short_lived:
            raise RunnerError(f"{self.name}: token response had no access_token")
        long_lived, expires_in = self._exchange_long_lived(short_lived)
        account_id, label = self.verify_token(long_lived)
        return tokens.TokenEntry(
            platform=self.name,
            access_token=long_lived,
            expires_at=time.time() + expires_in if expires_in else None,
            scopes=list(self.oauth_scopes),
            account_id=account_id or str(raw.get("user_id", "")),
            account_label=label,
        )

    # Subclasses supply these — the exchange/refresh endpoints differ per product.
    oauth_scopes: tuple[str, ...] = ()
    exchange_url: str = ""
    exchange_grant: str = ""
    refresh_url: str = ""
    refresh_grant: str = ""

    def _exchange_long_lived(self, short_lived: str) -> tuple[str, float]:
        """Trade the ~1h code-exchange token for the ~60-day one."""
        resp = requests.get(
            self.exchange_url,
            params={
                "grant_type": self.exchange_grant,
                "client_secret": os.environ.get(self.secret_env, ""),
                "access_token": short_lived,
            },
            timeout=60,
        )
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400 or "access_token" not in data:
            raise RunnerError(f"{self.name}: long-lived token exchange failed: {resp.text[:300]}")
        return data["access_token"], float(data.get("expires_in", 0))

    def refresh(self, entry: tokens.TokenEntry) -> tokens.TokenEntry:
        """Meta long-lived tokens renew using themselves — no refresh token."""
        resp = requests.get(
            self.refresh_url,
            params={"grant_type": self.refresh_grant, "access_token": entry.access_token},
            timeout=60,
        )
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400 or "access_token" not in data:
            raise RunnerError(
                f"{self.name}: refresh failed ({resp.text[:200]}). "
                f"A token unused for 60 days cannot be refreshed — re-run cli.auth."
            )
        entry.access_token = data["access_token"]
        entry.expires_at = time.time() + float(data.get("expires_in", 0))
        return entry

    secret_env: str = ""

    # ── preflight ───────────────────────────────────────────────────────────

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        v: list[Violation] = []
        if post.kind == "carousel" and len(post.media) < 2:
            v.append(Violation("block", "media", "a carousel needs at least 2 items"))
        for path in post.media:
            if path.suffix.lower() not in IMAGE_EXTS and post.kind == "carousel":
                v.append(
                    Violation(
                        "warn",
                        "media",
                        f"{path.name} is video in a carousel — supported, but it ingests "
                        f"slowly and fails more often than an all-image deck",
                    )
                )
        return v
