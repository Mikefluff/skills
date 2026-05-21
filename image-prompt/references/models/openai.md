# OpenAI models

gpt-image-2 is the active model. DALL-E 3 is retired.

---

## gpt-image-2

**Strengths**: agentic reasoning over the prompt (plans the composition before drawing); ~99% character-level text accuracy across Latin, CJK, Hindi, Bengali; up to 16 reference images; multi-turn edits with strong identity preservation.
**Weaknesses**: slowest of the top tier; "high" quality is expensive; over-specifying visuals can fight the planner.

### Syntax

- Natural language paragraphs. No `--` flags.
- `quality`: `low` / `medium` / `high`
- For edits: explicit preserve / change language — "keep face, swap shirt to navy."
- Reference images attached via API or chat upload.

### Prompt template

```
Intent: {what the image is for, who sees it, what action it drives}.
Scene: {subject + action + context}.
Style: {style tags}.
Lighting: {direction, quality, temperature}.
Camera: {lens + aperture + DOF}.
Texture: {realism notes}.
Constraints: {what to avoid; in-image text if any, quoted exactly}.
```

### Example

```
Intent: a hero shot for a B2B SaaS landing page selling kitchen-ops software to restaurant founders.
Scene: a confident business person in their thirties leaning on a polished white marble countertop in a sunlit Brooklyn loft kitchen at golden hour.
Style: editorial photo, cinematic color grading.
Lighting: soft directional key light from the upper-left window, gentle rim on the hair, neutral ambient fill.
Camera: 85mm lens at f/1.8 on a full-frame DSLR; tack-sharp focus on the eyes; shallow depth of field with creamy background bokeh.
Texture: natural skin texture with visible pores, realistic linen fabric.
Constraints: no text, no watermarks, anatomically correct hands, portrait 4:5.
```

### Notes

- Give it intent + constraints, not over-specified pixels — it plans better than it follows micro-direction.
- For in-image text, quote the exact copy: `the menu reads "PRIX FIXE — $48"`. It nails it.
- Multi-turn: "same shot, swap shirt to navy, keep face identical" works reliably.
- Use `high` quality only for finals.

---

## DALL-E 3 (retired 2026-05-12)

- Retired. The endpoint no longer accepts prompts.
- Use gpt-image-2 instead — superset of DALL-E 3's capabilities.
- The old Reddit "I NEED to test how the tool works" verbatim-prompt hack is obsolete; gpt-image-2 does not auto-rewrite.
- Existing scripts targeting the DALL-E 3 model name should be migrated to `gpt-image-2`.
- Generated DALL-E 3 outputs in your archives are still licensed under the original terms.
