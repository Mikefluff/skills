"""CLI entry: write the canonical original into a static-site repository.

The first step of a syndication run. Prints the URL the post will have once the
site rebuilds, which is what every later `--canonical` needs.

    python3 -m common.runners.cli.origin --text-file post.md --title "..."
    python3 -m common.runners.cli.publish --kind article --canonical <url> ...

Writes a file and stops. Committing and deploying stay manual — this is somebody's
blog repository, not a build artifact directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path

from ..errors import RunnerError
from ..staticblog import BlogConfig, PostDraft, slugify, write_post


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="origin",
        description="Write the canonical original into a static blog and print its future URL.",
    )
    p.add_argument("--title", required=True)
    p.add_argument("--text-file", type=Path, help="markdown body; '-' reads stdin")
    p.add_argument("--text", help="markdown body inline")
    p.add_argument("--description", default="", help="frontmatter description / SEO excerpt")
    p.add_argument("--tags", default="", help="comma-separated")
    p.add_argument("--slug", help="override the slug derived from the title")
    p.add_argument("--date", help="YYYY-MM-DD (default today)")
    p.add_argument("--draft", action="store_true", help="set the draft flag in frontmatter")
    p.add_argument("--overwrite", action="store_true", help="replace an existing file")
    p.add_argument(
        "--blog-dir",
        type=Path,
        default=os.environ.get("BLOG_CONTENT_DIR"),
        help="content directory (env: BLOG_CONTENT_DIR)",
    )
    p.add_argument(
        "--url-pattern",
        default=os.environ.get("BLOG_URL_PATTERN"),
        help="e.g. https://you.dev/posts/{slug}/ (env: BLOG_URL_PATTERN)",
    )
    p.add_argument(
        "--filename-pattern",
        default=os.environ.get("BLOG_FILENAME_PATTERN", "{slug}.md"),
        help="Hugo/Astro: {slug}.md · Jekyll: {year}-{month}-{day}-{slug}.md",
    )
    p.add_argument(
        "--draft-field",
        default=os.environ.get("BLOG_DRAFT_FIELD", "draft"),
        help="frontmatter key for the draft flag; empty string to omit it",
    )
    p.add_argument("--url-only", action="store_true", help="print just the URL")
    return p


def _body(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if not args.text_file:
        raise RunnerError("need --text-file or --text")
    if str(args.text_file) == "-":
        return sys.stdin.read()
    return args.text_file.read_text(encoding="utf-8")


def _invalid(args: argparse.Namespace) -> str | None:
    """The usage errors, in one place, so main() stays about the happy path."""
    if not args.blog_dir:
        return "missing --blog-dir (or BLOG_CONTENT_DIR)"
    if not args.url_pattern:
        return "missing --url-pattern (or BLOG_URL_PATTERN)"
    if "{slug}" not in args.url_pattern:
        return "--url-pattern must contain {slug}"
    if args.text is None and not args.text_file:
        return "need --text-file or --text"
    return None


def main() -> int:
    args = build_parser().parse_args()

    problem = _invalid(args)
    if problem:
        print(problem, file=sys.stderr)
        return 2

    try:
        draft = PostDraft(
            title=args.title,
            body=_body(args),
            description=args.description,
            tags=tuple(t.strip() for t in args.tags.split(",") if t.strip()),
            when=dt.date.fromisoformat(args.date) if args.date else None,
            slug=args.slug or slugify(args.title),
            draft=args.draft,
        )
    except (RunnerError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    config = BlogConfig(
        content_dir=Path(args.blog_dir).expanduser(),
        url_pattern=args.url_pattern,
        filename_pattern=args.filename_pattern,
        draft_field=args.draft_field or None,
    )

    try:
        drafted = write_post(config, draft, overwrite=args.overwrite)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.url_only:
        print(drafted.url)
        return 0

    print(f"wrote {drafted.path}")
    print(f"url   {drafted.url}")
    print()
    print("Not committed. Review, commit and deploy, then syndicate:")
    print(f"  python3 -m common.runners.cli.publish --kind article \\")
    print(f"    --text-file {args.text_file or '<body>'} --title {args.title!r} \\")
    print(f"    --canonical {drafted.url} --platform devto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
