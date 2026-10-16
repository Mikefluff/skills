"""Cast phase of a drama — the series' faces and places, judged, then handed to every scene.

  python3 -m common.runners.cli.reel_cast --plan-file <series>/ep01/plan.json [--only malai,village_storm] [--yes]

Reads the bible the plan names (plan["bible"], written by the drama chain) and
renders, through Nano Banana Pro on OpenRouter, one portrait per character to
<series>/cast/<id>.png and one plate per location to <series>/locations/<id>.png.
A vision critic reads each against its description; below 8/10 it is re-rolled
with the critic's fix. A character with a `voice_text` also gets a voice,
designed by ElevenLabs from its `voice` description, cut to 7 s at
<series>/cast/<id>.mp3. Assets already rendered from an unchanged description are
reused — that is what keeps a series' faces the same from episode to episode.

Then every scene gets its images in order (its cast, then its location) as
`reference_images`, its speakers' voices as `reference_audio` (on the
OpenRouter route they need a host: set "media_host" in the plan), and its `prompt` is composed: one line per image naming who
or where it is, the series look, then the scene's body. Run it again after
editing a scene; nothing is re-rendered that did not change.
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
from .. import drama
from ..errors import CostConfirmationDeclined, RunnerError

_PROVIDER = "openrouter-nano-banana-pro"
_PASS = 8

_JUDGE = """You are a casting director and a production designer checking one reference image for a film.
The image must be: {kind} — {spec}
Series look: {look}

Score 0-10 each: match (it is what the description says: age, build, face, hair, clothing; or the place, weather, time of day), usable (a {usable}), craft (no artefacts, extra limbs, text, watermark, frame within a frame), cinema (a photographed feature-film still, not stock or advertising, not a CG render).
Return JSON only: {{"match":0,"usable":0,"craft":0,"cinema":0,"issues":["..."],"fix":"one sentence the prompt should add"}}"""

_USABLE = {
    "cast": "single person, face unobstructed and sharp, head to waist, neutral light on the face, plain uncluttered "
            "background, nobody else in frame",
    "locations": "wide establishing view with no people in it, readable architecture and light",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_cast")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--only", help="comma-separated cast or location ids to re-roll even if cached")
    parser.add_argument("--tries", type=int, default=3, help="generations per asset at most (default 3)")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    return parser


def _hash(item: dict[str, Any], look: str) -> str:
    return hashlib.sha256(json.dumps([item.get("prompt"), item.get("identity"), item.get("description"), look],
                                     ensure_ascii=False).encode()).hexdigest()[:16]


def _take(kind: str, item: dict[str, Any], bible: dict[str, Any], prompt: str, take: Path) -> tuple[int, dict, float]:
    """One generation and its verdict: (score, verdict, dollars spent)."""
    from ..providers.openrouter_image import judge

    aspect = "3:4" if kind == "cast" else bible.get("aspect_ratio", "16:9")
    result = config.get_provider(_PROVIDER).generate(prompt, aspect_ratio=aspect)
    take.write_bytes(result.content)
    spec = item.get("identity") or item.get("description") or ""
    verdict = judge(_JUDGE.format(kind=kind, spec=spec, look=bible.get("look", ""), usable=_USABLE[kind]), [str(take)])
    score = min(int(verdict.get(k, 0)) for k in ("match", "usable", "craft", "cinema"))
    spent = float(result.extra.get("cost_usd") or 0) + float(verdict.get("cost_usd") or 0)
    return score, verdict, spent


def _render(kind: str, item: dict[str, Any], bible: dict[str, Any], out: Path, tries: int) -> dict[str, Any]:
    prompt, best, spent = item["prompt"], None, 0.0
    for attempt in range(1, tries + 1):
        score, verdict, cost = _take(kind, item, bible, prompt, out.with_name(f"{out.stem}.take{attempt}.png"))
        spent += cost
        print(f"  {item['id']} take {attempt}: {score}/10  {'; '.join(verdict.get('issues') or [])[:140]}",
              file=sys.stderr)
        if best is None or score > best["score"]:
            best = {"score": score, "take": attempt}
        if score >= _PASS:
            break
        prompt = f"{item['prompt']}\nCorrection: {verdict.get('fix', '')}"
    out.write_bytes(out.with_name(f"{out.stem}.take{best['take']}.png").read_bytes())
    for take in out.parent.glob(f"{out.stem}.take*.png"):
        take.unlink()
    return {**best, "cost_usd": round(spent, 4)}


def _todo(bible: dict[str, Any], state: dict[str, Any], only: set[str]) -> list[tuple[str, dict[str, Any]]]:
    """Assets to render: asked for, changed since their render, or missing."""
    look = bible.get("look", "")
    return [(kind, item) for kind in ("cast", "locations") for item in bible.get(kind) or []
            if item["id"] in only or state.get(item["id"], {}).get("hash") != _hash(item, look)
            or not drama.asset_path(bible, kind, item["id"]).is_file()]


_VOICE_SECONDS = 7.0


def _voice(item: dict[str, Any], bible: dict[str, Any], state: dict[str, Any]) -> None:
    """A designed voice for one character, cut to 7 s so two speakers fit one generation's audio."""
    from ..providers.elevenlabs import design_voice

    key, spec = f"{item['id']}:voice", _hash({"prompt": item.get("voice"), "identity": item["voice_text"]}, "")
    out = drama.asset_path(bible, "cast", item["id"], ".mp3")
    if state.get(key, {}).get("hash") == spec and out.is_file():
        return
    raw = out.with_name(f"{item['id']}.design.mp3")
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(design_voice(item.get("voice") or item["identity"], item["voice_text"]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-t", f"{_VOICE_SECONDS}",
                    "-af", f"afade=t=out:st={_VOICE_SECONDS - 0.3}:d=0.3", str(out)], check=True, capture_output=True)
    raw.unlink()
    state[key] = {"hash": spec}
    print(f"  {item['id']}: voice designed", file=sys.stderr)


def cast_scenes(plan: dict[str, Any], bible: dict[str, Any]) -> None:
    """Each scene's references and composed prompt, from the bible."""
    for scene in plan["shots"]:
        refs, _ = drama.references(scene, bible)
        audio, _ = drama.voices(scene, bible)
        kwargs = scene.setdefault("kwargs", {})
        kwargs["reference_images"] = refs
        if audio:
            kwargs["reference_audio"] = audio
            if plan.get("media_host"):
                kwargs["media_host"] = plan["media_host"]
        else:
            kwargs.pop("reference_audio", None)
        kwargs.setdefault("aspect_ratio", bible.get("aspect_ratio", "16:9"))
        kwargs.setdefault("generate_audio", True)
        scene["prompt"] = drama.compose(scene, bible)


def _render_assets(todo: list[tuple[str, dict[str, Any]]], bible: dict[str, Any], state: dict[str, Any],
                   state_path: Path, tries: int) -> None:
    """Faces and places that need it, then voices; state saved after each so a crash loses one asset at most."""
    save = lambda: state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")  # noqa: E731
    for kind, item in todo:
        out = drama.asset_path(bible, kind, item["id"])
        out.parent.mkdir(parents=True, exist_ok=True)
        state[item["id"]] = {**_render(kind, item, bible, out, tries), "hash": _hash(item, bible.get("look", ""))}
        save()
    for item in bible.get("cast") or []:
        if item.get("voice_text"):
            _voice(item, bible, state)
            save()


def run(args: argparse.Namespace) -> dict[str, Any]:
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    if not plan.get("bible"):
        raise RunnerError("plan names no bible; rerun the drama chain")
    bible = drama.load_bible((args.plan_file.parent / plan["bible"]).resolve())
    problems = drama.validate(plan, bible)
    if problems:
        raise RunnerError("episode does not match its bible:\n  " + "\n  ".join(problems))
    state_path = Path(bible["_dir"]) / "cast.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}

    todo = _todo(bible, state, set((args.only or "").split(",")) - {""})
    estimate = (config.get_provider(_PROVIDER).estimate_cost() or Decimal("0")) * len(todo) * args.tries
    print(f"Cast: {len(bible.get('cast') or [])} faces, {len(bible.get('locations') or [])} places, "
          f"{len(todo)} to render, up to ${estimate:.2f}.", file=sys.stderr)
    if todo:
        cost_mod.confirm(estimate, yes=args.yes)
    _render_assets(todo, bible, state, state_path, args.tries)
    cast_scenes(plan, bible)
    args.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"state": state, "bible": bible}


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_providers()
    try:
        report = run(args)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (RunnerError, drama.DramaError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    weak = [k for k, v in report["state"].items() if ":" not in k and v.get("score", 0) < _PASS]
    print(f"Cast: {report['bible']['_dir']}/cast/, locations/  (below {_PASS}/10: {', '.join(weak) or 'none'}). "
          "Look at them before rendering scenes.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
