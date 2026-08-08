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

echo "─── 1/14 validate ─────────────────────────────────────────────"
bash scripts/validate.sh

echo
echo "─── 2/14 writer/lint.py self-test ─────────────────────────────"
# skills/writer/examples/before-after.md contains intentional BEFORE samples that
# should trip the linter. Verdict must be "neuroslop suspected".
if ! command -v python3 >/dev/null 2>&1; then
  red "python3 not found — skipping writer linter self-test"
  exit 0
fi

verdict_out="$(python3 skills/writer/scripts/lint.py skills/writer/examples/before-after.md --scan-code-blocks 2>&1 || true)"
echo "$verdict_out" | head -8 | sed 's/^/  /'

if echo "$verdict_out" | grep -q "neuroslop suspected"; then
  green "  ✓ writer linter correctly flags before-after fixture as neuroslop"
else
  red   "  ✗ writer linter did NOT flag fixture — regression"
  exit 2
fi

echo
echo "─── 3/14 fixture snapshots ────────────────────────────────────"
bash tests/run.sh

echo
echo "─── 4/14 AFTER calibration samples ────────────────────────────"
# Calibration samples live inside fenced blocks, which lint.py masks by default —
# so the one thing a model copies verbatim is the one thing the linter misses.
python3 scripts/check-after-samples.py

echo
echo "─── 5/14 relative links ───────────────────────────────────────"
# validate.sh only resolves references/*.md inside the owning skill; cross-skill,
# docs-to-docs and repo-root links were unchecked until this step existed.
python3 scripts/check-links.py

echo
echo "─── 6/14 runner unit tests ────────────────────────────────────"
# stdlib unittest, no pytest dependency — the README promises no required deps.
python3 -m unittest discover -s tests/unit -t . -q

echo
echo "─── 7/14 pricing doc ↔ cost.PRICE_TABLE ───────────────────────"
# The published price table is generated from the code that bills. Drift here
# means the docs quote a number the runner does not charge.
python3 scripts/gen-pricing.py --check

echo
echo "─── 8/14 markdownlint (CI-pinned version) ─────────────────────"
# CI runs markdownlint-cli2-action@v16, which pins v0.13.0. Running a newer
# local version reports rules CI does not have (and misses none it does), so
# the version is pinned here too. Tracked files only: generated/ is ignored.
if command -v npx >/dev/null 2>&1; then
  # shellcheck disable=SC2046  # word splitting is the point: one arg per file
  if npx --yes markdownlint-cli2@0.13.0 $(git ls-files '*.md') >/tmp/mdlint.$$ 2>&1; then
    green "  ✓ markdownlint clean"
  else
    red "  ✗ markdownlint failed"
    grep -E "MD[0-9]+" /tmp/mdlint.$$ | head -20
    rm -f /tmp/mdlint.$$
    exit 1
  fi
  rm -f /tmp/mdlint.$$
else
  dim "  · npx not found — skipping markdownlint (CI still runs it)"
fi

echo
echo "─── 9/14 linter coverage doc ─────────────────────────────────"
# Generated from the category catalogue + lint.py. It went stale silently once.
python3 scripts/coverage.py --check

echo
echo "─── 10/14 launch-thread tweet lengths ────────────────────────"
# The old draft claimed "all tweets ≤280 (verified)" next to a checker that no
# longer parsed the file. Two tweets were over.
if python3 scripts/check-tweet-length.py >/dev/null; then
  green "  ✓ all tweets within 280"
else
  red "  ✗ a tweet overflows"
  python3 scripts/check-tweet-length.py | grep OVER
  exit 1
fi

echo
echo "─── 11/14 launch copy ────────────────────────────────────────"
# The copy lives inside fenced blocks, which lint.py masks, and the files carry
# lint-role: catalogue so the hook skips them. Without this step nothing ever
# checks the promotional copy for an anti-slop toolkit.
python3 scripts/check-launch-copy.py

echo
echo "─── 12/14 runners import smoke ─────────────────────────────────"
# common/runners is the optional execution layer. We don't require API keys —
# just confirm every provider module imports cleanly and registers.
if [ -d common/runners ]; then
  python3 -c "
import sys
sys.path.insert(0, '.')
from common.runners import config
config.load_all_providers()
provs = config.all_providers()
assert len(provs) >= 25, f'expected >=25 providers, got {len(provs)}'
by_modality = ' / '.join(
    f'{len(config.all_providers(m))} {m}'
    for m in ('image', 'video', 'music', 'audio', 'model')
)
counted = sum(len(config.all_providers(m)) for m in ('image', 'video', 'music', 'audio', 'model'))
assert counted == len(provs), f'{len(provs) - counted} provider(s) in no counted modality'
print(f'  ✓ {len(provs)} providers registered ({by_modality})')
" || { red "  ✗ runners import failed"; exit 3; }
  green "  ✓ common/runners imports OK"
else
  dim "  · no common/runners — skipping (this check matters only after v2.2)"
fi

echo "─── 13/14 code quality (structure + contracts) ────────────────"
# Thresholds and the frozen baseline live in scripts/check-code-quality.py.
# Contract and layering findings are never baselined — they are invariants.
python3 scripts/check-code-quality.py || { red "  ✗ code quality gate failed"; exit 3; }

echo
echo "─── 14/14 CLI surface ─────────────────────────────────────────"
# Every CLI module must import and build its parser. Cheap, and it is the only
# thing standing between a refactor and a runner that dies on invocation —
# these paths have no unit tests of their own.
python3 -c "
import importlib, pkgutil, sys
sys.path.insert(0, '.')
import common.runners.cli as clipkg
bad = []
n = 0
for mod in pkgutil.iter_modules(clipkg.__path__):
    if mod.name.startswith('_'):
        continue
    name = f'common.runners.cli.{mod.name}'
    try:
        m = importlib.import_module(name)
        if hasattr(m, 'build_parser'):
            m.build_parser().format_help()
        elif not hasattr(m, 'main'):
            bad.append(f'{name}: neither build_parser() nor main()')
            continue
        n += 1
    except Exception as exc:
        bad.append(f'{name}: {type(exc).__name__}: {exc}')
if bad:
    for b in bad:
        print(f'  ✗ {b}')
    sys.exit(1)
print(f'  ✓ {n} CLI modules import and expose a usable entry point')
" || { red "  ✗ CLI surface check failed"; exit 3; }

echo
green "smoke: OK"
