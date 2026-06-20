---
name: meme-card-maker
description: "Meme-format graphic generator — top + bottom text + optional centerpiece image. Impact-style bold typography. 5 templates: drake, distracted-boyfriend, expanding-brain, two-buttons, custom. Optional --base-photo. Default gpt-image-2. Use when: 'meme', 'meme template', 'meme image', 'мем', 'сделай мем'."

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
Meme-format graphic generator. Input: top text + bottom text + optional centerpiece (template or user photo). Output: classic meme-aesthetic image with Impact-style typography.

Distinct from `quote-card-maker`:
- Two text blocks (top + bottom), not one quote + attribution
- Impact-font bold-with-stroke typography (the universal meme look)
- Often references a known meme template (drake, distracted-boyfriend, expanding-brain)
- Aesthetic: meme template, NOT editorial — uglier is often funnier

Distinct from `flyer-maker` / `cover-maker`:
- No event details, no creator metadata
- Different aesthetic vocabulary (Impact font, stroke outline, low-fidelity feel)
- Often references specific cultural meme formats

This skill does NOT:
- Generate animated GIF memes — use `gif-maker` separately
- Watermark / credit the original meme template creator — that's your responsibility
- Verify cultural appropriateness — your judgment
- Translate meme captions — pass in target language
- Place text at PIXEL-perfect template positions — model approximates
</objective>

## ROLE

Read top text + bottom text + optional template hint + optional base photo → pick visual-integration-strong model → assemble prompt cueing Impact-style typography with stroke, meme aesthetic → batch execute → save PNGs.

## PIPELINE

1. **Resolve text**:
   - `--top "<text>"` — top caption (≤8 words, ALL CAPS rendered)
   - `--bottom "<text>"` — bottom caption (≤8 words, ALL CAPS rendered)
   - At least one of top / bottom required

2. **Resolve template** (optional):
   - `--template drake|distracted-boyfriend|expanding-brain|two-buttons|change-my-mind|custom`
   - `drake`: 2-panel "rejects / approves"
   - `distracted-boyfriend`: 3-character composition
   - `expanding-brain`: 4-panel ascending
   - `two-buttons`: sweaty decision
   - `change-my-mind`: seated man with sign
   - `custom`: just the captions on whatever centerpiece the model generates
   - Default: `custom`

3. **Resolve base photo** (optional):
   - `--base-photo <path-or-url>` — use user image as centerpiece
   - Implies `--template custom` (template hints are ignored when base photo is provided)

4. **Pick model**:
   - With `--base-photo`: `nano-banana-pro` (preserves visual, adds caption layer)
   - Template-based: `gpt-image-2` (best at illustration + text rendering)
   - Override: `--model <slug>`

5. **Compose ONE LLM call** — load [`common/visual-prompt-library/system-prompt.md`](../common/visual-prompt-library/system-prompt.md) (shared SYSTEM_PROMPT) and `buildUserMessage(opts)` with `Mode=meme-card`, `N=<variants>`, top + bottom captions + template + optional base photo. Spawn ONE Agent. Receives JSON `{"slides":[{"number":1,"prompt":"..."}]}` — 1–3 sentence prompts with template-specific composition + Impact-style typography cues + meme aesthetic ("white text with thick black stroke, all caps, low-fidelity, slight JPEG artifacts"). Captions in double quotes. See `references/templates.md` for template composition. Library styles via [`common/visual-prompt-library/styles/_index.md`](../common/visual-prompt-library/styles/_index.md).

6. **Estimate cost + confirm** — inherits `SKILLS_CAROUSEL_BUDGET=1.50`.

7. **Batch execute** — `common.runners.batch.run_batch()`.

8. **Output**:
   ```
   ./generated/meme/<slug>/
     meme-v1.png
     meme-v2.png
     manifest.json
     prompts.md
   ```

## MODES

### Required

- `meme-card-maker --top "<text>"` (top) OR `--bottom "<text>"` (bottom; at least one required)

### Optional content

- `--template drake|distracted-boyfriend|expanding-brain|two-buttons|change-my-mind|custom`
- `--base-photo <path-or-url>` — user image as centerpiece
- `--context "<note>"` — situational context to help the model interpret captions
- `--lang en|ru` — language hint (default: en)

### Visual

- `--variants N` — variants (default 3)
- `--model auto|<slug>` — image provider
- `--style-mod "<override>"` — append tweak (e.g., "extra pixelated, deepfried meme aesthetic")
- `--aspect square|portrait|landscape` — composition aspect (default `square` 1080×1080)

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
| [references/templates.md](references/templates.md) | Step 2 — meme template anatomy, composition cues per template |
| [references/typography.md](references/typography.md) | Step 5 — Impact font conventions, stroke outline rules, when to deviate |
| [references/troubleshoot.md](references/troubleshoot.md) | When text doesn't read, template doesn't recognize, etc. |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: drake template developer joke, custom photo meme, expanding-brain progression.

## CONSTRAINTS

- **Captions ≤8 words each.** Past 8, text overflows; Impact-style bold needs space.

- **ALL CAPS rendering.** All meme captions auto-uppercase. If you pass lowercase, it's rendered uppercase. Exception: `--lang ru` keeps mixed case for Cyrillic readability (Cyrillic ALL CAPS is harder to read).

- **Default model is `gpt-image-2`.** Best at illustration + integrated text. `nano-banana-pro` when base photo is provided.

- **Template recognition is approximate.** "Drake" template is approximated by the model — won't be pixel-identical to the original. For exact template: use a meme generator tool (Imgflip, Memegenerator).

- **Cultural sensitivity is YOUR responsibility.** The skill doesn't filter. Don't ship punchy memes about sensitive topics without consideration.

- **Generated memes can resemble copyrighted templates.** Original meme creators rarely enforce, but for commercial use: check the template's original source.

- **Cost confirm ONCE per batch.** Sum across variants.

- **Aspect default is square.** Most platforms display memes 1:1 well. `--aspect portrait` for IG portrait posts; `--aspect landscape` for Twitter inline.

- **Never print API keys.** Mask in errors.

## INVOCATION HINTS

When the user says any of:

- "make a meme", "meme for X", "meme template Y"
- "drake meme", "expanding brain meme", "distracted boyfriend"
- "сделай мем про X", "мем формат Y"
- "сгенерируй мем"

If the user names a template explicitly, set `--template <name>`. If unclear, default `--template custom` (lets the model interpret).

If the user pastes a photo path: `--base-photo <path>` + `--template custom`.

Defaults: `--variants 3 --aspect square --template custom --model gpt-image-2`. Without `--execute`, returns prompts.

This skill is distinct from:
- `quote-card-maker` — text-dominant editorial cards (single quote + attribution)
- `image-prompt` — free-form image gen (no meme conventions)
- `gif-maker` — animated content (memes here are static)
- `flyer-maker` / `cover-maker` — structured professional formats
