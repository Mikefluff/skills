# Document types

Four types of engineer-facing design documents. Pick the right one before writing — wrong type = wrong shape = wasted reader time.

---

## RFC — Request for Comments

**Purpose**: propose a non-trivial change, gather feedback, reach consensus.

**Status during life**: Draft → Proposed → Discussion → Accepted / Rejected / Superseded.

### Use RFC when

- The decision is **not yet made**
- The change has wide impact (cross-team / cross-system / public API / customer-facing)
- Multiple stakeholders need to review and weigh in
- You want a written record of WHY a choice was made (not just WHAT)

### Don't use RFC when

- The decision is trivial — overhead not worth it
- The decision is already made — use ADR instead (or Tech Spec)
- The "problem" is just a feature request — use a regular feature ticket

### Length / depth

- Typically **2-10 pages** of markdown (1000-5000 words)
- Detailed enough that a reader unfamiliar with the project can understand the proposal
- Includes alternatives, consequences, open questions

### Audience

- Engineers across multiple teams
- Tech leads / staff engineers
- Product / design where relevant
- Future-you (the doc is the institutional memory)

### Examples in the wild

- Python PEPs (peps.python.org)
- Rust RFCs (github.com/rust-lang/rfcs)
- Kubernetes Enhancement Proposals (KEPs)
- React's RFC repo (github.com/reactjs/rfcs)

---

## ADR — Architecture Decision Record

**Purpose**: capture a single decision **after** it's made.

**Status during life**: Proposed → Accepted → Deprecated / Superseded.

### Use ADR when

- A decision is **made** and you want to write it down for future reference
- The decision was a JUDGMENT CALL — multiple reasonable options, you picked one
- You want future engineers to understand WHY this code looks the way it does

### Don't use ADR when

- The decision is undecided — that's an RFC
- The decision is obvious / has no reasonable alternative
- The "decision" is just a small implementation detail

### Length / depth

- Typically **0.5-2 pages** of markdown (200-800 words)
- Compact: context + decision + consequences
- No exhaustive alternative analysis — just the alternatives that were genuinely considered

### Audience

- Future engineers maintaining this system
- New team members onboarding
- Architects auditing past decisions
- Yourself in 6 months

### Examples in the wild

- AWS Prescriptive Guidance ADR template
- ThoughtWorks Tech Radar (ADRs)
- ADR-tools (github.com/npryce/adr-tools) format

### Naming convention

Numbered + slug:
```
adr/
├── 0001-record-architecture-decisions.md
├── 0002-use-postgres-not-mysql.md
├── 0003-jwt-for-stateless-auth.md
├── 0004-rest-not-graphql.md
└── 0005-monorepo.md
```

The numbers establish chronology; the slug summarizes the decision.

---

## Tech spec

**Purpose**: specify how to BUILD something that's already decided.

**Status during life**: Draft → Approved → Building → Shipped → Archived.

### Use Tech Spec when

- The "what" and "why" are settled (often via a prior RFC)
- You need to spell out the "how" in enough detail that engineers can implement
- Cross-team dependencies need clear interface contracts

### Don't use Tech Spec when

- The "what" is still under debate — use RFC first
- The implementation is straightforward / trivial
- The audience is the public (use API docs / product docs)

### Length / depth

- Typically **3-15 pages** of markdown (1500-7500 words)
- Detailed enough that engineers can start implementing without further design conversations
- Includes: API surface, data model, edge cases, error states, performance budget, monitoring plan

### Audience

- The team building the thing
- Adjacent teams whose systems will integrate
- QA / SRE who will test / operate
- Future-you who'll need to remember the design

### Sections typical for tech specs

- Overview (what's being built, link to the RFC that decided to build it)
- Goals + non-goals (scope discipline)
- Detailed design (the meat — API surfaces, data flow, sequence diagrams if useful)
- Edge cases + error handling
- Performance / scaling targets
- Security considerations
- Monitoring + observability plan
- Rollout plan (feature flag, canary, gradual)
- Open questions

---

## Design doc

**Purpose**: explore a problem space; may not have a single recommendation yet.

**Status during life**: Exploring → Refined → (becomes RFC or is shelved).

### Use Design doc when

- The problem isn't yet clearly framed
- Multiple sub-decisions need to be made before any one big decision
- You want to think out loud before committing to a direction

### Don't use Design doc when

- You already know the proposed direction — use RFC
- You're making a single, focused decision — use ADR
- You're implementing — use Tech Spec

### Length / depth

- Typically **5-15 pages** of markdown (2500-7500 words)
- Often the longest of the four types — exploratory by nature
- Includes literature review, vendor comparisons, prototyping notes

### Audience

- Senior engineers / architects (most-likely readers)
- Future-self (a design doc often informs a later RFC; cite each other)
- Sometimes published as a public learning artifact

### Sections typical for design docs

- Background + motivation (longer than RFC's)
- Problem framing (sometimes the bulk of the doc — pinning down what the question actually is)
- Solution-space exploration (multiple candidate approaches, each with prototyping notes)
- Recommendation (often hedged: "lean toward X but want feedback")
- Open questions
- References / prior art

---

## Quick picker

| Situation | Document type |
|---|---|
| "We need to decide between X and Y" | **RFC** |
| "We decided X; let me write that down" | **ADR** |
| "We need to spell out HOW to build X" | **Tech Spec** |
| "I'm not sure what the problem even is yet" | **Design doc** |
| "Quick reminder of a small decision" | (Code comment, not a formal doc) |
| "We need to deprecate X" | **RFC** (if non-trivial) or **ADR** (if trivial) |
| "We just shipped X" | (Use `release-notes`, not this skill) |
| "What's our API documentation?" | (Use `essay-write` or a dedicated docs tool, not this skill) |

---

## Cross-doc relationships

These docs often reference each other:

- **Design doc → RFC**: design doc explores; once direction is clear, an RFC is written for the formal proposal
- **RFC → ADR**: RFC is accepted; an ADR is written capturing the final decision and the reasons (shorter than the RFC)
- **RFC → Tech Spec**: RFC says "build X"; tech spec says "here's HOW to build X"
- **ADR (old) → ADR (new)**: when superseded, the new ADR references the old one ("Supersedes ADR-0042")
- **RFC → release notes**: when the RFC's feature ships, release notes mention it briefly + link the RFC for those who want depth

---

## Hosting

| Type | Common location |
|---|---|
| RFC | Dedicated repo or `docs/rfc/` folder; PRs against it for review |
| ADR | `docs/adr/` folder in the relevant repo |
| Tech Spec | `docs/specs/` in the implementing team's repo, or shared docs platform (Notion / Confluence) |
| Design doc | Shared docs (Notion / Google Docs / Confluence) — exploratory, less version-controlled |

Pick based on the org's existing conventions; don't impose a new home with this skill.
