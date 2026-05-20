#!/usr/bin/env bash
# tests/run.sh — compare each fixture's lint output against its snapshot.
#
# Usage:
#   bash tests/run.sh            # compare; fail on drift
#   bash tests/run.sh --update   # rewrite snapshots (use when linter is intentionally changed)

set -euo pipefail

cd "$(dirname "$0")/.."

UPDATE_MODE="false"
[ "${1:-}" = "--update" ] && UPDATE_MODE="true"

fail=0
checked=0

red()   { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
dim()   { printf '\033[2m%s\033[0m\n' "$*"; }

mkdir -p tests/snapshots

for fix in tests/fixtures/*.md; do
  [ -f "$fix" ] || continue
  name="$(basename "$fix" .md)"
  snap="tests/snapshots/${name}.json"
  checked=$((checked + 1))

  # lint.py exits 0/1/2 to indicate the verdict bucket — that's data, not failure.
  # Use a temp file so the exit code doesn't trip set -e.
  tmp_out="$(mktemp)"
  python3 writer/scripts/lint.py "$fix" --json > "$tmp_out" || true
  actual="$(cat "$tmp_out")"
  rm -f "$tmp_out"

  if [ "$UPDATE_MODE" = "true" ]; then
    printf '%s\n' "$actual" > "$snap"
    green "→ $name (snapshot updated)"
    continue
  fi

  if [ ! -f "$snap" ]; then
    red "✗ $name — no snapshot yet (run with --update to seed)"
    fail=1
    continue
  fi

  expected="$(cat "$snap")"
  if [ "$actual" != "$expected" ]; then
    red "✗ $name — snapshot drift"
    diff <(printf '%s' "$expected") <(printf '%s' "$actual") || true
    fail=1
  else
    green "✓ $name"
  fi
done

echo
if [ "$fail" = "0" ]; then
  green "tests: OK ($checked fixture(s))"
else
  red   "tests: FAILED"
fi
exit "$fail"
