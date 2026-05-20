#!/usr/bin/env bash
# check-docs-consistency.sh — fail-fast checks that user-facing docs stay in
# sync with skills.json and with each other.
#
# Checks:
#   1. Every skill in skills.json appears in README's auto-generated table
#      (delegated to scripts/gen-skills-table.py --check)
#   2. Every skill folder on disk appears in skills.json
#   3. Every walkthrough's frontmatter `skills:` list references only real skills
#   4. Every skill is mentioned somewhere in docs/USER-GUIDE.md (link, code-fence,
#      or table cell)
#   5. New skill folders (since last release tag) must be mentioned in
#      CHANGELOG.md [Unreleased]
#   6. docs/SKILL-INDEX.md is up to date with skills.json (auto-generated)
#
# Usage:
#   bash scripts/check-docs-consistency.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

err=0

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
dim()    { printf '\033[2m%s\033[0m\n' "$*"; }

fail() { red "  ✗ $*"; err=1; }
pass() { green "  ✓ $*"; }
info() { dim  "  · $*"; }

skills_in_manifest() {
  python3 -c "import json; [print(s['name']) for s in json.load(open('skills.json'))['skills']]"
}

skill_dirs_on_disk() {
  for d in */; do
    name="${d%/}"
    if [ -f "$name/SKILL.md" ]; then
      echo "$name"
    fi
  done
}

# ── Check 1 — README table is in sync with skills.json ──────────────────────

echo "[1/6] README skills table ↔ skills.json"
if python3 scripts/gen-skills-table.py --check >/dev/null 2>&1; then
  pass "README table is up to date with skills.json"
else
  fail "README table out of date — run: python3 scripts/gen-skills-table.py --write"
  python3 scripts/gen-skills-table.py --check >&2 || true
fi
echo

# ── Check 2 — every disk skill folder is in skills.json ─────────────────────

echo "[2/6] skill folders on disk ↔ skills.json"
manifest_set=" $(skills_in_manifest | tr '\n' ' ')"
unregistered=""
for dir in $(skill_dirs_on_disk); do
  case "$manifest_set" in
    *" $dir "*) ;;
    *) unregistered="$unregistered $dir" ;;
  esac
done
if [ -z "$unregistered" ]; then
  pass "all skill folders are registered in skills.json"
else
  for d in $unregistered; do
    fail "skill folder $d/ has SKILL.md but is NOT in skills.json"
  done
fi
echo

# ── Check 3 — walkthroughs cite only real skills ────────────────────────────

echo "[3/6] docs/walkthroughs/ frontmatter ↔ skills.json"
if [ -d docs/walkthroughs ]; then
  walked=0
  for w in docs/walkthroughs/*.md; do
    [ -f "$w" ] || continue
    walked=$((walked + 1))
    # Extract the `skills:` list from frontmatter
    refs="$(awk '
      /^---$/ { fm++; next }
      fm == 1 && /^skills:/ { capture=1; next }
      fm == 1 && capture && /^[a-zA-Z]/ { capture=0 }
      fm == 1 && capture && /^  -/ { gsub(/^  - */, ""); print }
    ' "$w")"
    if [ -z "$refs" ]; then
      fail "$w has no frontmatter \`skills:\` list — add it (CI uses this)"
      continue
    fi
    bad=""
    for s in $refs; do
      case "$manifest_set" in
        *" $s "*) ;;
        *) bad="$bad $s" ;;
      esac
    done
    if [ -n "$bad" ]; then
      for s in $bad; do
        fail "$w references unknown skill: $s"
      done
    else
      pass "$w → covers: $(printf '%s ' "$refs")"
    fi
  done
  if [ "$walked" = "0" ]; then
    info "no walkthroughs found in docs/walkthroughs/ — skipping"
  fi
else
  info "docs/walkthroughs/ does not exist — skipping (mkdir docs/walkthroughs)"
fi
echo

# ── Check 4 — every skill is named somewhere in USER-GUIDE.md ───────────────

echo "[4/6] every skill is mentioned in docs/USER-GUIDE.md"
if [ -f docs/USER-GUIDE.md ]; then
  guide="$(cat docs/USER-GUIDE.md)"
  missing=""
  for s in $(skills_in_manifest); do
    case "$guide" in
      *"$s"*) ;;
      *) missing="$missing $s" ;;
    esac
  done
  if [ -z "$missing" ]; then
    pass "all skills referenced from USER-GUIDE.md"
  else
    for s in $missing; do
      fail "skill $s is not mentioned anywhere in docs/USER-GUIDE.md"
    done
  fi
else
  info "docs/USER-GUIDE.md missing — skipping (skill index belongs there)"
fi
echo

# ── Check 5 — new skills since last tag must be in CHANGELOG [Unreleased] ───

echo "[5/6] new skills since last v* tag ↔ CHANGELOG [Unreleased]"
last_tag="$(git tag --list 'v*' --sort=-v:refname | head -n1 || true)"
if [ -z "$last_tag" ]; then
  info "no v* tag yet — skipping (this check matters only after first release)"
else
  # Find skill folders added since last_tag (paths matching */SKILL.md)
  new_skill_paths="$(git diff --name-only --diff-filter=A "$last_tag"..HEAD -- '*/SKILL.md' 2>/dev/null || true)"
  new_skills=""
  for path in $new_skill_paths; do
    case "$path" in
      */SKILL.md)
        dir="${path%/SKILL.md}"
        # Only count top-level skill folders (no nested SKILL.md)
        case "$dir" in
          */*) ;;  # nested — skip
          *)   new_skills="$new_skills $dir" ;;
        esac
        ;;
    esac
  done
  if [ -z "$new_skills" ]; then
    info "no new skills added since $last_tag"
  else
    unreleased="$(awk '
      /^## \[Unreleased\]/ { capture=1; next }
      capture && /^## \[/  { exit }
      capture              { print }
    ' CHANGELOG.md)"
    missing_log=""
    for s in $new_skills; do
      case "$unreleased" in
        *"$s"*) ;;
        *) missing_log="$missing_log $s" ;;
      esac
    done
    if [ -z "$missing_log" ]; then
      pass "all new skills since $last_tag mentioned in CHANGELOG [Unreleased]"
    else
      for s in $missing_log; do
        fail "skill $s added since $last_tag but NOT in CHANGELOG [Unreleased]"
      done
    fi
  fi
fi

echo
# ── Check 6 — SKILL-INDEX.md is up to date with skills.json ─────────────────

echo "[6/6] docs/SKILL-INDEX.md ↔ skills.json"
if [ -f scripts/gen-skill-index.py ]; then
  if python3 scripts/gen-skill-index.py --check >/dev/null 2>&1; then
    pass "SKILL-INDEX.md is up to date with skills.json"
  else
    fail "SKILL-INDEX.md out of date — run: python3 scripts/gen-skill-index.py --write (or make gen-index)"
  fi
else
  info "scripts/gen-skill-index.py missing — skipping"
fi
echo

if [ "$err" = "0" ]; then
  green "docs-consistency: OK"
else
  red   "docs-consistency: FAILED"
fi
exit "$err"
