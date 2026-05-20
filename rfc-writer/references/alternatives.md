# Listing alternatives

An RFC / ADR / design doc without alternatives reads like a decree, not a proposal. The act of considering alternatives is what makes a doc trustworthy.

This file: how to find, compare, and present alternatives fairly.

---

## Why list alternatives

1. **Trust**: readers know the author actually evaluated options, not just picked the first idea
2. **Decision quality**: explicitly comparing alternatives surfaces hidden costs/benefits
3. **Future memory**: 2 years later, someone asks "did we consider X?" — the doc has the answer
4. **Stakeholder buy-in**: people who preferred a different alternative see their option taken seriously

If you can't think of any alternative — you haven't thought enough. Push harder.

---

## How many alternatives

- **RFC**: 2-4 alternatives + "do nothing"
- **ADR**: 2-3 alternatives + "status quo"
- **Tech spec**: usually doesn't list alternatives (the RFC already did)
- **Design doc**: 3-5+ alternatives (exploration is the point)

If you only have one alternative — it's not really a comparison. Find 1-2 more.

---

## The "do nothing" / "status quo" alternative

Always include the null case explicitly. Often surfaces hidden assumptions.

### Examples

```markdown
### Alternative: do nothing

If we don't migrate, we keep paying the 30ms-per-request latency, and the auth service
remains a SPOF. Cost over the next 12 months: ~$80k in incremental SRE pages and
~5% degradation in p99 latency on every downstream service.
```

```markdown
### Alternative: status quo

Keep the current Notion-based design docs. Pros: zero migration cost. Cons:
no version history, no offline access, hard to link from code. We've accepted these
costs for 3 years; this RFC explores whether the cost is now worth changing.
```

The "do nothing" alternative often loses on cost grounds — but stating its cost
explicitly is what makes the other alternatives' value visible.

---

## Section structure per alternative

Each alternative gets ~3-8 sentences. More for an RFC, less for an ADR.

### Standard template

```markdown
### Alternative N: {short name}

**Description**: {1-2 sentences. What this alternative is.}

**Pros**:
- {Specific advantage}
- {Specific advantage}

**Cons**:
- {Specific disadvantage}
- {Specific disadvantage}

**Why we (didn't / did) pick it**: {1-2 sentences. The decisive factor.}
```

For more concise ADRs:

```markdown
### {Alternative name}
{1 sentence describing it. 1 sentence why it's not picked.}
```

---

## Fairness: don't strawman alternatives

The instinct is to make alternatives look bad so the chosen option wins. Resist this.

❌ Strawmanned:
```
### Alternative: MongoDB
MongoDB is a slow, schemaless database that would force us to lose all our data
integrity guarantees and rebuild our app from scratch.
```

This sets up an alternative to obviously lose. Readers spot it and discount the rest
of your reasoning.

✅ Fair:
```
### Alternative: MongoDB
MongoDB would give us flexible schemas and easier horizontal scaling. The trade-off:
we'd lose strong transactional guarantees that our financial-data flows require, and
our team has more PostgreSQL operational experience. For an app dominated by
financial-data flows, PostgreSQL's trade-offs fit better.
```

Now readers trust the reasoning. The alternative is honestly described; the choice
between the two is on the trade-off, not a caricature.

---

## Common alternatives to consider

Before publishing an RFC, ask: "did I consider these?"

| Topic area | Alternatives to consider |
|---|---|
| **Choosing a database** | PostgreSQL, MySQL, MongoDB, DynamoDB, ScyllaDB, Cassandra, plus "use existing primary" |
| **Choosing a language for a service** | Existing-stack language, top alternative (often Go/Rust), niche pick if relevant |
| **Choosing an architecture** | Monolith, modular monolith, microservices, serverless, plus hybrid |
| **Choosing a protocol** | REST, GraphQL, gRPC, websocket, plus REST-with-streaming-extensions |
| **Choosing a cache** | In-memory, Redis, Memcached, application-level, plus "no cache, optimize the source" |
| **Choosing a queue** | Kafka, RabbitMQ, SQS, NATS, in-DB, plus "synchronous, no queue" |
| **Choosing a deployment** | K8s, Nomad, ECS, Fargate, EC2, plus PaaS (Heroku, Render, Vercel) |
| **Choosing an auth scheme** | Session cookies, JWT, opaque tokens, mTLS, OAuth flow X vs Y |
| **Migration approach** | Big bang, strangler fig, dual-write, branch-by-abstraction, plus "no migration, fork" |
| **Adding observability** | Metrics-only, logs-only, traces-only, full OTel, plus "rely on infra-level monitoring" |

For each, briefly evaluate: pros, cons, decisive factor.

---

## When alternatives genuinely don't exist

Sometimes the constraint space is narrow enough that there really are only 1-2 viable options. In that case:

```markdown
## Alternatives considered

This decision is constrained by {existing dependency / external requirement / team
expertise}. The viable alternatives are:

### Alternative: X
{...}

### Alternative: status quo
{...}

We did not consider {often-suggested alternative Y} because {specific constraint
that rules it out — e.g. "team has zero experience with Y and learning curve is
estimated at 6 months, exceeding the project deadline"}.
```

Be explicit about what's been ruled out before the comparison even starts. This
prevents readers from suggesting Y in feedback.

---

## The "why not X" pattern

Some alternatives are frequently raised by readers ("why didn't you just use X?").
Address them proactively:

```markdown
## Alternatives considered

### Why not GraphQL?

GraphQL was the obvious candidate. We didn't pick it because:
- Team has 4 years of REST tooling/expertise, ~6 months ramp-up estimated for GraphQL
- Our query patterns are simple (5-10 endpoints, 90% of usage covered by 3 of them)
- GraphQL's flexibility primarily helps when clients need varied data shapes; our clients
  are first-party and we control the query shape

In a different team with different query patterns, GraphQL would likely win. Here it
doesn't pencil out.
```

The "Why not X" pattern saves the team from rehashing the discussion in every code
review for the next 2 years.

---

## Comparison tables

For 3+ alternatives, a comparison table often beats prose:

```markdown
## Comparison

| Dimension | Option A | Option B | Option C |
|---|---|---|---|
| Effort to build | 4 weeks | 6 weeks | 8 weeks |
| Reversibility | High | Medium | Low |
| Performance (p95) | ~50ms | ~30ms | ~20ms |
| Team familiarity | High | Medium | Low |
| Operational cost | $200/mo | $400/mo | $800/mo |
| Strategic fit | Tactical | Balanced | Strategic |
```

Pair the table with a paragraph of synthesis: "Option B leans likely because the
operational cost is acceptable and team familiarity is high. Option C is faster but
the build effort and unfamiliarity push the date past Q3."

Tables work when the dimensions are comparable across alternatives. They don't work
when one alternative is fundamentally different in shape (e.g. comparing "rewrite"
vs "extend existing" — the dimensions don't line up).

---

## What NOT to do with alternatives

❌ List 8+ alternatives, half of which are minor variations
✅ Cluster similar alternatives ("Approach A with variant A.1, A.2") and pick the best representative

❌ Spend more words on the rejected alternatives than on the chosen one
✅ Chosen alternative gets full elaboration; rejected ones get the comparison-relevant detail only

❌ Use the "alternatives" section to bash competitors / tools you don't like
✅ Compare on capability, not vibes

❌ Skip the "do nothing" baseline
✅ Always include status quo as one of the alternatives

❌ "We didn't consider X because it's obviously wrong"
✅ "We did not consider X because {specific constraint that rules it out}"

❌ Decide first, then write alternatives to justify the decision
✅ Write alternatives to evaluate options, then decide

The last one is the hardest discipline. The RFC author often has a favorite at the
start of writing. Honest alternative comparison sometimes reveals that the
"obvious" pick isn't actually the best — that's the value of the exercise.

---

## Cross-references

- Document templates that include alternatives sections: [`templates.md`](templates.md)
- Where to flag uncertainty if alternatives aren't fully resolved: open-questions section in templates
- Review checklist for spotting weak alternatives sections: [`review-checklist.md`](review-checklist.md)
