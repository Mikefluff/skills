"""HTML proposal renderer for proposal-maker.

Pure-Python string assembly (no template engine). Produces a single,
self-contained `.html` file: brand tokens inlined as CSS custom properties,
a Google-Fonts link for the brand font, real product photos per line item,
clickable catalogue links, exact prices, and `@media print` rules so Cmd+P →
"Save as PDF" yields a clean, link-preserving document.

Three themes share one DOM; each is just a CSS block:
  - editorial : hero-led, generous whitespace, photo cards (default)
  - invoice   : compact business table, restrained
  - dark      : premium dark canvas, accent glow
"""

from __future__ import annotations

import base64
import html
import time
from typing import Any
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

_UA = "Mozilla/5.0 (compatible; proposal-maker/1.0)"

# --------------------------------------------------------------------------- i18n

_LABELS = {
    "ru": {
        "proposal": "Коммерческое предложение",
        "prepared_for": "Для",
        "qty": "Кол-во",
        "subtotal": "Итого",
        "stated_note": "В исходном расчёте указана сумма {stated} — она расходится с суммой позиций ниже.",
        "catalogue": "Каталог",
        "website": "Сайт",
        "generated": "Сформировано",
        "fields": {
            "date": "Дата", "event": "Событие", "name": "Клиент", "phone": "Телефон",
            "setup": "Монтаж", "time": "Время", "guests": "Гости",
            "location": "Локация", "comment": "Комментарий",
        },
    },
    "en": {
        "proposal": "Commercial Proposal",
        "prepared_for": "For",
        "qty": "Qty",
        "subtotal": "Total",
        "stated_note": "The original figure stated {stated}, which differs from the line items below.",
        "catalogue": "Catalogue",
        "website": "Website",
        "generated": "Generated",
        "fields": {
            "date": "Date", "event": "Event", "name": "Client", "phone": "Phone",
            "setup": "Setup", "time": "Time", "guests": "Guests",
            "location": "Location", "comment": "Comment",
        },
    },
}

_CURRENCY_SYMBOL = {"THB": "฿", "USD": "$", "EUR": "€", "RUB": "₽", "GBP": "£", "JPY": "¥"}
_SYMBOL_PREFIX = {"USD", "EUR", "GBP", "JPY"}

_META_ORDER = ("date", "phone", "guests", "location", "setup", "time", "comment")


def detect_lang(plan: dict[str, Any]) -> str:
    blob = " ".join(
        [str(v) for v in plan.get("client", {}).values()]
        + [it.get("name", "") for it in plan.get("items", [])]
    )
    return "ru" if any("Ѐ" <= ch <= "ӿ" for ch in blob) else "en"


def fmt_money(amount: float | None, currency: str) -> str:
    if amount is None:
        return ""
    whole = int(round(amount))
    grouped = f"{whole:,}".replace(",", " ") if amount == whole else f"{amount:,.2f}".replace(",", " ")
    sym = _CURRENCY_SYMBOL.get(currency, currency)
    if currency in _SYMBOL_PREFIX:
        return f"{sym}{grouped}"
    return f"{grouped} {sym}"


def _esc(s: Any) -> str:
    return html.escape(str(s if s is not None else ""))


# --------------------------------------------------------------------------- images

def _data_uri(url: str) -> str | None:
    if requests is None or not url or url.startswith("data:"):
        return url
    try:
        r = requests.get(url, headers={"User-Agent": _UA}, timeout=20)
        if r.status_code == 200 and r.content:
            ctype = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
            b64 = base64.b64encode(r.content).decode("ascii")
            return f"data:{ctype};base64,{b64}"
    except Exception:
        return url
    return url


def _resolve_images(plan: dict[str, Any], brand: dict[str, Any], embed: bool) -> None:
    if not embed:
        return
    if brand.get("logo_url"):
        brand["logo_url"] = _data_uri(brand["logo_url"])
    for it in plan.get("items", []):
        if it.get("thumb"):
            it["thumb"] = _data_uri(it["thumb"])


# --------------------------------------------------------------------------- CSS

_BASE_CSS = """
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;background:var(--page);color:var(--text);
  font-family:var(--font-body);line-height:1.5;font-size:15px}
a{color:inherit;text-decoration:none}
.page{max-width:840px;margin:0 auto;background:var(--bg);
  padding:56px 60px 40px}
.masthead{display:flex;align-items:center;justify-content:space-between;
  gap:24px;padding-bottom:24px;border-bottom:1px solid var(--hair)}
.brand{display:flex;align-items:center;gap:14px;min-width:0}
.brand img{height:42px;width:auto;max-width:220px;object-fit:contain}
.brand .brand-name{font-family:var(--font-heading);font-weight:700;
  font-size:19px;letter-spacing:-.01em}
.doc-kicker{font-size:11px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--accent);font-weight:600;white-space:nowrap}
.hero{padding:40px 0 28px}
.hero .event-title{font-family:var(--font-heading);font-weight:700;
  font-size:40px;line-height:1.05;letter-spacing:-.02em;margin:0}
.hero .prepared{margin:10px 0 0;color:var(--muted);font-size:16px}
.hero .tagline{margin:18px 0 0;color:var(--muted);max-width:60ch}
.meta{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
  gap:2px 28px;margin:28px 0 0;padding:0}
.meta .row{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--hair)}
.meta dt{color:var(--muted);font-size:12px;letter-spacing:.06em;
  text-transform:uppercase;min-width:96px;margin:0;padding-top:2px}
.meta dd{margin:0;font-weight:500}
.items{margin:36px 0 0;display:flex;flex-direction:column;gap:12px}
.item{display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center;
  padding:14px;border:1px solid var(--hair);border-radius:14px;
  background:var(--card);page-break-inside:avoid;break-inside:avoid}
.item.no-thumb{grid-template-columns:1fr auto}
.item .thumb{width:84px;height:84px;border-radius:10px;overflow:hidden;
  background:var(--hair);flex:none}
.item .thumb img{width:100%;height:100%;object-fit:cover;display:block}
.item .body{min-width:0}
.item .item-name{font-family:var(--font-heading);font-weight:600;font-size:17px;
  margin:0;letter-spacing:-.01em}
.item .item-name a{border-bottom:1.5px solid var(--accent);padding-bottom:1px}
.item .item-desc{margin:5px 0 0;color:var(--muted);font-size:13.5px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.item .qty{display:inline-block;margin-top:7px;font-size:12px;font-weight:600;
  color:var(--accent);background:var(--accent-soft);border-radius:999px;
  padding:2px 10px}
.item .item-price{font-family:var(--font-heading);font-weight:700;font-size:18px;
  white-space:nowrap;text-align:right}
.totals{margin:30px 0 0;padding-top:22px;border-top:2px solid var(--text)}
.totals .grand{display:flex;align-items:baseline;justify-content:space-between}
.totals .grand .label{font-family:var(--font-heading);font-weight:700;
  font-size:20px;letter-spacing:.02em;text-transform:uppercase}
.totals .grand .amount{font-family:var(--font-heading);font-weight:800;
  font-size:30px;color:var(--accent)}
.totals .note{margin:10px 0 0;font-size:12.5px;color:var(--muted)}
.colophon{margin:42px 0 0;padding-top:20px;border-top:1px solid var(--hair);
  display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;
  font-size:12.5px;color:var(--muted)}
.colophon a{color:var(--accent);font-weight:600}
.colophon .sep{opacity:.4}
@media (max-width:680px){.page{padding:32px 22px}.meta{grid-template-columns:1fr}
  .hero .event-title{font-size:30px}}
@media print{.page{padding:24px 0;max-width:none}body{font-size:12.5px}
  .item{border-color:var(--hair)}}
"""

_THEMES = {
    "editorial": """
:root{--page:#f2f1ec;--card:#ffffff;--hair:#e6e3da;--muted:#6c6a63}
.page{box-shadow:0 1px 40px rgba(0,0,0,.06)}
""",
    "invoice": """
:root{--page:#ffffff;--card:#ffffff;--hair:#e7e9ee;--muted:#697086}
.items{gap:0}
.item{border-radius:0;border-left:none;border-right:none;border-top:none}
.item:first-child{border-top:1px solid var(--hair)}
.item .thumb{width:60px;height:60px}
.hero .event-title{font-size:32px}
""",
    "dark": """
:root{--page:#0c0d10;--card:#16181d;--hair:#262a33;--muted:#9aa1ad}
.item .item-name a{border-bottom-color:var(--accent)}
.totals .grand .amount{text-shadow:0 0 28px var(--accent-soft)}
""",
}


def _theme_vars(brand: dict[str, Any], theme: str) -> str:
    accent = brand.get("accent") or "#1f6feb"
    accent2 = brand.get("accent2") or accent
    bg = "#16181d" if theme == "dark" else (brand.get("bg") if not brand.get("is_dark") else "#ffffff") or "#ffffff"
    text = "#f4f5f7" if theme == "dark" else "#16181d"
    fh = brand.get("font_heading") or "Inter"
    fb = brand.get("font_body") or fh or "Inter"
    # soft accent for chips/glows
    soft = _hex_alpha(accent, 0.14)
    return (
        f"--accent:{accent};--accent2:{accent2};--accent-soft:{soft};"
        f"--bg:{bg};--text:{text};"
        f"--font-heading:'{fh}',system-ui,sans-serif;"
        f"--font-body:'{fb}',system-ui,sans-serif;"
    )


def _hex_alpha(hexv: str, a: float) -> str:
    h = hexv.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except Exception:
        return f"rgba(31,111,235,{a})"
    return f"rgba({r},{g},{b},{a})"


# --------------------------------------------------------------------------- render

def pick_theme(brand: dict[str, Any]) -> str:
    return "dark" if brand.get("is_dark") else "editorial"


def _render_meta(client: dict[str, str], L: dict[str, Any]) -> str:
    rows = []
    for key in _META_ORDER:
        val = (client.get(key) or "").strip()
        if not val:
            continue
        label = L["fields"].get(key, key.title())
        rows.append(
            f'<div class="row"><dt>{_esc(label)}</dt><dd>{_esc(val)}</dd></div>'
        )
    return f'<dl class="meta">{"".join(rows)}</dl>' if rows else ""


def _render_item(it: dict[str, Any], currency: str, L: dict[str, Any]) -> str:
    # Prefer the salesperson's offer wording — og:title is often SEO-bloated.
    name = it.get("name") or it.get("canonical_name") or "—"
    url = it.get("url")
    name_html = _esc(name)
    if url:
        name_html = f'<a href="{_esc(url)}" target="_blank" rel="noopener">{name_html}</a>'
    desc = (it.get("desc") or "").strip()
    desc_html = f'<p class="item-desc">{_esc(desc)}</p>' if desc else ""
    qty_html = ""
    if it.get("qty"):
        qty_html = f'<span class="qty">{_esc(L["qty"])} ×{int(it["qty"])}</span>'
    price_html = _esc(fmt_money(it.get("price"), it.get("currency") or currency))

    thumb = it.get("thumb")
    if thumb:
        thumb_html = f'<div class="thumb"><img src="{_esc(thumb)}" alt="" loading="lazy"></div>'
        cls = "item"
    else:
        thumb_html = ""
        cls = "item no-thumb"
    return (
        f'<article class="{cls}">{thumb_html}'
        f'<div class="body"><h3 class="item-name">{name_html}</h3>{desc_html}{qty_html}</div>'
        f'<div class="item-price">{price_html}</div></article>'
    )


def render_html(
    plan: dict[str, Any],
    brand: dict[str, Any],
    *,
    lang: str = "auto",
    template: str = "auto",
    embed_images: bool = False,
) -> str:
    if lang == "auto":
        lang = detect_lang(plan)
    L = _LABELS.get(lang, _LABELS["en"])
    theme = pick_theme(brand) if template == "auto" else template
    if theme not in _THEMES:
        theme = "editorial"

    _resolve_images(plan, brand, embed_images)

    client = plan.get("client", {})
    items = plan.get("items", [])
    currency = plan.get("currency", "THB")

    # masthead
    # Show logo AND name together: many logos are monochrome SVGs that vanish on
    # a light canvas, so the name is the theme-independent identity anchor.
    logo = brand.get("logo_url")
    brand_name = brand.get("name") or ""
    parts = []
    if logo:
        parts.append(f'<img src="{_esc(logo)}" alt="{_esc(brand_name)}">')
    if brand_name:
        parts.append(f'<span class="brand-name">{_esc(brand_name)}</span>')
    if not parts:
        parts.append(f'<span class="brand-name">{_esc(L["proposal"])}</span>')
    brand_block = "".join(parts)

    # hero
    event = (client.get("event") or "").strip()
    name = (client.get("name") or "").strip()
    title = event or name or brand_name or L["proposal"]
    prepared = ""
    if name and (event or title != name):
        prepared = f'<p class="prepared">{_esc(L["prepared_for"])} {_esc(name)}</p>'
    tagline = (brand.get("tagline") or "").strip()
    tagline_html = f'<p class="tagline">{_esc(tagline)}</p>' if tagline and theme != "invoice" else ""

    meta_html = _render_meta(client, L)
    items_html = "".join(_render_item(it, currency, L) for it in items)

    # totals
    subtotal = plan.get("subtotal_computed") or 0
    grand_amount = fmt_money(subtotal, currency)
    note = ""
    if plan.get("total_mismatch") and plan.get("total_stated") is not None:
        stated = fmt_money(plan["total_stated"], plan.get("total_currency") or currency)
        note = f'<p class="note">{_esc(L["stated_note"].format(stated=stated))}</p>'

    # colophon
    footer = plan.get("footer", {})
    links = []
    if footer.get("catalog_url"):
        links.append(f'<a href="{_esc(footer["catalog_url"])}" target="_blank" rel="noopener">{_esc(L["catalogue"])}</a>')
    site = footer.get("site_url") or brand.get("url")
    if site:
        host = urlparse(site).netloc or site
        links.append(f'<a href="{_esc(site)}" target="_blank" rel="noopener">{_esc(host)}</a>')
    links.append(f'<span>{_esc(L["generated"])} {time.strftime("%d.%m.%Y")}</span>')
    colophon = ('<span class="sep">·</span>'.join(links))

    gfonts = brand.get("google_fonts_url")
    gfonts_link = f'<link rel="stylesheet" href="{_esc(gfonts)}">' if gfonts else ""
    css = ":root{" + _theme_vars(brand, theme) + "}" + _BASE_CSS + _THEMES.get(theme, "")

    return f"""<!doctype html>
<html lang="{_esc(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)} — {_esc(L["proposal"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{gfonts_link}
<style>{css}</style>
</head>
<body class="theme-{_esc(theme)}">
<main class="page">
  <header class="masthead">
    <div class="brand">{brand_block}</div>
    <div class="doc-kicker">{_esc(L["proposal"])}</div>
  </header>
  <section class="hero">
    <h1 class="event-title">{_esc(title)}</h1>
    {prepared}
    {tagline_html}
    {meta_html}
  </section>
  <section class="items">
    {items_html}
  </section>
  <section class="totals">
    <div class="grand"><span class="label">{_esc(L["subtotal"])}</span><span class="amount">{_esc(grand_amount)}</span></div>
    {note}
  </section>
  <footer class="colophon">{colophon}</footer>
</main>
</body>
</html>
"""


def to_pdf(html_str: str, out_path) -> bool:
    """Best-effort HTML→PDF. Tries Playwright, then WeasyPrint. Returns success."""
    out_path = str(out_path)
    # 1) Playwright (Chromium) — preserves links, web fonts, exact CSS.
    try:
        from playwright.sync_api import sync_playwright  # type: ignore

        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            page.set_content(html_str, wait_until="networkidle")
            page.pdf(path=out_path, format="A4", print_background=True,
                     margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"})
            browser.close()
        return True
    except Exception:
        pass
    # 2) WeasyPrint
    try:
        from weasyprint import HTML  # type: ignore

        HTML(string=html_str).write_pdf(out_path)
        return True
    except Exception:
        pass
    return False


if __name__ == "__main__":  # pragma: no cover
    import sys
    import common.runners.proposal_parse as P  # type: ignore

    src = open(sys.argv[1], encoding="utf-8").read() if sys.argv[1:] else sys.stdin.read()
    plan = P.parse(src)
    brand = {"accent": "#99cc66", "accent2": "#8cba51", "bg": "#ffffff",
             "font_heading": "Ubuntu", "font_body": "Ubuntu", "name": "Demo",
             "google_fonts_url": "https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;600;700&display=swap"}
    sys.stdout.write(render_html(plan, brand))
