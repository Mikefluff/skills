# Open-source models

Self-hosted / open-weights generators. SD 3.5 is the current workhorse; Qwen-Image for multilingual typography; HiDream-O1 for pixel-native fidelity.

---

## Stable Diffusion 3.5 (Large / Large Turbo / Medium)

**Strengths**: open weights, strong style range, large community + LoRA ecosystem; runs locally; commercial-friendly license.
**Weaknesses**: default outputs less polished than Flux / Imagen; tiers `Large` / `Large Turbo` / `Medium` differ in detail and speed.

### Critical caveat

The classic weight syntax `(word:1.3)` is a **no-op** in SD 3.5 — the model parses it without erroring but ignores the multiplier. Weighted-token emphasis only works on SDXL and SD 1.5. In SD 3.5, get emphasis via word order, repetition, and explicit description.

### Syntax

- Natural language OR comma-separated keyword style — both work.
- CFG (guidance scale): 4-7. Below 3.5 = washed; above 8 = overcooked.
- Steps: 28-50 for `Large`; 4-8 for `Large Turbo`.
- Negative prompt field supported.

### Prompt template

```
{subject + action + context}, {style tags}, {lighting}, {camera}, {texture}, {quality tags}
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen, editorial photo, golden hour key light from upper-left window, soft rim light on hair, 85mm lens, f/1.8, full-frame DSLR, natural skin texture, visible pores, sharp focus on eyes, 8K, ultra-realistic, photorealistic, cinematic color grading
```

Negative:
```
text, watermark, distorted anatomy, extra fingers, blurry, low resolution, plastic skin, oversaturated, oversmooth
```

### Notes

- Don't bother with `(token:1.3)` — silently ignored. Re-state the concept instead.
- `Large Turbo` for iteration, `Large` for finals, `Medium` for low-VRAM hosts.
- LoRA ecosystem is still catching up to SDXL — many style LoRAs are SDXL-only.

---

## SDXL + Lightning / Turbo (legacy)

- Still useful for LoRA-heavy and ControlNet workflows — the ecosystem is the deepest in open-source.
- Weight syntax `(word:1.3)` and `[word]` DOES work here, unlike SD 3.5.
- Lightning / Turbo variants are 1-4 step; great for real-time iteration.
- SD 3.5 supersedes for general-purpose generation — switch if you don't need a specific SDXL LoRA.
- Pose / depth / canny ControlNets are mature here and not yet matched on SD 3.5.

---

## Qwen-Image 2.0 (7B, Feb 2026) + Qwen-Image-2512 (20B, Jan 2026)

**Strengths**: Apache-2.0 license; native 2K output; paragraph-level multilingual typography — best in class for Chinese + English text in the same image; 1k-token instructions handled without truncation.
**Weaknesses**: photoreal portraits weaker than Flux / Imagen / gpt-image-2; community LoRAs scarce.

### Syntax

- Natural language, long instructions OK (up to ~1k tokens).
- Quote in-image text exactly, including Chinese characters.
- 7B (Qwen-Image 2.0) for speed, 20B (Qwen-Image-2512) for fidelity.

### Prompt template

```
{subject + action + context}, {style}, {lighting}, {camera}, {texture}.
In-image text: top reads "{exact line in language A}", bottom reads "{exact line in language B}".
```

### Example (multilingual text)

```
A confident business person leaning on marble countertop in a sunlit Brooklyn loft kitchen, editorial photo, soft window key light, 85mm f/1.8, natural skin texture, holding a bilingual menu card facing the camera, portrait 4:5.
In-image text: top in bold serif reads "OPEN KITCHEN", below in Chinese reads "开放厨房 — 布鲁克林 — 2026".
```

### Notes

- Pick Qwen-Image-2512 (20B) when typography fidelity matters more than speed.
- Outperforms Ideogram on CJK + Latin mixed copy; on Latin-only, Ideogram still wins.

---

## HiDream-O1-Image (May 8, 2026)

**Strengths**: MIT license; pixel-native architecture (no VAE — sharper detail at high resolution); 2048×2048 native; unified gen + edit + personalization in one model; ranked #8 on Artificial Analysis Arena at release.
**Weaknesses**: newest in the lineup — small community, few LoRAs, few host integrations.

### Syntax

- Natural language. No VAE means no VAE-related artifacts (no waxy skin).
- Edit and personalization run in the same model — no model swap.

### Prompt template

```
{subject + action + context}, {style}, {lighting}, {camera}, {texture}, {aspect}
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen at golden hour, editorial photo, cinematic color grading, soft directional key light from upper-left window, 85mm f/1.8, natural skin texture with visible pores, sharp focus on eyes, portrait 4:5
```

### Notes

- Pixel-native sharpness shows in skin and fabric — no upscaler needed for 2K outputs.
- Unified model means personalization (LoRA-equivalent) lives in the base — check host docs for the personalization endpoint.
- <!-- TODO: confirm canonical host (replicate / fal / official) and personalization API field names once stable -->
