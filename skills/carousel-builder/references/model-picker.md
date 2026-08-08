# Model picker — image provider for carousels

> Per-unit prices below are illustrative; the canonical table is
> [`common/references/model-pricing.md`](../../../common/references/model-pricing.md),
> generated from `common/runners/cost.py` — the same table that estimates your bill.
> Batch figures here are that unit price times the item count.

Decision tree + capability matrix for `--model auto`.

---

## Decision tree

```
1. --text-mode embedded?
     yes → text-friendly model only:
       (a) brand-colored / specific typography → ideogram-3-quality
       (b) Latin + CJK text required → gpt-image-2
       (c) photorealistic + text → nano-banana-pro (limited but works)
       Default: ideogram-3-quality
     no → continue

2. --style-ref provided?
     yes → multi-ref capable model:
       (a) ref is a person (identity preserve) → nano-banana-pro
       (b) ref is style/palette inspo → flux-2-pro
       (c) ref is a brand asset (logo, typography) → ideogram-3 or gpt-image-2
       Default: nano-banana-pro
     no → continue

3. style category from library frontmatter?
     - photoreal: true → flux-2-pro OR nano-banana-pro
     - illustration / 3D / abstract → nano-banana-pro OR flux-2-pro
     - heavy text + brand-clean → ideogram-3
     Default: flux-2-pro

4. Override if available providers are restricted by env vars.
   Drop any candidate whose env vars are not set; surface a warning.
   Final fallback: replicate (router) if REPLICATE_API_TOKEN is set.
```

---

## Capability matrix

Updated 2026-08.

| Slug | Provider | Modality | Text-in-image | Multi-ref | Identity preserve | Style transfer | Avg cost/slide | Latency |
|---|---|---|---|---|---|---|---|---|
| `gpt-image-2` | OpenAI | image | excellent (Latin + CJK) | yes (16) | medium | medium | $0.05-0.10 | 6-10s |
| `nano-banana-pro` | Google | image | good | yes (14) | excellent | good | $0.134 | 4-8s |
| `nano-banana-2` | Google | image | good | yes | good | good | $0.101 | 4-8s |
| `nano-banana-2-lite` | Google | image | fair | limited | fair | fair | $0.034 | 2-5s |
| `flux-2-pro` | BFL | image | fair | yes (4) | good | excellent | $0.06 | 5-12s |
| `flux-1-1-pro` | BFL | image | fair | no | good | excellent | $0.04 | 4-8s |
| `flux-kontext` | BFL | image | fair | yes (1, edit-mode) | good | excellent for edits | $0.05 | 5-10s |
| `flux-schnell` | BFL | image | poor | no | fair | fair | $0.003 | 1-3s |
| `ideogram-3` | Ideogram | image | excellent | yes (1, style-ref) | medium | medium | $0.04 | 4-8s |
| `ideogram-3-quality` | Ideogram | image | excellent (cleanest) | yes (1, style-ref) | medium | medium | $0.08 | 6-12s |
| `ideogram-3-turbo` | Ideogram | image | good | no | medium | medium | $0.02 | 2-5s |
| `fal-image` | fal.ai router | image | varies | varies | varies | varies | $0.03-0.10 | varies |
| `replicate-image` | Replicate router | image | varies | varies | varies | varies | $0.02-0.10 | varies |

---

## Choosing for the carousel use case (not single images)

Some models that look good for one-off generation FAIL on carousels because they drift across calls (different seed = different style fingerprint). For carousels:

- **Best style consistency across 8 calls**: Flux 2 Pro, Nano Banana Pro, Ideogram 3 Quality.
- **Worst consistency (style drifts noticeably across calls)**: Flux Schnell (fast but unstable), fal/replicate router (which sub-model spins up varies).

For Schnell / router-based models: pass `--seed <int>` if your --style-mod can include "seed N" (some providers honour this). Reduces drift but doesn't eliminate.

---

## Cost preview by carousel shape

8-slide carousel:

<!-- prices: batch=8 -->

| Model | Approx total |
|---|---|
| flux-schnell | $0.024 |
| ideogram-3-turbo | $0.16 |
| nano-banana-2-lite | $0.27 |
| flux-1-1-pro | $0.32 |
| ideogram-3 | $0.32 |
| gpt-image-2 (medium) | $0.40 |
| flux-2-pro | $0.48 |
| ideogram-3-quality | $0.64 |
| gpt-image-2 (high) | $0.80 |
| nano-banana-2 | $0.81 |
| nano-banana-pro | $1.07 |

`SKILLS_CAROUSEL_BUDGET` default cap: $1.50. Beyond that → warn + require `--yes` to proceed.

Google's tiers got a lot more expensive when Imagen retired and Gemini took over.
An 8-slide run on `nano-banana-pro` now lands at $1.07 — still inside the cap.
The same eight slides at 4K bill `nano-banana-pro` at $1.92 and trip it.
Iterate on the lite tier, then re-run the keeper at full quality.

---

## When to override `--model auto`

- You already have a Flux 2 Pro pipeline elsewhere and want consistency with that brand voice → force `--model flux-2-pro`.
- You're iterating quickly to validate the slide split — use `--model flux-schnell --variants 1` for cheap fast preview, then re-run final with `--model flux-2-pro --resume`.
- You need photorealistic faces / people specifically → force `--model nano-banana-pro` (best identity preservation).
- You need Russian / Cyrillic embedded text → force `--model gpt-image-2` (best non-Latin text rendering).
- Brand-style typography matching a logo → force `--model ideogram-3-quality`.

---

## Provider not registered / env var missing

If `--model <slug>` is passed but the env var is not set, the skill:

1. Prints a clear message: `set $X to use $Y`.
2. Falls back to `--prompts-only` mode (saves the prompts.md, does NOT generate).
3. Exits non-zero.

If `--model auto` and none of the candidates have env vars set:

1. Suggests setting OPENAI_API_KEY or GEMINI_API_KEY as the cheapest entry path.
2. Falls back to `--prompts-only` mode.
3. Exits non-zero.

---

## Future models (placeholder)

When new models ship, add a row to the matrix here + a price entry in `common/runners/cost.PRICE_TABLE` + a Provider class in `common/runners/providers/`. Decision tree above is naturally extensible — no per-model branching, just frontmatter-based routing.
