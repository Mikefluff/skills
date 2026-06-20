# INITE AI — saved proposal style

The brand look for INITE AI (AI-automation consulting, inite.ai), frozen so the next
client proposal renders the same in one pass. Deliberately different from the Double D
profile: this one is a minimal techy SaaS look, not a cinematic photo deck.

## Files

| File | What it is |
|---|---|
| `brand.json` | Resolved tokens — cyan `#22d3ee` accent, indigo `#1e3a8a` secondary, slate canvas `#0b1120`/`#0f172a`, **Fraunces** display serif + **Inter** body, white `inite.ai` logo. `is_dark` and the fonts are corrected here (the scraper returns `var(--font-inter)` and reads this Next.js site loosely). |
| `template.html` | The authored INITE proposal — a **clone source**, not a live document. Logo-only masthead, serif headline with one cyan italic word, 3 keyfacts, a hero visual, a before→after strip, a Protocol pipeline band (cyan arrows), three phases (Diagnose / Build / Handover) with cyan step circles + per-phase subtotals, a feature card with image + compact service cards with SVG node-glyphs, dot-grid background, running `thead`/`tfoot` colophons, `@page{margin:0}` full-bleed. |
| `img/hero.jpg`, `img/feature.jpg` | Reusable on-brand visuals (chaos→workflow node-graph / automation pipeline), compressed. Copy the `img/` folder alongside the template. Regenerate per offer if you want fresh ones. |

## The look in one line

Slate canvas, cyan `#22d3ee` accent, a Fraunces serif headline with a single cyan italic
word, Inter body and uppercase micro-labels, metric-forward (timeline / efficiency / ROI +
before→after), no photos — bordered service cards grouped into numbered Protocol phases.

## Reuse for a new INITE offer

INITE sells services, not catalogue products, so there are no per-item photos — skip
generation:

```bash
# 1) build the kit (parse + brand screenshot; no photo generation)
python3 proposal-maker/scripts/run.py --offer /tmp/new-offer.txt \
  --brand-url https://inite.ai --no-gen-photos

# 2) clone the saved style and swap the data
cp proposal-maker/brands/inite/template.html generated/proposal/<slug>/proposal.html
cp -r proposal-maker/brands/inite/img generated/proposal/<slug>/img   # hero + feature visuals
#   edit: hero (client name in the cyan <em>), the 3 keyfacts, the before→after strip,
#   the pipeline band, the Protocol phases + service cards (index / name / desc / WEEK / price),
#   and the total + optional retainer note. Keep the CSS, masthead, visuals and colophons.

# 3) render the PDF
python3 proposal-maker/scripts/run.py --pdf-from generated/proposal/<slug>/proposal.html
```

Deterministic `--quick` path with the tokens only:

```bash
python3 proposal-maker/scripts/run.py --offer /tmp/new-offer.txt \
  --quick --brand-file proposal-maker/brands/inite/brand.json --pdf
```

## Notes

- Offer items map to Protocol phases — Diagnose (the free diagnostic), Build (workflows +
  integration), Handover (training + hypercare). A monthly support retainer is shown as a
  note under the total, not summed into the fixed scope.
- Prefer `--brand-file brand.json` over a cold scrape so the cyan accent and Fraunces+Inter
  pairing are guaranteed.
