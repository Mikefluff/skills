#!/usr/bin/env bash
# install-precommit-hook.sh — install a local git pre-commit hook that runs
# the writer linter against staged .md files and runs `bash scripts/smoke.sh`.
#
# Idempotent: safe to re-run. Backs up any existing hook to pre-commit.bak
# on first install only (subsequent runs leave the backup alone).
#
# Uninstall: rm .git/hooks/pre-commit

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_DIR="$ROOT/.git/hooks"
HOOK="$HOOK_DIR/pre-commit"

if [ ! -d "$ROOT/.git" ]; then
  echo "error: not inside a git repository ($ROOT)" >&2
  exit 1
fi

mkdir -p "$HOOK_DIR"

if [ -f "$HOOK" ] && [ ! -f "$HOOK.bak" ]; then
  cp "$HOOK" "$HOOK.bak"
  echo "backed up existing pre-commit hook → $HOOK.bak"
fi

cat > "$HOOK" <<'HOOK_EOF'
#!/usr/bin/env bash
# pre-commit — installed by scripts/install-precommit-hook.sh
# Lints staged .md files with the writer linter and runs the smoke gate.
# To bypass once: git commit --no-verify

set -e

ROOT="$(git rev-parse --show-toplevel)"

# 1) Writer linter on staged .md files (skip deleted and skip calibration
#    fixtures whose nature is to contain intentional neuroslop).
staged_md="$(git diff --cached --name-only --diff-filter=ACMR -- '*.md' || true)"
if [ -n "$staged_md" ]; then
  fail=0
  while IFS= read -r f; do
    [ -f "$ROOT/$f" ] || continue
    case "$f" in
      # Calibration fixtures intentionally contain neuroslop
      */examples/before-after.md|tests/fixtures/*) continue ;;
      # Anti-pattern catalogues quote the patterns they document
      */references/banned-patterns*.md|common/references/banned-patterns*.md) continue ;;
      # CHANGELOG quotes new linter categories when shipping them
      CHANGELOG.md) continue ;;
      # User guide and launch drafts cite banned patterns as examples
      docs/USER-GUIDE.md|docs/LAUNCH-POST.md|docs/launch-posts/*) continue ;;
    esac
    code=0
    python3 "$ROOT/writer/scripts/lint.py" "$ROOT/$f" --quiet || code=$?
    if [ "$code" = "2" ]; then
      echo "pre-commit: $f flagged as neuroslop suspected — fix or bypass with --no-verify"
      fail=1
    fi
  done <<<"$staged_md"
  if [ "$fail" = "1" ]; then
    exit 1
  fi
fi

# 2) Smoke gate (validate + snapshot tests + lint regression)
if [ -x "$ROOT/scripts/smoke.sh" ] || [ -f "$ROOT/scripts/smoke.sh" ]; then
  bash "$ROOT/scripts/smoke.sh" >/dev/null
fi
HOOK_EOF

chmod +x "$HOOK"
echo "installed pre-commit hook → $HOOK"
echo "  ↳ runs writer linter on staged .md and bash scripts/smoke.sh"
echo "  ↳ bypass once: git commit --no-verify"
