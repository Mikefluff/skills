# Platform presets

Per-platform defaults for aspect, captions, hashtags, alt-text.

---

## Instagram

### Aspect

- Default: portrait `4:5` (1080 × 1350) — uses ~3× more feed real estate than 1:1
- Square `1:1` (1080 × 1080) — older convention, still works
- Story / Reel cover `9:16` (1080 × 1920) — only if posting to Story not feed

### Caption

- Length: 1 to ~2200 chars (cap). Sweet spot: 100-220 chars first paragraph (the visible part before "more"), full body up to 1500 chars.
- Structure:
  ```
  <hook line — first 100-125 chars MUST land the value prop>

  <body — 3-6 sentences, blank-line separated>

  <CTA — save / share / DM>

  ---

  <15-25 hashtags>
  ```

### Hashtags

- 15-25 mix. Don't use 30 (the ceiling) — it's a 2019 tactic, current best practice is 15-20.
- Mix:
  - 3-5 broad (1M+ posts) — `#productivity` `#ai` `#startup`
  - 7-12 mid (100K-1M) — `#aiproductivity` `#solofounder` `#startupgrowth`
  - 3-5 niche (10K-100K) — `#solopreneur2026` `#aifortools` (these get you to small-pool top-posts)
- Put on a separate line after the body, not in-line.
- Never repeat the same hashtag set across posts — Instagram throttles repetitive tagging.

### Alt-text per slide

Each slide gets descriptive alt-text (1-2 sentences). Helps screen readers + search ranking. Auto-generated from the per-slide prompt + headline.

---

## LinkedIn

### Aspect

- Default: square `1:1` (1080 × 1080) — LinkedIn's "Document" / multi-image post optimum
- Portrait `4:5` (1080 × 1350) — works but cropped slightly on feed
- Story `9:16` — not used on LinkedIn

### Caption

- Length: up to 3000 chars total. First 200 chars are the "above the fold" visible portion.
- Structure:
  ```
  <hook line — first 200 chars MUST stand alone as a hook>
                 (blank line is rendered, so use it for pacing)

  <body — 3-7 sentences, longer paragraphs OK, blank-line separated>

  <CTA — question-driven: "What's your take?" / "Disagree?" / "DM me for X">

  <Optional: 3-5 hashtags at end>
  ```

### Hashtags

- 3-5 max. LinkedIn doesn't reward many-hashtag posts.
- All mid-tier (`#leadership`, `#productmanagement`, `#startups`) — niche hashtags get little reach here.

### Tone

- More analytical, fewer emojis, no "save for later" CTAs.
- Questions get higher engagement than declarations.
- Avoid hard sells. Education + thoughtful position = top performance.

### Alt-text

Same as Instagram — per-slide.

---

## TikTok

### Aspect

- Default: vertical `9:16` (1080 × 1920) — TikTok's native frame
- TikTok carousels (photo mode): full-bleed vertical only

### Caption

- Length: 2200 chars total, but TikTok caption is read as accompaniment to scrolling — keep it short.
- Structure:
  ```
  <hook — 1 short line, ≤80 chars>
  <optional: 1 supporting line>
  <CTA — comment + follow>
  <hashtags inline, 3-5 max>
  ```

### Hashtags

- 3-5 max. Mix one trending sound-related, two topical, two niche.
- TikTok algorithm weights sound + early engagement heavily — hashtags are secondary signal.

### Sound / music credit

If a sound was paired in the carousel concept: caption credits it (`Sound: <name>`). Default TikTok carousels use sound from the library; that's not part of THIS skill — sound is picked inside the app.

---

## Cross-platform variant (rarely advised)

If the user wants ONE carousel for both Instagram and LinkedIn:

- Use square `1:1` aspect (LinkedIn primary, Instagram acceptable).
- Write two captions: `captions.md` has `# Instagram` and `# LinkedIn` sections.
- Same images, different copy + hashtags.

Don't run as ONE prompt batch with both captions. Run carousel once, write both captions in the captions.md.

---

## captions.md structure

```markdown
# Carousel: <topic title> · <platform>

_Slides: N · Style: <style-id> · Model: <model-slug> · Generated: <date>_

## Main caption (paste into <platform> caption box)

<full caption per platform rules>

---

## Per-slide alt-text

- **Slide 1 (hook)**: <alt-text 1-2 sentences>
- **Slide 2 (point)**: ...
- ...

---

## Per-slide headlines (for overlay mode)

If you're adding text via your design tool (Canva / Figma / Photoshop), the headlines are:

- Slide 1: "<exact headline text>"
- Slide 2: "<exact headline text>"
- ...

(For embedded-text-mode runs, these are the text that was REQUESTED to be rendered inside the image. Verify the model rendered them correctly; if not, fall back to overlay.)

---

## Posting checklist

- Aspect ratio matches platform: <yes/no>
- Hashtag count: <N>
- First 100/200 chars hook landed: <yes/no>
- CTA present in final slide AND caption: <yes/no>
- Alt-text added per slide: <yes/no>
- Source/credit (if research-driven): <yes/no — see brief at ...>
```
