# Film mode — voiced Seedance films without broken seams

A voiced film is a reel whose picture is cut against a spoken take: an ElevenLabs voice, a character from one reference photo who lip-syncs to it, and a dramatic arc that lands its events on the words. It runs in phases, and the order is the point — the prompts are written against a voice that already exists.

```
1. voice     python3 -m common.runners.cli.reel_voice --script-file vo.txt --voice-id <id> \
                 --output-dir ./generated/reel/<slug> [--max-seconds 30] [--lead 0.8] [--tail 1.5]
             → voice/master.wav, voice/seg-NN.wav, timing.json

2. direction ONE Agent with common/video-prompt-library/film-system-prompt.md
             user message built from timing.json + brief + character ref
             → film beats + storyboard frames + one Seedance prompt per shot (cut plan on the film clock,
               head handles, lip_sync shots get their stretch of the take) → plan.json

2b. board    python3 -m common.runners.cli.reel_board --plan-file ./generated/reel/<slug>/plan.json
             → one Nano Banana Pro keyframe per shot, judged by a Gemini critic, re-rolled below 8/10
             → board/contact.jpg; keyframes become the shot's ordered references (approve before video)

2c. previs   python3 -m common.runners.cli.reel_previs --plan-file ./generated/reel/<slug>/plan.json
             → previs/<label>.mp4 clay clips (Blender, headless, free) → each shot's @Video1

3. sound     python3 -m common.runners.cli.reel_sound --plan-file ./generated/reel/<slug>/plan.json
             → music cues + effects + beds generated, placed, mastered → soundtrack.wav
             (listen before paying for the picture)

4. render    python3 -m common.runners.cli.reel --plan-file ./generated/reel/<slug>/plan.json
             → shots/seg-NN.mp4 → trimmed, joined → hits snapped to the frames → soundtrack muxed → final.mp4
```

Run the render with `--cost-only` first. BytePlus bills tokens (seconds × width × height × 24 fps / 1024, $10.70 per million): a 30 s 9:16 film is about $6.93 at 720p and $15.60 at 1080p. fal resells per second and costs about twice as much at 720p.

---

## Why the last film broke, and what each piece fixes

| Symptom | Cause | Fix |
|---|---|---|
| Picture jumps at a seam | Segments generated independently. Each one re-invents camera, light and pose | ≤30 s: **no seams**, because Seedance 2.5 renders 4-30 s in one generation. Longer: each segment opens on the exact frame the previous one was cut on (`continue_from_previous`), or the seam is a designed cut such as a whiteout or an occlusion |
| Voice breaks or doubles at a seam | Each segment carried its own copy of the speech, cut at a fixed length, sometimes mid-word | Cuts go only in pauses (`voice_timing.plan_cuts`). The viewer hears one continuous master take, laid over after the join. Seedance's own audio is dropped |
| Events miss their lines | "When @Audio1 mentions SMOKE" asks the model to understand speech semantically. It doesn't, reliably | Events pinned to timecodes taken from ElevenLabs word alignment: `[7.4–9.1s]` |
| Mush, flat drama | About 20 staged events in 30 s, each line illustrated literally, every beat at the same volume | Event budget of one per 4 s, one controlling image, an intensity curve, and a quiet turn |
| Lip-sync drifts | Speech scheduled over wides, backs, macro and fast moves | Speech windows are close or medium shots with the face visible. Spectacle goes in the pauses |
| Subtitles or invented lines | Dialogue quoted in the prompt | Never quote the voiceover. Point at time instead |
| Seedance's own sound is mush | It re-voices the reference, invents a score, and puts effects where the model guessed | Its audio is discarded. The soundtrack is designed: music cues, effects and beds placed on the film clock, then mastered (next section) |

---

## Choosing the route

| Film length | Model | Seams |
|---|---|---|
| ≤ 30 s (incl. lead + tail) | `seedance-2-5` (BytePlus, `ARK_API_KEY`), `openrouter-seedance-2-5` (`OPENROUTER_API_KEY`, same token price, for when BytePlus will not take the card) or `fal-seedance-2-5` (`FAL_KEY`) | none: one generation |
| 30-60 s | `seedance-2-5`, `--max-seconds 30` | 1-2, in pauses, chained |
| any, on 2.0 | `seedance-2-0`, `--max-seconds 15` | every ≤15 s |

`continuity`:
- `reference` (default, both routes): the seam frame becomes the last `@Image`.
- `first_frame` (BytePlus only): conditions the first frame exactly. Stronger, but forces `ratio: adaptive`, and the vendor may refuse to combine it with reference images. Try it when a reference-chained seam still jumps.

Real human faces: Seedance blocks clearly identifiable real faces unless the account has passed its real-human verification. A stylised or generated character photo avoids the gate.

---

## The voice phase

- **Script and direction (Eleven v4, the default).** The model reads the text as written, so an undirected script comes back flat. Put a free-text delivery tag in brackets before each phrase that changes register: `[calm, low voice, a little tired, ironic]`, `[dry, sarcastic, half-smiling]`, `[warmer, sincere, quiet longing]`. Write tags in English and the text in its own language. `[pause]` and `[long pause]` hold silence, `...` gives a short beat, and CAPITALS stress one word. SSML breaks are ignored.
- **Voice.** A tag only works if the voice can already carry that register. Choose the voice by its description: a casual, sarcastic, tired voice for irony; a broadcaster for announcements. Then direct it.
- **Takes.** Tags are guidance, not guarantees, and takes differ. `--takes 3 --stability 0.3` writes `voice/take-1..3.mp3`. Listen and rerun with `--pick K`: existing takes are reused, so re-cutting the film against another take is free. Punctuation is still structure. A full stop gives a cut-able pause; if `reel_voice` reports "no cut plan", add one.
- **Fitting the length.** Directed reads run slower. `--tempo 1.04` retimes the picked take without changing pitch (0.96-1.06 is inaudible as an effect), and the word timings scale with it. Use it to land a ≤30 s film in one generation instead of trimming lines.
- **`--lead`** is picture before the first word, used for an opening image. **`--tail`** is picture after the last word, used for the resolution held in silence. Both count toward the 30 s.
- **No alignment** in the TTS response (the schema allows null) falls back to `/v1/forced-alignment` automatically. `--voice-file` takes a take you already have and aligns it the same way.

---

## The sound

Seedance's audio never reaches the viewer. The soundtrack is written by the same chain call as the prompts (`sound` in plan.json) and built in two layers.

**Sources** are generated once:
- music cues from Eleven Music, each with a composition plan whose section boundaries sit on the hits;
- effects and looped ambience beds from ElevenLabs sound generation (`eleven-sfx`).

**Placements** put a slice of a source on the film clock, with gain, treatment (`distant`, `muffled`, `thin`), ducking under the voice, and `snap`.

Musical drama is an edit, not a generation. Eleven Music sections are at least 3 s long, so a silence shorter than that can only be cut:
- a cue killed on the turn is a placement that ends there;
- a dip under an ironic line is one cue split into three placements with continuous offsets;
- the same cue placed again with `distant` is the world going on without him.

**Snap.** Seedance stages "the flash at 5.4 s" somewhere near 5.4 s. Every effect with `snap: true` is moved to the strongest brightness jump in the rendered picture within ±0.5 s. What actually got placed is written beside the mix as `soundtrack.placements.json`.

**Master.** The mix goes through EBU R128 loudness normalisation to −14 LUFS, −1 dBTP, the level Reels, Shorts and TikTok normalise to.

**Re-mixing.** Edit the placements in plan.json and rerun `reel_sound --picture <out>/picture.mp4`. Sources are reused from `sound/`, so a re-mix costs nothing.

## The camera is a previs, not a sentence

Shots generated from a keyframe plus a written camera move came back as cautious push-ins, with the camera hardly moving. Over the same stretch of the film, a 5 s clay previs (FPV over the decks, low down the line through the truss gates, crowd reveal, crane to top-down) given as `@Video1` came back as that move, frame for frame. Frame-to-frame motion measured 8–12, against 0.2–5 before. It cost $0.61 at 480p. Seedance 2.5's guide names clay renders as the input for "camera movement, pacing, shot-size transitions, subject trajectory, and blocking". So the chain designs the camera as data, and `reel_previs` renders it.

## One generation per shot

The keyframed one-generation film came out as a slideshow. Frame-to-frame motion was near zero for whole shots: Seedance, given ten keyframes to hold, held them. BytePlus's guide recommends 4–5 assets per generation, not eleven. The default is therefore the practice of studios that get directed results:
- **One generation per shot.** Each shot opens on its approved keyframe (image to video) and runs 4–6 s.
- **The cut is ours.** The film is cut frame-exact on the film clock, with `trim_start` skipping the model settling in.
- **Lip sync.** A `lip_sync` shot cannot take a first frame next to an audio reference, so its keyframe goes in as Image 2 and the runner slices its stretch of the master as Audio 1.
- **Price.** Seedance bills by the second, so ten 4-second shots cost about what one 40-second take would.

`reel_conform` without `--picture` reads each lip-sync shot from the manifest and leaves voice-over phrases where the master has them.

## Conforming the voice to the picture

Seedance does not play the audio reference back. It re-performs the script through a mouth on screen. When every phrase sits on a visible face, the re-performance lands within 0.1–0.3 s of the take ([openstory test](https://github.com/openstory-so/openstory/issues/1551)). When a phrase falls over a shot with no readable face, the model has no voice-over to fall back on, so it moves the phrase to the next face. On the first trial film, which put lines over a wide from behind, an overhead and a walk-away, this moved lines 1.5–3 s late and dropped words. The cure is the prompt: under rule 6 of the film system prompt, every word goes on a face. Conforming is the salvage for a picture that is already paid for. Run it after generation and before the final mix:

```
python3 -m common.runners.cli.reel_conform --plan-file <out>/plan.json --picture <out>/shots/<generated>.mp4
python3 -m common.runners.cli.reel --plan-file <out>/plan.json --resume --yes
```

The first command transcribes the generated audio with ElevenLabs speech-to-text, which costs a fraction of a cent. It then moves each breath group of the master to where the mouth says it, stretching by at most ±15%. A line the model moved more than 2 s away has landed in another shot, so it stays where the script put it. Sounds placed on words move with their words; snapped hits stay on their picture events. On the trial film, the median gap between the voice and the lips dropped from 1.13 s to 0.25 s. That is still visible, because lips read as out of sync beyond about 0.1 s. Conforming is the free fix; exact sync to the master take needs a lip-sync pass over the finished picture.

---

## The dramaturgy rules, in one breath

One controlling image. One event per 4 s at most. Setup, escalation, a quiet turn, consequence at the largest scale, and a resolution held in silence. Hits on word starts, reactions just after phrase ends, the turn in the longest pause. The face owns the speech and the camera owns the silence.

The full rule text is the SYSTEM_PROMPT. This file is the why.

---

## Worked example — the "prepared future" film

The original prompt (≈1,800 words) staged about 20 events in 30 s. Light, visual, smoke, drop, the "very live" beat, a delayed drop, the unexpected decision, three separate failures, an overhead reveal with a six-step material restore, a walk into darkness, a floor that forms, and a final light. It explained its own meaning to the model ("This is NOT another location", "The important point:"). It keyed events to quoted Russian phrases. It asked for one impossible continuous take across a duration that, on 2.0, had to be cut in two at an arbitrary second.

**Dramaturgy pass (illustrative timings; real ones come from timing.json):**

- **Controlling image:** a cue track. It is a physical path of lit floor markers running from the artist into the dark, with every future light, smoke and drop event already standing along it.

| at | function | int. | event (anchor) |
|---|---|---|---|
| 0.0 | setup | 1 | Macro eye, concert in the reflection, pull back to portrait (lead silence) |
| 3.2 | setup | 4 | He presses PLAY; the whole stage ignites on one frame (on *PLAY*) |
| 7.0 | escalation | 4 | One cue run in three hits: light, LED wall, smoke cannons. The camera enters the smoke and the lens goes white (on *свет* / *визуал* / *дым*) |
| 11.0 | escalation | 5 | Out of the white: the same stage as matte white previs. The drop stands ahead on the track and fires as he reaches it (on *дроп*) |
| 14.6 | escalation | 2 | "Very live": orbit stops in front of him, half-smile, music drops to relays (0.3 s after the phrase) |
| 17.4 | **turn** | 1 | He kills the kick and steps off the track. Stillness (longest pause) |
| 18.5 | consequence | 5 | The track's cues fire on, down an empty path. Crane up: the track runs hundreds of metres, and finished materials return along it (on *не слушает*) |
| 24.0 | resolution | 2 | He walks into black; a floor forms under each step (on *а я хочу*) |
| 28.5 | resolution | 1 | "Даже я." He stops and looks to camera. Silence. A far light appears. Cut (tail) |

**Cut from the original, and why:**
- The "delayed drop" beat. It makes the same point as the turn, weaker, 4 s earlier, and the budget has no room for it.
- The three separate failures. They became one consequence event.
- The six-material restore list. It is now one phrase.

The film loses nothing it needs and gains room for the turn to be quiet.

**Seedance 2.5 prompt (one generation, no seams):**

```
Vertical 9:16 cinematic film, 30 seconds, one continuous scene.
@Image1 is the man's identity: face, hairstyle, build, clothing. He looks exactly like @Image1 in every shot.
@Audio1 is his voice. He is the only speaker; his lips, breath and pauses follow @Audio1 exactly.
Electronic-concert realism: deep blacks, volumetric haze, real moving heads and LED walls, natural skin, film grain.
A line of lit floor markers runs from his feet into the dark; along it wait rigged lights, smoke cannons and a towering drop rig.
[0–3.2s] Extreme macro of his eye, stage lights in the reflection; slow pull back to a tight portrait.
[3.2–7.0s] Medium shot, he speaks, then presses one physical play button; every light, screen and motor starts on the same frame; slow orbit left begins.
[7.0–11.0s] Medium close-up, he speaks; a light cue, the LED wall, then the smoke cannons fire in three exact hits along the line; camera pushes into the smoke until the frame is white.
[11.0–14.6s] Out of the white: the same stage, same positions, every surface matte white like an architectural model; he speaks; ahead on the line the drop rig fires as he reaches it.
[14.6–17.4s] Orbit stops in front of him; a small half-smile; the white machinery runs on behind him.
[17.4–18.5s] He lifts one hand off the controls and steps sideways off the marker line. Stillness.
[18.5–24.0s] He speaks; cues keep firing down the line where he no longer stands; camera cranes overhead: the line runs hundreds of metres into darkness, turning back into a finished glowing concert.
[24.0–28.5s] Camera drops behind him to shoulder height; he walks into black; floor forms under each step.
[28.5–30s] Three-quarter close-up, he speaks, stops, looks at the lens; the concert runs far behind; after his last word one unknown light appears far ahead. Hard cut to black.
Sound: his voice from @Audio1, electronic pulse, relays, servos, smoke bursts; no music, no other voices.
Avoid: subtitles, on-screen text, logos, holographic interfaces, glitch effects, extra speaking people.
```

That is about 330 words against about 1,800, with eight timeline lines instead of twenty events. Speech falls only on medium and close shots. The two big moves, the push into the smoke and the crane, happen around the speech, not over it.

If the take runs past 30 s, `reel_voice` cuts in pauses and the segments chain. The cut it chooses is the longest pause in range, which in this film is the turn at 17.4. A seam there would split the quietest beat, so add a sentence break near 11.0 and rerun the voice phase. The cut then falls at the whiteout. Set `continue_from_previous: false` on segment 2 and let the white be the cut: a seam that is already a transition cannot jump.
