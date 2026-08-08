# Troubleshooting — flyer-maker

When the flyer doesn't come out right.

---

## Embedded text is misspelled / cut off / wobbly

**Symptom**: "Workshop: Slow Software" comes out as "Workshop: Slo Sotware" or some letters render as garbled glyphs.

**Causes + fixes**:

1. **Wrong model.** Nano Banana 2 / Flux generate broken text 30-60% of the time. Even Nano Banana Pro can wobble on long headlines.
   - Fix: `--model ideogram-3-quality` (best for text) OR `--model gpt-image-2` (best for text + photo combined).

2. **Headline too long.** >8 words = high failure rate.
   - Fix: shorten the title; move secondary info to `--subtitle` or `--cta`.

3. **Headline contains tricky characters or numbers.**
   - Long numbers (`1,847,392`) break often. Use word forms or simplify.
   - Special chars (`™`, `—`, `…`) sometimes render as gibberish.
   - Fix: rewrite to plain ASCII where possible; check the output and re-run that specific aspect via `--resume` after editing the prompt in manifest.json.

4. **Style anchor specifies a font category the model can't render at the requested aspect.**
   - Some script / decorative fonts can't be reproduced cleanly at small sizes (details zone).
   - Fix: simplify typography spec in `--style-mod "with cleaner sans-serif typography"`.

---

## Photo doesn't get embedded / model ignores it

**Symptom**: Pass `--photo ./speaker.jpg`, but the output flyer has a generic person, not the speaker.

**Causes + fixes**:

1. **Model isn't ref-capable.** `Nano Banana 2` (non-ultra), `flux-schnell`, `flux-1-1-pro` (single-image, no ref input) can't use `--photo`.
   - Fix: the skill should auto-substitute. If you passed `--strict`, drop it and re-run.

2. **Photo wasn't passed through.** Check manifest.json — does the item's `kwargs.image_url` contain the path?
   - Fix: make sure `--photo ./speaker.jpg` was actually in the command, with no typo on the path.

3. **Photo path doesn't exist or isn't readable.**
   - Fix: `ls -la ./speaker.jpg` to confirm it exists + has read permissions.

4. **Photo is too low-res.** Faces become a blur when the model upscales for a 1080×1920 flyer.
   - Fix: use a photo at ≥800px on the short edge.

5. **Style anchor overpowers the photo.**
   - Some style anchors (heavy illustration like `paper-cutout-craft`) push the model to interpret everything as illustration, including the photo.
   - Fix: use a photoreal-friendly style (`kinfolk-minimal`, `photo-editorial-bw`, `gradient-mesh-modern`) when you want the speaker face preserved.

---

## Wrong aspect ratio output

**Symptom**: Asked for `portrait` (1080×1350), got 1024×1024.

**Causes + fixes**:

1. **Model defaults to square.** `flux-schnell` is notorious for ignoring exact size requests.
   - Fix: use a model that honors aspect: `ideogram-3-quality`, `gpt-image-2`, `nano-banana-pro`, `flux-2-pro`.

2. **Provider returned a different size than requested.** Some providers round to their nearest supported aspect.
   - Fix: check the size in the output PNG metadata. If consistently wrong, manually resize in your image editor.

---

## Layout collapses / looks crowded

**Symptom**: Title + subtitle + date + location + CTA all overlap or compete for space.

**Causes + fixes**:

1. **Too many text elements.** The composition zones can hold ~4 text elements clearly. Past that, the model crowds.
   - Fix: drop `--subtitle` OR merge `--date` and `--time` into one field.

2. **Long location string.** "12345 Main Street Boulevard West, Brooklyn, New York 11201, USA" doesn't fit.
   - Fix: abbreviate. "Brooklyn Studio, NYC" works.

3. **Long CTA.** Past 10 words, the CTA crowds the details zone.
   - Fix: shorten. "Tickets in bio" beats "Tickets available now at the link in our bio".

4. **Aspect too small for content.** Squeezing a 5-element flyer into `square` is harder than `portrait`.
   - Fix: drop to `portrait` or `a4` for content-dense flyers.

---

## Style drifts across aspects

**Symptom**: Portrait looks editorial calm, square looks brutalist, story looks vintage.

**Causes + fixes**:

1. **Model fingerprint differs per call.** Each gen has stochastic variation.
   - Fix: lock to ONE model across all aspects (already enforced by the skill; if it happened, you might have edited manifest.json mid-run).

2. **Different aspect = different composition prompt = different visual feel.**
   - This is partly expected. To minimize drift, use a strong specific style anchor (e.g., `kinfolk-minimal` rather than `--style auto` for a brand-new event).

3. **Variants kick in.** `--variants 3` will produce different takes per aspect.
   - Fix: pick the best of the variants per aspect manually.

---

## Cost confirmation triggered for what feels small

<!-- prices: batch=3 -->

**Symptom**: 3-aspect run at `ideogram-3-quality` = $0.24. User expects no prompt but gets one.

**Cause**: Default budget is `SKILLS_CAROUSEL_BUDGET=$1.50` (flyer shares the carousel budget). $0.24 is well under — no prompt.

If you see a prompt:
- `--variants 3` × 3 aspects × $0.10 = $0.90, still under budget
- `--aspects portrait,square,story,landscape,a4` × $0.30 = $1.50, exactly at budget — confirmation prompts
- High-quality models bumped up = exceeds budget

**Fix**: `--yes` to skip; or lower variants / aspects / model tier.

---

## --resume doesn't pick up where I left off

**Symptom**: 1 aspect failed, `--resume` regenerates everything.

**Causes + fixes**:

1. **manifest.json was deleted.**
   - Fix: --resume needs the manifest. Without it, treat as fresh run.

2. **Output dir changed.**
   - Fix: --resume reads from the dir specified by `--output` (or `./generated/flyer/<event-slug>/` from the title slug). Pass the same `--output <dir>` to align.

---

## Photo subject doesn't look like the original photo

**Symptom**: The speaker's face in the output is close but not exactly the same person.

**Causes + fixes**:

1. **Wrong model.** Nano Banana Pro is the identity-preserve champion. Flux / Imagen lose identity often.
   - Fix: `--model nano-banana-pro`.

2. **Conflict between style anchor and photo.** Style says "illustrated flat vector" but photo is a high-res portrait. The model has to compromise.
   - Fix: pick a photoreal style (`kinfolk-minimal`, `photo-editorial-bw`).

3. **Photo lighting / angle is unusual.** Heavy backlight, extreme angle, partial occlusion — these confuse identity-preserve.
   - Fix: use a clean front-facing portrait with even lighting.

---

## A4 / print version doesn't look print-ready

**Symptom**: The `a4` aspect output looks fine on screen but blurry when printed.

**Cause**: Output is RGB at ~150 DPI (1240×1754 = 8.27×11.69" at 150 DPI). For true print at 300 DPI, you need 2480×3508 px.

**Fix**:
- Generate at `a4` first (cheaper, faster preview).
- Open in Affinity / Photoshop / GIMP.
- Upscale to 2480×3508 (Photoshop's "Preserve Details 2.0" or Affinity's Lanczos work well).
- Convert RGB → CMYK.
- Export PDF for print.

This is intentional friction. The skill is for digital flyers; for print-first projects, a dedicated DTP tool is better.

---

## "But it worked in the provider's web UI"

If the same prompt produces a beautiful flyer in Ideogram's web UI but garbage via API:

- Web UIs often have hidden defaults (safety filters relaxed, default style applied, watermarks toggled off).
- API requires explicit params. Compare the params used.

**Workaround**: copy the prompt from `prompts.md`, paste into the UI manually. The flyer is salvaged.

---

## QR codes / icons / specific logos

The skill doesn't generate QR codes or render specific brand logos. AI image models are bad at these — they "hallucinate" the QR pattern.

**Fix**: generate the flyer WITHOUT the QR; then overlay a real QR (`qrencode` CLI / qr.io / a real designer) and a real logo (PNG asset) in your image editor.

---

## Bilingual flyers — both languages on one image

Don't try `--title "Workshop / Воркшоп"` — mixed-script titles fail on most models.

**Fix**: run twice with `--lang en` and `--lang ru`. The skill saves to `<slug>-en/` and `<slug>-ru/` directories.

```bash
flyer-maker --title "Workshop: Slow Software" --date "15 June" --lang en --execute
flyer-maker --title "Воркшоп: Медленное ПО" --date "15 июня" --lang ru --execute
```
