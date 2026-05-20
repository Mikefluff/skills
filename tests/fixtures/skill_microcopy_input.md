# Input для microcopy — error states + empty states + buttons

## Context

SaaS project-management product. Default voice: friendly-professional. EN-only for now.

## What to write

### Error states (6)

1. **Network failure**: server unreachable
2. **Auth expired**: 401 from API
3. **Payment declined**: Stripe rejected card
4. **Permission denied**: user doesn't have edit access
5. **Validation failure**: form has invalid email
6. **Quota exceeded**: free plan hit 10-PR limit

### Empty states (3)

1. **First-time user, no projects yet**
2. **Filtered view with no matches**
3. **Cleared notification list — all caught up**

### Button labels (5)

1. Primary save action
2. Cancel
3. Delete project (destructive — modal confirm needed)
4. Continue to next onboarding step
5. Reset filters

## Constraints

- Apply 10 universal rules: plain language, action-oriented, no blame, no jargon, specific, sentence case, no exclamation marks for routine
- Each output respects per-element length budget (buttons ≤8 words; error inline ≤12 words; empty body ≤25 words)
- ALWAYS offer next step when possible
