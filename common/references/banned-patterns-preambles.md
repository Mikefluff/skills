# Banned patterns — excitement preambles

Shared anti-patterns across `cold-email`, `landing-copy`, and `release-notes`.
The base linter catches the regex-detectable subset under `WEAK_OPENER`
(see `skills/writer/scripts/lint.py`).

Preambles delay the change. The reader wants to know what shipped (release
notes), what you do (landing copy), or what you want (cold email) — not how
you feel about telling them.

## EN — banned openers

**Excitement preambles** (release notes / landing / outreach):

- "We're excited to announce …"
- "We're thrilled to share …"
- "We're proud to introduce …"
- "We're delighted to present …"
- "We're pleased to inform you that …"
- "We're happy to let you know …"

**Email-greeting preambles** (cold email):

- "I hope this email finds you well."
- "I hope you're doing great."
- "Trust this email finds you in good spirits."
- "Hope all is well."
- "Hope you're doing well!"
- "I just wanted to reach out about …"
- "I'm reaching out because …"

**Rule:** start with the change, the value, or the question. The reader will
infer your excitement from the substance.

## RU — banned openers

- «Мы рады сообщить, что …»
- «С гордостью представляем …»
- «С удовольствием объявляем …»
- «С радостью сообщаем …»
- «Я искренне надеюсь, что это письмо застанет вас в добром здравии …»
- «Просто хотел написать вам по поводу …»
- «Пишу вам, чтобы …» (when it's the first sentence — be specific instead)

**Правило:** начинайте с изменения, ценности, или вопроса. Эмоции читателю
не нужны — нужен предмет.

## Why this matters

LLMs default to preambles because they pad token count without committing to a
claim. Human readers parse the first 10 words as the most important; if those
10 words are "we're excited to announce a new" the actual headline is buried.

For release notes specifically: the changelog row is itself the announcement.
Adding "we're excited" duplicates information and signals AI-generated tone.

## Rewrite patterns

| Before | After |
| --- | --- |
| We're excited to announce v4.2 ships native dark mode. | v4.2 ships native dark mode. |
| We're proud to launch a new dashboard. | New dashboard: live ARR, MRR delta, per-segment churn. |
| Hope this finds you well — wanted to reach out about a collaboration. | Saw your team's open-source rate-limiter — we built the consumer side, want to compare notes? |
| Мы рады представить новую функцию: умные напоминания. | Умные напоминания: триггер по контексту звонка, не по календарю. |

## What's NOT banned

- Genuine first-time greeting in a personal email to a friend or colleague.
- "Thanks for joining" / "Thanks for your patience" in **transactional**
  messages where the sentiment is the substance.
- Formal templates required by HR / legal / regulatory tone — note those as
  explicit overrides in the project's style guide.
