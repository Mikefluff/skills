# Registers

Six named registers used by `tone-shifter`. Each register has detection markers (used to identify the source of an input) and production markers (used when generating the target).

The boundaries between registers are fuzzy — these are calibration anchors, not strict categories.

---

## 1. `casual`

Friend writing to friend. SMS/iMessage/Slack-DM territory.

**Detection markers**:

- contractions everywhere ("it's", "don't", "we'll", "should've")
- sentence-initial conjunctions ("And ...", "But ...", "So ...")
- sentence fragments
- 1st/2nd person dominant ("I", "you", "we")
- informal punctuation: ellipsis, em-dash, single hyphens for parentheticals
- minimal hedging
- colloquial vocabulary ("pretty cool", "kind of", "thing", "stuff")
- direct address ("look,", "okay,", "by the way,")
- emoji possible (not required)

**Production markers** (when shifting TO casual):

- max sentence ≤ 18 words; average ≤ 12
- contractions ON
- explicit "I think" / "we feel" hedges allowed
- one short sentence per beat — break compound sentences
- direct ask if there's an ask

---

## 2. `friendly-professional`

LinkedIn post / Substack newsletter / colleague-to-colleague Slack DM with some formality.

**Detection markers**:

- contractions present but selective
- mostly 1st/2nd person; occasional 3rd
- "Hi name," opener
- limited jargon
- mid-length sentences
- hedges present but not heavy ("probably", "we think", "in my experience")

**Production markers**:

- average sentence 14-20 words
- contractions ON for tone, OFF in headline/lead
- jargon allowed if standard in the field
- structure: hook → 2-3 points → close
- one rhetorical question OK

---

## 3. `business-formal`

Investor update, board memo, executive summary, formal email to stakeholders.

**Detection markers**:

- no contractions
- 3rd person dominant, but 1st-plural ("we") OK for org voice
- topic sentences lead paragraphs
- precise nouns, no jargon abuse
- numerics explicit ("$4.2M", "Q3 2025"), not rounded ("a few million", "last quarter")
- formal connectors ("therefore", "however", "additionally") — but no more than 2 per paragraph

**Production markers**:

- no contractions
- average sentence 18-25 words
- one claim per sentence; no run-ons
- absolute numbers, no vague magnitudes
- structure: thesis → evidence → implication → ask (if any)

---

## 4. `academic`

Journal abstract, scholarly book chapter, research paper.

**Detection markers**:

- passive voice tolerated ("it was found that ...", "the data suggest ...")
- 3rd person dominant; 1st-plural authorial "we"
- long subordinate sentences
- hedge-dense ("appears", "tends to", "may indicate", "consistent with")
- citation markers (\[1\], (Smith, 2020), "as shown in §3")
- nominalization tolerated ("the implementation of", "the consideration of")
- domain vocabulary expected

**Production markers**:

- average sentence 22-32 words
- hedges throughout — bare claims feel out of register
- citation hooks where evidence is referenced
- structure: background → method → finding → caveat
- avoid contractions, idioms, colloquialisms entirely

---

## 5. `technical`

API documentation, runbook, RFC, system-design doc, dev-blog.

**Detection markers**:

- code-fence frequent
- terms-of-art expected ("idempotent", "TTL", "ABI", "race condition")
- imperative voice for instructions ("Run X.", "Add Y.")
- 2nd person possible ("you can", "you should")
- structured headings (numbered or bulleted)
- examples follow rules
- minimal hedge density — direct statements

**Production markers**:

- short to medium sentences (12-22 words)
- code examples where useful
- one concept per paragraph
- explicit constraints ("MUST", "SHOULD", "MAY" if RFC-style)
- structure: what → why → how → caveats

---

## 6. `plain-explainer`

Wikipedia-style introductory article. Smart-novice audience. Public-radio-host voice.

**Detection markers**:

- short to medium sentences (10-18 words)
- 3rd person; minimal 1st
- avoids jargon; defines terms inline
- examples follow assertions
- hedging only where genuinely uncertain
- analogies grounded in everyday objects
- no contractions in the canonical-Wikipedia voice (but tolerated in newer style)

**Production markers**:

- vocabulary at 9th-grade reading level
- each technical term defined the first time it appears
- analogies + examples
- no in-group references ("As anyone in our field knows ...")
- structure: definition → example → why-it-matters → caveat

---

## Detection algorithm (rough)

If the user does NOT name the source register, infer it from these heuristics:

1. **Contractions present** + **1st/2nd person** + **short sentences** → likely `casual` or `friendly-professional`.
2. **No contractions** + **3rd person dominant** + **explicit numerics** → likely `business-formal`.
3. **Passive voice** + **citation markers** + **hedge-dense** → likely `academic`.
4. **Code fences** + **imperative voice** + **terms-of-art** → likely `technical`.
5. **Short sentences** + **definitions inline** + **analogies** → likely `plain-explainer`.

When two registers tie, prefer the higher-formality one. When unclear, ask the user.
