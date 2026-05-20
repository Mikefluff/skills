# Validation — Step 5 Writer Pass + Viral Layers

After the writer's 4-layer cleaning pass, run the two viral-specific layers below, then the "would I repost this?" reader-test. Do NOT show intermediate validation steps to the user — only the final clean text.

## Step 5: WRITER PASS (mandatory)

Apply the `writer` skill's 4-layer cleaning pass:
- Layer 1: full neuroslop regex check (20 categories, ~80 patterns)
- Layer 2: structural synthetics (staccato, double negations, "Просто ---" chunks, inversions, repetitions)
- Layer 3: surgical patches
- Layer 4: read-aloud final pass

In addition, run two viral-specific validations:

**Viral Layer A — Hook validation:**
Re-check the hook against ALL hook criteria. Key checks:
- Is it 7-12 words? Does it end with colon?
- One word in CAPS? Bait bracket at the end?
- Does it sound synthetic/formulaic? ("Few people know", "Amazing discovery")
- Does it spark genuine curiosity or just clickbait?
- Specific character + location? Unusual transfer verb?

If the hook fails any critical criterion — rewrite it.

**Viral Layer B — Content validation (42 rules + structure):**
- Are all points unique in form? (no two quotes, no two stories, no two data-points)
- Does each point have polarity/provocation? (rule 37)
- Any filler, banalities, or generalizations at the end of paragraphs?
- Any synthetic name-dropping? ("therapist from [city] told me", "mentor from X with N years")
- Any CTA cliches?
- Does the text sound like "a typical viral post"?
- Are all points approximately equal length? (no point 2x longer than another)
- Does fullText start with "1. "? Correct number of points?
- Is there a separate micro-conclusion paragraph between last point and CTA?
- Empty lines between all points?
- Count characters. Is the text within platform limits?
- Score the content mentally 0-100. If below 85 — fix before output.

If length exceeds limit — trim the longest point first, preserving CTA and micro-conclusion.

**Final pass — the "would I repost this?" test:**
Read the complete text one more time as a reader, not an editor:
- Would you save this? Would you send to a friend?
- Does every point deliver a genuine "wow"?
- Does the hook make you NEED to read the body?
- Is this clearly better than 90% of content on the topic?

If anything feels mediocre — fix it. If it's good — output it.

IMPORTANT: Do NOT show intermediate validation steps to the user. Only show the final clean text. The cleaning happens silently. If you had to make significant fixes, you may briefly note: "Cleaning fixed N issues" after the text.
