# Google models

Imagen 4 family for strict-adherence stills; Nano Banana Pro (= Gemini 3 Pro Image) for editorial multi-turn work.

---

## Imagen 4

**Strengths**: strict prompt adherence; 2K native output; top-class in-image text rendering (signs, posters, packaging copy); clean photoreal default.
**Weaknesses**: less "artistic" than Midjourney by default; no parameter flags — natural language only.

### Syntax

- Natural language only. No `--` flags.
- Aspect ratio is an API param (`aspectRatio: "4:5"` etc.), not in-prompt.
- Negative prompt via separate API field where exposed.

### Prompt template

```
{subject + action + context}. {style tags}. {lighting}. {camera + lens}. {texture / realism notes}.
```

### Example

```
A confident business person leaning on a marble countertop in a sunlit Brooklyn loft kitchen at golden hour. Editorial photo, cinematic color grading. Soft directional key light from the upper-left window, gentle rim catching the hair. 85mm lens at f/1.8 on a full-frame DSLR; tack-sharp focus on the eyes; shallow depth of field. Natural skin texture with visible pores, realistic linen fabric.
```

### Notes

- Spell instructions out — Imagen rewards specificity and punishes vagueness.
- For in-image text, quote the exact copy: `the sign reads "OPEN"`.

---

## Imagen 4 Ultra

**Strengths**: same grammar as Imagen 4 at higher fidelity, better detail in faces and fabric.
**Weaknesses**: highest cost in the family.

### Syntax

Same as Imagen 4.

### Prompt template

```
{full natural-language scene} — render at maximum detail
```

### Example

```
<Imagen 4 example above> — render at maximum detail; emphasize natural skin micro-texture and linen weave.
```

### Notes

- Reserve for hero shots, not iteration.
- Pricing (Vertex AI / Gemini API, May 2026): Imagen 4 Fast ~$0.02 / image, Imagen 4 (Standard) ~$0.04 / image, **Imagen 4 Ultra ~$0.06 / image** at 1024×1024 (sources disagree on a $0.08 figure on some 3rd-party resellers). See [intuitionlabs.ai pricing roundup](https://intuitionlabs.ai/articles/ai-image-generation-pricing-google-openai) and [cloudprice.net Imagen 4 Ultra](https://cloudprice.net/models/google-imagen-4-ultra).

---

## Imagen 4 Fast

**Strengths**: fastest in the family; cheap; good enough for moodboarding.
**Weaknesses**: visibly softer than Imagen 4 / Ultra; weaker text rendering.

### Syntax

Same as Imagen 4. Keep prompts shorter.

### Prompt template

```
{compact natural-language scene}, {style}, {lighting}, {camera}, {texture}
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen, editorial photo, soft window light, 85mm f/1.8, natural skin texture, 4:5
```

### Notes

- Iterate on Fast, finalize on Ultra.

---

## Nano Banana Pro (Gemini 3 Pro Image)

**Strengths**: 4K output; multi-person consistency up to 5 faces; up to 14 input reference images; "thinking mode" that plans the composition; web-grounded (can pull facts into infographics); strongest for slides, diagrams, infographics; respects verbatim camera / lighting / DOF / color-grading vocabulary.
**Weaknesses**: lives inside Gemini chat — automation needs the Gemini API, not a one-shot endpoint.

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
