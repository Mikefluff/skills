---
name: cover-maker
description: "Turn cover metadata (title / creator / subtitle / medium) into an album, book, podcast, report, deck, or magazine cover. Aspect auto-picked per medium. Optional photo/artwork reference. Multi-variant output. Use when: 'album cover', 'book cover', 'podcast cover', 'report cover', 'обложка для альбома / книги / подкаста / отчёта'."

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

## PIPELINE (v2.14.0+ — shared visual-prompt chain, same as carousel-builder)

1. **Resolve metadata**:
   - Required: `--title`
   - Strongly recommended: `--creator` (album artist / book author / podcast host / report org)
   - Optional: `--subtitle`, `--photo <path-or-url>`, `--brand-colors "<list>"`

2. **Resolve medium** — picks aspect + composition convention:
   - `--medium album` → 3000×3000 square (Spotify / Apple Music album art)
   - `--medium book` → 1600×2400 (2:3 portrait — Amazon KDP standard)
   - `--medium podcast` → 3000×3000 square (Apple Podcasts spec)
   - `--medium magazine` → 1600×2400 (2:3 — print magazine cover convention)
   - `--medium report` → 1240×1754 (A4 portrait at 150 DPI)
   - `--medium deck-cover` → 1920×1080 (16:9 — slide deck title slide)
   - `--medium linkedin-doc` → 1080×1080 (1:1 — LinkedIn document)
   - Custom: `--aspect WxH`

3. **Resolve style** — see [`common/visual-prompt-library/styles/_index.md`](../common/visual-prompt-library/styles/_index.md) (shared 13-style library):
   - `--style auto` (default): the LLM picks from the library based on title + creator + medium + tone.
   - `--style <name>`: explicit from the 13-style library (BIOTECH / CYBER-NOIR / BRUTALIST / VAPORWAVE / MILITARY / SCIENTIFIC / STREETWEAR / ART-DECO / BLUEPRINT / GRUNGE / GLAMOUR / NATURE / ADVENTURE).
   - `--style custom "<desc>"`: free-text override passed verbatim.

4. **Pick model** — see `references/model-picker.md`:
   - Heavy embedded text (covers always have text) → `ideogram-3-quality` (default) or `gpt-image-2`.
   - Photo reference + identity → `nano-banana-pro`.
   - Photo reference + brand palette → `flux-2-pro`.
   - Photoreal magazine-style cover → `imagen-4-ultra`.

5. **Compose ONE LLM call** — load [`common/visual-prompt-library/system-prompt.md`](../common/visual-prompt-library/system-prompt.md) (the shared SYSTEM_PROMPT) and `buildUserMessage(opts)` with:
   ```
   Mode: cover
   Number of images to generate (N): <variants, default 2>
   Aspect ratio: <medium aspect>
   Topic / theme: <title + creator context>
   Title: "<title verbatim>"
   Creator: "<creator verbatim>"
   Subtitle (optional): "<subtitle verbatim>"
   Medium: <medium>
   Visual style: <library entry full description OR customStyle text>
   [Optional: brand colors, photo reference flag, character description]

   Respond with a JSON object: { "slides": [...] }
   ```

   Spawn ONE Agent (subagent_type=`general-purpose`) with `system=SYSTEM_PROMPT` and `user=<built message>`. The agent returns JSON `{"slides":[{"number":1,"prompt":"..."},...]}` — N short (1–3 sentence) cover prompts, title + creator quoted, layout language, no carousel chrome (single-image mode).

   **Discipline (all enforced in the SYSTEM_PROMPT)**:
   - ONE LLM call, not per-variant subagents.
   - Each prompt 1–3 sentences.
   - Title + creator + subtitle in double quotes exactly.
   - No meta-labels (no `TITLE:` / `AUTHOR:` literals).
   - Title-dominant composition; creator in a consistent secondary zone.

   **Retry on bad output**: if malformed JSON or wrong N, re-run once with stricter reminder.

6. **Assemble plan.json** — items `[{index, label, prompt, kwargs:{size, image_url}}]`. `prompt` is LLM-returned text. `image_url` points to `--photo` when provided.

7. **Estimate cost + confirm** — inherits `SKILLS_CAROUSEL_BUDGET=1.50`.

8. **Batch execute** — `python3 -m common.runners.cli.cover --plan-file <plan.json> --yes` (or via `scripts/run.py`).

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

### Two-pass typography (v2.11.0 fallback — opt-in only)

The default v2.14.0 chain is LLM-prompt-then-image (text rendered by the image model, baked into the picture — same chain as carousel-builder). For book covers where text must be pixel-perfect (publisher imprint precision, multilingual layouts the model can't render), opt in with:

- `--typeset overlay` — runs the legacy two-pass: AI generates a TEXT-FREE background (per the imprint's prompt fragment) + Pillow typography composer overlays title + creator with bundled OFL fonts at the imprint's proper layout fractions.
- `--imprint nyrb-classics|penguin-marber-grid|mit-essential-knowledge|picador-modern|faber-modernist` — design-system preset for the typography composer (only with `--typeset overlay`).
- `--genre literary-fiction|thriller|non-fiction|academic|memoir|poetry|...` — auto-picks imprint (only with `--typeset overlay`). Mapping in `common/runners/cover_imprints.py:GENRE_DEFAULT_IMPRINT`.
- Default for all mediums: `--typeset ai` (single-pass, LLM writes the prompt, image model renders title + creator inside the image).

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
| [references/imprints.md](references/imprints.md) | When `--imprint` is set — full per-imprint design system specs (layout fractions, typography family, palette, prompt fragment) |
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
