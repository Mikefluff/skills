"""Style submission — package a user style for an upstream pull request.

Split out of cli/styles.py, which had grown past the module-size gate. This is
the one subcommand that reaches outside the machine: it produces a directory a
user hand-carries to GitHub, so most of its weight is the prose telling them
how. That prose lives in the two templates below rather than inside the
functions that fill them in.

Nothing here talks to the network. The package is written to the working
directory and the user drives git themselves — a style submission is not
something a CLI should do behind someone's back.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

from .. import styles as styles_mod
from .. import styles_authoring
from .. import styles_validate

def _preflight(args: argparse.Namespace) -> tuple["styles_mod.Style", str] | int:
    """Validate and locate the style. Returns (style, status) or an exit code.

    A style is validated before packaging because the reviewer on the other end
    would otherwise be the one to find the problem, days later.
    """
    try:
        style = styles_mod.load_style(args.style_id, args.modality)
    except FileNotFoundError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2

    issues = styles_validate.validate_style(style)
    if issues and not args.force:
        print(f"  ✗ style has {len(issues)} validation issue(s):", file=sys.stderr)
        for issue in issues:
            print(f"    - {issue}", file=sys.stderr)
        print(f"\n  Fix with: skills-styles edit {args.modality} {args.style_id}", file=sys.stderr)
        print("  Or pass --force to submit anyway (not recommended).", file=sys.stderr)
        return 2

    status = styles_authoring.resolution_status(args.style_id, args.modality)
    if status == "bundled":
        print(
            f"  · '{args.style_id}' is already in the bundled library — nothing to submit.",
            file=sys.stderr,
        )
        return 0
    if status == "override":
        print(f"  · '{args.style_id}' is a user override of a bundled style.", file=sys.stderr)
        print("    The PR will REPLACE the bundled version. Make sure that's intended.", file=sys.stderr)
        if not args.force and not _confirm("    Continue?"):
            return 0
    return style, status


def _write_package(style: "styles_mod.Style", args: argparse.Namespace,
                   status: str, source: Path) -> tuple[Path, Path]:
    """Write the package. Returns (package dir, the style file inside it)."""
    stamp = time.strftime("%Y%m%d-%H%M%S")
    pkg_dir = Path(f"./style-submission-{stamp}-{args.modality}-{args.style_id}").resolve()
    target = pkg_dir / "common" / "style-library" / args.modality / f"{args.style_id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)

    (pkg_dir / "PR-DESCRIPTION.md").write_text(
        _build_pr_description(style, args.modality, args.style_id, status), encoding="utf-8"
    )
    (pkg_dir / "README.md").write_text(
        _build_submission_readme(args.modality, args.style_id), encoding="utf-8"
    )
    return pkg_dir, target


def _print_next_steps(style: "styles_mod.Style", args: argparse.Namespace,
                      pkg_dir: Path, target: Path) -> None:
    print(f"  ✓ Submission package ready: {pkg_dir}")
    print()
    print("  Contents:")
    print(f"    common/style-library/{args.modality}/{args.style_id}.md")
    print("    PR-DESCRIPTION.md")
    print("    README.md  (step-by-step manual PR instructions)")
    print()
    print("  Next steps (manual, takes ~2 minutes):")
    print("    1. Fork https://github.com/Mikefluff/skills on GitHub")
    print(f"    2. Clone your fork, copy {target} into <fork>/common/style-library/{args.modality}/")
    print(f"    3. git checkout -b style/{args.modality}-{args.style_id}")
    print(f"    4. git add common/style-library/{args.modality}/{args.style_id}.md")
    print(f'    5. git commit -m "feat(style-library): add {args.modality} style \\"{style.display}\\""')
    print(f"    6. git push origin style/{args.modality}-{args.style_id}")
    print(f"    7. gh pr create --body-file {pkg_dir / 'PR-DESCRIPTION.md'}")
    print()
    print(f"  Full step-by-step: cat {pkg_dir / 'README.md'}")


def _cmd_submit(args: argparse.Namespace) -> int:
    checked = _preflight(args)
    if isinstance(checked, int):
        return checked
    style, status = checked

    source = styles_authoring.user_dir() / args.modality / f"{args.style_id}.md"
    if not source.is_file():
        print(f"  ✗ user-override file not found: {source}", file=sys.stderr)
        return 2

    pkg_dir, target = _write_package(style, args, status, source)
    _print_next_steps(style, args, pkg_dir, target)
    return 0


_PR_DESCRIPTION = """\
## What

{action_title} `common/style-library/{modality}/{style_id}.md` ({display}).

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
- **display**: {display}
- **mood**: {moods}
- **tags**: {tags}
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


def _build_pr_description(style: "styles_mod.Style", modality: str, style_id: str, status: str) -> str:
    """PR body. The "Why" section is deliberately left for the human to fill in."""
    return _PR_DESCRIPTION.format(
        action_title="Replace bundled" if status == "override" else "Add",
        modality=modality,
        style_id=style_id,
        display=style.display,
        moods=", ".join(style.mood) or "(none)",
        tags=", ".join(style.tags) or "(none)",
    )


_SUBMISSION_README = """\
# Submission package — {modality}/{style_id}

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


def _build_submission_readme(modality: str, style_id: str) -> str:
    return _SUBMISSION_README.format(modality=modality, style_id=style_id)
