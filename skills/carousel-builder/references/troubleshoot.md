# Troubleshooting

Things that go wrong with carousel-builder and how to fix them.

---

## Style drifts across slides (most common)

**Symptom**: Slide 1 looks great, slide 5 looks like a different style.

**Causes + fixes**:

1. **Different model invocations producing different style fingerprints.**
   - Fix: use ONE model for the whole batch. `--model flux-2-pro` (not auto if router picks vary).

2. **Style anchor too short / vague.**
   - Fix: pick a more specific library style. Free-form style descriptions almost always drift.

3. **Provider doesn't honor seeds.**
   - Most modern providers don't expose seed publicly. Use `--style-ref <first-slide.png>` after the first slide is generated — then re-run with refs anchored to slide 1.

4. **Long content prompts overpowering style anchor.**
   - Fix: keep slide content prompt ≤60 words. Anchor goes first. Content second.

5. **--style auto pulled too generic.**
   - Fix: pass `--style <id>` explicitly. Auto-pick is fast but loses on niche topics.

---

## Embedded text is misspelled or unreadable

**Symptom**: Headline reads "AI Praductivity Tools" or text is partially cut off.

**Causes + fixes**:

1. **Wrong model.** Nano Banana 2 + Flux generate broken text 30-60% of the time.
   - Fix: `--model ideogram-3-quality` (best for clean text) OR `--model gpt-image-2`.

2. **Headline too long.** >8 words = high failure rate.
   - Fix: shorten headlines to 3-6 words. Rewrite in `prompts.md` and `--resume`.

3. **Headline contains special chars or numbers in tight spaces.**
   - Numbers > 4 digits tend to break ("73%" is fine, "1,847,392" usually breaks).
   - Fix: use word forms ("under two million") or simplify.

4. **Style anchor specifies font that doesn't exist in the model's training.**
   - Fix: anchor with font category (serif / sans / display) rather than specific named font.

---

## Provider returns garbage / placeholder

**Symptom**: Output is solid color, abstract noise, or watermark.

**Causes + fixes**:

1. **Prompt triggered moderation filter.**
   - Check what content has names / brands / sensitive topics.
   - Fix: regenerate that slide with a softer prompt.

2. **Account quota exhausted.**
   - Check vendor dashboard for credit balance.
   - Most providers don't return 429 — they return a placeholder image.
   - Fix: top up credits, `--resume`.

3. **Free tier / sandbox account.**
   - OpenAI / Google sandbox keys produce reduced quality / watermarked output.
   - Fix: upgrade or switch provider.

---

## Cost confirmation triggered for what looks small

**Symptom**: User says "8 slides at $0.04 each is $0.32 — why am I being asked to confirm?"

**Cause**: $0.32 < default budget ($1.50), so it goes through silently. If the user IS being asked, they're over $1.50, likely:
- High-quality mode (gpt-image-2 high, ideogram-3-quality)
- `--variants 2` doubles cost
- 10 or 12 slides

**Fix**: pass `--yes`, OR lower variants, OR cheaper model.

---

## --resume doesn't skip succeeded slides

**Symptom**: After --resume, ALL slides are being re-generated.

**Causes + fixes**:

1. **Manifest.json was deleted or moved.**
   - Fix: --resume needs the manifest. Without it, treat as fresh run.

2. **Output dir was changed between runs.**
   - Fix: --resume reads from the dir specified by `--output` (or `./generated/carousel/<slug>/` from the topic slug). Pass the same dir.

3. **The skill rebuilt prompts (e.g., research file changed).**
   - The skill currently re-runs from the manifest's recorded prompts. If you ran with `--topic` and the topic changed slightly, slug also changed → new dir → new manifest.
   - Fix: pass `--output <same-dir-as-before>` to force resume into the same place.

---

## Slides take too long / time out

**Symptom**: First slide takes 60s+ instead of expected 10s.

**Causes + fixes**:

1. **First call is cold-start.**
   - Some providers (especially Replicate hosted models) take 30-60s for the first call.
   - Subsequent calls are fast. Wait it out.

2. **High parallelism + rate limit thrashing.**
   - Lower `--parallelism 1` and run sequentially.

3. **Poll timeout too short for async providers.**
   - Default 600s should be plenty for images. If you see TimeoutError, increase via the underlying CLI flag.

4. **Network issues.**
   - Check connectivity. The runner doesn't retry on network errors automatically.

---

## Caption tone doesn't match the carousel

**Symptom**: Visual carousel is editorial/calm, but caption reads like sales-pitch.

**Cause**: The CTA template defaulted to a sales-y pattern. Caption is templated, not LLM-generated dynamically against the style anchor's tone.

**Fix**: After generation, edit `captions.md` manually. Or re-run with a different `--platform` (LinkedIn captions tend to be quieter than Instagram).

---

## Style library lookup fails

**Symptom**: `FileNotFoundError: style 'X' not found for modality 'carousel'`.

**Causes + fixes**:

1. **Typo in --style id.**
   - Check `common/style-library/carousel/_index.md` for valid ids, or run `/skills-styles list carousel`.

2. **User override file is malformed.**
   - Check `~/.claude/style-library/carousel/<id>.md` — must have frontmatter with `id:` matching the filename.

3. **install.sh didn't copy the library.**
   - Verify: `ls ~/.claude/skills/common/style-library/carousel/ | head`
   - Fix: re-run `install.sh --update`.

---

## Auto-pick chose a bad style

**Symptom**: Auto-resolved to `memphis-90s` for a serious B2B carousel.

**Cause**: Topic keywords didn't have enough signal toward "professional" tags.

**Fix**: Pass `--style <id>` explicitly. The auto picker is a starting point, not authoritative.

Also report the bad pick — the auto-picker heuristics in `style-resolution.md` are tunable.

---

## Generated slides are inconsistent in aspect ratio

**Symptom**: 7 slides at 1080×1350 but slide 4 is 1024×1024.

**Cause**: Some providers don't honor exact size requests for non-standard aspects.

**Fix**:
- Use providers known to honor 4:5 portrait: gpt-image-2, ideogram-3, flux-2-pro.
- Avoid: flux-schnell (often defaults to 1024×1024 regardless).
- If a slide came out wrong size: `--resume` won't fix this since the manifest already says succeeded. Manual delete of that slide + re-edit manifest `status: failed` for that item, then `--resume`.

---

## "But it works in the provider's UI"

If a prompt works when pasted into a provider's web UI but fails via API:

- Web UIs often have hidden defaults (safety filters, default styles, watermarks toggled off).
- API requires explicit params. Check provider's `references/models/<vendor>.md` (in image-prompt skill) for the required params.

Workaround: copy the prompt from `prompts.md`, paste into the UI manually. The carousel is salvaged even if some slides go that route.
