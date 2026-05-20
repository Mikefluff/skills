---
name: canon-check
description: "Verify story-bible consistency for the author's book series before editing or committing. Greps character names / artifacts / locations in changed chapters, cross-references against story-bible.tex per book, flags drift. Read-only — produces a structured drift report; never edits files or the bible. Use before opening a new chapter, before committing a chapter, or when introducing a character / artifact / location that may have been established elsewhere."
license: MIT
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

<objective>
Read-only story-bible auditor для книжной серии автора. Перед любой вставкой, рерайтом главы или коммитом — сверяет упоминания персонажей / артефактов / локаций в текущем тексте с зафиксированным каноном книги. Сигналит про дрейф. Не правит ни главу, ни bible.

**Why this skill exists.** Автор ломал канон три раза подряд, каждый раз ловил вручную, цена — переписывание сцены, иногда дважды:

1. **ЭА ch03** — перенёс встречу с Ирэн без учёта хвата из АБ гл. 21 (большой и указательный сверху, остальные три снизу).
2. **ЭА ch06** — перенёс яйцо-Квинту из кабинета Вэй Лина в «комнату Номы» и дал ему мужской род.
3. **НК-триптих** — написал врезку про «рыжую», не проверив, что она уже зафиксирована в `interlude10.tex` как **Татьяна Ларина / Ginger / Рыжая Ведьма** с развёрнутой биографией.

Плюс невыясненные несоответствия из cleanup-session (требуют решения автора):
- ch05 — число смехов Вэй Лина (bible: 2; текст: 1).
- ch13 — возраст времяхода Лии (bible: «семилетней»; текст: 10 лет 8 месяцев, шесть фаз).
- эпилог — возраст отца Дана (bible: 74; текст: 84).

Use cases:
- перед открытием новой главы — проверить, что устанавливаемые имена / артефакты / локации не дублируют установленные;
- перед `git commit` — staged diff vs канон;
- при упоминании знакомого персонажа в новой сцене — собрать все его прошлые появления + bible entry;
- read-only аудит самого bible (что упоминается в тексте, но не зафиксировано).

**Books the skill knows about:**
- `god-academy` (АБ) — художка, `books/god-academy/notes/story-bible.tex`, раздел «КАНОН АБ»
- `era-arkhitektorov` (ЭА) — художка, `books/era-arkhitektorov/notes/story-bible.tex`, раздел «КАНОН АБ: детали, которые нельзя переврать» + собственный канон ЭА
- `heavenly-code` (НК) — нон-фикшн, биографический канон в `~/.claude/projects/.../memory/user_biography*.md` + `books/heavenly-code/notes/story-bible.tex` (раздел «КАНОН АВТОБИОГРАФИИ»)
</objective>

<instructions>

## ROLE

Story-bible auditor. **NOT continuity editor.** Скилл только сигналит про расхождения между:
- (a) текущим черновиком,
- (b) story-bible,
- (c) другими опубликованными главами той же книги.

Решает автор. Скилл не правит ни главу, ни bible.

## CORE PRINCIPLE — TRUST THE TEXT, NOT MEMORY

Когда находится противоречие между «что говорит текущая глава», «что говорит bible» и «что „помнит“ модель» — приоритет разрешения:

1. **Опубликованные главы той же книги** = ground truth. Всё, что зафиксировано в `books/<book>/ru/chapters/*.tex` — это канон, даже если bible молчит.
2. **Story-bible.tex** = следующий уровень канона. Если глава и bible расходятся — это материал для решения автором, не для автоправки.
3. **Память / утверждения о прошлом тексте** = НАИМЕНЕЕ доверенный источник. Если «помнишь», что было иначе, — ты ошибаешься. Грепни и перечитай.

Никогда не цитируй прошлый текст по памяти. Всегда `grep` + `Read` перед утверждением «в гл.~X было Y».

## ROUTING

Скилл определяет, какой bible применить, по пути файла. Полная таблица — в [references/routing.md](references/routing.md). Кратко:

```
books/god-academy/{ru,en,pt-br}/chapters/*.tex       → books/god-academy/notes/story-bible.tex
books/era-arkhitektorov/{ru,en,pt-br}/chapters/*.tex → books/era-arkhitektorov/notes/story-bible.tex
books/heavenly-code/{ru,en,pt-br}/chapters/*.tex     → ~/.claude/.../memory/user_biography*.md
                                                     + books/heavenly-code/notes/story-bible.tex
любой другой путь                                    → SKIP (тихо)
```

## MODES

### `chapter <book> <chN>` — полный канон-скан главы

```bash
# Пример:
canon-check chapter god-academy ch07
# → scans books/god-academy/ru/chapters/ch07.tex
#   (плюс en/ch07.tex и pt-br/ch07.tex если есть — но bible один)
```

Полный пасс по файлу: извлечь сущности → сверить с bible → собрать другие появления.

### `staged` — staged diff

```bash
git diff --cached --name-only
# для каждого .tex в books/<known>/{ru,en,pt-br}/chapters/ — pass по добавленным/изменённым строкам
```

### `entity <book> <name>` — все появления сущности

```bash
canon-check entity era-arkhitektorov "Ирэн"
# → bible entry + список всех файлов и строк, где появляется
```

Полезно перед написанием новой сцены с уже установленным персонажем.

### `audit-bible <book>` — структурный аудит bible

Найти сущности, которые упоминаются в `chapters/*.tex` ≥ N раз, но не имеют записи в bible (WARNING — «silent canon»). Не правит bible — только список.

## PIPELINE (краткая версия; полная — в [references/workflow.md](references/workflow.md))

**Шаг 1. Извлечь сущности из проверяемого текста.**
- **Персонажи:** capitalized слова (русские/латиница) + сверка с списком установленных имён из bible (`\subsection{Имена...}`, `\section{ГЛАВНЫЕ ПЕРСОНАЖИ}`, `\section{ВТОРОСТЕПЕННЫЕ ПЕРСОНАЖИ}`).
- **Артефакты:** словарь из bible (Квинта, яйцо, посох, PDF, трость, Nokia, феназепам, …) — каждая книга имеет свой словарь, см. `\subsection{Физические инварианты}`.
- **Локации:** топонимы из bible (`\subsection{Локации}` / `\subsection{Локации с весом}`).

**Шаг 2. Для каждой сущности — собрать контекст.**

```bash
# bible entry:
grep -n -A 5 "<entity>" books/<book>/notes/story-bible.tex

# другие появления в главах:
grep -rn "<entity>" books/<book>/ru/chapters/
```

Прочитать всё. Не цитировать по памяти.

**Шаг 3. Сравнить с текущим текстом.**

Искать противоречия:
- атрибут (возраст, профессия, локация, цвет) расходится с bible или с другой главой
- жест / физический инвариант (хват, лаг, число) изменён
- цитата-якорь перефразирована
- артефакт сменил локацию / владельца / род
- персонаж появился без имени, хотя в bible уже зафиксирован под именем

**Шаг 4. Если новая сущность — flag for author.**

Если в тексте появляется явная новая сущность (имя собственное, артефакт), которой нет в bible — **WARNING, не auto-add**. Скилл не правит bible. Решает автор: канонизировать или вычистить.

Полный список known incidents и pattern detection — в [references/known-incidents.md](references/known-incidents.md).

## SEVERITY LEVELS

- **BLOCKING** — текст явно противоречит конкретной записи в bible (пример: bible «Ирэн правша, хват большой+указательный сверху»; текст «взяла левой рукой»). Или: текст противоречит другой опубликованной главе той же книги.
- **WARNING (silent canon)** — сущность фигурирует в тексте ≥ 2 раз (в этой или других главах), но не имеет записи в bible. Должна быть добавлена.
- **WARNING (cross-chapter drift)** — bible молчит, но две главы дают разные атрибуты сущности.
- **INFO (canon expansion)** — введена новая деталь о уже зафиксированной сущности (не противоречие — расширение). Опционально добавить в bible.

## EXIT CODE (если запущен как pre-commit hook)

- `0` — только INFO. Можно коммитить.
- `1` — WARNING (silent canon / cross-chapter drift). Спросить автора.
- `2` — BLOCKING (явное противоречие). Прервать коммит.

В обычном вызове exit code не используется — только отчёт.

## INTEGRATION

Скилл сам не ставит hook. Если автор попросит — стандартный паттерн от style-check: `.git/hooks/pre-commit` вызывает враппер Claude Code с `/canon-check staged`. Скилл не редактирует `.git/hooks/` сам.

## OUTPUT FORMAT

Структурированный отчёт с тремя секциями (по severity) + SUMMARY с покрытием bible. Эталон — в [examples/sample-report.md](examples/sample-report.md).

## WHAT NOT TO DO

- **Не правит главы.** Только сигналит. Правки — через `prose-edit` или вручную автором.
- **Не правит story-bible.** Bible обновляет автор, после решения, какая версия канонична.
- **Не доверяет собственной памяти** о прошлых главах — всегда `grep` + `Read`. Если «помнишь» иначе, чем сказано в тексте — текст победил.
- **Не auto-canonize.** Новая сущность → WARNING для автора, не молчаливая запись в bible.
- **Не запускает sub-agents.** Read-only, всё через Read + Grep + Bash.
- **Не лезет в код.** `.py`, `.js`, `.ts`, `.go` — skip.
- **Не запускается в `/loop` или `/schedule`.** Это интерактивный аудит, а не cron.

</instructions>

## REFERENCES (load on demand)

| File | When to load |
| --- | --- |
| [references/workflow.md](references/workflow.md) | Нужны точные grep-команды для извлечения сущностей и сверки канона. 3-шаговый протокол с примерами. |
| [references/bible-format.md](references/bible-format.md) | Нужна структура `story-bible.tex` — какие разделы существуют, куда автор добавит новые записи. |
| [references/known-incidents.md](references/known-incidents.md) | Нужна калибровка по реальным канон-поломкам автора (хват Ирэн, яйцо-Квинта, рыжая ведьма + cleanup-session). |
| [references/routing.md](references/routing.md) | Решаешь, какой bible применить к конкретному пути. |
| [examples/sample-report.md](examples/sample-report.md) | Нужна калибровка тона/детализации отчёта. |
