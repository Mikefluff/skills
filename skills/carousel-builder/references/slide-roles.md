# Slide-role taxonomy — carousel-builder

Every carousel slide has a ROLE. The role determines:

1. **What kind of content** lives on the slide (hook idea vs framework boxes vs data badges)
2. **The composition** (hierarchy and visual structure to brief into `image-prompt`)
3. **The information density expectation** (a hook is sparse; a data slide is dense)

In v2.13.0+, the carousel-builder skill **chains the `image-prompt` skill** per slide. For each slide:

1. Gather the structured CONTENT (real headlines, real framework boxes, real data values + captions, real quote + attribution — see the per-role brief contracts below)
2. Compose a STRUCTURED BRIEF for `image-prompt` that includes the style anchor + role-specific composition guidance + actual content + universal rules + slide marker / swipe arrow / end marker + aspect
3. `image-prompt` returns a natural-language designer-grade prompt (~80-150 words, no meta-labels)
4. Place the returned prompt into the carousel plan as `items[i].prompt`

The CLI is a thin batch runner — it expects fully-written prompts in `items[].prompt`, NOT structured content. The Python prompt builder that existed in v2.10.x–v2.12.x was removed in v2.13.0; prompt writing belongs to the LLM (via image-prompt skill), not a template engine.

There are **9 supported roles**. A typical carousel uses 1 hook + 3-5 content slides + 1 CTA = 5-7 slides.

---

## How to brief `image-prompt` per slide

When invoking image-prompt for a slide, structure the brief like this (natural language, ≤200 words, designer voice — NOT a checklist of LABELS):

> Style anchor (verbatim from the chosen carousel style's text-in-image mode block).
>
> Slide N of M — role: `<role>`. Composition: `<role-specific composition guidance from below>`. Content to render IN the image (text-in-image mode), use exact quoted strings: "<title>", "<subtitle>", "<box headers and bodies>", "<data values and captions>", etc.
>
> Aspect: `<4:5 / 1:1 / 9:16>`. Slide marker bottom-center: "N из M" / "N of M". Bottom-right: swipe arrow ("листай →" / "swipe →") for slides 1..M−1, or end marker ("конец" / "end.") for the final slide.
>
> Multi-ref / character hint (if present and constant across deck): one sentence.
>
> Closing line — anti-AI-tells: sharp text rendering, all letters fully formed, no melted glyphs, no gradient text effects, no drop shadows on type, no AI face artifacts, no double-pupils, no extra fingers, no warped geometry.

`image-prompt` will absorb this brief and produce a single dense paragraph of designer-grade natural language. Do NOT pre-bake the answer with meta-labels like "HEADLINE: ..." / "SUBTITLE: ..." / "FRAMEWORK: ..." — that produces the magazine-with-text-overlay failure mode. Let image-prompt translate the structure into spatial / typographic / compositional language.

---

## Role catalog

### `hook` — provocation + setup

**Used for**: slide 1 of nearly every carousel. The job is to **stop the scroll** and earn the swipe to slide 2.

**Composition guidance** (brief to image-prompt):
- Large title (3-7 words) in upper-center or upper-left, bold, primary plate, 12-18% of frame height, 2-3 lines with balanced wrap, sentence case
- Subtitle (≤10 words) on a SEPARATE smaller secondary element (pill / chip / italic ribbon), visually distinct from headline plate, accent color, 3-5% of frame height
- Optional MAIN SUBJECT filling lower 50-65% of canvas (atmospheric scene-y element, character, or hero object), visually interacting with the type
- 3-5× scale contrast headline-to-subtitle; generous negative space; type and subject feel COMPOSED together not stacked
- Page indicator "1 of N" bottom-center
- Swipe arrow "→ listai / swipe →" bottom-right

**Content brief contract**:
- `title` (required, ≤7 words) — the provocation
- `subtitle` (optional, ≤10 words) — the deepening line
- `visual_hint` (optional, ≤20 words) — what scene/object dominates

**Info-density**: SPARSE. The hook earns the swipe by being sharp, not by being informative.

**Anti-pattern**: bullet lists on hook slides. The hook is one big idea, not a preview of the deck.

---

### `point` — one developed idea

**Used for**: middle slides where one substantive idea needs space to land. Different from `hook` (which is provocation only) and from `framework` (which is multiple components).

**Composition guidance**:
- Headline (≤7 words) upper-center
- Body 1-2 sentences (≤40 words total) on a panel/plate
- Optional supporting visual mid-frame
- Page indicator + swipe

**Content brief contract**:
- `title` (required, ≤7 words) — the idea
- `body` (required, ≤40 words) — the development / unpacking / consequence
- `attribution` (optional) — if quoting

**Info-density**: MEDIUM. One idea, with reasoning visible.

---

### `framework` — N-box / N-column model

**Used for**: when content is a structured model with named components (2x2 matrix, 4 quadrants, 3 pillars, 5 phases, etc.).

**Composition guidance**:
- SECTION LABEL at top — small all-caps eyebrow + thin accent underline naming the framework
- Grid of N boxes filling middle 65-75% of frame, equal-sized cells, consistent gutters, low-opacity tinted fill, 1px stroke border in accent color, rounded corners
- EACH CARD has: bold accent-colored eyebrow/number/label (3-4% of frame height) + neutral body text beneath (2-3% of frame height)
- Optional connecting arrows between boxes if it's a flow
- Visual weight equality across cards
- If character/MAIN SUBJECT is the constant unifier across the deck: position to right of grid or interacting with one card (overrides background-only policy)
- Page indicator + swipe

**Content brief contract**:
- `framework_name` (required, ≤6 words) — the model's name
- `boxes` (required, 2-9 entries) — each `{header, body}` with REAL content (not lorem-ipsum-like word salad)
- `box_layout` (optional) — `grid` / `2x2` / `horizontal` / `vertical` / `circular`
- `visual_hint` (optional) — character / hero subject if constant across deck

**Info-density**: HIGH. The framework IS the value of this slide.

---

### `data` — numbers in badges

**Used for**: when the slide's value is one or more striking numbers. Statistics, market sizes, growth rates, %s, ratios.

**Composition guidance**:
- One BIG number in a circle / pill / badge dominating the frame
- Caption beneath naming what the number means (≤8 words)
- If multiple stats: 2-4 badges in a row or grid, each with caption
- Optional small icon next to each number
- Page indicator + swipe

**Content brief contract**:
- `data_points` (required, 1-4 entries) — each `{value, caption}` (e.g., `{value: "78%", caption: "of teams ship late"}`)
- `source` (optional, ≤10 words) — small attribution beneath the badge

**Info-density**: HIGH but visual. The numbers do the work.

---

### `steps` — process / sequence

**Used for**: ordered procedure, how-to, journey, lifecycle. "Step 1 → Step 2 → Step 3".

**Composition guidance**:
- Small title at top naming the process
- Horizontal or vertical sequence of 3-7 numbered steps
- Each step has a header and a short body
- Arrows between steps
- Page indicator + swipe

**Content brief contract**:
- `process_name` (required, ≤6 words)
- `steps` (required, 3-7 entries) — each `{number, header, body}`
- `direction` (optional) — `horizontal` / `vertical` / `circular`

**Info-density**: HIGH. The sequence + each step's content.

---

### `comparison` — vs / before-after / two-column

**Used for**: contrasting two options, two states, two approaches.

**Composition guidance**:
- Title at top naming the comparison
- Two columns side-by-side, divided by a vertical rule or accent line
- Left column: label + body (e.g., "MYTH: ..." or "BEFORE: ...")
- Right column: label + body (e.g., "REALITY: ..." or "AFTER: ...")
- Page indicator + swipe

**Content brief contract**:
- `comparison_title` (required, ≤6 words)
- `left` (required) — `{label, body}`
- `right` (required) — `{label, body}`
- `divider_style` (optional) — `vertical-rule` / `arrow` / `vs-glyph`

**Info-density**: MEDIUM-HIGH. The contrast structure does most of the work.

---

### `quote` — pull quote

**Used for**: a single sentence/paragraph quote with attribution. Often a slide that anchors the deck's thesis.

**Composition guidance**:
- Open-quote glyph (large, decorative, style-appropriate)
- Quote text in italic or serif body, centered, taking 60-70% of frame
- Attribution beneath in smaller weight: "— <name>, <context>"
- AT MOST ONE small decorative element (inkwell silhouette, corner ornament, ivy leaf, etc.) — no full scene
- Page indicator + swipe

**Content brief contract**:
- `quote` (required, ≤25 words) — the text
- `attribution` (required) — `{name, context}`

**Info-density**: LOW (one quote) but HIGH IMPACT (carefully placed in the deck).

---

### `myth-vs-truth` — reality check

**Used for**: contrarian content. Common misconception on top, actual situation on bottom.

**Composition guidance**:
- Top half: label "MYTH" / "WHAT YOU'RE TOLD" / "THE STORY" in accent color + body sentence (≤20 words)
- Horizontal divider with a strong accent
- Bottom half: label "REALITY" / "WHAT ACTUALLY HAPPENS" / "THE FACT" in different accent + body sentence (≤20 words)
- Page indicator + swipe

**Content brief contract**:
- `myth_label` (optional, default "MYTH") — top label
- `myth` (required, ≤20 words) — the misconception
- `truth_label` (optional, default "REALITY") — bottom label
- `truth` (required, ≤20 words) — the correction

**Info-density**: MEDIUM. The contrast is the content.

---

### `cta` — call to action

**Used for**: final slide. Single clear action.

**Composition guidance**:
- Clear primary CTA phrase (≤8 words) on a prominent plate / button / underlay
- Optional secondary context line beneath (≤15 words) on a separate smaller sub-plate
- Author/brand attribution somewhere in frame (small, lower-left or lower-center)
- AT MOST ONE small decorative element OR character if constant across deck
- Page indicator "N of N" bottom-center
- End marker (NOT swipe arrow) bottom-right — "конец" / "end" / closing glyph

**Content brief contract**:
- `cta_text` (required, ≤8 words) — the action
- `context` (optional, ≤15 words) — the reasoning / what they'll get
- `attribution` (optional) — brand / author
- `visual_hint` (optional) — character / hero subject if constant across deck

**Info-density**: LOW (one CTA) but PURPOSEFUL.

**Anti-pattern**: multiple CTAs on the same slide. Pick one.

---

## Picking roles for a deck

### Default deck structure by slidesCount

| Slides | Roles |
|---|---|
| 3 | hook → point → cta |
| 5 | hook → point → framework-OR-data → point → cta |
| 6 | hook → point → framework → data → quote → cta |
| 7 | hook → point → framework → data → quote → comparison → cta |
| 8 | hook → point → framework → data → comparison → quote → steps → cta |
| 10 | hook → point × 6 (mix framework/data/quote/comparison) → cta |

### Per-domain bias

- **Education / explainer**: hook + framework + steps + comparison + cta. Use `myth-vs-truth` for contrarian takes.
- **Data-led / business**: hook + data + framework + comparison + cta.
- **Manifesto / contrarian essay**: hook + myth-vs-truth + quote + point + cta.
- **Product launch**: hook + framework (features) + data (proof) + quote (testimonial) + cta.
- **How-to**: hook + steps + point (warnings) + cta.
- **Curated list**: hook + (point × N) + cta. Or use one `framework` with N boxes if compact.

---

## Per-role composition density (info-per-frame)

Approximate target by role:

| Role | Words on slide | Layout density |
|---|---|---|
| hook | 5-15 | Sparse |
| point | 30-60 | Medium |
| framework | 30-80 | High |
| data | 5-30 (numbers dominate) | High visual |
| steps | 30-80 | High |
| comparison | 30-50 | Medium |
| quote | 15-35 | Low |
| myth-vs-truth | 25-50 | Medium |
| cta | 5-20 | Sparse |

Total deck word count: typically 200-450 across 5-8 slides.

---

## Anti-patterns

- **Python-template prompts**: a generated prompt that reads as "HEADLINE: X / SUBTITLE: Y / FRAMEWORK: Z" with meta-labels. The image model renders the labels as text. ALWAYS go through `image-prompt` so the brief becomes natural designer language.
- **Hook overload**: trying to communicate the full deck thesis in slide 1. Don't. Slide 1 earns the swipe.
- **Atmospheric middle slides**: middle slides MUST carry information. If a middle slide is just "vibes + a sentence", it's wasted. Use `framework` / `data` / `steps` / `comparison` roles with REAL content (not placeholder word salad) to force information density.
- **CTA-as-hook**: putting the CTA in slide 1 kills the swipe motivation. CTA goes LAST.
- **Same role repeated**: if you have 3 `point` slides in a row, the deck feels flat. Vary roles to vary visual rhythm.
- **No quote anywhere**: a quote slide (real attribution, real source) earns trust. Add one if the topic supports it.
- **Identical scene every slide**: caused by scene-y style anchors. Keep the anchor as VOCABULARY (palette + treatment + typography + element list), put per-slide scene cues in the role's `visual_hint` or composition guidance. See `_universal-rules.md` §0.
