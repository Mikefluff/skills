# Composing skills — workflow recipes

The 17 skills aren't independent — they stack. `writer` is the foundation; wrappers extend it; linters audit without mutating; meta-skills manage the collection itself.

This file is the **recipe book**: named workflows showing concrete skill chains for typical jobs.

---

## Core composition rules

1. **`writer` is the base** — 12 of 17 skills run `writer` as their final cleanup pass. You rarely call `writer` directly except for raw clean-up.
2. **Linters are read-only** — `style-check`, `translation-sync`, `canon-check` produce reports, never mutate text. Use as quality gates.
3. **One wrapper per pass** — don't try to chain `prose-edit` + `essay-write` on the same text in one go. Pick the right one for the genre.
4. **Linters AFTER wrappers** — apply rewrites first, then lint. The opposite order tells you what you already know.
5. **Meta-skills are operational** — `skills-update` doesn't edit text; it manages the collection.

---

## Layered architecture

```
┌─────────────── meta ───────────────┐
│  skills-update                     │
└────────────────────────────────────┘

┌─────────────── linters (read-only) ─┐
│  style-check                        │
│  translation-sync                   │
│  canon-check                        │
└─────────────────────────────────────┘

┌─────────────── wrappers ────────────┐
│  Prose:   viral-text, prose-edit,   │
│           essay-write,              │
│           pelevin-digression,       │
│           tone-shifter, cold-email  │
│  Visual:  image-prompt, video-prompt│
│  Product: microcopy, release-notes, │
│           rfc-writer, landing-copy  │
└─────────────────────────────────────┘

┌─────────────── base ────────────────┐
│  writer                             │
└─────────────────────────────────────┘
```

---

## Recipe library

### "Ship a SaaS product launch"
```
landing-copy → microcopy → release-notes → viral-text (RU) + viral-text (EN)
```
landing-copy writes hero + features + pricing; microcopy fills UI strings + 404; release-notes documents what shipped; viral-text generates social announcements per locale.

### "Write a fiction chapter, commit-ready"
```
prose-edit → pelevin-digression (optional) → canon-check → style-check
```
prose-edit rewrites; pelevin-digression inserts voice digressions; canon-check validates against story bible; style-check is the final read-only gate.

### "Verify a multilingual book translation"
```
translation-sync (audit) → prose-edit (RU) → tone-shifter (EN) → translation-sync (verify)
```
Initial parity audit; polish RU; ensure EN matches register; final parity confirm.

### "Pitch a startup to investors"
```
cold-email (first-touch) → cold-email (follow-up) → landing-copy (hero) → rfc-writer (tech spec for due diligence)
```
First-touch; anchored follow-up; landing for the deck; tech spec for engineering audience.

### "Generate visual content for a post"
```
image-prompt (cover) → video-prompt (Reel) → viral-text (caption)
```
Cover image; animate still into reel; caption with hook + CTA.

### "Write a non-fiction longread with sources"
```
essay-write → pelevin-digression (optional) → style-check
```
Drafts the longread (Manson coda, V/H/P markers); inserts voice flair; gate.

### "Document an architecture decision"
```
rfc-writer (RFC) → rfc-writer (ADR after) → release-notes (announce to users)
```
RFC opens discussion; ADR captures the decision; release-notes informs users when it ships.

### "Shift register of existing content"
```
tone-shifter (casual → business-formal) → writer (final cleanup)
```
Single-pass register shift + writer cleans typography and residue.

### "Build out a marketing site"
```
landing-copy (hero + features + pricing) → microcopy (UI + 404) → release-notes (changelog page) → SEO meta (in landing-copy)
```

### "Read-only quality gate (no edits)"
```
style-check
```
Standalone audit. Returns severity-tagged report; no mutations.

### "Insert a Pelevin-vector digression"
```
pelevin-digression → essay-write (non-fic) | prose-edit (fiction)
```
Digression as a patch; wrapped by the appropriate parent skill.

### "Story-bible audit"
```
canon-check
```
Read-only. Returns drift report.

### "Cover the entire content stack for a campaign"
```
landing-copy + image-prompt + video-prompt + viral-text + cold-email
```
Landing + visuals + organic + outbound. Each independent; cross-links live in your campaign brief.

### "Update the skills collection itself"
```
skills-update
```
Meta. Checks for newer release, shows CHANGELOG diff, runs install.sh --update.

---

## Skill-to-skill data flow

| From | Output | Into | Notes |
|---|---|---|---|
| `writer` | cleaned prose | any wrapper | wrapper's final pass |
| `viral-text` | full post | `style-check` | optional pre-publish gate |
| `prose-edit` | rewritten chapter | `canon-check` + `style-check` | both gates often run |
| `essay-write` | drafted essay | `pelevin-digression` → `style-check` | pelevin inserts then gate |
| `translation-sync` | parity report | (no skill) | author applies fixes |
| `tone-shifter` | re-voiced passage | `writer` | always |
| `cold-email` | email body | `writer` | always |
| `image-prompt` | MJ/DALL-E prompt | (external model) | paste-ready |
| `video-prompt` | motion prompt | (external model) | paste-ready |
| `microcopy` | UI strings | `writer` | optional cleanup |
| `release-notes` | changelog md | `writer` | optional cleanup |
| `rfc-writer` | RFC/ADR md | `writer` | optional cleanup |
| `landing-copy` | landing sections | `microcopy` + `writer` | UI strings + cleanup |

---

## Common anti-patterns

❌ **Linting before rewriting** — style-check on a raw draft tells you what the wrapper already knows. Use linters as final gates.

❌ **Stacking two wrappers on the same text** — `prose-edit` + `essay-write` on the same passage = competing rule sets. Pick one for the genre.

❌ **Translating with `tone-shifter`** — tone-shifter shifts register WITHIN a language. For RU↔EN, use `translation-sync` for verification + a wrapper in the target language.

❌ **Marketing copy via `essay-write`** — essay-write is for longread non-fiction; landing copy needs `landing-copy` (different rules, shorter forms).

❌ **`writer` for register shift** — writer cleans LLM-prose tells, doesn't change register. Use `tone-shifter`.

---

## Cross-references

- All 17 skills (auto-generated): [`../README.md#whats-in-the-box`](../README.md#whats-in-the-box)
- Scenario-based picker: [`USER-GUIDE.md`](USER-GUIDE.md)
- Walkthroughs (end-to-end flows): [`walkthroughs/`](walkthroughs/)
