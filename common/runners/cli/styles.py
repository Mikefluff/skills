"""Styles CLI — manage the local style library.

Subcommands:

  list [<modality>] [--user-only|--bundled-only]
                              List styles. Status: bundled / user-only / override.
  show <modality> <id>        Print the style file (resolved — user wins).
  add <modality> <id>         Create a new user style from the bundled template.
  add <modality> <id> --from <existing-id>
                              Create a new user style as a copy of an existing one.
  edit <modality> <id>        Open the user-override file in $EDITOR.
  remove <modality> <id>      Delete the user-override (bundled, if any, is untouched).
  validate <modality> <id>    Frontmatter + body schema check.
  diff <modality> <id>        Compare user-override against the bundled version.
  path [<modality>] [<id>]    Print resolved path(s).
  submit <modality> <id>      Build an upstream-PR submission package under
                              ./style-submission-<timestamp>/

Layout:
  bundled : <repo>/common/style-library/<modality>/<id>.md
  user    : ~/.claude/style-library/<modality>/<id>.md
"""

from __future__ import annotations

import argparse
import difflib
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .. import styles as styles_mod
from .. import styles_authoring
from .. import styles_validate
from ..styles import Modality
from ._styles_submit import _cmd_submit


_VALID_MODALITIES: tuple[Modality, ...] = ("carousel", "video", "music")


def _modality_arg(parser: argparse.ArgumentParser, *, optional: bool = False) -> None:
    if optional:
        parser.add_argument("modality", nargs="?", choices=_VALID_MODALITIES, default=None)
    else:
        parser.add_argument("modality", choices=_VALID_MODALITIES)


def _id_arg(parser: argparse.ArgumentParser, *, optional: bool = False) -> None:
    if optional:
        parser.add_argument("style_id", nargs="?", default=None)
    else:
        parser.add_argument("style_id")


_STATUS_MARKER = {
    "bundled":   "\033[2m·\033[0m bundled    ",
    "user-only": "\033[32m+\033[0m user-only ",
    "override":  "\033[33m*\033[0m override   ",
    "missing":   "  missing    ",
}


def _ids_in(directory: Path) -> set[str]:
    """Style ids in one modality directory. `_template.md` and READMEs are not styles."""
    if not directory.is_dir():
        return set()
    return {
        p.stem for p in directory.glob("*.md")
        if not p.name.startswith("_") and p.name.lower() != "readme.md"
    }


def _listed_ids(modality: str, args: argparse.Namespace) -> list[str]:
    bundled = _ids_in(styles_authoring.bundled_dir() / modality)
    user = _ids_in(styles_authoring.user_dir() / modality)
    if args.user_only:
        return sorted(user)
    if args.bundled_only:
        return sorted(bundled)
    return sorted(bundled | user)


def _print_modality(modality: str, ids: list[str]) -> None:
    print(f"# {modality}  ({len(ids)} style(s))")
    print()
    for sid in ids:
        status = styles_authoring.resolution_status(sid, modality)
        try:
            display = styles_mod.load_style(sid, modality).display
        except Exception:  # noqa: BLE001 — one broken file must not hide the list
            display = "(parse error)"
        print(f"  {_STATUS_MARKER.get(status, status)}  {sid:<32s}  {display}")
    print()


def _print_empty_hint(args: argparse.Namespace) -> None:
    if args.user_only:
        print(f"(no user-override styles in {styles_authoring.user_dir()})")
        print()
        print("Add one with:  skills-styles add <modality> <id>")
    elif args.bundled_only:
        print(f"(no bundled styles in {styles_authoring.bundled_dir()})")
    else:
        print("(no styles found)")


def _cmd_list(args: argparse.Namespace) -> int:
    modalities = [args.modality] if args.modality else list(_VALID_MODALITIES)
    printed = False
    for mod in modalities:
        ids = _listed_ids(mod, args)
        if not ids:
            continue
        printed = True
        _print_modality(mod, ids)
    if not printed:
        _print_empty_hint(args)
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    path = styles_authoring.resolved_path(args.style_id, args.modality)
    if path is None:
        print(f"  ✗ style not found: {args.modality}/{args.style_id}", file=sys.stderr)
        return 2
    status = styles_authoring.resolution_status(args.style_id, args.modality)
    print(f"# {path}  [{status}]")
    print()
    print(path.read_text(encoding="utf-8"), end="")
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    try:
        if args.source_id:
            target = styles_authoring.copy_existing(
                args.source_id, args.style_id, args.modality, overwrite=args.force
            )
            origin = f"copy of bundled '{args.source_id}'"
        else:
            target = styles_authoring.copy_template(
                args.modality, args.style_id, overwrite=args.force
            )
            origin = "from template"
    except FileExistsError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        print("    use --force to overwrite", file=sys.stderr)
        return 2
    except (FileNotFoundError, ValueError) as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2

    print(f"  ✓ Created {args.modality}/{args.style_id}.md  ({origin})")
    print(f"    Path: {target}")
    print(f"    Next: skills-styles edit {args.modality} {args.style_id}")
    print(f"    Then: skills-styles validate {args.modality} {args.style_id}")
    return 0


def _cmd_edit(args: argparse.Namespace) -> int:
    user_path = styles_authoring.user_dir() / args.modality / f"{args.style_id}.md"
    if not user_path.is_file():
        # Maybe it's a bundled style — offer to override
        bundled = styles_authoring.bundled_dir() / args.modality / f"{args.style_id}.md"
        if bundled.is_file():
            print(f"  · '{args.style_id}' is currently bundled-only.", file=sys.stderr)
            print(f"    To customize, create a user override:", file=sys.stderr)
            print(f"      skills-styles add {args.modality} {args.style_id} --from {args.style_id}", file=sys.stderr)
            return 2
        print(f"  ✗ style not found: {args.modality}/{args.style_id}", file=sys.stderr)
        return 2

    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if not editor:
        # No editor — just print the path so user can open manually
        print(f"  · $EDITOR not set. Open manually: {user_path}", file=sys.stderr)
        return 0
    try:
        subprocess.run([editor, str(user_path)], check=True)
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"  ✗ editor failed: {exc}", file=sys.stderr)
        return 1
    print(f"  ✓ Edited {user_path}")
    print(f"    Next: skills-styles validate {args.modality} {args.style_id}")
    return 0


def _cmd_remove(args: argparse.Namespace) -> int:
    user_path = styles_authoring.user_dir() / args.modality / f"{args.style_id}.md"
    if not user_path.is_file():
        print(f"  · {args.modality}/{args.style_id}: no user-override to remove", file=sys.stderr)
        return 0
    bundled_path = styles_authoring.bundled_dir() / args.modality / f"{args.style_id}.md"
    if not args.force:
        # Show what will happen
        if bundled_path.is_file():
            print(f"  This will remove your override and revert to the bundled '{args.style_id}'.")
        else:
            print(f"  This will delete your user-only style '{args.style_id}'. There is no bundled fallback.")
        print(f"  Use --force to confirm.")
        return 2
    user_path.unlink()
    print(f"  ✓ Removed {user_path}")
    if bundled_path.is_file():
        print(f"    Reverts to bundled: {bundled_path}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        style = styles_mod.load_style(args.style_id, args.modality)
    except FileNotFoundError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2
    issues = styles_validate.validate_style(style)
    status = styles_authoring.resolution_status(args.style_id, args.modality)
    print(f"# {args.modality}/{args.style_id}  [{status}]  ({style.source_path})")
    print()
    if not issues:
        print("  \033[32m✓\033[0m valid — passes all schema checks")
        return 0
    print(f"  \033[31m✗\033[0m {len(issues)} issue(s):")
    for issue in issues:
        print(f"    - {issue}")
    return 1


def _cmd_diff(args: argparse.Namespace) -> int:
    bundled = styles_authoring.bundled_dir() / args.modality / f"{args.style_id}.md"
    user = styles_authoring.user_dir() / args.modality / f"{args.style_id}.md"
    if not user.is_file():
        print(f"  · no user-override for {args.modality}/{args.style_id} — nothing to diff", file=sys.stderr)
        return 0
    if not bundled.is_file():
        print(f"  · no bundled '{args.modality}/{args.style_id}' — this is a user-only style", file=sys.stderr)
        return 0
    diff = difflib.unified_diff(
        bundled.read_text(encoding="utf-8").splitlines(keepends=True),
        user.read_text(encoding="utf-8").splitlines(keepends=True),
        fromfile=f"bundled/{args.modality}/{args.style_id}.md",
        tofile=f"user/{args.modality}/{args.style_id}.md",
        n=3,
    )
    for line in diff:
        sys.stdout.write(line)
    return 0


def _cmd_path(args: argparse.Namespace) -> int:
    if args.style_id:
        path = styles_authoring.resolved_path(args.style_id, args.modality)
        if path is None:
            print(f"  ✗ style not found: {args.modality}/{args.style_id}", file=sys.stderr)
            return 2
        print(path)
        return 0
    if args.modality:
        print(f"bundled: {styles_authoring.bundled_dir() / args.modality}")
        print(f"user:    {styles_authoring.user_dir() / args.modality}")
    else:
        print(f"bundled: {styles_authoring.bundled_dir()}")
        print(f"user:    {styles_authoring.user_dir()}")
    return 0



def _list_flags(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--user-only", action="store_true", help="show only user-overrides")
    group.add_argument("--bundled-only", action="store_true", help="show only bundled styles")


def _add_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--from", dest="source_id", default=None,
        help="copy an existing style as a starting point",
    )
    parser.add_argument("--force", action="store_true", help="overwrite if file exists")


def _remove_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--force", action="store_true", help="confirm deletion")


def _submit_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--force", action="store_true", help="skip validation gate / confirmations"
    )


@dataclass(frozen=True)
class _Sub:
    """One subcommand. Nearly all of them are just <modality> <id> plus a handler."""

    name: str
    help: str
    handler: Callable[[argparse.Namespace], int]
    optional_modality: bool = False
    optional_id: bool = False
    wants_id: bool = True
    extra: Callable[[argparse.ArgumentParser], None] | None = None


# Order here is the order in --help, so it is the order a reader meets them in.
_SUBCOMMANDS: tuple[_Sub, ...] = (
    _Sub("list", "list styles", _cmd_list,
         optional_modality=True, wants_id=False, extra=_list_flags),
    _Sub("show", "print a style file", _cmd_show),
    _Sub("add", "create a new user style from template or copy", _cmd_add, extra=_add_flags),
    _Sub("edit", "open user-override in $EDITOR", _cmd_edit),
    _Sub("remove", "delete a user-override", _cmd_remove, extra=_remove_flags),
    _Sub("validate", "frontmatter + body schema check", _cmd_validate),
    _Sub("diff", "diff user-override vs bundled", _cmd_diff),
    _Sub("path", "print resolved path(s)", _cmd_path,
         optional_modality=True, optional_id=True),
    _Sub("submit", "build an upstream-PR submission package", _cmd_submit, extra=_submit_flags),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="common.runners.cli.styles",
        description="Manage the local style library (bundled + user overrides at ~/.claude/style-library/).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    for spec in _SUBCOMMANDS:
        p = sub.add_parser(spec.name, help=spec.help)
        _modality_arg(p, optional=spec.optional_modality)
        if spec.wants_id:
            _id_arg(p, optional=spec.optional_id)
        if spec.extra is not None:
            spec.extra(p)
        p.set_defaults(func=spec.handler)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
