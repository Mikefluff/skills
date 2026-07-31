# Composing skills — workflow recipes

The 41 skills aren't independent — they stack. `writer` is the foundation; wrappers extend it; linters audit without mutating; orchestrators chain multiple wrappers + the execute layer + style libraries; meta-skills manage the collection.

This file is the **recipe book**: named workflows showing concrete skill chains for typical jobs.

---

## Contents

- [Core composition rules](#core-composition-rules)
- [Layered architecture](#layered-architecture)
- [Recipe library](#recipe-library)
  - [Prose recipes](#prose-recipes)
  - [Marketing & ops recipes](#marketing--ops-recipes)
  - [AI media recipes](#ai-media-recipes)
  - [Orchestrator recipes](#orchestrator-recipes)
  - [Meta recipes](#meta-recipes)
- [Skill-to-skill data flow](#skill-to-skill-data-flow)
- [Common anti-patterns](#common-anti-patterns)

---

## Core composition rules

1. **`writer` is the base.** 12 of 41 skills run `writer` as their final cleanup pass. You rarely call `writer` directly except for raw clean-up.
2. **Linters are read-only.** `style-check`, `translation-sync`, `canon-check` produce reports, never mutate text. Use as quality gates.
3. **One wrapper per pass.** Don't try to chain `prose-edit` + `essay-write` on the same text in one go. Pick the right one for the genre.
4. **Linters AFTER wrappers.** Apply rewrites first, then lint. The opposite order tells you what you already know.
5. **Orchestrators have one upstream feeder.** `research-brief` feeds `carousel-builder` and `reel-builder`. The orchestrator's outputs (manifest.json + style-used.md) are reproducible — keep them.
6. **Meta-skills are operational.** `skills-update` and `skills-keys` don't edit text; they manage the collection and its keys.

---

## Layered architecture

```
┌─────────────────── meta ────────────────────┐
│  skills-update  ·  skills-keys              │
└─────────────────────────────────────────────┘

┌─────────────────── orchestrators ───────────┐
│  research-brief                             │
│       │                                     │
│       ▼                                     │
│  carousel-builder  ·  reel-builder          │
│    (consume --research <path> from above)   │
└─────────────────────────────────────────────┘

┌─────────────────── linters (read-only) ─────┐
│  style-check  ·  translation-sync           │
│  canon-check                                │
└─────────────────────────────────────────────┘

┌─────────────────── wrappers ────────────────┐
│  Prose:    viral-text  prose-edit           │
│            essay-write  pelevin-digression  │
│            tone-shifter                     │
│  Marketing/ops:                             │
│            cold-email  microcopy            │
│            release-notes  rfc-writer        │
│            landing-copy                     │
│  Media:    image-prompt  video-prompt       │
│            music-prompt                     │
└─────────────────────────────────────────────┘

┌─────────────────── base ────────────────────┐
│  writer                                     │
└─────────────────────────────────────────────┘
```

The orchestrators sit ABOVE the wrappers because they CALL the wrappers internally (via `--execute` for image/video/music + via direct invocation for viral-text / essay-write).

---

## Recipe library

### Prose recipes

#### Write a fiction chapter, commit-ready

```
prose-edit → pelevin-digression (optional) → canon-check → style-check
```

`prose-edit` rewrites with Pelevin/Manson voice vector; `pelevin-digression` inserts voice digressions on demand; `canon-check` validates against story bible; `style-check` is the final read-only gate.

#### Write a non-fiction longread with sources

```
essay-write → pelevin-digression (optional) → style-check
```

`essay-write` drafts the longread (Manson coda, V/H/P markers, plain Russian); `pelevin-digression` inserts voice flair where the user asks; `style-check` gates the result.

#### Verify a multilingual book translation

```
translation-sync (audit) → prose-edit (RU) → tone-shifter (EN) → translation-sync (verify)
```

Initial parity audit; polish RU side; ensure EN matches register; final parity confirm.

#### Shift the register of existing content

```
tone-shifter (casual → business-formal) → writer (final cleanup)
```

Single-pass register shift + `writer` cleans typography and residue.

#### Story-bible audit only

```
canon-check
```

Read-only. Returns drift report. Pair with manual fixes, then re-run.

#### Read-only quality gate (no edits)

```
style-check
```

Standalone audit. Returns severity-tagged report; no mutations.

### Marketing & ops recipes

#### Ship a SaaS product launch

```
landing-copy → microcopy → release-notes → viral-text (RU) + viral-text (EN)
```

Landing-copy writes hero + features + pricing; microcopy fills UI strings + 404; release-notes documents what shipped; viral-text generates social announcements per locale.

#### Pitch a startup to investors

```
cold-email (first-touch) → cold-email (follow-up) → landing-copy (hero) → rfc-writer (tech spec)
```

First-touch; anchored follow-up; landing for the deck; tech spec for engineering audience.

#### Build out a marketing site

```
landing-copy (hero + features + pricing) → microcopy (UI + 404) → release-notes (changelog page) → landing-copy (SEO meta)
```

#### Document an architecture decision

```
rfc-writer (RFC) → rfc-writer (ADR after) → release-notes (announce when shipped)
```

RFC opens discussion; ADR captures the decision; release-notes informs users when it ships.

### AI media recipes

#### Generate a single image (prompt-only or executed)

```
image-prompt --execute --model <slug>
```

Picks the model; assembles the per-model prompt; if `--execute` and the model's env var is set, calls the API and saves PNG. Without `--execute`, returns paste-ready prompt only.

#### Generate a single video shot

```
video-prompt --execute --model <slug> --duration <s>
```

Same shape for video. Async poll-with-timeout; cost confirmation above $0.10.

#### Generate a music track

```
music-prompt --execute --model <slug>
```

Two-box workflow for Suno/Udio (Style + Lyrics); single-prompt for Lyria/Eleven/Stable Audio.

#### Cover the full content stack for a campaign (manual)

```
landing-copy + image-prompt + video-prompt + music-prompt + viral-text + cold-email
```

Landing + cover + reel + bgm + organic + outbound. Each independent; cross-links live in your campaign brief. For an automated end-to-end version see the orchestrator recipes.

### Orchestrator recipes

#### Research → carousel → reel (end-to-end, ONE command per stage)

```
research-brief → carousel-builder --research <path> → reel-builder --research <path>
```

`research-brief` produces a markdown brief at `./generated/research/<slug>-<date>.md`. Both downstream skills ingest it via `--research <path>` and reuse the same angle. Total wall time: ~6-10 min. Cost: $2-7 depending on provider mix.

Full walkthrough: [`walkthroughs/research-to-carousel-reel.md`](walkthroughs/research-to-carousel-reel.md).

#### Carousel from a research brief

```
carousel-builder --research <path> --platform <p> --slides <n> --style <id-or-auto> --execute
```

Splits brief into N slides with one consistent visual style (24-style library). Outputs PNG slides + captions + manifest. Use `--resume` to retry failed slides only.

#### Reel from a research brief

```
reel-builder --research <path> --shots <n> --style <video-id> --music-style <music-id> --execute
```

Drafts script from brief; generates 1-4 video shots + matched music; ffmpeg-stitches into final.mp4 with optional captions.

#### Carousel from a free topic (no research)

```
carousel-builder --topic "<text>" --platform instagram --execute
```

Internally invokes `viral-text` (for Instagram / TikTok) or `essay-write` (for LinkedIn) to draft content, then runs the same pipeline as the research-driven path.

#### Brand identity pack (logo + cover + quote card)

```
logo-maker --brand "<name>" --style wordmark --variants 6 --execute
cover-maker --title "<brand-product>" --creator "<brand>" --medium book --execute
quote-card-maker --quote "<brand-tagline>" --attribution "— <brand>" --style minimal-serif --execute
```

Pick the best logo variant. Use the same style anchor across all 3 for visual consistency (e.g., feed the same `--style swiss-grid-poster` to cover-maker and quote-card-maker). Cost: $0.50-1.50 total for a brand starter kit.

#### Quote card series for content marketing

```
for q in <list-of-quotes>; do
  quote-card-maker --quote "$q" --attribution "<source>" --style <fixed-anchor> --aspects square --execute --yes
done
```

Fixed `--style` across all = visually consistent series. Set `--aspects square,portrait` to ship to multiple platforms in one pass.

#### Animated reaction or hero loop (GIF)

```
gif-maker --prompt "<short-loop-description>" --model veo-3-1-fast --duration 3 --aspect 1:1 --execute
gif-maker --input ./reel-final.mp4 --aspect 1:1 --duration 2 --output ./reaction.gif
```

Two modes. Mode A reuses an existing MP4 (e.g., a shot from `reel-builder`). Mode B generates from a prompt. GIFs <2MB for Twitter/Slack performance.

#### Full launch campaign visuals (banner + cover + thumbnail)

```
banner-maker --headline "<launch-line>" --cta "<cta>" --brand "<name>" --presets og,linkedin-ad,facebook-ad --execute
cover-maker --title "<launch-line>" --creator "<brand>" --medium linkedin-doc --execute
thumbnail-maker --title "<launch-line>" --photo <hero> --type youtube --execute
```

Three skills, one launch line — covers OG previews + LinkedIn doc cover + YouTube video thumbnail. Run with the same `--style` for visual consistency. Cost: $0.50-1.50 total.

#### Brand identity + ad creatives (logo + banner ads)

```
logo-maker --brand "<name>" --style wordmark --variants 6 --execute
banner-maker --headline "<line>" --cta "<cta>" --brand "<name>" --logo ./generated/logo/<slug>/logo-v1.png --presets og,linkedin-ad,medium-rectangle --execute
```

Generate logo first → pass best variant as `--logo` to banner-maker so the brand mark inspires the banner composition.

#### Meme + carousel content (cultural commentary post)

```
meme-card-maker --top "<setup>" --bottom "<punchline>" --template drake --variants 4 --execute
carousel-builder --topic "<related-essay-angle>" --slides 5 --style swiss-grid-poster --execute
```

Meme as hook + carousel as substance. Post meme on Twitter (high reach), carousel on LinkedIn (long-form depth).

#### Restore + repurpose old assets (upscale + cover)

```
upscaler --image ./old-photo.jpg --scale 4 --replicate-model tencentarc/gfpgan --execute
cover-maker --title "<book>" --creator "<author>" --medium book --photo ./generated/upscaled/old-photo-4x.png --execute
```

Old family photo → upscale + face-restore → use as book cover reference.

#### Auto-caption a tutorial (transcribe + burn)

```
transcribe-maker --input ./tutorial.mp4 --format srt --lang en --output ./captions.srt --execute --yes
subtitle-burner burn ./tutorial.mp4 --subtitle ./captions.srt --style modern --output ./tutorial-captioned.mp4
```

End-to-end auto-captioning. Whisper transcribes; ffmpeg burns. Cost: ~$0.006/min Whisper + $0 ffmpeg.

#### Voiceover-driven explainer with music bed (TTS + mix)

```
voiceover-maker --prompt-file ./script.txt --model eleven-tts --voice-id <stable-id> --execute --yes
music-prompt --execute --model suno-v5-5 --prompt "ambient instrumental, gentle progression, ~2 min" --instrumental --execute --yes
# Manually replace silent video with voiceover (replace mode), then mix music under voice (duck mode):
audio-mix-maker --video ./screen-recording.mp4 --audio ./generated/audio/voiceover.mp3 --mode replace --output ./step1.mp4
audio-mix-maker --video ./step1.mp4 --audio ./generated/music/bed.mp3 --mode duck --volume 0.4 --duck-amount 0.5 --output ./final.mp4
```

Three skills, one explainer video with TTS narration + ducked music bed. Cost: ~$0.30-1.00 (depending on TTS provider + music length).

#### Style-transfer brand identity (logo → stylized variants)

```
logo-maker --brand "Lunar Vault" --style wordmark --variants 4 --execute
style-transfer --image ./generated/logo/lunar-vault/logo-v1.png --style watercolor --execute      # watercolor brand variant
style-transfer --image ./generated/logo/lunar-vault/logo-v1.png --style line-art --execute        # line-art brand variant
```

Generate a logo + produce stylized variations for different brand touchpoints (watercolor for editorial, line-art for icons, etc.).

### Meta recipes

#### Add or rotate API keys

```
skills-keys add OPENAI_API_KEY
skills-keys add GEMINI_API_KEY
skills-keys verify
```

Interactive silent prompts. Confirm by pinging vendor APIs.

#### Update the collection

```
skills-update
```

Checks for newer release, shows CHANGELOG diff, asks confirmation, runs `install.sh --update`.

---

## Skill-to-skill data flow

| From | Output | Into | Notes |
|---|---|---|---|
| `writer` | cleaned prose | any wrapper | wrapper's final pass |
| `viral-text` | full post | `style-check` | optional pre-publish gate |
| `prose-edit` | rewritten chapter | `canon-check` + `style-check` | both gates often run |
| `essay-write` | drafted essay | `pelevin-digression` → `style-check` | digression inserted then gate |
| `translation-sync` | parity report | (no skill) | author applies fixes |
| `tone-shifter` | re-voiced passage | `writer` | always |
| `cold-email` | email body | `writer` | always |
| `image-prompt` | per-model prompt | external model OR `--execute` | paste-ready, or call the API |
| `video-prompt` | per-model prompt | external model OR `--execute` | same |
| `music-prompt` | per-model prompt | external model OR `--execute` | same; Suno/Udio = two-box |
| `microcopy` | UI strings | `writer` | optional cleanup |
| `release-notes` | changelog md | `writer` | optional cleanup |
| `rfc-writer` | RFC/ADR md | `writer` | optional cleanup |
| `landing-copy` | landing sections | `microcopy` + `writer` | UI strings + cleanup |
| `research-brief` | markdown brief | `carousel-builder` / `reel-builder` | via `--research <path>` |
| `carousel-builder` | PNG slides + captions + manifest | (no skill; user posts) | manifest enables --resume |
| `reel-builder` | final.mp4 + components + manifest | (no skill; user posts) | manifest enables --resume |
| `skills-keys` | (writes ~/.skills.env) | runner CLIs | auto-loaded at runner startup |
| `skills-update` | (re-installs) | none | meta |

---

## Common anti-patterns

✗ **Linting before rewriting.** `style-check` on a raw draft tells you what the wrapper already knows. Use linters as final gates, not first passes.

✗ **Stacking two wrappers on the same text.** `prose-edit` + `essay-write` on the same passage = competing rule sets. Pick one for the genre.

✗ **Translating with `tone-shifter`.** `tone-shifter` shifts register WITHIN a language. For RU↔EN, use `translation-sync` for verification + a wrapper in the target language.

✗ **Marketing copy via `essay-write`.** `essay-write` is for longread non-fiction; landing copy needs `landing-copy` (different rules, shorter forms).

✗ **`writer` for register shift.** `writer` cleans LLM-prose tells, doesn't change register. Use `tone-shifter`.

✗ **Mixing image providers across carousel slides.** Even with the same style anchor, the model's fingerprint differs per call. Lock one provider per carousel.

✗ **Mixing video providers across reel shots.** Same reason. The reel-builder enforces one provider per reel.

✗ **Running `carousel-builder` / `reel-builder` without inspecting prompts first.** These are the most expensive operations in the collection ($0.50-$7). Always run `--prompts-only` first to inspect the assembled plan before spending.

✗ **Committing `~/.skills.env` to a repo.** Use `skills-keys` to manage; the file lives in `$HOME` by default. If you relocate it via `SKILLS_KEYS_FILE`, add the new path to `.gitignore`.

---

## Cross-references

- [All 41 skills (auto-generated table)](../README.md#whats-in-the-box)
- [Scenario-based picker](USER-GUIDE.md)
- [Walkthroughs (categorized index)](walkthroughs/)
- [Quickstart (5-minute first run)](QUICKSTART.md)
- [Style library (50 visual / directorial / music presets)](../common/style-library/)
