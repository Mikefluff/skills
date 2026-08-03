"""`python3 -m common.runners.cli.publish` — send finished assets to platforms.

Unlike every other CLI in this package, the default action is to do NOTHING.
Generation is retryable; publication is not. So:

    publish ./generated/carousel/foo --platform threads          → dry-run preview
    publish ./generated/carousel/foo --platform threads --yes    → asks, then posts

`--yes` is not "skip the prompt" here (that is what it means for cost
confirmation elsewhere) — it is "leave dry-run mode". The per-platform
confirmation still happens, because approving an Instagram post is not
approval to also post to X.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .. import config, receipts
from ..errors import PublishError, RunnerError
from ..publishers.base import IMAGE_EXTS, VIDEO_EXTS, Post, PostKind, Publisher

CAPTION_FILE = "captions.md"

# Headings under which carousel-builder / reel-builder put the main post body.
# Tolerant on purpose: captions.md is written by an agent, not by a runner, so
# the shape is a convention rather than a guarantee. Whatever gets extracted is
# shown in the dry-run preview, which is where a bad parse gets caught.
_MAIN_HEADING = re.compile(
    r"^#{1,6}\s*(main post|post caption|caption|post copy|основной пост|подпись)\b.*$",
    re.IGNORECASE,
)
_ANY_HEADING = re.compile(r"^#{1,6}\s+")


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


# ── building the Post ───────────────────────────────────────────────────────


def extract_caption(text: str) -> str:
    """Pull the main post body out of a captions.md, or fall back to the lot."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if _MAIN_HEADING.match(line.strip()):
            start = i + 1
            break

    if start is None:
        # No recognised heading — use everything, minus heading lines.
        body = "\n".join(ln for ln in lines if not _ANY_HEADING.match(ln))
        return body.strip()

    collected = []
    for line in lines[start:]:
        if _ANY_HEADING.match(line.strip()):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def _sorted_media(paths: list[Path]) -> list[Path]:
    """Numeric-aware sort so slide-2 precedes slide-10."""

    def key(p: Path):
        nums = [int(n) for n in re.findall(r"\d+", p.stem)]
        return (nums, p.name)

    return sorted(paths, key=key)


def discover_media(source: Path) -> tuple[list[Path], PostKind]:
    """Work out what a generated output dir is holding."""
    if source.is_file():
        ext = source.suffix.lower()
        if ext in VIDEO_EXTS:
            return [source], "video"
        if ext in IMAGE_EXTS:
            return [source], "image"
        raise RunnerError(f"unsupported file type: {source.name}")

    final = source / "final.mp4"
    if final.is_file():
        return [final], "video"

    videos = _sorted_media([p for p in source.glob("*") if p.suffix.lower() in VIDEO_EXTS])
    if videos:
        return ([videos[0]], "video") if len(videos) == 1 else (videos, "carousel")

    images = _sorted_media([p for p in source.glob("*") if p.suffix.lower() in IMAGE_EXTS])
    if len(images) > 1:
        return images, "carousel"
    if len(images) == 1:
        return images, "image"

    return [], "text"


def build_post(args: argparse.Namespace) -> tuple[Post, Path | None]:
    """Returns the Post plus the directory that should hold posted.json."""
    media: list[Path] = []
    kind: PostKind = "text"
    receipt_dir: Path | None = None

    if args.source:
        source = Path(args.source).expanduser()
        if not source.exists():
            raise RunnerError(f"source not found: {source}")
        media, kind = discover_media(source)
        receipt_dir = source if source.is_dir() else source.parent

    if args.text is not None:
        caption = args.text
    elif args.text_file:
        caption = args.text_file.read_text(encoding="utf-8").strip()
    elif receipt_dir and (receipt_dir / CAPTION_FILE).is_file():
        caption = extract_caption((receipt_dir / CAPTION_FILE).read_text(encoding="utf-8"))
    else:
        caption = ""

    if args.kind:
        kind = args.kind

    hashtags = tuple(h.strip() for h in args.hashtags.split(",") if h.strip())

    post = Post(
        kind=kind,
        text=caption,
        media=tuple(media),
        alt_texts=tuple(args.alt),
        title=args.title,
        link=args.link,
        hashtags=hashtags,
    )
    return post, receipt_dir


# ── presentation ────────────────────────────────────────────────────────────


def preview(post: Post, pub: Publisher, *, draft: bool) -> str:
    rendered = post.rendered_text()
    action = "DRAFT" if draft else "PUBLISH"
    out = [
        f"  → {action} to {pub.name}",
        f"    kind:  {post.kind}",
    ]
    if post.title:
        out.append(f"    title: {post.title}")
    if rendered:
        body = rendered if len(rendered) <= 600 else rendered[:600] + f"… (+{len(rendered) - 600} chars)"
        indented = "\n".join(f"      {ln}" for ln in body.splitlines())
        out.append(f"    text ({len(rendered)} chars):\n{indented}")
    for i, m in enumerate(post.media):
        size = m.stat().st_size / (1024 * 1024) if m.is_file() else 0
        alt = post.alt_for(i)
        alt_note = f'  alt="{alt[:40]}"' if alt else "  (no alt)"
        out.append(f"    media: {m.name}  {size:.1f} MB{alt_note}")
    return "\n".join(out)


def ask(question: str) -> bool:
    if not sys.stdin.isatty():
        sys.stderr.write(f"\n{question} — stdin is not a TTY, refusing to assume yes.\n")
        return False
    sys.stderr.write(f"\n{question} [y/N] ")
    sys.stderr.flush()
    return sys.stdin.readline().strip().lower() in {"y", "yes"}


def list_platforms() -> int:
    pubs = config.all_publishers()
    if not pubs:
        print("No publishers registered.", file=sys.stderr)
        return 1
    print("Platforms:")
    for p in pubs:
        if not p.available():
            state = f"missing env: {', '.join(p.missing_env())}"
        elif not p.token_ready():
            state = "configured, not authorised — run cli.auth"
        else:
            state = "ready"
        draft = " · draft" if p.supports_draft else ""
        print(f"  {p.name:12s} {state:48s} [{', '.join(sorted(p.supports))}{draft}]")
    return 0


def publish_container(args: argparse.Namespace, names: list[str], *, live: bool) -> int:
    """Second half of a --draft run: post the container that was staged then."""
    container_id = args.publish_container
    if len(names) != 1:
        print("--publish-container takes exactly one --platform", file=sys.stderr)
        return 2
    try:
        pub = config.get_publisher(names[0])
    except KeyError as exc:
        print(exc.args[0], file=sys.stderr)
        return 2
    if not hasattr(pub, "publish_container"):
        print(f"{pub.name} has no staged-container concept", file=sys.stderr)
        return 2
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

    # Record it when the source directory is known. Without this the container
    # goes live and nothing says so, and the next plain --yes run over the same
    # directory would happily publish it a second time.
    if args.source:
        try:
            post, receipt_dir = build_post(args)
        except RunnerError:
            receipt_dir = None
        if receipt_dir:
            receipts.record(receipt_dir, result, post.content_hash())
            print(f"Receipt: {receipts.path_for(receipt_dir)}")
    else:
        print(
            "  No source directory given, so no receipt was written — pass the "
            "output dir alongside --publish-container to keep posted.json honest."
        )
    return 0


def check(names: list[str]) -> int:
    rc = 0
    for name in names:
        try:
            pub = config.get_publisher(name)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
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


# ── main ────────────────────────────────────────────────────────────────────


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_publishers()

    if args.list_platforms:
        return list_platforms()

    if not args.platform:
        print("missing --platform. Use --list-platforms to see options.", file=sys.stderr)
        return 2

    names = [n.strip() for n in args.platform.split(",") if n.strip()]

    if args.check:
        return check(names)

    if args.publish_container:
        return publish_container(args, names, live=args.yes and not args.dry_run)

    try:
        post, receipt_dir = build_post(args)
    except RunnerError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    live = args.yes and not args.dry_run
    content_hash = post.content_hash()
    if not live:
        print("DRY RUN — nothing will be sent. Add --yes to publish for real.\n")

    published: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []

    for name in names:
        try:
            pub = config.get_publisher(name)
        except KeyError as exc:
            print(f"✗ {exc.args[0]}", file=sys.stderr)
            failed.append(name)
            continue

        # The user asked for a draft. If this platform has no draft concept,
        # quietly publishing live would betray that intent — skip instead.
        if args.draft and not pub.supports_draft:
            print(f"— {pub.name}: skipped, no draft support (drop --draft to publish live)")
            skipped.append(name)
            continue
        draft = args.draft

        violations = pub.preflight(post, draft=draft)
        blocking = [v for v in violations if v.severity == "block"]
        for v in violations:
            print(f"    {v}")
        if blocking:
            print(f"✗ {pub.name}: {len(blocking)} blocking issue(s) — not sent", file=sys.stderr)
            failed.append(name)
            continue

        print(preview(post, pub, draft=draft))

        # Both of these decide the outcome, so a dry run has to evaluate them
        # too — a preview that says "would proceed" about a post that is
        # already out, or that would die on a missing token, is worse than no
        # preview at all.
        prior = (
            receipts.find_blocking(receipt_dir, pub.name, content_hash, drafting=draft)
            if receipt_dir and not args.force
            else None
        )
        if prior:
            what = "staged as a draft" if prior.state == "draft" else prior.state
            print(
                f"— {pub.name}: skipped, identical content already {what} "
                f"at {prior.published_at} ({prior.permalink or 'no permalink'}). Use --force."
            )
            skipped.append(name)
            continue

        if not pub.available():
            print(f"✗ {pub.name}: missing env: {', '.join(pub.missing_env())}", file=sys.stderr)
            failed.append(name)
            continue

        if not pub.token_ready():
            print(
                f"✗ {pub.name}: not authorised. "
                f"Run: python3 -m common.runners.cli.auth --platform {pub.name}",
                file=sys.stderr,
            )
            failed.append(name)
            continue

        if not live:
            continue

        verb = "Create draft on" if draft else "PUBLISH to"
        if not ask(f"{verb} {pub.name}?"):
            print(f"— {pub.name}: declined")
            skipped.append(name)
            continue

        try:
            result = pub.publish(post, draft=draft)
        except (PublishError, RunnerError) as exc:
            print(f"✗ {pub.name}: {exc}", file=sys.stderr)
            failed.append(name)
            continue

        print(f"✓ {result.display()}")
        if receipt_dir:
            receipts.record(receipt_dir, result, content_hash)
        published.append(name)

    print()
    if not live:
        ready = len(names) - len(failed) - len(skipped)
        print(
            f"Dry run complete — {ready} of {len(names)} platform(s) would proceed "
            f"({len(skipped)} skipped, {len(failed)} blocked). Add --yes to publish."
        )
        return 1 if failed else 0

    print(f"Published: {len(published)} · skipped: {len(skipped)} · failed: {len(failed)}")
    if receipt_dir and published:
        print(f"Receipt: {receipts.path_for(receipt_dir)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
