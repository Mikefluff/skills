# Patch-refining strategy

A surgical-edit pattern for prose rewrites — instead of regenerating the entire text, produce small **search/replace patches** that get applied programmatically. The unchanged parts remain bit-identical.

This is an alternative to the default `prose-edit` flow (which rewrites a whole passage). Use patch-refining when:
- The user wants **minimal-change** edits ("just fix the broken sentences, don't touch the rest")
- The passage has **significant prose that should NOT change** (quotes, dialogue blocks, specific phrasing the user owns)
- You want **diff-able**, **reviewable** changes
- Long passages where regeneration risks introducing new errors elsewhere

---

## The pattern

```
input passage + validation report (or user-pointed issues)
       ↓
LLM produces a list of patches: { search: "...", replace: "...", reason: "..." }
       ↓
applyPatches() applies each programmatically (search must match exactly)
       ↓
report: { applied: [...], failed: [...], changePercent: X }
       ↓
if changePercent > 50% OR failed > applied → signal fallback to full rewrite
```

The LLM never sees the "after" text. It sees the "before" + the issues. It returns ONLY the deltas.

---

## Patch schema

Each patch is a structured object:

```json
{
  "search": "exact text to find (verbatim, with surrounding context if needed for uniqueness)",
  "replace": "the replacement text",
  "reason": "why this change — e.g. 'staccato cleanup', 'comma-splice fix', 'remove neuro filler'"
}
```

### Search-fragment rules

- `search` must match the original VERBATIM — punctuation, spaces, casing
- If a phrase appears multiple times and only one occurrence should change, include enough surrounding context to make the match unique
- Example: text has 3 "and" — to change one specific "and", search must be `"the cat and the dog"` not just `"and"`
- Whitespace matters — newlines, double-spaces, all preserved

### Replace rules

- `replace` can be shorter, longer, or empty (empty = delete)
- If reordering, do it as one patch (search the whole chunk, replace with reordered version)
- Don't try to be clever — straightforward search→replace, one transformation per patch

---

## When patches fail

A patch can fail because:
1. `search` doesn't match the original text exactly (whitespace, casing, escape chars)
2. Same `search` appears multiple times and the patch is ambiguous
3. Two patches collide (the second's `search` would have changed if the first applied)

The applyPatches function reports `failed: [...]` with the failure reason.

### Fallback rule

If `failed.length > applied.length` OR `changePercent > 50%`:
- The patch approach isn't appropriate for this passage (too many changes needed, OR LLM is hallucinating fragments that don't exist)
- Fall back to the default `prose-edit` full-rewrite flow

---

## When NOT to use patches

- **Translation**: patches won't help — every sentence changes
- **Voice shift**: the whole passage's voice changes; patches are wrong tool
- **Restructuring** (reordering paragraphs, merging two paragraphs): patches OK only if the structure changes are minimal
- **Significant rewrite** (>50% of the prose): just regenerate; patches are friction without benefit

Use patches when 90%+ of the original text should survive untouched.

---

## Pipeline integration with `prose-edit`

In `prose-edit`'s normal flow, the LLM rewrites a whole passage. The patch variant inserts BEFORE that:

```
1. User invokes /prose-edit chapter ch07.md
2. Default: full rewrite
3. With --patches flag: patch-refining mode
4. LLM produces patches list
5. applyPatches() runs programmatically
6. Report: shows applied vs failed patches
7. If fallback signalled → fall through to full rewrite
8. Else: present diff to user (search → replace pairs)
9. User accepts/rejects each individually
```

This gives users **per-change control** — accept the staccato cleanup, reject the voice shift, etc.

---

## LLM prompt template (patch mode)

```
You are reviewing this passage. Produce a list of SEARCH/REPLACE patches to fix the issues below. DO NOT rewrite the whole text. ONLY produce patches.

PASSAGE:
{original text}

ISSUES TO FIX:
{validation report — staccato in para 2, comma-splice in para 4, etc.}

OUTPUT JSON:
{
  "patches": [
    {
      "search": "verbatim text to find (with surrounding context if needed for uniqueness)",
      "replace": "the replacement",
      "reason": "what kind of fix — staccato, comma-splice, neuro filler, etc."
    },
    ...
  ],
  "analysis": {
    "problems": ["list of problems you saw"]
  }
}

RULES:
- Each search fragment MUST match the original VERBATIM
- If a phrase appears multiple times, include enough context to make it unique
- One transformation per patch
- DO NOT introduce new claims — only edit existing
- DO NOT change quoted speech or block quotes
- If a fix needs more than 5 patches in a single paragraph — flag it and signal fallback
```

---

## Example

### Original passage

```
Анна шла. Она шла медленно. Она думала. Дождь шёл. Никольская была пуста.
Она вышла из дома, но не помнила зачем. Не зачем, не куда, не во сколько.
Просто вышла. Просто шла. Просто думала.
```

### Issues (from validation)

- Staccato: paragraph 1 (5 short sentences in a row)
- Double-negation: "Не зачем, не куда, не во сколько"
- "Просто" обрубки: paragraph 3 (3x "Просто...")

### Patches produced

```json
{
  "patches": [
    {
      "search": "Анна шла. Она шла медленно. Она думала. Дождь шёл. Никольская была пуста.",
      "replace": "Анна шла медленно по пустой Никольской, думая о чём-то под мелким дождём.",
      "reason": "staccato cleanup — 5 short sentences merged with subordinate construction"
    },
    {
      "search": "Не зачем, не куда, не во сколько.",
      "replace": "Вышла наугад — ни цели, ни направления, ни времени.",
      "reason": "double-negation → contrast/specification form"
    },
    {
      "search": "Просто вышла. Просто шла. Просто думала.",
      "replace": "Шла. Думала. Дождь не утихал.",
      "reason": "просто-обрубки → varied sentence forms"
    }
  ],
  "analysis": {
    "problems": ["staccato in p1", "double-neg in p2", "просто-обрубки in p3"]
  }
}
```

### After programmatic apply

```
Анна шла медленно по пустой Никольской, думая о чём-то под мелким дождём.
Она вышла из дома, но не помнила зачем. Вышла наугад — ни цели, ни направления, ни времени.
Шла. Думала. Дождь не утихал.
```

Three patches, 100% applied, ~40% character change.

---

## When the user reviews patches

Present each patch as a diff:

```
PATCH 1 of 3 — staccato cleanup
─────────────────────────────────────────
- Анна шла. Она шла медленно. Она думала. Дождь шёл. Никольская была пуста.
+ Анна шла медленно по пустой Никольской, думая о чём-то под мелким дождём.

Accept? [y/N/edit]
```

The user accepts, rejects, or hand-edits each patch. The final passage applies only accepted patches.

---

## Cross-references

- Full prose-edit pipeline (default mode): [`../SKILL.md`](../SKILL.md)
- Structural patterns this catches: [`../../writer/references/structural-prose.md`](../../writer/references/structural-prose.md)
- Voice patterns it should NOT touch: [`voice.md`](voice.md)
- When to fall back to full rewrite: see "Fallback rule" above
