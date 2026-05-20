# Anchor Quotes — Canonical Translations

These phrases are load-bearing. They translate **literally**, without "improvement by meaning". Every `[ANCHOR_QUOTES]` finding in the parity report cites a row in one of these tables.

Anchor quotes are sentences where the EXACT wording carries the meaning. They are the lines you would put on the back cover. They are the lines the reader will quote back. They are the lines where word order and word count matter.

**Rule of use:** any deviation from the canonical translation in EN or PT-BR is BLOCKING. No extenders. No "improvements". No re-balancing of word count.

---

## Schema

Each book maintains its own anchor-quote table. The cells store the canonical translation; the row identifier locks the source.

| RU | EN | PT-BR |
|----|----|-------|
| _source-language quote, verbatim_ | _canonical EN — locked_ | _canonical PT-BR — locked_ |

Below: illustrative examples for two hypothetical books. Replace with your own anchor quotes as the manuscript stabilizes.

## Book A (fiction series, example)

| RU | EN | PT-BR |
|----|----|-------|
| «Quote A1 — short closing line of a chapter» | "Canonical EN A1." | "Canônica PT-BR A1." |
| «Quote A2 — character voice, two beats» | "Canonical EN A2 — two beats" | "Canônica PT-BR A2 — dois tempos" |
| «Quote A3 — three-word punch (period after each word)» | "Word. Word. Word." _(exact rhythm)_ | "Palavra. Palavra. Palavra." |
| «Quote A4 — minimal acknowledgement, two words» | "I know." _(strictly two words, period)_ | "Eu sei." |
| «Quote A5 — refusal with no extender» | "Don't do that again." _(not "please don't do that again")_ | "Não faça isso de novo." |

## Book B (non-fiction series, example)

| RU | EN | PT-BR |
|----|----|-------|
| «Quote B1 — aphoristic line, parallel structure» | "Canonical EN B1 — parallel structure." | "Canônica PT-BR B1 — estrutura paralela." |
| «Quote B2 — metaphor that must stay literal» | "Canonical EN B2 (literal image preserved)" | "Canônica PT-BR B2 (imagem literal preservada)" |

## Book C (new manuscript, example)

_Anchor quotes to be added as the manuscript stabilizes._ Source for additions: your story bible, e.g. `<book>/notes/story-bible.{md,tex,txt}` §canon-quotes section.

---

## Common drift patterns to flag

Concrete failure modes the auditor should look for:

1. **Added word in EN:** `"I know."` becomes `"Yes, I know."` or `"I know that."` or `"I'm aware."` — BLOCKING.
2. **Expanded clause in PT-BR:** `"Não faça isso de novo"` becomes `"Por favor, não faça isso de novo"` — BLOCKING.
3. **Word-count change:** `"Word. Word. Word."` becomes `"A whole, complete thing"` — BLOCKING.
4. **Punctuation change:** `"I know."` becomes `"I know"` (no period) or `"I know!"` — BLOCKING.
5. **Tense slip:** a past-perfective source rendered as a present-perfect-stative target — BLOCKING.
6. **Register slip:** a flat short utterance becomes formal or hedged in translation — BLOCKING. The rhythm of a quiet character's line is preserved by the exact wording.

## How the linter uses this file

For each anchor quote in the source-language file, grep the EN and PT-BR sibling chapter files for the canonical translation. Three failure modes:

1. **Canonical missing** — the source line is present, the registered EN/PT-BR line is absent in the corresponding chapter. BLOCKING.
2. **Canonical drifted** — a near-match is present but differs in word count, punctuation, or word choice. BLOCKING.
3. **Anchor candidate but unregistered** — a line in the source recurs across chapters or appears in chapter-opening / chapter-closing positions and is not in this file. WARNING — recommend adding.
