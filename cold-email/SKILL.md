---
name: cold-email
description: "Write or rewrite cold outreach emails to founders, VCs, recruiters, journalists, partners. 5-block structure (hook/value/ask/easy-yes/sign-off), ≤120-word budget, banned ceremony, anti-template subjects. Wraps `writer`. Use for first-touch, follow-up, intro request, warm-intro forwardable, re-engage."
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
Write a cold email that gets read and responded to. Not viral content (use `viral-text`). Not formal corporate (use `tone-shifter --to business-formal`). A direct, one-to-one message with a specific ask.

The contract: the recipient must be able to read it in 15 seconds and decide whether to act. Every word that doesn't earn that 15 seconds is a tax.

Use this skill when the user is writing:
- a first-touch outreach (founder → VC, candidate → recruiter, writer → editor, partner → partner)
- a follow-up to a non-response
- an intro request through a mutual connection
- a warm-intro template (the "forwardable" email)
- a re-engagement after a long pause

This skill does NOT:
- write viral posts (use `viral-text`)
- write long-form essays (use `essay-write`)
- shift register of existing content (use `tone-shifter`)
- write fiction outreach (DM to an author, fan letter) — those need a different voice.
</objective>

## ROLE

Read context (who is the recipient, what's the ask, what's the proof) → assemble the email with the 5-block structure → respect the length budget → run the banned-patterns check → final pass through `writer`.

## PIPELINE

1. **Gather intent.** Ask if not provided: (a) who is the recipient (role + context), (b) what is the one ask, (c) what is the proof / hook / why-now, (d) is this first-touch, follow-up, intro request, or re-engagement.

2. **Pick structure.** See `references/structure.md` for the 5-block template adapted to the email type. First-touch and follow-up have different leads.

3. **Length-budget check.** See `references/length-budget.md`. Hard cap: 200 words. Target: ≤120 words for first-touch. If draft exceeds budget, cut — see the cut-list in length-budget.md.

4. **Banned-patterns check.** See `references/banned-patterns.md`. Strip ceremony, hedges, vague intros, "I hope this email finds you well", "Hope you're doing great", "Just checking in".

5. **Final `writer` pass.** 4-layer cleanup. Even more strict than usual: cold email has no slack for slop.

6. **Output.** Subject line + body. Subject line follows its own rules (see `references/structure.md` section 6).

## MODES

- `cold-email first-touch <recipient> --ask <ask> --proof <proof>` — initial outreach
- `cold-email follow-up <previous>` — write a follow-up that doesn't repeat the original
- `cold-email intro-request <intro-via> --asking-for <intro-to> --why <reason>` — ask a mutual contact
- `cold-email forwardable <recipient-context> --ask <ask>` — the "forwardable" template designed to be pasted by the intro-giver into a separate thread
- `cold-email re-engage <last-context>` — re-open after silence

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/structure.md](references/structure.md) | When assembling the email — 5-block template per type, subject-line rules |
| [references/banned-patterns.md](references/banned-patterns.md) | After draft is assembled — the strip pass |
| [references/length-budget.md](references/length-budget.md) | When the draft exceeds 120/200 words — the cut-list |

## EXAMPLES

See [examples/](examples/) — three calibration emails (first-touch, follow-up, intro-request).

## CONSTRAINTS

- **One ask per email.** If the user wants two asks, write two emails.
- **No multi-paragraph windups.** The first sentence must contain a hook or be the hook. No "I'm reaching out because I've been a longtime admirer of your work in X."
- **Proof must be specific.** "We grew 4x in 6 months" beats "We've grown significantly." "I wrote the iOS chapter of Y" beats "I have experience in mobile."
- **Subject line must NOT include "Quick question", "Touching base", "Hi", or the recipient's name as a desperate hook.** See structure.md section 6.
- **Sign-off plain.** "Best, Name" or "Thanks, Name". Not "Cheers, Name" unless it matches your voice. Not "Warm regards" unless you genuinely use it.

## INVOCATION HINTS

When the user says any of:
- "write a cold email / outreach / pitch / intro request"
- "help me email this [VC / recruiter / journalist / founder]"
- "draft an outreach to ..."
- "write a follow-up to ..."
- "intro me to X via Y"
- "warm intro template"

Use this skill. If the message is internal (manager, team, peer who already knows you), use `tone-shifter` with target `friendly-professional` instead.
