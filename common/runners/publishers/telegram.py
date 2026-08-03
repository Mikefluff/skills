"""Telegram channel publishing via the Bot API.

Reference implementation for this layer, and the only platform of the seven
that can be verified end-to-end without an OAuth dance, a business account, or
an app review: create a bot with @BotFather, add it to a channel as admin,
done. Smoke tests target this module.

Bot API quirks worth knowing before reading the code:
  - A caption attached to media is capped at 1024 chars, but a plain text
    message gets 4096. Same "text" field to the user, two different limits.
  - Albums go through sendMediaGroup, where the files ride as multipart parts
    and the `media` array references them by `attach://<name>`.
  - Only the FIRST item of an album may carry a caption; a caption on later
    items is silently dropped.
  - Uploads are capped at 50 MB by the public Bot API (self-hosted Bot API
    servers lift this, which is why the error message says so).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

from ..errors import PublishError, RateLimitError
from .base import IMAGE_EXTS, VIDEO_EXTS, Post, Publisher, PublishResult, Violation, mime_for

API_ROOT = "https://api.telegram.org"

CAPTION_LIMIT = 1024
MESSAGE_LIMIT = 4096

# Verified 2026-08-03 against core.telegram.org/bots/faq — bots may upload files
# up to 50 MB through the public Bot API. sendPhoto documents a tighter 10 MB
# ceiling of its own, so photos are held to that rather than to the general cap.
UPLOAD_LIMIT_MB = 50.0
PHOTO_LIMIT_MB = 10.0


class TelegramPublisher(Publisher):
    name = "telegram"
    requires_env = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    requires_oauth = False
    supports = frozenset({"text", "image", "carousel", "video"})
    supports_draft = False
    needs_public_media_url = False
    doc_url = "https://core.telegram.org/bots/api"

    max_text_chars = MESSAGE_LIMIT
    max_hashtags = 10
    min_media = 0
    max_media = 10
    max_image_mb = PHOTO_LIMIT_MB
    max_video_mb = UPLOAD_LIMIT_MB

    # ── preflight ───────────────────────────────────────────────────────────

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        v: list[Violation] = []
        text = post.rendered_text()

        if post.media and len(text) > CAPTION_LIMIT:
            v.append(
                Violation(
                    "block",
                    "text",
                    f"{len(text)} chars: a caption on media is capped at {CAPTION_LIMIT} "
                    f"(a text-only post would allow {MESSAGE_LIMIT}). "
                    f"Shorten it, or post the text separately.",
                )
            )

        if post.kind == "carousel":
            if len(post.media) < 2:
                v.append(Violation("block", "media", "an album needs at least 2 files"))
            kinds = {"image" if m.suffix.lower() in IMAGE_EXTS else "video" for m in post.media}
            if len(kinds) > 1:
                v.append(
                    Violation(
                        "warn",
                        "media",
                        "album mixes images and video — Telegram allows it but the "
                        "layout is unpredictable across clients",
                    )
                )

        if post.kind == "text" and not post.text.strip():
            v.append(Violation("block", "text", "a text post needs text"))

        return v

    # ── publish ─────────────────────────────────────────────────────────────

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        if draft:
            # Checked before credentials on purpose: this request is impossible
            # regardless of how well the bot is configured, so "set your token"
            # would be a misleading thing to say. The CLI screens on
            # supports_draft first; reaching here means a caller bypassed it.
            raise PublishError(
                self.name, None, "Telegram has no draft concept — post it or don't"
            )

        self.ensure_available()
        chat_id = os.environ["TELEGRAM_CHAT_ID"]
        text = post.rendered_text()

        if post.kind == "text":
            result = self._call("sendMessage", data={"chat_id": chat_id, "text": text})
        elif post.kind == "carousel":
            result = self._send_album(chat_id, post, text)
        elif post.kind == "video":
            result = self._send_single("sendVideo", "video", chat_id, post.media[0], text)
        else:
            result = self._send_single("sendPhoto", "photo", chat_id, post.media[0], text)

        return self._to_result(result)

    # ── HTTP ────────────────────────────────────────────────────────────────

    def _url(self, method: str) -> str:
        return f"{API_ROOT}/bot{os.environ['TELEGRAM_BOT_TOKEN']}/{method}"

    def _call(
        self,
        method: str,
        *,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        timeout: float = 180.0,
    ) -> dict[str, Any]:
        try:
            resp = requests.post(self._url(method), data=data, files=files, timeout=timeout)
        except requests.RequestException as exc:
            raise PublishError(self.name, None, f"network error: {exc}") from exc

        try:
            payload = resp.json()
        except ValueError:
            raise PublishError(self.name, resp.status_code, resp.text[:500]) from None

        if not payload.get("ok"):
            desc = payload.get("description", resp.text[:500])
            code = payload.get("error_code", resp.status_code)
            if code == 429:
                retry = payload.get("parameters", {}).get("retry_after")
                suffix = f" — retry after {retry}s" if retry else ""
                raise RateLimitError(self.name, code, f"{desc}{suffix}")
            raise PublishError(self.name, code, desc)

        return payload["result"]

    def _send_single(
        self, method: str, field: str, chat_id: str, path: Path, caption: str
    ) -> dict[str, Any]:
        with path.open("rb") as fh:
            return self._call(
                method,
                data={"chat_id": chat_id, "caption": caption},
                files={field: (path.name, fh, mime_for(path))},
            )

    def _send_album(self, chat_id: str, post: Post, caption: str) -> dict[str, Any]:
        media_spec: list[dict[str, Any]] = []
        files: dict[str, Any] = {}
        handles = []

        try:
            for i, path in enumerate(post.media):
                key = f"file{i}"
                fh = path.open("rb")
                handles.append(fh)
                files[key] = (path.name, fh, mime_for(path))
                item: dict[str, Any] = {
                    "type": "video" if path.suffix.lower() in VIDEO_EXTS else "photo",
                    "media": f"attach://{key}",
                }
                if i == 0 and caption:
                    item["caption"] = caption
                media_spec.append(item)

            result = self._call(
                "sendMediaGroup",
                data={"chat_id": chat_id, "media": json.dumps(media_spec)},
                files=files,
            )
        finally:
            for fh in handles:
                fh.close()

        # sendMediaGroup returns a list of messages; the first anchors the album.
        return result[0] if isinstance(result, list) and result else {}

    def _to_result(self, result: dict[str, Any]) -> PublishResult:
        message_id = str(result.get("message_id", ""))
        chat = result.get("chat", {})
        username = chat.get("username")
        permalink = f"https://t.me/{username}/{message_id}" if username and message_id else None
        note = "" if permalink else "private chat/channel — no public permalink"
        return PublishResult(
            platform=self.name,
            post_id=message_id,
            state="published",
            permalink=permalink,
            note=note,
            extra={"chat_id": chat.get("id")},
        )


from ..config import register_publisher  # noqa: E402

register_publisher(TelegramPublisher())
