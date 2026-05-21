#!/usr/bin/env python3
"""image-prompt execute entry — delegates to common.runners.cli.image.

Resolves PYTHONPATH from this script's location so it works whether the skill
collection is installed at ~/.claude/skills/ or run directly from the repo.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Find the directory containing `common/` — walk up from this script.
HERE = Path(__file__).resolve()
for parent in HERE.parents:
    if (parent / "common" / "runners").is_dir():
        sys.path.insert(0, str(parent))
        break
else:
    sys.stderr.write(
        "ERROR: cannot locate common/runners. Did you run install.sh?\n"
    )
    sys.exit(1)

from common.runners.cli import image  # noqa: E402

if __name__ == "__main__":
    sys.exit(image.main())
