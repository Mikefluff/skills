# Text-in-image rendering

Per-model rules for rendering legible text inside generated images. Most failure modes are model choice, not prompt craft — pick the right model first.

---

## Text-rendering tier (2026)

Ranked best → worst:

1. **Ideogram 3 Quality** — paragraph-length, typographic control, kerning holds
2. **Nano Banana Pro** — paragraph-length, strong layout, multi-turn refinement
3. **Imagen 4 Ultra** — paragraph-length, strong across major scripts
4. **gpt-image-2** — paragraph-length, ~99% character accuracy
5. **Qwen-Image 2.0** — paragraph-length, best for CJK + Hindi + Bengali + mixed multilingual
6. **Flux 2 Pro** — ~60% accuracy on complex typography; one short phrase reliable
7. **Midjourney v7** — avoid > 5 words; tagline-tier only
8. **SDXL / SD 3.5** — avoid for any legible text; overlay in a design tool instead

---

## How to quote text in the prompt

- **Single-quote within prompt** — wrap the literal string:
  ```
  A wooden door with the text "WELCOME HOME" carved into a brass plaque.
  ```

- **Multi-line** — either `\n` or explicit layout:
  ```
  A poster reading:
  Line 1: "SUMMER NIGHTS"
  Line 2: "Live at the Rooftop"
  Line 3: "August 14"
  ```

- **Long copy** — describe layout explicitly so the model knows where lines break:
  ```
  Book cover with title "The Quiet Engine" at the top in large serif,
  subtitle "A Field Guide to Hard Decisions" below in smaller italic serif,
  author name "M. Vance" at the bottom in small caps.
  ```

---

## Length caps per model

| Model | Reliable length |
|---|---|
| Ideogram 3 Quality | paragraph+ |
| Nano Banana Pro | paragraph+ |
| Imagen 4 Ultra | paragraph+ |
| gpt-image-2 | paragraph+ (~99% char accuracy) |
| Qwen-Image 2.0 | paragraph+ (best for CJK + multilingual) |
| Flux 2 Pro | ~1 short phrase |
| Midjourney v7 | ≤ 5 words |
| SD 3.5 | avoid — overlay in Figma / Photoshop |

---

## Multilingual rendering

- **Qwen-Image 2.0** — leader for Chinese (Simplified + Traditional), Japanese, Korean, Hindi, Bengali, and mixed CJK + Latin. Apache-2.0, self-hostable.
- **gpt-image-2** — strong across Latin, CJK, Hindi, Bengali. Best closed-source multilingual option.
- **Imagen 4 Ultra** — strong on major scripts (Latin, Cyrillic, CJK, Arabic).
- **Ideogram 3 Quality** — strong on Latin + Cyrillic; weaker on CJK.
- **Avoid for non-Latin**: Midjourney v7, SDXL, Flux 2 Pro — output is hallucinated glyphs.

For Cyrillic specifically: Ideogram 3 and Imagen 4 are both reliable. Test before committing.

---

## Font hints

Most models don't expose true font names but respond to typographic descriptors:

**Form descriptors**:
- `serif`, `sans-serif`, `monospace`, `slab serif`, `display serif`
- `handwritten`, `calligraphy`, `brush script`, `cursive`
- `neon tube lettering`, `letterpress`, `engraved metal`, `embossed`
- `chiseled stone`, `wooden carved`, `gilded`, `painted on glass`

**Genre descriptors**:
- `art deco`, `y2k retro`, `brutalist`, `Bauhaus`
- `newspaper headline`, `1970s pulp paperback`, `1950s diner signage`
- `vintage Swiss design`, `Victorian poster`, `wild west wanted poster`
- `90s zine`, `cyberpunk neon`, `minimalist editorial`

**Weight / size hints**:
- `bold`, `thin`, `extra-light`, `condensed`, `wide`
- `large display size`, `small body copy`, `tight tracking`, `loose tracking`

---

## Anti-patterns

❌ Asking Midjourney / SDXL / Flux for > 5 words and expecting legibility. They hallucinate glyphs. Use Ideogram / Nano Banana / gpt-image-2 / Imagen.

❌ Asking any model for legally-protected typography — Coca-Cola script, Disney wordmark, Apple SF, Netflix logo. Model refuses, approximates, or returns infringing output. Use a vector tool with licensed type.

❌ Trying to render exact-typography brand assets in a generator. For pixel-perfect brand work: render the image in the generator, then overlay typography in Figma / Photoshop / Affinity with licensed fonts.

❌ Naming a specific font ("Helvetica Neue 75 Bold") and expecting it. Models don't have font libraries — they approximate by genre. Describe the look, not the file.

❌ Asking for non-Latin text from Midjourney / SDXL / Flux. The output is decorative-looking gibberish.

---

## Paste-ready templates

### Poster with title + tagline (Ideogram 3 Quality)

```
Event poster, art deco style, vertical 2:3 composition.
Title at top: "SUMMER NIGHTS" in large condensed sans-serif, gold on deep navy.
Subtitle below: "Live at the Rooftop" in smaller italic serif.
Date at bottom: "August 14, 2026" in small caps.
Tight kerning, generous negative space, centered alignment.
```

### Book cover with subtitle (Nano Banana Pro)

```
Book cover, 2:3 portrait, minimalist editorial style.
Title "The Quiet Engine" at the top, large serif display weight, charcoal on cream.
Subtitle "A Field Guide to Hard Decisions" below the title, smaller italic serif.
Author name "M. Vance" at the bottom, small caps, tight tracking.
Single abstract element in the center — a faint geometric line drawing.
```

### Multilingual signage (Qwen-Image 2.0)

```
Storefront signage, neon tube lettering, night scene.
Top line: "夜の灯" (large, warm white neon).
Bottom line: "Yoru no Akari" (smaller, magenta neon).
Brick wall background, slight reflection on wet pavement.
```

### Brand logo concept (Recraft V3)

```
Vector logo concept, flat 2D, transparent background.
Wordmark "NORTHWIND" in geometric sans-serif, bold weight, even letter spacing.
Single accent shape — a minimal compass-rose mark — left of the wordmark.
Two-color palette: deep navy + warm copper.
Clean SVG-ready geometry, no gradients, no shadows.
```

### Newspaper headline (Imagen 4 Ultra)

```
1950s newspaper front page, top-of-fold composition.
Masthead "THE EVENING STANDARD" in large blackletter serif.
Headline below: "ROCKET LAUNCH SUCCESSFUL" in bold condensed serif, all caps.
Subhead: "Crew safe; recovery underway off Cape Canaveral" in italic serif.
Aged newsprint texture, slight ink bleed, halftone photo placeholder centered.
```
