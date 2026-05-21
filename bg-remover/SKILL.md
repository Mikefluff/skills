---
name: bg-remover
description: "Background removal utility — take an image, output the same image with transparent background. Wraps Replicate-hosted background removal models (851-labs/background-remover by default; alternatives via --replicate-model). Single image input, transparent PNG output. Use when the user says 'remove the background', 'cut out the subject', 'transparent PNG', 'убери фон', 'вырежи фон с фотки'."
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
Remove the background from a photo. Single input image → output PNG with transparent (alpha channel) background. Subject preserved as-is; everything else becomes transparent.

This skill does NOT:
- Replace the background with a new image — for that, use the transparent PNG output + paste into a new background in your image editor, OR use `image-prompt --execute --model flux-kontext --image-url <photo> --prompt "subject in new setting"` for full reimagining
- Remove specific objects from a complex scene — only removes BACKGROUND (everything not the main subject)
- Process video — single image only (per call)
- Restore / upscale / sharpen — see future `upscaler` skill
</objective>

## ROLE

Read the input image → call a Replicate-hosted bg-removal model → save the transparent PNG.

## PIPELINE

1. **Resolve input**:
   - `--image <path-or-url>` (required)
   - Local file or remote URL

2. **Pick provider**:
   - Default: `851-labs/background-remover` (popular, accurate on photos)
   - Alternatives via `--replicate-model <id>`:
     - `851-labs/background-remover` — default; best general
     - `lucataco/remove-bg` — alternative
     - `cjwbw/rembg` — Python `rembg` library hosted
     - `pollinations/modnet` — MODNet (good for portraits)
   - Other Replicate bg-removers: pass via `--replicate-model <slug>`

3. **Execute** via the Replicate router (REPLICATE_API_TOKEN required).

4. **Save**:
   - Default: `./generated/bg-removed/<input-stem>-nobg.png` (transparent)
   - Custom: `--output <path>`

## MODES

### Required

- `bg-remover --image <path-or-url>`

### Options

- `--output <path>` — explicit output path
- `--replicate-model <id>` — override default bg-remover model
- `--execute` — defaults to true (this skill always executes; no prompt-only mode for a utility)
- `--yes` — skip cost confirmation
- `--check` — verify REPLICATE_API_TOKEN + connectivity

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/providers.md](references/providers.md) | Replicate bg-removal model comparison + when to pick which |
| [references/output-format.md](references/output-format.md) | Transparent PNG handling, alpha channel, downstream usage |
| [references/troubleshoot.md](references/troubleshoot.md) | When subject loses edges, hair gets cropped, etc. |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 2 calibration runs: portrait photo → transparent for avatar use; product shot → transparent for e-commerce listing.

## CONSTRAINTS

- **Single image per call.** For batch: run in a shell loop.

- **Replicate API key required.** Set via `/skills-keys add REPLICATE_API_TOKEN r8_...`.

- **Cost**: ~$0.001-0.005 per image depending on model. Very cheap.

- **Default model handles most photos well.** Switch to `pollinations/modnet` for portraits if hair edges are critical.

- **Subject must be CLEARLY distinguishable from background.** Models struggle with:
  - Subjects that match background color
  - Multiple subjects (picks one or merges)
  - Transparent objects (glass / water)
  - Hair against busy backgrounds (some loss of fine detail expected)

- **Output is always PNG with alpha channel.** RGB → RGBA conversion automatic.

- **Source resolution preserved.** Output dimensions match input.

- **No re-encoding to JPEG.** Transparent backgrounds require PNG (or WebP) — JPEG doesn't support transparency.

- **Never print API keys.**

- **Output dir is `./generated/bg-removed/`** by default.

## INVOCATION HINTS

When the user says any of:

- "remove the background", "cut out the subject"
- "transparent PNG", "no background version"
- "убери фон", "вырежи фон с фотки", "сделай прозрачный фон"
- "make the background transparent"

Defaults: `--image <path>` (required); auto-saves to `./generated/bg-removed/<stem>-nobg.png`.

If the user wants to REPLACE the background (not just remove), suggest:
1. Use this skill to get a transparent PNG.
2. Then use `image-prompt --execute --model flux-kontext --image-url <photo>` for AI-driven replacement.
3. OR open the transparent PNG in an image editor and composite with a new background manually.

This skill is distinct from:
- `image-prompt` / `avatar-maker` — they generate NEW images. This is a utility on EXISTING images.
- `subtitle-burner` — that's video utility. This is image utility.
- `upscaler` (planned) — that's resolution. This is background removal.
