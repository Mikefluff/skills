# User guide

The full scenarios index. New to the collection? Start with [QUICKSTART.md](QUICKSTART.md) — 5-minute first run. Then come back here when you need a specific scenario.

If you haven't installed yet:

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

Skills auto-discover after Claude Code restart. No `~/.claude/settings.json` edits required.

---

## Contents

- [Pick your scenario (jump table)](#pick-your-scenario)
- [The collection in one paragraph](#the-collection-in-one-paragraph)
- [Prose editing](#prose-editing)
- [Marketing & ops prose](#marketing--ops-prose)
- [AI media generation](#ai-media-generation)
- [Orchestrators (end-to-end)](#orchestrators-end-to-end)
- [Meta (collection management)](#meta-collection-management)
- [Composing skills + CI](#composing-skills--ci)

---

## Pick your scenario

Jump straight to the section for what you want to do.

### Write & edit prose

| You want to … | Section |
|---|---|
| Clean an LLM-shaped draft | [§ writer](#i-just-want-to-clean-a-draft) |
| Edit a fiction chapter | [§ prose-edit](#i-want-to-edit-a-fiction-chapter) |
| Write a long-form essay | [§ essay-write](#i-want-to-write-a-long-form-essay) |
| Verify a trilingual translation | [§ translation-sync](#i-want-to-verify-a-translation) |
| Audit against the story bible | [walkthrough](walkthroughs/canon-check-audit.md) |
| Insert a Pelevin-style digression | [walkthrough](walkthroughs/digression-insertion.md) |
| Rewrite in a different register | [§ tone-shifter](#tone-shifter--register-rewrites) |
| Read-only quality gate | [walkthrough](walkthroughs/style-check-gate.md) |
| Auto-lint every git commit | [walkthrough](walkthroughs/pre-commit-hook.md) |

### Marketing & ops prose

| You want to … | Section |
|---|---|
| Viral social-media post | [walkthroughs: RU](walkthroughs/viral-post.md) · [EN](walkthroughs/en-viral-post.md) |
| Cold outreach email | [§ cold-email](#i-want-to-write-a-cold-email) |
| UX microcopy | [§ microcopy](#i-want-to-write-ux-microcopy) |
| Release notes / changelog | [§ release-notes](#i-want-to-write-release-notes) |
| RFC / ADR / design doc | [§ rfc-writer](#i-want-to-write-an-rfc--design-doc) |
| Landing / SEO / ad copy | [§ landing-copy](#i-want-to-write-marketing-copy) |

### AI media generation

| You want to … | Section |
|---|---|
| Image prompt (14+ models) | [§ image-prompt](#i-want-to-write-an-ai-image-prompt) |
| Video prompt (20+ models) | [§ video-prompt](#i-want-to-write-an-ai-video-prompt) |
| Music prompt (10+ models) | [§ music-prompt](#i-want-to-write-an-ai-music-prompt) |

### Orchestrators (end-to-end)

| You want to … | Section |
|---|---|
| Research a topic with citations | [§ research-brief](#i-want-to-research-a-topic) |
| Build an N-slide carousel | [§ carousel-builder](#i-want-to-build-a-carousel) |
| Build a vertical reel | [§ reel-builder](#i-want-to-build-a-reel) |
| Full chain (research → carousel + reel) | [walkthrough](walkthroughs/research-to-carousel-reel.md) |

### Manage the collection

| You want to … | Section |
|---|---|
| Manage API keys (CRUD + verify) | [§ skills-keys](#i-want-to-manage-api-keys) |
| Update the collection | [walkthrough](#i-want-to-update-the-collection) |

Stuck? [FAQ](FAQ.md) · [Troubleshooting](TROUBLESHOOTING.md).

---

## The collection in one paragraph

Twenty-two skills layered on top of one base linter (`writer`):

- **Base**: `writer` strips 28 categories of LLM-prose tells from any text, in RU or EN. Runs as a final pass under every other prose skill.
- **Wrappers** (call `writer` automatically): 13 skills covering prose editing (`viral-text`, `prose-edit`, `essay-write`, `pelevin-digression`, `tone-shifter`), marketing + ops (`cold-email`, `microcopy`, `release-notes`, `rfc-writer`, `landing-copy`), and AI media prompts (`image-prompt`, `video-prompt`, `music-prompt`).
- **Linters** (read-only — produce reports, don't edit): `style-check` for pre-commit prose lint, `translation-sync` for RU/EN/PT-BR parity, `canon-check` for story-bible consistency.
- **Orchestrators** (end-to-end pipelines): `research-brief` produces cited research; `carousel-builder` turns topics into N-slide carousels; `reel-builder` produces stitched vertical reels with matched music.
- **Meta**: `skills-update` (apply newer release of this collection) and `skills-keys` (manage `~/.skills.env` API keys for the `--execute` layer).

Skills work on any text file (`.md`, `.tex`, `.txt`, …) — there's no assumed file format or project layout.

For the dependency graph and named workflows, see [COMPOSING.md](COMPOSING.md).
For an index of every skill by layer / domain / language, see [SKILL-INDEX.md](SKILL-INDEX.md).
For the categorized walkthrough list, see [walkthroughs/README.md](walkthroughs/README.md).

---

## Prose editing

### "I just want to clean a draft"

You don't need any of the wrappers. Invoke `writer` directly:

```
/writer clean
<paste your text>
```

It returns the cleaned text plus a short summary of what was fixed.

For an offline pre-check (no Claude call) — pipe your file through the linter:

```bash
python3 ~/.claude/skills/writer/scripts/lint.py path/to/draft.md
```

Exit codes: `0` clean · `1` borderline (2-4 hits) · `2` neuroslop suspected (5+ hits or one category 3+ times).

---

### "I want a viral post"

Invoke `/viral-text` with your topic. The skill researches the topic via WebSearch, then produces hook + 5 numbered points + micro-conclusion + CTA. Full walkthrough: [viral-post.md](walkthroughs/viral-post.md).

```
/viral-text [topic]
/viral-text [topic] platform=instagram points=3 lang=en
```

---

### "I want to edit a fiction chapter"

`/prose-edit chapter path/to/ch07.md` produces a list of proposed rewrites (staccato → long subordinate, comma-stitching → real subordination, double-negation → affirmative, etc.). Author reviews + accepts/rejects. Full walkthrough: [fiction-chapter.md](walkthroughs/fiction-chapter.md).

If you have a story bible, chain with `/canon-check chapter <book> ch07` afterwards to catch character / artifact / location drift.

---

### "I want to write a long-form essay"

`/essay-write chapter` asks for your thesis in one sentence, runs WebSearch for 3-5 sources, proposes the structure (лид → тезис → 3-7 sections → переход), then drafts the chapter with cited sources in narrative form. Full walkthrough: [non-fiction.md](walkthroughs/non-fiction.md).

If your chapter is a hypothesis chapter (claim isn't established fact), the skill enforces a mandatory **"что опровергнет эту гипотезу"** block — without it the chapter stops being non-fic and becomes a sermon.

---

### "I want to verify a translation"

`/translation-sync chapter <book> ch07` reads RU + EN + PT-BR versions of the same chapter and produces a structured parity report: typography per language, terminology consistency, anchor-quote drift, names / patronymics / diminutives, smoothed numbers. Read-only — you apply the fixes by hand. Full walkthrough: [translation-parity.md](walkthroughs/translation-parity.md).

---

### "I want to rewrite text in a different register" {#tone-shifter--register-rewrites}

`/tone-shifter --to <target> [--from <source>]` rewrites a passage in a named register without changing the underlying claims. Six registers: `casual`, `friendly-professional`, `business-formal`, `academic`, `technical`, `plain-explainer`.

```
/tone-shifter --to business-formal
<paste casual draft>

/tone-shifter --to plain-explainer --from academic
<paste research abstract>
```

Use cases: turning a casual brain-dump into an exec memo, rewriting an academic paragraph for a general audience, softening corporate-speak to friendly-professional. Preserves facts, structure, and information — shifts vocabulary, sentence length, contractions, hedges, jargon level. See `tone-shifter/references/registers.md` for the full taxonomy.

---

---

## Marketing & ops prose

### "I want to write a cold email"

`/cold-email first-touch <recipient-context>` drafts a first-touch outreach to founders, VCs, recruiters, journalists, or partners. 5-block structure (hook / value / ask / easy-yes / sign-off), ≤120-word budget, banned ceremony patterns (no "I hope this email finds you well"), anti-template subject lines.

```
/cold-email first-touch "Sarah at Acorn Capital, VC who led Beta Corp's A round"
/cold-email follow-up <previous email>
/cold-email intro-request via=Marcus to="CISO at MegaCorp" why="audit-log compression"
```

Modes: `first-touch`, `follow-up`, `intro-request` (produces both the email to the intro-giver and the forwardable block), `re-engage`, `forwardable`. See `cold-email/references/structure.md` for the per-variant template.

---

---

## AI media generation

### "I want to write an AI image prompt" {#i-want-to-write-an-ai-image-prompt}

`/image-prompt <topic-or-scene>` generates a prompt for Midjourney, DALL-E, Flux, Nano Banana, or Stable Diffusion. The skill follows a 6-part formula (subject + setting + style + lighting + camera + texture) with model-specific deltas.

```
/image-prompt cover image for the cold-email walkthrough
/image-prompt a confident founder leaning on marble countertop --model midjourney-v6
/image-prompt minimalist product shot of wireless earbuds --model flux-pro --variants 3
```

Targets supported: `midjourney-v6`, `dalle-3`, `flux-pro`, `nano-banana`, `sdxl`. Default style is photorealistic; `--style illustration` / `editorial` / `cinematic` overrides. Lighting and camera vocabulary live in `image-prompt/references/`.

**Execute via API** (v2.2+, optional). When an API key is set in env, add `--execute` to actually generate the image and save it:

```
/image-prompt a confident founder leaning on marble countertop --model gpt-image-2 --execute
/image-prompt minimalist product shot --model imagen-4-ultra --execute --yes
```

Asset lands in `./generated/image/`. Cost confirmation prompts for anything above $0.10 unless `--yes`. Missing key → falls back to prompt-only. Setup: `install.sh` auto-creates the runners venv and installs deps; you only need to export `OPENAI_API_KEY` / `GEMINI_API_KEY` / `BFL_API_KEY` / `FAL_KEY` / `REPLICATE_API_TOKEN` / `IDEOGRAM_API_KEY`. Full provider matrix in `image-prompt/references/execute.md`.

---

### "I want to write an AI video prompt" {#i-want-to-write-an-ai-video-prompt}

`/video-prompt <action-description>` generates a motion prompt for Kling, Veo, Sora, Runway, Pika, Hailuo, or Luma. The skill enforces the **CHARACTER FIRST, CAMERA SECOND** law and beat-structures the motion (Beat 1 / Beat 2 / Beat 3) to prevent the "frozen pose" failure mode.

```
/video-prompt animate this image: woman shouting at man across dinner table --model kling
/video-prompt POV first-person kiteboarder cutting across water --pacing action
/video-prompt slow build of tension between two characters --beat tension --model veo
```

Targets: `kling`, `veo`, `sora`, `runway`, `pika`, `hailuo`, `luma`. Each parses prompts differently — Kling needs explicit temporal markers `First [0-2s]: ... Then [2-5s]: ...`; Sora handles narrative prose; Runway prefers shorter prompts. Pacing modes (`narrative`, `action`, `comedy`, `documentary`, `timelapse`) adjust camera energy rules.

**Execute via API** (v2.2+, optional). Add `--execute` to call the video API and save an MP4. Video gens are long-running — the runner polls and prints progress. ALWAYS confirms cost unless `--yes`:

```
/video-prompt POV first-person kiteboarder --model veo-3-1-fast --duration 8 --execute
/video-prompt animate this still --model kling-3 --image-url ./still.jpg --execute --yes
/video-prompt add snowfall to dusk --model aleph --video-url ./clip.mp4 --execute
```

Setup adds `RUNWAY_API_KEY`, `KLING_ACCESS_KEY_ID` + `KLING_ACCESS_KEY_SECRET`, `OPENAI_SORA_API_ENABLED=1` (once Sora API is available). Full matrix in `video-prompt/references/execute.md`.

---

### "I want to write an AI music prompt" {#i-want-to-write-an-ai-music-prompt}

`/music-prompt <topic-or-brief>` generates a prompt for Suno v5.5, Udio v4, Google Lyria 3 Pro, ElevenLabs Music, Stable Audio 2.5, MusicGen, Tencent SongGeneration, Sonauto v2, Riffusion, or Mubert. The skill applies the 2026 canonical 8-category meta-tag taxonomy (Structure / Vocal delivery / Vocal effects / Instrumental / Mix-production / Energy-dynamics / Era-genre / FX), uses `|` stacking inside brackets, and respects the two-box Style+Lyrics workflow on Suno.

```
/music-prompt anthemic modern pop song about leaving home
/music-prompt UK drill verse about night driving --model suno-v5-5
/music-prompt long-form jazz fusion instrumental --model udio-v4 --instrumental
/music-prompt label-safe epic orchestral cue for trailer --model lyria-3-pro
/music-prompt indie folk ballad, breathy female vocal --model eleven-music --exclude "abrupt ending, electronic drums"
```

Targets: `suno-v5-5`, `udio-v4`, `lyria-3-pro`, `eleven-music`, `stable-audio-2-5`, `musicgen`, `tencent-song-generation`, `sonauto-v2`, `riffusion`, `mubert`. Genre recipes (`hyperpop`, `drill`, `country`, `lo-fi`, `ambient`, `orchestral`, `k-pop`, `afrobeats`, `jazz-fusion`, `hardcore-punk`, `synthwave`, `gospel`) live in `music-prompt/references/genre-recipes.md`. For Suno: brackets go in the Lyrics box ONLY; the Style of Music box accepts natural language only.

**Execute via API** (v2.2+, optional). Suno's two-box workflow maps to `--prompt` (style box) + `--lyrics-file` (lyrics box):

```
/music-prompt anthemic modern pop chorus --model suno-v5-5 --execute
/music-prompt label-safe orchestral cue --model lyria-3-pro --duration 1.5 --execute --yes
/music-prompt indie folk ballad --model eleven-music --execute
```

Setup adds `SUNO_API_KEY` + `SUNO_API_ENABLED=1`, `ELEVENLABS_API_KEY`, `LYRIA_API_ENABLED=1`. Full matrix in `music-prompt/references/execute.md`.

---

### "I want to write UX microcopy" {#i-want-to-write-ux-microcopy}

`/microcopy <element-type> for <context>` writes plain-language, action-oriented UI strings — error messages, empty states, tooltips, button labels, modal copy, 404/500 pages, onboarding cards.

```
/microcopy error message for payment declined
/microcopy empty state for first-time projects view
/microcopy 404 page for our SaaS app
/microcopy button label for canceling a subscription
/microcopy --improve "Click here to download your report"
```

Element types: button / error / empty-state / tooltip / helper-text / modal / 404 / 500 / offline / toast / inline-alert / onboarding-card. Length budgets enforced per type (button ≤ 8 words, modal title ≤ 8 words, etc.). Voice defaults to SaaS friendly-professional; override via product-type or brand-voice profile from `tone-shifter`.

---

### "I want to write release notes" {#i-want-to-write-release-notes}

`/release-notes <version> <changes-list>` writes user-facing release notes / changelogs in Keep-a-Changelog format. Sections: Added / Changed / Fixed / Deprecated / Removed / Security. Per-audience tone (end-user / developer / ops).

```
/release-notes v3.4.0 --from-git v3.3.0..HEAD
/release-notes v2.5 --audience dev --format github-release
/release-notes --recap quarterly Q2-2026
```

Strips marketing fluff ("revolutionary", "we're thrilled to announce"). Past tense for shipped work, ISO dates, specific numbers. For internal design docs → `rfc-writer`. For marketing landing announcements → `landing-copy`.

---

### "I want to write an RFC / design doc" {#i-want-to-write-an-rfc--design-doc}

`/rfc-writer <type> <topic>` writes engineer-facing design documents. Types: `rfc` (proposal under discussion) / `adr` (decision-after-the-fact) / `tech-spec` (HOW to build something decided) / `design-doc` (broad problem-space exploration).

```
/rfc-writer rfc "Migrate from REST to GraphQL"
/rfc-writer adr "Use PostgreSQL 16 for Payments service"
/rfc-writer tech-spec "Payments API v3"
/rfc-writer --review existing-rfc.md
```

Structure: context / problem / proposal / alternatives / consequences / decision / open questions. RFC 2119 keywords (MUST / SHOULD / MAY) for normative statements. Forces at-least-2-alternatives + "do nothing" baseline.

---

### "I want to write marketing copy" {#i-want-to-write-marketing-copy}

`/landing-copy <surface> <product-brief>` writes landing page sections, SEO meta tags, and paid ads. Surfaces:

```
/landing-copy hero "AI code review tool, B2B SaaS, targets eng managers"
/landing-copy features --count 6
/landing-copy seo-meta --page homepage
/landing-copy og-card --page pricing
/landing-copy google-ad <product> --variants 5
/landing-copy facebook-ad <product> --variants 3
/landing-copy linkedin-ad <product>
/landing-copy twitter-ad <product> --variants 3
```

Julian Shapiro hero formula, char limits per platform, i18n expansion factor, banned-pattern strip (no "revolutionary" / "world-class" / "Click here"). For viral organic posts → `viral-text`. For product UI strings → `microcopy`.

---

---

## Orchestrators (end-to-end)

### "I want to research a topic with cited sources" {#i-want-to-research-a-topic}

`/research-brief <topic>` produces a structured markdown brief — TL;DR, key facts with citations, notable quotes, suggested narrative angles, open questions, out-of-reach flags. Multi-source via WebSearch + WebFetch (always) + optional Firecrawl / Exa MCP (probed at runtime).

```
/research-brief "AI productivity tools for solo founders in 2026"
/research-brief "<topic>" --depth quick|standard|deep
/research-brief "<topic>" --format brief|outline|article-ready
/research-brief "<topic>" --for carousel|reel|post|essay|landing   # bias angles
/research-brief "<topic>" --lang en|ru|mixed
/research-brief "<topic>" --sources websearch,webfetch,firecrawl,exa
```

Output: `./generated/research/<topic-slug>-<YYYYMMDD>.md` with the brief + cited sources. The path is printed on the last line of stdout so downstream skills can ingest via `--research <path>`.

`research-brief` is the upstream feeder for `carousel-builder` and `reel-builder`. Chain: research → carousel + reel from the SAME brief = consistent angle across formats.

For full walkthrough: [research-to-carousel-reel](walkthroughs/research-to-carousel-reel.md).

---

### "I want to build a carousel" {#i-want-to-build-a-carousel}

`/carousel-builder --topic "<text>" | --research <path>` orchestrates: split content into N slides → resolve visual style from the bundled 24-style library → pick image provider → generate slides in parallel → write captions + manifest.

```
/carousel-builder --topic "5 mistakes new copywriters make" --platform instagram --slides 6 --style swiss-grid-poster --text-mode embedded --execute
/carousel-builder --research ./generated/research/<brief>.md --platform linkedin --slides 8 --style auto --execute
/carousel-builder --topic "Bauhaus fundamentals" --platform tiktok --slides 10 --style bauhaus-primary --style-ref ./my-mood-board.jpg --model nano-banana-pro --execute
/carousel-builder --topic "<text>" --prompts-only       # dry run: print prompts, don't generate
/carousel-builder --resume                              # re-run failed slides from manifest
```

Style library: 24 visual presets (kinfolk-minimal, swiss-grid-poster, art-deco-gold, neon-cyberpunk, gradient-mesh-modern, dark-academia, …). Browse `common/style-library/carousel/_index.md`. Add custom styles at `~/.claude/style-library/carousel/<id>.md`.

Outputs `./generated/carousel/<slug>/`:
- `slide-1.png ... slide-N.png` (sized per platform)
- `captions.md` (paste-ready post copy + per-slide alt-text)
- `manifest.json` (for --resume)
- `style-used.md` + `prompts.md` (reproducibility + fallback)

Default cost: $0.32-0.80 per 8-slide carousel depending on model. Budget cap: `SKILLS_CAROUSEL_BUDGET=1.50` (override).

For details: [carousel-builder/SKILL.md](../carousel-builder/SKILL.md) and [research-to-carousel-reel](walkthroughs/research-to-carousel-reel.md).

---

### "I want to build a reel" {#i-want-to-build-a-reel}

`/reel-builder --topic "<text>" | --research <path>` orchestrates the most-expensive workflow: script → 1-4 video shots + matched music + ffmpeg-stitched MP4 with optional burned-in captions.

```
/reel-builder --topic "fastest way to write a newsletter" --shots 3 --shot-duration 5 --style chazelle-musical-glow --music-style cinematic-orchestral --captions on --execute
/reel-builder --research ./generated/research/<brief>.md --shots 4 --aspect vertical --execute
/reel-builder --topic "<text>" --prompts-only           # dry run: print script + per-shot prompts
/reel-builder --resume                                  # re-run failed components from manifest
```

Style library: 12 directorial styles (wes-anderson-symmetric, fincher-cold-lowkey, nolan-imax-handheld, refn-neon-static, …) + 12 music genres (cinematic-orchestral, ambient-drone, synthwave, lofi-hiphop-chill, …). The directorial style FILE stores the director's name; the prompt sent to the model does NOT.

Outputs `./generated/reel/<slug>/`:
- `final.mp4` (9:16 vertical, 15s default)
- `shots/shot-{1..N}.mp4` (individual shots — kept for re-use)
- `music.mp3`
- `script.md` (screenplay + per-shot prompts + music prompt — paste fallback)
- `manifest.json`, `style-used.md`

Cost: $2-6 per 15s reel depending on video provider. Default budget cap: `SKILLS_REEL_BUDGET=4.00` — exceeding it triggers a confirmation prompt.

ffmpeg required for final stitch. install.sh offers to `brew install ffmpeg` / `apt-get install -y ffmpeg` automatically. Without ffmpeg, shots + music save separately and the skill prints the manual stitch command.

For details: [reel-builder/SKILL.md](../reel-builder/SKILL.md) and [research-to-carousel-reel](walkthroughs/research-to-carousel-reel.md).

---

---

## Meta (collection management)

### "I want to manage the style library" {#i-want-to-manage-the-style-library}

`/skills-styles` is the management UI for the local style library used by `carousel-builder`, `reel-builder`, and `music-prompt`. Bundled library at `<repo>/common/style-library/<modality>/<id>.md` is read-only; user overrides live at `~/.claude/style-library/<modality>/<id>.md` (user wins on resolution).

```
/skills-styles list                                   # bundled + user-overrides
/skills-styles list carousel --user-only              # only your custom carousel styles
/skills-styles show carousel kinfolk-minimal          # print resolved file
/skills-styles add carousel retro-soviet-poster       # new from template
/skills-styles add carousel my-variant --from kinfolk-minimal   # copy bundled as starting point
/skills-styles edit carousel my-variant               # opens $EDITOR
/skills-styles validate carousel my-variant           # frontmatter + body schema check
/skills-styles diff carousel my-variant               # vs bundled (when overriding)
/skills-styles remove carousel my-variant --force     # delete the user-override
/skills-styles submit carousel my-variant             # build ./style-submission-<ts>/ for upstream PR
```

`submit` validates first, then assembles a self-contained submission package with the file at the correct repo path + `PR-DESCRIPTION.md` template + step-by-step manual PR instructions. Does NOT run `gh pr create` for you (intentional — fork detection + multi-step gh interaction is brittle in v1).

After `add`, the file is a skeleton with `<placeholder>` text. Either edit yourself or ask Claude in chat to fill the content based on your description, then `validate`.

For details: [skills-styles/SKILL.md](../skills-styles/SKILL.md) · [usage reference](../skills-styles/references/usage.md) · [templates schema](../skills-styles/references/templates.md).

---

### "I want to manage API keys" {#i-want-to-manage-api-keys}

`/skills-keys` is the management UI over `~/.skills.env` — the runner's key store. Single source of truth for all `--execute` provider keys + gate flags.

```
/skills-keys list                                  # masked overview
/skills-keys add OPENAI_API_KEY sk-proj-...        # add or update
/skills-keys add OPENAI_API_KEY                    # interactive: silent stdin prompt
/skills-keys update OPENAI_API_KEY sk-new-...      # alias for add
/skills-keys remove OPENAI_API_KEY                 # delete entry
/skills-keys enable SUNO_API_ENABLED               # gate flag → upsert =1
/skills-keys disable LYRIA_API_ENABLED             # gate flag → remove
/skills-keys verify                                # ping all supported providers
/skills-keys verify OPENAI_API_KEY GEMINI_API_KEY  # verify specific keys
/skills-keys path                                  # print the keys-file path
/skills-keys export                                # eval-ready `export KEY="..."` lines
/skills-keys export --mask                         # same, but values masked
```

The file lives at `~/.skills.env` (override via `SKILLS_KEYS_FILE`), chmod 600. Runner loads it into `os.environ` at every CLI startup — explicit shell `export` always wins over file entries.

Verify covers 9 providers via lightweight HTTP probes (OpenAI, Gemini, Anthropic, BFL, Ideogram, Replicate, FAL, Runway, ElevenLabs). Suno + Kling don't expose verify-friendly endpoints — they show `unsupported`.

For details: [skills-keys/SKILL.md](../skills-keys/SKILL.md) and [skills-keys/references/usage.md](../skills-keys/references/usage.md).

---

### "I want auto-lint on every commit"

There's no built-in git-hook installer (we don't want to silently touch your `.git/` directory). The [pre-commit hook walkthrough](walkthroughs/pre-commit-hook.md) gives you a ready-to-paste `.git/hooks/pre-commit` script with two variants:

- Full Claude Code invocation of `/style-check staged` (smart; requires the CLI)
- Offline-only fallback via `python3 .../writer/scripts/lint.py` on staged diff (fast; no Claude needed)

---

### "I want to update the collection" {#i-want-to-update-the-collection}

Three ways:

```
/skills-update                                   # in Claude Code — checks + shows CHANGELOG diff + applies
```

```bash
bash install.sh --check                          # CLI: report version status
bash install.sh --update                         # re-pull latest tarball, overwrite installed skills
bash install.sh --update --prune                 # also remove skills no longer in upstream manifest
```

```bash
bash scripts/install-hook.sh                     # opt-in ambient status-line banner
```

After installing the banner, you'll see ` · skills v2.3.0→2.3.1 +1 skill (some-new-skill)` in your status line when a release is available. Never updates without confirmation.

---

## Composing skills + CI

### Use in your CI

If you want the writer linter to gate every push / PR in your own repository (no Claude Code required — pure Python regex pass), copy our GitHub Action template:

```bash
curl -fsSLO https://raw.githubusercontent.com/Mikefluff/skills/main/.github/workflows-template/skills-lint.yml.template
mv skills-lint.yml.template .github/workflows/skills-lint.yml
git add .github/workflows/skills-lint.yml && git commit -m "ci: add prose lint via Mikefluff/skills"
```

The template pins to a specific `SKILLS_VERSION` for reproducibility and lets you configure:

- `LINT_PATHS` — which files to lint (default: `**/*.md`)
- `FAIL_THRESHOLD` — `0` (clean only) / `1` (borderline+) / `2` (neuroslop only — default; lenient)
- Excluded paths — defaults to `node_modules/`, `vendor/`, `.git/`, `.skills-cache/`

Read the template comments before committing. The workflow runs in 30-60 seconds even on large repos because the linter is pure regex (no LLM call).

---

### Use the Docker image

For users who prefer containers — or who run their own CI / pre-commit pipelines that can't `curl | bash`:

```bash
# Lint a single file
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work/draft.md

# Lint every *.md in cwd
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint-all /work

# List installed skills
docker run --rm ghcr.io/mikefluff/skills list

# Pin a specific version
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills:1.3.1 lint /work/draft.md
```

Image tags: `latest` (main branch), `X.Y.Z` (pinned, no `v` prefix — Docker convention), `X.Y` (minor stream), `X` (major stream). Multi-arch (linux/amd64 + linux/arm64). Built from the same source as the curl-pipe installer.

---

### Configuration

Each skill respects what's in its own `references/` directory — you can tune behaviour without forking by overriding routing patterns, terminology canons, banned-construction lists, and so on. See the relevant skill's `references/` files for what's configurable:

- `style-check/references/routing.md` — which file patterns route to fiction vs non-fiction lint
- `translation-sync/references/terminology.md` — your project's term registry (Pointer Architecture, etc.)
- `translation-sync/references/anchor-quotes.md` — canonical translations for your quoted passages
- `canon-check/references/routing.md` — which book paths map to which story bible
- `writer/references/ru-calques.md` — your own additions to the calque dictionary

---

### Skills by layer (auto-generated)

See [`README.md § What's in the box`](../README.md#whats-in-the-box) for the up-to-date table. Regenerated from `skills.json` on every release.

---

## When something looks off

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for the common failure modes (banner doesn't show, marker missing, false-positive linter, ffmpeg missing for reel-builder, …).
2. Search [GitHub issues](https://github.com/Mikefluff/skills/issues) — your problem may already be reported.
3. Open a new issue: use the bug-report template (it asks for the right diagnostics up front).

---

## See also

- [QUICKSTART](QUICKSTART.md) — 5-minute first run
- [FAQ](FAQ.md) — answers to the questions people ask first
- [TROUBLESHOOTING](TROUBLESHOOTING.md) — known failure modes + fixes
- [COMPOSING](COMPOSING.md) — how the 22 skills compose; recipe library
- [SKILL-INDEX](SKILL-INDEX.md) — every skill indexed by layer / domain / language
- [walkthroughs/README.md](walkthroughs/README.md) — 19 walkthroughs, categorized
- [CONTRIBUTING](../CONTRIBUTING.md) — adding your own skill to the collection
- [VERSIONING](VERSIONING.md) — semver policy, release flow
