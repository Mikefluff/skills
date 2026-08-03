# Google models

One family now. Google folded dedicated image generation into Gemini and
retired Imagen; "Nano Banana" is the marketing name for the Gemini image models.

**Imagen 4 is gone.** Google shut `imagen-4.0-generate-001`,
`imagen-4.0-ultra-generate-001` and `imagen-4.0-fast-generate-001` down on
2026-06-30. The old slugs still resolve here — they print a warning and route to
the tier below — but there is no Imagen endpoint left to call.

| Retired slug | Routes to | Why that one |
|---|---|---|
| `imagen-4-ultra` | `nano-banana-pro` | Google's own named replacement |
| `imagen-4` | `nano-banana-2` | Same tier, same strict adherence |
| `imagen-4-fast` | `nano-banana-2-lite` | Cheapest tier, same iteration role |

---

## Nano Banana Pro (Gemini 3 Pro Image)

**Model id**: `gemini-3-pro-image`
**Strengths**: 4K output; multi-person consistency up to 5 faces; up to 14 input reference images; "thinking mode" that plans the composition; web-grounded (can pull facts into infographics); strongest for slides, diagrams, infographics; respects verbatim camera / lighting / DOF / color-grading vocabulary.
**Weaknesses**: the most expensive image call in the collection — $0.134 at 1K/2K, $0.24 at 4K. Reserve it for finals.
**Execute via**: `--execute --model nano-banana-pro` (env: `GEMINI_API_KEY`) — Gemini API.

### Syntax

- Natural language, multi-turn editorial conversation inside Gemini.
- Reference images attached as chat inputs.
- Camera / lighting / lens vocabulary is honored verbatim — say "85mm at f/1.8" and you get it.

### Prompt template

```
{subject + action + context}. {style tags}. {lighting — specify direction, quality, temperature}. {camera + lens + aperture + DOF}. {texture / realism notes}. {color grading}. Aspect: {ratio}.
```

### Example

```
A confident business person in their thirties leaning on a polished white marble countertop in a sunlit Brooklyn loft kitchen at golden hour. Editorial photo, cinematic color grading with warm highlights and cool shadows. Soft directional key light from the upper-left window at ~5500K, gentle rim light on the hair, neutral ambient fill. 85mm lens at f/1.8 on a full-frame DSLR; focus locked on the eyes; creamy background bokeh. Natural skin texture with visible pores, realistic linen fabric, slight specular highlight on the marble. Aspect: 4:5 portrait.
```

### Notes

- The killer feature is multi-turn refinement — generate, then say "same shot, swap shirt to navy, push fill 1 stop, keep face identical."
- Use reference images for product / character lock — up to 14.
- For infographics and slides: ask plainly, the model handles layout + text well.
- Pass `--resolution 4k` only when you need it; it nearly doubles the bill.

---

## Nano Banana 2 (Gemini 3.1 Flash Image)

**Model id**: `gemini-3.1-flash-image`
**Strengths**: the workhorse. State-of-the-art 4K, reliable in-image text, strong multi-reference handling, and a fraction of Pro's cost at $0.101 (2K) / $0.151 (4K). Inherits Gemini's world knowledge, so it can be told *what* a thing is rather than only what it looks like.
**Weaknesses**: less deliberate composition than Pro on dense layouts — Pro's thinking mode still wins on slides and infographics.
**Execute via**: `--execute --model nano-banana-2` (env: `GEMINI_API_KEY`).

### Syntax

Same grammar as Nano Banana Pro. Natural language, no flags, aspect ratio as an
API param.

### Prompt template

```
{subject + action + context}. {style tags}. {lighting}. {camera + lens}. {texture / realism notes}. Aspect: {ratio}.
```

### Notes

- This is the default choice for anything that is not a hero shot.
- Thinking effort is tunable — ask for high effort on composition-heavy work,
  minimal for straightforward stills.
- For in-image text, quote the exact copy: `the sign reads "OPEN"`.

---

## Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)

**Model id**: `gemini-3.1-flash-lite-image`
**Strengths**: Google's fastest and cheapest image model — $0.034 at 1K. The
moodboarding and iteration tier.
**Weaknesses**: visibly softer than Nano Banana 2; weaker text rendering. Do not
finalize on it.
**Execute via**: `--execute --model nano-banana-2-lite` (env: `GEMINI_API_KEY`).

### Prompt template

```
{compact natural-language scene}, {style}, {lighting}, {camera}, {texture}
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen, editorial photo, soft window light, 85mm f/1.8, natural skin texture, 4:5
```

### Notes

- Iterate on Lite, finalize on Nano Banana 2 or Pro.
- Keep prompts shorter than you would for the larger tiers.
