# Black Forest Labs (Flux) models

Photoreal-first generator family. Strong at text-in-image, hands, instruction-based editing.

---

## Flux 2 [pro]

**Strengths**: 32K-token prompt context, native 4MP output, up to 10 reference images per generation; best-in-Flux character + product consistency across a multi-shot set.
**Weaknesses**: slower per generation than Schnell or Krea; cost per image is the highest in the family.
**Execute via**: `--execute --model flux-2-pro` (env: `BFL_API_KEY`) — direct BFL API.

### Syntax

Natural language. Common params on Replicate / fal / BFL API:
- `aspect_ratio` — `1:1`, `16:9`, `9:16`, `4:5`, `2:3`, `3:2`
- `seed` — int, for reproducibility
- `output_quality` — 1-100
- `image_prompt` / `reference_images[]` — up to 10 URLs

### Prompt template

```
{subject + action + context}. {style tags}. {lighting}. {camera + lens}. {texture / realism notes}. {aspect-ratio cue in words}.
```

### Example

```
A confident business person leaning on a marble countertop, sunlit Brooklyn loft kitchen at golden hour. Editorial photo, cinematic color grading. Soft directional key light from upper-left window, gentle rim catching the hair. 85mm lens at f/1.8 on a full-frame DSLR, tack-sharp focus on the eyes, shallow depth of field. Natural skin texture with visible pores, realistic linen fabric. Portrait orientation, 4:5.
```

### Notes

- Use the long context — pack the full 6-part formula (subject, style, light, camera, texture, ratio) without compressing.
- Multi-ref is the killer feature for consistent character + product + interior across a set.
- **Flux 2 does NOT support negative prompts** (BFL official). Describe what you want positively — "sharp focus throughout" beats "no blur". This is the opposite of Flux 1.x / SDXL. Source: [docs.bfl.ml — FLUX.2 prompting guide](https://docs.bfl.ml/guides/prompting_guide_flux2).
- **Hex color anchoring** (Flux 2 specialty): say "vase in color #02EB3C" or "gradient from #02EB3C to #EDFA3C" — but always tie hex to a specific object. Loose hex codes drift.
- **Multi-ref input/output budget**: [pro] caps total input+output at 9 megapixels — at 1MP output you can attach up to 8 refs; at 2MP output, up to 7.
- **JSON-structured prompts** are supported on [pro] / [max] for production workflows (scene, subjects[], style, color_palette[], lighting, mood, camera{}).

---

## Flux 2 [dev]

**Strengths**: open weights, runs locally, same prompt grammar as Flux 2 [pro] at a lower quality ceiling.
**Weaknesses**: noticeably softer than [pro] at 4MP; needs more guidance on lighting.
**Execute via**: prompt-only — open weights, self-host. Workaround: `--execute --model flux-2-pro` (env: `BFL_API_KEY`) for the closed [pro] tier.

### Syntax

Same as Flux 2 [pro]. Hosts add `guidance_scale` (CFG-like) on some forks.

### Prompt template

```
{full natural-language scene}, {style}, {lighting}, {camera}, {texture}, {aspect}
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen, editorial photo, soft directional key light from window upper-left, 85mm lens f/1.8, full-frame DSLR, natural skin texture, visible pores, sharp focus on eyes, cinematic color grading, portrait 4:5
```

### Notes

- Best dev-tier option when you need self-hosted Flux output with commercial-friendly licensing.
- Pair with a Flux ControlNet for pose / depth control.

---

## Flux 1.1 [pro] Ultra (with Raw mode)

**Strengths**: "Raw mode" delivers a candid, less-AI aesthetic — grainier, more documentary; 4MP output; sharpest still-life and hand rendering at this tier.
**Weaknesses**: less stylized than v7 Midjourney; needs explicit style tags to avoid neutral look.
**Execute via**: `--execute --model flux-1-1-pro` (env: `BFL_API_KEY`) — direct BFL API.

### Syntax

- `raw: true` flag — switches to the candid aesthetic
- standard `aspect_ratio`, `seed`, `output_quality`

### Prompt template

```
{subject + action + context}, {style tags}, {lighting}, {camera}, {texture}, raw mode
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen, candid documentary photo, soft directional key light from window upper-left, 85mm lens f/1.8, full-frame DSLR, natural skin texture, visible pores, faint film grain, 4:5 — raw mode on
```

### Notes

- Use Raw when stock-photo / editorial / lifestyle "shot on a real camera" is the goal.
- Skip Raw for product shots — neutral mode is sharper.

---

## Flux Kontext [pro / max / dev]

**Strengths**: instruction-based edit on an input image — change ONLY what you describe, preserve the rest. Best-in-class for "swap shirt color, keep face and pose."
**Weaknesses**: not a from-scratch generator — needs an input image.
**Execute via**: `--execute --model flux-kontext` (env: `BFL_API_KEY`) — direct BFL API for [pro] / [max]; [dev] is open-weights self-host.

### Syntax

Input: original image + instruction text. Describe ONLY the change, not the full scene.
- `pro` — daily-driver edit tier
- `max` — highest fidelity, slowest
- `dev` — open-weights variant

### Prompt template

```
{verb the change}. Keep {what to preserve} unchanged.
```

### Example

Input: portrait of the business person from the running example.
```
Change the linen shirt from white to deep navy. Keep face, pose, lighting, and marble countertop unchanged.
```

### Notes

- DO NOT re-describe the full scene — Kontext interprets a full description as "redo everything."
- For multi-step edits, chain Kontext calls one change at a time.
- See docs.bfl.ml/guides/prompting_guide_kontext_i2i for the canonical instruction patterns.

---

## Flux Schnell

**Strengths**: fastest in the family (~1 sec on a host GPU); free tier on most platforms; great for iteration.
**Weaknesses**: lower fidelity than [pro] / Ultra; weaker at fine detail and text.
**Execute via**: `--execute --model flux-schnell` (env: `BFL_API_KEY`) — direct BFL API.

### Syntax

Same as Flux 2 [dev]. `num_inference_steps` typically 1-4.

### Prompt template

```
{compact natural-language scene}, {style}, {lighting}, {camera}, {texture}
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen, editorial photo, soft window light, 85mm f/1.8, natural skin texture, sharp focus, 4:5
```

### Notes

- Use for moodboarding / prompt iteration, then graduate to [pro] for finals.
- Keep prompts shorter than Flux 2 — Schnell ignores the long tail.

---

## FLUX.1 Krea [dev]

**Strengths**: tuned for the "no AI look" aesthetic — film grain, lens bloom, imperfect skin, slight color cast; the most photoreal-looking Flux for portraits and lifestyle.
**Weaknesses**: leans documentary — bad fit for clean product / studio renders.
**Execute via**: prompt-only — open weights, self-host. Workaround: `--execute --model flux-1-1-pro` (env: `BFL_API_KEY`) for closed BFL tier.

### Syntax

Same as Flux 2 [dev]. Krea responds strongly to film and analog vocabulary.

### Prompt template

```
{subject + action + context}, {analog / film style tags}, {natural lighting}, {camera}, {skin + grain texture}
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen, shot on Portra 400, slight film grain, mild lens bloom near the window, 85mm f/1.8, natural skin texture with visible pores and slight asymmetry, candid lifestyle photo, 4:5
```

### Notes

- Lean into analog vocab: "Portra 400", "Cinestill 800T", "Tri-X 400", "lens bloom", "halation."
- See bfl.ai/blog/flux-1-krea-dev for the canonical aesthetic targets.
- Pair with Flux 2 [pro] for set shots — Krea for the human moment, [pro] for the product hero.
