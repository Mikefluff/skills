---
name: flyer-maker
description: "Turn event details (title / date / location / CTA) plus optional photo into a poster / flyer / social-event-graphic with embedded text in a chosen style. Multi-aspect: portrait, square, story, landscape, a4. Use when: 'make a flyer for X', 'event poster', 'workshop flyer', 'meetup poster', 'афиша', 'плакат', 'флайер для мероприятия'."

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
End-to-end flyer / poster generator. Input: event details (title, optional date / location / CTA) plus an optional user-supplied photo. Output: N single-image variants at different aspect ratios, each with the event details embedded as text + the photo integrated (if provided) + a consistent visual style.

This skill orchestrates three lower-level components:
1. `image-prompt` style anchor + composition-zone vocabulary
2. `common/runners` execute layer — multi-aspect batch generation via the chosen image provider
3. `common/style-library/carousel/` — reuses the 24 carousel visual styles as the visual vocabulary (poster styles overlap heavily with editorial carousel styles)

Use when the user wants a finished flyer image — not just a prompt. Without `--execute`, returns the assembled prompts; with `--execute`, generates the actual PNGs.

This skill does NOT:
- Generate animated flyers (use `reel-builder` for motion)
- Render print-ready CMYK / 300DPI files — outputs are RGB at standard digital resolutions (1080 / 1240 px). For print: open the PNG in a real DTP tool (Affinity / InDesign / Photoshop) and convert.
- Compose multi-image collages — single image per aspect.
- Generate QR codes (deferred to v2.5.x — if you need a QR, generate separately and overlay manually).
- Search Eventbrite / Meetup / Luma for event metadata — you provide title / date / location explicitly.
- Replace a designer's judgment on layout — the composition zones are starter conventions; tweak via prompt iteration.
</objective>

## ROLE

Read the event details + optional photo + optional style → pick a model (text-friendly + multi-ref-capable if photo provided) → assemble per-aspect prompts with composition zones filled in → batch execute via the image provider → save PNGs + manifest → print paths.

## PIPELINE

1. **Resolve event details**:
   - Required: `--title`
   - Strongly recommended: at least one of `--date`, `--location`, or `--cta` (a flyer without a single detail is just a styled portrait)
   - Optional: `--subtitle`, `--time` (can be merged with date)

2. **Resolve photo** (optional):
   - `--photo <path-or-url>`: passed as reference image to the chosen model.
   - Multi-ref capable models needed (Nano Banana Pro / Flux Kontext / gpt-image-2 / Ideogram 3 / Seedream 5.0).
   - If `--photo` provided AND `--model auto`: skill picks a ref-capable model.
   - If `--photo` provided AND `--model <slug>` that can't handle refs: warn + auto-substitute, or exit if user passed `--strict`.

3. **Resolve style** — see `references/event-details.md`:
   - `--style <library-id>`: load from `common/style-library/carousel/<id>.md`. Use the `Style anchor (text-in-image mode)` block (flyers always have text).
   - `--style auto`: pick from library based on the event type implied by the title + the chosen tone (formal, casual, indie, corporate). Algorithm same as carousel-builder.
   - `--style-mod "<override>"`: append a tweak to the anchor.

4. **Pick model** — see `references/model-picker.md`:
   - `--model auto`:
     - Photo provided + identity preserve critical (named speaker) → `nano-banana-pro`
     - Photo provided + brand-style transfer needed → `flux-2-pro` or `seedream-5`
     - Photo provided + Latin/CJK text needed → `gpt-image-2`
     - No photo + text-heavy → `ideogram-3-quality`
     - No photo + photoreal style → `nano-banana-pro` or `flux-2-pro`
   - `--model <slug>`: explicit override.
   - ONE model for all aspects (consistency across the family).

5. **Build per-aspect prompts** — see `references/composition-zones.md`:
   Each aspect has a composition template with three zones:
   - **Headline zone** (top 20-25%): title in large bold typography
   - **Visual zone** (middle 50-55%): photo integration if provided, else style anchor visual
   - **Details zone** (bottom 25-30%): date + location + CTA in smaller typography

   The prompt assembly per aspect:
   ```
   <style anchor (text-in-image mode)>

   Composition: <aspect-specific zone template>

   Embed text:
     Headline: "<TITLE>"
     <Subtitle if present>
     <Date if present>
     <Location if present>
     <CTA if present>

   Aspect ratio: <portrait|square|story|landscape|a4>
   Size: <pixel dimensions>
   ```

6. **Estimate cost + confirm** — sum aspects × variants. Under default carousel budget ($1.50) → no prompt; over → ask once.

7. **Batch execute** — `common.runners.batch.run_batch()`:
   - Parallelism default 2 (each aspect = ~5-10s API call; running 3 in parallel rarely problematic but rate-limit safety)
   - Manifest updated after each aspect
   - `--resume` retries only failed aspects

8. **Output**:
   ```
   ./generated/flyer/<event-slug>/
     portrait.png            (1080×1350)
     square.png              (1080×1080)
     story.png               (1080×1920)
     landscape.png           (1920×1080, if requested)
     a4.png                  (1240×1754, if requested)
     manifest.json
     style-used.md
     prompts.md
   ```

   stdout last lines:
   ```
   Flyer: ./generated/flyer/<event-slug>/  (N/M aspects succeeded)
   Files: portrait.png · square.png · story.png
   ```

## MODES

### Required

- `flyer-maker --title "<text>"`

### Strongly recommended (provide ≥1)

- `--date "<text>"` — free-form date / time
- `--location "<text>"`
- `--cta "<text>"` — call to action (e.g., "Tickets: link in bio", "RSVP via DM", "Free entry")

### Optional content

- `--subtitle "<text>"` — secondary line under the title
- `--photo <path-or-url>` — reference image to embed (speaker face, venue shot, theme image)
- `--lang en|ru` — language of embedded text (default: matches the language of `--title`)

### Visual

- `--style auto|<library-id>` — visual style (uses carousel style library; default auto)
- `--style-mod "<override>"` — append a tweak to the chosen anchor
- `--aspects portrait,square,story,landscape,a4` — comma list (default: `portrait,square,story`)
- `--variants N` — N takes per aspect (default 1)
- `--model auto|<slug>` — image provider (default auto)

### Execution

- `--execute` — actually generate (else returns plan + prompts)
- `--output <dir>` — custom output (default `./generated/flyer/<event-slug>/`)
- `--parallelism N` — concurrent API calls (default 2, max 4)
- `--yes` — skip cost confirmation
- `--resume` — retry only failed aspects
- `--strict` — fail (don't auto-substitute) if `--model <slug>` can't handle `--photo`

### Inspection

- `--prompts-only` — print plan + per-aspect prompts, exit (no API call)
- `--cost-only` — print total cost, exit
- `--check` — validate env vars + library files exist

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
| [references/event-details.md](references/event-details.md) | Step 1 — required vs. optional fields, formatting conventions for date/time/location |
| [references/aspect-presets.md](references/aspect-presets.md) | Step 5 — pixel dimensions, social-platform-specific recommendations |
| [references/composition-zones.md](references/composition-zones.md) | Step 5 — headline/visual/details zone layouts per aspect, anti-clutter rules |
| [references/model-picker.md](references/model-picker.md) | Step 4 — auto-pick decision tree, capability matrix, cost preview |
| [references/troubleshoot.md](references/troubleshoot.md) | When text renders wrong, photo doesn't integrate, layout collapses |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: solo founder workshop with embedded speaker photo (Nano Banana Pro), conference poster without photo using bold typographic Swiss style (Ideogram 3 Quality), three-aspect launch event with Kinfolk-minimal aesthetic + RU+EN bilingual variant (gpt-image-2).

## CONSTRAINTS

- **Embedded text on image is the differentiator.** Without text rendering, this is just a styled image — use `image-prompt` directly. The skill defaults to text-friendly models because the title + details MUST land readable.

- **Headlines ≤8 words.** Past 8 words, even the best text-in-image models distort. The validator warns; the prompt assembly trims if longer.

- **One model for all aspects.** Mixing providers across the portrait / square / story batch breaks visual cohesion. Lock per-flyer.

- **One style for all aspects.** Same anchor across the batch.

- **Photo identity preserve uses Nano Banana Pro by default.** For speaker portraits in a flyer, NBP is the safest pick. Override with `--model gpt-image-2` if you need text + photo blended in a stylized layout.

- **Aspect compositions differ.** A 1080×1350 portrait and a 1080×1920 story have different headline/details zones — see `references/composition-zones.md`. Don't assume the prompt is identical across aspects.

- **Cost confirm ONCE per batch.** Sum across all aspects + variants.

- **`--prompts-only` is the safety dry-run.** Always recommend it for first iteration — flyers iterate on copy + composition more than on style.

- **Manifest updates after every aspect.** `--resume` retries only failed ones.

- **No QR codes in v1.** If you need a QR (ticketing link, venue map), generate separately and overlay in a real image editor.

- **No print-ready output in v1.** Outputs are RGB PNG at digital resolutions. For print: open in a DTP tool and convert.

- **Event-slug derived from title.** Default: kebab-case of title, max 40 chars + date suffix. Override via `--output <dir>`.

- **`--photo` accepts local paths AND URLs.** Provider routes accordingly.

- **Never print API keys.** Mask in errors.

- **Output dir is `./generated/flyer/<event-slug>/`** by default.

## INVOCATION HINTS

When the user says any of:

- "make a flyer for X", "event poster for Y", "workshop flyer"
- "meetup poster", "concert poster", "exhibition flyer"
- "use this photo on a flyer", "put my face on a workshop poster"
- "flyer with embedded date and location"
- "промо для мероприятия", "афиша", "плакат", "флайер"
- "сделай афишу для воркшопа / встречи / митапа"
- "афиша с моей фоткой"

Defaults: `--aspects portrait,square,story --style auto --model auto`. Without `--execute`, returns prompts + plan; with `--execute`, generates files.

If the user mentions a specific platform (Instagram → emphasize 4:5 portrait + 9:16 story; LinkedIn → emphasize 1:1 square + 1.91:1 landscape; print → suggest A4 aspect), bias `--aspects` accordingly.

This skill is **distinct from**:
- `image-prompt` — that writes prompts for any image; this orchestrates a multi-aspect batch for flyers specifically
- `carousel-builder` — that's N-slide narrative; this is 1-image-per-aspect event posters
- `reel-builder` — that's video; this is static images

For album / book / podcast covers: use `image-prompt --execute` with a simpler one-shot prompt (no event-details structure). A dedicated `cover-maker` skill is planned (see ROADMAP).

For YouTube thumbnails: `image-prompt --execute` with 16:9 size + face + bold title. A dedicated `thumbnail-maker` skill is planned.
