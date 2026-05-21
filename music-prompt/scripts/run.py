#!/usr/bin/env python3
"""music-prompt execute entry — delegates to common.runners.cli.music."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
for parent in HERE.parents:
    if (parent / "common" / "runners").is_dir():
        sys.path.insert(0, str(parent))
        break
else:
    sys.stderr.write("ERROR: cannot locate common/runners. Did you run install.sh?\n")
    sys.exit(1)

from common.runners.cli import music  # noqa: E402

if __name__ == "__main__":
    sys.exit(music.main())
