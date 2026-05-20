# Canon Term Registry

Every term that has a fixed cross-language translation lives here. Every `[TERMINOLOGY]` finding in the parity report cites a row in one of these tables.

**Rule of use:** if a term in the source file is in this registry, the target-language sides MUST match the registered translation. If the registered cell says "do not translate", the term stays in its source form across all three languages. If a term is missing from the registry, the auditor flags it as `TERM_UNREGISTERED` (warning, not blocking) and recommends adding to this file.

This file documents the **pattern** of running a canon-term registry. Specific terms are project-bound — replace the example rows with the actual coined words, branded concepts, and recurring imagery in your books. Keep the structure (tables grouped by book or by domain; "do not translate" markers; open-question lines).

---

## Shared concepts across the series (example)

For series with cross-book lore (recurring frameworks, named systems, world-building vocabulary):

| RU | EN | PT-BR |
|----|----|-------|
| _coined concept A_ | _canonical EN_ | _canonical PT-BR_ |
| _coined concept B_ | _canonical EN_ | _canonical PT-BR (open question — see below)_ |
| _do-not-translate marker_ | _stays in source form_ | _stays in source form_ |
| _proper noun (e.g. faction name)_ | _transliteration or English form, decided_ | _likewise_ |

## Book A specific (example)

| RU | EN | PT-BR |
|----|----|-------|
| _Term unique to Book A_ | _EN_ | _PT-BR_ |
| _Artifact name_ | _EN_ | _PT-BR_ |

## Book B specific (example)

| RU | EN | PT-BR |
|----|----|-------|
| _Term unique to Book B_ | _EN_ | _PT-BR_ |
| _Branded concept (do not translate)_ | _same as source_ | _same as source_ |
| _Bracketed marker_ `[VERIFIED]` | _leave in English_ | _leave in English_ |

---

## Open questions (to fix in vNext of this registry)

Terms with unresolved translation choices. When the author picks, move from here into the appropriate table above and remove the open marker.

- _Term_: keep as loanword or translate?
- _Term_: which of two candidate words catches the meaning best in EN?
- _Term_: which of two candidate words sounds more organic in PT-BR?
- _Neologism_: neologism in target, or transliteration?
- _Domain slang_: footnote-and-keep or adapt?

## How the linter uses this registry

For each source-language term in the registry, grep the corresponding EN and PT-BR chapter files for the canonical translation. Three failure modes:

1. **Drift** — EN file uses a different English term than the one registered. BLOCKING.
2. **Untranslated source word** — source-language term appears verbatim in EN file (and is not marked "do not translate"). BLOCKING.
3. **Unregistered term** — a source-language term that looks like a recurring concept (CamelCase, all-caps abbreviation, or a coined word) but is not in the registry. WARNING — recommend adding to this file.
