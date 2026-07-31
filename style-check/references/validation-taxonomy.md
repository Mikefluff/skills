# Validation taxonomy

Structured output schema for style-check verdicts. Use this when style-check should produce a **machine-readable report** (for CI/CD integration, downstream tooling, dashboards) rather than human-prose feedback.

The schema is also the structured input to `prose-edit/references/patch-refining.md` — patches consume validation findings to produce surgical fixes.

---

## Top-level structure

```json
{
  "overallScore": 75,
  "overallPassed": false,
  "scoreReasons": [
    "lack_of_specificity: Point 2 has no concrete numbers",
    "clickbait_no_payoff: Hook promises secret but text does not deliver"
  ],
  "hookAnalysis": { ... },
  "contentAnalysis": { ... },
  "structureAnalysis": { ... },
  "criticalIssues": [...],
  "improvementPriority": [...],
  "metrics": { "cta": 70, "grammar": 90, "length": 100, "style": 75 },
  "formattingRecommended": true
}
```

### Scoring rubric

- **Score: 0-100** for `overallScore` and each metric (cta / grammar / length / style)
- **Passing threshold: ≥ 80**. Below 80 → `overallPassed: false` AND `scoreReasons` MUST be populated with 3-5 reasons.

---

## scoreReasons taxonomy

When `overallScore < 80`, return 3-5 concrete reasons. Use ONLY these reason types (each entry: `"type: one-sentence explanation"`):

| Type | When to use | Example |
|---|---|---|
| `length` | Text too short/long, or wrong structure length | `"length: text exceeds the 4000-char Telegram limit"` |
| `lack_of_specificity` | Vague claims, no concrete details / numbers / examples | `"lack_of_specificity: Point 2 makes a claim about 'most people' without supporting numbers or examples"` |
| `promise_without_fact` | Hook or intro promises something not delivered or unsubstantiated | `"promise_without_fact: Hook claims '5 secrets' but only 3 actual insights given"` |
| `generic_fear` | Generic fear/appeal without concrete angle | `"generic_fear: appeal to 'falling behind' without naming what specifically is at stake"` |
| `clickbait_no_payoff` | Clickbait hook or title without resolution in text | `"clickbait_no_payoff: hook teases 'one habit that changed everything' but no specific habit is described"` |
| `filler_banality` | Filler, slogans, banalities, no insight | `"filler_banality: Point 4 is a generic productivity slogan with no original observation"` |
| `synthetic_template` | Sounds like AI template — name-dropping, formulaic CTA, "feels generic" | `"synthetic_template: contains 'therapist from Kazan said' name-dropping formula"` |
| `grammar_agreement` | Subject-verb / pronoun-antecedent / number / gender agreement errors | `"grammar_agreement: 'Никита сказала' — masculine name with feminine verb agreement"` |

This is a closed set. Don't invent new categories. If something doesn't fit, map to the closest.

---

## hookAnalysis

```json
{
  "score": 80,
  "passed": true,
  "issues": ["No CAPS word", "Sounds synthetic", "Lost curiosity"],
  "suggestions": ["Add CAPS to anchor word", "Make more conversational", "Restore genuine intrigue"],
  "improvedHook": "Rewritten hook (7-12 words, one CAPS word, ends with ':', preserves intent)"
}
```

### Hook evaluation criteria (27 checks)

For viral content, validate the hook against ALL 27 criteria from [`../../viral-text/references/hook-criteria.md`](../../viral-text/references/hook-criteria.md). The 27 criteria include:

- 7-12 words, no fluff
- One CAPS word
- Ends with ":"
- Bait bracket at the end (no commas inside)
- Specific subject + place / context
- Different transfer verb each time
- Controversy / polarizing
- No "one man said" / "some expert" patterns
- Realistic, verifiable
- Doesn't blame reader

If hook has issues — `improvedHook` MUST be populated with a NEW hook that addresses each issue, not a paraphrase.

### Hook quality red flags

- **SYNTHETIC FORMULATIONS** — "Few know", "The secret is", "Amazing fact" → these kill curiosity. Always critical.
- **LOST CURIOSITY** — hook reads like a template, no genuine spark
- **NOT NATURAL** — doesn't sound like real conversation
- **AUTHENTICITY** — marketing cliché, formulaic phrasing

Each is a critical issue requiring `improvedHook`.

---

## contentAnalysis

```json
{
  "score": 70,
  "passed": false,
  "issues": [
    {
      "type": "critical",
      "location": "Point 2",
      "problem": "Banality without insight",
      "suggestion": "Add concrete example or counter-conventional angle"
    },
    {
      "type": "warning",
      "location": "Paragraph 3",
      "problem": "Same rhythm as paragraph 2",
      "suggestion": "Vary sentence form or break with a quote"
    }
  ]
}
```

### Issue severity

- `critical` — blocks publication; must fix
- `warning` — should fix but text could ship
- `info` — observation; not a blocker

### Common content issues to check

1. **Filler, slogans, abstractions** — points without value
2. **Banal points** — obvious things, no insight
3. **Same paragraph templates** — uniform rhythm (synthetic AI signature)
4. **Paragraph generalizations at the end** — abstract conclusion vs concrete observation
5. **Few details / examples / quotes / numbers** — text reads as polotno not as ягодки
6. **No wow effect** — no "what?! I didn't know!"
7. **No polarity / provocation** — neutral statements throughout
8. **"One man said" / "some expert"** — vague attribution
9. **Paragraphs starting with questions** — viral-rule violation
10. **NEURO-TEXT** — any of the 23-category neuroslop signatures
11. **Grammar / agreement errors** — subject-verb, pronoun-antecedent, gender, number → always CRITICAL

### Synthetic / fake specificity (critical)

- Name-dropping templates ("therapist from [city] told me", "mentor with N years")
- Formulaic CTAs ("If this is you, write YES", "comment below")
- Stock metaphors ("works like a radar", "X calls X")
- "Red flags / green flags" lists without insight
- Same rhythm across all paragraphs

Each is a `synthetic_template` scoreReason and `critical` content issue.

---

## structureAnalysis

```json
{
  "paragraphsUnique": false,
  "hasDetails": false,
  "hasQuotes": true,
  "hasExamples": false,
  "hasNumbers": true
}
```

Boolean checks per structural element. Helps quickly identify what the post is missing.

---

## criticalIssues + improvementPriority

```json
{
  "criticalIssues": [
    "Banal points 2 and 4",
    "Synthetic name-drop in point 3",
    "Hook lost curiosity — sounds AI-templated"
  ],
  "improvementPriority": [
    "Rewrite point 2 with concrete examples",
    "Strip name-drop in point 3",
    "Regenerate hook — provide 3 alternatives"
  ]
}
```

- `criticalIssues` — what's specifically wrong (1 line each, ordered by severity)
- `improvementPriority` — what to do next (1 line each, paired to issues, ordered by impact)

The two lists are the actionable summary for the user.

---

## metrics (per-dimension scores)

```json
{
  "cta": 70,
  "grammar": 90,
  "length": 100,
  "style": 75
}
```

| Metric | What it scores |
|---|---|
| `cta` | For viral: hook + CTA quality + ctaWord usage. For standard: CTA present and verb-word in CTA. |
| `grammar` | Subject-verb agreement, pronoun-antecedent, gender/number, punctuation, typography |
| `length` | Text fits the target character / word range (e.g. Telegram 4000, Twitter 280, LinkedIn 3000) |
| `style` | Writer-layer + voice-layer quality (anti-neuroslop, no synthetic, voice consistency) |

Each is 0-100. The `overallScore` is roughly a weighted average but you can use it independently.

---

## formattingRecommended

```json
{
  "formattingRecommended": true
}
```

- `true` if typography / quote-style / dash-style needs cleanup OR if post should be split into multiple parts (e.g. exceeds platform limit)
- `false` if text is fine and formatter step can be skipped

This is a signal to downstream tooling — should the formatter run, or can it be skipped?

---

## Hook-only validator (when hook is checked separately)

Sometimes you want to validate ONLY the hook (e.g. before writing the body). In that case, the response is just `hookAnalysis`:

```json
{
  "score": 80,
  "passed": true,
  "issues": [...],
  "suggestions": [...],
  "improvedHook": "..."
}
```

---

## Content-only validator (when hook is validated separately)

If hook was already validated, the content pass excludes `hookAnalysis`:

```json
{
  "overallScore": 75,
  "overallPassed": false,
  "scoreReasons": [...],
  "contentAnalysis": {...},
  "structureAnalysis": {...},
  "criticalIssues": [...],
  "improvementPriority": [...],
  "metrics": {...},
  "formattingRecommended": true
}
```

---

## Pipeline integration

```
text → style-check
       ↓ (read-only, never mutates)
validation JSON (this taxonomy)
       ↓
optionally: → prose-edit (with --patches mode) consumes validation
       ↓
patches applied to original
       ↓
re-validate (loop)
```

The validation taxonomy is the **interface** between style-check and prose-edit. It's machine-readable, so downstream tools (CI, dashboards, automated refactors) can consume it.

---

## Cross-references

- Style-check pipeline (main): [`../SKILL.md`](../SKILL.md)
- Viral hook criteria (27): [`../../viral-text/references/hook-criteria.md`](../../viral-text/references/hook-criteria.md)
- Viral content rules: [`../../viral-text/references/viral-rules.md`](../../viral-text/references/viral-rules.md)
- Neuroslop catalogue (25 categories): [`../../writer/references/neuroslop-categories.md`](../../writer/references/neuroslop-categories.md)
- Synthetic constructions: [`../../writer/references/synthetic-constructions.md`](../../writer/references/synthetic-constructions.md)
- Patch-refining (consumes this taxonomy): [`../../prose-edit/references/patch-refining.md`](../../prose-edit/references/patch-refining.md)
