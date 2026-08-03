---
title: "Shift a passage to a different register"
persona: "Copywriter or PM with good content but the wrong tone"
time: "5-10 minutes"
skills:
  - tone-shifter
  - writer
---

# Shift a passage from one register to another

Сценарий: текст уже написан, факты на месте, аргумент звучит. Но это драфт для блога, а нужно письмо CEO. Или наоборот — formal one-pager надо превратить в casual newsletter intro. Менять смысл нельзя, менять регистр обязательно. Это работа для `tone-shifter`.

Скилл не переписывает идею. Он меняет:

- лексический регистр (formal verbs ↔ everyday verbs)
- длину и структуру предложений (subordinate clauses ↔ short stacks)
- степень hedging («it appears that» ↔ «is»)
- contraction policy (`do not` ↔ `don't`)
- jargon density (technical terms ↔ plain English)

И потом гонит результат через `writer` — стандартный antinyeyroslop pass.

## Intent — что значит «register»

Шесть фиксированных мишеней (см. `skills/tone-shifter/references/registers.md`):

- `business-formal` — quarterly report, board memo, legal-adjacent comms
- `business-casual` — internal Slack-but-written, weekly update, customer support email
- `academic` — journal article voice, hedged claims, citations expected
- `technical` — engineer-to-engineer, jargon allowed, terseness rewarded
- `friendly` — personal email, blog tone, contractions, one-syllable verbs
- `plain-explainer` — explain-it-like-I'm-12, no jargon, short sentences

`tone-shifter` не выбирает регистр сам. Ты говоришь `--to <register>`, скилл двигает в эту сторону.

## Setup

Скилл установлен из общего пакета. Работает на одном файле или на выделенном фрагменте через stdin.

## Step 1. Run with a target register

Базовый вызов:

```
/tone-shifter --to business-formal drafts/launch-announcement.md
```

Скилл читает файл, классифицирует current register (он считает baseline сам — обычно одно из шести), показывает delta перед тем как править:

```
Current register: business-casual (confidence 0.82)
Target register: business-formal
Deltas to apply:
  - contractions → expand (don't → do not, we're → we are)
  - hedge tightening (some users → certain users)
  - verb register (push out → release, ship → deliver)
  - sentence length: target avg 22 words (current 14)
  - banned for target: "tbh", "honestly", "kinda", "stuff"
```

На этом шаге можно отозвать одну из delta: `skip contractions` если ты хочешь сохранить разговорный голос внутри в остальном formal текста.

## Step 2. Review the diff

Скилл показывает unified diff, не сразу пишет в файл:

```diff
- We're stoked to announce that v3 is finally out the door.
+ We are pleased to announce that v3 is now generally available.

- The team pushed hard and honestly the result kinda blew us away.
+ The team executed against an aggressive timeline, and the result exceeded internal expectations.

- TL;DR: it's faster, cleaner, and a lot less buggy.
+ In summary, v3 delivers improved performance, a refined interface, and substantially fewer defects.
```

Ты решаешь: `apply`, `apply selective` (выбрать hunks), `discard`.

## Step 3. Apply, then writer-pass

После `apply` скилл прогоняет результат через `writer` (это автоматический финальный слой):

- antinyeyroslop regex — на случай если formal pass добавил «delve into», «navigate the complexities», «in today's fast-paced world»
- typography (smart quotes, em-dash policy)
- intensifier ladder («truly significant» → «significant»)

Это важно: formal pass любит навешивать AI-clichés. Writer-pass их сразу режет.

## Concrete before / after

Source (business-casual, draft):

```
Hey team — quick heads up. We're gonna pull the Friday deploy. There's a weird thing
happening with the auth service that nobody can repro consistently, but it scared
us enough to hit pause. We'll regroup Monday and figure out next steps. Sorry for
the late-Thursday vibes.
```

After `/tone-shifter --to business-formal`:

```
Team — a status update regarding the Friday deployment. We are postponing the
release. The authentication service is exhibiting intermittent behaviour that
has not been consistently reproduced, and the level of uncertainty warrants
holding the deploy. We will reconvene Monday to align on next steps. We
acknowledge the late notice and appreciate your flexibility.
```

After `/tone-shifter --to plain-explainer`:

```
We are not deploying on Friday. Something odd is happening with the login system.
We cannot reproduce it reliably, but it looks risky. We will meet Monday to decide
what to do next. Sorry for the late warning.
```

Same facts. Three registers. Different impact.

## Step 4. Multi-file mode

Для блока документов с одной целью регистра:

```
/tone-shifter --to academic --batch papers/draft-*.md
```

Скилл прогоняет каждый файл через тот же pipeline (classify → diff → apply → writer). На batch-режиме можно поставить `--auto-apply` чтобы пропустить ручное review каждого diff'а — но рекомендуется только если ты уже откалибровал режим на одном файле.

## Scenario 2 — Multi-stage shift (casual → academic → executive-summary)

Иногда нужен не один прыжок, а цепочка. Типичный случай: внутренняя записка написана в casual-стиле, нужна academic-версия для подачи в комитет, и **сразу же** короткий executive-summary для рассылки CEO. Один pass через `--to executive` обычно проваливается — слишком далеко от casual baseline, скилл теряет либо аргументацию, либо специфику.

Правильное решение — двухступенчатый shift:

```
/tone-shifter --to academic drafts/q3-notes.md          # ступень 1
/tone-shifter --to business-formal --scope summary --max-words 250 \
  outputs/q3-notes.academic.md                          # ступень 2
```

Что происходит:

1. **Ступень 1** (casual → academic). Текст приобретает hedging, vocabulary жёстче, sentence-length вырастает. Аргументация **формализуется**, факты остаются. Это база для дальнейшей работы.
2. **Ступень 2** (academic → executive). Скилл не пересказывает academic-версию заново — он экстрагирует claim-chain и сжимает до 250 слов. Получается короткий business-formal текст, но с уже отлитой логикой из ступени 1.

Когда какой подход уместен:

- **Один прыжок** работает, если delta-distance ≤ 1 register (`casual → business-casual`, `business-formal → academic`). Скилл уверенно движет по соседним позициям.
- **Многоступенчатый** нужен, если delta-distance ≥ 2 (`friendly → academic`, `plain-explainer → executive`). Прямой shift даёт «дешёвую формализацию» — лексика поменялась, структура нет.
- **Никогда** не делай 3+ ступени в один день на одном тексте. После третьего pass'а аргумент теряет связь с исходником, начинаются хуже-чем-AI-парафразы. Если нужно 3 разных регистра — сделай 3 параллельных one-step shift'а от source, не цепочку.

## Step N — Register matrix

Регистры — это не просто «формальнее/неформальнее». Это четыре параметра, которые меняются независимо. Матрица ниже — что двигается per dimension:

| Параметр / Регистр    | casual                          | neutral                            | business                                | academic                                |
|-----------------------|----------------------------------|------------------------------------|------------------------------------------|------------------------------------------|
| **Vocabulary**        | get, stuff, kinda, gonna, weird | use, things, somewhat, going to, unusual | utilise, items, considerably, intend to, atypical | employ, elements, substantially, anticipate, anomalous |
| **Sentence length**   | avg 8-12 слов, fragmenты ок      | avg 14-18 слов, простые сложные   | avg 20-26 слов, multiple subordinate    | avg 28-40 слов, parenthetical chains    |
| **Voice**             | active 95%, contractions всегда | active 80%, contractions иногда   | mixed 60/40, contractions только в diaologue | passive 50%+, no contractions          |
| **Cadence**           | stop-and-go, em-dashes, "—"     | прямая последовательность, "."     | semicolons, balanced clauses           | nested clauses, footnoted hedges        |

Скилл двигает все четыре параметра одновременно, не по отдельности. Если ты двинул только vocabulary (например через find/replace) — получится Frankenstein: формальные слова в short stop-and-go ритме. Читатель считает это сразу.

Override per dimension доступен через флаги:

```
/tone-shifter --to business --keep-cadence drafts/note.md
```

`--keep-cadence` оставит исходный ритм, поменяет только vocabulary + voice. Полезно когда «звучание» текста — это часть бренда (newsletter от founder'а, например).

## Edge case — Mixed registers в одном документе

Один документ часто требует **разных регистров в разных секциях**. Классический случай — CEO email с техническим аппендиксом: основное письмо в `business-formal`, аппендикс в `technical`. Прогнать один `--to business-formal` на весь файл — это убить технический раздел (превратить специфику в обтекаемость).

Решение — `--scope` маркеры. В исходнике размечаешь зоны:

```
<!-- tone:business-formal -->
Dear Board members,

Following our Q3 review, the leadership team has identified three operational
priorities that require capital reallocation in Q4...
<!-- /tone -->

<!-- tone:technical -->
## Appendix A — Database migration plan

We will execute a logical replication cutover from PG14 to PG16 on
2026-06-15 02:00 UTC. The slot lag SLO during cutover is < 200ms; we
will use `pg_logical_replication_slot` with `streaming=on` and
`synchronous_commit=remote_write`.
<!-- /tone -->
```

И запускаешь:

```
/tone-shifter --apply-markers drafts/board-email.md
```

Скилл движет каждую зону к своему target'у независимо. Это единственный безопасный способ — иначе ты либо потеряешь technical specificity, либо technical-стиль расползётся на CEO-обращение.

Без маркеров скилл считает baseline по first paragraph и применяет один target ко всему — что почти всегда дискредитирует одну из секций.

## Когда НЕ использовать tone-shifter

- **Просто почистить текст** — `writer clean`. Если регистр уже правильный, tone-shifter добавит лишнюю работу.
- **Переписать фрагмент художки** — `prose-edit`. Художественный голос — это не «register», это voice vector с десятками параметров.
- **Перевести между языками** — `tone-shifter` работает в пределах одного языка. Для cross-language см. `translation-sync` (read-only) или пиши заново на целевом языке.
- **Сменить argument** — скилл не меняет смысл. Если нужно «сделать утверждение менее категоричным», это hedge-shift, не tone-shift. Используй `--to academic`, который как побочный эффект hedge'ит.

## Troubleshooting

### Скилл не угадал current register

Передай вручную: `--from business-casual --to business-formal`. Без `--from` скилл классифицирует сам и иногда промахивается на коротких текстах (< 300 слов).

### После apply текст стал «звучать как робот»

Это типичная ловушка формального регистра. Запусти ещё один writer-pass в strict mode, и/или попроси: «после tone-shift убери все instances of `in conclusion`, `it is important to note`, `furthermore`». Скилл уважает custom bans поверх дефолтов.

### Хочу сохранить одну фразу как есть

Оберни её в `{{ keep: ... }}` — скилл уважает sentinel-маркеры. Полный список в `skills/tone-shifter/references/transformation-rules.md`.

### Diff слишком большой, нечитаем

Запусти `--scope paragraph` — скилл будет показывать diff по абзацам, ты accept'аешь по одному. Медленнее, но контролируемее.

### Shift был слишком агрессивный — потерян авторский голос

Самая болезненная ловушка. Признаки: текст formally correct, но звучит как written by committee. Узнаваемых оборотов автора нет, метафоры срезаны, ритм сглажен.

Причина: скилл по дефолту двигает все четыре параметра матрицы (vocabulary / sentence-length / voice / cadence). Если голос автора держится на cadence (пелевинские короткие фрагменты, мэнсоновские длинные сложноподчинённые), формальный shift его убьёт.

Лечение:

- Запусти ещё раз с `--keep-cadence` (сохраняет ритм исходника)
- Или `--keep-signature-phrases` (скилл идентифицирует 5-10 повторяющихся оборотов автора и оставляет их нетронутыми)
- Или откатись на `--scope paragraph` и accept'ай по одному абзацу — голос держится в 2-3 ключевых абзацах, остальные можно формализовать без потери

Иногда правильный ответ — **не делать shift**, а написать formal-версию с нуля. Если voice настолько силён, что без него текст теряет смысл — авто-shift не поможет.

### Shift получился косметическим — ничего не поменялось

Противоположная ловушка. Текст «прошёл pass», но читается так же, как был. Признаки: diff показывает 5-10 hunks, все они contractions (`don't → do not`), и больше ничего.

Причина: скилл классифицировал baseline слишком близко к target'у. Если baseline `business-casual` и target `business-formal` — delta-distance мала, скилл двигает только верхний слой (contractions + одно-два hedge-слова).

Лечение:

- Если действительно нужно сильное движение — задай через `--from friendly --to business-formal` (override classification, заставляет скилл считать baseline дальше)
- Или используй multi-stage (см. Scenario 2): casual → academic → business-formal. Двойной pass двигает агрессивнее, чем прямой прыжок.
- Если baseline уже близок к target'у — возможно, тебе не нужен tone-shifter. Может, нужен `writer clean` или structural rewrite.

### Register «съехал» к середине документа

В длинном документе (> 2000 слов) скилл иногда теряет target к концу. Первые 5 абзацев — `business-formal`, последние 5 — снова `business-casual`. Это известная проблема batch-mode на длинных файлах.

Лечение:

- Разбей файл на куски по 800-1200 слов и прогони каждый отдельно (`--scope file` per chunk)
- Или используй `--checkpoint-every 500-words` — скилл будет ре-классифицировать current state каждые 500 слов и корректировать
- Если документ структурирован (секции с заголовками) — добавь маркеры (см. Edge case выше) и прогони с `--apply-markers`. Маркеры заставляют скилл re-anchor на каждой секции.

## Related

- [pre-commit-hook.md](pre-commit-hook.md) — автоматизировать style-check после tone-shift'а
- [style-check-gate.md](style-check-gate.md) — verify, что shift не оставил AI-tells
- [microcopy-error-states.md](microcopy-error-states.md) — родственная задача, но для UX строк
- [skills/writer/SKILL.md](../../skills/writer/SKILL.md) — финальный слой, который гонится после tone-shift
