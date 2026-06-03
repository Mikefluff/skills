# Offer parse contract (`proposal_parse.py`)

The parser is forgiving — it reads the messy, real-world Telegram/WhatsApp offer as-is.
This documents what it understands so you can fix an offer when something parses wrong.

## Header fields (client block)

Lines of the form `<emoji?> <Key>: <value>`. Leading emoji/symbols are stripped, the key
is matched case-insensitively against aliases (RU + EN):

| Canonical | Aliases (any of) |
|---|---|
| `date` | Date, Дата |
| `name` | Name, Имя, Client, Клиент |
| `event` | Event, Событие, Мероприятие, Повод |
| `phone` | Phone, Телефон, Тел, Contact, Контакт |
| `setup` | Setup, Монтаж, Сетап |
| `time` | Time, Время |
| `guests` | Guests, Гости, Pax, Кол-во гостей |
| `location` | Location, Локация, Место, Адрес, Address |
| `comment` | Comment, Комментарий, Коммент, Note, Примечание |

Unknown `Key: value` lines are kept under `extra_fields` (not rendered by default).
Empty fields (`⏰ Time:` with no value) are parsed but omitted from the document.

`event` becomes the hero title; `name` becomes the "Prepared for" line; the rest fill the
meta grid in this order: date, phone, guests, location, setup, time, comment.

## Order section

Starts at a header line containing `Order` / `Заказ` / `Позиции` / `Items` / `Состав`
(short line, optionally ending `:`). Ends at the `Total:` line or the footer.

### Item line grammar

```
<name> [ (<url>) ] [ <qty> ] <dash> [<sym>] <price> [<currency>]
```

- **name** — everything left of the URL/qty/dash. Kept verbatim (the salesperson's
  wording is preferred over the catalogue's SEO title for display).
- **url** — first `(https://…)` in parentheses, or a bare URL. Optional. Drives the
  clickable link + the photo/description enrichment.
- **qty** — a bare integer sitting between the `)`/name and the dash (`… totem) 2 —`).
  Optional. Rendered as a `×N` chip. **The price is the line total as written — qty is
  never multiplied in.**
- **dash** — `—`, `–`, or `-`.
- **price** — digits with space/`,`/`.` grouping. `5 154 000`, `5,154,000`, `10000`,
  `2.500,50` (European) all parse. A currency **symbol may lead or trail** (`$1,200`,
  `1200 THB`, `€50`).
- **currency** — `THB ฿ บาท`, `USD $`, `EUR €`, `RUB ₽ руб`, `GBP £`, `JPY ¥`, plus
  `AED/IDR/SGD`. The document currency is the majority across items (fallback: the total's,
  else `THB`). Override with `--currency`.

Lines without a parseable dash+price are skipped (logged as a warning if the order is
otherwise empty).

## Total, mismatch, outliers

- `Total:` / `Итого:` / `Всего:` / `Сумма:` line → `total_stated` + currency.
- `subtotal_computed` = sum of item line prices (this is what the document shows).
- `total_mismatch` = true when stated vs computed differ beyond a 0.1% tolerance. The
  document uses the **computed** subtotal and notes the discrepancy.
- `price_outliers` = items whose price is ≥60% of the subtotal (only when ≥4 items). A
  near-certain typo signal — e.g. the seed offer's `Логистика — 5 000 000 THB` (97%).
  **Flagged, never auto-corrected.** Surface to the user and ask whether to fix the offer.

## Footer

Lines after the total. First bare URL → `catalog_url`. A `сайт …` / `site …` token or a
`www.*` host → `site_url` (used as the auto brand-url). Falls back to the catalog URL's
origin.

## Inspect it

```bash
python3 proposal-maker/scripts/run.py --offer /tmp/offer.txt --parse-only
```
Prints the full `skills.proposal.plan.v1` JSON — items, prices, flags, footer — with no
network calls. Use it to confirm parsing before rendering.
