"""Storyboard phase of a voiced film — one judged keyframe per shot, before any video.

Direction is decided here, on stills that cost cents, not in a 30-second render
that costs dollars: composition, lens, light and the acting beat of every shot.
Left to itself the video model frames everything centred, evenly lit and medium
— the first trial film did exactly that. Given the approved frames as ordered
references ("Use Images 2-N in order as keyframes"), Seedance 2.5 holds to them.

Each frame is generated (Nano Banana Pro through OpenRouter, with the character
photo and any earlier frames it names as references), then read back by a
vision model against its shot: framing, light, identity, whether it shows the
idea or merely illustrates the line, and whether it reads as cinema or as a
stock photo. A frame that fails is regenerated with
the critic's fix appended, up to --tries times; the best-scoring take is kept.

  python3 -m common.runners.cli.reel_board --plan-file <dir>/plan.json [--tries 3] [--yes]

Reads plan["board"] (written by the film chain), writes <dir>/board/<id>.png and
.jpg, board/board.json (scores, issues, cost) and board/contact.jpg, and hands
the frames to the shots: all of them as keyframes to a one-generation film, or
each to its own shot when every shot is its own generation. Frames
whose spec has not changed are reused, so editing one frame re-rolls only it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import config
from .. import cost as cost_mod
from ..errors import CostConfirmationDeclined, RunnerError

_PROVIDER = "openrouter-nano-banana-pro"
_PASS = 8
_AXES = ("framing", "light", "identity", "idea", "craft", "cinema")

_JUDGE = """You are a film director's eye checking one storyboard frame before it is animated.
Image 1 is the character reference. Image 2 is the frame.

The shot it must be:
{shot}

Must be true: {check}
Identity markers that must match Image 1: {identity}

Score 0-10 each: framing (shot size, angle, placement as specified), light (direction, colour, contrast as specified), identity (same man; markers match; 10 if the shot specifies he is not in frame and he is not), idea (the frame shows the beat's idea through a concrete image, not a literal illustration), craft (no artefacts, extra people, text, bad hands), cinema (reads as a frame grab from a feature film: real location, texture, imperfect optics, caught mid-action — score low for stock or advertising photography, glossy retouched skin, studio backdrop, a posed portrait, a CG render or a person composited into a scene).
Return JSON only:
{{"framing":0,"light":0,"identity":0,"idea":0,"craft":0,"cinema":0,"score":0,"issues":["..."],"fix":"one sentence the image prompt should add to fix the worst issue"}}
score = the minimum of the six."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_board")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--tries", type=int, default=3, help="generations per frame at most (default 3)")
    parser.add_argument("--only", help="comma-separated frame ids to re-roll even if cached")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    return parser


def _spec_hash(frame: dict[str, Any], identity: str) -> str:
    return hashlib.sha256(json.dumps([frame, identity], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


def _jpeg(png: Path) -> Path:
    jpg = png.with_suffix(".jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(png), "-q:v", "3", str(jpg)],
                   check=True, capture_output=True)
    return jpg


def _contact(frames: list[Path], out: Path) -> None:
    if not frames:
        return
    cols = min(len(frames), 5)
    rows = (len(frames) + cols - 1) // cols
    inputs = [arg for f in frames for arg in ("-i", str(f))]
    scaled = "".join(f"[{i}:v]scale=288:512,setsar=1[v{i}];" for i in range(len(frames)))
    pads = "".join(f"color=black:288x512:d=1[p{i}];" for i in range(len(frames), rows * cols))
    labels = "".join(f"[v{i}]" for i in range(len(frames))) + "".join(f"[p{i}]" for i in range(len(frames), rows * cols))
    layout = "|".join(f"{(i % cols) * 288}_{(i // cols) * 512}" for i in range(rows * cols))
    graph = f"{scaled}{pads}{labels}xstack=inputs={rows * cols}:layout={layout}[out]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                    "-frames:v", "1", str(out)], check=True, capture_output=True)


def _render(frame: dict[str, Any], refs: list[str], board: dict[str, Any], out: Path, tries: int) -> dict[str, Any]:
    from ..providers.openrouter_image import judge

    provider = config.get_provider(_PROVIDER)
    prompt, best, spent = frame["prompt"], None, 0.0
    for attempt in range(1, tries + 1):
        result = provider.generate(prompt, reference_images=refs, aspect_ratio=board.get("aspect_ratio", "9:16"))
        spent += float(result.extra.get("cost_usd") or 0)
        take = out.with_name(f"{out.stem}.take{attempt}.png")
        take.write_bytes(result.content)
        verdict = judge(_JUDGE.format(shot=frame["shot_spec"], check=frame.get("check", ""),
                                      identity=board.get("identity", "")), [board["character"], str(take)])
        spent += float(verdict.get("cost_usd") or 0)
        score = min(int(verdict.get(k, 0)) for k in _AXES)
        print(f"  {frame['id']} take {attempt}: {score}/10  {'; '.join(verdict.get('issues') or [])[:140]}",
              file=sys.stderr)
        if best is None or score > best["score"]:
            best = {"score": score, "take": attempt, "verdict": verdict}
        if score >= _PASS:
            break
        prompt = f"{frame['prompt']}\nCorrection: {verdict.get('fix', '')}"
    out.write_bytes(out.with_name(f"{out.stem}.take{best['take']}.png").read_bytes())
    return {**best, "cost_usd": round(spent, 4)}


def _attach(plan: dict[str, Any], frames: list[dict[str, Any]], jpgs: list[Path], character: str) -> None:
    """Hand the frames to the shots.

    One generation for the whole film: every frame, in order, as keyframe
    references after the character. One generation per shot: the shot's own
    frame. A silent or voice-over shot opens on it (`first_frame`, image to
    video). A lip-sync shot cannot — the vendor refuses a first frame next to an
    audio reference — so its frame goes in as a reference after the character
    and the prompt names it as the opening frame.
    """
    shots = plan.get("shots") or []
    if len(shots) == 1:
        shots[0].setdefault("kwargs", {})["reference_images"] = [character, *map(str, jpgs)]
        return
    by_shot = {int(f.get("shot", n)): (f, str(j)) for n, (f, j) in enumerate(zip(frames, jpgs), start=1)}
    previs = (plan.get("previs") or {}).get("shots") or {}
    for shot in shots:
        frame, jpg = by_shot.get(int(shot["index"]), (None, None))
        if jpg:
            _attach_frame(shot, frame, jpg, character, as_reference=bool(shot.get("lip_sync"))
                          or shot.get("label") in previs)


def _attach_frame(shot: dict[str, Any], frame: dict[str, Any], jpg: str, character: str, *,
                  as_reference: bool) -> None:
    kwargs = shot.setdefault("kwargs", {})
    if as_reference:
        # A previs clip is a reference too, and references exclude a first frame.
        kwargs.pop("first_frame", None)
        him = shot.get("lip_sync") or "character" in (frame.get("refs") or ["character"])
        kwargs["reference_images"] = [character, jpg] if him else [jpg]
    else:
        kwargs.pop("reference_images", None)
        kwargs["first_frame"] = jpg


def _stale(frames: list[dict[str, Any]], state: dict[str, Any], only: set[str], identity: str,
           out_dir: Path) -> list[dict[str, Any]]:
    """Frames to render: asked for by --only, changed since their last render, or missing."""
    return [f for f in frames if f["id"] in only or state.get(f["id"], {}).get("hash") != _spec_hash(f, identity)
            or not (out_dir / f"{f['id']}.png").is_file()]


def _render_all(board: dict[str, Any], todo: list[dict[str, Any]], state: dict[str, Any], state_path: Path,
                tries: int) -> None:
    """Render the stale frames in board order, saving state after each so a crash loses one frame at most.

    Every frame, rendered or reused, is registered by id first, so a later
    frame can name an earlier one as a reference.
    """
    out_dir, identity = state_path.parent, board.get("identity", "")
    paths: dict[str, str] = {"character": board["character"]}
    for frame in board.get("frames") or []:
        png = out_dir / f"{frame['id']}.png"
        if frame in todo:
            # A frame he is not in must not get his photo: the model puts him in anyway.
            # A ref to a frame since dropped from the board is skipped, not fatal.
            refs = [paths[r] for r in (frame.get("refs") or ["character"]) if r in paths]
            state[frame["id"]] = {**_render(frame, refs, board, png, tries), "hash": _spec_hash(frame, identity)}
            state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
        paths[frame["id"]] = str(png)


def run(args: argparse.Namespace) -> dict[str, Any]:
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    board = plan.get("board") or {}
    frames = board.get("frames") or []
    if not frames:
        raise RunnerError("plan has no board.frames; rerun the film chain")
    out_dir = Path(plan["output_dir"]) / "board"
    out_dir.mkdir(parents=True, exist_ok=True)
    state_path = out_dir / "board.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    only = set((args.only or "").split(",")) - {""}

    todo = _stale(frames, state, only, board.get("identity", ""), out_dir)
    estimate = (config.get_provider(_PROVIDER).estimate_cost() or Decimal("0")) * len(todo) * args.tries
    print(f"Board: {len(frames)} frames, {len(todo)} to render, up to ${estimate:.2f} "
          f"({args.tries} tries each at most).", file=sys.stderr)
    if todo:
        cost_mod.confirm(estimate, yes=args.yes)

    _render_all(board, todo, state, state_path, args.tries)
    character = board["character"]
    jpgs = [_jpeg(out_dir / f"{f['id']}.png") for f in frames]
    _contact(jpgs, out_dir / "contact.jpg")
    _attach(plan, frames, jpgs, character)
    args.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"frames": frames, "state": state, "contact": out_dir / "contact.jpg"}


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_providers()
    try:
        report = run(args)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (RunnerError, ValueError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    spent = sum(float(report["state"].get(f["id"], {}).get("cost_usd") or 0) for f in report["frames"])
    weak = [f["id"] for f in report["frames"] if report["state"].get(f["id"], {}).get("score", 0) < _PASS]
    print(f"Board: {report['contact']}  (spent ≈ ${spent:.2f}; below {_PASS}/10: {', '.join(weak) or 'none'})",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
