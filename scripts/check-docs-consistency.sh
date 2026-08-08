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
#   7. Dockerfile + package.json ship every registered skill (distribution drift)
#   8. Every price quoted in a skill doc is derivable from cost.PRICE_TABLE
#   9. Each skills.json blurb was reconciled against the current SKILL.md text
#  10. Every literal CLI command in the docs uses flags its parser accepts
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

# Skills live in skills/. This used to glob `*/` at the repo root, which matches
# bin, docs, scripts and nothing with a SKILL.md in it — so check 2 iterated an
# empty list and passed for every commit since the skills/ move. A gate that
# scans nothing reports the same green as a gate that scans everything, which is
# why the count is asserted below rather than trusted.
skill_dirs_on_disk() {
  for d in skills/*/; do
    name="${d%/}"
    if [ -f "$name/SKILL.md" ]; then
      basename "$name"
    fi
  done
}

# ── Check 1 — README table is in sync with skills.json ──────────────────────

echo "[1/10] README skills table ↔ skills.json"
if python3 scripts/gen-skills-table.py --check >/dev/null 2>&1; then
  pass "README table is up to date with skills.json"
else
  fail "README table out of date — run: python3 scripts/gen-skills-table.py --write"
  python3 scripts/gen-skills-table.py --check >&2 || true
fi
echo

# ── Check 2 — every disk skill folder is in skills.json ─────────────────────

echo "[2/10] skill folders on disk ↔ skills.json"
manifest_set=" $(skills_in_manifest | tr '\n' ' ')"
on_disk="$(skill_dirs_on_disk)"
disk_count="$(printf '%s\n' "$on_disk" | grep -c . || true)"
unregistered=""
for dir in $on_disk; do
  case "$manifest_set" in
    *" $dir "*) ;;
    *) unregistered="$unregistered $dir" ;;
  esac
done
if [ "$disk_count" -lt 2 ]; then
  fail "found $disk_count skill folders on disk — the scan is broken, not the repo"
elif [ -z "$unregistered" ]; then
  pass "all $disk_count skill folders are registered in skills.json"
else
  for d in $unregistered; do
    fail "skill folder $d/ has SKILL.md but is NOT in skills.json"
  done
fi
echo

# ── Check 3 — walkthroughs cite only real skills ────────────────────────────

echo "[3/10] docs/walkthroughs/ frontmatter ↔ skills.json"
if [ -d docs/walkthroughs ]; then
  walked=0
  for w in docs/walkthroughs/*.md; do
    [ -f "$w" ] || continue
    # README.md inside the walkthroughs dir is the categorized index, not a walkthrough.
    case "$(basename "$w")" in
      README.md) continue ;;
    esac
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

echo "[4/10] every skill is mentioned in docs/USER-GUIDE.md"
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

# ── Check 5 — new skills since last tag must be documented in CHANGELOG ─────
#
# The window is every CHANGELOG section above the last tagged version, not just
# [Unreleased]. This repo documents version sections directly and cuts tags
# manually, so a skill shipping in an untagged 2.20.0 belongs under [2.20.0] —
# scanning [Unreleased] alone would fail every such entry.

echo "[5/10] new skills since last v* tag ↔ CHANGELOG (untagged sections)"
last_tag="$(git tag --list 'v*' --sort=-v:refname | head -n1 || true)"
if [ -z "$last_tag" ]; then
  info "no v* tag yet — skipping (this check matters only after first release)"
else
  # Only skills/<name>/SKILL.md counts. The old pattern kept any */SKILL.md and
  # then discarded every path containing a slash as "nested" — which, after the
  # move into skills/, is all of them. post-publisher and schema-maker both
  # shipped through this gate without it ever looking at the CHANGELOG.
  new_skill_paths="$(git diff --name-only --diff-filter=A "$last_tag"..HEAD -- 'skills/*/SKILL.md' 2>/dev/null || true)"
  new_skills=""
  for path in $new_skill_paths; do
    case "$path" in
      skills/*/SKILL.md)
        dir="${path%/SKILL.md}"
        new_skills="$new_skills ${dir#skills/}"
        ;;
    esac
  done
  # Same trap as check 2: "no new skills" and "the pattern matches nothing" print
  # identically. If the layout moves again, say so instead of staying quiet.
  if [ ! -f "$(printf '%s\n' skills/*/SKILL.md | head -n1)" ]; then
    fail "pattern skills/*/SKILL.md matches nothing on disk — the scan is broken"
  elif [ -z "$new_skills" ]; then
    info "no new skills added since $last_tag"
  else
    # Capture from the top of the changelog down to (and excluding) the section
    # matching the last tag — everything above it is not yet released.
    tag_version="${last_tag#v}"
    unreleased="$(awk -v stop="## [$tag_version]" '
      index($0, stop) == 1 { exit }
      /^## \[/            { capture=1 }
      capture             { print }
    ' CHANGELOG.md)"
    missing_log=""
    for s in $new_skills; do
      case "$unreleased" in
        *"$s"*) ;;
        *) missing_log="$missing_log $s" ;;
      esac
    done
    if [ -z "$missing_log" ]; then
      pass "all new skills since $last_tag documented in CHANGELOG"
    else
      for s in $missing_log; do
        fail "skill $s added since $last_tag but NOT in CHANGELOG (any untagged section)"
      done
    fi
  fi
fi

echo
# ── Check 6 — SKILL-INDEX.md is up to date with skills.json ─────────────────

echo "[6/10] docs/SKILL-INDEX.md ↔ skills.json"
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

echo "[7/10] distribution manifests ↔ skills.json"
# Nothing checked this, which is how the npm package and the Docker image came
# to ship a 17-skill v1.x subset while skills.json advertised 42 — install.sh
# then warned about 25 missing skills inside the very artifacts meant to
# contain them. A registered skill that reaches neither channel is invisible to
# everyone who did not install from the git tarball.
#
# The per-skill enumeration this used to do is gone: both manifests now ship
# skills/ wholesale, so there is no list left to drift. What remains is the
# claim that makes that safe — every registered skill really is inside the
# directory the manifests ship, and both manifests really do ship it.
if ! python3 - <<'GATE7'
import json, re, sys
from pathlib import Path

registered = json.loads(Path("skills.json").read_text(encoding="utf-8"))["skills"]
errors = []

for entry in registered:
    d = Path(entry["dir"])
    if not d.is_dir():
        errors.append(f"skills.json points at a missing directory: {entry['dir']}")
    elif d.parts[0] != "skills":
        errors.append(f"{entry['name']} lives outside skills/ ({entry['dir']}) - nothing ships it")
    elif not (d / "SKILL.md").is_file():
        errors.append(f"{entry['dir']}/SKILL.md is missing")

dockerfile = Path("Dockerfile")
if dockerfile.is_file():
    copied = set(re.findall(r"^COPY (\S+?)/", dockerfile.read_text(encoding="utf-8"), re.M))
    for need in ("skills", "common"):
        if need not in copied:
            errors.append(f"Dockerfile does not COPY {need}/")

pkg = Path("package.json")
if pkg.is_file():
    listed = {f.rstrip("/") for f in json.loads(pkg.read_text(encoding="utf-8")).get("files", [])}
    for need in ("skills", "common"):
        if need not in listed:
            errors.append(f"package.json 'files' omits {need}/")

if errors:
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
print(f"  ✓ Dockerfile + package.json ship skills/ + common/ ({len(registered)} skills registered)")
GATE7
then
  fail "distribution manifests out of sync with skills.json"
fi
echo

# ── Check 8 — quoted prices are derivable from the billing table ────────────
#
# model-pricing.md is generated and therefore true. The skills quote prices in
# prose and in decision tables, and thirteen of those had gone stale — a
# nano-banana-pro thumbnail batch advertised at $0.45 bills $1.21. Reading the
# doc was how a user decided whether to run the batch.

echo "[8/10] quoted model prices ↔ cost.PRICE_TABLE"
if python3 scripts/check-prices.py >/dev/null 2>&1; then
  pass "$(python3 scripts/check-prices.py | head -n1)"
else
  fail "price claims contradict cost.PRICE_TABLE"
  python3 scripts/check-prices.py >&2 || true
fi
echo

# ── Check 9 — catalog blurbs were written against the current SKILL.md ───────
#
# The two descriptions are deliberately different texts for different readers.
# What is not allowed is the catalog one going stale unnoticed, which is how
# skills.json came to advertise "17 Claude Code skills" against 42 on disk.

echo "[9/10] skills.json blurbs ↔ SKILL.md descriptions"
if python3 scripts/check-skill-descriptions.py >/dev/null 2>&1; then
  pass "$(python3 scripts/check-skill-descriptions.py | head -n1)"
else
  fail "a SKILL.md description moved since its catalog blurb was written"
  python3 scripts/check-skill-descriptions.py >&2 || true
fi
echo

# ── Check 10 — documented commands would actually run ───────────────────────
#
# Skill-level flags (`/logo-maker --variants 4`) are conventions Claude reads;
# nothing can verify those. A literal `python3 -m common.runners.cli.X --flag`
# is different — a reader copies it verbatim, and argparse answers with
# "unrecognized arguments" rather than anything about what the doc meant.

echo "[10/10] documented CLI commands ↔ argparse"
if python3 scripts/check-cli-docs.py >/dev/null 2>&1; then
  pass "$(python3 scripts/check-cli-docs.py | head -n1)"
else
  fail "a documented command passes a flag its CLI rejects"
  python3 scripts/check-cli-docs.py >&2 || true
fi
echo

if [ "$err" = "0" ]; then
  green "docs-consistency: OK"
else
  red   "docs-consistency: FAILED"
fi
exit "$err"
