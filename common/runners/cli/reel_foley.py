"""Foley for a cut from a video-to-audio model: footsteps, cloth, props and impacts, synced to the picture.

  python3 -m common.runners.cli.reel_foley --plan-file <dir>/plan.json [--dry-run] [--gain -10]

The video model's own sound is thin and wrong (left out with "video_audio": false), and hand-placed effects
cover the story beats but not every step and rustle. This pass sends the cut's picture, in windows of whole
shots up to `WINDOW` seconds broken at scene changes, to Mirelo SFX 2.0 on fal (mirelo-ai/sfx2.0/video-to-
audio: effects only, no speech, no music), takes the voice-like sounds out of what comes back with the same
vocal separator the production layer used, and lays each window as a file source "foley_<n>" on the film's
clock under the effects. A window is kept in <out>/sound/foley/ by its shots' picture (their part keys in
trailer.picture.json), so after a shot is rendered again only the windows it is in are bought again.
Needs FAL_KEY; costs $0.01 a second of picture until 2026-12-13, then $0.015 (--dry-run prints it).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

MODEL = "mirelo-ai/sfx2.0/video-to-audio"
PRICE_PER_SECOND = 0.01
WINDOW = 30.0
_MAX_BYTES = 8 * 1024 * 1024
_ASK = {"preserve_speech": False, "num_samples": 1, "negative_prompt": "music, speech, voices, singing, talking",
        "text_prompt": "stylized 3D cartoon, playful crisp foley: footsteps, cloth, props, impacts"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_foley")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--gain", type=float, default=-10.0, help="dB of the foley layer in the mix")
    return parser


def windows(plan: dict[str, Any], limit: float = WINDOW) -> list[list[dict[str, Any]]]:
    """Consecutive shots grouped up to `limit` seconds, a new window at every scene change."""
    shots = sorted((s for s in plan["shots"] if not s.get("cut")), key=lambda s: float(s["clock_at"]))
    out: list[list[dict[str, Any]]] = []
    for shot in shots:
        cur = out[-1] if out else None
        span = float(shot["clock_at"]) + float(shot["trim_seconds"]) - float(cur[0]["clock_at"]) if cur else 0
        if cur and span <= limit and (shot.get("scene") == cur[-1].get("scene") or shot.get("bridge")):
            cur.append(shot)
        else:
            out.append([shot])
    return out


def _span(window: list[dict[str, Any]]) -> tuple[float, float]:
    return float(window[0]["clock_at"]), float(window[-1]["clock_at"]) + float(window[-1]["trim_seconds"])


def _key(window: list[dict[str, Any]], parts: dict[str, str]) -> str:
    """By the window's shots and their picture, and its length — not its place on the clock: a shot put in
    earlier in the film moves every later window, and their foley is the same sound one beat later."""
    a, b = _span(window)
    raw = [MODEL, _ASK, [(s["label"], parts.get(s["label"])) for s in window], round(b - a, 3)]
    return hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()[:16]


def _picture(film: Path, a: float, b: float, out: Path) -> Path:
    for crf in (28, 32, 36):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(film), "-an",
                        "-vf", "scale=854:-2", "-c:v", "libx264", "-crf", str(crf), str(out)], check=True)
        if out.stat().st_size < _MAX_BYTES * 0.74:  # base64 grows it by a third
            return out
    return out


def _call(body: dict[str, Any]) -> dict[str, Any]:
    head = {"Authorization": f"Key {os.environ['FAL_KEY']}", "Content-Type": "application/json"}

    def req(url: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        r = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=head,
                                   method="POST" if data else "GET")
        return json.loads(urllib.request.urlopen(r, timeout=180).read())

    queued = req(f"https://queue.fal.run/{MODEL}", body)
    while (state := req(queued["status_url"]).get("status")) != "COMPLETED":
        if state in ("FAILED", "ERROR", "CANCELED"):
            raise RuntimeError(f"foley {state}")
        time.sleep(3)
    return req(queued["response_url"])


def _make(film: Path, a: float, b: float, out: Path) -> None:
    from ._trailer_sound import without_voice

    clip = _picture(film, a, b, out.with_suffix(".mp4"))
    uri = "data:video/mp4;base64," + base64.b64encode(clip.read_bytes()).decode()
    got = _call({**_ASK, "video_url": uri, "duration": round(b - a, 2)})
    raw = out.with_name(out.stem + ".raw.wav")
    urllib.request.urlretrieve(got["audio"][0]["url"], raw)
    clean = without_voice(raw, out.parent / "separated")  # the model's grunts and babble are not ours
    if clean is None:
        # never lay the raw take: its babble reads as a second voice under the cast (the Tanya short)
        raw.unlink(missing_ok=True)
        raise RuntimeError("foley: the vocal separator failed; the take is not laid with its voices in it")
    clean.replace(out)
    for leftover in (clip, raw):
        leftover.unlink(missing_ok=True)


def lay(plan: dict[str, Any], files: list[tuple[Path, float, float]], gain: float) -> None:
    """The foley windows as file sources and placements; earlier foley_* entries replaced."""
    sound = plan.setdefault("sound", {})
    sound["sources"] = [s for s in sound.get("sources") or [] if not s["id"].startswith("foley_")]
    sound["placements"] = [p for p in sound.get("placements") or [] if not p["source"].startswith("foley_")]
    for n, (path, a, b) in enumerate(files):
        sid = f"foley_{n:03d}"
        sound["sources"].append({"id": sid, "kind": "file", "path": str(path)})
        sound["placements"].append({"source": sid, "at": round(a, 3), "length": round(b - a, 3), "gain_db": gain,
                                    "duck": False, "fade_in": 0.08, "fade_out": 0.08})


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    from .. import config

    config.load_all_providers()
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    out = args.plan_file.parent
    parts = dict(json.loads((out / "trailer.picture.json").read_text(encoding="utf-8"))["parts"])
    home = out / "sound" / "foley"
    home.mkdir(parents=True, exist_ok=True)
    plan_w = [(w, home / f"{_key(w, parts)}.wav", *_span(w)) for w in windows(plan)]
    todo = [(w, f, a, b) for w, f, a, b in plan_w if not f.is_file()]
    seconds = sum(b - a for _, _, a, b in todo)
    print(f"Foley: {len(plan_w)} window(s), {len(todo)} to make, {seconds:.0f} s ≈ ${seconds * PRICE_PER_SECOND:.2f}")
    if args.dry_run:
        return 0
    for w, f, a, b in todo:
        _make(out / "trailer.mp4", a, b, f)
        print(f"  {w[0]['label']}..{w[-1]['label']}  {b - a:.1f} s", file=sys.stderr)
    lay(plan, [(f, a, b) for _, f, a, b in plan_w], args.gain)
    args.plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
