# Model picker — thumbnail-maker

> Prices below are checked against
> [`common/references/model-pricing.md`](../../../common/references/model-pricing.md)
> by `scripts/check-prices.py`, which fails the build when a figure here stops
> matching `common/runners/cost.py` — the table that estimates your bill. Batch
> totals are that unit price times a count the file declares.

## Ideogram 4 is available as of 2026-08-08

`ideogram-4-turbo` / `ideogram-4` / `ideogram-4-quality` ($0.03 / $0.06 / $0.10)
call the v4 endpoint. Native 2K, and the current best typography Ideogram ships —
prefer `ideogram-4-quality` over `ideogram-3-quality` when legible text *is* the
job and the extra cent per image is irrelevant.

The v3 tiers stay the default here rather than flipping silently: they are what
every worked example in this skill was calibrated against. Pass `--model
ideogram-4-quality` to opt in.

`ideogram-3-flash` remains the cheapest tier — v4 has no FLASH speed yet.

---

---

## Decision tree

```
1. Photo provided (face)?
     yes:
        Heavy text (typical YouTube thumbnail)?
           → gpt-image-2 (best face + text balance)
        Face identity is THE priority?
           → nano-banana-pro
     no:
        Text-only thumbnail → ideogram-3-quality

2. Available env vars filter the result.
```

---

## Default

`auto`:
- Photo + face: `nano-banana-pro` if GEMINI_API_KEY set; else `gpt-image-2`
- No photo: `ideogram-3-quality` if IDEOGRAM_API_KEY set; else `gpt-image-2`

---

## Cost preview

<!-- prices: batch=3,9 -->

| Model | 3 placements × 1 variant | 3 × 3 variants (9 total) |
|---|---|---|
| nano-banana-pro | $0.40 | $1.21 |
| gpt-image-2 (med) | $0.15-0.30 | $0.45-0.90 |
| ideogram-3-quality | $0.27 | $0.81 |
| flux-2-pro | $0.18 | $0.54 |

All under default $1.50 budget.

---

## When to override

- **Face must be exactly preserved (creator's known face)**: `nano-banana-pro`.
- **Brand-clean typography matters more than face**: `ideogram-3-quality`.
- **CJK / Cyrillic title**: `gpt-image-2`.
- **Quick iteration on title copy**: `flux-schnell` for cheap preview, then re-run final with `nano-banana-pro` or `ideogram-3-quality`.
