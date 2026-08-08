"""Tumblr publishing via API v2 and the Neue Post Format.

General audience rather than a technical one, and no canonical field, so the
link home goes into the body. Worth having for reach; not for ranking signal.

Auth is a plain OAuth2 bearer token rather than the collection's OAuth flow —
Tumblr issues one from its own app console, which is fewer moving parts than
registering a redirect URI for a platform posted to occasionally.

Neue Post Format notes:
  - The body is a list of content blocks, not a string. A markdown article is
    one text block with `subtype: "markdown"`.
  - `state` takes published / draft / queue / private, so --draft is honest.
  - The blog identifier is the hostname, e.g. `myblog.tumblr.com`.
"""

from __future__ import annotations

import os
from typing import Any

from ..errors import PublishError
from ._json_api import post_json
from .base import Post, Publisher, PublishResult, Violation

API_ROOT = "https://api.tumblr.com/v2"

# Verified 2026-08-05 against tumblr.com/docs/en/api/v2.
MAX_TITLE = 300
MAX_TAGS = 30


class TumblrPublisher(Publisher):
    name = "tumblr"
    requires_env = ("TUMBLR_ACCESS_TOKEN", "TUMBLR_BLOG_ID")
    requires_oauth = False
    supports = frozenset({"article"})
    supports_draft = True
    doc_url = "https://www.tumblr.com/docs/en/api/v2"

    max_title_chars = MAX_TITLE
    max_hashtags = MAX_TAGS
    min_media = 0
    max_media = 0

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        out: list[Violation] = []
        if post.canonical_url:
            out.append(
                Violation(
                    "warn",
                    "canonical_url",
                    "Tumblr has no canonical field — the original is linked in the body "
                    "instead, so this post cannot pass ranking signal home",
                )
            )
        blog = os.environ.get("TUMBLR_BLOG_ID", "")
        if blog and "/" in blog:
            out.append(
                Violation(
                    "block",
                    "TUMBLR_BLOG_ID",
                    f"expected a blog hostname like 'myblog.tumblr.com', got '{blog}'",
                )
            )
        return out

    def _content_blocks(self, post: Post) -> list[dict[str, Any]]:
        body = post.text.strip()
        if post.canonical_url:
            body = f"{body}\n\n---\n\nOriginally published at {post.canonical_url}"
        return [{"type": "text", "text": body, "subtype": "markdown"}]

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        self.ensure_available()
        blog = os.environ["TUMBLR_BLOG_ID"]

        body: dict[str, Any] = {
            "content": self._content_blocks(post),
            "layout": [],
            "state": "draft" if draft else "published",
        }
        if post.hashtags:
            # NPF takes tags as a comma-separated string, not an array.
            body["tags"] = ",".join(post.hashtags)
        if post.title.strip():
            body["title"] = post.title.strip()

        payload = post_json(
            self.name,
            f"{API_ROOT}/blog/{blog}/posts",
            json=body,
            headers={
                "Authorization": f"Bearer {os.environ['TUMBLR_ACCESS_TOKEN']}",
                "Content-Type": "application/json",
            },
        )

        response = payload.get("response") or {}
        post_id = response.get("id_string") or response.get("id")
        if not post_id:
            raise PublishError(self.name, None, f"no post id in response: {payload}")

        return PublishResult(
            platform=self.name,
            post_id=str(post_id),
            state="draft" if draft else "published",
            permalink=response.get("display_text") or f"https://{blog}/post/{post_id}",
            note="link home is in the body — Tumblr has no canonical field",
        )


from ..config import register_publisher  # noqa: E402

register_publisher(TumblrPublisher())
