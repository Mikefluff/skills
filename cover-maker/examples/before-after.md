# cover-maker — calibration

3 example sessions.

---

## Example 1 — Album cover with reference artwork

### User says

> Make an album cover for "Lunar Vault" by Alex Reyes. Indie electronic, dark synthwave vibe. Here's the artwork reference: ./artwork.jpg

### Command

```
cover-maker --title "Lunar Vault" \
            --creator "Alex Reyes" \
            --medium album \
            --photo ./artwork.jpg \
            --style synthwave \
            --style-mod "dark blue and electric purple palette, late-night atmosphere" \
            --variants 3 \
            --execute
```

Wait — `synthwave` isn't a CAROUSEL style. Need to be careful. cover-maker uses the carousel style library; synthwave is in the MUSIC library. The skill auto-handles this: looks up the closest carousel style or falls back to a generic synthwave anchor.

Better command (using a carousel style):

```
cover-maker --title "Lunar Vault" \
            --creator "Alex Reyes" \
            --medium album \
            --photo ./artwork.jpg \
            --style neon-cyberpunk \
            --variants 3 \
            --execute
```

### What happens

1. **Style**: `neon-cyberpunk` from carousel library — synthwave-adjacent.
2. **Model auto-pick**: photo provided + identifiable artwork → could be flux-2-pro (palette transfer) or nano-banana-pro. Album covers favor palette transfer → `flux-2-pro`.
3. **Cost**: 3 × $0.06 = $0.18. Under budget.
4. **Output**:
   ```
   ./generated/cover/lunar-vault-album/
     album-v1.png     (3000×3000, neon palette, "LUNAR VAULT" embedded large, artist name subtle)
     album-v2.png
     album-v3.png
     manifest.json
     ...
   ```

### What to notice

- Album cover = 3000×3000 (Spotify spec). Title prominent. Artist name subtle.
- 3 variants gives the artist options to pick from.
- Reference artwork provides palette + composition guidance.

---

## Example 2 — Business book cover with author photo

### User says

> Book cover for "The Slow Software Manifesto" by Alex Smith. Author photo: ./alex-headshot.jpg. I want a clean, intellectual, swiss-grid feel.

### Command

```
cover-maker --title "The Slow Software Manifesto" \
            --creator "Alex Smith" \
            --medium book \
            --photo ./alex-headshot.jpg \
            --style swiss-grid-poster \
            --variants 2 \
            --execute
```

### What happens

1. **Style**: `swiss-grid-poster` explicit — clean, intellectual.
2. **Model auto-pick**: photo + photoreal preserve = `nano-banana-pro`. But heavy text rendering needed for book title → conflict.
   - Skill picks `nano-banana-pro` (identity wins for book covers — author photo is the brand).
   - If text quality is poor, user can override with `--model gpt-image-2` and accept slight identity drift.
3. **Cost**: 2 × $0.05 = $0.10. At threshold — no confirmation.
4. **Output**:
   ```
   ./generated/cover/slow-software-manifesto-book/
     book-v1.png      (1600×2400, swiss-grid composition, title top, author photo middle, author name bottom)
     book-v2.png
     manifest.json
     ...
   ```

### What to notice

- Book = 2:3 portrait. Title dominates top.
- Author photo embedded as central visual. Identity preserved.
- Swiss-grid feels appropriate for a business / non-fiction book on a serious topic.

---

## Example 3 — Podcast cover with bold typographic style

### User says

> Podcast cover for "Slow Software Podcast", hosted by Alex Smith. No host photo — just clean bold type. Brand color is muted teal.

### Command

```
cover-maker --title "Slow Software Podcast" \
            --creator "Hosted by Alex Smith" \
            --medium podcast \
            --style swiss-grid-poster \
            --style-mod "muted teal accent color, restrained sans-serif typography, single bold accent shape" \
            --variants 3 \
            --execute
```

### What happens

1. **Style**: `swiss-grid-poster` + custom palette via `--style-mod`.
2. **No photo** → text-heavy run → `--model ideogram-3-quality` (default for text-only covers).
3. **Cost**: 3 × $0.08 = $0.24. Under budget.
4. **Output**:
   ```
   ./generated/cover/slow-software-podcast/
     podcast-v1.png   (3000×3000, bold title dominant, host name subtle, teal accent)
     podcast-v2.png
     podcast-v3.png
     manifest.json
     ...
   ```

### What to notice

- Podcast = 3000×3000 (Apple Podcasts spec). Show name dominant — must read at 60×60px thumbnail.
- No photo: `ideogram-3-quality` is the right pick for clean text.
- 3 variants because podcast covers iterate on type + layout more than on illustration.
- Brand color baked into `--style-mod` — overrides the default style anchor's palette.

---

## Anti-pattern (don't do this)

### Stuffing the title

❌ `--title "The Slow Software Manifesto: A Complete Guide to Shipping Less and Caring More in the Age of AI Acceleration"`

Result: title text overflows, model truncates or distorts.

✓ Split into proper fields:

```
--title "The Slow Software Manifesto"
--subtitle "Shipping less, caring more"
```

### Using a low-fidelity model for final art

❌ `--model flux-schnell` for a published book cover.

Result: text often misspelled, low overall polish, low resolution.

✓ Use `flux-schnell` only for cheap fast preview / ideation. Use `ideogram-3-quality` or `nano-banana-pro` for final.

### Asking for spine + back cover

❌ "Make a full book wrap with spine and back."

Result: the skill produces front cover only.

✓ Generate front cover here, design spine + back in Affinity Publisher / InDesign manually.

### Mixing medium semantics

❌

```
cover-maker --title "Album X" --medium book
```

Result: book composition (title top, subject middle, author bottom) applied to what's actually an album — looks like a book.

✓ Match `--medium` to the actual cover type.

### Multi-language title

❌ `--title "The Manifesto: Манифест"` (Latin + Cyrillic in one title).

Result: rendering breaks on most models.

✓ Pick one language. Run twice for bilingual editions:

```
cover-maker --title "The Manifesto" --medium book --lang en --execute
cover-maker --title "Манифест" --medium book --lang ru --execute
```
