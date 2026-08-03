# Brand profiles — proposal-maker/brands/

Saved, reusable brand profiles. Each `<slug>/` holds a resolved `brand.json` (tokens verified against the real site — often correcting what a fresh scrape gets wrong), an authored `template.html` (the brand-faithful proposal to clone), cached `img/` assets when the brand's CDN is fragile, and a `README.md` with reuse instructions.

Prefer `--brand-file brands/<slug>/brand.json` over a fresh `--brand-url` scrape when a profile exists — profiles encode manual corrections a live scrape gets wrong (dark Tilda and Webflow sites reading as light, white SVG logos vanishing on light surfaces).

## Client profiles stay local

`.gitignore` excludes `brands/*/` by default. A saved profile carries a named client's brand tokens, their logo, and the authored structure of their real commercial offer — publishing that is the client's call, not yours. Your profiles live on your disk and work exactly the same; they simply do not travel with the repo.

The one profile that ships is the author's own brand, as a worked example of the format:

| Slug | Brand | Theme | Notes |
|---|---|---|---|
| [inite](inite/README.md) | INITE AI | light | Playfair Display for Cyrillic display type; cached hero/feature imagery in `img/` |

To publish a profile deliberately — your own brand, or a client who has agreed — add an exception next to the `inite` one in `.gitignore`.

## Adding a profile

1. Run a normal brand-kit build (`--brand-url <site>`), refine the authored HTML until the client-ready version.
2. Create `brands/<slug>/`: copy the corrected `brand.json`, the final `template.html`, any fragile remote assets into `img/`, and write a short `README.md` (what to swap per new offer: client block, items, totals; what to keep: CSS, colophons, print rules).
3. Add a row above.

## Reuse flow

```
python3 proposal-maker/scripts/run.py --offer <new-offer.txt> --brand-file proposal-maker/brands/<slug>/brand.json
```

Then clone `template.html` as the authoring base — swap the data blocks, keep the design system.
