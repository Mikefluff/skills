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
| [`audio-mix-maker`](../skills/audio-mix-maker/) | audio, editing | en / ru |
| [`bg-remover`](../skills/bg-remover/) | visual, editing | en / ru |
| [`cold-email`](../skills/cold-email/) | outreach, generation | en / ru |
| [`essay-write`](../skills/essay-write/) | non-fiction, generation | ru |
| [`gif-maker`](../skills/gif-maker/) | visual, generation, editing | en / ru |
| [`image-prompt`](../skills/image-prompt/) | visual, generation | en / ru |
| [`landing-copy`](../skills/landing-copy/) | marketing, generation | en / ru |
| [`microcopy`](../skills/microcopy/) | ux-copy, product, generation | en / ru |
| [`model-maker`](../skills/model-maker/) | visual, generation | en / ru |
| [`music-prompt`](../skills/music-prompt/) | audio, generation | en / ru |
| [`pelevin-digression`](../skills/pelevin-digression/) | fiction, non-fiction, generation | ru |
| [`prose-edit`](../skills/prose-edit/) | fiction, editing | ru |
| [`release-notes`](../skills/release-notes/) | product, tech-docs, generation | en / ru |
| [`rfc-writer`](../skills/rfc-writer/) | tech-docs, generation | en / ru |
| [`schema-maker`](../skills/schema-maker/) | tech-docs, generation | en |
| [`style-transfer`](../skills/style-transfer/) | visual, editing, generation | en / ru |
| [`subtitle-burner`](../skills/subtitle-burner/) | visual, editing | en / ru |
| [`tone-shifter`](../skills/tone-shifter/) | editing | en / ru |
| [`transcribe-maker`](../skills/transcribe-maker/) | audio, editing | en / ru |
| [`upscaler`](../skills/upscaler/) | visual, editing | en / ru |
| [`video-prompt`](../skills/video-prompt/) | visual, generation | en / ru |
| [`viral-text`](../skills/viral-text/) | marketing, social, generation | ru / en |
| [`voiceover-maker`](../skills/voiceover-maker/) | audio, generation | en / ru |

### Linters (read-only)

| Skill | Tags | Languages |
| --- | --- | --- |
| [`canon-check`](../skills/canon-check/) | fiction, audit | ru / en |
| [`style-check`](../skills/style-check/) | audit, editing | ru / en |
| [`translation-sync`](../skills/translation-sync/) | translation, audit | ru / en / pt-br |

### Orchestrators

| Skill | Tags | Languages |
| --- | --- | --- |
| [`avatar-maker`](../skills/avatar-maker/) | visual, generation, orchestration | en / ru |
| [`banner-maker`](../skills/banner-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`carousel-builder`](../skills/carousel-builder/) | visual, marketing, generation, orchestration | en / ru |
| [`cover-maker`](../skills/cover-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`flyer-maker`](../skills/flyer-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`logo-maker`](../skills/logo-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`meme-card-maker`](../skills/meme-card-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`post-publisher`](../skills/post-publisher/) | social, marketing, orchestration, ops | en / ru |
| [`proposal-maker`](../skills/proposal-maker/) | marketing, generation, orchestration | en / ru |
| [`quote-card-maker`](../skills/quote-card-maker/) | visual, marketing, generation, orchestration | en / ru |
| [`reel-builder`](../skills/reel-builder/) | visual, audio, marketing, generation, orchestration | en / ru |
| [`research-brief`](../skills/research-brief/) | research, generation | en / ru |
| [`style-suggest`](../skills/style-suggest/) | visual, generation | en / ru |
| [`thumbnail-maker`](../skills/thumbnail-maker/) | visual, marketing, generation, orchestration | en / ru |

### Meta

| Skill | Tags | Languages |
| --- | --- | --- |
| [`skills-keys`](../skills/skills-keys/) | ops | en / ru |
| [`skills-styles`](../skills/skills-styles/) | ops, visual | en / ru |
| [`skills-update`](../skills/skills-update/) | ops | en / ru |

## By domain

- **audio** — [`audio-mix-maker`](../skills/audio-mix-maker/), [`music-prompt`](../skills/music-prompt/), [`reel-builder`](../skills/reel-builder/), [`transcribe-maker`](../skills/transcribe-maker/), [`voiceover-maker`](../skills/voiceover-maker/)
- **fiction** — [`canon-check`](../skills/canon-check/), [`pelevin-digression`](../skills/pelevin-digression/), [`prose-edit`](../skills/prose-edit/)
- **marketing** — [`banner-maker`](../skills/banner-maker/), [`carousel-builder`](../skills/carousel-builder/), [`cover-maker`](../skills/cover-maker/), [`flyer-maker`](../skills/flyer-maker/), [`landing-copy`](../skills/landing-copy/), [`logo-maker`](../skills/logo-maker/), [`meme-card-maker`](../skills/meme-card-maker/), [`post-publisher`](../skills/post-publisher/), [`proposal-maker`](../skills/proposal-maker/), [`quote-card-maker`](../skills/quote-card-maker/), [`reel-builder`](../skills/reel-builder/), [`thumbnail-maker`](../skills/thumbnail-maker/), [`viral-text`](../skills/viral-text/)
- **non-fiction** — [`essay-write`](../skills/essay-write/), [`pelevin-digression`](../skills/pelevin-digression/)
- **outreach** — [`cold-email`](../skills/cold-email/)
- **product** — [`microcopy`](../skills/microcopy/), [`release-notes`](../skills/release-notes/)
- **research** — [`research-brief`](../skills/research-brief/)
- **social** — [`post-publisher`](../skills/post-publisher/), [`viral-text`](../skills/viral-text/)
- **tech-docs** — [`release-notes`](../skills/release-notes/), [`rfc-writer`](../skills/rfc-writer/), [`schema-maker`](../skills/schema-maker/)
- **ux-copy** — [`microcopy`](../skills/microcopy/)
- **visual** — [`avatar-maker`](../skills/avatar-maker/), [`banner-maker`](../skills/banner-maker/), [`bg-remover`](../skills/bg-remover/), [`carousel-builder`](../skills/carousel-builder/), [`cover-maker`](../skills/cover-maker/), [`flyer-maker`](../skills/flyer-maker/), [`gif-maker`](../skills/gif-maker/), [`image-prompt`](../skills/image-prompt/), [`logo-maker`](../skills/logo-maker/), [`meme-card-maker`](../skills/meme-card-maker/), [`model-maker`](../skills/model-maker/), [`quote-card-maker`](../skills/quote-card-maker/), [`reel-builder`](../skills/reel-builder/), [`skills-styles`](../skills/skills-styles/), [`style-suggest`](../skills/style-suggest/), [`style-transfer`](../skills/style-transfer/), [`subtitle-burner`](../skills/subtitle-burner/), [`thumbnail-maker`](../skills/thumbnail-maker/), [`upscaler`](../skills/upscaler/), [`video-prompt`](../skills/video-prompt/)

## By language

- **EN + PT-BR + RU** (1) — [`translation-sync`](../skills/translation-sync/)
- **EN + RU** (39) — [`audio-mix-maker`](../skills/audio-mix-maker/), [`avatar-maker`](../skills/avatar-maker/), [`banner-maker`](../skills/banner-maker/), [`bg-remover`](../skills/bg-remover/), [`canon-check`](../skills/canon-check/), [`carousel-builder`](../skills/carousel-builder/), [`cold-email`](../skills/cold-email/), [`cover-maker`](../skills/cover-maker/), [`flyer-maker`](../skills/flyer-maker/), [`gif-maker`](../skills/gif-maker/), [`image-prompt`](../skills/image-prompt/), [`landing-copy`](../skills/landing-copy/), [`logo-maker`](../skills/logo-maker/), [`meme-card-maker`](../skills/meme-card-maker/), [`microcopy`](../skills/microcopy/), [`model-maker`](../skills/model-maker/), [`music-prompt`](../skills/music-prompt/), [`post-publisher`](../skills/post-publisher/), [`proposal-maker`](../skills/proposal-maker/), [`quote-card-maker`](../skills/quote-card-maker/), [`reel-builder`](../skills/reel-builder/), [`release-notes`](../skills/release-notes/), [`research-brief`](../skills/research-brief/), [`rfc-writer`](../skills/rfc-writer/), [`skills-keys`](../skills/skills-keys/), [`skills-styles`](../skills/skills-styles/), [`skills-update`](../skills/skills-update/), [`style-check`](../skills/style-check/), [`style-suggest`](../skills/style-suggest/), [`style-transfer`](../skills/style-transfer/), [`subtitle-burner`](../skills/subtitle-burner/), [`thumbnail-maker`](../skills/thumbnail-maker/), [`tone-shifter`](../skills/tone-shifter/), [`transcribe-maker`](../skills/transcribe-maker/), [`upscaler`](../skills/upscaler/), [`video-prompt`](../skills/video-prompt/), [`viral-text`](../skills/viral-text/), [`voiceover-maker`](../skills/voiceover-maker/), [`writer`](../skills/writer/)
- **EN** (1) — [`schema-maker`](../skills/schema-maker/)
- **RU** (3) — [`essay-write`](../skills/essay-write/), [`pelevin-digression`](../skills/pelevin-digression/), [`prose-edit`](../skills/prose-edit/)

<!-- END skill-index -->
