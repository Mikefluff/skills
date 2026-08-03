"""Atomic writes for files that hold secrets.

Both credential stores need identical semantics — never leave a truncated file
behind, never widen permissions, never leave a readable temp file lying around
if the write fails:

  ~/.skills.env          keysfile.py  — long-lived app keys, KEY=VALUE
  ~/.skills-tokens.json  tokens.py    — short-lived OAuth tokens, JSON

mkstemp() creates with 0600 already; the explicit chmod guards against an
inherited umask on exotic filesystems, and os.replace() preserves the mode.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

SECRET_MODE = 0o600


def write_secret_text(path: Path, content: str) -> None:
    """Write `content` to `path` atomically with 0600 permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.chmod(tmp_path, SECRET_MODE)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def ensure_secure_perms(path: Path) -> None:
    """Best-effort chmod 600. Silent on failure — never break a runner over it."""
    if path.is_file():
        try:
            path.chmod(SECRET_MODE)
        except OSError:
            pass
