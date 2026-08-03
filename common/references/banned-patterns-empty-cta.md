# Banned patterns — empty CTAs

Shared anti-patterns across `landing-copy` and `microcopy`. The base linter
catches the regex-detectable subset under `EMPTY_CTA` (see
`skills/writer/scripts/lint.py`).

A CTA's job is to commit the reader to a specific next action. Empty CTAs
default the click to a vague verb that could mean anything; users either ignore
them or, worse, click and then bounce when the destination doesn't match the
implicit promise.

## EN — banned CTAs

| Banned | Why | Replace with |
| --- | --- | --- |
| Click here | "Here" carries no information; the link text should describe the destination | "Read the API spec" / "See the v4.2 changelog" |
| Tap here | Same as above | Verb + object |
| Learn more | Generic; what's the user about to learn? | "Learn how teams of 5+ use it" / "See pricing" |
| Read more | Cut sign that the headline didn't hook | Either commit to the topic ("Read the postmortem") or remove the link entirely |
| Get started | Without "with X", the reader doesn't know what they're starting | "Get started — free 14-day trial" / "Set up your first project" |
| Find out more | See "Learn more" | Specific verb |
| Submit | (Forms) implies bureaucratic submission rather than user value | "Save changes" / "Sign up" / "Apply discount" |

## RU — пустые CTAs

| Banned | Замена |
| --- | --- |
| Нажмите здесь | глагол + объект ("Скачать гайд") |
| Нажмите сюда | глагол + объект |
| Узнайте больше | конкретная тема ("Тарифы" / "Как работает интеграция") |
| Узнайте подробнее | конкретная тема |
| Подробнее | "Тарифы" / "Документация" / "Что нового в v4.2" |
| Перейти | глагол + куда ("Перейти к настройкам") |

## Verb-first rule

The first word of a CTA is the most important. It should be a **specific verb**
that names the action, not a meta-verb like "click", "tap", "submit", or
"continue".

| Specific verb | Use case |
| --- | --- |
| Read | content (blog post, doc page, changelog) |
| Watch | video, recorded demo |
| Compare | pricing tables, feature matrices |
| Start | free trial, onboarding flow |
| Book | demo, call, slot |
| See | example, sample, case study |
| Try | interactive demo, sandbox |
| Get | a specific artifact (PDF, template, checklist) |

## When `Get started` is OK

`Get started` is acceptable when **followed by an object**:

- "Get started with the API" ✓
- "Get started — free trial" ✓ (the em-dash adds context)
- "Get started" alone ✗ (linter catches this)

The base linter's regex requires no immediate `with X` qualifier; bare
`Get started` triggers `EMPTY_CTA`.

## Microcopy-specific notes

For buttons inside applications (vs marketing pages), the same rules apply but
the budget is tighter:

- Aim for **≤3 words**, ideally 1-2 verbs
- Match the user's mental model ("Save draft" not "Submit form")
- Don't use "OK" or "Yes" alone in destructive-action confirmations — name the
  destruction ("Delete account")

See `skills/microcopy/references/element-types.md` for the full per-element budget.
