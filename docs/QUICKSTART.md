# Quickstart — your first 5 minutes

Get from zero to a working install + your first run, with no surprises.

---

## 1. Install (30 seconds)

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

What this does:

- Copies 22 skills into `~/.claude/skills/`
- Copies shared references + the style library (50 visual / directorial / music presets)
- Auto-creates `~/.claude/skills/.runners-venv` with Python deps (for the optional `--execute` layer)
- Offers to install ffmpeg via brew / apt (needed only for the `reel-builder` skill)

Restart Claude Code. The skills auto-discover via their frontmatter — no settings file edits.

Other install methods (npm / Homebrew / Docker / local checkout / pinned version): [`INSTALL.md`](INSTALL.md).

---

## 2. Verify the install (10 seconds)

```bash
bash install.sh --check
```

Prints local-vs-remote version. If you just installed, it should say "up to date".

To list what's installed:

```bash
ls ~/.claude/skills/
```

You should see 22 skill folders + `common/`.

---

## 3. Your first prose edit (30 seconds, no API keys)

In Claude Code, paste an LLM-shaped draft and say:

> Run /writer on this. — `<your text>`

The skill returns a cleaned version with antinyeyroslop applied (28 categories of LLM tells removed), Russian-typography fixes, structural-synthesis fixes, and tone neutralization.

No keys, no setup. This is the floor of the toolkit.

---

## 4. Your first AI image (2 minutes, requires OPENAI_API_KEY or other)

### Without an API key (prompt-only)

> Give me an image-prompt for: hero shot of a calm Brooklyn loft at golden hour, kinfolk magazine aesthetic, 4:5 portrait.

You get a paste-ready prompt optimized for the model of choice. Paste into Midjourney / Flux / Imagen / wherever.

### With an API key (full execution)

```
/skills-keys add OPENAI_API_KEY
  value for OPENAI_API_KEY (not echoed): _   # paste, silent input

/skills-keys verify OPENAI_API_KEY
  ✓ OPENAI_API_KEY  valid  models endpoint OK
```

Then in Claude Code:

> Generate an image with image-prompt: a calm Brooklyn loft at golden hour. Use gpt-image-2. Execute it.

The skill writes the prompt, calls OpenAI, saves a PNG to `./generated/image/<timestamp>-gpt-image-2.png`, and prints the path.

Cost: ~$0.05 per image.

---

## 5. Your first end-to-end workflow (5 minutes, ~$0.50)

Compose research → carousel from one topic.

```
/research-brief "AI productivity tools for solo founders in 2026" --depth standard
```

Wall time ~2-4 min. Output: `./generated/research/ai-productivity-tools-solo-founders-20260521.md` with TL;DR + key facts (cited) + suggested angles.

```
/carousel-builder --research ./generated/research/ai-productivity-tools-solo-founders-20260521.md --platform linkedin --slides 8 --style auto --execute
```

Wall time ~1 min. Output: 8 PNG slides + `captions.md` + manifest in `./generated/carousel/<slug>/`. The 8 slides share a single visual style picked from the bundled library.

Cost: ~$0.48 (Flux 2 Pro × 8). Under the default $1.50 carousel budget → no confirmation prompt.

Full walkthrough including the reel: [walkthroughs/research-to-carousel-reel.md](walkthroughs/research-to-carousel-reel.md).

---

## 6. What to do next

Pick by what you need:

- **Prose editing** — [`USER-GUIDE` § prose section](USER-GUIDE.md#prose-editing) covers 13 prose skills (writer, viral-text, prose-edit, essay-write, tone-shifter, cold-email, microcopy, release-notes, rfc-writer, landing-copy, pelevin-digression, style-check, translation-sync, canon-check)
- **AI media generation** — [`USER-GUIDE` § media section](USER-GUIDE.md#ai-media-generation) for image / video / music prompts + the `--execute` layer
- **Orchestrators** — [`research-to-carousel-reel`](walkthroughs/research-to-carousel-reel.md) end-to-end recipe
- **Style library** — browse [`common/style-library/carousel/_index.md`](../common/style-library/carousel/_index.md), [`video/_index.md`](../common/style-library/video/_index.md), [`music/_index.md`](../common/style-library/music/_index.md)
- **All walkthroughs** — [`walkthroughs/README.md`](walkthroughs/README.md) (categorized index)
- **Compose multiple skills** — [`COMPOSING.md`](COMPOSING.md)

If something breaks: [`FAQ`](FAQ.md) · [`TROUBLESHOOTING`](TROUBLESHOOTING.md).

---

## Setup cheat sheet (copy-paste)

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

# Add the API keys you have (interactive silent prompts)
# (run inside Claude Code, one per provider you'll use)
/skills-keys add OPENAI_API_KEY
/skills-keys add GEMINI_API_KEY
/skills-keys add BFL_API_KEY
/skills-keys add ANTHROPIC_API_KEY
# … etc.

# Confirm they work
/skills-keys verify

# Optional: enable paid gate flags
/skills-keys enable SUNO_API_ENABLED
/skills-keys enable LYRIA_API_ENABLED

# Optional: configure S3-compatible storage mirror
/skills-keys add S3_BUCKET your-bucket
/skills-keys add S3_ACCESS_KEY ...
/skills-keys add S3_SECRET_KEY ...

# Update later
/skills-update             # in-Claude
bash install.sh --update   # CLI
```

That's all the setup. From here, just say what you want in plain language — Claude picks the right skill.
