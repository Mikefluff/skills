# Transformation rules

For each `source → target` pair, the specific deltas to apply. Apply only the deltas listed — do not "improve" content beyond the register shift.

If a pair you need is not listed, compose two listed shifts (e.g. `academic → casual` = `academic → plain-explainer` followed by `plain-explainer → casual`).

---

## casual → friendly-professional

- Capitalize sentence-initial conjunctions if they stay; or rewrite ("And so we" → "So we" or "We").
- Replace colloquial fillers: "kind of" → "somewhat"; "thing" / "stuff" → the specific noun; "pretty good" → "good" or "competent".
- Add a topic sentence per paragraph if missing.
- Soften emoji to text (😊 → "happy to ...", "great"); remove decorative emoji entirely.
- Hedges stay; reduce frequency by ~30%.

## casual → business-formal

- Remove all contractions.
- Shift 1st-singular to 1st-plural ("I think" → "we believe") UNLESS the text is explicitly personal.
- Replace 2nd person with role names where possible ("you can" → "the team can", "the reader can").
- Promote sentence fragments to complete sentences.
- Replace colloquial vocab with precise nouns.
- Numbers must be specific — flag any vague magnitudes for the user to fill.
- Remove emoji entirely.
- Add structure: lead with the thesis, follow with evidence.

## casual → academic

- All of `casual → business-formal`, plus:
- Add hedges where claims are not strictly proven ("appears", "tends to", "may indicate").
- Allow passive voice for findings ("it was observed that ...").
- Lengthen sentences with subordinate clauses where they add nuance.
- Replace narrative connectors ("and then", "so") with logical ones ("therefore", "consequently", "given that").

## casual → technical

- Replace narrative around mechanism with imperative/declarative.
- Substantive verbs preferred over "do" / "get" ("we set up" → "configure"; "we got" → "received" or "obtained").
- Add code-fences where the original used inline-quoted code, paths, or commands.
- Numbered steps for procedures.
- One concept per paragraph.

## casual → plain-explainer

- Define jargon inline the first time it appears.
- Replace insider references with general ones.
- Anchor every abstract claim with a concrete example.
- Keep sentence length moderate (12-18 words); break long ones.

---

## friendly-professional → business-formal

- Remove all contractions.
- Promote any remaining colloquial filler to precise vocabulary.
- Replace "I" with "we" where the voice represents an organization.
- Each paragraph must have a topic sentence.
- Numerics must be explicit.

## friendly-professional → academic

- All of `friendly-professional → business-formal`, plus:
- Add hedges.
- Add citation hooks where evidence is referenced ("as discussed in §X", "(citation needed)" placeholder for the user to fill).
- Allow longer sentences with subordinate clauses.

## friendly-professional → technical

- Convert any narrative-around-process into imperative steps.
- Add code-fences where inline-quoted technical terms appear.
- Strip rhetorical questions.
- Strip hooks; replace with a one-line problem statement.

## friendly-professional → plain-explainer

- Define jargon inline.
- Drop insider references.
- Shorten sentences (max 18 words).
- One concept per sentence.

---

## business-formal → friendly-professional

- Selective contractions ON (50-60% of contractable forms).
- Re-introduce 1st/2nd person where appropriate.
- Allow one rhetorical question per piece.
- Allow one paragraph to lead with a hook before the thesis.

## business-formal → casual

- All of `business-formal → friendly-professional`, plus:
- Contractions ON 100%.
- Sentence-initial conjunctions allowed.
- Sentence fragments allowed if rhythm calls for them.
- Drop formal connectors ("therefore", "however") in favor of "and", "but", "so" where possible.

## business-formal → academic

- Add hedges.
- Allow passive voice.
- Lengthen sentences (subordinate clauses).
- Add citation hooks.
- Replace 1st-plural "we" with 3rd-person constructs where the org voice can be neutralized ("the company found X" → "X was found").

## business-formal → technical

- Convert generalized claims into specific, testable assertions.
- Add code-fences and examples.
- One concept per paragraph.

## business-formal → plain-explainer

- Define each domain term inline.
- Add examples.
- Shorten sentences.

---

## academic → casual

- Strip all hedges ("appears" → "is"; "tends to" → "does"). Push the user to confirm whether they actually want the unhedged claims.
- Strip passive voice (rewrite as active).
- Strip citation markers (or footnote them).
- Contractions ON 100%.
- Short sentences.
- 1st/2nd person.
- Replace nominalized phrases ("the implementation of X") with verb forms ("implementing X").

## academic → plain-explainer

- Strip hedges where evidence is strong; keep where genuinely uncertain.
- Define each technical term inline.
- Strip citations or move to footnotes.
- Add analogies + concrete examples.
- Shorten sentences (max 18-22 words).
- Move from passive to active.

## academic → business-formal

- Strip ~50% of hedges (keep only those that signal genuine uncertainty).
- Convert academic citations to "as we've shown" or "based on Q2 data" — the business voice rarely cites externally.
- Active voice; shorter sentences.

## academic → technical

- Strip hedges except for genuine caveats.
- Add code-fences where techniques are described.
- Strip citations or replace with direct links.
- Imperative voice for procedures.

---

## technical → friendly-professional

- Soften imperatives ("Run X." → "You can run X.").
- Convert numbered steps into prose paragraphs where flow allows.
- Allow rhetorical questions.

## technical → casual

- All of `technical → friendly-professional`, plus:
- Contractions ON.
- 1st/2nd person dominant.
- Drop code-fences inline unless they're load-bearing.

## technical → plain-explainer

- Define each term-of-art inline.
- Add analogies for abstract concepts.
- Convert procedures into "here's what happens" prose where flow allows.
- Keep code-fences but explain each before showing.

## technical → academic

- Add hedges where claims are not formally proven.
- Allow longer sentences with subordinate clauses.
- Add citation hooks.

---

## plain-explainer → business-formal

- Remove inline definitions of jargon that the business audience already knows.
- Remove some analogies — business voice tolerates abstraction more than plain-explainer.
- Lengthen sentences.

## plain-explainer → academic

- Remove most analogies (they're too colloquial for academic register).
- Add hedges.
- Add citation hooks.
- Lengthen sentences.

## plain-explainer → technical

- Replace analogies with formal definitions.
- Add code-fences.
- Imperative voice for procedures.

## plain-explainer → friendly-professional

- Keep some analogies; drop very-elementary ones.
- Allow selective contractions.
- Add a hook lead.

## plain-explainer → casual

- Contractions ON.
- Shorten sentences further.
- Drop formal definitions; let context carry the meaning.

---

## Notes

- When the target register requires removing hedges, **ask the user first** if any specific claim becomes too strong without the hedge. Hedges are sometimes load-bearing for accuracy.
- When the target register requires shortening, the rewrite may need to merge two beats into one. This is allowed; just preserve all the facts.
- When the target register requires lengthening (e.g. casual → academic), do NOT pad with filler. If a casual sentence is 8 words, the academic version may be 22 — but every added word must add structure or precision, not noise.
