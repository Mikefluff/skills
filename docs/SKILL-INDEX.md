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
| [`writer`](../writer/) | editing | ru / en |

### Wrappers

| Skill | Tags | Languages |
| --- | --- | --- |
| [`viral-text`](../viral-text/) | marketing, social, generation | ru / en |
| [`prose-edit`](../prose-edit/) | fiction, editing | ru |
| [`essay-write`](../essay-write/) | non-fiction, generation | ru |
| [`pelevin-digression`](../pelevin-digression/) | fiction, non-fiction, generation | ru |
| [`tone-shifter`](../tone-shifter/) | editing | en / ru |
| [`cold-email`](../cold-email/) | outreach, generation | en / ru |
| [`image-prompt`](../image-prompt/) | visual, generation | en / ru |
| [`video-prompt`](../video-prompt/) | visual, generation | en / ru |
| [`music-prompt`](../music-prompt/) | audio, generation | en / ru |
| [`microcopy`](../microcopy/) | ux-copy, product, generation | en / ru |
| [`release-notes`](../release-notes/) | product, tech-docs, generation | en / ru |
| [`rfc-writer`](../rfc-writer/) | tech-docs, generation | en / ru |
| [`landing-copy`](../landing-copy/) | marketing, generation | en / ru |
| [`bg-remover`](../bg-remover/) | visual, editing | en / ru |
| [`voiceover-maker`](../voiceover-maker/) | audio, generation | en / ru |
| [`subtitle-burner`](../subtitle-burner/) | visual, editing | en / ru |
| [`gif-maker`](../gif-maker/) | visual, generation, editing | en / ru |
| [`upscaler`](../upscaler/) | visual, editing | en / ru |
| [`audio-mix-maker`](../audio-mix-maker/) | audio, editing | en / ru |
| [`style-transfer`](../style-transfer/) | visual, editing, generation | en / ru |
| [`transcribe-maker`](../transcribe-maker/) | audio, editing | en / ru |

### Linters (read-only)

| Skill | Tags | Languages |
| --- | --- | --- |
| [`style-check`](../style-check/) | audit, editing | ru / en |
| [`translation-sync`](../translation-sync/) | translation, audit | ru / en / pt-br |
| [`canon-check`](../canon-check/) | fiction, audit | ru / en |

### Meta

| Skill | Tags | Languages |
| --- | --- | --- |
| [`skills-update`](../skills-update/) | ops | en / ru |
| [`skills-keys`](../skills-keys/) | ops | en / ru |
| [`skills-styles`](../skills-styles/) | ops, visual | en / ru |

## By domain

- **audio** — [`music-prompt`](../music-prompt/), [`voiceover-maker`](../voiceover-maker/), [`reel-builder`](../reel-builder/), [`audio-mix-maker`](../audio-mix-maker/), [`transcribe-maker`](../transcribe-maker/)
- **fiction** — [`prose-edit`](../prose-edit/), [`canon-check`](../canon-check/), [`pelevin-digression`](../pelevin-digression/)
- **marketing** — [`viral-text`](../viral-text/), [`landing-copy`](../landing-copy/), [`carousel-builder`](../carousel-builder/), [`cover-maker`](../cover-maker/), [`thumbnail-maker`](../thumbnail-maker/), [`flyer-maker`](../flyer-maker/), [`reel-builder`](../reel-builder/), [`logo-maker`](../logo-maker/), [`quote-card-maker`](../quote-card-maker/), [`banner-maker`](../banner-maker/), [`meme-card-maker`](../meme-card-maker/), [`proposal-maker`](../proposal-maker/), [`post-publisher`](../post-publisher/)
- **non-fiction** — [`essay-write`](../essay-write/), [`pelevin-digression`](../pelevin-digression/)
- **outreach** — [`cold-email`](../cold-email/)
- **product** — [`microcopy`](../microcopy/), [`release-notes`](../release-notes/)
- **research** — [`research-brief`](../research-brief/)
- **social** — [`viral-text`](../viral-text/), [`post-publisher`](../post-publisher/)
- **tech-docs** — [`release-notes`](../release-notes/), [`rfc-writer`](../rfc-writer/)
- **ux-copy** — [`microcopy`](../microcopy/)
- **visual** — [`skills-styles`](../skills-styles/), [`image-prompt`](../image-prompt/), [`video-prompt`](../video-prompt/), [`carousel-builder`](../carousel-builder/), [`cover-maker`](../cover-maker/), [`thumbnail-maker`](../thumbnail-maker/), [`bg-remover`](../bg-remover/), [`avatar-maker`](../avatar-maker/), [`subtitle-burner`](../subtitle-burner/), [`flyer-maker`](../flyer-maker/), [`reel-builder`](../reel-builder/), [`logo-maker`](../logo-maker/), [`quote-card-maker`](../quote-card-maker/), [`gif-maker`](../gif-maker/), [`banner-maker`](../banner-maker/), [`meme-card-maker`](../meme-card-maker/), [`upscaler`](../upscaler/), [`style-transfer`](../style-transfer/), [`style-suggest`](../style-suggest/)

## By language

- **EN + PT-BR + RU** (1) — [`translation-sync`](../translation-sync/)
- **EN + RU** (38) — [`writer`](../writer/), [`viral-text`](../viral-text/), [`style-check`](../style-check/), [`canon-check`](../canon-check/), [`skills-update`](../skills-update/), [`skills-keys`](../skills-keys/), [`skills-styles`](../skills-styles/), [`tone-shifter`](../tone-shifter/), [`cold-email`](../cold-email/), [`image-prompt`](../image-prompt/), [`video-prompt`](../video-prompt/), [`music-prompt`](../music-prompt/), [`microcopy`](../microcopy/), [`release-notes`](../release-notes/), [`rfc-writer`](../rfc-writer/), [`landing-copy`](../landing-copy/), [`research-brief`](../research-brief/), [`carousel-builder`](../carousel-builder/), [`cover-maker`](../cover-maker/), [`thumbnail-maker`](../thumbnail-maker/), [`bg-remover`](../bg-remover/), [`avatar-maker`](../avatar-maker/), [`voiceover-maker`](../voiceover-maker/), [`subtitle-burner`](../subtitle-burner/), [`flyer-maker`](../flyer-maker/), [`reel-builder`](../reel-builder/), [`logo-maker`](../logo-maker/), [`quote-card-maker`](../quote-card-maker/), [`gif-maker`](../gif-maker/), [`banner-maker`](../banner-maker/), [`meme-card-maker`](../meme-card-maker/), [`upscaler`](../upscaler/), [`audio-mix-maker`](../audio-mix-maker/), [`style-transfer`](../style-transfer/), [`transcribe-maker`](../transcribe-maker/), [`style-suggest`](../style-suggest/), [`proposal-maker`](../proposal-maker/), [`post-publisher`](../post-publisher/)
- **RU** (3) — [`prose-edit`](../prose-edit/), [`essay-write`](../essay-write/), [`pelevin-digression`](../pelevin-digression/)

<!-- END skill-index -->
