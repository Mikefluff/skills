# Slide-role taxonomy — carousel-builder

Every carousel slide has a ROLE. The role determines:

1. **What kind of content** lives on the slide (hook idea vs framework boxes vs data badges)
2. **The composition template** (hierarchy and visual structure)
3. **The information density expectation** (a hook is sparse; a data slide is dense)

The Python prompt builder (`common/runners/carousel_prompt_builder.py`) takes `(style, role, content, slide_number, total)` and assembles a figma-rigor prompt by combining the style anchor + role template + content + universal rules.

There are **9 supported roles**. A typical carousel uses 1 hook + 3-5 content slides + 1 CTA = 5-7 slides.

---

## Role catalog

### `hook` — provocation + setup

**Used for**: slide 1 of nearly every carousel. The job is to **stop the scroll** and earn the swipe to slide 2.

**Composition template**:
- Large title (3-7 words) in upper-center or upper-left
- Subtitle (≤10 words) immediately beneath title — sets context or sharpens the question
- Minimal supporting visual (atmospheric, style-appropriate)
- Page indicator "1 of N" bottom-center
- Swipe arrow "→ listai / swipe →" bottom-right

**Content slot contract**:
- `title` (required, ≤7 words) — the provocation
- `subtitle` (optional, ≤10 words) — the deepening line
- `visual_hint` (optional, ≤20 words) — what scene/object dominates

**Info-density**: SPARSE. The hook earns the swipe by being sharp, not by being informative.

**Anti-pattern**: bullet lists on hook slides. The hook is one big idea, not a preview of the deck.

---

### `point` — one developed idea

**Used for**: middle slides where one substantive idea needs space to land. Different from `hook` (which is provocation only) and from `framework` (which is multiple components).

**Composition template**:
- Headline (≤7 words) upper-center
- Body 1-2 sentences (≤40 words total) on a panel/plate
- Optional supporting visual mid-frame
- Page indicator + swipe

**Content slot contract**:
- `title` (required, ≤7 words) — the idea
- `body` (required, ≤40 words) — the development / unpacking / consequence
- `attribution` (optional) — if quoting

**Info-density**: MEDIUM. One idea, with reasoning visible.

---

### `framework` — N-box / N-column model

**Used for**: when content is a structured model with named components (2x2 matrix, 4 quadrants, 3 pillars, 5 phases, etc.).

**Composition template**:
- Small title at top naming the framework
- Grid of N boxes/cells in the center
- Each box has a header (1-2 words) and body (3-8 words)
- Optional connecting arrows between boxes if it's a flow

**Content slot contract**:
- `framework_name` (required, ≤6 words) — the model's name
- `boxes` (required, 2-9 entries) — each `{header: <text>, body: <text>}`
- `box_layout` (optional, default "grid") — `grid` / `2x2` / `horizontal` / `vertical` / `circular`

**Info-density**: HIGH. The framework IS the value of this slide.

---

### `data` — numbers in badges

**Used for**: when the slide's value is one or more striking numbers. Statistics, market sizes, growth rates, %s, ratios.

**Composition template**:
- One BIG number in a circle / pill / badge dominating the frame
- Caption beneath naming what the number means (≤8 words)
- If multiple stats: 2-4 badges in a row or grid, each with caption
- Optional small icon next to each number
- Page indicator + swipe

**Content slot contract**:
- `data_points` (required, 1-4 entries) — each `{value: "<78%>", caption: "<text>"}`
- `source` (optional, ≤10 words) — small attribution beneath the badge

**Info-density**: HIGH but visual. The numbers do the work.

---

### `steps` — process / sequence

**Used for**: ordered procedure, how-to, journey, lifecycle. "Step 1 → Step 2 → Step 3".

**Composition template**:
- Small title at top naming the process
- Horizontal or vertical sequence of 3-7 numbered steps
- Each step has a header and a short body
- Arrows between steps
- Page indicator + swipe

**Content slot contract**:
- `process_name` (required, ≤6 words)
- `steps` (required, 3-7 entries) — each `{number: 1, header: "<text>", body: "<text>"}`
- `direction` (optional, default "horizontal") — `horizontal` / `vertical` / `circular`

**Info-density**: HIGH. The sequence + each step's content.

---

### `comparison` — vs / before-after / two-column

**Used for**: contrasting two options, two states, two approaches.

**Composition template**:
- Title at top naming the comparison
- Two columns side-by-side, divided by a vertical rule or accent line
- Left column: label + body (e.g., "MYTH: ..." or "BEFORE: ...")
- Right column: label + body (e.g., "REALITY: ..." or "AFTER: ...")
- Page indicator + swipe

**Content slot contract**:
- `comparison_title` (required, ≤6 words)
- `left` (required) — `{label: "<text>", body: "<text>"}`
- `right` (required) — `{label: "<text>", body: "<text>"}`
- `divider_style` (optional) — `vertical-rule` / `arrow` / `vs-glyph`

**Info-density**: MEDIUM-HIGH. The contrast structure does most of the work.

---

### `quote` — pull quote

**Used for**: a single sentence/paragraph quote with attribution. Often a slide that anchors the deck's thesis.

**Composition template**:
- Open-quote glyph (large, decorative, style-appropriate)
- Quote text in italic or serif body, centered, taking 60-70% of frame
- Attribution beneath in smaller weight: "— <name>, <context>"
- Page indicator + swipe

**Content slot contract**:
- `quote` (required, ≤25 words) — the text
- `attribution` (required) — `{name: "<...>", context: "<...>"}`

**Info-density**: LOW (one quote) but HIGH IMPACT (carefully placed in the deck).

---

### `myth-vs-truth` — reality check

**Used for**: contrarian content. Common misconception on top, actual situation on bottom.

**Composition template**:
- Top half: label "MYTH" / "WHAT YOU'RE TOLD" / "THE STORY" in accent color
  - Body sentence (≤20 words) — the false/incomplete version
- Horizontal divider with a strong accent
- Bottom half: label "REALITY" / "WHAT ACTUALLY HAPPENS" / "THE FACT" in different accent
  - Body sentence (≤20 words) — the corrective
- Page indicator + swipe

**Content slot contract**:
- `myth_label` (optional, default "MYTH") — top label
- `myth` (required, ≤20 words) — the misconception
- `truth_label` (optional, default "REALITY") — bottom label
- `truth` (required, ≤20 words) — the correction

**Info-density**: MEDIUM. The contrast is the content.

---

### `cta` — call to action

**Used for**: final slide. Single clear action.

**Composition template**:
- Clear primary CTA phrase (≤8 words) on a prominent plate / button / underlay
- Optional secondary context line beneath (≤15 words)
- Author/brand attribution somewhere in frame
- Page indicator "N of N" bottom-center
- End marker (NOT swipe arrow) bottom-right — "конец" / "end" / closing glyph

**Content slot contract**:
- `cta_text` (required, ≤8 words) — the action
- `context` (optional, ≤15 words) — the reasoning / what they'll get
- `attribution` (optional) — brand / author

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

- **Hook overload**: trying to communicate the full deck thesis in slide 1. Don't. Slide 1 earns the swipe.
- **Atmospheric middle slides**: middle slides MUST carry information. If a middle slide is just "vibes + a sentence", it's wasted — it's why carousels feel hollow. Use `framework` / `data` / `steps` / `comparison` roles to force information density.
- **CTA-as-hook**: putting the CTA in slide 1 kills the swipe motivation. CTA goes LAST.
- **Same role repeated**: if you have 3 `point` slides in a row, the deck feels flat. Vary roles to vary visual rhythm.
- **No quote anywhere**: a quote slide (real attribution, real source) earns trust. Add one if the topic supports it.
