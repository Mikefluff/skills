# Instrumental tags — anchoring genre by instrument

Instrument choice does more genre-anchoring work than the genre word itself. `[Pedal Steel Guitar]` says "country" without writing "country". `[808 Sub Bass]` says "trap" without writing "trap". Combine carefully — instruments from incompatible genres muddy the result.

Base catalog lives in [`meta-tags.md`](./meta-tags.md#4-instrumental). This file is the deep dive.

---

## Why instrumental tags matter

The model maps each instrument tag to a learned set of genre / era / production conventions. So:

- `[Hammond Organ]` brings 60s soul / 70s rock / gospel baggage.
- `[808 Sub Bass]` brings modern trap / drill baggage.
- `[Pedal Steel Guitar]` brings country / Americana baggage.

Stack 3-4 instruments inside the same genre lane and the model converges. Stack across lanes and you either get fusion (intentional) or sludge (unintentional).

---

## Drums and percussion

| Tag | Sound |
|---|---|
| `[Acoustic Kit]` | Live drum kit, room mic'd |
| `[808 Kick]` | Long sub-heavy kick, trap signature |
| `[808 Sub Bass]` | Pitched 808, bass-line role |
| `[Trap Hi-Hats]` | Rolled hats, 1/16 + 1/32 |
| `[Trap Triplet Hi-Hats]` | Triplet rolls, drill / Migos signature |
| `[Drill Hi-Hats]` | Syncopated, off-grid |
| `[Slidey 808]` | Pitch-bent 808, UK drill signature |
| `[Linn Drum]` | 80s digital kit, Prince / pop staple |
| `[Drum Machine]` | Generic programmed kit |
| `[Live Drums]` | Performed, human timing |
| `[Gated Reverb Drums]` | 80s big snare with gated reverb tail |
| `[Half-Time Drums]` | Snare on 3 instead of 2 and 4 |
| `[Double-Time Drums]` | Twice the snare density |
| `[Polyrhythmic Percussion]` | Two competing meters |
| `[Hand Drums]` | Generic world hand-percussion |
| `[Tabla]` | Indian classical drums |
| `[Taiko]` | Japanese ensemble drums |
| `[Bongo]` | Latin pair hand drums |

---

## Bass

| Tag | Sound |
|---|---|
| `[Sub Bass]` | Pure low-frequency sine, club-system focus |
| `[Synth Bass]` | Generic synth low-end |
| `[Sidechained Synth Bass]` | Pumped against the kick, EDM signature |
| `[Slap Bass]` | Funk / 80s pop signature |
| `[Fretless Bass]` | Smooth, vocal-like — jazz / soft rock |
| `[Walking Bass]` | Stepwise quarter-notes, jazz / blues |
| `[Acoustic Upright Bass]` | Jazz / folk / bluegrass |
| `[Distorted Bass]` | Rock / industrial |
| `[Reese Bass]` | Detuned-saw bass, drum-and-bass signature |

---

## Guitars

| Tag | Sound |
|---|---|
| `[Acoustic Guitar]` | Generic steel-string |
| `[Clean Electric]` | Undriven electric, jazz / indie clean |
| `[Distorted Power Chords]` | Rock baseline, 5-chords |
| `[Jangly 60s Guitar]` | Rickenbacker chime, Beatles / Byrds |
| `[Surf Guitar]` | Tremolo + spring reverb, Dick Dale |
| `[Pedal Steel Guitar]` | Country signature, sliding sustain |
| `[12-String]` | Doubled-string strum, folk-rock |
| `[Nylon Classical]` | Spanish / classical |
| `[Slide Guitar]` | Blues / Americana glissando |
| `[Wah Wah Guitar]` | Filter-swept lead, 70s funk / rock |
| `[Tremolo Picked]` | Rapid single-note repetition |
| `[Whammy Bar Bends]` | Pitch-bent rock lead |
| `[Heavy Distortion]` | Metal / hard rock baseline |

---

## Keys

| Tag | Sound |
|---|---|
| `[Grand Piano]` | Concert grand, classical / pop |
| `[Upright Piano]` | Smaller piano, intimate |
| `[Honky-Tonk Piano]` | Detuned saloon piano |
| `[Rhodes]` | Electric piano, soul / jazz / lofi |
| `[Wurlitzer]` | Electric piano, lighter than Rhodes, rock / soul |
| `[Hammond Organ]` | B3 organ family, soul / rock / gospel |
| `[B3 Organ]` | Specifically Hammond B3 with Leslie |
| `[Mellotron]` | Tape-replay strings/flutes, prog rock |
| `[Synth Pad]` | Sustained synth chord bed |
| `[Lead Synth]` | Single-line synth melody |
| `[Analog Synth]` | Warm subtractive, Moog / Prophet feel |
| `[FM Bell Synth]` | DX7 bells, 80s pop |
| `[Pluck Synth]` | Short percussive synth, modern pop |
| `[Saw Lead]` | Bright sawtooth lead |
| `[Supersaw]` | Stacked detuned saws, trance / EDM |
| `[Arp]` | Arpeggiator pattern |

---

## Strings

| Tag | Sound |
|---|---|
| `[Orchestral Strings]` | Full string section |
| `[String Quartet]` | Two violins, viola, cello |
| `[Cinematic Strings Rise]` | Crescendo string swell |
| `[Pizzicato]` | Plucked strings |
| `[Solo Violin]` | Single violin |
| `[Solo Cello]` | Single cello |

---

## Brass / wind

| Tag | Sound |
|---|---|
| `[Brass Section]` | Trumpets + trombones + saxes ensemble |
| `[Trumpet]` | Solo trumpet |
| `[Saxophone Solo]` | Lead sax, tenor or alto |
| `[Flute]` | Solo flute |
| `[Clarinet]` | Solo clarinet |
| `[French Horn]` | Solo or section, orchestral |

---

## Ethnic / world

| Tag | Region |
|---|---|
| `[Sitar]` | India |
| `[Oud]` | Middle East |
| `[Erhu]` | China |
| `[Shamisen]` | Japan |
| `[Bagpipes]` | Scotland / Ireland |
| `[Accordion]` | French chanson / polka / cumbia |
| `[Mandolin]` | Bluegrass / Italian folk |
| `[Banjo]` | Bluegrass / country / folk |

---

## Musical FX & risers

These are MUSICAL transitions performed by instruments, distinct from production FX in [`mix-production-tags.md`](./mix-production-tags.md).

| Tag | Effect |
|---|---|
| `[White Noise Riser]` | Filtered noise ramp into a section |
| `[Layered White Noise Riser]` | Multiple noise risers stacked |
| `[Reverse Cymbal]` | Cymbal played backwards as a swell |
| `[Vinyl Crackle]` | Static / pops layer for lofi |
| `[Sub Drop Impact]` | Sub-frequency boom on the downbeat |
| `[Tape Stop]` | Pitch-and-speed dropoff like a tape deck powering off |
| `[Glitch Edit]` | Stutter-repeat edits on a beat |
| `[Strings Rise]` | Bowed-strings crescendo |

---

## Anti-patterns

- **5+ lead instruments in one stack.** `[Guitar Solo | Piano Solo | Saxophone Solo | Trumpet | Sitar]` — they fight for the same frequency real estate. Pick 1-2 lead, rest support.
- **Cross-genre instruments without intent.** `[Pedal Steel Guitar]` + `[808 Sub Bass]` reads as "country trap fusion" — fine if deliberate, sludgy if accidental.
- **Inventing instruments.** `[Quantum Synth]`, `[Bass Cathedral]` — silently ignored. Stick to canonical names.
- **Brand-named patches.** "Korg M1 piano", "Yamaha CP70" — works inconsistently. Use the family name (`[FM Bell Synth]`, `[Electric Piano]`) instead.
- **Multiple bass tags.** `[Sub Bass | 808 Sub Bass | Reese Bass]` — model averages and you lose all three signatures. Pick one.
- **Too many percussion layers.** Drum + 808 + tabla + bongo + hand drums — rhythmic soup. Cap at 2-3 percussion elements.

---

## Genre → instrument quick picker

| Genre | Default instrument stack |
|---|---|
| Modern pop | `[Acoustic Kit] [Synth Bass] [Pluck Synth] [Stacked Harmonies]` |
| Trap | `[808 Kick] [808 Sub Bass] [Trap Hi-Hats] [Pluck Synth]` |
| Drill | `[Slidey 808] [Drill Hi-Hats] [Dark Piano]` |
| 80s synthwave | `[Linn Drum] [FM Bell Synth] [Analog Synth] [Gated Reverb Drums]` |
| Country | `[Acoustic Kit] [Pedal Steel Guitar] [Acoustic Guitar] [Fiddle]` |
| Gospel | `[Live Drums] [Hammond Organ] [Grand Piano] [Gospel Choir]` |
| Indie folk | `[Acoustic Guitar] [Upright Piano] [Brushed Drums] [Solo Cello]` |
| EDM festival | `[Acoustic Kit] [Sidechained Synth Bass] [Supersaw] [White Noise Riser]` |
| Lofi hip-hop | `[Drum Machine] [Rhodes] [Vinyl Crackle] [Synth Pad]` |
| K-pop | `[808 Kick] [Pluck Synth] [Supersaw] [Stacked Harmonies] [Brass Section]` |
| 60s Motown | `[Live Drums] [Walking Bass] [Tambourine] [Brass Section]` |
| Phonk | `[808 Sub Bass] [Cowbell] [Distorted Bass] [Memphis Chops]` |

---

## RU терминология

| RU | EN tag |
|---|---|
| Акустический кит / живые барабаны | `[Acoustic Kit]` / `[Live Drums]` |
| Бочка / kick | `[808 Kick]` |
| Хэты / трэп-хэты | `[Trap Hi-Hats]` / `[Trap Triplet Hi-Hats]` |
| Гейтед-реверб (барабаны) | `[Gated Reverb Drums]` |
| Хаф-тайм / двойной темп | `[Half-Time Drums]` / `[Double-Time Drums]` |
| Сабовый бас / 808 | `[Sub Bass]` / `[808 Sub Bass]` |
| Синт-бас | `[Synth Bass]` |
| Слэп-бас | `[Slap Bass]` |
| Безладовый бас | `[Fretless Bass]` |
| Walking bass / шагающий бас | `[Walking Bass]` |
| Акустическая гитара | `[Acoustic Guitar]` |
| Чистая электрогитара | `[Clean Electric]` |
| Перегруз / power chords | `[Distorted Power Chords]` / `[Heavy Distortion]` |
| Слайд-гитара | `[Slide Guitar]` |
| Педальная сталь | `[Pedal Steel Guitar]` |
| Рояль | `[Grand Piano]` |
| Электропиано (Rhodes) | `[Rhodes]` |
| Хаммонд / орган | `[Hammond Organ]` / `[B3 Organ]` |
| Аналоговый синт | `[Analog Synth]` |
| Pad / синт-подложка | `[Synth Pad]` |
| Supersaw / суперсо | `[Supersaw]` |
| Струнная секция | `[Orchestral Strings]` |
| Пиццикато | `[Pizzicato]` |
| Дудуки и духовые | `[Brass Section]` |
| Сакс-соло | `[Saxophone Solo]` |
| Аккордеон | `[Accordion]` |
| Банджо / мандолина | `[Banjo]` / `[Mandolin]` |

---

## Cross-links

- Full tag catalog: [`meta-tags.md`](./meta-tags.md)
- Vocal arrangements layered with instruments: [`vocal-tags.md`](./vocal-tags.md)
- Mix processing for instruments: [`mix-production-tags.md`](./mix-production-tags.md)
