# flyer-maker — calibration

3 example sessions showing input → expected output shape.

---

## Example 1 — Solo founder workshop with embedded speaker photo

### User says

> Make a flyer for a workshop called "Slow Software" on June 15 at Brooklyn Studio NYC, tickets via link in bio. Here's a photo of the speaker: ./alex-headshot.jpg

### What happens

1. Claude assembles the plan and invokes:

```
flyer-maker --title "Workshop: Slow Software" \
            --date "15 June · 19:00" \
            --location "Brooklyn Studio, NYC" \
            --cta "Tickets: link in bio" \
            --photo ./alex-headshot.jpg \
            --style auto \
            --aspects portrait,square,story \
            --execute
```

2. **Style auto-pick**: based on "workshop" + "solo founder" + presence of speaker photo, picks `kinfolk-minimal` (editorial, photoreal-friendly). Logs alternatives `swiss-grid-poster`, `gradient-mesh-modern` to stderr.

3. **Model auto-pick**: `--photo` provided + identity preserve critical → `nano-banana-pro`.

4. **Builds 3 prompts** (portrait / square / story), each with:
   - Kinfolk-minimal style anchor (text-in-image mode)
   - Composition zones per aspect
   - Embedded text: title "Workshop: Slow Software", date "15 June · 19:00", location "Brooklyn Studio, NYC", CTA "Tickets: link in bio"
   - Reference image: `./alex-headshot.jpg`

5. **Cost**: 3 × $0.05 = $0.15. Under default budget — no confirmation.

6. **Execute**: 3 parallel API calls (parallelism 2). ~25s wall time.

7. **Output**:
   ```
   ./generated/flyer/workshop-slow-software/
     portrait.png            (1080×1350, kinfolk editorial layout, Alex's face preserved as central subject)
     square.png              (1080×1080, same composition tighter)
     story.png               (1080×1920, vertical with Alex full-body / shoulders-up)
     manifest.json
     style-used.md
     prompts.md
   ```

8. stdout:
   ```
   Flyer: ./generated/flyer/workshop-slow-software/  (3/3 aspects succeeded)
   Files: portrait.png · square.png · story.png
   ```

### What to notice

- One conversational request → 3 ready-to-post flyer variants.
- Identity-preserve takes priority over text rendering when `--photo` is present (NBP > Ideogram for this case).
- The same Kinfolk style anchor across all 3 aspects keeps the family cohesive.
- Composition zones differ per aspect (story has safe-zone reservations; square has tighter details band).

---

## Example 2 — Conference poster, no photo, bold Swiss-grid typography

### User says

> Make a conference poster for "Postmodern Russian Literature: A Reading Group". October 5-7 at the public library in Brooklyn, free entry. Use that brutalist Swiss-grid style.

### What happens

1. Command:

```
flyer-maker --title "Postmodern Russian Literature" \
            --subtitle "A Reading Group" \
            --date "October 5-7" \
            --location "Brooklyn Public Library" \
            --cta "Free entry" \
            --style swiss-grid-poster \
            --aspects portrait,square,a4 \
            --execute
```

2. No `--photo`. Title is text-heavy. **Model auto-pick**: `ideogram-3-quality` (best text + brand-clean composition).

3. **Builds 3 prompts**:
   - Swiss-grid-poster style anchor (text-in-image mode) — Helvetica/Akzidenz-Grotesk, primary palette, asymmetric grid
   - Composition: top headline + middle typographic block + bottom details
   - Text: 2 lines (title + subtitle) + 3 lines (date + location + CTA)

4. **Cost**: 3 × $0.08 = $0.24. Under budget.

5. **Execute**: ~30s.

6. **Output**:
   ```
   ./generated/flyer/postmodern-russian-literature-reading-group/
     portrait.png            (1080×1350)
     square.png              (1080×1080)
     a4.png                  (1240×1754)
     manifest.json
     ...
   ```

7. Stylistically: bold Helvetica + black/red + offset grid + minimal decorative elements.

### What to notice

- No photo → Ideogram 3 Quality is the right pick for clean text rendering.
- `--aspects portrait,square,a4` skips story (no IG Story planned) and adds A4 for posting at the library bulletin board.
- `swiss-grid-poster` style was explicit — no auto-pick. Useful when the user has a strong opinion.

---

## Example 3 — Three-aspect launch event with RU+EN bilingual variants

### User says

> Make event posters for our "Lunar Vault" gallery opening. December 1, 7pm, at the Stieglitz Gallery in St. Petersburg. RSVP via Telegram @lunarvault. I want one set in English for international press, one in Russian for local. Use that warm watercolor aesthetic with our logo as a reference.

### What happens

1. Two runs (one per language):

```
# English version
flyer-maker --title "LUNAR VAULT" \
            --subtitle "An Opening" \
            --date "December 1 · 19:00" \
            --location "Stieglitz Gallery, St. Petersburg" \
            --cta "RSVP @lunarvault on Telegram" \
            --photo ./lunarvault-logo.png \
            --style watercolor-soft \
            --aspects portrait,square,story \
            --lang en \
            --execute

# Russian version
flyer-maker --title "ЛУННЫЙ СВОД" \
            --subtitle "Открытие" \
            --date "1 декабря · 19:00" \
            --location "Музей Штиглица, Санкт-Петербург" \
            --cta "RSVP @lunarvault в Telegram" \
            --photo ./lunarvault-logo.png \
            --style watercolor-soft \
            --aspects portrait,square,story \
            --lang ru \
            --execute
```

2. `--photo ./lunarvault-logo.png` is the logo, NOT a face. **Model auto-pick**: photo + brand-asset use case + text-heavy → `gpt-image-2` (best at multi-ref with text, handles Latin + Cyrillic both).

3. Two output dirs:
   ```
   ./generated/flyer/lunar-vault-an-opening-en/
     portrait.png · square.png · story.png
   ./generated/flyer/lunar-vault-an-opening-ru/
     portrait.png · square.png · story.png
   ```

4. Both sets share visual identity (watercolor-soft + logo reference) but text content differs.

5. **Total cost**: 6 × $0.05-0.10 = $0.30-0.60. Under budget.

### What to notice

- Bilingual = two separate runs. The skill does NOT auto-translate.
- Same style + same logo reference → both sets feel like one campaign with two locales.
- `gpt-image-2` chosen over `nano-banana-pro` because the photo is a LOGO (no identity to preserve) and text rendering is the bigger concern (Cyrillic in the RU set).
- Watercolor-soft style is photoreal-adjacent — works with logo reference embedded as a watermark-like element rather than central subject.

---

## Anti-pattern (don't do this)

### Stuffing the title

❌ `flyer-maker --title "Workshop: Slow Software · December 15 at 7pm · Brooklyn Studio NYC · Tickets in bio · Limited seats"`

Result: title overflows, model truncates or distorts.

✓ Split into proper fields:

```
--title "Workshop: Slow Software" \
--date "Dec 15 · 19:00" \
--location "Brooklyn Studio, NYC" \
--cta "Limited tickets · link in bio"
```

### Asking for QR codes

❌ "Add a QR code linking to the Eventbrite page"

Result: AI image models hallucinate the QR pattern. The output looks like a QR but doesn't scan.

✓ Generate the flyer without QR; overlay a real QR (from `qrencode` / qr.io / a designer) in your image editor.

### Using a `flux-schnell` for a final poster

❌ `--model flux-schnell` for the final output.

Result: text often misspelled, aspect ratio sometimes ignored, low overall polish.

✓ Use `flux-schnell` for FAST IDEATION (cheap preview); use `ideogram-3-quality` or `nano-banana-pro` for the final.

### Bilingual title

❌ `--title "Workshop / Воркшоп"`

Result: mixed scripts in one headline → AI image models render gibberish.

✓ Two separate runs with `--lang en` and `--lang ru`.
