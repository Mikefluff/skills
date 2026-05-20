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

# Promote the accumulated [Unreleased] section into a new [<new>] section.
# Layout we expect:
#
#   ## [Unreleased]
#
#   ### Added
#   - foo
#
#   ## [<previous-version>] — DATE
#   ...
#
# After bump:
#
#   ## [Unreleased]
#
#   ## [<new>] — TODAY
#
#   ### Added
#   - foo
#
#   ## [<previous-version>] — DATE
#   ...
#
# If [Unreleased] is empty (nothing accumulated), we still insert an empty
# section with a placeholder bullet so the release notes aren't blank.

tmp="$(mktemp)"
python3 - "$new" "$today" >"$tmp" <<'PY'
import sys, re, pathlib

new_ver, today = sys.argv[1], sys.argv[2]
text = pathlib.Path("CHANGELOG.md").read_text()

# Split on top-level "## [..." headers, keeping the delimiter
parts = re.split(r"(?m)^(?=## \[)", text)
head, *sections = parts

new_sections = []
for sec in sections:
    if sec.startswith("## [Unreleased]"):
        # Strip the "## [Unreleased]" header line, keep the body
        body = re.sub(r"^## \[Unreleased\][^\n]*\n", "", sec, count=1)
        body = body.strip("\n")
        if not body.strip():
            body = "### Changed\n- (no notable changes captured in Unreleased — see commit log for v" + new_ver + ")"
        # Emit fresh empty Unreleased + new versioned section
        new_sections.append("## [Unreleased]\n\n")
        new_sections.append(f"## [{new_ver}] — {today}\n\n{body}\n\n")
    else:
        new_sections.append(sec)

out = head + "".join(new_sections)
sys.stdout.write(out)
PY
mv "$tmp" CHANGELOG.md

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
