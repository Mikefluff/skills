"""Background removal CLI — calls the Replicate router with a bg-removal model.

Single image in, transparent PNG out. No batch (use a shell loop for batch).

Default model: 851-labs/background-remover (popular Replicate model).
Override via --replicate-model <user>/<model>.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import _tool

DEFAULT_REPLICATE_MODEL = "851-labs/background-remover"

OUTPUT = _tool.ToolOutput(
    directory=Path("./generated/bg-removed"),
    suffix="-nobg",
    verb="Background removed",
)


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.bg")
    _tool.add_common_arguments(parser, "./generated/bg-removed/<stem>-nobg.png")
    parser.add_argument(
        "--replicate-model",
        default=DEFAULT_REPLICATE_MODEL,
        help=f"Replicate model id (default: {DEFAULT_REPLICATE_MODEL})",
    )
    args = parser.parse_args()

    provider = _tool.resolve_provider("replicate-image")
    if provider is None:
        return 2

    early = _tool.preflight(
        provider, args,
        ready_line="OK: replicate-image configured. Run without --check to remove background.",
        cost_line="estimated cost: ~$0.001-0.005 per image (Replicate bg-removal models)",
    )
    if early is not None:
        return early

    print(
        f"Removing background via Replicate model '{args.replicate_model}' ...",
        file=sys.stderr,
    )
    kwargs = {
        "replicate_model": args.replicate_model,
        "image_url": args.image,
        "variants": 1,
    }
    return _tool.run(provider, "", kwargs, args, OUTPUT)


if __name__ == "__main__":
    sys.exit(main())
