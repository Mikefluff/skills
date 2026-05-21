# skills

[![ci](https://github.com/Mikefluff/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Mikefluff/skills/actions/workflows/ci.yml)
[![version](https://img.shields.io/github/v/release/Mikefluff/skills?label=version)](https://github.com/Mikefluff/skills/releases/latest)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

AI content toolkit for [Claude Code](https://docs.claude.com/en/docs/claude-code/skills) — prose editing without LLM-shaped output, AI media generation (image / video / music) with optional in-line execution, and end-to-end content orchestrators (research → carousel / reel). Russian-first, English-capable.

**Twenty-two skills** across five layers: one base + thirteen wrappers + three linters + three orchestrators + two meta. Plain markdown, MIT-licensed, no required external deps (ffmpeg is optional for reel stitching).

---

## Install

```bash
# Curl — 5 seconds, no deps
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

Other methods (npm, Homebrew, Docker, local checkout, pinned version, custom prefix): [`docs/INSTALL.md`](docs/INSTALL.md).

Skills appear after Claude Code session restart. Discovery is automatic via the `name:` and `description:` fields in each skill's frontmatter — no `~/.claude/settings.json` edits required.

**API keys** (for `--execute` mode — entirely optional): manage via `/skills-keys add OPENAI_API_KEY ...` inside Claude Code, or copy `.env.example` to `~/.skills.env`. See [Managing keys](#managing-api-keys) below.

---

## Start here

- **[Quickstart](docs/QUICKSTART.md)** — your first 5 minutes
- **[User Guide](docs/USER-GUIDE.md)** — full scenarios index
- **[Walkthroughs](docs/walkthroughs/)** — 19 step-by-step recipes, categorized
- **[Skill Index](docs/SKILL-INDEX.md)** — all 22 skills by layer/domain/language
- **[Composing recipes](docs/COMPOSING.md)** — named workflows for chaining skills
- **[Style library](common/style-library/)** — 50 visual + directorial + genre presets used by carousel-builder / reel-builder / music-prompt

If something looks wrong: [FAQ](docs/FAQ.md) · [Troubleshooting](docs/TROUBLESHOOTING.md).

---

## What you can do

### Write & edit prose

| Scenario | Skill(s) | Walkthrough |
|---|---|---|
| Clean an LLM-shaped draft | [`writer`](writer/) | [USER-GUIDE](docs/USER-GUIDE.md#i-just-want-to-clean-a-draft) |
| Viral social post (RU + EN) | [`viral-text`](viral-text/) → writer | [RU](docs/walkthroughs/viral-post.md) · [EN](docs/walkthroughs/en-viral-post.md) |
| Edit a fiction chapter (Pelevin/Manson voice) | [`prose-edit`](prose-edit/) → writer | [fiction-chapter](docs/walkthroughs/fiction-chapter.md) |
| Draft a long-form essay (RU) | [`essay-write`](essay-write/) → writer | [non-fiction](docs/walkthroughs/non-fiction.md) |
| Verify a trilingual translation (RU/EN/PT-BR) | [`translation-sync`](translation-sync/) | [translation-parity](docs/walkthroughs/translation-parity.md) |
| Audit a chapter against your story bible | [`canon-check`](canon-check/) | [canon-check-audit](docs/walkthroughs/canon-check-audit.md) |
| Insert a Pelevin-style digression | [`pelevin-digression`](pelevin-digression/) | [digression-insertion](docs/walkthroughs/digression-insertion.md) |
| Rewrite in a different register (formal↔casual…) | [`tone-shifter`](tone-shifter/) → writer | [tone-shift](docs/walkthroughs/tone-shift.md) |
| Write a cold outreach email | [`cold-email`](cold-email/) → writer | [cold-email-pitch](docs/walkthroughs/cold-email-pitch.md) |
| Write UX microcopy (errors / empty states / tooltips) | [`microcopy`](microcopy/) → writer | [microcopy-error-states](docs/walkthroughs/microcopy-error-states.md) |
| Write release notes / changelog | [`release-notes`](release-notes/) → writer | [release-notes-saas](docs/walkthroughs/release-notes-saas.md) |
| Write an RFC / ADR / design doc | [`rfc-writer`](rfc-writer/) → writer | [rfc-architecture](docs/walkthroughs/rfc-architecture.md) |
| Write landing / SEO / ad copy | [`landing-copy`](landing-copy/) → writer | [landing-launch](docs/walkthroughs/landing-launch.md) |

### Generate AI media (prompt-first, execute optional)

| Scenario | Skill(s) | Walkthrough |
|---|---|---|
| Generate an image prompt for 14+ models (Midjourney v7, Flux 2, Imagen 4 Ultra, Nano Banana Pro, gpt-image-2, Ideogram 3, Seedream 4.5, …) | [`image-prompt`](image-prompt/) | [image-prompt-cover](docs/walkthroughs/image-prompt-cover.md) |
| Generate a video prompt for 20+ models (Veo 3.1 + audio, Sora 2, Kling 3.0, Runway Gen-4 / Aleph V2V, Luma Ray 3, Pika, Hailuo, Hunyuan, Wan 2.2, Seedance, …) | [`video-prompt`](video-prompt/) | [video-prompt-reel](docs/walkthroughs/video-prompt-reel.md) |
| Generate a music prompt for 10+ models (Suno v5.5, Udio v4, Lyria 3 Pro, ElevenLabs Music, Stable Audio 2.5, MusicGen, …) | [`music-prompt`](music-prompt/) | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-an-ai-music-prompt) |
| Actually run the prompt through the vendor API and save a real PNG / MP4 / MP3 | any of the three above + `--execute` | [execute-end-to-end](docs/walkthroughs/execute-end-to-end.md) |

### Orchestrate end-to-end

| Scenario | Skill(s) | Walkthrough |
|---|---|---|
| Research a topic with cited sources (WebSearch + WebFetch + optional Firecrawl/Exa MCP) | [`research-brief`](research-brief/) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |
| Turn topic / research into an N-slide Instagram / LinkedIn / TikTok carousel (24 visual styles, batch execute) | [`carousel-builder`](carousel-builder/) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |
| Turn topic / research / script into a vertical reel (12 directorial styles + 12 music genres + ffmpeg stitch) | [`reel-builder`](reel-builder/) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |

### Manage the collection

| Scenario | Skill | Walkthrough |
|---|---|---|
| Manage API keys (add / remove / update / verify / enable gate flags) | [`skills-keys`](skills-keys/) | [skills-keys/examples/before-after.md](skills-keys/examples/before-after.md) |
| Update the collection itself | [`skills-update`](skills-update/) | n/a — invoke directly |
| Auto-lint every git commit | [`style-check`](style-check/) | [pre-commit-hook](docs/walkthroughs/pre-commit-hook.md) |
| Run a read-only quality gate | [`style-check`](style-check/) | [style-check-gate](docs/walkthroughs/style-check-gate.md) |

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
| [`skills-keys`](skills-keys/) | meta | en/ru | Manage API keys for the runner's --execute layer. CRUD on ~/.skills.env (chmod 600): list / add / update / remove / enable / disable gate flags / verify (ping vendor APIs) / export. Single source of truth for OPENAI / GEMINI / BFL / FAL / REPLICATE / RUNWAY / KLING / SUNO / ELEVENLABS / IDEOGRAM / ANTHROPIC keys + gate flags + S3 storage env vars. Explicit shell exports always win over file entries. |
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

Skills compose: wrappers call `writer` internally; linters reference the same rule files but don't mutate; orchestrators chain multiple wrappers + the execute runner. See [docs/COMPOSING.md](docs/COMPOSING.md) for the full dependency graph and named workflows.

---

## The `--execute` layer (optional)

`image-prompt`, `video-prompt`, `music-prompt` produce paste-ready prompts by default. Pass `--execute` and they ALSO call the vendor API and save real PNG / MP4 / MP3 assets. Without API keys they stay prompt-only — no breakage.

`carousel-builder` and `reel-builder` are orchestrators built on this layer — they assemble batches of prompts and execute them with a single style anchor + cost confirmation.

```bash
# image
~/.claude/skills/image-prompt/scripts/run.py --execute --model gpt-image-2 --prompt "..."

# video (cost confirmation prompts; --yes to skip)
~/.claude/skills/video-prompt/scripts/run.py --execute --model veo-3-1-fast --prompt "..." --duration 8

# music
~/.claude/skills/music-prompt/scripts/run.py --execute --model suno-v5-5 --prompt "..." --lyrics-file ./lyrics.txt
```

Vendors covered: OpenAI (gpt-image-2, Sora 2, TTS), Google (Imagen 4, Nano Banana Pro, Veo 3.1, Lyria 3 Pro), Black Forest Labs (Flux family + Kontext), Runway (Gen-4 + Aleph), Kuaishou (Kling 3.0), Ideogram (3 Turbo/Default/Quality), ElevenLabs (Music + TTS), Suno (v5.5), fal.ai + Replicate routers for everything else (Seedream, Hunyuan, LTX-2, Wan, MusicGen, Stable Audio, many open-source).

Output: assets land at `./generated/<modality>/<timestamp>-<model>.<ext>`. If `S3_BUCKET` is set, they also upload to S3-compatible storage (AWS S3 / DigitalOcean Spaces / Cloudflare R2 / MinIO) and the URL is printed alongside.

Setup is one command:

```bash
# Inside Claude Code, after install
/skills-keys add OPENAI_API_KEY sk-proj-...
/skills-keys add GEMINI_API_KEY AIza...
/skills-keys verify             # ping each vendor; confirm valid/invalid/unknown
```

The runner auto-creates `~/.claude/skills/.runners-venv` and installs Python deps (requires Python ≥ 3.10). Override with `SKILLS_SKIP_VENV=1` if Python is missing.

Full provider matrix + cost preview + per-vendor troubleshooting: `image-prompt/references/execute.md`, `video-prompt/references/execute.md`, `music-prompt/references/execute.md`.

---

## Managing API keys

Keys for the `--execute` layer live in `~/.skills.env` (chmod 600). The runner auto-loads it into `os.environ` at every CLI startup — explicit shell exports still win.

```bash
/skills-keys list                                    # masked overview
/skills-keys add OPENAI_API_KEY                      # interactive (silent stdin prompt)
/skills-keys update OPENAI_API_KEY sk-proj-new...    # rotate
/skills-keys remove OPENAI_API_KEY
/skills-keys enable SUNO_API_ENABLED                 # gate-flag shortcut
/skills-keys verify                                  # ping 9 providers (OpenAI/Gemini/Anthropic/BFL/Ideogram/Replicate/FAL/Runway/Eleven)
/skills-keys export                                  # eval-ready lines for current shell
```

Full reference: [skills-keys/references/usage.md](skills-keys/references/usage.md) · [examples](skills-keys/examples/before-after.md).

Don't have an API key for one of these vendors? The matching skill stays in prompt-only mode — paste the generated prompt into the vendor's UI manually. No skill requires any key.

---

## Updating

```bash
/skills-update                                       # in-Claude check + apply
bash install.sh --check                              # CLI version diff
bash install.sh --update                             # re-install from latest release
```

Optional ambient banner in your shell status line (opt-in): `bash scripts/install-hook.sh`. Shows ` · skills v2.3.0→2.3.1 +1 skill` when an update exists. Never updates without confirmation.

---

## Common install flags

```bash
# Install a subset
curl -fsSL .../install.sh | bash -s -- --skills writer,viral-text

# Custom prefix
curl -fsSL .../install.sh | bash -s -- --prefix /tmp/skills

# Pin a version
curl -fsSL .../install.sh | bash -s -- --version 2.3.0

# Update existing install (re-install + new deps)
bash install.sh --update

# Diff local vs latest
bash install.sh --check

# Uninstall everything
bash install.sh --uninstall
```

Full installer help: `bash install.sh --help` · [`docs/INSTALL.md`](docs/INSTALL.md).

---

## Repo layout

```
skills/
├── README.md                # this file
├── VERSION                  # semver, single source of truth
├── CHANGELOG.md             # Keep-a-Changelog
├── skills.json              # machine-readable manifest used by the installer
├── install.sh               # pure-bash installer, curl-pipeable
├── .env.example             # template for ~/.skills.env (manage via /skills-keys)
├── Makefile                 # local dev convenience
├── CONTRIBUTING.md          # how to add / report / propose a skill
│
├── <skill-name>/            # 22 skills, one folder each
│
├── common/
│   ├── references/          # shared anti-pattern catalogues (hype words, preambles, …)
│   ├── runners/             # optional Python execute layer (image/video/music)
│   │   ├── providers/       # 14 image + 10 video + 5 music + 2 audio = 31 providers
│   │   ├── cli/             # per-modality CLI entries (image / video / music / carousel / reel / keys)
│   │   ├── styles.py        # style library loader
│   │   ├── batch.py         # parallel executor for carousel / reel
│   │   ├── ffmpeg.py        # concat / audio mix / caption burn-in
│   │   ├── keysfile.py      # CRUD over ~/.skills.env
│   │   ├── verify.py        # HTTP probes for 9 providers
│   │   └── requirements.txt
│   └── style-library/       # 50 bundled styles (24 carousel + 12 director + 12 music)
│
├── docs/
│   ├── QUICKSTART.md        # 5-minute first run
│   ├── USER-GUIDE.md        # scenarios with TOC
│   ├── COMPOSING.md         # dependency graph + named workflows
│   ├── INSTALL.md           # detailed install methods
│   ├── SKILL-INDEX.md       # auto-generated, by layer/domain/language
│   ├── FAQ.md               # short Q&A
│   ├── TROUBLESHOOTING.md   # when things break
│   ├── VERSIONING.md        # semver policy + release flow
│   ├── LINTER-COVERAGE.md   # auto-generated regex coverage
│   ├── LAUNCH-POST.md       # frozen v1.9 launch copy
│   └── walkthroughs/
│       ├── README.md        # categorized index
│       └── *.md             # 19 detailed flows
│
├── scripts/                 # validate + smoke + doc generators
├── hooks/                   # ambient update banner (opt-in)
├── tests/                   # fixture snapshots
├── bin/                     # the `skills` CLI shim (npm package)
└── .github/                 # workflows + issue/PR templates + SECURITY.md
```

---

## Local development

```bash
make help                       # list all targets
make install                    # install from this checkout into ~/.claude/skills/
make smoke                      # validate + linter regression + fixture snapshots
make check-docs                 # docs-consistency gate
make gen-readme                 # regenerate the skills table
make new-skill NAME=foo-bar DESC="..."
```

Releases are manual — bump `VERSION`, write the CHANGELOG entry, tag `vX.Y.Z`, push tag, create GitHub Release. See [docs/VERSIONING.md](docs/VERSIONING.md).

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](LICENSE).
