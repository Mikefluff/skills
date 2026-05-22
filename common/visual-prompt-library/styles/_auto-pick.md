# Style auto-pick matrix

When the user gives `--style auto` (or no style flag at all), the skill consults this matrix to resolve a slug based on the topic / brief.

## How to read

Run through rows in order. Pick the first row whose signal terms match the topic / brief. If multiple match, prefer the higher row (the table is hand-ranked by confidence). If nothing matches, fall back to the default at the bottom.

| Signal in topic / brief | Style slug |
|---|---|
| AI / tech / algorithms / data / security / surveillance / hacking | [cyber-noir](cyber-noir.md) |
| Money / luxury / status / elite / wealth-building / high-net-worth | [art-deco](art-deco.md) |
| Beauty / fashion / lifestyle / cosmetics / red-carpet / celebrity | [glamour](glamour.md) |
| Nature / ecology / wellness / mindfulness / organic / botanical | [nature](nature.md) |
| Adventure / outdoor sports / travel / expedition / mountains | [adventure](adventure.md) |
| Trends / drops / hype / urgency / streetwear / sneakers / sneaker culture | [streetwear](streetwear.md) |
| Research / education / data / evidence / academic / journal / paper / manifesto | [scientific](scientific.md) |
| How-to / process / architecture / engineering / blueprints / mechanics | [blueprint](blueprint.md) |
| Strategy / competition / planning / tactics / intelligence / operations | [military](military.md) |
| Hard truths / criticism / power / civic-architecture / no-ornament | [brutalist](brutalist.md) |
| Exposé / journalism / underground / punk / conspiracy / scandal | [grunge](grunge.md) |
| Retro / nostalgia / irony / 80s-90s / kitsch / vaporwave-aesthetic | [vaporwave](vaporwave.md) |
| Psychology / health / growth / habits / neuroscience / inner-process | [biotech](biotech.md) |
| Premium B2B / Scandinavian brand / mindful tech / considered editorial / quiet luxury / design-led communication | [nordic-minimal](nordic-minimal.md) |
| Exposé / red-flag / debunking / scam-detection / cult-of-personality / lifestyle-vs-substance / fake-guru-critique / признаки X-cult | [deconstructed-luxury-expose](deconstructed-luxury-expose.md) |
| Clinical exposé / debunking pseudo-therapy / manipulation tactics / blame-shifting / gaslighting in coaching / fake-diagnosis / MLM-debunk / "обесценивание сложности" | [clinical-debunk](clinical-debunk.md) |
| Fake exclusivity / "продали доступ к окружению" / batch-as-VIP / MLM buyer-chat / mass-membership as elite / "сильное окружение" critique / Like Центр / БМ-style debunk | [vip-massovka](vip-massovka.md) |

## Default fallback

If no signal matches (truly generic / ambiguous topic), default to [`scientific`](scientific.md) — safe, credible, restrained, works for almost anything that doesn't already lean strongly into another style.

## Extending the matrix

When you add a new style to the library, optionally add a row above with the topic signals that should auto-resolve to your style. Order matters — higher rows win on ties.
