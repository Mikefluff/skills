---
name: banner-maker
description: "Banner-ad / display-creative generator with standard-size presets: Google Display (leaderboard, medium rectangle, mobile, skyscraper), LinkedIn, OG image, Twitter card, Facebook ad, header. Text-heavy ad aesthetic, ideogram-3-quality default. Use when: 'banner ad', 'display ad', 'OG image', 'Twitter card', 'баннер для рекламы', 'OG-картинка'."

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
Banner-ad generator. Input: headline + CTA + optional subhead + brand + style. Output: N preset-sized banners (Google Display + social platforms).

Distinct from `flyer-maker`:
- Smaller aspect ratios (mostly horizontal, often extreme like 728×90 or 1456×180)
- Dense text + CTA conventions (ad copy, not editorial)
- Per-preset standard sizes (no custom aspects in v1)
- "Ad feel" aesthetic — direct, conversion-focused, brand-loud

Distinct from `cover-maker` / `thumbnail-maker`:
- No artist / author / title-as-subject
- Standard ad-platform sizes (presets, not "medium")
- Includes explicit CTA element
- Very small visual zones in some presets (300×250 has ~80% text)

This skill does NOT:
- Generate animated banners (HTML5 / GIF) — static PNGs only
- A/B test variants for click-through — generate options, you measure
- Place actual brand logo file in pixel-perfect position — model approximates; for exact placement use a vector design tool
- Match exact platform ad-creative spec (file size, character limits) — that's downstream QA
</objective>

## ROLE

Read headline + CTA + brand + style + presets → pick text-strong model → assemble per-preset prompts with composition zones (headline / subhead / CTA / brand mark zone) → batch execute → save PNGs.

## PIPELINE

1. **Resolve content**:
   - Required: `--headline "<text>"` (the dominant text — 3-7 words ideal)
   - Required: `--cta "<text>"` (e.g., "Start free trial", "Learn more", "Get the demo")
   - Strongly recommended: `--brand "<name>"`
   - Optional: `--subhead "<text>"`, `--logo <path-or-url>`

2. **Resolve presets** — multi-preset batch:
   - `--presets og,linkedin-ad,leaderboard` — comma list (default `og,linkedin-ad`)
   - Available presets:
     - `og` — 1200×630 (OG image / Twitter card preview / blog header)
     - `linkedin-ad` — 1200×627 (LinkedIn Sponsored Content)
     - `facebook-ad` — 1200×628 (Facebook News Feed ad)
     - `twitter-card` — 1500×500 (Twitter profile header / large card)
     - `leaderboard` — 1456×180 (Google Display 728×90 scaled 2× for retina)
     - `medium-rectangle` — 600×500 (Google Display 300×250 scaled 2×)
     - `mobile-banner` — 640×200 (Google Display 320×100 scaled 2×)
     - `wide-skyscraper` — 320×1200 (Google Display 160×600 scaled 2×)

3. **Resolve style** — see `references/style-presets.md`:
   - `--style auto`: picks vibrant + text-friendly carousel style
   - `--style swiss-grid-poster` — clean editorial
   - `--style gradient-mesh-modern` — vibrant tech
   - `--style brutalist-grid` — high-contrast / bold

4. **Pick model**:
   - Default: `ideogram-3-quality` — best embedded text
   - Alt: `gpt-image-2` (better for illustrated visual element)
   - With logo reference: `nano-banana-pro` (preserves brand mark)

5. **Compose ONE LLM call** — load [`common/visual-prompt-library/system-prompt.md`](../../common/visual-prompt-library/system-prompt.md) (shared SYSTEM_PROMPT) and `buildUserMessage(opts)` with `Mode=banner`, `N=<presets count>`, headline + CTA + brand + subhead + style + per-preset aspect ratios. Spawn ONE Agent. Receives JSON `{"slides":[{"number":1,"prompt":"..."}]}` — 1–3 sentence prompts per preset following composition-zone hints (see `references/composition-zones.md`: leaderboard/mobile horizontal → headline LEFT + CTA RIGHT; medium-rectangle/OG balanced → headline TOP + visual MIDDLE + CTA BOTTOM; skyscraper vertical → headline TOP + CTA BOTTOM). Headline + CTA + brand in double quotes. Library styles via [`common/visual-prompt-library/styles/_index.md`](../../common/visual-prompt-library/styles/_index.md).

6. **Estimate cost + confirm** — inherits `SKILLS_CAROUSEL_BUDGET=1.50`.

7. **Batch execute** — `common.runners.batch.run_batch()`.

8. **Output**:
   ```
   ./generated/banner/<slug>/
     og.png
     linkedin-ad.png
     leaderboard.png
     manifest.json
     style-used.md
     prompts.md
   ```

## MODES

### Required

- `banner-maker --headline "<text>" --cta "<text>"`

### Recommended

- `--brand "<name>"`

### Optional content

- `--subhead "<text>"`
- `--logo <path-or-url>` — brand mark reference
- `--lang en|ru` — language hint (default: auto-detect)

### Visual

- `--presets og,linkedin-ad,leaderboard,medium-rectangle,mobile-banner,wide-skyscraper,facebook-ad,twitter-card` — comma list (default `og,linkedin-ad`)
- `--style auto|<library-id>` — visual style
- `--style-mod "<override>"` — tweak
- `--variants N` — variants per preset (default 1)
- `--model auto|<slug>` — image provider

### Execution

- `--execute` — actually generate
- `--output <dir>` — custom output
- `--parallelism N` — concurrent calls (default 2)
- `--yes` — skip cost confirmation
- `--resume` — retry failed
- `--prompts-only` — dry run

## STRUCTURED LAYOUT (Ideogram 4 only)

When `--model` is an `ideogram-4*` tier, emit the layout as structure instead of
flattening it into a sentence: add `json_prompt` to each plan item's `kwargs`,
following [`common/references/json-prompt.md`](../../common/references/json-prompt.md).
This skill already knows where every element goes; sending that directly is what
stops the arrangement drifting between variants.

On any v3 tier the provider refuses a `json_prompt` rather than ignoring it, so
keep the prose prompt as written and send nothing extra.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/aspect-presets.md](references/aspect-presets.md) | Step 2 — exact pixel dimensions per preset + platform target |
| [references/composition-zones.md](references/composition-zones.md) | Step 5 — per-preset composition templates (where headline / CTA / visual go) |
| [references/style-presets.md](references/style-presets.md) | Step 3 — which library styles work as ad anchors |
| [references/troubleshoot.md](references/troubleshoot.md) | When text wraps wrong, CTA gets lost, extreme aspects fail |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: SaaS launch (OG + LinkedIn), Google Display leaderboard + medium rectangle, conference event Twitter card.

## CONSTRAINTS

- **Headline ≤7 words.** Past 7, text gets crowded in narrow presets (leaderboard, mobile-banner).

- **CTA is short.** "Start free trial" / "Learn more" / "Get demo". Never longer than 4 words.

- **Brand mark is small.** Logo / wordmark sits in a corner (top-left or bottom-right). Doesn't dominate the composition.

- **Extreme aspects are unforgiving.** Leaderboard (1456×180) and mobile-banner (640×200) have very limited vertical real estate. Headline must fit one line. Skill auto-truncates to 5 words for these presets.

- **Default model is text-rendering-strongest.** `ideogram-3-quality` is the default — ad banners live and die on legibility.

- **One brand voice per batch.** All presets share the same headline / CTA / style. Run multiple batches for A/B tests.

- **Cost confirm ONCE per batch.** Sum across presets × variants.

- **Per-platform spec compliance is YOUR responsibility.** Google Display has limits (150KB file size, JPG/PNG/GIF). LinkedIn caps at 5MB. We output PNG — you may need to compress before upload.

- **Logo file is approximated, not pixel-replicated.** Model places "logo region" near a corner; exact mark replacement is a downstream design-tool step.

- **Never print API keys.** Mask in errors.

## INVOCATION HINTS

When the user says any of:

- "banner ad", "display ad", "Google Display creative"
- "OG image", "Twitter card", "LinkedIn ad creative"
- "Facebook ad image", "social ad"
- "баннер для рекламы", "OG-картинка", "креатив для рекламы"
- "превью для шарения" / "preview image for sharing"

Map "social preview / OG / шарилка" → `og` preset (1200×630). Map "LinkedIn ad" → `linkedin-ad`. Map "Google Display" → `leaderboard` + `medium-rectangle` (the two most-used IAB sizes). Map "Twitter card / header" → `twitter-card`.

Defaults: `--presets og,linkedin-ad --variants 1 --style auto --model ideogram-3-quality`. Without `--execute`, returns prompts.

This skill is distinct from:
- `cover-maker` — book/album/podcast covers with title+creator
- `flyer-maker` — event posters with date+location+CTA
- `thumbnail-maker` — 16:9 content marketing with face+title
- `logo-maker` — brand mark only (no headline/CTA)
- `quote-card-maker` — text-dominant (no CTA / brand emphasis)
- `image-prompt` — free-form (no platform presets)
