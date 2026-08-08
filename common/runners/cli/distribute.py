"""CLI entry: submission packets for directories and registries.

Renders only. Every directory here is an outward-facing, hard-to-reverse
submission, and several of them (awesome-claude-code most explicitly) require a
human to fill the form — automating the send would risk a ban. So this prepares
the material and stops.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import directories

ROOT = Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="distribute",
        description="Write submission packets for directories, registries and curated lists.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("./generated/distribution"),
        help="output directory (default ./generated/distribution)",
    )
    p.add_argument(
        "--only",
        help=f"comma-separated subset. Known: {', '.join(directories.SPECS)}",
    )
    p.add_argument("--list", action="store_true", help="show the directories and exit")
    p.add_argument("--root", type=Path, default=ROOT, help="repo root to read project facts from")
    return p


def _list() -> int:
    width = max(len(s.slug) for s in directories.SPECS.values())
    for slug in directories.DEFAULT_ORDER:
        spec = directories.SPECS[slug]
        print(f"  {spec.slug:<{width}}  {spec.link:<9}  {spec.label}")
        print(f"  {'':<{width}}  {'':<9}  {spec.route}")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if args.list:
        return _list()

    chosen = directories.DEFAULT_ORDER
    if args.only:
        chosen = tuple(s.strip() for s in args.only.split(",") if s.strip())

    try:
        written = directories.write_packets(args.root, args.out, directories=chosen)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"cannot read project facts: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote {len(written)} packet(s) to {args.out}:")
    for path in written:
        print(f"  {path.name}")
    print("\nNothing was submitted. Each of these is a manual, one-time submission —")
    print("awesome-claude-code in particular bans automated ones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
