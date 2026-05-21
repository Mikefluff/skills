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
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .. import styles as styles_mod
from ..styles import Modality


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


def _cmd_list(args: argparse.Namespace) -> int:
    modalities = [args.modality] if args.modality else list(_VALID_MODALITIES)
    bundled_root = styles_mod.bundled_dir()
    user_root = styles_mod.user_dir()
    any_printed = False
    for mod in modalities:
        # Discover all ids in both dirs
        bundled_ids = set()
        if (bundled_root / mod).is_dir():
            bundled_ids = {p.stem for p in (bundled_root / mod).glob("*.md") if not p.name.startswith("_") and p.name.lower() != "readme.md"}
        user_ids = set()
        if (user_root / mod).is_dir():
            user_ids = {p.stem for p in (user_root / mod).glob("*.md") if not p.name.startswith("_") and p.name.lower() != "readme.md"}

        if args.user_only:
            all_ids = sorted(user_ids)
        elif args.bundled_only:
            all_ids = sorted(bundled_ids)
        else:
            all_ids = sorted(bundled_ids | user_ids)

        if not all_ids:
            continue

        any_printed = True
        print(f"# {mod}  ({len(all_ids)} style(s))")
        print()
        for sid in all_ids:
            status = styles_mod.resolution_status(sid, mod)
            marker = {
                "bundled":   "\033[2m·\033[0m bundled    ",
                "user-only": "\033[32m+\033[0m user-only ",
                "override":  "\033[33m*\033[0m override   ",
                "missing":   "  missing    ",
            }.get(status, status)
            try:
                st = styles_mod.load_style(sid, mod)
                display = st.display
            except Exception:  # noqa: BLE001
                display = "(parse error)"
            print(f"  {marker}  {sid:<32s}  {display}")
        print()
    if not any_printed:
        if args.user_only:
            print(f"(no user-override styles in {styles_mod.user_dir()})")
            print()
            print("Add one with:  skills-styles add <modality> <id>")
        elif args.bundled_only:
            print(f"(no bundled styles in {styles_mod.bundled_dir()})")
        else:
            print("(no styles found)")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    path = styles_mod.resolved_path(args.style_id, args.modality)
    if path is None:
        print(f"  ✗ style not found: {args.modality}/{args.style_id}", file=sys.stderr)
        return 2
    status = styles_mod.resolution_status(args.style_id, args.modality)
    print(f"# {path}  [{status}]")
    print()
    print(path.read_text(encoding="utf-8"), end="")
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    try:
        if args.source_id:
            target = styles_mod.copy_existing(
                args.source_id, args.style_id, args.modality, overwrite=args.force
            )
            origin = f"copy of bundled '{args.source_id}'"
        else:
            target = styles_mod.copy_template(
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
    user_path = styles_mod.user_dir() / args.modality / f"{args.style_id}.md"
    if not user_path.is_file():
        # Maybe it's a bundled style — offer to override
        bundled = styles_mod.bundled_dir() / args.modality / f"{args.style_id}.md"
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
    user_path = styles_mod.user_dir() / args.modality / f"{args.style_id}.md"
    if not user_path.is_file():
        print(f"  · {args.modality}/{args.style_id}: no user-override to remove", file=sys.stderr)
        return 0
    bundled_path = styles_mod.bundled_dir() / args.modality / f"{args.style_id}.md"
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
    issues = styles_mod.validate_style(style)
    status = styles_mod.resolution_status(args.style_id, args.modality)
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
    bundled = styles_mod.bundled_dir() / args.modality / f"{args.style_id}.md"
    user = styles_mod.user_dir() / args.modality / f"{args.style_id}.md"
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
        path = styles_mod.resolved_path(args.style_id, args.modality)
        if path is None:
            print(f"  ✗ style not found: {args.modality}/{args.style_id}", file=sys.stderr)
            return 2
        print(path)
        return 0
    if args.modality:
        print(f"bundled: {styles_mod.bundled_dir() / args.modality}")
        print(f"user:    {styles_mod.user_dir() / args.modality}")
    else:
        print(f"bundled: {styles_mod.bundled_dir()}")
        print(f"user:    {styles_mod.user_dir()}")
    return 0


def _cmd_submit(args: argparse.Namespace) -> int:
    # 1. Validate first
    try:
        style = styles_mod.load_style(args.style_id, args.modality)
    except FileNotFoundError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2
    issues = styles_mod.validate_style(style)
    if issues and not args.force:
        print(f"  ✗ style has {len(issues)} validation issue(s):", file=sys.stderr)
        for i in issues:
            print(f"    - {i}", file=sys.stderr)
        print(f"\n  Fix with: skills-styles edit {args.modality} {args.style_id}", file=sys.stderr)
        print(f"  Or pass --force to submit anyway (not recommended).", file=sys.stderr)
        return 2

    # 2. Check this is a user style, not bundled
    status = styles_mod.resolution_status(args.style_id, args.modality)
    if status == "bundled":
        print(f"  · '{args.style_id}' is already in the bundled library — nothing to submit.", file=sys.stderr)
        return 0
    if status == "override":
        print(f"  · '{args.style_id}' is a user override of a bundled style.", file=sys.stderr)
        print(f"    The PR will REPLACE the bundled version. Make sure that's intended.", file=sys.stderr)
        if not args.force and not _confirm("    Continue?"):
            return 0

    source = styles_mod.user_dir() / args.modality / f"{args.style_id}.md"
    if not source.is_file():
        print(f"  ✗ user-override file not found: {source}", file=sys.stderr)
        return 2

    # 3. Build submission package
    ts = time.strftime("%Y%m%d-%H%M%S")
    pkg_dir = Path(f"./style-submission-{ts}-{args.modality}-{args.style_id}").resolve()
    target_in_pkg = pkg_dir / "common" / "style-library" / args.modality / f"{args.style_id}.md"
    target_in_pkg.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target_in_pkg)

    pr_desc = _build_pr_description(style, args.modality, args.style_id, status)
    (pkg_dir / "PR-DESCRIPTION.md").write_text(pr_desc, encoding="utf-8")
    (pkg_dir / "README.md").write_text(_build_submission_readme(args.modality, args.style_id, status), encoding="utf-8")

    print(f"  ✓ Submission package ready: {pkg_dir}")
    print()
    print(f"  Contents:")
    print(f"    common/style-library/{args.modality}/{args.style_id}.md")
    print(f"    PR-DESCRIPTION.md")
    print(f"    README.md  (step-by-step manual PR instructions)")
    print()
    print(f"  Next steps (manual, takes ~2 minutes):")
    print(f"    1. Fork https://github.com/Mikefluff/skills on GitHub")
    print(f"    2. Clone your fork, copy {target_in_pkg} into <fork>/common/style-library/{args.modality}/")
    print(f"    3. git checkout -b style/{args.modality}-{args.style_id}")
    print(f"    4. git add common/style-library/{args.modality}/{args.style_id}.md")
    print(f'    5. git commit -m "feat(style-library): add {args.modality} style \\"{style.display}\\""')
    print(f"    6. git push origin style/{args.modality}-{args.style_id}")
    print(f"    7. gh pr create --body-file {pkg_dir / 'PR-DESCRIPTION.md'}")
    print()
    print(f"  Full step-by-step: cat {pkg_dir / 'README.md'}")
    return 0


def _build_pr_description(style: "styles_mod.Style", modality: str, style_id: str, status: str) -> str:
    action = "replace bundled" if status == "override" else "add"
    return f"""## What

{action.title()} `common/style-library/{modality}/{style_id}.md` ({style.display}).

## Why

<Explain the gap this fills: what use case or aesthetic is currently not served by
any bundled style? What problem does this style solve for the user?>

## Reviewer checklist

- [ ] Frontmatter matches the schema (run `skills-styles validate {modality} {style_id}`)
- [ ] `Style anchor` is model-agnostic (works with all relevant providers)
- [ ] No copyrighted living artist names anywhere in the prompt-facing fields
- [ ] No real-brand mimicry in anchor text
- [ ] Mood + tags don't duplicate existing styles' identity
- [ ] Color palette / typography are concrete (not vibes)
- [ ] Caption tone reads as a one-line directive, not generic advice
- [ ] If `text_friendly: true`, the text-in-image anchor includes typography specs

## Style metadata

- **id**: `{style_id}`
- **display**: {style.display}
- **mood**: {', '.join(style.mood) or '(none)'}
- **tags**: {', '.join(style.tags) or '(none)'}
- **source**: built locally with `skills-styles`

## Sample usage

After this merges, users can apply the style via:

```
carousel-builder --topic "<example>" --style {style_id} --execute
```

(adjust for video / music modality as appropriate)

## Out-of-scope for this PR

- This PR is library-only — no skill behaviour or runner-code changes.
"""


def _build_submission_readme(modality: str, style_id: str, status: str) -> str:
    return f"""# Submission package — {modality}/{style_id}

This directory contains everything you need to submit your style upstream.

## Files

- `common/style-library/{modality}/{style_id}.md` — the style file, at the EXACT path it needs to land in the repo
- `PR-DESCRIPTION.md` — PR body template (fill in the "Why" section)
- `README.md` — this file

## Manual PR submission (2 minutes)

### 1. Fork the repo

Go to https://github.com/Mikefluff/skills and click "Fork".

### 2. Clone your fork

```bash
cd /tmp
git clone https://github.com/<your-username>/skills.git
cd skills
git remote add upstream https://github.com/Mikefluff/skills.git
```

### 3. Sync with upstream

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### 4. Create a branch

```bash
git checkout -b style/{modality}-{style_id}
```

### 5. Copy the style file

From this submission package into the fork:

```bash
cp common/style-library/{modality}/{style_id}.md <path-to-fork>/common/style-library/{modality}/
```

### 6. Verify it loads

```bash
cd <path-to-fork>
bash scripts/validate.sh
```

Should print `validate: OK`.

### 7. Commit

```bash
git add common/style-library/{modality}/{style_id}.md
git commit -m 'feat(style-library): add {modality} style {style_id}'
```

### 8. Push

```bash
git push origin style/{modality}-{style_id}
```

### 9. Open the PR

```bash
gh pr create --title 'feat(style-library): add {modality} style {style_id}' \\
  --body-file ../style-submission-*/PR-DESCRIPTION.md
```

Or open via the GitHub web UI — it'll detect the branch and offer "Compare & pull request".

## Quality bar

PRs are reviewed manually. Things that get a request-for-changes:

- Style anchor too generic / vague (must be specific enough to lock the aesthetic)
- Frontmatter incomplete or types wrong
- Copyrighted living-artist names in any prompt-facing field
- Real-brand mimicry in anchor text ("Apple's WWDC look")
- Duplicate of an existing bundled style with marginal differences
- Hype words ("stunning", "amazing", "revolutionary")

If the style genuinely adds something new (a directorial grammar / aesthetic / genre not covered), it has a high chance of being merged.
"""


def _confirm(prompt: str) -> bool:
    if not sys.stdin.isatty():
        return False
    sys.stderr.write(f"{prompt} [y/N] ")
    sys.stderr.flush()
    ans = sys.stdin.readline().strip().lower()
    return ans in {"y", "yes"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="common.runners.cli.styles",
        description="Manage the local style library (bundled + user overrides at ~/.claude/style-library/).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list styles")
    _modality_arg(p_list, optional=True)
    group = p_list.add_mutually_exclusive_group()
    group.add_argument("--user-only", action="store_true", help="show only user-overrides")
    group.add_argument("--bundled-only", action="store_true", help="show only bundled styles")
    p_list.set_defaults(func=_cmd_list)

    p_show = sub.add_parser("show", help="print a style file")
    _modality_arg(p_show)
    _id_arg(p_show)
    p_show.set_defaults(func=_cmd_show)

    p_add = sub.add_parser("add", help="create a new user style from template or copy")
    _modality_arg(p_add)
    _id_arg(p_add)
    p_add.add_argument("--from", dest="source_id", default=None, help="copy an existing style as a starting point")
    p_add.add_argument("--force", action="store_true", help="overwrite if file exists")
    p_add.set_defaults(func=_cmd_add)

    p_edit = sub.add_parser("edit", help="open user-override in $EDITOR")
    _modality_arg(p_edit)
    _id_arg(p_edit)
    p_edit.set_defaults(func=_cmd_edit)

    p_remove = sub.add_parser("remove", help="delete a user-override")
    _modality_arg(p_remove)
    _id_arg(p_remove)
    p_remove.add_argument("--force", action="store_true", help="confirm deletion")
    p_remove.set_defaults(func=_cmd_remove)

    p_validate = sub.add_parser("validate", help="frontmatter + body schema check")
    _modality_arg(p_validate)
    _id_arg(p_validate)
    p_validate.set_defaults(func=_cmd_validate)

    p_diff = sub.add_parser("diff", help="diff user-override vs bundled")
    _modality_arg(p_diff)
    _id_arg(p_diff)
    p_diff.set_defaults(func=_cmd_diff)

    p_path = sub.add_parser("path", help="print resolved path(s)")
    _modality_arg(p_path, optional=True)
    _id_arg(p_path, optional=True)
    p_path.set_defaults(func=_cmd_path)

    p_submit = sub.add_parser("submit", help="build an upstream-PR submission package")
    _modality_arg(p_submit)
    _id_arg(p_submit)
    p_submit.add_argument("--force", action="store_true", help="skip validation gate / confirmations")
    p_submit.set_defaults(func=_cmd_submit)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
