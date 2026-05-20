# What Must NOT Be Smoothed

Categories that must remain specific in EN and PT-BR translations. The single most common drift in machine and human translation is replacing a concrete detail with a "smoother" approximation. The series rejects this on principle.

Every `[NO_SMOOTHING]` finding in the parity report cites a row here.

---

## Numbers, durations, dimensions

**Rule:** every quantity is literal. No rounding, no "approximately", no "a few".

| BEFORE (drift) | AFTER (canon) |
|-----------------|----------------|
| `under a second` | `900 milliseconds` |
| `quase um segundo` | `900 milissegundos` |
| `a couple of weeks` | `17 days` |
| `algumas semanas` | `17 dias` |
| `several cracks` | `eleven cracks` |
| `algumas rachaduras` | `onze rachaduras` |
| `roughly 0.4` | `R² = 0.41` (kept verbatim) |
| `a huge audience` | `three hundred thousand subscribers` |
| `300K subscribers` | `three hundred thousand subscribers` _(prose form — see [typography.md](typography.md))_ |
| `uma grande audiência` | `trezentos mil assinantes` |

**Particular failure mode to flag:** `300K` is wrong twice — first because it abbreviates a concrete number, second because it is digits in prose where the rule is words-spelled-out.

## Exact years

| BEFORE | AFTER |
|---------|--------|
| `back in the seventies` | `in 1973` |
| `recently` | `in 2024` |
| `nos anos setenta` | `em 1973` |

If the RU has a specific year, the EN and PT-BR must carry the same year. "Decades ago" is not an acceptable substitute for "in 1986".

## Specific street names, districts, locations

Real locations stay specific. Transliteration + first-mention footnote per [names-and-realia.md](names-and-realia.md), but never replaced with a generic.

| BEFORE | AFTER |
|---------|--------|
| `a Moscow neighborhood` | `Khamovniki` |
| `a building in central Moscow` | `Lubyanka` |
| `a tower in Moscow` | `Shukhov Tower` |
| `Trolleybus 15` → `the trolleybus` | `Trolleybus 15` (specific number preserved) |
| `algum bairro de Moscou` | `Khamovniki` |

## Specific brand names

Real brands stay real. No generic substitutes.

| BEFORE | AFTER |
|---------|--------|
| `a Russian bank` | `Tinkoff` |
| `a Russian e-gov portal` | `Gosuslugi` |
| `um banco russo` | `Tinkoff` |

## Specific drug names

Pharmacological detail is canon-bearing in the books — characters take specific drugs for specific reasons.

| BEFORE | AFTER |
|---------|--------|
| `a sedative` | `Phenazepam` |
| `an antacid` | `Gastroshield` |
| `um calmante` | `Phenazepam` _(with footnote on first mention)_ |

## Idioms — equivalent yes, smoothed no

Idioms get equivalent idioms, not smoothed-out paraphrases.

| RU | EN (correct equivalent) | EN (wrong — smoothing) |
|-----|--------------------------|------------------------|
| закрыть гештальт | close the loop | resolve the situation |
| не мытьём так катаньем | by hook or by crook | one way or another |

| RU | PT-BR (correct equivalent) | PT-BR (wrong — smoothing) |
|-----|------------------------------|-----------------------------|
| не мытьём так катаньем | por bem ou por mal | de uma forma ou de outra |

**Exception:** if the idiom carries a **concrete image** important to the scene (e.g. a fish-related idiom in a fishing scene), keep the literal image and add a brief in-line gloss instead of swapping it.

## Formulas, equations, scientific notation

Formulas stay byte-identical across languages. No re-notation.

| BEFORE (drift) | AFTER (canon) |
|-----------------|----------------|
| `the formula H equals the negative sum...` | `H = -\sum p(x) \log_2 p(x)` |
| `kT log 2` | `kT \ln 2` (specific base preserved) |

## Journal names

Scientific journals carry English names everywhere, including RU. No transliteration.

| BEFORE (drift in RU/PT-BR) | AFTER (canon) |
|------------------------------|----------------|
| `«Природа»` for `Nature` | `Nature` |
| `«Физический обзор»` | `Physical Review` |
| `Fronteiras em Física` | `Frontiers in Physics` |

## What "smoothing" looks like in practice — three diagnostic questions

When auditing a translated paragraph, ask:

1. **Did a number become a vibe?** ("900 ms" → "fast")
2. **Did a name become a category?** ("Tinkoff" → "the bank")
3. **Did a duration become a feeling?** ("17 days" → "a while")

If yes to any: BLOCKING. The reader gives up specifics for a reason — the author is making a precise claim. Smoothing the claim is mistranslation, not stylistic adaptation.

## What is NOT smoothing — legitimate adaptations

These changes are fine and should NOT be flagged:

- EN compactness: a Russian compound sentence becomes two EN sentences if the meaning is preserved. (EN is ~30% more compact than RU.)
- PT-BR mellowness: a sharp RU staccato gets one more comma in PT-BR if the rhythm fits. (PT-BR has longer words.)
- Equivalent idiom for equivalent idiom (see above).
- Word order change required by target-language syntax.

The line: **adapt rhythm, preserve facts**. Numbers, dates, names, brands, drugs, formulas, journals — never adapted, only translated.
