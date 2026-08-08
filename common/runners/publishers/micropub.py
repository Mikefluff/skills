"""Micropub — one adapter, many destinations.

Micropub is the IndieWeb posting standard, so a single publisher reaches
Micro.blog, WordPress with the Micropub plugin, and any other endpoint that
implements the spec. That is the reason it is here: every other publisher in
this collection is one vendor's API, and this one is a protocol.

The endpoint is whatever the user's own site advertises, so both the URL and the
token are configuration rather than constants. Point `MICROPUB_ENDPOINT` at the
value your site publishes as `rel="micropub"`, and get the token from your
IndieAuth token endpoint.

The spec's useful details:
  - JSON bodies wrap *every* property value in an array, even single ones.
  - Success is 201 or 202, and the created URL comes back in `Location` — not
    in the body, which may be empty.
  - `mp-syndicate-to` asks the endpoint to cross-post on your behalf, which some
    implementations support and most ignore.
"""

from __future__ import annotations

import os
from typing import Any

import requests

from ..errors import PublishError, RateLimitError
from .base import Post, Publisher, PublishResult, Violation


class MicropubPublisher(Publisher):
    name = "micropub"
    requires_env = ("MICROPUB_ENDPOINT", "MICROPUB_TOKEN")
    requires_oauth = False
    supports = frozenset({"article"})
    supports_draft = False  # post-status is an extension, not core spec
    doc_url = "https://micropub.spec.indieweb.org/"

    min_media = 0
    max_media = 0

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        out: list[Violation] = []
        endpoint = os.environ.get("MICROPUB_ENDPOINT", "")
        if endpoint and not endpoint.startswith(("http://", "https://")):
            out.append(
                Violation("block", "MICROPUB_ENDPOINT", f"not an absolute URL: {endpoint}")
            )
        if post.canonical_url:
            out.append(
                Violation(
                    "warn",
                    "canonical_url",
                    "sent as u-syndication; whether your endpoint honours it as a "
                    "canonical link depends on the implementation",
                )
            )
        return out

    def _body(self, post: Post) -> dict[str, Any]:
        properties: dict[str, list[Any]] = {
            "name": [post.title.strip()],
            "content": [post.text],
        }
        if post.hashtags:
            properties["category"] = list(post.hashtags)
        if post.description.strip():
            properties["summary"] = [post.description.strip()]
        if post.canonical_url:
            # u-syndication is the IndieWeb convention for "this also lives here".
            properties["syndication"] = [post.canonical_url]
        targets = post.extra.get("syndicate_to")
        if targets:
            properties["mp-syndicate-to"] = list(targets)
        return {"type": ["h-entry"], "properties": properties}

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        self.ensure_available()
        endpoint = os.environ["MICROPUB_ENDPOINT"]

        try:
            resp = requests.post(
                endpoint,
                json=self._body(post),
                headers={
                    "Authorization": f"Bearer {os.environ['MICROPUB_TOKEN']}",
                    "Content-Type": "application/json",
                },
                timeout=60,
            )
        except requests.RequestException as exc:
            raise PublishError(self.name, None, f"network error: {exc}") from exc

        if resp.status_code == 429:
            raise RateLimitError(self.name, 429, "rate limited by the Micropub endpoint")

        # The spec's success codes. Anything else is a failure regardless of body.
        if resp.status_code not in (200, 201, 202):
            raise PublishError(self.name, resp.status_code, resp.text[:300])

        location = resp.headers.get("Location")
        if not location:
            raise PublishError(
                self.name,
                resp.status_code,
                "endpoint accepted the post but returned no Location header, "
                "so the created URL is unknown (the spec requires one)",
            )

        return PublishResult(
            platform=self.name,
            post_id=location,
            state="published" if resp.status_code != 202 else "pending_review",
            permalink=location,
            note="accepted for processing" if resp.status_code == 202 else "",
        )


from ..config import register_publisher  # noqa: E402

register_publisher(MicropubPublisher())
