# Imprint presets — cover-maker (v2.11.0+, opt-in fallback path under v2.14.0+)

**Scope note (v2.14.0+):** the default cover-maker chain is the shared LLM-prompt → image-with-baked-text pipeline (see [`common/visual-prompt-library/system-prompt.md`](../../common/visual-prompt-library/system-prompt.md)) — the image model renders title + creator inside the picture, using the typography genre + composition signature from the chosen style library entry. The imprint presets below are the **opt-in `--typeset overlay` fallback** for cases where text must be pixel-perfect (publisher-exact tracking, complex multilingual layouts, specific OFL-font reproduction). They use real publisher design systems with bundled OFL fonts via Pillow composition.

A book cover is not "an image with a title on top" — it's a **designed layout**: title placed at exact fractions of cover height, in a specific font family, at a specific weight, with a specific palette and tracking. Real publishers (NYRB Classics, Penguin, MIT Press, Picador, Faber) have rigorous design systems.

The `--imprint <name>` flag (under `--typeset overlay`) encodes a real publisher design system. The pipeline becomes **two-pass**:

1. AI model generates a TEXT-FREE background image (per the imprint's prompt fragment)
2. The typography composer overlays title + author with bundled OFL fonts at the imprint's exact layout

Output: a cover that actually looks designed, not "image-with-floating-title".

---

## When to use

- `--medium book` ALWAYS benefits from `--imprint`
- For album / podcast / magazine — current v1 doesn't ship imprints; the AI handles the layout
- For custom layouts: use `--imprint custom --layout-file <path>` (planned for v2.12.0)

---

## Provided imprints

### `nyrb-classics`

**Inspired by**: New York Review Books Classics.

**Aesthetic**: painterly / photographic background art (oil painting, mid-century photograph), centered colored title plate in the upper third, modernist sans-caps title, smaller author below title inside the plate.

**Layout**:

- Title plate band: `y=15% to y=50%`, oxblood red `#8B2C28` at 92% opacity
- Title: Inter Bold 700, 5.2% of cover height, white, ALL CAPS, +60‰ tracking, centered, max 4 lines
- Author: Inter Medium 500, 2.0% of cover height, white, +140‰ tracking, centered inside band

**Genres**: literary fiction, classics, translated fiction, essay.

**Prompt cue**: painterly atmospheric background, mid-20th-century European literary fiction visual vocabulary, muted earthy palette, calmer region in upper third for plate overlay.

---

### `penguin-marber-grid`

**Inspired by**: Romek Marber's 1963 Penguin Crime tri-band design.

**Aesthetic**: three horizontal bands — title band top 27%, illustration band middle 50%, author band bottom 23%. Bold conceptual illustration in middle. Limited palette: cream + ink + single accent.

**Layout**:

- Title band: top 27%, solid warm cream `#F5F0E8`
- Title: Inter SemiBold 600, 6.0% of cover height, ink black, sentence case, +20‰ tracking, centered
- Two thin black rules at 27% and 77% (band separators)
- Author: Inter Medium 500, 2.5% of cover height, ink black, centered in bottom band

**Genres**: classic fiction, crime, thriller, non-fiction.

**Prompt cue**: single bold conceptual illustration in the middle 50% only, flat-vector aesthetic, 2-3 color palette, top 27% and bottom 23% must be PURE solid cream (reserved for typography bands).

---

### `mit-essential-knowledge`

**Inspired by**: MIT Press Essential Knowledge series.

**Aesthetic**: top half typography (title dominant), bottom half abstract diagrammatic visual. Academic primer pocketable. Modern sans-serif.

**Layout**:

- Title: Inter Bold 700, 9.0% of cover height (LARGE), top-left aligned, ink black on white, max 4 lines
- Top 55% reserved for typography (pure white)
- Bottom 45% is the visual zone
- Author: Inter Medium 500, 2.5% of cover height, bottom-left

**Genres**: academic, non-fiction, popular science, technology, science.

**Prompt cue**: abstract diagrammatic visual in bottom 45% only, flat geometric shapes, limited palette with single accent (cyan / red / chartreuse), top 55% must be pure white.

---

### `picador-modern`

**Inspired by**: Picador Modern Classics.

**Aesthetic**: refined typographic top with bold display serif, minimal flat-color visual accent below, generous negative space.

**Layout**:

- Title: Playfair Display Bold 700, 8.0% of cover height, sentence case, ink black on cream, centered
- Author: EB Garamond Regular 400, 2.8% of cover height, +100‰ tracking, centered bottom
- A thin black hairline at y=90% (separator above author)

**Genres**: literary fiction, memoir, essay, essays.

**Prompt cue**: small flat-color symbolic illustration mid-lower frame (about 25% of width), warm cream background, single muted accent (dusty rose / soft terracotta / muted teal), generous negative space.

---

### `faber-modernist`

**Inspired by**: Faber & Faber poetry / criticism / manifesto covers (Albertus / Wolpe heritage).

**Aesthetic**: typography-as-image. Solid bold flat-color background. Large display lettering centered. No photograph, no illustration.

**Layout**:

- Title: Cinzel Bold 700, 11.0% of cover height (very large), centered, ALL CAPS, +40‰ tracking, off-white on bold field
- Author: EB Garamond Regular 400, 3.0% of cover height, +180‰ tracking, centered bottom
- Thin hairline at y=85%

**Genres**: poetry, essay, criticism, manifesto, non-fiction.

**Prompt cue**: SOLID FIELD of one rich saturated color (cobalt / oxblood / olive / aubergine), subtle paper grain texture, NO illustration, NO image.

---

## Genre → imprint default mapping

When `--genre` is provided but no `--imprint`, this mapping picks the default:

| Genre | Default imprint |
|---|---|
| `literary-fiction` | `nyrb-classics` |
| `classics` | `nyrb-classics` |
| `translated-fiction` | `nyrb-classics` |
| `thriller`, `crime` | `penguin-marber-grid` |
| `non-fiction`, `popular-science`, `science`, `technology`, `academic` | `mit-essential-knowledge` |
| `memoir`, `essay`, `essays` | `picador-modern` |
| `poetry`, `criticism`, `manifesto` | `faber-modernist` |

---

## Plan-file fields (v2.11.0+)

To use an imprint via raw plan.json:

```json
{
  "schema": "skills.cover.plan.v1",
  "medium": "book",
  "imprint": "nyrb-classics",
  "genre": "essay",
  "typeset": "overlay",
  "title": "...",
  "creator": "...",
  ...
}
```

The CLI auto-defaults `typeset` to `overlay` when `medium=book` AND (`imprint` is set OR `genre` is set).

---

## Adding a custom imprint

For v2.11.0, custom imprints require editing `common/runners/cover_imprints.py`. A future v2.12 release will add `--layout-file <path>` to load a JSON layout spec without code changes.

To extend the bundled set: add a new entry to `IMPRINTS` dict in `cover_imprints.py`, then re-install. Layout spec is documented in `common/runners/typography.py:TypeLayout`.

---

## Why this works

AI image models (gpt-image-2, Imagen 4, Flux) render text **into** images — they don't typeset. The result feels like a magazine illustration with a caption overlay, not like a designed book. By separating:

1. **Background art** — what AI is good at (atmospheric visuals, photoreal subjects, painterly style)
2. **Typography** — what AI is bad at (consistent letterforms, baseline grids, exact kerning, designer-grade hierarchy)

…and doing typography in Pillow with real bundled OFL fonts at imprint-faithful proportions, we get covers that read as **professionally designed** rather than **AI-generated with text awkwardly squeezed in**.

Reference research: BeYourCover, Inkfluence, NYRB / Penguin / MIT Press / Picador / Faber design system documentation. Pattern adopted by every pro AI-cover designer working in 2026.
