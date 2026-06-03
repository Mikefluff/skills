"""Brand-kit collector for proposal-maker (LLM-authoring mode).

Instead of filling a fixed template, the default flow hands the orchestrating
LLM everything it needs to *author* a bespoke, brand-faithful proposal:

  - a SCREENSHOT of the brand site (so the model can SEE the visual language),
  - the logo asset downloaded locally,
  - resolved brand tokens (brand.json) and the parsed offer (offer.json),
  - a BRIEF.md that bundles tokens + the full item table + authoring rules.

Screenshotting uses whatever Chromium-class browser is on the machine (Chrome /
Chromium / Edge / Brave) in headless mode — no extra dependency. Everything is
best-effort: a missing browser just means no screenshot, and the brief says so.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

_UA = "Mozilla/5.0 (compatible; proposal-maker/1.0)"

_CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]
_CHROME_NAMES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "microsoft-edge", "brave-browser", "chrome",
]


def find_browser() -> str | None:
    for p in _CHROME_CANDIDATES:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
    for name in _CHROME_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def capture_screenshot(url: str, out_path: Path, *, width: int = 1280,
                       height: int = 4200, timeout: int = 60) -> bool:
    """Headless full-ish-page screenshot of `url`. Returns success."""
    browser = find_browser()
    if not browser:
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        browser, "--headless", "--disable-gpu", "--no-sandbox",
        "--hide-scrollbars", "--force-device-scale-factor=1",
        f"--window-size={width},{height}",
        f"--screenshot={out_path}", url,
    ]
    try:
        subprocess.run(cmd, timeout=timeout, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=False)
    except Exception:
        return False
    return out_path.exists() and out_path.stat().st_size > 0


_IMG_SRC_RE = None  # lazy-compiled in compress_html_images


def compress_html_images(html_str: str, *, max_width: int = 1400, quality: int = 82) -> str:
    """Download every remote <img src> in the HTML, downscale to `max_width`,
    re-encode (JPEG for opaque, PNG for alpha), and inline as a base64 data URI.
    Shrinks a photo-heavy PDF from ~14 MB to ~1-2 MB. Needs Pillow + requests;
    if either is missing, or a fetch/decode fails, that image is left untouched."""
    import base64
    import io
    import re

    if requests is None:
        return html_str
    try:
        from PIL import Image
    except ImportError:
        return html_str

    src_re = re.compile(r'src\s*=\s*"(https?://[^"]+)"', re.IGNORECASE)
    urls = list(dict.fromkeys(src_re.findall(html_str)))
    cache: dict[str, str] = {}

    for url in urls:
        # don't try to rasterise SVGs (logos) — leave them vector
        if url.lower().split("?")[0].endswith(".svg"):
            continue
        try:
            r = requests.get(url, headers={"User-Agent": _UA}, timeout=20)
            if r.status_code != 200 or not r.content:
                continue
            im = Image.open(io.BytesIO(r.content))
            im.load()
            if im.width > max_width:
                h = round(im.height * max_width / im.width)
                im = im.resize((max_width, h), Image.LANCZOS)
            buf = io.BytesIO()
            has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
            if has_alpha:
                im.convert("RGBA").save(buf, format="PNG", optimize=True)
                mime = "image/png"
            else:
                im.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
                mime = "image/jpeg"
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            cache[url] = f"data:{mime};base64,{b64}"
        except Exception:
            continue

    for url, data_uri in cache.items():
        html_str = html_str.replace(f'"{url}"', f'"{data_uri}"')
    return html_str


_GS_CANDIDATES = ["/usr/local/bin/gs", "/opt/homebrew/bin/gs", "/usr/bin/gs"]


def find_ghostscript() -> str | None:
    for name in ("gs", "gswin64c", "gswin32c"):
        found = shutil.which(name)
        if found:
            return found
    for p in _GS_CANDIDATES:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
    return None


def _gs_shrink(in_pdf: Path, out_pdf: Path, dpi: int = 144) -> bool:
    """Recompress a PDF's images to JPEG at `dpi` via Ghostscript. Chrome stores
    print images near-losslessly (a photo proposal balloons to ~15 MB); gs brings
    it to ~0.5-2 MB while keeping text/vectors crisp and links intact."""
    gs = find_ghostscript()
    if not gs:
        return False
    cmd = [
        gs, "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.5", "-dPDFSETTINGS=/ebook", "-dAutoRotatePages=/None",
        "-dDownsampleColorImages=true", "-dColorImageDownsampleType=/Bicubic",
        f"-dColorImageResolution={dpi}",
        "-dDownsampleGrayImages=true", "-dGrayImageDownsampleType=/Bicubic",
        f"-dGrayImageResolution={dpi}",
        f"-sOutputFile={out_pdf}", str(in_pdf),
    ]
    try:
        subprocess.run(cmd, timeout=120, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=False)
    except Exception:
        return False
    return out_pdf.exists() and out_pdf.stat().st_size > 0


def print_pdf(html_path: Path, out_pdf: Path, *, compress: bool = True,
              dpi: int = 144, timeout: int = 90) -> bool:
    """Render a local HTML file to PDF via the system browser's headless
    print-to-PDF (no Python deps; keeps links, web fonts, dark full-bleed),
    then optionally shrink images with Ghostscript. Falls back to
    Playwright/WeasyPrint when no browser is found. Returns success."""
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    src_path = Path(html_path)
    raw = out_pdf.with_suffix(".raw.pdf") if compress else out_pdf
    rendered = False

    browser = find_browser()
    if browser:
        url = f"file://{src_path.resolve()}"
        for header_flag in ("--no-pdf-header-footer", "--print-to-pdf-no-header"):
            cmd = [browser, "--headless", "--disable-gpu", "--no-sandbox",
                   header_flag, f"--print-to-pdf={raw}", url]
            try:
                subprocess.run(cmd, timeout=timeout, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, check=False)
            except Exception:
                continue
            if raw.exists() and raw.stat().st_size > 0:
                rendered = True
                break

    if not rendered:
        # fallback: playwright / weasyprint on the HTML string
        try:
            from . import proposal_render
            if proposal_render.to_pdf(src_path.read_text(encoding="utf-8"), raw):
                rendered = True
        except Exception:
            rendered = False
    if not rendered:
        return False

    if not compress:
        return out_pdf.exists() and out_pdf.stat().st_size > 0

    # compress raw → out_pdf, then drop the raw file
    ok = _gs_shrink(raw, out_pdf, dpi=dpi)
    try:
        if ok and raw.exists():
            raw.unlink()
        elif not ok:
            raw.replace(out_pdf)  # gs unavailable → keep the full-res render
            ok = out_pdf.exists()
    except Exception:
        pass
    return out_pdf.exists() and out_pdf.stat().st_size > 0


def download_asset(url: str, out_dir: Path, stem: str = "logo") -> Path | None:
    if requests is None or not url or url.startswith("data:"):
        return None
    try:
        r = requests.get(url, headers={"User-Agent": _UA}, timeout=20)
        if r.status_code != 200 or not r.content:
            return None
    except Exception:
        return None
    ext = os.path.splitext(urlparse(url).path)[1].lower() or ".img"
    if len(ext) > 6:
        ext = ".img"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stem}{ext}"
    path.write_bytes(r.content)
    return path


def _fmt_price(it: dict[str, Any]) -> str:
    p = it.get("price")
    if p is None:
        return "—"
    return f"{int(p):,}".replace(",", " ") if p == int(p) else f"{p:,.2f}".replace(",", " ")


_IMG_PROVIDER_PREF = ["gpt-image-2", "imagen-4-fast", "imagen-4",
                      "nano-banana-pro", "imagen-4-ultra"]


def _brand_mood(brand: dict[str, Any]) -> str:
    if brand.get("is_dark"):
        return "dark cinematic, neon accents, dramatic low-key lighting, moody"
    return "bright, clean, editorial daylight, airy"


def _pick_image_provider():
    """First available image provider (keys from ~/.skills.env), or None."""
    try:
        from . import config, keysfile
        keysfile.load_into_env()
        config.load_all_providers()
    except Exception:
        return None
    for name in _IMG_PROVIDER_PREF:
        try:
            p = config.get_provider(name)
        except Exception:
            continue
        if p.available():
            return p
    return None


def generate_photo(item_name: str, brand: dict[str, Any], out_path: Path,
                   *, event: str = "", size: str = "1536x1024") -> bool:
    """Generate one on-brand, photoreal image for a service that has no catalogue
    photo. Returns success. Needs an image provider key (gpt-image-2 / Imagen /
    Nano Banana via ~/.skills.env); returns False if none configured."""
    provider = _pick_image_provider()
    if provider is None:
        return False
    accent = brand.get("accent") or ""
    prompt = (
        f"Professional event-production photograph of {item_name}"
        + (f" at a {event} celebration" if event else "")
        + f", {_brand_mood(brand)}, accent colour {accent}, Phuket nightlife, "
        "shallow depth of field, photorealistic, high detail, "
        "no text, no watermark, no logo, no people staring at camera"
    )
    try:
        from .providers.base import JobHandle
        res = provider.generate(prompt, size=size, quality="medium")
        if isinstance(res, JobHandle):
            from . import poll
            res = poll.poll_until(provider, res, timeout=180)
        content = getattr(res, "content", None)
        if not content:
            return False
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(content)
        return True
    except Exception:
        return False


def fill_missing_photos(items: list[dict[str, Any]], brand: dict[str, Any],
                        out_dir: Path, *, event: str = "", enable: bool = True,
                        on_progress=None) -> int:
    """For items still without a photo after URL enrichment, generate an on-brand
    one into <out_dir>/img/ and point the item's thumb at it (relative path, so it
    resolves both in the browser and the PDF). Returns count generated."""
    if not enable:
        return 0
    missing = [(i, it) for i, it in enumerate(items) if not it.get("thumb")]
    if not missing or _pick_image_provider() is None:
        return 0
    img_dir = out_dir / "img"
    n = 0
    for i, it in missing:
        slug = re.sub(r"[^0-9A-Za-zА-Яа-яЁё]+", "-", it.get("name") or f"item{i}").strip("-").lower()[:30]
        rel = f"img/{i:02d}-{slug or 'item'}.png"
        if generate_photo(it.get("name") or "", brand, out_dir / rel, event=event):
            it["thumb"] = rel
            it["thumb_source"] = "generated"
            n += 1
            if on_progress:
                on_progress(it["name"])
    return n


def write_brief(
    brief_path: Path,
    plan: dict[str, Any],
    brand: dict[str, Any],
    *,
    screenshot: Path | None,
    logo_local: Path | None,
    lang: str,
) -> None:
    client = plan.get("client", {})
    cur = plan.get("currency", "")
    L = []
    A = L.append

    A("# Proposal authoring brief\n")
    A("> You (the orchestrator) are authoring a bespoke, **brand-faithful** HTML "
      "proposal. Do NOT fill a generic template — mirror the brand site's visual "
      "language. Read the screenshot below FIRST.\n")

    A("## 1. Look at the brand")
    if screenshot:
        A(f"- **Screenshot:** `{screenshot}` — OPEN IT (Read tool). Match its mood "
          "(dark/light), type scale, accent usage, logo placement, imagery feel.")
    else:
        A("- **Screenshot:** none (no headless browser found) — rely on tokens below "
          "and, if possible, fetch the site yourself.")
    A(f"- **Site:** {brand.get('url') or '—'}")
    A("")

    A("## 2. Brand tokens (resolved)")
    A(f"- Name: **{brand.get('name') or '—'}**  ·  Tagline: {brand.get('tagline') or '—'}")
    A(f"- Accent: `{brand.get('accent')}`  ·  Secondary: `{brand.get('accent2')}`")
    A(f"- Background: `{brand.get('bg')}`  ·  Text: `{brand.get('text')}`  ·  "
      f"is_dark (heuristic): `{brand.get('is_dark')}` — TRUST THE SCREENSHOT over this flag.")
    A(f"- Fonts: heading **{brand.get('font_heading') or '—'}**, body "
      f"**{brand.get('font_body') or '—'}**")
    A(f"- Google Fonts: `{brand.get('google_fonts_url') or '—'}`")
    if logo_local:
        A(f"- Logo (local): `{logo_local}` — **may be a monochrome/white SVG**. On a "
          "dark header use as-is; on a light header tint via "
          "`filter:brightness(0) invert(1)` for white, or place on a dark/accent plate. "
          "Always pair with the brand NAME so identity survives.")
    else:
        A(f"- Logo (remote): {brand.get('logo_url') or '—'}")
    A("")

    A("## 3. The offer (render EXACTLY — never invent or silently change numbers)")
    fields = [(k, v) for k, v in client.items() if v]
    if fields:
        A("**Client:** " + "  ·  ".join(f"{k}: {v}" for k, v in fields))
    A(f"**Currency:** {cur}  ·  **Computed subtotal:** "
      f"{_fmt_price({'price': plan.get('subtotal_computed', 0)})} {cur}")
    if plan.get("total_mismatch"):
        A(f"\n> ⚠ Stated total ({plan.get('total_stated')}) ≠ computed subtotal. Use "
          "computed; mention the discrepancy to the user.")
    for o in plan.get("price_outliers", []):
        A(f"\n> ⚠ **'{o['name']}' is {o['share']*100:.0f}% of the total** "
          f"({o['price']}). Almost certainly a typo — ASK the user before using it. "
          "Do not silently rewrite.")
    A("\n**Line items** (qty is a separate column — price is the line total as written):\n")
    A("| # | Item | Qty | Price | Link | Photo (og:image) |")
    A("|---|------|-----|-------|------|------------------|")
    for i, it in enumerate(plan.get("items", []), 1):
        A(f"| {i} | {it.get('name','')} | {it.get('qty') or ''} | "
          f"{_fmt_price(it)} {it.get('currency') or cur} | {it.get('url') or ''} | "
          f"{it.get('thumb') or '—'} |")
    A("")

    A("## 4. Author the proposal")
    A(f"1. Write a single self-contained **`proposal.html`** into this folder "
      f"(`{brief_path.parent}`). Inline CSS + the Google Fonts link above.")
    A("2. Mirror the screenshot: same dark/light mood, type weight/case, accent "
      "colour, logo treatment, generous rhythm. Make it look like THIS brand.")
    A("3. **Group items into 4–7 logical categories** named for the client's domain "
      "(e.g. Звук и свет / Доп оборудование / Артисты / Декорации / Сервис) — never one "
      "long pile. Give each a **large, scannable header** (big type, accent marker) so the "
      "client sees the sections at a glance, plus its item count and **per-category "
      "subtotal**. Order categories sensibly. Lead the hero with a **prominent Date / Time "
      "/ Location block** (large) — those are what the client checks first.")
    A("4. **Vary density — don't render everything large.** Showpiece / high-value items "
      "get a big photo card; utility / low-cost items (controllers, stands, staff, "
      "logistics) get a **compact 2-column row** (small 44px thumb + name + price). This "
      "keeps it readable and not sprawling. Use your judgment per item.")
    A("5. Each item: real `og:image` photo (reference the Tilda URLs directly — they "
      "hotlink fine), name linking to its catalogue URL, a quantity chip where given, the "
      "price. Items whose `Photo` column already points at `img/…` are **AI-generated "
      "on-brand** stand-ins (picked because the offer had no link) — use them, and note to "
      "the user they can swap in a real photo. Never leave a blank/placeholder if a photo "
      "can be sourced.")
    A("6. Exact prices + clickable links. Computed subtotal as the grand total.")
    A(f"7. Language: **{lang}** labels.")
    A("8. **Print CSS — required, the PDF depends on it:**")
    A("   - `@page{size:A4;margin:0}` so there are NO white page margins (full-bleed).")
    A("   - Running header AND footer that repeat on EVERY page with uniform spacing — "
      "use the **table head/foot** pattern (a `position:fixed` band can't reserve "
      "per-page space and looks broken on inner pages):")
    A("     ```html")
    A("     <table class=\"sheet\"><thead><tr><td><div class=\"rh\">logo + name + "
      "doc title</div></td></tr></thead>")
    A("     <tfoot><tr><td><div class=\"rf\">contact · site</div></td></tr></tfoot>")
    A("     <tbody><tr><td> …all content (hero, item grid, total)… </td></tr></tbody></table>")
    A("     ```")
    A("     ```css")
    A("     table.sheet{width:100%;border-collapse:collapse}")
    A("     table.sheet>thead,table.sheet>tfoot{display:none}      /* screen */")
    A("     @media print{ @page{size:A4;margin:0} html,body{background:<page-bg>}")
    A("       table.sheet>thead{display:table-header-group}        /* repeats every page */")
    A("       table.sheet>tfoot{display:table-footer-group}")
    A("       table.sheet>thead>tr>td{padding:0 0 20px}   /* uniform gap UNDER header every page */")
    A("       table.sheet>tfoot>tr>td{padding:20px 0 0}    /* uniform gap ABOVE footer every page */")
    A("       .screen-header,.screen-footer{display:none}          /* hide scroll-view chrome */")
    A("       .card,.row,.total{break-inside:avoid;page-break-inside:avoid}")
    A("       .cat-h{break-after:avoid;page-break-after:avoid} }  /* category header not orphaned */")
    A("     ```")
    A("   - Put the gap padding on the thead/tfoot `<td>` (NOT on the content cell) — it "
      "sits inside the repeated group, so the breathing space is identical on every page; "
      "content-cell padding only spaces the first/last page and looks crooked on inner ones.")
    A("   - The `.rh`/`.rf` bands carry the dark/brand background + the accent hairline so "
      "they look like real letterhead colophons.")
    A("9. Verify: screenshot your `proposal.html`, Read it back; iterate until on-brand.")
    A("10. PDF: `proposal-maker/scripts/run.py --pdf-from <…/proposal.html>` — renders via "
      "the browser then Ghostscript-shrinks photos (~15 MB → ~0.5 MB), links preserved.")
    A("")
    A("_Offline / no-LLM fallback: re-run with `--quick` to render a deterministic "
      "themed template instead._")

    brief_path.write_text("\n".join(L), encoding="utf-8")
