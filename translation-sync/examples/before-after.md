# translation-sync — calibration before/after pairs

3 paired examples of RU↔EN translation drift, each restored to parity. Every pair includes the drifted source/target pair, the parity-restored pair, a parity-report excerpt (exactly what the skill would emit for each state), and Deltas naming the specific drift class.

How to read these:

- The **Before** is the drifted state: RU added a sentence the EN doesn't have, or EN lost a paragraph from the RU, or the chapter title diverged between languages. These are the three most common drift shapes after a depth-pass on one language only.
- The **After** is the parity-restored state. The skill does NOT translate; it surfaces what's missing. The After columns show what the author produced after reading the report.
- The **parity-report excerpt** is the structured output `translation-sync` would emit for each state. The drift classes match `references/checklist.md` and the severity tiers match the SKILL.md spec (BLOCKING / WARNING / INFO).
- The **Deltas** name the specific drift type (added sentence, lost paragraph, divergent title) and the rule reference.

These are calibration samples. The book name «your-book» and the chapter numbers are placeholders.

---

## Example 1 — RU added a sentence not in EN

**Context.** A RU depth-pass on chapter 08 inserted a one-sentence parenthetical aside about a character's grandmother. The EN version was not touched; it still reflects the pre-aside state. The aside is concrete and load-bearing (mentions a specific year and a place name) — not just rhythmic filler — so the drift is BLOCKING, not stylistic tolerance.

### Before — drifted

**RU** (`your-book/ru/chapters/ch08.md`, lines 42–46):

> Марк зашёл в подъезд первым, и пока он шёл к лифту, Анна на секунду задержалась у почтовых ящиков, где её бабка в восемьдесят седьмом году получила телеграмму о смерти мужа и сделала вид, что не получила, потому что почтальон был чужой и ему было неудобно. Анна тряхнула головой, как будто отгоняла осу, и пошла за Марком. Лифт уже опустился на первый этаж, и они вошли в него одновременно — Марк с правой стороны, Анна с левой, как всегда, без обсуждения.

**EN** (`your-book/en/chapters/ch08.md`, lines 42–44):

> Mark entered the building first, and while he walked towards the lift, Anna paused for a moment by the post boxes. She shook her head as if waving off a wasp, and followed him. The lift had already come down to the ground floor, and they stepped into it at the same time — Mark on the right, Anna on the left, as always, without discussion.

**Parity-report excerpt (before):**

```
=== translation-sync ===
Mode: chapter your-book ch08
Languages: ru en
Routing: typography + terminology + anchor-quotes + names/realia + no-smoothing
         + content-parity

[CONTENT_PARITY] ru → en
  ru L42 — sentence present, 38 words:
        «...где её бабка в восемьдесят седьмом году получила
         телеграмму о смерти мужа и сделала вид, что не получила,
         потому что почтальон был чужой и ему было неудобно.»
  en L42 — sentence ABSENT from corresponding location.
  → BLOCKING: load-bearing aside dropped in EN.
     Contains a date (1987) and a setting-anchor (the post boxes
     as memory site) that recur in ch11 and ch19 — the EN version
     of ch11 references «her grandmother's telegram» with no
     prior set-up in EN ch08. This drift would cascade.
  (checklist.md §content-parity, what-not-to-smooth.md §dates)

[NO_SMOOTHING] ru → en
  ru "восемьдесят седьмом году" → en (absent)
  → BLOCKING: year «1987» lost in EN. If the EN sentence is
     restored, the year must remain explicit («in 1987» / «back
     in '87»), not smoothed to «one summer» or «years ago».
     (what-not-to-smooth.md §dates)

=== SUMMARY ===
Files checked: 2 (your-book/ru/ch08.md, en/ch08.md)
Findings:
  - content parity:  1 (BLOCKING — sentence dropped)
  - no-smoothing:    1 (BLOCKING — date lost in dropped sentence)
Severity totals:
  BLOCKING: 2
  WARNING:  0
  INFO:     0
Recommended action:
  - Translate the dropped RU sentence into EN, preserving the
    year «1987» and the post-box anchor verbatim.
Exit code (pre-commit): 2
```

### After — parity restored

**RU** (`your-book/ru/chapters/ch08.md`, lines 42–46) — unchanged:

> Марк зашёл в подъезд первым, и пока он шёл к лифту, Анна на секунду задержалась у почтовых ящиков, где её бабка в восемьдесят седьмом году получила телеграмму о смерти мужа и сделала вид, что не получила, потому что почтальон был чужой и ему было неудобно. Анна тряхнула головой, как будто отгоняла осу, и пошла за Марком. Лифт уже опустился на первый этаж, и они вошли в него одновременно — Марк с правой стороны, Анна с левой, как всегда, без обсуждения.

**EN** (`your-book/en/chapters/ch08.md`, lines 42–46) — sentence added back:

> Mark entered the building first, and while he walked towards the lift, Anna paused for a moment by the post boxes — the same post boxes where, in 1987, her grandmother had received the telegram about her husband's death and pretended she hadn't, because the postman was a stranger and it would have made him uncomfortable. She shook her head as if waving off a wasp, and followed him. The lift had already come down to the ground floor, and they stepped into it at the same time — Mark on the right, Anna on the left, as always, without discussion.

**Parity-report excerpt (after):**

```
=== translation-sync ===
Mode: chapter your-book ch08
Languages: ru en

[CONTENT_PARITY] ru → en
  L42 — sentence count and key-anchor parity: OK
  L42 — date "1987" present in both languages: OK
  L42 — setting anchor "post boxes / почтовые ящики" present
        in both languages with co-located grandmother reference: OK

[NO_SMOOTHING] ru → en
  L42 — "восемьдесят седьмом году" → "in 1987" — OK (literal)

=== SUMMARY ===
Files checked: 2
Findings: 0
Severity totals: BLOCKING 0 / WARNING 0 / INFO 0
Exit code (pre-commit): 0
```

**Deltas**

- EN ch08 L42 — full sentence inserted matching the RU aside: «the same post boxes where, in 1987, her grandmother had received the telegram about her husband's death and pretended she hadn't, because the postman was a stranger and it would have made him uncomfortable.»
- Date kept literal: «восемьдесят седьмом году» → «in 1987» (not «back in the late eighties», not «years ago» — what-not-to-smooth.md §dates)
- Setting anchor explicitly bound: «the same post boxes where ...» — preserves the post-boxes as memory site, which ch11 EN already references downstream
- Severity drop in the report: 2 BLOCKING → 0 findings. Pre-commit exit code: 2 → 0.
- Drift class: **content parity / sentence dropped from target** (checklist.md §15-point #7); severity BLOCKING when the dropped material contains a date, place, or recurring anchor

---

## Example 2 — EN lost a paragraph

**Context.** During an EN copy-edit pass, an editor collapsed three short paragraphs into one «for rhythm». In doing so, a middle paragraph that contained an authorial digression about a real institution (with a real founding-year date) was silently dropped. The RU version still has it. The drift is the inverse of Example 1: now the target language is the one missing material.

### Before — drifted

**RU** (`your-book/ru/chapters/ch15.md`, lines 88–96):

> Через два дня Марк пришёл в библиотеку Института мировой литературы и попросил выдать ему подшивку «Огонька» за весь шестьдесят восьмой год.
>
> Институт мировой литературы — это, для тех кто не знает, тяжёлое серое здание на Поварской улице в Москве, построенное в начале девятнадцатого века для одного из Долгоруких и переданное АН СССР в тридцать втором году под нужды только что созданного ИМЛИ; внутри пахнет старым деревом, ксерокопиями и одной конкретной маркой шампуня, которой пользуется главный библиограф Зинаида Михайловна с восемьдесят первого года, не желая менять привычки.
>
> Подшивка была толстая, переплетённая в коленкор болотного цвета, и Марк, открыв первую страницу, сразу понял, что просидит здесь до закрытия.

**EN** (`your-book/en/chapters/ch15.md`, lines 88–92) — three paragraphs collapsed into one, middle digression lost:

> Two days later Mark came to the library of the Gorky Institute of World Literature and asked for the bound run of *Ogonyok* for the whole of 1968. The volume was thick, bound in swamp-green cloth, and as soon as he opened the first page he knew he would be there until closing time.

**Parity-report excerpt (before):**

```
=== translation-sync ===
Mode: chapter your-book ch15
Languages: ru en

[CONTENT_PARITY] ru → en
  ru L90-92 — full digression paragraph present, 67 words:
        «Институт мировой литературы — это, для тех кто не знает,
         тяжёлое серое здание на Поварской улице в Москве,
         построенное в начале девятнадцатого века ... главный
         библиограф Зинаида Михайловна с восемьдесят первого года,
         не желая менять привычки.»
  en L88-92 — paragraph ABSENT.
  → BLOCKING: full authorial digression dropped in EN.
     Contains a real institution (IMLI), a real street (Povarskaya),
     two real-historical dates (early 19c, 1932), and a recurring
     minor character (Zinaida Mikhailovna, since 1981 — referenced
     again in ch22).
  (checklist.md §content-parity)

[NAMES_REALIA] ru → en
  ru "Поварская улица" → en (absent due to dropped paragraph)
  → BLOCKING: cultural realia first-mention lost — when restored,
     EN must include a brief footnote on first mention per
     names-and-realia.md §cultural realia.
  ru "Зинаида Михайловна" → en (absent)
  → BLOCKING: minor character first-mention dropped — character
     recurs in ch22; EN ch22 currently references «the chief
     bibliographer» with no prior set-up in EN.

[NO_SMOOTHING] ru → en
  ru "тридцать втором году" → en (absent)
  ru "восемьдесят первого года" → en (absent)
  → BLOCKING: two dates lost with the dropped paragraph.

=== SUMMARY ===
Files checked: 2
Findings:
  - content parity:  1 (BLOCKING — paragraph dropped)
  - names/realia:    2 (BLOCKING — street + character first-mention)
  - no-smoothing:    2 (BLOCKING — two dates)
Severity totals:
  BLOCKING: 5
  WARNING:  0
  INFO:     0
Recommended action:
  - Restore the middle paragraph in EN ch15, preserving:
    - "1932" (year IMLI received the building)
    - "1981" (year Zinaida Mikhailovna started)
    - "Povarskaya" (street name, kept literal)
    - "Zinaida Mikhailovna" (full first-mention before ch22)
  - Add first-mention footnote for Povarskaya per
    names-and-realia.md §cultural realia.
Exit code (pre-commit): 2
```

### After — parity restored

**RU** (`your-book/ru/chapters/ch15.md`, lines 88–96) — unchanged.

**EN** (`your-book/en/chapters/ch15.md`, lines 88–96) — paragraph restored:

> Two days later Mark came to the library of the Gorky Institute of World Literature and asked for the bound run of *Ogonyok* for the whole of 1968.
>
> The Gorky Institute of World Literature — for those who do not know — is a heavy grey building on Povarskaya Street[^1] in Moscow, built at the start of the nineteenth century for one of the Dolgoruky princes and handed over to the Soviet Academy of Sciences in 1932 for the use of the just-founded IMLI; inside, it smells of old wood, photocopies, and one particular brand of shampoo that the chief bibliographer Zinaida Mikhailovna has used since 1981, having no wish to change her habits.
>
> The volume was thick, bound in swamp-green cloth, and as soon as he opened the first page he knew he would be there until closing time.
>
> [^1]: Povarskaya Street — a central Moscow street, traditionally housing aristocratic mansions and, since the Soviet period, academic institutions.

**Parity-report excerpt (after):**

```
=== translation-sync ===
Mode: chapter your-book ch15
Languages: ru en

[CONTENT_PARITY] ru → en
  L88-96 — paragraph count: 3 / 3 — OK
  L90-92 — digression paragraph restored, key anchors present:
           IMLI, Povarskaya, 1932, Zinaida Mikhailovna, 1981
[NAMES_REALIA] ru → en
  L90 — "Povarskaya Street" first-mention footnote: present — OK
  L92 — "Zinaida Mikhailovna" first-mention before ch22: OK
[NO_SMOOTHING] ru → en
  L91 — "тридцать втором году" → "1932" — OK
  L92 — "восемьдесят первого года" → "1981" — OK

=== SUMMARY ===
Files checked: 2
Findings: 0
Severity totals: BLOCKING 0 / WARNING 0 / INFO 0
Exit code (pre-commit): 0
```

**Deltas**

- EN ch15 L90–92 — full middle paragraph translated and restored
- All four dates / proper nouns kept literal:
  - «тридцать втором году» → «1932» (not «in the early Soviet period»)
  - «восемьдесят первого года» → «1981» (not «since the early eighties»)
  - «Поварская улица» → «Povarskaya Street» (transliterated, not «the main street»)
  - «Зинаида Михайловна» → «Zinaida Mikhailovna» (full first-mention before ch22 references «the chief bibliographer»)
- First-mention footnote added for «Povarskaya Street» per names-and-realia.md §cultural realia
- IMLI / «Институт мировой литературы» — kept literal with the established «Gorky Institute of World Literature» rendering (per terminology.md, if registered; otherwise: WARNING for registration)
- Severity drop in the report: 5 BLOCKING → 0 findings. Pre-commit exit code: 2 → 0.
- Drift class: **content parity / paragraph dropped from target** + **names/realia / first-mention dropped** + **no-smoothing / dates lost** (compound drift — one editorial decision triggered three rule violations)

---

## Example 3 — Chapter title divergence

**Context.** The RU chapter title was tightened in a depth-pass from «Зеркало в коридоре Каменноостровского» to «Зеркало в коридоре». The EN title was not synced; it still reflects the longer original. The PT-BR title was synced to the new short form. The result: three languages, two titles, no canonical answer. Worse, the EN longer form contains the toponym «Kamennoostrovsky», which the author specifically removed (it was a research artefact that didn't survive the edit).

### Before — drifted

**RU** (`your-book/ru/chapters/ch12.md` L1):

```
# Зеркало в коридоре
```

**EN** (`your-book/en/chapters/ch12.md` L1):

```
# The Mirror in the Kamennoostrovsky Corridor
```

**PT-BR** (`your-book/pt-br/chapters/ch12.md` L1):

```
# O espelho no corredor
```

**Parity-report excerpt (before):**

```
=== translation-sync ===
Mode: chapter your-book ch12
Languages: ru en pt-br

[CONTENT_PARITY] chapter title — three-way divergence
  ru   L1 — "Зеркало в коридоре"                            (3 words)
  en   L1 — "The Mirror in the Kamennoostrovsky Corridor"   (6 words)
  pt-br L1 — "O espelho no corredor"                         (4 words)
  → BLOCKING: titles diverge across all three languages.
     RU and PT-BR are in parity (short form); EN is the
     stale long form. The toponym "Kamennoostrovsky" was
     intentionally removed from RU in the depth-pass (see
     anchor-quotes.md §ch12 note: «title shortened, toponym
     dropped, was research artefact»).
  (checklist.md §chapter-title-parity)

[NAMES_REALIA] en
  L1 — "Kamennoostrovsky" — toponym should not appear in
       the chapter title per the post-depth-pass canon.
       The word is fine in the chapter body where it
       organically belongs; it is not fine as a load-bearing
       title element.
  (anchor-quotes.md §ch12 note, names-and-realia.md
   §cultural realia §when-to-cut-from-title)

=== SUMMARY ===
Files checked: 3 (ru, en, pt-br)
Findings:
  - content parity:  1 (BLOCKING — title divergence three-way)
  - names/realia:    1 (BLOCKING — toponym in title against canon)
Severity totals:
  BLOCKING: 2
  WARNING:  0
  INFO:     0
Recommended action:
  - Sync EN title to the short form to match RU and PT-BR:
    "The Mirror in the Corridor".
  - Remove "Kamennoostrovsky" from the title; the word stays
    in the body of the chapter where it is contextually
    introduced (ch12 L42 EN).
Exit code (pre-commit): 2
```

### After — parity restored

**RU** L1 — unchanged: `# Зеркало в коридоре`

**EN** L1 — synced:

```
# The Mirror in the Corridor
```

**PT-BR** L1 — unchanged: `# O espelho no corredor`

**Parity-report excerpt (after):**

```
=== translation-sync ===
Mode: chapter your-book ch12
Languages: ru en pt-br

[CONTENT_PARITY] chapter title — three-way parity check
  ru   L1 — "Зеркало в коридоре"           (3 words)
  en   L1 — "The Mirror in the Corridor"   (5 words)
  pt-br L1 — "O espelho no corredor"        (4 words)
  → OK: all three titles render the same short canonical
     form; word-count differences are within natural
     language tolerance (RU 3 / EN 5 / PT-BR 4 reflects
     the article systems, not content divergence).

[NAMES_REALIA] en
  L1 — no toponym in title — OK
  L42 — "Kamennoostrovsky" — toponym present in body
        where it is contextually introduced — OK

=== SUMMARY ===
Files checked: 3
Findings: 0
Severity totals: BLOCKING 0 / WARNING 0 / INFO 0
Exit code (pre-commit): 0
```

**Deltas**

- EN ch12 L1: «The Mirror in the Kamennoostrovsky Corridor» → «The Mirror in the Corridor»
- Toponym «Kamennoostrovsky» removed from title; the word is preserved in EN ch12 body at L42 («the mirror at the end of the Kamennoostrovsky corridor, where Alyona used to hang her coat»), which is where the canon allows it (the body sets the toponym; the title is the short reference)
- Word-count check post-fix: RU 3 / EN 5 / PT-BR 4 — within natural article-system tolerance (EN's «The ... in the ...» adds 2 articles; PT-BR's «no» contracts one)
- No change to RU or PT-BR — they were already in parity
- Severity drop in the report: 2 BLOCKING → 0 findings. Pre-commit exit code: 2 → 0.
- Drift class: **content parity / chapter title** + **names/realia / toponym in title against canon** (checklist.md §chapter-title-parity + anchor-quotes.md §ch12 note); severity BLOCKING when the divergence involves a deliberately-removed canonical element, not just word-order tolerance

---

## Pattern summary

Across all 3 pairs:

1. The skill never translates. It surfaces the gap and names the rule that was violated; the author closes the gap.
2. «Content parity» is the umbrella drift class. It splits into three shapes in these pairs: added sentence (target lost it), dropped paragraph (target lost it), divergent title (one of N languages is stale).
3. Compound drift is common: a single editorial decision (drop a paragraph) can trigger violations in three categories at once (content-parity + names/realia + no-smoothing). The report surfaces each separately so the fix is structured.
4. Severity in translation-sync is unforgiving on **load-bearing material**: dates, place names, recurring characters, anchor quotes, chapter titles. Stylistic differences (rhythm, sentence count, idiom equivalence) stay INFO.
5. The pre-commit exit code (0 / 1 / 2) follows severity. The author can disable the hook for stylistic-only WARN runs; BLOCKING dates and titles should remain hard-gated.
