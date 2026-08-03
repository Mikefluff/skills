"""Atomic writes — never leave a truncated file behind.

Two callers, two reasons.

The credential stores need identical semantics and 0600 on top of it:

  ~/.skills.env          keysfile.py  — long-lived app keys, KEY=VALUE
  ~/.skills-tokens.json  tokens.py    — short-lived OAuth tokens, JSON

mkstemp() creates with 0600 already; the explicit chmod guards against an
inherited umask on exotic filesystems, and os.replace() preserves the mode.

The batch manifest needs the atomicity and not the permissions — it is an
artifact the user reads, and it is rewritten after every item so that a crash
is survivable. Written non-atomically, a crash during the write leaves a
half-file and the next --resume cannot parse it, which defeats the feature in
the one situation it exists for.
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


def write_text(path: Path, content: str) -> None:
    """Write `content` to `path` atomically, with ordinary permissions.

    Same replace-in-place guarantee as write_secret_text, without forcing 0600
    — this is for artifacts, not credentials. The temp file is created 0600 by
    mkstemp and relaxed to whatever the umask would have given a normal write,
    so a reader's permissions are not surprising.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.chmod(tmp_path, 0o666 & ~_umask())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _umask() -> int:
    """Read the process umask without leaving it changed."""
    current = os.umask(0)
    os.umask(current)
    return current


def ensure_secure_perms(path: Path) -> None:
    """Best-effort chmod 600. Silent on failure — never break a runner over it."""
    if path.is_file():
        try:
            path.chmod(SECRET_MODE)
        except OSError:
            pass
