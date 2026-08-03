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

from .proposal_css import _BASE_CSS, _THEMES, _theme_vars

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


# --------------------------------------------------------------------------- render

def pick_theme(brand: dict[str, Any]) -> str:
    return "dark" if brand.get("is_dark") else "editorial"


def _resolve_theme(brand: dict[str, Any], template: str) -> str:
    """An unknown --template falls back rather than rendering an unstyled page."""
    theme = pick_theme(brand) if template == "auto" else template
    return theme if theme in _THEMES else "editorial"


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


def _render_brand(brand: dict[str, Any], L: dict[str, Any]) -> str:
    """Masthead identity.

    Logo AND name together: many logos are monochrome SVGs that vanish on a
    light canvas, so the name is the theme-independent identity anchor.
    """
    name = brand.get("name") or ""
    logo = brand.get("logo_url")
    parts = []
    if logo:
        parts.append(f'<img src="{_esc(logo)}" alt="{_esc(name)}">')
    if name:
        parts.append(f'<span class="brand-name">{_esc(name)}</span>')
    if not parts:
        parts.append(f'<span class="brand-name">{_esc(L["proposal"])}</span>')
    return "".join(parts)


def _hero_title(client: dict[str, str], brand: dict[str, Any], L: dict[str, Any]) -> str:
    """What the document is about, in descending order of specificity."""
    return (
        (client.get("event") or "").strip()
        or (client.get("name") or "").strip()
        or (brand.get("name") or "")
        or L["proposal"]
    )


def _hero_lines(title: str, client: dict[str, str], brand: dict[str, Any],
                theme: str, L: dict[str, Any]) -> tuple[str, str]:
    """(prepared-for line, tagline line). Either may be empty."""
    name = (client.get("name") or "").strip()
    event = (client.get("event") or "").strip()
    prepared = ""
    # Skip it when the title already IS the client's name — no point saying
    # "Acme Events / prepared for Acme Events".
    if name and (event or title != name):
        prepared = f'<p class="prepared">{_esc(L["prepared_for"])} {_esc(name)}</p>'

    tagline = (brand.get("tagline") or "").strip()
    # An invoice is a record, not a brochure; a tagline reads as noise on one.
    tagline_html = (
        f'<p class="tagline">{_esc(tagline)}</p>'
        if tagline and theme != "invoice" else ""
    )
    return prepared, tagline_html


def _totals_note(plan: dict[str, Any], currency: str, L: dict[str, Any]) -> str:
    """Surface a stated total that disagrees with the computed one."""
    if not (plan.get("total_mismatch") and plan.get("total_stated") is not None):
        return ""
    stated = fmt_money(plan["total_stated"], plan.get("total_currency") or currency)
    return f'<p class="note">{_esc(L["stated_note"].format(stated=stated))}</p>'


def _render_colophon(plan: dict[str, Any], brand: dict[str, Any], L: dict[str, Any]) -> str:
    footer = plan.get("footer", {})
    links = []
    if footer.get("catalog_url"):
        links.append(
            f'<a href="{_esc(footer["catalog_url"])}" target="_blank" rel="noopener">'
            f'{_esc(L["catalogue"])}</a>'
        )
    site = footer.get("site_url") or brand.get("url")
    if site:
        host = urlparse(site).netloc or site
        links.append(f'<a href="{_esc(site)}" target="_blank" rel="noopener">{_esc(host)}</a>')
    links.append(f'<span>{_esc(L["generated"])} {time.strftime("%d.%m.%Y")}</span>')
    return '<span class="sep">·</span>'.join(links)


# The page itself. Every hole is filled by one of the helpers above, so the
# document's shape can be read without stepping through the code that builds it.
_PAGE = """\
<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — {proposal}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{gfonts_link}
<style>{css}</style>
</head>
<body class="theme-{theme}">
<main class="page">
  <header class="masthead">
    <div class="brand">{brand_block}</div>
    <div class="doc-kicker">{proposal}</div>
  </header>
  <section class="hero">
    <h1 class="event-title">{title}</h1>
    {prepared}
    {tagline_html}
    {meta_html}
  </section>
  <section class="items">
    {items_html}
  </section>
  <section class="totals">
    <div class="grand"><span class="label">{subtotal_label}</span><span class="amount">{grand_amount}</span></div>
    {note}
  </section>
  <footer class="colophon">{colophon}</footer>
</main>
</body>
</html>
"""


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
    theme = _resolve_theme(brand, template)

    _resolve_images(plan, brand, embed_images)

    client = plan.get("client", {})
    items = plan.get("items", [])
    currency = plan.get("currency", "THB")

    brand_block = _render_brand(brand, L)
    title = _hero_title(client, brand, L)
    prepared, tagline_html = _hero_lines(title, client, brand, theme, L)
    meta_html = _render_meta(client, L)
    items_html = "".join(_render_item(it, currency, L) for it in items)

    grand_amount = fmt_money(plan.get("subtotal_computed") or 0, currency)
    note = _totals_note(plan, currency, L)
    colophon = _render_colophon(plan, brand, L)

    gfonts = brand.get("google_fonts_url")
    gfonts_link = f'<link rel="stylesheet" href="{_esc(gfonts)}">' if gfonts else ""

    return _PAGE.format(
        lang=_esc(lang),
        title=_esc(title),
        proposal=_esc(L["proposal"]),
        gfonts_link=gfonts_link,
        css=":root{" + _theme_vars(brand, theme) + "}" + _BASE_CSS + _THEMES.get(theme, ""),
        theme=_esc(theme),
        brand_block=brand_block,
        prepared=prepared,
        tagline_html=tagline_html,
        meta_html=meta_html,
        items_html=items_html,
        subtotal_label=_esc(L["subtotal"]),
        grand_amount=_esc(grand_amount),
        note=note,
        colophon=colophon,
    )


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
