# Style index — visual-prompt-library/styles/

Catalog of available styles. The library is extensible — drop a new `<slug>.md` file here (see [`_schema.md`](_schema.md)) and add a one-line entry below.

Auto-pick matrix: [`_auto-pick.md`](_auto-pick.md). System prompt loader: [`../system-prompt.md`](../system-prompt.md).

| Slug | Name | When to use |
|---|---|---|
| [biotech](biotech.md) | BIOTECH / ORGANIC | Psychology, neuroscience, habits, internal processes, health, growth, transformation, medicine, biology |
| [cyber-noir](cyber-noir.md) | CYBER-NOIR / DIGITAL | Technology, AI, algorithms, systems, data, hacking, security, surveillance |
| [brutalist](brutalist.md) | BRUTALIST / CONCRETE | Hard truths, criticism, breaking illusions, power, business reality, no ornamentation |
| [vaporwave](vaporwave.md) | VAPORWAVE / RETRO-FUTURE | Nostalgia, retro analysis, irony, aesthetic, 80s/90s, kitsch |
| [military](military.md) | MILITARY / TACTICAL | Strategy, planning, discipline, operations, competition, classified data |
| [scientific](scientific.md) | SCIENTIFIC / ACADEMIC | Research, data, statistics, evidence, methodology, education |
| [streetwear](streetwear.md) | STREETWEAR / HYPE | Trends, drops, hype, urgency, limited editions, consumer culture |
| [art-deco](art-deco.md) | ART DECO / GATSBY | Luxury, status, timeless, elite, classic, money, success |
| [blueprint](blueprint.md) | BLUEPRINT / TECHNICAL | Processes, instructions, how-to, solution architecture, engineering |
| [grunge](grunge.md) | GRUNGE / NEWSPAPER | Exposés, scandals, journalism, raw truth, underground, anti-establishment |
| [glamour](glamour.md) | GLAMOUR / GLOSSY | Fashion, beauty, lifestyle, premium brand, celebrities, glossy magazines |
| [nature](nature.md) | NATURE / ORGANIC | Ecology, nature, healthy living, sustainability, wellness, organic products |
| [adventure](adventure.md) | ADVENTURE / OUTDOOR | Adventures, hiking, outdoor sports, expeditions, mountains, ocean |
| [nordic-minimal](nordic-minimal.md) | NORDIC MINIMAL / QUIET-PREMIUM | Premium B2B, Scandinavian-brand content, mindful-tech communication, considered editorial, quiet luxury |
| [deconstructed-luxury-expose](deconstructed-luxury-expose.md) | DECONSTRUCTED LUXURY / EXPOSÉ | Red-flag pattern recognition, debunking, exposés of fake gurus / lifestyle-as-credential, critical content about luxury-bait sales |
| [clinical-debunk](clinical-debunk.md) | CLINICAL DEBUNK / MISDIAGNOSIS | Exposing manipulation tactics, debunking pseudo-therapy / coaching gaslighting, diagnostic takedowns of blame-shifting language |
| [vip-massovka](vip-massovka.md) | VIP / МАССОВКА (EXCLUSIVITY DEFACED) | Exposing fake exclusivity marketing, "продали доступ к окружению" critiques, batch-as-VIP unmasking, mass-membership marketed as elite |
| [applause-ledger](applause-ledger.md) | APPLAUSE LEDGER (EVIDENCE GAP) | Exposing testimonial-as-proof tactic, "восторгов много а цифр нет" critiques, atmosphere vs result contrast, mass-testimonial debunk |

18 styles — 13 ported from figma's SEEDREAM_SYSTEM_PROMPT (`/Users/mikefluff/Documents/figma/app/lib/carousel/slidePrompts/systemPrompt.js`). Extend by adding more.

## Adding a new style — quick checklist

1. Create `<your-slug>.md` with the frontmatter from [`_schema.md`](_schema.md).
2. Add a row above (alphabetical or thematic — your call).
3. If it should auto-pick on certain topic signals, add a row to [`_auto-pick.md`](_auto-pick.md).
4. No code changes anywhere else — every visual skill picks it up.

## Resolution order in skills

When a visual skill receives a style request:

1. `--style <slug>` → load `styles/<slug>.md`. Error if not found.
2. `--style custom "<desc>"` → skip library entirely; pass `<desc>` verbatim as `Visual style` in the user message.
3. `--style auto` (default) → consult `_auto-pick.md` matrix → resolve to a slug → load that file.
4. Library style + customStyle modifier (e.g. `--style art-deco --style-mod "but with the character on every slide"`) → load library entry + append modifier to the `Visual style` field.
