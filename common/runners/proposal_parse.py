"""Offer parser for proposal-maker.

Turns a free-form, telegram-style commercial offer into a structured
``skills.proposal.plan.v1`` dict. Pure stdlib — no network, no third-party deps.

Input shape (the seed Double D Project case)::

    📆 Date: 30-06-2026
    👤 Name: Миша
    🎉 Event: Birthday Party
    ...
    🧾 Order:
    Пакет PICNIC Basic (https://…/paket-picnic-basic)  — 10000 THB
    Трипод / Тотем (https://…/tripod-totem) 2 — 6000 THB
    Авторская Фотозона  — 20000 THB
    ...
    💰Total: 5154000 THB

    🗃️Фото и Видео Услуг (Каталог)
    https://www.doubledproject.com/catalogue сайт www.doubledproject.com

Item-line grammar::

    <name> [ (<url>) ] [ <qty:int> ] <dash> <price> [<currency>]

The number after the dash is read as the **line total as written** (never
multiplied by qty); ``qty`` is surfaced as a separate column. The stated grand
total is parsed but the subtotal is **recomputed** from the items and a
``total_mismatch`` flag is raised on disagreement — we never silently rewrite a
human's number.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

SCHEMA = "skills.proposal.plan.v1"

# Dash variants that separate the item body from its price.
_DASH = "—–-"

# Currency tokens we recognise → normalised code. Order matters (longest first).
_CURRENCY = {
    "THB": "THB", "฿": "THB", "บาท": "THB",
    "USD": "USD", "$": "USD",
    "EUR": "EUR", "€": "EUR",
    "RUB": "RUB", "₽": "RUB", "РУБ": "RUB", "RUR": "RUB",
    "GBP": "GBP", "£": "GBP",
    "JPY": "JPY", "¥": "JPY",
    "AED": "AED", "IDR": "IDR", "SGD": "SGD",
}

# Header-field aliases (lower-cased, emoji/punctuation stripped) → canonical key.
_FIELD_ALIASES = {
    "date": "date", "дата": "date",
    "name": "name", "имя": "name", "client": "name", "клиент": "name",
    "event": "event", "событие": "event", "мероприятие": "event", "повод": "event",
    "phone": "phone", "телефон": "phone", "тел": "phone", "contact": "phone", "контакт": "phone",
    "setup": "setup", "монтаж": "setup", "сетап": "setup",
    "time": "time", "время": "time",
    "guests": "guests", "гости": "guests", "кол-во гостей": "guests", "pax": "guests",
    "location": "location", "локация": "location", "место": "location", "адрес": "location", "address": "location",
    "comment": "comment", "комментарий": "comment", "коммент": "comment", "note": "comment", "примечание": "comment",
}

_ORDER_HEADERS = ("order", "заказ", "позиции", "items", "состав")
_TOTAL_KEYS = ("total", "итого", "всего", "сумма", "grand total")

_URL_RE = re.compile(r"\((https?://[^)\s]+)\)")
_BARE_URL_RE = re.compile(r"https?://[^\s)]+")

# Currency token alternation, reused by item + total parsing. A symbol may sit
# either before ($1,200) or after (1200 THB) the number.
_CUR_ALT = r"THB|USD|EUR|RUB|RUR|GBP|JPY|AED|IDR|SGD|บาท|руб\.?|РУБ|[฿$€₽£¥]"
_AMOUNT_RE = re.compile(
    r"(?P<cur1>" + _CUR_ALT + r")?\s*"
    r"(?P<price>\d[\d.,\s\u00a0\u202f]*?)\s*"
    r"(?P<cur2>" + _CUR_ALT + r")?\s*$",
    re.IGNORECASE,
)
# item price: same shape, anchored to a leading dash so qty/name stay on the left.
_PRICE_RE = re.compile(r"[" + _DASH + r"]\s*" + _AMOUNT_RE.pattern, re.IGNORECASE)

_QTY_RE = re.compile(r"(?:^|\s|x|х|×)(\d{1,4})\s*$", re.IGNORECASE)


def _strip_lead_emoji(s: str) -> str:
    """Drop leading emoji / symbols / whitespace so 'key' parsing is clean."""
    i = 0
    for ch in s:
        cat = unicodedata.category(ch)
        if ch.isalnum() or ch in "+":
            break
        # keep stripping symbols (So/Sk/Sc), punctuation, separators, marks
        if cat[0] in "SPZMC" or ch.isspace():
            i += 1
            continue
        break
    return s[i:].lstrip()


def _norm_currency(tok: str | None) -> str | None:
    if not tok:
        return None
    t = tok.strip().rstrip(".").upper()
    return _CURRENCY.get(t) or _CURRENCY.get(tok.strip())


def _parse_amount(raw: str) -> float | None:
    """'5 154 000' / '5,154,000' / '1.234,50' / '10000' → float."""
    if not raw:
        return None
    s = raw.replace(" ", "").replace(" ", "").replace(" ", "")
    if not s:
        return None
    has_comma, has_dot = "," in s, "." in s
    if has_comma and has_dot:
        # last separator is the decimal point
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif has_comma:
        # comma as decimal only if it looks like ',dd' at the very end
        if re.search(r",\d{1,2}$", s):
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        digits = re.sub(r"[^\d.]", "", s)
        try:
            return float(digits) if digits else None
        except ValueError:
            return None


def _parse_item_line(line: str) -> dict[str, Any] | None:
    m = _PRICE_RE.search(line)
    if not m:
        return None
    price = _parse_amount(m.group("price"))
    if price is None:
        return None
    currency = _norm_currency(m.group("cur2") or m.group("cur1"))
    left = line[: m.start()]

    url = None
    um = _URL_RE.search(left)
    if um:
        url = um.group(1)
        left = left[: um.start()] + " " + left[um.end():]
    else:
        bm = _BARE_URL_RE.search(left)
        if bm:
            url = bm.group(0)
            left = left[: bm.start()] + " " + left[bm.end():]

    qty = None
    qm = _QTY_RE.search(left.rstrip())
    if qm:
        qty = int(qm.group(1))
        left = left[: qm.start(1)]

    name = re.sub(r"\s+", " ", left).strip(" .·•-–—")
    if not name:
        name = "—"
    return {
        "name": name,
        "url": url,
        "qty": qty,
        "price": price,
        "currency": currency,
        # enrichment slots (filled later by proposal_brand.enrich_items)
        "thumb": None,
        "desc": None,
        "canonical_name": None,
    }


def _split_key_value(line: str) -> tuple[str, str] | None:
    body = _strip_lead_emoji(line)
    if ":" not in body:
        return None
    key, _, val = body.partition(":")
    key = key.strip().lower()
    if not key or len(key) > 32:
        return None
    return key, val.strip()


def _is_order_header(low: str) -> bool:
    label = low.rstrip(": ").strip()
    return len(low) <= 40 and any(
        label == h or label.startswith(h + " ") or label.endswith(" " + h)
        for h in _ORDER_HEADERS
    )


def _is_footer_line(line: str) -> bool:
    body = _strip_lead_emoji(line).strip()
    low = body.lower()
    if not body:
        return False
    if body.startswith(("http://", "https://", "www.")):
        return True
    if re.search(r"(?:сайт|site)\s*:?\s*(?:https?://|www\.)?[\w.-]+\.\w{2,}", low):
        return True
    # bare "… (Каталог)" label line with no price
    if ("каталог" in low or "catalogue" in low) and not _PRICE_RE.search(line):
        return True
    return False


def parse(text: str) -> dict[str, Any]:
    """Parse a raw offer into a ``skills.proposal.plan.v1`` dict."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    client: dict[str, str] = {}
    extra: dict[str, str] = {}
    items: list[dict[str, Any]] = []
    total_stated: float | None = None
    total_currency: str | None = None
    footer: dict[str, str | None] = {"catalog_url": None, "site_url": None}

    in_order = False
    seen_total = False
    footer_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = _strip_lead_emoji(line).strip()
        low = stripped.lower()

        if not stripped:
            continue

        # Everything after the grand total is footer material.
        if seen_total:
            footer_lines.append(line)
            continue

        kv = _split_key_value(line)

        # Total line — also closes the order section.
        if kv and any(kv[0] == k or kv[0].startswith(k) for k in _TOTAL_KEYS):
            pm = _AMOUNT_RE.search(kv[1])
            if pm:
                total_stated = _parse_amount(pm.group("price")) if pm else None
                total_currency = _norm_currency(pm.group("cur2") or pm.group("cur1")) if pm else None
            seen_total = True
            in_order = False
            continue

        # Order section header (e.g. "🧾 Order:", "Заказ:").
        if not in_order and _is_order_header(low):
            in_order = True
            continue

        # Inside the order: try item first — product URLs contain 'catalogue',
        # so item-parse MUST win over footer heuristics.
        if in_order:
            item = _parse_item_line(line)
            if item:
                items.append(item)
                continue

        # Narrow footer detection (bare URL / "сайт" / catalogue label).
        if _is_footer_line(line):
            footer_lines.append(line)
            in_order = False
            continue

        # Header key:value.
        if kv:
            key, val = kv
            canon = _FIELD_ALIASES.get(key)
            if canon:
                client[canon] = val
            elif val:
                extra[key] = val
            continue

    # Footer extraction
    footer_blob = "\n".join(footer_lines)
    urls = _BARE_URL_RE.findall(footer_blob)
    if urls:
        footer["catalog_url"] = urls[0]
    # site domain: token after 'сайт'/'site', or a www.* host, or derive from catalog
    sm = re.search(r"(?:сайт|site)\s*:?\s*((?:https?://)?[\w.-]+\.\w{2,})", footer_blob, re.IGNORECASE)
    if not sm:
        sm = re.search(r"\b((?:https?://)?www\.[\w.-]+\.\w{2,})", footer_blob)
    if sm:
        host = sm.group(1)
        footer["site_url"] = host if host.startswith("http") else "https://" + host
    elif footer["catalog_url"]:
        m = re.match(r"(https?://[^/]+)", footer["catalog_url"])
        footer["site_url"] = m.group(1) if m else None

    # Currency resolution: majority vote across items, fallback to total's.
    item_currencies = [it["currency"] for it in items if it["currency"]]
    if item_currencies:
        currency = max(set(item_currencies), key=item_currencies.count)
    else:
        currency = total_currency or "THB"
    for it in items:
        if not it["currency"]:
            it["currency"] = currency

    subtotal = round(sum(it["price"] for it in items if it["price"]), 2)
    mismatch = (
        total_stated is not None
        and abs(total_stated - subtotal) > max(1.0, subtotal * 0.001)
    )

    # Outliers: a single line dominating the subtotal usually means a typo
    # (the seed offer's 5 000 000 logistics line is 97% of the total). We flag,
    # never auto-correct — the orchestrator decides.
    outliers: list[dict[str, Any]] = []
    if subtotal > 0 and len(items) >= 4:
        for idx, it in enumerate(items):
            if it["price"] and it["price"] / subtotal >= 0.6:
                outliers.append({
                    "index": idx,
                    "name": it["name"],
                    "price": it["price"],
                    "share": round(it["price"] / subtotal, 4),
                })

    return {
        "schema": SCHEMA,
        "client": client,
        "extra_fields": extra,
        "items": items,
        "currency": currency,
        "subtotal_computed": subtotal,
        "total_stated": total_stated,
        "total_currency": total_currency or currency,
        "total_mismatch": bool(mismatch),
        "price_outliers": outliers,
        "footer": footer,
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    src = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1], encoding="utf-8").read()
    print(json.dumps(parse(src), ensure_ascii=False, indent=2))
