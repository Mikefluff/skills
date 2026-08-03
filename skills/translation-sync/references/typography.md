# Per-Language Typography Rules

Per-language hard rules. Every typography finding in the parity report cites a row in one of these tables.

## Quotes

| Language | Outer | Inner | Notes |
|----------|-------|-------|-------|
| **RU** | `<<...>>` (ёлочки) | `\enquote{...}` | No straight `"..."` ever. |
| **EN** | `` ``...'' `` (TeX) | `` `...' `` | Straight `"..."` is wrong. Always TeX-style. |
| **PT-BR** | `` ``...'' `` (TeX) | `` `...' `` | English style is house rule. Brazilian norm also permits French «...», but **the series uses English style** for cross-language parity. |

## Dashes

- **All languages:** long em-dash `---` (three minuses in LaTeX). Never `--`. Never `-`.
- **Direct speech:** em-dash followed by a non-breaking space: `--- Зубную щётку --- можно.`
- **EN spacing:** the same long em-dash, **with spaces around it** in our series — against American norm, in sync with RU/PT-BR rhythm. House rule.
- **PT-BR:** em-dash for dialogue (travessão), with spaces — same as EN/RU.

## Ellipsis

| Language | Form | Spacing |
|----------|------|---------|
| **RU / PT-BR** | `…` or `\dots` | Space before/after if between words |
| **EN** | `…` or `\dots` | Space before/after if between words |

Three dots in a row (`...`) — never. Always the single-character ellipsis or the LaTeX command.

## Italics

- Used to mark **semantic emphasis**, not "this is a term".
- Terms get `\textit{}` **only on first introduction**.
- **In translation:** italics stay on the same word as in the original.
  - If RU italicizes _способ_, then EN italicizes _the way_, not _the manner_ (even if `the manner` sounds better — that is no longer a precise italic).
  - The position of italics is part of the canon.

## Numbers

| Language | Form for `28` | Form for `300,000 subscribers` | Year | Decimal |
|----------|---------------|--------------------------------|------|---------|
| **RU** | `двадцать восемь` (spelled out) | `триста тысяч подписчиков` | `2026` (digits) | `0.3%` (digits) |
| **EN** | `twenty-eight` (with hyphen) | `three hundred thousand subscribers` | `2026` (digits) | `0.3%` (digits) |
| **PT-BR** | `vinte e oito` (no hyphen) | `trezentos mil assinantes` | `2026` (digits) | `0,3%` (PT-BR uses comma) |

Rule: **all numbers in prose spelled out**, except years and decimals (decimals are concrete measurements — they stay digits).

`300K subscribers` and `a huge audience` are both wrong. The first because it's not prose form; the second because it smooths concrete numbers. See [what-not-to-smooth.md](what-not-to-smooth.md).

## LaTeX-specific marks

- **EN math/formulas:** preserve LaTeX exactly. `H = -\sum p(x) \log_2 p(x)` stays. No re-notation into alternative formats.
- **References to chapters/sections:** RU uses `гл.`, EN uses `ch.`, PT-BR uses `cap.` — but a META_REF in the narrator's voice ("as in chapter 4 of AB") is forbidden in all languages (per `prose-edit` ban; mirrored here).

## Detection patterns (for the linter)

For automated flagging, search for these patterns per file's language directory:

| Language | Search for | Means |
|----------|-----------|-------|
| **RU** | `"\w+"` (straight quotes around a word) | Wrong: should be `<<...>>` |
| **RU** | ` -- ` or ` - ` between words | Wrong: should be `---` |
| **EN** | `"\w+"` outside math/inline code | Wrong: should be `` ``...'' `` |
| **EN** | `\w---\w` (em-dash without spaces) | Wrong by house rule: should be ` --- ` |
| **PT-BR** | `«...»` | Wrong: house rule is English-style `` ``...'' `` |
| **PT-BR** | `\w---\w` (em-dash without spaces) | Wrong by house rule |
| **Any** | `\.\.\.` (three literal dots) | Wrong: should be `…` or `\dots` |
| **Any** | digits in body prose (not year, not decimal, not LaTeX math) | Suspect: probable failure of "numbers spelled out" rule |
