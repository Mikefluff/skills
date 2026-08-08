"""Qiita publishing via API v2.

Japanese-language technical audience. Only worth targeting with Japanese
content — an English article on Qiita reaches nobody and reads as spam to the
people it does reach. The skill will not translate for you; run the body through
`translation-sync` first if that is the intent.

Qiita has no canonical field, but its guidelines ask that reposted content link
the original, so the link is appended to the body automatically.

Auth is a personal access token with the `write_qiita` scope, from Settings →
Applications. Rate limit is 1000 authenticated requests an hour, which no
sensible use of this will approach.
"""

from __future__ import annotations

import os
import re
from typing import Any

from ..errors import PublishError
from ._json_api import post_json
from .base import Post, Publisher, PublishResult, Violation

API_URL = "https://qiita.com/api/v2/items"

# Verified 2026-08-05 against qiita.com/api/v2/docs.
MAX_TAGS = 5
MIN_TAGS = 1

# Rough test for "does this contain Japanese": hiragana, katakana or CJK.
_JAPANESE = re.compile(r"[぀-ゟ゠-ヿ一-鿿]")


class QiitaPublisher(Publisher):
    name = "qiita"
    requires_env = ("QIITA_TOKEN",)
    requires_oauth = False
    supports = frozenset({"article"})
    supports_draft = True  # `private: true` is Qiita's draft equivalent
    doc_url = "https://qiita.com/api/v2/docs"

    max_hashtags = MAX_TAGS
    min_media = 0
    max_media = 0

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        out: list[Violation] = []

        if not post.hashtags:
            out.append(
                Violation("block", "hashtags", "Qiita requires at least one tag")
            )
        elif len(post.hashtags) > MAX_TAGS:
            out.append(
                Violation(
                    "block",
                    "hashtags",
                    f"{len(post.hashtags)} tags; Qiita accepts at most {MAX_TAGS}",
                )
            )

        if not _JAPANESE.search(post.title + post.text):
            out.append(
                Violation(
                    "warn",
                    "text",
                    "no Japanese detected. Qiita's audience reads Japanese; an English "
                    "post there reaches nobody. Translate first (translation-sync)",
                )
            )

        if post.canonical_url:
            out.append(
                Violation(
                    "warn",
                    "canonical_url",
                    "Qiita has no canonical field — the original is linked at the end of "
                    "the body, which is what their guidelines ask for",
                )
            )
        return out

    def _body(self, post: Post, *, draft: bool) -> dict[str, Any]:
        body = post.text.strip()
        if post.canonical_url:
            body = f"{body}\n\n---\n\n> 初出: {post.canonical_url}"
        return {
            "title": post.title.strip(),
            "body": body,
            # `versions` is required per tag by the schema; an empty list means
            # "no version constraint", which is what a prose article wants.
            "tags": [{"name": t, "versions": []} for t in post.hashtags],
            "private": draft,
            "tweet": False,
        }

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        self.ensure_available()

        payload = post_json(
            self.name,
            API_URL,
            json=self._body(post, draft=draft),
            headers={
                "Authorization": f"Bearer {os.environ['QIITA_TOKEN']}",
                "Content-Type": "application/json",
            },
        )

        item_id = payload.get("id")
        if not item_id:
            raise PublishError(self.name, None, f"no item id in response: {payload}")

        return PublishResult(
            platform=self.name,
            post_id=str(item_id),
            state="draft" if draft else "published",
            permalink=payload.get("url"),
            note="private (Qiita's draft equivalent)" if draft else "",
        )


from ..config import register_publisher  # noqa: E402

register_publisher(QiitaPublisher())
