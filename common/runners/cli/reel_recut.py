"""reel-recut CLI — finished reels out of talking-head footage that already exists.

  takes   which clips are takes of the same thing, and lines said twice   (free)
  check   validate a plan and print each episode's cuts and captions      (free)
  build   render episodes and their covers
  covers  render covers only
  sheet   contact sheets of the finished reels, for review

Nothing here calls a paid API. Transcripts come from `transcribe --words`,
cutaways and music from the generation skills; this CLI only edits.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .. import recut_build, recut_cover, recut_layers, recut_plan
from .. import recut_timeline as tl


def _load(args: argparse.Namespace) -> recut_plan.Plan | None:
    """The plan, or None after printing why it cannot be built."""
    if not args.plan_file.is_file():
        print(f"  ✗ plan not found: {args.plan_file}", file=sys.stderr)
        return None
    plan = recut_plan.load(args.plan_file)
    found = recut_plan.problems(plan)
    for problem in found:
        print(f"  ✗ {problem}", file=sys.stderr)
    return None if found else plan


def _chosen(plan: recut_plan.Plan, only: list[int] | None) -> list[dict]:
    return [ep for ep in plan.episodes if not only or ep["n"] in only]


def _chrome() -> str | None:
    chrome = recut_layers.find_chrome()
    if chrome is None:
        print("  ✗ Chrome or Chromium not found — it renders the graphics. Install one or set $CHROME.", file=sys.stderr)
    return chrome


def _cmd_takes(args: argparse.Namespace) -> int:
    files = sorted(args.words.glob("*.json"))
    if not files:
        print(f"  ✗ no transcripts (*.json) in {args.words}", file=sys.stderr)
        return 2
    loaded = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in files}
    groups = tl.duplicate_takes({name: data.get("text", "") for name, data in loaded.items()})
    print(f"# {len(files)} clip(s), {len(groups)} group(s) of duplicate takes")
    for group in groups:
        sizes = ", ".join(f"{name} ({len(loaded[name].get('text', ''))} chars)" for name in group)
        print(f"  same content, fullest first: {sizes}")
    for name, data in loaded.items():
        for first, second, phrase in tl.repeated_lines(data.get("words", [])):
            print(f"  {name}: «{phrase}» said at {first:.2f}s and again at {second:.2f}s — cut [{first:.2f}, {second:.2f}]")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    plan = _load(args)
    if plan is None:
        return 2
    for ep in _chosen(plan, args.only):
        info = recut_build.report(recut_build.decide(plan, ep))
        print(f"\n[{info['n']:02d}] {info['slug']}  {info['seconds']:.1f}s (speech {info['speech']:.1f}s)")
        print(f"  removed: {info['removed']}")
        print(f"  framing: {' '.join(f'{mode}@{a}' for a, _b, mode in info['framing'])}")
        print(f"  captions: {' | '.join(info['captions'])}")
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    plan, chrome = _load(args), _chrome()
    if plan is None or chrome is None:
        return 2
    failed = 0
    for ep in _chosen(plan, args.only):
        try:
            out = recut_build.build(plan, ep, chrome, preview=args.preview)
            print(f"  ✓ [{ep['n']:02d}] {out}", file=sys.stderr)
            if not args.no_cover:
                print(f"  ✓ [{ep['n']:02d}] {recut_cover.cover(plan, ep, chrome)}", file=sys.stderr)
        except RuntimeError as exc:
            failed += 1
            print(f"  ✗ [{ep['n']:02d}] {exc}", file=sys.stderr)
    print(str(plan.out))
    return 1 if failed else 0


def _cmd_covers(args: argparse.Namespace) -> int:
    plan, chrome = _load(args), _chrome()
    if plan is None or chrome is None:
        return 2
    for ep in _chosen(plan, args.only):
        print(str(recut_cover.cover(plan, ep, chrome)))
    return 0


def _cmd_sheet(args: argparse.Namespace) -> int:
    plan = _load(args)
    if plan is None:
        return 2
    out_dir = args.out_dir or plan.work / "sheets"
    for ep in _chosen(plan, args.only):
        video = plan.out / f"{ep['slug']}.mp4"
        if not video.is_file():
            print(f"  · [{ep['n']:02d}] not built yet", file=sys.stderr)
            continue
        seconds = recut_build.duration_of(video)
        print(str(recut_cover.contact_sheet(video, out_dir / f"{ep['slug']}.jpg", seconds)))
    return 0


def _plan_command(sub, name: str, helptext: str, func) -> argparse.ArgumentParser:
    parser = sub.add_parser(name, help=helptext)
    parser.add_argument("--plan-file", type=Path, required=True, help="the edit plan (plan.json)")
    parser.add_argument("--only", type=int, nargs="+", help="episode numbers; default all")
    parser.set_defaults(func=func)
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="common.runners.cli.reel_recut",
        description="Re-edit existing talking-head clips into finished vertical reels.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    takes = sub.add_parser("takes", help="find duplicate takes and lines said twice")
    takes.add_argument("--words", type=Path, required=True, help="folder of word-level transcripts (*.json)")
    takes.set_defaults(func=_cmd_takes)

    _plan_command(sub, "check", "validate the plan; print cuts, framing and captions", _cmd_check)
    build = _plan_command(sub, "build", "render episodes and covers", _cmd_build)
    build.add_argument("--preview", action="store_true", help="fast low-quality encode for review")
    build.add_argument("--no-cover", action="store_true", help="skip the covers")
    _plan_command(sub, "covers", "render covers only", _cmd_covers)
    sheet = _plan_command(sub, "sheet", "contact sheets of the finished reels", _cmd_sheet)
    sheet.add_argument("--out-dir", type=Path, help="where the sheets go (default <work>/sheets)")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
