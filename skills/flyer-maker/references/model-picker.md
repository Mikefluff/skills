# Model picker — flyer-maker

> Per-unit prices below are illustrative; the canonical table is
> [`common/references/model-pricing.md`](../../../common/references/model-pricing.md),
> generated from `common/runners/cost.py` — the same table that estimates your bill.
> Batch figures here are that unit price times the item count.

Decision tree for `--model auto` + capability matrix.

---

## Decision tree

```
1. --photo provided?
     yes:
        Photo is a person's face AND identity preservation critical (named speaker)?
           yes → nano-banana-pro  (best identity preserve)
           no  → continue
        Photo is a brand asset (logo / palette / texture ref)?
           yes → flux-2-pro or seedream-4.5  (best style/palette transfer)
        Photo is a generic theme image (mood-board / environmental)?
           → flux-2-pro
        Heavy embedded text required AND photo?
           → gpt-image-2  (best text-with-multi-ref balance)
        Default for photo + flyer text:
           → nano-banana-pro
     no: continue

2. Embedded text density (the flyer always has SOME embedded text — title + maybe details)?
     Brand-clean typography needed AND no photo?
        → ideogram-3-quality  (cleanest text rendering, brand-style transfer)
     Latin AND non-Latin scripts mixed (CJK / Cyrillic) AND no photo?
        → gpt-image-2  (best multilingual text)
     Standard Latin text only AND no photo?
        → ideogram-3-quality  OR  imagen-4-ultra
     Photoreal style required AND no photo?
        → imagen-4-ultra

3. Available env vars?
     drop candidates whose env vars aren't set
     fallback: flux-2-pro (BFL_API_KEY) or replicate-image router
```

### Default pick

`auto` with default settings (no photo, no special requirements):

- **First choice**: `ideogram-3-quality` if `IDEOGRAM_API_KEY` is set — cleanest text rendering.
- **Second**: `gpt-image-2` if `OPENAI_API_KEY` is set — best balance, supports CJK + Latin.
- **Third**: `flux-2-pro` if `BFL_API_KEY` is set — good style transfer, decent text.
- **Fallback**: `replicate-image` router.

With `--photo`:

- **First choice**: `nano-banana-pro` (identity preserve) if `GEMINI_API_KEY` set.
- **Second**: `gpt-image-2` if `OPENAI_API_KEY` set (16-ref capable, text-friendly).
- **Third**: `flux-kontext` or `flux-2-pro` if `BFL_API_KEY` set.

---

## Capability matrix

Updated 2026-05.

| Slug | Provider | Text-in-image | Multi-ref | Identity preserve | Style transfer | Cost/flyer | Latency |
|---|---|---|---|---|---|---|---|
| `ideogram-3-quality` | Ideogram | excellent (cleanest) | yes (1 style-ref) | medium | medium | $0.08 | 6-12s |
| `ideogram-3` | Ideogram | excellent | yes (1 style-ref) | medium | medium | $0.04 | 4-8s |
| `gpt-image-2` | OpenAI | excellent (Latin + CJK) | yes (up to 16) | medium | medium | $0.05-0.10 | 6-10s |
| `nano-banana-pro` | Google | good | yes (8) | excellent | good | $0.05 | 4-8s |
| `imagen-4-ultra` | Google | good | limited (1) | good | good | $0.06 | 5-9s |
| `imagen-4` | Google | fair | no | fair | fair | $0.04 | 4-7s |
| `flux-2-pro` | BFL | fair | yes (4) | good | excellent | $0.06 | 5-12s |
| `flux-kontext` | BFL | fair | yes (1, edit-mode) | good | excellent for edits | $0.05 | 5-10s |
| `flux-1-1-pro` | BFL | fair | no | good | excellent | $0.04 | 4-8s |
| `seedream-4.5` (via fal) | ByteDance | fair | yes (4) | good | excellent for photoreal | $0.04 (fal router) | 6-12s |
| `flux-schnell` | BFL | poor | no | fair | fair | $0.003 | 1-3s |

### Cost preview by aspect count

| Model | 3 aspects (default) | 5 aspects (full set) |
|---|---|---|
| flux-schnell | $0.009 | $0.015 |
| ideogram-3 | $0.12 | $0.20 |
| flux-1-1-pro | $0.12 | $0.20 |
| nano-banana-pro | $0.15 | $0.25 |
| gpt-image-2 (medium) | $0.15 | $0.25 |
| imagen-4 | $0.12 | $0.20 |
| flux-2-pro | $0.18 | $0.30 |
| imagen-4-ultra | $0.18 | $0.30 |
| ideogram-3-quality | $0.24 | $0.40 |
| gpt-image-2 (high) | $0.30 | $0.50 |

All under the default `SKILLS_CAROUSEL_BUDGET=$1.50` (flyer-maker uses the carousel budget since the modality is shared). No confirmation prompt under that.

---

## Photo handling caveats

### Nano Banana Pro

- Best identity preserve (face / pose / outfit) in the industry.
- Sometimes pulls toward photographic realism even when the style anchor is illustrated. Use `--style-mod "stylized illustrated interpretation, not photographic"` to nudge.
- Handles text-in-image at "good" level — fine for headlines, can wobble on long details.

### gpt-image-2

- Up to 16 refs.
- Best text rendering when you also need a photo embedded — sweet spot for flyer-with-speaker.
- Sometimes loses identity sharpness vs. NBP — face becomes "a person who looks like" rather than "this exact person".

### Flux Kontext

- Best when you want to EDIT an existing image (e.g., "take this venue photo and add the event title overlay"). Different from text-to-image-with-ref.
- Less ideal when you want to compose a NEW image with the photo as a sub-element.

### Flux 2 Pro / Seedream 4.5

- Excellent for palette + texture + composition transfer.
- Weaker on identity preserve — face may shift.

### Imagen 4 Ultra

- Photoreal style very strong.
- Limited multi-ref (1 image).
- Decent text rendering, not as clean as Ideogram.

---

## Provider not registered / env var missing

If `--model <slug>` is passed but the env var is not set:

1. Print clear message: `set $X to use $Y`.
2. Fall back to `--prompts-only` mode.
3. Exit non-zero.

If `--model auto` and no candidate has env vars set:

1. Suggest setting `OPENAI_API_KEY` or `GEMINI_API_KEY` as the cheapest entry path.
2. Fall back to `--prompts-only`.
3. Exit non-zero.

---

## When to override `auto`

- **Brand-style flyer (existing brand visual identity)**: force `--model ideogram-3-quality` for cleanest text + reliable typography.
- **Speaker headshot critical**: force `--model nano-banana-pro` regardless of text needs.
- **RU / Cyrillic text**: force `--model gpt-image-2` (best non-Latin support).
- **Iterating quickly to validate copy / composition**: force `--model flux-schnell` for cheap fast preview, then re-run final with `--model ideogram-3-quality`.
- **A4 print preview**: force `--model imagen-4-ultra` for photoreal layout (handles dense detail at 1240×1754).
- **Editing existing event poster**: use `image-prompt --execute --model flux-kontext --image-url <existing.png>` directly — `flyer-maker` is for creating from scratch.
