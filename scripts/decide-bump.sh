#!/usr/bin/env bash
# decide-bump.sh — parse conventional commits since the last release tag and
# emit one of: major | minor | patch | none on stdout.
#
# Used by .github/workflows/release.yml.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Find the last release tag (v*). If none, use the root commit.
last_tag="$(git tag --list 'v*' --sort=-v:refname | head -n1 || true)"
if [ -z "$last_tag" ]; then
  range="$(git rev-list --max-parents=0 HEAD | tail -n1)..HEAD"
else
  range="${last_tag}..HEAD"
fi

# Collect commit subjects + bodies
commits="$(git log --pretty=format:'%s%n%b%n---END---' "$range" 2>/dev/null || true)"

if [ -z "$commits" ]; then
  echo "none"
  exit 0
fi

has_major="false"
has_minor="false"
has_patch="false"

while IFS= read -r line; do
  case "$line" in
    *"BREAKING CHANGE:"*|*"BREAKING-CHANGE:"*)
      has_major="true"
      ;;
  esac
done <<EOF
$commits
EOF

# Match conventional types on subject lines only (first line of each commit)
subjects="$(git log --pretty=format:'%s' "$range" 2>/dev/null || true)"
while IFS= read -r subject; do
  [ -z "$subject" ] && continue
  case "$subject" in
    *"!:"*)                        has_major="true" ;;
    feat:*|feat\(*\):*)            has_minor="true" ;;
    fix:*|fix\(*\):*)              has_patch="true" ;;
    perf:*|perf\(*\):*)            has_patch="true" ;;
    refactor:*|refactor\(*\):*)    has_patch="true" ;;
  esac
done <<EOF
$subjects
EOF

if [ "$has_major" = "true" ]; then
  echo "major"
elif [ "$has_minor" = "true" ]; then
  echo "minor"
elif [ "$has_patch" = "true" ]; then
  echo "patch"
else
  echo "none"
fi
