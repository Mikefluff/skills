---
title: "Write error messages for a payment flow"
persona: "PM filling out an error-states matrix for Stripe checkout"
time: "15-20 minutes"
skills:
  - microcopy
  - writer
---

# Six error states for a Stripe checkout flow

Сценарий: ты — PM, релизишь payment update в SaaS-продукте. Engineer спрашивает: «дай мне финальные строки для шести error states — что пишем, когда платёж падает». Нужны строки, которые не блеймят пользователя, не звучат как сгенерённые ChatGPT'ом, всегда дают следующий шаг и помещаются в 2 строки модала.

Это работа для `microcopy`. Скилл собирает по фиксированным правилам с per-state длинными budget'ами и банлистом UX-clichés.

## Intent — три правила, которые применяются всегда

1. **Не блеймь пользователя.** «You entered an invalid card» — bad. «We couldn't validate this card» — better. «That card didn't go through — try another, or contact your bank» — best.
2. **Не используй жаргон.** «401 Unauthorized», «SSL handshake failed», «Quota exceeded» — это не для user-facing. Скилл переводит на plain language.
3. **Всегда давай следующий шаг.** Error без next-step = тупик. Скилл refuse'ит финализировать строку без actionable continuation.

Плюс per-element length budgets (см. `skills/microcopy/references/length-budgets.md`):

- Modal error title — 4-7 слов
- Modal error body — ≤ 20 слов
- Inline field error — ≤ 12 слов
- Toast notification — ≤ 15 слов

## Setup

Скилл установлен. EN-only по дефолту. Состояния перечислены в `skills/microcopy/references/element-types.md`.

## Step 1. Define the matrix

```
/microcopy error-states checkout-flow
```

Скилл просит matrix. Ты передаёшь шесть состояний:

```
1. network — connection lost mid-submit
2. auth-expired — session expired between page-load and submit
3. payment-declined — card was rejected by issuer
4. quota — user hit free-tier transaction limit
5. validation — wrong CVV format
6. server-500 — backend died, not user's fault
```

Для каждого состояния скилл собирает 4 поля: title / body / primary CTA / secondary CTA (или dismiss).

## Step 2. Concrete brief per state

Скилл хочет минимальный context per state:

```
1. network — what user was doing: «submitting card details for $49 subscription»
2. auth-expired — what user sees right before: «card form, submit clicked»
3. payment-declined — issuer codes available? «yes — code 51 insufficient_funds, code 05 do_not_honor, etc.»
4. quota — what's the plan? «free tier: 5 transactions/month, upgrade is $19/mo»
5. validation — which field? «CVV — 3 digits, user entered 4»
6. server-500 — anything user can do? «no, autoretry in 30s»
```

## Step 3. The six finals

Скилл применяет правила + writer-pass:

### 1. network

```
TITLE       Connection dropped
BODY        We didn't process the payment. Your card wasn't charged. Try again
            when you're back online.
PRIMARY     Retry
SECONDARY   Cancel
```

Why: «didn't process» (не блейм юзера), «card wasn't charged» (snap anxiety), «try again when back online» (next step + cause).

### 2. auth-expired

```
TITLE       Sign in to continue
BODY        Your session expired while you were filling out the form. Sign in
            again — we kept your details.
PRIMARY     Sign in
SECONDARY   —
```

Why: «sign in» (action не «authenticate»), «we kept your details» (anxiety snap — they don't lose 5 minutes of typing), no secondary CTA (no escape — they need to sign in).

### 3. payment-declined

```
TITLE       That card didn't go through
BODY        Your bank declined the charge. Try a different card, or contact
            your bank — sometimes they flag online payments by mistake.
PRIMARY     Try another card
SECONDARY   Contact support
```

Why: «that card didn't go through» (passive, doesn't blame the user, doesn't blame the card), «sometimes they flag by mistake» (gives benefit of doubt — maybe issuer false-positive, maybe insufficient funds, framing is neutral), two CTAs because user can self-serve or escalate.

Issuer code 51 / 05 / etc. — скилл deliberately NOT exposing к user. Internal team может ловить per-code и varying body, но default — generic, friendly, non-blame.

### 4. quota

```
TITLE       You're on the free plan
BODY        You've used all 5 free transactions this month. Upgrade to Pro
            ($19/mo) for unlimited, or wait until next month.
PRIMARY     Upgrade to Pro
SECONDARY   Maybe later
```

Why: «you're on the free plan» (statement, not accusation — «you exceeded» = blame), specific number («5», not «your limit»), specific price («$19/mo», not «affordable»), two paths (upgrade OR wait — agency), «Maybe later» (not «Cancel» — quota isn't an error you cancel).

### 5. validation

```
TITLE       —  (inline field error, no modal)
INLINE      CVV is 3 digits — usually on the back of your card.
```

Why: inline only (не модал — too much friction for a typo), «3 digits» (specific), «usually on the back» (helpful, not condescending), no «invalid» / «incorrect» — that's redundant с inline error itself.

### 6. server-500

```
TITLE       Something broke on our end
BODY        We're already looking at it. Your card wasn't charged. We'll
            retry in a moment — you can stay on this page.
PRIMARY     —  (no CTA, auto-retry)
SECONDARY   Contact support
```

Why: «on our end» (explicit ownership — это критично), «card wasn't charged» (anxiety snap), «we're already looking» (signals incident response without overclaiming SLA), «stay on this page» (anchor against tab-close), no primary CTA (auto-retry, no manual action needed).

## Step 4. Banned patterns scanner

Скилл прогоняет финалы через banlist (см. `skills/microcopy/references/banned-words.md`):

- «Oops!» / «Whoops!» — infantilizing
- «Something went wrong» — generic, useless without specifics
- «Please try again» — без объяснения почему
- «Error: 500» / status codes in user-facing copy
- «Invalid input» — say what's invalid
- «Permission denied» — say what permission, how to get it
- «Loading...» c эллипсисом на error (это loader, не error)
- «We're sorry but...» — apology pile-up
- «Unfortunately» — softener that adds words, no value

Если в финалах bot-tells остались — writer-pass их режет в финале.

## Step 5. Tone consistency across states

Скилл финиширует с tone audit:

```
Tone audit — checkout-flow error states (6 states)
  - first-person ratio: 50% (we/we're)
  - second-person ratio: 50% (you/your)
  - apology count: 0 ✓
  - blame-language count: 0 ✓
  - banned-pattern hits: 0 ✓
  - average title length: 5.0 words ✓ (budget 4-7)
  - average body length: 17.3 words ✓ (budget ≤20)
  - "card wasn't charged" repeated in 3 states ✓
    (anxiety-snap pattern — keep consistent)
```

Если ratio / lengths off — скилл предлагает adjustments.

## Когда НЕ использовать microcopy

- **Long-form help article / docs** — это не microcopy. Используй `essay-write` или прямую writing.
- **Marketing copy** — другие правила (см. `landing-copy`). Hero ≠ error state.
- **Legal copy (ToS / privacy)** — legal должен пилотировать legal, не microcopy skill.
- **Локализация уже написанных строк** — другая работа. Microcopy пишет источник, не локализует.

## Troubleshooting

### Engineer wants the technical code in the body

«They asked for `(code: 51)` so they can debug» — fair, но не в primary body. Скилл предлагает шаблон: основной user-facing body + collapsed «Technical details» секция (revealed via «Show details» link). Полная схема в `skills/microcopy/references/rules.md`.

### Body превышает 20 слов и не сжимается

Скорее всего ты сочетал две задачи в одном error. Split. Например: payment-declined separately от «contact your bank with this reference number». Two states, two error messages.

### Все шесть финалов «звучат одинаково»

Это deliberate — consistent tone across states. Если хочется variation: разные verbs (try / retry / sign in / upgrade), разные anchor phrases. Скилл сам diversifies verbs but anchors («card wasn't charged») держит consistent.

### Локализация ломает length budgets

DE / FR / RU длиннее EN на 20-40%. Если строка fits EN budget но breaks DE — переписать на shorter EN явно: добавь `--target-langs en,de,fr`. Скилл будет cap'ить под worst language.

## Related

- [tone-shift.md](tone-shift.md) — если у тебя уже есть errors, но wrong register
- [landing-launch.md](landing-launch.md) — где microcopy используется параллельно (404 / forms / FAQ)
- [release-notes-saas.md](release-notes-saas.md) — родственная задача с разделением user / dev audiences
- [skills/microcopy/references/length-budgets.md](../../skills/microcopy/references/length-budgets.md) — все per-element budgets
