"""CLI entry: JSON-LD structured data and llms.txt.

Reads a markdown post — the same file `cli.origin` writes — and emits the
schema block to paste into the page head.

The FAQPage extraction is where this pays for itself. The AEO linter already
pushes headings into question form; this turns those headings and the paragraph
under each into Q&A pairs, so the structure that helps a human scan is the same
structure an engine quotes. No second authoring pass.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from ..schema_ld import (
    ArticleMeta,
    Author,
    LlmsSection,
    SchemaError,
    article,
    faq_page,
    llms_txt,
    organization,
    render,
)

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_HEADING = re.compile(r"^(#{2,3})\s+(.*)$")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Minimal YAML frontmatter reader — scalars and inline lists only.

    A real YAML parser is not a dependency worth adding for four keys, and the
    frontmatter this reads is the frontmatter `cli.origin` writes.
    """
    match = _FRONTMATTER.match(text)
    if not match:
        return {}, text
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields, text[match.end():]


def extract_faq(body: str, *, limit: int = 10) -> list[tuple[str, str]]:
    """Question-form headings plus the first paragraph under each."""
    pairs: list[tuple[str, str]] = []
    current: str | None = None
    buffer: list[str] = []

    def close() -> None:
        nonlocal current, buffer
        if current and buffer:
            pairs.append((current, " ".join(buffer).strip()))
        current, buffer = None, []

    for raw in body.splitlines():
        heading = _HEADING.match(raw)
        if heading:
            close()
            text = heading.group(2).strip()
            current = text if text.rstrip().endswith("?") else None
            continue
        if current is None:
            continue
        if not raw.strip():
            if buffer:
                close()
            continue
        buffer.append(raw.strip())
    close()
    return pairs[:limit]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="schema",
        description="Generate JSON-LD structured data, or an llms.txt file.",
    )
    p.add_argument("--from", dest="source", type=Path, help="markdown post to read")
    p.add_argument("--types", default="article,faq", help="article,faq,organization")
    p.add_argument("--url", default="", help="canonical URL of the page")
    p.add_argument("--title", default="", help="override the frontmatter title")
    p.add_argument("--description", default="")
    p.add_argument("--author-name", default="")
    p.add_argument("--author-url", default="")
    p.add_argument("--knows-about", default="", help="comma-separated topics for the author entity")
    p.add_argument("--same-as", default="", help="comma-separated profile URLs")
    p.add_argument("--publisher-name", default="")
    p.add_argument("--publisher-url", default="")
    p.add_argument("--date-modified", default="", help="ISO date; defaults to datePublished")
    p.add_argument("--raw", action="store_true", help="omit the <script> wrapper")
    p.add_argument("--llms-txt", action="store_true", help="render an llms.txt instead")
    p.add_argument("--site-name", default="", help="llms.txt: site name")
    p.add_argument("--site-summary", default="", help="llms.txt: one-line summary")
    return p


def _tuple(value: str) -> tuple[str, ...]:
    return tuple(v.strip() for v in value.split(",") if v.strip())


def _llms(args: argparse.Namespace) -> int:
    if not args.site_name or not args.site_summary:
        print("--llms-txt needs --site-name and --site-summary", file=sys.stderr)
        return 2
    section = LlmsSection(title="Docs", links=[])
    if args.url:
        section.links.append((args.site_name, args.url, "home"))
    sys.stdout.write(
        llms_txt(
            name=args.site_name,
            summary=args.site_summary,
            sections=[section] if section.links else [],
            details=(
                "Note: llms.txt is a community convention. No major engine has "
                "committed to reading it in production, so treat it as tidy "
                "infrastructure rather than a ranking lever."
            ),
        )
    )
    return 0


def _nodes(args, fields: dict[str, str], body: str, title: str, author) -> list[dict]:
    """Assemble the requested schema nodes."""
    wanted = _tuple(args.types)
    nodes: list[dict] = []

    if "article" in wanted:
        nodes.append(
            article(
                ArticleMeta(
                    headline=title,
                    description=args.description or fields.get("description", ""),
                    url=args.url,
                    date_published=fields.get("date", ""),
                    date_modified=args.date_modified,
                    author=author,
                    publisher_name=args.publisher_name,
                    publisher_url=args.publisher_url,
                    keywords=_tuple(fields.get("tags", "").strip("[]")),
                )
            )
        )

    if "faq" in wanted:
        pairs = extract_faq(body)
        if pairs:
            nodes.append(faq_page(pairs))
        else:
            print(
                "note: no question-form headings found — no FAQPage emitted. "
                "Question headings are what engines quote; see writer --aeo.",
                file=sys.stderr,
            )

    if "organization" in wanted and args.publisher_name and args.publisher_url:
        nodes.append(organization(args.publisher_name, args.publisher_url))
    return nodes


def main() -> int:
    args = build_parser().parse_args()

    if args.llms_txt:
        return _llms(args)

    fields: dict[str, str] = {}
    body = ""
    if args.source:
        if not args.source.is_file():
            print(f"not found: {args.source}", file=sys.stderr)
            return 2
        fields, body = parse_frontmatter(args.source.read_text(encoding="utf-8"))

    title = args.title or fields.get("title", "")
    if not title:
        print("need a title — pass --title or a markdown file with frontmatter", file=sys.stderr)
        return 2

    author = None
    if args.author_name:
        author = Author(
            name=args.author_name,
            url=args.author_url,
            knows_about=_tuple(args.knows_about),
            same_as=_tuple(args.same_as),
        )

    try:
        nodes = _nodes(args, fields, body, title, author)
        if not nodes:
            print("nothing to emit for --types " + args.types, file=sys.stderr)
            return 2
        print(render(nodes, script_tag=not args.raw))
    except SchemaError as exc:
        print(f"schema error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
