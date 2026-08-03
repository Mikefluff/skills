"""Presentation for the publish CLI — previews, prompts, listings, summary.

Separated from the orchestration so that what the user is shown before an
irreversible action is one readable file rather than print() calls scattered
through a decision loop. The preview is the last thing standing between a
typo and an audience, so it is worth being able to read it on its own.

Nothing here decides anything. `Outcome` is returned by the orchestrator and
consumed here only to count.
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path

from .. import receipts
from ..publishers.base import Post, Publisher

MB = 1024 * 1024
PREVIEW_TEXT_LIMIT = 600
PREVIEW_ALT_LIMIT = 40


class Outcome(Enum):
    """What happened to one platform in one run.

    WOULD_PROCEED only occurs on a dry run: everything passed and the only
    reason nothing was sent is that --yes was absent.
    """

    PUBLISHED = "published"
    WOULD_PROCEED = "would proceed"
    SKIPPED = "skipped"
    FAILED = "failed"


def preview(post: Post, pub: Publisher, *, draft: bool) -> str:
    action = "DRAFT" if draft else "PUBLISH"
    out = [f"  → {action} to {pub.name}", f"    kind:  {post.kind}"]
    if post.title:
        out.append(f"    title: {post.title}")
    out.extend(_text_block(post))
    out.extend(_media_block(post))
    return "\n".join(out)


def _text_block(post: Post) -> list[str]:
    rendered = post.rendered_text()
    if not rendered:
        return []
    body = rendered
    if len(body) > PREVIEW_TEXT_LIMIT:
        body = body[:PREVIEW_TEXT_LIMIT] + f"… (+{len(rendered) - PREVIEW_TEXT_LIMIT} chars)"
    indented = "\n".join(f"      {ln}" for ln in body.splitlines())
    return [f"    text ({len(rendered)} chars):\n{indented}"]


def _media_block(post: Post) -> list[str]:
    out = []
    for i, path in enumerate(post.media):
        size = path.stat().st_size / MB if path.is_file() else 0
        alt = post.alt_for(i)
        note = f'  alt="{alt[:PREVIEW_ALT_LIMIT]}"' if alt else "  (no alt)"
        out.append(f"    media: {path.name}  {size:.1f} MB{note}")
    return out


def ask(question: str) -> bool:
    if not sys.stdin.isatty():
        sys.stderr.write(f"\n{question} — stdin is not a TTY, refusing to assume yes.\n")
        return False
    sys.stderr.write(f"\n{question} [y/N] ")
    sys.stderr.flush()
    return sys.stdin.readline().strip().lower() in {"y", "yes"}


def describe_platforms(publishers: list[Publisher]) -> int:
    if not publishers:
        print("No publishers registered.", file=sys.stderr)
        return 1
    print("Platforms:")
    for p in publishers:
        draft = " · draft" if p.supports_draft else ""
        print(f"  {p.name:12s} {_state(p):48s} [{', '.join(sorted(p.supports))}{draft}]")
    return 0


def _state(pub: Publisher) -> str:
    if not pub.available():
        return f"missing env: {', '.join(pub.missing_env())}"
    if not pub.token_ready():
        return "configured, not authorised — run cli.auth"
    return "ready"


def report_readiness(pairs: list[tuple[str, Publisher | None]]) -> int:
    rc = 0
    for name, pub in pairs:
        if pub is None:
            rc = 2
            continue
        if not pub.available():
            print(f"{pub.name}: missing env: {', '.join(pub.missing_env())}", file=sys.stderr)
            rc = 2
        elif not pub.token_ready():
            print(
                f"{pub.name}: no usable token. "
                f"Run: python3 -m common.runners.cli.auth --platform {pub.name}",
                file=sys.stderr,
            )
            rc = 2
        else:
            print(f"{pub.name}: ready")
    return rc


def summarise(outcomes: list[Outcome], *, live: bool, receipt_dir: Path | None) -> int:
    tally = {o: outcomes.count(o) for o in Outcome}
    print()

    if not live:
        print(
            f"Dry run complete — {tally[Outcome.WOULD_PROCEED]} of {len(outcomes)} platform(s) "
            f"would proceed ({tally[Outcome.SKIPPED]} skipped, {tally[Outcome.FAILED]} blocked). "
            f"Add --yes to publish."
        )
        return 1 if tally[Outcome.FAILED] else 0

    print(
        f"Published: {tally[Outcome.PUBLISHED]} · skipped: {tally[Outcome.SKIPPED]} "
        f"· failed: {tally[Outcome.FAILED]}"
    )
    if receipt_dir and tally[Outcome.PUBLISHED]:
        print(f"Receipt: {receipts.path_for(receipt_dir)}")
    return 1 if tally[Outcome.FAILED] else 0
