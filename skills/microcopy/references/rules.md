# Universal microcopy rules

10 rules that apply to ALL microcopy regardless of element type. If you violate any of these, the string is wrong even if it sounds good in isolation.

---

## 1. Plain language — 8th-grade reading level

Use the simpler word when one exists. Default to monosyllables.

| ❌ | ✅ |
|---|---|
| `Authenticate` | `Sign in` |
| `Initialize` | `Set up` |
| `Terminate` | `End` / `Cancel` |
| `Subsequent` | `Next` |
| `Modify` | `Edit` / `Change` |
| `Commence` | `Start` |
| `Acquire` | `Get` |
| `Utilize` | `Use` |
| `Endeavor to` | `Try to` |
| `Approximately` | `About` |
| `Currently` | `Now` |
| `In order to` | `To` |
| `Due to the fact that` | `Because` |
| `At this point in time` | `Now` |

Test: can a 13-year-old read this and understand? If yes, ship.

---

## 2. Action-oriented — verb first when possible

Buttons, CTAs, primary actions all start with a verb. The user knows what they'll DO.

| ❌ Noun-first | ✅ Verb-first |
|---|---|
| `Account creation` | `Create account` |
| `User invitation` | `Invite user` |
| `File upload` | `Upload file` |
| `Settings configuration` | `Configure settings` (or just `Settings` if it's a nav link) |
| `Confirmation` | `Confirm` |
| `Submission` | `Submit` |
| `Request a demo` | `Request demo` |

Helper text and tooltips can be more conversational, but buttons / CTAs need verbs upfront.

---

## 3. Never blame the user

Frame everything as "what happened" not "what you did wrong". Even if the user did do something wrong.

| ❌ User blame | ✅ Neutral framing |
|---|---|
| `Your input is invalid` | `This email is missing the @ symbol` |
| `You entered an incorrect password` | `That password doesn't match — try again` |
| `Wrong file format` | `We accept PDFs and images only` |
| `Your card was rejected` | `The card was declined — try another` |
| `You don't have permission` | `This action requires admin access — ask your workspace admin` |
| `Required field` | `Email is required` (without "your error", just a fact) |
| `You exceeded the limit` | `You've reached the 1000-item limit` (factual, no judgment) |

The shift: from accusing → describing.

---

## 4. Never use jargon (developer-speak, system-speak)

User-facing text uses user-level vocabulary. System / dev terminology stays in logs.

| ❌ Jargon | ✅ Plain |
|---|---|
| `Authentication failed` | `We couldn't sign you in` |
| `Server error 500` | `Something on our end broke` |
| `Request timeout` | `That took too long — try again` |
| `Invalid token` | `Your session expired — sign in again` |
| `Database error` | `We couldn't save that — try again in a minute` |
| `Null reference exception` | `Something's missing — refresh the page` |
| `Validation failure` | `Some fields need fixing — see below` |
| `Network unavailable` | `You appear to be offline` |

If the developer needs the technical term for logs, keep it in the error `code` field. User sees friendly text.

---

## 5. Be specific about what failed

Don't say "an error occurred". Say what failed.

| ❌ Vague | ✅ Specific |
|---|---|
| `Error occurred` | `We couldn't save your draft — your changes aren't lost, try again in a moment` |
| `Something went wrong` | `We couldn't process the payment — the card was declined` |
| `Action failed` | `The image failed to upload — try a smaller file` |
| `Invalid request` | `The link has expired — request a new one` |

The user wants to know: WHY can't I proceed, and WHAT can I do?

---

## 6. Always offer next step

Every error message that CAN have a next step DOES have one.

| Error context | Next step |
|---|---|
| Network failure | `Check your connection or try again in a minute` |
| Permission denied | `Ask your workspace admin for access` |
| Auth expired | `Sign in again to continue` |
| Validation failure | (show the field-level errors so user knows what to fix) |
| Payment declined | `Try a different card or update payment details` |
| File too large | `Try a smaller file — max is 10MB` |
| Quota reached | `Upgrade your plan to add more` (or "remove unused items") |
| Server error | `Refresh and try again, or come back in a minute` |

If you genuinely can't offer a next step (e.g. terms violation, account closed), at least tell them WHERE to find more info (`Email support@... for help`).

---

## 7. Sentence case (default)

Use sentence case for headings, buttons, and most UI text. Title Case is for proper nouns and brand names.

| ❌ Title case | ✅ Sentence case |
|---|---|
| `Save Changes` | `Save changes` |
| `Create New Project` | `Create new project` |
| `Forgot Your Password?` | `Forgot your password?` |
| `Account Settings` | `Account settings` (or just `Settings`) |
| `Sign In With Google` | `Sign in with Google` |

Exception: when the brand specifically uses Title Case across all UI (some banking / luxury brands). Match the brand's choice.

---

## 8. Active voice

Subject does the verb. Avoid "by" + passive constructions.

| ❌ Passive | ✅ Active |
|---|---|
| `The file was uploaded by you` | `You uploaded the file` (or just `Uploaded`) |
| `Your request has been received` | `We received your request` |
| `The action was completed successfully` | `Done!` (or `Saved` or specific result) |
| `Settings have been saved` | `Settings saved` (toast version: just `Saved`) |
| `Your subscription will be cancelled` | `We'll cancel your subscription` |

Exception: when the subject is unknown or genuinely uninteresting:
- ✅ `Your password was reset` (you don't know who did it — could be you, could be email link)

---

## 9. No exclamation marks for routine actions

Reserved for genuine celebrations. The default tone is calm.

| ❌ | ✅ |
|---|---|
| `Saved!` | `Saved` |
| `File uploaded!` | `File uploaded` |
| `Welcome!` | `Welcome` (or `Welcome to {app}`) |
| `Done!` | `Done` |
| `Hello!` | `Hello` (or `Hi {Name}`) |

When exclamation IS appropriate:
- ✅ `Congratulations on your first project!` (genuine milestone)
- ✅ `100% complete — nice work!` (achievement)
- ✅ `🎉 First steps done!` (intentional celebration moment)

The rule: ask, "would a calm person say this with an exclamation in real life?" If no — strip the !.

---

## 10. Localizable — no idioms, puns, culture-specific references

Microcopy gets translated. Anything that's culturally specific breaks in translation.

| ❌ Hard to localize | ✅ Localizable |
|---|---|
| `Knocked it out of the park!` | `Great work!` |
| `That's a wrap` | `Done` / `Saved` |
| `Bummer!` | `That didn't work` |
| `Oopsie-daisy` | `Something went wrong` |
| `Houston, we have a problem` | `Something went wrong` |
| `Easy peasy` | `Quick and easy` (or just describe it) |

Exception: single-locale products can be more playful. But if your product supports multiple languages, every cute phrase becomes a translator's headache.

---

## Bonus: 3 cardinal sins (immediately fix)

These are universal disqualifiers — if you see them, strip on sight:

### a. "Please" in buttons

❌ `Please save`, `Please cancel`, `Please confirm`
✅ `Save`, `Cancel`, `Confirm`

### b. "Click here" / "Click to..."

❌ `Click here to download`, `Click to learn more`
✅ `Download report`, `Learn more`

The user knows it's a click; the verb describes the destination.

### c. Apologies in routine flows

❌ `Sorry! Your file is too big.`
✅ `That file is too large — max is 10MB.`

Save apologies for genuine inconveniences (outages, prolonged delays, data loss risks).

---

## The 3-test checklist

Before submitting any microcopy, run it through these:

1. **Plain-language test**: Can a 13-year-old read it?
2. **Blame test**: Does it accuse the user, or describe what happened?
3. **Next-step test**: If something failed, does the user know what to do?

If any answer is no — rewrite.
