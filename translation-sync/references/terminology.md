# Canon Term Registry

Every term that has a fixed cross-language translation lives here. Every `[TERMINOLOGY]` finding in the parity report cites a row in one of these tables.

**Rule of use:** if a term in the RU source is in this registry, the EN and PT-BR sides MUST match the registered translation. If the registered cell says "do not translate", the term stays in its source form across all three languages. If a term is missing from the registry, the auditor flags it as `TERM_UNREGISTERED` (warning, not blocking) and recommends adding to this file.

---

## Reality stack (shared across all three books)

| RU | EN | PT-BR |
|----|----|-------|
| стек реальности | reality stack | pilha da realidade |
| слой | layer | camada |
| рендер | render | renderização |
| подпись (субъектная) | signature | assinatura |
| якорь | anchor | âncora |
| rewrite | rewrite (loanword; **not** rebirth/transformation) | rewrite (masculine; **not** reescrita — **open question**) |
| continuity through rewrite | continuity through rewrite | continuidade através do rewrite |
| relink | relink | relink (loanword) |
| Intention Field | Intention Field | Campo de Intenção |
| морфогенез | morphogenesis | morfogênese |
| меметический паразит | memetic parasite | parasita memético |
| интегративная агентность / интегратор | integrative agency / integrator | agência integrativa / integrador |
| поток (118) | flow (118) / current (118) — **open question** | fluxo (118) |
| каузальный долг | causal debt | dívida causal |
| когнитивный конус | cognitive cone | cone cognitivo |
| дан-лаг | Dan-lag | Dan-lag (loanword) |
| субъектный инвариант | subject invariant | invariante de sujeito |
| архонт / Гептарх | Archon / Heptarch | Arconte / Heptarca |
| Ордо / Форса / Либер | Ordo / Forsa / Liber | Ordo / Forsa / Liber (Latin school names — **leave as-is**) |
| хранитель инварианта | invariant keeper | guardião do invariante |
| падший бессмертный | fallen immortal | imortal caído |

## EA (Era of Architects) specific

| RU | EN | PT-BR |
|----|----|-------|
| Архитектор | Architect | Arquiteto |
| Архитектура (модель) | Architecture | Arquitetura |
| Монолит | Monolith | Monolito |
| Альфа-партнёры | Alpha partners | parceiros Alfa |
| Триада | Triad | Tríade |
| Дельта | Delta | Delta |
| макро-контакт | macro-contact | macro-contato |
| Хроники стека | Stack Chronicles | Crônicas da pilha |
| Времяход | Timewalk | Caminhada no tempo / Timewalk — **open question** |
| Книга Жизни | Book of Life | Livro da Vida |
| синдром БМЯ («бедный маленький Я») | PLM syndrome («poor little me») | síndrome do PEM («pobre pequeno eu») |
| Институт Пробуждения Населения | Institute of Population Awakening (ИнПроб → InProb) | Instituto do Despertar Populacional |
| Архитектор-1 | Architect-1 | Arquiteto-1 |
| Росподпись | RosSignature | RusAssinatura — **open question** |
| приложение «Подпись» | Signature app | aplicativo Assinatura |
| Эхо-1 | Echo-1 | Eco-1 |

## HC (Heavenly Code) specific

| RU | EN | PT-BR |
|----|----|-------|
| Pointer Architecture | Pointer Architecture (proper noun, **do not translate**) | Pointer Architecture |
| указатель | pointer | apontador |
| разыменование | dereferencing | desreferenciamento |
| конфликт указателей | pointer conflict | conflito de apontadores |
| архив (тёмная материя) | archive | arquivo |
| трёхуровневая достоверность | three-tier confidence | confiança em três níveis |
| [VERIFIED] / [HYPOTHESIS] / [PERSONAL] | [VERIFIED] / [HYPOTHESIS] / [PERSONAL] _(leave in English)_ | [VERIFIED] / [HYPOTHESIS] / [PERSONAL] |

---

## Open questions (to fix in v1.1 of this registry)

These terms have unresolved translation choices. When the author picks, move from here into the appropriate table above and remove the open marker.

- `rewrite` in PT-BR: keep as `rewrite` (loanword) or translate as `reescrita`?
- `flow 118` vs `current 118` in EN for `поток 118` — which word catches the integrator more precisely?
- `Timewalk` vs `Caminhada no tempo` in PT-BR — which sounds more organic?
- `Росподпись` in PT-BR (`RusAssinatura`?) — neologism or transliteration?
- Artyom's military slang (`двухсотый`, `трёхсотый`) — footnote or adapt?

## How the linter uses this registry

For each RU term in the registry, grep the corresponding EN and PT-BR chapter files for the canonical translation. Three failure modes:

1. **Drift** — EN file uses a different English term than the one registered. BLOCKING.
2. **Untranslated source word** — RU term appears verbatim in EN file (and is not marked "do not translate"). BLOCKING.
3. **Unregistered term** — RU term that looks like a recurring concept (CamelCase, all-caps abbreviation, or a coined word) but is not in the registry. WARNING — recommend adding to this file.
