---
title: "Set up style-check as a git pre-commit hook"
persona: "any prose author who wants automatic linting on every commit"
time: "10 minutes one-time setup"
skills:
  - style-check
  - writer
---

# Run style-check automatically on every commit

The collection is already installed. You've used `/style-check staged` a few times and confirmed the report looks right. Now you want it to run on every `git commit` automatically — so you can't forget. This walkthrough wires it into `.git/hooks/pre-commit`.

The install scripts shipped with this repo deliberately do **not** touch your `.git/` directory. Git hooks are per-clone state; we don't write into them without your explicit setup. You do it once, per repo.

## What the hook does

On every `git commit`:

1. Git invokes `.git/hooks/pre-commit`.
2. The hook runs `style-check staged` against the staged diff.
3. The hook reads the exit code:
   - `0` — only INFO findings → commit proceeds silently
   - `1` — WARNING present → hook prints the report, prompts you (y/n)
   - `2` — BLOCKING present → hook prints the report, aborts the commit

You can always bypass with `git commit --no-verify` when needed (see below).

## Exit-code semantics (important for git)

Git's contract with `pre-commit` hooks is simple:

- **exit 0** — proceed with the commit
- **exit non-zero** — abort

`style-check` produces three meaningful codes — we map them to git's two:

| style-check exit | Meaning | Hook behaviour |
|---|---|---|
| `0` | only INFO | proceed (exit 0) |
| `1` | WARNING | prompt; on `y` → exit 0, on `n` → exit 1 |
| `2` | BLOCKING | abort (exit 1, print findings) |

You can also configure it to **always block on WARNING** (strict mode) — see the variant at the bottom of the script.

## Variant A — full Claude Code invocation

This variant uses the actual `/style-check` skill via Claude Code's CLI. Best fidelity (all rule layers, full report), slower (a few seconds per commit).

Create `.git/hooks/pre-commit` with this content:

```bash
#!/usr/bin/env bash
# pre-commit hook — runs style-check against staged diff via Claude Code.
#
# Exit codes:
#   0 — commit allowed
#   1 — commit aborted

set -uo pipefail

# Skip the hook entirely if Claude Code isn't installed (don't block clones
# that don't have it).
if ! command -v claude >/dev/null 2>&1; then
  echo "[pre-commit] claude CLI not found — skipping style-check"
  exit 0
fi

# Run the skill against staged diff. The skill reports to stdout, exit code
# carries the severity.
output="$(claude -p "/style-check staged" 2>&1)"
sk_exit=$?

case "$sk_exit" in
  0)
    # only INFO — silently proceed
    exit 0
    ;;
  1)
    # WARNING — show report, ask author
    echo "$output"
    echo
    echo "[pre-commit] style-check returned WARNING. Proceed with commit? [y/N]"
    read -r answer </dev/tty
    case "$answer" in
      y|Y|yes) exit 0 ;;
      *)       echo "[pre-commit] aborted"; exit 1 ;;
    esac
    ;;
  2)
    # BLOCKING — abort
    echo "$output"
    echo
    echo "[pre-commit] style-check found BLOCKING findings — commit aborted."
    echo "[pre-commit] fix them, restage, recommit. (Bypass: git commit --no-verify)"
    exit 1
    ;;
  *)
    echo "[pre-commit] style-check exited with unexpected code $sk_exit"
    echo "$output"
    exit 1
    ;;
esac
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

## Variant B — offline-linter-only fallback

This variant calls the offline regex linter directly (`skills/writer/scripts/lint.py`) — no Claude Code roundtrip. Much faster (~50ms), much narrower coverage (regex-only, no LLM reasoning). Use this if you're committing often and don't want the latency, or if you don't have `claude` in the commit-time environment.

```bash
#!/usr/bin/env bash
# pre-commit hook — offline-only neuroslop check via skills/writer/scripts/lint.py.
#
# Faster but narrower than Variant A. Catches regex-detectable patterns;
# misses voice drift, structural synthesis nuance, canon issues.
#
# Exit codes:
#   0 — commit allowed
#   1 — commit aborted

set -uo pipefail

LINTER="$HOME/.claude/skills/writer/scripts/lint.py"

if [ ! -f "$LINTER" ]; then
  echo "[pre-commit] skills/writer/scripts/lint.py not found at $LINTER — skipping"
  exit 0
fi

# Only check staged .md / .tex / .txt / .rst files (skip everything else
# — including code, binaries, anything not prose).
files="$(git diff --cached --name-only --diff-filter=AM \
         | grep -E '\.(md|tex|txt|rst)$' || true)"

if [ -z "$files" ]; then
  exit 0
fi

worst=0
report=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  # The linter exits: 0 clean / 1 borderline (2-4 hits) / 2 suspected (5+).
  out="$(python3 "$LINTER" "$f" 2>&1)"
  code=$?
  if [ "$code" -gt "$worst" ]; then worst="$code"; fi
  if [ "$code" -gt 0 ]; then
    report="$report
=== $f ===
$out"
  fi
done <<< "$files"

case "$worst" in
  0) exit 0 ;;
  1)
    echo "$report"
    echo
    echo "[pre-commit] borderline neuroslop (2-4 hits). Proceed? [y/N]"
    read -r answer </dev/tty
    case "$answer" in y|Y|yes) exit 0 ;; *) exit 1 ;; esac
    ;;
  2)
    echo "$report"
    echo
    echo "[pre-commit] neuroslop suspected (5+ hits or any category 3+ times)."
    echo "[pre-commit] commit aborted. (Bypass: git commit --no-verify)"
    exit 1
    ;;
esac
```

Same `chmod +x .git/hooks/pre-commit` to enable.

## Strict mode (block on WARNING)

If you want WARNING to also block (no prompt), replace the `1)` case in Variant A with:

```bash
  1)
    echo "$output"
    echo
    echo "[pre-commit] style-check returned WARNING — commit aborted (strict mode)."
    exit 1
    ;;
```

## Configuring routing for your project

`style-check` decides which rule layer (fiction / non-fiction / generic) to apply by file path. The default patterns are illustrative — adapt to your project's directory layout. Full table and override pattern: [skills/style-check/references/routing.md](../../skills/style-check/references/routing.md).

Quick example: if your fiction lives in `novels/**/*.tex` instead of `fiction/**/*.md`, you tell the skill that once (per-project config) and the hook picks it up automatically.

## Bypassing the hook

Sometimes you legitimately need to commit without lint — quick WIP commit, mid-rebase squash, intentional stylistic exception. Use:

```bash
git commit --no-verify -m "wip: scaffolding"
```

Don't add `--no-verify` to your aliases or `.gitconfig` — it defeats the purpose. Use it inline, deliberately, per commit.

## Troubleshooting

### Hook is slow

Variant A makes a Claude Code call every commit — usually 3-8 seconds. If that drags:

- Switch to Variant B (offline) for the hook; run `/style-check staged` manually before push.
- Or scope tighter: in Variant A, pre-filter staged files to only `.md` / `.tex` (the linter would skip code anyway, but pre-filtering means `claude` doesn't even spin up if no prose is staged).

### Hook fails on macOS bash 3.2

macOS ships with bash 3.2 by default (2007 vintage). The scripts above are bash 3.2 compatible — no associative arrays, no `mapfile`, no `&&`-chained `if`. If yours still fails, check the shebang:

```bash
#!/usr/bin/env bash
```

If `/usr/bin/env` doesn't find a bash, replace with `/bin/bash`. If you need bash 5 features for something custom, install via Homebrew (`brew install bash`) and shebang `#!/usr/local/bin/bash` or `#!/opt/homebrew/bin/bash`.

### False positive on legitimate prose

`style-check` shouldn't false-positive on staccato or inversions that are intentionally part of your voice — the fiction layer (`prose-edit`) knows about that. But the offline linter (Variant B) is regex-only and can false-positive on, e.g., a deliberate three-word sentence.

If it's a one-off — `--no-verify` and move on. If it's a pattern: see [skills/style-check/references/severity.md](../../skills/style-check/references/severity.md) for how to demote a category from BLOCKING to WARNING (or to silence) for your project.

### Hook doesn't run

Check:

```bash
ls -la .git/hooks/pre-commit
# should show: -rwxr-xr-x (executable)
```

If not executable: `chmod +x .git/hooks/pre-commit`. If the file isn't there at all — git uses `.git/hooks/pre-commit.sample` by default but never runs it (the `.sample` suffix is git's convention for inactive examples). You need the file at exactly `.git/hooks/pre-commit` (no extension).

## See also

- [translation-parity.md](translation-parity.md) — wire `translation-sync` the same way for multilingual books
- [fiction-chapter.md](fiction-chapter.md) — the manual workflow this hook automates
- [skills/style-check/references/pre-commit-hook.md](../../skills/style-check/references/pre-commit-hook.md) — additional snippets and patterns
- [docs/FAQ.md](../FAQ.md) — common questions
