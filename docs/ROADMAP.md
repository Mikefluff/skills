# Roadmap

Identified gaps where the collection is functional but UX-painful. Tracked here so they don't get lost between releases.

Not all of these will be built. They're sorted by user-likely-to-want vs. effort, with notes on what could ship as a skill vs. what's better left as a one-liner in `image-prompt --execute` / `video-prompt --execute`.

Last updated: 2026-08-08 (post v2.24.0, structural audit unreleased).

---

## What landed in recent releases

- v2.22.0 — structural gates + the publishing layer refactored to pass them
- v2.21.0 — `post-publisher` (Instagram / Threads / TikTok / X / YouTube / Telegram / LinkedIn via official APIs)
- v2.20.0 — `proposal-maker` + `style-suggest` promoted; copy-paste artifact gate
- v2.19.0 — `carousel-builder --animate`; text-stability kwargs across Kling + Runway
- v2.18.0 — canonical video-prompt SYSTEM_PROMPT chain; Veo 3.1 text-overlay preservation
- v2.17.0 — `proposal-maker` (brand-copying commercial proposals)
- v2.16.0 — `style-suggest` (visual-style generator)
- v2.14.0-2.15.0 — shared `visual-prompt-library`, style library split per file
- v2.11.0-2.13.0 — two-pass typography for book covers; carousel prompt chain rewritten
- v2.10.0 — `audio-mix-maker` + `style-transfer` + `transcribe-maker` (ffmpeg audio mixing, Flux-Kontext stylization, Whisper transcription)
- v2.9.0 — `banner-maker` + `meme-card-maker` + `upscaler` (display ads / meme graphics / image super-resolution)
- v2.8.0 — `logo-maker` + `quote-card-maker` + `gif-maker` (brand mark / aphorism graphic / short looping animation)
- v2.7.0 — `cover-maker` + `thumbnail-maker` + `bg-remover` (album/book/podcast covers, 16:9 thumbnails, transparent PNG utility)
- v2.6.0 — `avatar-maker` + `voiceover-maker` + `subtitle-burner`
- v2.5.0 — `flyer-maker` (event posters / flyers / promo graphics with multi-aspect output)
- v2.4.0 — `skills-styles` (local style library CRUD + upstream PR helper)
- v2.3.1 — `skills-keys` (API key management with verify)
- v2.3.0 — `research-brief` + `carousel-builder` + `reel-builder` + 50-style library
- v2.2.x — optional API execution layer (image / video / music)

---

## Next session — brief

Two jobs, written down so the next session starts from what is already known
rather than re-deriving it.

### Job 1 — research what is worth adding

**Time-critical first.** The Sora 2 removal lands **2026-09-24**. After that
date the providers and their price entries should be deleted rather than left
warning, and the migration table in
[`skills/video-prompt/references/execute.md`](../skills/video-prompt/references/execute.md)
stops earning its space. Check the date before anything else.

**Registry re-verification is due 2026-12-03.** `tests/unit/test_model_registry.py`
fails after 120 days without a manual check; `LAST_REVIEWED` is 2026-08-03. Do
not just move the date — re-verify `PINNED_MODEL_IDS` and `PRICE_TABLE` against
vendor docs, which is the whole point of the marker.

**Known-pending items** already researched, waiting on someone else to ship:

- Ideogram 4 — open weights out, no v4 API endpoint. Wire when one appears, and
  teach `banner-maker` / `flyer-maker` / `logo-maker` to emit layout as JSON
  instead of flattening structure into prose.
- Seedream 5 Pro layered PNG output — no host exposes the field yet. This is the
  one that would change the retry loop for every text-in-image skill.
- FLUX 3, Meta Muse Image — early access, no API.
- Hashnode — API works but needs Pro; check whether that changed.

**Open questions worth actual research**, none of which this session covered:

- Modalities the collection has no answer for. 3D / spatial, voice cloning with
  consent workflows, realtime/streaming, document generation (the pre-built
  pptx/xlsx/docx Skills exist on the API surface but not in Claude Code).
- Claude Code platform features the skills do not use. Hooks beyond the
  pre-commit example, MCP servers as a distribution shape, subagents, whatever
  has shipped since. The plugin manifest landed in v2.23.0 and immediately
  unlocked a directory submission — there may be more of that kind.
- Whether anything has displaced the AEO findings from 2026-08. That research
  has a short half-life; the 17.3% structural-lift study and the citation
  overlap numbers should be re-checked, not assumed.

### Job 2 — audit the structure

Done in the unreleased section. What the audit actually found, and what it left:

**Done — two gates had never run.** `check-docs-consistency.sh` checks 2 and 5
both scanned the pre-`skills/` layout and matched nothing, so they passed by
looking at an empty list. `post-publisher` and `schema-maker` shipped through
check 5 without it opening the CHANGELOG. Both now assert their scan found
something, which is the general lesson: a gate that scans nothing prints the
same green as a gate that scans everything.

**Done — prices in the docs contradicted the billing table.** Thirteen of 153
hand-written price claims were wrong, understating a batch by up to 2.7x.
`scripts/check-prices.py` is gate 8; batch arithmetic is declared per file with
`<!-- prices: batch=N -->`.

**Done — the two description sources.** Not merged: they address different
readers and forcing parity would make both worse. `docs/skill-descriptions.lock.json`
records the SKILL.md text each catalog blurb was written against, and gate 9
fails when it moves, printing all three texts.

**Done — `skills.json` pointed at a schema that 404'd.** `docs/skills.schema.json`
now exists and `test_skills_manifest.py` validates against it, stdlib-only. It
caught a `deps` entry holding a directory path.

**Done — the distribution table.** Four-word status vocabulary, routes must name
live `make` targets, 90-day review marker. npm is on 2.23.0 against a repo on
2.24.0, because `make publish-npm` skipped itself on an expired login.

**Still open — eight near-identical single-image orchestrators.** `flyer-maker`,
`cover-maker`, `thumbnail-maker`, `avatar-maker`, `logo-maker`,
`quote-card-maker`, `banner-maker`, `meme-card-maker` share a pipeline and
differ mostly in aspect presets and a model default. This is a product decision,
not a cleanup, so the audit left it alone. Two things it can now report: the
Python is already shared (`common/runners/cli/*`, each `run.py` is a 25-line
shim), and the duplication that actually costs is in the markdown — five of the
eight carry their own `model-picker.md`, ten exist across the collection. Gate 8
now catches the drift those files used to hide, which lowers the cost of leaving
them split. Decide on discovery grounds, not maintenance ones.

**Still open — `writer/SKILL.md` is ~27 KB.** It is the base every prose skill
loads. Check whether progressive disclosure is actually happening or whether the
body should move into `references/`.

**Still open — no round-trip test for any publisher.** 745 tests, all offline.
Nothing proves a publisher's request body is what the vendor accepts — the two
live bugs found in ElevenLabs (wrong duration field, dropped lyrics) were caught
by reading docs, not by the suite. Consider recorded-fixture tests against real
response shapes.

**Still open — `common/runners/` is 30+ modules.** Check the layering still
reads: providers, publishers, CLI, and now `syndication` / `directories` /
`staticblog` / `schema_ld` sitting at top level next to `cost` and `config`.

---

## Open — model platform

Found by the 2026-08-03 registry audit. These are not new skills; they are the
execution layer keeping pace with vendors who move faster than the release
cadence.

### Sora 2 removal — hard deadline 2026-09-24

OpenAI deletes the Videos API and both Sora slugs on that date, with no
successor. The providers warn on every call and the pickers already route
elsewhere. What remains: delete the providers and the price entries once the
date passes, and drop the migration table from
[`skills/video-prompt/references/execute.md`](../skills/video-prompt/references/execute.md)
after it stops being useful.

### Ideogram 4 — wire it when the endpoint appears

Shipped 2026-06-03 with open weights and JSON-first prompting. The hosted API
still exposes only the v3 generate path, so `--execute` stays on v3. Two things
to do when v4 lands:

1. Register `ideogram-4-turbo` / `-4` / `-4-quality` at $0.03 / $0.06 / $0.10.
2. Teach `banner-maker` / `flyer-maker` / `logo-maker` to emit layout as JSON
   instead of flattening their internal structure into a prose sentence. This is
   the larger of the two — it is a second prompt mode, not a new slug.

### Seedream 5 Pro — layered output

One render decomposes into 10+ editable PNG layers. That changes the retry loop
for every text-in-image skill: a typo becomes a layer edit rather than a
regeneration, which is currently the main cause of style drift across a
carousel set. Needs a host that exposes the layered response — fal and Replicate
both mirror Seedream but not yet that field.

### FLUX 3 / Meta Muse Image — watch only

FLUX 3 (2026-07-23) generates image, video and audio from one set of weights but
is early-access with no API and no published pricing. Muse Image (2026-07-07)
has no public API. Documented in the model references, not wired.

---

## High value · low effort (single-image siblings of flyer-maker)

Each of these reuses 90% of the flyer-maker / carousel-builder infrastructure: structured event-style input → composition zones → multi-aspect batch → existing style library.

### `cover-maker` ✅ SHIPPED v2.7.0

**For**: album / book / podcast / report / deck-cover / LinkedIn-banner covers.

**Distinct from flyer-maker**: no date/location/CTA conventions; instead `--medium {album|book|podcast|report}` + `--title` + `--creator` + `--subtitle`. Aspect defaults are different per medium (album 1:1, book 2:3 portrait, podcast 1:1, report 1:√2 A4).

**Tradeoff**: very similar to flyer-maker; could be merged into one skill with `--type {flyer|cover}`. Argument for separate: cleaner Claude routing via SKILL.md descriptions, distinct invocation triggers.

**Effort**: 1 day.

### `avatar-maker` ✅ SHIPPED v2.6.0

**For**: profile pictures, headshots, social-media avatars from a user photo.

**Distinct**: identity preserve is THE differentiator; uses `nano-banana-pro` by default. No text in image. Aspect: 1:1 + variants (1:1 cropped tight for Twitter, 4:5 for LinkedIn cover, 9:16 for cover banners).

**Effort**: 1 day.

### `thumbnail-maker` ✅ SHIPPED v2.7.0

**For**: YouTube / blog / podcast-episode thumbnails. Face + bold title.

**Distinct**: aspect always 16:9 (1280×720 / 1920×1080); face placement variants (left, right, center); title overlay variants. The "thumbnail aesthetic" is its own grammar — bright contrast, exaggerated facial expressions, big text, eyeline rules.

**Effort**: 1 day.

### `banner-maker` ✅ SHIPPED v2.9.0

**For**: banner ads at standard sizes (Google Display 728×90 leaderboard, 300×250 medium rectangle, LinkedIn ad 1080×108, OG image 1200×630).

**Distinct**: standard-size presets, dense text + CTA, very small visual zone. Different aesthetic conventions from flyer (more "ad" feel, less editorial).

**Effort**: 1 day.

### `logo-maker` ✅ SHIPPED v2.8.0

**For**: brand mark / logo / wordmark.

**Distinct**: defaults to `ideogram-3-quality` (cleanest text), single image (no aspects), transparent BG hint, brief constraints (color count, style — minimal / illustrated / typographic / geometric).

**Effort**: 0.5 day. Almost a wrapper around image-prompt with a few defaults.

### `quote-card-maker` ✅ SHIPPED v2.8.0

**For**: bold quote + minimal visual. Twitter / Instagram quote cards.

**Distinct**: text-dominant composition (typography IS the image), short text (1-3 sentences), attribution line. Style anchor from carousel library with text-friendly bias.

**Effort**: 0.5 day.

### `meme-card-maker` ✅ SHIPPED v2.9.0

**For**: meme-format graphics with top + bottom text + optional centerpiece image.

**Distinct**: text positioning conventions (Impact-style top + bottom captions), can take a user photo or a generic stock-style image as base. Aesthetic is "meme template" not "editorial".

**Effort**: 0.5 day.

---

## High value · medium effort (audio extras)

These extend the runner's audio capabilities beyond music-prompt.

### `voiceover-maker` ✅ SHIPPED v2.6.0

**For**: text → narration MP3 via ElevenLabs TTS (or OpenAI TTS).

**Why it's a gap**: ElevenLabs Music + Suno are wired up, but plain TTS isn't surfaced as a dedicated skill. Currently you have to call `python3 ~/.claude/skills/music-prompt/scripts/run.py --model gpt-4o-mini-tts --prompt "..."` which is awkward and not what the skill is "for".

**What it adds**:
- Script → MP3
- Voice picker (ElevenLabs voice library / OpenAI's 6 voices)
- Speed / emotion controls
- Sentence-level pause hints

**Effort**: 1 day.

### `subtitle-burner` ✅ SHIPPED v2.6.0

**For**: take an existing MP4 + a subtitle file (SRT or VTT or plain text) → output MP4 with burned-in captions.

**Why it's a gap**: `common/runners/ffmpeg.py` has `burn_captions()` ready. But there's no skill that wraps it for "I have a video, add subtitles only". reel-builder uses it inline, but you can't invoke standalone.

**What it adds**:
- Reads SRT/VTT → ffmpeg drawtext filter sequence
- Or reads plain text + auto-timing based on audio (requires Whisper integration — heavier)
- Style presets (modern bold / kinetic / minimal black-bar)

**Effort**: 1-2 days (lightweight version is 1 day; with Whisper auto-timing it's 2-3 days).

### `audio-mix-maker` ✅ SHIPPED v2.10.0

**For**: take a video + a music file → mix them. Sometimes the user has the video + the music already and just needs a final.

**Why it's a gap**: `mix_audio_over_video` exists in ffmpeg.py but only inside reel-builder. Bare "mix this music onto this video" isn't a skill.

**What it adds**:
- Volume + fade-in/fade-out
- Mix mode: `replace` / `overlay` (overlay = keep diegetic) / `duck` (lower music when dialogue present — sidechain compressor)

**Effort**: 0.5 day (basic) to 2 days (with VAD ducking).

### `gif-maker` ✅ SHIPPED v2.8.0

**For**: short looping animation. Sometimes 2-3s on loop serves better than a still image.

**Why it's a gap**: video-prompt covers it, but the output is MP4, not GIF. No `--format gif`.

**What it adds**:
- Wraps video-prompt for 1-3 second clips (Mode B), or convert an existing MP4 (Mode A)
- Convert MP4 → GIF via ffmpeg with 2-pass palette optimization (palettegen + paletteuse + bayer dithering)
- Aspect presets (1:1 social, 9:16 story, 16:9 banner, 2:1 wide, 4:5, 1:2)

**Effort**: 0.5 day.

---

## Medium value · medium effort (image utilities)

These call existing third-party providers (Replicate / fal). Pattern: thin wrapper around a single provider endpoint.

### `upscaler` ✅ SHIPPED v2.9.0

**For**: image-upscaling (4× or 8×) for low-res images.

**Provider options**: Replicate (Real-ESRGAN default, GFPGAN for faces, SwinIR alt, clarity-upscaler for max fidelity).

**Why it's a gap**: no skill wraps "I have this blurry image, sharpen it". Currently you'd use `image-prompt --execute --model replicate-image --replicate-model real-esrgan --image-url ...` which is awkward + not discoverable.

**Effort**: 0.5 day. Simple wrapper.

### `bg-remover` ✅ SHIPPED v2.7.0

**For**: remove background from a photo (for product shots, profile pics, ID photos).

**Provider options**: Replicate (rembg, BiRefNet), fal (background removal), or local (no API) via `rembg` Python package.

**Why it's a gap**: similar to upscaler — discoverability + ergonomics.

**Effort**: 0.5 day.

### `style-transfer` ✅ SHIPPED v2.10.0

**For**: "make this photo look like {sketch / oil painting / watercolor / cyberpunk}".

**Provider options**: Flux Kontext (best for natural-language style transfer), Nano Banana Pro, fal hosted style-transfer models.

**Why it's a gap**: doable with `image-prompt --execute --model flux-kontext --image-url <photo> --prompt "transform into watercolor style"` — but no preset.

**Effort**: 0.5 day.

---

## High effort — defer

### `deck-maker`

**For**: pitch deck / slide deck. 16:9 landscape, text-heavy, multi-slide with hierarchical content.

**Why it's deferred**: a full deck is more structured than a carousel — needs sections (title slide / problem / solution / market / team / ask), per-slide layout templates, font hierarchy, footer brand strip. carousel-builder almost handles it but the slide-split assumes IG/LinkedIn portrait posts, not deck slides.

**Effort**: 3-5 days. Substantial.

### `print-ready-export`

**For**: take a digital flyer / cover, convert to print-ready CMYK 300DPI PDF.

**Why it's deferred**: real DTP requires Affinity / InDesign / Photoshop. The conversion + bleed + crop marks workflow is brittle if automated. A `print-tips` documentation page is probably more useful than a skill.

**Effort**: 2-3 days for a partial solution + many edge cases.

### `event-discovery`

**For**: scrape Eventbrite / Meetup / Luma for upcoming events matching criteria, then auto-populate `flyer-maker` fields.

**Why it's deferred**: scraping has legal/TOS complications. Better as a manual "paste the event details" workflow.

### `transcribe-maker` ✅ SHIPPED v2.10.0 (was `whisper-transcription`)

**For**: video / audio → SRT / VTT / JSON / plain-text transcript via OpenAI Whisper.

**Why it's a gap**: closes the loop with `subtitle-burner` — produce captions, then burn them in.

**Effort**: 1-2 days. Shipped with full format support (SRT / VTT / text / JSON / verbose_json with word-level timestamps).

---

## Non-goals (explicit)

These are NOT planned:

- **AI-driven prompt-engineering for content moderation** — bypassing AI safety filters is out of scope.
- **Stock-photo generation at scale** — that's what stock photo sites are for.
- **DALL-E 3 integration** — OpenAI removed dall-e-2 and dall-e-3 from the API on 2026-05-12. gpt-image-2 is the replacement, and we have it.
- **Midjourney API integration** — still no public API as of 2026-08, V8.1 included.
- **Removing/replacing background of generated images** — handled by `bg-remover` on USER photos, not generated ones (just regenerate with a different background prompt).
- **Real-time chat/streaming AI features** — out of scope for a Claude Code skill collection.

---

## Suggesting a new skill

If you have a use case that isn't covered:

1. Check this roadmap to see if it's listed as deferred or non-goal.
2. Open a GitHub issue with:
   - Use case description
   - Why existing skills don't cover it (manually composable vs. needs orchestration?)
   - Sketch of the CLI / invocation
3. Or just PR a skill following the [`CONTRIBUTING.md`](../CONTRIBUTING.md) flow — uses the same shape as existing skills.

---

## Cadence

Releases are manual, roughly weekly when there's substantial new functionality. Bug-fix-only releases happen ad-hoc.

The current pace (5 minor releases in 2 weeks) is the front-loaded build-out phase. Expect slower cadence once the orchestrator family is complete (likely after `cover-maker` + `avatar-maker` + `thumbnail-maker` land).
