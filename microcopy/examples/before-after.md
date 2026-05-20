# microcopy — calibration before/after pairs

10 paired examples covering common element types. Each shows weak version, rewrite, and deltas applied.

---

## 1. Button — destructive action

### Before

```
Are You Sure You Want to Delete This?
```

### After

```
Delete account
```

### Deltas
- Title case → sentence case (in some brands; rule depends)
- Question → action verb
- Wrapped ambiguity → specific destructive verb + noun
- 8 words → 2 words

Use this in the **button**. The "are you sure" warning goes in the modal title/body, not the button.

---

## 2. Modal — confirmation

### Before

```
Title: Confirmation
Body: Are you sure you want to delete this account? This cannot be undone.
Button: OK
```

### After

```
Title: Delete account?
Body: This permanently removes your account, including 247 saved drafts and 12 connected integrations. We can't restore it after this.
Primary: Delete account
Secondary: Cancel
```

### Deltas
- Title: "Confirmation" (no info) → "Delete account?" (specific action)
- Body: vague "cannot be undone" → explicit consequence (247 drafts, 12 integrations)
- Primary button "OK" (ambiguous on destructive) → "Delete account" (commits the action)
- Added secondary "Cancel" for clear escape

---

## 3. Inline form error — email validation

### Before

```
Invalid Email Address.
```

### After

```
This email is missing the @ symbol
```

### Deltas
- User-blame ("invalid") → factual ("missing the @")
- Tells them WHAT to fix instead of judging input
- 3 words → 6 words (more clarity, still under 12-word budget)
- No period needed (inline errors often skip)

---

## 4. Empty state — first-time user, no projects

### Before

```
Heading: No Projects Found
Body: Looks like you don't have any projects yet!
CTA: Create New Project
```

### After

```
Heading: Your first project goes here
Body: Get started — adding a project takes about 30 seconds.
CTA: Add project
```

### Deltas
- Heading reframed from emptiness ("No projects") to invitation ("Your first goes here")
- Apology / softening ("Looks like... yet!") → specific value-claim ("takes about 30 seconds")
- CTA tightened from 3 words to 2 (verb-noun)
- No "!" anywhere

---

## 5. Error — network failure

### Before

```
Error: Unable to connect to server. Please try again later.
```

### After

```
We couldn't reach our servers
Check your connection or try again in a minute.
```

### Deltas
- Generic "error" → specific user-facing description
- Jargon ("server") in title → friendly ("our servers")
- "Please try again later" → "in a minute" (specific time estimate)
- Added "check your connection" — the most-likely root cause

---

## 6. Toast notification — save confirmation

### Before

```
Your changes have been saved successfully!
```

### After

```
Saved
```

### Deltas
- 5 words → 1 word
- Passive ("have been saved") → state ("Saved")
- Removed exclamation (routine action, not celebration)
- For toast: 1 word fits perfectly in the 3-second window

If undo is available:
```
Saved · Undo
```

---

## 7. 404 page

### Before

```
404 Error
Page not found. The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
```

### After

```
This page doesn't exist
The link might be broken, or the page might have moved.
```

Primary CTA: `Back to home`
Secondary CTA: `Search` (if site has search)

### Deltas
- Removed "404 Error" technical code (or move it to small subscript)
- Stripped jargon ("removed, had its name changed, or is temporarily unavailable") → plain 2-line explanation
- Two specific causes user can map to their experience
- Added concrete next-step CTAs

---

## 8. Helper text — password field on signup

### Before

```
Password must be at least 8 characters long and contain at least one number and one special character.
```

### After

```
8+ characters, with a number or symbol
```

### Deltas
- 17 words → 7 words
- "must be at least 8 characters long" → "8+ characters"
- "contain at least one number and one special character" → "with a number or symbol"
- Constraint stated as requirement, not as warning

---

## 9. Tooltip — export button

### Before

```
This button allows you to export the selected items.
```

### After

```
Export the filtered list as CSV
```

### Deltas
- Don't restate the button label ("export")
- Add value: tells user what format + what subset (filtered, not all)
- 9 words → 6 words
- Removed "This button allows you to" — empty preamble

---

## 10. Onboarding card — step 1

### Before

```
Welcome to Acme!
Acme is the leading platform for project management. We help thousands of teams collaborate, track progress, and ship faster than ever. Let's get started by creating your first project!
```

### After

```
Welcome
Let's set up your first project — takes about 2 minutes.
```

CTA: `Create project`

### Deltas
- Marketing prose ("leading platform... thousands of teams... ship faster than ever") → deleted (this is the onboarding card, not a sales page)
- Focused on the immediate next action (create project)
- Added time estimate (lowers friction)
- 32 words → 11 words

---

## Pattern summary

Across all 10 rewrites, the consistent moves:

1. **Cut filler** — "in order to", "please", "just", "simply", "looks like" — usually 30-50% length reduction with zero loss
2. **Replace generic with specific** — "an error" → what failed; "no projects" → "your first project"
3. **Verb-first for actions** — "Account creation" → "Create account"
4. **Strip user blame** — "Invalid input" → "This email is missing the @"
5. **Sentence case** — match natural-reading flow
6. **Skip apologies for routine flows** — save them for genuine inconvenience
7. **Always offer next step** — error tells what to do; empty state tells what to add
8. **One concept per element** — modal body can be 50 words; button label cannot
9. **Time estimates lower friction** — "takes 30 seconds" / "in a minute" beats "shortly"
10. **No exclamation marks for routine** — `Saved`, not `Saved!`

These 10 patterns cover ~80% of microcopy improvements. Apply them mechanically before considering anything fancier.
