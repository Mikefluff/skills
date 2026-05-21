---
name: image-prompt
description: "Write prompts for 14+ frontier AI image generators (Midjourney v7, Flux 2 / Flux Kontext, Imagen 4 Ultra, Nano Banana Pro / Gemini 3 Image, gpt-image-2, Ideogram 3, Recraft V3, Seedream 4.5, Qwen-Image, HiDream-O1, Krea-1, SD 3.5, SDXL). Modes: text-to-image, edit (preserve/change), multi-reference, text-in-image. 6-part formula + per-model deltas, character/identity locks, weighted multi-ref. Use when the user says 'prompt for an image', 'Midjourney prompt', 'edit this image with Kontext', 'character consistency across covers', 'poster with multi-line text'."
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
Generate a tight, model-aware prompt for AI image generation. Output: one well-formed prompt string (optionally + a negativePrompt, reference list, or edit instruction). This skill does NOT call the image model — it produces the text you paste into Midjourney / Flux / Imagen / Nano Banana / gpt-image-2 / Ideogram / Recraft / Seedream / Qwen-Image / HiDream / Krea / SD.

Use when the user wants an image for a specific scene, post cover, product mock, portrait, hero illustration, abstract background, OR wants to edit an existing image with character preserved, OR wants a multi-reference composite (character + style + palette), OR wants legible text inside an image. The skill picks the right model + mode + vocabulary that produces sharp, coherent output instead of generic "AI image".

This skill does NOT:
- generate the image itself (that's the model)
- design layouts or multi-frame compositions (use a design tool)
- write video prompts (use `video-prompt`)
</objective>

## ROLE

Read the request → identify subject + intent (generate / edit / multi-ref / text-heavy) → pick target model from `references/model-picker.md` → assemble the prompt using the 6-part formula plus the conditional 7th block (references) → add lighting + camera + texture hints → return the prompt + optional negative or reference list.

## PIPELINE

1. **Clarify if needed.** If the user gave only a topic ("cover for a post about cold-emails"), pick a sensible default subject ("close-up of an empty mailbox at dawn") and check before committing. If they gave a full scene, skip.

2. **Mode select.** Pick one:
   - `t2i` — text-to-image (default).
   - `edit` — modify an existing image; preserve identity / lighting / pose, change one thing.
   - `multi-ref` — compose from multiple reference images (character + product + style).
   - `text-heavy` — legible text is the subject (poster, book cover, signage).

3. **Pick model.** Default by intent — see `references/model-picker.md`:
   - Editorial / fashion / "vibes" → Midjourney v7
   - Photoreal portrait / product → Flux 2 Pro or Imagen 4 Ultra
   - Text-heavy → Ideogram 3 Quality or Nano Banana Pro
   - Edit → Flux Kontext or Nano Banana Pro or gpt-image-2
   - Multi-ref composite → Seedream 4.5 (weighted roles) or Flux 2 Pro or gpt-image-2
   - Self-host / open-weights → Flux 2 [dev], SD 3.5, Qwen-Image 2.0 (CJK), HiDream-O1
   - Cheap iteration → Flux Schnell / Imagen 4 Fast / Ideogram 3 Turbo

4. **Build the prompt** — see `references/prompt-formula.md`:
   ```
   {subject + action} + {setting} + {style} + {lighting} + {camera/lens} + {texture/realism}
   ```
   When mode is `edit` or `multi-ref`, the 7th conditional block fires — see `references/editing-prompting.md`.

5. **Load model-specific syntax** from `references/models/<vendor>.md` and apply (flags / NL phrasing / weighted refs / preserve-change grammar).

6. **Add negative prompt** if useful (mainly SDXL / Flux). Standard set: `text, watermark, logo, distorted anatomy, extra fingers, blurry, low resolution`.

7. **Output.** Return:
   - The prompt as one fence-block (paste-ready)
   - Optional negative as a second fence-block
   - For multi-ref: an annotated list of refs with roles + weights
   - 1-line note: which model + mode + key conventions applied
   - If `--variants N` requested — N alternatives with different style / lighting / camera

## MODES

- `image-prompt <topic-or-scene>` — generate default prompt (intent-routed model)
- `image-prompt <scene> --model <name>` — target a specific model. Valid: `midjourney-v7`, `flux-2-pro`, `flux-2-dev`, `flux-1-1-pro-ultra`, `flux-kontext`, `flux-schnell`, `flux-krea`, `imagen-4`, `imagen-4-ultra`, `imagen-4-fast`, `nano-banana-pro`, `gpt-image-2`, `ideogram-3`, `recraft-v3`, `seedream-4-5`, `qwen-image`, `hidream-o1`, `krea-1`, `sd-3-5`, `sdxl`
- `image-prompt <scene> --style <style>` — force a style (`photorealistic`, `editorial`, `3d-render`, `illustration`, `product-shot`, `cinematic`, `minimalist`, `no-ai-look`)
- `image-prompt <scene> --edit` — edit mode; expects a source image (URL or path). Generates preserve/change instruction.
- `image-prompt <scene> --reference <path-or-url>[@<role>:<weight>]` — attach a reference. Repeatable. Roles: `character`, `style`, `palette`, `layout`. Weights 0-1. Triggers multi-ref mode.
- `image-prompt <scene> --variants 3` — 3 alternatives with different style or lighting
- `image-prompt <scene> --improve` — user provides a weak prompt + the bad output description; skill rewrites

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/model-picker.md](references/model-picker.md) | Always at step 3 — intent → model → which model-file to load |
| [references/prompt-formula.md](references/prompt-formula.md) | When building any prompt — 6-part formula + per-part vocabularies |
| [references/lighting-vocabulary.md](references/lighting-vocabulary.md) | When picking lighting hints — portrait / scene / quality-of-light dictionaries |
| [references/camera-vocabulary.md](references/camera-vocabulary.md) | When the image should look photographic — lens/sensor/quality-tag dictionary |
| [references/editing-prompting.md](references/editing-prompting.md) | Mode `edit` or `multi-ref` — preserve/change grammar, identity locks, weighted refs |
| [references/text-in-image.md](references/text-in-image.md) | Mode `text-heavy` — per-model rules for legible text + multilingual |
| [references/models/midjourney.md](references/models/midjourney.md) | Midjourney v7 (and v8 preview) — `--sref`, `--oref`, `--raw`, `--ar`, `--s`, `--c`, `--no`, `--p`, `--w` |
| [references/models/flux.md](references/models/flux.md) | Flux 2 Pro/Dev, 1.1 Pro Ultra (Raw), Kontext, Schnell, Krea |
| [references/models/google.md](references/models/google.md) | Imagen 4 / 4 Ultra / 4 Fast + Nano Banana Pro (Gemini 3 Pro Image) |
| [references/models/openai.md](references/models/openai.md) | gpt-image-2 (DALL-E 3 retirement note) |
| [references/models/ideogram-recraft.md](references/models/ideogram-recraft.md) | Ideogram 3 Turbo/Default/Quality + Recraft V3 (SVG) |
| [references/models/bytedance-seedream.md](references/models/bytedance-seedream.md) | Seedream 4.5 / 5.0 (weighted multi-ref) |
| [references/models/open-source.md](references/models/open-source.md) | SD 3.5 + SDXL legacy + Qwen-Image 2.0 + HiDream-O1 |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — calibration pairs covering portrait, product, scene, abstract, illustration, text-in-image (Ideogram 3), edit (Flux Kontext), multi-reference composite (Seedream 4.5), open-weights (Qwen-Image).

## CONSTRAINTS

- **Don't name real people.** Use role descriptors ("a confident business person") not real names.
- **Don't promise reliable text > 1 short phrase outside text-tier models.** Reliable text: Ideogram 3 Quality, Nano Banana Pro, Imagen 4 Ultra, gpt-image-2, Qwen-Image. Avoid > 5 words in Midjourney / Flux 2 Pro (≈60%); avoid entirely in SD 3.5 / SDXL. For exact typography: render in a design tool, not the generator.
- **For character consistency across multiple images** — use a model that supports identity locks: Midjourney v7 (`--oref`), Flux Kontext, Nano Banana Pro (up to 5 people), gpt-image-2 (16 refs), Seedream 4.5 (Character weight 1.0).
- **Don't re-describe the ref's appearance in the prompt.** When `--reference` is attached as Character, the prompt should describe wardrobe / action / expression / environment — NOT face / hair / body. Re-describing overrides the ref and causes drift.
- **Don't mix Midjourney `--` flags into NL-only models.** Imagen / gpt-image-2 / Nano Banana Pro / Flux NL prompts ignore (or break on) `--ar`, `--s`, `--style raw`, etc. Use API params or NL phrasing instead.
- **SD 3.5 weight syntax `(word:1.3)` is a no-op.** Despite accepting the syntax, SD 3.5 ignores weights. Use keyword priority order. Weights DO work on SDXL / SD 1.5.
- **One subject per prompt** unless explicitly multi-subject. The model can't render "a cat, a dog, a horse, and a fox" cleanly.
- **Specific lighting beats abstract.** "Soft directional key light from upper left" > "good lighting".
- **Don't bury the subject.** First 12-15 words anchor the model.
- **Kontext deviation**: in edit mode with Flux Kontext / Nano Banana Pro / gpt-image-2, the prompt is JUST the change instruction — don't restate subject / setting / style from the source image.

## INVOCATION HINTS

When the user says any of:
- "generate / write / make me a prompt for an image / cover / illustration / artwork"
- "Midjourney / Flux / Imagen / Nano Banana / gpt-image-2 / Ideogram / Seedream / Recraft / Qwen-Image / SD prompt for..."
- "edit this image", "change the dress color, keep the face", "preserve identity"
- "character consistency across covers / chapters"
- "multi-reference", "composite from these images"
- "poster / book cover / signage with legible text"
- "cover image / hero image / thumbnail / illustration prompt"
- "product shot / portrait / scene prompt"
- "improve this image prompt"

RU triggers (use the skill when the user writes any of):
- «промпт для Midjourney / Flux / Imagen / Nano Banana / gpt-image-2 / Ideogram / Seedream / Recraft / Qwen / HiDream / SD»
- «обложка для статьи / поста / лонгрида»
- «отредактируй картинку», «поменяй цвет платья, оставь лицо», «сохрани идентичность»
- «единый персонаж на всех обложках», «character consistency»
- «постер с текстом», «обложка книги с подзаголовком»
- «hero-картинка для лендинга»
- «улучшить промпт для изображения»
- «multi-reference композит», «комбинация рефов»

The prompt itself is usually written in English (most models parse EN best). Only when the user explicitly asks for an RU-language prompt should the body be RU. RU terminology mapping for lighting + camera vocabulary lives in [`references/lighting-vocabulary.md`](references/lighting-vocabulary.md) (section `RU терминология`).

For multilingual text rendering INSIDE the image (Chinese, Japanese, mixed scripts), use Qwen-Image 2.0 — see [`references/text-in-image.md`](references/text-in-image.md).

Use this skill. For video — use `video-prompt` (different vocabulary, has temporal flow + camera movement, not single-frame lighting).
