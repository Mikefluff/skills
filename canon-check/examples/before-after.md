# canon-check — calibration before/after pairs

3 paired examples covering the recurring canon-break shapes this skill is designed to catch: age inconsistency, weapon-name mismatch, timeline contradiction. Each pair shows the drifted manuscript passage, the corrected passage anchored back to the bible, and a Deltas subsection listing exactly what changed.

How to read these:

- The **Before** is a draft a writer might commit by accident — the prose reads fine in isolation, but contradicts the project's own canon (the bible + already-published chapters).
- The **After** is the same passage, minimally rewritten to restore canon parity. The author keeps their sentence shape and voice; only the contradicting fact moves.
- The **Deltas** name the canon source, the specific contradiction, and what was changed. `canon-check` does not produce the After — it produces the report that makes the After possible.

These pairs are calibration, not real chapter excerpts. The book/character names are placeholders.

---

## Example 1 — Character age inconsistency

**Context.** Bible §3.1 fixes Mira's age at the start of ch.12: «Мире 14 лет — отец погиб три года назад, когда ей было 11; маме сорок один.» Two earlier chapters (ch.07, ch.09) state her age consistently. A late rewrite of ch.12 accidentally re-aged her to 16, in a single sentence — and pulled forward the father's death by two years to keep the «three years ago» phrase intact.

### Before

> Мира стояла у окна и считала трещины в стекле — их было семь, как всегда, как в тот вечер, когда ей было тринадцать и отец впервые не пришёл домой. Сейчас ей шестнадцать, и трещины не изменились. Мама на кухне переставляла чашки — те же чашки, которые она расставляла пять лет назад, в неделю после похорон, когда никому не хотелось пить, но руки требовали движения.

### After

> Мира стояла у окна и считала трещины в стекле — их было семь, как всегда, как в тот вечер, когда ей было одиннадцать и отец впервые не пришёл домой. Сейчас ей четырнадцать, и трещины не изменились. Мама на кухне переставляла чашки — те же чашки, которые она расставляла три года назад, в неделю после похорон, когда никому не хотелось пить, но руки требовали движения.

**Deltas**

- «шестнадцать» → «четырнадцать» — restored to bible §3.1 «Мире 14 лет на момент ch.12»
- «тринадцать» → «одиннадцать» — bible §3.1 fixes the father's death «когда ей было 11, три года назад»; ch.07:142 and ch.09:88 both confirm «одиннадцать, три года назад»
- «пять лет назад» → «три года назад» — same source; the «five years» figure was a side-effect of pulling Mira's age to sixteen, not an independent canon revision
- Seven cracks in the window — kept (bible §3.2 lists «семь трещин» as a recurring physical detail across chapters, not an age-bound one)
- Mother's behaviour (переставляла чашки) — kept; no canon attached
- Detection class: **bible-prescribed age / temporal mismatch** (known-incidents.md cat 4); severity BLOCKING

---

## Example 2 — Weapon-name mismatch (artifact / generic-vs-canonical drift)

**Context.** Bible §4.2 (Artifacts) lists Vasily's weapon as «нож «Старшина» — складной, рукоять из карельской берёзы, лезвие 95 мм, дядин подарок на восемнадцатилетие». The artifact has been called «Старшина» by name in ch.02, ch.05, ch.11. In a draft of ch.14, the writer reaches for the gesture from memory and writes a generic «складник» — losing the canonical name. Worse: a sentence later, the blade gets described as «семисантиметровый», which contradicts the bible's 95 mm.

### Before

> Василий вытащил из заднего кармана складник, раскрыл его привычным движением — пальцы знали кнопку лучше, чем глаза. Семисантиметровое лезвие блеснуло в свете дворового фонаря. Он подержал его секунду на ладони, как держал в восемнадцать, когда отец ещё был жив и дядя ещё носил ему такие подарки.

### After

> Василий вытащил из заднего кармана «Старшину», раскрыл его привычным движением — пальцы знали кнопку лучше, чем глаза. Девяностопятимиллиметровое лезвие блеснуло в свете дворового фонаря. Он подержал его секунду на ладони, как держал в восемнадцать, когда отец ещё был жив и дядя ещё носил ему такие подарки.

**Deltas**

- «складник» → «Старшина» (в кавычках) — restored to bible §4.2 canonical artifact name; the generic descriptor appeared in ch.02:88, ch.05:201, ch.11:42 every time tied to the proper name «Старшина», so dropping the name is generic-vs-canonical drift, not a stylistic variant
- «семисантиметровое лезвие» → «девяностопятимиллиметровое лезвие» — bible §4.2 fixes the blade at 95 mm; «семисантиметровое» is a 25% miscount, not a paraphrase
- «отец ещё был жив» — kept (bible §3.1 confirms father alive at Vasily's 18; this is canon-consistent)
- «дядин подарок» implied by «дядя ещё носил такие подарки» — kept (bible §4.2 names the uncle as the gift-giver)
- Detection class: **generic-vs-canonical-name drift** (known-incidents.md cat 3) + **bible-prescribed count mismatch** (cat 4); severity BLOCKING on both

---

## Example 3 — Timeline contradiction (cross-chapter drift)

**Context.** Bible §2.4 (Timeline) records: «Анна уезжает в Тбилиси в марте 2019-го; возвращается в августе 2020-го; всего семнадцать месяцев». Chapter 04 (Анна's POV, dated «весна 2019») describes her packing. Chapter 11 (другой POV, дата «июль 2020») mentions she ещё в Тбилиси. A draft of ch.18 (set «осенью 2021», a year after her return) accidentally has her saying she was away «два с половиной года» — and dates her departure to «осень 2018», which contradicts both the bible and ch.04.

### Before

> — Когда ты уехала? — спросил он, и Анна задумалась, как задумываются над тем, что и так знают наизусть.
> — Осенью две тысячи восемнадцатого. Двадцать четвёртого сентября, если уж точно. Меня не было два с половиной года, и за это время в подъезде поменяли четыре консьержки и одну дверь, а ты так и не научился запоминать новые коды.

### After

> — Когда ты уехала? — спросил он, и Анна задумалась, как задумываются над тем, что и так знают наизусть.
> — В марте две тысячи девятнадцатого. Двадцать третьего, если уж точно. Меня не было семнадцать месяцев, и за это время в подъезде поменяли четыре консьержки и одну дверь, а ты так и не научился запоминать новые коды.

**Deltas**

- «осенью две тысячи восемнадцатого» → «в марте две тысячи девятнадцатого» — bible §2.4 fixes departure as March 2019; ch.04:12 («сборы, мартовский снег») confirms; «осень 2018» would put her in Tbilisi during a scene where she's still in the home flat (ch.03:144)
- «Двадцать четвёртого сентября» → «Двадцать третьего» — the day was never canonized exactly, but ch.04:88 dates the goodbye scene «двадцать третье число», so «двадцать четвёртое» drifts by one day from a softly-canonized detail; «сентября» dropped, the month moves to March implicitly via the previous correction
- «два с половиной года» → «семнадцать месяцев» — bible §2.4 explicit count; ch.18 scene is «осень 2021», so the gap from March 2019 to August 2020 plus the year-since-return gives 17 months away, not 30 months
- Four concierges + one door — kept (no canon attached; a colour detail, not a count tied to identity)
- Detection class: **age / temporal contradiction** (known-incidents.md cat 4, temporal sub-shape); severity BLOCKING

---

## Pattern summary

Across all 3 pairs:

1. The bible is cited by section number; the After never invents a canon source the report could not point to.
2. The minimum fix wins — one number, one name, one date. The author's voice and rhythm stay untouched.
3. Cross-chapter confirmation matters as much as the bible — if ch.04 and ch.07 already agreed, the rewrite of ch.12 is the outlier, not the canon.
4. Generic descriptors («складник», «redhead», «friend from out of town») almost always refer to an entity that has already been named in the text. Restore the name; do not invent a new one.
5. The Deltas section maps each change to a known-incidents.md detection class — that lineage is what the report would emit, and what makes the fix defensible to the author.
