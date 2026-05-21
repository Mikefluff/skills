# Roadmap

Identified gaps where the collection is functional but UX-painful. Tracked here so they don't get lost between releases.

Not all of these will be built. They're sorted by user-likely-to-want vs. effort, with notes on what could ship as a skill vs. what's better left as a one-liner in `image-prompt --execute` / `video-prompt --execute`.

Last updated: 2026-05-21 (post v2.9.0).

---

## What landed in recent releases

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

## High value · low effort (single-image siblings of flyer-maker)

Each of these reuses 90% of the flyer-maker / carousel-builder infrastructure: structured event-style input → composition zones → multi-aspect batch → existing style library.

### `cover-maker`

**For**: album / book / podcast / report / deck-cover / LinkedIn-banner covers.

**Distinct from flyer-maker**: no date/location/CTA conventions; instead `--medium {album|book|podcast|report}` + `--title` + `--creator` + `--subtitle`. Aspect defaults are different per medium (album 1:1, book 2:3 portrait, podcast 1:1, report 1:√2 A4).

**Tradeoff**: very similar to flyer-maker; could be merged into one skill with `--type {flyer|cover}`. Argument for separate: cleaner Claude routing via SKILL.md descriptions, distinct invocation triggers.

**Effort**: 1 day.

### `avatar-maker`

**For**: profile pictures, headshots, social-media avatars from a user photo.

**Distinct**: identity preserve is THE differentiator; uses `nano-banana-pro` by default. No text in image. Aspect: 1:1 + variants (1:1 cropped tight for Twitter, 4:5 for LinkedIn cover, 9:16 for cover banners).

**Effort**: 1 day.

### `thumbnail-maker`

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

### `voiceover-maker`

**For**: text → narration MP3 via ElevenLabs TTS (or OpenAI TTS).

**Why it's a gap**: ElevenLabs Music + Suno are wired up, but plain TTS isn't surfaced as a dedicated skill. Currently you have to call `python3 ~/.claude/skills/music-prompt/scripts/run.py --model gpt-4o-mini-tts --prompt "..."` which is awkward and not what the skill is "for".

**What it adds**:
- Script → MP3
- Voice picker (ElevenLabs voice library / OpenAI's 6 voices)
- Speed / emotion controls
- Sentence-level pause hints

**Effort**: 1 day.

### `subtitle-burner`

**For**: take an existing MP4 + a subtitle file (SRT or VTT or plain text) → output MP4 with burned-in captions.

**Why it's a gap**: `common/runners/ffmpeg.py` has `burn_captions()` ready. But there's no skill that wraps it for "I have a video, add subtitles only". reel-builder uses it inline, but you can't invoke standalone.

**What it adds**:
- Reads SRT/VTT → ffmpeg drawtext filter sequence
- Or reads plain text + auto-timing based on audio (requires Whisper integration — heavier)
- Style presets (modern bold / kinetic / minimal black-bar)

**Effort**: 1-2 days (lightweight version is 1 day; with Whisper auto-timing it's 2-3 days).

### `audio-mix-maker`

**For**: take a video + a music file → mix them. Sometimes the user has the video + the music already and just needs a final.

**Why it's a gap**: `mix_audio_over_video` exists in ffmpeg.py but only inside reel-builder. Bare "mix this music onto this video" isn't a skill.

**What it adds**:
- Volume + fade-in/fade-out
- Mix mode: `replace` / `overlay` (overlay = keep diegetic) / `duck` (lower music when dialogue present — would need a VAD)

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

### `bg-remover`

**For**: remove background from a photo (for product shots, profile pics, ID photos).

**Provider options**: Replicate (rembg, BiRefNet), fal (background removal), or local (no API) via `rembg` Python package.

**Why it's a gap**: similar to upscaler — discoverability + ergonomics.

**Effort**: 0.5 day.

### `style-transfer`

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

### `whisper-transcription`

**For**: video → SRT subtitle file via OpenAI Whisper.

**Why it's deferred** (but would be useful for `subtitle-burner`): requires Whisper API integration; OpenAI has it but quality varies; running locally requires ffmpeg + whisper.cpp.

**Effort**: 1-2 days.

---

## Non-goals (explicit)

These are NOT planned:

- **AI-driven prompt-engineering for content moderation** — bypassing AI safety filters is out of scope.
- **Stock-photo generation at scale** — that's what stock photo sites are for.
- **DALL-E 3 integration** — superseded by gpt-image-2 (which we have).
- **Midjourney API integration** — no public API exists as of 2026-05.
- **Removing/replacing background of generated images** — handled by `bg-remover` (planned) on USER photos, not generated ones (just regenerate with a different background prompt).
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
