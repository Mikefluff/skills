---
title: "Standalone style-check as a pre-publish gate"
persona: "Author wanting a manual quality verdict without auto-edits"
time: "3-5 minutes per file"
skills:
  - style-check
---

# Run style-check as a manual pre-publish gate

Сценарий: текст уже доведён — прогнан через `writer`, `prose-edit` или `essay-write`, ты сам его перечитал. Перед публикацией хочется один независимый read-only verdict: где ещё остались следы нейрослопа, структурной синтетики, voice drift. Не для авто-правки — для решения «отдавать или ещё крутить».

`style-check` именно для этого. Он:

- ничего не правит
- ничего не предлагает к правке
- только показывает findings с severity и точным местом
- возвращает exit-код, по которому можно гейтить CI или ручной workflow

Это отличает его от `writer`, `prose-edit`, `essay-write` — те **редактируют**. `style-check` — это линза, не редактор.

Если тебе нужен auto-fix — иди в `writer` / `prose-edit` / `essay-write`. Если нужен gate в pre-commit hook — см. [pre-commit-hook.md](pre-commit-hook.md). Если нужен ручной verdict перед публикацией — этот walkthrough.

## Intent — что значит «read-only gate»

Read-only — это не «менее строгий», это «не мутирует файл». Severity и пороги — те же, что в редактирующих скиллах. Просто `style-check` останавливается на отчёте.

Зачем отдельный read-only режим:

- **тестирование редакторских правок** — прогнал `prose-edit`, принял половину diff'а, хочешь увидеть, что осталось без новых мутаций
- **проверка чужого текста** — переводчик / соавтор прислал главу, ты хочешь verdict до того, как звать его в обсуждение правок
- **финальный gate** — до публикации; не хочется случайно перередактировать
- **CI** — на каждый PR в книжный/блоговый репозиторий

## Setup

Скилл уже установлен (если установлен общий пакет). Файлы, которые он понимает:

- `.md` (markdown — основной формат)
- `.tex` (LaTeX — для книжных проектов)
- `.txt` (plain text)
- `.rst` (reStructuredText)

Routing — какой rule layer применять (fiction / non-fiction / generic / viral) — определяется по пути файла. Дефолтные паттерны:

| Path pattern | Layer |
|---|---|
| `*/fiction/**`, `**/chapters/**` | `prose-edit` rules (художка) |
| `*/essays/**`, `*/posts/**`, `*/articles/**` | `essay-write` rules (нон-фикшн) |
| `*/viral/**`, `*/social/**` | `viral-text` rules (соцсети) |
| остальное | `writer` rules (generic чистка) |

Полная таблица + override-паттерн под твой проект — в [skills/style-check/references/routing.md](../../skills/style-check/references/routing.md). Layer можно переопределить вручную (см. ниже).

## Step 1. Point at a file or directory

### Single file

```
/style-check file essays/attention-economy.md
```

### Directory recursively

```
/style-check dir essays/
```

### Staged diff (для проверки перед коммитом без хука)

```
/style-check staged
```

### Explicit mode (override автоматического routing)

```
/style-check file experimental-piece.md --mode=fiction
```

Допустимые modes: `fiction`, `non-fiction`, `viral`, `generic`. Без `--mode` — routing по пути.

## Step 2. Read the report

Иллюстративный отчёт (один файл, mixed severity):

```
=== style-check ===
Mode: file essays/attention-economy.md
Layer: non-fiction (essay-write rules + writer 23-category)
Length: 4,128 words

[BLOCKING] essays/attention-economy.md
  L42  — NYEYROSLOP — AI_QA_HOOK («звучит знакомо?»)
         Категория: 23-я в writer, бан без обсуждения
  L188 — STRUCTURAL_SYNTHETIC — три параллельных абзаца «не X, а Y»
         Подряд 3 раза, при дефолтном пороге 2
  L312 — META_FILLER — «как мы уже видели выше»
         Голос-рассказчик в нон-фикшн эссе — ок, но «как мы видели»
         сводит читателя к школьной лекции

[WARNING] essays/attention-economy.md
  L77  — DOUBLE_NEGATION — «не невозможно увидеть»
         Двойное отрицание в утвердительном контексте
  L201 — CALQUE_EN — «делать смысл» (вместо «иметь смысл»)
  L355 — ADJECTIVE_PILE — 4 прилагательных подряд («сложное, многослойное,
         глубокое, неочевидное»)
  L412 — COMPARISON_OVERLOAD — 8-я метафора в эссе (порог 6 для non-fic)

[INFO] essays/attention-economy.md
  L99  — LONG_SENTENCE — 78 слов в одном предложении
         Не блокер, но проверь, читается ли вслух одним вдохом
  L501 — REPETITION_INTERWORD — слово «внимание» 14 раз на 200 слов
         Тематически оправдано, но обрати внимание

=== SUMMARY ===
essays/attention-economy.md: 3 BLOCKING · 4 WARNING · 2 INFO
Exit code: 2 (BLOCKING present)
```

Структура отчёта — формальная, чтобы можно было grep'ать в CI. Полная схема в [skills/style-check/references/output-format.md](../../skills/style-check/references/output-format.md).

## Severity levels

Три уровня. Жёсткие правила, не «настроение скилла»:

### BLOCKING

«Это не вопрос вкуса.» Что попадает:

- **NYEYROSLOP** — типовые AI-фразы (25 категорий из `writer`: «звучит знакомо?», «давайте разберёмся», «как мы все знаем», и т.д.)
- **STRUCTURAL_SYNTHETIC** — синтетические структуры (3+ параллельных абзаца, серии «не X, а Y», шаблонные riff'ы)
- **META_REF** в художке — отсылка на главу/книгу в голосе рассказчика
- **TAVTOLOGY** — корень в корне («открытое открытие», «свободный freedom»)
- **CANON_VIOLATION** для художки — если параллельно подключён `canon-check`

Exit-код 2. CI должен ломаться.

### WARNING

«Посмотри глазами и реши.» Что попадает:

- **DOUBLE_NEGATION** — двойное отрицание в утвердительном контексте
- **CALQUE_EN** / **CALQUE_RU** — подозрение на кальку
- **ANGLICISM** — англицизм в авторском голосе (не в диалоге)
- **STACCATO** — 3 односоставных подряд (в художке — BLOCKING, в нон-фике — WARNING)
- **ADJECTIVE_PILE** — 4+ прилагательных подряд
- **COMPARISON_OVERLOAD** — больше 6 метафор на эссе

Exit-код 1. CI обычно пропускает с предупреждением; в строгом режиме — ломается.

### INFO

«На твой вкус.» Что попадает:

- **LONG_SENTENCE** — > 60 слов в одном предложении
- **REPETITION_INTERWORD** — частое слово (но тематическое)
- **RHYTHM_NOTE** — изменение средней длины предложения по сравнению с типичной автора
- **CANON_EXPANSION** — новая деталь к канону (не противоречие)

Exit-код 0. CI всегда проходит. Информация для автора, не сигнал к правке.

Полный список категорий + пороги — в [skills/style-check/references/severity.md](../../skills/style-check/references/severity.md).

## Как читать findings — что «must fix», что «consider»

Простое правило: **BLOCKING правь, WARNING смотри, INFO забудь** (если не интересно).

Но есть нюансы:

### BLOCKING можно отклонить — но осознанно

`META_REF` на L312 в эссе про экономику внимания — если ты намеренно делаешь голос-лектор, то это **приём**, не дефект. `style-check` не знает твоей задумки. Игнорируй, прокомментируй в PR-описании, иди дальше.

### WARNING иногда серьёзнее BLOCKING

`STACCATO` в авторском голосе нон-фикшн эссе — формально WARNING (порог по умолчанию). Но если у тебя 8 таких мест в одной статье — это ритмический tic, и стоит чинить. Смотри на **плотность**, не только на severity отдельного findings.

### INFO часто полезнее, чем кажется

`REPETITION_INTERWORD — слово «внимание» 14 раз на 200 слов` — тематически оправдано (эссе же про внимание). Но если ты не заметил, что слово вылезло 14 раз — может, стоит подумать о 2-3 синонимах. Не блокер. Просто сигнал.

## Когда НЕ использовать style-check

- **Нужен auto-fix** — используй `writer clean`, `prose-edit`, `essay-write`. Они правят. `style-check` только показывает.
- **Нужен hook автоматически на коммите** — см. [pre-commit-hook.md](pre-commit-hook.md). Отдельный walkthrough про автоматизацию.
- **Текст ещё в драфте, не дописан** — `style-check` будет ругаться на структурные вещи, которые ты ещё не решил. Прогоняй после первого черновика, не на полу-черновике.
- **Художественный эксперимент, где правила нарочно нарушены** — поэтический текст, стилизация под архаизм, постмодернистский пастиш. Скилл не знает контекста и нашумит. Игнорируй или меняй layer вручную.

## Troubleshooting

### Скилл вернул 0 findings на тексте, который я считаю кривым

Проверь две вещи:

1. **Layer.** Если файл попал в `generic` слой (просто `writer`), а текст — художка, многие BLOCKING-категории не сработали (художественные правила в `prose-edit` строже). Запусти явно: `--mode=fiction`.
2. **Длина.** На текстах < 200 слов многие пороги не срабатывают (нужна выборка для статистики). Это by design — короткий пост не должен валить ту же сетку, что и эссе на 5000 слов.

Если оба ок, а текст всё равно «чувствуется кривым» — твоя интуиция видит больше, чем regex+правила. Скилл — нижняя граница, не верхняя.

### Слишком много findings на текст, который я считаю хорошим

Скорее всего — wrong layer. Художку прогнал через `essay-write` rules: будет ругаться на staccato, на отсутствие источников, на короткие предложения. Запусти с правильным `--mode`.

Если layer правильный, но findings всё равно много на любимом тексте — посмотри, что бьёт. Если 80% findings — одна категория (например, `STACCATO`) и это твой авторский голос — можно демотировать категорию для проекта (см. [skills/style-check/references/severity.md](../../skills/style-check/references/severity.md), раздел «project-level overrides»). Это не отключение скилла, это калибровка под голос.

### Exit-код 2, но в выводе только WARNING

Это бывает, когда у тебя один INFO + один BLOCKING, но в кратком превью видны только последние. Скрольни вверх или запусти с `--verbose` — увидишь все findings, не только последние 10. Exit-код всегда отражает worst severity.

### Скилл ругается на цитату

`L188 — STRUCTURAL_SYNTHETIC — три параллельных абзаца «не X, а Y»` — но это цитата из чужого текста, в блоке `> ...`. Скилл не различает свои и цитированные строки.

Что делать:

- проверь руками — если это действительно цитата, игнорируй findings (упомяни в PR-описании)
- или оберни цитату в HTML-комментарий-маркер, который скилл понимает (см. [skills/style-check/references/routing.md](../../skills/style-check/references/routing.md), раздел «inline exclusions»)

### Хочу гейтить только BLOCKING в CI, WARNING пропускать

Это дефолт. Exit-коды:

- `0` — только INFO → CI проходит
- `1` — WARNING (без BLOCKING) → CI обычно проходит, может пропустить с warning
- `2` — BLOCKING → CI ломается

Если хочешь строгий режим (`exit 1` тоже валит CI) — это в скрипте CI решается, не в скилле. См. [pre-commit-hook.md](pre-commit-hook.md), раздел «strict mode».

## Related

- [pre-commit-hook.md](pre-commit-hook.md) — автоматизировать тот же чек на каждом коммите
- [fiction-chapter.md](fiction-chapter.md) — место `style-check` в конце цепочки художки
- [non-fiction.md](non-fiction.md) — то же для нон-фикшн эссе
- [skills/writer/SKILL.md](../../skills/writer/SKILL.md) — если нужен auto-fix вместо verdict
- [skills/prose-edit/SKILL.md](../../skills/prose-edit/SKILL.md) — auto-fix для художки
- [skills/essay-write/SKILL.md](../../skills/essay-write/SKILL.md) — auto-fix для нон-фикшн
- [docs/FAQ.md](../FAQ.md) — частые вопросы
