# Review checklist

Use when reviewing an existing RFC / ADR / tech spec / design doc — your own draft before publishing, or someone else's submitted for review.

The checklist flags the most common weaknesses across engineering design docs.

---

## Structural completeness

- [ ] **Document type explicit** — header says "RFC" or "ADR" or "Tech Spec", not implicit
- [ ] **Status field present** — Proposed / Accepted / Rejected / Superseded, current
- [ ] **Date(s) on the document** — created date, last-updated date if revised
- [ ] **Author(s) listed** with contact info
- [ ] **Summary / Overview** in first 100 words — reader knows what the doc is about before deciding to read more

---

## Problem framing

- [ ] **Problem statement is concrete** — describes specific user/system pain, not abstract concerns
- [ ] **Evidence cited** — links to bug reports, performance data, support tickets, user feedback, not "users want X"
- [ ] **Scope is bounded** — non-goals section explicit, or implicit constraints clear from text
- [ ] **Why now?** — addresses timing; if not now, why is this being proposed in this RFC?
- [ ] **Stakeholders identified** — who's affected (team / system / user), who needs to weigh in

---

## Proposal quality

- [ ] **Detailed enough to imagine the result** — reader can mentally simulate the proposed system
- [ ] **API surface, data model, sequence flow** described concretely where applicable
- [ ] **Migration / adoption plan** for non-trivial changes
- [ ] **Backwards compatibility** addressed — what breaks, what stays, what's the bridge
- [ ] **Edge cases** identified — what happens when X is null, Y is 0, Z is unreachable, etc.
- [ ] **Performance / resource impact** estimated, with rough numbers
- [ ] **Security implications** considered — threat model, mitigations
- [ ] **Operational impact** — what changes for ops/SRE (new dashboards, alerts, runbooks)

---

## Alternatives

- [ ] **At least 2-3 alternatives** considered (RFC) / **at least 1-2** (ADR)
- [ ] **"Do nothing" / status quo** included as one alternative
- [ ] **Each alternative described fairly** — not strawmanned
- [ ] **Decisive factor for each rejection** is named
- [ ] **Frequently-suggested alternatives addressed** ("Why not X?") proactively
- [ ] **Alternatives not just minor variants** — meaningful differences in approach

---

## Consequences

- [ ] **Positive consequences** listed — what this enables / improves
- [ ] **Negative consequences** listed honestly — what gets harder, what risks introduced
- [ ] **Mitigations** for each negative consequence
- [ ] **Reversibility** addressed — can we undo this if it doesn't work? At what cost?
- [ ] **Long-term consequences** considered — what does this look like in 12-24 months?

---

## Open questions

- [ ] **Open questions section exists** — even if you think you've answered everything, surface what's uncertain
- [ ] **Each question is specific and answerable** — not "we'll figure it out"
- [ ] **Question is actionable** — reader knows how to help answer it (more research, decision needed, prototype, etc.)
- [ ] **Distinguishes between** "unknown that needs research" vs "decision needed from leadership" vs "blocked on external"

---

## Writing quality

- [ ] **No marketing language** — "revolutionary", "best-in-class", "powerful" stripped
- [ ] **No filler** — "we're excited to propose" / "this is going to be amazing" stripped
- [ ] **RFC 2119 keywords** used correctly in normative statements (UPPERCASE only when normative)
- [ ] **Past tense for shipped work** ("we did X") / **present tense for current state** / **future tense only for "after this RFC is accepted"**
- [ ] **Plain language** — not jargon-dense unless audience is specialist
- [ ] **Active voice** — "Service X does Y" not "Y is done by Service X"
- [ ] **Specific over abstract** — "30ms latency" not "noticeable latency"
- [ ] **No emoji** in formal docs
- [ ] **Diagrams have captions** or are explained in text
- [ ] **Code snippets justified** — long blocks (> 30 lines) replaced with a gist link

---

## References

- [ ] **Prior RFCs / ADRs** linked
- [ ] **Related code / files** linked (specific commits or current HEAD?)
- [ ] **External sources** (vendor docs, RFCs, papers) linked
- [ ] **Internal discussions** (mailing list, Slack thread, meeting notes) linked
- [ ] **No broken links** — verify before publishing

---

## Common weak signals (RFC-specific)

When reviewing an RFC, scan for these red flags:

### 🚩 "We will see in the future"

Treat as: missing Open Question OR missing Risk in Consequences. Force the author to commit to one of:
- Decision now (with rationale)
- Decision later (in Open Questions with what triggers it)
- Out of scope (in Non-Goals)

### 🚩 Numbers without source

> "This will reduce latency by 50%."

How was that number derived? Benchmark? Estimate? Vendor claim? If derived, link to where. If estimated, say "estimated".

### 🚩 Vague scope

> "This RFC proposes a system for handling notifications."

Which notifications? For which users? At what scale? Force the author to bound scope explicitly.

### 🚩 No "Why not X?"

The RFC describes solution Y but doesn't address solution X — the one the reviewer is mentally screaming about. Force the author to add "Why not X" with substantive reasoning.

### 🚩 Single-author Slack-DM style

Reads like the author hasn't shown it to anyone yet. Suggest a pre-review pass with one peer before opening for broader review.

### 🚩 No migration plan for non-trivial changes

If the proposal touches existing systems, "we will migrate later" isn't a plan. Force a migration section: dual-write? Branch-by-abstraction? Big bang? Strangler? Estimated effort?

### 🚩 No rollback strategy

What happens if we ship this and it's worse than the status quo? Can we roll back in 5 minutes? 5 days? Never (one-way door)? Force this question.

---

## Common weak signals (ADR-specific)

### 🚩 "It seemed like the right thing"

Subjective justifications need to be replaced by specific trade-offs. "Postgres is the right choice because we know it" is OK if "team has 5 years operational experience with Postgres, zero with MongoDB" is the underlying claim.

### 🚩 Missing "considered alternatives"

An ADR without alternatives is just a decree. Always at least: "Considered X (rejected because Y)".

### 🚩 Long context, short decision

The "Context" section is 80% of the ADR. The "Decision" section is one sentence. Likely the author hasn't actually decided yet — they need an RFC, not an ADR.

### 🚩 Wrong document type

Often an ADR is actually an RFC in disguise — author hasn't yet committed to the decision but is writing as if they have. If the consequences include "we'll see how it goes," it's still proposed; rewrite as RFC.

---

## Common weak signals (Tech Spec-specific)

### 🚩 "TBD" everywhere

A tech spec with multiple "TBD" sections isn't ready to be built. Force resolution before approval — or back to RFC stage.

### 🚩 No "Goals + Non-goals" section

Without explicit non-goals, scope creep is guaranteed during implementation. Force the section.

### 🚩 No rollout plan

Tech spec without rollout plan = "build it, deploy it, hope" — high risk. Force feature flag / canary / gradual stages.

### 🚩 No monitoring plan

How will we know if this thing is healthy in production? If no metrics, logs, traces are specified — force them.

### 🚩 No error-handling

The "happy path" is described in detail; failures are hand-waved. Force at least: what happens on dependency unavailability, timeout, malformed input.

---

## Common weak signals (Design doc-specific)

### 🚩 Single recommendation without options

Design docs are exploration. If you already know the answer, write an RFC. If you're exploring, the doc should explore — multiple options with honest comparison.

### 🚩 No prior art / literature review

Has someone else solved this problem? Almost certainly yes. Force a section: how do {company X, paper Y, open-source project Z} approach this? What do we learn from their approach?

### 🚩 "Just figure it out as we go"

The doc concludes with implementation plans but no commitment to a direction. That's exploration without decision. Acceptable in the early stages; force a "next steps" section that commits to research / prototyping / RFC.

---

## How to deliver review feedback

When reviewing, use **specific, actionable** comments:

✅ "In §3, the migration plan doesn't address what happens if the dual-write fails on the new system. Suggest: add explicit conflict-resolution policy (LWW? Manual reconciliation?)."
❌ "Migration section needs work."

✅ "The 'Why not GraphQL?' rationale is one sentence ('REST is simpler'). Suggest: name the specific simplicity gain — concrete examples of where the team's REST tooling/expertise helps."
❌ "Alternatives section is weak."

The specific feedback gives the author exactly what to fix. The vague feedback wastes everyone's time.

---

## Quick "first 60 seconds" check

When you receive an RFC and only have 60 seconds:

1. **Summary**: clear? Read like a doc-summary, not a marketing pitch?
2. **Status**: present?
3. **Motivation**: concrete? Cites evidence?
4. **Alternatives**: at least 2 + status quo?
5. **Consequences**: both positive AND negative listed?
6. **Open questions**: present with specific questions?

If any of these are missing — the doc isn't review-ready. Send back with one-paragraph note before doing the deeper review.

---

## Cross-references

- Templates that this checklist evaluates against: [`templates.md`](templates.md)
- Document-type picking guide: [`document-types.md`](document-types.md)
- RFC 2119 keyword usage: [`rfc-2119.md`](rfc-2119.md)
- Listing alternatives well: [`alternatives.md`](alternatives.md)
