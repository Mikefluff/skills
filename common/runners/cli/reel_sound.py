"""Sound-only pass of a voiced film — hear the soundtrack before paying for the picture.

  python3 -m common.runners.cli.reel_sound --plan-file <out>/plan.json [--picture <out>/picture.mp4]

Generates the plan's `sound` sources (or reuses ones already on disk), mixes
them with the voiceover, masters, and writes `<out>/soundtrack.wav`. With
`--picture`, hits marked `snap` move onto the frames where the picture flashes
and the result is muxed to `<out>/final-sound.mp4` — the way to re-mix a
finished film after editing placements, without regenerating anything.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .. import config
from .. import cost as cost_mod
from .. import ffmpeg_film
from ..errors import CostConfirmationDeclined
from . import _reel_sound


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_sound")
    parser.add_argument("--plan-file", type=Path, required=True, help="path to plan.json with a sound block")
    parser.add_argument("--picture", type=Path, help="finished picture to snap hits to and mux with")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_providers()
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    sound, voice = plan.get("sound"), Path((plan.get("voiceover") or {}).get("path") or "")
    if not sound or not voice.is_file():
        print("plan needs a `sound` block and an existing `voiceover.path`", file=sys.stderr)
        return 2
    out = Path(plan.get("output_dir") or args.plan_file.parent)
    try:
        cost_mod.confirm_batch(_reel_sound.estimate(sound), n_items=len(sound.get("sources") or []),
                               modality="sound", yes=args.yes)
        sources = _reel_sound.generate(sound, out, resume=True)
        soundtrack = _reel_sound.render(sound, sources, voice, out / "soundtrack.wav", args.picture)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.picture:
        final = out / "final-sound.mp4"
        ffmpeg_film.mux(args.picture, soundtrack, final)
        print(str(final))
    else:
        print(str(soundtrack))
    return 0


if __name__ == "__main__":
    sys.exit(main())
