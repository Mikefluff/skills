# Camera vocabulary — exact terms

Use these exact terms in motion prompts. Models are trained on the named cinematic verbs — `slow dolly push-in` parses cleanly, `camera moves forward` does not.

Never paraphrase. Never use generic descriptions when a named move exists.

---

## DOLLY — physically moves camera through space

| Term | What it does | Use for |
|---|---|---|
| `slow dolly push-in` | Camera moves toward subject slowly | Building intimacy, drawing focus, intensifying emotion |
| `slow dolly pull-back` | Camera retreats from subject | Revealing context, emotional release, "letting go" beats |
| `fast dolly in` | Quick aggressive move toward subject | Hook shots, sudden intensity |
| `vertigo effect` (dolly zoom) | Camera retreats while lens zooms in (background expands) | Shock, dissociation, awe |

---

## PAN / TILT — pivot from a fixed point

| Term | What it does | Use for |
|---|---|---|
| `slow pan left` | Horizontal pivot left | Following slow motion, revealing context |
| `slow pan right` | Horizontal pivot right | Same, mirrored |
| `tilt up` | Vertical pivot upward | Awe, reveal of something tall, looking up |
| `tilt down` | Vertical pivot downward | Resignation, shame, looking at ground |
| `whip pan` | Violent lateral blur transition (within one shot) | Specialty — energy spike, between two subjects |

---

## TRACKING — follows subject laterally

| Term | What it does | Use for |
|---|---|---|
| `lateral tracking shot` | Camera moves sideways with subject | Walking, running shots |
| `leading shot` | Camera retreats as subject walks forward | Subject "approaches" the audience |
| `following shot` | Camera chases from behind | Pursuit, exploration |
| `side tracking alongside subject` | Travels parallel to motion | Conversation while walking, action sequences |

---

## CRANE / PEDESTAL — vertical

| Term | What it does | Use for |
|---|---|---|
| `crane up` | Epic lift high into the air | Endings, reveals of scale |
| `crane down` | Descend slowly to subject | Establishing, "arriving" |
| `pedestal up` | Vertical lift, no tilt | Subtle increase of perspective |
| `pedestal down` | Vertical descent, no tilt | Subtle drop |

---

## ORBIT — circular around subject

| Term | What it does | Use for |
|---|---|---|
| `orbit 180` | Half-circle arc around subject | Revealing two sides |
| `slow cinematic arc` | Wide curve revealing side profile | Drama, character moments |
| `fast 360 orbit` | Full high-energy circle | Action, energy spike, climax |

---

## AERIAL / DRONE

| Term | What it does | Use for |
|---|---|---|
| `drone fly-over` | High altitude forward flight | Establishing wide, journeys |
| `epic drone reveal` | Rise then tilt down to scene | Big openings, scale reveals |
| `large-scale drone orbit` | Wide circular at altitude | Hero shots, location intros |
| `top-down god's-eye` | Pointing straight down, slow twist | Geometric, dramatic, "fate" beats |
| `FPV drone dive` | Aggressive dive into scene | Adrenaline, action peaks |

---

## FLY-THROUGH

| Term | What it does | Use for |
|---|---|---|
| `camera flies through window` | Enters a new space through a portal | Spatial transitions |
| `camera flies through gap` | Through narrow opening | Scene transitions, mystery |
| `camera flies through tunnel` | Through enclosure | Punch into next environment |

---

## HANDHELD

| Term | What it does | Use for |
|---|---|---|
| `handheld shoulder-cam drift` | Realistic sway | Documentary feel, intimacy |
| `documentary shaky motion` | Gritty realism | Action, conflict, urgency |
| `subtle handheld vibration` | Slight tremor | Tension hold shots |

---

## SPECIALTY

| Term | What it does | Use for |
|---|---|---|
| `Dutch angle roll` | Tilts on Z-axis | Unease, dissonance |
| `worm's-eye tracking` | Ground-level, looking up | Making subject feel massive |
| `bullet time` | Frozen moment + slow orbit | Iconic peak moments |
| `hyperlapse` | Rapid forward + time-accelerated | Travel, change-over-time |
| `barrel roll` | 360° forward spin | Disorienting, surreal |
| `snap zoom` / `crash zoom` | Rapid punch-in to face | Hook shots, reveal |
| `rack focus` | Shift focus near→far or far→near | Reveals, transitions of attention |
| `POV walk` | First-person bobbing motion | Immersion, POV shots |
| `speed ramp` | Gradual slow-down or speed-up | Drama, action accents |
| `freeze frame` | Hold one moment | Specialty endings |

---

## Translation table — generic → exact

When you find yourself wanting to write a generic camera direction, use this exact-term map:

| ❌ Generic (causes confusion) | ✅ Exact (parses cleanly) |
|---|---|
| "Camera moves forward" | `slow dolly push-in` (or `fast dolly in`) |
| "Camera goes back" | `slow dolly pull-back` |
| "Camera pans" | `slow pan left` or `slow pan right` (always specify direction) |
| "Camera tilts" | `tilt up` or `tilt down` |
| "Camera circles subject" | `orbit 180` or `slow cinematic arc` |
| "Camera follows" | `following shot` (from behind) or `leading shot` (retreats ahead) |
| "Camera goes up" | `crane up` or `pedestal up` (crane is bigger) |
| "Aerial / sky shot" | `drone fly-over`, `epic drone reveal`, `top-down god's-eye` |
| "Camera zooms in" | `slow dolly push-in` (physical) or `snap zoom` / `crash zoom` (lens) |
| "Camera moves around" | Pick: `orbit 180`, `slow cinematic arc`, `fast 360 orbit` |
| "Slight camera movement" | `subtle handheld vibration` or `slow drift` |
| "Static shot" | `locked camera` (but always specify SOMETHING — even a locked camera should have "subtle handheld vibration" for liveness) |
| "Reveal" | Pick a physical move: `crane up to reveal`, `slow dolly pull-back reveals`, `rack focus to reveal` |

---

## Combining moves

Sometimes a shot needs TWO movements layered. The model handles ~2 simultaneous moves cleanly; 3+ becomes incoherent.

✅ Two layered moves (works):
- "Slow dolly push-in WITH slight pedestal up"
- "Lateral tracking shot LEFT WITH subtle Dutch angle roll"
- "Crane up TURNING into orbit 180"

❌ Three+ layered moves (incoherent):
- "Slow dolly push-in with orbit and tilt up and rack focus"

If you need three things to happen, split into two shots.

---

## Camera + emotion matrix (quick picker)

| Emotional beat | Default camera moves |
|---|---|
| Hook (first shot, peak tension) | `crash zoom to face` / `fast dolly in` / `whip pan ending on close-up` |
| Tension / climax | `slow dolly push-in` / `handheld shoulder-cam drift` / `subtle handheld vibration` |
| Breathing / resolution | `slow dolly pull-back` / `slow cinematic arc` / `subtle drift` |
| Setup / establishing | `crane down to subject` / `slow pan revealing scene` / `epic drone reveal` |
| Action / chase | `following shot` / `side tracking` / `FPV drone dive` |
| POV / first-person | `POV walk` / `subject's-eye view tracking` |
| Reveal | `slow dolly pull-back reveals` / `rack focus reveals` / `crane up to reveal` |
| Surreal / unease | `Dutch angle roll` / `vertigo effect` / `barrel roll` |
| Documentary / candid | `handheld shoulder-cam drift` / `documentary shaky motion` |
| Time-pass / change | `hyperlapse` / `speed ramp` |

---

## Anti-patterns

❌ Camera move as first sentence on action shots — violates CHARACTER FIRST law:
> "Slow dolly push-in. She delivers a sharp gesture."
→ Model freezes the gesture; renders the camera move.
✅ Action first, camera last:
> "Beat 1 (0-2s): she delivers 3-4 sharp jabbing motions with her finger... Camera: locked with subtle handheld vibration."

❌ Three+ simultaneous moves:
> "Push-in with orbit with tilt up with rack focus"
→ Model picks one arbitrarily.

❌ Transition language inside one shot:
> "Camera pans to reveal, then cuts to the door"
→ "Cut" is an edit term; the model can't render it within one shot. Use one move only.

❌ Vague camera direction:
> "Cinematic camera work, dynamic shot"
→ Empty calorie. Specify the actual move.

✅ The right form:
> "Beat 1 (0-2s): {character action}. Beat 2 (2-5s): {escalation}. Beat 3 (5-8s): {resolution}. Camera: slow dolly push-in throughout, locked focus on subject's eyes."
