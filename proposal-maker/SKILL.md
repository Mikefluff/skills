---
name: proposal-maker
description: "Turn a raw commercial offer (client + line items + total) into an HTML proposal whose style copies a brand website. LLM-authored from a brand screenshot; --quick offline fallback. Output: proposal.html with clickable links + exact prices, prints to PDF. Use when: 'make a proposal', 'commercial offer', 'КП', 'коммерческое предложение'."

license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
End-to-end commercial-proposal generator. Input: a free-form offer (client block +
itemised order with prices + total, usually pasted from Telegram/WhatsApp) and a brand
site to copy the look from. Output: a single self-contained `proposal.html` that genuinely
**looks like that brand** and prints to a clean PDF.

The default is **LLM-authored, screenshot-driven**. A deterministic template can't capture
"dark, bold, dramatic brand with a green accent and uppercase display type" — it reads
colours by frequency and gets the mood wrong. So instead: a Python step assembles a
**brand kit**, and you (the orchestrator) *look at the brand* and *write the markup*.

Execute-layer modules under `common/runners/`:
1. `proposal_parse.py` — offer text → structured `skills.proposal.plan.v1` (items, prices,
   recomputed subtotal, mismatch + outlier flags).
2. `proposal_brand.py` — scrape brand tokens (accent / fonts / logo / name) + enrich each
   item with its real catalogue photo + description (`og:` tags).
3. `proposal_kit.py` — screenshot the brand site (headless Chrome), download the logo,
   write `BRIEF.md` bundling tokens + the item table + authoring rules.
4. `proposal_render.py` — the `--quick` deterministic themed template + HTML→PDF helper.

Why a document and NOT an image deck: a proposal carries **exact prices** and **clickable
product links**. AI image generation garbles both. You write real HTML text.

This skill does NOT: generate slides/images (use `carousel-builder`/`flyer-maker`); invent
prices or discounts; silently rewrite a suspicious number (it flags, you ask); log into a
CRM or send anything; compute tax/VAT.
</objective>

## ROLE

Build the brand kit → **look at the brand screenshot** → surface data-quality warnings to
the user → **author a bespoke `proposal.html` that mirrors the brand** → verify it by
screenshotting your own output → deliver. Fall back to `--quick` only when there's no LLM
loop or no network.

## PIPELINE (default — LLM-authored)

1. **Capture the offer.** Save the user's pasted offer verbatim to a temp file (or pipe via
   stdin). Don't reformat — the parser handles emoji headers, RU/EN keys, `Name (url) qty —
   price CUR` lines, and `Total:`.

2. **Build the brand kit:**
   ```bash
   python3 proposal-maker/scripts/run.py --offer /tmp/offer.txt
   # brand site auto-detected from the offer footer; or pass --brand-url <site>
   ```
   This writes to `./generated/proposal/<slug>/`: `site.png` (the brand screenshot),
   `logo.*`, `brand.json`, `offer.json` (enriched with per-item photo URLs), and
   `BRIEF.md`.

3. **Look at the brand.** `Read` `site.png` — actually view it. Note: dark vs light mood,
   type weight/case, where/how the logo sits, accent colour usage, imagery feel. Then read
   `BRIEF.md` for the tokens + the full item table (names, qty, prices, links, photo URLs).

4. **Surface warnings.** If the run printed `⚠ stated total ≠ computed` or `⚠ '<item>' is
   N% of the total — possible typo`, **tell the user and ask** before using that number.
   (The seed Double D offer has `Логистика 5 000 000` — 97% of the total — almost certainly
   `5 000`.) Never auto-fix; confirm, then correct the offer text and re-run if needed.

5. **Author `proposal.html`** into the kit folder. House rules:
   - **Mirror the screenshot.** Same mood (dark canvas if the site is dark), same type
     personality (the brand font from `BRIEF.md` via its Google Fonts link), the accent as
     the one hot colour, the logo placed like the site places it.
   - **Logo treatment.** Brand logos are often monochrome/white SVGs. On a dark header use
     as-is; on a light header tint to white via `filter:brightness(0) invert(1)` or set it
     on a dark/accent plate. **Always show the brand name beside it** so identity survives.
   - **Prominent key facts.** Lead the hero with a big Date / Time / Location block — the
     fields the client checks first — above smaller secondary pills (guests, phone).
   - **Group by category.** Split the items into 4–7 logical categories named for the
     client's domain (e.g. Звук и свет / Доп оборудование / Артисты / Декорации / Сервис),
     each with a **large, scannable header** (big type + accent marker), item count, and
     **per-category subtotal**. Never one long pile.
   - **Vary density.** Showpiece / high-value items → big photo cards; utility / low-cost
     items (controllers, stands, staff, logistics) → compact 2-column rows (small thumb +
     name + price). Don't render everything large — it reads as sprawling.
   - **Real photos.** Each item gets its `og:image` from `BRIEF.md` (Tilda URLs hotlink
     fine). Items the kit could not photograph from a link get an **auto-generated on-brand
     image** (kit fills these; marked in `BRIEF.md`) — use it and tell the user they can
     swap a real one. Never a blank/placeholder if a photo can be sourced.
   - **Exact data.** Prices and links exactly as parsed; the computed subtotal is the total;
     quantity chips where given.
   - **Self-contained.** One file: inline `<style>`, the Google Fonts `<link>`, CSS custom
     properties for the tokens.
   - **Print CSS (required — the PDF depends on it).** `@page{size:A4;margin:0}` to kill
     white margins (full-bleed). Running header **and** footer on every page via the
     **table `<thead>`/`<tfoot>`** pattern (`display:table-header-group`/`-footer-group` in
     print) — a `position:fixed` band can't reserve per-page space and looks broken on
     inner pages. `break-inside:avoid` on cards/total. `BRIEF.md` ships the exact recipe.

6. **Verify your output.** Screenshot the HTML you wrote and look at it:
   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
     --hide-scrollbars --window-size=1100,3600 --screenshot=/tmp/check.png \
     "file://$PWD/generated/proposal/<slug>/proposal.html"
   ```
   `Read` `/tmp/check.png`. Iterate until it genuinely reads as the brand. (`proposal_kit`
   exposes `find_browser()` for the binary path across platforms.)

7. **PDF (optional).** Render the authored HTML to PDF via the system browser (no extra
   deps — keeps clickable links + the dark background):
   ```bash
   python3 proposal-maker/scripts/run.py --pdf-from generated/proposal/<slug>/proposal.html
   # → proposal.pdf next to it
   ```
   No headless browser? Tell the user to open `proposal.html` and Cmd/Ctrl+P → Save as PDF.

8. **Deliver.** Print the paths (`proposal.html` + `proposal.pdf`).

## --quick (deterministic, offline / no-LLM)

Renders one of three CSS themes (editorial / invoice / dark) from `proposal_render.py` —
no screenshot, no authoring. Use when offline, when there's no LLM loop, or for a fast
draft. Themes + auto-pick: see `references/templates.md`.

```bash
python3 proposal-maker/scripts/run.py --offer /tmp/offer.txt --quick --template dark --pdf
```

## MODES

### Required
- `--offer <path|->` or `--offer-text "<…>"`.

### Brand (overrides stack on top)
- `--brand-url <site>` (else auto-detected from the offer footer) · `--brand-file <brand.json>` ·
  `--no-brand` (defaults, no network) · `--accent <#hex>` · `--font "<Family>"` ·
  `--logo <url|path>` · `--brand-name "<Name>"`.

### Build / look
- (default) brand-kit mode · `--quick` deterministic template · `--template auto|editorial|invoice|dark` (quick only) ·
  `--lang auto|ru|en` · `--no-thumbnails` · `--embed-images` (quick) · `--currency <CODE>`.

### Output / inspection
- `--pdf` (quick mode: render PDF via the system browser) · `--pdf-from <html>` (render any
  HTML file to PDF and exit — the default-mode PDF step) · `--output <dir>` ·
  `--parse-only` (parsed JSON, no network — best first dry-run) · `--check` (deps +
  `--brand-url` reachability).

## REFERENCES (load on demand)

| File | When |
|---|---|
| `BRIEF.md` (generated per run) | The live authoring brief — tokens, item table, rules. Read it every run. |
| [references/offer-format.md](references/offer-format.md) | Parse contract — header keys, item grammar, qty vs line-total, total/outlier policy. |
| [references/brand-extraction.md](references/brand-extraction.md) | What's scraped + manual overrides + the screenshot/kit step. |
| [references/templates.md](references/templates.md) | The 3 `--quick` themes + auto-pick. |
| [references/troubleshoot.md](references/troubleshoot.md) | Fonts/photos/logo/PDF/encoding issues. |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — the Double D Project event offer:
the deterministic template (the wrong, light read) vs. the LLM-authored, brand-faithful
dark proposal, plus the logistics-outlier handling.

## CONSTRAINTS

- **Look before you build.** In default mode you MUST view `site.png` before authoring.
  Don't trust `brand.json.is_dark` over your own eyes — the colour heuristic misreads
  dark Tilda/Webflow sites as light.
- **Copying the site's style is the whole point.** Match its mood, type, accent, logo.
- **Exact prices + clickable links.** Never render them as generated images.
- **Recompute, never silently rewrite.** Show the computed subtotal; flag a disagreeing
  stated total and any line ≥60% of the total; ask the user.
- **Verify by screenshot.** Author → screenshot → look → iterate. Don't ship unseen.
- **Enrichment is best-effort.** A dead catalogue link leaves that item text-only.
- **Output is `./generated/proposal/<slug>/`**; slug from client name + event + date.
- **No secrets.** Pure public-web scraping; no API keys.

## INVOCATION HINTS

Trigger when the user says: "make a proposal / commercial offer / quote", "turn this offer
into a nice document", "КП", "коммерческое предложение", "оффер для клиента", "смету
покрасивее", "proposal in the style of <site>", "копируй стиль с сайта"; or pastes a
Telegram/WhatsApp offer with 📆/👤/🧾/💰 fields + a price list.

Default: build the kit, view the screenshot, author the HTML. Recommend `--parse-only`
first if the offer formatting looks unusual. Reach for `--quick` only when offline or when
no authoring loop is available.

Distinct from `flyer-maker`/`carousel-builder`/`cover-maker` (those generate IMAGES) and
`landing-copy`/`cold-email` (those write prose).
