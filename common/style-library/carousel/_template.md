---
id: <ID>
modality: carousel
display: "<Human-readable name>"
mood: [<mood-tag-1>, <mood-tag-2>]
tags: [<tag-1>, <tag-2>, <tag-3>]
text_friendly: true
photoreal: false
---

# <Human-readable name>

**Vibe**: <one sentence — emotional/cultural anchor>.

**Palette**: <3-5 specific color names, e.g. "muted oat, charcoal, single rust accent">.

**Typography**: <serif/sans/display + specific reference fonts + weight/case treatment>.

**Medium**: <photograph | flat vector | 3D render | watercolor | hand-drawn | mixed + concrete descriptors>.

**Composition**: <framing rules — symmetry, negative space, rule-of-thirds, edge-bleeds, etc>.

**Style anchor (carousel)**:
> <80-150 word, model-agnostic prompt fragment appended to every slide prompt to lock the style. Single descriptive paragraph, NOT bullets. Must include: medium descriptor + palette + typography hint + composition rule + 1-2 era/cultural cues. This is the most important field.>

**Style anchor (text-in-image mode)**:
> <variant of above tuned for models that put text INSIDE the image — gpt-image-2 / Ideogram 3 / Nano Banana 2. Include explicit typography spec, example "headline 'HEADLINE TEXT HERE' in <font-style>", layout hint. ~60-100 words.>

**Best for**: <2-4 use cases — e.g. "thought-leadership posts, founder narratives, brand storytelling">.

**Avoid for**: <2-3 mismatches — e.g. "loud sales pitches, quick promo, sports brands">.

**Suggested models**: <comma list ranked by fit — e.g. "Nano Banana Pro (best identity-preserve), Flux 2 Pro, Nano Banana 2, gpt-image-2 (text mode)">.

**Caption tone**: <one-line guidance for the post copy that pairs with this aesthetic>.

<!--
Conventions enforced by `skills-styles validate`:

- Every frontmatter field listed above is required.
- id must be kebab-case (a-z 0-9 -), max ~40 chars, match the filename.
- modality must be 'carousel'.
- mood + tags are lists of lowercase strings.
- text_friendly + photoreal must be true/false (not "yes" / 1 / etc).
- Every **<field>**: marker in the body is required.
- Style anchor (carousel) must be ≥40 chars.
- NO copyrighted living artist names in any anchor text.
- NO real-brand mimicry in anchors — use era + cultural movement.
- NO emoji in any field.

Run `skills-styles validate carousel <ID>` after editing.
-->
