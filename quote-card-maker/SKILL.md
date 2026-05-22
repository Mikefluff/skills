---
name: quote-card-maker
description: "Quote card / aphorism graphic generator — bold short text + attribution + minimal visual. Output: text-dominant composition where typography IS the image (1080×1080 square, 1080×1350 portrait, 1080×1920 story). Wraps image-prompt --execute + the carousel style library (24 visual styles) with a text-friendly bias. Default model: ideogram-3-quality (cleanest embedded text). Multi-aspect for Twitter / Instagram / LinkedIn quote posts. Outputs: ./generated/quote/<slug>/<aspect>.png + manifest.json. Use when the user says 'quote card', 'aphorism graphic', 'pull quote post', 'цитата для соцсетей', 'афоризм на картинке', 'постер с цитатой'."
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
Quote-card generator. Input: short text (1-3 sentences) + attribution + optional style. Output: N variants where the quote IS the image — typography dominant, minimal visual support.

Distinct from `cover-maker`:
- No medium / title / creator — just a quote and an attribution
- Text is the SUBJECT, not the label on top of an image
- Different composition: type takes 60-80% of the frame
- Default to text-rendering-strongest model

Distinct from `flyer-maker`:
- No event details — quote cards are timeless
- No CTA / date / location — just text + attribution
- Different aesthetic: editorial, not promotional

This skill does NOT:
- Generate long-form text graphics (>3 sentences) — for that, use `carousel-builder` (multi-slide)
- Translate quotes — pass the quote in the target language
- Verify attribution authenticity (Mark Twain didn't say half the things he's quoted on) — that's your responsibility
- Add watermarks / brand bumpers — append in your editor if needed
</objective>

## ROLE

Read quote + attribution + style → pick text-strong + clean-typography-capable model → assemble per-aspect prompts where typography dominates 60-80% of the frame → batch execute → save PNGs.

## PIPELINE

1. **Resolve quote**:
   - Required: `--quote "<text>"`
   - 1-3 sentences, ideally ≤20 words
   - Required-recommended: `--attribution "<name>"` (or `--anonymous` for unattributed)

2. **Resolve aspect** — multi-aspect by default:
   - `--aspects square,portrait,story` — comma list (default `square`)
   - `square` — 1080×1080 (Twitter / IG square / LinkedIn)
   - `portrait` — 1080×1350 (IG portrait — Vogue/editorial vibe)
   - `story` — 1080×1920 (IG Stories / Reels cover)
   - `landscape` — 1200×630 (Twitter header / OG image)

3. **Resolve style** — see `references/style-presets.md`:
   - `--style auto`: picks text-friendly styles from carousel library
   - `--style swiss-grid-poster` — Swiss grid typography (default text-friendly)
   - `--style editorial-magazine` — magazine layout
   - `--style monochrome-bold` — high-contrast B&W
   - `--style minimal-serif` — Bodoni-esque serif on cream
   - Or any carousel library style with text-anchor strength

4. **Pick model**:
   - Default: `ideogram-3-quality` (text leader)
   - Override: `--model gpt-image-2` (when style demands a textured visual element)

5. **Compose ONE LLM call** — load [`common/visual-prompt-library/system-prompt.md`](../common/visual-prompt-library/system-prompt.md) (shared SYSTEM_PROMPT, same as carousel-builder / cover-maker) and `buildUserMessage(opts)` with `Mode=quote-card`, `N=<aspects count>`, quote + attribution + style + aspect ratios. Spawn ONE Agent with that system + user. Receives JSON `{"slides":[{"number":1,"prompt":"..."}]}` — 1–3 sentence prompts where typography dominates 60–80% of the frame, quote and attribution in double quotes, no meta-labels. Library styles via [`common/visual-prompt-library/styles/_index.md`](../common/visual-prompt-library/styles/_index.md).

6. **Estimate cost + confirm** — inherits `SKILLS_CAROUSEL_BUDGET=1.50`.

7. **Batch execute** — `common.runners.batch.run_batch()`.

8. **Output**:
   ```
   ./generated/quote/<slug>/
     square.png
     portrait.png
     story.png
     manifest.json
     style-used.md
     prompts.md
   ```

## MODES

### Required

- `quote-card-maker --quote "<text>" --attribution "<name>"`

### Optional content

- `--anonymous` — explicit no-attribution mode
- `--lang en|ru` — language hint (default: auto-detect)
- `--context "<note>"` — e.g., "from his 1843 journal", "essay on freedom"

### Visual

- `--aspects square,portrait,story,landscape` — comma list (default `square`)
- `--style auto|<library-id>` — visual style
- `--style-mod "<override>"` — tweak (e.g., "with single accent line in vermillion")
- `--variants N` — variants per aspect (default 1)
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
| [references/style-presets.md](references/style-presets.md) | Step 3 — which library styles work best as quote-card anchors, when to pick which |
| [references/composition-zones.md](references/composition-zones.md) | Step 5 — per-aspect text-dominant composition templates |
| [references/troubleshoot.md](references/troubleshoot.md) | When text wraps wrong, attribution dominates, style fights legibility |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: philosophy quote in editorial style, marketing aphorism in vibrant style, RU literature quote in minimal serif style.

## CONSTRAINTS

- **Quote ≤20 words.** Past 20 words, text gets too small to read on mobile. Long quotes belong in carousel-builder (multi-slide).

- **One quote per card.** Don't mix multiple quotes — that's a carousel.

- **Attribution is short.** "— Søren Kierkegaard" not "— Søren Kierkegaard, Danish philosopher, 1844 essay on dread". Add context via `--context` (it goes into prompt as a separate styling hint).

- **Typography dominates.** All variants reserve 60-80% of the frame for the quote text. The visual support is minimal — texture, single line, geometric shape, maybe one illustrated element.

- **Default model is text-rendering-strongest.** `ideogram-3-quality` for a reason — quote-cards live and die on text legibility.

- **Multi-aspect = same quote across formats.** All aspects share the same quote/attribution; composition adapts.

- **Cost confirm ONCE per batch.** Sum across aspects × variants.

- **Quote authenticity is YOUR responsibility.** The skill doesn't verify attributions.

- **Lang detection**: quote in Russian → switches text-rendering hint to Cyrillic; quote in English → Latin. Mixed-script quotes work but render less reliably.

- **Never print API keys.** Mask in errors.

## INVOCATION HINTS

When the user says any of:

- "quote card", "aphorism graphic", "pull quote post"
- "make a quote post for Instagram / Twitter"
- "цитата для соцсетей", "афоризм на картинке", "постер с цитатой"
- "сделай цитату Кьеркегора в монохромном стиле"

If the user pastes a long quote (>20 words), suggest carousel-builder instead. If the user wants multiple quotes, suggest a loop or carousel.

Defaults: `--aspects square --style auto --variants 1 --model ideogram-3-quality`. Without `--execute`, returns prompts.

Default style picks (`--style auto`):

- Quote feels philosophical / literary → `minimal-serif` or `editorial-magazine`
- Quote feels marketing-y / motivational → `swiss-grid-poster` or `gradient-mesh-modern`
- Quote feels punchy / contrarian → `monochrome-bold` or `brutalist-grid`

This skill is distinct from:
- `carousel-builder` — multi-slide narrative. This is single card.
- `cover-maker` — albums/books with title+creator. This is text-as-subject.
- `flyer-maker` — events. This is timeless quotes.
- `image-prompt` — free-form. This is structured typography-dominant cards.
