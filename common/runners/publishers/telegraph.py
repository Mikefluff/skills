"""Telegraph publishing — telegra.ph.

The odd one out in this set, and worth having for exactly that reason: no OAuth,
no application review, no account even — createAccount hands back a token on the
spot. It is the fastest way to put a piece of long-form text behind a stable URL,
and it renders natively inside Telegram, which matters if any of the distribution
runs through a channel.

What it does not do is SEO. Telegraph pages carry no canonical tag and no author
domain, so this is a reach and convenience play, not a ranking one. The canonical
URL is still written into the page as a visible source line, because a reader
arriving from Telegram should be able to find the original.

Content format: Telegraph takes a DOM tree as JSON — a list of strings and
{"tag", "attrs", "children"} objects — not HTML and not markdown. The converter
below covers the subset that survives the round trip; anything richer should go
to dev.to instead.
"""

from __future__ import annotations

import os
import re
from typing import Any

from ..errors import PublishError
from ._json_api import post_json
from .base import Post, Publisher, PublishResult, Violation

API_ROOT = "https://api.telegra.ph"

# Verified 2026-08-05 against telegra.ph/api.
MAX_TITLE = 256
MAX_CONTENT_BYTES = 64 * 1024

# Telegraph accepts a short allow-list of tags. Anything else is dropped by the
# API, so the converter never emits one.
_INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_LIST_ITEM = re.compile(r"^\s*[-*]\s+(.*)$")


def _inline(text: str) -> list[Any]:
    """Split a line into text and anchor nodes. Links are the only inline form
    Telegraph reliably keeps, and they are the ones that matter here."""
    nodes: list[Any] = []
    cursor = 0
    for match in _INLINE_LINK.finditer(text):
        if match.start() > cursor:
            nodes.append(text[cursor : match.start()])
        nodes.append({"tag": "a", "attrs": {"href": match.group(2)}, "children": [match.group(1)]})
        cursor = match.end()
    if cursor < len(text):
        nodes.append(text[cursor:])
    return nodes or [""]


def _list_node(lines: list[str]) -> dict[str, Any]:
    items = [
        {"tag": "li", "children": _inline(m.group(1))}
        for m in (_LIST_ITEM.match(line) for line in lines)
        if m
    ]
    return {"tag": "ul", "children": items}


def _block_node(block: str) -> dict[str, Any]:
    """One markdown block → one Telegraph node.

    Headings collapse to h3/h4 because Telegraph supports only those two levels;
    the page title is already an h1 the API renders itself.
    """
    lines = block.split("\n")

    if all(_LIST_ITEM.match(line) for line in lines):
        return _list_node(lines)

    if block.startswith("```"):
        code = "\n".join(line for line in lines if not line.startswith("```"))
        return {"tag": "pre", "children": [code]}

    heading = _HEADING.match(lines[0])
    if heading and len(lines) == 1:
        level = "h3" if len(heading.group(1)) <= 2 else "h4"
        return {"tag": level, "children": _inline(heading.group(2))}

    return {"tag": "p", "children": _inline(" ".join(lines))}


def markdown_to_nodes(body: str) -> list[Any]:
    """Markdown subset → Telegraph node list."""
    return [_block_node(b.strip()) for b in body.split("\n\n") if b.strip()]


class TelegraphPublisher(Publisher):
    name = "telegraph"
    requires_env = ()  # a token is created on demand if none is set
    requires_oauth = False
    supports = frozenset({"article"})
    supports_draft = False
    doc_url = "https://telegra.ph/api"

    max_title_chars = MAX_TITLE
    min_media = 0
    max_media = 0  # images must already be hosted and referenced in the body

    def _extra_preflight(self, post: Post, *, draft: bool = False) -> list[Violation]:
        out: list[Violation] = []
        nodes = markdown_to_nodes(post.text)
        size = len(str(nodes).encode("utf-8"))
        if size > MAX_CONTENT_BYTES:
            out.append(
                Violation(
                    "block",
                    "text",
                    f"rendered content is ~{size // 1024} KB; Telegraph caps a page at 64 KB",
                )
            )
        if post.canonical_url:
            out.append(
                Violation(
                    "warn",
                    "canonical_url",
                    "Telegraph has no canonical tag — the URL is added as a visible "
                    "source line instead, so this page cannot pass ranking signal home",
                )
            )
        return out

    def _token(self) -> str:
        """Reuse TELEGRAPH_ACCESS_TOKEN, or mint a throwaway account.

        A minted token is printed once so it can be saved; without it, the page
        exists but is no longer editable by this machine.
        """
        existing = os.environ.get("TELEGRAPH_ACCESS_TOKEN")
        if existing:
            return existing

        payload = post_json(
            self.name,
            f"{API_ROOT}/createAccount",
            json={"short_name": os.environ.get("TELEGRAPH_SHORT_NAME", "skills")},
            headers={"Content-Type": "application/json"},
        )
        if not payload.get("ok"):
            raise PublishError(self.name, None, payload.get("error", "createAccount failed"))
        return payload["result"]["access_token"]

    def _content(self, post: Post) -> list[Any]:
        nodes = markdown_to_nodes(post.text)
        if post.canonical_url:
            nodes.append(
                {
                    "tag": "p",
                    "children": [
                        "Originally published at ",
                        {
                            "tag": "a",
                            "attrs": {"href": post.canonical_url},
                            "children": [post.canonical_url],
                        },
                    ],
                }
            )
        return nodes

    def publish(self, post: Post, *, draft: bool = False) -> PublishResult:
        token = self._token()
        minted = not os.environ.get("TELEGRAPH_ACCESS_TOKEN")

        body: dict[str, Any] = {
            "access_token": token,
            "title": post.title.strip()[:MAX_TITLE],
            "content": self._content(post),
            "return_content": False,
        }
        author = post.extra.get("author_name")
        if author:
            body["author_name"] = str(author)
        if post.canonical_url:
            body["author_url"] = post.canonical_url

        payload = post_json(
            self.name,
            f"{API_ROOT}/createPage",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        if not payload.get("ok"):
            raise PublishError(self.name, None, payload.get("error", "createPage failed"))

        page = payload["result"]
        note = "live"
        if minted:
            note = (
                f"live. A throwaway account was created — save this to edit the page later: "
                f"TELEGRAPH_ACCESS_TOKEN={token}"
            )
        return PublishResult(
            platform=self.name,
            post_id=page.get("path", ""),
            state="published",
            permalink=page.get("url"),
            note=note,
        )


from ..config import register_publisher  # noqa: E402

register_publisher(TelegraphPublisher())
