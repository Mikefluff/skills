# Troubleshooting — meme-card-maker

---

## Captions don't read like memes

**Symptom**: captions look like generic typography, not Impact-stroke meme convention.

**Cause**: model didn't bind the typography cue strongly enough.

**Fix**:

1. Reinforce in `--style-mod`: `"thick white text with heavy 6px black stroke outline, Impact font face, classic internet meme typography, no other text styles"`.
2. Confirm `--model gpt-image-2` (best at meme typography). Switch if you overrode.
3. Re-roll: meme typography is stochastic; more variants = higher hit rate.

---

## Template not recognizable

**Symptom**: requested `--template drake` but output doesn't look like Drake.

**Cause**: image-gen models approximate famous templates; not pixel-identical.

**Fix**:

1. Add more cues: `--style-mod "two-panel vertical stack with the same person in both panels — top panel: dismissive hand gesture rejecting the caption; bottom panel: enthusiastic gesture approving the caption"`.
2. Or accept the approximation — modern memes don't always need the canonical Drake.
3. For pixel-exact templates: use Imgflip / Memegenerator (browser tools with the actual template baked in).

---

## Captions are misspelled

**Symptom**: "USING JIRA" rendered as "USIN8 JIRA" or similar.

**Cause**: image-gen text hallucination.

**Fix**:

1. Switch to `--model ideogram-3-quality` (stronger text rendering, but less "meme-y" look).
2. Re-roll with more variants.
3. Manual fix: pick the closest variant, retype captions in Photoshop / Affinity Photo / Pixelmator.

---

## Captions positioned wrong

**Symptom**: top caption appears in middle or bottom of image.

**Cause**: model interpreted `--top` as just "caption" without position binding.

**Fix**:

1. Strengthen positional cue: `--style-mod "top caption appears at the very top edge of the image, bottom caption appears at the very bottom edge, never in the middle"`.
2. Use template hints (`--template drake` etc.) — they bind positions stronger than `custom`.

---

## Base photo not preserved

**Symptom**: `--base-photo` passed but output doesn't look like the photo.

**Cause**: wrong model for image-to-image with identity preserve.

**Fix**:

1. Switch to `--model nano-banana-pro` (identity-preserve specialist).
2. Or use `--model flux-2-pro` if palette/style transfer is the goal vs strict identity.

---

## Captions appear UPPERCASE for Cyrillic too

**Symptom**: Russian text rendered as "КОГДА ПИШЕШЬ КОД" — hard to read.

**Cause**: skill's default uppercase rule didn't apply lang-specific override.

**Fix**:

1. Confirm `--lang ru` is set.
2. Add `--style-mod "Cyrillic typography in mixed case (not all caps), bold condensed Cyrillic font like Bebas Neue or Akrobat, white with black stroke"`.

---

## Image looks "too clean" / too polished

**Symptom**: output looks like a polished design, not a meme.

**Cause**: model defaulted to editorial composition.

**Fix**:

1. Add `--style-mod "intentionally low-fidelity, classic 2010s internet meme aesthetic, slight JPEG compression artifacts, not polished or editorial"`.
2. Pick a "deepfried" variant: `--style-mod "deepfried meme aesthetic, oversaturated, distorted typography, intentionally bad quality for ironic effect"`.

---

## Want to override fonts entirely

For a brand-specific meme campaign (e.g., your brand uses Inter or a custom font):

```
--style-mod "use [Brand Font] in place of Impact, maintain bold + stroke convention for meme readability"
```

Note: image-gen models can't render specific commercial fonts by name. They'll approximate by shape. For exact font matching: generate without text, then add typography in Figma / Affinity.

---

## Multi-caption template (>2 captions) needed

The skill's v1 supports 2 captions (`--top` + `--bottom`). For 4-panel templates like `expanding-brain`:

Pack all captions into `--top` separated by ` / ` :

```
--top "USE FORMATTER / USE LINTER / USE TYPE CHECKER / DELETE THE CODE" --template expanding-brain
```

The model distributes them across the 4 panels.

Alternative for 4+ captions: switch to `carousel-builder --slides 4 --style monochrome-bold` for a meme-as-carousel format.

---

## Cost is higher than expected

3 variants × `gpt-image-2` (medium) ($0.04) = $0.12 per batch. Reasonable.

For exploration: lower variant count or use `--cost-only` first.

---

## Want animated meme

Static PNG only. For animated:

1. Generate the static meme here.
2. Add motion in Photoshop (timeline) or a dedicated GIF tool.
3. Or: use `gif-maker --prompt "<meme description>"` for a fresh animated meme (not the same as a meme template, but in the meme aesthetic).

---

## Want template that's not in the supported list

For templates beyond the 5 supported (e.g., "Galaxy Brain Reverse", "Buff Doge vs Cheems"):

Use `--template custom` + describe the template in `--context`:

```
--template custom --context "buff doge vs cheems format — buff dog on left labeled top caption, small sad cheems dog on right labeled bottom caption"
```

The model will approximate. For pixel-exact: use a browser meme generator.
