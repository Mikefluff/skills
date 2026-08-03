# Length budgets

Per element type. These are hard ceilings unless brand voice explicitly contradicts.

---

## Quick table

| Element | Words | Characters (approx) |
|---|---|---|
| Button label | 1-3 (max 8) | 4-25 |
| Tooltip | ≤ 12 | ≤ 60 |
| Helper text (form) | ≤ 15 | ≤ 80 |
| Inline form error | ≤ 12 | ≤ 60 |
| Toast notification | ≤ 15 | ≤ 80 |
| Inline alert / banner | ≤ 30 | ≤ 150 |
| Empty state heading | ≤ 6 | ≤ 35 |
| Empty state body | ≤ 25 | ≤ 130 |
| Empty state CTA | ≤ 4 | ≤ 20 |
| Modal title | ≤ 8 | ≤ 45 |
| Modal body | ≤ 50 | ≤ 280 |
| Modal primary action | ≤ 3 | ≤ 18 |
| Onboarding card heading | ≤ 8 | ≤ 45 |
| Onboarding card body | ≤ 35 | ≤ 180 |
| 404 / 500 headline | ≤ 6 | ≤ 35 |
| 404 / 500 body | ≤ 40 | ≤ 200 |
| 404 / 500 primary CTA | ≤ 3 | ≤ 18 |

---

## Why these specific numbers

### Buttons (1-3 words, max 8)

- Mobile design constrains horizontal space — a button label that wraps is broken UX
- Eye-tracking research: users read button labels as one chunk, not as a sentence
- 1-3 word buttons are recognizable by shape alone after the first time

### Tooltips (≤ 12 words)

- Tooltips are a quick orientation, not a help article
- Hover-tooltips dismiss when the cursor moves; 12-word tooltips can be read in ~2 seconds
- Anything longer should be a help-modal link

### Errors (≤ 12 words inline, ≤ 30 toast/alert)

- Inline errors next to a form field need to fit in the field's adjacent space
- Toast/alert errors need to be readable in 3-4 seconds before they dismiss
- Modal errors get more space for body but title is still ≤ 8 words

### Empty states

- Heading is a hook — 6 words is enough to invite + orient
- Body explains: 25 words = ~2 short sentences
- CTA is the bet: 4 words max because users scan for the action

### Modals

- Modal titles are read in ≤ 1.5 seconds — 8 words max
- Modal bodies have permission to be longer (user is committed) — 50 words
- Action buttons stay 3 words

### Full-page errors (404, 500, offline)

- Big visual + big headline + body = scannable from across the room
- Headline 6 words is the scan-friendly limit
- Body 40 words gives one sentence of context + one sentence of next step

---

## What to do when you can't fit the budget

### Option 1 — Split into multiple elements

If your error needs 30 words but the inline error budget is 12, split:
- Inline (12 words): `Email format is wrong — see why`
- Modal/tooltip on click (full): "Email format expected: username@domain.com. We don't accept aliases or plus-addressing for new signups."

### Option 2 — Rewrite

Most budget violations are flab. Strip:
- "We're sorry, but" — delete
- "Please" — usually delete
- "In order to" → "To"
- "Due to the fact that" → "Because"
- Adjectives that don't add meaning

### Option 3 — Element-type mismatch

If you genuinely need 80 words to explain something — it's not a button or a tooltip. It's help documentation. Move it to a help article and link.

---

## When to deliberately go shorter than budget

The budget is a ceiling, not a target. Often less is more.

| Element | Budget | Often better |
|---|---|---|
| Button | 1-3 words | 1 word: `Save`, `Cancel`, `Continue` |
| Empty state CTA | 4 words | 2 words: `Add project` |
| Modal title | 8 words | 4-5 words: `Delete "ProjectName"?` |
| Toast | 15 words | 3-5 words: `Project saved. Undo?` |

The shortest version that's still clear wins.

---

## Character counts (when CMS / API constrains)

Some platforms / databases have hard char limits. Common ones to plan for:

- iOS push notification body: 178 characters (after that it truncates in lock screen)
- Android notification body: ~240 characters
- Twitter / X post: 280 characters
- LinkedIn post (above-fold): ~210 characters
- Slack message preview: ~140 characters
- Email subject (mobile gmail): ~30-40 characters visible
- Email preview text (gmail): ~90 characters

If the microcopy will be sent through one of these channels, budget for the channel's truncation.

---

## i18n considerations

Many languages expand when translated:

- English → German: typically +30-50% longer
- English → Russian: typically +20-40% longer
- English → French: typically +15-25% longer
- English → Japanese / Chinese: typically -50% (CJK is denser)

If you're targeting multilingual, leave 30-50% headroom in your English budget. A 6-word English heading might become 9 in German — make sure your UI can accommodate.
