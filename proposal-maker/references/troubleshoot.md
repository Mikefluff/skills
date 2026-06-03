# Troubleshoot

## Items parse wrong / are missing
- Run `--parse-only` to see exactly what the parser produced (no network).
- Each item needs a **dash before the price**: `Name (url) — 10000 THB`. A line with no
  `—`/`–`/`-` before the number is skipped.
- Item URLs that contain `catalogue` are fine — item-parsing runs before footer detection.
- A name ending in a number with no qty intended (e.g. "Studio 54") will read the trailing
  number as qty. Reword, or move the number: "54 Studio".
- See [offer-format.md](offer-format.md) for the full grammar.

## "stated total ≠ computed" warning
Expected and healthy — the document shows the **computed** subtotal. Check whether a line
price is mistyped. Tell the user; fix the offer text and re-run. Never hand-edit
`offer.json` for delivery — fix the source offer so it stays the truth.

## A line item is flagged as a possible typo
A single line ≥60% of the total triggers `price_outliers` (e.g. `5 000 000` vs an intended
`5 000`). Confirm with the user, correct the offer, re-run.

## Brand colours/fonts are wrong or default-blue
- The site may serve styles via external CSS/JS the scraper can't see. Override:
  `--accent "#hex" --font "Family"`.
- Confirm reachability: `--check --brand-url <site>`.
- `brand.json.ok=false` → the site didn't load; defaults + overrides were used.

## Logo is invisible / faint on the light themes
The logo is likely a white/monochrome SVG. The brand **name** is always shown beside it as
the anchor. Options: pass a raster/dark `--logo <url>`, use `--brand-name`, or
`--template dark`.

## Photos don't load
- Online viewing references the brand CDN directly; some CDNs block hotlinking. Use
  `--embed-images` to base64-inline them into a portable single file.
- A specific item shows no photo → that catalogue page had no `og:image` or was blocked
  (best-effort; the item renders text-only).
- `--no-thumbnails` disables all photo fetching (offline / fastest).

## Cyrillic / emoji look broken
The file is UTF-8 with `<meta charset="utf-8">`. If a downstream tool mangles it, open the
HTML directly in a browser rather than a plain-text previewer.

## PDF
- Primary renderer is the **system browser's headless print-to-PDF** (Chrome / Chromium /
  Edge / Brave) — no Python deps, keeps clickable links, web fonts, and dark full-bleed
  backgrounds. Then Playwright, then WeasyPrint as fallbacks.
- Default (LLM) mode: after authoring, run
  `proposal-maker/scripts/run.py --pdf-from <…/proposal.html>` → writes `proposal.pdf`
  beside it.
- Quick mode: add `--pdf`.
- No browser/renderer at all → open `proposal.html` and Cmd/Ctrl+P → Save as PDF (identical
  result).
- **Size:** the browser stores print images near-losslessly (~15 MB for ~17 photo cards),
  so `print_pdf` runs a **Ghostscript** pass by default (`/ebook` @ 144 dpi) → ~0.5 MB,
  links intact. No `gs` installed → the full-res PDF is kept (`brew install ghostscript` /
  `apt install ghostscript` to enable shrinking). `--no-compress` keeps full-res;
  `--pdf-dpi 110` for even smaller, `--pdf-dpi 220` for print-grade.
- **Running header/footer (колонтитулы):** repeat on every page via the table
  `<thead>`/`<tfoot>` pattern with gap padding on the head/foot `<td>`. If inner-page
  content sits flush against a band, the gap padding is missing or was put on the content
  cell (where it only spaces the first/last page) — move it onto the thead/tfoot `<td>`.
- **White page margins:** add `@page{size:A4;margin:0}` and set `html,body{background:…}`
  so the full-bleed colour reaches the page edges.

## Currency shows the code instead of a symbol
Only THB/USD/EUR/RUB/GBP/JPY have symbols; others render the code. Override the whole
document with `--currency THB`.
