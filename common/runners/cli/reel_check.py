"""Check phase of a drama — did each scene say its lines, with the right faces?

  python3 -m common.runners.cli.reel_check --plan-file <series>/ep01/plan.json [--only sc03] [--min-speech 0.8]

For every rendered scene: its sound, over the part the edit uses, goes through
ElevenLabs speech-to-text in the episode's language and is compared with the
scene's script letter by letter (Thai and Japanese write no spaces between
words; a word count would fail them). Then its first, middle and last used
frames go to a vision model next to the cast portraits: same people, nobody
doubled, no subtitles burnt in. Writes <out>/check.json and prints the one
command that re-renders what failed:

  python3 -m common.runners.cli.reel --plan-file <plan.json> --redo sc03,sc07

Nobody on the team has to read the language: a scene whose transcript does not
match its script is re-rendered on the same evidence a native speaker would use.
Costs about a cent per scene.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .. import config
from .. import drama
from .. import ffmpeg_film
from ..errors import ProviderError, RunnerError

_LOOK = """Images 1-{n} are the cast of this scene: {names}. The last image shows three frames of the rendered scene, left to right: start, middle, end.
The scene is meant to be: {scene}

Return JSON only: {{"identity":0,"doubles":false,"text_on_screen":false,"issues":["..."]}}
identity 0-10: every person who is in the frames is recognisably one of the cast images (face, hair, clothing); 10 if nobody's face is visible.
doubles: the same character appears twice at the same moment.
text_on_screen: subtitles, captions, logos or any written text burnt into the picture."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_check")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--only", help="comma-separated scene labels to check (default: all rendered)")
    parser.add_argument("--min-speech", type=float, default=0.8,
                        help="share of the script's letters that must be heard (default 0.8)")
    parser.add_argument("--min-identity", type=int, default=7, help="lowest passing identity score (default 7)")
    return parser


def _rendered(out_dir: Path) -> dict[int, Path]:
    manifest = out_dir / "manifest.json"
    if not manifest.is_file():
        raise RunnerError(f"no manifest at {manifest}; render the episode first")
    return {int(it["index"]): Path(it["output_path"]) for it in json.loads(manifest.read_text(encoding="utf-8"))["items"]
            if it.get("status") == "succeeded" and it.get("output_path")}


def _window(scene: dict[str, Any]) -> tuple[float, float]:
    kwargs = scene.get("kwargs") or {}
    start = float(scene.get("trim_start") or 0)
    return start, float(scene.get("trim_seconds") or kwargs.get("duration_seconds") or 5)


def _speech(scene: dict[str, Any], clip: Path, language: str, work: Path) -> dict[str, Any]:
    from ..providers.elevenlabs import transcribe

    script = drama.scene_script(scene)
    if not script:
        return {"speech": None}
    start, length = _window(scene)
    mp3 = work / f"{scene['label']}-speech.mp3"
    ffmpeg_film.extract_audio(clip, mp3, start=start, length=length)
    heard = " ".join(w["text"] for w in transcribe(mp3.read_bytes(), language))
    mp3.unlink()
    return {"speech": round(drama.speech_match(script, heard), 3), "script": script, "heard": heard}


def _look(scene: dict[str, Any], clip: Path, bible: dict[str, Any], work: Path) -> dict[str, Any]:
    from ..providers.openrouter_image import judge

    cast = [c for c in bible.get("cast") or [] if c["id"] in (scene.get("cast") or [])]
    start, length = _window(scene)
    strip = work / f"{scene['label']}-look.jpg"
    stamps = [start + 0.2, start + length / 2, start + length - 0.2]
    pick = "+".join(f"between(t\\,{t - 0.02:.2f}\\,{t + 0.02:.2f})" for t in stamps)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-vf",
                    f"select='{pick}',scale=320:-1,tile=3x1:padding=8:color=white", "-frames:v", "1",
                    "-fps_mode", "passthrough", str(strip)], check=True, capture_output=True)
    images = [str(drama.asset_path(bible, "cast", c["id"])) for c in cast] + [str(strip)]
    verdict = judge(_LOOK.format(n=len(cast), names=", ".join(c["name"] for c in cast) or "nobody",
                                 scene=scene["body"][:700]), images)
    strip.unlink()
    return {k: verdict.get(k) for k in ("identity", "doubles", "text_on_screen", "issues")}


def _fails(result: dict[str, Any], min_speech: float, min_identity: int) -> list[str]:
    why = []
    if result.get("speech") is not None and result["speech"] < min_speech:
        why.append(f"speech {result['speech']:.2f}")
    if int(result.get("identity") or 0) < min_identity:
        why.append(f"identity {result.get('identity')}/10")
    why += [flag.replace("_", " ") for flag in ("doubles", "text_on_screen") if result.get(flag)]
    return why


def run(args: argparse.Namespace) -> dict[str, Any]:
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    bible = drama.load_bible((args.plan_file.parent / plan["bible"]).resolve())
    out_dir = Path(plan["output_dir"])
    clips, only = _rendered(out_dir), set((args.only or "").split(",")) - {""}
    report_path = out_dir / "check.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    for scene in sorted(plan["shots"], key=lambda s: int(s["index"])):
        clip = clips.get(int(scene["index"]))
        if not clip or (only and scene["label"] not in only):
            continue
        result = {**_speech(scene, clip, bible["language"], out_dir), **_look(scene, clip, bible, out_dir)}
        result["fails"] = _fails(result, args.min_speech, args.min_identity)
        report[scene["label"]] = result
        print(f"  {scene['label']}: {'; '.join(result['fails']) or 'ok'}", file=sys.stderr)
        report_path.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_providers()
    try:
        report = run(args)
    except (RunnerError, ProviderError, KeyError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    redo = [label for label, r in report.items() if r.get("fails")]
    if redo:
        print(f"Re-render: python3 -m common.runners.cli.reel --plan-file {args.plan_file} --redo {','.join(redo)}",
              file=sys.stderr)
        return 4
    print("Check: every scene said its lines with the right faces.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
