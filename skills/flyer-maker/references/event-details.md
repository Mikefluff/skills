# Event details — what to collect

Required vs. recommended fields, formatting conventions, edge cases.

---

## Required

### `--title "<text>"`

The headline. Renders large at the top of the flyer.

Constraints:
- **≤8 words** — past 8, text-in-image models distort. Skill warns at 6+ words.
- **Title Case or ALL CAPS** for impact. The skill doesn't enforce — it passes through. ALL CAPS often reads better at large sizes; Title Case feels more editorial.
- Avoid mid-headline line breaks unless the headline is exactly two short phrases of similar weight ("WORKSHOP / SLOW SOFTWARE").

Examples that work:
- `"Workshop: Slow Software"` (3 words)
- `"AI for Solo Founders"` (4 words)
- `"Postmodern Russian Literature: A Reading Group"` (5 words + descriptor — borderline)

Examples that need trimming:
- `"The Complete Guide to Building Successful Solo Founder Businesses in 2026"` (too long — use a shorter headline + subtitle)

---

## Strongly recommended (at least one)

A flyer without a date / location / CTA is just a styled headshot. Pass at least one of:

### `--date "<text>"`

Free-form date — the skill passes through verbatim. Conventional formats:

- `"15 June 2026"` (international)
- `"June 15, 2026"` (US)
- `"15 июня 2026"` (RU)
- `"Sat 15 Jun · 19:00"` (combined day + time)
- `"Every Tuesday, 7pm"` (recurring)

The skill includes `--date` content in the **details zone** at the bottom of the flyer.

### `--location "<text>"`

Venue name + city (or virtual).

- `"Brooklyn Studio, NYC"`
- `"Punkt Cafe · Berlin"`
- `"Online (Zoom link DM'd)"`
- `"123 Maple Ave, San Francisco"` (full address — gets truncated visually if long)

### `--cta "<text>"`

Call to action — the "what to do" line.

- `"Tickets: link in bio"`
- `"RSVP via DM"`
- `"Free entry · BYOB"`
- `"Limited seats · sliding scale"`
- `"Доступ по предварительной записи"`

Keep CTA to ≤10 words. Longer text in the details zone competes with the headline visually.

---

## Optional

### `--subtitle "<text>"`

A secondary line under the title. Used for tagline / description / hook.

- `"A reading group for the modernism-curious"`
- `"How to ship without a team"`
- `"Сезонная пьеса · одно вечернее представление"`

Subtitle is rendered smaller than the headline, larger than the details. Typography from the style anchor handles the hierarchy.

### `--time "<text>"`

Time of event. Usually merged with `--date`, but separate if the date is a series:

- `--date "Every Tuesday"` + `--time "19:00-21:00"`
- `--date "October 5-7"` + `--time "10am-6pm daily"`

When both are passed, the skill concatenates them in the details zone.

### `--lang en|ru`

Language of the embedded text. Default: auto-detect from `--title`. Pass explicit when:

- Mixing languages within one flyer (title EN, details RU)
- Forcing a language different from the title (rare)

The skill currently does NOT auto-translate. If you want bilingual flyers, run twice with different content:

```bash
/flyer-maker --title "Workshop: Slow Software" --date "15 June" --lang en
/flyer-maker --title "Воркшоп: Медленное ПО" --date "15 июня" --lang ru
```

Outputs go to separate `<slug>-en/` and `<slug>-ru/` directories (skill appends `-<lang>` if `--lang` ≠ auto-detected).

### `--photo <path-or-url>`

Reference image — passed to the chosen model as `image_url` kwarg.

- Local path: `./speaker.jpg` (will be uploaded by the provider if needed)
- Public URL: `https://example.com/photo.jpg` (provider fetches directly)

Use for:
- Speaker headshots (Nano Banana Pro preserves identity best)
- Venue shots (any multi-ref model — Flux 2 Pro / Seedream 5.0 work well)
- Theme images (mood-board reference)
- Brand assets (logo / color palette reference)

Don't use:
- Copyrighted images you don't have rights to
- Faces of people who haven't consented
- Low-resolution images that'll grain badly when scaled up to the flyer size

If `--photo` is passed AND `--model` is a non-ref-capable model, the skill:
- Default: auto-substitutes a ref-capable model (warn on stderr)
- With `--strict`: exits non-zero with the substitution suggestion

---

## What gets embedded in the prompt

The skill assembles per-aspect prompts that include:

```
Embed text:
  Headline: "<TITLE>"
  Subtitle: "<SUBTITLE>"             (if present)
  Date: "<DATE>"                      (if present)
  Time: "<TIME>"                      (if present, otherwise concatenated with date)
  Location: "<LOCATION>"              (if present)
  CTA: "<CTA>"                        (if present)
```

The model is instructed to render these as readable text within the composition zones (see `composition-zones.md`). It's not a layout engine — the AI image model decides exact placement based on the style anchor + composition hints.

---

## Slug rules

Event-slug derived from `--title`:

- Kebab-case lowercase
- Strip stop words (the, a, an, of, in, on, for, to) unless dropping them breaks meaning
- Max 40 chars
- ASCII only — transliterate non-Latin: "Воркшоп: Медленное ПО" → "workshop-slow-software"

Examples:

- `"Workshop: Slow Software"` → `workshop-slow-software`
- `"AI for Solo Founders in 2026"` → `ai-for-solo-founders-2026`
- `"Постмодерн: Сорокин"` → `postmodern-sorokin`

If the same slug + date already has a flyer dir, the skill appends `-2`, `-3`, etc.

Override with `--output <dir>` to fully control the path.

---

## Anti-patterns (don't do this)

### Stuffing everything into the title

❌ `--title "Workshop: Slow Software · Sat 15 June 19:00 at Brooklyn Studio NYC · Tickets in bio"`

Result: title text overflows, model truncates / distorts.

✓ `--title "Workshop: Slow Software" --date "Sat 15 Jun · 19:00" --location "Brooklyn Studio, NYC" --cta "Tickets in bio"`

### Conflicting language in a single flyer

❌ `--title "Workshop" --date "15 июня" --location "Brooklyn"`

Result: mixed-script rendering tends to look broken on most models.

✓ Pick one language per flyer. Run twice for bilingual.

### Pulling in a tiny / blurry photo

❌ `--photo ./240x240-pixelated.jpg`

Result: model can't extract identity / palette cleanly; output looks like a worse version of the input.

✓ Use a clean, well-lit image at ≥800px on the short edge.

### No date / location / CTA

❌ `--title "Slow Software"` (no other fields)

Result: a styled wordmark on a poster background. Probably not what you wanted.

✓ Add at least one detail field, or use `image-prompt` directly for a generic styled image.
