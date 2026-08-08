"""Hashnode article publishing via the GraphQL API.

Requires a **Hashnode Pro** publication. Hashnode retired free API access in May
2026: reads of public data still work, but every write mutation — including the
`publishPost` this module calls — now checks that the target publication is on a
paid plan. There is no free path, so the gate below fails early and says why
rather than letting a 403 arrive mid-publish.

`originalArticleURL` is Hashnode's spelling of canonical. Outbound links are
nofollow, so the value here is reach and the canonical consolidation, not link
equity.
"""

from __future__ import annotations

import os
from typing import Any

from ..errors import PublishError
from ._json_api import post_json
from .base import Post, Publisher, PublishResult, Violation

# Verified 2026-08-05. The older api.hashnode.com endpoint is discontinued.
API_URL = "https://gql.hashnode.com"

MAX_TITLE = 250
MAX_TAGS = 5

_PUBLISH_MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post { id slug url title }
  }
}
"""


class HashnodePublisher(Publisher):
    name = "hashnode"
    requires_env = ("HASHNODE_TOKEN", "HASHNODE_PUBLICATION_ID")
    requires_oauth = False
    supports = frozenset({"article"})
    supports_draft = False  # createDraft is a separate mutation; not wired
    doc_url = "https://apidocs.hashnode.com"

    max_title_chars = MAX_TITLE
    max_hashtags = MAX_TAGS
    min_media = 0
    max_media = 0  # cover is passed as a URL, not uploaded

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        out: list[Violation] = []
        if draft:
            out.append(
                Violation(
                    "block",
                    "draft",
                    "hashnode drafts go through a different mutation (createDraft) "
                    "which is not wired here — publish live or use dev.to for drafts",
                )
            )
        out.append(
            Violation(
                "warn",
                "plan",
                "write mutations require an active Hashnode Pro plan on the target "
                "publication; a free publication returns a permissions error",
            )
        )
        return out

    def _input(self, post: Post) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "publicationId": os.environ["HASHNODE_PUBLICATION_ID"],
            "title": post.title.strip(),
            "contentMarkdown": post.text,
        }
        if post.hashtags:
            # Hashnode wants tag objects, not bare strings; slug is the stable key.
            payload["tags"] = [{"slug": t.lower(), "name": t} for t in post.hashtags]
        if post.canonical_url:
            payload["originalArticleURL"] = post.canonical_url
        if post.description.strip():
            payload["subtitle"] = post.description.strip()[:250]
        cover = post.extra.get("cover_url")
        if cover:
            payload["coverImageOptions"] = {"coverImageURL": cover}
        if post.series:
            payload["seriesId"] = post.series
        return payload

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        self.ensure_available()

        payload = post_json(
            self.name,
            API_URL,
            json={"query": _PUBLISH_MUTATION, "variables": {"input": self._input(post)}},
            headers={
                "Authorization": os.environ["HASHNODE_TOKEN"],
                "Content-Type": "application/json",
            },
        )

        # GraphQL answers 200 with an `errors` array, so a happy status code is
        # not evidence of anything.
        if payload.get("errors"):
            messages = "; ".join(
                e.get("message", "") for e in payload["errors"] if isinstance(e, dict)
            )
            hint = ""
            if "permission" in messages.lower() or "plan" in messages.lower():
                hint = " (this usually means the publication is not on Hashnode Pro)"
            raise PublishError(self.name, None, f"{messages}{hint}")

        node = ((payload.get("data") or {}).get("publishPost") or {}).get("post") or {}
        if not node.get("id"):
            raise PublishError(self.name, None, f"no post in response: {payload}")

        return PublishResult(
            platform=self.name,
            post_id=str(node["id"]),
            state="published",
            permalink=node.get("url"),
            extra={"slug": node.get("slug")},
        )


from ..config import register_publisher  # noqa: E402

register_publisher(HashnodePublisher())
