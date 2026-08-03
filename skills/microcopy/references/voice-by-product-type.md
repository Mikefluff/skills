# Voice by product type

Microcopy voice should match the product's audience and use context. Six common product types with voice adjustments.

---

## 1. SaaS — friendly-professional (default)

Audience: working adults using software at work. Mostly knowledgeable.

### Voice signature

- Direct, calm, slight warmth
- Light contractions OK (`we'll`, `you're`)
- Helpful but not chatty
- No emoji in errors; OK in onboarding / achievements

### Sample tone

- Success: `Settings saved`
- Empty state: `Your first project goes here — start by adding one.`
- Error: `We couldn't reach our servers. Check your connection or try again in a minute.`
- Onboarding: `Welcome — let's set up your first integration.`

---

## 2. Developer tools — terse, technical literacy assumed

Audience: developers / sysadmins. Want fast info, hate hand-holding.

### Voice signature

- Even more direct than SaaS
- Technical accuracy more important than friendliness
- Few contractions
- No exclamation marks anywhere
- Error messages can include actual technical context (with the user-friendly explanation alongside)

### Sample tone

- Success: `Deployed`
- Empty state: `No deployments yet. Run \`deploy --init\` to get started.`
- Error: `Build failed — check the logs above. Most common cause: missing env var.`
- CLI confirmation: `This will overwrite the production database. Continue?`

---

## 3. Fintech — careful, trust-building

Audience: handling money. Trust is the product.

### Voice signature

- Calm, precise, never playful
- No exclamation marks anywhere
- Spell out consequences explicitly
- No "oops" or casual language
- Show numbers / amounts / dates clearly

### Sample tone

- Success: `Transfer complete. $500.00 sent to John Smith. Reference: #4427.`
- Empty state: `No transactions yet. Once you make your first transfer, it'll appear here.`
- Error: `We couldn't process this transfer. Your money has not been moved. Try again, or contact support.`
- Destructive: `Cancel scheduled transfer? The $1,200 transfer to John Smith on Dec 15 will not be sent.`

---

## 4. E-commerce — warm, conversion-aware

Audience: shoppers. Friction kills conversion.

### Voice signature

- Friendlier than SaaS, with light enthusiasm
- Light emoji OK in achievements (order confirmed, first purchase)
- Reassurance during payment / checkout
- Clear progress indicators

### Sample tone

- Success: `Order confirmed — we'll email you when it ships.`
- Empty cart: `Your cart is empty. Browse our latest collection.`
- Error: `We couldn't process your payment. No charges were made. Try a different card?`
- Out of stock: `This is sold out. Want us to email when it's back in stock?`

---

## 5. Consumer mobile app — playful, brand-forward

Audience: general consumers. Brand voice is the product's personality.

### Voice signature

- Most flexibility for brand voice
- Emoji OK in achievements + first-use
- Slightly playful in success states
- Concise (mobile context)
- Still calm in errors

### Sample tone

- Success: `Saved 🎉` (or just `Saved`)
- Empty state: `Looking a little empty here. Add your first {item} to see things happen.`
- Error: `Something's not right. Try refreshing.`
- Onboarding: `Welcome aboard! Quick tour?`

---

## 6. B2B enterprise — formal, careful

Audience: enterprise admins, IT, procurement. Often non-technical decision-makers.

### Voice signature

- Most formal of all product types
- No contractions
- No emoji ever
- Conservative phrasing
- Explicit about implications, especially for billing / permissions

### Sample tone

- Success: `Configuration saved.`
- Empty state: `No users have been provisioned. Add users from the Administration panel.`
- Error: `The action could not be completed. Please contact your administrator.`
- Destructive: `Delete the organization "Acme Inc."? This action will deprovision all 247 users, archive all data for 90 days, and is irreversible.`

---

## Cross-product common ground

Regardless of product type:

- **Errors stay calm.** Even a fintech error speaks softly; even a consumer app doesn't apologize obsequiously.
- **Buttons stay 1-3 words.** No product type benefits from "Click here to do the thing".
- **No blame.** Universal.
- **Always offer next step when possible.** Universal.

---

## Adjusting for brand voice override

If the user provides a brand-voice JSON profile (from `tone-shifter`), apply it AFTER picking the product-type voice as the default.

Pipeline:
1. Product type → default voice
2. Brand-voice profile (if any) → adjustments to vocabulary / banned words / hook patterns
3. Final cleanup pass via `writer`

Example: SaaS product (default = friendly-professional) + brand profile { tone: "humorous", vocabulary: ["ship", "build", "real talk"] } → output is friendly-professional structure with playful vocab and informal hook patterns.

---

## When the user doesn't specify product type

Ask. If they don't know, default to **SaaS friendly-professional**. It's the safest, most-universal voice and works for ~70% of products.
