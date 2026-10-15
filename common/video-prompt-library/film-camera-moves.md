# Camera moves for film previs — a library, in previs coordinates

> Read by the film chain (`film-system-prompt.md`, PART 3b) when it writes `previs`. A shot names one move from this list and sets its keys from the numbers here. The numbers are synthesis from standard practice and the geometry of the source shots, not quotes, unless a source sits next to them. Sources: concert and music-video practice (Boiler Room, *Stop Making Sense*, *Climax*, *The Revenant*, *Athena*, Fred again.. *rubberband*, ODESZA/McCartney FPV, *This Is America*), gathered 2026-10-15.

Coordinates: metres, stage floor z = 0, his eye line z ≈ 1.7, deck top z ≈ 0.95, he stands at (0, −0.15) facing +y toward the crowd. Lens in mm full-frame; vertical 9:16 means the horizontal field is narrow (35 mm sees 32° across), so lateral pans feel twice as fast — prefer booms, tilts, dives and dollies.

| id | move | why | keys (pos → look, lens, timing) | shake | cut in / out |
|---|---|---|---|---|---|
| boiler_reverse | behind the booth, his shoulder dark in the bottom third, crowd and beams facing the lens | puts the viewer in the booth; the crowd is the subject | camera 1.2–1.8 m behind him at z 1.9, look over his head to the crowd; 24–28 mm; creep forward 0.05 m/s | 0.15° @0.7 Hz (0.004) | in on a cue firing; out when a beam flares the lens |
| foh_compression | front-of-house long lens, crowd heads soft at the bottom, him waist-up, LED wall on top | voyeuristic, monumental, indifferent | camera 30–40 m out at z 2.5 (FOH riser), look at his chest; 200–300 mm; locked or drift-zoom 1–2 %/s | 0.002 | the observer shot; ideal at the turn |
| deck_slider | lateral slide across the decks 10 cm above the controls | tactility; proves it is live; the ECU end of the scale | z 1.05, 0.3 m from his hands, slide 0.03–0.08 m/s parallel to the deck edge, 2–4 s; 60–100 mm | 0 | in 2 frames after a finger moves; out on the cue |
| fisheye_low_push | ultra-wide, very close and low, looking up; he balloons, truss curves over | swagger, dominance — once per film, ≤1.5 s | camera 0.4–0.7 m from his face at z 0.9, look up 20–30°; 10–14 mm; push 0.1–0.2 m/s | 0.01 | in on a drop, out hard on the next downbeat |
| snorricam | camera fixed to his chest, face fixed, world swings | dislocation; his world moves, he doesn't | camera keyed to his hero pos + (0, +0.55 forward, z 1.8), look at his face; 18–24 mm; turn him 30–60°/s | 0.006 | in when he lifts his hands; out on a wide where he is small |
| steadicam_lead | wide and close, leading or following at walking pace | presence; the lens shares his air | 0.6–1.2 m from him at eye height ±0.2, moving 1.2–1.4 m/s with him; 14–21 mm | 0.004 + step bob | long, 4–8 s; the walk-off |
| booth_orbit | half orbit around the booth at constant radius | scale; the background spins behind a stable face | orbit radius 2.5–3.5 m, height 1.6, 25–40°/s (180° in 4.5–7 s), ease in/out 0.5 s; 28–35 mm; plan a beam/LED flash behind him at 120–150° of travel | 0.004 | out as a truss leg passes the lens (hidden wipe) |
| crane_reveal | rise from intimacy to epic, holding him in the bottom third | lifts the stakes | start z 1.8, 2 m from him; boom to z 8–10 while pulling back 0.5–0.75 m/s, look tilting down; 24 mm; 4–6 s, ease-out 1.5 s | 0.002 | in from a close insert; out at the top or hold as "the show without him" |
| gods_eye | dead overhead, slow yaw | detachment, fate; beams and floor become pattern | z 15–25 straight above the booth (look straight down, a key 0.1 m off-axis), slow yaw 2–4°/s via roll; 24–35 mm; stage axis along the frame height | 0 | 3–5 s hold |
| snap_rise | still for 2–4 s, then a sudden rise to overhead in 1–1.5 s | the rupture is the gesture — on the build to the drop | locked at z 1.3, 35 mm; then over 1.0–1.5 s forward 1 m and up 8 m, look turning straight down; ease "ease" with the jump near the end | 0 | lands overhead and holds |
| fpv_dive | one flying path from high behind the crowd, through a truss gap, flaring out near him | kinetic; the venue as a single space | start z 18–22 behind the crowd, dive at 30–40° at 8–12 m/s through a 0.5–1 m truss gap, flare to 1–2 m/s 4 m from him; 14–16 mm; bank roll 15–30° into turns, back to 0 within 0.4 s; nose down 10–20° in the dive | 0.002 + roll | 4–8 s; cut on the truss pass (2–4 dark frames) |
| fpv_skim | low and fast along the stage line from behind him toward the crowd, cues firing as it reaches them, then up | the prepared future, flown through | start over his shoulder z 1.8; drop to z 0.5 over the line at 6–8 m/s; pull up into top-down at the stage edge; 16–18 mm | 0.002 | as in the proven test shot |
| demme_lockoff | locked medium at eye line, long hold | trust; stillness as confidence | 4–6 m from him at z 1.7; 50–75 mm; zero motion 4–8 s; he can leave frame and the frame stays | 0 | at the turn: hold the empty booth 1–2 s while cues fire |
| hard_silhouette | one hard source behind him, big shadow, rim only | graphic, iconic | camera 5 m, eye line, 35 mm; a fired light directly behind him 160–180° from camera | 0 | 3–5 s |
| slowmo_pullback | from 0.5 m off his face to 6 m, everything inside slowed | the emotional peak in suspension | start 0.5 m, 35 mm, pull back to 6 m over the shot at 0.15–0.3 m/s; say "slow motion" in the prompt | 0.002 | one shot, 5–8 s |
| walk_away | static or creeping, he walks away into a light ahead of him | an ending that leaves | camera z 1.5, 50 mm, creep forward 0.2 m/s; he walks away at 1.3 m/s; the exit light (a fired block) beyond him in frame | 0.002 | the final 4–6 s |
| discovery_track | one continuous Steadicam move that discovers events on bar lines | choreography of camera on choreography | 24–32 mm, 1–2.5 m from him; each reveal pans 30–60°, starting 6 frames before the beat | 0.004 | whole phrase |
| low_follow | low, wide, tilted up: him and the full rig in one frame | scale and person together | camera z 1.0 (0.7 above the deck if on stage), 2 m behind him, tilted up 10°, following at 1.3 m/s; 17–21 mm | 0.006 | 3–6 s |
| dolly_zoom | dolly back 2 m while zooming 35→70 mm (or in with 50→24) over 2–3 s | vertigo; the world grows behind him | lens keys change while the camera moves the opposite way; his head size constant | 0 | exactly on the downbeat he lifts his hands |
| whip | 600–1200°/s for 4–6 frames, blurred; vertical whip (tilt) reads best in 9:16 | joins two shots in one motion | last 3 frames of shot A and first 3 of shot B, same direction; "snap" ease on the keys a few frames apart | — | on beat 1 of a phrase |
| crash_zoom | 24→85 mm in 4–8 frames, 1-frame overshoot | lands on a detail with the kick | lens keys 0.2–0.3 s apart, ease "linear" | — | once or twice per film |
| speed_ramp | 100→20 % over 6 frames, hold 1–2 s, then 20→300 % into the cut | the beam freezes in the air | say it in the prompt; in previs, slow the keys accordingly | — | ramp down as the cue fires |
| fg_wipe | a truss leg, a head, the operator's shoulder crosses the lens at 0.3–1 m, filling >80 % for 2–4 frames | hides cuts, gives parallax | an "extra" block 0.3–1 m from the lens path; camera trucks 0.5–1 m/s past it | — | cut inside the wipe |
| worms_eye | 10 cm above the stage deck, 1.5–2 m in front of the booth, tilted up 25–35° | the hero shot; beams fan over him | camera z 0.1, 16–20 mm; beams behind him fire toward the lens; deck edge soft in the bottom 15 % | 0.002 | 2–4 s |
| gear_rack | lens just behind screens, faders or the desk, rack focus to him | depth; the machine in front of the man | 50–85 mm, foreground 0.2 m, subject 3 m; rack over 12–18 frames, landing on the beat | 0 | 2–3 s |
| desk_ots | behind the lighting operator, his shoulder and fader bank soft, stage compressed far away | the cue is fired here | camera 0.8 m behind the operator's shoulder, 85–135 mm; console in the bottom 30 % | 0.003 | match-cut his finger on GO → the beam hitting |
| empty_arena | rehearsal arena from the seats, lights running for nobody | the show continues without him | 24 mm, z 8–15 at the back of the floor or seating; hold or creep 0.02 m/s | 0 | 3–5 s |
| overhead_decks | straight down on the decks and his hands | the livestream angle; circles for match cuts | z 2.9 (2 m above the deck) looking straight down, 24 mm | 0.002 | match jog wheel → crowd ring |

Shake values are previs `shake` (noise strength in metres on the rig); rotation shake is implied by it at these distances.

## Vertical 9:16 composition

- The top 12 % and bottom 20 % carry platform UI: no faces or hands there. Eyes on the line 33–38 % from the top; 6–10 % headroom in mediums.
- Stack depth vertically: foreground at the bottom (decks, crowd heads, console, 0.3–1 m, soft), him in the middle band, the rig and beams in the top 40 %.
- Truss legs and speaker hangs as rails at ⅓ and ⅔ of the width; beams fanning up the long axis.
- Move vertically: booms, tilts, dives, crane rises. Lateral pans ≤15°/s or ≥600°/s (a whip) — nothing in between.
- In wides he is small: 8–12 % of the frame height, in the lower third.

## Editing grammar (scale by 120 / BPM; 120 BPM: a beat is 0.5 s, a bar 2 s)

- Shot length follows the phrase: intro shots 2 bars, the build 1 bar → half → a beat (≤4 in a row), the peak one long move of 2–4 bars, the turn one held shot of 3–4 bars. Cut on the downbeat or 2 frames before it.
- Never cut between neighbouring sizes: jump at least two (ECU ↔ extreme wide, MCU ↔ wide). One scale-jump climax per film (deck insert → god's eye).
- Cut in the middle of a move, entering the next shot 3–4 frames into its move, in the same direction and speed. Keep the stage up-frame in crowd angles; cross the 180° line only on a whip or an overhead.
- Match cuts: circles (jog wheel → crowd ring), finger on GO → beam hitting, a white strobe frame → a white LED wall.
- Escalate with four levers together — shorter shots, wider lenses, more shake, faster camera. The turn inverts all four at once: one long lens, locked, no shake, a long hold, and the frame left empty 1–2 s after he exits.
- At most 8 one- or two-frame strobe flashes in 30 s, in the peak only; they can hide 3–4 hard cuts.
