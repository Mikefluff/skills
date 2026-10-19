"""Cast phase of a drama — the series' faces and places, judged, then handed to every scene.

  python3 -m common.runners.cli.reel_cast --plan-file <series>/ep01/plan.json [--only malai,village_storm] [--yes]

Reads the bible the plan names (plan["bible"], written by the drama chain) and
renders, through Nano Banana Pro on OpenRouter, one portrait per character to
<series>/cast/<id>.png and one plate per location to <series>/locations/<id>.png.
One take each; with --judge a vision critic reads each against its description
and re-rolls it below 8/10. A character with a `voice_text` also gets a voice,
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
from .. import spend
from ..errors import CostConfirmationDeclined, RunnerError
from ._cast_scenes import (  # noqa: F401 — re-exported: reel_cast.cast_scenes etc.
    _board_frame,
    _bridge_scene,
    _extend_scene,
    _first_frame_scene,
    _rendered,
    cast_scenes,
)

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
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--plan-file", type=Path, help="an episode or trailer plan: render, then cast its scenes")
    src.add_argument("--bible", type=Path, help="render the bible's faces and places only, before any plan exists")
    parser.add_argument("--no-voices", action="store_true", help="skip designing voices (faces and places only)")
    parser.add_argument("--voices-only", action="store_true",
                        help="design voices only (for --only ids, or every speaker); no image is drawn")
    parser.add_argument("--judge", action="store_true",
                        help="let a vision critic score each take and re-roll weak ones (off: one take, judged by eye)")
    parser.add_argument("--only", help="comma-separated cast or location ids to re-roll even if cached")
    parser.add_argument("--tries", type=int, default=3, help="with --judge: generations at most (default 3)")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    return parser


def _hash(item: dict[str, Any], look: str) -> str:
    return hashlib.sha256(json.dumps([item.get("prompt"), item.get("identity"), item.get("description"), look,
                                      *(item.get("refs") or [])],
                                     ensure_ascii=False).encode()).hexdigest()[:16]


def _take_refs(item: dict[str, Any], bible: dict[str, Any]) -> list[str]:
    """The pictures a take is drawn from: a double's original, else the master, then the place's photographs."""
    # A double ("like": another cast id) is drawn from that character's portrait, so the faces really match.
    like = [str(drama.asset_path(bible, "cast", item["like"]))] if item.get("like") else []
    # A film drawn from one existing picture ("master" in the bible): every face and place is taken from it, not invented.
    master = [str(drama.master_path(bible))] if bible.get("master") and not like else []
    # A real place the film is set in: its photographs (item["refs"], relative to the bible) follow the master.
    photos = [str(Path(bible["_dir"]) / r) for r in item.get("refs") or []]
    return like + master + photos


def _take(kind: str, item: dict[str, Any], bible: dict[str, Any], prompt: str, take: Path) -> tuple[int, dict, float]:
    """One generation and its verdict: (score, verdict, dollars spent)."""
    from ..providers.openrouter_image import judge

    aspect = "3:4" if kind == "cast" else bible.get("aspect_ratio", "16:9")
    # bible["image_provider"] / ["image_model"] pick another drawer (e.g. gpt-image-2 + gpt-image-2.5-sunburst)
    result = config.get_provider(bible.get("image_provider") or _PROVIDER).generate(
        prompt, aspect_ratio=aspect, reference_images=_take_refs(item, bible), model_id=bible.get("image_model"),
        quality=bible.get("image_quality", "high"))
    take.write_bytes(result.content)
    drawn = float(result.extra.get("cost_usd") or 0)
    if not bible.get("_judge", True):
        return 10, {}, drawn
    spec = item.get("identity") or item.get("description") or ""
    verdict = judge(_JUDGE.format(kind=kind, spec=spec, look=bible.get("look", ""), usable=_USABLE[kind]), [str(take)])
    score = min(int(verdict.get(k, 0)) for k in ("match", "usable", "craft", "cinema"))
    return score, verdict, drawn + float(verdict.get("cost_usd") or 0)


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
    # The look is not part of an asset's identity: regrading the film must not silently
    # replace every face and place the storyboard was drawn from. Re-roll on purpose with --only.
    items = [(kind, item) for kind in ("cast", "locations") for item in bible.get(kind) or []]
    if only:
        todo = [(kind, item) for kind, item in items if item["id"] in only]
    else:
        todo = [(kind, item) for kind, item in items
                if state.get(item["id"], {}).get("hash") != _hash(item, "")
                or not drama.asset_path(bible, kind, item["id"]).is_file()]
    return sorted(todo, key=lambda pair: bool(pair[1].get("like")))  # doubles after the faces they copy


def _asset_lines(todo: list[tuple[str, dict[str, Any]]], bible: dict[str, Any], state: dict[str, Any],
                 only: set[str], per: Decimal) -> list[spend.Line]:
    def why(kind: str, item: dict[str, Any]) -> str:
        if item["id"] in only:
            return spend.ASKED
        return spend.CHANGED if drama.asset_path(bible, kind, item["id"]).is_file() else spend.MISSING
    return [(item["id"], per, why(kind, item)) for kind, item in todo]


def _voice_why(item: dict[str, Any], bible: dict[str, Any], state: dict[str, Any]) -> str | None:
    """Why `_voice` would buy this character a voice (ElevenLabs, unpriced here), or None when it reuses one."""
    entry, sample = state.get(f"{item['id']}:voice") or {}, drama.asset_path(bible, "cast", item["id"], ".mp3")
    lib = item.get("voice_library")
    spec = f"library:{lib['id']}" if lib else _hash({"prompt": item.get("voice"), "identity": item["voice_text"]}, "")
    if entry.get("hash") == spec and entry.get("voice_id") and sample.is_file():
        return None
    # A library actor whose id still matches only needs its sample read again: that is missing, not changed.
    return spend.CHANGED if entry and entry.get("hash") != spec else spend.MISSING


def _voice_lines(bible: dict[str, Any], state: dict[str, Any], args: argparse.Namespace) -> list[spend.Line]:
    only = set((args.only or "").split(",")) - {""}
    if args.no_voices:
        return []
    speakers = [i for i in [*(bible.get("cast") or []), *(bible.get("offscreen_voices") or [])]
                if i.get("voice_text") and (not only or i["id"] in only)]
    return [(f"voice:{i['id']}", None, why) for i in speakers if (why := _voice_why(i, bible, state))]


_VOICE_SECONDS = 7.0


def _voice(item: dict[str, Any], bible: dict[str, Any], state: dict[str, Any]) -> None:
    """A designed voice for one character, kept in the account (its voice_id goes to cast.json) and cut to a
    7 s sample at cast/<id>.mp3 so two speakers fit one generation's audio."""
    from ..providers.elevenlabs import add_library_voice, designed_voice, save_voice

    if item.get("voice_library"):
        _library_voice(item, state, add_library_voice)
        _library_sample(item, bible, state)
        return
    key, spec = f"{item['id']}:voice", _hash({"prompt": item.get("voice"), "identity": item["voice_text"]}, "")
    out = drama.asset_path(bible, "cast", item["id"], ".mp3")
    if state.get(key, {}).get("hash") == spec and out.is_file() and state[key].get("voice_id"):
        return
    raw = out.with_name(f"{item['id']}.design.mp3")
    raw.parent.mkdir(parents=True, exist_ok=True)
    description = item.get("voice") or item["identity"]
    audio, generated = designed_voice(description, item["voice_text"])
    raw.write_bytes(audio)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-t", f"{_VOICE_SECONDS}",
                    "-af", f"afade=t=out:st={_VOICE_SECONDS - 0.3}:d=0.3", str(out)], check=True, capture_output=True)
    raw.unlink()
    title = bible.get("title") or Path(bible["_dir"]).name
    state[key] = {"hash": spec, "voice_id": save_voice(f"{title} — {item['name']}", description, generated)}
    print(f"  {item['id']}: voice designed and saved", file=sys.stderr)


def _library_voice(item: dict[str, Any], state: dict[str, Any], add) -> None:
    """A recorded actor from the Voice Library, added to the account once; v4 acts best on these."""
    lib, key = item["voice_library"], f"{item['id']}:voice"
    spec = f"library:{lib['id']}"
    if state.get(key, {}).get("hash") == spec and state[key].get("voice_id"):
        return
    state[key] = {"hash": spec, "voice_id": add(lib["owner"], lib["id"], lib.get("name") or item["name"]),
                  "accent": lib.get("accent", "")}
    print(f"  {item['id']}: voice {lib.get('name')} added from the Voice Library", file=sys.stderr)


def _library_sample(item: dict[str, Any], bible: dict[str, Any], state: dict[str, Any]) -> None:
    """A library actor has no designed sample, but a scene that speaks sends one as its voice reference:
    the actor reads the character's voice_text on Eleven v4, cut to the same 7 s."""
    out = drama.asset_path(bible, "cast", item["id"], ".mp3")
    if out.is_file():
        return
    raw = out.with_name(f"{item['id']}.read.mp3")
    raw.write_bytes(config.get_provider("eleven-tts").generate(
        item["voice_text"], voice_id=state[f"{item['id']}:voice"]["voice_id"], model_id="eleven_v4").content)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-t", f"{_VOICE_SECONDS}",
                    "-af", f"afade=t=out:st={_VOICE_SECONDS - 0.3}:d=0.3", str(out)], check=True, capture_output=True)
    raw.unlink()
    print(f"  {item['id']}: voice sample read by {item['voice_library'].get('name')}", file=sys.stderr)


def _render_assets(todo: list[tuple[str, dict[str, Any]]], bible: dict[str, Any], state: dict[str, Any],
                   state_path: Path, args: argparse.Namespace) -> None:
    """Faces and places that need it, then voices; state saved after each so a crash loses one asset at most."""
    save = lambda: state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")  # noqa: E731
    for kind, item in todo:
        out = drama.asset_path(bible, kind, item["id"])
        out.parent.mkdir(parents=True, exist_ok=True)
        state[item["id"]] = {**_render(kind, item, bible, out, args.tries), "hash": _hash(item, "")}
        save()
    for item in [*(bible.get("cast") or []), *(bible.get("offscreen_voices") or [])]:
        only = set((args.only or "").split(",")) - {""}
        if not args.no_voices and item.get("voice_text") and (not only or item["id"] in only):
            _voice(item, bible, state)
            save()


def _load(args: argparse.Namespace) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """The plan (None with --bible) and its bible, checked against each other."""
    if args.bible:
        return None, drama.load_bible(args.bible.resolve())
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    if not plan.get("bible"):
        raise RunnerError("plan names no bible; rerun the drama chain")
    bible = drama.load_bible((args.plan_file.parent / plan["bible"]).resolve())
    problems = drama.validate(plan, bible)
    if problems:
        raise RunnerError("episode does not match its bible:\n  " + "\n  ".join(problems))
    return plan, bible


def run(args: argparse.Namespace) -> dict[str, Any]:
    plan, bible = _load(args)
    bible["_judge"] = args.judge
    if not args.judge:
        args.tries = 1
    state_path = Path(bible["_dir"]) / "cast.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}

    only = set((args.only or "").split(",")) - {""}
    todo = [] if args.voices_only else _todo(bible, state, only)
    drawer = config.get_provider(bible.get("image_provider") or _PROVIDER)
    per = (drawer.estimate_cost(quality=bible.get("image_quality", "high")) or Decimal("0")) * args.tries
    estimate = per * len(todo)
    spend.show("Cast", _asset_lines(todo, bible, state, only, per) + _voice_lines(bible, state, args))
    print(f"Cast: {len(bible.get('cast') or [])} faces, {len(bible.get('locations') or [])} places, "
          f"{len(todo)} to render, up to ${estimate:.2f}.", file=sys.stderr)
    if todo:
        cost_mod.confirm(estimate, yes=args.yes)
    _render_assets(todo, bible, state, state_path, args)
    if plan is not None:
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
