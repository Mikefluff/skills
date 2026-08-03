#!/usr/bin/env python3
"""gif-maker entry — delegates to common.runners.cli.gif."""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT: Path | None = None
for parent in HERE.parents:
    if (parent / "common" / "runners").is_dir():
        ROOT = parent
        break

if ROOT is None:
    sys.stderr.write("ERROR: cannot locate common/runners. Did you run install.sh?\n")
    sys.exit(1)

_VENV_PY = ROOT / ".runners-venv" / "bin" / "python3"
if _VENV_PY.exists() and sys.executable != str(_VENV_PY):
    os.execv(str(_VENV_PY), [str(_VENV_PY), str(HERE), *sys.argv[1:]])

sys.path.insert(0, str(ROOT))
from common.runners.cli import gif  # noqa: E402

if __name__ == "__main__":
    sys.exit(gif.main())
