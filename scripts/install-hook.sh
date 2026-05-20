#!/usr/bin/env bash
# install-hook.sh — idempotently install the skills-update-banner.js status-line
# hook into Claude Code's user settings.
#
# Usage:
#   bash scripts/install-hook.sh              # install (with confirmation if conflict)
#   bash scripts/install-hook.sh --yes        # install, accept safe defaults on conflict
#   bash scripts/install-hook.sh --uninstall  # remove ONLY if statusLine points to our banner
#   bash scripts/install-hook.sh --settings <path>   # override settings.json location

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK_PATH="$REPO_ROOT/hooks/skills-update-banner.js"

SETTINGS_PATH="${HOME}/.claude/settings.json"
ASSUME_YES="false"
DO_UNINSTALL="false"

log()   { printf '  %s\n' "$*" >&2; }
note()  { printf '\033[2m%s\033[0m\n' "$*" >&2; }
warn()  { printf '\033[33m! %s\033[0m\n' "$*" >&2; }
err()   { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; }
ok()    { printf '\033[32m✓ %s\033[0m\n' "$*" >&2; }

die()   { err "$*"; exit 1; }

usage() {
  sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
}

while [ $# -gt 0 ]; do
  case "$1" in
    --yes|-y)    ASSUME_YES="true"; shift ;;
    --uninstall) DO_UNINSTALL="true"; shift ;;
    --settings)  SETTINGS_PATH="$2"; shift 2 ;;
    --help|-h)   usage ;;
    *) die "Unknown flag: $1 (try --help)" ;;
  esac
done

have_cmd() { command -v "$1" >/dev/null 2>&1; }

require_cmd() {
  for c in "$@"; do have_cmd "$c" || die "missing required command: $c"; done
}

require_cmd python3

# ---- Helpers ---------------------------------------------------------------

py_eval() {
  # py_eval <script> [<settings-path>] [<hook-path>]
  # All settings access goes through python for safe JSON r/w.
  python3 - "$SETTINGS_PATH" "$HOOK_PATH" <<PY
import json, os, sys
settings_path, hook_path = sys.argv[1], sys.argv[2]

def load():
    if not os.path.exists(settings_path):
        return {}
    try:
        with open(settings_path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None  # corrupt

def save(data):
    os.makedirs(os.path.dirname(settings_path) or ".", exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

action = $1
if action == "status":
    data = load()
    if data is None:
        print("CORRUPT"); sys.exit(0)
    sl = data.get("statusLine")
    if not isinstance(sl, dict):
        print("ABSENT"); sys.exit(0)
    cmd = sl.get("command", "")
    if hook_path in cmd:
        print("OURS")
    else:
        print("OTHER")
        print(cmd)
    sys.exit(0)

if action == "install":
    data = load() or {}
    data["statusLine"] = {
        "type": "command",
        "command": "node " + hook_path,
    }
    save(data)
    sys.exit(0)

if action == "uninstall":
    data = load() or {}
    sl = data.get("statusLine")
    if isinstance(sl, dict) and hook_path in sl.get("command", ""):
        del data["statusLine"]
        save(data)
        print("REMOVED")
    else:
        print("NOT_OURS")
    sys.exit(0)

sys.exit(2)
PY
}

# ---- Main ------------------------------------------------------------------

log ""
log "skills-update-banner — hook installer"
log "───────────────────────────────────"
note "settings:  $SETTINGS_PATH"
note "hook:      $HOOK_PATH"
log ""

[ -f "$HOOK_PATH" ] || die "hook script not found at $HOOK_PATH"

if [ "$DO_UNINSTALL" = "true" ]; then
  result="$(py_eval '"uninstall"' 2>&1 || true)"
  case "$result" in
    REMOVED)
      ok "uninstalled — restart Claude Code session for the change to take effect"
      ;;
    NOT_OURS)
      warn "settings.json statusLine does not point to our hook — nothing to remove"
      ;;
    *)
      warn "unexpected result: $result"
      ;;
  esac
  log ""
  exit 0
fi

# Default: install / re-confirm
status="$(py_eval '"status"' 2>&1 || true)"
existing_cmd=""
case "$status" in
  CORRUPT*)
    die "settings.json at $SETTINGS_PATH is not valid JSON — fix it first"
    ;;
  OURS*)
    ok "already installed (settings.json statusLine points to our hook)"
    log "  restart Claude Code session if you haven't recently"
    log ""
    exit 0
    ;;
  ABSENT*)
    note "no existing statusLine in settings — clean install"
    ;;
  OTHER*)
    existing_cmd="$(printf '%s' "$status" | sed -n '2p')"
    warn "settings.json already has a different statusLine command:"
    printf '    \033[2m%s\033[0m\n' "$existing_cmd" >&2
    log ""
    if [ "$ASSUME_YES" = "true" ]; then
      note "(--yes given; defaulting to CANCEL — we won't clobber)"
      log ""
      exit 0
    fi
    log "Choose:"
    log "  o — overwrite (replace existing with ours)"
    log "  c — cancel (default, recommended)"
    printf '  ? [o/C] ' >&2
    read -r choice
    case "$choice" in
      o|O) note "overwriting" ;;
      *)   note "cancelled — your existing statusLine is preserved"; exit 0 ;;
    esac
    ;;
  *)
    die "unexpected status from settings probe: $status"
    ;;
esac

py_eval '"install"'
ok "installed"
log ""
log "Verify:"
log "  cat $SETTINGS_PATH"
log ""
log "Restart any active Claude Code session for the banner to appear."
log "To remove later:  bash scripts/install-hook.sh --uninstall"
log ""
