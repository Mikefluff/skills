# reel-builder calibration

3 example runs.

---

## Example 1 — 3-shot vertical reel from a topic, with Suno music

### User request

> reel-builder --topic "The fastest way to write your first newsletter" --shots 3 --shot-duration 5 --style chazelle-musical-glow --music-style cinematic-orchestral --captions on --execute

### What happens

1. **Script draft** via viral-text: hook → "Sit down. Pick a topic that pisses you off. Write 300 words." → payoff "Hit send tonight."

2. **3-shot screenplay**:
   - Shot 1 (hook, 0-5s): close-up hands on laptop, golden-hour window light, magic-hour glow on keys. Caption: "Day 1 newsletter."
   - Shot 2 (beat, 5-10s): wider — person at desk typing fast, dynamic Steadicam follow, sustained eye contact with imagined reader. Caption: "Topic. Anger. 300 words."
   - Shot 3 (payoff, 10-15s): laptop closes, finger hits "Send" button, smile. Caption: "Hit send tonight."

3. **Video style**: chazelle-musical-glow (kinetic + romantic) — anchor includes "saturated primaries, Steadicam choreography, magic-hour key light, motivated practical lights, smooth dolly tracking parallel to subject".

4. **Music style**: cinematic-orchestral — Lyria 3 Pro field-driven prompt assembled (string-heavy, building, ~90 BPM, 17s duration with 2s safety margin).

5. **Provider auto-pick**: video → veo-3-1 (kinetic + dialogue-friendly style); music → lyria-3-pro (cinematic-orchestral hint).

6. **Cost estimate**: 3 × 5s × $0.40 = $6.00 (Veo) + $0.10/min × 17s ≈ $0.03 = $6.03 total. Over $4.00 default reel budget → confirmation prompt.

7. **Execute**: 3 video shots in parallel (parallelism 2), then 3rd shot. Music generates concurrently. ~120s wall time.

8. **ffmpeg stitch**: concat 3 shots → mix Lyria track → burn 3 captions → final.mp4.

9. **Output**:
   ```
   ./generated/reel/fastest-way-first-newsletter/
     final.mp4              (15s, 1080×1920, ~3-5 MB)
     shots/
       shot-1.mp4
       shot-2.mp4
       shot-3.mp4
     music.mp3              (17s, ~270 KB)
     script.md
     manifest.json
     style-used.md
   ```

10. stdout:
   ```
   Reel: ./generated/reel/fastest-way-first-newsletter/final.mp4
   Components: ./generated/reel/fastest-way-first-newsletter/{shots/, music.mp3, script.md}
   ```

---

## Example 2 — 1-shot atmospheric reel with Stable Audio

### User request

> reel-builder --topic "Slow Sunday morning, French press coffee" --shots 1 --shot-duration 8 --style tarkovsky-slow-meditative --music-style ambient-drone --captions off --video-provider sora-2 --music-provider stable-audio-2-5 --execute

### What happens

1. **Script draft**: brief mood prompt — single sustained shot, water boiling sound, slow pour.

2. **1-shot screenplay**:
   - Shot 1 (0-8s): wide static of a kitchen window in soft pre-dawn light, French press on the counter, slow zoom-in as water is poured. Steam rises. No dialogue.

3. **Video style**: tarkovsky-slow-meditative — anchor includes "natural light, soft sepia palette, slow durational shot, water as motif, intentional stillness".

4. **Music style**: ambient-drone — Stable Audio prompt: "ambient drone, sustained low strings, no rhythm, 60 BPM, 10 seconds of contemplative space".

5. **Provider**: sora-2 explicitly (10s max — handles 8s), stable-audio-2-5 explicit.

6. **Captions**: off (atmospheric reel — no text).

7. **Cost**: 1 × 8s × $0.10 = $0.80 (Sora) + $0.05 (Stable Audio) = $0.85. Under budget — no confirmation.

8. **Execute**: 1 video + 1 music in parallel. ~100s wall time.

9. **ffmpeg stitch**: no concat (single shot) → mix audio → no captions → final.mp4.

10. **Output**:
   ```
   ./generated/reel/slow-sunday-morning-french-press/
     final.mp4              (8s)
     shots/
       shot-1.mp4
     music.mp3              (10s)
     script.md
     manifest.json
     style-used.md
   ```

---

## Example 3 — 4-shot product reel from research brief, with Kling 3.0 + Lyria

### User request

> reel-builder --research ./generated/research/vertical-ai-veterinary-20260521.md --shots 4 --shot-duration 5 --style fincher-cold-lowkey --music-style cinematic-orchestral --aspect vertical --video-provider kling-3-0 --music-provider lyria-3-pro --execute --yes

### What happens

1. **Read research brief**: TL;DR + key facts on vertical AI for veterinary clinics. Picks angle "the bottleneck is front-desk, not clinical AI" from the brief's Suggested angles.

2. **4-shot screenplay**:
   - Shot 1 (hook, 0-5s): close-up on vet's hands typing into outdated software, fluorescent overhead light. Cold tone. Caption: "Vet tech is broken."
   - Shot 2 (setup, 5-10s): wider — vet looks up at a long line of pet owners in waiting room. Caption: "AI's solving the wrong problem."
   - Shot 3 (turn, 10-15s): cut to clean modern interface mock-up on monitor — the right problem (intake, insurance). Caption: "The bottleneck is front-desk."
   - Shot 4 (payoff, 15-20s): hand reaches for the new system, click. Smile. Caption: "Save 20 minutes per visit."

3. **Video style**: fincher-cold-lowkey — anchor includes "anamorphic 2.39:1, deep teal palette, micro push-in, surveillance grade lighting, motivated single-source key light".

4. **Music style**: cinematic-orchestral — Lyria field-driven prompt with brass swell building under 22s duration.

5. **Provider**: kling-3-0 (identity carry-over via Elements — vet character consistent across all 4 shots) + lyria-3-pro.

6. **Cost**: 4 × 5s × $0.10 = $2.00 (Kling) + $0.10/min × 22s ≈ $0.04 = $2.04 total. Under $4.00 budget, but `--yes` was passed anyway.

7. **Execute**: 4 video shots in parallel (parallelism 2 → 2 batches of 2), then Lyria music. ~150s wall time.

8. **ffmpeg stitch**: concat 4 shots → mix Lyria → burn 4 captions → final.mp4 (20s).

9. **Output**:
   ```
   ./generated/reel/vertical-ai-veterinary-clinics/
     final.mp4              (20s vertical, ~5-7 MB)
     shots/
       shot-1.mp4 ... shot-4.mp4
     music.mp3              (22s)
     script.md
     manifest.json
     style-used.md
   ```

---

## Anti-pattern (don't do this)

### Mixing video providers across shots

Don't try `--video-provider veo-3-1 --video-provider-shot-2 sora-2` (and similar) — even if implemented, the visual fingerprints differ enough that the reel feels stitched-from-different-films. v1 enforces one provider per reel; future versions won't change this default.

### >5 shots in 15-20s

Past 5 shots, each gets <4s — too short for the model to do anything meaningful. If you need a longer narrative, do 5 shots × 6s = 30s OR rethink the script for fewer, denser shots.

### Generated dialogue in every shot

If 3 shots all have spoken lines, the reel becomes talking-head bouncing with no visual breathing room. Reserve dialogue for 1 shot max (often the payoff).

### --captions on with `tarkovsky-slow-meditative` or `david-lynch-dream-static`

These styles work BECAUSE of stillness + ambiguity. Burned-in text breaks the spell. For these styles default to `--captions off`.
