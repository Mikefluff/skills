---
name: cover-maker
description: "Orchestrator skill — turn cover metadata (title / creator / subtitle / medium) into an album / book / podcast / report / deck / magazine cover. Wraps image-prompt --execute + the carousel style library (24 visual styles) + the runner's batch executor. Picks aspect by medium (album 1:1, book 2:3 portrait, podcast 1:1, magazine 2:3, report 1:√2 A4). Multi-variant output. Optional photo / artwork reference. Outputs: ./generated/cover/<slug>/<medium>.png + manifest.json. Use when the user says 'album cover', 'book cover', 'podcast cover', 'report cover', 'обложка для альбома / книги / подкаста / отчёта'."
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
Cover image generator. Input: cover metadata (title + creator + optional subtitle + medium type) plus optional reference image (artwork, photo, logo). Output: N variants in the medium's native aspect.

Distinct from `flyer-maker`:
- No event details (date / location / CTA) — covers have title + creator
- Aspect varies by MEDIUM, not platform (album = 1:1; book = 2:3 portrait; podcast = 1:1; magazine = 2:3 magazine cover; report = 1:√2 A4)
- Different composition conventions (titles dominate; minimal supporting metadata)

Distinct from `image-prompt`:
- Structured input (medium / title / creator) vs free-form prompt
- Multi-variant batch (default 2-3 takes per medium)
- Auto-picks model based on text needs + style

This skill does NOT:
- Generate physical book bindings / album sleeves / cover spreads (back covers, spines) — single front-cover image only
- Generate ISBN barcodes / catalog numbers — overlay manually in your editor
- Source rights-cleared imagery — provide your own photo via --photo
- Cover scaling for specific marketplace dimensions (Amazon KDP / Spotify Canvas / Apple Music) — generate at the medium's standard aspect, resize/upscale in a DTP tool
</objective>

## ROLE

Read metadata + medium + optional photo + style → pick aspect from medium → pick text-friendly + (if photo) multi-ref-capable model → assemble per-variant prompts with composition zones → batch execute → save PNGs.

## PIPELINE

1. **Resolve metadata**:
   - Required: `--title`
   - Strongly recommended: `--creator` (album artist / book author / podcast host / report org)
   - Optional: `--subtitle`, `--photo <path-or-url>`

2. **Resolve medium** — picks aspect:
   - `--medium album` → 3000×3000 square (Spotify / Apple Music album art)
   - `--medium book` → 1600×2400 (2:3 portrait — Amazon KDP standard)
   - `--medium podcast` → 3000×3000 square (Apple Podcasts spec)
   - `--medium magazine` → 1600×2400 (2:3 — print magazine cover convention)
   - `--medium report` → 1240×1754 (A4 portrait at 150 DPI)
   - `--medium deck-cover` → 1920×1080 (16:9 — slide deck title slide)
   - `--medium linkedin-doc` → 1080×1080 (1:1 — LinkedIn document)
   - Custom: `--aspect WxH`

3. **Resolve style** — see `references/cover-types.md`:
   - `--style auto`: picks based on medium + content tone
   - `--style <library-id>`: explicit from carousel library

4. **Pick model**:
   - Heavy embedded text (covers always have text) → `ideogram-3-quality` (default) or `gpt-image-2`
   - Photo reference + identity → `nano-banana-pro`
   - Photo reference + brand palette → `flux-2-pro`
   - Photoreal magazine-style cover → `imagen-4-ultra`

5. **Build per-variant prompts** — see `references/composition-zones.md`:
   - Different mediums = different composition templates
   - Album: title + artist centered or stacked
   - Book: title block + author at bottom OR top, dominant visual middle
   - Podcast: title + host name on a single bold layout
   - Magazine: masthead at top + cover line + image dominant

6. **Estimate cost + confirm** — inherits `SKILLS_CAROUSEL_BUDGET=1.50`.

7. **Batch execute** — `common.runners.batch.run_batch()`.

8. **Output**:
   ```
   ./generated/cover/<slug>/
     <medium>-v1.png
     <medium>-v2.png
     <medium>-v3.png    (if --variants 3)
     manifest.json
     style-used.md
     prompts.md
   ```

## MODES

### Required

- `cover-maker --title "<text>" --medium album|book|podcast|magazine|report|deck-cover|linkedin-doc`

### Recommended

- `--creator "<name>"` — artist / author / host / org

### Optional content

- `--subtitle "<text>"` — secondary line
- `--photo <path-or-url>` — reference image
- `--lang en|ru` — language hint (default: auto-detect from title)

### Visual

- `--style auto|<library-id>` — visual style
- `--style-mod "<override>"` — append a tweak
- `--variants N` — variants (default 2)
- `--aspect WxH` — custom aspect (overrides medium default)
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
| [references/cover-types.md](references/cover-types.md) | Step 1-2 — per-medium conventions, what fields are needed, typography expectations |
| [references/aspect-presets.md](references/aspect-presets.md) | Step 2 — exact pixel dimensions per medium + platform target |
| [references/composition-zones.md](references/composition-zones.md) | Step 5 — per-medium composition templates (album / book / podcast / magazine / report / deck) |
| [references/model-picker.md](references/model-picker.md) | Step 4 — model auto-pick, when to override |
| [references/troubleshoot.md](references/troubleshoot.md) | When text renders wrong, layout fails, photo doesn't integrate |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: album cover with reference artwork, business book cover with author photo, podcast cover with bold typographic style.

## CONSTRAINTS

- **Title is the dominant element.** Cover composition prioritizes title legibility. Keep titles ≤6 words for best results.

- **Creator name is recommended but optional** — for an album with featured artists, list one main creator and put the rest in `--subtitle`.

- **One medium per run.** Don't mix album + book in the same call. Run twice if you need both.

- **One style for variants.** All variants share the same anchor; they differ in stochastic interpretation, not in style.

- **Embedded text quality is paramount.** Default to `ideogram-3-quality` for any text-heavy cover. The model picker enforces this.

- **Photo-reference covers**: pair `--photo` with `nano-banana-pro` (identity) or `flux-2-pro` (brand palette transfer).

- **Cost confirm ONCE per batch.** Sum across variants.

- **No print-bleed marks / crop guides.** Output is the cover image only. For physical print: import to InDesign / Affinity Publisher for bleed + crop marks.

- **Backside / spine: out of scope.** Single front-cover image only.

- **Never print API keys.** Mask in errors.

## INVOCATION HINTS

When the user says any of:

- "album cover for X", "book cover for Y", "podcast cover", "report cover"
- "magazine cover", "deck cover slide", "LinkedIn doc cover"
- "обложка для альбома / книги / подкаста / отчёта"
- "сделай обложку для X"

If the medium isn't clear from context, ask once. Default if unspecified: `album` (most common request).

If the user mentions a platform (Spotify → 3000×3000 album; Amazon KDP → 2:3 portrait book; Apple Podcasts → 3000×3000 podcast), bias `--medium` accordingly.

Defaults: `--medium album --variants 2 --style auto --model auto`. Without `--execute`, returns prompts.

This skill is distinct from:
- `flyer-maker` — events with date/location, NOT covers with title/creator
- `image-prompt` — free-form image generation; this is structured covers
- `avatar-maker` — single subject portrait, NOT title-driven cover
- `thumbnail-maker` — 16:9 with bold title for content marketing, NOT artist/author covers
