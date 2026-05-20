# Beat structure + CHARACTER FIRST law

The single most important file in this skill. The default failure mode of AI video models is **freezing one pose** for the entire clip. Every rule here exists to prevent that.

---

## The fundamental law: CHARACTER FIRST, CAMERA SECOND

Never start a motion prompt with a camera move when characters are in action. The model animates **what you describe first**. If you lead with camera, it renders camera and freezes the character into a "beautiful postcard with frozen mannequins" (figma's exact phrase).

❌ WRONG ORDER (produces frozen character):
> "Slow dolly push-in on Sarah. She extends her arm angrily, leaning forward."

✅ RIGHT ORDER:
> "Beat 1 (0-2s): Sarah delivers 3-4 sharp jabbing motions with her finger toward the man across the table, arm cycling between full extension and partial pullback, never settling. Her jaw clenches between bursts.
> Beat 2 (2-5s): the man flinches at the first jab, shifts weight backward, jaw tightens.
> Beat 3 (5-8s): Sarah holds the final jab in place, finger inches from his face, shoulders heaving with breath.
> Camera: slow dolly push-in throughout, subtle handheld vibration, focus locked on Sarah's hand."

The camera direction is the LAST sentence. The model gets character to animate first; camera is the supporting frame around it.

---

## Beat structure (mandatory for action shots)

Every motion prompt that involves action uses Beat 1 / Beat 2 / Beat 3 timing. This forces the model to interpolate between distinct moments instead of picking one pose.

Roughly:
- **Beat 1** = first 30% of duration
- **Beat 2** = middle 40%
- **Beat 3** = final 30%

For an 8-second clip: 0-2.5s / 2.5-5.5s / 5.5-8s.
For a 4-second clip: 0-1.3s / 1.3-2.6s / 2.6-4s.

### Template

```
Beat 1 (0-Xs): [initiating action — what character starts doing]
Beat 2 (X-Ys): [escalation — what shifts, what character 2 does, what reaction]
Beat 3 (Y-end): [resolution — final pose, sustained tension, or release]
Camera: [one sentence — supporting camera direction]
```

### Per-beat checklist

Beat 1:
- WHO moves first
- WHAT body parts move
- HOW (fast / slow / shaky / fluid)
- For 2+ characters: ONLY one character initiates here

Beat 2:
- Escalation: louder, faster, more body parts engaged, OR
- Reaction: the second character's physical response
- Camera: usually no change yet

Beat 3:
- Resolution: final pose OR sustained held tension OR release
- Camera: typically the move completes here
- For 2+ characters: both finish their arcs

---

## Repeated actions vs single gestures

This is the OTHER killer. A single-instance gesture description ("he extends his arm") tells the model to render ONE pose and freeze it. The fix: force continuous motion via repeated language.

### Pattern map

| ❌ Single gesture (frozen) | ✅ Repeated/continuous (animated) |
|---|---|
| "He extends his arm" | "He delivers 3-4 sharp jabbing motions, arm cycling between full extension and partial pullback, never returning to rest" |
| "She shouts at him" | "Her mouth opens wide as she shouts, continuous jaw and lip movement, head shaking with each word burst, throat visibly tense, sharp exhale bursts between phrases" |
| "They look at each other" | "Beat 1: subject A glances at subject B, holds for half a second; Beat 2: subject B's eyes drop, then slowly return; Beat 3: subject A breaks eye contact, looks down" |
| "He picks up the cup" | "Beat 1: hand reaches forward, fingers wrap the handle; Beat 2: cup lifts in continuous motion, slight tilt; Beat 3: cup arrives at lips, sip motion" |
| "She types on the keyboard" | "Continuous typing — fingers cycling across keys at fast pace, wrist remaining stable, occasional pauses for thought" |
| "He smiles" | "Smile builds gradually — corners of mouth lift first, then eyes crinkle, expression settles after 1 second and holds" |

### The "never fully" pattern

The strongest anti-freeze language is "never fully [returns / settles / stops]":

- "Arm never fully returns to rest"
- "Smile never fully settles into a fixed expression"
- "Gaze never fully locks — continuous slight micro-adjustment"
- "Body never fully stops moving — slight sway, breathing, weight shifts"

This forces the model to keep interpolating.

---

## Two-character (or more) shots

"They look at each other" = synchronised statues.

### The rule: describe EACH character separately within EACH beat

```
Beat 1 (0-Xs):
- Character A: {their action}
- Character B: {their action OR holds, awaiting}

Beat 2 (X-Ys):
- Character A: {escalation}
- Character B: {reaction, physical response}

Beat 3 (Y-end):
- Character A: {final pose}
- Character B: {their final pose or reaction}
```

### Reaction-character body checklist

When character B is reacting (not initiating), still describe their body:

- Physical reaction: "flinches at first contact", "shifts weight back", "freezes mid-step"
- Posture under pressure: "jaw tightens", "shoulders stiffen", "hands close into fists"
- Face: "controlled expression — irritation, then pressure, blinks slowly, holds eye contact"
- Breathing: "controlled breathing, one noticeable swallow"

---

## Body detail for emotion shots

For any shot involving yelling, arguing, fighting, crying, running, dancing, or strong emotion — describe these layers explicitly or the model freezes:

### Aggressor / active character

- **Mouth / jaw / lips**: "mouth opens wide, continuous jaw movement while shouting, lips shaping words"
- **Neck / throat**: "neck muscles tense, throat visibly working, jaw set hard"
- **Torso / posture**: "torso lunging forward, chest heaving, shoulders tight and raised"
- **Arms / hands**: "repeated jabbing motions" / "finger stabbing the air in short thrusts"
- **Secondary motion**: "jacket catching the momentum of each jab", "hair bouncing with head movement"
- **Breathing**: "chest heaving, sharp exhale bursts, body taut with adrenaline"

### Reactor / passive character

- **Physical reaction**: "flinches at first contact, shifts weight back, half-step retreat"
- **Posture under pressure**: "jaw tightens, shoulders stiffen, small restrained movement as if holding back"
- **Face**: "controlled expression: irritation → pressure → blinks → holds eye contact"
- **Breathing**: "controlled breathing, one noticeable swallow"

### Gentle / emotional (no fighting but still performance)

- **Face**: "expression shifts gradually: [start emotion] → [end emotion], never frozen mid-expression"
- **Eyes**: "blinks naturally, gaze direction shifts slightly twice during the shot"
- **Breath**: "slow, visible chest rise and fall, 2-3 full breaths during the shot"
- **Secondary**: "hair / fabric moves slightly with breath or ambient air"

---

## Physical realism — objects, equipment, sports

Identify every specific physical object in the still / scene. Then describe motion that's **physically consistent** with how that object actually behaves.

### Rule

If the image shows a kiteboard / skateboard / motorcycle / surfboard / rowing shell / etc. — name the exact equipment and describe motion physics that match:
- Edge angles
- Body position under load
- Equipment behavior under force
- Realistic constraints of the activity

❌ Generic: "rides the wave gracefully"
✅ Specific: "kiteboard edge cuts hard against the water, body position low and rotated 30° toward the kite, kite-lines visibly taut and vibrating with tension, water spray fans behind the board at 45°"

❌ Generic: "performs the activity"
✅ Specific: "knees bent into the suspension on the BMX, front wheel lifting through the takeoff arc, body weight rolling over the bars at the apex"

### Props stay

Any prop visible in the scene must remain physically present and behave consistently:
- "Laptop screen glow continuous" (doesn't blink off)
- "Cup stays in hand" (doesn't teleport)
- "Papers on desk shift slightly with airflow" (don't disappear)
- "Phone screen lights face from below throughout"

---

## Forbidden phrases (cause frozen-pose output)

Replace ALL of these on sight:

| ❌ Banned | ✅ Replace with |
|---|---|
| "Occasionally glance" | "Beat 1: glance left; Beat 2: gaze drops; Beat 3: glance back, holds" |
| "Subtle smile" | "Smile builds gradually — corners of mouth lift first, then eyes crinkle, settles after 1s" |
| "Subtle movement" | Name the specific body-part movement with timing |
| "Adds life" | Empty calorie — delete and describe what literally moves |
| "Extends an arm" | "Delivers 3-4 sharp arm extensions with wrist snapping forward, partial pullback between, never fully returns to rest" |
| "Makes a gesture" | Describe the specific gesture with body-part precision and repetition |
| "Dynamic atmosphere" | Empty calorie — delete |
| "Performs the activity" | Name the activity's specific motion physics |
| "Moves gracefully" | Replace with: speed (slow / fast), body-part involvement, equipment interaction |
| "Reacts" | Name the specific physical reaction (flinch, shift, freeze, retreat) |
| "Looks at" | Name the eye movement: "gaze locks on", "eyes track from X to Y", "blinks then focuses" |

Any of these phrases makes the model freeze. The replacements force specific, timed, repeated motion.

---

## motionPrompt structure (final template)

```
Beat 1 (0-Xs): [WHO does WHAT — body-part specific, repeated, with timing]
Beat 2 (X-Ys): [escalation / reaction — both characters if 2+]
Beat 3 (Y-end): [resolution / final pose / held tension]

Environment: [one specific environmental motion — papers flutter, dust drifts, screen glow flickers]

Camera: [one sentence — locked / subtle handheld / slow dolly push-in / etc.]
```

Total: 5-8 sentences. Dense, specific, performance-first, physically grounded.

---

## Story-grounded motion

The action must feel like it belongs to THIS specific story beat, not generic movement. A confrontation must carry the stakes of this specific relationship; a celebration must feel like THIS person's win.

Embed the emotional meaning in the motion description, not just the mechanics:

❌ Mechanical: "She delivers 3 sharp arm jabs"
✅ Story-grounded: "She delivers 3 sharp arm jabs, voice cracking on the second one — the words finally landing after months of bottling them up"

The emotional context goes in the description WITH the motion, not separately. It's not a screenplay direction; it's a single integrated description.

---

## Quick-reference checklist

Before submitting any motion prompt, verify:

- [ ] First sentence is CHARACTER action, not camera move (if action shot)
- [ ] Beat 1 / Beat 2 / Beat 3 structure present with explicit time markers
- [ ] Each character (if 2+) described separately within each beat
- [ ] Repeated / continuous language used (not single-instance gestures)
- [ ] Body parts named explicitly (not "moves" or "reacts")
- [ ] Forbidden phrases stripped (occasionally glance, subtle smile, adds life, etc.)
- [ ] Physical realism for any sport / equipment / vehicle
- [ ] Props stay (any object in still still present + behaving consistently)
- [ ] One camera direction at the end
- [ ] No transition language ("cut to", "reveal", "fade to") inside one shot
- [ ] 5-8 sentences total
