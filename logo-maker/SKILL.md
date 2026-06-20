---
name: logo-maker
description: "Brand mark / wordmark / logo generator. Default ideogram-3-quality for clean embedded text (gpt-image-2 fallback). Six presets: wordmark, minimal, illustrated, typographic, geometric, emblem. Optional palette hint. N variants per call. Use when: 'logo', 'brand mark', 'wordmark', 'логотип', 'эмблема', 'фирменный знак'."

license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Logo generator. Input: brand name + optional tagline + style preset + palette hint. Output: N stochastic variants of the same brief.

Distinct from `cover-maker`:
- No artist / author / medium fields — just brand
- Single image (no aspect variants — logos work the same at all sizes by design)
- Different model bias: `ideogram-3-quality` is the default (best embedded text rendering)
- Aesthetic conventions: clean, geometric, often single-color, isolated on background

Distinct from `flyer-maker`:
- No event details — logos are timeless brand artifacts, not event-specific
- No multi-aspect — same mark serves all platforms
- Very minimal composition (logo dominates frame; no headline blocks)

This skill does NOT:
- Generate full brand books (typography systems, color tokens, voice guidelines) — single mark image only
- Vectorize the output to SVG — that's a separate step (open the PNG in Vectornator / Illustrator / Affinity Designer + auto-trace)
- Guarantee trademarkability — outputs may resemble existing marks; check with a trademark search before commercial use
- Remove the background — chain with `bg-remover` if you need transparent PNG
</objective>

## ROLE

Read brand + style preset + palette → pick text-strong model → assemble variant prompts that strongly cue "logo isolated on white background, no shadows, vector aesthetic" → batch execute → save PNGs.

## PIPELINE

1. **Resolve brand**:
   - Required: `--brand "<name>"`
   - Optional: `--tagline "<line>"`

2. **Resolve style preset** — see `references/style-presets.md`:
   - `--style wordmark` — pure typography, no icon (default if brand name ≤2 words)
   - `--style minimal` — geometric mark + optional brand name
   - `--style illustrated` — pictorial / mascot
   - `--style typographic` — custom lettering, ornamental type
   - `--style geometric` — angular / parametric (Bauhaus-like)
   - `--style emblem` — badge / seal / circular composition

3. **Palette hint** (optional but recommended):
   - `--palette "two tones, deep teal + warm cream"` — natural-language palette description
   - Defaults to "monochrome black on white" when omitted

4. **Pick model**:
   - Default: `ideogram-3-quality` — cleanest text rendering in image-gen, perfect for wordmarks
   - Fallback: `gpt-image-2` — better for illustrated + emblem styles with subtle text
   - Override: `--model <slug>`

5. **Compose ONE LLM call** — load [`common/visual-prompt-library/system-prompt.md`](../common/visual-prompt-library/system-prompt.md) (shared SYSTEM_PROMPT) and `buildUserMessage(opts)` with `Mode=logo`, `N=<variants>`, brand + tagline + style preset + palette. Spawn ONE Agent. Receives JSON `{"slides":[{"number":1,"prompt":"..."}]}` — 1–3 sentence prompts cueing isolated-on-white, no background clutter, vector look. Brand name in double quotes. The N prompts share the same content brief but allow stochastic variation in execution (different geometric interpretations, different palette emphasis within the constraint).

6. **Estimate cost + confirm** — inherits `SKILLS_CAROUSEL_BUDGET=1.50`.

7. **Batch execute** — `common.runners.batch.run_batch()`.

8. **Output**:
   ```
   ./generated/logo/<slug>/
     logo-v1.png
     logo-v2.png
     logo-v3.png      (if --variants 3)
     manifest.json
     prompts.md
   ```

## MODES

### Required

- `logo-maker --brand "<name>"`

### Optional content

- `--tagline "<line>"` — secondary text (e.g., "since 2024", "engineered minds")
- `--palette "<hint>"` — natural-language palette description
- `--lang en|ru` — language hint (default: auto-detect)

### Visual

- `--style wordmark|minimal|illustrated|typographic|geometric|emblem` — default wordmark
- `--style-mod "<override>"` — append tweak (e.g., "with a single accent dot in orange")
- `--variants N` — variants (default 4 — logos benefit from more options)
- `--model auto|<slug>` — image provider

### Execution

- `--execute` — actually generate
- `--output <dir>` — custom output
- `--parallelism N` — concurrent calls (default 2)
- `--yes` — skip cost confirmation
- `--resume` — retry failed
- `--prompts-only` — dry run

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/style-presets.md](references/style-presets.md) | Step 2 — exact composition rules per preset, when to pick which, common mistakes |
| [references/model-picker.md](references/model-picker.md) | Step 4 — which model handles which style best, text vs icon strengths |
| [references/troubleshoot.md](references/troubleshoot.md) | When text gets garbled, icon looks generic, palette ignored |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: SaaS wordmark, illustrated mascot, geometric emblem.

## CONSTRAINTS

- **Brand name ≤3 words** for best wordmark rendering. Past 3 words, switch to abbreviation or acronym.

- **Pick ONE style preset per run.** Don't mix wordmark + illustrated in the same batch — variants should explore one direction at a time.

- **More variants = better selection.** Default 4 (vs 2 for cover-maker) because logo selection is inherently subjective.

- **Default to embedded-text-strong model.** `ideogram-3-quality` is the default for a reason — text rendering breaks 90% of generated logos.

- **Vector workflow is a separate step.** Output is raster (PNG). To get SVG: pick best variant → open in Illustrator/Affinity Designer/Vectornator → auto-trace → manually clean up.

- **Isolation hint is built into the prompt.** All variants cue "isolated on white background, no shadows, no environment". To get transparent PNG: chain with `bg-remover`.

- **No multi-aspect output.** A logo works the same across all aspects; produce ONE mark, scale as needed in your design tool.

- **Cost confirm ONCE per batch.** Sum across variants.

- **Trademark check is YOUR responsibility.** The skill cannot verify uniqueness — run a trademark search before commercial use.

- **Never print API keys.** Mask in errors.

## INVOCATION HINTS

When the user says any of:

- "design a logo for X", "logo for my brand", "create a wordmark"
- "brand mark", "company emblem", "monogram"
- "логотип", "сделай лого", "фирменный знак", "эмблема", "брендовый знак"

If the user mentions a domain (SaaS, restaurant, agency), bias `--style` accordingly:
- SaaS / tech → `wordmark` or `geometric`
- Restaurant / artisan → `illustrated` or `emblem`
- Editorial / studio → `typographic`
- Personal brand → `wordmark` with `--style-mod "elegant"`

Defaults: `--style wordmark --variants 4 --model ideogram-3-quality`. Without `--execute`, returns prompts.

This skill is distinct from:
- `cover-maker` — albums/books/podcasts. This is brand identity.
- `flyer-maker` — events. This is timeless brand.
- `thumbnail-maker` — content marketing. This is brand identity.
- `image-prompt` — free-form. This is structured logo conventions with strong text-rendering bias.
