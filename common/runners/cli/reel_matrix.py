"""The shot matrix of a cut: what every shot is built from, by which route and why, and where it stands.

  python3 -m common.runners.cli.reel_matrix --plan-file <dir>/plan.json [--pin t26=seedance,t41=wan] [--apply]

Prints the matrix and writes it to <out>/matrix.md. --pin fixes a shot's route by
hand (kept over the rules on every rebuild); --apply writes each shot's
video_provider from the matrix into the plan, so reel_cast and reel follow it.
Nothing is generated and nothing is paid for. See common/runners/shot_matrix.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .. import shot_matrix as sm


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_matrix")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--pin", default="", help="label=route pairs (wan, seedance), comma-separated")
    parser.add_argument("--apply", action="store_true", help="write each shot's video_provider from the matrix")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    matrix = plan.setdefault("matrix", {})
    for pair in filter(None, (p.strip() for p in args.pin.split(","))):
        label, route = pair.split("=")
        if route not in sm.ROUTES:
            print(f"unknown route {route!r}; have {', '.join(sm.ROUTES)}", file=sys.stderr)
            return 2
        matrix[label] = {**matrix.get(label, {}), "route": route, "pinned": True, "why": "pinned by hand"}
    rows = sm.build(plan)
    if args.apply or args.pin:
        changed = sm.apply(plan, rows) if args.apply else []
        plan["matrix"] = rows
        args.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if changed:
            print(f"Route changed: {', '.join(changed)}", file=sys.stderr)
    text = sm.table(rows)
    (Path(plan.get("output_dir") or args.plan_file.parent) / "matrix.md").write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
