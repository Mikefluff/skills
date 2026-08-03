"""~/.skills.env — managed key store for runners.

Plaintext `KEY=VALUE` lines, chmod 600. Loaded into os.environ at runner
startup so providers see the keys without the user having to `source` the
file in their shell.

Precedence: explicit shell export > ~/.skills.env > unset.

The file is NEVER read by `os.environ` directly — only loaded via
load_into_env() at runner start. CLI mutations (add/remove/update) edit
the file in place atomically.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from . import atomicfile

KEYS_FILE = Path(os.environ.get("SKILLS_KEYS_FILE", str(Path.home() / ".skills.env")))
_KV_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=\s*(.*)$")


@dataclass
class KeyEntry:
    name: str
    value: str

    def masked(self) -> str:
        return mask(self.value)


def mask(value: str | None) -> str:
    """Return a redacted representation safe to print."""
    if not value:
        return "(unset)"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}…{value[-4:]}"


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in {'"', "'"}:
        return s[1:-1]
    return s


def ensure_secure_perms() -> None:
    atomicfile.ensure_secure_perms(KEYS_FILE)


def read_all() -> list[KeyEntry]:
    """Parse the file. Preserves order. Skips comments + blank lines."""
    if not KEYS_FILE.is_file():
        return []
    out: list[KeyEntry] = []
    for line in KEYS_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = _KV_RE.match(stripped)
        if not m:
            continue
        out.append(KeyEntry(name=m.group(1), value=_strip_quotes(m.group(2))))
    return out


def get(name: str) -> str | None:
    for entry in read_all():
        if entry.name == name:
            return entry.value
    return None


def upsert(name: str, value: str) -> bool:
    """Write the key, replacing any existing entry. Returns True if new, False if replaced."""
    name = name.strip()
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
        raise ValueError(f"invalid env var name: {name!r} (must match ^[A-Z][A-Z0-9_]*$)")
    value = value.strip()
    KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing_lines: list[str] = []
    if KEYS_FILE.is_file():
        existing_lines = KEYS_FILE.read_text(encoding="utf-8").splitlines()
    replaced = False
    new_lines: list[str] = []
    for line in existing_lines:
        m = _KV_RE.match(line.strip())
        if m and m.group(1) == name:
            new_lines.append(f"{name}={value}")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        if new_lines and not new_lines[-1].strip().startswith("#") and new_lines[-1].strip():
            new_lines.append("")
        # Group by family with a header on first add
        new_lines.append(f"{name}={value}")
    _atomic_write("\n".join(new_lines) + "\n")
    ensure_secure_perms()
    return not replaced


def remove(name: str) -> bool:
    """Delete the entry. Returns True if removed, False if absent."""
    if not KEYS_FILE.is_file():
        return False
    lines = KEYS_FILE.read_text(encoding="utf-8").splitlines()
    new_lines = []
    removed = False
    for line in lines:
        m = _KV_RE.match(line.strip())
        if m and m.group(1) == name:
            removed = True
            continue
        new_lines.append(line)
    if removed:
        _atomic_write("\n".join(new_lines) + ("\n" if new_lines else ""))
        ensure_secure_perms()
    return removed


def load_into_env(*, override: bool = False) -> int:
    """Load entries from ~/.skills.env into os.environ.

    By default, an existing os.environ value WINS (shell exports take priority
    over file entries). Pass override=True to force the file's value.

    Returns the count of variables loaded.
    """
    count = 0
    for entry in read_all():
        if entry.name in os.environ and not override:
            continue
        if entry.value:
            os.environ[entry.name] = entry.value
            count += 1
    return count


def _atomic_write(content: str) -> None:
    """Write KEYS_FILE atomically (write to temp + rename)."""
    atomicfile.write_secret_text(KEYS_FILE, content)


def export_lines(*, mask_values: bool = False) -> list[str]:
    """Return shell-export lines for the current file. eval-able when not masked."""
    lines: list[str] = []
    for entry in read_all():
        val = mask(entry.value) if mask_values else entry.value
        # Quote with double quotes; escape inner double-quotes
        safe = val.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'export {entry.name}="{safe}"')
    return lines
