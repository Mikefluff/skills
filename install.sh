#!/usr/bin/env bash
# install.sh — installer for Mikefluff/skills (Claude Code skill collection)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --skills writer,viral-text
#   bash install.sh --copy-from .                 # install from local checkout
#   bash install.sh --update                      # re-pull latest and overwrite
#   bash install.sh --version 0.2.0               # install specific tag
#
# Flags:
#   --skills <a,b,c>      Install only the listed skills (default: all)
#   --copy-from <path>    Install from a local repo checkout instead of GitHub release
#   --update              Force overwrite of existing skill directories
#   --version <tag>       Install a specific release tag (default: latest)
#   --prefix <path>       Override install prefix (default: ~/.claude/skills)
#   --dry-run             Print actions without executing
#   --help                Show this help

set -euo pipefail

REPO_OWNER="Mikefluff"
REPO_NAME="skills"
REPO_SLUG="${REPO_OWNER}/${REPO_NAME}"
DEFAULT_PREFIX="${HOME}/.claude/skills"

# Defaults
SKILLS_FILTER=""
COPY_FROM=""
FORCE_UPDATE="false"
TARGET_VERSION="latest"
PREFIX="${DEFAULT_PREFIX}"
DRY_RUN="false"

log()  { printf '  %s\n' "$*" >&2; }
note() { printf '\033[2m%s\033[0m\n' "$*" >&2; }
warn() { printf '\033[33m! %s\033[0m\n' "$*" >&2; }
err()  { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; }
ok()   { printf '\033[32m✓ %s\033[0m\n' "$*" >&2; }

die() { err "$*"; exit 1; }

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
}

# Parse args
while [ $# -gt 0 ]; do
  case "$1" in
    --skills)     SKILLS_FILTER="$2"; shift 2 ;;
    --copy-from)  COPY_FROM="$2";     shift 2 ;;
    --update)     FORCE_UPDATE="true"; shift ;;
    --version)    TARGET_VERSION="$2"; shift 2 ;;
    --prefix)     PREFIX="$2";        shift 2 ;;
    --dry-run)    DRY_RUN="true";     shift ;;
    --help|-h)    usage ;;
    *) die "Unknown flag: $1 (try --help)" ;;
  esac
done

have_cmd() { command -v "$1" >/dev/null 2>&1; }

require_cmd() {
  for cmd in "$@"; do
    have_cmd "$cmd" || die "missing required command: $cmd"
  done
}

run() {
  if [ "$DRY_RUN" = "true" ]; then
    note "[dry-run] $*"
  else
    eval "$@"
  fi
}

# ---- Source resolution -----------------------------------------------------

resolve_source() {
  if [ -n "$COPY_FROM" ]; then
    [ -d "$COPY_FROM" ] || die "--copy-from path does not exist: $COPY_FROM"
    [ -f "$COPY_FROM/skills.json" ] || die "--copy-from path missing skills.json: $COPY_FROM"
    SRC_DIR="$(cd "$COPY_FROM" && pwd)"
    SRC_VERSION="$(cat "$SRC_DIR/VERSION" 2>/dev/null || echo "local")"
    note "source: local checkout at $SRC_DIR (version $SRC_VERSION)"
    return
  fi

  require_cmd curl tar

  if [ "$TARGET_VERSION" = "latest" ]; then
    note "fetching latest release tag from GitHub..."
    if have_cmd jq; then
      TARGET_VERSION="$(curl -fsSL "https://api.github.com/repos/${REPO_SLUG}/releases/latest" | jq -r '.tag_name')"
    else
      TARGET_VERSION="$(curl -fsSL "https://api.github.com/repos/${REPO_SLUG}/releases/latest" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')"
    fi
    [ -n "$TARGET_VERSION" ] && [ "$TARGET_VERSION" != "null" ] || die "could not resolve latest release tag (no releases yet?)"
  fi

  case "$TARGET_VERSION" in
    v*) TAG="$TARGET_VERSION" ;;
    *)  TAG="v$TARGET_VERSION" ;;
  esac

  TARBALL_URL="https://github.com/${REPO_SLUG}/archive/refs/tags/${TAG}.tar.gz"
  TMPDIR="$(mktemp -d)"
  trap 'rm -rf "$TMPDIR"' EXIT

  note "downloading $TARBALL_URL"
  if ! curl -fsSL "$TARBALL_URL" -o "$TMPDIR/skills.tar.gz"; then
    die "failed to download tarball — does tag $TAG exist?"
  fi
  run "tar -xzf '$TMPDIR/skills.tar.gz' -C '$TMPDIR'"

  SRC_DIR="$(find "$TMPDIR" -maxdepth 1 -mindepth 1 -type d | head -n1)"
  [ -d "$SRC_DIR" ] || die "unexpected tarball layout"
  SRC_VERSION="$(cat "$SRC_DIR/VERSION" 2>/dev/null || echo "${TAG#v}")"
  note "source: tarball $TAG → $SRC_DIR (version $SRC_VERSION)"
}

# ---- Skill enumeration -----------------------------------------------------

enumerate_skills() {
  local manifest="$SRC_DIR/skills.json"
  [ -f "$manifest" ] || die "manifest not found: $manifest"

  if have_cmd jq; then
    ALL_SKILLS="$(jq -r '.skills[].name' "$manifest" | tr '\n' ' ')"
  else
    ALL_SKILLS="$(grep -oE '"name": *"[^"]+"' "$manifest" | sed -E 's/.*"name": *"([^"]+)".*/\1/' | tr '\n' ' ')"
  fi

  if [ -n "$SKILLS_FILTER" ]; then
    INSTALL_SKILLS="$(echo "$SKILLS_FILTER" | tr ',' ' ')"
    # validate every requested skill exists in manifest
    for s in $INSTALL_SKILLS; do
      case " $ALL_SKILLS " in
        *" $s "*) ;;
        *) die "unknown skill: $s (available: $ALL_SKILLS)" ;;
      esac
    done
  else
    INSTALL_SKILLS="$ALL_SKILLS"
  fi
}

# ---- Install ---------------------------------------------------------------

install_one() {
  local name="$1"
  local src="$SRC_DIR/$name"
  local dst="$PREFIX/$name"

  if [ ! -d "$src" ] || [ ! -f "$src/SKILL.md" ]; then
    warn "skipping $name (no SKILL.md in $src)"
    return
  fi

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    if [ "$FORCE_UPDATE" != "true" ]; then
      warn "$name already installed at $dst (use --update to overwrite)"
      return
    fi
    run "rm -rf '$dst'"
  fi

  run "cp -R '$src' '$dst'"
  ok "installed $name → $dst"
}

write_install_marker() {
  local marker="$PREFIX/.skills-collection.json"
  local payload
  payload="$(cat <<EOF
{
  "collection": "${REPO_SLUG}",
  "version": "${SRC_VERSION}",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "skills": [$(echo "$INSTALL_SKILLS" | tr ' ' '\n' | grep -v '^$' | sed 's/.*/"&"/' | paste -sd, -)]
}
EOF
  )"
  if [ "$DRY_RUN" = "true" ]; then
    note "[dry-run] would write $marker:"
    note "$payload"
  else
    printf '%s\n' "$payload" >"$marker"
  fi
}

# ---- Main ------------------------------------------------------------------

main() {
  log ""
  log "Mikefluff/skills installer"
  log "─────────────────────────"

  resolve_source
  enumerate_skills

  mkdir -p "$PREFIX"

  log ""
  log "Installing to: $PREFIX"
  log "Skills:        $(echo "$INSTALL_SKILLS" | tr -s ' ' ' ')"
  log "Force update:  $FORCE_UPDATE"
  log "Dry run:       $DRY_RUN"
  log ""

  for skill in $INSTALL_SKILLS; do
    install_one "$skill"
  done

  write_install_marker

  log ""
  ok "done. installed $(echo $INSTALL_SKILLS | wc -w | tr -d ' ') skills at $PREFIX"
  log ""
  log "Next steps:"
  log "  • Open Claude Code — skills will be auto-discovered by name"
  log "  • To check for updates later: invoke /skills-update inside Claude Code"
  log "  • To uninstall a skill:       rm -rf $PREFIX/<skill-name>"
  log ""
}

main "$@"
