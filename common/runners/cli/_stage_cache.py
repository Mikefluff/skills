"""What a pipeline stage already made, and from what — so a rerun redoes only the outputs whose inputs moved.

Each stage keeps one small JSON of stamps (output name → the key of the inputs it was made from) beside its
outputs. An output is reused when its file is on disk and its stamp equals the key of its inputs now; a file's
part of a key is its path, size and mtime, so a file rewritten with new content (or touched) counts as changed.
"""

from __future__ import annotations

import atexit
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from ..atomicfile import write_text


def file_sig(path: Path | str) -> list[Any]:
    """A file's part of a key: its path, size and mtime (None when it is not on disk)."""
    p = Path(path)
    if not p.is_file():
        return [str(p), None]
    st = p.stat()
    return [str(p), st.st_size, st.st_mtime_ns]


def key(*parts: Any) -> str:
    """A short hash of everything an output is made from."""
    raw = json.dumps(parts, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def write_if_changed(path: Path, text: str) -> bool:
    """Write `text` atomically unless the file already holds it; True when written. Leaves the mtime of an
    unchanged file alone, so whatever keys on it is not invalidated by a rerun that changed nothing."""
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    write_text(path, text)
    return True


def save_json(path: Path, data: Any) -> bool:
    """A plan (or any JSON) written the way the stages write plan.json, only when it changed."""
    return write_if_changed(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


class Stamps:
    """name → key of the inputs that output was made from, kept in one JSON file."""

    def __init__(self, path: Path):
        self.path = path
        try:
            self.data: dict[str, str] = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        except ValueError:
            self.data = {}

    def fresh(self, name: str, stamp: str, out: Path) -> bool:
        """True when `out` is on disk and was made from inputs with this key."""
        return self.data.get(name) == stamp and out.is_file()

    def set(self, name: str, stamp: str) -> None:
        self.data[name] = stamp

    def save(self) -> None:
        write_if_changed(self.path, json.dumps(self.data, indent=1, sort_keys=True) + "\n")


def run_once(cmd: list[str], output: Path) -> bool:
    """Run an ffmpeg command unless `output` was made by this very command from these very input files and is
    untouched since (stamps beside it); True when it ran. A mix whose voices, sounds and graph did not move is
    not mixed again."""
    import subprocess

    stamps = Stamps(output.parent / "made.json")
    made = key([file_sig(a) if flag == "-i" and Path(a).is_file() else a for flag, a in zip(["", *cmd], cmd)])
    if output.is_file() and stamps.data.get(output.name) == key(made, file_sig(output)):
        return False
    subprocess.run(cmd, check=True, capture_output=True)
    if output.is_file():
        stamps.set(output.name, key(made, file_sig(output)))
        stamps.save()
    return True


_PROBED: dict[str, Any] = {}
_NEW: dict[str, Any] = {}
_PROBE_FILE = Path(os.environ.get("SKILLS_PROBE_CACHE") or Path.home() / ".cache" / "skills" / "probed.json")


def probed(path: Path, probe: Any) -> Any:
    """`probe(path)` (a length, whether it has sound), asked once per version of the file: kept across runs in
    ~/.cache/skills/probed.json ($SKILLS_PROBE_CACHE), keyed by the probe, the path, its mtime and size."""
    module, qual = getattr(probe, "__module__", None), getattr(probe, "__qualname__", None)
    name = f"{module}.{qual}"
    if not (path.is_file() and isinstance(module, str) and isinstance(qual, str)):
        return probe(path)  # a probe without a name (a test's stand-in) is never kept
    if not _PROBED:
        _PROBED.update(_load_probes())
    st = path.stat()
    stamp = key(name, str(path.resolve()), st.st_mtime_ns, st.st_size)
    if stamp not in _PROBED:
        _PROBED[stamp] = probe(path)
        if isinstance(_PROBED[stamp], (bool, int, float)):
            _NEW[stamp] = _PROBED[stamp]
    return _PROBED[stamp]


def _load_probes() -> dict[str, Any]:
    try:
        return json.loads(_PROBE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


@atexit.register
def _save_probes() -> None:
    if _NEW:
        _PROBE_FILE.parent.mkdir(parents=True, exist_ok=True)
        write_text(_PROBE_FILE, json.dumps({**_load_probes(), **_NEW}, sort_keys=True) + "\n")
        _NEW.clear()
