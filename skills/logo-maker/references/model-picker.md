# Model picker — logo-maker

> Per-unit prices below are illustrative; the canonical table is
> [`common/references/model-pricing.md`](../../../common/references/model-pricing.md),
> generated from `common/runners/cost.py` — the same table that estimates your bill.
> Batch figures here are that unit price times the item count.

## Default: `ideogram-3-quality`

Text rendering is everything for logos. ~90% of generated logos fail because the text is mangled. Ideogram 3 Quality is the current best-in-class for embedded text.

| Strength | Score |
|---|---|
| Text legibility | best |
| Custom lettering / ornamental type | best |
| Clean geometric shapes | good |
| Illustration / mascot | OK |
| Single-color palette obedience | best |

**Use for**: wordmark, typographic, minimal-with-text, geometric-with-text.

---

## Fallback: `gpt-image-2`

When the logo is icon-heavy and text is secondary (or absent).

| Strength | Score |
|---|---|
| Text legibility | very good |
| Clean illustration | best |
| Mascot / character | best |
| Complex compositions (emblem) | best |
| Multi-color palette obedience | very good |

**Use for**: illustrated, emblem, complex minimal (icon + small wordmark).

---

## Specialized: `flux-2-pro`

For brand-palette-led work where matching exact colors matters more than text fidelity.

**Use for**: rebrand projects where you have a precise palette to match. Pair with `--style-mod "exact palette: #2D5F7C, #F4E9D8, #B33B26"`.

**Avoid**: brands where text rendering is the dominant concern.

---

## Anti-defaults

Do NOT use for logos:

- **flux-schnell** — too low quality for production logos
- **sdxl-1.0** — older, text rendering is poor
- **veo / sora** — these are video models
- **Nano Banana 2** — strong for photoreal but inconsistent on vector aesthetics

---

## When to override defaults

| Scenario | Override |
|---|---|
| Wordmark with very long brand name | `--model ideogram-3-quality` + `--style-mod "abbreviation form: <ACRONYM>"` |
| Illustrated logo with no text | `--model gpt-image-2` |
| Emblem with text around a circle | `--model gpt-image-2` (better at circular text) |
| Exact palette match required | `--model flux-2-pro` + explicit hex codes in `--palette` |
| Budget-conscious exploration (many variants) | `--model ideogram-3-turbo` (faster, cheaper, lower quality) |

---

## Cost guide (approximate, May 2026)

| Model | $/image | Speed |
|---|---|---|
| `ideogram-3-quality` | $0.08 | ~20s |
| `ideogram-3-turbo` | $0.03 | ~5s |
| `gpt-image-2` (low) | $0.04 | ~10s |
| `gpt-image-2` (high) | $0.19 | ~25s |
| `flux-2-pro` | $0.05 | ~15s |

Default batch of 4 variants × ideogram-3-quality ≈ $0.32. Well under the $1.50 carousel budget cap.
