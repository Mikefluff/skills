#!/usr/bin/env bash
# validate.sh — frontmatter + cross-link validation for all skills in the repo.
# Exits non-zero on any error so it can serve as a CI gate.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

err=0
checked=0

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
dim()    { printf '\033[2m%s\033[0m\n' "$*"; }

fail() { red "  ✗ $*"; err=1; }
pass() { green "  ✓ $*"; }
info() { dim  "  · $*"; }

# Enumerate skills from skills.json
if command -v jq >/dev/null 2>&1; then
  SKILLS="$(jq -r '.skills[].dir' skills.json)"
else
  SKILLS="$(grep -oE '"dir": *"[^"]+"' skills.json | sed -E 's/.*"dir": *"([^"]+)".*/\1/')"
fi

for skill in $SKILLS; do
  echo "[$skill]"
  checked=$((checked + 1))

  if [ ! -f "$skill/SKILL.md" ]; then
    fail "missing $skill/SKILL.md"
    continue
  fi

  # 1) Frontmatter required fields
  awk_check_fm() {
    awk -v missing="" '
      /^---$/ { fm++; next }
      fm == 1 {
        if (/^name:/)         seen_name=1
        if (/^description:/)  seen_desc=1
        if (/^license:/)      seen_license=1
        if (/^allowed-tools:/) seen_tools=1
      }
      END {
        if (!seen_name)    print "name"
        if (!seen_desc)    print "description"
        if (!seen_license) print "license"
        if (!seen_tools)   print "allowed-tools"
      }
    ' "$1"
  }
  missing=$(awk_check_fm "$skill/SKILL.md")
  if [ -n "$missing" ]; then
    fail "frontmatter missing fields: $(echo $missing | tr '\n' ' ')"
  else
    pass "frontmatter OK (name, description, license, allowed-tools)"
  fi

  # 2) Cross-link check: every references/<file>.md mentioned in SKILL.md must exist
  links="$(grep -oE 'references/[a-z0-9_-]+\.md' "$skill/SKILL.md" | sort -u || true)"
  link_err=0
  for link in $links; do
    if [ -f "$skill/$link" ]; then
      :
    else
      fail "broken link in SKILL.md: $link"
      link_err=1
    fi
  done
  if [ -z "$links" ]; then
    info "no references/ links to check"
  elif [ "$link_err" = "0" ]; then
    pass "all references/ links resolve ($(echo "$links" | wc -l | tr -d ' ') checked)"
  fi

  # 3) examples/ check (optional but recommended)
  if [ -d "$skill/examples" ]; then
    n=$(find "$skill/examples" -type f -name '*.md' | wc -l | tr -d ' ')
    if [ "$n" -eq 0 ]; then
      yellow "  · examples/ exists but is empty"
    else
      pass "examples/ has $n file(s)"
    fi
  fi
done

echo
if [ "$err" = "0" ]; then
  green "validate: OK ($checked skill(s) checked)"
else
  red   "validate: FAILED"
fi
exit "$err"
