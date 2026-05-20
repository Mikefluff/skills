#!/usr/bin/env bash
# bump.sh — bump VERSION + open a new CHANGELOG section.
#
# Usage:
#   scripts/bump.sh patch | minor | major
#   scripts/bump.sh patch --commit          # also create a chore(release) commit
#
# Does NOT push and does NOT tag — those live in CI (release.yml) or are run by
# hand from the Makefile (make release).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LEVEL="${1:-}"
DO_COMMIT="false"
[ "${2:-}" = "--commit" ] && DO_COMMIT="true"

case "$LEVEL" in
  patch|minor|major) ;;
  *) echo "usage: $0 patch|minor|major [--commit]" >&2; exit 2 ;;
esac

[ -f VERSION ] || { echo "missing VERSION file" >&2; exit 1; }

current="$(cat VERSION | tr -d '[:space:]')"
IFS='.' read -r maj min pat <<EOF
$current
EOF

case "$LEVEL" in
  patch) pat=$((pat + 1)) ;;
  minor) min=$((min + 1)); pat=0 ;;
  major) maj=$((maj + 1)); min=0; pat=0 ;;
esac

new="${maj}.${min}.${pat}"
today="$(date +%Y-%m-%d)"

printf '%s\n' "$new" > VERSION
echo "VERSION: $current → $new"

# Update skills.json top-level version
if command -v jq >/dev/null 2>&1; then
  jq --arg v "$new" '.version = $v' skills.json >skills.json.tmp && mv skills.json.tmp skills.json
else
  python3 - <<PY
import json, sys, pathlib
p = pathlib.Path("skills.json")
data = json.loads(p.read_text())
data["version"] = "$new"
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY
fi
echo "skills.json: version → $new"

# Insert new section into CHANGELOG.md right after "## [Unreleased]"
tmp="$(mktemp)"
awk -v new="$new" -v date="$today" '
  /^## \[Unreleased\]/ {
    print
    print ""
    print "## [" new "] — " date
    next
  }
  { print }
' CHANGELOG.md > "$tmp" && mv "$tmp" CHANGELOG.md

# Append compare link at the bottom (replace the first [Unreleased] anchor too)
python3 - <<PY
import re, pathlib
p = pathlib.Path("CHANGELOG.md")
text = p.read_text()
new = "$new"

# Update [Unreleased] anchor to compare against new tag
text = re.sub(
    r"\[Unreleased\]: https://github\.com/Mikefluff/skills/compare/v[\d.]+\.\.\.HEAD",
    f"[Unreleased]: https://github.com/Mikefluff/skills/compare/v{new}...HEAD",
    text,
)

# Add anchor for new version if missing
anchor = f"[{new}]: https://github.com/Mikefluff/skills/releases/tag/v{new}"
if anchor not in text:
    text = text.rstrip() + "\n" + anchor + "\n"

p.write_text(text)
PY
echo "CHANGELOG.md: new section [$new] inserted"

if [ "$DO_COMMIT" = "true" ]; then
  git add VERSION CHANGELOG.md skills.json
  git commit -m "chore(release): v$new"
  echo "committed: chore(release): v$new"
fi

echo
echo "Next:"
echo "  • Fill the new [${new}] section in CHANGELOG.md with notable changes"
echo "  • git tag v${new} && git push --tags    (or let CI do it)"
