# Banned patterns — marketing hype

Shared anti-patterns across `cold-email`, `landing-copy`, and `release-notes`.
The base linter catches the regex-detectable subset under `MARKETING_HYPE`
(see `skills/writer/scripts/lint.py`).

These adjectives are red flags because they make claims the reader cannot verify
without proof. Replace each with a **specific number, named customer, or concrete
behavior**.

## EN — hype superlatives (catalogue)

| Banned | Replace with |
| --- | --- |
| revolutionary | named change ("replaces N hours of manual triage with a single click") |
| game-changing | specific delta ("cut review-time 60% at Stripe") |
| world-class | named team or comparable ("built by people who shipped X at Y") |
| industry-leading | data point ("ranked #1 in GZ benchmark, 2025") |
| cutting-edge | named technique ("uses constraint propagation, not LLMs") |
| best-in-class | benchmark ("p50 latency 12ms vs industry avg 84ms") |
| groundbreaking | what it actually breaks ("first to support concurrent multi-doc edit") |
| next-generation | what generation, what's different ("v2: rewritten in Rust, 14× throughput") |
| state-of-the-art | citation ("matches ICML 2025 baseline on Y dataset") |
| unparalleled | comparable competitor + delta |
| unmatched | comparable competitor + delta |
| transformative | the literal transformation, with numbers |
| disruptive | the literal disruption, with names |
| innovative | the literal innovation, with mechanism |

## RU — гипер-прилагательные

| Banned | Replace with |
| --- | --- |
| революционный (вне AI_INTENSIFIER NP) | конкретное изменение с цифрами |
| прорывной | named delta |
| инновационный | в чём именно инновация (механизм) |
| передовой | сравнение с конкурентом |
| уникальный | что именно не повторяется |
| лидер отрасли | benchmark / numbers |
| мирового класса | named comparable |
| беспрецедентный | данные |

## How to spot in your draft

1. **Adjective without measurable substance.** "A revolutionary platform" — revolutionary against what baseline? Strip the adjective; lead with the specific behavior or number.
2. **Synonym stacking.** "Revolutionary, game-changing, industry-leading solution" — three hype words means you don't have one real claim. Pick one and prove it.
3. **Marketing copy that opens with hype.** First sentence with `revolutionary` is almost always a signal the author doesn't know the differentiator yet. Rewrite the opening as a verb describing what the product does, not an adjective describing how impressive it is.

## What's NOT banned

These words **are fine** in technical contexts where they refer to a specific concept:

- "revolutionary" in a history paper (genuine revolution as historical event)
- "innovative" in a patent abstract (the legally-defined innovation)
- "best-in-class" inside a benchmark paragraph that *names the class and the comparison*

The base linter catches them anywhere; humans should still allow them in those narrow contexts.
