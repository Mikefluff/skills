---
title: "Draft a viral LinkedIn / X post in English"
persona: "EN content marketer / founder / personal-brand author"
time: "10-15 minutes"
skills:
  - viral-text
  - writer
---

<!-- lint-role: catalogue -->
<!-- This walkthrough shows AI slop being cleaned, so it quotes the patterns it removes. -->

# An EN viral post in one pass

Scenario: you have a topic in your head ("how senior engineers actually use AI day-to-day"), you want a clean LinkedIn or X post ready to publish. No manual hook-tuning, no rewriting the conclusion, no scraping LLM-tells out of the draft — `viral-text` does the structural work, `writer` does the cleanup.

This is the EN counterpart of the [Russian viral-post walkthrough](viral-post.md). Most of the workflow is identical; differences are flagged below.

## Step 1. Invoke the skill

In Claude Code:

```
/viral-text how senior engineers actually use AI day-to-day lang=en platform=linkedin
```

Defaults: 5 numbered points, hook + micro-conclusion + CTA, ~250-400 words.

For X (Twitter):

```
/viral-text [topic] lang=en platform=x points=3
```

X target: ≤280 chars per post if single-tweet, or thread of 5-7 tweets if `thread=true`.

## Step 2. Research phase

The skill calls `WebSearch` for the topic and pulls 5-8 anchor sources. You see the source URLs before the draft — if a source looks irrelevant or you have a better one in mind, you can intervene with:

```
add source <url>
remove source 3
skip research
```

The research step usually takes 20-40 seconds. The skill cites the strongest 2-3 sources inline.

## Step 3. The draft

The default EN structure (controlled by `viral-text/references/viral-rules.md` § "EN viral hook patterns"):

```
HOOK
{counter-intuitive claim OR specific outcome OR named contrast}

CONTEXT
{1-2 sentences anchoring why this matters now}

THE BODY
1. {first point — lead with a verb, ≤7 words}
2. {second point}
3. ...
5. {fifth point}

MICRO-CONCLUSION
{1-2 sentences pulling the points into one frame}

NLP-FRAMED QUESTION
{open question that invites response — see below}

CTA
{specific ask: subscribe / save / share / DM}
```

### What the EN hook should NOT be

The skill enforces a hook deny-list:

- "In a world where..." — cliche
- "Have you ever wondered..." — passive
- "Let's dive in" — promises no value
- "I want to talk about..." — telegraphing the wind-up
- "🚨 BREAKING:" or any emoji-heavy opening (LinkedIn audience downgrade)

Working EN hook templates the skill will use:

- "Most people don't know..."
- "Here's what nobody tells you about {X}..."
- "I spent {N} {years/months} on {X}. The shortcut:"
- "Stop doing {X}. Start doing {Y}."
- "The biggest mistake in {X} is..."

If the first draft hook is weak, ask:

```
rewrite hook — more specific / less generic / counter-intuitive
```

### What the NLP-framed question is

Final paragraph (one sentence) that turns the post into a discussion starter. Examples:

- "What would change in your week if you tried this for 14 days?"
- "Which of these 5 do you actually do — and which one are you ignoring?"
- "If you could only keep one habit, which would it be?"

The question must be specific. Generic ones ("What do you think?") get ignored on LinkedIn.

## Step 4. The cleanup pass (automatic — `writer`)

After the skill drafts the body, it auto-runs `writer` on the result:

- Strip 25 categories of AI-slop (now with EN coverage — see `writer/references/neuroslop-categories.md` § "EN AI-style signatures")
- Typography: smart quotes (`"X"` not `"X"`), em-dashes (`—` not `--` or `-`)
- Comma-splice fixes
- Em-dash overuse trim (the classic Claude-tell — limit to 1-2 per paragraph)
- Intensifier ladder trim ("truly remarkable" → "remarkable")
- Balance-hedge removal ("while there are valid points on both sides..." → just pick a side or remove)

EN-specific patterns automatically caught and stripped:

- "It's important to note that..." → cut entirely
- "delve into" → "look at" / "explore"
- "tapestry of" → cut metaphor
- "navigate the complexities of" → "deal with"
- "in today's fast-paced world" → cut intro
- "in conclusion" as paragraph opener → cut
- Triplets of synonyms ("smart, capable, and intelligent") → pick one

## Step 5. Review

The output appears as a single fence-block. Read through it once:

- Hook lands in ≤12 words? If not: "rewrite hook"
- Does the body have one idea per point? If two ideas got merged: "split point N"
- Is the conclusion specific, not generic? "rewrite conclusion — more specific"
- CTA: does it ask for one clear action? If vague: "rewrite CTA — clearer ask"

Common edits at this stage:

```
shorten — target 250 words
expand point 3 — add concrete example
swap points 2 and 4
add source for claim X
```

## Step 6. Copy out

The final block is ready to paste into LinkedIn / X / Substack / Threads / etc.

For LinkedIn, you may want to add line breaks between paragraphs (`viral-text` outputs them, but some pasting workflows collapse them).

For X threads (`platform=x thread=true`), each tweet is on its own line with `1/` `2/` numbering. Paste-as-thread tools (Hypefury, Buffer, native X) usually preserve this.

## Common edits — quick reference

| What you want | How to ask |
|---|---|
| Hook too generic | `rewrite hook — counter-intuitive` |
| Points too generic | `rewrite point N — more specific` |
| Conclusion is filler | `rewrite conclusion — name a specific outcome` |
| Whole thing too long | `shorten to ~250 words` |
| Too AI-sounding | `re-run writer pass — strict mode` |
| Wrong tone for audience | use [`tone-shifter`](../USER-GUIDE.md#tone-shifter--register-rewrites) to shift to `casual` or `business-formal` |

## What `viral-text` does NOT do

- Write the post for a private audience (use [`cold-email`](../USER-GUIDE.md#i-want-to-write-a-cold-email) — different rules)
- Write longform essays (use [`essay-write`](non-fiction.md))
- Translate from RU to EN (use [`translation-sync`](translation-parity.md) for that — but `translation-sync` is read-only; for a translation rewrite use `tone-shifter` or write fresh in EN)
- Schedule the post (use your social-media scheduling tool)

## Troubleshooting

### "Hook is dead-generic. I asked for counter-intuitive."

The model sometimes plays it safe. Try: `rewrite hook — make it controversial, take a stance, willing to lose 20% of audience`. The skill respects this — it'll narrow the hook even if it costs reach.

### "Skill cited a source I don't trust."

Just `remove source N` — the skill will rewrite the claim that depended on it.

### "Output passes `writer` but still reads AI."

Two paths:
1. `re-run writer pass — strict mode` (forces a second pass with tighter heuristics)
2. Manual: copy the post, open the relevant references file (`viral-text/references/viral-rules.md` or equivalent), spot-check against your voice samples, and `prose-edit` it for voice.

### "X thread mode broke — tweets are over 280 chars."

The skill respects 280 chars per tweet, but counting emoji + URL bytes is imperfect. Ask: `shorten tweet 3 — target 240 chars`.

### EN clean-prose linter false-positive on legitimate prose

If `writer/scripts/lint.py` fires on prose you know is clean, file a bug with the fragment. The EN regex set is younger than the RU one and may need tightening.

## Related

- [Viral post (RU)](viral-post.md) — same workflow, Russian audience
- [Cold email](../USER-GUIDE.md#i-want-to-write-a-cold-email) — for one-to-one outreach instead of broadcast
- [Style-check gate](style-check-gate.md) — to verify the post passes a read-only quality bar before publishing
- [Tone-shifter](../USER-GUIDE.md#tone-shifter--register-rewrites) — to retarget the same content for a different audience register
