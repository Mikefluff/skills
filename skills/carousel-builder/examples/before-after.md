# Carousel-builder calibration

3 example runs showing input → expected output shape.

---

## Example 1 — 8-slide LinkedIn carousel from research brief

### User request

> carousel-builder --research ./generated/research/ai-productivity-tools-marketers-20260521.md --platform linkedin --slides 8 --style auto --model flux-2-pro --execute

### What happens

1. Reads the research brief. Extracts TL;DR + Key facts + Notable quotes + 3 Suggested angles. Picks angle #1 "The 4-tool stack that 73% of founders use" since `--for carousel` was the brief's intended use.

2. Splits into 8 slides:
   - Slide 1 hook: "The 4-Tool Stack 73% of Solo Founders Now Use"
   - Slides 2-4: three of the four tools, one per slide
   - Slide 5: data slide with the 73% stat
   - Slide 6: quote from the brief
   - Slide 7: synthesis — voice-first is winning
   - Slide 8: CTA — "Follow [Name] for more on solo-founder tooling"

3. `--style auto`: derives tags `[tech, b2b, professional, modern, editorial]`. Top 3 candidates from library: `kinfolk-minimal`, `swiss-grid-poster`, `gradient-mesh-modern`. Picks `kinfolk-minimal` (best LinkedIn fit). Logs alternatives to stderr.

4. Builds 8 prompts. Each: style anchor (carousel mode, ~140 words) + slide content (~60 words) + composition hint + aspect 1080×1080.

5. Estimates cost: 8 × $0.06 (flux-2-pro) = $0.48. Below threshold $1.50 — no confirmation needed since well under.

6. Runs batch via Flux 2 Pro with parallelism 3. Manifest updates after each slide. ~50s wall time total.

7. Composes captions.md with LinkedIn structure: 200-char hook + 3-para body + question CTA + 4 hashtags. Per-slide alt-text.

8. Output:
   ```
   ./generated/carousel/ai-productivity-tools-stack/
     slide-1.png ... slide-8.png
     captions.md
     manifest.json
     style-used.md
     prompts.md
   ```

9. stdout:
   ```
   Carousel: ./generated/carousel/ai-productivity-tools-stack/  (8/8 slides succeeded)
   Captions: ./generated/carousel/ai-productivity-tools-stack/captions.md
   ```

### What to notice

- Linked source brief → carousel = single command end-to-end.
- Auto-style picks editorial LinkedIn-appropriate aesthetic. Alternatives logged so user can re-run with `--style swiss-grid-poster` if they want.
- 8 slides, 4:5 → square auto-switched because `--platform linkedin` overrides to 1:1.
- Total cost printed at completion.

---

## Example 2 — 6-slide Instagram with embedded text (Ideogram)

### User request

> carousel-builder --topic "5 mistakes new copywriters make" --slides 6 --platform instagram --text-mode embedded --style swiss-grid-poster --model ideogram-3-quality --execute

### What happens

1. No research brief — drafts content via `viral-text` (Instagram → viral-text per pipeline step 1). Output: hook + 5 mistakes + CTA in ~300 words.

2. Split: 6 slides = hook + 4 points + CTA (5 mistakes condensed into 4 paired with hook+CTA to fit 6-slide template).

3. `--style swiss-grid-poster` explicit. Loads `Style anchor (text-in-image mode)` (because `--text-mode embedded`) — includes typography spec: Helvetica/Akzidenz-Grotesk variants, primary palette, headline placeholder.

4. `--model ideogram-3-quality` explicit. Best for embedded text + brand-clean aesthetic. Cost: 6 × $0.08 = $0.48.

5. Builds prompts. Each has:
   - Style anchor (~110 words)
   - Slide content (~50 words)
   - Composition hint per role
   - Aspect 4:5 (1080×1350)
   - Embedded headline: e.g. slide 2 = `Headline text: "DON'T BURY THE LEDE"`

6. Batch execute. Ideogram returns clean embedded text on all 6 slides.

7. Captions: Instagram structure with 20 hashtags + save/share CTA.

8. Output:
   ```
   ./generated/carousel/5-mistakes-new-copywriters/
     slide-1.png ... slide-6.png  (each 1080×1350 with rendered headline)
     captions.md
     manifest.json
     style-used.md
     prompts.md
   ```

### What to notice

- Embedded headlines mean the user can post the carousel WITHOUT touching Canva — Ideogram rendered the text correctly.
- The headlines in `prompts.md` are the source of truth for fallback (if Ideogram broke text on a slide, user can re-render manually using the same prompt).
- Cost $0.48 (within default $1.50 carousel budget — no confirmation).

---

## Example 3 — 10-slide TikTok carousel with user reference image

### User request

> carousel-builder --topic "Bauhaus design fundamentals" --slides 10 --platform tiktok --style-ref ./my-bauhaus-mood-board.jpg --style bauhaus-primary --model nano-banana-pro --execute --yes

### What happens

1. Drafts content via `viral-text` (TikTok). Output: ~300 words on Bauhaus principles.

2. Split: 10 slides = hook + 7 design points + conclusion + CTA.

3. `--style bauhaus-primary` + `--style-ref <image>` BOTH passed. Style anchor (carousel) loaded for text. User's mood-board attached as reference image to every Nano Banana Pro call.

<!-- prices: batch=10 -->

4. `--model nano-banana-pro` — supports multi-ref. 10 × $0.134 = $1.34.

5. `--platform tiktok` → aspect 9:16 (1080×1920).

6. Builds 10 prompts. Each combines:
   - Bauhaus-primary library anchor (red/yellow/blue + black, geometric, modernist)
   - Slide content (specific Bauhaus principle)
   - Composition hint per role
   - Image ref attached
   - 9:16 aspect

7. `--yes` skips confirmation (user already knows the cost). Batch executes with parallelism 3.

8. ~80s wall time. Nano Banana Pro tends to preserve the ref's geometric language across all 10 slides — strong consistency.

9. Output:
   ```
   ./generated/carousel/bauhaus-design-fundamentals/
     slide-1.png ... slide-10.png  (each 1080×1920)
     captions.md  (TikTok-styled, 3 hashtags, short caption)
     manifest.json
     style-used.md  (notes both library + reference image used)
     prompts.md
   ```

### What to notice

- BOTH style mechanisms combined: library text anchor for grammar + user image for palette/composition signature.
- Nano Banana Pro chosen because it's best at multi-ref propagation.
- TikTok preset → 9:16 vertical aspect, 3 hashtags, short caption.
- `--yes` used since user has run this style many times and knows the cost.

---

## Anti-pattern (don't do this)

### Mixing models across slides

> carousel-builder --topic "X" --slides 8 --model auto

Then internally varying provider per slide ("flux for slides 1-4, ideogram for 5-8"). DON'T. Even with the same style anchor, different model fingerprints produce visibly different aesthetics. The carousel feel breaks.

If you want variation, use `--variants 2` to generate 2 versions of each slide WITHIN the same model. Pick the best one per slide for the final.

### Long headlines in embedded text mode

> Slide 1 headline: "The 5 Most Important Productivity Tools Every Solo Founder Should Be Using in 2026"

Too long. Model truncates or distorts. Headlines ≤8 words is the rule.

### Auto-style on a non-mainstream topic

> carousel-builder --topic "ancient Mayan astronomy" --style auto

Auto-pick might give you `kinfolk-minimal` (default for "vaguely intellectual"). Pass `--style <id>` explicitly for niche topics. Browse `common/style-library/carousel/_index.md` to see what's available.
