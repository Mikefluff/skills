---
name: prose-edit
description: "Fiction-prose rewrite + style pass. Wraps `writer`; adds voice vector (Pelevin/Manson — not impersonation), no-business-editing rules, artistic rewrite over compression, 5-trigger structural-synthesis detector, depth-pass checklist. Use when rewriting a fiction chapter / scene / passage. Pairs with `canon-check`."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Fiction style pass on top of `writer`. Works on any text file (markdown, LaTeX, plain text) — no assumed project layout or file extension.

The skill does NOT write a chapter from scratch. It:
- rewrites an existing fragment per fiction voice rules
- catches what the generic `writer` pass misses (fiction-specific synthetic-prose patterns layered on top of universal ones)
- defers story-bible consistency to the separate `canon-check` skill (compose them — see [docs/COMPOSING.md](../docs/COMPOSING.md))
</objective>

<instructions>

## DEPENDENCY ON `writer`

Все базовые правила (антинейрослоп regex 20 категорий, типографика, стаккато/отрицания/обрубки/инверсии/повторы, кальки) уже живут в `writer/SKILL.md`. Этот скилл их НЕ дублирует — он применяет их через `writer` 4-layer pass плюс добавляет художественный слой поверх.

При работе с фрагментом всегда заканчивай writer pass'ом до выдачи.

## CRITICAL — что НЕ переносить из бизнес-редактирования

Художественная проза живёт по другим правилам. Не применять к ней:

- **filler trim** — повторы и «лишние» слова часто работают как ритм/голос
- **восклицания** — характерные для автора, не убирать
- **неполные предложения** — могут быть художественным приёмом (НО! не путать с нейрослоп-стаккато: 3+ односоставных подряд по чужому шаблону — это всё равно правится через writer)
- **сжатие диалога** — реплики персонажей имеют свою длину и ритм
- **«улучшение» метафор** в сторону «правильности» — авторская образность важнее формальной чистоты

Если конфликт между правилом writer и художественной целесообразностью — оставляй авторский вариант и помечай в сводке.

## Voice references (краткое резюме)

Ориентир — Пелевин + приёмы Мэнсона как вектор, не подражание. Перед правкой прогонять 10-пунктовый style drift checklist (штампы / пафос / проповеди / Netflix-моменты / резонёрство / морализаторство / гладкость / самоповтор / объяснительность / псевдоумность).

Полный список и пояснения — [references/voice.md](references/voice.md).

## Canon check + meta-references + anglicisms (краткое резюме)

В голосе рассказчика запрещены meta-ссылки на свои же книги/главы и латиница/IT-слэнг (в прямой речи персонажей допустимо). Story-bible consistency — задача отдельного скилла `canon-check`; этот скилл его не дублирует.

Полный протокол и исключения для meta-refs / anglicisms — [references/canon-check.md](references/canon-check.md).

## Rewrite principles (краткое резюме)

Структурную синтетику (стаккато/отрицания/обрубки) в авторском голосе чинить ДЛИННЫМ рерайтом — сложноподчинённая фраза с конкретным образом, а НЕ заменой точек на запятые. Сверху — self-implication caveats, «flat statement → разворот» ToV pattern, лимит 3-5 сравнений на главу и 5-триггерный Structural Synthesis Detector.

Полные правила, примеры «БЫЛО / ПЛОХО / НАДО» и список архитектурных триггеров — [references/rewrite-principles.md](references/rewrite-principles.md).

## Prose cleanness checklist (краткое резюме)

10 пунктов pre-commit шероховатостей: опечатки в датах/числах, согласования, антецеденты, метафора-смысл, тавтологии «корень в корне», бессмысленные сравнения, повтор слова 3×, кальки, русский порядок слов, цельность реплик. Перечитывать вслух весь изменённый фрагмент.

Полный чек-лист — [references/cleanness-checklist.md](references/cleanness-checklist.md).

## Rewrite pitfalls (краткое резюме)

Типовые ловушки литературного рерайта: тавтологии корень-в-корне, бессмысленные сравнения, повтор слова 3×, подмена голоса на «гладче», перевод метафоры в буквальность, объяснение шутки. После рерайта читать вслух.

Полный разбор ловушек — [references/pitfalls.md](references/pitfalls.md).

## No synthetic AI-words (краткое резюме)

«Рамка / нарратив / дискурс / парадигма / концепт / оптика (как метафора)» — чистить даже если стояло в оригинале. Замены живут отдельной картой.

Полная карта замен — [references/synthetic-ai-words.md](references/synthetic-ai-words.md).

## MODES OF OPERATION

### `rewrite <file> <lines>` — точечный рерайт фрагмента
Пользователь указывает файл и диапазон строк. Скилл:
1. Читает контекст (вся глава/окружающие абзацы, не только указанный фрагмент)
2. Применяет writer pass + художественный слой
3. Возвращает diff с правками + короткую сводку («исправлено: стаккато ×2, нейрослоп ×1, тавтология ×1»)
4. НЕ коммитит — это решает автор. Для canon-check вызвать одноимённый скилл отдельно.

### `chapter <file>` — проход по главе целиком
1. Читает всю главу
2. Прогоняет writer 4-layer pass + художественный слой
3. Выдаёт пронумерованный список предлагаемых правок (строка → старое → новое → почему)
4. НЕ редактирует напрямую — автор смотрит список и решает

### `lint <file>` — read-only проверка
Только список нарушений с локациями, никаких правок. Полезно перед коммитом.

```
ch07.md:142 — STACCATO (3+ односоставных подряд)
ch07.md:201 — TAVTOLOGY («открытое открытие»)
ch07.md:289 — META-REF («как в главе 4 первой книги»)
ch07.md:312 — ANGLICISM в авторском голосе («post-door»)
```

### `diff-check <commit>` — пасс по последнему коммиту
Берёт diff последнего коммита (или указанного range), прогоняет lint только на добавленные строки. Полезно как pre-commit hook.

## OUTPUT FORMAT

Для `rewrite` и `chapter` режимов — выдача в формате:

```
[FILE:line] [CATEGORY]
- БЫЛО: <цитата>
- НАДО: <предложение>
- ПОЧЕМУ: <короткое объяснение, не больше одной строки>
```

Для `lint` и `diff-check` — только сводка без предложений правок (если автор не попросил).

В конце — общая сводка:
```
Прогон: Layer 1 — N1 hits, Layer 2 — N2 violations, художественный слой — N3 hits.
Голос: drift низкий/средний/высокий.
```

(Для story-bible consistency — отдельный пасс через `canon-check`.)

## WHAT NOT TO DO

- **Не использовать Agent / sub-agents** для текста книги. Sub-agent'ы на слабых моделях пишут мусор. Все правки — самостоятельно, в foreground. Агенты допустимы только для git/grep/build, не для содержательной работы с прозой.
- **Не коммитить за автора.** Скилл предлагает — автор решает.
- **Не «улучшать» работающую шероховатость.** Если фрагмент звучит странно, но в этом голос автора — оставить.
- **Не применять виральные правила.** Никаких numbered points, hook'ов, CTA, NLP-вопросов в художке.
- **Не переводить художку.** Если файл в RU — работаем в русском. Multi-language parity — задача `translation-sync`, не этого скилла.

</instructions>

## REFERENCES (load on demand)

| File | When to load |
|------|--------------|
| [references/voice.md](references/voice.md) | Перед любым художественным пассом — сверить вектор голоса и 10-пунктовый style drift checklist. |
| [references/canon-check.md](references/canon-check.md) | Когда автор использует meta-ссылки на свои же книги/главы или вставляет латиницу/IT-слэнг в голос рассказчика. (Story-bible consistency — отдельный скилл `canon-check`.) |
| [references/rewrite-principles.md](references/rewrite-principles.md) | Когда нужно переписать структурную синтетику (стаккато/отрицания/тире-цепочки) — длинный артистический рерайт, ToV, Structural Synthesis Detector. |
| [references/cleanness-checklist.md](references/cleanness-checklist.md) | Перед коммитом — 10-пунктовый прогон по pre-commit шероховатостям. |
| [references/pitfalls.md](references/pitfalls.md) | После рерайта — проверить, не свалился ли результат в типовую ловушку. |
| [references/synthetic-ai-words.md](references/synthetic-ai-words.md) | При встрече «рамка / нарратив / дискурс / парадигма / концепт / оптика» — карта замен. |
| [references/depth-pass.md](references/depth-pass.md) | 10-пунктный Postirony depth-pass checklist + IT-blog test для отличия художки от статьи. |
| [examples/before-after.md](examples/before-after.md) | Калибровка: образцы БЫЛО/НАДО для staccato, double negation, длинного рерайта, ToV pattern, тавтологии, comparison overload. |
