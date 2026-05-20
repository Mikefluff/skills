# rfc-writer — calibration before/after pairs

4 paired examples: ADR / RFC / Tech Spec / Design doc, each showing weak version → strong version with deltas.

---

## 1. ADR (Architecture Decision Record)

### Before (weak)

```markdown
# Database Decision

We're going to use PostgreSQL for the new service. This is the best choice because
it's reliable and our team knows it. PostgreSQL is a powerful relational database
with great features. We considered other options too.
```

What's wrong:
- No status / date / authors
- "Best choice" without justification
- Marketing language ("powerful", "great features")
- "Other options too" but no list
- No context — why this decision needed to be made
- No consequences

### After (rewrite)

```markdown
# ADR-0007: Use PostgreSQL 16+ for the Payments service primary store

**Status**: Accepted
**Date**: 2026-05-20
**Authors**: A. Petrov, B. Smith

## Context

The Payments service handles ~50 RPS of mutating financial transactions, requires
strong consistency, and must integrate with our existing primary OLTP databases
(both Postgres). The service owns ~2GB of transactional data today, projected to
~15GB in 18 months.

We had to choose the primary store within Q2 (deadline tied to public launch).

## Decision

We will use PostgreSQL 16+ as the primary OLTP database for the Payments service.
Hosted on managed RDS (us-east-1 + us-west-2 for HA), with logical replication
for cross-region.

## Consequences

- **Positive**: team has 5 years of operational experience with Postgres; tooling
  (backup, query optimization, schema migrations) is established; strong
  transactional guarantees match financial-data requirements
- **Positive**: integrates cleanly with our existing Postgres-based services (shared
  schema-migration tooling, monitoring)
- **Negative**: vertical scaling has limits — at projected growth, we may need to
  shard at 50GB+ (estimated Q2 2027); read replicas help but don't eliminate this
- **Risk**: schema migrations on financial data require careful pre-flight; we'll
  use Flyway + pre-prod replay against production snapshot before each release

## Considered alternatives

### MongoDB
Flexible schemas would help during early iteration, but financial-data flows
require strong transactions across multiple documents. Multi-document
transactions in MongoDB are supported but operationally less mature than
Postgres transactions. Team has no MongoDB experience; learning curve ~6 months.

### DynamoDB
Excellent horizontal scaling, no operational overhead. But our query patterns
include complex joins (transaction history with user-context join) — modeling
these in DynamoDB requires multiple denormalized tables + maintenance complexity.
Cost is also higher at our query volume.

### Use existing primary database (shared schema)
Would avoid running another database. But Payments needs schema isolation for
PCI-DSS compliance; shared schema creates audit complexity and blast-radius
issues. Rejected by Security team.

### Status quo (no Payments service)
Not viable; Payments service is a strategic priority for the Q3 launch.

## References

- RFC-0042: Payments service architecture
- ADR-0001: Database standards across services
- PCI-DSS audit scope (internal, link omitted)
```

### Deltas applied
- ADR header with number + decision-as-title
- Status, date, authors
- Context provides specific numbers (RPS, data size, deadline)
- Decision in present tense, specific (PostgreSQL 16+, RDS, multi-region)
- Consequences both positive AND negative, with mitigations
- 4 alternatives considered (not "other options"), each with fair description and decisive factor
- References to related docs

---

## 2. RFC

### Before (weak)

```markdown
# RFC: Migrating to GraphQL

We should switch from REST to GraphQL because GraphQL is the modern way to build
APIs. It will solve many of our problems and is used by lots of big companies.

## Proposal

We'll rewrite our API to use GraphQL.

## Pros
- More modern
- Flexible queries
- Less data over the wire

## Cons
- Some learning curve

We will see how it goes after migration.
```

What's wrong:
- No status, date, author
- No motivation (what problem are we solving?)
- "Modern way to build APIs" — vague, marketing-flavored
- Pros/Cons trivial, no specifics
- No alternatives
- No migration plan
- "We will see how it goes" — non-commitment

### After (rewrite)

```markdown
# RFC-0089: Add GraphQL endpoint alongside REST for first-party clients

**Status**: Proposed
**Author**: C. Johnson <cj@example.com>
**Created**: 2026-05-20
**Discussion**: [GitHub PR #1247](https://github.com/example/rfcs/pull/1247)

## Summary

Add a GraphQL endpoint at `/v3/graphql` for first-party clients (web app, mobile),
keeping the existing REST endpoints for third-party API consumers. First-party
clients will migrate to GraphQL over Q3-Q4 2026.

## Motivation

The web app's project-list view fetches data via 4 sequential REST calls totaling
~1.2s of latency on slow connections. Mobile app shows similar patterns. We've
measured 18% of mobile sessions abandon before the project list loads.

Each new feature shipped this year (collaboration, search, notifications) has
added 1-2 REST endpoints purpose-built for the client. We now maintain 47
endpoints with overlapping concerns.

## Detailed proposal

### Endpoint

We will add `/v3/graphql` accepting standard GraphQL queries and mutations. The
existing REST endpoints under `/v2/` remain unchanged.

### Schema

Initial schema covers the resources used by the project-list view (Project,
User, Notification, Comment). Subsequent quarters extend the schema to cover the
rest of the surface (Settings, Billing, etc.).

### Implementation

We will use Apollo Server (Node.js) for the GraphQL gateway. Existing REST
endpoints become the resolver-layer's data source (no underlying-data changes).
This decouples the migration to GraphQL from any underlying-storage changes.

### Performance targets

- p95 query latency for the project-list query: ≤ 400ms (compared to 1.2s today
  via REST)
- p99: ≤ 800ms
- Schema introspection MUST be disabled in production (only enabled in dev/test)

### Conventions

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14.

### Compatibility

- Existing REST endpoints continue to work without change for 18 months minimum
- Third-party clients are notified of GraphQL availability but NOT forced to
  migrate
- First-party clients migrate per-view, not all-at-once

## Alternatives considered

### Status quo — keep REST only
Cost: continued endpoint sprawl, ~3 new endpoints per quarter, and the latency
issue on multi-resource views remains. This is the null case; the RFC's value is
measured against this.

### Migrate to GraphQL fully (deprecate REST)
Faster long-term — single API surface. But REST is consumed by ~500 third-party
integrations; forcing migration is high-cost user-pain. We instead add GraphQL
alongside.

### Implement BFF (Backends for Frontends) layer with REST
A per-client REST aggregator instead of GraphQL. Solves the latency problem but
adds a separate codebase per client and doesn't solve endpoint sprawl. Requires
more headcount.

### tRPC (TypeScript-only RPC)
Considered for the web app. Better DX than GraphQL within TypeScript ecosystems.
But mobile clients are in Swift/Kotlin and would need separate clients. GraphQL
covers all three first-party clients with one schema.

### REST + extension fields
Lower-effort. Each existing endpoint accepts an `expand` parameter to nest
related resources. Reduces sequential calls but doesn't generalize — every
endpoint must support every expansion. Considered, found at parity for the
project-list query but worse for future endpoints.

## Consequences

### Positive

- p95 project-list latency expected to drop from 1.2s → ~400ms (60% improvement)
- Endpoint sprawl reduced — new features shipped via schema changes, not new
  endpoints
- First-party clients gain query flexibility without server-side endpoint design
- Mobile session-abandon rate expected to improve from 18% → ~12% (estimated)

### Negative

- New runtime dependency (Apollo Server) — operational overhead
- Schema management becomes a coordination concern across teams (need to
  establish schema-review process)
- Caching is harder with GraphQL than REST (no per-URL cacheability) — we accept
  some CDN cache-hit-rate decrease in exchange for client-side speed
- Onboarding: new engineers need GraphQL training (estimated 1-2 weeks ramp-up
  for client-side; 2-4 weeks for server-side)

### Mitigations

- Operational: Apollo Server runs in our existing K8s setup; we add it to standard
  monitoring/alerting
- Schema review: we'll require a 24h review window for breaking schema changes;
  non-breaking additive changes auto-merge
- Caching: implement persisted queries + dataloader on resolvers; CDN cache-hit
  rate impact monitored, escalation if > 15% degradation

## Adoption plan

| Phase | Window | Scope |
|---|---|---|
| Phase 0 | June 2026 | Infrastructure + auth + first read query (Project) |
| Phase 1 | July-August 2026 | Web project-list view migrated; metrics-driven validation |
| Phase 2 | September 2026 | Mobile project-list view; iOS + Android in parallel |
| Phase 3 | Q4 2026 | Remaining first-party views; deprecation timeline for redundant REST |

### Rollback

The GraphQL endpoint can be disabled via feature flag without affecting REST.
First-party clients fall back to REST automatically (clients ship with both
codepaths during the transition).

## Open questions

- **Schema federation**: should we use Apollo Federation now or start monolithic
  and federate later? (We lean monolithic for v1; federation is a future concern.)
- **Authorization**: GraphQL field-level auth vs query-level — currently TBD;
  follow-up RFC required before Phase 0.
- **N+1 query risk**: dataloader handles common cases; we need to define an
  audit/alerting strategy for unusual query shapes.

## References

- [GraphQL spec](https://spec.graphql.org/October2021/)
- [Apollo Server docs](https://www.apollographql.com/docs/apollo-server/)
- RFC-0042: API v2 design
- ADR-0019: Endpoint design conventions
- [Internal] Project-list latency analysis (link omitted)
- [Internal] Q1 mobile session-abandon metrics dashboard
```

### Deltas applied
- Specific number for the title and proposal
- Status, author, date, discussion link
- Concrete motivation with numbers (1.2s latency, 18% abandon, 47 endpoints, 3/quarter growth)
- Detailed proposal with API surface, schema, implementation, performance targets, conventions section
- RFC 2119 keyword usage explicit (with conventions block)
- 4 alternatives + status quo, each with substantive comparison
- Both positive AND negative consequences, with specific numbers and mitigations
- Phased adoption plan in a table
- Rollback strategy
- Specific open questions with what triggers each
- Real references (internal + external)

---

## 3. Tech Spec

### Before (weak)

```markdown
# Tech Spec: New Payments API

This document describes our new Payments API. The API will allow users to make
payments.

## Goals
- Build a payment system

## Design
We'll build it using PostgreSQL and Stripe.

## Open questions
- Lots to figure out
```

What's wrong:
- Empty/generic content throughout
- "Lots to figure out" — surrender flag
- No goals/non-goals discipline
- No detailed design
- No edge cases, errors, performance, security, observability, rollout

### After (rewrite — abbreviated for example)

```markdown
# Tech Spec: Payments API v3

**Status**: Approved
**Owner**: Payments Team
**Reviewers**: Eng-Architecture, Security, SRE
**Created**: 2026-05-20
**RFC**: [RFC-0042: Payments service architecture](https://example.com/rfcs/0042)

## Overview

Implement the public-facing Payments API at `/v3/payments`, providing CRUD over
PaymentIntents and refunds. Backed by Stripe for processing; data stored in our
own Postgres (ADR-0007).

## Goals

- Synchronous payment creation with idempotent retries
- ≤200ms p95 latency for `POST /payments`
- Stripe webhook verification + processing
- PCI-DSS compliance: never store raw PAN; tokens only
- 99.95% availability target

## Non-goals

- Subscriptions billing (Stripe Billing, handled separately by `subscriptions` service)
- Multi-currency conversion (deferred to v4)
- Dispute / chargeback workflow (handled by Customer Support tooling, not this API)
- Reporting / analytics (data flows to data lake; queries handled there)

## Detailed design

### API surface

| Endpoint | Description |
|---|---|
| `POST /v3/payments` | Create PaymentIntent (idempotent on `Idempotency-Key` header) |
| `GET /v3/payments/{id}` | Retrieve a PaymentIntent |
| `POST /v3/payments/{id}/refund` | Issue a refund (idempotent on `Idempotency-Key`) |
| `GET /v3/payments?cursor=...&limit=...` | Paginated listing |

[Full OpenAPI spec in attached YAML.]

### Data model

```sql
CREATE TABLE payments (
  id              TEXT PRIMARY KEY,                  -- ulid-encoded
  user_id         TEXT NOT NULL,
  amount_cents    BIGINT NOT NULL CHECK (amount_cents > 0),
  currency        CHAR(3) NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
  status          TEXT NOT NULL CHECK (status IN ('pending', 'succeeded', 'failed', 'refunded')),
  stripe_intent_id TEXT NOT NULL UNIQUE,
  idempotency_key TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_user_id ON payments (user_id, created_at DESC);
CREATE INDEX idx_payments_idempotency ON payments (idempotency_key) WHERE idempotency_key IS NOT NULL;
```

[More detail in detailed design section continues...]

### Sequence (synchronous create)

1. Client POSTs to `/v3/payments` with `Idempotency-Key`
2. Service checks idempotency cache (Redis, 24h TTL)
3. If duplicate → return cached response
4. If new → call Stripe `payment_intents.create` (with same idempotency key forwarded)
5. Store result in Postgres
6. Return 201 with PaymentIntent body
7. Webhook handler updates status asynchronously when Stripe confirms

## Edge cases + error handling

- **Stripe unreachable**: 502 returned to client; idempotency key NOT stored (so client can retry safely); alert on >1% 502 rate
- **Concurrent retries with same idempotency key**: first request wins; subsequent retries get cached response
- **Amount = 0 or negative**: 400 Bad Request with specific error code
- **Currency unsupported**: 400 with `error.code = unsupported_currency`
- **User unauthorized to make payment for the requested entity**: 403 with `error.code = forbidden`
- **DB unreachable after Stripe call succeeded**: 202 Accepted; webhook will reconcile

## Performance + scaling

- Target: 500 RPS (sustained), 2000 RPS (peak)
- p95: 200ms; p99: 500ms (including Stripe round-trip)
- Connection pooling: 20 connections per pod, 8 pods = 160 connection limit (well under Postgres 500-connection limit)
- Database hot path is single index lookup + insert; no joins in synchronous path

## Security

- All endpoints require `Bearer` token; tokens validated by gateway before reaching service
- PCI-DSS: service never receives raw card data — only Stripe payment-method IDs
- Webhook signature verification with rotating secret; secret rotated weekly via SSM
- Stripe API key stored in AWS Secrets Manager, rotated quarterly
- All requests logged WITHOUT sensitive fields (amount and IDs OK; full request body redacted)

## Observability

**Metrics**:
- `payments_requests_total` (counter, labels: method, status_code)
- `payments_request_duration_seconds` (histogram, labels: method)
- `payments_stripe_calls_total` (counter, labels: action, status)
- `payments_stripe_call_duration_seconds` (histogram, labels: action)

**Logs** (JSON):
- request_id, method, path, status, duration_ms, user_id (no PII beyond user_id)

**Traces**: OTel; spans for: incoming request, idempotency check, Stripe call, DB ops

**Alerts**:
- p95 > 500ms for 5 minutes → page
- Error rate > 2% for 5 minutes → page
- Stripe 5xx rate > 1% for 5 minutes → page
- DB connection failures > 10/min → page

## Rollout plan

- Week 1: deploy to staging; internal test suite
- Week 2: production deploy, behind feature flag, 0% rollout
- Week 3: enable for internal test account (1% effective rollout)
- Week 4-5: 10% → 25% → 50% (3 days each)
- Week 6: 100%
- Rollback: feature flag off → all traffic routed to v2 (existing)

## Open questions

- **Refund partial vs full**: currently spec requires full refund only. Should we support
  partial in v3 or defer to v4? (RFC follow-up needed if v3.)
- **Multi-region replication**: today single-region us-east-1. Add eu-west-1 for EU latency
  and GDPR data-residency requirements? (Cross-team decision needed.)

## References

- RFC-0042: Payments service architecture
- ADR-0007: PostgreSQL choice
- ADR-0019: API endpoint conventions
- Stripe API docs: https://stripe.com/docs/api/payment_intents
- [Internal] PCI-DSS audit checklist
```

### Deltas applied
- Status, owner, reviewers, RFC link
- Specific overview (one sentence)
- Goals AND non-goals
- Detailed design with API surface table, SQL schema with constraints, sequence diagram
- Edge cases enumerated
- Performance targets with specific numbers
- Security section addressing PCI-DSS explicitly
- Observability section with metrics names, logs format, traces, alerts (specific thresholds)
- Phased rollout plan with rollback
- Open questions specific (not "lots to figure out")
- References to RFC, ADRs, vendor docs

---

## 4. Design doc (problem exploration)

### Before (weak)

```markdown
# Design Doc: Notifications

We need to think about how to improve notifications. Currently they're not great.
We should look at what other companies do and figure out a plan.
```

What's wrong:
- No problem statement
- No specifics on current pain
- "Look at what other companies do" — should already have done so
- "Figure out a plan" — design doc should advance the question, not just punt

### After (rewrite — abbreviated)

```markdown
# Design Doc: Multi-channel notifications strategy

**Status**: Exploring
**Author**: D. Lee
**Created**: 2026-05-20
**Last updated**: —

## Problem statement

Today, all notifications go via email + in-app. Users complain about three patterns
(from Q1 2026 support tickets, 312 total complaints in this bucket):

1. **Volume**: 42% of complaints (130 tickets): too many notifications per day. No
   user-controllable batching beyond per-feature "off" toggle.
2. **Wrong channel**: 38% (118): user wants SMS for security alerts but not for
   marketing, and the inverse. Cannot select channel per category.
3. **Timing**: 20% (64): notifications at inconvenient hours, particularly
   cross-timezone (e.g. user in Singapore receives marketing emails at 3am).

Additionally, we're discussing adding Slack and SMS as channels for Q3-Q4. Adding
these to the current architecture would worsen the volume/wrong-channel problems.

## Goals

Explore approaches to multi-channel notification preferences that:
- Reduce volume complaints by 50%+
- Allow per-category × per-channel preferences
- Respect quiet hours and timezone
- Scale to support adding new channels (Slack, SMS, push) without combinatorial
  per-channel code

## Non-goals

- Building Slack and SMS channels themselves (separate spec)
- Migrating in-app notifications to a different storage (orthogonal concern)
- Changing what events generate notifications (notification firing logic stays;
  delivery logic changes)

## Constraints + assumptions

- ~50M users; current notification volume ~120M/day across all channels
- Email is the dominant channel (95% of volume today); not deprecating it
- We have 6 months until Slack/SMS channel goes live (Q4)
- Existing notification system is a single Postgres table + worker queue; works
  fine at current volume
- Privacy: phone numbers (for SMS) require new consent flow; out of scope for this
  doc but a hard dep for Q4

## Solution space exploration

### Approach A: Per-channel preferences (feature flag style)

Each user has a matrix of {category} × {channel} → on/off. Total ~30 categories × 5
channels = 150 toggles per user.

**Pros**:
- Maximum user control
- Conceptually simple
- Maps directly to UI: a 30×5 grid (or grouped)

**Cons**:
- UX nightmare for non-power-users; most won't visit settings
- New categories or channels = touching the matrix per user
- Default state of new toggles: on or off? Wrong default → user complaint

### Approach B: Channel-tiered notifications

Notifications carry a "priority" (security / important / standard / marketing).
User picks: "send security via SMS, important via SMS+email, standard via email
only, marketing via in-app only". 4 tiers × 5 channels = 20 effective settings,
with sensible defaults.

**Pros**:
- Simpler UI (4 rows × 5 columns)
- New notification categories slot into existing tiers (mostly)
- Easy to default sensibly (e.g. security: SMS+email by default)

**Cons**:
- Categorizing every notification correctly is a coordination challenge across
  teams
- Categories may overlap (an "important" notification with a marketing flavor)

### Approach C: User-driven discovery + quiet preferences

Don't pre-categorize. Track per-user response to each notification (open / click /
ignore). After N samples per (user, category) pair, lower delivery frequency
automatically. User has a global "quiet hours" + per-category override.

**Pros**:
- Adapts to actual user behavior, not declared preferences
- Reduces total volume without explicit settings
- Easier to add new categories (no per-user setup)

**Cons**:
- Requires interaction tracking infrastructure (we have analytics but not
  notification-specific click tracking)
- Privacy/transparency concern: "the system decides for me"
- Slow to react when user genuinely wants to opt in (e.g. they newly subscribe to
  a feature)
- Cold-start problem for new users

### Approach D: Hybrid — defaults + overrides

Apply (B) for defaults: pre-categorize notifications by tier. Apply (C) for
adaptive: dampen frequency when user repeatedly ignores. Allow (A)-style overrides
for users who explicitly visit settings.

**Pros**:
- Defaults are sensible for the majority
- Adaptive dampening reduces volume for engaged-but-bored users
- Power users have full control

**Cons**:
- Most complex to implement
- Three competing dimensions to debug ("why didn't I get this notification?")

## Comparison

| Dimension | A | B | C | D |
|---|---|---|---|---|
| Reduces volume | ✓ if user opts in | ✓ | ✓ (auto) | ✓✓ |
| User effort | Very high | Medium | Zero | Medium |
| Engineering effort | Medium | Medium | High (tracking infra) | High |
| New channel cost | Per-channel edit | Per-channel edit | Per-channel edit | Per-channel edit |
| Default behavior | Toggles-on or off (problem) | Sensible per-tier | Random | Sensible per-tier |
| User trust | High | High | Lower (opaque) | Medium |

## Recommendation (tentative)

I lean toward **Approach D** (hybrid). Reasoning:

- Approach B by itself gets us most of the wins with reasonable engineering cost
- Approach C's automatic dampening is the biggest volume reducer without forcing
  user settings — high upside, but the trust issue is real
- Combining (B defaults + C adaptive + A power-user overrides) covers the most
  cases without over-relying on any one mechanism

Open question: should we ship Approach B in Q3 and add Approach C dampening in
Q4? Phased approach is lower risk.

## Open questions

- **Categorization workflow**: how do new notification categories get assigned a
  tier? Engineering self-classifies? Product reviews? Audit cycle?
- **Adaptive dampening**: what's the threshold for "ignored"? Click-rate < X% over
  Y samples? Need product input.
- **Privacy disclosure**: if we implement Approach C, what's the user-facing
  disclosure language? Legal review required.
- **Defaults audit**: who reviews per-category defaults at launch? When do we
  re-audit?

## Next steps

1. Talk to Notifications team about (B) feasibility (this week)
2. Check with Analytics about per-notification click-tracking gaps (this week)
3. Mock UI for (B) tier preferences (next 2 weeks; prototype with 5 users)
4. If (B) prototyping looks promising → RFC for Q3 implementation
5. Separately: spec for adaptive dampening (Approach C) — Q4 RFC

## References

- [Internal] Q1 2026 support ticket analysis (Notifications bucket)
- [Internal] Notifications service current architecture
- [Slack thread] #notifications-revamp design discussion
- [External] Slack's per-channel notification preferences design
- [External] Stripe Atlas: Notification UX best practices
```

### Deltas applied
- Status (Exploring) clear up front
- Concrete problem statement with numbers (312 complaints, 42%/38%/20% breakdown)
- Goals AND non-goals AND constraints
- 4 approaches explored fairly (not just "look at what others do")
- Each approach with pros/cons honest
- Comparison table
- Recommendation is honest about uncertainty ("I lean toward D")
- Specific open questions
- Concrete next steps (with timelines)
- Mix of internal + external references

---

## Pattern summary

Across all 4 rewrites:

1. **Always**: status + date + author header
2. **Always**: motivation/context cites specific evidence (numbers, tickets, metrics)
3. **Always**: alternatives section with at least 2-3 + status quo
4. **Always**: consequences both positive AND negative, with mitigations
5. **Always**: open questions specific (not "we'll figure it out")
6. **ADR**: short, focused; decision is the centerpiece
7. **RFC**: detailed proposal + alternatives + adoption plan + open questions
8. **Tech Spec**: API surface, edge cases, performance, security, observability, rollout
9. **Design doc**: problem framing + multiple approaches + tentative recommendation
10. **Strip marketing language**: "powerful", "modern", "best-in-class" — every time
