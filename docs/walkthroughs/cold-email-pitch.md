---
title: "Cold-pitch a VC for a seed round"
persona: "Founder reaching out to an investor for the first time"
time: "10-15 minutes"
skills:
  - cold-email
  - writer
---

# A cold email to a VC partner that gets read

Сценарий: ты — founder. Подняла seed, нашла Partner в Acorn Capital, которая лидила два relevant deal в твоей категории за последние 12 месяцев. Хочешь one-shot first-touch письмо. Не пять страниц «hope this finds you well». Не выпрашивающий тон. Не AI-fluff про «exciting opportunity». Просто понятное «вот мы, вот тяга, можно поговорить?».

Это работа для `cold-email`. Скилл собирает по фиксированной 5-блочной структуре с ≤120-word budget и банлистом ceremonial patterns.

## Intent — что значит «cold» по правилам скилла

Cold = no prior context. Ты не представлена, не commented on their podcast, не attended their portfolio event. Если есть warm intro — это другой жанр (см. `intro-request` subskill).

Cold email должен сделать три вещи в первом абзаце:

1. Доказать, что ты прочитала, кто они (one specific datapoint)
2. Дать им основание прочитать ещё 60 секунд (one specific traction signal)
3. Сделать easy yes (one specific small ask)

Если не получается в первом абзаце — письмо не работает.

## Setup

Скилл установлен. EN-only (по дефолту — большинство VC outreach на английском). Если нужен RU — pass `--lang ru`, но банлист короче и less battle-tested.

## Step 1. Invoke with target

```
/cold-email first-touch "Sarah Chen at Acorn Capital"
```

Скилл сразу задаст 4 вопроса (без них ничего не пишет):

```
1. Why this investor specifically? (one sentence, one specific fact about them)
2. What's your hook for them? (one sentence — the strongest traction signal)
3. What's the ask? (15 min call / deck review / specific question / intro to portfolio CEO)
4. Any prior contact? (event / mutual / Twitter reply / nothing)
```

Если ты отвечаешь vague («I think she invests in fintech» — too generic), скилл толкает обратно: «name a specific portfolio company or specific public statement». Cold email с generic «I see you invest in fintech» — мёртвое письмо.

## Step 2. The 5-block structure

Скилл строит по фиксированным блокам (см. `skills/cold-email/references/structure.md`):

```
SUBJECT
{6-10 words, no clickbait, no "quick question", no all-caps}

BLOCK 1 — HOOK (≤25 words)
{the one specific fact about them + the relevance signal}

BLOCK 2 — VALUE / TRACTION (≤35 words)
{what you're building + the strongest number/proof}

BLOCK 3 — ASK (≤15 words)
{specific small ask — NOT "thoughts?" or "would love to chat"}

BLOCK 4 — EASY YES (≤15 words)
{the lowest-friction path to yes: deck link, calendar link, "no need to reply"}

BLOCK 5 — SIGN-OFF (≤10 words)
{name, role, company, no signature blocks with logos}
```

Word budget total: ≤120 в теле письма (excluding subject + sign-off).

## Step 3. The banned patterns

Скилл автоматически режет:

- «Hope this finds you well» / «Hope you're having a great week»
- «I'll keep this brief» — потом не keeping it brief
- «I came across your profile» / «I noticed you...»
- «Exciting opportunity» / «game-changing» / «revolutionary»
- «Quick question» в subject (overused, signals spam)
- «Just following up» (use в follow-up, не в first-touch)
- «Touching base» / «circling back» (corporate ceremony)
- Three-paragraph wind-up before the actual ask
- Emoji в subject line (одно exception — direct industry signal, e.g. ⚡ для energy)

Если ты вставляешь banned phrase вручную, writer-pass его снимает в финале.

## Step 4. Concrete before / after

Answers fed to the skill:

1. **Why Sarah specifically?** — «She led Plaid's Series A and wrote a 2024 thesis on embedded compliance for SMB fintech.»
2. **Hook?** — «We have 47 paying SMBs, $112K MRR after 5 months, 18% MoM growth, zero churn.»
3. **Ask?** — «15 min intro call this/next week, link below.»
4. **Prior contact?** — «None.»

Output (illustrative, post-`writer`):

```
Subject: Embedded compliance for SMBs — 47 customers, $112K MRR

Sarah —

Your 2024 thesis on embedded compliance for SMB fintech is the clearest writeup
I've found on what we're building.

We launched Ledger Guard in December — automated SOC 2 and KYC workflows for
fintech SMBs. Five months in: 47 paying customers, $112K MRR, 18% MoM growth,
zero churn.

Open to a 15-minute call this or next week?

Deck (5 slides, no login): ledgerguard.co/sarah
Calendar: cal.com/maya/15

— Maya Patel, founder, Ledger Guard
```

Word count (body): 78 words. Word budget: 120. Spend conservative — leaves room for one specific fact about Sarah's recent tweet/podcast if you have one.

## Step 5. Review pass — read it like the recipient

`cold-email` финиширует с self-review checklist (auto-printed):

```
✓ Subject line ≤ 10 words, no clickbait? YES
✓ Block 1 names one specific fact about recipient? YES
✓ Block 2 has one specific number? YES (3 numbers, 1 too many — consider cutting)
✓ Ask is specific and small? YES (15 min call)
✓ Easy yes (link)? YES (deck + calendar)
✓ No banned ceremony patterns? PASS
✓ Total body ≤ 120 words? YES (78)
⚠ Three numbers in Block 2 — recipient retains one. Consider cutting MoM or churn.
```

Это не auto-edit — это hint. Ты решаешь, оставить ли три числа или резать до двух.

## Когда НЕ использовать cold-email

- **Есть warm intro** — другой жанр. Используй `cold-email intro-request` для запроса intro, а follow-up после intro — обычное письмо без skill.
- **Это follow-up на ранее отправленное** — `cold-email follow-up`. Другие правила (не повторять hook, добавить one new datapoint).
- **B2B sales email (sales rep → buyer)** — другие правила; cold-email tuned for founder→investor, операционал → специалист, не для SDR pipeline.
- **Mass-personalized template (10 recipients at once)** — скилл против variable substitution в hook'е. Если ты пишешь 10 писем с {{firstname}} — это spam, не cold-email.

## Troubleshooting

### Скилл отказывается писать без specific datapoint про recipient

Это by design. Cold email без specific fact = spam. Если нечего сказать про recipient — либо research больше, либо don't send. См. `skills/cold-email/references/structure.md`.

### Hook не получается узким — слишком много traction signals

Выбери один. Самый сильный. MRR > customers > growth-rate > funding > press. Скилл будет настаивать: один номер в hook, остальные в Block 2.

### Письмо в плане «excited to share» / «would love to learn»

Это default LLM mode. Запусти `re-run writer-pass strict` — writer срубит. Или просто скажи: «no first-person enthusiasm verbs (excited/thrilled/eager/passionate)». Скилл honors custom bans.

### Subject line получился generic («Introduction», «Hello from {company}»)

`rewrite subject — specific outcome or specific number`. Хороший subject = частичный TL;DR письма. Bad: «Introduction». Good: «47 SMB customers, asking for 15 min».

## Related

- [tone-shift.md](tone-shift.md) — если уже есть draft, но wrong register
- [microcopy-error-states.md](microcopy-error-states.md) — родственная задача с word budgets
- [viral-post.md](viral-post.md) — broadcast version (1→many) того же impulse
- [skills/cold-email/references/structure.md](../../skills/cold-email/references/structure.md) — полная схема 5-блочной структуры
