# Mix modes — when to pick which

3 modes. Each implies a different ffmpeg filter chain and a different listener experience.

---

## `replace` (default)

**What it does**: drops the video's original audio track entirely; uses the music file as the sole audio.

**When to pick**:
- Silent screen recordings → add music for engagement
- Source has bad audio (wind, background noise, room echo) and you want to replace
- Music videos where the visual is supplementary

**Listener experience**: just music. No dialogue, no ambient sound from the source.

**ffmpeg filter chain**: `-map 0:v -map 1:a` (use video from input 0, audio from input 1).

**Quality**: video is `-c:v copy` (no re-encode). Audio is AAC 192kbps.

---

## `overlay`

**What it does**: mixes the music ON TOP of the original audio. Both are audible at their full requested volumes.

**When to pick**:
- B-roll footage with natural sound (street, nature, restaurant) + music bed
- Documentary feel — preserve ambient atmosphere while adding score
- When original audio is part of the story but you want to lift the energy

**Listener experience**: ambient/dialogue mixed with music. Music tends to dominate if `--volume` is high; lower it for "background music bed" feel.

**ffmpeg filter chain**: `[1:a]volume,afade[music];[0:a][music]amix=inputs=2:duration=first`.

**Quality**: both tracks re-encoded to AAC 192kbps.

**Tuning**:
- For background music bed: `--volume 0.3` to `0.5` (music sits behind speech)
- For equal mix: `--volume 0.7` to `0.8` (default 0.8 is balanced)
- For music-forward: `--volume 1.0` (music slightly louder than source)

---

## `duck`

**What it does**: like overlay, but with a sidechain compressor. When the original audio has signal (speech, loud moments), the music auto-attenuates by `--duck-amount` (default 60% attenuation). When the source is quiet, the music returns to full volume.

**When to pick**:
- Podcast-style video with voiceover/dialogue + music bed
- Explainer videos where the speech is the primary signal
- Anywhere you want music to "breathe" around speech

**Listener experience**: music plays normally during quiet moments and pauses; music dims (but doesn't disappear) under speech. Professional broadcast feel.

**ffmpeg filter chain**: complex chain with `sidechaincompress` filter — the original audio drives the compression of the music.

**Quality**: both tracks re-encoded; the sidechain compression introduces minor processing.

**Tuning**:
- `--duck-amount 0.4` — aggressive ducking (music nearly mutes under speech)
- `--duck-amount 0.6` (default) — balanced
- `--duck-amount 0.8` — subtle ducking (music only slightly lowers)

**Caveat**: duck mode REQUIRES a non-silent source audio. If your source video is silent (no speech), duck mode behaves identically to overlay. For silent source → use replace.

---

## Decision tree

```
Source video has NO useful audio (silent / bad audio)
  → replace

Source video has VOICEOVER or DIALOGUE you want to preserve
  → duck

Source video has AMBIENT SOUND you want to keep alongside music
  → overlay
```

---

## Per-mode example use cases

### replace

- Phone screen recording of an app demo → add upbeat music
- B-roll cityscape with wind noise → replace with cinematic music
- Slideshow of photos with no narration → music only

### overlay

- Walking-through-Brooklyn b-roll with street ambient → music + street sounds
- Cooking video with sizzle / chop sounds → keep ambient + music bed
- Travel vlog where ambient is part of the vibe → both audible

### duck

- Podcast video (host talking to camera) → music bed under speech
- YouTube tutorial with screen recording + voiceover → music ducks under voice
- Interview with two speakers + intro/outro music → music ducks when anyone talks

---

## Volume + fade interactions

Default `--volume 0.8 --fade-out 0.5`:
- Music at 80% of its source loudness (most music files are mastered loud; 80% prevents clip)
- Half-second fade-out at the end (avoids hard cut)

Common tweaks:
- Cinematic intro: `--fade-in 2.0 --fade-out 2.0 --volume 0.7`
- Punchy social: `--fade-in 0 --fade-out 0.3 --volume 1.0`
- Background bed (overlay/duck): `--volume 0.4 --fade-in 0 --fade-out 1.0`

---

## What this skill doesn't do

- **Mid-clip volume automation** (music swells at minute 0:30) — use DaVinci / Premiere
- **Multi-track mixing** (music + SFX + voiceover separately) — use a DAW (Audacity, Reaper, Logic)
- **EQ / compression / mastering** — use a DAW
- **Music sync to beat markers** — manual NLE work

For these: this skill produces the BASELINE mix; refine in a NLE / DAW for polished work.
