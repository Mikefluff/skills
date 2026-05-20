# cold-email — calibration before/after pairs

4 paired examples covering EN founder→VC first-touch, EN sales→enterprise buyer, RU founder→Russian VC, and EN follow-up after no-reply. Each pair shows a generic «Hope this finds you well» template (the kind a competent professional sends when they don't know any better) and the same email rewritten under cold-email's 5-block structure with anchored opening, specific proof, single ask, and easy yes.

How to read these:

- The **Before** has the classic failure modes: ceremony openers («Hope this finds you well»), vague intros («I'm reaching out because»), no anchor («I'm a big fan of your work»), no specifics («significant growth», «extensive experience»), no ask the recipient can act on in 15 seconds, hedge language («I was wondering if», «would love to»), and a generic closing line. Subject line is empty calorie.
- The **After** rewrites under cold-email's rules: subject line carries the hook, body opens with a specific anchor («Saw the X round»), proof is in concrete numbers and named names, one ask with a time-bound, easy-yes lower-friction option, plain sign-off. Length budget ≤120 words for first-touch, ≤80 for follow-up.
- The **Deltas** name the specific patterns removed (with word counts) and the rule references (`structure.md`, `banned-patterns.md`, `length-budget.md`).

---

## Example 1 — EN founder → VC (first-touch)

**Context.** A US-based B2B SaaS founder writes to a Series-A partner whose fund just led a round in an adjacent vertical (developer tools). The founder has $2.1M ARR, 12 enterprise customers, three of them recognizable names. Wants a 20-minute meeting to walk the deck.

### Before (~175 words)

> Subject: Quick question
>
> Hi Patricia,
>
> I hope this email finds you well! My name is David Kim and I'm the co-founder and CEO of Nimbus, a B2B SaaS startup that's been disrupting the developer-tools space for the past 22 months.
>
> I've been a longtime admirer of your work at Magnet Ventures, and I was incredibly impressed by your recent investment in DevForge. Given the synergies I see between our work and your portfolio, I wanted to reach out personally to introduce myself.
>
> We've been growing rapidly — we now have a number of enterprise customers and significant ARR. Our customer base includes several well-known companies, and our product is being used by thousands of developers globally. I would love to set up a quick call to discuss potential opportunities for collaboration and learn more about your investment thesis.
>
> Would you be open to a 30-minute Zoom next week? I'm flexible with timing.
>
> Looking forward to hearing from you!
>
> Best regards,
> David Kim
> Co-founder & CEO, Nimbus Technologies Inc.

### After (~98 words)

> Subject: $2.1M ARR in dev tools — fit for Magnet?
>
> Hi Patricia,
>
> Saw the DevForge round — congrats on leading. We're in an adjacent wedge: pre-merge code-review automation for engineering teams of 20-200. $2.1M ARR over 22 months, 12 enterprise customers including Stripe, Datadog, and Cloudflare.
>
> Raising A in Q3. Worth 20 min next week to see if Magnet would be a fit?
>
> Happy to send the deck cold either way.
>
> Best,
> David Kim
> Co-founder, Nimbus · nimbus.dev

**Deltas**

- Subject «Quick question» → «$2.1M ARR in dev tools — fit for Magnet?» (banned-patterns.md §Subject-line bans; carries one number, one shared-context anchor, fits under 50-char cap) — structure.md §6
- «I hope this email finds you well!» — removed (-9 words; banned-patterns.md §Ceremony openers)
- «My name is David Kim and I'm the co-founder and CEO of Nimbus, a B2B SaaS startup that's been disrupting...» (24 words of bio in sentence 1) → name moves to signature; role implied by context; «disrupting» cut entirely (-24; structure.md §Block 1)
- «I've been a longtime admirer of your work» — removed (-8 words; banned-patterns.md §Vague intros — flattery without proof)
- «I was incredibly impressed by your recent investment» → «Saw the DevForge round — congrats on leading» (-5 words; one specific deal referenced; CEO position of «led» the round shown via «leading») — structure.md §Anchored opening
- «Given the synergies I see between our work and your portfolio» — removed (-12 words; CORPORATE)
- «We've been growing rapidly» / «a number of enterprise customers» / «significant ARR» / «several well-known companies» / «thousands of developers globally» (39 words of vague proof) → «$2.1M ARR over 22 months, 12 enterprise customers including Stripe, Datadog, and Cloudflare» (15 words of specific proof; net -24, +specificity) — structure.md §Block 2
- «I would love to set up a quick call to discuss potential opportunities for collaboration and learn more about your investment thesis» → «Raising A in Q3. Worth 20 min next week to see if Magnet would be a fit?» (-19 words; one specific ask, time-bounded, one purpose) — structure.md §Block 3
- «30-minute Zoom» → «20 min» — lower friction (structure.md §Block 3 timing)
- «I'm flexible with timing» — removed (-3 words; implied)
- «Looking forward to hearing from you!» → «Happy to send the deck cold either way» (-5 words; banned «looking forward», replaced with easy-yes that offers a next step) — banned-patterns.md §Closing line bans + structure.md §Block 4
- «Best regards» → «Best» (default per structure.md §Sign-off)
- «Nimbus Technologies Inc.» → «Co-founder, Nimbus · nimbus.dev» (one line, one link, no legal entity in signature)
- Total: 175 → 98 words, well under 120-word first-touch target — length-budget.md §First-touch

---

## Example 2 — EN sales → enterprise buyer (first-touch)

**Context.** An account executive at a security-tooling vendor writes to a VP of Engineering at a 2,000-person fintech. The AE has a real anchor: the VP recently spoke on a podcast about their supply-chain-security migration. The product genuinely solves the next-step problem the VP described as «still open».

### Before (~165 words)

> Subject: Opportunity to enhance your security posture
>
> Dear Mr. Reyes,
>
> I hope you are doing well. My name is Sarah Chen and I am a Senior Account Executive at SentinelStack, a leading provider of supply-chain security solutions. I'll keep this brief — I know you must be incredibly busy.
>
> I came across your podcast appearance on the Engineering Edge show and was very impressed by your insights on supply-chain security. We've been helping companies like yours strengthen their security posture, and I think there might be some great synergies between our work and what you're doing at Mercury Pay.
>
> I'd love to schedule a 30-minute call to learn more about your current challenges and explore how SentinelStack might be able to help. Would next Tuesday or Wednesday work for you?
>
> Looking forward to your favorable response!
>
> Warm regards,
> Sarah Chen
> Senior Account Executive, SentinelStack Inc.

### After (~110 words)

> Subject: SBOM signing gap you mentioned on Engineering Edge
>
> Hi Marco,
>
> On Engineering Edge (ep 87, the 34-minute mark) you said SBOM-signing was «still open» after the supply-chain migration. That gap is the specific thing SentinelStack closes — signs SBOMs at build, verifies at deploy, blocks unsigned artefacts in the CI/CD layer with one config line.
>
> Three Mercury-Pay-shape customers running it in prod today: Plaid, Brex, Modern Treasury. Median time-to-first-signature in production after rollout: 11 days.
>
> Worth 20 min next week to show the Brex deployment shape? They had the closest stack to yours.
>
> Or a 'no' is fine — I'll send the architecture one-pager cold and stop.
>
> Best,
> Sarah Chen
> SentinelStack · sentinelstack.io

**Deltas**

- Subject «Opportunity to enhance your security posture» → «SBOM signing gap you mentioned on Engineering Edge» (banned subject «Opportunity to {anything}» — banned-patterns.md §Subject-line bans; replaced with specific shared context the recipient owns) — structure.md §6
- «Dear Mr. Reyes» → «Hi Marco» (overly formal in cold outreach; recipient's culture is podcast-going engineering exec, not enterprise procurement) — structure.md §Block 1 opening
- «I hope you are doing well» — removed (-5 words; banned-patterns.md §Ceremony openers)
- «My name is Sarah Chen and I am a Senior Account Executive at SentinelStack, a leading provider of supply-chain security solutions» (22 words of bio + self-description) → name moves to signature; product mention compressed into the body sentence that actually does work; «leading provider» removed (banned-patterns.md §Multi-paragraph windup + banned MARKETING_HYPE) — net -22 words
- «I'll keep this brief — I know you must be incredibly busy» — removed (-12 words; banned-patterns.md §Ceremony openers, both clauses)
- «I came across your podcast appearance ... was very impressed by your insights» → «On Engineering Edge (ep 87, the 34-minute mark) you said SBOM-signing was "still open"» (-7 words; replaces generic flattery with timestamped, quoted anchor) — banned-patterns.md §Vague intros + structure.md §Anchored opening
- «strengthen their security posture» / «great synergies» — removed (CORPORATE; banned)
- Added concrete proof: 3 customers (Plaid, Brex, Modern Treasury) + 1 number (11 days time-to-first-signature) — structure.md §Block 2 (proof = numbers + named names)
- «30-minute call to learn more about your current challenges and explore how SentinelStack might be able to help» (20 words) → «20 min next week to show the Brex deployment shape» (10 words; one specific ask, one specific deliverable, time-bounded, references the closest-shape customer) — structure.md §Block 3
- «next Tuesday or Wednesday» — removed (over-specifying availability before the recipient has even agreed)
- «Looking forward to your favorable response!» → «Or a 'no' is fine — I'll send the architecture one-pager cold and stop» (-3 words but adds an easy-yes + out, which is the highest-ROI line in the email) — banned-patterns.md §Closing line bans + cold-email outreach.md §calibration note on the «no is fine» pattern
- «Warm regards» → «Best» (banned in cold outreach; too formal) — structure.md §Sign-off bans
- «Senior Account Executive, SentinelStack Inc.» → «SentinelStack · sentinelstack.io» (title dropped — implied by context, and the role isn't what earns the meeting; the SBOM-specific anchor is)
- Total: 165 → 110 words, under 120-word first-touch target

---

## Example 3 — RU founder → Russian VC (first-touch)

**Context.** Фаундер B2B fintech-сервиса для малого бизнеса пишет партнёру российского/СНГ-фокусированного фонда. $600K ARR, 14 клиентов (включая два узнаваемых российских ритейлера), 18 месяцев с запуска. Фонд недавно вложился в Trinity Bank — смежная вертикаль, но не пересекаются. Цель — встреча на 20 минут.

### Before (~200 слов)

> Тема: Здравствуйте!
>
> Добрый день, уважаемый Дмитрий Викторович!
>
> Надеюсь, моё письмо застанет вас в добром здравии. Меня зовут Алексей Соколов, я являюсь основателем и генеральным директором компании FinFlow — это инновационное B2B SaaS-решение в области финтех-инструментов для малого и среднего бизнеса, которое за последний год активно набирает обороты на российском рынке.
>
> Долгое время являюсь поклонником вашего фонда и был приятно удивлён вашей недавней инвестицией в Trinity Bank. В связи с этим, и принимая во внимание ту синергию, которую я вижу между нашими направлениями деятельности, я хотел бы обратиться к вам напрямую, чтобы коротко представиться и рассказать о нашем продукте.
>
> За последние месяцы у нас наблюдается уверенный и стабильный рост, мы успешно работаем с целым рядом крупных корпоративных клиентов и имеем значительную ежемесячную выручку. Я был бы крайне признателен за возможность организовать короткий созвон на 30-40 минут на следующей неделе для обсуждения потенциального сотрудничества и дальнейших шагов.
>
> Заранее благодарю за уделённое время и внимание.
>
> С наилучшими пожеланиями,
> Алексей Соколов
> Основатель и Генеральный директор, ООО «ФинФлоу Технолоджис»

### After (~110 слов)

> Тема: B2B fintech для малого бизнеса, $600K ARR — фит для фонда?
>
> Здравствуйте, Дмитрий!
>
> Видел раунд в Trinity Bank — поздравляю. Мы в смежной плоскости: финтех-инструменты для малого и среднего бизнеса (платежи, эквайринг, начисления подрядчикам в один клик), $600K ARR за 18 месяцев, 14 клиентов — включая «Магнит» и «Ленту» (HR-департаменты для выплат подрядчикам, не основной бизнес).
>
> Поднимаем seed в Q3. 20 минут на следующей неделе — есть смысл созвониться, чтобы понять фит?
>
> Если 20 минут — это много, готов прислать дек холодным письмом.
>
> С уважением,
> Алексей Соколов
> Основатель, FinFlow · finflow.ru

**Deltas**

- Тема «Здравствуйте!» (пустая) → «B2B fintech для малого бизнеса, $600K ARR — фит для фонда?» — одна цифра, шейп фонда, конкретный сектор; банится «приветствие в теме» по structure-ru.md §Subject + банится в EN-параллели — banned-patterns.md §Subject-line bans
- «Уважаемый Дмитрий Викторович» → «Здравствуйте, Дмитрий!» — отчество оставляем ТОЛЬКО если получатель публично его использует; для венчура/IT в РФ норма — обращение по имени; structure-ru.md §Greeting
- «Надеюсь, моё письмо застанет вас в добром здравии» — удалено (-10 слов; RU-калька от «I hope this finds you well»; banned-patterns.md §Ceremony openers, RU-variant)
- «Меня зовут Алексей Соколов, я являюсь основателем и генеральным директором компании FinFlow — это инновационное B2B SaaS-решение в области финтех-инструментов для малого и среднего бизнеса, которое за последний год активно набирает обороты на российском рынке» (38 слов представления + 3 банных конструкции: «являюсь» BUREAU_INV, «инновационное» AI_INTENSIFIER, «активно набирает обороты» VAGUE) → имя ушло в подпись; продукт описан конкретно («платежи, эквайринг, начисления подрядчикам в один клик»); net -28 слов с +специфика
- «Долгое время являюсь поклонником вашего фонда» — удалено (-7 слов; banned-patterns.md §Vague intros + BUREAU_INV «являюсь»)
- «был приятно удивлён» → «Видел ... — поздравляю» (-3 слова; конкретный якорь без льстивости)
- «В связи с этим, и принимая во внимание ту синергию, которую я вижу между нашими направлениями деятельности» — канцелярит выкинут целиком (-14 слов)
- «За последние месяцы у нас наблюдается уверенный и стабильный рост, мы успешно работаем с целым рядом крупных корпоративных клиентов и имеем значительную ежемесячную выручку» (25 слов; «наблюдается» BUREAU_INV, «целым рядом» VAGUE, «значительную» VAGUE) → «$600K ARR за 18 месяцев, 14 клиентов — включая "Магнит" и "Ленту"» (12 слов; конкретные числа + узнаваемые RU-бренды + честная скобка про HR-департаменты, не основной бизнес — calibration на честность) — structure.md §Block 2
- «короткий созвон на 30-40 минут на следующей неделе для обсуждения потенциального сотрудничества и дальнейших шагов» (15 слов) → «20 минут на следующей неделе — есть смысл созвониться, чтобы понять фит?» (12 слов; structure.md §Block 3 timing — 20 минут вместо 30-40)
- «Заранее благодарю за уделённое время и внимание» → «С уважением» (-7 слов; structure-ru.md §Sign-off — «С уважением» это RU-нейтральный дефолт, не выпрашивает ответ)
- «С наилучшими пожеланиями» → «С уважением» (banned-patterns.md §RU-equivalent; «С наилучшими пожеланиями» — слишком приторно для cold-аутрича)
- «ООО "ФинФлоу Технолоджис"» → «FinFlow · finflow.ru» — юр.лицо в подписи cold-email не нужно, только бренд + ссылка
- Добавлен easy-yes («Если 20 минут — это много, готов прислать дек холодным письмом») — structure.md §Block 4
- Total: 200 → 110 слов, в RU budget'е ≤120 слов для first-touch — length-budget.md §First-touch

---

## Example 4 — EN follow-up after no-reply

**Context.** Founder sent the first email from Example 1 to Patricia at Magnet Ventures 11 days ago. No response. In the meantime: Magnet announced its fourth fund close ($350M); Nimbus added a new logo (HashiCorp) and crossed $2.4M ARR. Both events are real anchor candidates for the bump.

### Before (~120 words)

> Subject: Re: Quick question
>
> Hi Patricia,
>
> Just wanted to bump this up to the top of your inbox. I know you must be incredibly busy, so apologies for the follow-up.
>
> I sent you an email last week about Nimbus — we're a B2B SaaS company in the developer-tools space that's been growing rapidly. I'd really love to set up a quick call to discuss potential opportunities for collaboration and to share more about our journey.
>
> If now isn't a good time, I completely understand — would love to circle back in a few weeks.
>
> Looking forward to your response!
>
> Best,
> David Kim
> Co-founder & CEO, Nimbus Technologies Inc.

### After (~72 words)

> Subject: Re: $2.1M ARR in dev tools — fit for Magnet?
>
> Hi Patricia,
>
> Following up on the May 9 note. Saw the Magnet-IV close — congrats on $350M. With the new fund I'd guess your A pipeline is opening up.
>
> Two updates since: HashiCorp joined as customer #13, ARR ticked to $2.4M (+$300K in 11 days). Still planning a Q3 round; 20 min next week worth it?
>
> Or a 'no' is fine — I'll stop after this.
>
> Best,
> David
> Nimbus · nimbus.dev

**Deltas**

- Subject — kept original threading «Re: $2.1M ARR in dev tools — fit for Magnet?» (structure.md §follow-up subject rule: never change subject mid-thread)
- «Just wanted to bump this up to the top of your inbox» — removed (-12 words; banned-patterns.md §Follow-up specific bans, «Just bumping this up» literal)
- «I know you must be incredibly busy, so apologies for the follow-up» — removed (-12 words; banned-patterns.md §Follow-up bans, pity-framing)
- «I sent you an email last week about Nimbus — we're a B2B SaaS company in the developer-tools space that's been growing rapidly» (22 words of re-explanation) → removed entirely; trust that Patricia can scroll up if she cares — structure.md §follow-up «do NOT re-explain the original pitch»
- Added concrete new anchor: «Saw the Magnet-IV close — congrats on $350M» — structure.md §follow-up Block 2 «Why now: new context that justifies the bump»
- Added one new datapoint pair: «HashiCorp joined as customer #13, ARR ticked to $2.4M (+$300K in 11 days)» — exactly one new thing per follow-up (rule from outreach.md follow-up calibration notes)
- «I'd really love to set up a quick call ...» → «20 min next week worth it?» (-13 words; same ask, less verbose) — structure.md §follow-up Block 3
- «If now isn't a good time, I completely understand — would love to circle back in a few weeks» — removed (-19 words; banned-patterns.md §Follow-up bans, «in case my last email got buried» equivalent)
- «Looking forward to your response!» → «Or a 'no' is fine — I'll stop after this» — banned closing replaced with explicit out (the highest-ROI line in any follow-up) — banned-patterns.md §Closing line bans + follow-up.md calibration
- «Best, David Kim / Co-founder & CEO / Nimbus Technologies Inc.» → «Best, David / Nimbus · nimbus.dev» — second-touch sign-off can drop title and use first-name only (structure.md §Sign-off alternatives, «when you've already established multi-message rapport»)
- Total: 120 → 72 words, well under 80-word follow-up target — length-budget.md §Follow-up

---

## Pattern summary

Across all 4 pairs:

1. The subject line is the first hook. It carries either a number, a shared context, or a specific outcome — never «Quick question», «Hi», «Touching base», «Opportunity to {x}», or «Здравствуйте!».
2. The first sentence of the body is anchored to something specific the recipient owns: a round they led, a podcast they appeared on, a deal they closed. «I hope this finds you well» / «Надеюсь, моё письмо застанет вас в добром здравии» / «I've been a longtime admirer» — strip on sight.
3. Proof is numbers + named names, never «significant growth», «rapidly growing», «значительная выручка», or «целый ряд крупных корпоративных клиентов». If you don't have the numbers, don't send the email yet.
4. One ask per email. Time-bounded (20 minutes, not 30-40). Easy-yes lower-friction option attached.
5. Closing line: «Happy to send the deck cold either way» / «Or a 'no' is fine — I'll stop after this» / «Готов прислать дек холодным письмом». Never «Looking forward to your response», never «Заранее благодарю».
6. Sign-off plain (Best / С уважением). Signature one line. No legal entity, no four-line corporate footer.
7. Follow-ups: do not repeat the original pitch; add exactly one new anchor (their news + your news); offer the explicit out; subject keeps original `Re:` threading.
8. Length budgets: first-touch ≤120 words EN / ≤120 слов RU; follow-up ≤80 words / ≤80 слов. If you can't fit, cut — see `length-budget.md` for the cut-list.
