# Example — Double D Project event offer

The calibration case: a Telegram-style event-production offer pointing at
`www.doubledproject.com`.

## The raw offer (pasted)

```
📆 Date: 30-06-2026
👤 Name: Миша
🎉 Event: Birthday Party
📞 Phone: +66 00-000-0000
🗓 Comment: 30

🧾 Order:
Пакет PICNIC Basic (https://…/paket-picnic-basic)  — 10000 THB
Трипод / Тотем (https://…/tripod-totem) 2 — 6000 THB
…
Логистика (https://…/logistika)  — 5000000 THB

💰Total: 5154000 THB
…  сайт www.doubledproject.com
```

## Why the deterministic template was wrong

`--quick` ranks colours by frequency. Tilda serves lots of white in CSS even on a black
page, so it read `bg #ffffff`, picked the light `editorial` theme, and the **white logo
SVG vanished on white**. The result looked generic and *off-brand* — the real site is dark,
bold, uppercase, with a green accent and dramatic performer photography. A frequency
ranker can't see that. **An LLM looking at a screenshot can.**

## The default flow (LLM-authored)

```bash
python3 proposal-maker/scripts/run.py --offer /tmp/dd_offer.txt
```
```
… reading brand style from https://www.doubledproject.com
… enriched 16/16 item(s) with catalogue photos
⚠ 'Логистика' is 97% of the total (5000000.0) — possible typo; confirm with the user.
… screenshotting https://www.doubledproject.com for the brand kit

Brand kit ready: generated/proposal/миша-birthday-party-30-06-2026  (17 items, 5 154 000 ฿)
  → VIEW the screenshot:  …/site.png
  → READ the brief, then author proposal.html here:  …/BRIEF.md
```

Then the orchestrator:
1. **Views `site.png`** — sees a dark canvas, white "DD" logo, uppercase green-accent
   display type, cinematic event photos.
2. Reads `BRIEF.md` — brand tokens (`#99cc66`, Ubuntu + its Google Fonts link) and the full
   item table with real `og:image` URLs.
3. **Flags the outlier** to the user — `Логистика 5 000 000` is 97% of the total; confirms
   it should be `5 000`.
4. **Authors `proposal.html`** mirroring the brand: black canvas, white DD logo
   (`filter:brightness(0) invert(1)`) + brand name, uppercase `BIRTHDAY PARTY` with a green
   `PARTY`, accent pills for the meta, a 2-column grid of cinematic photo cards with green
   `×N` chips, a total band with a green glow, real catalogue links.
5. **Screenshots its own output**, looks at it, iterates until it reads as the brand.

The difference is night and day — the authored version looks like a Double D deck; the
template looked like a generic invoice.

## --quick (offline / no-LLM fallback)

```bash
python3 proposal-maker/scripts/run.py --offer /tmp/dd_offer.txt --quick --template dark
```
Renders the deterministic dark theme — decent, brand-coloured, but a fixed layout. Use when
there's no authoring loop or no network. `--template editorial|invoice|dark`,
`--lang ru|en`, `--no-thumbnails`, `--embed-images`, `--pdf` all apply here.

## Another brand

```bash
python3 proposal-maker/scripts/run.py --offer /tmp/other.txt --brand-url https://stripe.com
# → kit with stripe.com screenshot → author a clean, Stripe-flavoured proposal
```
