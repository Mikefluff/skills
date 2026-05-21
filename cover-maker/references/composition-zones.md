# Composition zones — cover-maker

Per-medium composition templates. Each `--medium` has a distinct zone layout.

---

## Three-zone model

Like other -maker skills, covers use three zones:

1. **Title zone** — title + optional subtitle
2. **Visual zone** — illustration / photo / abstract
3. **Creator zone** — author / artist / organization

The proportions and positioning vary by medium.

---

## Album (1:1, 3000×3000)

```
┌─────────────────────┐
│                     │
│   [Title zone]      │  ← Top 20-25% OR overlaid centrally
│   Album title       │
│   (Artist)          │
│                     │
├─────────────────────┤
│                     │
│                     │
│   [Visual zone]     │  ← Middle 55% — artwork dominates
│   Artwork / photo   │
│                     │
│                     │
├─────────────────────┤
│   [Creator zone]    │  ← Bottom 20% OR overlaid in artwork
│   Artist name       │
└─────────────────────┘
```

Composition prompt fragment:

> Album cover composition, 1:1 square. Title text "<TITLE>" rendered prominently — either at the top in bold display weight OR integrated into the artwork. Visual zone dominant — artwork / photographic subject fills middle 55%. Artist name "<CREATOR>" subtle at bottom OR overlaid. Genre-appropriate composition: rock / metal = chaotic + maximalist; electronic = clean + minimal; jazz = restrained + photographic; pop = bold typography + central subject.

Genre-driven variations:

- **Hyperpop / experimental**: title scattered across the artwork, asymmetric, multi-color
- **Indie / folk**: hand-drawn / watercolor / illustrated, title humble + smaller
- **Hip-hop**: title bold + central, artist name prominent
- **Electronic / techno**: minimal, abstract / geometric, single accent color
- **Classical / jazz**: photographic, restrained typography
- **Metal / hardcore**: maximalist, dark palette, distorted typography

---

## Book (2:3 portrait, 1600×2400)

```
┌──────────────────┐
│  [Title zone]    │  ← Top 30% — title dominant
│  BOOK TITLE      │
│  Subtitle here   │
│                  │
├──────────────────┤
│                  │
│                  │
│  [Visual zone]   │  ← Middle 50% — illustration/photo
│                  │
│                  │
│                  │
│                  │
├──────────────────┤
│  [Creator zone]  │  ← Bottom 20%
│  Author Name     │
└──────────────────┘
```

Composition prompt fragment:

> Book cover composition, 2:3 portrait aspect. Title zone top 30%: "<TITLE>" in large display typography, with optional subtitle "<SUBTITLE>" immediately below in smaller weight. Visual zone middle 50%: <visual content>. Creator zone bottom 20%: "<CREATOR>" in subtle but legible weight. Genre-appropriate composition: literary fiction = restrained, photographic, minimal text decoration; genre fiction = bolder typography + atmospheric visual; non-fiction = clean, structured, sometimes abstract / geometric visual.

Genre-driven variations:

- **Literary fiction**: photo-realistic or painterly cover, restrained title, modernist serif typography
- **Thriller / mystery**: dark palette, atmospheric, bold title
- **Romance**: warm palette, often photographic, script + serif mix
- **Sci-fi / fantasy**: illustrated, dramatic, colored title with effects
- **Business / self-help**: typographic-dominant, abstract geometric visual, sans-serif
- **Memoir**: portrait photo, sans-serif modern title
- **Academic**: restrained, swiss-grid, minimalist

---

## Podcast (1:1, 3000×3000)

```
┌─────────────────────┐
│                     │
│                     │
│   [Title zone]      │  ← 40-60% — show name DOMINANT
│   SHOW NAME         │
│   (subtitle)        │
│                     │
│                     │
├─────────────────────┤
│   [Mascot/logo]     │  ← Optional, lower-third
│   [Creator zone]    │  ← Hosted by Name
└─────────────────────┘
```

Composition prompt fragment:

> Podcast cover composition, 1:1 square. Show name "<TITLE>" is the dominant element — large, bold, instantly readable at thumbnail scale. Optional subtitle "<SUBTITLE>" in smaller weight. Optional mascot / illustration / logo as a supporting element. Host name "<CREATOR>" subtle at bottom. Bold restrained typography. Single accent color for brand consistency. The cover must be legible at 60×60px (Apple Podcasts list view).

Common variations:

- **Personality show**: large title + small host photo, host's name overlaid
- **Topic show**: typographic-dominant, single illustration as accent
- **Network show**: bold title + smaller network-brand tag
- **Limited series**: dramatic title + atmospheric visual

---

## Magazine (2:3 portrait, 1600×2400)

```
┌──────────────────┐
│ [MASTHEAD]       │  ← Top 12% — large display
├──────────────────┤
│ [issue date]     │  ← Below masthead, smaller
├──────────────────┤
│                  │
│                  │
│  [Hero subject]  │  ← Middle 55-65% — face / scene
│                  │
│                  │
├──────────────────┤
│ [Cover lines]    │  ← Bottom 20-30%
│ 3-7 headlines    │
│ arranged around  │
│ the subject      │
└──────────────────┘
```

Composition prompt fragment:

> Magazine cover composition, 2:3 portrait. Top 12%: masthead "<TITLE>" in large display typography (custom-feel font). Below masthead: small issue date / number. Middle 55-65%: hero subject — face / object / scene. Cover lines (3-7 headline teasers) arranged around or below the subject, in mixed typography sizes. Color palette: bold + contrasted. The cover must read at newsstand / phone-screen scale.

For magazine covers, the `--subtitle` is often the date / issue number, and `--photo` is highly recommended (hero subject).

---

## Report (A4, 1240×1754)

```
┌──────────────────────────┐
│                          │
│ [Title zone]             │  ← Top 25%
│ Report Title             │
│ Subtitle / Category      │
│                          │
├──────────────────────────┤
│                          │
│                          │
│ [Visual zone]            │  ← Middle 55%
│ Chart-feel / abstract    │
│ or photographic          │
│                          │
│                          │
├──────────────────────────┤
│ [Creator zone]           │  ← Bottom 20%
│ Organization name        │
│ Date / version           │
└──────────────────────────┘
```

Composition prompt fragment:

> Report cover composition, A4 portrait. 1cm margin on all sides. Top 25%: title "<TITLE>" in large display typography with subtitle "<SUBTITLE>" below. Middle 55%: visual zone — abstract / data-feel / photographic, depending on report category. Bottom 20%: organization name "<CREATOR>" + date / version. Restrained corporate / institutional aesthetic. Reserved hierarchy. More whitespace than other mediums.

---

## Deck-cover (16:9 landscape, 1920×1080)

Two layout modes:

**Top-headline (default)**:

```
┌───────────────────────────────────────┐
│  [Title zone]                         │
│  Title  Subtitle                      │
├───────────────────────────────────────┤
│                                       │
│         [Visual zone]                 │
│                                       │
├───────────────────────────────────────┤
│ [Creator] · Date · Version            │
└───────────────────────────────────────┘
```

**Side-headline** (`--composition side-headline`):

```
┌────────────────┬──────────────────────┐
│  [Title]       │                      │
│                │                      │
│  Title         │   [Visual zone]      │
│  Subtitle      │                      │
│                │                      │
├────────────────┤                      │
│  [Creator]     │                      │
└────────────────┴──────────────────────┘
   40%               60%
```

Composition prompt fragment (top-headline):

> Deck cover slide composition, 16:9. Top 25%: title "<TITLE>" with optional subtitle "<SUBTITLE>". Middle 50%: visual element (abstract geometric / illustration / hero photo). Bottom 25%: creator "<CREATOR>" + date / version on a single horizontal line. Corporate pitch-deck aesthetic.

---

## LinkedIn-doc (1:1, 1080×1080)

```
┌─────────────────┐
│  [DocType tag]  │  ← Top 8% — "Whitepaper" / "Guide" / etc.
├─────────────────┤
│                 │
│  [Title zone]   │  ← 35% — title dominant
│  TITLE          │
│  Subtitle       │
│                 │
├─────────────────┤
│                 │
│  [Visual]       │  ← Middle 40%
│                 │
│                 │
├─────────────────┤
│  [Creator]      │  ← Bottom 15%
│  Author / Org   │
└─────────────────┘
```

Composition prompt fragment:

> LinkedIn document cover, 1:1 square. Top 8%: document type tag "<SUBTITLE>" (e.g., "Whitepaper", "Guide", "Annual Report"). Title zone 35%: "<TITLE>" in large display typography. Middle 40%: visual element — abstract / data / illustrative. Bottom 15%: creator "<CREATOR>" + tagline. Clean professional typographic dominance.

---

## Anti-clutter (enforced by prompt template)

1. **Title dominant.** All other elements support, never compete.
2. **Max 4 text elements** total (title + subtitle + creator + optional cover-line for magazines).
3. **One typeface category.** Style anchor specifies; model picks rendering.
4. **Negative space.** Especially for editorial / minimal styles.
5. **Subject doesn't overlap title.** Photographic covers must compose the subject below or around the title.

---

## Custom composition

For non-standard layouts: edit the per-medium templates in this file + add a `--composition` flag in `common/runners/cli/cover.py`. Current v1 supports default-per-medium + `side-headline` for deck-cover only.
