---
name: microcopy
description: "Write UX microcopy — error messages, empty states, tooltips, button labels, helper text, modals, 404/500 pages, onboarding. Plain language, action-oriented, ≤8 words for buttons, never blames user. Wraps `writer`. Use when the user says 'error message', 'empty state', 'tooltip wording', 'button label', 'onboarding text'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Write microcopy strings for software product UI. Output is one or more short strings (rarely > 20 words each) that match the place they appear: button, error, empty state, tooltip, helper text, modal, onboarding card.

Use when the user wants to fill a UI element with text. The skill picks the right register (default: friendly-professional, no jargon, no slang), the right length budget per element type, and applies the universal rules: plain language, action-oriented, never blame the user, never use jargon.

This skill does NOT:
- write marketing landing pages (different scale + register)
- write technical documentation (use `essay-write` for longer-form docs)
- design layouts or component structures (use a design tool)
- write cold outreach (use `cold-email`)
</objective>

## ROLE

Read the request → identify UI element type → check length budget → write the string(s) → run universal rules check → return paste-ready text.

## PIPELINE

1. **Identify element type.** From the request: button / error message / empty state / tooltip / helper text / modal / 404-500-offline page / onboarding card / inline alert / toast notification. Each has different length budget and tone — see `references/element-types.md`.

2. **Identify context.** What's around the element? What did the user just do (or fail to do)? What's the next action they can take? Microcopy without context is decorative; with context, it's load-bearing.

3. **Apply length budget.** See `references/length-budgets.md`:
   - Button label: ≤ 8 words (most: 1-3 words)
   - Tooltip: ≤ 12 words
   - Error message: 1 sentence (≤ 20 words)
   - Helper text: 1 short sentence
   - Empty state heading: ≤ 6 words; body: ≤ 25 words
   - Modal title: ≤ 8 words; body: ≤ 50 words

4. **Apply universal rules** — see `references/rules.md`:
   - Plain language (8th-grade reading level)
   - Action-oriented (verb first when possible)
   - Never blame the user ("Your input is wrong" ❌ → "This email is missing the @" ✅)
   - Never use jargon (system-level, not user-level)
   - Be specific (don't say "an error occurred" — say what failed)
   - Always offer next step (what should the user DO?)

5. **Pick voice.** Default: friendly-professional (see `references/voice-by-product-type.md` for adjustments). Override only if user names a different brand voice.

6. **Output.** One or multiple strings (if alternatives are useful), each formatted for paste. If error → also include the structured form: `code`, `title`, `body`, `action`.

## MODES

- `microcopy <element-type> for <context>` — write a single string
- `microcopy --variants 3 <element-type>` — return 3 alternatives in different registers (e.g. casual / friendly / minimal)
- `microcopy error <error-context>` — structured error: title + body + primary action
- `microcopy empty-state <context>` — structured empty state: heading + body + primary CTA + secondary
- `microcopy 404 / 500 / offline / maintenance` — full-page error
- `microcopy --improve <existing-string>` — rewrite a weak existing string with notes on why

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/element-types.md](references/element-types.md) | Identifying element type — full taxonomy with examples per type |
| [references/length-budgets.md](references/length-budgets.md) | Checking budget — exact word and character limits per type |
| [references/rules.md](references/rules.md) | Applying the 10 universal rules (plain language, action verbs, no blame, no jargon, etc.) |
| [references/voice-by-product-type.md](references/voice-by-product-type.md) | Picking voice — adjustments for SaaS / dev tool / fintech / e-commerce / consumer / B2B |
| [references/banned-words.md](references/banned-words.md) | Strip list — words that mark text as low-quality microcopy (jargon, hedge words, robot-speak) |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 10 calibration pairs covering errors, buttons, empty states, tooltips, 404 pages.

## CONSTRAINTS

- **Never blame the user.** Always frame as "this didn't happen" not "you did it wrong".
- **Never use jargon.** "Authentication failed" → "We couldn't sign you in".
- **Always offer next step.** Error tells what failed AND what to do. Empty state tells what's missing AND what to add.
- **Use sentence case for buttons.** "Save changes" not "Save Changes" (unless the brand specifically uses title case).
- **No exclamation marks for routine actions.** Reserved for genuine celebrations (signup complete, first achievement). Default tone is calm.
- **No emojis in errors.** They look infantilizing. OK in achievement / onboarding microcopy if brand allows.
- **Be specific about what failed.** "Server error" ❌ → "We couldn't reach our servers — check your connection or try again in a minute" ✅
- **Don't use technical codes user-facing.** "HTTP 500" stays in the dev console; user sees friendly explanation.
- **Plural / singular careful.** "1 item selected" not "1 items selected". Most i18n libraries handle this; check the platform.
- **Localizable.** Avoid puns, idioms, culture-specific references unless the product is single-locale.

## INVOCATION HINTS

When the user says any of:
- "write / rewrite an error message for..."
- "empty state copy for..."
- "tooltip wording / helper text for..."
- "button label / button copy"
- "404 / 500 / offline page text"
- "onboarding text / card copy"
- "modal title / modal body"
- "toast notification text"
- "inline alert wording"

RU triggers (use the skill when the user writes any of):
- «текст ошибки / сообщение об ошибке / напиши ошибку для ...»
- «empty state на русском / пустое состояние / "ничего не найдено"»
- «лейбл для кнопки / надпись на кнопке / текст кнопки»
- «тултип / подсказка при наведении / hover-текст»
- «404 / 500 / страница "оффлайн" на русском»
- «онбординг-карточка / текст для туториала»
- «текст модалки / заголовок модального окна»
- «уведомление / toast / поп-ап текст»
- «перепиши эту микрокопию короче»

For RU patterns per UI element (typography «ёлочки», обращение «вы», friendly vs formal register), see [`references/element-types.md`](references/element-types.md) section `RU patterns per element`.

Use this skill. For longer-form (landing page sections, marketing copy) → not this skill; use `essay-write` or a marketing-specific skill.

If user wants register/tone shift of EXISTING microcopy — pair with `tone-shifter` (e.g. shift formal → friendly).
