# Input для rfc-writer — ADR for database choice

## Type

ADR (decision already made, capturing rationale).

## Topic

ADR-0007: Use PostgreSQL 16+ for the new Payments service primary store.

## Context

- Payments service handles ~50 RPS, requires strong consistency
- Integrates with our existing primary OLTP (Postgres)
- ~2GB transactional data today, ~15GB projected in 18 months
- PCI-DSS compliance required
- Decision deadline: Q2 (launch dependency)

## Considered alternatives

- MongoDB (rejected — multi-document transactions weaker)
- DynamoDB (rejected — complex joins for tx history)
- Shared schema in existing primary (rejected — PCI-DSS audit complexity)
- Status quo (rejected — Payments is strategic priority)

## Constraints

- Length: 0.5-2 pages (ADR convention)
- Status: Accepted
- RFC 2119 keywords only where genuinely normative
- No marketing language; engineer audience
