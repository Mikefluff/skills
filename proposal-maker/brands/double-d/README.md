# Double D Project — saved proposal style

The brand look we built for the Double D Project (event agency, Phuket) commercial
proposal, frozen so the next offer renders the same way in one pass instead of being
re-derived by hand.

## Files

| File | What it is |
|---|---|
| `brand.json` | Resolved brand tokens — accent `#99cc66`, secondary `#8cba51`, **dark** canvas `#0a0b0d`, Ubuntu, the white DD logo SVG. `is_dark` is forced to `true` here (the live scraper misreads this Tilda site as light). |
| `template.html` | The authored dark proposal — a **clone source**, not a live document. Hero with big Date/Time/Location keyfacts, 5 category blocks (Звук и Свет / Доп оборудование / Артисты / Декорации / Сервис) with large headers + per-category subtotals, big photo cards for showpieces + compact rows for utility items, running `thead`/`tfoot` colophons, `@page{margin:0}` full-bleed. |

## The look in one line

Near-black canvas, lime-green `#99cc66` accent, Ubuntu uppercase display headline with one
green accent word, cinematic per-item photos, category grouping with large scannable
headers, letterhead colophons on every page, prints to a Ghostscript-compressed PDF.

## Reuse for a new Double D offer

```bash
# 1) build the kit for the new offer (gets BRIEF.md + per-item catalogue photos)
python3 proposal-maker/scripts/run.py --offer /tmp/new-offer.txt

# 2) clone the saved style and swap the data
cp proposal-maker/brands/double-d/template.html \
   generated/proposal/<new-slug>/proposal.html
#   then edit: hero (event / client name), the Date/Time/Location keyfacts,
#   the category blocks + their items/prices/links/photos (from the new BRIEF.md),
#   and the grand total. Keep the CSS, masthead, colophons, and @page rules as-is.

# 3) render the PDF
python3 proposal-maker/scripts/run.py --pdf-from generated/proposal/<new-slug>/proposal.html
```

For the deterministic `--quick` template instead, feed the tokens directly:

```bash
python3 proposal-maker/scripts/run.py --offer /tmp/new-offer.txt \
  --quick --brand-file proposal-maker/brands/double-d/brand.json --pdf
```

## Notes

- Per-item photos come from the catalogue `og:image` (referenced by URL). Items the offer
  leaves without a link get an **AI-generated on-brand image** per offer (e.g. the
  «Авторская Фотозона» shot) — these are not stored here, they're regenerated per run.
- Prefer `--brand-file brand.json` over a fresh scrape so the dark mood and `#99cc66`
  accent are guaranteed; a cold scrape would read the site as light.
