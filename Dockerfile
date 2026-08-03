# Mikefluff/skills — Docker image
#
# Ships the writer linter (pure Python regex, no LLM) plus all skill markdown,
# for users who want to lint prose in CI / containerized workflows without
# running `curl | bash` on their host.
#
# Usage
# -----
#
#   # Lint a single file
#   docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work/draft.md
#
#   # Lint all .md in cwd
#   docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint-all /work
#
#   # Print the writer linter's category coverage
#   docker run --rm ghcr.io/mikefluff/skills coverage
#
#   # Shell into the image (skills mounted at /skills)
#   docker run --rm -it --entrypoint /bin/sh ghcr.io/mikefluff/skills
#
# Tags
# ----
#   :latest     — main branch (always rebuilds)
#   :X.Y.Z      — pinned to a specific release (Docker convention: no `v` prefix)
#   :X.Y        — minor-stream alias
#   :X          — major-stream alias
#
# Build locally
# -------------
#   docker build -t mikefluff/skills .
#   docker run --rm -v "$PWD:/work" mikefluff/skills lint /work/README.md

FROM python:3.12-alpine AS base

LABEL org.opencontainers.image.title="Mikefluff/skills"
LABEL org.opencontainers.image.description="Prose-editing Claude Code skills + offline writer linter"
LABEL org.opencontainers.image.source="https://github.com/Mikefluff/skills"
LABEL org.opencontainers.image.licenses="MIT"

RUN apk add --no-cache \
      bash \
      git \
    && adduser -D -u 1000 lint

WORKDIR /skills

# Copy in lean order so that changes to docs/tests don't bust the layer
# containing the linter itself.
COPY writer/scripts/ /skills/writer/scripts/
COPY writer/SKILL.md /skills/writer/
COPY writer/references/ /skills/writer/references/
COPY writer/examples/ /skills/writer/examples/

# Copy remaining skills (read-only reference material — useful inside the image
# but not needed for lint.py to run).
COPY audio-mix-maker/    /skills/audio-mix-maker/
COPY avatar-maker/       /skills/avatar-maker/
COPY banner-maker/       /skills/banner-maker/
COPY bg-remover/         /skills/bg-remover/
COPY canon-check/        /skills/canon-check/
COPY carousel-builder/   /skills/carousel-builder/
COPY cold-email/         /skills/cold-email/
COPY cover-maker/        /skills/cover-maker/
COPY essay-write/        /skills/essay-write/
COPY flyer-maker/        /skills/flyer-maker/
COPY gif-maker/          /skills/gif-maker/
COPY image-prompt/       /skills/image-prompt/
COPY landing-copy/       /skills/landing-copy/
COPY logo-maker/         /skills/logo-maker/
COPY meme-card-maker/    /skills/meme-card-maker/
COPY microcopy/          /skills/microcopy/
COPY music-prompt/       /skills/music-prompt/
COPY pelevin-digression/ /skills/pelevin-digression/
COPY post-publisher/     /skills/post-publisher/
COPY proposal-maker/     /skills/proposal-maker/
COPY prose-edit/         /skills/prose-edit/
COPY quote-card-maker/   /skills/quote-card-maker/
COPY reel-builder/       /skills/reel-builder/
COPY release-notes/      /skills/release-notes/
COPY research-brief/     /skills/research-brief/
COPY rfc-writer/         /skills/rfc-writer/
COPY skills-keys/        /skills/skills-keys/
COPY skills-styles/      /skills/skills-styles/
COPY skills-update/      /skills/skills-update/
COPY style-check/        /skills/style-check/
COPY style-suggest/      /skills/style-suggest/
COPY style-transfer/     /skills/style-transfer/
COPY subtitle-burner/    /skills/subtitle-burner/
COPY thumbnail-maker/    /skills/thumbnail-maker/
COPY tone-shifter/       /skills/tone-shifter/
COPY transcribe-maker/   /skills/transcribe-maker/
COPY translation-sync/   /skills/translation-sync/
COPY upscaler/           /skills/upscaler/
COPY video-prompt/       /skills/video-prompt/
COPY viral-text/         /skills/viral-text/
COPY voiceover-maker/    /skills/voiceover-maker/

# Shared runner layer + style libraries. Not a skill, so not in skills.json,
# and therefore not in the generated list above — it needs its own line.
COPY common/             /skills/common/

# Helper scripts the entrypoint dispatches to
COPY scripts/coverage.py /skills/scripts/coverage.py
COPY scripts/lint-description.py /skills/scripts/lint-description.py
COPY scripts/validate.sh /skills/scripts/validate.sh
COPY skills.json /skills/skills.json
COPY VERSION /skills/VERSION
COPY README.md /skills/README.md

# Lightweight entrypoint dispatch
COPY <<'ENTRYPOINT' /usr/local/bin/skills-entrypoint.sh
#!/usr/bin/env bash
# NB: no `set -e` — the lint loop intentionally handles non-zero exits.
set -uo pipefail

cmd="${1:-lint-all}"
shift || true

case "$cmd" in
  lint)
    # Lint a single file
    exec python3 /skills/writer/scripts/lint.py "$@"
    ;;
  lint-all)
    # Lint every *.md in the given dir (default /work)
    dir="${1:-/work}"
    fail=0
    while IFS= read -r -d '' f; do
      out="$(python3 /skills/writer/scripts/lint.py "$f" 2>&1)"
      code=$?
      verdict="$(printf '%s\n' "$out" | head -1)"
      if [ "$code" -ge 2 ]; then
        printf 'FAIL: %s — %s\n' "$f" "$verdict"
        printf '%s\n' "$out" | head -15
        printf '\n'
        fail=1
      else
        printf 'OK:   %s — %s\n' "$f" "$verdict"
      fi
    done < <(find "$dir" -type f -name "*.md" \
             -not -path "*/node_modules/*" \
             -not -path "*/.git/*" \
             -not -path "*/vendor/*" \
             -print0)
    exit "$fail"
    ;;
  coverage)
    # Print linter category coverage stats
    exec python3 /skills/scripts/coverage.py
    ;;
  validate)
    # Validate skills.json + frontmatter
    exec bash /skills/scripts/validate.sh
    ;;
  list)
    # List installed skills
    python3 -c "
import json
m = json.load(open('/skills/skills.json'))
print(f\"Mikefluff/skills v{m['version']} — {len(m['skills'])} skills\")
for s in m['skills']:
    layer = s.get('layer', '?')
    langs = '/'.join(s.get('languages', []))
    print(f\"  {s['name']:<22} {layer:<8} {langs}\")
"
    ;;
  version)
    cat /skills/VERSION
    ;;
  help|-h|--help)
    cat <<EOF
Mikefluff/skills — Docker entrypoint

Commands:
  lint FILE                 lint a single markdown file
  lint-all [DIR]            lint every *.md in DIR (default /work)
  coverage                  print linter category coverage
  validate                  validate skills.json + frontmatter
  list                      list installed skills
  version                   print collection version
  help                      this message

Mount your working directory as /work:
  docker run --rm -v "\$PWD:/work" ghcr.io/mikefluff/skills lint-all /work

EOF
    ;;
  *)
    echo "skills-entrypoint: unknown command: $cmd" >&2
    echo "Try: skills-entrypoint help" >&2
    exit 2
    ;;
esac
ENTRYPOINT
RUN chmod +x /usr/local/bin/skills-entrypoint.sh

USER lint
WORKDIR /work

ENTRYPOINT ["/usr/local/bin/skills-entrypoint.sh"]
CMD ["help"]
