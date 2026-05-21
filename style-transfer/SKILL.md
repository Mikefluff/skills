---
name: style-transfer
description: "Apply an artistic style to an existing image. Default provider Flux Kontext (best for natural-language style transfer). 12 style presets (watercolor / oil-painting / sketch / line-art / ink-wash / cyberpunk / studio-ghibli / pixar-3d / manga / art-deco / low-poly / vaporwave) + custom mode with --prompt-mod. Single image in, stylized image out. Use when the user says 'style transfer', 'make this look like X', 'turn this photo into a watercolor', 'стилизуй фото', 'переведи в стиль X', 'переведи в акварель / манга / гибли'."
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
Image style-transfer utility. Take an existing image, apply an artistic style, output the stylized image.

Distinct from `image-prompt`:
- Operates on an EXISTING image (image-to-image edit), not from scratch
- 12 curated style presets — pick + go, no prompt engineering needed
- Default provider: Flux Kontext (best at natural-language style transfer)

Distinct from `bg-remover` / `upscaler`:
- They are utility (segmentation, resolution). This is creative stylization.
- All three are image-in-image-out wrappers — shared shape.

Distinct from `meme-card-maker`:
- meme adds text + template composition. This is pure visual stylization.

This skill does NOT:
- Generate entirely new images (use `image-prompt`)
- Style-transfer videos (frame-by-frame breaks temporal coherence — use Runway / Kaiber)
- Match an EXACT artist's style (model approximates; for legal/ethical reasons, well-known living artists shouldn't be reproduced)
- Vectorize / convert to SVG (output remains raster PNG)
- Preserve identity perfectly across heavy stylization (faces may transform; for ID-preserve use Nano Banana Pro)
</objective>

## ROLE

Read input image + style preset → call image-to-image edit provider (Flux Kontext default) → save stylized output.

## PIPELINE

1. **Resolve input**:
   - `--image <path-or-url>` (required)

2. **Pick style preset** — see `references/styles.md`:
   - `--style watercolor` — soft washes, paper texture
   - `--style oil-painting` — thick impasto strokes
   - `--style sketch` — pencil shading
   - `--style line-art` — clean outlines on white
   - `--style ink-wash` — Chinese sumi-e
   - `--style cyberpunk` — neon glow, retrofuturistic
   - `--style studio-ghibli` — hand-painted animation
   - `--style pixar-3d` — smooth 3D animation
   - `--style manga` — black-white screentone
   - `--style art-deco` — geometric 1920s
   - `--style low-poly` — triangulated 3D
   - `--style vaporwave` — pastel retro
   - `--style custom` — supply `--prompt-mod "<your-description>"`

3. **Pick provider**:
   - Default: `flux-kontext` — best for natural-language style transfer
   - Alt: `nano-banana-pro` — when face/identity matters
   - Alt: `replicate-image` (with `--replicate-model <slug>`) — for specific style-transfer models

4. **Execute** via the provider with image-to-image edit mode.

5. **Save**:
   - Default: `./generated/stylized/<input-stem>-<style>.png`
   - Custom: `--output <path>`

## MODES

### Required

- `style-transfer --image <path-or-url> --style <preset>`

### Optional

- `--model auto|<slug>` — image provider (default flux-kontext)
- `--prompt-mod "<custom-description>"` — additional style hint, or REQUIRED when `--style custom`
- `--output <path>` — explicit output path
- `--yes` — skip cost confirmation
- `--check` — verify env + connectivity

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/styles.md](references/styles.md) | Detailed description per preset, expected results, common pitfalls |
| [references/providers.md](references/providers.md) | Provider comparison: Flux Kontext vs Nano Banana Pro vs Replicate alternatives |
| [references/troubleshoot.md](references/troubleshoot.md) | When style is too subtle, too aggressive, faces distort, palette wrong |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: portrait to watercolor, urban scene to cyberpunk, sketch from photograph.

## CONSTRAINTS

- **Default provider needs BFL_API_KEY.** Flux Kontext is from Black Forest Labs. Set via `/skills-keys add BFL_API_KEY ...`. For other providers (Nano Banana Pro → GEMINI_API_KEY; Replicate → REPLICATE_API_TOKEN).

- **Cost**: ~$0.05 per stylization (Flux Kontext). Other providers vary $0.02-0.10.

- **One style per call.** Don't try to combine 2 styles in `--style-mod`; pick one preset and let it dominate.

- **Heavy stylization changes identity.** Watercolor preserves likeness ~70%. Studio-Ghibli ~50%. Cyberpunk ~30%. For identity-critical: use `--model nano-banana-pro` (better preserve) or accept reduced fidelity for stronger style.

- **Output is raster PNG.** For vector / SVG conversion: vectorize after (Illustrator auto-trace, Vectornator, vectorizer.ai).

- **Custom style requires `--prompt-mod`.** When `--style custom`, you MUST provide a natural-language style description.

- **Living-artist styles**: don't request "in the style of [living artist name]" — ethically / legally fraught. Use style descriptors instead (e.g., "watercolor" not "Hayao Miyazaki style"). Studio Ghibli is a STUDIO style descriptor (common public reference); preset cues movement not specific creators.

- **Never print API keys.** Mask in errors.

- **Output dir is `./generated/stylized/`** by default.

## INVOCATION HINTS

When the user says any of:

- "style transfer", "make this look like X"
- "turn this photo into a watercolor / oil painting / sketch / manga / etc."
- "стилизуй фото", "переведи в стиль X"
- "переведи в акварель / манга / гибли / киберпанк"

If the user names a style explicitly, match to a preset. If their phrasing is unique ("turn this into 1920s Soviet propaganda poster"), use `--style custom --prompt-mod "1920s Soviet propaganda poster style, bold red and black, geometric typography, heroic figures, constructivist aesthetic"`.

Defaults: `--style watercolor --model flux-kontext`. The skill always executes — there's no prompt-only mode for a utility.

This skill is distinct from:
- `image-prompt` — generates new images, not edits existing
- `bg-remover` — segmentation
- `upscaler` — resolution
- `cover-maker` / `flyer-maker` / etc. — composition + text
- `quote-card-maker` / `meme-card-maker` — typography-dominant
