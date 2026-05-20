# Banned patterns

Every pattern here is an automatic strip. Do not soften them — remove or rewrite.

> **See also (shared across cold-email / landing-copy / release-notes):**
> [`common/references/banned-patterns-hype.md`](../../common/references/banned-patterns-hype.md) ·
> [`common/references/banned-patterns-preambles.md`](../../common/references/banned-patterns-preambles.md)

---

## Ceremony openers (strip on sight)

Greeting preambles ("I hope this email finds you well", "Hope all is well", etc.) live in
[`common/references/banned-patterns-preambles.md`](../../common/references/banned-patterns-preambles.md).
The base linter catches them under `WEAK_OPENER`.

Outreach-specific ceremony — strip these too:

- "I'll keep this brief."
- "I know you're busy, so I'll get right to the point."
- "Sorry for the cold email."
- "Apologies for reaching out unsolicited."

Why banned: they announce a behavior instead of demonstrating it. If you respect the recipient's time, prove it by getting to the point — don't promise it.

---

## Vague intros

- "I'm reaching out because ..." — passive; replace with the actual reason.
- "I came across your profile / company / work ..." — generic. Be specific: "I read your essay on X" / "I saw {company} announced Y".
- "I've been following your work for a while ..." — flattery without proof. Either cite a specific piece, or skip.
- "I'm a big fan of your {company / podcast / book}." — flattery. The recipient assumes you're not.
- "I wanted to introduce myself and ..." — wasted line. Just start with the hook.
- "I noticed you ..." — passive. "You shipped X" is direct.

---

## Hedge language (strip or replace)

- "I was wondering if ..."  → direct ask
- "I would love to ..." → "I'd like to ..." (and prefer just stating the ask)
- "It would be amazing if ..." → "Could we ..."
- "I was hoping that maybe ..." → "Could we ..."
- "Just wanted to ..." → "Wanted to ..." (still weak — usually delete the whole "wanted to" frame)
- "I might be wrong, but ..." → assert directly; the recipient will tell you if you're wrong

---

## Follow-up specific bans

- "Just bumping this up." — explicitly forbidden
- "Just following up." — explicitly forbidden
- "Bumping this." — explicitly forbidden
- "In case my last email got buried ..." — implies your email is buryable
- "I know you must be slammed, but ..." — apologizing-for-existing
- "Sorry to be a pest." — never
- "I'll stop bothering you after this." — never

Better follow-up openers:
- "Following up on {date} re {topic}." (factual)
- "Quick re-ask: {one specific sentence}." (direct)
- "{New context that justifies the bump}." (anchored to news)

---

## Closing line bans

- "Looking forward to hearing from you!" — empty, expectant; strip
- "Excited to potentially work together!" — premature; strip
- "Hoping for your favorable response." — never
- "Awaiting your reply." — never
- "TIA" / "TYIA" / "Thx" — looks needy or rushed
- "Cheers!" with exclamation — too perky for first-touch unless your normal voice
- "Have a great day!" — generic; if your voice does this, fine, but don't default to it

Better closes:
- "Happy to send the deck cold." — offers next step
- "Or a 'no' is fine — won't follow up further." — gives them an out
- "If this is the wrong person, who should I ask?" — useful re-route

---

## Self-deprecation that backfires

- "I know this is a long shot, but ..." — telegraphs low confidence
- "I'm probably one of many emails today ..." — yes, and?
- "I doubt you have time for this, but ..." — already lost
- "This is a bit of a Hail Mary ..." — desperation

If you genuinely have low confidence, don't send the email. If you're sending it, write it confidently.

---

## "We" when you mean "I" (in solo outreach)

If you are reaching out alone, do not use plural "we" — the recipient will think you're a marketing automation. Use "I". (Exception: when "we" means your company, and the ask is org-level.)

---

## Multi-paragraph windup

> "Hi {Name},
>
> I hope this email finds you well. My name is X and I've been working in the Y space for over Z years. I've had the pleasure of building several products in this domain, and I'm now leading a new initiative at {Company} that I think might be of interest to you.
>
> I'd love to set up a call to discuss potential synergies between our work and your portfolio. Below I've attached a one-pager that gives more context ..."

Everything above this line is a strip. The ENTIRE email could be:

> "Hi {Name}, we just shipped {product} after {Z years} in {Y space}. Worth 15 min next week to see if it fits {their fund / their company / their use case}?"

---

## Subject-line bans (re-listed)

- "Quick question"
- "Touching base"
- "Hi" / "Hi {Name}"
- "Hello"
- "Following up"
- "Are you the right person at {company}?"
- "Opportunity to [anything]"
- ALL CAPS subjects
- `[URGENT]` / `[!]` / `[ACTION NEEDED]`
- Emoji in subject (unless cultural fit)

---

## Genuine names that look templated

Real cold emails sometimes use these because templates use them. Avoid them even when they're true:

- "I noticed your team just raised a Series A — congrats!" — read as template
- "Loved your recent post on {topic}!" — read as template
- "Saw you're hiring for {role} — wanted to reach out personally!" — read as template

If your specific compliment is real, prove it with a specific detail. "Your point about X in the {publication} essay is what made me reach out — I built Y based on similar reasoning" beats "Loved your recent post!"

---

## When in doubt — the audit question

For every sentence in the draft, ask: "Does this earn the next sentence?"

If yes, keep. If no, cut.

Then run `writer/scripts/lint.py` on the result to catch anything regex-detectable that survived.
