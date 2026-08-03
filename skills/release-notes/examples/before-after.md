# release-notes — calibration before/after pairs

5 paired examples covering SaaS / API library / mobile / breaking release / quarterly recap. Each shows weak release notes and the rewrite this skill should produce.

---

## 1. SaaS minor release (end users)

### Before (weak)

```markdown
## What's new in v3.4

We're SO excited to announce v3.4 of Acme — our most ambitious release yet! 🚀
After months of hard work, we're thrilled to share some game-changing improvements
that will revolutionize how you use Acme.

### Features
- Dark mode is finally here! 🌙 You'll love how seamless and beautiful it looks.
- We've added quick search across workspaces — a powerful new way to navigate.
- New "Mute thread" option (you'll love this one).

### Improvements
- Improved performance across the board
- Enhanced search functionality
- Better notifications

### Bug fixes
- Fixed various bugs
- Squashed some pesky issues
```

What's wrong:
- "SO excited", "thrilled", "most ambitious", "revolutionize", "game-changing" — marketing hype
- "improved performance across the board" — no number
- "Better notifications" — what specifically?
- "Various bugs" — useless
- Emoji per bullet
- "you'll love this" — speaking for the user

### After (rewrite)

```markdown
## v3.4.0 — 2026-05-20

### Added
- Dark mode (Settings → Appearance → Dark)
- Quick search across all workspaces (`Cmd+K`)
- "Mute thread" option in conversation right-click menu

### Changed
- Notifications now batch into a single email when 5+ arrive in 10 minutes (was: one email per notification)
- Search latency reduced from 2.1s to 380ms

### Fixed
- Search occasionally returned no results when query had a leading space
- Bulk-export failed for organizations with >500 projects (memory leak)
- "Save draft" sometimes flashed twice when typing quickly
- Dark mode rendering broke on Safari 17.0-17.2 (pre-launch beta users only)
```

### Deltas applied
- Stripped all marketing hype (-12 phrases)
- Removed emoji per bullet (kept only the ISO date in header — no emoji at all)
- "Improved performance" → specific number (2.1s → 380ms)
- "Various bugs" → 4 specific bullets
- "You'll love" → deleted (speaks for user, presumptuous)
- Past tense throughout (Added/Changed/Fixed)
- No lead paragraph (routine minor release doesn't need one)

---

## 2. API library minor release (developers)

### Before (weak)

```markdown
## v2.5 release notes

We're proud to release the latest version of our SDK with some incredible enhancements!

### What's new
- Powerful new bulk export endpoint
- Webhook signing for better security
- Better pagination support
- Some breaking changes (sorry!) — please check the docs

### Bug fixes
- Various improvements to error handling
- Performance is now much better
- Fixed several issues with retries
```

What's wrong:
- "Proud", "incredible enhancements" — marketing
- "Sorry" for breaking changes — should be explicit about WHAT breaks, not apologize
- "Some breaking changes" — must be in **Breaking** section with specifics
- "Various improvements to error handling" — meaningless
- "Performance is now much better" — no number
- "Several issues with retries" — list them
- "Please check the docs" — link to specific migration guide

### After (rewrite)

```markdown
## v2.5.0 — 2026-05-20

### Breaking
- **`Client.export()` signature**: now returns `Promise<Export>` (the export ID is `result.id`); previously returned `Promise<string>`. Migration: replace `const id = await client.export(...)` with `const { id } = await client.export(...)`. See [migration guide](https://docs.example.com/migrations/v2.5).

### Added
- `POST /v2/exports` endpoint for asynchronous bulk export (>500 records). Returns `202 Accepted` with a job ID; poll `GET /v2/exports/{id}` for status.
- `Webhook.secret` field — used for HMAC signature verification. Sign with `X-Webhook-Signature` header on incoming requests.
- `Client.exports.list({ limit, cursor })` — cursor-based pagination

### Changed
- Default `retry_count` for failed webhooks: 3 → 5
- `429 Too Many Requests` responses now include a `Retry-After` header (seconds)
- Error messages from `Client.batch()` now include the specific failed request index

### Fixed
- `Client.webhooks.create()` threw when `events` was an empty array; now validates upfront with a clearer error
- Race condition in `Client.batch()` when concurrent requests > 50
- Retry logic skipped the first attempt on transient network errors (now retries from attempt 1)
```

### Deltas applied
- Marketing hype stripped
- "Some breaking changes" → explicit **Breaking** section with migration steps
- Pagination "support" → specific cursor-based pattern with API surface
- "Various improvements to error handling" → 3 specific fixes
- "Performance much better" → specific changes (retry_count, Retry-After header, batch errors)
- Each bullet has concrete API surface (method name, parameter, status code, header)

---

## 3. Mobile app (end users via app store)

### Before (weak)

```markdown
## v4.2 update

This update includes the latest features and improvements!

- Dark mode support
- Bug fixes and performance improvements
- We've squashed many bugs to give you a smoother experience
- New emoji reactions on messages
```

What's wrong:
- "Latest features and improvements" — empty
- "Bug fixes and performance improvements" — useless
- "Smoother experience" — vague
- App-store update notes have a specific format

### After (rewrite — app store style)

```markdown
## v4.2 — 2026-05-20

### What's new
- 🌙 Dark mode — toggle in Settings → Appearance
- 💬 Emoji reactions on messages (long-press to react)
- ⚡ App opens 40% faster on iPhone 12 and older

### Fixed
- Notifications occasionally arrived 30+ minutes late on iOS 17.3
- "Sign in with Apple" failed on iPad mini 6th gen
- Conversation list scrolled to the top after switching apps
- Profile photo upload failed for HEIC images >5MB
```

### Deltas applied
- App-store format: emoji used sparingly for visual scan (one per bullet in "What's new" only)
- "Bug fixes and performance improvements" → 4 specific fixes with device/iOS specificity
- Performance claim got a specific number (40% faster on iPhone 12+ older)
- Past tense throughout

---

## 4. Major release with breakage (developers)

### Before (weak)

```markdown
## v3.0 — Major Release! 🚀

We're SO excited to share v3.0 with you! This is our biggest release ever and represents
months of hard work from our amazing team. We've added tons of new features and made
some breaking changes that we think will make Acme even better.

### Major changes
- API v2 is now the default
- Removed legacy endpoints (sorry!)
- Some new features
- Various improvements

We're thrilled to have you on this journey with us!
```

What's wrong:
- Hype overload
- "Tons of new features" — empty
- "Some new features" — empty
- "Various improvements" — empty
- "On this journey with us" — marketing, irrelevant to release notes
- "Sorry" for removals — should be migration links

### After (rewrite)

```markdown
## v3.0.0 — 2026-05-20 (major release — see breaking changes)

This release moves the API to v2 by default and removes the v0/v1 endpoints
deprecated since 2025. Existing integrations require updates — see
[v2.x → v3.0 migration guide](https://docs.example.com/migrations/v3).

### Breaking
- **API**: `POST /v0/exports` and `POST /v1/exports` removed (deprecated since v2.0). Use `POST /v2/exports`. [Migration steps](https://docs.example.com/migrations/exports-v0-to-v2).
- **API**: `Client.export()` no longer accepts a single string parameter. Pass an options object: `Client.export({ format: 'csv', filter: '...' })`.
- **CLI**: `--legacy-format` flag removed. Use `--format <name>`.
- **Behavior**: New API responses use ISO 8601 dates by default. Set `Accept-Format: legacy` to opt out (will be removed in v4.0).

### Added
- `POST /v2/imports` endpoint — symmetric to exports, async with job IDs
- `webhook_secret` field on all `Webhook` resources
- TypeScript SDK with full type definitions (`@example/sdk-ts`)
- Python async client (`example-async`)

### Changed
- Default `retry_count` for failed requests: 3 → 5
- Error responses now include a `request_id` field for support traceability

### Removed
- `POST /v0/exports` and `POST /v1/exports` (see Breaking)
- `--legacy-format` CLI flag (see Breaking)
- Internet Explorer support in the web dashboard

### Security
- All session tokens now rotate every 24 hours (was 7 days)
- Patched session-fixation in OAuth callback ([CVE-2026-0123](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2026-0123), severity: medium)
```

### Deltas applied
- Hype stripped completely
- Header signals "major release — see breaking changes"
- Short lead paragraph (3 sentences) with migration link
- Breaking section with specific endpoints, methods, opt-out windows, migration links
- Removed empty bucket descriptions in favor of specific bullets
- Migration link liberally — every breaking change has one
- Specific CVE link with severity

---

## 5. Quarterly recap (end users + developers)

### Before (weak)

```markdown
## Q2 2026 Recap

What a quarter! We've shipped so many incredible features and we're so excited about
where Acme is going. Here are some highlights from a busy three months:

- Real-time collaboration (it's amazing!)
- Dark mode (finally!)
- API v2 (a huge upgrade!)
- Tons of bug fixes
- Better performance

We can't wait for Q3 — even bigger things are coming! 🎉
```

What's wrong:
- "What a quarter" — empty
- "So many incredible features" — no count
- "So excited", "can't wait" — feelings
- "Tons of bug fixes" — give a number
- "Better performance" — give a number
- "Even bigger things are coming" — forward-looking promise (don't make in recap)

### After (rewrite)

```markdown
## Q2 2026 — Three Months in Review

**Theme**: collaboration + search

**Big launches**
- **Real-time collaboration** (v3.2, 2026-04-10) — multiple cursors, presence indicators, conflict-free editing
- **Quick search** (v3.4, 2026-05-20) — Cmd+K across all workspaces, 5x faster than v3.3 search
- **API v2** (v3.0, 2026-04-01) — async exports, cursor pagination, webhook signatures, TypeScript SDK

**Notable improvements**
- Search latency: 2.1s → 380ms (5x faster, v3.1)
- Mobile cold start: 1.4s → 800ms (40% faster on iPhone 12+ and older, v3.3)
- Dark mode (v3.4)

**Bug fixes**
- 47 reported bugs closed across v3.0-v3.4
- Notable: Unicode emoji search crash, OAuth redirect loop, bulk-export timeout for >500 projects, iPad mini 6th gen sign-in

**By the numbers**
- 3 minor releases (v3.0, v3.2, v3.4) + 2 patches (v3.1, v3.3)
- 142 commits from 8 contributors
- Zero unplanned downtime (vs. 47 minutes in Q1 2026)
- Zero security incidents

**Migration heads-up for Q3**
- API v0/v1 deprecation removal in v4.0 (estimated August 2026)
- See [API v2.x → v3.0 migration](https://docs.example.com/migrations/v3) if you haven't migrated yet

[Per-release changelogs →](https://example.com/changelog)
```

### Deltas applied
- Removed hype + feelings
- "What a quarter" → explicit theme
- Counts everywhere (3 launches, 47 bugs, 142 commits, 0 downtime)
- "Big launches" with version + date + concrete behavior
- "Notable improvements" with before/after numbers
- "By the numbers" — pure stats section
- Forward-looking section is concrete: migration deadline + link
- No "can't wait for Q3" emotional close

---

## Pattern summary

Across all 5 rewrites:

1. **Strip hype**: revolutionary / game-changing / SO excited / proud / amazing → deleted
2. **Replace vague with specific numbers**: "performance better" → "2.1s → 380ms"
3. **Past tense for shipped work**: "we are adding" → "Added"
4. **Migration links for every breaking change**
5. **Specific behaviors**: name the endpoint, the method, the button location
6. **Bullet per concept**: never merge two changes into one bullet
7. **No emoji per bullet** (occasional milestone emoji is OK in user-facing notes)
8. **Concrete dates**: ISO 8601, no "last week" or "recently"
9. **Audience-aware**: end-user words for end users, API surface for developers, infra terms for ops
10. **No marketing CTAs**: release notes aren't a sales channel

---

## 6. (RU) Релиз B2B-SaaS для российских юзеров

### Контекст

RU B2B SaaS, CRM для агентств. Минорный релиз v4.2. Целевая аудитория — конечные пользователи (менеджеры в агентствах). Канал — changelog на сайте + email-рассылка подписчикам.

### До (слабо — RU калька с EN-маркетинга)

```markdown
## v4.2 — что нового!

Мы безумно рады поделиться нашим самым амбициозным релизом за всё время существования продукта! 🚀
После месяцев напряжённой работы наша команда счастлива представить game-changing улучшения,
которые революционно изменят ваш опыт работы с CRM.

### Фичи
- Тёмная тема наконец-то здесь! 🌙 Вы будете в восторге от того, как круто она выглядит.
- Мы добавили быстрый поиск по всем рабочим пространствам — потрясающе мощный новый способ навигации!
- Новая опция "Mute thread" (вам понравится!) 

### Улучшения
- Улучшена производительность по всем направлениям
- Улучшен функционал поиска
- Улучшены уведомления

### Багфиксы
- Исправлены различные баги
- Подавили несколько надоедливых проблем!
```

What's wrong:
- «Безумно рады», «амбициозный», «game-changing», «революционно» — RU-калька маркетингового EN-хайпа
- «Вы будете в восторге», «вам понравится» — speaks for the user (как в EN)
- Восклицания везде (нарушает RU-rule о «!»)
- «Mute thread» — англицизм без перевода
- «Улучшена производительность по всем направлениям» — без чисел
- «Подавили несколько надоедливых проблем» — emotional + vague
- 🚀 + 🌙 в каждом буллете — RU-emoji-noise (сильнее, чем в EN)

### После (rewrite)

```markdown
## v4.2.0 — 2026-05-20

### Добавлено
- Тёмная тема (Настройки → Внешний вид → Тёмная)
- Быстрый поиск по всем рабочим пространствам (`Cmd+K`)
- Опция «Отключить уведомления для треда» в контекстном меню разговора

### Изменено
- Уведомления объединяются в одно письмо при поступлении 5+ за 10 минут (раньше приходило по одному письму на каждое)
- Архивы проектов хранятся 12 месяцев (раньше 6 месяцев)
- Задержка поиска уменьшена с 2,1 с до 380 мс

### Исправлено
- Поиск иногда не находил результатов, если запрос начинался с пробела
- Массовый экспорт падал у организаций с 500+ проектами (утечка памяти)
- «Сохранить черновик» иногда срабатывал дважды при быстром наборе
- Тёмная тема некорректно отображалась в Safari 17.0-17.2 (только бета-пользователи)
```

### Применённые дельты

- «Что нового!» в шапке → нейтральная версия + ISO-дата
- Удалён вводный абзац с маркетинговым хайпом (8 фраз)
- «Mute thread» → «Отключить уведомления для треда» (RU end-user секция кириллизирует общеупотребительные термины)
- «Улучшена производительность по всем направлениям» → конкретные числа (2,1 с → 380 мс с RU-десятичной запятой)
- «Различные баги» / «надоедливые проблемы» → 4 конкретных bullet'а с указанием браузера, размера orgs, поведения
- Эмодзи (🚀, 🌙) убраны полностью — стандарт RU B2B
- «Mute», «Cmd+K» — оставлены кириллицей описание + EN keyboard-shortcut (по правилу из `audience-tone.md` § RU)
- «Архивы проектов хранятся 12 месяцев» — RU-формулировка через «хранятся», не калька «expire»
- Все буллеты в прошедшем времени для shipped work («Уведомления объединяются» — настоящее, описывающее новое поведение; «исправлено» / «уменьшена» — прошедшее для свершившегося)
