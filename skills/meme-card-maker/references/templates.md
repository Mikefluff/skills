# Meme templates — anatomy + composition cues

5 supported templates + `custom`. Each describes the canonical layout the model approximates.

---

## `drake` (Drake Hotline Bling)

**Anatomy**: 2-panel vertical stack.
- Top panel: Drake making "no thanks" face, left-side-pointing. Caption labels the rejected option.
- Bottom panel: Drake making "yes please" face, left-side-pointing. Caption labels the approved option.

**When to use**: comparing 2 options where one is clearly preferred (often joking that the unconventional / harder option is the "good" choice).

**Caption pattern**:
- top: the rejected option
- bottom: the approved option

**Example**:
- top: "USING JIRA TO TRACK BUGS"
- bottom: "CRYING IN THE SHOWER"

**Composition cue**: 2 panels stacked, captions on the right side of each panel, Impact font with stroke.

---

## `distracted-boyfriend`

**Anatomy**: 3-character horizontal composition.
- Left: man walking with girlfriend (the "expected" choice)
- Middle: girlfriend looking shocked
- Right: man looking back at woman in red dress (the "tempting" alternative)

**When to use**: showing temptation / distraction from the "right" choice.

**Caption pattern**:
- top (optional): general context
- bottom or label-overlay-style: 3 labels — "boyfriend = me", "girlfriend = my project", "woman in red = new shiny tech"

**Composition cue**: 3 characters, labels overlay each face/character.

**Note**: caption-as-overlay is harder for image-gen than top/bottom blocks. Skill cues "labels overlaid on each of the 3 characters identifying them" — model approximates.

---

## `expanding-brain`

**Anatomy**: 4-panel vertical stack, each panel showing a progressively larger / more "enlightened" brain.
- Panel 1: small brain (basic / dumb idea)
- Panel 2: glowing brain (better idea)
- Panel 3: brain expanding beyond skull (smart idea)
- Panel 4: galaxy / transcendent brain (galaxy-brain idea)

**When to use**: ascending series of "ideas" from basic to absurd-galaxy-brain.

**Caption pattern**: 4 captions, one per panel.

**Skill simplification**: in v1, we only support 2 captions (`--top` = panel 1, `--bottom` = panel 4). For full 4-panel: include all 4 in `--top` separated by ` / ` (e.g., "USE FORMATTER / USE LINTER / USE TYPE CHECKER / DELETE THE CODE").

**Composition cue**: 4 stacked panels, brain icon left + caption right per panel.

---

## `two-buttons` (Sweaty Decision)

**Anatomy**: sweaty man (often hand near 2 red buttons) deciding between 2 options.

**When to use**: showing agonizing decision between 2 things that are actually the same / obvious.

**Caption pattern**:
- top: "[red button text] · [red button text]" (the two options)
- bottom: short label of the decision-maker's role (optional)

**Composition cue**: sweaty character + 2 labeled red buttons.

---

## `change-my-mind`

**Anatomy**: seated man (Steven Crowder) at a folding table with a sign reading the meme caption. Often outdoors.

**When to use**: stating a controversial / contrarian opinion as if inviting debate.

**Caption pattern**:
- top: usually unused or "CHANGE MY MIND" label
- bottom: the opinion / claim

**Composition cue**: seated character at table with prominent sign showing the bottom caption.

---

## `custom` (default)

**Anatomy**: model generates the centerpiece based on `--context` or the captions themselves.

**When to use**: when the joke doesn't fit a known template — let the model interpret.

**Caption pattern**: top + bottom standard placement.

**Composition cue**: "classic internet meme template aesthetic, centerpiece image relevant to the captions, top caption + bottom caption in Impact-style typography".

---

## Per-template prompt template hints

All templates share:

1. **Impact-style typography** — bold white text with thick black stroke outline, all caps for English captions.
2. **Caption placement** — top caption near top edge, bottom caption near bottom edge, both centered horizontally.
3. **Image quality cues** — "classic internet meme template aesthetic, low-fidelity, slight compression artifacts for authenticity" (counter-intuitively, slightly-degraded looks more authentic for memes).
4. **No watermarks / signatures** — the template should be clean.

---

## Decision tree

```
Comparing 2 options, one obviously preferred
  → drake

Showing temptation / distraction from right choice
  → distracted-boyfriend

Series of escalating ideas (basic → galaxy-brain)
  → expanding-brain

Agonizing decision between similar options
  → two-buttons

Stating controversial opinion
  → change-my-mind

Custom joke / not template-shaped
  → custom (default)
```

If the user describes the meme by content without naming a template, infer the closest template from the caption structure:

- "X vs Y" with preference → drake
- "When X but also Y" → distracted-boyfriend
- "Just X / Actually Y / Galaxy brain Z" → expanding-brain
- "Choosing between X and Y" (joking they're the same) → two-buttons
- "[opinion]. change my mind." → change-my-mind
