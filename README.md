# skills

[![ci](https://github.com/Mikefluff/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Mikefluff/skills/actions/workflows/ci.yml)
[![version](https://img.shields.io/github/v/release/Mikefluff/skills?label=version)](https://github.com/Mikefluff/skills/releases/latest)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**42 skills for [Claude Code](https://docs.claude.com/en/docs/claude-code/skills) that make content — and refuse to let it read like a machine made it.**

Prose editing that strips the tells. Prompt engineering for 40+ image, video and
music models, with optional one-command execution against the real APIs. And
orchestrators that carry a job the whole way: research question → carousel →
published post; raw price list → a proposal styled from the client's own website.

Russian-first, English throughout. Plain markdown, MIT, no required dependencies.

## What it actually does

The same cold email, before and after `cold-email` → `writer`:

<table>
<tr><th align="left" width="50%">Before — 175 words</th><th align="left" width="50%">After — 98 words</th></tr>
<tr valign="top"><td>

> **Subject: Quick question**
>
> Hi Patricia,
>
> I hope this email finds you well! My name is David Kim and I'm the co-founder
> and CEO of Nimbus, a B2B SaaS startup that's been disrupting the
> developer-tools space for the past 22 months.
>
> I've been a longtime admirer of your work at Magnet Ventures, and I was
> incredibly impressed by your recent investment in DevForge. Given the
> synergies I see between our work and your portfolio, I wanted to reach out
> personally to introduce myself.
>
> We've been growing rapidly — we now have a number of enterprise customers and
> significant ARR. […]

</td><td>

> **Subject: $2.1M ARR in dev tools — fit for Magnet?**
>
> Hi Patricia,
>
> Saw the DevForge round — congrats on leading. We're in an adjacent wedge:
> pre-merge code-review automation for engineering teams of 20-200. $2.1M ARR
> over 22 months, 12 enterprise customers including Stripe, Datadog, and
> Cloudflare.
>
> Raising A in Q3. Worth 20 min next week to see if Magnet would be a fit?
>
> Happy to send the deck cold either way.
>
> Best,
> David Kim
> Co-founder, Nimbus · nimbus.dev

</td></tr>
</table>

Every cut is attributable to a rule, not to taste — "I hope this email finds you
well" to `banned-patterns.md §Ceremony openers`, the 24-word bio to
`structure.md §Block 1`. The [full pair with every delta](skills/cold-email/examples/before-after.md)
is in the repo, along with three more.

There is also an offline linter, so the same rules can gate a commit with no API
call and no model in the loop:

```console
$ python3 ~/.claude/skills/writer/scripts/lint.py draft.md
writer-lint: borderline (3 hits)
gate passed: no hard bans.

Hits:
  L1:42  [caution] GPT_FILLER   "it's important to note"
  L2:30  [caution] GPT_FILLER   "Let's dive into"
  L6:1   [caution] AI_BRIDGE    'Moreover'
```

Exit codes are hook-shaped, so `style-check` can run it on staged files and stop
the commit — [pre-commit walkthrough](docs/walkthroughs/pre-commit-hook.md).

## How it fits together

One skill does the prose work — [`writer`](skills/writer/) — and eleven others
route through it rather than restating its rules. `viral-text` knows about hooks
and platforms; it does not know about em-dashes, because `writer` does. The same
shape holds for media: nine skills build on [`image-prompt`](skills/image-prompt/).

That is the whole architecture. 42 skills: 1 base, 21 wrappers, 3 linters,
14 orchestrators, 3 meta.

---

## Install

```bash
# Curl — 5 seconds, no deps
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

Other methods (npm, Homebrew, Docker, local checkout, pinned version, custom prefix): [`docs/INSTALL.md`](docs/INSTALL.md).

Skills appear after Claude Code session restart. Discovery is automatic via the `name:` and `description:` fields in each skill's frontmatter — no `~/.claude/settings.json` edits required.

**API keys** (for `--execute` mode — entirely optional): manage via `/skills-keys add OPENAI_API_KEY ...` inside Claude Code, or copy `.env.example` to `~/.skills.env`. See [Managing keys](#managing-api-keys) below.

---

## Documentation

The full doc hub: [`docs/`](docs/README.md). Most-used pages:

| Page | What |
|---|---|
| [QUICKSTART](docs/QUICKSTART.md) | 5-minute first run — install → first prose edit → first AI image → first end-to-end |
| [USER-GUIDE](docs/USER-GUIDE.md) | The scenarios index — pick what you want to do |
| [walkthroughs/](docs/walkthroughs/README.md) | 20 step-by-step recipes, categorized |
| [CONTRIBUTING](CONTRIBUTING.md) · [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) | Adding a skill, reporting a bug, house rules |
| [SKILL-INDEX](docs/SKILL-INDEX.md) | Every skill by layer / domain / language |
| [COMPOSING](docs/COMPOSING.md) | Named workflows for chaining skills + data flow + anti-patterns |
| [INSTALL](docs/INSTALL.md) | Install methods (curl, npm, brew, Docker, local, pinned) |
| [FAQ](docs/FAQ.md) · [TROUBLESHOOTING](docs/TROUBLESHOOTING.md) | When something looks off |

The bundled style libraries used by the orchestrators: [carousel](common/style-library/carousel/_index.md) · [video](common/style-library/video/_index.md) · [music](common/style-library/music/_index.md) · [visual-prompt styles (extensible, 23 entries)](common/visual-prompt-library/styles/_index.md).

The shared LLM prompt chains behind the visual skills: [image chain](common/visual-prompt-library/system-prompt.md) (carousel / cover / quote / meme / banner / logo — typographic template + style fields + orientation lock) and [video chain](common/video-prompt-library/system-prompt.md) (reel shots / carousel animation — overlay-heavy i2v discipline, `lock_first_last` + `negative_prompt` text-stability). Saved brand profiles for proposal-maker: [proposal-maker/brands/](skills/proposal-maker/brands/_index.md).

---

## What you can do

### Write & edit prose

| Scenario | Skill(s) | Walkthrough |
|---|---|---|
| Clean an LLM-shaped draft | [`writer`](skills/writer/) | [USER-GUIDE](docs/USER-GUIDE.md#i-just-want-to-clean-a-draft) |
| Viral social post (RU + EN) | [`viral-text`](skills/viral-text/) → writer | [RU](docs/walkthroughs/viral-post.md) · [EN](docs/walkthroughs/en-viral-post.md) |
| Edit a fiction chapter (Pelevin/Manson voice) | [`prose-edit`](skills/prose-edit/) → writer | [fiction-chapter](docs/walkthroughs/fiction-chapter.md) |
| Draft a long-form essay (RU) | [`essay-write`](skills/essay-write/) → writer | [non-fiction](docs/walkthroughs/non-fiction.md) |
| Verify a trilingual translation (RU/EN/PT-BR) | [`translation-sync`](skills/translation-sync/) | [translation-parity](docs/walkthroughs/translation-parity.md) |
| Audit a chapter against your story bible | [`canon-check`](skills/canon-check/) | [canon-check-audit](docs/walkthroughs/canon-check-audit.md) |
| Insert a Pelevin-style digression | [`pelevin-digression`](skills/pelevin-digression/) | [digression-insertion](docs/walkthroughs/digression-insertion.md) |
| Rewrite in a different register (formal↔casual…) | [`tone-shifter`](skills/tone-shifter/) → writer | [tone-shift](docs/walkthroughs/tone-shift.md) |
| Write a cold outreach email | [`cold-email`](skills/cold-email/) → writer | [cold-email-pitch](docs/walkthroughs/cold-email-pitch.md) |
| Write UX microcopy (errors / empty states / tooltips) | [`microcopy`](skills/microcopy/) → writer | [microcopy-error-states](docs/walkthroughs/microcopy-error-states.md) |
| Write release notes / changelog | [`release-notes`](skills/release-notes/) → writer | [release-notes-saas](docs/walkthroughs/release-notes-saas.md) |
| Write an RFC / ADR / design doc | [`rfc-writer`](skills/rfc-writer/) → writer | [rfc-architecture](docs/walkthroughs/rfc-architecture.md) |
| Write landing / SEO / ad copy | [`landing-copy`](skills/landing-copy/) → writer | [landing-launch](docs/walkthroughs/landing-launch.md) |

### Generate AI media (prompt-first, execute optional)

| Scenario | Skill(s) | Walkthrough |
|---|---|---|
| Generate an image prompt for 14+ models (Midjourney v7, Flux 2, Imagen 4 Ultra, Nano Banana Pro, gpt-image-2, Ideogram 3, Seedream 4.5, …) | [`image-prompt`](skills/image-prompt/) | [image-prompt-cover](docs/walkthroughs/image-prompt-cover.md) |
| Generate a video prompt for 20+ models (Veo 3.1 + audio, Sora 2, Kling 3.0, Runway Gen-4 / Aleph V2V, Luma Ray 3, Pika, Hailuo, Hunyuan, Wan 2.2, Seedance, …) | [`video-prompt`](skills/video-prompt/) | [video-prompt-reel](docs/walkthroughs/video-prompt-reel.md) |
| Generate a music prompt for 10+ models (Suno v5.5, Udio v4, Lyria 3 Pro, ElevenLabs Music, Stable Audio 2.5, MusicGen, …) | [`music-prompt`](skills/music-prompt/) | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-an-ai-music-prompt) |
| Voiceover / narration via TTS (ElevenLabs multilingual + OpenAI gpt-4o-mini-tts) | [`voiceover-maker`](skills/voiceover-maker/) | [skills/voiceover-maker/examples/before-after.md](skills/voiceover-maker/examples/before-after.md) |
| Burn captions onto an existing video (SRT / VTT / plain text + ffmpeg) | [`subtitle-burner`](skills/subtitle-burner/) | [skills/subtitle-burner/examples/before-after.md](skills/subtitle-burner/examples/before-after.md) |
| Actually run the prompt through the vendor API and save a real PNG / MP4 / MP3 | any of the prompt skills + `--execute` | [execute-end-to-end](docs/walkthroughs/execute-end-to-end.md) |

### Orchestrate end-to-end

| Scenario | Skill(s) | Walkthrough |
|---|---|---|
| Research a topic with cited sources (WebSearch + WebFetch + optional Firecrawl/Exa MCP) | [`research-brief`](skills/research-brief/) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |
| Turn topic / research into an N-slide Instagram / LinkedIn / TikTok carousel (24 visual styles, batch execute) | [`carousel-builder`](skills/carousel-builder/) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |
| Turn topic / research / script into a vertical reel (12 directorial styles + 12 music genres + ffmpeg stitch) | [`reel-builder`](skills/reel-builder/) | [research-to-carousel-reel](docs/walkthroughs/research-to-carousel-reel.md) |
| Make a flyer / event poster / promo graphic (title + date + location + optional photo, multi-aspect) | [`flyer-maker`](skills/flyer-maker/) | [skills/flyer-maker/examples/before-after.md](skills/flyer-maker/examples/before-after.md) |
| Turn a raw offer / price list into a beautiful commercial proposal (КП) styled from a website — real product photos, exact prices, print-to-PDF | [`proposal-maker`](skills/proposal-maker/) | [skills/proposal-maker/examples/before-after.md](skills/proposal-maker/examples/before-after.md) |
| Headshot / profile-pic / avatar variants from a photo (identity-preserve via Nano Banana Pro, multi-aspect) | [`avatar-maker`](skills/avatar-maker/) | [skills/avatar-maker/examples/before-after.md](skills/avatar-maker/examples/before-after.md) |

### Manage the collection

| Scenario | Skill | Walkthrough |
|---|---|---|
| Manage API keys (add / remove / update / verify / enable gate flags) | [`skills-keys`](skills/skills-keys/) | [skills/skills-keys/examples/before-after.md](skills/skills-keys/examples/before-after.md) |
| Manage the style library (add / edit / validate / submit upstream) | [`skills-styles`](skills/skills-styles/) | [skills/skills-styles/examples/before-after.md](skills/skills-styles/examples/before-after.md) |
| Update the collection itself | [`skills-update`](skills/skills-update/) | n/a — invoke directly |
| Auto-lint every git commit | [`style-check`](skills/style-check/) | [pre-commit-hook](docs/walkthroughs/pre-commit-hook.md) |
| Run a read-only quality gate | [`style-check`](skills/style-check/) | [style-check-gate](docs/walkthroughs/style-check-gate.md) |

---

## What's in the box

<!-- BEGIN skills-table (auto-generated; run `make gen-readme`) -->

| Skill | Layer | Languages | Purpose |
| --- | --- | --- | --- |
| [`writer`](skills/writer/) | base | ru/en | Base clean-prose editor — antinyeyroslop (25 catalogued categories + copy-paste artifacts + rhythm metrics), typography, structural synthetics, RU calques. Invoked by all other prose skills. |
| [`viral-text`](skills/viral-text/) | wrapper | ru/en | Write viral social media content — hooks, numbered points, micro-conclusion with NLP question, CTA. 41 viral content rules + platform adaptation. |
| [`prose-edit`](skills/prose-edit/) | wrapper | ru | Fiction rewrite layer — Pelevin/Manson voice vector, 10-item style drift checklist, no meta-refs / anglicisms in narrator voice, long artistic rewrite (no comma-stitching), ToV pattern, 5-trigger structural-synthesis detector, Postirony depth-pass. |
| [`essay-write`](skills/essay-write/) | wrapper | ru | Non-fiction layer — long subordinate sentences (Manson style), source-backed claims, philosophy through humor, biography through scenes, plain-Russian for complex content. |
| [`style-check`](skills/style-check/) | linter | ru/en | Read-only pre-commit lint that stacks writer + prose-edit + essay-write rules. Routes by configurable path patterns (fiction vs non-fic), BLOCKING/WARNING/INFO severity, exit-code semantics for git hook. |
| [`translation-sync`](skills/translation-sync/) | linter | ru/en/pt-br | Read-only pre-commit parity checker for trilingual book translations (RU↔EN↔PT-BR) — typography per language, terminology canon, anchor-quote drift, names/patronymics/diminutives, cultural realia footnotes, no-smoothing of numbers/brands/dates. BLOCKING/WARNING/INFO severity with exit-code semantics for git hook. |
| [`canon-check`](skills/canon-check/) | linter | ru/en | Story-bible consistency auditor for any book series. Greps entities (characters / artifacts / locations) in changed chapters, cross-references the project's story-bible document, flags BLOCKING contradictions / WARNING gaps / INFO new details. Read-only — trust the text, not memory. |
| [`pelevin-digression`](skills/pelevin-digression/) | wrapper | ru | Write a Pelevin-style digression for a fiction or non-fiction passage — 12 structural techniques + 5 banned constructions. Wraps prose-edit (fiction) or essay-write (non-fic). Invoked by request, not auto-applied. |
| [`skills-update`](skills/skills-update/) | meta | en/ru | User-invocable update check + apply for this collection. Compares local install marker with latest GitHub release, shows CHANGELOG diff, asks for confirmation, runs install.sh --update. |
| [`skills-keys`](skills/skills-keys/) | meta | en/ru | Manage API keys for the runner's --execute layer. CRUD on ~/.skills.env (chmod 600): list / add / update / remove / enable / disable gate flags / verify (ping vendor APIs) / export. Single source of truth for OPENAI / GEMINI / BFL / FAL / REPLICATE / RUNWAY / KLING / SUNO / ELEVENLABS / IDEOGRAM / ANTHROPIC keys + gate flags + S3 storage env vars. Explicit shell exports always win over file entries. |
| [`skills-styles`](skills/skills-styles/) | meta | en/ru | Manage the local style library — bundled styles (24 carousel + 12 video director + 12 music genre) plus user overrides at ~/.claude/style-library/<modality>/<id>.md. CRUD on user styles (add / edit / remove / show / list / diff / validate / path) and build upstream-PR submission packages (submit). Frontmatter + body schema validation per modality. Templates ship with the library. |
| [`tone-shifter`](skills/tone-shifter/) | wrapper | en/ru | Rewrite a passage in a different register (formal↔casual, business↔academic, technical↔friendly, plain-explainer) without changing meaning. 6 registers + named transformation deltas. Wraps writer as final cleanup. |
| [`cold-email`](skills/cold-email/) | wrapper | en/ru | Write or rewrite cold outreach emails (first-touch, follow-up, intro request, re-engage). 5-block structure, ≤120-word budget, banned ceremony patterns, anti-template subject lines. Wraps writer as final cleanup. |
| [`image-prompt`](skills/image-prompt/) | wrapper | en/ru | Write prompts for 14+ frontier AI image generators (Midjourney v7, Flux 2 / Flux Kontext, Imagen 4 Ultra, Nano Banana Pro / Gemini 3 Image, gpt-image-2, Ideogram 3, Recraft V3, Seedream 4.5, Qwen-Image, HiDream-O1, Krea-1, SD 3.5, SDXL). Modes: text-to-image, edit (preserve/change), multi-reference, text-in-image. 6-part formula + per-model deltas, character/identity locks, weighted multi-ref. |
| [`video-prompt`](skills/video-prompt/) | wrapper | en/ru | Write prompts for 20+ frontier AI video generators (Veo 3.1 + native audio, Sora 2 + cameos, Kling 3.0 / Elements, Runway Gen-4 / Aleph V2V / Act-One, Luma Ray 3 / Modify, Pika 2.2 / Pikaframes, Hailuo 02, Higgsfield, LTX-2, HunyuanCustom, Wan 2.2, Seedance). Modes: T2V / I2V / V2V / extend / multi-shot / dialogue+audio. CHARACTER FIRST law, beat structure, exact camera vocabulary, identity-reference grammar, pacing modes (incl. dialogue-scene + music-video). |
| [`music-prompt`](skills/music-prompt/) | wrapper | en/ru | Write prompts for 10+ frontier AI music generators (Suno v5.5, Udio v4, Google Lyria 3 Pro, ElevenLabs Music, Stable Audio 2.5, MusicGen, Tencent SongGeneration, Sonauto v2, Riffusion, Mubert). 2026 canonical 8-category meta-tag taxonomy, `\|` stacking, two-box Style+Lyrics workflow (Suno), exclude-styles (Eleven), field-driven (Lyria). 12 genre recipes. |
| [`microcopy`](skills/microcopy/) | wrapper | en/ru | Write UX microcopy — error messages, empty states, tooltips, button labels, helper text, modals, 404/500 pages, onboarding. Plain language, action-oriented, never blame user, length budgets per element type. Wraps writer for final cleanup. |
| [`release-notes`](skills/release-notes/) | wrapper | en/ru | Write user-facing release notes + changelogs. Keep-a-Changelog format, sections Added/Changed/Fixed/Deprecated/Removed/Security. Per-audience tone (user/dev/ops). Anti-marketing-fluff bans. Wraps writer. |
| [`rfc-writer`](skills/rfc-writer/) | wrapper | en/ru | Write engineer-facing design docs — RFCs, ADRs, Tech Specs, Design Docs. Structure: context/problem/proposal/alternatives/consequences/decision. RFC 2119 (MUST/SHOULD/MAY). Review checklist for spotting weak alternatives sections. |
| [`landing-copy`](skills/landing-copy/) | wrapper | en/ru | Write marketing copy — landing page sections (hero/features/pricing/FAQ), SEO meta (title+description+OG+Twitter), ad copy (Google/Facebook/LinkedIn/X). Julian Shapiro hero formula, char limits per platform. Wraps writer. |
| [`research-brief`](skills/research-brief/) | orchestrator | en/ru | Produce a structured research brief on any topic — TL;DR, key facts with citations, notable quotes, suggested angles, open questions. 3-15 queries by depth, multi-source (WebSearch + WebFetch + optional Firecrawl/Exa MCP). Output is a markdown file ready for downstream consumption by carousel-builder, reel-builder, viral-text, essay-write, landing-copy. |
| [`carousel-builder`](skills/carousel-builder/) | orchestrator | en/ru | Turn a topic or research brief into an N-slide Instagram / LinkedIn / TikTok carousel with consistent visual style and ready-to-post captions. Wraps essay-write + viral-text + image-prompt --execute + common style library (24 visual styles). Outputs PNG slides + captions.md + manifest. Modes: --topic / --research; --style auto\|<library-id>\|--style-ref <image>; --slides 3-12; --platform instagram\|linkedin\|tiktok; --text-mode embedded\|overlay\|none; --execute; --resume. |
| [`cover-maker`](skills/cover-maker/) | orchestrator | en/ru | Turn cover metadata (title / creator / subtitle / medium) into an album / book / podcast / report / deck / magazine cover. Wraps image-prompt --execute + the carousel style library (24 visual styles) + the runner's batch executor. Picks aspect by medium. Multi-variant output. Optional photo / artwork reference. Outputs: ./generated/cover/<slug>/<medium>.png + manifest.json. |
| [`thumbnail-maker`](skills/thumbnail-maker/) | orchestrator | en/ru | Produce YouTube / blog / podcast-episode thumbnails. 16:9 default (1280×720 standard, 1920×1080 high-res). Face + bold title aesthetic; supports face-placement variants (left / right / center). Wraps image-prompt --execute + the carousel style library + the runner's batch executor. Outputs: ./generated/thumbnail/<slug>/<variant>.png + manifest.json. |
| [`bg-remover`](skills/bg-remover/) | wrapper | en/ru | Background removal utility — image in, transparent PNG out. Wraps Replicate-hosted background removal models (851-labs/background-remover by default). Single image input, transparent PNG output. ~$0.001-0.005 per image. |
| [`avatar-maker`](skills/avatar-maker/) | orchestrator | en/ru | Turn a user photo into N profile-pic / headshot / avatar variants in a consistent style. Wraps image-prompt --execute + the carousel style library + the runner's batch executor. Identity preserve is THE differentiator — defaults to nano-banana-pro for best face preservation. Multi-aspect output (square 1:1, square-tight, cover 4:5, story 9:16, wide 16:9). Outputs: ./generated/avatar/<slug>/<aspect>-v<N>.png + manifest.json. |
| [`voiceover-maker`](skills/voiceover-maker/) | wrapper | en/ru | Text-to-speech skill — script in, MP3 out. Wraps the runner's audio modality (ElevenLabs eleven-tts + OpenAI gpt-4o-mini-tts). Supports voice picker, multilingual TTS (Eleven), speed control, long-form scripts. Auto-picks provider based on language + script length + brand-voice needs. Saves to ./generated/audio/<timestamp>-<model>.mp3. |
| [`subtitle-burner`](skills/subtitle-burner/) | wrapper | en/ru | Burn captions / subtitles onto an existing video via ffmpeg. Supports SRT, WebVTT, and plain-text subtitle sources. Style presets (modern / minimal / bold) + per-flag customization (font-size, color, backplate). Outputs <video>-subtitled<ext>. No API calls — pure ffmpeg. Subcommands: burn / preview. |
| [`flyer-maker`](skills/flyer-maker/) | orchestrator | en/ru | Turn event details (title / date / location / CTA) plus an optional photo into a poster/flyer/social-event-graphic with embedded text in a chosen visual style. Wraps image-prompt --execute + the carousel style library (24 visual styles) + the runner's batch executor. Picks a text-friendly + multi-ref-capable model (gpt-image-2 / ideogram-3-quality / nano-banana-pro). Multi-aspect output (portrait / square / story / landscape / a4). Outputs: ./generated/flyer/<event-slug>/<aspect>.png + manifest.json + prompts.md. |
| [`reel-builder`](skills/reel-builder/) | orchestrator | en/ru | Turn a topic / research brief / script into a vertical reel: 1-4 video shots + matched background music + ffmpeg-stitched final.mp4 with optional burned-in captions. Wraps viral-text + video-prompt --execute + music-prompt --execute + common video/music style library + ffmpeg. Outputs final.mp4 + shots/ + music.mp3 + script.md + manifest. Modes: --topic / --research / --script-file; --shots 1-5; --style auto\|<library-id>; --music-style auto\|<library-id>; --captions on\|off; --execute; --resume. |
| [`logo-maker`](skills/logo-maker/) | orchestrator | en/ru | Brand mark / wordmark / logo generator. Defaults to ideogram-3-quality (cleanest embedded text). Six style presets (wordmark / minimal / illustrated / typographic / geometric / emblem) + optional palette hint. Single-image output, N stochastic variants per call. Outputs: ./generated/logo/<slug>/logo-v<N>.png + manifest.json. |
| [`quote-card-maker`](skills/quote-card-maker/) | orchestrator | en/ru | Quote card / aphorism graphic generator — short text + attribution on a typography-dominant composition. Wraps image-prompt --execute + the carousel style library biased toward text-friendly anchors (minimal-serif / swiss-grid / editorial-magazine / monochrome-bold / gradient-mesh-modern / russian-constructivist). Multi-aspect (square / portrait / story / landscape). Default model ideogram-3-quality. Outputs: ./generated/quote/<slug>/<aspect>.png + manifest.json. |
| [`gif-maker`](skills/gif-maker/) | wrapper | en/ru | Short looping GIF utility. Mode A: convert existing MP4 → GIF via ffmpeg 2-pass palette optimization. Mode B: generate 1-3s clip via a video provider (Veo / Kling / fal-video / Sora) then convert. Aspect crop presets (1:1 / 9:16 / 16:9 / 4:5 / 2:1). Outputs: ./generated/gif/<name>.gif. |
| [`banner-maker`](skills/banner-maker/) | orchestrator | en/ru | Banner-ad / display-creative generator with standard-size presets — Google Display (leaderboard, medium-rectangle, mobile-banner, wide-skyscraper), OG image, LinkedIn ad, Facebook ad, Twitter card. Headline + CTA + brand composition. Default model ideogram-3-quality for clean embedded text. Outputs: ./generated/banner/<slug>/<preset>.png + manifest.json. |
| [`meme-card-maker`](skills/meme-card-maker/) | orchestrator | en/ru | Meme-format graphic generator — top text + bottom text + optional centerpiece image. Wraps image-prompt --execute with Impact-style typography (bold white text + thick black stroke). Supports 5 template hints (drake / distracted-boyfriend / expanding-brain / two-buttons / change-my-mind) + custom mode. Optional --base-photo for user-image centerpiece. Default model gpt-image-2. Outputs: ./generated/meme/<slug>/meme-v<N>.png + manifest.json. |
| [`upscaler`](skills/upscaler/) | wrapper | en/ru | Image upscaling utility — single image in, upscaled image out (2× / 4× / 8×). Wraps Replicate-hosted upscalers (Real-ESRGAN default; alternatives: GFPGAN for faces, SwinIR, clarity-upscaler). Optional --face-enhance for portrait restoration. ~$0.005-0.02 per image. |
| [`audio-mix-maker`](skills/audio-mix-maker/) | wrapper | en/ru | Mix a music / audio track onto an existing video via ffmpeg. Three modes: replace (drop original audio), overlay (mix both audible), duck (sidechain compressor lowers music when speech detected). Volume + fade controls. No API calls — pure ffmpeg. |
| [`style-transfer`](skills/style-transfer/) | wrapper | en/ru | Apply an artistic style to an existing image. Default provider Flux Kontext. 12 style presets (watercolor / oil-painting / sketch / line-art / ink-wash / cyberpunk / studio-ghibli / pixar-3d / manga / art-deco / low-poly / vaporwave) + custom mode. ~$0.05 per image. |
| [`transcribe-maker`](skills/transcribe-maker/) | wrapper | en/ru | Transcribe audio / video to SRT / WebVTT / JSON / plain text via OpenAI Whisper. Auto-detects language or accepts ISO-639-1 hint. ~$0.006/min. Closes the loop with subtitle-burner — produce captions from video, then burn them in. 25 MB file limit. |
| [`style-suggest`](skills/style-suggest/) | orchestrator | en/ru | Visual-style generator — turn a text description and/or reference image into a fully-structured style entry that drops into common/visual-prompt-library/styles/. Adapted from figma's StyleSuggestAgent: takes free-form input, checks the existing catalog for duplicates (similarity ≥ 0.72), otherwise produces a new entry with all v2.15.0 schema fields (background / accents / elements / mood / accent_text_color / typography / composition_signature / when_to_use). The new style is immediately usable by every visual-output skill via the shared chain. |
| [`proposal-maker`](skills/proposal-maker/) | orchestrator | en/ru | Turn a raw, telegram-style commercial offer into a self-contained, brand-faithful HTML proposal whose style is copied from a website. Default flow is LLM-authored: a Python step builds a brand kit (site screenshot + logo + accent/font tokens + per-item catalogue photos + BRIEF.md), then the orchestrator authors bespoke HTML mirroring the brand. Items missing a photo get an on-brand generated image; prices and links stay exact; prints to a Ghostscript-compressed PDF. A --quick mode renders a deterministic theme (editorial/invoice/dark). Output: ./generated/proposal/<slug>/. |
| [`post-publisher`](skills/post-publisher/) | orchestrator | en/ru | Publish finished assets to Instagram / Threads / TikTok / X / YouTube / Telegram / LinkedIn through the official APIs. Takes a carousel-builder or reel-builder output directory, reads captions.md, runs a per-platform preflight (char limits, media count, file size, posting caps), previews, confirms per platform, then publishes and writes a posted.json receipt so the same content cannot go out twice. Dry-run by default; --yes leaves it; --draft where the platform has drafts. OAuth tokens live in ~/.skills-tokens.json with automatic refresh. |

<!-- END skills-table -->

Skills compose: wrappers call `writer` internally; linters reference the same rule files but don't mutate; orchestrators chain multiple wrappers + the execute runner. See [docs/COMPOSING.md](docs/COMPOSING.md) for the full dependency graph and named workflows.

---

## The `--execute` layer (optional)

`image-prompt`, `video-prompt`, `music-prompt` produce paste-ready prompts by default. Pass `--execute` and they ALSO call the vendor API and save real PNG / MP4 / MP3 assets. Without API keys they stay prompt-only — no breakage.

`carousel-builder` and `reel-builder` are orchestrators built on this layer — they assemble batches of prompts and execute them with a single style anchor + cost confirmation.

```bash
# image
~/.claude/skills/image-prompt/scripts/run.py --execute --model gpt-image-2 --prompt "..."

# video (cost confirmation prompts; --yes to skip)
~/.claude/skills/video-prompt/scripts/run.py --execute --model veo-3-1-fast --prompt "..." --duration 8

# music
~/.claude/skills/music-prompt/scripts/run.py --execute --model suno-v5-5 --prompt "..." --lyrics-file ./lyrics.txt
```

Vendors covered: OpenAI (gpt-image-2, Sora 2, TTS), Google (Imagen 4, Nano Banana Pro, Veo 3.1, Lyria 3 Pro), Black Forest Labs (Flux family + Kontext), Runway (Gen-4 + Aleph), Kuaishou (Kling 3.0), Ideogram (3 Turbo/Default/Quality), ElevenLabs (Music + TTS), Suno (v5.5), fal.ai + Replicate routers for everything else (Seedream, Hunyuan, LTX-2, Wan, MusicGen, Stable Audio, many open-source).

Output: assets land at `./generated/<modality>/<timestamp>-<model>.<ext>`. If `S3_BUCKET` is set, they also upload to S3-compatible storage (AWS S3 / DigitalOcean Spaces / Cloudflare R2 / MinIO) and the URL is printed alongside.

Setup is one command:

```bash
# Inside Claude Code, after install
/skills-keys add OPENAI_API_KEY sk-proj-...
/skills-keys add GEMINI_API_KEY AIza...
/skills-keys verify             # ping each vendor; confirm valid/invalid/unknown
```

The runner auto-creates `~/.claude/skills/.runners-venv` and installs Python deps (requires Python ≥ 3.10). Override with `SKILLS_SKIP_VENV=1` if Python is missing.

Full provider matrix + cost preview + per-vendor troubleshooting: `skills/image-prompt/references/execute.md`, `skills/video-prompt/references/execute.md`, `skills/music-prompt/references/execute.md`.

---

## Managing API keys

Keys for the `--execute` layer live in `~/.skills.env` (chmod 600). The runner auto-loads it into `os.environ` at every CLI startup — explicit shell exports still win.

```bash
/skills-keys list                                    # masked overview
/skills-keys add OPENAI_API_KEY                      # interactive (silent stdin prompt)
/skills-keys update OPENAI_API_KEY sk-proj-new...    # rotate
/skills-keys remove OPENAI_API_KEY
/skills-keys enable SUNO_API_ENABLED                 # gate-flag shortcut
/skills-keys verify                                  # ping 9 providers (OpenAI/Gemini/Anthropic/BFL/Ideogram/Replicate/FAL/Runway/Eleven)
/skills-keys export                                  # eval-ready lines for current shell
```

Full reference: [skills/skills-keys/references/usage.md](skills/skills-keys/references/usage.md) · [examples](skills/skills-keys/examples/before-after.md).

Don't have an API key for one of these vendors? The matching skill stays in prompt-only mode — paste the generated prompt into the vendor's UI manually. No skill requires any key.

---

## Updating

```bash
/skills-update                                       # in-Claude check + apply
bash install.sh --check                              # CLI version diff
bash install.sh --update                             # re-install from latest release
```

Optional ambient banner in your shell status line (opt-in): `bash scripts/install-hook.sh`. Shows ` · skills v2.3.0→2.3.1 +1 skill` when an update exists. Never updates without confirmation.

---

## Common install flags

```bash
# Install a subset
curl -fsSL .../install.sh | bash -s -- --skills writer,viral-text

# Custom prefix
curl -fsSL .../install.sh | bash -s -- --prefix /tmp/skills

# Pin a version
curl -fsSL .../install.sh | bash -s -- --version 2.3.0

# Update existing install (re-install + new deps)
bash install.sh --update

# Diff local vs latest
bash install.sh --check

# Uninstall everything
bash install.sh --uninstall
```

Full installer help: `bash install.sh --help` · [`docs/INSTALL.md`](docs/INSTALL.md).

---

## Repo layout

```
skills/
├── README.md                # this file
├── VERSION                  # semver, single source of truth
├── CHANGELOG.md             # Keep-a-Changelog
├── skills.json              # machine-readable manifest used by the installer
├── install.sh               # pure-bash installer, curl-pipeable
├── .env.example             # template for ~/.skills.env (manage via /skills-keys)
├── Makefile                 # local dev convenience
├── CONTRIBUTING.md          # how to add / report / propose a skill
├── CODE_OF_CONDUCT.md       # short; scales up if the project does
├── SECURITY.md              # how to report a vulnerability
│
├── skills/                  # the 42 skills, one folder each
│   └── <skill-name>/
│       ├── SKILL.md         # frontmatter + the rules; this IS the skill
│       ├── references/      # deep material loaded on demand
│       ├── examples/        # before/after calibration pairs
│       └── scripts/         # only where a skill ships code (writer's linter)
│
├── common/
│   ├── references/          # shared anti-pattern catalogues (hype words, preambles, …)
│   ├── runners/             # optional Python execute layer (image/video/music)
│   │   ├── providers/       # 14 image + 10 video + 5 music + 3 audio = 32 providers
│   │   ├── cli/             # per-modality CLI entries (image / video / music / carousel / reel / keys)
│   │   ├── styles.py        # style library loader
│   │   ├── batch.py         # parallel executor for carousel / reel
│   │   ├── ffmpeg.py        # concat / audio mix / caption burn-in
│   │   ├── keysfile.py      # CRUD over ~/.skills.env
│   │   ├── verify.py        # HTTP probes for 9 providers
│   │   └── requirements.txt
│   └── style-library/       # 48 bundled styles (24 carousel + 12 director + 12 music)
│
├── docs/
│   ├── QUICKSTART.md        # 5-minute first run
│   ├── USER-GUIDE.md        # scenarios with TOC
│   ├── COMPOSING.md         # dependency graph + named workflows
│   ├── INSTALL.md           # detailed install methods
│   ├── SKILL-INDEX.md       # auto-generated, by layer/domain/language
│   ├── FAQ.md               # short Q&A
│   ├── TROUBLESHOOTING.md   # when things break
│   ├── VERSIONING.md        # semver policy + release flow
│   ├── LINTER-COVERAGE.md   # auto-generated regex coverage
│   ├── LAUNCH-POST.md       # frozen v1.9 launch copy
│   └── walkthroughs/
│       ├── README.md        # categorized index
│       └── *.md             # 20 detailed flows
│
├── scripts/                 # validate + smoke + doc generators
├── hooks/                   # ambient update banner (opt-in)
├── tests/                   # fixtures + snapshots, runner unit tests, model-in-loop evals
├── bin/                     # the `skills` CLI shim (npm package)
└── .github/                 # workflows + issue/PR templates
```

---

## Local development

```bash
make help                       # list all targets
make install                    # install from this checkout into ~/.claude/skills/
make smoke                      # 14 gates: validate, linter, snapshots, samples, links,
                                #           unit tests, pricing, markdownlint, coverage, tweets,
                                #           launch copy, imports, code quality, CLI surface
make test-unit                  # runner unit tests alone
make check-docs                 # docs-consistency gate
make gen                        # regenerate every derived file (README table, indexes, coverage)
make new-skill NAME=foo-bar DESC="..."
```

Releases are manual: `make bump-minor` → fill the CHANGELOG section → `make release` (verifies, tags, pushes) → publish the GitHub release. That last step matters — `install.sh` resolves `latest` from the newest *published release*, so a bare tag leaves `curl` installs on the previous version. See [docs/VERSIONING.md](docs/VERSIONING.md).

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](LICENSE).
