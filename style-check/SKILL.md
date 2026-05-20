---
name: style-check
description: "Read-only pre-commit lint поверх writer/prose-edit/essay-write. Берёт staged diff (или указанный файл / range коммитов) и сигналит про нейрослоп, синтетику, нарушения голоса. Не правит — только показывает. Использовать перед `git commit` или как pre-commit hook."
license: MIT
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

<objective>
Универсальный read-only линтер по стилистическим правилам автора. Не пишет, не правит, не коммитит — только проверяет.

Use cases:
- перед `git commit` — проверить staged изменения на нейрослоп
- post-commit — проверить последний коммит
- ручной запуск на файле / диапазоне строк
- pre-commit hook (если автор добавит его в `.git/hooks/pre-commit`)

Скилл сам определяет, какой набор правил применить (writer / prose-edit / essay-write) по пути файла:
- `books/{god-academy,era-arkhitektorov}/*/chapters/` → художка (prose-edit)
- `books/heavenly-code/*/chapters/` → нон-фикшн (essay-write)
- `preprints/`, `*.md`, `*.tex` вне `books/` → базовый writer
- любое другое — базовый writer
</objective>

<instructions>

## DEPENDENCY

Этот скилл использует правила из:
- `writer/SKILL.md` — базовый антинейрослоп (20 категорий) + структурная синтетика
- `prose-edit/SKILL.md` — художественный слой для АБ/ЭА
- `essay-write/SKILL.md` — нон-фикшн слой для НК/эссе

Скилл НЕ пишет и НЕ правит. Только читает файлы, прогоняет правила и возвращает структурированный отчёт.

## ROUTING

Скилл определяет набор правил по пути файла (художка → writer+prose-edit, нон-фикшн НК → writer+essay-write, всё остальное → writer; код пропускается). Полная таблица маршрутизации, edge cases и список расширений-исключений — в [references/routing.md](references/routing.md).

## MODES

### `staged` (default) — проверить staged изменения
```bash
git diff --cached --name-only
```
Для каждого staged файла:
1. Если двоичный или код — пропустить
2. Получить добавленные/изменённые строки: `git diff --cached -U0 <file>`
3. Применить соответствующий набор правил (по routing)
4. Выдать отчёт

### `last` — проверить последний коммит
```bash
git diff HEAD~1 HEAD --name-only
```
Аналогично, но на последнем коммите.

### `range <from>..<to>` — проверить диапазон коммитов
```bash
git diff <from>..<to> --name-only
```

### `file <path>` — проверить весь файл целиком
Не diff, а полный пасс по файлу. Полезно для проверки старых файлов.

### `file <path> <line1>:<line2>` — проверить диапазон строк
Полный пасс по указанному фрагменту.

## OUTPUT FORMAT

Структурированный отчёт по файлам с группировкой нарушений (L<line> CATEGORY «цитата» → правило/совет), плюс блок `=== SUMMARY ===` со счётчиками по слоям и разбивкой по severity. Полный пример отчёта-эталона — в [references/output-format.md](references/output-format.md), отдельный калибровочный артефакт — в [examples/sample-report.md](examples/sample-report.md).

## SEVERITY LEVELS

Три уровня: **BLOCKING** (canon drift, uncited claim, fabricated source, broken latex), **WARNING** (нейрослоп ≥2 совпадения, staccato/inversion/double-neg, tavtology/meta-ref/anglicism, academic pathos, viral format), **INFO** (1-совпадение L1, metaphor overload, style drift). Полный список категорий по уровням — в [references/severity.md](references/severity.md).

## EXIT CODE (если запущен как pre-commit hook)

При использовании в качестве git hook'а:
- `0` — только INFO, можно коммитить
- `1` — есть WARNING, спросить автора (или показать и продолжить — зависит от настройки)
- `2` — есть BLOCKING, прервать коммит

В обычном вызове (не hook) — exit code не используется, только отчёт.

## INTEGRATION

Скилл сам не ставит хук. Если автор попросит — выдать инструкцию по установке `.git/hooks/pre-commit`-враппера. Готовый bash-снипет и шаги установки — в [references/pre-commit-hook.md](references/pre-commit-hook.md).

## WHAT NOT TO DO

- **Не правит файлы.** Только читает и сигналит. Для правки — `writer`/`prose-edit`/`essay-write`.
- **Не запускает sub-agents.** Это легковесный read-only скилл, всё делается напрямую через Read+Grep+Bash.
- **Не выдумывает источники для проверки фабрикации.** Просто помечает подозрительные ссылки как `UNVERIFIED_SOURCE`, проверка — на авторе.
- **Не блокирует коммит автоматически без exit code.** Если запущен как обычный скилл — только отчёт. Блокировка — только через установленный hook.
- **Не лезет в код.** `.py`, `.js`, `.ts`, `.go` и т.п. — пропускает молча.

</instructions>

## REFERENCES (load on demand)

| File | When to load |
| --- | --- |
| [references/routing.md](references/routing.md) | Решаешь, какой набор правил применить к конкретному пути / расширению; нужны edge cases. |
| [references/severity.md](references/severity.md) | Нужно классифицировать нарушение по BLOCKING / WARNING / INFO или сверить полный список категорий. |
| [references/output-format.md](references/output-format.md) | Формируешь итоговый отчёт — нужен полный шаблон с примером и блоком SUMMARY. |
| [references/pre-commit-hook.md](references/pre-commit-hook.md) | Автор просит поставить style-check как git pre-commit hook — нужен bash-снипет и шаги. |
| [examples/sample-report.md](examples/sample-report.md) | Нужна калибровка тона/детализации отчёта — эталонный сэмпл. |
