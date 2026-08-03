# Skill index

Auto-generated map of every skill in the collection — by layer, by
domain, and by supported language. The body between the markers below
is regenerated from `skills.json` by `python3 scripts/gen-skill-index.py
--write` (or `make gen-index`).

For scenario-driven discovery ("I want to write a landing page"), see
[USER-GUIDE.md](USER-GUIDE.md). For workflow recipes (chaining multiple
skills), see [COMPOSING.md](COMPOSING.md).

<!-- BEGIN skill-index (auto-generated; run `make gen-index`) -->

## By layer

### Base

| Skill | Tags | Languages |
| --- | --- | --- |
| [`writer`](../skills/writer/) | editing | ru / en |

### Wrappers

| Skill | Tags | Languages |
| --- | --- | --- |
| [`viral-text`](../skills/viral-text/) | marketing, social, generation | ru / en |
| [`prose-edit`](../skills/prose-edit/) | fiction, editing | ru |
| [`essay-write`](../skills/essay-write/) | non-fiction, generation | ru |
| [`pelevin-digression`](../skills/pelevin-digression/) | fiction, non-fiction, generation | ru |
| [`tone-shifter`](../skills/tone-shifter/) | editing | en / ru |
| [`cold-email`](../skills/cold-email/) | outreach, generation | en / ru |
| [`image-prompt`](../skills/image-prompt/) | visual, generation | en / ru |
| [`video-prompt`](../skills/video-prompt/) | visual, generation | en / ru |
| [`music-prompt`](../skills/music-prompt/) | audio, generation | en / ru |
| [`microcopy`](../skills/microcopy/) | ux-copy, product, generation | en / ru |
| [`release-notes`](../skills/release-notes/) | product, tech-docs, generation | en / ru |
| [`rfc-writer`](../skills/rfc-writer/) | tech-docs, generation | en / ru |
| [`landing-copy`](../skills/landing-copy/) | marketing, generation | en / ru |
| [`bg-remover`](../skills/bg-remover/) | visual, editing | en / ru |
| [`voiceover-maker`](../skills/voiceover-maker/) | audio, generation | en / ru |
| [`subtitle-burner`](../skills/subtitle-burner/) | visual, editing | en / ru |
| [`gif-maker`](../skills/gif-maker/) | visual, generation, editing | en / ru |
| [`upscaler`](../skills/upscaler/) | visual, editing | en / ru |
| [`audio-mix-maker`](../skills/audio-mix-maker/) | audio, editing | en / ru |
| [`style-transfer`](../skills/style-transfer/) | visual, editing, generation | en / ru |
| [`transcribe-maker`](../skills/transcribe-maker/) | audio, editing | en / ru |

### Linters (read-only)

| Skill | Tags | Languages |
| --- | --- | --- |
| [`style-check`](../skills/style-check/) | audit, editing | ru / en |
| [`translation-sync`](../skills/translation-sync/) | translation, audit | ru / en / pt-br |
| [`canon-check`](../skills/canon-check/) | fiction, audit | ru / en |

### Orchestrators

| Skill | Tags | Languages |
| --- | --- | --- |
| [`research-brief`](../skills/research-brief/) | research, generation | en / ru |
| [`carousel-builder`](../skills/carousel-builder/) | visual, marketing, generation, orchestration | en / ru |
| [`cover-maker`](../skills/cover-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`thumbnail-maker`](../skills/thumbnail-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`avatar-maker`](../skills/avatar-maker/) | visual, generation, orchestration | en / ru |
| [`flyer-maker`](../skills/flyer-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`reel-builder`](../skills/reel-builder/) | visual, audio, marketing, generation, orchestration | en / ru |
| [`logo-maker`](../skills/logo-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`quote-card-maker`](../skills/quote-card-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`banner-maker`](../skills/banner-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`meme-card-maker`](../skills/meme-card-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`style-suggest`](../skills/style-suggest/) | visual, generation | en / ru |
| [`proposal-maker`](../skills/proposal-maker/) | marketing, generation, orchestration | en / ru |
| [`post-publisher`](../skills/post-publisher/) | social, marketing, orchestration, ops | en / ru |

### Meta

| Skill | Tags | Languages |
| --- | --- | --- |
| [`skills-update`](../skills/skills-update/) | ops | en / ru |
| [`skills-keys`](../skills/skills-keys/) | ops | en / ru |
| [`skills-styles`](../skills/skills-styles/) | ops, visual | en / ru |

## By domain

- **audio** — [`music-prompt`](../skills/music-prompt/), [`voiceover-maker`](../skills/voiceover-maker/), [`reel-builder`](../skills/reel-builder/), [`audio-mix-maker`](../skills/audio-mix-maker/), [`transcribe-maker`](../skills/transcribe-maker/)
- **fiction** — [`prose-edit`](../skills/prose-edit/), [`canon-check`](../skills/canon-check/), [`pelevin-digression`](../skills/pelevin-digression/)
- **marketing** — [`viral-text`](../skills/viral-text/), [`landing-copy`](../skills/landing-copy/), [`carousel-builder`](../skills/carousel-builder/), [`cover-maker`](../skills/cover-maker/), [`thumbnail-maker`](../skills/thumbnail-maker/), [`flyer-maker`](../skills/flyer-maker/), [`reel-builder`](../skills/reel-builder/), [`logo-maker`](../skills/logo-maker/), [`quote-card-maker`](../skills/quote-card-maker/), [`banner-maker`](../skills/banner-maker/), [`meme-card-maker`](../skills/meme-card-maker/), [`proposal-maker`](../skills/proposal-maker/), [`post-publisher`](../skills/post-publisher/)
- **non-fiction** — [`essay-write`](../skills/essay-write/), [`pelevin-digression`](../skills/pelevin-digression/)
- **outreach** — [`cold-email`](../skills/cold-email/)
- **product** — [`microcopy`](../skills/microcopy/), [`release-notes`](../skills/release-notes/)
- **research** — [`research-brief`](../skills/research-brief/)
- **social** — [`viral-text`](../skills/viral-text/), [`post-publisher`](../skills/post-publisher/)
- **tech-docs** — [`release-notes`](../skills/release-notes/), [`rfc-writer`](../skills/rfc-writer/)
- **ux-copy** — [`microcopy`](../skills/microcopy/)
- **visual** — [`skills-styles`](../skills/skills-styles/), [`image-prompt`](../skills/image-prompt/), [`video-prompt`](../skills/video-prompt/), [`carousel-builder`](../skills/carousel-builder/), [`cover-maker`](../skills/cover-maker/), [`thumbnail-maker`](../skills/thumbnail-maker/), [`bg-remover`](../skills/bg-remover/), [`avatar-maker`](../skills/avatar-maker/), [`subtitle-burner`](../skills/subtitle-burner/), [`flyer-maker`](../skills/flyer-maker/), [`reel-builder`](../skills/reel-builder/), [`logo-maker`](../skills/logo-maker/), [`quote-card-maker`](../skills/quote-card-maker/), [`gif-maker`](../skills/gif-maker/), [`banner-maker`](../skills/banner-maker/), [`meme-card-maker`](../skills/meme-card-maker/), [`upscaler`](../skills/upscaler/), [`style-transfer`](../skills/style-transfer/), [`style-suggest`](../skills/style-suggest/)

## By language

- **EN + PT-BR + RU** (1) — [`translation-sync`](../skills/translation-sync/)
- **EN + RU** (38) — [`writer`](../skills/writer/), [`viral-text`](../skills/viral-text/), [`style-check`](../skills/style-check/), [`canon-check`](../skills/canon-check/), [`skills-update`](../skills/skills-update/), [`skills-keys`](../skills/skills-keys/), [`skills-styles`](../skills/skills-styles/), [`tone-shifter`](../skills/tone-shifter/), [`cold-email`](../skills/cold-email/), [`image-prompt`](../skills/image-prompt/), [`video-prompt`](../skills/video-prompt/), [`music-prompt`](../skills/music-prompt/), [`microcopy`](../skills/microcopy/), [`release-notes`](../skills/release-notes/), [`rfc-writer`](../skills/rfc-writer/), [`landing-copy`](../skills/landing-copy/), [`research-brief`](../skills/research-brief/), [`carousel-builder`](../skills/carousel-builder/), [`cover-maker`](../skills/cover-maker/), [`thumbnail-maker`](../skills/thumbnail-maker/), [`bg-remover`](../skills/bg-remover/), [`avatar-maker`](../skills/avatar-maker/), [`voiceover-maker`](../skills/voiceover-maker/), [`subtitle-burner`](../skills/subtitle-burner/), [`flyer-maker`](../skills/flyer-maker/), [`reel-builder`](../skills/reel-builder/), [`logo-maker`](../skills/logo-maker/), [`quote-card-maker`](../skills/quote-card-maker/), [`gif-maker`](../skills/gif-maker/), [`banner-maker`](../skills/banner-maker/), [`meme-card-maker`](../skills/meme-card-maker/), [`upscaler`](../skills/upscaler/), [`audio-mix-maker`](../skills/audio-mix-maker/), [`style-transfer`](../skills/style-transfer/), [`transcribe-maker`](../skills/transcribe-maker/), [`style-suggest`](../skills/style-suggest/), [`proposal-maker`](../skills/proposal-maker/), [`post-publisher`](../skills/post-publisher/)
- **RU** (3) — [`prose-edit`](../skills/prose-edit/), [`essay-write`](../skills/essay-write/), [`pelevin-digression`](../skills/pelevin-digression/)

<!-- END skill-index -->
