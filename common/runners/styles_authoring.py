"""Style authoring — creating, locating and reporting on style files.

Split out of styles.py, which had grown past the module-size gate. styles.py
answers "load me a style"; this answers "where does a style live, and how do I
start a new one". Both halves are re-exported from styles, so
`styles_mod.copy_template(...)` keeps working.

The user directory always wins over the bundled one. That is the whole point of
the override mechanism, and resolution_status() exists so a CLI can tell the
user which copy they are actually editing.
"""

from __future__ import annotations

import re
from pathlib import Path

from .styles import _BUNDLED_DIR, _USER_DIR, Modality

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def template_path(modality: Modality, *, library_root: Path | None = None) -> Path:
    """Path to the bundled _template.md for a modality."""
    root = library_root or _BUNDLED_DIR
    return root / modality / "_template.md"


def copy_template(
    modality: Modality,
    new_id: str,
    *,
    user_dir: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Copy `<modality>/_template.md` to `<user_dir>/<modality>/<new_id>.md`,
    replacing the `<ID>` and `<modality>` placeholders.

    Returns the path of the newly created user-override file.
    Raises FileExistsError if the target exists and overwrite=False.
    Raises FileNotFoundError if the template doesn't exist.
    Raises ValueError if new_id isn't kebab-case.
    """
    if not _KEBAB_ID_RE.fullmatch(new_id):
        raise ValueError(f"id '{new_id}' must match ^[a-z][a-z0-9-]{{1,40}}$ (kebab-case)")

    tpl = template_path(modality)
    if not tpl.is_file():
        raise FileNotFoundError(f"no template for modality '{modality}' at {tpl}")

    user_root = user_dir or (Path.home() / ".claude" / "style-library")
    target = user_root / modality / f"{new_id}.md"

    if target.exists() and not overwrite:
        raise FileExistsError(f"style already exists at {target} (use overwrite=True to replace)")

    target.parent.mkdir(parents=True, exist_ok=True)
    body = tpl.read_text(encoding="utf-8")
    body = body.replace("<ID>", new_id).replace("<MODALITY>", modality)
    target.write_text(body, encoding="utf-8")
    return target


def copy_existing(
    source_id: str,
    new_id: str,
    modality: Modality,
    *,
    user_dir: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Copy an existing bundled style as a starting point for a new user style.

    Frontmatter `id` is rewritten to `new_id`. Display name gets a TODO suffix.
    """
    if not _KEBAB_ID_RE.fullmatch(new_id):
        raise ValueError(f"id '{new_id}' must match ^[a-z][a-z0-9-]{{1,40}}$ (kebab-case)")

    source = _default_library.load(source_id, modality)

    user_root = user_dir or (Path.home() / ".claude" / "style-library")
    target = user_root / modality / f"{new_id}.md"
    if target.exists() and not overwrite:
        raise FileExistsError(f"style already exists at {target} (use overwrite=True to replace)")

    text = source.source_path.read_text(encoding="utf-8")
    text = re.sub(r"^id:\s*.*$", f"id: {new_id}", text, count=1, flags=re.MULTILINE)
    text = re.sub(
        r'^display:\s*"(.+)"$',
        lambda m: f'display: "{m.group(1)} (custom)"',
        text,
        count=1,
        flags=re.MULTILINE,
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def resolution_status(style_id: str, modality: Modality) -> str:
    """Return one of: 'user-only' / 'override' / 'bundled' / 'missing'.

    - user-only: exists ONLY in user dir
    - override:  exists in both (user dir shadows bundled)
    - bundled:   exists ONLY in bundled
    - missing:   nowhere
    """
    user_path = _USER_DIR / modality / f"{style_id}.md"
    bundled_path = _BUNDLED_DIR / modality / f"{style_id}.md"
    user_exists = user_path.is_file()
    bundled_exists = bundled_path.is_file()
    if user_exists and bundled_exists:
        return "override"
    if user_exists:
        return "user-only"
    if bundled_exists:
        return "bundled"
    return "missing"


def resolved_path(style_id: str, modality: Modality) -> Path | None:
    """Return the actual file path the loader will use (user wins over bundled)."""
    user_path = _USER_DIR / modality / f"{style_id}.md"
    if user_path.is_file():
        return user_path
    bundled = _BUNDLED_DIR / modality / f"{style_id}.md"
    return bundled if bundled.is_file() else None


def bundled_dir() -> Path:
    return _BUNDLED_DIR


def user_dir() -> Path:
    return _USER_DIR
