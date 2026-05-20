#!/usr/bin/env bash
# install.sh — installer for Mikefluff/skills (Claude Code skill collection)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --skills writer,viral-text
#   bash install.sh --copy-from .                 # install from local checkout
#   bash install.sh --update                      # re-pull latest and overwrite
#   bash install.sh --version 0.2.0               # install specific tag
#   bash install.sh --list                        # print available skills, exit
#   bash install.sh --check                       # report local-vs-remote version, exit
#   bash install.sh --uninstall                   # remove all installed skills + marker
#
# Flags:
#   --skills <a,b,c>      Install only the listed skills (default: all)
#   --copy-from <path>    Install from a local repo checkout instead of GitHub release
#   --update              Force overwrite of existing skill directories
#   --prune               With --update: remove installed skills NOT in the new manifest
#   --version <tag>       Install a specific release tag (default: latest)
#   --prefix <path>       Override install prefix (default: ~/.claude/skills)
#   --list                Print available skills (from manifest) and exit
#   --check               Report local marker vs latest release and exit
#   --uninstall           Remove all skills listed in the install marker + the marker
#   --yes / -y            Skip confirmation prompts
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
PRUNE="false"
TARGET_VERSION="latest"
PREFIX="${DEFAULT_PREFIX}"
DRY_RUN="false"
ASSUME_YES="false"
MODE="install"   # install | list | check | uninstall

log()  { printf '  %s\n' "$*" >&2; }
note() { printf '\033[2m%s\033[0m\n' "$*" >&2; }
warn() { printf '\033[33m! %s\033[0m\n' "$*" >&2; }
err()  { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; }
ok()   { printf '\033[32m✓ %s\033[0m\n' "$*" >&2; }

die() { err "$*"; exit 1; }

usage() {
  sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
}

# Parse args
while [ $# -gt 0 ]; do
  case "$1" in
    --skills)     SKILLS_FILTER="$2"; shift 2 ;;
    --copy-from)  COPY_FROM="$2";     shift 2 ;;
    --update)     FORCE_UPDATE="true"; shift ;;
    --prune)      PRUNE="true";       shift ;;
    --version)    TARGET_VERSION="$2"; shift 2 ;;
    --prefix)     PREFIX="$2";        shift 2 ;;
    --dry-run)    DRY_RUN="true";     shift ;;
    --list)       MODE="list";        shift ;;
    --check)      MODE="check";       shift ;;
    --uninstall)  MODE="uninstall";   shift ;;
    --yes|-y)     ASSUME_YES="true";  shift ;;
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
    "$@"
  fi
}

confirm() {
  if [ "$ASSUME_YES" = "true" ]; then
    return 0
  fi
  printf '  %s [y/N] ' "$1" >&2
  read -r ans
  case "$ans" in
    y|Y|yes|YES) return 0 ;;
    *) return 1 ;;
  esac
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
  run tar -xzf "$TMPDIR/skills.tar.gz" -C "$TMPDIR"

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
    run rm -rf "$dst"
  fi

  run cp -R "$src" "$dst"
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

# ---- New modes -------------------------------------------------------------

read_marker() {
  local marker="$PREFIX/.skills-collection.json"
  if [ ! -f "$marker" ]; then
    echo ""
    return
  fi
  cat "$marker"
}

extract_marker_version() {
  # arg: marker JSON content (string)
  printf '%s' "$1" | grep -oE '"version": *"[^"]+"' | head -n1 | sed -E 's/.*"version": *"([^"]+)".*/\1/'
}

extract_marker_skills() {
  printf '%s' "$1" | grep -oE '"skills": *\[[^]]*\]' | head -n1 |
    grep -oE '"[a-z0-9_-]+"' | sed 's/"//g' | tr '\n' ' '
}

fetch_remote_tag() {
  require_cmd curl
  local tag
  if have_cmd jq; then
    tag="$(curl -fsSL "https://api.github.com/repos/${REPO_SLUG}/releases/latest" | jq -r '.tag_name' 2>/dev/null || true)"
  else
    tag="$(curl -fsSL "https://api.github.com/repos/${REPO_SLUG}/releases/latest" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/' || true)"
  fi
  [ -z "$tag" ] || [ "$tag" = "null" ] && return 1
  printf '%s' "${tag#v}"
}

semver_cmp() {
  # echoes -1 / 0 / 1 for a < b / a == b / a > b
  local a="$1" b="$2"
  local av bv
  for i in 1 2 3; do
    av="$(printf '%s' "$a" | cut -d. -f"$i")"
    bv="$(printf '%s' "$b" | cut -d. -f"$i")"
    av="${av:-0}"
    bv="${bv:-0}"
    [ "$av" -lt "$bv" ] && { echo -1; return; }
    [ "$av" -gt "$bv" ] && { echo 1; return; }
  done
  echo 0
}

cmd_list() {
  resolve_source
  enumerate_skills
  local manifest="$SRC_DIR/skills.json"
  log ""
  log "Mikefluff/skills — available (v${SRC_VERSION})"
  log "──────────────────────────────────────────"
  for s in $ALL_SKILLS; do
    local desc=""
    if have_cmd jq; then
      desc="$(jq -r --arg n "$s" '.skills[] | select(.name==$n) | .description' "$manifest" 2>/dev/null || echo "")"
    fi
    if [ -n "$desc" ]; then
      printf '  \033[32m%-22s\033[0m %s\n' "$s" "${desc:0:120}" >&2
    else
      printf '  \033[32m%s\033[0m\n' "$s" >&2
    fi
  done
  log ""
}

cmd_check() {
  log ""
  log "Mikefluff/skills — version check"
  log "──────────────────────────────"
  local marker local_v remote_v cmp
  marker="$(read_marker)"
  if [ -z "$marker" ]; then
    warn "not installed — run install.sh to bootstrap"
    log ""
    return 0
  fi
  local_v="$(extract_marker_version "$marker")"
  [ -n "$local_v" ] || { warn "marker present but version unreadable"; return 0; }

  note "local:  v${local_v}"
  if ! remote_v="$(fetch_remote_tag)"; then
    warn "could not reach GitHub — try again later"
    return 0
  fi
  note "remote: v${remote_v}"

  cmp="$(semver_cmp "$local_v" "$remote_v")"
  if [ "$cmp" = "0" ]; then
    ok "up to date — v${local_v}"
  elif [ "$cmp" = "-1" ]; then
    warn "update available — v${local_v} → v${remote_v}"
    log "  (run install.sh --update OR invoke /skills-update inside Claude Code)"
  else
    note "local is ahead of latest release — nothing to do"
  fi
  log ""
}

cmd_uninstall() {
  local marker local_v installed
  marker="$(read_marker)"
  if [ -z "$marker" ]; then
    warn "no install marker at $PREFIX — nothing to uninstall"
    return 0
  fi
  local_v="$(extract_marker_version "$marker")"
  installed="$(extract_marker_skills "$marker")"
  [ -n "$installed" ] || { warn "marker has no skills list — manual cleanup required"; return 0; }

  log ""
  log "Mikefluff/skills — uninstall"
  log "──────────────────────────"
  log "Prefix:    $PREFIX"
  log "Version:   v${local_v}"
  log "Will remove:"
  for s in $installed; do
    log "  • $s"
  done
  log "  • .skills-collection.json (marker)"
  log ""

  if ! confirm "proceed?"; then
    note "aborted by user"
    return 0
  fi

  for s in $installed; do
    local dst="$PREFIX/$s"
    if [ -e "$dst" ] || [ -L "$dst" ]; then
      run rm -rf "$dst"
      ok "removed $s"
    else
      note "$s already absent"
    fi
  done
  run rm -f "$PREFIX/.skills-collection.json"
  ok "uninstalled"
  log ""
}

prune_removed() {
  # Called after install_one loop when --update + --prune.
  # Remove skills under PREFIX that were in the OLD marker but NOT in the new INSTALL_SKILLS.
  local marker old_skills new_set name
  marker="$(read_marker)"
  [ -z "$marker" ] && return 0
  old_skills="$(extract_marker_skills "$marker")"
  [ -z "$old_skills" ] && return 0

  new_set=" $INSTALL_SKILLS "
  for name in $old_skills; do
    case "$new_set" in
      *" $name "*) ;;  # still present, keep
      *)
        local dst="$PREFIX/$name"
        if [ -e "$dst" ] || [ -L "$dst" ]; then
          run rm -rf "$dst"
          ok "pruned $name (no longer in upstream manifest)"
        fi
        ;;
    esac
  done
}

# ---- Main ------------------------------------------------------------------

main() {
  case "$MODE" in
    list)
      cmd_list
      ;;
    check)
      cmd_check
      ;;
    uninstall)
      cmd_uninstall
      ;;
    install)
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
      log "Prune:         $PRUNE"
      log "Dry run:       $DRY_RUN"
      log ""

      for skill in $INSTALL_SKILLS; do
        install_one "$skill"
      done

      if [ "$FORCE_UPDATE" = "true" ] && [ "$PRUNE" = "true" ]; then
        prune_removed
      fi

      write_install_marker

      log ""
      ok "done. installed $(echo "$INSTALL_SKILLS" | wc -w | tr -d ' ') skills at $PREFIX"
      log ""
      log "Next steps:"
      log "  • Open Claude Code — skills will be auto-discovered by name"
      log "  • To check for updates later: invoke /skills-update inside Claude Code"
      log "  • Want ambient update banner?  bash scripts/install-hook.sh"
      log "  • To uninstall:                 bash install.sh --uninstall"
      log ""
      ;;
  esac
}

main "$@"
