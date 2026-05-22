---
id: _universal-rules
modality: carousel
display: "Universal carousel rules"
metadata-only: true
---

# Universal carousel rules

Every carousel slide prompt — regardless of chosen style — must obey these rules. The Python prompt builder (`common/runners/carousel_prompt_builder.py`) injects them into every generated prompt automatically. **Do not duplicate per-style.**

---

## 1. Static carousel elements (in every slide)

Each slide is one frame of a carousel — the user swipes through them. Three universal UI elements must appear on every slide so the viewer reads it as a carousel:

### Page indicator

Bottom-center of the frame. Small, subtle, set in the chosen-style accent typography. Exact text: `"<N> из <total>"` (RU) or `"<N> of <total>"` (EN). Always in double-quotes inside the prompt.

Examples:
- `"1 из 5"` / `"3 из 7"` / `"5 of 5"`
- `bottom center small subtle text: "2 из 5"`

### Swipe hint (slides 1 to N−1)

Bottom-right corner. Arrow glyph + label. Style-color appropriate.

Examples:
- `"листай →"`
- `"swipe →"`
- A thin arrow shape with adjacent text

### End marker (last slide ONLY)

Bottom-right corner (REPLACES swipe arrow on final slide). Style-appropriate end-of-deck indicator.

Examples:
- `"конец"` / `"end."` / `"finis"` / `"·"`
- A small geometric closing glyph

### Slide marker (optional, style-permitting)

Lower-outer corner. Slide number in style-appropriate notation:
- Modernist styles → Arabic numeral, tabular figures, top-right
- Classical / academic styles → Roman numeral (I, II, III, IV, V), lower-outer corner
- Industrial / tactical → `[001]` `[002]` bracketed in tabular monospace

---

## 2. Infographic grammar (universal patterns)

Each slide must read as **infographic**, not as a paragraph dump or atmospheric image with a caption. Use ONE of these layout patterns per slide based on the content type:

### Numbered list

```
Large number "1." or "01" left of each line.
First item: "<text>"
Second item: "<text>"
Third item: "<text>"
```

### Comparison / table

```
Two columns side-by-side: "<column-A-header>" | "<column-B-header>"
Row 1: "<A-1>" | "<B-1>"
Row 2: "<A-2>" | "<B-2>"
```

OR before-after:
```
Left side label: "<BEFORE>" with description "<text>"
Right side label: "<AFTER>" with description "<text>"
Connecting arrow between sides.
```

### Data badge / callout

```
Large circle or pill-shape with one big number: "<78>" or "<3×>" or "<$2M>"
Caption beneath: "<short context>"
```

### Quote block

```
Open-quote glyph, then italic body: "<quote-text>"
Attribution beneath in smaller weight: "— <name>, <context>"
```

### Steps / process

```
Numbered horizontal sequence: 01 → 02 → 03 → 04
Step 1: "<title>" + "<body>"
Step 2: "<title>" + "<body>"
Connecting arrows between steps.
```

### Myth vs reality

```
Top half: label "MYTH" or "WHAT YOU'RE TOLD" + "<text>"
Bottom half: label "REALITY" or "WHAT ACTUALLY HAPPENS" + "<text>"
Horizontal divider with a contrasting accent line.
```

### Framework / N-box

```
N-column or NxM grid of boxes:
Box 1: header "<H>" + body "<B>"
Box 2: header "<H>" + body "<B>"
...
```

---

## 3. Text-in-image discipline

Every text element that should APPEAR on the rendered slide must be in DOUBLE QUOTES in the prompt. The image model treats unquoted text as a description of the scene, not as text-to-render.

✓ `large headline upper-center: "Software, slowly."`
✗ `Headline: Software, slowly.` (model may not render it)

---

## 4. Composition language

Use natural-language position descriptors. Do not invent layout markup.

- ✓ `large headline upper-center`, `bottom-right`, `centered on the canvas`, `aligned to the left third`
- ✗ `HEADLINE`, `BODY`, `SUBTITLE`, `CTA`, `FOOTER` (these literal words will be rendered as text on the image)
- ✗ `1080×1080`, `1:1 aspect ratio`, `Instagram`, `IG`, `LinkedIn` (these can render as text)
- ✗ `#FF0000`, `rgba(...)` (hex / color codes can render)

---

## 5. Information density rules

Per slide:

- **Title:** ≤6 words. Sentence case or all-caps depending on style.
- **Subtitle / supporting line:** ≤10 words.
- **Body text:** ≤30 words total across all body slots on the slide.
- **List items:** 2-5 items per slide. Each item ≤6 words.
- **Total visible text on slide:** ≤80 words. If content is longer, split across two slides.

If the source content is dense (technical breakdown, deep argument), use FEWER slots per slide with HIGHER information density per slot (data badges, charts, frameworks). Don't smear paragraphs across slides.

---

## 6. Style-anchor primacy

Every prompt must begin with the chosen style's **text-in-image mode anchor** verbatim (or near-verbatim). This sets the aesthetic before any layout instruction. The builder loads this from the style file.

---

## 7. Forbidden patterns (universal — apply to every prompt)

In addition to forbidden composition markup (§4):

- No watermarks, no QR codes, no website URLs (unless the slide is specifically a CTA with a website).
- No logos other than the brand explicitly named in the content.
- No emojis unless the style explicitly permits them.
- No drop shadows on text unless the style specifies them.
- No gradients on text unless the style specifies them.
- No more than 2 typefaces visible per slide.
- No fake AI text artifacts (mangled letters, half-formed glyphs from poor rendering — emphasize "sharp text only, all text fully formed and legible").

---

## 8. Anti-AI-tells

Add these closing modifiers to every prompt to suppress common AI failure modes:

```
Sharp text rendering, all letters fully formed, no melted glyphs, no gradient text effects, no drop shadows on type, no AI face artifacts, no double-pupils, no extra fingers, no warped geometry.
```

---

## 9. Per-style overrides

A style file MAY override any universal rule in its own `# Style-specific overrides` section. The builder applies overrides AFTER universal rules. Example: `brutalist-grid` may override the page-indicator typography to bracketed tabular monospace `[02/05]`.

---

## 10. Loading order in the builder

The Python prompt builder concatenates in this order:

1. Style anchor (text-in-image mode block)
2. Slide-role composition template (from `slide-roles.md`)
3. Content slots filled in (title + body + list items + data points etc., all quoted)
4. Static carousel elements (page indicator + swipe/end + slide marker, style-appropriate)
5. Anti-AI-tells closing line

The output is a single dense paragraph ≤1500 chars, ready to send to the image provider.
