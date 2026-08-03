# skills-styles — example sessions

4 realistic sessions showing how to use the skill end-to-end.

---

## Example 1 — Create a carousel style from scratch

### User says

> Create a custom carousel style called "retro-soviet-poster" — bold constructivist composition, red and beige palette, sans-serif typography in the spirit of Rodchenko-era constructivism. Should work for editorial / cultural / book carousel posts.

### What Claude does

1. Creates the skeleton:

```
~/.claude/skills/skills-styles/scripts/run.py add carousel retro-soviet-poster
```

```
  ✓ Created carousel/retro-soviet-poster.md  (from template)
    Path: /Users/.../.claude/style-library/carousel/retro-soviet-poster.md
    Next: skills-styles edit carousel retro-soviet-poster
    Then: skills-styles validate carousel retro-soviet-poster
```

2. Opens the file, fills the placeholders. Final content (excerpted):

```markdown
---
id: retro-soviet-poster
modality: carousel
display: "Retro Constructivist Poster"
mood: [bold, intellectual, austere]
tags: [editorial, typographic, geometric, two-color, propaganda-era]
text_friendly: true
photoreal: false
---

# Retro Constructivist Poster

**Vibe**: 1920s avant-garde graphic design — workers' presses, the modernist
shock of typography-as-image. Idea-first, geometry-driven, decisively framed.

**Palette**: saturated red, weathered cream, deep ink black, occasional muted ochre accent.

**Typography**: bold geometric sans (Futura Bold, Aktiv Grotesk, Druk Wide).
All-caps headlines, tight letterspacing, layered scale shifts.

**Medium**: flat 2-color print aesthetic with paper grain — letterpress / linocut
texture, slight registration offset, halftone screens for any photo elements.

**Composition**: asymmetric diagonal anchor; off-grid typography blocks; one
oversized number or letter dominating; deliberate negative space; circles + bars
as structural elements.

**Style anchor (carousel)**:
> Constructivist graphic-design poster from the 1920s avant-garde period — saturated
> red, weathered cream, deep black, occasional muted ochre. Bold geometric sans-serif
> typography in all caps with tight letterspacing and layered scale shifts. Flat
> 2-color print with paper grain texture, slight registration offset, halftone screens
> on any photographic elements. Asymmetric diagonal composition, off-grid typography
> blocks, one oversized number or letter dominating the frame, generous negative space.
> Circles, bars, and geometric primitives as structural devices. Idea-first, austere,
> decisively framed.

**Style anchor (text-in-image mode)**:
> Constructivist poster, bold geometric sans-serif headline "HEADLINE TEXT HERE" in
> all caps, tight letterspacing, layered scale shifts. Saturated red and cream
> palette, flat print aesthetic with paper grain. Asymmetric diagonal composition,
> one oversized number or letter dominating, halftone accents.

**Best for**: editorial posts, manifesto-style carousels, cultural / book / theory content, niche-intellectual brand storytelling.

**Avoid for**: friendly SaaS marketing, e-commerce product shots, kid-oriented content, anything that needs to feel inviting and modern-corporate.

**Suggested models**: Ideogram 3 Quality (best text rendering), gpt-image-2, Flux 2 Pro.

**Caption tone**: declarative, idea-forward, no hedging or hype — "This is the case for X. Here are five points."
```

3. Validates:

```
~/.claude/skills/skills-styles/scripts/run.py validate carousel retro-soviet-poster
```

```
# carousel/retro-soviet-poster  [user-only]  (/Users/.../.claude/style-library/carousel/retro-soviet-poster.md)

  ✓ valid — passes all schema checks
```

4. Optionally tests it with a real carousel:

> Use my retro-soviet-poster style for a 6-slide LinkedIn carousel about "manifesto for slow software".

Carousel-builder loads the user-override automatically (no extra flags needed — `--style retro-soviet-poster` resolves to the user file).

### What to notice

- One short conversation creates a fully-functional style that downstream skills pick up immediately.
- The skill builds the skeleton; Claude (in conversation context) fills the content based on the user's description.
- Validation is the safety net — if Claude misses a required field, validate flags it.

---

## Example 2 — Create a video style as a copy of an existing one

### User says

> Make a video style called "wong-kar-wai-tokyo" — same neon-dream grammar but tuned for Tokyo-set night scenes specifically. Use the existing wong-kar-wai-neon-dream as a starting point.

### What Claude does

1. Copies the existing style as a starting point:

```
~/.claude/skills/skills-styles/scripts/run.py add video wong-kar-wai-tokyo --from wong-kar-wai-neon-dream
```

```
  ✓ Created video/wong-kar-wai-tokyo.md  (copy of bundled 'wong-kar-wai-neon-dream')
    Path: /Users/.../.claude/style-library/video/wong-kar-wai-tokyo.md
    Next: skills-styles edit video wong-kar-wai-tokyo
    Then: skills-styles validate video wong-kar-wai-tokyo
```

2. Edits the file to specialize for Tokyo:
   - Changes `display` to "Wong Kar-wai · Tokyo night"
   - Adds tags: `[tokyo, urban-night, neon-koban, shibuya-density]`
   - Edits Color palette: emphasizes red lantern + greenish vending-machine + cyan combini light
   - Edits Cinematography anchor: bias toward rain-slick narrow streets and convenience-store interiors
   - Updates the Shot anchor to mention the rain-slick narrow streets / kanji signage / late-night vending machine glow
   - Adjusts Action vocabulary to include Tokyo-specific moves ("static behind kanji subway-station sign, character emerges through frame-right", "rain-streaked taxi window cutaway, character's reflection ghosted in glass")

3. Validates:

```
~/.claude/skills/skills-styles/scripts/run.py validate video wong-kar-wai-tokyo
```

```
  ✓ valid — passes all schema checks
```

### What to notice

- `--from <existing-id>` is the right starting point when the new style is a SPECIALIZATION of an existing one, not a fresh aesthetic.
- The skill rewrote `id:` and appended " (custom)" to display — Claude further refined display to "Wong Kar-wai · Tokyo night".
- The validator doesn't enforce that the new id be distinct from existing tags or moods — that's reviewer judgment (and reasonable for a fork like this).

---

## Example 3 — Validate and submit a music genre upstream

### User says

> I made a custom music genre called "phonk-cowbell" (slowed memphis-rap derivative, phonk subgenre with cowbell percussion). I want to submit it to upstream so other people can use it.

### What Claude does

1. Validates first:

```
~/.claude/skills/skills-styles/scripts/run.py validate music phonk-cowbell
```

Imagine it fails:

```
# music/phonk-cowbell  [user-only]  (...)

  ✗ 2 issue(s):
    - 'bpm_range' must be 'NN-NN' string (got '70')
    - body missing field: 'ElevenLabs Music prompt' (expected line starting with '**ElevenLabs Music prompt**:')
```

2. Fixes the issues by editing the file:
   - Changes `bpm_range: "70"` to `bpm_range: "65-80"`
   - Adds the ElevenLabs Music prompt block

3. Re-validates:

```
  ✓ valid — passes all schema checks
```

4. Builds the submission package:

```
~/.claude/skills/skills-styles/scripts/run.py submit music phonk-cowbell
```

```
  ✓ Submission package ready: /current/dir/style-submission-20260521-203045-music-phonk-cowbell

  Contents:
    common/style-library/music/phonk-cowbell.md
    PR-DESCRIPTION.md
    README.md  (step-by-step manual PR instructions)

  Next steps (manual, takes ~2 minutes):
    1. Fork https://github.com/Mikefluff/skills on GitHub
    2. Clone your fork, copy ... into <fork>/common/style-library/music/
    3. git checkout -b style/music-phonk-cowbell
    4. git add common/style-library/music/phonk-cowbell.md
    5. git commit -m "feat(style-library): add music style \"Phonk · cowbell\""
    6. git push origin style/music-phonk-cowbell
    7. gh pr create --body-file .../PR-DESCRIPTION.md

  Full step-by-step: cat .../README.md
```

5. The user follows the 7 steps; the PR gets reviewed and merged.

### What to notice

- Submit refuses to build a package for an invalid style (good gate).
- The package is self-contained — no need to have the skills repo cloned to run the submission flow.
- PR-DESCRIPTION.md is a fillable template, not a final body — user adds the "Why" section explaining the use case.
- Step 7 (`gh pr create`) uses the body from PR-DESCRIPTION.md — that's the only file that needs editing before submission.

---

## Example 4 — Customize a bundled style + see the diff

### User says

> The bundled kinfolk-minimal style is too cool. Make me a warmer variant with amber accents.

### What Claude does

1. Creates an override by copying the bundled style:

```
~/.claude/skills/skills-styles/scripts/run.py add carousel kinfolk-minimal --from kinfolk-minimal --force
```

(`--force` because adding `kinfolk-minimal` to user dir while the bundled one with the same id exists would otherwise be flagged.)

Actually no — this isn't quite right. Adding `kinfolk-minimal` (same id) is intentional for an override. The `add --force` is needed only if there's ALREADY a user override.

Let me redo:

```
~/.claude/skills/skills-styles/scripts/run.py add carousel kinfolk-minimal --from kinfolk-minimal
```

```
  ✓ Created carousel/kinfolk-minimal.md  (copy of bundled 'kinfolk-minimal')
    Path: /Users/.../.claude/style-library/carousel/kinfolk-minimal.md
    Next: skills-styles edit carousel kinfolk-minimal
    Then: skills-styles validate carousel kinfolk-minimal
```

Now `list` shows it as `override`:

```
*  override   kinfolk-minimal                  Kinfolk minimal (custom)
```

2. Edits the file:
   - Adds `amber-warm` to tags
   - Changes Palette: oat → warm oat with amber accent; cream → cream with amber undertone; charcoal → soft brown-charcoal
   - Updates Style anchor (carousel) to mention "amber undertones, warm-shifted color temperature" twice
   - Removes "single muted-green accent" (was the original); replaces with "single amber accent"
   - Updates Best for to mention warmer hospitality / coffee / book brand contexts

3. Reviews the diff:

```
~/.claude/skills/skills-styles/scripts/run.py diff carousel kinfolk-minimal
```

```diff
--- bundled/carousel/kinfolk-minimal.md
+++ user/carousel/kinfolk-minimal.md
@@ -3,8 +3,8 @@
 modality: carousel
-display: "Kinfolk minimal"
+display: "Kinfolk minimal (warmer)"
 mood: [calm, refined, lifestyle]
-tags: [editorial, neutral, slow-living, ...]
+tags: [editorial, amber-warm, slow-living, ...]
 text_friendly: true
 photoreal: false
 ---
@@ -15,12 +15,12 @@
 **Vibe**: ...

-**Palette**: muted oat, cream, charcoal, single muted-green accent...
+**Palette**: warm oat with amber undertone, cream, soft brown-charcoal, single amber accent...
```

4. Validates:

```
  ✓ valid — passes all schema checks
```

5. Optionally submits as a new style (NOT as a replacement — that would overwrite the bundled one which isn't what the user wants):

Actually here the user wants to KEEP the bundled cool version + ALSO have their warm variant available. The right move is to rename the user override to a different id:

```
mv ~/.claude/style-library/carousel/kinfolk-minimal.md ~/.claude/style-library/carousel/kinfolk-amber.md
# edit the id: line inside the file to match
```

Then:

```
~/.claude/skills/skills-styles/scripts/run.py validate carousel kinfolk-amber
```

```
  ✓ valid
```

This is now a NEW style, not an override. The user can submit it upstream without replacing the bundled cool variant.

### What to notice

- Override workflow is for LOCAL customization. If you want to share the variant upstream as a SEPARATE style, rename to a distinct id (the validator checks id matches filename — so updating both is required).
- The diff command makes it easy to see what changed before submitting.
- Validate keeps you honest — if you forget to rename inside the file after `mv`, it'll flag the id/filename mismatch.

---

## Anti-pattern (don't do this)

### Editing bundled files directly

Don't:

```bash
vim ~/.claude/skills/common/style-library/carousel/kinfolk-minimal.md
```

The file is bundled — it'll get overwritten on the next `install.sh --update`. ALWAYS work in `~/.claude/style-library/` (the user dir) instead, via `skills-styles add --from <id>`.

### Submitting without validating

Don't:

```
skills-styles submit carousel my-style --force
```

`--force` skips validation. The reviewer will reject styles with schema issues; you'll waste a round-trip. Validate first, fix, then submit.

### Naming styles after specific brands

Don't:

```
skills-styles add carousel notion-look
```

(Even if it's clearly Notion-inspired.) Reviewer rejects real-brand mimicry. Name by aesthetic: `gradient-mesh-modern` or `developer-platform-clean`.

### Naming carousel styles after artists

Don't:

```
skills-styles add carousel banksy-stencil
```

Use era + medium + movement: `subway-stencil-80s` is fine.
