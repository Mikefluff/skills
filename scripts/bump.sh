#!/usr/bin/env bash
# bump.sh — bump VERSION and open a CHANGELOG section for the new version.
#
# This script was referenced by the Makefile (`make bump-patch|bump-minor|bump-major`)
# and by docs/VERSIONING.md but did not exist, so every documented path for cutting
# a release failed with "No such file or directory". VERSION was then bumped by hand
# and tags stopped being created — which is why the last tag drifted eight versions
# behind the changelog, and why `install.sh` (default `--version latest`, resolved
# from the newest GitHub release) served a stale bundle.
#
# Usage:
#   bash scripts/bump.sh patch          # 2.20.0 -> 2.20.1
#   bash scripts/bump.sh minor          # 2.20.0 -> 2.21.0
#   bash scripts/bump.sh major          # 2.20.0 -> 3.0.0
#   bash scripts/bump.sh 2.21.0         # explicit version
#   bash scripts/bump.sh patch --dry-run
#
# What it does NOT do: commit, tag, or push. Bumping is a working-tree edit you
# review; `make release` does the tagging once the bump is committed.

set -euo pipefail

cd "$(dirname "$0")/.."

red()   { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
dim()   { printf '\033[2m%s\033[0m\n' "$*"; }

DRY_RUN="false"
LEVEL=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN="true" ;;
    patch|minor|major) LEVEL="$arg" ;;
    [0-9]*.[0-9]*.[0-9]*) LEVEL="$arg" ;;
    *) red "unknown argument: $arg"; exit 2 ;;
  esac
done

if [ -z "$LEVEL" ]; then
  red "usage: bash scripts/bump.sh <patch|minor|major|X.Y.Z> [--dry-run]"
  exit 2
fi

[ -f VERSION ] || { red "VERSION file missing"; exit 1; }
CURRENT="$(tr -d '[:space:]' < VERSION)"

case "$CURRENT" in
  [0-9]*.[0-9]*.[0-9]*) ;;
  *) red "VERSION does not look like X.Y.Z: '$CURRENT'"; exit 1 ;;
esac

MAJOR="${CURRENT%%.*}"
REST="${CURRENT#*.}"
MINOR="${REST%%.*}"
PATCH="${REST#*.}"

case "$LEVEL" in
  patch) NEXT="$MAJOR.$MINOR.$((PATCH + 1))" ;;
  minor) NEXT="$MAJOR.$((MINOR + 1)).0" ;;
  major) NEXT="$((MAJOR + 1)).0.0" ;;
  *)     NEXT="$LEVEL" ;;
esac

if [ "$NEXT" = "$CURRENT" ]; then
  red "next version equals current ($CURRENT) — nothing to do"
  exit 1
fi

if git rev-parse "v$NEXT" >/dev/null 2>&1; then
  red "tag v$NEXT already exists — pick another version"
  exit 1
fi

TODAY="$(date +%Y-%m-%d)"

echo "current: $CURRENT"
echo "next:    $NEXT   ($LEVEL)"
echo "date:    $TODAY"

if grep -q "^## \[$NEXT\]" CHANGELOG.md; then
  dim "CHANGELOG already has a [$NEXT] section — leaving it alone"
  NEEDS_SECTION="false"
else
  NEEDS_SECTION="true"
fi

if [ "$DRY_RUN" = "true" ]; then
  green "dry run — no files written"
  exit 0
fi

printf '%s\n' "$NEXT" > VERSION
green "VERSION -> $NEXT"

if [ "$NEEDS_SECTION" = "true" ]; then
  python3 - "$NEXT" "$TODAY" <<'PY'
import pathlib, sys
version, today = sys.argv[1], sys.argv[2]
p = pathlib.Path("CHANGELOG.md")
text = p.read_text(encoding="utf-8")
marker = "## [Unreleased]"
if marker not in text:
    raise SystemExit("CHANGELOG.md has no '## [Unreleased]' heading — cannot insert")
section = f"{marker}\n\n## [{version}] — {today}\n\n### Added\n\n- \n"
p.write_text(text.replace(marker, section, 1), encoding="utf-8")
PY
  green "CHANGELOG: opened [$NEXT] — $TODAY"
fi

echo
dim "next steps:"
dim "  1. fill in the CHANGELOG bullets for [$NEXT]"
dim "  2. bash scripts/smoke.sh && bash scripts/check-docs-consistency.sh"
dim "  3. git commit -am \"chore(release): v$NEXT\""
dim "  4. make release        # tags v$NEXT and pushes"
