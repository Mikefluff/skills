# skills

Collection of Claude Code / Claude Agent SDK skills.

A "skill" here is a self-contained Markdown package that Claude loads on demand: a `SKILL.md` with frontmatter, optional `references/`, `scripts/`, and `examples/`. See the official spec: https://docs.claude.com/en/docs/claude-code/skills

---

## Skills in this repo

Скиллы организованы по слоям: один базовый редактор (`writer`) + четыре обёртки/линтера поверх него.

| Skill | Layer | Purpose |
|---|---|---|
| [`writer`](writer/) | base | Базовый редактор-стилист чистой прозы. Антинейрослоп (23 категории), типографика, структурная синтетика (стаккато / двойные отрицания / обрубки / инверсии / повторы), RU-калек словарь. Подключается из любого текстового скилла как обязательный финальный шаг pipeline. Может вызываться напрямую (`clean` / `lint` / `apply`). |
| [`viral-text`](viral-text/) | wrapper | Write viral social media content (RU/EN) — hooks, 5 numbered points, micro-conclusion with NLP question, CTA. 41 viral content rules, hook criteria, research via WebSearch, platform adaptation (Telegram/Threads/Instagram/Twitter/LinkedIn/Facebook), Layer A+B validation. Built on top of `writer`. |
| [`prose-edit`](prose-edit/) | wrapper | Художественный рерайт для книг автора. Голос (Пелевин/Мэнсон), 10-item style drift checklist, canon-check, NO meta-refs / NO anglicisms in narrator voice, длинный артистический рерайт вместо сокращения, AB ToV pattern, 5-trigger structural synthesis detector, anti-tautology checklist. |
| [`essay-write`](essay-write/) | wrapper | Нон-фикшн (главы НК, лонгриды, эссе). Длинные сложноподчинённые (Мэнсон-стиль), source-backed claims, philosophy through humor, biography through scenes, plain-Russian for complex content, anti-academic-pathos bans, sparing-with-metaphors. |
| [`style-check`](style-check/) | linter | Read-only pre-commit lint поверх writer/prose-edit/essay-write. Auto-routes по пути файла (`books/god-academy/` → художка; `books/heavenly-code/` → нон-фикшн), severity levels (BLOCKING/WARNING/INFO), exit-code semantics для git hook. |

Будущие скиллы добавляются как отдельные подпапки рядом с существующими.

---

## Layout per skill (SOTA structure)

```
<skill-name>/
├── SKILL.md              # entrypoint — frontmatter + concise router; reference-files linked
├── references/           # progressive disclosure: загружается только когда нужно
│   └── *.md
├── scripts/              # optional executables (Python / shell)
│   └── *.py
└── examples/             # canonical inputs/outputs for calibration
    └── *.md
```

Принципы:

- **SKILL.md** — компактный (≤ 300 строк), описывает цель, контракт, общие правила, и линкует тяжёлые секции в `references/`.
- **references/\*.md** — детальные правила/таблицы/каталоги, не грузятся в контекст модели, пока не понадобятся.
- **scripts/** — детерминированный код (offline regex линт, генераторы), который дешевле и надёжнее LLM-прохода.
- **examples/** — калибровочные before/after, на которых проверяется, что обновление SKILL.md не сломало поведение.

---

## Install

### Вариант 1 — symlink одного скилла в пользовательскую коллекцию

```bash
ln -s "$(pwd)/writer" ~/.claude/skills/writer
```

После этого Claude Code увидит скилл в списке доступных. Триггер: `/writer` (если поддерживается user-invocable) или автоматически по описанию из frontmatter. Аналогично для остальных (`viral-text`, `prose-edit`, `essay-write`, `style-check`).

Если ставишь набор целиком — обязательно линковать `writer` первым, поскольку остальные на него ссылаются.

### Вариант 2 — клонировать репо и подложить весь набор

```bash
git clone https://github.com/Mikefluff/skills.git ~/code/skills
for d in ~/code/skills/*/; do
  name=$(basename "$d")
  [ -f "$d/SKILL.md" ] && ln -s "$d" ~/.claude/skills/"$name"
done
```

### Вариант 3 — project-scoped

Скопировать нужную подпапку в `.claude/skills/<name>/` внутри проекта. Скилл будет виден только в этом проекте.

---

## Usage of `writer` standalone

Три режима (см. `writer/SKILL.md` → INPUT / OUTPUT CONTRACT):

- `clean` (default) — почистить переданный текст по всем правилам, вернуть финал + краткую сводку нарушений
- `lint` — пройтись и показать список нарушений с локациями, без правок
- `apply` — внутренний шаг под-скилла, без отдельного output

Plus есть offline regex линтер:

```bash
python3 writer/scripts/lint.py path/to/text.md
# or
cat draft.md | python3 writer/scripts/lint.py -
# JSON output
python3 writer/scripts/lint.py draft.md --json
```

Exit codes: `0` clean (0-1 hits) · `1` borderline (2-4) · `2` neuroslop suspected (5+ или категория 3+).

---

## Contributing

Если хочется добавить свой скилл — следовать SOTA-структуре выше:

1. Папка `<skill-name>/`
2. `SKILL.md` с frontmatter (`name`, `description`, `license`, `allowed-tools`)
3. Тяжёлые правила — в `references/*.md`, линкуются из SKILL.md
4. Если есть детерминированная логика — `scripts/`
5. Калибровочные кейсы — `examples/`
6. Линкануть скилл в `README.md` (этот файл) в таблице выше

---

## License

MIT — см. [LICENSE](LICENSE).
