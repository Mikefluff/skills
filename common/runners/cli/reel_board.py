"""Storyboard phase of a voiced film — one judged keyframe per shot, before any video.

Direction is decided here, on stills that cost cents, not in a 30-second render
that costs dollars: composition, lens, light and the acting beat of every shot.
Left to itself the video model frames everything centred, evenly lit and medium
— the first trial film did exactly that. Given the approved frames as ordered
references ("Use Images 2-N in order as keyframes"), Seedance 2.5 holds to them.

Each frame is generated (Nano Banana Pro through OpenRouter, with the character
photo and any earlier frames it names as references), then read back by a
vision model against its shot only with --judge: framing, light, identity,
whether it shows the idea or merely illustrates the line, and whether it reads
as cinema or as a stock photo; a frame that fails is then regenerated with the
critic's fix appended, up to --tries times. By default there is one take per
frame and nothing is regenerated: the frames are judged by eye, and the ones
rejected are re-drawn with --only.

  python3 -m common.runners.cli.reel_board --plan-file <dir>/plan.json [--tries 3] [--yes]

Reads plan["board"] (written by the film chain), writes <dir>/board/<id>.png and
.jpg, board/board.json (scores, issues, cost) and board/contact.jpg, and hands
the frames to the shots: all of them as keyframes to a one-generation film, or
each to its own shot when every shot is its own generation. Frames
whose spec has not changed are reused, so editing one frame re-rolls only it.

Before anything is paid for, every frame to draw is listed with why: asked for
(--only), missing, changed since its last render, or failed last time.
--mark-current re-stamps the cache of every frame whose png is on disk, drawing
nothing — for when the cache rule changed and not the frames (board.json written
by a version that hashed the shot number would otherwise redraw the whole board).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import config
from .. import cost as cost_mod
from ..errors import CostConfirmationDeclined, ProviderError, RunnerError
from ._board_cache import _LOOK, _spec_hash, _stale, _summary, _why, mark_current  # noqa: F401 — re-exported

_PROVIDER = "openrouter-nano-banana-pro"
_PASS = 8
_AXES = ("framing", "light", "identity", "idea", "craft", "cinema")

_JUDGE = """You are a film director's eye checking one storyboard frame before it is animated.
{refs} The last image is the frame.

The shot it must be:
{shot}

Must be true: {check}
Identity markers that must match Image 1: {identity}

Score 0-10 each: framing (shot size, angle, placement as specified), light (direction, colour, contrast as specified), identity (every person from a reference is recognisably that person, markers match; 10 if the shot specifies nobody from the references is in frame and nobody is), idea (the frame shows the beat's idea through a concrete image, not a literal illustration), craft (no artefacts, extra people, text, bad hands), cinema (reads as a frame grab from a feature film: real location, texture, imperfect optics, caught mid-action — score low for stock or advertising photography, glossy retouched skin, studio backdrop, a posed portrait, a CG render or a person composited into a scene).
Return JSON only:
{{"framing":0,"light":0,"identity":0,"idea":0,"craft":0,"cinema":0,"score":0,"issues":["..."],"fix":"one sentence the image prompt should add to fix the worst issue"}}
score = the minimum of the six."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_board")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--tries", type=int, default=3, help="with --judge: generations at most (default 3)")
    parser.add_argument("--only", help="comma-separated frame ids to re-roll even if cached")
    parser.add_argument("--judge", action="store_true",
                        help="let a vision critic score each take and re-roll weak ones (off: one take, judged by eye)")
    parser.add_argument("--mark-current", action="store_true",
                        help="draw nothing: re-stamp the cache of every frame whose png exists (with --only, of "
                             "those frames), so frames hashed under an older rule are not redrawn; prints which")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    return parser


def _jpeg(png: Path) -> Path:
    jpg = png.with_suffix(".jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(png), "-q:v", "3", str(jpg)],
                   check=True, capture_output=True)
    return jpg


def _contact(frames: list[Path], out: Path, wide: bool = False) -> None:
    if not frames:
        return
    if wide:
        _contact_wide(frames, out)
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


def _refs_note(names: list[str]) -> str:
    if not names:
        return "There are no reference images."
    return " ".join(f"Image {n} is {name}." for n, name in enumerate(names, start=1))


def _contact_wide(frames: list[Path], out: Path) -> None:
    """16:9 frames, four to a row, in shot order."""
    cols, w, h = min(len(frames), 4), 480, 270
    rows = (len(frames) + cols - 1) // cols
    inputs = [arg for f in frames for arg in ("-i", str(f))]
    cells = rows * cols
    scaled = "".join(f"[{i}:v]scale={w}:{h},setsar=1[v{i}];" for i in range(len(frames)))
    pads = "".join(f"color=black:{w}x{h}:d=1[p{i}];" for i in range(len(frames), cells))
    labels = "".join(f"[v{i}]" for i in range(len(frames))) + "".join(f"[p{i}]" for i in range(len(frames), cells))
    layout = "|".join(f"{(i % cols) * w}_{(i // cols) * h}" for i in range(cells))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
                    f"{scaled}{pads}{labels}xstack=inputs={cells}:layout={layout}[out]", "-map", "[out]",
                    "-frames:v", "1", str(out)], check=True, capture_output=True)


def _bible_assets(plan: dict[str, Any], board: dict[str, Any], plan_file: Path) -> None:
    """A drama plan's frames may name cast and location ids: their rendered portraits and plates become refs."""
    if not plan.get("bible"):
        return
    from .. import drama

    bible = drama.load_bible((plan_file.parent / plan["bible"]).resolve())
    assets, names = {}, {}
    for kind in ("cast", "locations"):
        for item in bible.get(kind) or []:
            path = drama.asset_path(bible, kind, item["id"])
            if not path.is_file():
                raise RunnerError(f"{kind} {item['id']} has no image yet: run common.runners.cli.reel_cast first")
            assets[item["id"]] = str(path)
            names[item["id"]] = (f"{item['name']} ({item['identity']})" if kind == "cast"
                                 else f"the location: {item['description']}")
    if bible.get("master"):
        assets["master"], names["master"] = str(drama.master_path(bible)), "the original picture the film is drawn from"
    board["_assets"], board["_asset_names"] = assets, names


def _people(frame: dict[str, Any], refs: list[str]) -> list[tuple[str, str]]:
    """The references the critic sees — the people and places the frame was drawn from, not earlier frames."""
    names = frame.get("_ref_names") or ["the character reference"] * len(refs)
    return [(r, n) for r, n in zip(refs, names) if not n.startswith("frame ")]


def _padded(image: Path) -> bool:
    """True when both side edges are flat white: the picture was drawn narrower than its canvas."""
    from PIL import Image, ImageStat

    with Image.open(image) as im:
        gray = im.convert("L")
        w, h = gray.size
        strip = max(2, w // 50)
        edges = [ImageStat.Stat(gray.crop(box)) for box in ((0, 0, strip, h), (w - strip, 0, w, h))]
    # white only: a frame graded to black at its edges is the look, not padding
    return all(e.stddev[0] < 3 and e.mean[0] > 245 for e in edges)


def _draw(slug: str, model_id: str | None, prompt: str, refs: list[str], board: dict[str, Any]):
    return config.get_provider(slug).generate(
        prompt, reference_images=refs, aspect_ratio=board.get("aspect_ratio", "9:16"), model_id=model_id,
        image_size=board.get("image_size"), reasoning=board.get("reasoning"), quality=board.get("image_quality", "high"))


def _no_image(exc: Exception) -> dict[str, Any]:
    return {"issues": [f"no image: {' '.join(str(exc).split())[:300]}"], "fix": ""}


def _drawn(frame: dict[str, Any], refs: list[str], board: dict[str, Any], prompt: str) -> tuple[Any, dict[str, Any]]:
    """(result, {}) or (None, the refusal as a verdict); a moderation refusal goes to the fallback drawer once."""
    try:
        # board["image_model"] / ["image_size"] / ["reasoning"] pick the model (e.g. google/gemini-nano-banana-2.1),
        # 1K/2K/4K and thinking depth; unset, the provider's Nano Banana Pro at 2K.
        # board["image_provider"] swaps the drawer itself (e.g. "gpt-image-2" with image_model gpt-image-2.5-sunburst).
        return _draw(board.get("image_provider") or _PROVIDER, board.get("image_model"), prompt, refs, board), {}
    except ProviderError as exc:
        fallback = board.get("fallback_provider")
        if not (fallback and "moderation" in str(exc)):
            return None, _no_image(exc)
    # one vendor's safety filter refusing a cartoon frame is not a verdict on it: the other vendor draws it
    print(f"  {frame['id']}: refused by the safety filter, drawn by {fallback}", file=sys.stderr)
    try:
        return _draw(fallback, None, prompt, refs, board), {}
    except ProviderError as again:
        return None, _no_image(again)


def _take(frame: dict[str, Any], refs: list[str], board: dict[str, Any], prompt: str, take: Path) -> tuple[int, dict, float]:
    """One generation and its verdict: (score, verdict, dollars). A refusal scores 0 and costs a retry, not the board."""
    from ..providers.openrouter_image import judge

    result, refused = _drawn(frame, refs, board, prompt)
    if result is None:
        return 0, refused, 0.0
    take.write_bytes(result.content)
    drawn = float(result.extra.get("cost_usd") or 0)
    if _padded(take):
        # The model sometimes draws a narrower picture on a 16:9 canvas; a video model animates the bars too.
        return 0, {"issues": ["drawn with blank bars at the sides"], "fix": ""}, drawn
    if not board.get("_judge", True):
        return 10, {}, drawn
    people = _people(frame, refs)
    verdict = judge(_JUDGE.format(refs=_refs_note([n for _, n in people]), shot=frame["shot_spec"],
                                  check=frame.get("check", ""), identity=board.get("identity", "")),
                    [r for r, _ in people] + [str(take)])
    score = min(int(verdict.get(k, 0)) for k in _AXES)
    return score, verdict, drawn + float(verdict.get("cost_usd") or 0)


def _render(frame: dict[str, Any], refs: list[str], board: dict[str, Any], out: Path, tries: int) -> dict[str, Any]:
    """The best of up to `tries` takes; {"score": 0, "failed": True} when the model drew nothing at all."""
    prompt, best, spent = frame["prompt"], None, 0.0
    for attempt in range(1, tries + 1):
        take = out.with_name(f"{out.stem}.take{attempt}.png")
        score, verdict, cost = _take(frame, refs, board, prompt, take)
        spent += cost
        print(f"  {frame['id']} take {attempt}: {score}/10  {'; '.join(verdict.get('issues') or [])[:320]}",
              file=sys.stderr)
        if take.is_file() and (best is None or score > best["score"]):
            best = {"score": score, "take": attempt, "verdict": verdict}
        if score >= _PASS:
            break
        prompt = f"{frame['prompt']}\nCorrection: {verdict.get('fix', '')}" if verdict.get("fix") else frame["prompt"]
    if best is None:
        return {"score": 0, "failed": True, "cost_usd": round(spent, 4)}
    out.write_bytes(out.with_name(f"{out.stem}.take{best['take']}.png").read_bytes())
    for take in out.parent.glob(f"{out.stem}.take*.png"):
        take.unlink()  # the kept take is <id>.png; the scores of every take stay in board.json
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


def _known_refs(board: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    """What a frame's refs can name before any frame is drawn: the character, or a drama's cast and places."""
    paths = {"character": board["character"]} if board.get("character") else {}
    names = {"character": "the character reference", **(board.get("_asset_names") or {})}
    return {**paths, **(board.get("_assets") or {})}, names


def _render_all(board: dict[str, Any], todo: list[dict[str, Any]], state: dict[str, Any], state_path: Path,
                tries: int) -> None:
    """Render the stale frames in board order, saving state after each so a crash loses one frame at most.

    Every frame, rendered or reused, is registered by id first, so a later
    frame can name an earlier one as a reference.
    """
    out_dir, identity = state_path.parent, board.get("identity", "")
    paths, names = _known_refs(board)
    for frame in board.get("frames") or []:
        png = out_dir / f"{frame['id']}.png"
        if frame in todo:
            # A frame he is not in must not get his photo: the model puts him in anyway.
            # A ref to a frame since dropped from the board is skipped, not fatal.
            wanted = [r for r in (frame.get("refs") or ["character"]) if r in paths]
            refs = [paths[r] for r in wanted]
            named = {**frame, "_ref_names": [names.get(r, f"frame {r}") for r in wanted]}
            state[frame["id"]] = {**_render(named, refs, board, png, tries), "hash": _spec_hash(frame, identity)}
            state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
        if png.is_file():  # a frame the model refused is not a reference for later ones
            paths[frame["id"]] = str(png)


def _finish(plan: dict[str, Any], board: dict[str, Any], frames: list[dict[str, Any]],
            out_dir: Path) -> list[dict[str, Any]]:
    """Contact sheet and hand-off for the frames that were drawn; the ones the model refused are named."""
    drawn = [f for f in frames if (out_dir / f"{f['id']}.png").is_file()]
    missing = [f["id"] for f in frames if f not in drawn]
    if missing:
        print(f"Board: no image for {', '.join(missing)}; rewrite their prompts and run again with --only.",
              file=sys.stderr)
    frames, jpgs = drawn, [_jpeg(out_dir / f"{f['id']}.png") for f in drawn]
    _contact(jpgs, out_dir / "contact.jpg", wide=board.get("aspect_ratio") == "16:9")
    board.pop("_assets", None)
    board.pop("_judge", None)
    board.pop("_asset_names", None)
    if board.get("character"):
        _attach(plan, frames, jpgs, board["character"])
    return frames


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

    stale = _stale(frames, state, only, board.get("identity", ""), out_dir)
    todo = [f for f, _ in stale]
    if not args.judge:
        args.tries = 1
    drawer = config.get_provider(board.get("image_provider") or _PROVIDER)
    per_frame = (drawer.estimate_cost(quality=board.get("image_quality", "high")) or Decimal("0")) * args.tries
    estimate = per_frame * len(todo)
    _summary(stale, per_frame, only)
    print(f"Board: {len(frames)} frames, {len(todo)} to render, up to ${estimate:.2f} "
          f"({args.tries} tries each at most).", file=sys.stderr)
    if todo:
        cost_mod.confirm(estimate, yes=args.yes)

    _bible_assets(plan, board, args.plan_file)
    board["_judge"] = args.judge
    _render_all(board, todo, state, state_path, args.tries)
    frames = _finish(plan, board, frames, out_dir)
    args.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"frames": frames, "state": state, "contact": out_dir / "contact.jpg"}


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_providers()
    if args.mark_current:
        marked = mark_current(args)
        print(f"Board: re-stamped {len(marked)} frame(s): {', '.join(marked) or 'none needed'}", file=sys.stderr)
        return 0
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
