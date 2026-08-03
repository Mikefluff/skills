---
name: tone-shifter
description: "Rewrite text in a different register without changing meaning — formal↔casual, business↔academic, technical↔friendly, plain-explainer. 6 named registers + transformation deltas. Wraps `writer`. Use when the user says 'make this more casual / formal / accessible / business-like', 'rewrite for younger audience'."
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
Tone-shift a passage from one register to another while preserving the underlying claims, facts, structure, and information density. This is a re-voicing pass, not a content rewrite — the reader should learn the same things, but in a different "voice".

Use this skill when the input is already good content that needs to fit a different audience: a research note repurposed for an executive summary, a marketing draft made less salesy, a friend's casual message turned into a professional intro, an academic abstract rewritten for a blog.

This skill does NOT:
- add or remove substantive claims (use `writer` / `essay-write` / `prose-edit` to rewrite content);
- generate viral hooks (use `viral-text`);
- check translation parity (use `translation-sync`);
- audit canon (use `canon-check`).
</objective>

## ROLE

Read input + target register → output the same content rewritten in the target register → run the `writer` 4-layer cleanup so the result is shippable.

## PIPELINE

1. **Detect source register.** Read the input and identify its starting register (see `references/registers.md`). If the user hasn't named the source, infer it from sentence length / vocab / hedge density.

2. **Confirm target register.** The user must name the target. If unclear, ask: "Which register? casual / friendly-professional / business-formal / academic / technical / plain-explainer."

3. **Identify deltas.** Look up `references/transformation-rules.md` for the source→target pair and gather the specific changes: contractions on/off, sentence length, vocab swaps, hedge density, jargon level, person (1st / 2nd / 3rd).

4. **Apply transformations clause-by-clause.** Don't paraphrase the whole text in one shot — that loses content. Walk through each sentence and apply only the deltas that fit. Preserve original sentence boundaries when possible.

5. **Pass through `writer`.** Final 4-layer clean: typography, anti-slop regex categories, structural-prose, ru-calques. This is the same final pass every other wrapper runs — see `writer/SKILL.md`.

6. **Diff-report.** Show before/after side-by-side with a 1-line note on which deltas were applied. The user reviews; they can ask for a different register or a partial revert.

## MODES

- `tone-shifter <text> --to <register>` — shift to named target
- `tone-shifter <text> --to <register> --from <register>` — explicit source (skips detection)
- `tone-shifter <text> --to <register> --conservative` — apply only safe deltas (vocab + contractions); skip restructuring
- `tone-shifter <text> --analyze` — return only the detected source register + suggested targets, do not rewrite
- `tone-shifter <text> --profile <profile.json>` — apply a custom brand-voice JSON profile (vocabulary, avoidWords, hooks, ctaPhrases) on top of register shift
- `tone-shifter --infer-profile <samples...>` — read 2-5 sample texts and output a brand-voice JSON profile for review
- `tone-shifter <text> --verify-profile <profile.json>` — read-only check: does the passage match the profile? Returns structured report.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/registers.md](references/registers.md) | When detecting source or naming target — defines the 6 registers and their detection markers |
| [references/transformation-rules.md](references/transformation-rules.md) | After source+target known — the specific deltas to apply for each pair |
| [references/brand-voice-profile.md](references/brand-voice-profile.md) | When user provides a custom brand-voice profile (JSON), or asks for one to be inferred from samples — overlays registers with concrete vocabulary / banned words / hooks / CTAs |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) for 4 calibration pairs covering the most-common shifts.

## CONSTRAINTS

- **Do not change facts.** If the input says "we raised $4M in 2023", the output cannot say "we raised several million" or "we raised in the early 2020s".
- **Do not change structure unless register demands it.** Casual register may merge two short academic sentences into one. Academic register may split a casual run-on. But the order of points stays.
- **Do not invent transitions.** The transformation is local. If the input has rough transitions, they stay rough — the user can run `prose-edit` for that.
- **Preserve quoted speech verbatim.** Quoted material does not get tone-shifted; only narration around it.
- **Person changes (1st → 3rd, you → reader) only if the target register strictly requires it.** Otherwise preserve original person.

## INVOCATION HINTS

When the user says any of:
- "make this more casual / formal / professional / friendly / academic / accessible"
- "rewrite for a younger / older audience"
- "turn this into [email / Slack / LinkedIn / blog / academic] tone"
- "less salesy", "less corporate", "less jargon", "less formal"
- "give me a plain-English version"

Use this skill. If the user wants a viral version (hook + CTA), use `viral-text`. If they want fiction voice, use `prose-edit`.
