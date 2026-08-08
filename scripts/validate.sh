#!/usr/bin/env bash
# validate.sh — frontmatter + cross-link validation for all skills in the repo.
# Exits non-zero on any error so it can serve as a CI gate.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

err=0
checked=0
desc_pass=0
desc_info=0
desc_warn=0

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
    fail "frontmatter missing fields: $(echo "$missing" | tr '\n' ' ')"
  else
    pass "frontmatter OK (name, description, license, allowed-tools)"
  fi

  # 2) Cross-link check: every local markdown link in SKILL.md must resolve.
  #
  # This used to grep for a path *shape* — one optional `../` then `references/`.
  # It matched the tail of anything deeper, so a correct
  # `../../common/references/x.md` was reported broken as `../common/...`, and a
  # path merely mentioned in prose was checked as if it were a link. Extract the
  # link targets instead, and let the filesystem resolve them.
  links="$(python3 - "$skill/SKILL.md" <<'EXTRACT'
import re, sys
from pathlib import Path

path = Path(sys.argv[1])
skill_dir = path.parent
checked = 0
broken = []
for target in re.findall(r"\]\(([^)\s]+)\)", path.read_text(encoding="utf-8")):
    target = target.split("#", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:")):
        continue
    if not target.endswith(".md"):
        continue
    checked += 1
    resolved = (skill_dir / target).resolve()
    if not resolved.is_file():
        broken.append(target)

print(checked)
for target in broken:
    print(target)
EXTRACT
)"
  # First line is how many links were looked at; the rest are the broken ones.
  # Reporting the count matters: "no links to check" and "every link resolves"
  # must not print the same thing.
  link_total="$(printf '%s\n' "$links" | head -n1)"
  link_broken="$(printf '%s\n' "$links" | tail -n +2)"
  link_err=0
  for link in $link_broken; do
    fail "broken link in SKILL.md: $link"
    link_err=1
  done
  if [ "${link_total:-0}" = "0" ]; then
    info "no local markdown links to check"
  elif [ "$link_err" = "0" ]; then
    pass "all local links resolve ($link_total checked)"
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

  # 4) description quality (advisory, never blocks)
  if [ -x scripts/lint-description.py ] || [ -f scripts/lint-description.py ]; then
    desc_out="$(python3 scripts/lint-description.py "$skill" 2>&1)"
    # Echo every line except the verdict line, and count the verdict.
    printf '%s\n' "$desc_out" | while IFS= read -r line; do
      case "$line" in
        *"description-verdict:"*) ;;  # consumed below
        *) [ -n "$line" ] && printf '%s\n' "$line" ;;
      esac
    done
    verdict_line="$(printf '%s\n' "$desc_out" | grep 'description-verdict:' || true)"
    case "$verdict_line" in
      *PASS*) desc_pass=$((desc_pass + 1)) ;;
      *INFO*) desc_info=$((desc_info + 1)) ;;
      *WARN*) desc_warn=$((desc_warn + 1)) ;;
    esac
  fi
done

echo
# 5) Tag-dictionary validation (against scripts/gen-skill-index.py allowlist)
if [ -f scripts/gen-skill-index.py ]; then
  if ! python3 - <<'PY' "$ROOT/skills.json"
import json, sys, re

path = sys.argv[1]
# Pull ALLOWED_TAGS from gen-skill-index.py without importing (no PYTHONPATH dance)
src = open("scripts/gen-skill-index.py", encoding="utf-8").read()
domain = set(re.findall(r'"([a-z-]+)"', re.search(r'DOMAIN_TAGS = \{([^}]+)\}', src).group(1)))
func = set(re.findall(r'"([a-z-]+)"', re.search(r'FUNCTION_TAGS = \{([^}]+)\}', src).group(1)))
allowed = domain | func

manifest = json.load(open(path, encoding="utf-8"))
errors = []
missing_tags = []
for s in manifest["skills"]:
    name = s["name"]
    tags = s.get("tags")
    if tags is None:
        missing_tags.append(name)
        continue
    if not isinstance(tags, list):
        errors.append(f"{name}: tags must be a list")
        continue
    bad = [t for t in tags if t not in allowed]
    if bad:
        errors.append(f"{name}: unknown tags {bad}; allowed: {sorted(allowed)}")

if missing_tags:
    print(f"  · skills without tags: {missing_tags}")
if errors:
    for e in errors:
        print(f"  ✗ tag error: {e}")
    sys.exit(1)
print(f"  ✓ tags OK ({len(manifest['skills'])} skills validated against closed dict)")
PY
  then
    err=1
  fi
fi

echo
if [ "$err" = "0" ]; then
  green "validate: OK ($checked skill(s) checked)"
else
  red   "validate: FAILED"
fi

# Description-quality summary (advisory)
total_desc=$((desc_pass + desc_info + desc_warn))
if [ "$total_desc" -gt 0 ]; then
  dim "description quality: $desc_pass PASS · $desc_info INFO · $desc_warn WARN"
fi

exit "$err"
