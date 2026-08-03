"""The `post_info` body TikTok expects, and the budgets that constrain it.

Split out of tiktok.py because video and photos are two endpoints with two
different field tables, and keeping both shapes next to each other is the only
way to see that they differ. They were assumed identical once, which put a
2200-character carousel caption into a 90-rune field.

Verified 2026-08-03 against the two references:

  video   /doc/content-posting-api-reference-direct-post
          title "The video caption. The maximum length is 2200 in UTF-16
          runes." Plus disable_duet, disable_stitch.

  photos  /doc/content-posting-api-reference-photo-post
          title "The maximum length for photo posts is 90 in UTF-16 runes."
          description "The maximum length for photo posts is 4000 in UTF-16
          runes." No duet or stitch field is listed.

Not sent, and documented as required on both endpoints: brand_content_toggle
and brand_organic_toggle. Whether the API actually refuses without them cannot
be established without publishing, so they are named in
skills/post-publisher/references/platform-limits.md rather than guessed at here.

Everything is a plain function of the post — no I/O, no credentials.
"""

from __future__ import annotations

import os
from typing import Any

from .base import Post

VIDEO_TITLE_LIMIT = 2200
PHOTO_TITLE_LIMIT = 90
PHOTO_DESCRIPTION_LIMIT = 4000

PHOTO_KINDS = frozenset({"image", "carousel"})


def text_limit_for(post: Post) -> int:
    """The caption budget for this post — the description on a photo post."""
    return PHOTO_DESCRIPTION_LIMIT if post.kind in PHOTO_KINDS else VIDEO_TITLE_LIMIT


def photo_title(post: Post) -> str:
    """A headline for a photo post, within the 90-rune ceiling.

    An explicit --title wins; otherwise the first non-blank caption line, which
    is where the hook already lives in everything this repo writes.
    """
    if post.title.strip():
        return post.title.strip()[:PHOTO_TITLE_LIMIT]
    for line in post.text.splitlines():
        if line.strip():
            return line.strip()[:PHOTO_TITLE_LIMIT]
    return ""


def privacy_level(info: dict[str, Any]) -> str:
    """Honour what the creator's account actually allows.

    A private account has no PUBLIC_TO_EVERYONE option and passing it is an
    error, so the configured value is used only when the account offers it.
    """
    options = info.get("privacy_level_options") or []
    wanted = os.environ.get("TIKTOK_PRIVACY_LEVEL", "PUBLIC_TO_EVERYONE")
    if wanted in options:
        return wanted
    return options[0] if options else "SELF_ONLY"


def post_info(post: Post, info: dict[str, Any]) -> dict[str, Any]:
    common = {
        "privacy_level": privacy_level(info),
        "disable_comment": bool(info.get("comment_disabled", False)),
    }
    if post.kind in PHOTO_KINDS:
        return {
            **common,
            "title": photo_title(post),
            "description": post.rendered_text()[:PHOTO_DESCRIPTION_LIMIT],
        }
    return {
        **common,
        "title": post.rendered_text()[:VIDEO_TITLE_LIMIT],
        "disable_duet": bool(info.get("duet_disabled", False)),
        "disable_stitch": bool(info.get("stitch_disabled", False)),
    }
