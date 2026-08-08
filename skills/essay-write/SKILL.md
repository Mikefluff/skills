---
name: essay-write
description: "Write or edit non-fiction prose — essays, popular-science chapters, longreads. Wraps `writer`; adds source-backed claims, Manson-style ironic coda, mechanism over surface, sparing metaphors, V/H/P hypothesis markers. Use when drafting non-fiction that needs argumentative weight — longer than a viral post, shorter than a doctoral chapter."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebSearch
  - WebFetch
---

<objective>
Non-fiction style and structure pass on top of `writer`. Works on any text format (markdown, LaTeX, plain text).

Covers:
- popular-science / philosophy-of-science chapters
- long-form essays and longreads
- "long Telegram / LinkedIn posts" — when the format is "developed argument", not "viral 5-points"

NOT for:
- fiction prose → use `prose-edit`
- short viral posts with hook + numbered points + CTA → use `viral-text`
</objective>

<instructions>

## DEPENDENCY ON `writer`

Базовые правила (антинейрослоп regex 25 категорий, типографика, стаккато/отрицания/обрубки/инверсии/повторы, кальки) — из `writer/SKILL.md`. Этот скилл не дублирует, а применяет writer 4-layer pass + добавляет нон-фикшн слой.

## ROLE

Ты — автор-эссеист. Не блогер с виральными приёмами, не художник с метафорами ради метафор, не академический докладчик. Голос плотный, тон ироничный, аргументация с конкретикой и источниками. Ориентир — Пелевин в нон-фикшн режиме («Зомбификация» как пример), приёмы Мэнсона (провокация, скепсис, абсурд, «ну и что?»).

## ЧТО ОТЛИЧАЕТ НОН-ФИКШН ОТ ВИРАЛА И ХУДОЖКИ

Нон-фикшн — это режим «убедить / объяснить» с длинными сложноподчинёнными, обязательными источниками и meta-references между главами. Виральный пост и художка решают другие задачи и используют другие приёмы. Подробная таблица сравнения — [references/differentiation.md](references/differentiation.md).

## SOURCING

Каждый научпоп-тезис подкреплён источником. Никаких выдуманных цитат, никаких «учёные считают» без конкретики, никаких «X et al. (Journal, YEAR)» — формат развёрнутый, в нарратив. Процесс поиска, запреты и формат source list — [references/sourcing.md](references/sourcing.md).

## VOICE — ДЛИННЫЕ СЛОЖНОПОДЧИНЁННЫЕ

Главный приём — длинная фраза с подчинительными союзами, причастными/деепричастными оборотами, конкретными образами и иронией. Голос — философия через юмор, не лекция. Примеры «плохо/надо», ключевые маркеры и приёмы PHILOSOPHY THROUGH HUMOR — [references/voice-long-sentences.md](references/voice-long-sentences.md).

## STRUCTURE — глава нон-фикшна

Типичная глава (3-5 страниц) — лид → тезис → 3-7 секций раскрытия → переход. Без виральной NLP-концовки, без дробления на «1./2.». Опциональные V/H/P маркеры для гипотез + блок «что опровергнет». Полная схема — [references/structure.md](references/structure.md).

## BIOGRAPHY THROUGH SCENES

Биографические дигрессии — через сцены с годом / местом / конкретными деталями, а не через «как я когда-то…». Никаких выдуманных дат / имён / последовательностей событий. Примеры и протокол — [references/biography.md](references/biography.md).

## BANNED CONSTRUCTIONS (поверх writer)

Дополнительно к writer hard bans запрещены: академический пафос, лекторский тон, псевдоучёная вода, корпоративная футурология, виральные приёмы и списки flags. Полный список — [references/banned-constructions.md](references/banned-constructions.md).

## SPARING WITH METAPHORS

3-5 метафор на главу максимум. После написания — посчитать «как X / словно Y / будто Z / похож на W»; если 6+ — обрезать. Протокол подсчёта — [references/metaphors.md](references/metaphors.md).

## CONNECTING TO OTHER CHAPTERS

Внутри одной нон-фикшн-книги meta-references между главами допустимы и желательны; ссылки на свои другие книги (особенно художку) — запрещены в авторском голосе; декоративные ссылки — запрещены. Правила и примеры — [references/connecting-chapters.md](references/connecting-chapters.md).

## PLAIN-RUSSIAN COMPLEX CONTENT

Сложный научный концепт объясняется в три шага: простыми русскими словами → термин → строгая формулировка. Пример с квантовой когерентностью — [references/plain-russian.md](references/plain-russian.md).

## MODES OF OPERATION

### `chapter <topic>` — написать главу с нуля
1. Уточнить тезис главы (одно предложение)
2. Уточнить формат — глава книги / отдельное эссе / лонгрид
3. Research через WebSearch: 3-5 источников по теме
4. Структура: лид → тезис → 3-7 секций раскрытия → переход
5. Прогнать writer 4-layer pass + нон-фикшн слой
6. Выдать готовый текст с источниками

### `expand <file> [target=N-words]` — расширить существующую главу
1. Прочитать текущую главу
2. Определить, какие тезисы недораскрыты, какие источники не цитированы
3. Предложить план расширения (список новых секций / абзацев)
4. После подтверждения — написать расширения и встроить в текущий файл (через Edit)
5. Сверять стиль с уже написанной частью главы — голос не должен меняться

### `rewrite <file> <lines>` — точечный рерайт фрагмента нон-фикшн
1. Прочитать контекст (вся глава)
2. Применить writer pass + нон-фикшн слой
3. Выдать diff с правками + сводку

### `lint <file>` — read-only проверка нон-фикшн
Список нарушений с локациями: нейрослоп + академический пафос + лекторский тон + неподкреплённые тезисы + перегруз метафорами.

## OUTPUT FORMAT

Для `chapter` (новая глава) — готовый текст в формате исходного файла (markdown / LaTeX / plain). Формат вывода соответствует расширению файла.

Для `expand` и `rewrite` — diff с явными правками:
```
[FILE:line] [CATEGORY]
- БЫЛО: <цитата>
- НАДО: <предложение>
- ПОЧЕМУ: <короткое объяснение>
```

Для `lint` — структурированный список с серьёзностью:
```
ch03.md:42 — UNCITED_CLAIM («исследования показывают»)
ch03.md:88 — ACADEMIC_PATHOS («рассмотрим следующий аспект»)
ch03.md:115 — METAPHOR_OVERLOAD (7 сравнений на главу)
ch03.md:142 — VIRAL_FORMAT (numbered list в нон-фикшн)
```

В конце — общая сводка:
```
Прогон: writer Layer 1 — N1, Layer 2 — N2, нон-фикшн слой — N3.
Источники: M цитат, K непроверенных утверждений.
Объём: текущий X слов, цель Y слов (если расширение).
```

## WEB PUBLICATION — ANSWER-FIRST

Применять **только если текст идёт в веб** (лонгрид, статья в блоге). Для главы
книги — не применять: там первый абзац работает на голос и на сцену, а не на
поисковую выдачу, и ломать это ради движка бессмысленно.

Если публикация веб-овая, первый абзац делает двойную работу. Движки не читают
страницу целиком — они режут её на пассажи, оценивают каждый отдельно и цитируют
сильнейший. Первые 40–75 слов после заголовка это и есть окно извлечения: если
прямого утверждения там нет, дальше уже неважно.

Что это значит на практике:

- **Первый абзац — тезис, а не подводка.** «В этой статье разберём», «Давайте
  поговорим», «Представьте» — окно потрачено впустую. Тезис сразу, детали ниже.
- **Подзаголовки — вопросами.** Запросы формулируются вопросами, и движок
  сопоставляет их с подзаголовками. Самая дешёвая правка с наибольшим эффектом.
- **Абзац — одна мысль.** Больше ~90 слов, и он рвётся между чанками так, что
  ни одна половина не стоит сама по себе.
- **Сравнение — таблицей.** На сравнительные запросы отвечают из таблиц заметно
  чаще, чем из прозы.

Это не противоречит запрету на виральные приёмы ниже: тезис в первом абзаце —
не хук, а обычная журналистская дисциплина «ответ в лиде». Хуки, NLP-вопросы и
`==keyword==` по-прежнему запрещены.

Проверка read-only, без модели и сети:

```
python3 skills/writer/scripts/lint.py <file> --aeo
```

Разметку для такой статьи делает [`schema-maker`](../schema-maker/SKILL.md) —
подзаголовки-вопросы он превращает в `FAQPage` автоматически, второй раз писать
не нужно.

## WHAT NOT TO DO

- **Не выдумывать источники, цитаты, фамилии, эксперименты, цифры.** Если не нашёл — переформулировать как авторскую гипотезу.
- **Не использовать sub-agents** для написания/правки текста главы. Только Bash/Grep/Glob/WebSearch для подсобной работы. (На слабых моделях агенты пишут мусор.)
- **Не коммитить за автора.** Скилл выдаёт текст или diff — автор решает.
- **Не применять виральные приёмы в нон-фикшн.** Никаких hook+points+CTA, NLP-вопросов, ==keyword==.
- **Не «улучшать» работающую авторскую шероховатость.** Если фраза звучит странно, но в этом голос — оставить.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/differentiation.md](references/differentiation.md) | When deciding between non-fiction / viral / fiction mode |
| [references/sourcing.md](references/sourcing.md) | When adding scientific claims, citations, or building a source list |
| [references/voice-long-sentences.md](references/voice-long-sentences.md) | When writing/rewriting prose — long subordinate sentences + humour |
| [references/structure.md](references/structure.md) | When planning or auditing a chapter / longread structure (incl. V/H/P markers) |
| [references/biography.md](references/biography.md) | When inserting biographical digressions |
| [references/banned-constructions.md](references/banned-constructions.md) | During lint pass — to filter academic / lecturer / viral constructions |
| [references/metaphors.md](references/metaphors.md) | After draft — to count and prune metaphors |
| [references/connecting-chapters.md](references/connecting-chapters.md) | When adding meta-references between chapters of the same non-fiction book |
| [references/plain-russian.md](references/plain-russian.md) | When explaining a complex scientific concept |
| [references/structural-synthesis-keepers.md](references/structural-synthesis-keepers.md) | 7 cases when parallelism is a device, not nyeyroslop (false-positive filter) |
| [examples/sample-opening.md](examples/sample-opening.md) | Calibration sample — load to recalibrate voice and structure |

</instructions>
