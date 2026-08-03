---
name: carousel-builder
description: "Turn a topic or research brief into an N-slide Instagram / LinkedIn / TikTok carousel with consistent visual style and ready-to-post captions. Modes: --topic / --research; --slides 3-12; --platform; --aspect; --text-mode. Use when: 'make a carousel about X', 'turn this research into a post', '8 slides on Y', 'carousel for LinkedIn'."

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
- Post to platforms — that is `post-publisher`, which takes this skill's output directory as its input.
</objective>

## ROLE

Topic / research → split content into N slides → pick style + model → assemble 8 per-slide prompts (style anchor + slide content + composition hint) → batch execute via image provider (one provider for all slides for consistency) → write slides + captions + manifest → print final paths.

## PIPELINE (v2.14.0+ — promptCarousel chain, mirrors `figma/app/lib/carousel/promptCarousel/`)

1. **Resolve input** — topic OR research brief OR finished post text:
   - `--research <path>`: read the brief, extract TL;DR / key facts / suggested angles as the topic.
   - `--content-file <path>`: user-supplied finished post text. PRESERVE the author's voice — direct quotes + cuts only, no paraphrasing. If the text contains `==word==` accent markers, those words become accent-color callouts on the relevant slides.
   - `--topic "<text>"`: short topic string. Optionally invoke `viral-text` (IG/TikTok) or `essay-write` (LinkedIn) first to produce ~150-220 word post text with `==accents==` if the topic is rich enough to benefit. For pure promo decks (course invitation / product launch), topic-only is sufficient.

2. **Resolve style** — see [`common/visual-prompt-library/styles/_index.md`](../../common/visual-prompt-library/styles/_index.md):
   - `--style <name>`: explicit style from the 13-name library (`BIOTECH`, `CYBER-NOIR`, `BRUTALIST`, `VAPORWAVE`, `MILITARY`, `SCIENTIFIC`, `STREETWEAR`, `ART-DECO`, `BLUEPRINT`, `GRUNGE`, `GLAMOUR`, `NATURE`, `ADVENTURE`). The library entry's full description is passed verbatim into the LLM user message.
   - `--style custom`: user provides a `customStyle` description as a free-text override. Passed verbatim.
   - `--style auto` (default): LLM auto-picks based on topic / tone / audience / goal — see the matrix at the bottom of `style-library.md`.
   - `--style-ref <image>`: optional style reference image. Image-side multi-ref + the text style instruction.
   - `--character-ref <image>`: optional character reference photo. The LLM is instructed NOT to describe face/build (the image-side reference handles identity); it describes pose/action/position only.
   - `--brand-colors "<list>"`: optional named colors that MUST be the dominant palette in every slide.

3. **Pick model** — see [`references/model-picker.md`](references/model-picker.md):
   - `--model auto` (default): nano-banana-pro (text-in-image leader + multi-ref). Alternatives: gpt-image-2 (16 refs, top text rendering), Ideogram 3 Quality (text-heavy posters), Flux 2 Pro (photo-real).
   - One model for all slides — mixing models breaks consistency.

4. **Compose ONE LLM call** — load [`common/visual-prompt-library/system-prompt.md`](../../common/visual-prompt-library/system-prompt.md) (the SYSTEM_PROMPT) and `buildUserMessage(opts)` filled with the resolved inputs. Spawn ONE Agent (subagent_type=`general-purpose`) with `system=SYSTEM_PROMPT` and `user=<built message>`. The agent returns JSON `{"slides":[{"number":1,"prompt":"..."},...]}` — N short (1–3 sentence) image prompts, text-in-quotes, layout language, carousel chrome (page indicator + swipe/end marker) appended to each.

   **Discipline (all enforced in the SYSTEM_PROMPT — do NOT bypass)**:
   - ONE LLM call, not per-slide subagents (per-slide breaks visual consistency).
   - Each prompt 1–3 sentences. No 250-word spec-dumps with "12% frame height" / "1px stroke" — those produce magazine-with-overlay slop.
   - Text-to-render in double quotes exactly.
   - No meta-labels in the prompt body (no literal `HEADLINE:` / `SUBTITLE:` / `FRAMEWORK:` — they render as visible text on the image).
   - Infographic discipline for middle slides — real numbers / real names / real steps / real cards, never atmospheric vibes + a sentence.
   - Slide 1 = hook, last slide = CTA (full CTA phrase verbatim, no condensing).
   - Visual consistency across slides — same palette + treatment + character.

   **Retry on bad output**: if the agent returns malformed JSON OR fewer than N slides OR any prompt is missing carousel chrome / has forbidden literals (HEADLINE / hex codes / "Instagram"), re-run the agent ONCE with a stricter reminder appended. After 2 attempts, ship the partial result and warn the user.

5. **Assemble plan.json** — items `[{index, label, prompt, kwargs:{size, image_url}}]`. `prompt` is the LLM-returned text verbatim. `image_url` points to the character ref photo when provided (multi-ref capable provider locks identity). Single canonical path (e.g. `/tmp/plan.json` or `./generated/carousel/<slug>/plan.json`) — overwrite each run, don't proliferate `plan-v1.json` / `plan-v2.json`.

6. **Estimate cost + confirm** — sum per-slide estimates × N slides. If total > $0.10 and not `--yes`, prompt for confirmation. See `common/runners/cost.confirm_batch()`.

7. **Batch execute** — `python3 -m common.runners.cli.carousel --plan-file <plan.json> --yes`:
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

### Animation (chained reel — see "`--animate`" section below)

- `--animate` — after slides render, animate each slide via the video-chain SYSTEM_PROMPT + reel CLI (one command, no manual plan assembly)
- `--animate-duration 4|8` — seconds per shot (default 4)
- `--animate-provider veo-3-1-fast|veo-3-1|kling-3|runway-gen-4` — default veo-3-1-fast
- `--animate-stitch on|off` — ffmpeg-concat into one reel (on, default) or N independent clips (off)

### Inspection / dry-run

- `--prompts-only` — print all per-slide prompts, don't generate (use this to review before spending)
- `--cost-only` — print total estimated cost, exit
- `--check` — validate env vars + style file + research file exist; exit 0 if ready

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [common/visual-prompt-library/system-prompt.md](../../common/visual-prompt-library/system-prompt.md) | Step 4 — **PRIMARY**: the shared SYSTEM_PROMPT (verbatim) + buildUserMessage shape + retry policy + invocation pattern. Used by all visual-output skills (carousel / cover / flyer / quote / meme / banner / logo). |
| [common/visual-prompt-library/styles/_index.md](../../common/visual-prompt-library/styles/_index.md) | Step 2 — 13 named visual styles + auto-pick matrix. Shared library across all visual skills. |
| [references/slide-roles.md](references/slide-roles.md) | Optional — when briefing the LLM with substantive content per slide (framework boxes / data points / quote attribution), this file documents the 9 role-content contracts. NOT required — the SYSTEM_PROMPT in `common/visual-prompt-library/system-prompt.md` already enforces infographic discipline. |
| [common/style-library/carousel/_universal-rules.md](../../common/style-library/carousel/_universal-rules.md) | Legacy — the rules are now embedded in `common/visual-prompt-library/system-prompt.md` SYSTEM_PROMPT. Keep this file for back-compat link checks but prefer the system-prompt reference. |
| [references/slide-split.md](references/slide-split.md) | Legacy — replaced by the SYSTEM_PROMPT's infographic vocabulary section. |
| [references/style-resolution.md](references/style-resolution.md) | Legacy — replaced by `style-library.md` (which includes auto-pick matrix). |
| [references/model-picker.md](references/model-picker.md) | Step 3 — model auto-pick decision tree, capability matrix |
| [references/platform-presets.md](references/platform-presets.md) | Step 8 — caption rules per platform, hashtag policy, char limits |
| [references/batch-execute.md](references/batch-execute.md) | Step 6-7 — how batch runner works, manifest format, retry semantics, failure handling |
| [references/troubleshoot.md](references/troubleshoot.md) | When generation fails or style drifts across slides |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: 8-slide LinkedIn carousel from a research brief (Flux 2 Pro), 6-slide Instagram with embedded text (Ideogram 3 Quality), 10-slide TikTok with user-provided reference image (Nano Banana Pro).

## `--animate` — one-command carousel → animated reel (v2.19.0+)

With `--animate`, the skill continues past the static deck into a stitched animated reel WITHOUT any manual plan-file assembly:

1. **Slides render first** (steps above) → N slide PNGs + the slide-content summaries already in hand.

2. **Spawn ONE Agent with the canonical video SYSTEM_PROMPT** at [`../common/video-prompt-library/system-prompt.md`](../../common/video-prompt-library/system-prompt.md). Fill `buildUserMessage(opts)` with:
   - Mode `i2v`, N shots, aspect `9:16`, 4s per shot, target model (default `veo-3-1-fast`).
   - Per shot: the slide PNG path as `image_url` + a one-line summary of the slide's overlay text (so the LLM can pick a motion that fits the slide's rhetoric — it must NOT re-describe the text in the output prompt).
   - The character-identity marker (8–15 words) when a character ref was used.
   - Suggested micro-gesture variety across the deck (head turn / hand lift / finger tap / nod / blink — one distinct verb per shot).
   The Agent returns `{"shots":[{"index":N,"prompt":"...","kwargs":{...}}]}` — all N shots in ONE call. The SYSTEM_PROMPT enforces the full i2v discipline (2-sentence cap, 80-word cap, single motion verb, global lock verbatim, `lock_first_last` + `negative_prompt` kwargs for overlay-heavy frames, no punitive labels, subject-anchored contact motion).

3. **Build the reel plan mechanically** — each returned shot becomes a `skills.reel.plan.v1` item (label `shot-NN-<slug>`; labels MUST start with `shot-` or the reel CLI skips them). Write to `<output_dir>/reel-plan.json` (single canonical path, overwrite).

4. **Run the reel CLI**:
   ```
   python3 -m common.runners.cli.reel --plan-file <output_dir>/reel-plan.json --yes            # stitched final.mp4
   python3 -m common.runners.cli.reel --plan-file <output_dir>/reel-plan.json --yes --skip-stitch  # N independent clips (IG carousel-as-reels)
   ```
   Concat order follows plan index (fixed v2.18.0) — parallel finish order can't scramble the sequence.

5. **Verify against the source slides** — spot-check first frames of each shot mp4 against the slide PNGs (index ↔ content match). If a shot fails on Veo's safety filter (`no videos`), soften the PROMPT body per SYSTEM_PROMPT rule 10 and `--resume`.

Flags: `--animate` (off by default) · `--animate-duration 4|8` (default 4) · `--animate-provider veo-3-1-fast|veo-3-1|kling-3|runway-gen-4` (default veo-3-1-fast; pick non-Fast Veo when `last_frame` drift-lock matters more than cost) · `--animate-stitch on|off` (default on).

Cost (Veo 3.1 fast, $0.15/s): 3×4s = $1.80 · 5×4s = $3.00 · 8×4s = $4.80. Veo 3.1 standard ($0.40/s) is ~2.7× — use for publication-grade text stability (`last_frame` supported).

Cost (Kling 3 / Runway Gen-4 / Sora 2) — see `common/runners/cost.py` for per-provider pricing; all four accept `image_url` for image-to-video.

## CONSTRAINTS

- **ONE LLM call, not per-slide.** The carousel-builder SYSTEM_PROMPT is designed to receive all N prompts in a single response. Per-slide subagent calls break visual consistency and miss the "deck as cohesive sequence" framing. Tried and rejected in earlier versions.

- **1–3 sentence prompts only.** Image models perform best with concise prompts. 250+ word spec-dumps with "12% frame height" / "1px stroke" / percentages produce magazine-with-overlay output. The SYSTEM_PROMPT enforces this.

- **Style description = VOCABULARY + treatment, not a fixed recurring scene.** A style entry like "BIOTECH / ORGANIC — deep teal background, neural pathways, cyan glow" describes the visual language. Avoid baking literal scenes like "library reading room at dusk" into the style — every slide will render the same setting.

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

- **Text-mode embedded ONLY with text-friendly models.** Ideogram 3 / gpt-image-2 / Nano Banana 2 — others get a warning + automatic fallback to overlay mode. List enforced in `references/model-picker.md`.

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

This skill is downstream of `research-brief` (consumes the brief) and upstream of `post-publisher`, which reads this skill's output directory — slides plus `captions.md` — and sends it to Instagram / Threads / TikTok / LinkedIn. When the user says "и выложи" after a deck is generated, hand the output directory to `post-publisher`; it dry-runs by default, so nothing goes out without a confirmation.
