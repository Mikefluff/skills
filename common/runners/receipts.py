"""posted.json — what already went out, so it does not go out twice.

Every other runner in this repo is safely re-runnable: regenerate a slide and
you have spent a few cents. Re-run a publish and your followers see the post
twice. So publishing keeps a receipt next to the assets it published:

    ./generated/carousel/<slug>/
      slide-1.png ...
      captions.md
      manifest.json   ← generation state (existing)
      posted.json     ← publication state (this module)

Keyed on (platform, content_hash) so that editing the caption and re-running is
correctly treated as a new post, while re-running the identical command is not.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .publishers.base import PublishResult

RECEIPT_FILE = "posted.json"
SCHEMA_VERSION = 1


@dataclass
class Receipt:
    platform: str
    post_id: str
    state: str
    content_hash: str
    published_at: str  # ISO 8601 UTC
    permalink: str | None = None
    note: str = ""


def path_for(source_dir: Path) -> Path:
    return source_dir / RECEIPT_FILE


def load(source_dir: Path) -> list[Receipt]:
    path = path_for(source_dir)
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # A damaged receipt must not block publishing — but it also must not
        # silently claim "nothing published". The CLI warns on an empty result
        # when the file exists but did not parse.
        return []
    known = {f for f in Receipt.__dataclass_fields__}
    return [Receipt(**{k: v for k, v in r.items() if k in known}) for r in data.get("receipts", [])]


def find(source_dir: Path, platform: str, content_hash: str) -> Receipt | None:
    """Most recent receipt for this exact content on this platform, any state."""
    for r in reversed(load(source_dir)):
        if r.platform == platform and r.content_hash == content_hash:
            return r
    return None


def find_blocking(source_dir: Path, platform: str, content_hash: str, *, drafting: bool) -> Receipt | None:
    """The receipt that should stop this run, if any.

    State matters, and ignoring it broke the workflow the drafts exist for.
    Staging a draft, reviewing it, then publishing is the documented path for
    Meta and TikTok — and a receipt that treats `draft` as "already done" turns
    the second half of that into a --force, which is exactly backwards: the
    user deliberately staged it in order to publish it.

    So: publishing is blocked only by a previous publication. Drafting is
    blocked by either, since re-staging something already staged or already
    live has no purpose.
    """
    prior = find(source_dir, platform, content_hash)
    if prior is None:
        return None
    if prior.state == "published":
        return prior
    return prior if drafting else None


def record(source_dir: Path, result: PublishResult, content_hash: str) -> Receipt:
    """Append a receipt. Written immediately after each platform succeeds, so a
    crash mid-fan-out cannot cause a re-post of the platforms already done."""
    receipt = Receipt(
        platform=result.platform,
        post_id=result.post_id,
        state=result.state,
        content_hash=content_hash,
        published_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        permalink=result.permalink,
        note=result.note,
    )
    existing = load(source_dir)
    existing.append(receipt)
    path = path_for(source_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": SCHEMA_VERSION, "receipts": [asdict(r) for r in existing]}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return receipt
