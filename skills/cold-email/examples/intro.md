# Intro request — calibration

You are asking a mutual contact (the intro-giver) to introduce you to a third party (the target). The skill produces TWO outputs: the email to the intro-giver + the forwardable block they can paste to the target.

---

## Scenario — founder asks an advisor to intro them to a CISO at a target customer

**Context.** Founder building a B2B-security SaaS. Wants the advisor (former CISO at a different company) to introduce them to the CISO at MegaCorp, a target enterprise customer. The advisor knows the target through a SecOps forum.

### Email A — to the intro-giver (advisor)

> Subject: Intro request: {Target Name} at MegaCorp?
>
> Hi Marcus,
>
> Could you intro me to {Target Name} at MegaCorp? We just hit GA on the audit-log compression product — relevant to a problem MegaCorp's SecOps team has flagged publicly twice this year (5x audit-log storage cost growth).
>
> Forwardable below — only if you're comfortable.
>
> Best,
> John
>
> ---
>
> Forwardable for {Target Name}:
>
> Subject: Audit-log compression — 73% reduction at three enterprise SecOps teams
>
> Hi {Target Name},
>
> Marcus suggested we should connect.
>
> Acme just shipped audit-log compression — averaging 73% storage reduction across three enterprise customers, with zero query-latency regression.
>
> Saw MegaCorp's recent posts about audit-log cost growth. Worth 20 minutes to see if it's relevant?
>
> Happy to send a one-pager cold. Otherwise no obligation — thanks Marcus.
>
> John Smith
> CEO, Acme · acme.co

---

### Why the structure works

**Email A** (to advisor):
- One ask, one sentence
- One specific reason ("relevant to a problem MegaCorp's SecOps team has flagged publicly twice this year")
- Forwardable explicitly offered ("only if you're comfortable")
- No bio for the advisor — they know who you are

**Forwardable** (the block):
- Anchored to advisor's reputation in 1 line ("Marcus suggested we should connect")
- One specific proof in 1 sentence ("73% storage reduction across three enterprise customers")
- Anchored to the recipient's own public problem
- The advisor's name in the sign-off thanks them by name — frame for them
- 80 words exactly

---

## Common errors in intro requests

### Error 1 — burying the ask

> Hi Marcus,
>
> Hope you're doing well — it's been a while since we caught up at the SecOps forum. I've been thinking about the conversation we had about audit-log infrastructure ...

The advisor has to read 50 words to find out what you want. By word 50 they're already thinking about something else.

### Error 2 — asking the advisor to do the writing

> Hi Marcus, would you be open to intro me to {Target Name} at MegaCorp?

No forwardable. Now the advisor has to draft the email. They will not.

### Error 3 — over-stuffed forwardable

> Forwardable for {Target Name}:
>
> Hi {Target Name},
>
> Marcus and I went to college together where we both studied computer science, and we've been collaborating on security tooling for almost a decade. He thought you'd be interested in what we're building at Acme...

The forwardable should NOT explain the advisor. The advisor explains themselves.

### Error 4 — forwardable for someone the target shouldn't know

> Forwardable for {Target Name}:
>
> Hi {Target Name},
>
> John reached out to me about ...

NO. The forwardable is from the advisor's perspective ("Marcus suggested we should connect"), pasted by the advisor into a NEW thread with the target. It is NOT a third-person summary.

---

## Variant — re-engage warm intro

If the intro-giver has already introduced you to the target months ago and that thread went cold, the follow-up should be addressed directly to the target, not the intro-giver:

> Subject: Re: Marcus connected us — audit-log compression
>
> Hi {Target Name},
>
> Following up from Marcus's intro in {month}. We hit GA last week with the audit-log compression product.
>
> Across three enterprise customers, 73% average storage reduction, zero query-latency regression.
>
> Worth 20 minutes now? Or "no" is fine.
>
> Best,
> John

Note: this is now a re-engage email, not an intro request. Different template — see `references/structure.md` `re-engage` variant.

---

## Rules from these examples

1. **Two outputs per intro request**: email to intro-giver + forwardable block.
2. **Forwardable is from the intro-giver's perspective**, pasted into a NEW thread, addressed to the target.
3. **The forwardable thanks the intro-giver by name** in the sign-off — gives them attribution they can show their network.
4. **Anchor to the target's own public problem** — the forwardable is one sentence of YOUR proof, one sentence of WHY THEM.
5. **Total budget**: email A ≤80 words + forwardable ≤80 words.
