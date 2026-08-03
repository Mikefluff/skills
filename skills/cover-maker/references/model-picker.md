# Model picker — cover-maker

> Per-unit prices below are illustrative; the canonical table is
> [`common/references/model-pricing.md`](../../../common/references/model-pricing.md),
> generated from `common/runners/cost.py` — the same table that estimates your bill.
> Batch figures here are that unit price times the item count.

Decision tree + capability matrix.

---

## Decision tree

```
1. Heavy embedded text (titles always have text)?
     yes (default for covers) → continue
2. Photo / artwork reference provided?
     yes:
        Photo is a person's identifiable face (author / artist / cover star)?
           → nano-banana-pro (best identity preserve)
        Photo is a brand asset / artwork (palette + style transfer)?
           → flux-2-pro or seedream-4.5
        Photo + lots of text (magazine masthead + cover lines + hero)?
           → gpt-image-2 (best multi-ref + text balance)
     no: continue
3. Magazine / photoreal cover (no provided photo, but photoreal style chosen)?
     → imagen-4-ultra
4. Default for text-heavy cover, no photo?
     → ideogram-3-quality (cleanest text rendering, brand-style transfer)
5. Available env vars?
     drop candidates without env vars
     fallback: flux-2-pro (BFL_API_KEY) or replicate-image router
```

### Default pick

`auto` with default settings:

- **No photo**: `ideogram-3-quality` if `IDEOGRAM_API_KEY` set; else `gpt-image-2`; else `flux-2-pro`.
- **Photo (identifiable face)**: `nano-banana-pro` if `GEMINI_API_KEY` set.
- **Photo (brand / palette)**: `flux-2-pro` if `BFL_API_KEY` set.
- **Magazine (photoreal hero)**: `imagen-4-ultra` or `gpt-image-2`.

---

## Capability matrix

| Slug | Text-in-image | Multi-ref | Identity preserve | Style transfer | Cost / variant | Best for cover |
|---|---|---|---|---|---|---|
| `ideogram-3-quality` | excellent (cleanest) | yes (1 style-ref) | medium | medium | $0.08 | Text-heavy book / podcast / deck / LinkedIn / report DEFAULT |
| `ideogram-3` | excellent | yes (1 style-ref) | medium | medium | $0.04 | Quick iteration |
| `gpt-image-2` | excellent (Latin + CJK) | yes (up to 16) | medium | medium | $0.05-0.10 | Magazine, multi-text + photo |
| `nano-banana-pro` | good | yes (8) | excellent | good | $0.05 | Author / artist photo embedded |
| `imagen-4-ultra` | good | limited (1) | good | good | $0.06 | Photoreal magazine / book |
| `flux-2-pro` | fair | yes (4) | good | excellent | $0.06 | Palette / texture transfer |
| `flux-kontext` | fair | yes (1, edit-mode) | good | excellent (edit) | $0.05 | Edit existing artwork |
| `seedream-4.5` (fal) | fair | yes (4) | good | excellent (photoreal) | $0.04 | Photoreal stylization |

### Anti-recommendations

- `flux-schnell`: too low fidelity for cover text rendering
- `imagen-4` (non-ultra): limited multi-ref, less polish
- `replicate-image` router: variable; only use if specific Replicate model is required

---

## Cost preview by variant count

| Model | 1 variant | 2 variants (default) | 3 variants | 5 variants |
|---|---|---|---|---|
| ideogram-3-quality | $0.08 | $0.16 | $0.24 | $0.40 |
| ideogram-3 | $0.04 | $0.08 | $0.12 | $0.20 |
| gpt-image-2 (med) | $0.05 | $0.10 | $0.15 | $0.25 |
| nano-banana-pro | $0.05 | $0.10 | $0.15 | $0.25 |
| flux-2-pro | $0.06 | $0.12 | $0.18 | $0.30 |

All under default `SKILLS_CAROUSEL_BUDGET=$1.50`. No confirmation prompt for typical runs.

---

## Per-medium recommendations

| Medium | Default model | Why |
|---|---|---|
| `album` | nano-banana-pro (if artist photo) / flux-2-pro (if abstract) | Identity matters when artist face is featured |
| `book` | ideogram-3-quality | Title legibility is THE priority for sales |
| `podcast` | ideogram-3-quality | Bold typography legible at thumbnail scale |
| `magazine` | gpt-image-2 (best text + photo combo) / imagen-4-ultra | Multi-text layout + photoreal hero |
| `report` | ideogram-3-quality | Clean corporate typography |
| `deck-cover` | ideogram-3-quality | Professional title + subtitle clarity |
| `linkedin-doc` | ideogram-3-quality | Same as deck-cover |

---

## When to override `auto`

- **Specific brand-typography flyer** (logo + brand colors): force `--model ideogram-3-quality` with `--photo <brand-asset>` and a brand-aligned style.
- **Author photo on book cover with strong style transfer** (e.g., painterly oil-portrait style): force `--model nano-banana-pro` BUT accept that identity will reduce as style intensifies. Or use `image-prompt --execute --model flux-kontext --image-url <photo>` for edit-mode.
- **Cyrillic / CJK title**: force `--model gpt-image-2` (best non-Latin text rendering).
- **Quick iteration on title copy / layout**: force `--model ideogram-3` (no -quality suffix) for cheaper takes; final with `--model ideogram-3-quality`.
- **Editing an existing cover** ("take this album cover and add a year label"): use `image-prompt --execute --model flux-kontext --image-url <existing.png> --prompt "..."` directly — cover-maker is for creating from scratch.

---

## Provider env-var prerequisites

| Provider | Required env vars |
|---|---|
| `ideogram-3-quality` / `ideogram-3` | `IDEOGRAM_API_KEY` |
| `gpt-image-2` | `OPENAI_API_KEY` |
| `nano-banana-pro` / `imagen-4-ultra` | `GEMINI_API_KEY` |
| `flux-2-pro` / `flux-kontext` | `BFL_API_KEY` |
| `seedream-4.5` (via fal router) | `FAL_KEY` |

Run `/skills-keys verify` to confirm providers are reachable.
