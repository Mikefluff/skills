---
title: "Write an ADR for a database choice"
persona: "Tech lead documenting why we picked PostgreSQL"
time: "20-30 minutes"
skills:
  - rfc-writer
  - writer
---

# ADR-0007 — choose the primary OLTP database

Сценарий: команда обсуждала three недели, в каком хранилище держать primary application data. Уперлись в выбор: PostgreSQL vs MongoDB vs DynamoDB vs «just use the legacy MySQL we already have». Решение принято — PostgreSQL. Нужен ADR, который через два года новый engineer прочитает и поймёт, почему так, а не как.

Это работа для `rfc-writer`. Скилл собирает по фиксированной ADR-структуре с обязательной «considered alternatives» секцией.

## Intent — что значит «good ADR»

Architecture Decision Record (см. Michael Nygard's original template, расширенный в `skills/rfc-writer/references/templates.md`):

- **Status** — proposed / accepted / deprecated / superseded
- **Context** — что подталкивает к решению. Не история, не roadmap — текущие constraints и forces.
- **Decision** — что решено. Одно предложение в active voice.
- **Consequences** — что меняется. Both positive AND negative. Если только positive — incomplete ADR.
- **Considered alternatives** — какие варианты обсуждали, почему отвергли. ADR без этой секции = post-hoc rationalization.

Скилл refuse'ит финализировать ADR без обязательной alternatives section с минимум 3 options + reasoning per option.

## Intent — RFC 2119 keywords

`rfc-writer` enforces RFC 2119 normative language (см. `skills/rfc-writer/references/rfc-2119.md`):

- **MUST** / **MUST NOT** — absolute requirements
- **SHOULD** / **SHOULD NOT** — recommendations with documented exceptions
- **MAY** — optional, implementer's choice

«We will probably use» / «we kinda want to» / «it would be nice if» — скилл переписывает в normative form или вырезает claim.

## Setup

Скилл установлен. Output формат: Markdown с YAML frontmatter (для tooling, parseable). Output путь: по convention `docs/adr/NNNN-slug.md`.

## Step 1. Invoke with the decision

```
/rfc-writer adr "primary OLTP database choice" --number 7
```

Скилл задаёт 6 questions (без всех — не финализирует):

```
1. What's the decision in one sentence?
2. What forced the decision now? (not background — current constraints)
3. What alternatives were considered? (minimum 3, including "status quo" / "do nothing")
4. Who's affected? (teams / services / users)
5. What metrics will tell us this was right/wrong in 6 months?
6. Who reviewed this decision? (names or roles)
```

## Step 2. The brief

Answers:

1. **Decision** — Use PostgreSQL 16 as the primary OLTP database for all new services.
2. **Forces now** — current MySQL 5.7 EOL'd in October 2023, two services already hitting MySQL JSON-type limitations, new compliance requirement for row-level security, two team members joined from Postgres-shop background.
3. **Alternatives** — (a) PostgreSQL, (b) MongoDB, (c) DynamoDB, (d) status-quo: stay on MySQL and upgrade to 8.0.
4. **Affected** — backend platform team (owns DBs), three product teams (will migrate), SRE (new ops runbook).
5. **6-month metrics** — p99 query latency for write-heavy endpoints, ops on-call pages tagged db-incident, dev velocity self-report (post-migration survey).
6. **Reviewers** — Platform lead (Ana), SRE lead (Sven), CTO (rubber-stamp).

## Step 3. The finalized ADR

Скилл собирает + прогоняет через writer:

```markdown
---
adr: 0007
title: Use PostgreSQL 16 as primary OLTP database
status: accepted
date: 2026-05-20
deciders: [ana-platform, sven-sre, mike-cto]
supersedes: []
superseded-by: []
---

# ADR-0007 — Use PostgreSQL 16 as primary OLTP database

## Status

**Accepted** — 2026-05-20, by Platform lead (Ana), SRE lead (Sven), CTO (Mike).

## Context

We currently run on MySQL 5.7. Three forces push us off:

1. **MySQL 5.7 EOL'd in October 2023.** We are on extended support
   with no security patches beyond critical issues. Upgrade to 8.0 is
   non-trivial — multiple incompatibilities documented in our staging
   audit (see the staging migration audit).
2. **JSON-type ceiling.** Two services (notifications, audit-log) hit
   MySQL's JSON-field query performance ceiling. Mitigation paths
   (denormalize, separate document store) add complexity without
   solving the root issue.
3. **Compliance — row-level security.** New SOC 2 requirement for
   tenant-scoped row-level access. MySQL has no native RLS; we would
   need application-layer enforcement (fragile, audit-unfriendly).

If we are migrating anyway, the decision is which target.

## Decision

We **MUST** use PostgreSQL 16 as the primary OLTP database for all
new services starting in Q3 2026. Existing services on MySQL 5.7
**SHOULD** migrate within 12 months. Services with documented
exceptions (legacy revenue-critical paths) **MAY** remain on MySQL
through end of 2027, with sunset plan attached.

## Consequences

### Positive

- Native JSONB with GIN indices solves the JSON-ceiling problem for
  notifications and audit-log without architectural change.
- Native row-level security (RLS) directly satisfies SOC 2 tenant
  scoping. Replaces ~2,000 lines of application-layer enforcement.
- Mature ecosystem: pgvector (already need for embeddings),
  TimescaleDB option for metrics, logical replication for CDC.
- Two team members joined recently from a Postgres-heavy shop and
  bring operational knowledge.

### Negative

- One-time migration cost. Initial estimate: 4 engineer-quarters
  across platform + 3 product teams.
- SRE on-call runbook rewrites. Existing playbooks are MySQL-specific.
- Stripe-extract pipeline (downstream consumer) reads from MySQL
  binlog. PostgreSQL logical decoding is different — pipeline rewrite
  required.
- Some tooling gaps: Percona Toolkit equivalents on Postgres are
  fragmented (pg_repack + pg_partman + pgBackRest vs single Percona
  suite).

### Neutral

- License: both PostgreSQL and MySQL are open-source. No cost delta.
- Hiring market: roughly equivalent (Postgres slightly more common
  in modern stacks; MySQL more common in older shops).

## Considered alternatives

### Alternative 1 — MongoDB

**Rejected.** Strengths: flexible schema (helpful for evolving
notification payloads), strong document-model story.

Why rejected:
- Most of our data is highly relational (users, orgs, billing,
  subscriptions, tasks). Forcing it into documents creates a worse
  fit than the MySQL pain we are leaving.
- Transactional guarantees are weaker per-shard. Our billing service
  requires multi-row transactions; Mongo's multi-document
  transactions are slower and operationally complex.
- Compliance story for RLS is weaker — Mongo's field-level
  encryption helps but does not directly implement RLS.

### Alternative 2 — DynamoDB

**Rejected.** Strengths: managed, predictable performance, no ops
overhead, scales horizontally.

Why rejected:
- Lock-in to AWS pricing model. Our current cloud commitment runs
  through 2027; migration to multi-cloud is in the 3-year roadmap
  (separate ADR pending).
- Query model (no joins, no flexible filters) does not fit
  application patterns. Most pages already involve joins across 3-5
  tables. DynamoDB would require either denormalization
  (write-amplification) or a separate query layer (ElasticSearch).
- Cost projection at expected scale is ~2.3× our estimated Postgres
  cost on self-managed RDS or similar. See [cost-model.xlsx]
  (../analyses/db-cost-model-2026.xlsx).

### Alternative 3 — Stay on MySQL, upgrade to 8.0

**Rejected.** Strengths: incremental, no team retraining, preserves
existing tooling and runbooks.

Why rejected:
- Migration 5.7 → 8.0 is itself non-trivial (see audit). We pay the
  migration cost without solving the JSON-ceiling, RLS-compliance,
  and ecosystem-gap problems.
- We would still face the JSON and RLS issues. Application-layer
  RLS is fragile and audit-unfriendly.
- Strategic: MySQL's pace of feature evolution has slowed. Postgres
  is where ecosystem investments are happening (pgvector,
  logical-replication tooling, RLS maturity).

### Alternative 4 — Do nothing (status quo)

**Rejected.** Strengths: no migration cost, no risk of new bugs.

Why rejected:
- Not a viable option. MySQL 5.7 has no security patches beyond
  critical issues. Staying past end of 2026 creates compliance and
  CVE-exposure risk that outweighs migration cost.

## How we will know this was right (6-month review)

By 2026-12-01 we **MUST** review these metrics:

- p99 query latency for write-heavy endpoints (target: ≤ current MySQL p99)
- on-call pages tagged `db-incident` (target: ≤ baseline)
- dev velocity self-report from migrated teams (target: net positive)
- compliance audit (target: pass with RLS implemented natively)

If two of four are red, we **SHOULD** convene a post-mortem ADR
documenting what we learned and whether to course-correct.

## References

- Postgres 16 release notes
- Our MySQL 5.7 → 8.0 migration audit (internal)
- DynamoDB cost model (internal spreadsheet)
- Michael Nygard, "Documenting Architecture Decisions" (2011)
```

## Step 4. The review checklist

Скилл финиширует с auto-review:

```
=== ADR-0007 review checklist ===

✓ Status set (accepted)
✓ Context names ≥ 1 force (named 3)
✓ Decision is one sentence in active voice
✓ Consequences include both positive AND negative
✓ Alternatives section has ≥ 3 options
✓ Each alternative has reasoning, not just "rejected"
✓ "Do nothing" alternative explicitly considered
✓ Review trigger / metrics defined (4 metrics, 6-month review)
✓ Reviewers named
⚠ References section thin — consider adding link to MySQL 5.7 EOL announcement
⚠ "We MUST" appears 1 time — verify normative force is intentional
```

«⚠» — рекомендации, не блокеры. «✓» — passed.

## Когда НЕ использовать rfc-writer

- **One-line decision in chat** — overkill. ADR — для decisions, к которым через год новый engineer вернётся с вопросом «почему так».
- **Tactical sprint plan** — не architecture. Sprint planning artifact, не ADR.
- **Marketing positioning document** — это `landing-copy` territory, не engineering decision.
- **Decision уже отменено / превзойдено** — write the new ADR superseding the old, не rewrite the old. ADRs are append-only history.

## Troubleshooting

### Скилл refuse'ит финал без alternatives section

By design. ADR без «considered alternatives» = post-hoc rationalization. Если ты не рассматривала альтернативы — почему ты уверена, что текущий выбор правильный? Подумай ещё раз, потом возвращайся.

### Команда хочет «short ADR» (one paragraph)

Это template choice — `rfc-writer` поддерживает `--style mini` (одна страница, без detailed alternatives). Но я бы предостерёг: для decisions с 4-quarter migration cost mini-ADR не оправдан. Для one-week tactical decision — fine.

### Status «proposed» — могу ли я сразу написать «accepted»?

Можно, если decision уже принято (как в этом примере). Workflow: write as proposed → reviewers comment → flip to accepted on merge. Если ты finalized decision до review — write accepted, but include reviewer signatures.

### Скилл предлагает добавить «How we will know this was right»

Это не optional. ADR без review-trigger = decision без feedback loop. Если ты не знаешь, как проверишь correctness через 6 месяцев — ты не знаешь, что измеряешь. Подумай о метриках до финализации.

## Related

- [release-notes-saas.md](release-notes-saas.md) — где shipped decisions появляются user-facing
- [tone-shift.md](tone-shift.md) — если у тебя есть draft ADR в wrong tone (slack message → formal doc)
- [landing-launch.md](landing-launch.md) — внешнее представление того же decision (если решение выходит наружу)
- [skills/rfc-writer/references/templates.md](../../skills/rfc-writer/references/templates.md) — полная schema ADR
