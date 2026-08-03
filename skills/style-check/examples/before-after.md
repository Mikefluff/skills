# style-check — calibration before/after pairs

3 paired examples showing prose passages with hidden neuroslop tells, the same passages rewritten clean, and a linter-report excerpt showing severity drop from WARNING/neuroslop → INFO/clean. Each pair tests the skill's actual job: read the prose, name the slop pattern by category, leave the editing to the author.

How to read these:

- The **Before** is a passage with embedded slop signatures. They are not always immediately ugly — that's the point: «let's be honest», «in this context», «embarked on a journey» all read as normal English/Russian until you know the pattern. The lint catches them by regex.
- The **After** is the same passage minimally rewritten — the author keeps voice and argument, only the slop signatures move out.
- The **linter-report excerpt** is exactly what style-check would emit for each version. The category labels match `skills/writer/references/neuroslop-categories.md` and the severity scale matches `references/severity.md`.
- The **Deltas** name the specific pattern (category + line) removed.

These are calibration samples. The prose is illustrative — short enough to fit, long enough to host real slop.

---

## Example 1 — «Let's-be-honest» hook + GPT_FILLER cluster (Russian, essay register)

**Context.** A draft opening for a longform essay on professional burnout. The writer thinks they're being direct and informal. The lint sees four neuroslop signatures in five sentences.

### Before

> Давайте честно: профессиональное выгорание стало повсеместным явлением в современном мире. Важно понимать, что многие из нас сталкиваются с этим, но боятся признаться. Стоит отметить, что симптомы выгорания часто маскируются под обычную усталость. Шаг за шагом мы привыкаем работать на износ, не замечая, как это меняет нас. Суть в том, что выгорание — это не личная слабость, а системная проблема.

**Linter-report excerpt (before):**

```
=== style-check ===
Mode: file essays/draft01.md
Routing: writer + essay-write

[FILE 1] essays/draft01.md
  ----
  L1:1   AI_QA           «Давайте честно:»
                          → стоковый виральный hook (writer L1 cat 1)
  L1:8   GPT_FILLER      «Важно понимать, что»
                          → паразитная вводная (writer L1 cat 7)
  L1:142 GPT_FILLER      «Стоит отметить, что»
                          → паразитная вводная (writer L1 cat 7)
  L1:201 AI_QA           «Шаг за шагом»
                          → стоковый темпоральный филлер (writer L1 cat 1)
  L1:289 AI_QA           «Суть в том, что»
                          → стоковая виральная связка (writer L1 cat 1)

=== SUMMARY ===
Files checked: 1
Total violations:
  - writer L1 (regex): 5  (3 categories triggered ≥2 times)
Severity:
  - WARNING (neuroslop ≥2 matches per category): 5
Verdict: neuroslop suspected (5+ hits)
Exit code (pre-commit): 2
```

### After

> Профессиональное выгорание стало одной из тех тем, которые в кулуарах конференций обсуждают чаще, чем на самих конференциях, и реже всего — с теми, у кого оно сейчас. Симптомы маскируются под обычную усталость, под лень, под характер, под отсутствие силы воли — под что угодно, лишь бы не под выгорание, потому что выгорание подразумевает, что система, на которую человек работал, его этого ресурса лишила, а это уже разговор не про человека, а про систему. Системы такие разговоры не любят.

**Linter-report excerpt (after):**

```
=== style-check ===
Mode: file essays/draft01.md
Routing: writer + essay-write

[FILE 1] essays/draft01.md
  ----
  (no findings)

=== SUMMARY ===
Files checked: 1
Total violations: 0
Severity:
  - BLOCKING: 0
  - WARNING:  0
  - INFO:     0
Verdict: clean
Exit code (pre-commit): 0
```

**Deltas**

- L1:1 `«Давайте честно:»` — AI_QA cat 1, removed; replaced with a concrete observation about conference kuluars (no filler hook)
- L1:8 `«Важно понимать, что»` — GPT_FILLER cat 7, removed; the claim («symptoms маскируются») now stands on its own
- L1:142 `«Стоит отметить, что»` — GPT_FILLER cat 7, removed; the same content moves into a flowing subordinate clause
- L1:201 `«Шаг за шагом»` — AI_QA cat 1, removed; the «gradual habituation» argument is dropped (it was filler) and replaced with the «не под выгорание» chain, which carries the gradual sense without the stock phrase
- L1:289 `«Суть в том, что»` — AI_QA cat 1, removed; the closing thesis is restructured as «а это уже разговор не про человека, а про систему», which lands the same point through the prose instead of through a meta-marker
- Severity drop in the report: 5 WARNING → 0 findings (clean). Pre-commit exit code: 2 → 0.

---

## Example 2 — «In this context» filler + EMBARKED_ON_JOURNEY metaphor (English, fiction register)

**Context.** A draft passage from a novel's chapter five. The narrator describes a character returning to a city she used to live in. The Before has two of the most-common LLM tells in literary English: the «in this context» filler and the «embarked on a journey» worn metaphor.

### Before

> She returned to Lisbon after seven years. In this context, the city felt smaller than she remembered — narrower streets, lower buildings, the same trams running on schedules she had forgotten how to read. She had embarked on a journey of self-discovery, although she would not have called it that; she would have called it, if asked, simply «going back». It is interesting to note that the apartment she had once shared with Pedro was now a souvenir shop, selling miniature azulejos to tourists who took photographs of the doorway without knowing what had been behind it.

**Linter-report excerpt (before):**

```
=== style-check ===
Mode: file fiction/ch05.md
Routing: writer + prose-edit

[FILE 1] fiction/ch05.md
  ----
  L1:34  AI_TELL_PHRASE  «In this context»
                          → filler transition; cut entirely
                          (writer L1 cat EN-7)
  L1:206 EN_AI_METAPHOR   «embarked on a journey of self-discovery»
                          → AI-tell vocabulary; replace with concrete action
                          (writer L1 cat EN-3)
  L1:368 GPT_FILLER       «It is interesting to note that»
                          → filler transition; cut entirely
                          (writer L1 cat EN-7)
  L1:14  TAUTOLOGY        «returned ... back» (implied by «going back» 4 lines later)
                          → minor — same backward-motion idea stated thrice
                          (prose-edit cleanness #5)

=== SUMMARY ===
Files checked: 1
Total violations: 4
Severity:
  - WARNING: 3 (filler transitions × 2, AI metaphor × 1)
  - INFO:    1 (tautology — author's call)
Verdict: borderline (3 WARNING hits)
Exit code (pre-commit): 1
```

### After

> She came back to Lisbon after seven years. The city felt smaller than she remembered — narrower streets, lower buildings, the same trams running on schedules she had forgotten how to read. She had not come to find herself; she had come because her cousin was getting married, and because the ticket had been cheap, and because some part of her wanted to see whether the apartment she had once shared with Pedro was still there. It was not. It was a souvenir shop now, selling miniature azulejos to tourists who took photographs of the doorway without knowing what had been behind it.

**Linter-report excerpt (after):**

```
=== style-check ===
Mode: file fiction/ch05.md
Routing: writer + prose-edit

[FILE 1] fiction/ch05.md
  ----
  (no findings)

=== SUMMARY ===
Files checked: 1
Total violations: 0
Severity:
  - BLOCKING: 0
  - WARNING:  0
  - INFO:     0
Verdict: clean
Exit code (pre-commit): 0
```

**Deltas**

- L1:34 `«In this context»` — AI_TELL_PHRASE cat EN-7, removed; the sentence stands on its own without the discourse marker
- L1:206 `«embarked on a journey of self-discovery»` — EN_AI_METAPHOR cat EN-3 (one of the most-flagged AI-tell phrases in any prose linter); replaced with three concrete reasons («cousin's wedding», «cheap ticket», «whether the apartment was still there»). This is the prose-edit principle «replace AI metaphor with character-specific concrete» (prose-edit/SKILL.md §worn metaphors).
- L1:368 `«It is interesting to note that»` — GPT_FILLER cat EN-7, removed; the apartment-souvenir-shop reveal becomes its own short sentences («It was not. It was a souvenir shop now.») — a deliberate device, not staccato slop (prose-edit/structural-prose.md §intentional staccato).
- L1:14 `«returned ... back»` — INFO-level tautology resolved by changing «returned» → «came back», so «back» is no longer redundant
- Severity drop in the report: 3 WARNING + 1 INFO → 0 findings (clean). Pre-commit exit code: 1 → 0.

---

## Example 3 — Mixed cluster: corporate hype + uncited claim + viral format (Russian, non-fiction register)

**Context.** A draft chapter on remote work for a popular-science book. The author is gesturing toward an argument but reaching for corporate slogans and bullet-form structure that doesn't belong in a book chapter.

### Before

> Удалённая работа стала ключевой метрикой современного бизнеса. Исследования показывают, что компании, которые внедряют гибридные модели, получают значительные преимущества. Это создаёт новые точки роста и драйверы роста для всей индустрии.
>
> Три ключевых тезиса:
>
> 1. Удалёнка повышает продуктивность.
> 2. Гибрид снижает затраты на офис.
> 3. Сотрудники становятся счастливее.
>
> В конечном итоге, революционный подход к организации труда меняет всё.

**Linter-report excerpt (before):**

```
=== style-check ===
Mode: file books/ch03-remote.md
Routing: writer + essay-write

[FILE 1] books/ch03-remote.md
  ----
  L1:24  CORPORATE       «ключевой метрикой»
                          → corporate slang in essay register
                          (writer L1 cat 6 + essay-write banned)
  L1:60  UNCITED_CLAIM   «Исследования показывают, что»
                          → no source named; either cite or rewrite as
                          author's hypothesis
                          (essay-write/sourcing.md §uncited)
  L1:142 CORPORATE       «значительные преимущества»
                          → vague benefit (writer L1 cat 6)
  L1:201 CORPORATE       «точки роста и драйверы роста»
                          → corporate slang × 2
                          (writer L1 cat 6)
  L3:1   VIRAL_FORMAT    «Три ключевых тезиса: 1./2./3.»
                          → numbered-list format inside non-fiction
                          (essay-write/banned-constructions.md §viral)
  L9:1   PSEUDO_SMART    «В конечном итоге,»
                          → epistemic posing (writer L1 cat 3)
  L9:24  AI_INTENSIFIER  «революционный подход»
                          → AI-flavoured intensifier (writer L1 cat 4)

=== SUMMARY ===
Files checked: 1
Total violations: 7
Severity:
  - BLOCKING: 1 (uncited claim — essay-write/sourcing.md)
  - WARNING:  6 (corporate × 3, viral format × 1, pseudo-smart × 1, intensifier × 1)
  - INFO:     0
Verdict: neuroslop suspected (7+ hits)
Exit code (pre-commit): 2
```

### After

> Гибридная модель работы из исключения превратилась в дефолт у западных tech-компаний быстрее, чем академические исследователи успели её толком описать — что само по себе любопытно, потому что обычно происходит наоборот. Имя с соавторами (Quarterly Journal of Economics, 2024, выборка 1612 сотрудников Trip.com) показали, что переход на гибрид 3/2 снизил квартальный churn на 35% без значимого падения performance-метрик; экономия на офисных площадях у их работодателя в годовом выражении составила $2 000 на сотрудника, и это, видимо, и есть тот самый «бизнес-кейс», о котором без подобных цифр говорить было невозможно.
>
> Из этой и нескольких параллельных работ постепенно проступает контур того, что гибрид — это не идеология и не модный жест, а просто другая точка равновесия между двумя издержками, которую рынок наконец нашёл и в которой собирается какое-то время посидеть, пока не появится повод посчитать заново.

**Linter-report excerpt (after):**

```
=== style-check ===
Mode: file books/ch03-remote.md
Routing: writer + essay-write

[FILE 1] books/ch03-remote.md
  ----
  (no findings)

=== SUMMARY ===
Files checked: 1
Total violations: 0
Severity:
  - BLOCKING: 0
  - WARNING:  0
  - INFO:     0
Verdict: clean
Exit code (pre-commit): 0
```

**Deltas**

- L1:24 `«ключевой метрикой»` — CORPORATE cat 6, removed; replaced with a specific observation about default-vs-exception
- L1:60 `«Исследования показывают, что»` — UNCITED_CLAIM (BLOCKING), replaced with a real-shape source citation (journal + year + sample + cohort + effect size: «Quarterly Journal of Economics, 2024, выборка 1612 сотрудников Trip.com», «churn -35%», «$2000/сотрудник») — essay-write/sourcing.md §full-citation format
- L1:142 `«значительные преимущества»` — CORPORATE cat 6 / VAGUE_BENEFIT, replaced with the specific numbers from the cited source
- L1:201 `«точки роста и драйверы роста»` — CORPORATE cat 6 × 2, removed entirely
- L3:1 `«Три ключевых тезиса: 1./2./3.»` — VIRAL_FORMAT inside non-fiction (essay-write/banned-constructions.md), dissolved into flowing argument — the three claims survive but as embedded clauses
- L9:1 `«В конечном итоге,»` — PSEUDO_SMART cat 3, removed; the closing thought becomes a separate paragraph with a Manson-style coda landing («посчитать заново»)
- L9:24 `«революционный подход»` — AI_INTENSIFIER cat 4, removed entirely; the new ending refuses the «revolution» frame deliberately («не идеология и не модный жест»)
- Severity drop in the report: 1 BLOCKING + 6 WARNING → 0 findings (clean). Pre-commit exit code: 2 → 0.

---

## Pattern summary

Across all 3 pairs:

1. The Before passages all read «fine» on first glance — the lint catches what the eye misses by regex match against the 23-category catalogue.
2. Severity scales tier the response: a single hit is INFO, ≥2 hits in one category is WARNING, an UNCITED_CLAIM in essay register is BLOCKING (it's a sourcing failure, not a style preference).
3. The skill never edits. It reports. The After columns above are what the author produced after reading the report — the skill's job ends at the linter output.
4. Pre-commit exit codes follow the severity: 0 (clean), 1 (WARNING — author decides), 2 (BLOCKING — commit aborted).
5. Replacing slop with a void («delete the filler and stop») is fine for AI_QA / GPT_FILLER. Replacing it with a concrete image (Example 2's three reasons; Example 3's $2000/employee figure) is what turns the After from «merely passes lint» into prose that earns the page.
