---
id: <ID>
modality: video
display: "<Director name + descriptor>"
mood: [<mood-tag-1>, <mood-tag-2>]
tags: [<cinematography-tag-1>, <cinematography-tag-2>, <cinematography-tag-3>]
pacing: medium
dialogue_friendly: true
---

# <Director name + descriptor>

**Inspired by**: <single director's body of work — name films explicitly so the AI model can lock>. Use this style WITHOUT including the director's name in the actual model prompt (their name is for the user, not the API).

**Cinematography anchor**: <one paragraph describing the visual language: lens, depth, lighting, color treatment, motion, framing convention. 100-150 words. Model-agnostic so it works with Veo 3.1 / Sora 2 / Kling 3.0 / Runway Gen-4>.

**Color palette**: <3-5 concrete colors that recur across this style>.

**Lens & framing**: <focal length, depth-of-field convention, common framings — e.g. "anamorphic 2.39:1, shallow DoF, dutch-tilt low-angle for character intros, centered medium for dialogue">.

**Lighting**: <e.g. "hard top-key, deep shadows below eye line, single colored practical visible in every frame">.

**Motion language**: <camera motion conventions — handheld? tripod? dolly? zooms?>.

**Editing rhythm**: <cuts per minute, cut style — match-on-action, smash-cut, dissolve, long take?>.

**Shot anchor (per-shot prompt fragment)**:
> <80-150 word fragment that will be APPENDED to every shot's prompt to lock the style. Single descriptive paragraph. Pure visual language — no narrative content. Model-agnostic. This is the most important field. NEVER include the director's name here.>

**Action vocabulary**:
- <8-12 SPECIFIC camera + character moves this style uses — e.g. "slow push-in to face on emotional reveal">
- <"static wide of room with character entering frame-left">
- <"whip pan with sound cue">
- <"dolly track parallel to walking subject">

**Sound design implications**: <2-3 lines about audio expectations — diegetic? scored? wall of sound? long ambient?>.

**Best for**: <2-3 use cases — e.g. "product reveal, narrative micro-doc, character monologue">.

**Avoid for**: <2-3 anti-fits — e.g. "kinetic sports edits, comedy, quick CTA">.

**Suggested duration**: <"3-shot × 6s" / "1-shot × 10s" / etc — what works best at reel length>.

**Suggested music style**: <one music-library ID that pairs well — e.g. "ambient-drone" or "cinematic-orchestral">.

<!--
Conventions enforced by `skills-styles validate`:

- pacing must be one of: slow, medium, snap, kinetic.
- dialogue_friendly must be true/false.
- The director's name MUST appear in `display:` and `Inspired by:` only.
- The director's name MUST NOT appear in `Cinematography anchor`, `Shot anchor`,
  or any Action vocabulary item — those go to the model.
- Shot anchor must be ≥40 chars + model-agnostic (no Veo/Sora-specific syntax).
- Action vocabulary should have 8-12 items.
- NO emoji.

Run `skills-styles validate video <ID>` after editing.
-->
