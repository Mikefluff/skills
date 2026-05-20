# Параллельный фрагмент RU↔EN для translation-sync

## RU

Анна Петровна вышла из дома в 7:15 утра, держа в руке тёмно-серый зонт. Никольская улица была пуста — даже дворники ещё не вышли. До метро было около 350 метров, и она шла медленно, считая шаги.

## EN

Anna Petrovna left home at 7:15am, holding a dark grey umbrella. Nikolskaya Street was empty — even the street sweepers had not come out yet. The metro station was about 350 meters away, and she walked slowly, counting her steps.

## Деталь, которую парный аудит должен поймать

- RU: «Никольская улица» (full canonical name)
- EN: "Nikolskaya Street" (transliteration consistent)
- RU: «7:15 утра» — canonical RU time format
- EN: "7:15am" — canonical EN time format
- RU: «350 метров» — нет округления
- EN: "350 meters" — нет округления (smoothing check passes)
- RU: «тёмно-серый» (hyphenated compound)
- EN: "dark grey" (consistent compound rendering)
