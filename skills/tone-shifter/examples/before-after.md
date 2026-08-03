# tone-shifter — calibration before/after pairs

Four representative shifts. Each shows the source register, target register, the deltas applied, and the resulting rewrite. Use these as ground truth when calibrating the skill — if a real output diverges from these, prefer the calibration.

---

## Example 1 — `casual → business-formal`

**Source (casual)**

> So we're thinking we'll launch the beta in like late March, maybe April. Honestly, the team's been killing it — we shipped the auth flow in 2 weeks instead of the 6 we'd planned. There's a couple of bugs left but nothing scary. We just need to lock in the pricing tiers and we're good to go.

**Deltas applied**

- contractions OFF (`we're`, `we'd`, `we're`, etc.)
- 1st-singular → 1st-plural (kept "we" — already plural)
- vague magnitudes → explicit ("like late March, maybe April" → "late March 2026")
- colloquial vocab → precise ("killing it" → "exceeded expectations"; "a couple of bugs" → "two outstanding bugs"; "scary" → "blocking")
- topic sentence added per paragraph
- promoted to one claim per sentence

**Target (business-formal)**

> We are on track to launch the beta in late March 2026. The team has exceeded expectations: the auth flow shipped in two weeks against a six-week plan. Two outstanding bugs remain; neither is blocking. The remaining gate is the pricing-tier decision.

---

## Example 2 — `academic → plain-explainer`

**Source (academic)**

> Recent work in machine learning has demonstrated that the predictive performance of transformer-based language models tends to scale logarithmically with the number of parameters, conditional on training data adequacy (Hoffmann et al., 2022). This relationship, while consistent across the explored parameter range, may exhibit diminishing returns beyond a yet-undetermined threshold.

**Deltas applied**

- citation marker → footnote/reference moved out (here: dropped, with note that user should re-attach)
- hedges adjusted — kept "may exhibit" (genuine uncertainty), removed "tends to" (well-established)
- nominalization → verb form ("the predictive performance" → "models predict better")
- analogy added ("logarithmically" → "but each doubling helps less than the last")
- inline definitions ("transformer-based language models" → "the language models behind tools like ChatGPT")
- shortened sentences

**Target (plain-explainer)**

> Recent research has shown that the language models behind tools like ChatGPT predict better when they have more internal parameters — but each doubling helps less than the last. This pattern holds across all the model sizes researchers have tested. It might break down at some point, but no one has found that point yet.

---

## Example 3 — `business-formal → friendly-professional`

**Source (business-formal)**

> Q3 revenue increased 24% year-over-year, driven primarily by enterprise expansion in the EMEA region. The company onboarded 17 new logos exceeding $100K ARR. Sales-cycle compression of 18% indicates improved product-market fit. Looking forward, we anticipate Q4 to track ahead of plan, contingent on the renewal of three strategic accounts.

**Deltas applied**

- selective contractions ON ("we are" stayed; nothing else was contractable in source)
- "the company" → "we" for organizational voice
- "year-over-year" → "from last year" (less formal)
- hook lead allowed
- "logos" jargon — kept (audience knows it)
- rhetorical question allowed (used at end)

**Target (friendly-professional)**

> Q3 was strong. Revenue grew 24% from last year, mostly from new enterprise customers in EMEA. We brought on 17 new logos over $100K ARR, and our sales cycle got 18% shorter — a good sign that product-market fit is improving. We expect Q4 to track ahead of plan, assuming three strategic renewals close. Want the breakdown by segment?

---

## Example 4 — `technical → casual`

**Source (technical)**

> To prevent race conditions when multiple workers update the shared cache, wrap mutations in a Redis `WATCH`/`MULTI`/`EXEC` transaction. Workers that detect a watch-failure must retry with exponential backoff (jitter recommended). The lease TTL should match the worst-case worker timeout to prevent indefinite locks.

**Deltas applied**

- imperative voice → narrative
- 2nd-person allowed
- jargon retained where audience knows it (Redis terms kept — `WATCH`/`MULTI`/`EXEC`)
- shorter sentences
- contractions ON
- procedure → "here's how" prose

**Target (casual)**

> Race conditions are the classic worker-cache problem. The fix: wrap every mutation in a Redis transaction (`WATCH`/`MULTI`/`EXEC`). If your worker hits a watch-failure, just retry — but use exponential backoff with jitter, otherwise everyone retries at the same moment and you get a thundering herd. One more thing: pick the lease TTL based on your worst-case worker timeout. Anything shorter and you'll get locks that never clear.

---

## Calibration notes

- The shift IS the work. Do not "improve" the source beyond the register change. If example 1's source had a factual error, the target would carry the same error — that's `prose-edit`'s job, not `tone-shifter`'s.
- Where two registers can express the same idea in similar length (e.g. `friendly-professional → business-formal`), the target is often only 5-10% different in word count.
- Where registers are far apart (e.g. `academic → casual`), expect 30-50% word-count change and significant restructuring.
- Always pass through `writer` as final cleanup before returning the result.
