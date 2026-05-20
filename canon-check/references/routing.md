# ROUTING — какой canon-источник применить

По пути проверяемого файла:

```
books/god-academy/{ru,en,pt-br}/chapters/*.tex
    → books/god-academy/notes/story-bible.tex

books/era-arkhitektorov/{ru,en,pt-br}/chapters/*.tex
    → books/era-arkhitektorov/notes/story-bible.tex
    + books/god-academy/notes/story-bible.tex
      (раздел «КАНОН АБ» — для проверки наследия)

books/heavenly-code/{ru,en,pt-br}/chapters/*.tex
    → books/heavenly-code/notes/story-bible.tex
    + ~/.claude/projects/-Users-mikefluff-Documents-godacademy/memory/user_biography*.md
      (биографический канон, includes user_biography_kesha.md, user_biography_mogwai.md)

books/*/notes/*.tex
books/*/notes/*.md
    → SKIP (это сами bibles и заметки — не главы)

любой другой путь
    → SKIP тихо
```

---

## Почему ЭА читает оба bible

ЭА — прямой сиквел АБ. Раздел `КАНОН АБ` в bible АБ описывает то, что **нельзя ретропроецировать в АБ из ЭА**. Но это же — каркас, который ЭА **обязана соблюсти**: хват Ирэн, цитаты-якоря, имена-возрасты ключевых персонажей.

Конкретно — детали, которые ЭА **наследует** от АБ:

- Хват матери (большой+указательный сверху)
- Дан-лаг 900 мс
- Возрасты: Дан 28 на сентябрь 2026 — отсчёт от этой точки
- Цитаты-якоря: «Я знаю.» (два слова отца), «Один. Целый. Черновик.» (финал АБ)
- Локации: Шаболовка, Хамовники (для АБ), Нескучный сад, Баррикадная
- Безымянный PDF (нельзя называть Михаила Савченко в художке)

Детали, которые **в ЭА изменились** и это новый канон:

- Яйцо получило имя **Квинта**
- Вэй Лин переехал из Хамовников в Академию
- Появилась трость, Nokia (ЭА-канон, не ретропроецировать в АБ)

При канон-чеке ЭА главы — оба bible открываются, оба читаются. При канон-чеке АБ главы — только bible АБ.

---

## Почему НК читает и bible, и memory

НК — нон-фикшн. «Канон» здесь — биография автора, а не выдуманная вселенная. Биография фрагментарно зафиксирована в:

1. `books/heavenly-code/notes/story-bible.tex` — структурированный канон (хронология, жёны/дети, локации с весом)
2. `~/.claude/.../memory/user_biography.md` — основной биографический файл
3. `user_biography_details.md` — углублённые детали
4. `user_biography_kesha.md`, `user_biography_mogwai.md` — отдельные арки (мемуарные)

Между ними иногда есть расхождения. **Правило:** при противоречии bible vs memory — спросить автора, не угадывать. memory может быть устаревшей; bible может быть неполной.

---

## Edge cases

- **Файл в `arcs/` / `lore/` / `inserts/` / `dialogs/`** — это вставки в художку. Если из контекста ясно, в какую книгу — применить bible этой книги. Если непонятно — SKIP с предупреждением.
- **Файл в `preprints/`** — научные тексты, канон-чек не нужен. SKIP.
- **Главы вне `ru/`** (`en/`, `pt-br/`) — это переводы. Канон тот же, что у RU-оригинала. Канон-чек применим, но **физические инварианты + цитаты-якоря** проверяются ещё строже: переводчик не должен сглаживать конкретику.
- **Код (`.py`, `.js`, `.ts`, etc.)** — SKIP молча.

---

## Кратко в одной таблице

| Path pattern | Bible | Доп. источники |
| --- | --- | --- |
| `books/god-academy/{ru,en,pt-br}/chapters/*.tex` | `god-academy/notes/story-bible.tex` | — |
| `books/era-arkhitektorov/{ru,en,pt-br}/chapters/*.tex` | `era-arkhitektorov/notes/story-bible.tex` | + АБ bible (наследие) |
| `books/heavenly-code/{ru,en,pt-br}/chapters/*.tex` | `heavenly-code/notes/story-bible.tex` | + `memory/user_biography*.md` |
| `books/*/notes/*` | — (это и есть bible) | SKIP |
| `preprints/**`, code files, `.gitignore`, … | — | SKIP молча |
