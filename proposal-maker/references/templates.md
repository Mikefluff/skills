# Templates

Three themes share one DOM (masthead → hero + client meta → item cards → totals →
colophon). A theme is just a CSS block layered over the base; all three consume the same
brand tokens (`--accent`, `--bg`, `--text`, `--font-heading`, `--font-body`). Switch with
`--template`.

## `editorial` (default for light sites)

Hero-led, generous whitespace, warm off-white page behind a white sheet with a soft drop
shadow. Large product photos (84px), 2-line description clamp, accent-underlined item
links. Best for **lifestyle / events / creative / hospitality** brands — the Double D
event offer lives here.

## `invoice`

Compact, restrained, business-document feel. Edge-to-edge item rows (hairline separators,
no card borders/shadow), smaller 60px photos, no tagline, tighter hero. Best for **B2B /
agency / services / formal quotes** where the client expects a clean line-item statement.

## `dark`

Premium dark canvas (`#0c0d10` page, `#16181d` cards), accent glow on the grand total,
photos pop. Best for **nightlife / production / tech / luxury** brands, or whenever the
source site is itself dark (auto-selected then). Also the safe choice when the brand logo
is a white/monochrome SVG (it stays visible).

## Auto-pick (`--template auto`, default)

- Source site is dark-dominant (`brand.is_dark`) → `dark`.
- Otherwise → `editorial`.

Choose `invoice` manually when the offer is long and the client wants a sober,
spreadsheet-like read; choose `dark` for impact or for white-logo brands on which the
editorial masthead logo would be faint.

## Print / PDF

Every theme ships `@media print` rules: exact colour adjust, A4-friendly width, and
`page-break-inside: avoid` on item cards so a card never splits across pages. Open
`proposal.html` and Cmd/Ctrl+P → "Save as PDF" for a perfect, clickable-link PDF, or pass
`--pdf` to auto-render when playwright/weasyprint is installed.
