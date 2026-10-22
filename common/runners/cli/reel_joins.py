"""The joins of a cut, checked: what carries the viewer across each cut, and where nothing does.

  python3 -m common.runners.cli.reel_joins --plan-file <dir>/plan.json [--sheet] [--from LABEL] [--to LABEL]

Prints the plan's join warnings (common/runners/cut_joins.py: a new scene or a jump in time on a plain cut, a
bridge played in part, a jump cut). --sheet also reads the picture the cut was last built from (the kept parts
named in <out>/trailer.picture.json): for each cut it takes the last frame of one shot and the first of the
next, measures how far apart they are in light and colour, and draws them side by side, warnings in red, into
<out>/joins/sheet-NN.jpg (12 cuts a sheet), with the numbers in <out>/joins/joins.json. A plain cut whose two
frames are almost wholly apart in light and colour is reported as a jolt. Nothing is generated and nothing is paid for.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .. import cut_joins, shot_matrix

PER_SHEET = 12
WIDTH = 360  # one frame on the sheet
JOLT = 0.9  # colour-and-light distance (0..1) above which a plain cut reads as a jolt; below it, a cut is a cut
_EDGE = {"cut": 0.04}  # how far inside a part its edge frame is taken; past a transition's half otherwise
_PAST_TRANSITION = 0.45


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_joins")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--sheet", action="store_true", help="measure and draw every cut from the kept parts")
    parser.add_argument("--from", dest="start", default=None, help="first shot label of the stretch to draw")
    parser.add_argument("--to", dest="end", default=None, help="last shot label of the stretch to draw")
    return parser


def _parts(out: Path) -> list[tuple[str, Path]]:
    """(label, part file) of every clip and still the cut was last built from, in clock order."""
    from ._animatic_parts import _code, _hash

    signature = json.loads((out / "trailer.picture.json").read_text(encoding="utf-8"))
    home = out / "parts"
    return [(label, home / f"{_hash([key, _code()])}.mp4") for label, key in signature["parts"]
            if not label.startswith("card ") and " freeze" not in label]


def _length(path: Path) -> float:
    run = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(path)], capture_output=True, text=True, check=True)
    return float(run.stdout.strip())


def _frame(part: Path, at: float, dest: Path) -> Path:
    """The frame `at` seconds into the part; a negative `at` counts back from its end."""
    if not dest.is_file() or dest.stat().st_mtime < part.stat().st_mtime:
        seek = ["-sseof", f"{at:.3f}"] if at < 0 else ["-ss", f"{at:.3f}"]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *seek, "-i", str(part),
                        "-frames:v", "1", "-vf", f"scale={WIDTH}:-2,format=yuvj420p", str(dest)], check=True)
    return dest


def _distance(a: Path, b: Path) -> dict[str, float]:
    """How far two frames are apart: mean light (0..1) and a colour histogram distance (0..1), and the two
    combined."""
    import numpy as np
    from PIL import Image

    def stats(p: Path):
        img = np.asarray(Image.open(p).convert("HSV").resize((64, 36)), dtype=float) / 255
        hist, _, _ = np.histogram2d(img[..., 0].ravel(), img[..., 1].ravel(), bins=8, range=[[0, 1], [0, 1]])
        return img[..., 2].mean(), hist / hist.sum()

    (la, ha), (lb, hb) = stats(a), stats(b)
    light, colour = abs(la - lb), 0.5 * float(np.abs(ha - hb).sum())
    return {"light": round(light, 3), "colour": round(colour, 3), "apart": round(min(1.0, 2 * light + colour), 3)}


def _measure(plan: dict[str, Any], out: Path, into: dict[str, str]) -> list[dict[str, Any]]:
    shots = {s["label"]: s for s in cut_joins.live(plan)}
    frames, parts, cuts = out / "joins" / "frames", _parts(out), []
    frames.mkdir(parents=True, exist_ok=True)
    for (a, pa), (b, pb) in zip(parts, parts[1:]):
        kind = into.get(b) or "cut"
        inset = _EDGE.get(kind, _PAST_TRANSITION)
        last = _frame(pa, -max(min(inset, _length(pa) / 2), 0.1), frames / f"{a}.last.jpg")
        first = _frame(pb, min(inset, _length(pb) / 2), frames / f"{b}.first.jpg")
        sa, sb = shots.get(a, {}), shots.get(b, {})
        cut = {"from": a, "to": b, "into": kind, "scene": [sa.get("scene"), sb.get("scene")],
               "last": str(last), "first": str(first), **_distance(last, first)}
        if kind == "cut" and cut["apart"] > JOLT:
            cut["jolt"] = True
        cuts.append(cut)
    return cuts


def _draw(cuts: list[dict[str, Any]], problems: list[str], out: Path) -> list[Path]:
    from PIL import Image, ImageDraw

    sheets, h = [], round(WIDTH * 9 / 16)
    for n in range(0, len(cuts), PER_SHEET):
        page = cuts[n:n + PER_SHEET]
        sheet = Image.new("RGB", (WIDTH * 2 + 520, (h + 8) * len(page)), "white")
        pen = ImageDraw.Draw(sheet)
        for row, cut in enumerate(page):
            y = row * (h + 8)
            for col, key in enumerate(("last", "first")):
                sheet.paste(Image.open(cut[key]).resize((WIDTH, h)), (col * WIDTH, y))
            said = [p for p in problems if cut["from"] in p.split(" ")[0:3] or p.startswith(cut["to"] + ":")]
            bad = said or cut.get("jolt")
            text = [f"{cut['from']} → {cut['to']}   [{cut['into']}]   scene {cut['scene'][0]}→{cut['scene'][1]}",
                    f"apart {cut['apart']}  (light {cut['light']}, colour {cut['colour']})"
                    + ("   JOLT" if cut.get("jolt") else "")] + [p.split(": ", 1)[-1][:70] for p in said]
            pen.multiline_text((WIDTH * 2 + 12, y + 8), "\n".join(text), fill="red" if bad else "black", spacing=6)
        path = out / "joins" / f"sheet-{n // PER_SHEET + 1:02d}.jpg"
        sheet.save(path, quality=85)
        sheets.append(path)
    return sheets


def _stretch(cuts: list[dict[str, Any]], start: str | None, end: str | None) -> list[dict[str, Any]]:
    labels = [c["from"] for c in cuts]
    i = labels.index(start) if start in labels else 0
    j = labels.index(end) + 1 if end in labels else len(cuts)
    return cuts[i:j]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    into = shot_matrix.transitions(plan)
    speeds = {s["label"]: shot_matrix.speed(s, plan) for s in cut_joins.live(plan)}
    problems = cut_joins.join_problems(plan, into, speeds)
    for problem in problems:
        print(f"  join: {problem}")
    print(f"Joins: {len(problems)} warning(s) from the plan.")
    if not args.sheet:
        return 0
    out = args.plan_file.parent
    cuts = _measure(plan, out, into)
    (out / "joins" / "joins.json").write_text(json.dumps(cuts, ensure_ascii=False, indent=1), encoding="utf-8")
    for cut in cuts:
        if cut.get("jolt"):
            print(f"  jolt: {cut['from']} → {cut['to']}, apart {cut['apart']}")
    for sheet in _draw(_stretch(cuts, args.start, args.end), problems, out):
        print(f"Sheet: {sheet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
