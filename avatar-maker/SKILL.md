---
name: avatar-maker
description: "Turn a user photo into N profile-pic / headshot / avatar variants in a consistent style. Identity-preserve focused, defaults to nano-banana-pro. Multi-aspect (square, square-tight, cover 4:5, story 9:16). Use when: 'make me an avatar', 'profile picture from this photo', 'headshot variants', 'LinkedIn profile pic', 'аватарка', 'портрет', 'хедшот'."

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
Headshot / profile-pic / avatar generator. Input: user photo (REQUIRED) + optional style + optional aspect set. Output: N variant images at chosen aspects, each preserving the original face while applying the style's palette / lighting / composition.

Distinct from flyer-maker / carousel-builder:
- Single subject focus (the face). No event details, no narrative split, no embedded text.
- Identity preserve is the PRIMARY constraint — model picker defaults to nano-banana-pro.
- Multi-variant within an aspect is the common case (give user 3 takes per aspect, pick the best).

This skill does NOT:
- Generate avatars from text alone — `--photo` is required (use `image-prompt` for text-only portrait generation).
- Render text overlays (name / handle / title) — avatars are visual only. Add text in your design tool if needed.
- Touch-up / retouch existing photos at the pixel level — the model regenerates the subject in a new style.
- Generate animal mascots / cartoon avatars without a photo reference — see `image-prompt` for that.
- Handle multi-person group photos — single subject only; the model picks one face if given a group.
</objective>

## ROLE

Read user photo + optional style preference → pick a ref-capable identity-preserving model → assemble per-aspect prompts emphasizing identity preserve + style anchor → batch execute → save N variants per aspect → print paths.

## PIPELINE

1. **Resolve photo** (required):
   - `--photo <path-or-url>`: local file or remote URL.
   - Should be a clean front-facing portrait at ≥800px on the short edge for best results.

2. **Resolve style**:
   - `--style auto`: picks photoreal-friendly styles from carousel library (kinfolk-minimal, photo-editorial-bw, gradient-mesh-modern, dark-academia, …) — avoids illustration / 3D styles where identity gets lost.
   - `--style <library-id>`: explicit library entry. Uses the `Style anchor (carousel)` block.
   - `--style-mod "<override>"`: tweak.

3. **Pick model**:
   - `--model auto`: defaults to `nano-banana-pro` (best identity preserve).
     - If identity preserve isn't the priority (style transfer first) → `flux-2-pro` or `seedream-4.5`.
     - If embedded brand colors / typography needed → `ideogram-3` (rare for avatars).
   - `--model <slug>`: override.
   - ONE model across all aspects + variants.

4. **Build per-aspect prompts**:
   ```
   <style anchor (carousel)>

   Portrait of the person from the reference image. Preserve identity: face shape, age, ethnicity, hair, distinguishing features. Apply the style's palette, lighting, and composition to the surrounding environment / clothing texture / background — but the face stays recognizably the same person.

   Framing: <aspect-specific>
   Aspect ratio: <ratio>
   Size: <pixel dimensions>
   ```

5. **Estimate cost + confirm** — `aspects × variants × per-image cost`. Default 1 aspect × 3 variants × $0.05 = $0.15. Under budget.

6. **Batch execute** — `common.runners.batch.run_batch()`. Parallelism 3.

7. **Output**:
   ```
   ./generated/avatar/<slug>/
     square-v1.png ... square-v<N>.png   (1080×1080)
     cover-v1.png ... cover-v<N>.png      (1080×1350, if requested)
     story-v1.png ... story-v<N>.png      (1080×1920, if requested)
     manifest.json
     style-used.md
     prompts.md
   ```

## MODES

### Required

- `avatar-maker --photo <path-or-url>`

### Style

- `--style auto|<library-id>` — visual style (default: auto, picks photoreal-friendly)
- `--style-mod "<override>"` — tweak the anchor

### Aspect + variants

- `--aspects square,square-tight,cover,story` — comma list (default: `square`)
- `--variants N` — variants per aspect (default 3 — sweet spot for picking the best)
- `--slug <name>` — output directory slug (default: derived from photo filename)

### Execution

- `--model auto|<slug>` — image provider (default `nano-banana-pro`)
- `--execute` — actually generate (else returns prompts)
- `--output <dir>` — custom output dir
- `--parallelism N` — concurrent API calls (default 3)
- `--yes` — skip cost confirmation
- `--resume` — retry failed variants
- `--prompts-only` — dry run, save prompts.md, exit
- `--cost-only` — print total cost, exit
- `--strict` — exit if `--model <slug>` can't handle photo refs

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/model-picker.md](references/model-picker.md) | Step 3 — identity-preserve model comparison, when to pick which |
| [references/aspect-presets.md](references/aspect-presets.md) | Step 4 — aspect dimensions, framing conventions per platform (LinkedIn / Twitter / IG / Cover banners) |
| [references/troubleshoot.md](references/troubleshoot.md) | When face doesn't look like the original / style overpowers identity / variants look identical |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: founder headshot for LinkedIn (kinfolk-minimal, 3 variants), photo-editorial B&W portrait set, multi-aspect avatar set for someone setting up new social accounts (square + cover-banner + story).

## CONSTRAINTS

- **Identity preserve is paramount.** Nano Banana Pro is the safest pick. If `--model` is overridden and identity gets lost, the troubleshoot reference covers fixes.

- **Use a clean source photo.** ≥800px on the short edge. Front-facing or 3/4. Even lighting. Avoid heavy shadow / backlight / partial occlusion.

- **No mid-image text.** Avatars are visual-only. Don't add `--title` or similar.

- **Default 3 variants per aspect.** Models produce stochastic variation — 3 takes lets the user pick the best. Past 5, diminishing returns.

- **One model across the run.** Mixing providers breaks consistency.

- **One style across the run.** Same anchor across all aspects + variants.

- **Photoreal-friendly styles win.** Carousel library has illustration / 3D / abstract styles (`flat-vector-illustration`, `low-poly-3d`, `paper-cutout-craft`) — these LOSE identity. `--style auto` filters them out. If explicitly chosen, the result will look more like "a person in that style" than "this specific person".

- **Cost confirm ONCE per batch.** Sum across aspects × variants.

- **Output slug derived from photo filename** by default. Override via `--slug` or `--output`.

- **Manifest updates after every variant.** `--resume` retries failed only.

- **Photo can be local or URL.** Provider routes accordingly.

- **Never print API keys.** Mask in errors.

- **Output dir is `./generated/avatar/<slug>/`** by default.

## INVOCATION HINTS

When the user says any of:

- "make me an avatar / profile pic from this photo"
- "headshot variants", "portrait variants"
- "LinkedIn profile picture", "Twitter profile pic", "Instagram avatar"
- "professional headshot", "business portrait"
- "branded avatar set" (variants in different aspects for cross-platform consistency)
- "сделай аватарку / портрет / хедшот"
- "профиль для LinkedIn / Twitter / IG"
- "аватарка с моей фоткой"

Defaults: `--aspects square --variants 3 --style auto --model nano-banana-pro`. Without `--execute`, returns prompts; with `--execute`, generates.

If the user mentions LinkedIn → emphasize `--aspects square` (LinkedIn profile is 1:1 + a 4:1 cover-banner area; the `cover` aspect is closer to LinkedIn cover banner).

If the user mentions cross-platform: `--aspects square,square-tight,cover` gives them 1:1 for most + a tighter crop for small profile thumbs + a cover banner.

This skill is distinct from:
- `flyer-maker` — that's events with embedded text; this is identity-preserved portraits
- `image-prompt` — that's any image; this is specifically photo-input → variant portraits
- `carousel-builder` — that's narrative slides; this is variants of one subject
