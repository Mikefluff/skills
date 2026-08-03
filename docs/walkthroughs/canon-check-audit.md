---
title: "Story-bible audit for a fresh chapter"
persona: "Novelist with a multi-book series and a written canon"
time: "8-12 minutes"
skills:
  - canon-check
---

# Audit a fresh chapter against the story bible

Сценарий: 17-я глава длинной серии только что дописана. Тысячи слов, десятки имён, артефактов, локаций — половина из них уже была в главах 1-16, половина появилась только что. Перед коммитом хочется убедиться, что:

- никто из старых персонажей не вернулся под чужим именем (или новое имя не пересеклось с уже существующим)
- ни одна задокументированная физическая черта не вывернулась (правша — левша, синие глаза — карие, 32 года — 47)
- новая локация не назвалась так же, как уже описанная двумя главами раньше
- никакая новая сущность не «протекла» в текст без записи в bible

Канон не держится в голове — он держится в `notes/story-bible.md`. Скилл `canon-check` — это read-only сверка одной главы со всем накопленным каноном. Не правит ни главу, ни bible. Только показывает расхождения.

## Setup

Скилл ожидает, что у проекта есть story-bible в одном из стандартных мест:

- `notes/story-bible.md` (по умолчанию)
- `<series>/notes/story-bible.md`
- `bible.md` в корне репозитория

Формат — простой markdown с секциями `# Characters`, `# Artifacts`, `# Locations`. Полная схема в [skills/canon-check/references/bible-format.md](../../skills/canon-check/references/bible-format.md). Минимальный пример:

```markdown
# Characters

## Левитан
- роль: главный антагонист
- возраст: 47
- глаза: серые
- рука: правша (хват: большой+указательный сверху)
- отметины: шрам над левой бровью (после ch12)

# Locations

## Южное Бутово
- административно: район Москвы
- упоминался: ch02, ch08, ch14
```

Поддерживаемые форматы главы: `.md`, `.tex`, `.txt`. RTF и DOCX — нет (предполагается, что черновики уже в plain text).

## Step 1. Run the audit

```
/canon-check chapter chapters/17.md bible notes/story-bible.md
```

Если оба пути дефолтные — можно короче:

```
/canon-check chapter 17
```

Скилл:

1. Извлекает все proper nouns из `chapters/17.md` (персонажи, артефакты, локации, бренды-как-реалии).
2. Кросс-референсит с `notes/story-bible.md`.
3. Кросс-референсит с предыдущими главами (`chapters/01.md..16.md`) — на случай молчаливых противоречий.
4. Выдаёт структурированный отчёт.

Полный workflow расписан в [skills/canon-check/references/workflow.md](../../skills/canon-check/references/workflow.md).

## Step 2. Read the report

Иллюстративный вывод (сокращён, мешаный severity):

```
=== canon-check ===
Mode: chapter chapters/17.md
Bible: notes/story-bible.md
Cross-referenced: chapters/01.md..16.md (16 prior chapters)

[BLOCKING] chapters/17.md
  L88 — CHARACTER_CONTRADICTION — «Левитан взял чашку левой рукой»
        Bible (story-bible.md §Levitan): «правша, хват: большой+указательный сверху»
        Prior appearances confirming: ch02:L142, ch05:L201, ch11:L88

  L204 — CHARACTER_CONTRADICTION — «зелёные глаза Анны»
        Bible (story-bible.md §Anna): «глаза: карие»
        Prior appearances confirming: ch03:L77, ch09:L312

  L319 — NAME_COLLISION — новый персонаж «Митя» (диминутив от Дмитрия?)
        Conflict: ch05.md:L88 — есть «Митя», но это сын Левитана (8 лет)
        Текущий контекст: коллега-программист, ~30 лет
        Two distinct people share a name → BLOCKING

[WARNING] chapters/17.md
  L256 — SILENT_CANON — персонаж «Тоня Гримберг» появляется впервые
        No entry in story-bible.md
        Appearances in other chapters: 0
        Action: либо канонизировать (добавить bible entry), либо переименовать,
                либо подтвердить как одноразового

  L411 — LOCATION_DRIFT — «Южное Бутово, улица Грина»
        Bible (story-bible.md §Yuzhnoye-Butovo): улицы не зафиксированы
        Prior appearances: ch08 упоминает «улица Грина» — совпадает
        Action: добавить в bible-entry для канонической связки

[INFO] chapters/17.md
  L342 — CANON_EXPANSION — у Левитана упомянут шрам над правой бровью
        Bible: «шрам над левой бровью (после ch12)»
        Possible typo OR второй шрам — author's call

  L505 — NEW_ARTIFACT — «голубой ключ от двери на крышу»
        First appearance — no prior context
        Не противоречие, расширение
        Action: опционально внести в bible §Artifacts

=== SUMMARY ===
chapters/17.md: 3 BLOCKING · 2 WARNING · 2 INFO
Known incidents: 0 (see skills/canon-check/references/known-incidents.md)
```

## Step 3. Severity — как читать

### BLOCKING

Прямое противоречие задокументированному канону или коллизия имён. Текст не врёт случайно — либо ты намеренно меняешь канон (тогда меняй и bible отдельным коммитом), либо опечатался. Каждый BLOCKING — это одно из трёх:

- **CHARACTER_CONTRADICTION** — физический инвариант (рука, глаза, возраст, рост, родинка) поменялся. Bible говорит одно, текст — другое.
- **NAME_COLLISION** — два разных человека/артефакта/места под одним именем в пределах серии.
- **CANON_CONTRADICTION** (артефакты, локации) — задокументированное свойство опровергнуто текстом.

Принцип: **trust the text, not memory**. Скилл не правит ни главу, ни bible. Решает автор.

### WARNING

Молчаливое расширение канона: что-то новое попало в текст без записи. Не обязательно ошибка — но автор должен принять решение явно.

- **SILENT_CANON** — персонаж/артефакт/локация появляется впервые. Bible silent.
- **LOCATION_DRIFT** — детали локации добавляются, но не противоречат bible.
- **AGE_CREEP** — возраст указан в новой главе и расходится с расчётом по таймлайну на 1-2 года (внутри tolerance, но стоит заметить).

### INFO

Не противоречие, а потенциальное расширение, которое стоит положить в bible — чтобы следующая глава его поймала.

- **CANON_EXPANSION** — новая деталь, не отрицающая старую (новый шрам, новая привычка).
- **NEW_ARTIFACT** / **NEW_LOCATION** — первое появление, контекст одноразовый.

Полная таблица severity и порогов — в [skills/canon-check/references/known-incidents.md](../../skills/canon-check/references/known-incidents.md).

## Что скилл НЕ делает

- **Не правит главу.** Только сообщает. Все правки — руками автора, или через `prose-edit` на следующем этапе.
- **Не правит bible.** Bible мутирует только автор, отдельным коммитом, явно.
- **Не предлагает каноническую правду.** Если есть противоречие — скилл показывает обе стороны, не выбирает.
- **Не делает stylistic call.** Это `prose-edit` и `style-check`. Здесь только канон.
- **Не угадывает диминутивы.** Если в bible нет связки «Дмитрий → Митя», скилл не предположит её сам — он сообщит NAME_COLLISION и оставит решение автору.

## Troubleshooting

### Bible ещё не существует

Заведи пустой файл с минимальной структурой:

```markdown
# Characters

# Artifacts

# Locations
```

Скилл при пустом bible будет всё помечать как SILENT_CANON — это нормально, постепенно наполнишь. См. [skills/canon-check/references/bible-format.md](../../skills/canon-check/references/bible-format.md).

### False positive — герой не сам взял чашку

`L88 — Левитан взял чашку левой рукой` — а в реплике контекст: «Левитан передал чашку, и Анна взяла её левой». Скилл атрибутировал действие не тому персонажу. Это типовая false-positive: anaphora resolution в художке нетривиальна.

Что делать:

- Проверь руками — действительно ли формулировка читается двусмысленно. Если да — переформулируй (это правка не от канона, а от ясности).
- Если формулировка однозначна, а скилл всё равно бьёт — отметь как known incident в [skills/canon-check/references/known-incidents.md](../../skills/canon-check/references/known-incidents.md) и иди дальше.

### Ambiguous entity — это новый персонаж или диминутив?

`L319 — Митя` — скилл не знает, новое это лицо или диминутив от уже существующего. Он показывает оба варианта. Решение — автора. Если это диминутив — допиши в bible связку (`## Дмитрий → diminutive: Митя`), и следующий прогон поймёт.

### Routing — почему не сработало на `.docx`

`canon-check` работает только с plain-text форматами. Конвертируй в `.md` (pandoc, ручная вычитка) перед прогоном. Полные правила маршрутизации — в [skills/canon-check/references/routing.md](../../skills/canon-check/references/routing.md).

### Глава большая, прогон долгий

Скилл — read-only, но всё равно несколько секунд на тысячи слов. Если глава > 20K слов и прогон ощутимый — разбей на сцены и прогоняй посценово (`/canon-check chapter chapters/17-scene-1.md`). Это пограничный кейс, обычно глава умещается в 8-12 минут включая чтение отчёта.

## Related

- [fiction-chapter.md](fiction-chapter.md) — место `canon-check` в полной цепочке от драфта до коммита
- [skills/prose-edit/SKILL.md](../../skills/prose-edit/SKILL.md) — следующий шаг после canon-фикса: художественный рерайт
- [skills/style-check/SKILL.md](../../skills/style-check/SKILL.md) — финальный лит-чек перед коммитом
- [docs/FAQ.md](../FAQ.md) — частые вопросы
