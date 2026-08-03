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
from dataclasses import dataclass
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


_IMG_SRC_RE = re.compile(r'src\s*=\s*"(https?://[^"]+)"', re.IGNORECASE)


def _encode_image(raw: bytes, max_width: int, quality: int) -> str | None:
    """Downscale and re-encode one image as a data URI. None if it will not decode."""
    try:
        from PIL import Image
    except ImportError:
        return None

    import base64
    import io

    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
        if im.width > max_width:
            height = round(im.height * max_width / im.width)
            im = im.resize((max_width, height), Image.LANCZOS)

        buf = io.BytesIO()
        # Alpha has to survive — a cut-out product shot on a coloured canvas
        # gets a white box around it otherwise.
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        if has_alpha:
            im.convert("RGBA").save(buf, format="PNG", optimize=True)
            mime = "image/png"
        else:
            im.convert("RGB").save(
                buf, format="JPEG", quality=quality, optimize=True, progressive=True
            )
            mime = "image/jpeg"
    except Exception:  # noqa: BLE001 — one unreadable image must not lose the rest
        return None

    return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"


def _fetch(url: str) -> bytes | None:
    try:
        response = requests.get(url, headers={"User-Agent": _UA}, timeout=20)
    except Exception:  # noqa: BLE001
        return None
    return response.content if response.status_code == 200 and response.content else None


def compress_html_images(html_str: str, *, max_width: int = 1400, quality: int = 82) -> str:
    """Download every remote <img src> in the HTML, downscale to `max_width`,
    re-encode (JPEG for opaque, PNG for alpha), and inline as a base64 data URI.
    Shrinks a photo-heavy PDF from ~14 MB to ~1-2 MB. Needs Pillow + requests;
    if either is missing, or a fetch/decode fails, that image is left untouched."""
    if requests is None:
        return html_str

    for url in dict.fromkeys(_IMG_SRC_RE.findall(html_str)):
        # Leave SVGs vector — rasterising a logo is a downgrade, not a saving.
        if url.lower().split("?")[0].endswith(".svg"):
            continue
        raw = _fetch(url)
        if raw is None:
            continue
        data_uri = _encode_image(raw, max_width, quality)
        if data_uri:
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

    if not _render_pdf(src_path, raw, timeout):
        return False
    if compress:
        _shrink_in_place(raw, out_pdf, dpi)
    return out_pdf.exists() and out_pdf.stat().st_size > 0


def _print_via_browser(browser: str, src_path: Path, raw: Path, timeout: int) -> bool:
    """Headless print-to-PDF. The header flag was renamed between Chrome
    versions, so both spellings are tried before giving up on the browser."""
    url = f"file://{src_path.resolve()}"
    for header_flag in ("--no-pdf-header-footer", "--print-to-pdf-no-header"):
        cmd = [browser, "--headless", "--disable-gpu", "--no-sandbox",
               header_flag, f"--print-to-pdf={raw}", url]
        try:
            subprocess.run(cmd, timeout=timeout, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=False)
        except Exception:  # noqa: BLE001
            continue
        if raw.exists() and raw.stat().st_size > 0:
            return True
    return False


def _render_pdf(src_path: Path, raw: Path, timeout: int) -> bool:
    """Browser first — it keeps links, web fonts and full-bleed backgrounds.
    Playwright / WeasyPrint is the fallback when no browser is installed."""
    browser = find_browser()
    if browser and _print_via_browser(browser, src_path, raw, timeout):
        return True
    try:
        from . import proposal_render

        return bool(proposal_render.to_pdf(src_path.read_text(encoding="utf-8"), raw))
    except Exception:  # noqa: BLE001
        return False


def _shrink_in_place(raw: Path, out_pdf: Path, dpi: int) -> None:
    """Ghostscript-shrink raw into out_pdf. Without gs, keep the full-res render
    rather than losing the document to a missing optional dependency."""
    shrunk = _gs_shrink(raw, out_pdf, dpi=dpi)
    try:
        if shrunk:
            raw.unlink(missing_ok=True)
        else:
            raw.replace(out_pdf)
    except Exception:  # noqa: BLE001
        pass


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
            res = provider.poll(res, timeout=180)
        content = getattr(res, "content", None)
        if not content:
            return False
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(content)
        return True
    except Exception:
        return False


def fill_missing_photos(items: list[dict[str, Any]], brand: dict[str, Any],
                        out_dir: Path, *, event: str = "", on_progress=None) -> int:
    """For items still without a photo after URL enrichment, generate an on-brand
    one into <out_dir>/img/ and point the item's thumb at it (relative path, so it
    resolves both in the browser and the PDF). Returns count generated."""
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
