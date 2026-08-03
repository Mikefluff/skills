---
name: thumbnail-maker
description: "Produce YouTube / blog / podcast-episode thumbnails. 16:9 default (1280×720, 1920×1080). Face + bold title aesthetic; face-placement variants (left / right / center). Model picked for face preserve + text rendering. Use when: 'YouTube thumbnail', 'blog header image', 'podcast episode cover', 'обложка для youtube видео / поста / эпизода'."

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
Thumbnail generator. Input: title + optional face photo + optional style. Output: N variants at 16:9 (YouTube / blog / podcast-episode thumbnail).

Distinct from `cover-maker`:
- Aspect: ALWAYS 16:9 (no medium variation)
- Aesthetic: bright contrast, large text, exaggerated facial expressions — "thumbnail look"
- Variants vary in FACE PLACEMENT (left / right / center) more than in style

Distinct from `flyer-maker`:
- No event details (date / location)
- Stronger emphasis on the FACE if photo provided
- Different typography conventions (bigger, often colored, with stroke / shadow)

This skill does NOT:
- Generate YouTube banner art (different aspect — use `cover-maker --aspect 2560x1440` or `image-prompt --execute`)
- Generate animated thumbnails — static images only
- Source rights-cleared face references — provide your own
- Optimize for click-through (subjective — picks best of 3-5 manually)
</objective>

## ROLE

Read title + optional face → pick model (text-friendly + ref-capable) → assemble per-variant prompts with face-placement + bold title composition → batch execute → save PNGs.

## PIPELINE

1. **Resolve title**:
   - Required: `--title`
   - 3-7 words is the sweet spot for thumbnails
   - High-energy phrasing works best ("How I Built X in 30 Days", "STOP DOING THIS")

2. **Resolve photo** (optional):
   - `--photo <path-or-url>` — face reference
   - Identity preserve via Nano Banana Pro (default)

3. **Resolve style** — see `references/composition-zones.md`:
   - `--style auto`: picks vibrant + text-friendly styles
   - Default for "YouTube look": `gradient-mesh-modern` or `swiss-grid-poster` with vibrant accent

4. **Face placement variants**:
   - `--placements left,right,center` — default `left,right,center` (3 variants)
   - The same face / title / style; placement varies
   - Maximizes the chance of "the one that works for click"

5. **Pick model**:
   - Photo + face → `nano-banana-pro` (identity preserve)
   - No photo + heavy text → `ideogram-3-quality`
   - Mixed → `gpt-image-2`

6. **Build per-variant prompts** — composition zones per placement (face-left + text-right; face-right + text-left; face-center-bottom + text-top).

7. **Batch execute** — parallel.

8. **Output**:
   ```
   ./generated/thumbnail/<slug>/
     thumbnail-left.png       (face left, text right)
     thumbnail-right.png      (face right, text left)
     thumbnail-center.png     (face center, text top)
     manifest.json
     style-used.md
     prompts.md
   ```

## MODES

### Required

- `thumbnail-maker --title "<text>"`

### Optional

- `--photo <path-or-url>` — face / subject reference
- `--subtitle "<text>"` — secondary line (rare for thumbnails)
- `--style auto|<library-id>` — visual style
- `--style-mod "<override>"` — tweak
- `--placements left,right,center,top,bottom` — comma list (default `left,right,center`)
- `--variants N` — variants per placement (default 1; >1 gives N takes per placement)
- `--lang en|ru` — language hint
- `--model auto|<slug>` — provider
- `--aspect WxH` — override default 1920×1080 (e.g., `1280x720` for low-res)

### Type presets

- `--type youtube` — 1920×1080 (default), bright + bold aesthetic
- `--type blog` — 1200×630 (OG image standard), more editorial
- `--type podcast-episode` — 1920×1080 with podcast-cover-feel

### Execution

- `--execute` — actually generate
- `--output <dir>` — custom output
- `--parallelism N` — concurrent calls
- `--yes` — skip cost confirmation
- `--resume` — retry failed
- `--prompts-only` — dry run

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/model-picker.md](references/model-picker.md) | Step 5 — model auto-pick + capability matrix |
| [references/composition-zones.md](references/composition-zones.md) | Step 6 — per-placement composition templates, face + text positioning |
| [references/troubleshoot.md](references/troubleshoot.md) | When face placement collides with text, contrast issues, click-bait avoidance |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: YouTube tutorial thumbnail with creator face, blog header without photo, podcast episode cover with guest portrait.

## CONSTRAINTS

- **Title 3-7 words.** Past 7, text crowds + becomes unreadable at thumbnail scale.

- **Title is THE focal point.** Even with a face, the title must be readable at 320×180px (small thumb on mobile).

- **One face per thumbnail.** Multiple faces compete; pick one main subject.

- **Face placement variants are stochastic.** "Left" / "right" / "center" guide the model but don't lock pixel-perfect.

- **Bright contrast is the YouTube look.** The default `--style auto` biases toward vibrant + high-contrast styles. Override with `--style photo-editorial-bw` for editorial blog feel.

- **Don't add too many text elements.** Title + optional subtitle = max 2. Past that, thumbnail looks crowded.

- **Reasonable click-bait avoidance.** The skill doesn't enforce "non-clickbait" — that's editorial judgment. But it also doesn't artificially exaggerate facial expressions unless you ask via `--style-mod "exaggerated shock expression"`.

- **One model across the variant set.** Lock per-thumbnail.

- **Cost confirm ONCE.** Sum across placements × variants.

- **Per-platform image sizing**:
  - YouTube: 1280×720 minimum, 1920×1080 high-res
  - Blog OG image: 1200×630
  - Podcast episode art: 1920×1080
  - LinkedIn article cover: 1200×627

- **Never print API keys.** Mask in errors.

## INVOCATION HINTS

When the user says any of:

- "YouTube thumbnail", "blog header image", "podcast episode cover"
- "thumbnail for my video", "create thumbnail variants"
- "обложка для YouTube видео / поста / эпизода"
- "превью для видео"

If unclear, default to `--type youtube`. If user mentions "blog post" → `--type blog`. If "podcast episode" → `--type podcast-episode`.

Defaults: `--type youtube --placements left,right,center --style auto --model auto`. Without `--execute`, returns prompts.

This skill is distinct from:
- `cover-maker` — that's albums/books/podcasts (general "cover" with title + creator). This is specifically thumbnail-aspect content marketing.
- `flyer-maker` — events. This is content marketing.
- `avatar-maker` — single-subject portrait. This adds text + 16:9 framing.
- `image-prompt` — free-form. This is structured thumbnail conventions.
