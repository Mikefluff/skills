#!/usr/bin/env bash
# smoke.sh — quick end-to-end regression check.
# Runs validate.sh + spot-checks writer's offline linter against canonical
# example fixtures (which intentionally contain neuroslop).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

red()   { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
dim()   { printf '\033[2m%s\033[0m\n' "$*"; }

if [ ! -x scripts/validate.sh ]; then
  red "scripts/validate.sh is not executable"; exit 1
fi

echo "─── 1/3 validate ─────────────────────────────────────────────"
bash scripts/validate.sh

echo
echo "─── 2/3 writer/lint.py self-test ─────────────────────────────"
# writer/examples/before-after.md contains intentional BEFORE samples that
# should trip the linter. Verdict must be "neuroslop suspected".
if ! command -v python3 >/dev/null 2>&1; then
  red "python3 not found — skipping writer linter self-test"
  exit 0
fi

verdict_out="$(python3 writer/scripts/lint.py writer/examples/before-after.md --scan-code-blocks 2>&1 || true)"
echo "$verdict_out" | head -8 | sed 's/^/  /'

if echo "$verdict_out" | grep -q "neuroslop suspected"; then
  green "  ✓ writer linter correctly flags before-after fixture as neuroslop"
else
  red   "  ✗ writer linter did NOT flag fixture — regression"
  exit 2
fi

echo
echo "─── 3/3 fixture snapshots ────────────────────────────────────"
bash tests/run.sh

echo
green "smoke: OK"
