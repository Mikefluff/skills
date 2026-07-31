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
  hard_ban_files=""
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
    # A file may declare itself a catalogue of anti-patterns. Several SKILL.md
    # files list the phrases they exist to strip ("world-class", "Click here"),
    # and walkthroughs demonstrate slop being cleaned. Linting those for slop
    # measures the examples, not the prose. The marker lives in the file so this
    # list stops growing every time a skill documents what it bans.
    if head -40 "$ROOT/$f" | grep -q '<!-- lint-role: catalogue -->'; then
      continue
    fi
    # Read verdict and gate as separate signals. The exit code cannot carry both:
    # a hard ban returns 3, which would otherwise mask a "neuroslop suspected"
    # density verdict and let the worse file through.
    read -r verdict gate <<EOF
$(python3 "$ROOT/writer/scripts/lint.py" "$ROOT/$f" --json 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["verdict"].split()[0], d["gate"])' 2>/dev/null \
  || echo "clean pass")
EOF
    # The gate targets prose deliverables. This repo's own Russian documentation
    # uses em-dashes throughout — references/typography.md scopes the ban to
    # "прозы и виральных постов". Worth naming, not worth refusing the commit.
    if [ "$gate" = "fail" ]; then
      hard_ban_files="$hard_ban_files $f"
    fi
    if [ "$verdict" = "neuroslop" ]; then
      echo "pre-commit: $f flagged as neuroslop suspected — fix, add"
      echo "  <!-- lint-role: catalogue -->  if it quotes patterns on purpose,"
      echo "  or bypass once with --no-verify"
      fail=1
    fi
  done <<<"$staged_md"
  if [ -n "$hard_ban_files" ]; then
    echo "pre-commit: hard bans present (not blocking):$hard_ban_files"
    echo "  run  python3 writer/scripts/lint.py <file>  to see them"
  fi
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
