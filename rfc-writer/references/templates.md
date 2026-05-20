# Templates

Full section structures per document type. Use these as scaffolds — fill each section; delete sections that genuinely don't apply.

---

## RFC template

```markdown
# RFC-XXXX: {short title — verb + object}

**Status**: Proposed
**Author**: {name + email}
**Created**: 2026-05-20
**Updated**: —
**Discussion**: {link to PR / mailing list thread / Slack channel}

---

## Summary

{1-3 sentences. What is being proposed. Read by people deciding whether to read further.}

## Motivation

{Why we're considering this change. The problem we're trying to solve. Concrete evidence:
- User complaints / support tickets
- Performance data
- Security findings
- Strategic priorities
}

## Detailed proposal

{The bulk of the RFC. What we propose to build / change / remove. Concrete enough that a reader can imagine the result.

Sub-sections as needed:
- ### API changes
- ### Data model
- ### Migration plan
- ### Backwards compatibility
- ### Security considerations
}

## Alternatives considered

### Alternative 1: {name}

{Description. Why it was considered. Why it wasn't chosen.}

### Alternative 2: {name}

{Same shape.}

### Alternative 3: do nothing

{The null case. What happens if we don't change anything. Often surfaces hidden assumptions.}

## Consequences

### Positive

- {What this enables or improves}
- {Specific metric or capability gained}

### Negative

- {What gets harder}
- {What risk is introduced}
- {Cost (time, infra, complexity)}

### Mitigations

- {How we handle each negative}
- {Fallback plans / rollback strategy}

## Adoption plan

{How we get from current state to proposed state. Phased rollout? Feature flag? Migration tooling? Estimated timeline.}

## Open questions

- {Question 1 — what's still unknown}
- {Question 2}

## References

- {Prior RFCs}
- {Related code / docs}
- {External references / vendor docs / academic papers}
```

---

## ADR template

```markdown
# ADR-NNNN: {short title — decision + subject}

**Status**: Accepted | Proposed | Deprecated | Superseded by ADR-MMMM
**Date**: 2026-05-20
**Authors**: {names}

## Context

{1-2 paragraphs. What's the situation? What forces are at play? Enough context that a reader 5 years later can understand WHY this decision needed to be made.}

## Decision

{The decision, stated in present tense. "We will use PostgreSQL." not "We decided to..." or "We are going to...".

Be specific:
- "We will use PostgreSQL 16+ as the primary OLTP database for the X service"
NOT:
- "We will use a relational database" (too vague)
}

## Consequences

{What follows from this decision. Both good and bad. Future-tense for what's coming.}

- Positive: {what this enables}
- Negative: {what trade-off we accept}
- Risk: {what could go wrong; how we'd notice}

## Considered alternatives

### {Alternative 1}
{Why we considered it. Why we didn't pick it.}

### {Alternative 2}
{Same.}

(Keep this brief — ADR is short. Just the alternatives that were genuinely considered.)

## References

- {Link to the prior RFC if there was one}
- {Related ADRs}
```

### Real ADR example (shape only)

```markdown
# ADR-0003: Use JWT for stateless auth between services

**Status**: Accepted
**Date**: 2026-04-15
**Authors**: A. Petrov, B. Smith

## Context

The X service makes 200+ requests per second to the Y service. Each request requires
verifying the caller's identity. Currently, Y service calls back to the auth service to
verify a session token — adding ~30ms latency per request and creating a single point
of failure when auth service is degraded.

## Decision

We will use signed JWTs (RS256, 5-minute TTL) issued by the auth service and verified
locally by each downstream service. Each service maintains the auth service's public
key, refreshed daily.

## Consequences

- **Positive**: 30ms latency removed per request; downstream services tolerate auth-service
  outages until the next public-key refresh
- **Negative**: token revocation has up to 5 minutes of lag (TTL); compromised tokens
  remain valid until expiry
- **Risk**: if public-key refresh fails for >24h, all auth fails. Mitigation: alert on
  refresh-failure; cache last-known-good key with 7-day grace

## Considered alternatives

### Session-per-request to auth service (status quo)
30ms latency per request is the cost; SPOF on auth service is the bigger issue.

### Opaque tokens with Redis cache
Adds Redis as a hard dependency; benefit over JWT is marginal.

### mTLS with service certificates
Operationally heavier; certificate rotation is high friction. Considered for future.

## References

- RFC-0042: Stateless auth proposal
- ADR-0001: Service-to-service security model
```

---

## Tech spec template

```markdown
# Tech Spec: {feature name}

**Status**: Draft | Approved | Building | Shipped
**Owner**: {team or individual}
**Reviewers**: {names}
**Created**: 2026-05-20
**Last updated**: —
**RFC**: {link to the RFC that decided to build this, if any}

---

## Overview

{1-3 sentences. What we're building, briefly. For context only; the RFC has the WHY.}

## Goals + non-goals

### Goals
- {What this delivers}
- {Specific functional / non-functional outcomes}
- {Performance targets}

### Non-goals
- {What this explicitly does NOT do}
- {Out-of-scope concerns}
- {Future work, not in this iteration}

Surfacing non-goals prevents scope creep. State them explicitly even if "obvious".

## Detailed design

{The bulk of the spec. How we'll build it. Concrete enough that engineers can implement.

Sub-sections as needed:
- ### API surface
  - Endpoints, method signatures, parameters, response shapes
- ### Data model
  - Schemas, indexes, migrations
- ### Sequence diagrams
  - For non-trivial flows
- ### State machines
  - For stateful entities
- ### Module boundaries
  - What goes in which service / package
}

## Edge cases + error handling

- {Edge case 1: what happens when ...}
- {Edge case 2}
- {Error: how it's surfaced / logged / retried}

## Performance + scaling

- **Targets**: {RPS, latency p50/p95/p99, throughput, memory}
- **Capacity plan**: {how we'll scale, where the bottlenecks are}
- **Benchmarks**: {what we measured, where the numbers came from}

## Security

- {Threat model — who's the attacker, what's at risk}
- {Mitigations}
- {Authn / authz approach}
- {Data classification + encryption}

## Observability

- **Metrics**: {what we'll emit}
- **Logs**: {what we'll log, log levels}
- **Traces**: {what we'll trace}
- **Alerts**: {what triggers paging}
- **Dashboards**: {what dashboards we'll build}

## Rollout plan

- **Phase 1**: {feature flag, internal users only}
- **Phase 2**: {beta, opt-in customers}
- **Phase 3**: {gradual rollout, e.g. 10% → 50% → 100%}
- **Rollback**: {how to roll back if metrics degrade}

## Open questions

- {Question 1}
- {Question 2}

## References

- {Related RFCs / ADRs}
- {Vendor docs}
- {Prior art}
```

---

## Design doc template

```markdown
# Design Doc: {problem space}

**Status**: Exploring | Refined | Shelved | Became RFC-XXXX
**Author**: {name}
**Created**: 2026-05-20
**Last updated**: —

## Problem statement

{2-5 paragraphs. What problem we're trying to solve. Concrete, with evidence:
- Specific user pain
- Numbers (complaints, lost revenue, latency)
- Competitive landscape if relevant
- Why now (timing)
}

## Goals

{High-level outcomes we want.}

## Non-goals

{Explicit out-of-scope.}

## Constraints + assumptions

- {Constraints: budget, time, team size, existing systems}
- {Assumptions: what we're assuming about users, tech, market}

State assumptions explicitly — readers may disagree and surface a hidden blocker.

## Solution space exploration

### Approach A: {name}

{Description, prototyping notes, pros / cons, rough cost estimate.}

### Approach B: {name}

{Same shape.}

### Approach C: {name}

{Same shape.}

### Hybrid / combinations

{If applicable.}

## Comparison

{Table or narrative comparing approaches across dimensions:
- Effort
- Risk
- Reversibility
- Strategic fit
- Performance
- User impact
}

## Recommendation (tentative)

{1-2 paragraphs. Which approach leans likely. Honest about uncertainty.

"I lean toward Approach B because of {reasons}, but want feedback on {open question}."}

## Open questions

- {What's still unknown}
- {What needs more research}
- {What stakeholder feedback we're missing}

## Next steps

- {Action item — research X further}
- {Action item — talk to Y team about Z}
- {Action item — once direction is clear, write an RFC}

## References

- {Internal docs, related design discussions}
- {External: papers, vendor docs, competitor analyses}
- {Prior art in the org}
```

---

## Section-naming conventions

Across all 4 doc types, use these section names exactly:

- **Summary** (RFC) / **Overview** (Tech Spec) / **Context** (ADR) / **Problem statement** (Design doc)
- **Motivation** / **Why**
- **Detailed proposal** / **Decision** / **Detailed design**
- **Alternatives considered** / **Considered alternatives**
- **Consequences**
- **Open questions**
- **References**

Consistency across docs makes them scannable for engineers who read many of them.

---

## What NOT to include

❌ A "Background" section that's just a textbook explanation of the technology you're using — link the docs instead
❌ A "Why I'm writing this" preamble — just write the thing
❌ "TL;DR" at the top of an ADR — the whole ADR IS the TL;DR
❌ "We will see in the future" — put it in Open Questions
❌ Marketing language — strip on sight
❌ Code samples longer than ~30 lines without a reason — link a gist or PR instead
❌ Screenshots without captions — caption them or remove
❌ Mermaid / PlantUML diagrams without alt-text or explanation — readers may not see images

---

## RU template variants

Для команд, работающих по-русски (российские бэкенд-команды, EE/CIS-стартапы, RU-only-инженерные департаменты), все 4 шаблона выше переводятся как есть. Структура и логика — те же. Эта секция — locale-overlay.

### Важно: RFC 2119 keywords остаются на английском

Конвенция RFC 2119 (BCP 14) — глобальный стандарт. Ключевые слова `MUST`, `MUST NOT`, `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, `REQUIRED`, `RECOMMENDED`, `MAY`, `OPTIONAL` пишутся ВСЕ КАПСОМ на английском даже в полностью русском документе. Это намеренная конвенция: визуально выделяет нормативные утверждения от описательных, и обеспечивает консистентность с международными RFC.

Не переводить:
- ❌ «Клиенты ДОЛЖНЫ отправлять заголовок Authorization» — выглядит как обычный шрифт с заглавной (читается как давление автора, а не как нормативное правило)
- ❌ «Клиенты ОБЯЗАНЫ ...» — то же самое

Правильно:
- ✅ «Клиенты MUST отправлять заголовок `Authorization` со всеми запросами к `/v3/*`»
- ✅ «Версия `Authorization: Bearer <token>` SHOULD соответствовать формату RFC 6750»
- ✅ «Клиенты MAY включать заголовок `X-Request-ID` для трассировки»

И обязательная conventions-секция в RFC:

```markdown
### Конвенции

Ключевые слова «MUST», «MUST NOT», «REQUIRED», «SHALL», «SHALL NOT», «SHOULD», «SHOULD NOT», «RECOMMENDED», «NOT RECOMMENDED», «MAY» и «OPTIONAL» в данном документе интерпретируются согласно BCP 14 ([RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) + [RFC 8174](https://www.ietf.org/rfc/rfc8174.txt)).
```

### RU ADR — пример

```markdown
# ADR-0007: Использовать PostgreSQL 16+ как основной OLTP-стор сервиса Payments

**Статус**: Принято
**Дата**: 2026-05-20
**Авторы**: А. Петров, Б. Смирнов

## Контекст

Сервис Payments обрабатывает ~50 RPS мутирующих финансовых транзакций, требует строгой
консистентности и должен интегрироваться с нашими существующими первичными OLTP-базами
(обе на Postgres). Сервис владеет ~2 ГБ транзакционных данных сегодня, прогноз на 18
месяцев — ~15 ГБ.

Выбор основного стора нужно было сделать в Q2 (дедлайн привязан к публичному запуску).

## Решение

Мы будем использовать PostgreSQL 16+ в качестве основной OLTP-базы для сервиса Payments.
Хостинг — managed RDS (us-east-1 + us-west-2 для HA), с логической репликацией для
кросс-регионального доступа. Сервис MUST использовать `pg_advisory_lock` для миграций
схемы; ручные DDL-операции на проде SHALL NOT выполняться без pre-flight на снапшоте
прода.

## Последствия

- **Положительные**: у команды 5 лет операционного опыта с Postgres; инструментарий
  (бэкап, оптимизация запросов, миграции схемы) уже выстроен; строгие транзакционные
  гарантии соответствуют требованиям финансовых данных
- **Отрицательные**: вертикальное масштабирование имеет пределы — при прогнозируемом
  росте, шардирование может понадобиться при 50+ ГБ (примерно Q2 2027); read-реплики
  помогают, но не устраняют проблему
- **Риск**: миграции схемы на финансовых данных требуют аккуратной подготовки; будем
  использовать Flyway + pre-prod replay против снапшота продакшна перед каждым релизом

## Рассмотренные альтернативы

### MongoDB
Гибкие схемы помогли бы на ранних итерациях, но финансовые потоки требуют сильных
транзакций между документами. Multi-document транзакции в MongoDB поддерживаются, но
операционно менее зрелые, чем транзакции в Postgres. У команды нет опыта с MongoDB;
кривая обучения ~6 месяцев.

### DynamoDB
Отличное горизонтальное масштабирование, нет операционных накладных расходов. Но наши
шаблоны запросов включают сложные join'ы (история транзакций + контекст пользователя) —
моделирование в DynamoDB требует множественных денормализованных таблиц + сложности
поддержки. Стоимость также выше при нашем объёме запросов.

### Использовать существующую первичную базу (общая схема)
Избавило бы от запуска ещё одной БД. Но Payments требует изоляции схемы для соответствия
PCI-DSS; общая схема создаёт сложности аудита и проблемы blast-radius. Отклонено
командой Security.

### Status quo — без сервиса Payments
Не вариант; Payments — стратегический приоритет для запуска в Q3.

## Ссылки

- RFC-0042: Архитектура сервиса Payments
- ADR-0001: Стандарты по базам данных между сервисами
- Скоуп PCI-DSS аудита (internal, ссылка опущена)
```

### Localized section headers — RU mapping

Если команда пишет полностью по-русски, заголовки секций переводятся консистентно:

| EN | RU |
|---|---|
| Status | Статус |
| Author / Authors | Автор / Авторы |
| Created | Создано |
| Updated | Обновлено |
| Discussion | Обсуждение |
| Summary | Резюме |
| Motivation | Мотивация |
| Detailed proposal | Детальное предложение |
| Detailed design | Детальный дизайн |
| API surface | Поверхность API |
| Data model | Модель данных |
| Migration plan | План миграции |
| Backwards compatibility | Обратная совместимость |
| Security considerations | Соображения безопасности |
| Conventions | Конвенции |
| Alternatives considered | Рассмотренные альтернативы |
| Considered alternatives | Рассмотренные альтернативы |
| Consequences | Последствия |
| Positive | Положительные |
| Negative | Отрицательные |
| Mitigations | Меры по минимизации рисков |
| Adoption plan | План внедрения |
| Rollback | Откат |
| Open questions | Открытые вопросы |
| References | Ссылки |
| Goals | Цели |
| Non-goals | Не-цели |
| Constraints + assumptions | Ограничения и допущения |
| Solution space exploration | Исследование пространства решений |
| Recommendation (tentative) | Рекомендация (предварительная) |
| Next steps | Следующие шаги |
| Performance + scaling | Производительность и масштабирование |
| Edge cases + error handling | Граничные случаи и обработка ошибок |
| Observability | Наблюдаемость |
| Rollout plan | План выкатки |
| Status: Proposed / Accepted / Rejected / Superseded / Deprecated | Статус: Предложено / Принято / Отклонено / Заменено / Устарело |

### Что НЕ переводить

- **RFC 2119 keywords** (см. выше)
- **Технические термины**: `cursor pagination`, `idempotency key`, `webhook`, `mTLS`, `OAuth callback`, `connection pool` — оставлять оригинал. Если есть устоявшийся RU-перевод («ключ идемпотентности», «пул соединений») — допустимо использовать, но первый раз в документе сопровождать английским термином в скобках.
- **Имена endpoint'ов, методов, параметров, типов данных** — всегда оригинал в backticks: `POST /v2/exports`, `Client.export()`, `Promise<Export>`.
- **Имена сервисов, ADR-ссылок** — `ADR-0007`, `RFC-0042` (английская аббревиатура + цифры).
- **Имена компаний / продуктов / стандартов** — Stripe, Apollo Server, K8s, GDPR, SOC 2, PCI-DSS.

### Дата + статус

- Дата — ISO 8601: `2026-05-20`. Не «20 мая 2026» (это для прозы, не для метаданных документа).
- Статус — переведён по таблице выше, но в pull-request-обсуждениях принято писать `Status: Proposed` английским для скорости review.
- Версии — `v3.0.0` (semver), без перевода.
