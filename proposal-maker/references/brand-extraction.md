# Brand extraction (`proposal_brand.py`)

"Copy the style from a site" = read the brand's public HTML/CSS and lift the design tokens
a proposal needs. Pure `requests` + stdlib regex — no headless browser, no API key. Works
well on Tilda / Webflow / WordPress / most marketing sites because they expose enough in
the served HTML and in `og:` meta.

## What `extract(url)` returns (`brand.json`)

| Field | Source | Notes |
|---|---|---|
| `accent`, `accent2` | hex + `rgb()` colours in inline styles & `<style>`, ranked by frequency, filtered to saturated mid-luminance | drops near-white/black/grey; the most-used vivid colour wins |
| `bg`, `text`, `is_dark` | most-frequent near-white (or near-black for dark-dominant sites) | drives the auto theme + text colour |
| `font_heading`, `font_body` | `fonts.googleapis.com/css2?family=…` links first, then ranked `font-family:` declarations | generic stacks (Arial, system-ui, Roboto…) skipped |
| `google_fonts_url` | the page's Google Fonts link, or one synthesised from the family names | injected into the document `<head>` |
| `logo_url` | `<img>` whose src/alt smells of "logo", else `og:image`, else apple-touch-icon/favicon | resolved to absolute |
| `name`, `tagline` | `og:site_name` → `og:title` → `<title>` (trimmed at `-`/`\|`); `og:description` | `name` is the masthead identity |
| `hero_url` | `og:image` | reserved for future hero use |

Calibration (doubledproject.com): `accent #99cc66`, `accent2 #8cba51`, `font Ubuntu`
(+ correct css2 link with `subset=latin,cyrillic`), logo `DD_logo_Vector.svg`,
name `Ивент-Агентство на Пхукете`.

## The brand kit (default mode)

Token scraping alone misreads mood — a dark Tilda/Webflow site serves white-heavy CSS and
gets ranked as light. So the default mode also captures a **screenshot** of the brand site
(`proposal_kit.capture_screenshot()` via any headless Chrome/Chromium/Edge/Brave, found by
`find_browser()`), downloads the logo locally, and writes `BRIEF.md`. The orchestrator
**looks at `site.png`** and authors HTML from what it sees — the screenshot overrides the
`is_dark` heuristic. No browser installed → the kit ships without a screenshot and says so.

## Per-item enrichment

`enrich_items(items)` fetches each line item's URL (thread-pooled, cap 6, failure-tolerant)
and fills:
- `thumb` ← `og:image` (the real product photo)
- `desc` ← `og:description` (double-decoded, nbsp-stripped)
- `canonical_name` ← `og:title` (kept in data, but the offer's own wording is displayed)

ON by default. `--no-thumbnails` skips it (faster, fully offline). A blocked/dead link
just leaves that item text-only.

## When the scrape misses

Some sites hide colours/fonts behind external CSS or JS. Override explicitly — overrides
always beat the scrape:

```bash
--accent "#99cc66" --font "Ubuntu" \
--logo "https://…/logo.svg" --brand-name "Double D Project"
```

- No usable accent found → defaults to `#1f6feb` (a neutral blue). Pass `--accent`.
- Logo is a monochrome/white SVG → may be faint on a light theme. The brand **name** is
  always shown next to it; use `--template dark` or a raster `--logo` if it must pop.
- Site unreachable → `brand.json.ok` is false, defaults + overrides are used; the document
  still renders.

## Reuse a brand

The first run writes `brand.json`. Reuse it across proposals for the same client without
re-scraping:

```bash
python3 proposal-maker/scripts/run.py --offer next.txt \
  --brand-file ./generated/proposal/<slug>/brand.json
```
