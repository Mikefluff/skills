# Forbidden substitutions — Layer 3 guard

Slop replaced by kindred slop is still slop.

This is the failure mode that makes a cleaning pass *look* successful while changing nothing. The mechanism is mechanical: a repetition penalty pushes the model toward synonym substitution instead of deletion. Asked to remove «ключевой», it reaches for «важнейший». Asked to kill «не только X, но и Y», it produces «как X, так и Y» — same contrast, same cadence, new packaging.

Resist it. The default treatment for slop is **deletion**, not translation.

---

## Treatment hierarchy

Apply in order. Only fall through when the level above genuinely cannot work.

1. **Delete.** Most slop is water; after removal nothing is lost. Try this first, always.
2. **Replace with a fact or a concrete detail.** «Прочный» → «выдерживает 150 кг». An abstraction → an example.
   **The fact must come from the original or from context you were given.** An invented verifiable fact is worse than the slop it replaced — it is a lie inside someone else's text. If there is no fact available, delete the construction and ask for the missing number in the summary («если места действительно ограничены, верните с числом»).
3. **Rewrite simpler.** Shorter, more direct, with a conversational word.

A synonym is not a treatment. It is level zero, and it does not count.

---

## The table

| Was | Not allowed | Treatment |
|---|---|---|
| «не только X, но и Y» | «как X, так и Y», «и X, и Y», «X, а также Y» carrying the same contrast | two plain sentences, or one without the opposition |
| «—» everywhere | «:» or «;» everywhere, swapped mechanically | a full stop, a comma, or «-» chosen per sense |
| «ключевой» | «важнейший», «центральный», «критический» | delete, or say concretely *why* it matters |
| a word from the AI vocabulary (AI_INTENSIFIER) | another word from the same list | delete, or substitute a fact |
| «X - валюта Y» | «X - это новый Y» and other aphorism formulas | the concrete claim the formula was hiding |
| rule of three | a fresh triplet built from different words | one precise word, or specifics |
| falsely profound ending («и в этом весь смысл») | rewriting it into a more elegant metaphor | delete it; end on the last concrete sentence. If a closer is required, use a flat conclusion or the next step |
| a "После" sample from any reference file | copying it verbatim into your output | examples demonstrate a move, they are not blanks to fill |
| «Знакомо?» (AI_QA) | another stock rhetorical question | delete the question; state the claim |
| «В современном мире…» (FILLER_INTRO) | «В наши дни…», «Сегодня, как никогда…» | open on the actual claim |

---

## Three rules for the fabric of a replacement

How the new text knits into the old matters as much as what it says.

- **A replacement inherits the voice around it.** Read the paragraph before and after. If they run on short phrases, direct address, colloquial turns — your insert must carry the same moves. A sterile patch on live text is as visible as the slop was.
- **One move, once.** If you fixed a construction with a contrast, or by dropping a cliché, do not repeat that same manoeuvre elsewhere in the text. A repeated fix becomes a recognizable pattern in its own right.
- **A replacement longer than 22 words splits.** A long insert is almost always two sentences wearing one coat.

---

## Delete the water, not the function

A call to action, an offer, a deadline, a link, a contact, a price — these are the working parts of a text, not decoration. Treat them at levels 2-3 (replace / simplify), never at level 1.

A push notification with no CTA and a landing page with no offer have stopped doing their job, however much cleaner they read. This is the single most common way a cleaning pass destroys value while scoring well on every slop metric.

After editing, check explicitly: every functional element of the original is still present, at least one instance of each.

Relevant beyond `writer` — see `landing-copy`, `cold-email`, `microcopy`, `viral-text`, `release-notes`.

---

## Do not touch

Over-editing is as damaging as under-editing. A single «однако» means nothing; «однако» plus a rule of three plus «яркое наследие» plus a «Заключение» section is a confession.

Leave alone:

- Quotes, titles, proper names — even when they contain banned words
- Concrete odd details («юрист, который снимал офис над моим зубным»). A model rounds details off; a human keeps them
- Mixed feelings and unresolved positions
- Digressions, self-corrections, parenthetical doubts. A model does not interrupt itself; a human does
- Dry text with none of the catalogued patterns — that is just dry text, not AI
- Live syntax: plain «есть»/«это», plain verbs («умер», not «ушёл из жизни»), flat assertions without hedging, bulky colloquial connectives («из-за того, что»). People write this way; do not "improve" it
- Genre: in fiction and journalism the rule of three, dashes in dialogue, and long sentences are often deliberate. Edit them only alongside other markers

---

Sources: the substitution-trap framing and the fabric rules are adapted from [smixs/humanizer-ru](https://github.com/smixs/humanizer-ru) (MIT).
