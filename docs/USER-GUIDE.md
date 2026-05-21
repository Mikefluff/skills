# User guide

This is the entry point for using the collection — pick the scenario closest to what you want to do.

If you haven't installed yet, run:

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

Then open Claude Code — skills are auto-discovered by name. No `~/.claude/settings.json` edits required (the optional update banner is a separate one-line step covered in [pre-commit-hook walkthrough](walkthroughs/pre-commit-hook.md) and [FAQ](FAQ.md)).

---

## Pick your starting point

| You want to … | Walkthrough |
|---|---|
| Write a viral social-media post (Telegram / Instagram / Threads / etc.) | [Viral post (RU)](walkthroughs/viral-post.md) · [Viral post (EN)](walkthroughs/en-viral-post.md) |
| Rewrite a fiction chapter from rough draft to commit-ready | [Fiction chapter](walkthroughs/fiction-chapter.md) |
| Draft a long-form essay or popular-science chapter with sources | [Non-fiction long-form](walkthroughs/non-fiction.md) |
| Verify a translation matches across RU / EN / PT-BR | [Translation parity](walkthroughs/translation-parity.md) |
| Auto-lint every commit before it lands | [Pre-commit hook](walkthroughs/pre-commit-hook.md) |
| Audit a fresh chapter against your story bible | [Story-bible audit](walkthroughs/canon-check-audit.md) |
| Insert a Pelevin-vector digression into an essay or scene | [Digression insertion](walkthroughs/digression-insertion.md) |
| Get a read-only quality verdict without auto-edits | [Style-check gate](walkthroughs/style-check-gate.md) |
| Rewrite text in a different register (casual ↔ business ↔ academic ↔ plain) | [Tone-shifter](#tone-shifter--register-rewrites) |
| Draft a cold-outreach email (founder / recruiter / journalist / VC) | [Cold-email](#cold-email--outreach-drafting) |
| Generate prompts for AI image models (Midjourney v7 / Flux 2 / Imagen 4 / Nano Banana Pro / gpt-image-2 / Ideogram 3 / Seedream 4.5 / Qwen-Image / HiDream / SD 3.5) | [Image-prompt](#i-want-to-write-an-ai-image-prompt) |
| Generate prompts for AI video models (Veo 3.1 + audio / Sora 2 + cameos / Kling 3.0 + Omni / Runway Gen-4 + Aleph V2V / Luma Ray 3 / Pika 2.2 / Hailuo 02 / Higgsfield / LTX-2 / Hunyuan / Wan 2.2 / Seedance 2.0) | [Video-prompt](#i-want-to-write-an-ai-video-prompt) |
| Generate prompts for AI music models (Suno v5.5 / Udio v4 / Lyria 3 Pro / ElevenLabs Music / Stable Audio 2.5 / MusicGen) | [Music-prompt](#i-want-to-write-an-ai-music-prompt) |
| Write UX microcopy (errors, empty states, tooltips, buttons) | [Microcopy](#i-want-to-write-ux-microcopy) |
| Write release notes / changelogs / product update | [Release-notes](#i-want-to-write-release-notes) |
| Write an RFC / ADR / design doc / tech spec | [RFC-writer](#i-want-to-write-an-rfc--design-doc) |
| Write landing page / SEO meta / paid ad copy | [Landing-copy](#i-want-to-write-marketing-copy) |
| Stuck or confused | [FAQ](FAQ.md) · [Troubleshooting](TROUBLESHOOTING.md) |

---

## The collection in one paragraph

Seventeen skills layered on top of one base linter (`writer`):

- **Base**: `writer` strips 28 categories of LLM-prose tells from any text, in RU or EN. Runs as a final pass under every other prose skill in the collection.
- **Wrappers** (call `writer` automatically): `viral-text` for social posts, `prose-edit` for fiction, `essay-write` for non-fiction longreads, `pelevin-digression` for opt-in voice inserts, `tone-shifter` for register changes, `cold-email` for outreach.
- **Linters** (read-only — produce reports, don't edit): `style-check` for pre-commit prose lint, `translation-sync` for multilingual parity, `canon-check` for story-bible consistency.
- **Meta**: `skills-update` checks for new releases of this collection and applies them on confirmation.

Skills work on any text file (`.md`, `.tex`, `.txt`, …) — there's no assumed file format or project layout.

For the dependency graph and composition patterns, see [COMPOSING.md](COMPOSING.md).
For an index of every skill by layer, domain, and language, see [SKILL-INDEX.md](SKILL-INDEX.md).

---

## Two-minute orientation by use case

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

### "I want to write a cold email"

`/cold-email first-touch <recipient-context>` drafts a first-touch outreach to founders, VCs, recruiters, journalists, or partners. 5-block structure (hook / value / ask / easy-yes / sign-off), ≤120-word budget, banned ceremony patterns (no "I hope this email finds you well"), anti-template subject lines.

```
/cold-email first-touch "Sarah at Acorn Capital, VC who led Beta Corp's A round"
/cold-email follow-up <previous email>
/cold-email intro-request via=Marcus to="CISO at MegaCorp" why="audit-log compression"
```

Modes: `first-touch`, `follow-up`, `intro-request` (produces both the email to the intro-giver and the forwardable block), `re-engage`, `forwardable`. See `cold-email/references/structure.md` for the per-variant template.

---

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

### "I want auto-lint on every commit"

There's no built-in git-hook installer (we don't want to silently touch your `.git/` directory). The [pre-commit hook walkthrough](walkthroughs/pre-commit-hook.md) gives you a ready-to-paste `.git/hooks/pre-commit` script with two variants:

- Full Claude Code invocation of `/style-check staged` (smart; requires the CLI)
- Offline-only fallback via `python3 .../writer/scripts/lint.py` on staged diff (fast; no Claude needed)

---

## Use in your CI

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

## Use the Docker image

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

## Configuration

Each skill respects what's in its own `references/` directory — you can tune behaviour without forking by overriding routing patterns, terminology canons, banned-construction lists, and so on. See the relevant skill's `references/` files for what's configurable:

- `style-check/references/routing.md` — which file patterns route to fiction vs non-fiction lint
- `translation-sync/references/terminology.md` — your project's term registry (Pointer Architecture, etc.)
- `translation-sync/references/anchor-quotes.md` — canonical translations for your quoted passages
- `canon-check/references/routing.md` — which book paths map to which story bible
- `writer/references/ru-calques.md` — your own additions to the calque dictionary

---

## Skills by layer (auto-generated)

See [`README.md`](../README.md#whats-in-the-box) for the up-to-date table. The table is regenerated from `skills.json` on every release.

---

## Updating the collection

```
/skills-update                                 # check + apply via Claude Code
```

Or from the shell:

```bash
bash install.sh --check                        # report version status
bash install.sh --update                       # re-pull latest tarball, overwrite installed skills
bash install.sh --update --prune               # also remove skills no longer in upstream manifest
```

Or install the opt-in ambient status-line banner once:

```bash
bash scripts/install-hook.sh
```

After that, you'll see ` · skills v1.0.1→1.2.0 +1 skill (some-new-skill)` in your status line when a release is available.

---

## When something looks off

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for the common failure modes (banner doesn't show, marker missing, false-positive linter, …).
2. Search [GitHub issues](https://github.com/Mikefluff/skills/issues) — your problem may already be reported.
3. Open a new issue: use the bug-report template (it asks for the right diagnostics up front).

---

## See also

- [FAQ](FAQ.md) — answers to the questions people ask first
- [TROUBLESHOOTING](TROUBLESHOOTING.md) — known failure modes + fixes
- [COMPOSING](COMPOSING.md) — how the 17 skills compose; recipe library
- [SKILL-INDEX](SKILL-INDEX.md) — every skill indexed by layer / domain / language
- [CONTRIBUTING](../CONTRIBUTING.md) — adding your own skill to the collection
- [VERSIONING](VERSIONING.md) — semver policy, release flow
