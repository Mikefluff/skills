#!/usr/bin/env bash
# new-skill.sh — bootstrap a new skill folder with the SOTA layout.
#
# Usage:
#   scripts/new-skill.sh <skill-name>
#   scripts/new-skill.sh foo-bar --description "Foo bar skill" --layer wrapper --deps writer

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

NAME="${1:-}"
[ -n "$NAME" ] || { echo "usage: $0 <skill-name> [--description <desc>] [--layer base|wrapper|linter] [--deps a,b]" >&2; exit 2; }
shift || true

DESC=""
LAYER="wrapper"
DEPS="writer"

while [ $# -gt 0 ]; do
  case "$1" in
    --description) DESC="$2"; shift 2 ;;
    --layer)       LAYER="$2"; shift 2 ;;
    --deps)        DEPS="$2"; shift 2 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

# Skills moved under skills/ in v2.22.0; this script kept scaffolding into the
# repo root, which put every new skill somewhere validate.sh does not look.
# NAME stays bare — it is the frontmatter `name:` — and DIR carries the path.
DIR="skills/$NAME"

if [ -d "$DIR" ]; then
  echo "directory $DIR already exists — aborting" >&2; exit 1
fi

mkdir -p "$DIR/references" "$DIR/examples"

cat >"$DIR/SKILL.md" <<EOF
---
name: $NAME
description: "${DESC:-TODO: one-line description suitable for skill discovery}"
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
TODO: what this skill is for, when to invoke, what the contract is.
</objective>

## ROLE

TODO.

## PIPELINE

TODO. If this skill wraps \`writer\`, add: "Final step: apply skills/writer/SKILL.md 4-layer cleaning pass before output."

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/TODO.md](references/TODO.md) | TODO |
EOF

cat >"$DIR/references/.gitkeep" <<'EOF'
# Move heavy rule tables, checklists, and exhaustive catalogues here.
# Link from SKILL.md as [references/<name>.md](references/<name>.md).
EOF

cat >"$DIR/examples/.gitkeep" <<'EOF'
# Calibration BEFORE/AFTER pairs or canonical input/output samples.
EOF

echo "✓ scaffolded $DIR/"
echo
echo "Next:"
echo "  1. Fill $DIR/SKILL.md (frontmatter description + objective + pipeline)"
echo "  2. Move heavy rules into $DIR/references/"
echo "  3. Add a calibration example to $DIR/examples/"
echo "  4. Register in skills.json (deps: $DEPS, layer: $LAYER)"
echo "  5. Add to README.md table"
echo "  6. bash scripts/validate.sh   # confirm frontmatter + cross-links"
