---
name: image-prompt
description: "Write prompts for AI image generators (Midjourney, DALL-E, Flux, Nano Banana, Stable Diffusion). Subject → setting → style → lighting → camera/lens → texture/realism, plus per-model deltas and negative prompts. Use when the user says 'prompt for an image', 'generate a Midjourney prompt', 'cover image for this post', 'product shot prompt'."
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
Generate a tight, model-aware prompt for AI image generation. Output: one well-formed prompt string (optionally + a negativePrompt). This skill does NOT call the image model — it produces the text you paste into Midjourney / DALL-E / Flux / Nano Banana / SD WebUI.

Use when the user wants an image for a specific scene, post cover, product mock, portrait, hero illustration, or abstract background. The skill picks the right vocabulary for the target model and bakes in lighting, camera, and texture hints that produce sharp, coherent output instead of generic "AI image".

This skill does NOT:
- generate the image itself (that's the model)
- design layouts or multi-frame compositions (use a design tool)
- write video prompts (use `video-prompt`)
</objective>

## ROLE

Read the request → identify subject, scene, intended style → pick a target model (or model-agnostic) → assemble the prompt using the 6-part formula → add lighting + camera + texture hints → return the prompt + optional negative.

## PIPELINE

1. **Clarify if needed.** If the user gave only a topic ("generate a cover for a post about cold-emails"), pick a sensible default subject ("close-up of an empty mailbox at dawn") and check with the user before committing. If they gave a full scene, skip clarification.

2. **Pick model.** Default: Midjourney v6 (most general-purpose). If user names a model — use its specific vocabulary (see `references/model-specifics.md`).

3. **Build the prompt using the formula** — see `references/prompt-formula.md`:
   ```
   {subject + action} + {setting} + {style} + {lighting} + {camera/lens} + {texture/realism}
   ```

4. **Add negative prompt** (optional, for photorealistic/editorial styles) — see `references/model-specifics.md`. Standard set: `text, watermark, logo, distorted anatomy, extra fingers, blurry, low resolution`. SD-1.5/SDXL benefit most.

5. **Output.** Return:
   - The prompt as one fence-block (paste-ready)
   - Optional negative as a second fence-block
   - 1-line note: which model conventions were applied
   - If multiple variants useful — offer 2-3 alternatives with different style or lighting

## MODES

- `image-prompt <topic-or-scene>` — generate default Midjourney v6 prompt
- `image-prompt <scene> --model <name>` — target a specific model (`midjourney-v6`, `dalle-3`, `flux-pro`, `nano-banana`, `sdxl`)
- `image-prompt <scene> --style <style>` — force a style (`photorealistic`, `editorial`, `3d-render`, `illustration`, `product-shot`, `cinematic`, `minimalist`)
- `image-prompt <scene> --variants 3` — return 3 alternatives with different style or lighting
- `image-prompt <scene> --improve` — user provides a weak prompt + the model output that was bad; skill rewrites the prompt

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/prompt-formula.md](references/prompt-formula.md) | When building any prompt — the 6-part formula + per-part vocabularies |
| [references/lighting-vocabulary.md](references/lighting-vocabulary.md) | When picking lighting hints — portrait / scene / quality-of-light dictionaries |
| [references/camera-vocabulary.md](references/camera-vocabulary.md) | When the image should look photographic — lens/sensor/quality-tag dictionary |
| [references/model-specifics.md](references/model-specifics.md) | When the user names a specific model — per-model deltas (MJ params, SD weights, DALL-E phrasing, Nano Banana hints, Flux strengths) |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 5 calibration pairs (weak prompt → strong prompt) covering portrait, product, scene, abstract, and illustration.

## CONSTRAINTS

- **Don't name real people.** Use role descriptors ("a confident business person") not real names.
- **Don't promise text inside the image.** Most models butcher text. If text IS the subject, flag this to the user and suggest doing the text overlay in a design tool.
- **Don't use the model's parameter syntax in DALL-E or natural-language prompts.** Midjourney uses `--ar 16:9 --s 250`; DALL-E/Flux/Nano-Banana use natural language ("widescreen 16:9").
- **One subject per prompt** unless explicitly multi-subject. The model can't render "a cat, a dog, a horse, and a fox" cleanly.
- **Specific lighting beats abstract.** "Soft directional key light from upper left" > "good lighting". "Neon signs casting magenta glow" > "moody lighting".
- **Don't bury the subject.** First 12-15 words define what the model anchors on.

## INVOCATION HINTS

When the user says any of:
- "generate / write / make me a prompt for an image / cover / illustration / artwork"
- "Midjourney / DALL-E / Flux / Nano Banana / Stable Diffusion prompt for..."
- "cover image / hero image / thumbnail / illustration prompt"
- "product shot / portrait / scene prompt"
- "improve this image prompt"

Use this skill. For video — use `video-prompt` (different vocabulary, has temporal flow + camera movement, not single-frame lighting).
