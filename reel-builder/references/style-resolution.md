# Style resolution — video

How `--style auto / <library-id>` is resolved into the shot anchor.

---

## Decision flow

```
if --style <library-id>:
    style = load_style(<id>, "video")
    shot anchor = style.anchor("Shot anchor (per-shot prompt fragment)")
    music suggestion = style.section("Suggested music style")  # used by music auto-pick

elif --style auto:
    candidates = library.find_by_tags(<tags derived from topic/script>, "video")
    pick top 3, log alternatives, use top 1
    same anchor extraction

if --style-mod "<override>":
    shot anchor = shot anchor + " " + override
```

---

## `--style auto` algorithm

### Step 1 — Tags from topic + script tone

The script's emotional anchor + content type maps to tag preferences:

- **Calm / educational / B2B explainer**: tags `[medium-pacing, dialogue-friendly, restrained]`
- **Energetic / promo / hook-driven**: tags `[kinetic, snap-cuts, bold]`
- **Atmospheric / mood / brand**: tags `[slow, monumental, immersive]`
- **Comedic / fast / playful**: tags `[snap, comedic, rhythmic]`
- **Cinematic / narrative / dramatic**: tags `[slow-burn, dramatic, anamorphic]`

### Step 2 — Pacing constraint

If the topic implies short snappy content (lists, jokes, hooks), prefer `pacing: snap` or `pacing: kinetic` styles:
- `edgar-wright-snap-cuts`
- `chazelle-musical-glow` (kinetic)
- `inarritu-long-take-handheld` (kinetic but immersive)

If the topic is mood / narrative / atmospheric, prefer `pacing: slow` or `medium`:
- `tarkovsky-slow-meditative`
- `villeneuve-monumental`
- `refn-neon-static`
- `david-lynch-dream-static`

### Step 3 — Dialogue constraint

If the script has spoken dialogue lines on camera, the style MUST have `dialogue_friendly: true`. Drop candidates that don't.

Dialogue-friendly styles in the library:
- `chazelle-musical-glow`
- `edgar-wright-snap-cuts`
- `fincher-cold-lowkey`
- `inarritu-long-take-handheld`
- `nolan-imax-handheld`
- `soderbergh-natural-light`

Non-dialogue-friendly (use only for silent / atmospheric reels):
- `david-lynch-dream-static`
- `refn-neon-static`
- `tarkovsky-slow-meditative`
- `villeneuve-monumental`
- `wes-anderson-symmetric` (works for short stylized dialogue but pacing is restrained)
- `wong-kar-wai-neon-dream`

### Step 4 — Log alternatives

Print to stderr:
```
Style: edgar-wright-snap-cuts (auto). Alternatives: chazelle-musical-glow, inarritu-long-take-handheld.
Override with --style <id>.
```

---

## Shot anchor application

Each shot's prompt is built as:

```
<shot anchor (from style library, ~100-150 words, model-agnostic visual grammar)>

<screenplay action description for THIS shot (30-60 words)>

Composition: <framing from screenplay, derived from style's action vocabulary>.
Duration: <N> seconds.
Aspect: <9:16 vertical | 1:1 | 16:9>.

<if dialogue> Spoken: "<exact line>" (subject lips synced).
```

The anchor appears verbatim for all N shots. The action description differs per shot.

---

## Director-name hygiene

The library STORES the director's name in:
- `display:` frontmatter (UI / user-facing)
- `Inspired by:` body line (user-facing — explains the lineage)

The library NEVER puts the director's name in:
- `Shot anchor (per-shot prompt fragment)` — this goes to the API
- `Action vocabulary` items — also for prompt building
- `Cinematography anchor` — also model-facing

This means: when the carousel/reel skill loads a style and reads `style.anchor("Shot anchor (...)")`, the returned text has cinematography vocabulary ONLY. The director's name never reaches the API.

This is by design: most video providers refuse or scrub artist-mimicry prompts. The library captures the directorial GRAMMAR (lens, lighting, motion, palette, pacing) so the provider can build it without knowing whose work it's based on.

---

## Combining `--style-mod` with library anchors

`--style-mod "<override>"` is appended to the shot anchor as a final sentence. Use for:

- Color: `"but warmer with amber and rust tones instead of neutral"`
- Lighting: `"with stronger key/fill ratio, harder shadows"`
- Mood: `"but more intimate, single-character focus throughout"`
- Camera: `"but locked tripod throughout — no handheld"`

Avoid:
- Contradicting core grammar ("Wes Anderson symmetric but messy handheld" — fights)
- Adding a completely different style ("Wes Anderson symmetric but make it neon cyberpunk" — pick a different `--style <id>`)

---

## Style consistency across shots

The video provider doesn't have explicit "match shot 1 style" controls. Consistency comes from:

1. **Same shot anchor** — appended to every shot's prompt. Major factor.
2. **Same provider** — Veo's style fingerprint differs from Sora's. Lock per-reel.
3. **Color palette in anchor** — repeats palette words in each prompt to reinforce.
4. **Identity carry-over** — if a character appears in multiple shots:
   - Reference the same DETAILED description in each (height, hair, clothing, age, ethnicity).
   - Models that support image-ref between shots (Kling 3.0 Elements): pass shot 1's last-frame as ref to shot 2.
   - Don't rely on names — "Maria" in shot 1 vs shot 2 produces different people. Use the visual description repeatedly.

5. **Setting carry-over** — same location descriptor: "modern minimal Brooklyn loft, large window, oak floor, natural light through gauzy curtains". Repeat verbatim.

---

## "Suggested music style" handoff

Each video style file has a `**Suggested music style**:` field that points to a music library id (e.g. "ambient-drone" or "cinematic-electronic").

When `--music-style auto`:
1. Read the video style's suggested music id.
2. Verify the music style exists in `common/style-library/music/`.
3. Load and use.

When `--music-style <explicit>`: user override wins.

---

## What gets saved to `style-used.md`

```markdown
# Style used: <video-style-id> + <music-style-id>

## Video

**Library file**: <path>
**Shot anchor** (applied to all shots):
> <full anchor text>

**Modifier**: <--style-mod text, if any>
**Alternatives considered (if auto)**: <list>

## Music

**Library file**: <path>
**Music prompt assembled**:
> <full Suno Style box / Lyria prompt / etc>

## Provider routing

- Video: <slug>
- Music: <slug>
```

Reproducibility: future runs can copy this file's anchors into `--script-file` mode for byte-identical reproduction.
