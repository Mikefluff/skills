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
| Publish it to a social platform | [§ post-publisher](#i-want-to-publish-a-post) |
| Full chain (research → carousel + reel) | [walkthrough](walkthroughs/research-to-carousel-reel.md) |
| Full chain (generate → publish) | [walkthrough](walkthroughs/publish-to-social.md) |

### Manage the collection

| You want to … | Section |
|---|---|
| Manage API keys (CRUD + verify) | [§ skills-keys](#i-want-to-manage-api-keys) |
| Update the collection | [walkthrough](#i-want-to-update-the-collection) |

Stuck? [FAQ](FAQ.md) · [Troubleshooting](TROUBLESHOOTING.md).

---

## The collection in one paragraph

Forty-two skills layered on top of one base linter (`writer`):

- **Base**: `writer` strips 25 catalogued categories of LLM-prose tells from any text, in RU or EN, plus chatbot copy-paste artifacts and rhythm metrics. Runs as a final pass under every other prose skill.
- **Wrappers** (21): prose editing (`viral-text`, `prose-edit`, `essay-write`, `pelevin-digression`, `tone-shifter`), marketing + ops (`cold-email`, `microcopy`, `release-notes`, `rfc-writer`, `landing-copy`), AI media prompts (`image-prompt`, `video-prompt`, `music-prompt`), and media utilities (`bg-remover`, `voiceover-maker`, `subtitle-burner`, `gif-maker`, `upscaler`, `audio-mix-maker`, `style-transfer`, `transcribe-maker`).
- **Linters** (read-only — produce reports, don't edit): `style-check` for pre-commit prose lint and AI-detection audits, `translation-sync` for RU/EN/PT-BR parity, `canon-check` for story-bible consistency.
- **Orchestrators** (14, end-to-end pipelines): `research-brief` produces cited research; `carousel-builder` turns topics into N-slide carousels; `reel-builder` produces stitched vertical reels with matched music; `post-publisher` sends any of that to Instagram / Threads / TikTok / X / YouTube / Telegram / LinkedIn through the official APIs; `proposal-maker` turns a raw offer into a brand-faithful HTML proposal; `style-suggest` turns a description or reference image into a new visual-style entry; single-image orchestrators (`flyer-maker` / `cover-maker` / `thumbnail-maker` / `avatar-maker` / `logo-maker` / `quote-card-maker` / `banner-maker` / `meme-card-maker`) ship structured visual artifacts.
- **Meta** (3): `skills-update` (apply a newer release of this collection), `skills-keys` (manage `~/.skills.env` API keys for the `--execute` layer), `skills-styles` (manage the local style library).

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

Use cases: turning a casual brain-dump into an exec memo, rewriting an academic paragraph for a general audience, softening corporate-speak to friendly-professional. Preserves facts, structure, and information — shifts vocabulary, sentence length, contractions, hedges, jargon level. See `skills/tone-shifter/references/registers.md` for the full taxonomy.

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

Modes: `first-touch`, `follow-up`, `intro-request` (produces both the email to the intro-giver and the forwardable block), `re-engage`, `forwardable`. See `skills/cold-email/references/structure.md` for the per-variant template.

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

Targets supported: `midjourney-v6`, `dalle-3`, `flux-pro`, `nano-banana`, `sdxl`. Default style is photorealistic; `--style illustration` / `editorial` / `cinematic` overrides. Lighting and camera vocabulary live in `skills/image-prompt/references/`.

**Execute via API** (v2.2+, optional). When an API key is set in env, add `--execute` to actually generate the image and save it:

```
/image-prompt a confident founder leaning on marble countertop --model gpt-image-2 --execute
/image-prompt minimalist product shot --model nano-banana-pro --execute --yes
```

Asset lands in `./generated/image/`. Cost confirmation prompts for anything above $0.10 unless `--yes`. Missing key → falls back to prompt-only. Setup: `install.sh` auto-creates the runners venv and installs deps; you only need to export `OPENAI_API_KEY` / `GEMINI_API_KEY` / `BFL_API_KEY` / `FAL_KEY` / `REPLICATE_API_TOKEN` / `IDEOGRAM_API_KEY`. Full provider matrix in `skills/image-prompt/references/execute.md`.

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

Setup adds `RUNWAY_API_KEY`, `KLING_ACCESS_KEY_ID` + `KLING_ACCESS_KEY_SECRET`, `OPENAI_SORA_API_ENABLED=1` (once Sora API is available). Full matrix in `skills/video-prompt/references/execute.md`.

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

Targets: `suno-v5-5`, `udio-v4`, `lyria-3-pro`, `eleven-music`, `stable-audio-2-5`, `musicgen`, `tencent-song-generation`, `sonauto-v2`, `riffusion`, `mubert`. Genre recipes (`hyperpop`, `drill`, `country`, `lo-fi`, `ambient`, `orchestral`, `k-pop`, `afrobeats`, `jazz-fusion`, `hardcore-punk`, `synthwave`, `gospel`) live in `skills/music-prompt/references/genre-recipes.md`. For Suno: brackets go in the Lyrics box ONLY; the Style of Music box accepts natural language only.

**Execute via API** (v2.2+, optional). Suno's two-box workflow maps to `--prompt` (style box) + `--lyrics-file` (lyrics box):

```
/music-prompt anthemic modern pop chorus --model suno-v5-5 --execute
/music-prompt label-safe orchestral cue --model lyria-3-pro --duration 1.5 --execute --yes
/music-prompt indie folk ballad --model eleven-music --execute
```

Setup adds `SUNO_API_KEY` + `SUNO_API_ENABLED=1`, `ELEVENLABS_API_KEY`, `LYRIA_API_ENABLED=1`. Full matrix in `skills/music-prompt/references/execute.md`.

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

**Animate it** (v2.19.0+): add `--animate` and the deck continues into an animated reel — each slide becomes a 4s image-to-video shot (subtle character micro-gesture, all overlay text frozen via the video-chain discipline), ffmpeg-stitched into one final.mp4. `--animate-provider veo-3-1-fast` (default, $0.15/s) or `veo-3-1` for publication-grade text stability. 5 slides × 4s ≈ $3.00 on Fast. The motion prompts are written by the shared [video chain](../common/video-prompt-library/system-prompt.md) — not by hand.

For details: [skills/carousel-builder/SKILL.md](../skills/carousel-builder/SKILL.md) and [research-to-carousel-reel](walkthroughs/research-to-carousel-reel.md).

---

### "I want a cover (album / book / podcast / report)" {#i-want-a-cover}

`/cover-maker --title "<text>" --medium album|book|podcast|magazine|report|deck-cover|linkedin-doc --creator "<name>"` produces a cover at the medium's native aspect (album 1:1, book 2:3, podcast 1:1, magazine 2:3, report A4, deck 16:9, linkedin-doc 1:1). Optional `--photo` reference. Reuses carousel style library.

```
/cover-maker --title "Lunar Vault" --creator "Alex Reyes" --medium album --photo ./artwork.jpg --style neon-cyberpunk --execute
/cover-maker --title "The Slow Software Manifesto" --creator "Alex Smith" --medium book --photo ./alex.jpg --style swiss-grid-poster --execute
/cover-maker --title "Slow Software Podcast" --creator "Hosted by Alex" --medium podcast --style swiss-grid-poster --execute
```

For details: [skills/cover-maker/SKILL.md](../skills/cover-maker/SKILL.md).

---

### "I want a YouTube / blog / podcast thumbnail" {#i-want-a-thumbnail}

`/thumbnail-maker --title "<text>"` produces 16:9 thumbnails with face-placement variants (left / right / center). Default `--type youtube` (1920×1080). Optional `--photo` reference.

```
/thumbnail-maker --title "How I Built a SaaS in 30 Days" --photo ./me.jpg --type youtube --execute
/thumbnail-maker --title "The Slow Software Manifesto" --type blog --style kinfolk-minimal --execute
/thumbnail-maker --title "Why We Killed Our Roadmap" --photo ./guest.jpg --type podcast-episode --variants 2 --execute
```

For details: [skills/thumbnail-maker/SKILL.md](../skills/thumbnail-maker/SKILL.md).

---

### "I want to remove the background from a photo" {#i-want-to-remove-background}

`/bg-remover --image <path>` removes background via Replicate. Single image in, transparent PNG out. ~$0.001-0.005 per image.

```
/bg-remover --image ./me.jpg --execute
/bg-remover --image ./shoe.jpg --output ./products/shoe-cutout.png --execute
/bg-remover --image ./portrait.jpg --replicate-model pollinations/modnet --execute
```

For details: [skills/bg-remover/SKILL.md](../skills/bg-remover/SKILL.md).

---

### "I want avatar / headshot variants from a photo" {#i-want-to-make-an-avatar}

`/avatar-maker --photo <path>` produces N profile-pic / headshot variants in a consistent style. Identity-preserve is the priority — defaults to `nano-banana-pro` (industry-best at face preservation).

```
/avatar-maker --photo ./alex-headshot.jpg --style auto --variants 3 --execute
/avatar-maker --photo ./me.jpg --style photo-editorial-bw --variants 5 --aspects square --execute
/avatar-maker --photo ./me.jpg --style gradient-mesh-modern --aspects square,square-tight,cover,wide --variants 2 --execute   # cross-platform
```

Aspects:

- `square` (1080×1080) — default; LinkedIn / Twitter / IG / GitHub
- `square-tight` (1080×1080, face-fills-frame) — small thumbs
- `cover` (1080×1350) — IG portrait / LinkedIn cover-banner area
- `story` (1080×1920) — IG Story background
- `wide` (1920×1080) — Twitter header / YouTube banner base

Style library: reuses the 24 carousel styles, filtered to photoreal-friendly (`--style auto` skips illustration / 3D / abstract which lose identity).

Cost: $0.15-0.45 per typical run (1-3 aspects × 3 variants × $0.05 NBP). Under default budget.

For details: [skills/avatar-maker/SKILL.md](../skills/avatar-maker/SKILL.md) · [model-picker](../skills/avatar-maker/references/model-picker.md).

---

### "I want a voiceover / TTS narration" {#i-want-a-voiceover}

`/voiceover-maker --prompt "<script>"` (or `--prompt-file <path>`) generates an MP3 from text via the runner's audio modality. Wraps ElevenLabs `eleven-tts` (multilingual, brand-voice) + OpenAI `gpt-4o-mini-tts` (cheap fast English-strong).

```
/voiceover-maker --prompt "Welcome to the show." --model gpt-4o-mini-tts --voice alloy --execute
/voiceover-maker --prompt-file ./episode-intro.txt --model eleven-tts --voice-id 21m00Tcm4TlvDq8ikWAM --execute
/voiceover-maker --prompt-file ./ru-narration.txt --model eleven-tts --lang ru --execute
/voiceover-maker --check --model eleven-tts                                                      # verify env + connectivity
/voiceover-maker --prompt "test" --model gpt-4o-mini-tts --cost-only                              # preview cost
```

Auto-pick:

- English short-form → `gpt-4o-mini-tts` (cheap: ~$0.015/min)
- Multilingual or long-form (>2 min) → `eleven-tts` (~$0.30/min)
- Brand voice consistency across episodes → `eleven-tts --voice-id <stable-id>`

Outputs `./generated/audio/<timestamp>-<model>.mp3`. Cost preview built in; confirmation past $0.10.

For details: [skills/voiceover-maker/SKILL.md](../skills/voiceover-maker/SKILL.md) · [voice-picker](../skills/voiceover-maker/references/voice-picker.md) · [script-format](../skills/voiceover-maker/references/script-format.md).

---

### "I want to burn subtitles onto my video" {#i-want-to-burn-subtitles}

`/subtitle-burner burn <video> --subtitle <file>` burns captions onto an existing MP4 / MOV / WebM via ffmpeg. No API calls — pure ffmpeg. Style presets: `modern` (white on black backplate), `minimal` (no backplate), `bold` (yellow + dense backplate).

```
/subtitle-burner burn ./tiktok.mp4 --subtitle ./caps.srt --style modern
/subtitle-burner burn ./reel.mp4 --subtitle ./captions.vtt --style bold
/subtitle-burner burn ./morning.mp4 --subtitle ./quick-text.txt --style modern    # plain text distributed across video
/subtitle-burner burn ./clip.mp4 --inline "FINALLY HERE." --style bold            # single caption for entire clip
/subtitle-burner preview --subtitle ./caps.srt                                    # parse + print cues, no burn
```

Subtitle sources:

- `.srt` — standard SubRip format
- `.vtt` — WebVTT (from YouTube, web exports)
- `.txt` — plain text, evenly distributed across video duration (uses ffprobe)
- `--inline "<text>"` — single caption for the whole video

Output: `<video>-subtitled<ext>` (or `--output <path>`).

ffmpeg required. install.sh offers auto-install. No per-run cost.

For details: [skills/subtitle-burner/SKILL.md](../skills/subtitle-burner/SKILL.md) · [subtitle-formats](../skills/subtitle-burner/references/subtitle-formats.md) · [ffmpeg-styling](../skills/subtitle-burner/references/ffmpeg-styling.md).

---

### "I want to make a flyer / event poster" {#i-want-to-make-a-flyer}

`/flyer-maker --title "<event>" --date "<when>" --location "<where>"` produces a multi-aspect event flyer (portrait + square + story by default) with embedded text in a chosen visual style. Optionally embeds a speaker photo or brand asset as a reference image.

```
/flyer-maker --title "Workshop: Slow Software" --date "15 June · 19:00" --location "Brooklyn Studio, NYC" --cta "Tickets: link in bio" --photo ./speaker.jpg --execute
/flyer-maker --title "Концерт" --date "20 ноября" --location "Зал \"Космос\"" --style art-deco-gold --aspects portrait,square,story --lang ru --execute
/flyer-maker --title "Conference Poster" --style swiss-grid-poster --aspects a4 --execute    # A4 print preview
/flyer-maker --title "..." --prompts-only                                                     # dry run
```

Style library: reuses the 24 carousel visual styles (kinfolk-minimal, swiss-grid-poster, art-deco-gold, neon-cyberpunk, …). Pass `--style auto` to let the skill pick based on event type.

Outputs `./generated/flyer/<event-slug>/`:

- `portrait.png` (1080×1350, IG/LinkedIn feed)
- `square.png` (1080×1080)
- `story.png` (1080×1920, IG Story / TikTok)
- `landscape.png` (1920×1080, LinkedIn / Twitter card / OG image) — opt in via `--aspects`
- `a4.png` (1240×1754, A4 portrait preview at 150 DPI) — opt in
- `manifest.json` + `style-used.md` + `prompts.md`

Default cost: $0.15-0.50 per 3-aspect run depending on model. Budget cap inherits from `SKILLS_CAROUSEL_BUDGET=1.50`.

For details: [skills/flyer-maker/SKILL.md](../skills/flyer-maker/SKILL.md) and [skills/flyer-maker/examples/before-after.md](../skills/flyer-maker/examples/before-after.md).

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

For details: [skills/reel-builder/SKILL.md](../skills/reel-builder/SKILL.md) and [research-to-carousel-reel](walkthroughs/research-to-carousel-reel.md).

---

### "I want to publish a post" {#i-want-to-publish-a-post}

`/post-publisher <dir>` closes the last mile: it takes a `carousel-builder` or
`reel-builder` output directory, reads `captions.md`, and sends it to the
platform. Instagram, Threads, TikTok, X, YouTube, Telegram and LinkedIn, all
through their official APIs.

**Publishing is irreversible, so dry-run is the default.** Without `--yes`
nothing leaves the machine; with `--yes` each platform is still confirmed
separately.

```
/post-publisher ./generated/carousel/<slug>/ --platform instagram,threads
/post-publisher ./generated/carousel/<slug>/ --platform instagram --draft --yes
/post-publisher ./generated/reel/<slug>/ --platform tiktok --draft --yes
/post-publisher --kind text --text "..." --platform telegram --yes
/post-publisher --list-platforms                        # what is configured
```

Before the first post, connect the account once:

```
python3 -m common.runners.cli.auth --platform threads    # browser OAuth flow
python3 -m common.runners.cli.auth --status              # what is connected
skills-keys accounts                                     # the same, from the keys skill
```

Start with **Telegram** (no OAuth at all — a BotFather token and an admin bot)
or **Threads** (simplest OAuth, and a text post needs no S3 bucket). Instagram
is the worst place to start: it needs a Business account, a registered app and
an S3 bucket before the first post can go out, because Instagram fetches media
from a URL rather than accepting uploaded bytes.

Two behaviours worth knowing:

- **`--draft` is a promise.** On a platform without drafts (Telegram, X,
  LinkedIn) the platform is *skipped*, never published live.
- **Receipts prevent double-posting.** Each success appends to `posted.json` in
  the source directory. Re-running the identical command is refused; editing the
  caption counts as new content and goes through. `--force` overrides.

TikTok deserves its own warning: direct publishing requires passing TikTok's app
audit, and an unaudited app has every post silently forced to SELF_ONLY — the
API reports success and nobody can see the post. Use `--draft`, which lands it
in the app inbox and always works.

Setup per platform: [skills/post-publisher/references/oauth-setup.md](../skills/post-publisher/references/oauth-setup.md).
When the API path is genuinely closed (unaudited TikTok, personal Instagram,
company LinkedIn pages), [browser-fallback.md](../skills/post-publisher/references/browser-fallback.md)
covers posting by hand without breaking the receipt trail.

For details: [skills/post-publisher/SKILL.md](../skills/post-publisher/SKILL.md) and
[publish-to-social](walkthroughs/publish-to-social.md).

---

### "I want to design a logo / brand mark" {#i-want-to-make-a-logo}

`/logo-maker --brand "<name>"` generates N stochastic logo variants. Defaults to `ideogram-3-quality` for cleanest embedded text. Pick from six style presets: `wordmark` / `minimal` / `illustrated` / `typographic` / `geometric` / `emblem`.

```
/logo-maker --brand "Lunar Vault" --style wordmark --palette "deep teal + warm cream" --variants 4 --execute
/logo-maker --brand "Brooklyn Bean Co" --tagline "Roasted since 2024" --style illustrated --variants 6 --model gpt-image-2 --execute
/logo-maker --brand "Axis & Atrium" --style geometric --style-mod "Bauhaus 1923 inspiration, intersecting triangles + circle" --execute
```

Single image output (no aspect multiplexing — logos work the same at all sizes). Default `--variants 4` because logo selection is inherently subjective.

To get transparent BG: chain with `bg-remover`. To get SVG: pick best variant → vector tool → auto-trace.

For details: [skills/logo-maker/SKILL.md](../skills/logo-maker/SKILL.md) · [style-presets](../skills/logo-maker/references/style-presets.md).

---

### "I want a quote card / aphorism post" {#i-want-to-make-a-quote-card}

`/quote-card-maker --quote "<text>" --attribution "<name>"` builds a typography-dominant card where the quote IS the image. Multi-aspect (square / portrait / story / landscape).

```
/quote-card-maker --quote "Anxiety is the dizziness of freedom." --attribution "— Søren Kierkegaard" --style minimal-serif --aspects square,portrait --execute
/quote-card-maker --quote "The best time to plant a tree was 20 years ago." --attribution "— Chinese proverb" --style gradient-mesh-modern --aspects square,landscape --execute
/quote-card-maker --quote "Если в первом акте на стене висит ружьё, то в последнем оно должно выстрелить." --attribution "— А.П. Чехов" --style russian-constructivist --aspects story --lang ru --execute
```

Style presets: `minimal-serif` (literary/philosophical), `swiss-grid-poster` (marketing), `monochrome-bold` (manifesto), `editorial-magazine` (long-form), `gradient-mesh-modern` (SaaS/tech), `russian-constructivist` (RU heritage).

≤20 words per quote. Past that, use `carousel-builder` to split across slides.

For details: [skills/quote-card-maker/SKILL.md](../skills/quote-card-maker/SKILL.md) · [style-presets](../skills/quote-card-maker/references/style-presets.md).

---

### "I want a short looping GIF" {#i-want-a-gif}

`/gif-maker` runs in two modes: convert an existing MP4 → optimized GIF, or generate a 1-3s clip via a video provider and convert.

```
/gif-maker --input ./reel.mp4 --aspect 1:1 --duration 2.0 --output ./twitter.gif                # Mode A: convert
/gif-maker --prompt "Abstract neural mesh waves rippling, seamless loop" --model veo-3-1-fast --duration 3 --aspect 2:1 --execute    # Mode B: generate + convert
/gif-maker --input ./long.mp4 --start 12.0 --duration 1.5 --aspect 1:1 --width 480 --fps 10 --output ./slack-reaction.gif
```

2-pass palette generation (palettegen + paletteuse) for high-quality color. Aspect crop presets: `1:1` / `9:16` / `16:9` / `4:5` / `2:1` / `1:2`. Default `--fps 12 --width 720`.

ffmpeg required. install.sh offers auto-install. Mode B cost: $1.20-3.00 per 3-sec clip depending on provider.

For details: [skills/gif-maker/SKILL.md](../skills/gif-maker/SKILL.md) · [quality-tuning](../skills/gif-maker/references/quality-tuning.md) · [model-picker](../skills/gif-maker/references/model-picker.md).

---

### "I want a banner ad / OG image / display creative" {#i-want-a-banner}

`/banner-maker --headline "<text>" --cta "<text>"` produces multi-preset display creatives in standard ad sizes — OG (1200×630), LinkedIn ad, Facebook ad, Twitter card, Google Display (leaderboard / medium-rectangle / mobile-banner / wide-skyscraper).

```
/banner-maker --headline "Ship 10x faster" --cta "Start free trial" --brand "Acme Cloud" --presets og,linkedin-ad --style swiss-grid-poster --execute
/banner-maker --headline "Build faster" --cta "Try free" --presets leaderboard,medium-rectangle --style gradient-mesh-modern --variants 3 --execute
/banner-maker --headline "DevConf 2026" --subhead "Brooklyn · June 20-22" --cta "Get ticket" --presets twitter-card --style brutalist-grid --execute
```

Defaults: `--presets og,linkedin-ad --variants 1 --style auto --model ideogram-3-quality`. Presets are at @2x retina resolution; downscale for 1× platform upload.

For details: [skills/banner-maker/SKILL.md](../skills/banner-maker/SKILL.md) · [aspect-presets](../skills/banner-maker/references/aspect-presets.md) · [composition-zones](../skills/banner-maker/references/composition-zones.md).

---

### "I want a meme" {#i-want-a-meme}

`/meme-card-maker --top "<text>" --bottom "<text>"` produces Impact-style meme cards. Optional `--template drake|distracted-boyfriend|expanding-brain|two-buttons|change-my-mind|custom` for template hints. Optional `--base-photo` to use a user photo as centerpiece.

```
/meme-card-maker --top "Using Jira to track bugs" --bottom "Crying in the shower" --template drake --variants 3 --execute
/meme-card-maker --top "Me waiting for the build to pass" --bottom "Still failing" --base-photo ./mittens.jpg --execute
/meme-card-maker --top "Use formatter / Use linter / Use type checker / Delete the code" --template expanding-brain --aspect portrait --execute
```

Defaults: `--variants 3 --aspect square --template custom --model gpt-image-2`. Captions auto-uppercase for English; mixed-case for Cyrillic.

For details: [skills/meme-card-maker/SKILL.md](../skills/meme-card-maker/SKILL.md) · [templates](../skills/meme-card-maker/references/templates.md) · [typography](../skills/meme-card-maker/references/typography.md).

---

### "I want to upscale / enhance an image" {#i-want-to-upscale}

`/upscaler --image <path> --scale 4` runs the image through a Replicate-hosted super-resolution model. Default Real-ESRGAN; switch to `--replicate-model tencentarc/gfpgan` for face restoration; `--face-enhance` flag toggles face restoration in Real-ESRGAN.

```
/upscaler --image ./generated/image/cover.png --scale 4 --execute                                                                  # 1024 → 4096 AI-gen
/upscaler --image ./grandma-1972.jpg --scale 4 --replicate-model tencentarc/gfpgan --execute                                       # face restoration
/upscaler --image ./shoe-iphone.jpg --scale 2 --replicate-model philz1337x/clarity-upscaler --output ./products/shoe-2k.png --execute  # product
```

Cost: ~$0.005-0.02 per image. Output: `./generated/upscaled/<stem>-<scale>x.png` (or `--output`).

For details: [skills/upscaler/SKILL.md](../skills/upscaler/SKILL.md) · [providers](../skills/upscaler/references/providers.md) · [use-cases](../skills/upscaler/references/use-cases.md).

---

### "I want to mix music onto a video" {#i-want-to-mix-audio}

`/audio-mix-maker --video <path> --audio <path>` mixes a music track onto a video via ffmpeg. Three modes — `replace` (drop original audio), `overlay` (mix both audible), `duck` (sidechain compressor lowers music when speech detected).

```
/audio-mix-maker --video ./screen-recording.mp4 --audio ./music.mp3 --mode replace --fade-out 1.0                        # silent recording → music
/audio-mix-maker --video ./tutorial.mp4 --audio ./ambient-bed.mp3 --mode duck --volume 0.6 --duck-amount 0.5              # voiceover with music ducked
/audio-mix-maker --video ./broll.mp4 --audio ./cello.mp3 --mode overlay --volume 0.4 --fade-in 2 --fade-out 3            # keep ambient + add music bed
```

No API calls — pure ffmpeg. ffmpeg required.

For details: [skills/audio-mix-maker/SKILL.md](../skills/audio-mix-maker/SKILL.md) · [modes](../skills/audio-mix-maker/references/modes.md).

---

### "I want to style-transfer an image (turn photo into watercolor / cyberpunk / etc.)" {#i-want-style-transfer}

`/style-transfer --image <path> --style <preset>` applies an artistic style to an existing image via Flux Kontext (best for natural-language style transfer). 12 style presets + custom mode.

```
/style-transfer --image ./me.jpg --style watercolor --execute
/style-transfer --image ./street.jpg --style cyberpunk --execute
/style-transfer --image ./me.jpg --style custom --prompt-mod "1920s Soviet constructivist propaganda poster style, bold red and black" --execute
```

Style presets: `watercolor` / `oil-painting` / `sketch` / `line-art` / `ink-wash` / `cyberpunk` / `studio-ghibli` / `pixar-3d` / `manga` / `art-deco` / `low-poly` / `vaporwave` / `custom`.

Cost: ~$0.05 per image. Output: `./generated/stylized/<stem>-<style>.png`.

For details: [skills/style-transfer/SKILL.md](../skills/style-transfer/SKILL.md) · [styles](../skills/style-transfer/references/styles.md).

---

### "I want to transcribe audio / video to subtitles" {#i-want-to-transcribe}

`/transcribe-maker --input <path>` transcribes audio or video to SRT / WebVTT / JSON / plain text via OpenAI Whisper. Auto-detects language or accepts `--lang ru` hint.

```
/transcribe-maker --input ./tutorial.mp4 --format srt --lang en --output ./tutorial.srt --execute               # captions for subtitle-burner
/transcribe-maker --input ./podcast.mp3 --format text --lang ru --output ./podcast-transcript.txt --execute   # plain transcript
/transcribe-maker --input ./interview.mp4 --format verbose_json --output ./interview.json --execute            # word-level timestamps
```

Cost: ~$0.006/min. File size limit: 25 MB (Whisper API constraint — see `preprocessing` reference for splitting).

Chain with `subtitle-burner` for end-to-end auto-captioning:

```
/transcribe-maker --input ./video.mp4 --format srt --output ./captions.srt --execute
/subtitle-burner burn ./video.mp4 --subtitle ./captions.srt --style modern --output ./video-captioned.mp4
```

For details: [skills/transcribe-maker/SKILL.md](../skills/transcribe-maker/SKILL.md) · [formats](../skills/transcribe-maker/references/formats.md) · [preprocessing](../skills/transcribe-maker/references/preprocessing.md).

---

### "I want a commercial proposal (КП) styled like a brand site" {#i-want-a-proposal}

`/proposal-maker --offer <path>` turns a raw, telegram-style offer (client block + line items with catalogue links + total) into a self-contained `proposal.html` whose visual style is copied from a brand website — real product photos, exact prices, clickable links, prints to clean PDF. LLM-authored from a screenshot of the brand site by default; `--quick` renders an offline themed template.

```
/proposal-maker --offer ./offer.txt                                          # brand auto-detected from the offer footer
/proposal-maker --offer ./offer.txt --brand-url https://client-site.com      # explicit brand site
/proposal-maker --offer ./offer.txt --brand-file proposal-maker/brands/double-d/brand.json   # saved profile (preferred when it exists)
/proposal-maker --offer ./offer.txt --quick --template dark --pdf            # offline, no LLM
```

**Saved brand profiles** — client-ready designs are saved under [proposal-maker/brands/](../skills/proposal-maker/brands/_index.md) (`brand.json` tokens + authored `template.html` to clone + cached assets). Profiles encode manual corrections a live scrape gets wrong (dark Tilda sites scrape as light; white SVG logos vanish). After finishing a proposal for a new brand, save it as a profile.

For details: [skills/proposal-maker/SKILL.md](../skills/proposal-maker/SKILL.md) · [examples](../skills/proposal-maker/examples/before-after.md).

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

For details: [skills/skills-styles/SKILL.md](../skills/skills-styles/SKILL.md) · [usage reference](../skills/skills-styles/references/usage.md) · [templates schema](../skills/skills-styles/references/templates.md).

---

### "I want a new visual style from a description or a reference image" {#i-want-a-new-visual-style}

`/style-suggest` writes a new entry for the shared visual-prompt style library, the one every image-producing skill reads (`carousel-builder`, `cover-maker`, `flyer-maker`, `quote-card-maker`, `banner-maker`, `logo-maker`, `thumbnail-maker`, `avatar-maker`, `meme-card-maker`).

It checks the existing catalogue for a near-duplicate first and tells you when one already covers your idea, rather than growing the library with variations of the same thing.

```
/style-suggest "тёплая плёночная эстетика, зерно, выцветшие тона"
/style-suggest --image ./reference.jpg
/style-suggest --image ./poster.png "но холоднее и с более жёсткой сеткой"
```

Output is a complete entry in the v2.15.0 schema — background, accents, elements, mood, accent_text_color, typography, composition_signature, when_to_use — dropped into `common/visual-prompt-library/styles/`. It is usable immediately, no restart.

Difference from `/skills-styles`: that one manages the *carousel / video / music* style library by hand (list, add from template, edit, validate, submit). This one *authors* a visual-prompt entry from your description or image.

For details: [skills/style-suggest/SKILL.md](../skills/style-suggest/SKILL.md).

---

### "I want to turn an offer into a commercial proposal" {#i-want-a-commercial-proposal}

`/proposal-maker` takes a raw, telegram-style offer — client, line items with catalogue links, total — and produces a self-contained `proposal.html` whose visual style is copied from a brand's website.

The default flow is LLM-authored: a Python step builds the brand kit (site screenshot, logo, accent and font tokens, per-item catalogue photos, `BRIEF.md`), then the skill writes bespoke HTML mirroring that brand. Line items missing a photo get an on-brand generated image. Prices and links stay exact — nothing about the commercial terms is generated.

```
/proposal-maker --offer ./offer.txt --brand https://client-site.com
/proposal-maker --offer ./offer.txt --brand https://client-site.com --pdf
/proposal-maker --offer ./offer.txt --quick --theme editorial     # offline, deterministic
```

`--quick` skips the brand scrape and renders one of three fixed themes (editorial / invoice / dark) — useful with no network or when the client has no site. Output prints to a link-preserving, Ghostscript-compressed PDF.

Saved brand profiles live in [proposal-maker/brands/](../skills/proposal-maker/brands/_index.md) and can be reused across proposals for the same client.

For details: [skills/proposal-maker/SKILL.md](../skills/proposal-maker/SKILL.md).

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

For details: [skills/skills-keys/SKILL.md](../skills/skills-keys/SKILL.md) and [skills/skills-keys/references/usage.md](../skills/skills-keys/references/usage.md).

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

- `skills/style-check/references/routing.md` — which file patterns route to fiction vs non-fiction lint
- `skills/translation-sync/references/terminology.md` — your project's term registry (Pointer Architecture, etc.)
- `skills/translation-sync/references/anchor-quotes.md` — canonical translations for your quoted passages
- `skills/canon-check/references/routing.md` — which book paths map to which story bible
- `skills/writer/references/ru-calques.md` — your own additions to the calque dictionary

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
- [COMPOSING](COMPOSING.md) — how the 42 skills compose; recipe library
- [SKILL-INDEX](SKILL-INDEX.md) — every skill indexed by layer / domain / language
- [walkthroughs/README.md](walkthroughs/README.md) — 19 walkthroughs, categorized
- [CONTRIBUTING](../CONTRIBUTING.md) — adding your own skill to the collection
- [VERSIONING](VERSIONING.md) — semver policy, release flow
