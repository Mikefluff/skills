# Model picker

> Per-unit prices below are illustrative; the canonical table is
> [`common/references/model-pricing.md`](../../common/references/model-pricing.md),
> generated from `common/runners/cost.py` — the same table that estimates your bill.
> Batch figures here are that unit price times the item count.

Decision tree — given user intent, pick the right model and load the right model-file. Use this before writing any prompt.

---

## By intent → model

- **Editorial / fashion / "vibes"** → Midjourney v7 → [`models/midjourney.md`](models/midjourney.md)
- **Photoreal portrait / product (max detail)** → Flux 2 Pro or Imagen 4 Ultra → [`models/flux.md`](models/flux.md) / [`models/google.md`](models/google.md)
- **"No AI look" / grainy / imperfect** → Krea-1 (or Flux Krea [dev]) → [`models/flux.md`](models/flux.md)
- **Text-in-image** (poster, book cover, multi-line copy) → Ideogram 3 Quality or Nano Banana Pro → [`models/ideogram-recraft.md`](models/ideogram-recraft.md) / [`models/google.md`](models/google.md) + load [`text-in-image.md`](text-in-image.md)
- **Edit existing image** (single change, character preserved) → Flux Kontext or Nano Banana Pro or gpt-image-2 → load [`editing-prompting.md`](editing-prompting.md)
- **Character consistency across multiple images** → Nano Banana Pro (up to 5 people) / gpt-image-2 (up to 16 refs) / Flux Kontext / Seedream 4.5 (weighted) → load [`editing-prompting.md`](editing-prompting.md)
- **Multi-image composition** (character + product + style mix) → Seedream 4.5 weighted refs or Flux 2 Pro multi-ref → load [`editing-prompting.md`](editing-prompting.md)
- **Vector / SVG / flat icon** → Recraft V3 → [`models/ideogram-recraft.md`](models/ideogram-recraft.md)
- **Fast cheap iteration** → Flux Schnell, Imagen 4 Fast, Ideogram 3 Turbo, SDXL Lightning, Seedream Turbo
- **Self-host / open-weights** → Flux 2 [dev], SD 3.5 Large, Qwen-Image 2.0 (Apache-2.0), HiDream-O1 (MIT) → [`models/open-source.md`](models/open-source.md)
- **Chinese / Japanese / multilingual text rendering** → Qwen-Image 2.0 → [`models/open-source.md`](models/open-source.md)
- **Total budget control + LoRA / ControlNet ecosystem** → SDXL → [`models/open-source.md`](models/open-source.md)

---

## By capability matrix

| Model | Photoreal | Text-in-image | Edit | Multi-ref | Character lock | Multilingual | Open-weights |
|---|---|---|---|---|---|---|---|
| Midjourney v7 | ✓ | partial (≤5 words) | partial (`--oref`) | partial | ✓ (`--oref`) | no | no |
| Flux 2 Pro | ✓ | partial (~60%) | ✓ (Kontext) | ✓ (≤10) | ✓ | partial | partial (dev) |
| Flux Kontext | partial | partial | ✓ | partial | ✓ | partial | no |
| Krea-1 / Flux Krea | partial | no | partial | no | no | no | partial (dev) |
| Imagen 4 Ultra | ✓ | ✓ | partial | partial | partial | ✓ | no |
| Nano Banana Pro | ✓ | ✓ | ✓ | ✓ (14 inputs) | ✓ (5 people) | ✓ | no |
| gpt-image-2 | ✓ | ✓ | ✓ | ✓ (≤16) | ✓ | ✓ | no |
| Ideogram 3 Quality | ✓ | ✓ | partial | partial | partial | partial | no |
| Recraft V3 | partial | ✓ | partial | no | no | partial | no |
| Seedream 4.5 | ✓ | partial | ✓ | ✓ (weighted) | ✓ | partial | no |
| SDXL | partial | no | ✓ (i2i) | ✓ (ControlNet) | ✓ (LoRA) | no | ✓ |
| SD 3.5 Large | ✓ | partial | ✓ | partial | partial | partial | ✓ |
| Qwen-Image 2.0 | ✓ | ✓ | partial | partial | partial | ✓ (CJK leader) | ✓ (Apache-2.0) |
| HiDream-O1 | ✓ | partial | partial | no | no | partial | ✓ (MIT) |

---

## Quick-pick cheat sheet

```
If you just want one good model and one fallback:
  - Midjourney v7      → editorial / vibes
  - Flux 2 Pro         → photoreal portrait + product
  - Ideogram 3 Quality → anything with text
That covers ~80% of needs.
```
