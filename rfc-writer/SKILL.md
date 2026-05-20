---
name: rfc-writer
description: "Write engineer-facing design documents — RFCs, ADRs (Architecture Decision Records), Tech Specs, Design Docs. Structure: context / problem / proposal / alternatives / consequences / decision / open questions. RFC 2119 keywords (MUST/SHOULD/MAY). Use when the user says 'write an RFC for...', 'design doc for...', 'ADR for...', 'tech spec for...'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Write a design document that engineers can review, critique, and decide on. Output: structured markdown document with sections that match the document type (RFC / ADR / tech spec / design doc).

Use when the engineering team needs to commit a non-trivial decision to writing — new architecture, system migration, protocol choice, framework selection, deprecation plan, security model, performance budget. Not for release notes (that's `release-notes`). Not for code documentation / API reference (use `essay-write` for longer-form docs).

This skill does NOT:
- write user-facing release notes (use `release-notes`)
- write marketing landing pages (use `landing-copy`)
- write API documentation / code docs (use `essay-write` for longer prose; for reference docs use a dedicated tool)
- generate code (it documents decisions about code, doesn't write code)
- pick the answer for the user — the skill helps STRUCTURE the discussion; the team / author makes the decision
</objective>

## ROLE

Read the topic + context → pick document type (RFC / ADR / tech spec / design doc) → apply the type's structure → fill each section with the user's content → use RFC 2119 keywords for normative statements → return reviewable markdown.

## PIPELINE

1. **Pick document type.** See `references/document-types.md`:
   - **RFC** (Request for Comments) — proposal under discussion; may have multiple revisions before consensus
   - **ADR** (Architecture Decision Record) — captures a single decision after it's made; short, focused
   - **Tech spec** — specifies how to BUILD something already decided
   - **Design doc** — broader than RFC; explores a problem space, may not have a single recommendation yet

2. **Gather inputs.** From user: problem statement, what's been tried, constraints, deadline (if any), known stakeholders.

3. **Apply structure.** Each document type has its own section template. See `references/templates.md`.

4. **Use RFC 2119 keywords correctly.** MUST / MUST NOT / SHOULD / SHOULD NOT / MAY for normative statements. See `references/rfc-2119.md`.

5. **Surface alternatives.** RFCs and design docs must explore at least 2-3 alternatives. ADRs explicitly list "considered alternatives" before the decision. See `references/alternatives.md`.

6. **Spell out consequences.** Every proposal has trade-offs. Make them explicit:
   - **Positive**: what this enables / improves
   - **Negative**: what gets harder / what risks are introduced
   - **Mitigations**: how to handle the negatives

7. **Add open questions.** Things the doc doesn't yet answer. Surfaces these for reviewer feedback.

8. **Final pass.** Run through `writer` for prose cleanup. RFCs need to be READABLE — many people will read them.

## MODES

- `rfc-writer rfc <topic>` — generate an RFC for an open question
- `rfc-writer adr <decision>` — generate an ADR for a settled decision
- `rfc-writer tech-spec <feature>` — generate a tech spec for an approved feature
- `rfc-writer design-doc <problem-space>` — broader design doc exploring a problem
- `rfc-writer --from-template <type>` — start from a blank template only
- `rfc-writer --review <existing-rfc>` — critique an existing RFC (missing sections, weak alternatives, undocumented risks)

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/document-types.md](references/document-types.md) | When picking the type — when to use RFC vs ADR vs spec vs design doc |
| [references/templates.md](references/templates.md) | When assembling — full section structure per document type |
| [references/rfc-2119.md](references/rfc-2119.md) | When writing normative statements — MUST / SHOULD / MAY semantics |
| [references/alternatives.md](references/alternatives.md) | When listing alternatives — how to compare fairly, when to drop one, "why not X" pattern |
| [references/review-checklist.md](references/review-checklist.md) | When reviewing existing docs — common gaps and weak points to flag |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 4 calibration pairs: ADR / RFC / tech spec / design doc showing weak vs strong versions.

## CONSTRAINTS

- **Document type drives structure.** Don't pad an ADR with RFC sections; don't compress an RFC into ADR brevity.
- **State the problem before the proposal.** A reader who doesn't know the problem can't evaluate the proposal.
- **Show your work — list alternatives.** "We considered A but went with B because..." is what makes a doc credible. A doc with no alternatives reads like a decree.
- **Use RFC 2119 keywords for normative statements.** "Clients MUST send `Authorization` header" not "Clients should send Authorization header" (lowercase "should" is non-normative).
- **No marketing language.** "Revolutionary approach", "best-in-class architecture" — strip on sight. The doc is for engineers; they want correctness, not hype.
- **No "we will see in the future".** State what's known; for what's unknown, put it in "Open questions".
- **Cite sources.** Link to: prior RFCs, related code, benchmarks, vendor docs, mailing-list threads. Engineers verify claims.
- **No emoji in RFCs / ADRs.** Doc is read by a wide audience including future-you; emoji ages poorly and looks unprofessional.
- **Date the document.** ISO 8601. RFCs may be revised; date each revision.
- **Status field.** Every RFC/ADR has a status: Proposed / Accepted / Rejected / Superseded / Deprecated.

## INVOCATION HINTS

When the user says any of:
- "write an RFC for ..."
- "design doc for ..."
- "ADR / Architecture Decision Record"
- "tech spec / technical specification"
- "spec out the X system"
- "document the decision to use X"
- "explore alternatives for ..."
- "review this RFC"

Use this skill. For user-facing release notes → `release-notes`. For prose documentation → `essay-write`. For viral / marketing content about a launch → `viral-text` or `landing-copy`.
