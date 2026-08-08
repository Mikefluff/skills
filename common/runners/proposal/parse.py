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
from dataclasses import dataclass, field
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
        # enrichment slots (filled later by brand.enrich_items)
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


def _is_total_key(key: str) -> bool:
    return any(key == k or key.startswith(k) for k in _TOTAL_KEYS)


@dataclass
class _Scan:
    """What one pass over the offer's lines found."""

    client: dict[str, str] = field(default_factory=dict)
    extra: dict[str, str] = field(default_factory=dict)
    items: list[dict[str, Any]] = field(default_factory=list)
    total_stated: float | None = None
    total_currency: str | None = None
    footer_lines: list[str] = field(default_factory=list)
    in_order: bool = False
    seen_total: bool = False

    def take_total(self, value: str) -> None:
        """The grand total also closes the order section."""
        match = _AMOUNT_RE.search(value)
        if match:
            self.total_stated = _parse_amount(match.group("price"))
            self.total_currency = _norm_currency(match.group("cur2") or match.group("cur1"))
        self.seen_total = True
        self.in_order = False

    def take_field(self, key: str, value: str) -> None:
        """A known label goes to the client block; anything else is kept aside."""
        canon = _FIELD_ALIASES.get(key)
        if canon:
            self.client[canon] = value
        elif value:
            self.extra[key] = value


def _scan_lines(lines: list[str]) -> _Scan:
    scan = _Scan()
    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = _strip_lead_emoji(line).strip()
        if not stripped:
            continue

        # Everything after the grand total is footer material.
        if scan.seen_total:
            scan.footer_lines.append(line)
            continue

        kv = _split_key_value(line)
        if kv and _is_total_key(kv[0]):
            scan.take_total(kv[1])
            continue

        # Order section header (e.g. "🧾 Order:", "Заказ:").
        if not scan.in_order and _is_order_header(stripped.lower()):
            scan.in_order = True
            continue

        # Inside the order, item-parse MUST win over the footer heuristics —
        # product URLs contain 'catalogue', which the footer check matches on.
        if scan.in_order:
            item = _parse_item_line(line)
            if item:
                scan.items.append(item)
                continue

        if _is_footer_line(line):
            scan.footer_lines.append(line)
            scan.in_order = False
            continue

        if kv:
            scan.take_field(*kv)
    return scan


def _site_url(blob: str, catalog_url: str | None) -> str | None:
    """A labelled 'сайт:' host, else a bare www host, else the catalogue's origin."""
    match = re.search(
        r"(?:сайт|site)\s*:?\s*((?:https?://)?[\w.-]+\.\w{2,})", blob, re.IGNORECASE
    )
    if not match:
        match = re.search(r"\b((?:https?://)?www\.[\w.-]+\.\w{2,})", blob)
    if match:
        host = match.group(1)
        return host if host.startswith("http") else "https://" + host
    if catalog_url:
        origin = re.match(r"(https?://[^/]+)", catalog_url)
        return origin.group(1) if origin else None
    return None


def _extract_footer(footer_lines: list[str]) -> dict[str, str | None]:
    blob = "\n".join(footer_lines)
    urls = _BARE_URL_RE.findall(blob)
    catalog_url = urls[0] if urls else None
    return {"catalog_url": catalog_url, "site_url": _site_url(blob, catalog_url)}


def _resolve_currency(items: list[dict[str, Any]], total_currency: str | None) -> str:
    """Majority vote across the items; the total's currency is the fallback.

    A vote rather than first-wins: one line typed ฿ where the rest say THB
    should not decide the whole document.
    """
    seen = [it["currency"] for it in items if it["currency"]]
    if seen:
        return max(set(seen), key=seen.count)
    return total_currency or "THB"


def _find_outliers(items: list[dict[str, Any]], subtotal: float) -> list[dict[str, Any]]:
    """Flag a line that dominates the subtotal — usually a typo.

    The seed offer's 5 000 000 logistics line is 95% of its total. Flagged,
    never auto-corrected: the orchestrator decides. Below four items a large
    share is ordinary, so the check does not run.
    """
    if subtotal <= 0 or len(items) < 4:
        return []
    return [
        {
            "index": index,
            "name": item["name"],
            "price": item["price"],
            "share": round(item["price"] / subtotal, 4),
        }
        for index, item in enumerate(items)
        if item["price"] and item["price"] / subtotal >= 0.6
    ]


def parse(text: str) -> dict[str, Any]:
    """Parse a raw offer into a ``skills.proposal.plan.v1`` dict."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    scan = _scan_lines(lines)

    currency = _resolve_currency(scan.items, scan.total_currency)
    for item in scan.items:
        if not item["currency"]:
            item["currency"] = currency

    subtotal = round(sum(it["price"] for it in scan.items if it["price"]), 2)
    # A stated total is reported, never trusted: the computed subtotal is what
    # the proposal charges, and a disagreement is surfaced rather than resolved.
    mismatch = (
        scan.total_stated is not None
        and abs(scan.total_stated - subtotal) > max(1.0, subtotal * 0.001)
    )

    return {
        "schema": SCHEMA,
        "client": scan.client,
        "extra_fields": scan.extra,
        "items": scan.items,
        "currency": currency,
        "subtotal_computed": subtotal,
        "total_stated": scan.total_stated,
        "total_currency": scan.total_currency or currency,
        "total_mismatch": bool(mismatch),
        "price_outliers": _find_outliers(scan.items, subtotal),
        "footer": _extract_footer(scan.footer_lines),
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    src = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1], encoding="utf-8").read()
    print(json.dumps(parse(src), ensure_ascii=False, indent=2))
