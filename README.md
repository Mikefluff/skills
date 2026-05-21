# skills

[![ci](https://github.com/Mikefluff/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Mikefluff/skills/actions/workflows/ci.yml)
[![release](https://github.com/Mikefluff/skills/actions/workflows/release.yml/badge.svg)](https://github.com/Mikefluff/skills/actions/workflows/release.yml)
[![version](https://img.shields.io/github/v/release/Mikefluff/skills?label=version)](https://github.com/Mikefluff/skills/releases/latest)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A small, opinionated collection of [Claude Code](https://docs.claude.com/en/docs/claude-code/skills) skills for editing prose without producing text that reads like LLM output. Russian-first, English-capable.

**Twenty-one skills**, one base linter + thirteen wrappers + three linters + three orchestrators + one meta-skill. Plain markdown, MIT-licensed, no required external deps (ffmpeg optional for reel stitching).

---

## Install

```bash
# Curl (5 seconds, no deps)
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

# npm
npm install -g @mikefluff/skills && skills install

# Homebrew (after tap)
brew tap mikefluff/tap https://github.com/Mikefluff/homebrew-tap
brew install mikefluff/tap/skills && skills install

# Docker (for CI — no install into ~/.claude needed)
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work/draft.md
```

Skills appear after Claude Code session restart. Discovery is automatic via `name:` and `description:` in each skill's frontmatter — no `~/.claude/settings.json` edits required.

For all install options + troubleshooting, see [`docs/INSTALL.md`](docs/INSTALL.md).

---

## First time? Start here

**→ [User Guide](docs/USER-GUIDE.md)** — pick your scenario, walk through it end-to-end.

**→ [Skill Index](docs/SKILL-INDEX.md)** — all 21 skills indexed by layer, domain, and language.

**→ [Composing recipes](docs/COMPOSING.md)** — 14 named workflows showing how to chain skills.

Quick scenario picker:

| You want to … | Walkthrough |
|---|---|
| Write a viral social-media post | [RU](docs/walkthroughs/viral-post.md) · [EN](docs/walkthroughs/en-viral-post.md) |
| Edit a fiction chapter | [fiction-chapter](docs/walkthroughs/fiction-chapter.md) |
| Draft a long-form essay | [non-fiction](docs/walkthroughs/non-fiction.md) |
| Verify a multilingual translation | [translation-parity](docs/walkthroughs/translation-parity.md) |
| Auto-lint every commit | [pre-commit-hook](docs/walkthroughs/pre-commit-hook.md) |
| Audit a chapter against your story bible | [canon-check-audit](docs/walkthroughs/canon-check-audit.md) |
| Insert a Pelevin-vector digression | [digression-insertion](docs/walkthroughs/digression-insertion.md) |
| Run a read-only quality gate | [style-check-gate](docs/walkthroughs/style-check-gate.md) |
| Rewrite text in a different register | [USER-GUIDE](docs/USER-GUIDE.md#tone-shifter--register-rewrites) |
| Draft a cold outreach email | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-a-cold-email) |
| Generate an AI image prompt (Midjourney v7 / Flux 2 / Imagen 4 / Nano Banana Pro / gpt-image-2 / Ideogram 3 / Seedream 4.5 / Qwen-Image / HiDream / SD 3.5 — edit, multi-ref, text-in-image) | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-an-ai-image-prompt) |
| Generate an AI video prompt (Veo 3.1 + audio, Sora 2 + cameos, Kling 3.0 / Elements, Runway Gen-4 / Aleph V2V, Luma Ray 3, Pika 2.2, Hailuo 02, Higgsfield, LTX-2, Hunyuan, Wan 2.2, Seedance — T2V / I2V / V2V / multi-shot / dialogue) | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-an-ai-video-prompt) |
| Generate an AI music prompt (Suno v5.5, Udio v4, Lyria 3 Pro, ElevenLabs Music, Stable Audio 2.5, MusicGen — meta-tags, `\|` stacking, two-box Style+Lyrics workflow, 12 genre recipes) | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-an-ai-music-prompt) |
| Write UX microcopy (errors, empty states, tooltips, buttons) | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-ux-microcopy) |
| Write release notes / changelogs | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-release-notes) |
| Write an RFC / ADR / design doc | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-an-rfc--design-doc) |
| Write marketing copy (landing / SEO / ads) | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-marketing-copy) |
| Research a topic with cited sources (WebSearch + WebFetch + optional Firecrawl / Exa MCP) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |
| Build an Instagram / LinkedIn / TikTok carousel end-to-end (24 visual styles + batch execute) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |
| Build a vertical reel end-to-end (12 directorial styles + 12 music genres + ffmpeg stitch) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |

If something looks wrong: [FAQ](docs/FAQ.md) · [Troubleshooting](docs/TROUBLESHOOTING.md).

---

## What's in the box

<!-- BEGIN skills-table (auto-generated; run `make gen-readme`) -->

| Skill | Layer | Languages | Purpose |
| --- | --- | --- | --- |
| [`writer`](writer/) | base | ru/en | Base clean-prose editor — antinyeyroslop (28 categories), typography, structural synthetics, RU calques. Invoked by all other prose skills. |
| [`viral-text`](viral-text/) | wrapper | ru/en | Write viral social media content — hooks, numbered points, micro-conclusion with NLP question, CTA. 41 viral content rules + platform adaptation. |
| [`prose-edit`](prose-edit/) | wrapper | ru | Fiction rewrite layer — Pelevin/Manson voice vector, 10-item style drift checklist, no meta-refs / anglicisms in narrator voice, long artistic rewrite (no comma-stitching), ToV pattern, 5-trigger structural-synthesis detector, Postirony depth-pass. |
| [`essay-write`](essay-write/) | wrapper | ru | Non-fiction layer — long subordinate sentences (Manson style), source-backed claims, philosophy through humor, biography through scenes, plain-Russian for complex content. |
| [`style-check`](style-check/) | linter | ru/en | Read-only pre-commit lint that stacks writer + prose-edit + essay-write rules. Routes by configurable path patterns (fiction vs non-fic), BLOCKING/WARNING/INFO severity, exit-code semantics for git hook. |
| [`translation-sync`](translation-sync/) | linter | ru/en/pt-br | Read-only pre-commit parity checker for trilingual book translations (RU↔EN↔PT-BR) — typography per language, terminology canon, anchor-quote drift, names/patronymics/diminutives, cultural realia footnotes, no-smoothing of numbers/brands/dates. BLOCKING/WARNING/INFO severity with exit-code semantics for git hook. |
| [`canon-check`](canon-check/) | linter | ru/en | Story-bible consistency auditor for any book series. Greps entities (characters / artifacts / locations) in changed chapters, cross-references the project's story-bible document, flags BLOCKING contradictions / WARNING gaps / INFO new details. Read-only — trust the text, not memory. |
| [`pelevin-digression`](pelevin-digression/) | wrapper | ru | Write a Pelevin-style digression for a fiction or non-fiction passage — 12 structural techniques + 5 banned constructions. Wraps prose-edit (fiction) or essay-write (non-fic). Invoked by request, not auto-applied. |
| [`skills-update`](skills-update/) | meta | en/ru | User-invocable update check + apply for this collection. Compares local install marker with latest GitHub release, shows CHANGELOG diff, asks for confirmation, runs install.sh --update. |
| [`tone-shifter`](tone-shifter/) | wrapper | en/ru | Rewrite a passage in a different register (formal↔casual, business↔academic, technical↔friendly, plain-explainer) without changing meaning. 6 registers + named transformation deltas. Wraps writer as final cleanup. |
| [`cold-email`](cold-email/) | wrapper | en/ru | Write or rewrite cold outreach emails (first-touch, follow-up, intro request, re-engage). 5-block structure, ≤120-word budget, banned ceremony patterns, anti-template subject lines. Wraps writer as final cleanup. |
| [`image-prompt`](image-prompt/) | wrapper | en/ru | Write prompts for 14+ frontier AI image generators (Midjourney v7, Flux 2 / Flux Kontext, Imagen 4 Ultra, Nano Banana Pro / Gemini 3 Image, gpt-image-2, Ideogram 3, Recraft V3, Seedream 4.5, Qwen-Image, HiDream-O1, Krea-1, SD 3.5, SDXL). Modes: text-to-image, edit (preserve/change), multi-reference, text-in-image. 6-part formula + per-model deltas, character/identity locks, weighted multi-ref. |
| [`video-prompt`](video-prompt/) | wrapper | en/ru | Write prompts for 20+ frontier AI video generators (Veo 3.1 + native audio, Sora 2 + cameos, Kling 3.0 / Elements, Runway Gen-4 / Aleph V2V / Act-One, Luma Ray 3 / Modify, Pika 2.2 / Pikaframes, Hailuo 02, Higgsfield, LTX-2, HunyuanCustom, Wan 2.2, Seedance). Modes: T2V / I2V / V2V / extend / multi-shot / dialogue+audio. CHARACTER FIRST law, beat structure, exact camera vocabulary, identity-reference grammar, pacing modes (incl. dialogue-scene + music-video). |
| [`music-prompt`](music-prompt/) | wrapper | en/ru | Write prompts for 10+ frontier AI music generators (Suno v5.5, Udio v4, Google Lyria 3 Pro, ElevenLabs Music, Stable Audio 2.5, MusicGen, Tencent SongGeneration, Sonauto v2, Riffusion, Mubert). 2026 canonical 8-category meta-tag taxonomy, `\|` stacking, two-box Style+Lyrics workflow (Suno), exclude-styles (Eleven), field-driven (Lyria). 12 genre recipes. |
| [`microcopy`](microcopy/) | wrapper | en/ru | Write UX microcopy — error messages, empty states, tooltips, button labels, helper text, modals, 404/500 pages, onboarding. Plain language, action-oriented, never blame user, length budgets per element type. Wraps writer for final cleanup. |
| [`release-notes`](release-notes/) | wrapper | en/ru | Write user-facing release notes + changelogs. Keep-a-Changelog format, sections Added/Changed/Fixed/Deprecated/Removed/Security. Per-audience tone (user/dev/ops). Anti-marketing-fluff bans. Wraps writer. |
| [`rfc-writer`](rfc-writer/) | wrapper | en/ru | Write engineer-facing design docs — RFCs, ADRs, Tech Specs, Design Docs. Structure: context/problem/proposal/alternatives/consequences/decision. RFC 2119 (MUST/SHOULD/MAY). Review checklist for spotting weak alternatives sections. |
| [`landing-copy`](landing-copy/) | wrapper | en/ru | Write marketing copy — landing page sections (hero/features/pricing/FAQ), SEO meta (title+description+OG+Twitter), ad copy (Google/Facebook/LinkedIn/X). Julian Shapiro hero formula, char limits per platform. Wraps writer. |
| [`research-brief`](research-brief/) | orchestrator | en/ru | Produce a structured research brief on any topic — TL;DR, key facts with citations, notable quotes, suggested angles, open questions. 3-15 queries by depth, multi-source (WebSearch + WebFetch + optional Firecrawl/Exa MCP). Output is a markdown file ready for downstream consumption by carousel-builder, reel-builder, viral-text, essay-write, landing-copy. |
| [`carousel-builder`](carousel-builder/) | orchestrator | en/ru | Turn a topic or research brief into an N-slide Instagram / LinkedIn / TikTok carousel with consistent visual style and ready-to-post captions. Wraps essay-write + viral-text + image-prompt --execute + common style library (24 visual styles). Outputs PNG slides + captions.md + manifest. Modes: --topic / --research; --style auto\|<library-id>\|--style-ref <image>; --slides 3-12; --platform instagram\|linkedin\|tiktok; --text-mode embedded\|overlay\|none; --execute; --resume. |
| [`reel-builder`](reel-builder/) | orchestrator | en/ru | Turn a topic / research brief / script into a vertical reel: 1-4 video shots + matched background music + ffmpeg-stitched final.mp4 with optional burned-in captions. Wraps viral-text + video-prompt --execute + music-prompt --execute + common video/music style library + ffmpeg. Outputs final.mp4 + shots/ + music.mp3 + script.md + manifest. Modes: --topic / --research / --script-file; --shots 1-5; --style auto\|<library-id>; --music-style auto\|<library-id>; --captions on\|off; --execute; --resume. |

<!-- END skills-table -->

Skills compose: wrappers call `writer` internally; linters reference the same rule files but don't mutate. See [docs/COMPOSING.md](docs/COMPOSING.md) for the dependency graph.

---

## Optional API execution (v2.2+)

The `image-prompt`, `video-prompt`, and `music-prompt` skills can call vendor APIs and save real PNG / MP4 / MP3 assets when API keys are set in env. Without keys, the skills stay prompt-only — the v2.1 behaviour.

`install.sh` auto-creates `~/.claude/skills/.runners-venv` and installs the Python deps (requires Python ≥ 3.10) — **no separate `pip install` step**. Per-skill `scripts/run.py` re-execs through that venv automatically. Override with `SKILLS_SKIP_VENV=1 bash install.sh ...` to skip auto-venv (or if Python is missing).

Setup (one-time):

```bash
cp .env.example ~/.skills.env
${EDITOR:-vi} ~/.skills.env                    # fill in keys you have
set -a; source ~/.skills.env; set +a
```

Usage:

```bash
# image
python3 ~/.claude/skills/image-prompt/scripts/run.py --list-providers
python3 ~/.claude/skills/image-prompt/scripts/run.py --model gpt-image-2 --prompt "..."

# video (cost confirmation prompts; --yes to skip)
python3 ~/.claude/skills/video-prompt/scripts/run.py --model veo-3-1-fast --prompt "..." --duration 8

# music
python3 ~/.claude/skills/music-prompt/scripts/run.py --model suno-v5-5 --prompt "..." --lyrics-file ./lyrics.txt
```

Provider coverage:

- **OpenAI**: gpt-image-2 (image), Sora 2 / Sora 2 Pro (video — gated), gpt-4o-mini-tts (audio)
- **Google**: Imagen 4 / 4 Ultra / 4 Fast, Nano Banana Pro (image); Veo 3.1 / Fast (video); Lyria 3 Pro (music — gated)
- **Black Forest Labs**: Flux 1.1 Pro, Flux 2 Pro, Flux Kontext, Flux Schnell
- **Runway**: Gen-4, Gen-4 Turbo, Aleph
- **Kuaishou**: Kling 3.0
- **Ideogram**: Ideogram 3 Turbo / Default / Quality
- **ElevenLabs**: Eleven Music, Eleven TTS
- **Suno**: Suno v5.5 (gated)
- **fal.ai + Replicate routers**: cross-vendor — Flux, Seedream, Hunyuan, LTX-2, Wan, MusicGen, Stable Audio, many open-source models accessible through one of these two routers.

Output: assets land at `./generated/<modality>/<timestamp>-<model>.<ext>`. If `S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY` are also set, they're uploaded to your bucket (AWS S3 / DigitalOcean Spaces / Cloudflare R2 / MinIO supported) and the URL is printed alongside.

Full provider matrix + cost preview + troubleshooting: see `image-prompt/references/execute.md`, `video-prompt/references/execute.md`, `music-prompt/references/execute.md`.

---

## Updates

Three ways, increasing in eagerness:

1. **On demand:** invoke `/skills-update` inside Claude Code.
2. **Ambient status-line banner** *(opt-in)*: `bash scripts/install-hook.sh`. Shows ` · skills v1.0.1→1.2.0 +1 skill` when an update exists.
3. **CLI:** `bash install.sh --check` / `bash install.sh --update [--prune]`.

The banner / `/skills-update` never updates without explicit user confirmation.

---

## Common install flags

```bash
# install a subset
curl -fsSL .../install.sh | bash -s -- --skills writer,viral-text

# install to a custom prefix
curl -fsSL .../install.sh | bash -s -- --prefix /tmp/skills

# pin a specific version
curl -fsSL .../install.sh | bash -s -- --version 1.0.1

# re-install (overwrite existing skills)
bash install.sh --update

# check what's installed vs what's available
bash install.sh --check

# uninstall everything
bash install.sh --uninstall
```

Full installer help: `bash install.sh --help`.

---

## Repo layout

```
skills/
├── README.md                # this file
├── VERSION                  # semver, single source of truth
├── CHANGELOG.md             # Keep-a-Changelog
├── skills.json              # machine-readable manifest used by installer
├── install.sh               # pure-bash installer, curl-pipeable
├── Makefile                 # local dev convenience
├── CONTRIBUTING.md          # how to add a skill / report a bug / propose new one
├── docs/
│   ├── USER-GUIDE.md        # ← start here as a user
│   ├── walkthroughs/        # detailed per-scenario flows
│   ├── FAQ.md
│   ├── TROUBLESHOOTING.md
│   ├── COMPOSING.md         # dependency graph + composition patterns
│   ├── VERSIONING.md        # semver policy + release flow
│   └── LINTER-COVERAGE.md   # auto-generated regex coverage
├── scripts/
│   ├── validate.sh          # frontmatter + cross-link + description-quality check
│   ├── check-docs-consistency.sh  # skills.json ↔ README ↔ USER-GUIDE ↔ walkthroughs
│   ├── gen-skills-table.py  # regenerate the README skills table from skills.json
│   ├── smoke.sh             # validate + writer linter regression + fixture snapshots
│   ├── coverage.py          # regenerate docs/LINTER-COVERAGE.md
│   ├── bump.sh              # bump VERSION + promote [Unreleased] CHANGELOG section
│   ├── new-skill.sh         # bootstrap a new skill folder
│   ├── decide-bump.sh       # parse conventional commits since last tag
│   ├── lint-description.py  # frontmatter description quality (advisory)
│   └── install-hook.sh      # idempotent status-line banner installer
├── hooks/
│   └── skills-update-banner.js
├── tests/                   # fixture snapshots for writer/scripts/lint.py
├── .github/                 # workflows + issue/PR templates + SECURITY.md
└── <skill-name>/            # the 18 skills, one folder each
```

---

## Local development

```bash
make help                       # list all targets
make install                    # install from this checkout to ~/.claude/skills/
make smoke                      # validate + linter regression + fixture snapshots
make check-docs                 # docs-consistency gate
make gen-readme                 # regenerate skills table
make new-skill NAME=foo-bar DESC="..."
```

Releases are automatic — push a conventional-commit message (`feat:`, `fix:`, `feat!:`, etc.) and `.github/workflows/release.yml` bumps + tags + publishes. See [docs/VERSIONING.md](docs/VERSIONING.md).

Want to contribute? Read [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome.

---

## License

MIT — see [LICENSE](LICENSE).
