"""The matrix of takes: every paid render of a film, by shot, with what it shows and whether the edit can reuse it.

  python3 -m common.runners.cli.reel_takes --plan-file <dir>/plan.json [--history <plan copy> ...] [--sheet]
      [--set <file> status=rejected reason="..."] [--usable <file> 1.0-3.4,5-6]

Fills in <out>/takes.json (see common/runners/take_ledger.py: time, length, prompt, size, move, status,
usable windows), prints the takes grouped by shot and writes <out>/takes.md. --history adds saved copies of the
plan to read an old take's body from (<out>/plan.json.bak and <out>/plan.*.json are always read). --set
writes key=value fields on one take (status, reason, content, size, move); --usable gives its windows.
--sheet draws a 5-frame strip per alternate or rejected take into <out>/takes/<stem>.jpg and stacks them into
<out>/takes/contact.jpg; a strip newer than its clip is never drawn again. Every alternate is printed with the
reel_insert entry that puts it in the cut as a clip shot. Nothing is generated and nothing is paid for.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .. import take_ledger as tl

FRAMES = 5
WIDTH = 192  # one frame of a strip


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_takes")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--history", type=Path, nargs="*", default=[], help="saved copies of the plan")
    parser.add_argument("--set", nargs="+", action="append", default=[], metavar="FILE KEY=VALUE",
                        help="<file> key=value ...; repeatable")
    parser.add_argument("--usable", nargs=2, action="append", default=[], metavar=("FILE", "WINDOWS"))
    parser.add_argument("--sheet", action="store_true", help="draw strips and a contact sheet of the unused takes")
    return parser


def _history(plan_file: Path, extra: list[Path]) -> list[tuple[str, dict[str, Any], float]]:
    out = plan_file.parent
    paths = [p for p in [out / "plan.json.bak", *sorted(out.glob("plan.*.json")), *extra] if p.is_file()]
    return [(p.name, json.loads(p.read_text(encoding="utf-8")), p.stat().st_mtime) for p in dict.fromkeys(paths)]


def _edit(ledger: list[dict[str, Any]], args: argparse.Namespace) -> None:
    for file, *pairs in args.set:
        tl.set_fields(tl.find(ledger, file), pairs)
    for file, text in args.usable:
        tl.find(ledger, file)["usable"] = tl.windows(text)


def _row(t: dict[str, Any]) -> str:
    move = (t.get("move") or "")[:40].replace("|", "/")
    return (f"| {Path(t['file']).name} | {t.get('created') or ''} | {t.get('size', '?')} | {move} | "
            f"{t.get('duration') or '?'} | {t.get('status')} | {t.get('reason') or ''} | {t.get('content') or ''} |")


def _summary(ledger: list[dict[str, Any]]) -> str:
    count = {k: sum(t.get("status") == k for t in ledger) for k in ("in cut", "alternate", "rejected")}
    spent = sum(float(t.get("cost_usd") or 0) for t in ledger)
    return (f"\n{len(ledger)} takes, ${spent:.2f}; in cut {count['in cut']}, alternates {count['alternate']}, "
            f"rejected {count['rejected']}.")


def table(ledger: list[dict[str, Any]], labels: list[str]) -> str:
    """Takes grouped by shot label, oldest first; then the reel_insert entry for every alternate."""
    head = "| file | created | size | move | s | status | reason | content |\n|" + "---|" * 8
    out = []
    for label in sorted({t["label"] for t in ledger}):
        mine = sorted((t for t in ledger if t["label"] == label), key=lambda t: t.get("created") or "")
        out += [f"\n### {label}\n", head, *map(_row, mine)]
    out.append(_summary(ledger))
    alts = [t for t in ledger if t.get("status") == "alternate"]
    if alts:
        out.append("\nReuse an alternate: paste its entry into a reel_insert file (insert_after: where it goes).\n")
        out += [f"- `{json.dumps(tl.insert_entry(t, labels), ensure_ascii=False)}`" for t in alts]
    return "\n".join(out)


def _ffmpeg(*args: str) -> bool:
    return subprocess.run(["ffmpeg", "-v", "error", "-y", *args], capture_output=True, check=False).returncode == 0


def strip(clip: Path, jpg: Path, seconds: float) -> bool:
    """FRAMES frames spread over the take, side by side; skipped when the strip is newer than the clip."""
    if jpg.is_file() and jpg.stat().st_mtime >= clip.stat().st_mtime:
        return True
    jpg.parent.mkdir(parents=True, exist_ok=True)
    rate = FRAMES / max(seconds, 0.5)
    return _ffmpeg("-i", str(clip), "-vf", f"fps={rate:.4f},scale={WIDTH}:-2,tile={FRAMES}x1",
                   "-frames:v", "1", "-q:v", "4", str(jpg))


def _fresh(strips: list[Path], jpg: Path, names: str) -> bool:
    listing = jpg.with_suffix(".txt")
    if not (jpg.is_file() and listing.is_file()) or listing.read_text(encoding="utf-8") != names:
        return False
    return all(s.stat().st_mtime <= jpg.stat().st_mtime for s in strips)


def contact(strips: list[Path], jpg: Path) -> bool:
    """The strips stacked, top to bottom; skipped when nothing changed since it was drawn."""
    names = "\n".join(s.name for s in strips)
    if not strips or _fresh(strips, jpg, names):
        return bool(strips)
    inputs = [x for s in strips for x in ("-i", str(s))]
    graph = "".join(f"[{i}:v]" for i in range(len(strips))) + f"vstack=inputs={len(strips)}"
    ok = _ffmpeg(*inputs, "-filter_complex", graph if len(strips) > 1 else "null", "-q:v", "4", str(jpg))
    if ok:
        jpg.with_suffix(".txt").write_text(names, encoding="utf-8")
    return ok


def sheet(ledger: list[dict[str, Any]], out: Path) -> Path:
    """Strips of every alternate and rejected take, and their contact sheet, in clock order of the takes."""
    unused = sorted((t for t in ledger if t.get("status") != "in cut" and (out / t["file"]).is_file()),
                    key=lambda t: (t["label"], t.get("created") or ""))
    strips = []
    for t in unused:
        jpg = out / "takes" / f"{Path(t['file']).stem}.jpg"
        if strip(out / t["file"], jpg, float(t.get("duration") or 4)):
            strips.append(jpg)
    contact(strips, out / "takes" / "contact.jpg")
    return out / "takes" / "contact.jpg"


def main() -> int:
    args = build_parser().parse_args()
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    plan.setdefault("output_dir", str(args.plan_file.parent))
    out = Path(plan["output_dir"])
    ledger = tl.backfill(plan, json.loads((out / "takes.json").read_text(encoding="utf-8"))
                         if (out / "takes.json").is_file() else [], _history(args.plan_file, args.history))
    try:
        _edit(ledger, args)
    except (KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    (out / "takes.json").write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    text = table(ledger, [s["label"] for s in plan["shots"] if not s.get("cut")])
    (out / "takes.md").write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.sheet:
        print(f"Contact sheet: {sheet(ledger, out)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
