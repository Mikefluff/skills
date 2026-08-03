# thumbnail-maker — calibration

3 example sessions.

---

## Example 1 — YouTube tutorial with creator face

### User says

> YouTube thumbnail for my new tutorial "How I Built a SaaS in 30 Days". Here's my photo: ./me.jpg

### Command

```
thumbnail-maker --title "How I Built a SaaS in 30 Days" \
                --photo ./me.jpg \
                --type youtube \
                --placements left,right,center \
                --execute
```

### What happens

1. **Style auto**: picks `gradient-mesh-modern` (vibrant, modern, text-friendly).
2. **Model auto**: `nano-banana-pro` (identity preserve).
3. **Cost**: 3 × $0.05 = $0.15.
4. **Output**:
   ```
   ./generated/thumbnail/how-i-built-a-saas-in-30-days/
     thumbnail-left.png      (face left, title right, 1920×1080)
     thumbnail-right.png     (mirror)
     thumbnail-center.png    (face center-bottom, title top)
     manifest.json
     ...
   ```

User picks the one that feels strongest and uploads to YouTube.

---

## Example 2 — Blog header without photo

### User says

> Blog header image for "The Slow Software Manifesto". No face — just clean editorial title.

### Command

```
thumbnail-maker --title "The Slow Software Manifesto" \
                --type blog \
                --style kinfolk-minimal \
                --execute
```

### What happens

1. **No photo** → `--model ideogram-3-quality` (best for clean text).
2. **`--type blog`** → 1200×630 (OG image standard).
3. **Style**: `kinfolk-minimal` explicit.
4. **3 placements still applied** but with no face: variations come from typography placement + decorative elements.
5. **Cost**: 3 × $0.08 = $0.24.
6. **Output**: `./generated/thumbnail/slow-software-manifesto/thumbnail-{left,right,center}.png` (1200×630 each).

User picks one and embeds in their blog post as the OG image / hero.

---

## Example 3 — Podcast episode with guest

### User says

> Podcast episode cover for "Slow Software Podcast" episode 12 with guest Sarah Chen. Title: "Why We Killed Our Roadmap". Guest photo: ./sarah-portrait.jpg.

### Command

```
thumbnail-maker --title "Why We Killed Our Roadmap" \
                --subtitle "Slow Software Podcast · Ep. 12" \
                --photo ./sarah-portrait.jpg \
                --type podcast-episode \
                --style swiss-grid-poster \
                --variants 2 \
                --execute
```

### What happens

1. **Photo + face** → `nano-banana-pro`.
2. **`--type podcast-episode`** → 1920×1080.
3. **Subtitle** provides series + episode-number tag.
4. **3 placements × 2 variants = 6** images.
5. **Cost**: 6 × $0.05 = $0.30.
6. **Output**: 6 PNGs (left-v1, left-v2, right-v1, right-v2, center-v1, center-v2).

Brand consistency: same `--style swiss-grid-poster` as the main podcast cover (from cover-maker) → episodes feel like one series.

---

## Anti-pattern

### Stuffing the title

❌ `--title "The Complete Guide to Building Successful Solo Founder Businesses in 2026"`

Result: text crowds, illegible at thumbnail scale.

✓ Shorten or split:

```
--title "The Solo Founder Stack"
--subtitle "How 73% are doing it differently"
```

### Multiple faces

❌ Pass a group photo, expect all faces to be in the thumbnail.

Result: AI picks one face, others become blurry / generic.

✓ Crop to one face before running.

### Asking for "shock face"

If you want a high-impact emotional expression, the style-mod should be specific:

```
--style-mod "wide-eyed surprise expression"
```

But know that exaggerated shock is a YouTube trope that can feel inauthentic. Use sparingly.

### Wrong aspect for the platform

YouTube: 16:9 (default). Blog: 1200×630. Podcast: 16:9 with podcast-cover-feel.

Don't mix them up — `--type` picks the right preset.
