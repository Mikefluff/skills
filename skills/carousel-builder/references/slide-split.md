# Slide split — how to break content into N slides

How content gets divided into role-tagged slides, and the composition hint each role applies.

---

## Slide-count templates

### 3 slides — minimal teaser

| # | Role | Purpose |
|---|---|---|
| 1 | hook | Headline + one-liner |
| 2 | point | Main message in one slide |
| 3 | cta | Action |

### 6 slides — short post

| # | Role | Purpose |
|---|---|---|
| 1 | hook | Headline + hook one-liner |
| 2-4 | point | 3 distinct points |
| 5 | conclusion | Micro-conclusion |
| 6 | cta | Action |

### 8 slides (default) — standard carousel

| # | Role | Purpose |
|---|---|---|
| 1 | hook | Bold headline + one-liner question or claim |
| 2 | point | Setup / context |
| 3 | point | Key fact #1 |
| 4 | data | Statistic, chart-like, or framework |
| 5 | point | Key fact #2 |
| 6 | quote | Notable quote OR framework |
| 7 | conclusion | Synthesis / micro-conclusion |
| 8 | cta | Action — "save / share / DM / sign up" |

### 10 slides — long-form explainer

| # | Role | Purpose |
|---|---|---|
| 1 | hook | Headline |
| 2 | point | The problem framing |
| 3-5 | point | 3 distinct facts |
| 6 | data | Stat or framework |
| 7 | quote | Authority quote |
| 8 | framework | Visual model / framework / map |
| 9 | conclusion | Synthesis |
| 10 | cta | Action |

### 12 slides — long deep-dive

12 = 8 standard + 4 extra `point` slides. Best for LinkedIn educational posts where attention budget is high.

---

## Composition hint per role

The "Composition" line in each per-slide prompt is role-driven. The style anchor handles the AESTHETIC; the composition hint handles the LAYOUT for that slide.

### hook (slide 1)

> Composition: bold centered headline takes 50-60% of frame, secondary tagline below; high contrast, generous negative space; subject (if visual) lower-right corner balancing the type weight.

For embedded text mode, the headline is the literal text — render at large size, prominent typography, in the palette of the style anchor.

### point

> Composition: a single illustrative element centered or rule-of-thirds; supporting text headline upper-third (if embedded) OR caption space lower-third (if overlay); one focal subject only.

### data

> Composition: numerical or framework visual — a single big number / percent / chart-like shape dominating center; minimal supporting text; high information density.

### quote

> Composition: text-dominant slide; large quoted line in the style's display typography; attribution smaller below-right; minimal or no illustrative element — let the text be the image.

### framework

> Composition: schematic / diagrammatic — boxes, arrows, axes, layered shapes that imply a model. Restrained palette. Position labels with white space.

### conclusion

> Composition: similar to hook but inverted — calmer, denser type, more body text space; subject element receding to background.

### cta

> Composition: bold simple visual — single subject or graphic mark; large call-to-action text; arrow / pointer / circular element implying action; high contrast.

---

## Auto-split from a research brief

When `--research <path>` is passed and the brief has these sections (per research-brief output-format):

| Brief section | Carousel role mapping |
|---|---|
| TL;DR sentence 1 | Hook (slide 1) |
| TL;DR sentence 2-3 | Point (slide 2) |
| Key facts bullets 1-N | Distribute to point + data slides (3-5 of them) |
| Notable quotes | One quote slide (slide 6 or 7) |
| Suggested angles | Used to pick OVERALL angle (which suggested angle to lean on) — not a slide |
| Open questions / Out of reach | Skip — these are research-internal |
| TL;DR sentence 3 (contrarian frame) | Often becomes the conclusion |
| Closing | CTA — usually a save / follow / DM action tied to the angle |

If the brief is `--for carousel` (in metadata), it's already structured to support this split.

---

## Auto-split from a free-form `--topic`

The skill drafts content first via `essay-write` or `viral-text`, then splits the draft into roles.

Heuristic for splitting:
1. First sentence → hook
2. Find the 3-5 strongest claims (named facts / numbers / definitions) → point / data slides
3. Find any quotable line → quote slide
4. Final synthesis → conclusion
5. CTA: pick from { "save for later" | "share with [audience]" | "DM for [resource]" | "follow for more on [topic]" } — let context pick.

---

## Slide content prompt template

For each slide, after style anchor is applied, the content portion of the per-slide prompt looks like:

```
SLIDE_<N>/<TOTAL> · role: <role>

Subject / scene: <one-sentence visual description — what the IMAGE shows>.

<if role is data> Number / framework: <the specific number or shape to render>.

<if role is quote> Quote text: "<exact quote>".

<if embedded text mode> Headline text: "<EXACT HEADLINE for this slide, 3-8 words>".

Composition: <role-specific from above>.

Aspect ratio: <portrait 4:5 | square 1:1 | story 9:16>.
```

That content block is APPENDED to the style anchor. Provider gets the full prompt as one string.

---

## Headline writing per slide (embedded text mode)

When `--text-mode embedded`:

- Headlines are 3-8 words. Longer = the AI image model truncates or distorts.
- All-caps for impact-heavy roles (hook, cta). Sentence case for educational (point, conclusion).
- One typeface per carousel — drawn from the style anchor's typography spec.
- No mid-headline line breaks unless the headline is exactly 2 short phrases.
- Quote slide: the quote IS the visual. No additional headline. Just the quote + attribution.

When `--text-mode overlay` or `--text-mode none`:

- Headlines still get DRAFTED for the captions.md file (so the user can overlay them in their design tool).
- Prompts do NOT include "embed headline text" instructions.

---

## CTA writing rules

| Platform | CTA style |
|---|---|
| Instagram | "Save for later · Share with someone who needs this" |
| LinkedIn | "Follow [Name] for more on [topic]. Drop a comment with your take." |
| TikTok | "Comment 'X' for the link" or "Save · Share · Follow" |

CTA slide visual:
- Single bold word or short phrase
- An action symbol (arrow, bookmark, share icon shape — abstracted into the style)
- High contrast — must be the most attention-grabbing slide

---

## Caption split

`captions.md` has two parts:

1. **Main post caption** — what the user pastes into the platform's caption box. Per platform rules in `platform-presets.md`.

2. **Per-slide alt-text** — accessibility alt-text for each slide. 1-2 sentences describing what's visible (helps screen readers + ranks the post). Generated automatically from the slide content prompt.

Example:

```markdown
# Caption — instagram

The 4 tools that 73% of solo founders now use daily.
Voice-first AI is winning. Vertical tools beat horizontal hubs.
What's in your stack?

#solofounder #aiproductivity #foundertools #startup #2026 ...

---

## Slide alt-text

- Slide 1: Bold serif headline "The Solo Founder Stack 2026" centered on muted cream background with a small bookmark-shaped accent in burnt sienna lower-right.
- Slide 2: ...
```
