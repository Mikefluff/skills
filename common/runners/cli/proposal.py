"""Proposal document builder CLI — the execute layer for proposal-maker.

Pipeline: read offer → parse → resolve brand (scrape / file / manual) →
enrich line items with catalogue photos → render self-contained HTML →
optional PDF → write outputs + manifest. No paid API; HTTP only.

Outputs (default ./generated/proposal/<slug>/):
  proposal.html   self-contained, clickable links, print-to-PDF ready
  proposal.pdf    only with --pdf AND a local renderer (playwright/weasyprint)
  brand.json      resolved brand tokens
  offer.json      parsed offer (skills.proposal.plan.v1)
  manifest.json   run metadata
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .. import proposal_brand as brand_mod
from .. import proposal_brief as brief_mod
from .. import proposal_kit as kit_mod
from .. import proposal_parse as parse_mod
from .. import proposal_render as render_mod


def _slugify(*parts: str, max_len: int = 50) -> str:
    raw = "-".join(p for p in parts if p)
    raw = re.sub(r"[^0-9A-Za-zА-Яа-яЁё]+", "-", raw).strip("-").lower()
    raw = re.sub(r"-{2,}", "-", raw)
    return (raw[:max_len].strip("-")) or "proposal"


def _read_offer(args: argparse.Namespace) -> str:
    if args.offer_text:
        return args.offer_text
    if args.offer:
        if str(args.offer) == "-":
            return sys.stdin.read()
        p = Path(args.offer)
        if not p.is_file():
            print(f"offer file not found: {p}", file=sys.stderr)
            raise SystemExit(2)
        return p.read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("No offer. Pass --offer <path|-> or --offer-text '<...>' or pipe via stdin.",
          file=sys.stderr)
    raise SystemExit(2)


def _resolve_brand(args: argparse.Namespace, plan: dict) -> dict:
    brand: dict
    if args.brand_file:
        brand = json.loads(Path(args.brand_file).read_text(encoding="utf-8"))
    else:
        url = args.brand_url
        if not url and not args.no_brand:
            # auto-detect from the offer footer ("сайт www.example.com")
            url = (plan.get("footer") or {}).get("site_url")
        if url:
            print(f"… reading brand style from {url}", file=sys.stderr)
            brand = brand_mod.extract(url)
            if not brand.get("ok"):
                print(f"  (could not fetch {url} — using defaults + overrides)", file=sys.stderr)
        else:
            brand = {  # neutral defaults
                "url": None, "ok": False, "name": None, "tagline": None,
                "accent": "#1f6feb", "accent2": "#1f6feb", "bg": "#ffffff",
                "text": "#111111", "is_dark": False, "font_heading": None,
                "font_body": None, "google_fonts_url": None, "logo_url": None,
                "hero_url": None,
            }
    # manual overrides win
    if args.accent:
        brand["accent"] = args.accent
        brand["accent2"] = args.accent
    if args.font:
        brand["font_heading"] = args.font
        brand["font_body"] = args.font
        brand["google_fonts_url"] = brand_mod.google_fonts_link([args.font])
    if args.logo:
        brand["logo_url"] = args.logo
    if args.brand_name:
        brand["name"] = args.brand_name
    return brand


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="common.runners.cli.proposal")
    ap.add_argument("--offer", help="offer file path, or '-' for stdin")
    ap.add_argument("--offer-text", dest="offer_text", help="offer text inline")
    ap.add_argument("--brand-url", dest="brand_url", help="site to copy style from")
    ap.add_argument("--brand-file", dest="brand_file", help="reuse a saved brand.json")
    ap.add_argument("--no-brand", action="store_true", help="skip brand scrape; defaults only")
    ap.add_argument("--accent", help="override accent colour (#hex)")
    ap.add_argument("--font", help="override font family name")
    ap.add_argument("--logo", help="override logo URL/path")
    ap.add_argument("--brand-name", dest="brand_name", help="override brand name")
    ap.add_argument("--quick", action="store_true",
                    help="skip LLM authoring — render a deterministic themed template")
    ap.add_argument("--template", default="auto", choices=["auto", "editorial", "invoice", "dark"])
    ap.add_argument("--lang", default="auto", choices=["auto", "ru", "en"])
    ap.add_argument("--no-thumbnails", action="store_true", help="skip per-item photo/desc fetch")
    ap.add_argument("--no-gen-photos", dest="no_gen_photos", action="store_true",
                    help="don't generate on-brand images for items missing a photo")
    ap.add_argument("--embed-images", action="store_true", help="base64-inline images (portable file)")
    ap.add_argument("--currency", help="override currency code (e.g. THB)")
    ap.add_argument("--pdf", action="store_true", help="(quick mode) also render a PDF")
    ap.add_argument("--pdf-from", dest="pdf_from", help="render this HTML file to <same-name>.pdf and exit (uses headless browser)")
    ap.add_argument("--no-compress", dest="no_compress", action="store_true",
                    help="skip the Ghostscript image-shrink pass (keeps full-res, ~15 MB)")
    ap.add_argument("--pdf-dpi", dest="pdf_dpi", type=int, default=144,
                    help="image resolution for the PDF compression pass (default 144; lower = smaller)")
    ap.add_argument("--output", type=Path, help="output dir")
    ap.add_argument("--parse-only", action="store_true", help="print parsed offer JSON and exit (no network)")
    ap.add_argument("--check", action="store_true", help="verify deps + brand-url reachable, exit")
    ap.add_argument("--yes", action="store_true", help="(reserved) skip confirmations")
    return ap


def _cmd_pdf_from(args: argparse.Namespace) -> int:
    """--pdf-from renders an already-authored HTML file and stops."""
    src = Path(args.pdf_from)
    if not src.is_file():
        print(f"--pdf-from: file not found: {src}", file=sys.stderr)
        return 2
    out_pdf = src.with_suffix(".pdf")
    if kit_mod.print_pdf(src, out_pdf, compress=not args.no_compress,
                         dpi=args.pdf_dpi):
        mb = out_pdf.stat().st_size / 1e6
        print(f"PDF: {out_pdf}  ({mb:.1f} MB"
              f"{'' if args.no_compress else ', photos compressed'})", file=sys.stderr)
        print(str(out_pdf))
        return 0
    print("Could not render PDF — no headless browser / renderer found. Open "
          f"{src} in a browser and Cmd/Ctrl+P → Save as PDF.", file=sys.stderr)
    return 1


def _cmd_check(args: argparse.Namespace) -> int:
    """Report whether the dependencies and the brand URL are usable."""
    ok = brand_mod.requests is not None
    print(f"requests: {'OK' if ok else 'MISSING (pip install requests)'}", file=sys.stderr)
    if args.brand_url:
        b = brand_mod.extract(args.brand_url)
        if b.get("ok"):
            print(f"brand {args.brand_url}: OK — accent {b['accent']}, "
                  f"font {b.get('font_heading')}, logo {'yes' if b.get('logo_url') else 'no'}",
                  file=sys.stderr)
        else:
            print(f"brand {args.brand_url}: UNREACHABLE", file=sys.stderr)
            return 2
    return 0 if ok else 2


def _load_plan(args: argparse.Namespace) -> dict:
    """Read the offer and parse it, applying any --currency override."""
    plan = parse_mod.parse(_read_offer(args))
    if args.currency:
        plan["currency"] = args.currency.upper()
        for item in plan["items"]:
            item["currency"] = item["currency"] or plan["currency"]
    return plan


def _warn_about(plan: dict) -> None:
    """Surface the parser's doubts on stderr in both modes."""
    if not plan["items"]:
        print("WARNING: no line items parsed — check the offer format "
              "(see references/offer-format.md).", file=sys.stderr)
    if plan.get("total_mismatch"):
        print(f"⚠ stated total {plan.get('total_stated')} ≠ computed "
              f"{plan.get('subtotal_computed')} — using computed.", file=sys.stderr)
    for outlier in plan.get("price_outliers", []):
        print(f"⚠ '{outlier['name']}' is {outlier['share'] * 100:.0f}% of the total "
              f"({outlier['price']}) — possible typo; confirm with the user.", file=sys.stderr)


@dataclass
class _Job:
    """Everything both output modes need, resolved once."""

    args: argparse.Namespace
    plan: dict
    brand: dict
    out_dir: Path
    slug: str
    lang: str


def _generate_missing_photos(plan: dict, brand: dict, out_dir: Path,
                             args: argparse.Namespace) -> None:
    """Fill any item that ended up with no catalogue photo, if a key allows it."""
    missing = [it["name"] for it in plan["items"] if not it.get("thumb")]
    if not missing or args.no_gen_photos:
        return

    if kit_mod._pick_image_provider() is None:
        print(f"… {len(missing)} item(s) without a photo and no image key set — "
              f"they'll need a picked photo: {', '.join(missing)}", file=sys.stderr)
        return

    print(f"… {len(missing)} item(s) without a photo — generating on-brand "
          f"images: {', '.join(missing)}", file=sys.stderr)
    generated = kit_mod.fill_missing_photos(
        plan["items"], brand, out_dir,
        event=(plan.get("client", {}) or {}).get("event", ""),
        on_progress=lambda nm: print(f"  ✓ generated photo for {nm}", file=sys.stderr),
    )
    print(f"… generated {generated} photo(s) (AI, on-brand — swap for a real one if you "
          f"have it)", file=sys.stderr)


def _manifest_base(job: _Job) -> dict:
    """The fields both manifests carry. Each mode adds its own on top."""
    plan, brand = job.plan, job.brand
    return {
        "skill": "proposal-maker", "slug": job.slug, "lang": job.lang,
        "brand_url": brand.get("url"), "brand_ok": brand.get("ok"),
        "accent": brand.get("accent"), "font": brand.get("font_heading"),
        "item_count": len(plan["items"]), "currency": plan.get("currency"),
        "subtotal_computed": plan.get("subtotal_computed"),
        "total_stated": plan.get("total_stated"),
        "total_mismatch": plan.get("total_mismatch"),
        "price_outliers": plan.get("price_outliers"),
        "thumbnails": not job.args.no_thumbnails,
    }


def main() -> int:
    args = build_parser().parse_args()

    if args.pdf_from:
        return _cmd_pdf_from(args)
    if args.check:
        return _cmd_check(args)

    plan = _load_plan(args)
    if args.parse_only:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    _warn_about(plan)
    brand = _resolve_brand(args, plan)

    if not args.no_thumbnails:
        n = brand_mod.enrich_items(plan["items"])
        print(f"… enriched {n}/{sum(1 for it in plan['items'] if it.get('url'))} "
              f"item(s) with catalogue photos", file=sys.stderr)

    client = plan.get("client", {})
    slug = _slugify(client.get("name", ""), client.get("event", ""), client.get("date", ""))
    out_dir = Path(args.output) if args.output else Path("./generated/proposal") / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    _generate_missing_photos(plan, brand, out_dir, args)

    lang = render_mod.detect_lang(plan) if args.lang == "auto" else args.lang
    (out_dir / "brand.json").write_text(json.dumps(brand, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "offer.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    job = _Job(args=args, plan=plan, brand=brand, out_dir=out_dir, slug=slug, lang=lang)
    return _run_quick(job) if args.quick else _run_kit(job)


def _write_kit_manifest(job: _Job, shot_ok: bool, logo_local: Path | None) -> None:
    files = ["BRIEF.md", "brand.json", "offer.json", "manifest.json"]
    if shot_ok:
        files.append("site.png")
    if logo_local:
        files.append(logo_local.name)
    manifest = {
        **_manifest_base(job),
        "mode": "kit",
        "screenshot": shot_ok,
        "logo_local": logo_local.name if logo_local else None,
        "files": files,
    }
    (job.out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _run_kit(job: _Job) -> int:
    """Default mode: assemble a brand kit for an LLM to author the proposal from."""
    plan, brand, out_dir, lang = job.plan, job.brand, job.out_dir, job.lang
    shot = out_dir / "site.png"
    shot_ok = False
    if brand.get("url"):
        print(f"… screenshotting {brand['url']} for the brand kit", file=sys.stderr)
        shot_ok = kit_mod.capture_screenshot(brand["url"], shot)
        if not shot_ok:
            print("  (no headless browser found — kit ships without a screenshot)",
                  file=sys.stderr)
    logo_local = None
    if brand.get("logo_url"):
        logo_local = kit_mod.download_asset(brand["logo_url"], out_dir, stem="logo")
    brief = out_dir / "BRIEF.md"
    brief_mod.write_brief(
        brief, plan, brand,
        brief_mod.BriefContext(
            screenshot=shot if shot_ok else None,
            logo_local=logo_local,
            lang=lang,
        ),
    )

    _write_kit_manifest(job, shot_ok, logo_local)

    print(f"\nBrand kit ready: {out_dir}  "
          f"({len(plan['items'])} items, "
          f"{render_mod.fmt_money(plan.get('subtotal_computed'), plan.get('currency'))})", file=sys.stderr)
    if shot_ok:
        print(f"  → VIEW the screenshot:  {shot}", file=sys.stderr)
    print(f"  → READ the brief, then author proposal.html here:  {brief}", file=sys.stderr)
    print("  (offline / no-LLM? re-run with --quick for a themed template.)", file=sys.stderr)
    print(str(out_dir))
    return 0


def _run_quick(job: _Job) -> int:
    """--quick: render the deterministic themed template, no LLM in the loop."""
    args, plan, brand, out_dir = job.args, job.plan, job.brand, job.out_dir
    lang, slug = job.lang, job.slug
    theme = render_mod.pick_theme(brand) if args.template == "auto" else args.template
    html = render_mod.render_html(
        plan, brand, lang=args.lang, template=args.template, embed_images=args.embed_images,
    )
    html_path = out_dir / "proposal.html"
    html_path.write_text(html, encoding="utf-8")

    files = ["proposal.html", "brand.json", "offer.json", "manifest.json"]
    if args.pdf:
        pdf_path = out_dir / "proposal.pdf"
        if kit_mod.print_pdf(html_path, pdf_path, compress=not args.no_compress,
                             dpi=args.pdf_dpi):
            files.insert(1, "proposal.pdf")
            mb = pdf_path.stat().st_size / 1e6
            print(f"… PDF rendered: {pdf_path} ({mb:.1f} MB)", file=sys.stderr)
        else:
            print("… no headless browser/renderer found — open proposal.html in a "
                  "browser and Cmd/Ctrl+P → Save as PDF (links preserved).", file=sys.stderr)

    manifest = {
        "skill": "proposal-maker", "mode": "quick", "slug": slug, "lang": lang,
        "template": theme, "brand_url": brand.get("url"), "brand_ok": brand.get("ok"),
        "accent": brand.get("accent"), "font": brand.get("font_heading"),
        "item_count": len(plan["items"]), "currency": plan.get("currency"),
        "subtotal_computed": plan.get("subtotal_computed"),
        "total_stated": plan.get("total_stated"),
        "total_mismatch": plan.get("total_mismatch"),
        "price_outliers": plan.get("price_outliers"),
        "thumbnails": not args.no_thumbnails, "embed_images": args.embed_images,
        "files": files,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nProposal: {out_dir}  "
          f"({len(plan['items'])} items, {render_mod.fmt_money(plan.get('subtotal_computed'), plan.get('currency'))}, "
          f"theme '{theme}')", file=sys.stderr)
    print(f"Open: {html_path}", file=sys.stderr)
    print(str(out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
