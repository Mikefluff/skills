---
name: carousel-builder
description: "Orchestrator skill — turns a topic or research brief into an N-slide Instagram / LinkedIn / TikTok carousel with consistent visual style and ready-to-post captions. Wraps essay-write + viral-text (for content) + image-prompt --execute (for slides) + common style library (24 visual styles). Modes: --topic / --research; --style auto|<library-id>|--style-ref <image>; --slides 3-12; --platform instagram|linkedin|tiktok; --aspect portrait|square|story; --text-mode embedded|overlay|none; --execute; --resume. Outputs: ./generated/carousel/<slug>/slide-{1..N}.png + captions.md + manifest.json. Use when the user says 'make a carousel about X', 'turn this research into a post', '8 slides on Y', 'carousel for LinkedIn'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
End-to-end carousel generator. Input: topic OR research brief. Output: N image files with consistent visual style + per-slide caption + final post copy + manifest for --resume.

This skill orchestrates four lower-level skills:
1. `essay-write` or `viral-text` → drafts the content
2. `image-prompt` style anchor + per-slide prompts
3. `common/runners` execute layer → batch generation via the chosen provider
4. `common/style-library/carousel/` → style anchor (24 bundled styles + user overrides)

Use when the user wants a finished carousel, not just prompts. Without `--execute`, returns the 8 prompts + captions for manual paste; with `--execute`, generates and saves the actual PNG slides.

This skill does NOT:
- Compose the slides into a single tall image — Instagram / LinkedIn handle multi-image posts natively.
- Add text overlays via a design tool — text either gets generated INSIDE the image (gpt-image-2 / Ideogram / Imagen) via `--text-mode embedded`, or is left to the user's editor (`--text-mode overlay`).
- Generate animated carousels (those are reels — use `reel-builder`).
- Post to platforms — output is files you upload via the platform's UI / API.
</objective>

## ROLE

Topic / research → split content into N slides → pick style + model → assemble 8 per-slide prompts (style anchor + slide content + composition hint) → batch execute via image provider (one provider for all slides for consistency) → write slides + captions + manifest → print final paths.

## PIPELINE

1. **Resolve input source**:
   - `--research <path>`: read the brief. Use TL;DR as hero, Key facts as slide content, Suggested angles to inform tone.
   - `--topic "<text>"`: invoke `essay-write` (long-form) or `viral-text` (hook-driven) to produce 200-400 word source content first. Choose based on `--platform`:
     - `instagram` / `tiktok` → `viral-text`
     - `linkedin` → `essay-write`

2. **Split into slides** — see `references/slide-split.md`:
   - Default 8 slides: hook → 5 points → micro-conclusion → CTA.
   - 6-slide: hook → 3 points → conclusion → CTA.
   - 10-slide: hook → 7 points → conclusion → CTA.
   - 3-slide (minimal): hook → main → CTA.
   - Each slide has a `role` field: `hook` | `point` | `data` | `quote` | `framework` | `conclusion` | `cta`.

3. **Resolve style** — see `references/style-resolution.md`:
   - `--style <id>`: load from `common/style-library/carousel/<id>.md`. Use the `Style anchor (carousel)` block; if `--text-mode embedded`, use the `Style anchor (text-in-image mode)` block instead.
   - `--style auto`: examine topic + tone → narrow candidates to 3-5 from library → pick first, log alternatives.
   - `--style-ref <path>`: skip library; use the user's image as multi-ref. Requires a model that supports image-ref (Nano Banana Pro / Flux Kontext / Seedream / Ideogram ref-mode).
   - `--style auto` + `--style-ref <path>`: BOTH — library style anchor TEXT + user reference IMAGE. Provider gets both.

4. **Pick model** — see `references/model-picker.md`:
   - `--model auto`: text-heavy slide AND `--text-mode embedded` → gpt-image-2 or Ideogram 3 Quality. Photo-realistic style → Flux 2 Pro / Imagen 4 Ultra. Illustration / 3D style → Nano Banana Pro / Flux 2 Pro. Multi-ref present → Nano Banana Pro.
   - `--model <slug>`: override. Validate that the model is registered + env var is set.
   - ONE model for all slides. Mixing models breaks consistency.

5. **Build per-slide prompts** — see `references/slide-split.md` for the composition hint per role. Each prompt:
   ```
   <style anchor (carousel)>

   <slide content prompt, 30-80 words, includes the SPECIFIC subject for this slide>

   Composition: <role-specific framing>. Aspect: <4:5 for portrait | 1:1 for square | 9:16 for story>.

   <if embedded text mode> Embed headline text: "<EXACT TEXT TO RENDER>" in <typography hint from style anchor>.
   ```

6. **Estimate cost + confirm** — sum per-slide estimates × N slides. If total > $0.10 and not `--yes`, prompt for confirmation. See `common/runners/cost.confirm_batch()`.

7. **Batch execute** — `common.runners.batch.run_batch()`:
   - Parallelism: default 3 (rate-limit safe).
   - Manifest: `./generated/carousel/<slug>/manifest.json` updated after every slide.
   - `--resume` picks up succeeded slides from the manifest, only retries failures.

8. **Compose captions** — `references/platform-presets.md` defines per-platform caption rules:
   - Instagram: hook (1 sentence) + body (3-5 sentences) + CTA + 15-25 hashtags
   - LinkedIn: longer narrative (300-800 chars), no hashtags spam, end with question CTA
   - TikTok: short post copy + 3-5 hashtags + sound credit if applicable
   Write per-slide caption (1-2 sentences) AND the main post caption. Both saved to `captions.md`.

9. **Output**:
   ```
   ./generated/carousel/<slug>/
     slide-1.png  ... slide-N.png
     captions.md         # main post + per-slide alts
     manifest.json       # for --resume
     style-used.md       # snapshot of style anchor (for reproducibility)
     prompts.md          # all N per-slide prompts (for inspection / paste fallback)
   ```

   stdout last lines:
   ```
   Carousel: ./generated/carousel/<slug>/  (N/M slides succeeded)
   Captions: ./generated/carousel/<slug>/captions.md
   ```

## MODES

### Input

- `carousel-builder --topic "<text>"` — generate content first via essay-write/viral-text, then slides
- `carousel-builder --research <path>` — ingest a research-brief markdown file
- `carousel-builder --content-file <path>` — use already-written content (skip step 1)
- `carousel-builder --slide-script-file <path>` — bring your own pre-split slide content (skip step 2)

### Style

- `--style auto` — pick from library based on topic + tone
- `--style <library-id>` — explicit style (see `common/style-library/carousel/_index.md`)
- `--style-ref <image-path>` — use user image as ref (requires multi-ref capable model)
- `--style-mod "<override snippet>"` — append a tweak to the chosen style anchor (e.g. "but with cooler color temperature")

### Structure

- `--slides N` — default 8, range 3-12
- `--platform instagram|linkedin|tiktok` — preset for aspect + caption rules (default instagram)
- `--aspect portrait|square|story` — overrides platform default (4:5 / 1:1 / 9:16)
- `--text-mode embedded|overlay|none` — embedded = text inside image (Ideogram/gpt-image-2/Imagen); overlay = no text in image, user adds in Canva; none = no text at all
- `--variants N` — generate N visual variations of each slide (default 1)

### Execution

- `--execute` — actually generate images (requires API key for chosen model)
- `--model auto|<slug>` — image provider (default auto-pick)
- `--output <dir>` — custom output dir (default `./generated/carousel/<slug>/`)
- `--parallelism N` — concurrent API calls (default 3, max 6)
- `--yes` — skip cost confirmation
- `--resume` — pick up from manifest.json after a partial failure

### Inspection / dry-run

- `--prompts-only` — print all per-slide prompts, don't generate (use this to review before spending)
- `--cost-only` — print total estimated cost, exit
- `--check` — validate env vars + style file + research file exist; exit 0 if ready

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/slide-split.md](references/slide-split.md) | Step 2 — how to split content into N slides with roles + composition rules |
| [references/style-resolution.md](references/style-resolution.md) | Step 3 — auto-pick algorithm, ref-image rules, multi-ref provider compatibility |
| [references/model-picker.md](references/model-picker.md) | Step 4 — model auto-pick decision tree, capability matrix |
| [references/platform-presets.md](references/platform-presets.md) | Step 8 — caption rules per platform, hashtag policy, char limits |
| [references/batch-execute.md](references/batch-execute.md) | Step 6-7 — how batch runner works, manifest format, retry semantics, failure handling |
| [references/troubleshoot.md](references/troubleshoot.md) | When generation fails or style drifts across slides |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: 8-slide LinkedIn carousel from a research brief (Flux 2 Pro), 6-slide Instagram with embedded text (Ideogram 3 Quality), 10-slide TikTok with user-provided reference image (Nano Banana Pro).

## CONSTRAINTS

- **One style anchor across all slides.** Use the SAME provider, SAME style anchor text, SAME aspect ratio for every slide. The only thing that varies per slide is the content prompt + the role-specific composition hint. Mixing breaks the carousel feel.

- **One model for the whole carousel.** Don't mix Flux 2 Pro + Ideogram 3 across slides — even with the same anchor, the model's style fingerprint differs and the carousel loses cohesion.

- **Style library is the source of truth for visual consistency.** Don't write free-form style descriptions inside this skill. If `--style auto` and no library entry fits, pick the closest match + `--style-mod "<override>"`.

- **Cost confirm ONCE per batch.** Sum total across N slides, ask user once before the first call. Don't ask per-slide.

- **Manifest updates after every slide.** Crash safety — if API fails mid-batch, `--resume` picks up where it left off.

- **Failure mode**: if K of N slides fail, save the K successes + log the M failures in manifest. Exit code 1 (non-fatal). User can `--resume` to retry only failures.

- **Prompts saved alongside output.** Every run writes `prompts.md` with the 8 per-slide prompts. User can copy any failed prompt and paste manually into the provider's UI.

- **Never print API keys.** Mask in errors. Reference env var names only.

- **Output dir is `./generated/carousel/<slug>/`** by default. Don't write outside it without explicit `--output`.

- **Slug = kebab-case-of-topic, max 40 chars.** Same convention as research-brief. Date suffix if collision.

- **Text-mode embedded ONLY with text-friendly models.** Ideogram 3 / gpt-image-2 / Imagen 4 — others get a warning + automatic fallback to overlay mode. List enforced in `references/model-picker.md`.

- **No copyrighted living artist names in prompts.** Style library entries never reference artists by name in their anchor text (already enforced by the library schema).

- **No real-brand mimicry in prompts.** "WWDC-style", "Apple's recap aesthetic" — banned. Use generic descriptors. Library entries already follow this.

- **`--prompts-only` is the safety dry-run.** Before any expensive batch, recommend `--prompts-only` so user can sanity-check.

- **Captions: write per-platform.** Don't write Instagram captions for a LinkedIn carousel.

## INVOCATION HINTS

When the user says any of:
- "carousel about / on X", "8 slides about Y"
- "Instagram carousel", "LinkedIn carousel", "TikTok carousel"
- "make a post on X" (clarify if image / carousel / reel)
- "turn this research into slides", "carousel from this brief"
- "10-slide explainer on Z"

RU triggers:
- «карусель про X», «8 слайдов про Y»
- «карусель для Instagram / LinkedIn / TikTok»
- «сделай пост / карусель из этого ресерча»
- «10-слайдовый разбор Z»

If the user gives a topic but no platform: default to `instagram`, ask once if LinkedIn or TikTok is meant. If the user gives a research file path, default to the format the brief was prepared for (`--for carousel` markers in the brief metadata).

Defaults: `--slides 8 --platform instagram --aspect portrait --text-mode embedded --model auto`. Without `--execute`, returns prompts + caption text for manual paste. With `--execute`, generates slides.

This skill is downstream of `research-brief` (consumes the brief) and upstream of any manual post — final step is uploading the slides to the platform's UI.
