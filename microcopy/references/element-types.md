# UI element types

Microcopy isn't one thing. Each UI element has its own length budget, register, structure, and failure modes.

---

## Button labels

The shortest, highest-friction element. Every word costs.

### Shape

| Length | Use when |
|---|---|
| 1 word | Default for primary actions: `Save`, `Cancel`, `Delete`, `Continue`, `Submit` |
| 2-3 words | When the verb needs an object: `Add member`, `Cancel order`, `Send invite`, `Create account` |
| 4-6 words | Rare — only when ambiguity demands clarity: `Save and continue editing` |
| 7+ words | Almost always wrong — split into label + helper text |

### Rules

- **Verb first**: `Send invite` ✅, `Invite send` ❌
- **No "Please"** in button labels (looks needy)
- **No questions in buttons**: `Send?` ❌; the button is the action, the question goes in the title/body
- **Match the action**: `Submit` if the form is a submission; `Save` if changes persist; `Continue` if next step; `Got it` for dismissal of info
- **Avoid ambiguous "OK"** for destructive actions: `Delete account` not `OK`

### Common patterns

| Action | Label |
|---|---|
| Primary save | `Save`, `Save changes`, `Save as draft` |
| Primary submit | `Submit`, `Send`, `Publish` |
| Primary continue | `Continue`, `Next`, `Get started` |
| Primary creation | `Create [item]`, `Add [item]` |
| Cancel / dismiss | `Cancel`, `Close`, `Dismiss`, `Not now` |
| Destructive | `Delete`, `Remove`, `Discard`, `Cancel order` |
| Confirmation | `Confirm`, `I understand`, `Got it` |
| Reset | `Reset`, `Clear all`, `Start over` |

---

## Error messages

What broke + (when relevant) what to do.

### Shape

```
{What broke, plain language}
{Optional: how to fix it / what to try next}
```

### Length budget

- Inline error (form field): 1 short sentence, ≤ 12 words
- Toast / alert: 1-2 sentences, ≤ 30 words
- Modal error: title + 1-2 sentences body + 1 primary action

### Rules

- **State what failed, not what you did wrong**: ❌ "Invalid email address" → ✅ "This email address is missing the @ symbol"
- **No technical codes user-facing**: ❌ "HTTP 401 Unauthorized" → ✅ "Your session expired — sign in again to continue"
- **Always include next step when one exists**: ✅ "We couldn't reach our servers. Check your connection or try again in a minute."
- **Match severity**: a typo in a form is calm; a payment failure is calm but urgent; loss-of-data is calm AND careful

### Structured error pattern (modal)

```json
{
  "code": "PAYMENT_DECLINED",
  "title": "Your payment didn't go through",
  "body": "The card we have on file was declined. This might be a temporary hold by your bank, or the card may need updating.",
  "primaryAction": "Update card",
  "secondaryAction": "Try a different card"
}
```

The `code` stays in logs / dev console. User sees `title` + `body` + buttons.

### Common error templates

| Situation | Title | Body |
|---|---|---|
| Network failure | `We couldn't reach our servers` | `Check your connection or try again in a minute.` |
| Auth expired | `Your session expired` | `Sign in again to continue where you left off.` |
| Permission denied | `You don't have access to this` | `Ask {workspace_admin} for the right role.` |
| Validation (email) | `This email is missing the @ symbol` | (inline; no body needed) |
| Payment declined | `Your payment didn't go through` | `The card we have was declined. Try a different card or update payment details.` |
| Rate limited | `Slow down a bit` | `You're making too many requests. Try again in a few seconds.` |
| Generic 500 | `Something on our end broke` | `Our team's been notified. Refresh and try again, or come back in a minute.` |

---

## Empty states

Shown when there's no data yet — first-time use, filtered view with no matches, completed/dismissed list.

### Shape

```
{Heading — what's missing OR what's possible}
{Body — context + invitation}
{Primary CTA — the action to fill the empty space}
{Secondary CTA — alternative (often "Learn more" or "Import")}
```

### Length budget

- Heading: ≤ 6 words
- Body: ≤ 25 words
- Primary CTA: ≤ 4 words

### Rules

- **Don't apologize for emptiness**: ❌ "Sorry, nothing here yet" → ✅ "Your first project goes here"
- **Make it inviting, not embarrassing**: empty state is opportunity to do the next-good thing
- **Anchor to the user's action context**: if they filtered → "No matches for '{query}'"; if they're new → "Start by adding your first {item}"

### Common templates

| Situation | Heading | Body | CTA |
|---|---|---|---|
| First-time (no data) | `Your first {item} goes here` | `Start by adding one — it takes about 30 seconds.` | `Add {item}` |
| Filtered (no matches) | `No matches for "{query}"` | `Try a broader search, or clear the filters.` | `Clear filters` |
| Completed list | `You're all caught up` | `Nothing left in your queue. Take a break.` | `Add new` |
| No notifications | `No notifications yet` | `When something happens, you'll see it here.` | (no CTA) |
| No team members | `Your team is just you` | `Invite a teammate to share the workspace.` | `Invite` |

---

## Tooltips

Hover-or-focus reveal of additional context.

### Length budget

- ≤ 12 words
- One sentence max
- Plain language, no jargon (the tooltip is for clarification — use jargon and it's still confusing)

### Rules

- **Don't restate the label**: if the button says `Export`, the tooltip should NOT be `Export this`. Add value: `Export the filtered list as CSV`.
- **Don't be a help article**: tooltips are quick orientation. Longer info goes in a `?` modal or help link.
- **Avoid placeholders**: if the tooltip says `Click for more info`, delete it.

### Common templates

| Element | Tooltip |
|---|---|
| `Export` button | `Export the filtered list as CSV` |
| `Star` icon | `Save to favorites` |
| `?` next to a field | `Why we ask: we use this to send password reset emails.` |
| Username letter avatar | `{User's name} — {role}` |
| Status badge | `{State} since {date}` |

---

## Helper text (form fields)

Below a field, gives format / context / why.

### Length budget

- ≤ 15 words
- One short sentence

### Rules

- **Tell them what to enter**: ✅ `Use the email tied to your account`
- **Tell them why**: ✅ `Used for two-factor authentication only`
- **Show format if non-obvious**: ✅ `Format: +1 555 123 4567`
- **Don't restate the label**: ❌ Label `Phone`, helper `Enter your phone`

### Common templates

| Field | Helper text |
|---|---|
| Email (signup) | `We'll send a confirmation to this address.` |
| Password (signup) | `8+ characters, with a number or symbol.` |
| Phone | `Format: +1 555 123 4567 — used for two-factor only.` |
| Domain | `Your team accesses the workspace at this URL.` |
| API key name | `So you can identify this key later (e.g. "prod-server").` |

---

## Modals (confirmation / info)

### Confirmation modals (destructive action)

```
Title: {What's about to happen}, framed as a question OR clear statement
Body: {Consequence — what will be lost, who will be affected}
Primary: {The action verb} (destructive — red usually)
Secondary: {Cancel}
```

### Length budget

- Title: ≤ 8 words
- Body: ≤ 50 words
- Primary action: ≤ 3 words

### Rules

- **Spell out the consequence**: ✅ `This will permanently delete the project, including all 247 tasks and 12 attachments.`
- **Match the primary button to the action**: if it's "Delete project", the body should be about deletion, the button should say `Delete` not `OK`
- **Don't double-confirm common destructive actions**: deleting a draft doesn't need a modal; deleting an archive does

### Common templates

| Action | Title | Body | Primary |
|---|---|---|---|
| Delete project | `Delete "{Project name}"?` | `This permanently removes the project and all 247 items inside it. This can't be undone.` | `Delete project` |
| Sign out | `Sign out?` | `You'll need to sign back in to access your workspace.` | `Sign out` |
| Discard changes | `Discard changes?` | `Your unsaved changes will be lost.` | `Discard` |
| Cancel subscription | `Cancel subscription?` | `Your account remains active until {date}. After that, your data is archived for 90 days, then permanently deleted.` | `Cancel subscription` |

---

## Inline alerts / banners

In-page warnings, info, errors, success — usually appears above content.

### Length budget

- 1-2 sentences max
- ≤ 30 words
- Strong action when relevant

### Variants

- **Info banner**: announcing something new (`New: filter saved searches`)
- **Warning banner**: something needs attention (`Your trial ends in 3 days — add payment to keep going`)
- **Error banner**: page-level problem (`We couldn't load your data — try refreshing`)
- **Success banner**: confirmation of completed action (`Settings saved`)

---

## Toast notifications

Brief, auto-dismissing confirmation or info.

### Length budget

- ≤ 15 words
- One sentence

### Rules

- **For success**: confirm action + (optionally) undo: `Project saved. Undo?`
- **For info**: be specific: `New comment from {Person} on {Task}`
- **For warning**: include next step: `Connection lost. Reconnecting...`
- **Avoid for errors**: errors usually need persistence; use inline alert or modal

---

## Onboarding cards (multi-step)

Sequential explanation of a feature.

### Length budget

- Card heading: ≤ 8 words
- Card body: ≤ 35 words
- Per step

### Rules

- **One concept per card**: don't try to explain everything in step 1
- **Anchor visually**: each card should reference what the user can see on screen
- **Active verb in the heading**: `Connect your first integration` not `Integrations`

---

## 404 / 500 / Offline pages

Full-page error states.

### Shape

```
{Big visual / illustration}
{Headline — what happened, friendly}
{Body — 1-2 sentences with context}
{Primary action — usually back home, search, or retry}
{Optional secondary action}
```

### Length budget

- Headline: ≤ 6 words
- Body: ≤ 40 words
- Buttons: 1-3 words

### Common templates

| Page | Headline | Body | Primary |
|---|---|---|---|
| 404 | `This page doesn't exist` | `The link might be broken, or the page might have moved.` | `Back to home` |
| 500 | `Something broke on our end` | `Our team's been notified. Refresh in a minute, or come back later.` | `Refresh` |
| Offline | `You're offline` | `Check your connection — we'll reconnect automatically when you're back.` | (no CTA, auto-reconnect) |
| Maintenance | `We're doing some maintenance` | `Back in about 30 minutes. Sorry for the interruption.` | (no CTA) |

---

## Quick element-type picker

If you don't know what type of microcopy to write, ask:

1. What's the element's visible role on the page? (button / banner / modal / etc.)
2. What did the user just do (or fail to do)?
3. What's the next action they can take?
4. Is this state temporary (toast) or persistent (inline alert) or page-level (404 page)?

Once you know these, the right template falls out.

---

## RU patterns per element

RU-микрокопия живёт по тем же length-budget'ам, что и EN. Меняется регистр (формальный vs дружеский), типографика и форма обращения. Эта секция — overlay поверх английских правил.

### Универсальные RU-правила

- **Обращение «вы»** в формальных продуктах (банковский, страховой, гос, B2B-enterprise) — всегда, со строчной буквы внутри предложения, с заглавной — только в персонализированных welcome-сообщениях по имени.
- **«Ты»** — допустимо в потребительских продуктах для молодой аудитории (Spotify-RU, Яндекс.Музыка, фитнес-приложения), но должно быть консистентно по всему продукту.
- **Кавычки** — внутри продукта используются «ёлочки», внутри них (при двойной вложенности) — „лапки“. Не использовать "программистские кавычки" в готовом UI-тексте.
- **Тире** — длинное тире (em-dash) « — » с пробелами в RU, не дефис « - ». В коде и пути файла — обычный hyphen.
- **Числа** — пробелы между разрядами через неразрывный пробел: `1 200 ₽`, `247 проектов`. Знак рубля после числа с пробелом.
- **Восклицания** — ещё более строго, чем в EN. В RU «!» воспринимается как давление или фамильярность. Использовать ТОЛЬКО для празднования первого достижения. Никогда — в ошибках, тостах, помощи.
- **Капс** — почти всегда нет. RU-капс читается как крик. Исключения: коды состояний (200, 401), технические обозначения (ID, URL).
- **Эмодзи** — допустимы в empty-state и онбординге для дружеских продуктов; никогда в ошибках; никогда в B2B-enterprise. Тон-маркер сильнее, чем в EN.

### Buttons — RU

| Действие | EN | RU дружеский | RU формальный |
|---|---|---|---|
| Primary save | Save | Сохранить | Сохранить |
| Submit form | Submit / Send | Отправить | Отправить |
| Continue | Continue / Next | Дальше | Продолжить |
| Cancel | Cancel | Отмена | Отменить |
| Delete | Delete | Удалить | Удалить |
| Discard | Discard | Не сохранять | Отклонить изменения |
| Confirm | I understand / Got it | Понятно | Подтвердить |
| Sign in | Sign in | Войти | Войти |
| Sign up | Sign up | Создать аккаунт | Зарегистрироваться |
| Add member | Add member | Добавить участника | Пригласить участника |

Правила:
- Глагол первым, как в EN: «Отправить приглашение», не «Приглашение отправить».
- «Пожалуйста» в кнопках — никогда (даже более жёстко, чем EN «no please»).
- «ОК» — то же, что в EN: избегать для деструктивных действий, использовать «Удалить аккаунт», не «ОК».

### Error messages — RU

Формальный регистр (банки, B2B):
> **Сессия истекла**
> Войдите снова, чтобы продолжить работу.

Дружеский регистр (потребительский SaaS):
> **Что-то пошло не так с подключением**
> Проверьте интернет и попробуйте через минуту.

Правила:
- Никогда «Ошибка!» с восклицанием — это давление. «Что-то пошло не так» / «Не удалось ...» — мягче и точнее.
- Никогда «Вы ввели неправильно» — те же anti-blame правила, что в EN. «Здесь не хватает символа @» / «Похоже, в адресе нет @».
- Технические коды (HTTP 401, ERR_NETWORK) — не показываем пользователю. Они уходят в логи.
- «Пожалуйста, попробуйте снова» — канцелярит, режется. Просто «Попробуйте снова» или конкретное действие.

### Empty states — RU

Дружеский:
> **Здесь появятся ваши проекты**
> Добавьте первый — это займёт около 30 секунд.
> [Добавить проект]

Формальный:
> **Проектов пока нет**
> Создайте первый проект, чтобы начать работу.
> [Создать проект]

Правила:
- «Извините, ничего не найдено» — режется. «Ничего не найдено по запросу "{query}"» — нейтрально.
- «Список пуст» — не извинение, а констатация. Дальше — приглашение к действию.

### Tooltips и helper text — RU

- Максимум 12 слов, как в EN.
- Если EN-тултип использует короткие глагольные конструкции («Save to favorites»), RU вариант часто длиннее на 1-2 слова из-за русского словообразования («Сохранить в избранное»). Это нормально — длина не overflow'ит.
- Не повторять лейбл кнопки. Если кнопка «Экспорт», тултип — «Скачать отфильтрованный список в CSV», не «Экспортировать данные».

### Onboarding и success-сообщения — RU

- В RU онбординге «Добро пожаловать!» — допустимо с восклицанием (это и есть «genuine celebration»). Но только в первом шаге.
- «Поздравляем!» — допустимо для первого достижения. На рутинные действия — нет.
- «Готово» / «Сохранено» / «Отправлено» — без точки в конце для тостов, как и в EN.

### 404 / 500 / offline — RU

| Page | Friendly RU | Formal RU |
|---|---|---|
| 404 | «Такой страницы нет» / «Ссылка не работает или страница переехала.» | «Страница не найдена» / «Запрошенная страница не существует.» |
| 500 | «У нас что-то сломалось» / «Команда уже знает. Обновите через минуту.» | «Произошла внутренняя ошибка» / «Мы уже работаем над её устранением.» |
| Offline | «Нет интернета» / «Подключитесь к сети — мы продолжим автоматически.» | «Отсутствует подключение к сети» |
| Maintenance | «У нас профилактика» / «Вернёмся примерно через 30 минут.» | «Технические работы» / «Ориентировочное время восстановления — 30 минут.» |

Дружеский — для потребительских продуктов, контент-площадок, образовательных. Формальный — банки, гос, корпорат-B2B, медицина.

### Voice по типу продукта — RU

| Тип продукта | Тон | Обращение | Эмодзи |
|---|---|---|---|
| Банк / страхование | Формальный | «вы» с маленькой | Нет |
| Гос / госуслуги | Формальный | «вы» с маленькой | Нет |
| B2B enterprise | Формально-нейтральный | «вы» | Минимум |
| B2B SaaS (стартап) | Friendly-professional | «вы» | Изредка |
| Потребительский SaaS | Friendly | «вы» / «ты» (выбрать одно) | Допустимо |
| Образование / контент | Friendly | «ты» в детских; «вы» во взрослых | Допустимо |
| Игры | Casual | «ты» | Да |
| Финтех (Тинькофф-стиль) | Friendly-direct | «вы» | Дозированно |
