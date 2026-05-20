# Audience and tone

Release notes have three primary audiences. The same change written for each looks different. Always identify the audience first.

---

## 1. End users (consumer / SaaS product UI users)

People who use the **product** through its UI. Don't read changelogs religiously; only care about what they can now do (or have to do).

### Voice

- Friendly-professional, occasional light warmth
- Concrete benefit-first phrasing
- Short bullets
- Light emoji acceptable for milestones (🎉 first integration, 🚀 launch) — never required
- Plain language; explain technical terms inline if they appear

### Example

```markdown
## v3.4 — 2026-05-20

### Added
- Dark mode — toggle in Settings → Appearance
- "Mute thread" option in the right-click menu on any conversation
- Quick search across all your workspaces (`Cmd+K`)

### Changed
- Notifications now batch into a single email when you receive 5+ in 10 minutes
- Project archives expire after 12 months (was 6) — more time to recover

### Fixed
- Search occasionally returned no results when query had a leading space
- "Save draft" sometimes flashed twice when you typed quickly
```

### What to AVOID for end users

- Internal codenames ("Project Phoenix") — use the product name users see
- Engineering jargon ("idempotent retries", "race condition") — describe the symptom
- Version numbers without context ("dropped support for v1") — say what version of WHAT
- "Backend" / "frontend" / "API" terminology — users don't need to know which layer changed
- Emoji per bullet — distracting; reserved for occasional milestones

---

## 2. Developers (API / SDK consumers)

People who **build against** the product. Read changelogs religiously. Need to know exactly what changed and what to migrate.

### Voice

- Direct, terse, precise
- Endpoint / method / parameter names verbatim
- Code-fence for code references inline
- Link to docs / migration guides liberally
- No emoji at all
- Past tense for shipped work

### Example

```markdown
## v2.5.0 — 2026-05-20

### Added
- `POST /v2/exports` endpoint for asynchronous bulk export (>500 records)
- `webhook_secret` field on `Webhook` object — used for signature verification
- `Client.exports.list({ limit, cursor })` — paginated listing
- Support for `arm64` in the Docker image

### Changed
- `Client.export()` returns a `Promise<Export>` instead of a string (the export ID is now `result.id`) — non-breaking; the string was previously deprecated
- Default `retry_count` for failed webhooks: 3 → 5
- `429` responses now include a `Retry-After` header

### Deprecated
- `POST /v1/exports` — use `POST /v2/exports`. Removal in v3.0 (est. Q3 2026). See [migration guide](https://docs.example.com/migrations/exports-v1-to-v2).

### Fixed
- `Client.webhooks.create()` threw when `events` was an empty array; now validates upfront with a clearer error
- Race condition in `Client.batch()` when concurrent requests > 50

### Security
- Patched session-fixation in OAuth callback handler ([CVE-2026-1234](...))
```

### What to AVOID for developers

- Marketing language — "powerful new endpoint" → just describe it
- Hand-waving ("improved error handling") → specify what's better
- Backwards-incompatible changes hidden in "Changed" — must be in **Breaking**
- Code samples without context — minimum: function signature OR endpoint method + path
- Generic descriptions when the developer needs to migrate — always link the migration guide

---

## 3. Ops / SRE / DevOps (deployers + monitorers)

People who **deploy and operate** the product (self-hosted) or downstream integrations (depend on uptime, observability, infra).

### Voice

- Most technical of the three
- Infrastructure terminology expected (Docker, K8s, Helm, Terraform, etc.)
- Performance / resource / scaling numbers prominent
- No emoji
- Past tense

### Example

```markdown
## v4.2.0 — 2026-05-20

### Added
- ARM64 builds (`linux/arm64` Docker image at `ghcr.io/example/app:4.2.0-arm64`)
- Prometheus `process_jvm_heap_used_bytes` metric in `/metrics`
- `--metrics-port` flag (default `9090`) — separate port for metrics scraping
- Helm chart `chart.example.com/app` published at v4.2.0

### Changed
- Default JVM heap: 512MB → 1GB. Override with `JAVA_OPTS=-Xmx512m` if needed.
- Database migrations now run with `pg_advisory_lock` to prevent races during rolling deploys
- Logs format default changed from `text` to `json` (configurable via `LOG_FORMAT`)

### Fixed
- Memory leak in connection pool when DB was unreachable for >5 minutes
- Worker processes were not shutting down cleanly on SIGTERM (would terminate after grace period)

### Security
- Container now runs as non-root user `appuser` (uid 1000) by default
```

### What to AVOID for ops

- User-facing UI screenshots — irrelevant
- "Improved performance" — give the actual numbers
- "Better observability" — list the new metrics / log fields / endpoints
- Vague impact statements — "memory leak" must say what was leaking, when, and the trigger condition

---

## Mixed audience (most common)

Many releases target multiple audiences (a SaaS that has both a UI and an API). Two patterns:

### Pattern A: separate sections per audience

```markdown
## v3.5 — 2026-05-20

### For end users
- Dark mode
- Quick search Cmd+K

### For API consumers
- `POST /v2/exports` endpoint
- Deprecated `POST /v1/exports`

### For ops
- ARM64 image
- New Prometheus metric
```

Use when changes are clearly bucketed by audience and the audiences don't overlap heavily.

### Pattern B: one stream with audience tags inline

```markdown
## v3.5 — 2026-05-20

### Added
- **[User]** Dark mode — Settings → Appearance
- **[API]** `POST /v2/exports` endpoint
- **[Ops]** ARM64 Docker image at `ghcr.io/example/app:3.5.0-arm64`
- **[User]** Cmd+K search across workspaces

### Changed
- **[User]** Email batching now triggers at 5 notifications / 10 minutes
- **[API]** Default `retry_count`: 3 → 5
- **[Ops]** Default JVM heap: 512MB → 1GB

### Fixed
- **[User]** Search returned no results when query had a leading space
- **[API]** Race condition in `Client.batch()` for >50 concurrent
- **[Ops]** Memory leak in connection pool during DB outages >5min
```

Use when audiences are clearly tagged (and consistent) and readers can scan for their relevant items.

### Picking between A and B

- Few items per audience (< 5) — Pattern B (less visual chunking, faster scan)
- Many items per audience (> 10) — Pattern A (clearer mental boundary)
- One audience dominates — single stream, ignore the others

---

## Per-channel adjustments

The same release note adjusts slightly for different publication channels:

| Channel | Audience focus | Length | Format notes |
|---|---|---|---|
| **Changelog page on the website** | All | Full | Markdown, with sections, all changes |
| **GitHub release notes** | Developers + ops | Full | Markdown, github-flavored, copy-paste of changelog or trimmed |
| **Email to subscribers** | End users primarily | Trimmed | Top 3-5 highlights + link to full changelog |
| **In-app modal / banner** | End users | Very trimmed | 1-3 most-important things + dismiss |
| **Social media post** | Marketing-adjacent | Hook + 1-3 things | Use `viral-text` skill instead |
| **API status / dashboard widget** | Developers + ops | Bullet list | Compact, dev-tone |

---

## Cross-references

- Section breakdown: [`sections.md`](sections.md)
- Length per format: [`structure.md`](structure.md)
- Words to strip: [`banned-patterns.md`](banned-patterns.md)

---

## RU tone notes

RU-аудитория ожидает чуть более формального регистра, чем EN, особенно в B2B и финтехе. Эта секция — overlay поверх трёх audience-режимов выше.

### Универсальные RU-правила

- **Заголовки секций** — на русском, не калькой с английского: «Добавлено» (не «Добавлены»), «Изменено», «Исправлено», «Удалено», «Безопасность», «Устарело» (для Deprecated), «Критические изменения» (для Breaking).
- **Версия + дата в шапке** — формат остаётся `v3.4.0 — 2026-05-20` (ISO дата работает в обоих языках; русское «20 мая 2026» допустимо для in-app анонсов, но не для changelog'а).
- **Эмодзи** — стрипать сильнее, чем в EN. В RU «🚀» и «🎉» в каждом буллете воспринимаются как маркетинговый шум. Допустимо: одна 🎉 на блок «Большие запуски» в квартальной сводке. В B2B-релизах — не использовать вообще.
- **Восклицания** — никогда в changelog'е, даже в потребительском. RU «!» давит сильнее EN «!».
- **Числа** — пробелы между разрядами: «1 200 ₽», «50 000 запросов», «380 мс». Десятичные через запятую: «1,2 с» (если на ru-локали). Технические единицы через точку: «1.2 GB» допустимо в developer/ops контексте.
- **Англицизмы** — в developer/ops секциях оставлять как есть («cursor pagination», «Retry-After header», «webhook»). В end-user секции — кириллизировать общеупотребительные («тёмная тема» вместо «dark mode», «уведомление» вместо «notification»), оставлять оригинал для названий продуктов и стандартов («Cmd+K», «SOC 2», «GDPR»).

### End users (RU)

```markdown
## v3.4.0 — 2026-05-20

### Добавлено
- Тёмная тема (Настройки → Внешний вид → Тёмная)
- Быстрый поиск по всем рабочим пространствам (`Cmd+K`)
- Опция «Отключить уведомления для треда» в контекстном меню разговора

### Изменено
- Уведомления теперь объединяются в одно письмо при поступлении 5+ за 10 минут (раньше — по одному письму на уведомление)
- Задержка поиска уменьшена с 2,1 с до 380 мс

### Исправлено
- Поиск иногда не находил результатов, если запрос начинался с пробела
- Массовый экспорт падал у организаций с 500+ проектами (утечка памяти)
- «Сохранить черновик» иногда срабатывал дважды при быстром наборе
```

Особенности RU end-user:
- «You'll love this» / «Take a break» — не переводятся. Эмоциональные обращения вырезаются.
- «Get started» в кнопках → «Начать» / «Открыть настройки» (конкретный глагол).
- «Trial / freemium» → «Пробный период / бесплатный план» (на консьюмерских; в стартап-tech-сегменте «trial» допустимо).

### Developers (RU)

В developer-секции RU работает ровно как EN — большая часть остаётся на английском (endpoint paths, метод-имена, типы данных). RU только в комментариях и описаниях.

```markdown
## v2.5.0 — 2026-05-20

### Критические изменения
- **`Client.export()`**: возвращает `Promise<Export>` (ID экспорта теперь `result.id`); ранее возвращался `Promise<string>`. Миграция: замените `const id = await client.export(...)` на `const { id } = await client.export(...)`. См. [руководство по миграции](https://docs.example.com/migrations/v2.5).

### Добавлено
- Endpoint `POST /v2/exports` для асинхронного массового экспорта (>500 записей). Возвращает `202 Accepted` с job ID; статус по `GET /v2/exports/{id}`.

### Безопасность
- Закрыта session-fixation уязвимость в OAuth callback ([CVE-2026-1234](...))
```

### Ops (RU)

Ровно как EN, RU только в комментариях. Технические термины и команды — оригинал (`pg_advisory_lock`, `SIGTERM`, `JAVA_OPTS`).

### Mixed audience (RU)

Pattern B (inline-теги) работает, но теги переводим:

```markdown
## v3.5 — 2026-05-20

### Добавлено
- **[Пользователь]** Тёмная тема — Настройки → Внешний вид
- **[API]** Endpoint `POST /v2/exports`
- **[Ops]** ARM64-образ `ghcr.io/example/app:3.5.0-arm64`
- **[Пользователь]** Поиск Cmd+K по всем пространствам
```

### Per-channel adjustments (RU)

| Канал | Особенность |
|---|---|
| Changelog на сайте | Полностью на RU, ISO-даты |
| GitHub release notes | Можно оставлять EN, если репо open-source с международной аудиторией; смешивать в одном release не стоит |
| Email подписчикам | RU для RU-юзеров, тогда «Что нового» вместо «What's new» в шапке |
| In-app модалка | 1-3 пункта, RU, «Узнать подробнее →» в качестве CTA вместо «Learn more» |
| Соцсети | Не этот скилл — для RU-постов про релиз использовать `viral-text` (он знает RU воздух/типографику) |
