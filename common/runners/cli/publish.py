"""`python3 -m common.runners.cli.publish` — send finished assets to platforms.

Unlike every other CLI in this package, the default action is to do NOTHING.
Generation is retryable; publication is not. So:

    publish ./generated/carousel/foo --platform threads          → dry-run preview
    publish ./generated/carousel/foo --platform threads --yes    → asks, then posts

`--yes` is not "skip the prompt" here (that is what it means for cost
confirmation elsewhere) — it is "leave dry-run mode". The per-platform
confirmation still happens, because approving an Instagram post is not
approval to also post to X.

This module is argparse plus orchestration. Working out what a directory
contains lives in `postsource`, and rendering a post for the user lives in
`_publish_view`, so that neither needs a parser to be tested.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import config, postsource, receipts
from ..errors import RunnerError
from ..postsource import PostOverrides, build_post
from ..publishers.base import Post, Publisher
from ._publish_view import Outcome, ask, describe_platforms, preview, report_readiness, summarise

# Re-exported for the tests and for anything that used to import them from here.
discover_media = postsource.discover_media
extract_caption = postsource.extract_caption


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="common.runners.cli.publish",
        description="Publish finished assets to social platforms. Dry-run unless --yes.",
    )
    p.add_argument("source", nargs="?", help="output dir (./generated/...) or a single media file")
    p.add_argument("--platform", "--platforms", dest="platform", help="comma-separated: telegram,threads,...")
    p.add_argument("--kind", choices=["text", "image", "carousel", "video"], help="override auto-detection")
    p.add_argument("--text", help="caption/body (overrides captions.md)")
    p.add_argument("--text-file", type=Path, help="read caption from this file verbatim")
    p.add_argument("--title", default="", help="video/article title (YouTube, LinkedIn)")
    p.add_argument("--hashtags", default="", help="comma-separated, with or without '#'")
    p.add_argument("--alt", action="append", default=[], help="alt text, repeat per media file in order")
    p.add_argument("--link", help="URL to attach where the platform supports it")
    p.add_argument("--draft", action="store_true", help="create a draft instead of publishing")
    p.add_argument("--yes", action="store_true", help="leave dry-run mode (still asks per platform)")
    p.add_argument("--dry-run", action="store_true", help="explicit no-op preview (the default)")
    p.add_argument("--force", action="store_true", help="publish even if posted.json says it already went out")
    p.add_argument("--list-platforms", action="store_true", help="show platforms and their readiness")
    p.add_argument("--check", action="store_true", help="readiness check for --platform, no posting")
    p.add_argument(
        "--publish-container",
        metavar="ID",
        help="publish a container left by an earlier --draft run (Meta platforms)",
    )
    return p


def post_from_args(args: argparse.Namespace) -> tuple[Post, Path | None]:
    caption = args.text
    if caption is None and args.text_file:
        caption = args.text_file.read_text(encoding="utf-8").strip()
    return build_post(
        args.source,
        PostOverrides(
            caption=caption,
            kind=args.kind,
            title=args.title,
            hashtags=tuple(h.strip() for h in args.hashtags.split(",") if h.strip()),
            alt_texts=tuple(args.alt),
            link=args.link,
        ),
    )


# ── one platform ────────────────────────────────────────────────────────────


def run_platform(
    pub: Publisher, post: Post, args: argparse.Namespace, receipt_dir: Path | None, *, live: bool
) -> Outcome:
    """Take one platform from candidate to published, or explain why not.

    Split out of main() so the per-platform decision sequence reads as one
    thing: the order of these gates is the safety contract, and it was hard to
    audit inside a hundred-line loop.
    """
    if args.draft and not pub.supports_draft:
        print(f"— {pub.name}: skipped, no draft support (drop --draft to publish live)")
        return Outcome.SKIPPED

    violations = pub.preflight(post, draft=args.draft)
    for v in violations:
        print(f"    {v}")
    blocking = [v for v in violations if v.severity == "block"]
    if blocking:
        print(f"✗ {pub.name}: {len(blocking)} blocking issue(s) — not sent", file=sys.stderr)
        return Outcome.FAILED

    print(preview(post, pub, draft=args.draft))

    # Evaluated on a dry run too: a preview claiming "would proceed" about a
    # post that is already out, or one that would die on a missing token, is
    # worse than no preview at all.
    blocked_by = _prior_receipt(receipt_dir, pub, post, args)
    if blocked_by is not None:
        return blocked_by
    not_ready = _readiness(pub)
    if not_ready is not None:
        return not_ready

    if not live:
        return Outcome.WOULD_PROCEED

    verb = "Create draft on" if args.draft else "PUBLISH to"
    if not ask(f"{verb} {pub.name}?"):
        print(f"— {pub.name}: declined")
        return Outcome.SKIPPED

    return _send(pub, post, args, receipt_dir)


def _prior_receipt(
    receipt_dir: Path | None, pub: Publisher, post: Post, args: argparse.Namespace
) -> Outcome | None:
    if receipt_dir is None or args.force:
        return None
    prior = receipts.find_blocking(receipt_dir, pub.name, post.content_hash(), drafting=args.draft)
    if prior is None:
        return None
    what = "staged as a draft" if prior.state == "draft" else prior.state
    print(
        f"— {pub.name}: skipped, identical content already {what} "
        f"at {prior.published_at} ({prior.permalink or 'no permalink'}). Use --force."
    )
    return Outcome.SKIPPED


def _readiness(pub: Publisher) -> Outcome | None:
    if not pub.available():
        print(f"✗ {pub.name}: missing env: {', '.join(pub.missing_env())}", file=sys.stderr)
        return Outcome.FAILED
    if not pub.token_ready():
        print(
            f"✗ {pub.name}: not authorised. "
            f"Run: python3 -m common.runners.cli.auth --platform {pub.name}",
            file=sys.stderr,
        )
        return Outcome.FAILED
    return None


def _send(
    pub: Publisher, post: Post, args: argparse.Namespace, receipt_dir: Path | None
) -> Outcome:
    try:
        result = pub.publish(post, draft=args.draft)
    except RunnerError as exc:
        print(f"✗ {pub.name}: {exc}", file=sys.stderr)
        return Outcome.FAILED
    print(f"✓ {result.display()}")
    if receipt_dir:
        receipts.record(receipt_dir, result, post.content_hash())
    return Outcome.PUBLISHED


# ── subcommands ─────────────────────────────────────────────────────────────


def publish_container(args: argparse.Namespace, names: list[str], *, live: bool) -> int:
    """Second half of a --draft run: post the container that was staged then."""
    if len(names) != 1:
        print("--publish-container takes exactly one --platform", file=sys.stderr)
        return 2
    pub = _resolve(names[0])
    if pub is None:
        return 2
    if not hasattr(pub, "publish_container"):
        print(f"{pub.name} has no staged-container concept", file=sys.stderr)
        return 2

    container_id = args.publish_container
    if not live:
        print(f"DRY RUN — would publish container {container_id} on {pub.name}. Add --yes.")
        return 0
    if not ask(f"PUBLISH staged container {container_id} on {pub.name}?"):
        print("— declined")
        return 0

    try:
        result = pub.publish_container(container_id)
    except RunnerError as exc:
        print(f"✗ {pub.name}: {exc}", file=sys.stderr)
        return 1
    print(f"✓ {result.display()}")
    _record_container(args, result)
    return 0


def _record_container(args: argparse.Namespace, result) -> None:
    """Without this the container goes live and nothing says so, and the next
    plain --yes run over the same directory would publish it again."""
    if not args.source:
        print(
            "  No source directory given, so no receipt was written — pass the "
            "output dir alongside --publish-container to keep posted.json honest."
        )
        return
    try:
        post, receipt_dir = post_from_args(args)
    except RunnerError:
        return
    if receipt_dir:
        receipts.record(receipt_dir, result, post.content_hash())
        print(f"Receipt: {receipts.path_for(receipt_dir)}")


def _resolve(name: str) -> Publisher | None:
    try:
        return config.get_publisher(name)
    except KeyError as exc:
        print(f"✗ {exc.args[0]}", file=sys.stderr)
        return None


# ── main ────────────────────────────────────────────────────────────────────


def _informational(args: argparse.Namespace, names: list[str]) -> int | None:
    """Modes that never publish. Returns an exit code, or None to carry on."""
    if args.list_platforms:
        return describe_platforms(config.all_publishers())
    if not names:
        print("missing --platform. Use --list-platforms to see options.", file=sys.stderr)
        return 2
    if args.check:
        return report_readiness([(n, _resolve(n)) for n in names])
    return None


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_publishers()

    names = [n.strip() for n in (args.platform or "").split(",") if n.strip()]
    early = _informational(args, names)
    if early is not None:
        return early

    live = args.yes and not args.dry_run

    if args.publish_container:
        return publish_container(args, names, live=live)

    try:
        post, receipt_dir = post_from_args(args)
    except RunnerError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not live:
        print("DRY RUN — nothing will be sent. Add --yes to publish for real.\n")

    outcomes = []
    for name in names:
        pub = _resolve(name)
        if pub is None:
            outcomes.append(Outcome.FAILED)
            continue
        outcomes.append(run_platform(pub, post, args, receipt_dir, live=live))

    return summarise(outcomes, live=live, receipt_dir=receipt_dir)


if __name__ == "__main__":
    sys.exit(main())
