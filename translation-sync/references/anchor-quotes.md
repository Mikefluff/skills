# Anchor Quotes — Canonical Translations

These phrases are load-bearing. They translate **literally**, without "improvement by meaning". Every `[ANCHOR_QUOTES]` finding in the parity report cites a row in one of these tables.

Anchor quotes are sentences where the EXACT wording carries the meaning. They are the lines you would put on the back cover. They are the lines the reader will quote back. They are the lines where word order and word count matter.

**Rule of use:** any deviation from the canonical translation in EN or PT-BR is BLOCKING. No extenders. No "improvements". No re-balancing of word count.

---

## AB (God Academy)

| RU | EN | PT-BR |
|----|----|-------|
| «Мама ушла» (7-year-old Dan, _past tense_) | "Mum's gone" | "A mãe foi-se" |
| «Зубную щётку — можно» (Wei Lin, ch.5) | "Toothbrush is fine" | "A escova de dentes — pode" |
| «Для отчёта — достаточно» (ch.4, ch.15) | "For the report — enough" | "Para o relatório — basta" |
| «Ноль три процента» (Lena) | "Zero point three percent" | "Zero vírgula três por cento" |
| «Я — аналитик. Это то же самое, только без гранта и с пистолетом» (Artyom, ch.11) | "I'm an analyst. Same thing, just without the grant and with a gun" | "Sou analista. É a mesma coisa, só que sem bolsa de pesquisa e com uma arma" |
| «Программа — одна. Режим — выбираете вы» (Dan, ch.11) | "The program is one. The mode is your choice" | "O programa é um. O modo, você escolhe" |
| «Больше так не делай» (Artyom, ch.18) | "Don't do that again" _(not "please don't do that again")_ | "Não faça isso de novo" |
| «Она не умерла. Это всё, что я могу сказать» (Dan, ch.25) | "She didn't die. That's all I can tell you" | "Ela não morreu. É tudo o que posso dizer" |
| «Я знаю» (father, ch.25) | "I know." _(strictly two words, period)_ | "Eu sei." |
| «Один. Целый. Черновик» (finale) | "One. Whole. Draft." | "Um. Inteiro. Rascunho." |
| «Добро пожаловать» (Wei Lin, ch.24) | "Welcome." _(no extenders)_ | "Bem-vindo." |
| «Ужас — это ОГО» (Kira, ch.22) | "Terror is WOW." | "O pavor é UAU." |
| «Значит, не хочет» (Seryozha about the lift) | "Means it doesn't want to" | "Significa que não quer" |
| «Она. — Пауза. — Не опасна, скорее любопытна: вы её чем-то заинтересовали» (Wei Lin, ch.4) | "She. — Pause. — Not dangerous, rather curious: you've interested her with something." | "Ela. — Pausa. — Não é perigosa, mais curiosa: você a interessou de algum modo." |

## HC (Heavenly Code)

| RU | EN | PT-BR |
|----|----|-------|
| «Учёный с ответом — лектор. Учёный с вопросом — учёный» | "A scientist with an answer is a lecturer. A scientist with a question is a scientist." | "Um cientista com uma resposta é um palestrante. Um cientista com uma pergunta é um cientista." |
| «Карта здесь черновая, с драконами в углу» | "The map here is a draft, with dragons in the corner" | "O mapa aqui é rascunho, com dragões no canto" |
| «У меня вместо труб — указатели» | "Where others see pipes, I see pointers" | "Onde outros veem canos, eu vejo apontadores" |
| «Шестерёнки смотрят на него в ответ» | "The gears look back at him" | "As engrenagens olham de volta para ele" |

## EA (Era of Architects)

_Anchor quotes to be added as the manuscript stabilizes; the EA text is still in active depth-pass through ch08._ Source for additions: `books/era-arkhitektorov/notes/story-bible.tex` §КАНОН АБ + §Врезки.

---

## Common drift patterns to flag

Concrete failure modes the auditor should look for:

1. **Added word in EN:** `"I know."` becomes `"Yes, I know."` or `"I know that."` or `"I'm aware."` — BLOCKING.
2. **Expanded clause in PT-BR:** `"Não faça isso de novo"` becomes `"Por favor, não faça isso de novo"` — BLOCKING.
3. **Word-count change:** `"One. Whole. Draft."` becomes `"A whole, complete draft"` — BLOCKING.
4. **Punctuation change:** `"I know."` becomes `"I know"` (no period) or `"I know!"` — BLOCKING.
5. **Tense slip:** `«Мама ушла»` (past, perfective) rendered as `"Mum is gone"` (present-perfect-stative) — BLOCKING. The canon is `"Mum's gone"`.
6. **Register slip:** `"Toothbrush is fine"` becomes `"A toothbrush will do"` — BLOCKING. The rhythm of Wei Lin's line is preserved by the exact wording.

## How the linter uses this file

For each anchor quote in the RU file, grep the EN and PT-BR sibling chapter files for the canonical translation. Three failure modes:

1. **Canonical missing** — the RU line is present, the registered EN/PT-BR line is absent in the corresponding chapter. BLOCKING.
2. **Canonical drifted** — a near-match is present but differs in word count, punctuation, or word choice. BLOCKING.
3. **Anchor candidate but unregistered** — a line in RU recurs across chapters or appears in chapter-opening / chapter-closing positions and is not in this file. WARNING — recommend adding.
