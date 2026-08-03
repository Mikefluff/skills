# Ideogram & Recraft models

Brand-design specialists. Ideogram for legible typography; Recraft for vector / icon / flat illustration.

---

## Ideogram 3 (Turbo / Default / Quality)

**Strengths**: best legible in-image text in the industry; clean brand-design output; multi-paragraph copy stays legible in the Quality tier; character consistency via the Ideogram Character feature.
**Weaknesses**: photoreal portraits weaker than Flux / Imagen / gpt-image-2; aesthetic less editorial than Midjourney.
**Execute via**: `--execute --model ideogram-3-turbo` / `ideogram-3` / `ideogram-3-quality` (env: `IDEOGRAM_API_KEY`) — Ideogram API.

### Syntax

- Natural language. Quote in-image text exactly with straight quotes.
- Tiers: `Turbo` (fast / cheap), `Default` (balanced), `Quality` (best text + detail).
- `aspect_ratio` param, `magic_prompt` toggle (auto-expansion — turn OFF for strict adherence).
- Style presets: `realistic`, `design`, `3d`, `anime`, `general`.

### Prompt template

```
{subject + action + context}, {style preset}. The {sign / poster / cover} reads "{exact copy line 1}" and below "{exact copy line 2}".
```

### Example (poster with multi-line copy)

```
A confident business person leaning on marble countertop in a sunlit Brooklyn loft kitchen, editorial photo style, holding a printed poster facing camera. The poster reads in bold serif "OPEN KITCHEN" at the top, and below in smaller sans-serif "Brooklyn — Est. 2026 — Prix Fixe $48". Soft directional window light, 85mm f/1.8, natural skin texture, portrait 4:5. Style: realistic.
```

### Notes

- Quote text verbatim with straight quotes — curly quotes confuse the renderer.
- Use Quality tier when copy is longer than one line.
- Turn `magic_prompt` OFF when you have a precise brief — otherwise it rewrites you.
- Ideogram Character: upload a reference face to lock identity across a campaign.

---

## Recraft V3

**Strengths**: vector-native — true SVG output for logos, icons, flat illustrations; brand-system design (palette + style lock across a set); cleanest flat-illustration model on the market.
**Weaknesses**: not for photoreal; not for complex scenes.
**Execute via**: prompt-only — no native Recraft adapter in v2.2. Workaround: `--execute --model fal-image --fal-model fal-ai/recraft-v3` (fal.ai mirror).

### Syntax

- Natural language + style selection.
- Output modes: `raster` (PNG) or `vector` (SVG).
- Style controls: `digital_illustration`, `vector_illustration`, `realistic_image`, plus user-trainable style profiles.
- `style_id` — reference a saved brand style for palette + stroke consistency.

### Prompt template

```
{subject as a noun}, {flat / vector / icon style descriptor}, {palette}, {composition cue}, {output mode: vector SVG}.
```

### Example (logo / icon)

```
A minimalist line-art icon of a chef's knife crossed with a wooden spoon, flat vector illustration, two-color palette (deep navy and warm cream), centered on a transparent background, no text, geometric balance, output as SVG vector.
```

### Notes

- For logo work, lock a `style_id` once, then generate the full set against it.
- Vector output is editable in Figma / Illustrator — no upscaling needed.
- Keep prompts noun-first and composition-explicit; Recraft is literal.
