"""dev.to (Forem) article publishing.

The anchor of the syndication set, for one reason that has nothing to do with
audience size: **dev.to marks outbound links dofollow**. Medium, Hashnode,
HackerNoon and every Russian platform mark them nofollow or rel=ugc, so a link
home from those passes no ranking signal at all. dev.to is the only one here
that does.

It also honours `canonical_url`, which is what makes the rest of the chain work:
publish here with canonical pointing at your own post, then let Medium's "Import
a Story" pull this URL in — Medium sets its own canonical back to the source
automatically, so a platform with no usable API still ends up pointing home.

API notes:
  - Auth is a bare `api-key` header, not a Bearer token.
  - The body is wrapped: {"article": {...}}, not the fields at top level.
  - Four tags maximum, and the API rejects a fifth rather than truncating.
  - `published: false` creates a real draft, so --draft is honest here.
"""

from __future__ import annotations

import os
from typing import Any

from ..errors import PublishError
from ._json_api import post_json
from .base import Post, Publisher, PublishResult, Violation

API_URL = "https://dev.to/api/articles"

# Verified 2026-08-05 against developers.forem.com/api/v1. The tag cap is a hard
# API constraint, not a style guideline — hence a block below rather than the
# generic hashtag warning.
MAX_TAGS = 4
MAX_TITLE = 250


class DevToPublisher(Publisher):
    name = "devto"
    requires_env = ("DEVTO_API_KEY",)
    requires_oauth = False
    supports = frozenset({"article"})
    supports_draft = True
    needs_public_media_url = True  # main_image is a URL; dev.to fetches it
    doc_url = "https://developers.forem.com/api/v1#tag/articles"

    max_title_chars = MAX_TITLE
    max_hashtags = MAX_TAGS
    min_media = 0
    max_media = 1  # cover image only

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        out: list[Violation] = []

        if len(post.hashtags) > MAX_TAGS:
            out.append(
                Violation(
                    "block",
                    "hashtags",
                    f"{len(post.hashtags)} tags; the API accepts at most {MAX_TAGS} "
                    f"and rejects the request rather than dropping the extras",
                )
            )

        # Forem tags are alphanumeric — a hyphen or a space silently becomes a
        # different tag than the author meant, or a 422.
        for tag in post.hashtags:
            if not tag.isalnum():
                out.append(
                    Violation(
                        "warn",
                        "hashtags",
                        f"tag '{tag}' is not alphanumeric; dev.to will normalise or reject it",
                    )
                )

        if not post.description.strip():
            out.append(
                Violation(
                    "warn",
                    "description",
                    "no description — dev.to will auto-excerpt the first lines, "
                    "which is rarely the sentence you would pick for search results",
                )
            )
        return out

    def _body(self, post: Post, *, draft: bool) -> dict[str, Any]:
        article: dict[str, Any] = {
            "title": post.title.strip(),
            "body_markdown": post.text,
            "published": not draft,
        }
        if post.hashtags:
            article["tags"] = list(post.hashtags)
        if post.canonical_url:
            article["canonical_url"] = post.canonical_url
        if post.description.strip():
            article["description"] = post.description.strip()
        if post.series:
            article["series"] = post.series

        cover = post.extra.get("cover_url")
        if cover:
            article["main_image"] = cover
        if post.extra.get("organization_id"):
            article["organization_id"] = int(post.extra["organization_id"])
        return {"article": article}

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        self.ensure_available()

        payload = post_json(
            self.name,
            API_URL,
            json=self._body(post, draft=draft),
            headers={
                "api-key": os.environ["DEVTO_API_KEY"],
                "Content-Type": "application/json",
            },
        )

        article_id = payload.get("id")
        if not article_id:
            raise PublishError(self.name, None, f"no article id in response: {payload}")

        url = payload.get("url") or payload.get("canonical_url")
        return PublishResult(
            platform=self.name,
            post_id=str(article_id),
            state="draft" if draft else "published",
            permalink=url,
            note=(
                "draft saved — publish it from the dev.to dashboard"
                if draft
                else "live. To mirror onto Medium, use Import a Story with this URL: "
                "Medium sets its canonical back to the source for you."
            ),
            extra={"slug": payload.get("slug"), "canonical_url": payload.get("canonical_url")},
        )


from ..config import register_publisher  # noqa: E402

register_publisher(DevToPublisher())
