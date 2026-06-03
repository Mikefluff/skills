"""Brand-style extractor + per-item enrichment for proposal-maker.

`extract(url)` mines a website's public HTML/CSS for the design tokens a
proposal needs to *look like that brand*: accent colour, fonts (incl. the
Google Fonts link), logo, name, tagline, hero image. `enrich_items(items)`
fetches each line-item's catalogue page for its `og:image` / `og:title` /
`og:description` so the proposal shows real product photos and copy.

Only dependency is `requests` (already in requirements.txt). Everything else is
stdlib + regex — Tilda / Webflow / Wordpress pages all expose enough in the
served HTML for a good-enough brand read, and manual overrides cover the rest.
"""

from __future__ import annotations

import concurrent.futures
import html
import re
from typing import Any
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:  # pragma: no cover - requests is a declared dep
    requests = None  # type: ignore

_UA = "Mozilla/5.0 (compatible; proposal-maker/1.0; +https://github.com/Mikefluff/skills)"
_TIMEOUT = 20

_HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
_RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})", re.IGNORECASE)
_FONT_DECL_RE = re.compile(r"font-family\s*:\s*([^;{}\"']+)", re.IGNORECASE)
_GF_RE = re.compile(r"fonts\.googleapis\.com/css2?\?[^\"'\s>]+", re.IGNORECASE)
_GF_FAMILY_RE = re.compile(r"family=([^:&\"']+)", re.IGNORECASE)

_GENERIC_FONTS = {
    "arial", "sans-serif", "serif", "monospace", "helvetica", "inherit",
    "-apple-system", "blinkmacsystemfont", "system-ui", "ui-sans-serif",
    "segoe ui", "roboto", "cursive", "fantasy", "tahoma", "verdana",
}


# ----------------------------------------------------------------------------- fetch

def _get(url: str) -> str | None:
    if requests is None:
        return None
    try:
        r = requests.get(url, headers={"User-Agent": _UA}, timeout=_TIMEOUT)
        if r.status_code == 200 and r.text:
            return r.text
    except Exception:
        return None
    return None


def _meta(html_text: str, prop: str) -> str | None:
    """Read a <meta property|name="..." content="..."> value (order-agnostic)."""
    pat = re.compile(
        r"<meta[^>]+(?:property|name)\s*=\s*[\"']" + re.escape(prop) + r"[\"'][^>]*>",
        re.IGNORECASE,
    )
    m = pat.search(html_text)
    if not m:
        return None
    cm = re.search(r"content\s*=\s*[\"']([^\"']*)[\"']", m.group(0), re.IGNORECASE)
    if not cm:
        return None
    # og copy is often double-encoded (&amp;nbsp;) — unescape twice, drop nbsp.
    val = html.unescape(html.unescape(cm.group(1)))
    val = val.replace("\xa0", " ").replace("​", "").strip()
    return val or None


def _title(html_text: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    return html.unescape(m.group(1)).strip() if m else None


# ----------------------------------------------------------------------------- colour

def _hex_norm(h: str) -> str:
    h = h.lower()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def _rgb(hexv: str) -> tuple[int, int, int]:
    h = hexv.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _luma(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _saturation(rgb: tuple[int, int, int]) -> float:
    r, g, b = (c / 255 for c in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == 0:
        return 0.0
    return (mx - mn) / mx


def _collect_colors(html_text: str) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for m in _HEX_RE.finditer(html_text):
        hexv = _hex_norm(m.group(1))
        counts[hexv] = counts.get(hexv, 0) + 1
    for m in _RGB_RE.finditer(html_text):
        r, g, b = (min(255, int(x)) for x in m.groups())
        hexv = "#%02x%02x%02x" % (r, g, b)
        counts[hexv] = counts.get(hexv, 0) + 1
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)


def _pick_palette(colors: list[tuple[str, int]]) -> dict[str, str]:
    """Choose accent + secondary (saturated, not near-white/black), plus bg/text."""
    accent = accent2 = None
    saturated: list[tuple[str, int, float]] = []
    for hexv, n in colors:
        rgb = _rgb(hexv)
        l, s = _luma(rgb), _saturation(rgb)
        if s >= 0.25 and 25 <= l <= 235:
            saturated.append((hexv, n, s))
    # rank saturated colours by frequency, then vividness
    saturated.sort(key=lambda t: (t[1], t[2]), reverse=True)
    if saturated:
        accent = saturated[0][0]
        for hexv, _n, _s in saturated[1:]:
            if hexv != accent:
                accent2 = hexv
                break

    # background: most frequent near-white (or near-black for dark sites)
    light = [(h, n) for h, n in colors if _luma(_rgb(h)) >= 240]
    dark = [(h, n) for h, n in colors if _luma(_rgb(h)) <= 24]
    bg = (light[0][0] if light else "#ffffff")
    # If the site is clearly dark-dominant, flip.
    if dark and light and dark[0][1] > light[0][1] * 1.5:
        bg = dark[0][0]
    text = "#111111" if _luma(_rgb(bg)) >= 128 else "#f5f5f5"

    return {
        "accent": accent or "#1f6feb",
        "accent2": accent2 or accent or "#1f6feb",
        "bg": bg,
        "text": text,
        "is_dark": _luma(_rgb(bg)) < 128,
    }


# ----------------------------------------------------------------------------- fonts

def _pick_fonts(html_text: str) -> dict[str, str | None]:
    google_url = None
    gm = _GF_RE.search(html_text)
    families: list[str] = []
    if gm:
        google_url = "https://" + gm.group(0)
        for fam in _GF_FAMILY_RE.findall(google_url):
            name = fam.split(":")[0].replace("+", " ").strip()
            if name and name.lower() not in _GENERIC_FONTS:
                families.append(name)

    # also scan font-family declarations, ranked by frequency
    decl_counts: dict[str, int] = {}
    for m in _FONT_DECL_RE.finditer(html_text):
        first = m.group(1).split(",")[0].strip().strip("'\"")
        if first and first.lower() not in _GENERIC_FONTS and len(first) <= 40:
            decl_counts[first] = decl_counts.get(first, 0) + 1
    ranked = [f for f, _ in sorted(decl_counts.items(), key=lambda kv: kv[1], reverse=True)]

    ordered: list[str] = []
    for f in families + ranked:
        if f not in ordered:
            ordered.append(f)

    heading = ordered[0] if ordered else None
    body = ordered[1] if len(ordered) > 1 else heading
    return {"font_heading": heading, "font_body": body, "google_fonts_url": google_url}


def google_fonts_link(families: list[str]) -> str | None:
    """Build a css2 link for any families we have names for but no link."""
    fams = [f for f in families if f]
    if not fams:
        return None
    parts = "&".join(
        "family=" + f.replace(" ", "+") + ":wght@300;400;500;600;700" for f in dict.fromkeys(fams)
    )
    return f"https://fonts.googleapis.com/css2?{parts}&display=swap"


# ----------------------------------------------------------------------------- logo

def _pick_logo(html_text: str, base_url: str) -> str | None:
    og = _meta(html_text, "og:image")
    # prefer an <img> that smells like a logo over a generic og:image
    for m in re.finditer(r"<img[^>]+>", html_text, re.IGNORECASE):
        tag = m.group(0)
        if re.search(r"(logo|brand)", tag, re.IGNORECASE):
            src = re.search(r"\bsrc\s*=\s*[\"']([^\"']+)[\"']", tag, re.IGNORECASE)
            if src and not src.group(1).startswith("data:"):
                return urljoin(base_url, src.group(1))
    if og:
        return og
    # apple-touch-icon / favicon
    for rel in ("apple-touch-icon", "icon", "shortcut icon"):
        lm = re.search(
            r"<link[^>]+rel\s*=\s*[\"'][^\"']*" + re.escape(rel) + r"[^\"']*[\"'][^>]*>",
            html_text, re.IGNORECASE,
        )
        if lm:
            hm = re.search(r"href\s*=\s*[\"']([^\"']+)[\"']", lm.group(0), re.IGNORECASE)
            if hm:
                return urljoin(base_url, hm.group(1))
    return None


def _brand_name(html_text: str) -> str | None:
    name = _meta(html_text, "og:site_name") or _meta(html_text, "og:title") or _title(html_text)
    if not name:
        return None
    # trim "Brand - tagline" / "Brand | tagline" → "Brand"
    for sep in (" — ", " - ", " | ", " · ", ": "):
        if sep in name:
            head = name.split(sep)[0].strip()
            if 2 <= len(head) <= 60:
                return head
    return name.strip()


# ----------------------------------------------------------------------------- public

def extract(url: str) -> dict[str, Any]:
    """Mine brand tokens from a site. Always returns a dict (never raises)."""
    parsed = urlparse(url if "://" in url else "https://" + url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    out: dict[str, Any] = {
        "url": base, "ok": False, "name": None, "tagline": None,
        "accent": "#1f6feb", "accent2": "#1f6feb", "bg": "#ffffff",
        "text": "#111111", "is_dark": False,
        "font_heading": None, "font_body": None, "google_fonts_url": None,
        "logo_url": None, "hero_url": None,
    }
    page = _get(base) or _get(parsed.geturl())
    if not page:
        return out

    out["ok"] = True
    out.update(_pick_palette(_collect_colors(page)))
    out.update(_pick_fonts(page))
    if not out["google_fonts_url"]:
        out["google_fonts_url"] = google_fonts_link([out["font_heading"], out["font_body"]])
    out["logo_url"] = _pick_logo(page, base)
    out["hero_url"] = _meta(page, "og:image")
    out["name"] = _brand_name(page)
    out["tagline"] = _meta(page, "og:description") or _meta(page, "description")
    return out


def _enrich_one(url: str) -> dict[str, Any]:
    page = _get(url)
    if not page:
        return {}
    return {
        "thumb": _meta(page, "og:image"),
        "canonical_name": _meta(page, "og:title"),
        "desc": _meta(page, "og:description"),
    }


def enrich_items(items: list[dict[str, Any]], *, max_workers: int = 6) -> int:
    """Fill thumb/desc/canonical_name for items that carry a URL. Returns count
    enriched. Failure-tolerant: a dead link just leaves that item text-only."""
    targets = [(i, it) for i, it in enumerate(items) if it.get("url")]
    if not targets or requests is None:
        return 0
    enriched = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_enrich_one, it["url"]): i for i, it in targets}
        for fut in concurrent.futures.as_completed(futs):
            idx = futs[fut]
            try:
                data = fut.result()
            except Exception:
                data = {}
            if data and any(data.values()):
                for k, v in data.items():
                    if v:
                        items[idx][k] = v
                enriched += 1
    return enriched


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    target = sys.argv[1] if sys.argv[1:] else "https://www.doubledproject.com"
    print(json.dumps(extract(target), ensure_ascii=False, indent=2))
