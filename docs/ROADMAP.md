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

**Known-pending items** — all five re-checked 2026-08-08, two had moved:

- Ideogram 4 — **endpoint shipped, wired.** The v3 tiers were also found priced
  under the vendor's published rate; fixed. The JSON-prompt half is still open.
- Seedream 5 Pro layered output — **host shipped** (`layerize` on fal). Now
  blocked on `GenerationResult` carrying one asset; the router refuses rather
  than dropping layers it billed for.
- FLUX 3 — still application-gated, no public API, no pricing.
- Meta Muse Image — still no public API. The Meta Model API that did open is for
  Muse Spark 1.1, a reasoning model; different product.
- Hashnode — unchanged and already handled: Pro required, preflight says so.

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

**Decided — the eight single-image makers stay separate.** The premise was that
`flyer-maker`, `cover-maker`, `thumbnail-maker`, `avatar-maker`, `logo-maker`,
`quote-card-maker`, `banner-maker` and `meme-card-maker` are near-identical.
Measured, they are not: same-named reference files share 4–19% of their text,
and 656 bytes of prose is duplicated verbatim across three or more of them. The
pipeline they share is already shared, in `common/runners/cli/_maker.py`, with
each `run.py` a 25-line shim.

Merging would trade eight precise `description:` triggers for one vague enough
to match all eight, which is how a skill stops being found. The duplication that
did cost — price tables edited together on every vendor refresh — is now gate 8's
problem rather than a maintainer's. Rule written up in
[`CONTRIBUTING.md`](../CONTRIBUTING.md#adding-a-new-skill): split on routing,
merge on defaults, extract shared *data* into `common/`.

**Done — the CLI surface is introspectable, and documented commands are checked.**
Nine maker modules built their parser inside `parse_args`, so the only way to
learn what flags they took was to run them. Every module now exposes a zero-arg
`build_parser()`, and gate 10 verifies the 88 literal commands in the docs
against it. No drift today; the point is the class.

**Closed — `writer/SKILL.md` was measured in the wrong unit.** 27 KB is its size
on disk, where 59% of the file is Cyrillic and every such character costs two
UTF-8 bytes. In characters it is 16,633, behind `carousel-builder` at 19,778.
Progressive disclosure is happening: the Layer 1 section is an index of 25
category names pointing at `references/neuroslop-categories.md` rather than a
copy of it, and every skill over 10,000 characters carries a load-on-demand
table. `tests/unit/test_skill_size.py` now holds that line for the next skill —
400 lines maximum, and a `references/` link required past 10,000 characters.

**Half done — publisher contracts.** Both ElevenLabs bugs were field-name
mistakes, and a field-name mistake is invisible to a test that checks the value
it just inserted: `body["duration_secs"] == 30` passes whether or not the vendor
has heard of `duration_secs`. `tests/unit/test_publisher_contracts.py` pins the
*vocabulary* instead — each article publisher's request body against the field
list in the vendor's own docs, cited with a checked-on date. Renaming
`body_markdown` to `body_md` now fails three tests.

What that still cannot prove is that the vendor accepts the vocabulary. That
needs a recorded response fixture and a key, and remains open. The social
publishers (Instagram / Threads / TikTok / X / YouTube / LinkedIn) have no
`_body()` seam yet, so they are not covered either.

**Done — `common/runners/` layering.** Was 31 top-level modules beside four
packages; six of them were `proposal_*`, 1,747 lines of one skill's
implementation occupying a fifth of the top level, so reading the runner's
layout told you more about `proposal-maker` than about the runner. They are now
`common/runners/proposal/` — 25 modules beside five packages.

The move was not free, which is the argument for having done it: two lazy
imports inside `kit.py` (`from . import config, keysfile` and
`from .providers.base import JobHandle`) silently changed meaning, and both sat
inside a bare `except Exception` that returns `False`. One was caught by a test
written for exactly that reason; the other had no test and would have disabled
photo generation without a message.

`styles*` (3 modules) and `typography*` (2) stay flat on purpose. They are
shared infrastructure rather than one skill's guts, `styles.py` already acts as
a facade re-exporting the other two, and grouping them would be churn for
symmetry.

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

### Ideogram 4 — half wired

The endpoint appeared. Done 2026-08-08: `ideogram-4-turbo` / `-4` / `-4-quality`
at $0.03 / $0.06 / $0.10, posting to `/v1/ideogram-v4/generate` with
`rendering_speed`. The prompt field is `text_prompt`, not v3's `prompt`, and both
the path and the field name are pinned — sending a v4 slug to the v3 path returns
a valid image from the wrong model at the wrong price, and nothing in the response
says so.

Checking the vendor page for this also turned up that every v3 tier had been
priced *under* what Ideogram charges — $0.02/$0.04/$0.08 against $0.03/$0.06/$0.09
— which is the one direction `cost.py` is not allowed to be wrong in, on
`logo-maker`'s default path. Fixed, and gate 8 pulled twenty-six documented
figures along with it.

**Done — the larger half.** `json_prompt` goes through: the provider sends it or
the prose field, never both, and refuses it on a v3 tier rather than letting the
call succeed with the layout silently dropped. The contract lives once in
[`common/references/json-prompt.md`](../common/references/json-prompt.md); the
three layout skills point at it.

What is untested is whether structured prompts actually hold a layout better than
prose — that needs generating both and comparing, which needs a key. The claim in
the reference is the vendor's, and is labelled as such.

**Deliberately not done — flipping defaults.** `logo-maker` and friends still
default to `ideogram-3-quality`; the pickers now name v4 and say when to prefer
it. Changing a default changes what every existing user pays and gets, and it
cannot be justified without generating on both and comparing.

### Seedream 5 Pro — layered output, and what blocks it now

The host appeared. `bytedance/seedream/v5/pro/layerize` has been live on fal
since 2026-07-08: image plus prompt in, 2-17 transparent PNGs out, each with a
z-index, a bounding box and a name. $0.03375 per layer under 1536², $0.0675
above. Checked 2026-08-08.

**Done 2026-08-08.** `GenerationResult` grew `companions`, a suffix rather than a
rewrite: a provider returning one file behaves exactly as before, and the field
is empty for every model but this one. `output.save_result()` writes the set,
naming each file after its own layer (`-01-subject.png`, not `-01.png`) because a
directory of numbers is a puzzle rather than a layer set. `batch.py` records them
in the manifest, so `--resume` does not buy seventeen layers again to recover a
filename it already had.

The estimate quotes the 17-layer ceiling. Layerize bills per layer produced and
the count is not knowable before the call; quoting one image would say $0.05
against a possible $0.57, and `cost.py` is allowed to come in over the receipt,
never under.

Still to use it: no skill reaches for layerize on its own yet. The payoff the
roadmap argued for — a typo becoming a layer edit instead of a regeneration —
needs a text-in-image skill to notice a bad render and re-run one layer, which is
a retry-loop change, not a provider one.

### FLUX 3 / Meta Muse Image — watch only, re-checked 2026-08-08

FLUX 3 generates image, video and audio from one set of weights. Still gated:
application-only early access, Video and Action first, Image "in the coming
weeks", open-weight Dev last. No public API, no published pricing for any tier.

Muse Image still runs only inside Meta's own apps. What Meta did open is the
Meta Model API for **Muse Spark 1.1**, a reasoning model — a different product
that this collection has no use for. Do not confuse the two when re-checking.

Hashnode was on this list too and comes off it: the Pro requirement did not
change, it hardened — since May 2026 publication-scoped *reads* need Pro as
well. `publishers/hashnode.py` already fails preflight with that reason, so
nothing to do.

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
