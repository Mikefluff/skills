# Brand-voice JSON profile

A complement to the 6 abstract registers (`casual`, `friendly-professional`, `business-formal`, `academic`, `technical`, `plain-explainer` — see [`registers.md`](registers.md)).

**Why two axes?**

- **Registers** are abstract categorical: every "casual" piece shares vocabulary norms, sentence length, contraction policy. Registers are good for "make this passage more X".
- **Brand voice** is concrete custom: a specific writer or company has their own signature words, banned-by-them words, opening hooks, and CTA phrases. A brand voice can OVERLAY a register — "casual but with these specific words always, these specific words never".

When the user provides a brand-voice profile (or asks the skill to infer one), use it ALONGSIDE the register target. The result is both shifted-to-register AND aligned-to-brand.

---

## Profile schema (JSON)

```json
{
  "name": "Acme — playful-expert",
  "tone": "friendly",
  "styles": ["storytelling", "tips"],
  "vocabulary": [
    "ship",
    "lean in",
    "real talk",
    "the receipts",
    "moves the needle"
  ],
  "avoidWords": [
    "synergy",
    "leverage",
    "circle back",
    "deep dive",
    "obviously"
  ],
  "hooks": [
    "Real talk:",
    "Here's the thing nobody mentions:",
    "We've seen this 47 times in {industry}:",
    "Three months in, the numbers say:"
  ],
  "ctaPhrases": [
    "Reply 'YES' if you want the playbook.",
    "Want the dashboard? Comment 'send'.",
    "Tag the founder who needs this.",
    "DM 'audit' for a free review."
  ],
  "register": "friendly-professional"
}
```

### Field reference

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Short 2-4 word label. Output language = brand's language. |
| `tone` | enum | yes | One of: `professional`, `friendly`, `humorous`, `inspirational`, `educational` |
| `styles` | string[] | yes | 1-3 from: `storytelling`, `tips`, `listicle`, `tutorial`, `review`, `news` |
| `vocabulary` | string[] | yes | 5-15 key phrases the brand habitually uses (signature words, owned phrases, professional terms) |
| `avoidWords` | string[] | yes | 3-10 words/phrases the brand should NEVER use (clichés, conflicting register, words competitors over-use) |
| `hooks` | string[] | yes | 3-5 ready-to-use opening templates (real phrases, not abstract descriptions) |
| `ctaPhrases` | string[] | yes | 3-5 ready-to-use call-to-action phrases |
| `register` | enum | no | Optional default register from `registers.md`. If absent, infer from `tone`. |

---

## Tone taxonomy (5)

The `tone` field is one of these. Each implies a default register but can be overridden:

| Tone | Implied register | Notes |
|---|---|---|
| `professional` | business-formal | Default tone for corporate / B2B / enterprise voices |
| `friendly` | friendly-professional | Approachable but with substance |
| `humorous` | casual | Self-aware, plays with conventions; risky for some audiences |
| `inspirational` | friendly-professional | Aspirational, motivational; high-risk for sounding hollow |
| `educational` | plain-explainer | Teacher-voice; assumes audience wants to learn, not be sold to |

The combination `tone` + `register` produces 5 × 6 = 30 possible matrices, but in practice only ~10 are common (most `inspirational` falls in `friendly-professional` or `casual`, etc.).

---

## Styles taxonomy (6)

The `styles` field is 1-3 of these. Multiple styles let the brand mix patterns:

| Style | Shape | Use case |
|---|---|---|
| `storytelling` | Narrative with characters, scenes, dialogue | Founder-personal-brand, podcasts, longform |
| `tips` | Numbered actionable points | Newsletters, LinkedIn, how-to content |
| `listicle` | Curated lists with brief commentary | Roundups, "best of" content |
| `tutorial` | Step-by-step instructional | Educational, dev-blogs |
| `review` | Critical analysis with verdicts | Product reviews, tool comparisons |
| `news` | Time-sensitive event reporting | Industry updates, breaking analysis |

Mix examples:
- `[storytelling, tips]` — founder-style essay that ends with concrete takeaways
- `[review, tips]` — "I tried X for 30 days, here's what works"
- `[news, listicle]` — "5 things that happened this week"

---

## Modes

### Mode 1 — Apply existing profile

User provides JSON profile + a passage. Skill rewrites passage to:
1. Match `register` (default: derived from `tone`) — see `registers.md` for the shift mechanics
2. Inject vocabulary words where natural (don't force-stuff them — 1-2 mentions OK)
3. Strip avoidWords (replace with synonyms or just remove)
4. Optionally replace the existing hook/CTA with one from the profile (if the passage has weak hook/CTA)

### Mode 2 — Infer profile from samples

User provides 2-5 sample texts (or a brand description). Skill analyzes them and outputs the JSON profile. Then asks the user whether to also apply it to a new passage.

Heuristic for inference:
- Read 2-5 samples
- Identify recurring phrases (vocabulary candidates)
- Identify register (sentence length, contractions, formality markers)
- Identify hook patterns (first sentences of each piece)
- Identify CTA patterns (last paragraph of each piece)
- Identify what's NOT there (likely avoidWords)
- Output JSON; ask user to refine

### Mode 3 — Verify a draft against an existing profile

Read-only: produce a checklist
- Vocabulary words: present? frequency? (target: 1-3 per piece)
- avoidWords: any present? (target: 0)
- Hook from profile? Or original?
- CTA from profile? Or original?
- Register match (vs profile's declared register)?

Output: structured report; user decides whether to rewrite.

---

## Discriminator vs simple register-shift

If the user just says "make this more casual" without providing a profile — use [`registers.md`](registers.md). Don't make up a profile.

If the user provides specific words ("use these terms", "never say X"), specific hook templates, or sample texts to mimic — use brand-voice profile mode.

Rule of thumb: if the answer to "what specifically distinguishes this brand?" is more than a register name, use brand-voice profile.

---

## Multilingual notes

The profile fields `vocabulary`, `avoidWords`, `hooks`, `ctaPhrases` must be in the BRAND's language (the language they write in). If the brand writes in Russian, those fields are Russian. The `tone` and `styles` enums are always the same English values regardless of brand language (they're taxonomy labels).

---

## Pipeline integration

```
input passage + (optional) profile JSON
  ↓
detect source register (from `registers.md`)
  ↓
target register = profile.register (if provided) OR user-specified target
  ↓
apply register-shift transformation deltas (from `transformation-rules.md`)
  ↓
[if profile provided] inject vocabulary, strip avoidWords, optionally swap hook/CTA
  ↓
final writer cleanup pass
  ↓
output rewritten passage + (optional) diff report
```

---

## Cross-references

- Register taxonomy: [`registers.md`](registers.md)
- Per-pair transformation deltas: [`transformation-rules.md`](transformation-rules.md)
- Hooks for viral content (different from brand-voice hooks): [`../../viral-text/references/hook-taxonomy.md`](../../viral-text/references/hook-taxonomy.md)
- CTA bans (don't put these in profile.ctaPhrases): [`../../writer/references/synthetic-constructions.md`](../../writer/references/synthetic-constructions.md) §2
