#!/usr/bin/env python3
"""
gen-skill-index.py — generate docs/SKILL-INDEX.md from skills.json.

Index groups all skills by layer, then by domain tag, then lists languages.
Also produces a "by language" cross-reference section.

Usage:
    python3 scripts/gen-skill-index.py            # print to stdout
    python3 scripts/gen-skill-index.py --write    # update SKILL-INDEX.md in place
    python3 scripts/gen-skill-index.py --check    # exit 1 if SKILL-INDEX.md out of date

Markers in docs/SKILL-INDEX.md:
    <!-- BEGIN skill-index (auto-generated; run `make gen-index`) -->
    <!-- END skill-index -->

Closed tag dictionary (validated by scripts/validate.sh):
    Domain tags:  fiction, non-fiction, marketing, social, product, tech-docs,
                  ux-copy, visual, outreach
    Function:     editing, generation, audit, translation, ops
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills.json"
INDEX = ROOT / "docs" / "SKILL-INDEX.md"

BEGIN = "<!-- BEGIN skill-index (auto-generated; run `make gen-index`) -->"
END = "<!-- END skill-index -->"

LAYER_ORDER = ["base", "wrapper", "linter", "meta"]
LAYER_HEADINGS = {
    "base": "Base",
    "wrapper": "Wrappers",
    "linter": "Linters (read-only)",
    "meta": "Meta",
}

DOMAIN_TAGS = {
    "fiction", "non-fiction", "marketing", "social", "product",
    "tech-docs", "ux-copy", "visual", "outreach",
}
FUNCTION_TAGS = {"editing", "generation", "audit", "translation", "ops"}
ALLOWED_TAGS = DOMAIN_TAGS | FUNCTION_TAGS


def render_layer_section(skills: list[dict]) -> str:
    out: list[str] = []
    out.append("## By layer\n")
    by_layer: dict[str, list[dict]] = {}
    for s in skills:
        by_layer.setdefault(s.get("layer", "?"), []).append(s)
    for layer in LAYER_ORDER:
        if layer not in by_layer:
            continue
        out.append(f"### {LAYER_HEADINGS[layer]}\n")
        out.append("| Skill | Tags | Languages |")
        out.append("| --- | --- | --- |")
        for s in by_layer[layer]:
            name = s["name"]
            dir_ = s["dir"]
            tags = ", ".join(s.get("tags", [])) or "—"
            langs = " / ".join(s.get("languages", []))
            out.append(f"| [`{name}`](../{dir_}/) | {tags} | {langs} |")
        out.append("")
    return "\n".join(out)


def render_domain_section(skills: list[dict]) -> str:
    out: list[str] = []
    out.append("## By domain\n")
    by_domain: dict[str, list[dict]] = {}
    for s in skills:
        for t in s.get("tags", []):
            if t in DOMAIN_TAGS:
                by_domain.setdefault(t, []).append(s)
    for domain in sorted(by_domain):
        names = ", ".join(f"[`{s['name']}`](../{s['dir']}/)" for s in by_domain[domain])
        out.append(f"- **{domain}** — {names}")
    out.append("")
    return "\n".join(out)


def render_language_section(skills: list[dict]) -> str:
    by_lang: dict[tuple[str, ...], list[dict]] = {}
    for s in skills:
        key = tuple(sorted(s.get("languages", [])))
        by_lang.setdefault(key, []).append(s)
    out: list[str] = []
    out.append("## By language\n")
    for key in sorted(by_lang, key=lambda k: (-len(k), k)):
        label = " + ".join(k.upper() for k in key) or "—"
        names = ", ".join(f"[`{s['name']}`](../{s['dir']}/)" for s in by_lang[key])
        out.append(f"- **{label}** ({len(by_lang[key])}) — {names}")
    out.append("")
    return "\n".join(out)


def render_block(manifest: dict) -> str:
    skills = manifest["skills"]
    body = "\n\n".join([
        render_layer_section(skills).rstrip(),
        render_domain_section(skills).rstrip(),
        render_language_section(skills).rstrip(),
    ])
    return f"{BEGIN}\n\n{body}\n\n{END}\n"


def replace_block(index_text: str, new_block: str) -> str | None:
    pattern = re.compile(
        re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?",
        re.DOTALL,
    )
    if not pattern.search(index_text):
        return None
    return pattern.sub(new_block, index_text)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--write", action="store_true", help="update SKILL-INDEX.md in place")
    p.add_argument("--check", action="store_true", help="exit 1 if SKILL-INDEX.md is out of date")
    args = p.parse_args(argv)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rendered = render_block(manifest)

    if args.check:
        if not INDEX.exists():
            print(f"ERROR: {INDEX} does not exist. Run `make gen-index`.", file=sys.stderr)
            return 2
        index_text = INDEX.read_text(encoding="utf-8")
        updated = replace_block(index_text, rendered)
        if updated is None:
            print(
                f"ERROR: {INDEX} is missing BEGIN/END markers.",
                file=sys.stderr,
            )
            return 2
        if updated != index_text:
            print(
                "ERROR: docs/SKILL-INDEX.md is out of date.\n"
                "Regenerate with: python3 scripts/gen-skill-index.py --write\n"
                "Or: make gen-index",
                file=sys.stderr,
            )
            return 1
        print("docs/SKILL-INDEX.md is up to date.")
        return 0

    if args.write:
        if not INDEX.exists():
            # Bootstrap a fresh file with markers + the block
            INDEX.parent.mkdir(parents=True, exist_ok=True)
            INDEX.write_text(
                _bootstrap_header() + rendered,
                encoding="utf-8",
            )
            print(f"Created {INDEX}")
            return 0
        index_text = INDEX.read_text(encoding="utf-8")
        updated = replace_block(index_text, rendered)
        if updated is None:
            print(
                f"ERROR: {INDEX} is missing BEGIN/END markers — refusing to write.",
                file=sys.stderr,
            )
            return 2
        if updated != index_text:
            INDEX.write_text(updated, encoding="utf-8")
            print(f"Updated {INDEX}")
        else:
            print(f"{INDEX} already up to date — no changes.")
        return 0

    print(rendered, end="")
    return 0


def _bootstrap_header() -> str:
    return (
        "# Skill index\n\n"
        "Auto-generated map of every skill in the collection — by layer, by\n"
        "domain, and by supported language. The body between the markers below\n"
        "is regenerated from `skills.json` by `python3 scripts/gen-skill-index.py\n"
        "--write` (or `make gen-index`).\n\n"
        "For scenario-driven discovery (\"I want to write a landing page\"), see\n"
        "[USER-GUIDE.md](USER-GUIDE.md). For workflow recipes (chaining multiple\n"
        "skills), see [COMPOSING.md](COMPOSING.md).\n\n"
    )


if __name__ == "__main__":
    sys.exit(main())
