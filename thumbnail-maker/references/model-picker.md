# Model picker — thumbnail-maker

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

| Model | 3 placements × 1 variant | 3 × 3 variants (9 total) |
|---|---|---|
| nano-banana-pro | $0.15 | $0.45 |
| gpt-image-2 (med) | $0.15-0.30 | $0.45-0.90 |
| ideogram-3-quality | $0.24 | $0.72 |
| flux-2-pro | $0.18 | $0.54 |

All under default $1.50 budget.

---

## When to override

- **Face must be exactly preserved (creator's known face)**: `nano-banana-pro`.
- **Brand-clean typography matters more than face**: `ideogram-3-quality`.
- **CJK / Cyrillic title**: `gpt-image-2`.
- **Quick iteration on title copy**: `flux-schnell` for cheap preview, then re-run final with `nano-banana-pro` or `ideogram-3-quality`.
