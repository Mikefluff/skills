# Cover types — per-medium conventions

Each medium has typography + composition + size conventions. Pick the right `--medium` and the skill applies them.

---

## Album cover

**Aspect**: 1:1 (square). 3000×3000 is the Spotify / Apple Music spec.

**Typography conventions**:
- Title can be large + bold (genre-dependent)
- Artist name often smaller, sometimes hidden inside the artwork
- Genre tags / track count rarely on the cover

**Composition**:
- Subject-dominant (artwork or photo central)
- Title overlaid OR offset to side
- Heavy graphic / illustrative styles common
- Some genres (jazz, classical) use restrained typography; others (hyperpop, hardcore) use chaotic / maximalist treatment

**Required fields**:
- `--title` (album title)
- `--creator` (artist name) — strongly recommended

**Style hints**: photoreal-portrait styles, holographic, neon-cyberpunk, retro-magazine, watercolor work well. Avoid corporate / Swiss-grid which feel wrong for music.

**Recommended models**: `nano-banana-pro` (artist photo), `flux-2-pro` (palette), `ideogram-3-quality` (text-heavy clean covers).

---

## Book cover

**Aspect**: 2:3 portrait. 1600×2400 is Amazon KDP standard (matches most print POD specs).

**Typography conventions**:
- Title dominant — top half, large display weight
- Subtitle (if any) smaller, immediately below
- Author name at the bottom OR very small at top
- Genre-driven: fiction has restrained text + photographic/illustrative imagery; non-fiction often has bigger text + minimalist visual

**Composition**:
- Top zone: title (3-7 words typical)
- Middle zone: visual element OR continuation of title typography
- Bottom zone: author name + (optionally) endorsement / tagline

**Required fields**:
- `--title` (book title)
- `--creator` (author name) — strongly recommended

**Style hints**:
- Literary fiction: `photo-editorial-bw`, `kinfolk-minimal`
- Genre fiction (thriller / horror): `neon-cyberpunk`, `dark-academia`
- Business / non-fiction: `swiss-grid-poster`, `gradient-mesh-modern`
- Romance: `watercolor-soft`, `polaroid-faded`

**Recommended models**: `ideogram-3-quality` (default for text-heavy), `flux-2-pro` (palette/photoreal blend), `nano-banana-pro` (author photo embedded).

---

## Podcast cover

**Aspect**: 1:1 (square). 3000×3000 is the Apple Podcasts spec (also fits Spotify / Google Podcasts / Overcast / etc).

**Typography conventions**:
- Show name DOMINANT (it's the brand)
- Host name optional (some shows include, many don't)
- Tagline rare on the cover (goes in the description)
- Tight, branded typography — episodes share the same cover; consistency matters

**Composition**:
- Center-stacked or asymmetric typography
- Often a single bold graphic element (logo / mascot / abstract shape)
- Avoid photos unless the show is host-personality-driven (e.g., "Joe Rogan Experience" style)
- Color palette is the brand asset — consistent across episodes

**Required fields**:
- `--title` (show name)
- `--creator` (host name) — optional but common

**Style hints**: bold + clean works best — `swiss-grid-poster`, `bauhaus-primary`, `art-deco-gold`, `gradient-mesh-modern`, `sticker-mascot` (cartoon mascot covers).

**Recommended models**: `ideogram-3-quality` (text-clean default), `gpt-image-2` (Latin + CJK), `flux-2-pro` (palette consistency).

---

## Magazine cover

**Aspect**: 2:3 portrait. 1600×2400 typical (matches print magazine convention).

**Typography conventions**:
- **Masthead** (publication name) at top — large display, often custom typography
- Issue number / date in small caps below masthead OR in a corner
- Multiple "cover lines" (headlines for inside stories) — usually 3-7 lines, arranged around the central image
- "Hero image" (subject) dominates the visual zone

**Composition**:
- Top 15%: masthead
- Middle 65%: hero subject (face / object / scene)
- Cover lines arranged around the subject — left side, right side, bottom, or scattered
- Color palette: bold, contrasted; magazines need impact at the newsstand / phone-screen scale

**Required fields**:
- `--title` (masthead — magazine name)
- `--subtitle` (issue / date / cover-line teaser, optional)
- `--photo` (hero image, strongly recommended)

**Style hints**: `photo-editorial-bw`, `retro-magazine-70s`, `swiss-grid-poster`, `art-deco-gold`. Magazine aesthetics lean editorial.

**Recommended models**: `gpt-image-2` (best for multi-text + photo combined), `nano-banana-2` (photoreal cover), `nano-banana-pro` (identity-preserve for cover-star portraits).

---

## Report cover

**Aspect**: 1:√2 (~1240×1754 at 150 DPI, ~2480×3508 at 300 DPI). A4 portrait.

**Typography conventions**:
- Title large and clear — corporate or academic feel
- Subtitle / report number / date
- Organization name + logo space (logo overlaid externally)
- Often a date stamp or category tag

**Composition**:
- Top 25%: title + subtitle
- Middle 50%: visual (chart-style, abstract data viz, or photographic)
- Bottom 25%: organization name + date + category

**Required fields**:
- `--title` (report title)
- `--subtitle` (report subtitle / category)
- `--creator` (organization)

**Style hints**: `swiss-grid-poster`, `gradient-mesh-modern`, `bauhaus-primary`, `kinfolk-minimal`. Restrained, corporate / institutional.

**Recommended models**: `ideogram-3-quality` (clean text), `flux-2-pro` (brand palette).

---

## Deck cover (slide deck title slide)

**Aspect**: 16:9 landscape. 1920×1080.

**Typography conventions**:
- Big title (5-8 words)
- Subtitle / version / date on a single line
- Speaker name + role often at bottom

**Composition**:
- Top-half: title (large)
- Middle: optional visual (abstract / illustrative)
- Bottom-left or bottom-right: subtitle + creator

**Required fields**:
- `--title`
- `--creator` — speaker / company

**Style hints**: `swiss-grid-poster`, `gradient-mesh-modern`, `flat-vector-illustration`. Corporate / pitch-deck feel.

**Recommended models**: `ideogram-3-quality`, `flux-2-pro`.

---

## LinkedIn document cover (multi-page PDF)

**Aspect**: 1:1 (square). 1080×1080.

**Typography conventions**:
- Title + subtitle dominant
- Document type tag ("Whitepaper", "Annual Report", "Guide")
- Author / org footer

**Composition**:
- Top half: title
- Middle: visual element
- Bottom: document type + author

**Required fields**:
- `--title`
- `--creator` — author/org
- `--subtitle` — document type or one-line description

**Style hints**: `swiss-grid-poster`, `gradient-mesh-modern`, `kinfolk-minimal`, `flat-vector-illustration`.

---

## Custom medium

If you need a medium not listed here, use `--aspect WxH` to specify dimensions and pass through to the generic cover composition (title-dominant, optional subtitle, optional creator at bottom).

Examples:

```bash
cover-maker --title "Annual Report 2026" --creator "Acme Corp" --aspect 1080x1920 --style swiss-grid-poster --execute   # vertical for IG Story / TikTok
```

---

## Title constraints

Across all mediums:

- **≤6 words** for best results. Longer titles distort.
- **Use sentence case or title case**. ALL CAPS works for high-impact mediums (rock album, hardcore podcast). Sentence case for editorial / literary / corporate.
- **Avoid mid-title line breaks** unless the title is two clear halves of similar weight.
- **Special characters** (`™`, `&`, `—`) sometimes render as garbage. Test, adjust.
- **Numbers** in titles: `2026` reads fine; `1,847,392` does not. Spell out or simplify.

---

## Creator field

- Album: artist name (one main artist; featuring artists in `--subtitle`)
- Book: author name (or `Author Name with Co-Author Name`)
- Podcast: "Hosted by Name" or just "Name" — both work
- Magazine: not used in masthead (masthead IS the title); `--creator` ignored
- Report: organization name ("Acme Corp" or "Acme Research")
- Deck-cover: speaker name or company

---

## Subtitle field

Use sparingly. If the design feels balanced WITHOUT a subtitle, omit it.

Common uses:

- Book: tagline OR "A Novel" / "A Memoir"
- Album: featured artists or year
- Podcast: tagline ("A show about <topic>")
- Magazine: cover-line teaser
- Report: date / category / issue number
- Deck-cover: version + audience ("v2 · Investor Deck")

---

## Photo / reference image

Use `--photo` when:

- Album cover features a specific artist / band photo
- Book cover features the author photo (memoir / autobiography)
- Magazine cover features a hero subject (celebrity / story protagonist)
- You have a specific artwork / illustration you want integrated

Don't use `--photo` when:

- The cover should be purely typographic
- The "photo" is a logo (use brand assets in your editor instead)
- The reference is a low-res / heavily filtered image
