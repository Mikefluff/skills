#!/usr/bin/env python3
"""
gen-skills-table.py — generate the "What's in the box" markdown table from
skills.json and optionally write it into README.md between the BEGIN/END
markers.

Usage:
    python3 scripts/gen-skills-table.py            # print to stdout
    python3 scripts/gen-skills-table.py --write    # update README.md in place

Markers in README.md:
    <!-- BEGIN skills-table (auto-generated; run `make gen-readme`) -->
    <!-- END skills-table -->

CI uses `--check` mode to fail the build if README.md is out of date:
    python3 scripts/gen-skills-table.py --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills.json"
README = ROOT / "README.md"

BEGIN = "<!-- BEGIN skills-table (auto-generated; run `make gen-readme`) -->"
END = "<!-- END skills-table -->"


def render_table(manifest: dict) -> str:
    rows: list[str] = []
    rows.append("| Skill | Layer | Languages | Purpose |")
    rows.append("| --- | --- | --- | --- |")
    for s in manifest["skills"]:
        name = s["name"]
        dir_ = s["dir"]
        layer = s.get("layer", "?")
        langs = "/".join(s.get("languages", []))
        desc = s.get("description", "").strip()
        # Markdown table cells can't contain literal `|` — escape if any
        desc = desc.replace("|", "\\|")
        rows.append(f"| [`{name}`]({dir_}/) | {layer} | {langs} | {desc} |")
    return "\n".join(rows)


def render_block(manifest: dict) -> str:
    table = render_table(manifest)
    return f"{BEGIN}\n\n{table}\n\n{END}\n"


def replace_block(readme_text: str, new_block: str) -> str:
    pattern = re.compile(
        re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?",
        re.DOTALL,
    )
    if not pattern.search(readme_text):
        # Markers absent — caller should know
        return None  # type: ignore[return-value]
    return pattern.sub(new_block, readme_text)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--write", action="store_true", help="update README.md in place")
    p.add_argument("--check", action="store_true", help="exit 1 if README.md is out of date")
    args = p.parse_args(argv)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rendered = render_block(manifest)

    if args.check:
        readme = README.read_text(encoding="utf-8")
        updated = replace_block(readme, rendered)
        if updated is None:
            print(
                f"ERROR: {README} is missing the BEGIN/END markers.\n"
                f"Add this somewhere in the file:\n\n{BEGIN}\n(table here)\n{END}\n",
                file=sys.stderr,
            )
            return 2
        if updated != readme:
            print(
                "ERROR: README.md skills table is out of date.\n"
                "Regenerate with:\n  python3 scripts/gen-skills-table.py --write\n"
                "Or:\n  make gen-readme",
                file=sys.stderr,
            )
            return 1
        print("README.md skills table is up to date.")
        return 0

    if args.write:
        readme = README.read_text(encoding="utf-8")
        updated = replace_block(readme, rendered)
        if updated is None:
            print(
                f"ERROR: {README} is missing the BEGIN/END markers — refusing to write.\n"
                f"Add this somewhere in the file:\n\n{BEGIN}\n(table here)\n{END}\n",
                file=sys.stderr,
            )
            return 2
        if updated != readme:
            README.write_text(updated, encoding="utf-8")
            print(f"Updated {README}")
        else:
            print(f"{README} already up to date — no changes.")
        return 0

    # Default: print to stdout
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
