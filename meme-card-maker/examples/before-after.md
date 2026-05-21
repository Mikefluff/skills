# meme-card-maker — calibration

3 example sessions.

---

## Example 1 — Drake template, developer joke

### User says

> Сделай мем формата Drake — наверху "Using Jira to track bugs", снизу "Crying in the shower".

### Plan

```
meme-card-maker
  --top "Using Jira to track bugs"
  --bottom "Crying in the shower"
  --template drake
  --variants 3
  --execute
```

### What happens

1. Skill picks `gpt-image-2` (default; best meme typography + composition).
2. Template `drake` cues 2-panel vertical stack with Drake-like character + rejection/approval gestures.
3. Captions auto-uppercase for English: "USING JIRA TO TRACK BUGS" / "CRYING IN THE SHOWER".
4. Impact-style typography with thick black stroke.
5. 3 variants for selection.
6. Outputs:
   - `./generated/meme/using-jira-shower/meme-v1.png` through `meme-v3.png`
   - `manifest.json`, `prompts.md`
7. Estimated cost ~$0.12.

### Next steps

- Pick best variant.
- For pixel-exact Drake: take to Imgflip with the captions — better template fidelity.

---

## Example 2 — Custom photo meme

### User says

> У меня есть фото моего кота (`./mittens.jpg`). Сделай мем — top: "ME WAITING FOR THE BUILD TO PASS", bottom: "STILL FAILING".

### Plan

```
meme-card-maker
  --top "Me waiting for the build to pass"
  --bottom "Still failing"
  --base-photo ./mittens.jpg
  --template custom
  --model nano-banana-pro
  --variants 3
  --execute
```

### What happens

1. `--base-photo` triggers `nano-banana-pro` selection (best identity preserve).
2. `--template custom` lets model use the cat photo as centerpiece.
3. Captions overlaid in Impact-style at top/bottom edges.
4. Variants vary in stroke thickness + slight composition tweaks.
5. Outputs in `./generated/meme/build-failing-cat/`.

### Notes

- Identity preserve = your cat stays recognizable across variants.
- Estimated cost ~$0.21 (3 variants × $0.07 NBP).

---

## Example 3 — Expanding-brain progression

### User says

> Expanding brain meme: "Use formatter / Use linter / Use type checker / Delete the code".

### Plan

```
meme-card-maker
  --top "Use formatter / Use linter / Use type checker / Delete the code"
  --template expanding-brain
  --aspect portrait
  --variants 3
  --execute
```

### What happens

1. `expanding-brain` template cues 4-panel vertical stack with progressively-glowing brain.
2. The 4 captions in `--top` (separated by ` / `) distribute across panels.
3. `--aspect portrait` (1080×1350) — fits 4 panels vertically.
4. Impact-style typography on each panel.
5. Outputs in `./generated/meme/dev-galaxybrain/`.

### Anti-pattern (don't do this)

❌ Pass 4 captions as `--top` AND `--bottom` (would be 8 captions, breaks template).

✓ Encode all 4 in `--top` separated by ` / ` for `expanding-brain`.

---

## Anti-patterns (across examples)

### Caption too long

❌ `--top "Me when the CI passes on the first try after I rewrote the entire authentication system from scratch and the code looks beautiful"`

Result: text wraps to 4+ lines, illegible.

✓ Shorten ruthlessly. Memes are PUNCH lines. "ME WHEN CI PASSES FIRST TRY" (5 words) >> "Me when the CI passes on the first try..." (20 words).

### Editorial / polished aesthetic

❌ Expecting Pinterest-style polish.

Memes are CULTURE. The aesthetic is intentionally rough — Impact font, JPEG artifacts, slightly-degraded look. If you want polished editorial: use `quote-card-maker`.

### Cultural sensitivity not considered

❌ Generating memes about sensitive topics (politics, tragedy, marginalized groups) without thought.

The skill doesn't filter. Your judgment. When in doubt: don't ship.

### Trying to copy a copyrighted template exactly

❌ Asking for "exact replica of [specific commercial meme template]".

✓ Memes are cultural commons — approximating common formats (drake, distracted-boyfriend) is fine. Pixel-replicating commercial templates / brand mascots: don't.

### Expecting Russian Impact

❌ `--lang ru` + expecting Impact font Cyrillic rendering.

Impact has weak Cyrillic. Skill switches to "bold condensed Cyrillic sans" automatically. Results vary — Cyrillic memes don't have the same canonical typography as English.
