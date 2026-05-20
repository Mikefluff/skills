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

Шесть фиксированных мишеней (см. `tone-shifter/references/registers.md`):

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

Оберни её в `{{ keep: ... }}` — скилл уважает sentinel-маркеры. Полный список в `tone-shifter/references/markers.md`.

### Diff слишком большой, нечитаем

Запусти `--scope paragraph` — скилл будет показывать diff по абзацам, ты accept'аешь по одному. Медленнее, но контролируемее.

## Related

- [pre-commit-hook.md](pre-commit-hook.md) — автоматизировать style-check после tone-shift'а
- [style-check-gate.md](style-check-gate.md) — verify, что shift не оставил AI-tells
- [microcopy-error-states.md](microcopy-error-states.md) — родственная задача, но для UX строк
- [writer/SKILL.md](../../writer/SKILL.md) — финальный слой, который гонится после tone-shift
