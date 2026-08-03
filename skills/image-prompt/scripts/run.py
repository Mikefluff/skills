#!/usr/bin/env python3
"""image-prompt execute entry — delegates to common.runners.cli.image.

Auto-discovery:
1. Walks up to find the dir containing `common/runners/`.
2. If a sibling `.runners-venv/` exists (created by install.sh), re-execs via
   that venv's python so vendor SDK deps are available without a manual pip
   install. Falls through to the current interpreter otherwise.
"""

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

# If install.sh created a venv next to runners, re-exec via that interpreter
# so the user doesn't need to `pip install` separately.
_VENV_PY = ROOT / ".runners-venv" / "bin" / "python3"
if _VENV_PY.exists() and sys.executable != str(_VENV_PY):
    os.execv(str(_VENV_PY), [str(_VENV_PY), str(HERE), *sys.argv[1:]])

sys.path.insert(0, str(ROOT))
from common.runners.cli import image  # noqa: E402

if __name__ == "__main__":
    sys.exit(image.main())
