# Exemplar design systems and UX

Products with strong, coherent systems, spread across categories. Study **why** their visual and UX choices fit their product, then apply that reasoning to yours. Copying their surface creates the next uniform look: the "Linear look" and Stripe's gradient are already SaaS clichés ([LogRocket](https://blog.logrocket.com/ux-design/linear-design), [UX Collective](https://bootcamp.uxdesign.cc/the-rise-of-linear-style-design-origins-trends-and-techniques-4fd96aab7646)).

Each entry: **Visual** (type, color, layout, motion, voice) · **UX** (interaction patterns, and the expectation it set for its category) · **Signature** · **Fits when** · **Don't copy**. Details marked † have not been checked against the live product: treat them as leads to look at, not facts.

## Developer and infrastructure tools

**Linear** ([redesign notes](https://linear.app/now/how-we-redesigned-the-linear-ui))
- Visual: Inter Display headings, Inter body. Themes generated in LCH from three inputs (base, accent, contrast) instead of ~98 hand-picked tokens; elevation from the same math. Dense rows, neutral palette, hairline borders†.
- UX: keyboard-first, cmd-K for everything, instant optimistic updates through a local sync engine†. It set the expectation that tools feel instant.
- Signature: speed as the brand. Fits: power-user tools. Don't copy: purple glows and gradient headlines†.

**Vercel / Geist** ([docs](https://vercel.com/geist/introduction))
- Visual: Geist Sans, Mono, Serif and Pixel. High-contrast accessible colors. Foundations: colors, typography, materials, grid, with the grid core to the look. Components ship as `@vercel/geistcn`.
- UX: every push gets a preview URL; deploy status and logs are always one step away†.
- Signature: stark black and white with an exposed grid†. Fits: developer infrastructure. Don't copy: decorative grid lines with no structure behind them.

**Raycast** ([press kit](https://www.raycast.com/press))
- Visual: brand red `#FF6363` on `#151515` / `#202123`, dark-first, its own icon template.
- UX: a launcher where everything is a command, with keyboard-only flows and extensions†.
- Signature: one warm red on near-black, glossy native feel†. Fits: desktop utilities. Don't copy: gloss without native-quality execution.

**Railway** ([railway.com](https://railway.com))
- Visual and UX: the product is a canvas where services and connections render as a graph; the graph is both UI and marketing visual. Live logs and deploy state sit on the canvas†.
- Fits: products whose real model is a graph or pipeline. Don't copy: graph visuals for products that aren't graphs.

**Fly.io** ([fly.io](https://fly.io))
- Visual: casual, nerdy voice; hand-drawn storybook illustration and a light palette against the dark dev-tool convention†.
- UX: CLI-first, with docs that start from a working command†.
- Fits: brands that sell on personality and have an illustrator. Don't copy: generic illustration packs standing in for real art.

## Fintech

**Stripe** ([stripe.com](https://stripe.com)) †
- Visual: animated gradient mesh, fine-line technical diagrams, precise docs typography.
- UX: inline card validation, one-click autofill (Link), docs with your own live API keys inside copy-paste examples. It made interactive, personalised docs the norm.
- Fits: developer-facing money products. Don't copy: the gradient, which is now the generic SaaS look.

**Mercury** ([mercury.com](https://mercury.com)) †
- Visual: serif display type, soft cool gradients, editorial photography, calm luxury.
- UX: fast onboarding, cmd-K inside a bank. It made banking feel like a modern tool.
- Fits: premium B2B finance. Don't copy: serif plus gradient as a costume over a weak product.

**CRED** ([cred.club](https://cred.club), [NeoPOP design system](https://github.com/CRED-CLUB/neopop-web)) † (India)
- Visual: NeoPOP, raised 3D-edge "pop" buttons, black backgrounds, bold accents, a premium members-only voice.
- UX: bill payment as a reward ritual, with haptics, celebrations and rewards. Effective, and also criticised as gamification.
- Fits: aspirational consumer rewards. Don't copy: the exclusivity voice on a mass-market product, or engagement tricks.

**Zerodha Kite** ([kite.zerodha.com](https://kite.zerodha.com)) † (India)
- Visual: dense and quiet, almost no color except red and green for profit and loss.
- UX: keyboard order entry, a fast watchlist, nudges before risky trades, no push spam. Calm by design: friction added on purpose to protect the user.
- Fits: tools that need trust and dense data. Don't copy: the bare look without the speed under it.

## Productivity and creative tools

**Things** ([culturedcode.com/things](https://culturedcode.com/things/)) †
- Visual: native Apple feel, generous padding, a single blue, satisfying micro-animation.
- UX: drag the "Magic Plus" to insert anywhere, natural-language dates, Quick Entry from anywhere, deliberately no collaboration. It sells focus and polish as the feature.
- Fits: personal daily tools. Don't copy: Apple conventions on platforms that aren't Apple's.

**Panic** ([panic.com](https://panic.com)) †
- Visual: each product gets its own illustrated world (Playdate yellow, Nova), witty copy.
- UX: native conventions and clear permission dialogs; Playdate's crank is a new input. It showed indie software can match big-company polish.
- Fits: small studios with personality. Don't copy: whimsy without the craft.

**Are.na** ([are.na](https://www.are.na)) †
- Visual: nearly unstyled, system serif and sans, grey blocks.
- UX: blocks and channels, connect anything to many places, chronological feeds, no likes. Social without algorithmic ranking.
- Fits: research, collecting, slow tools. Don't copy: "plain" as an excuse for weak hierarchy.

## Opinionated and editorial

**HEY / 37signals** ([hey.com](https://www.hey.com)) †
- Visual: hand-drawn illustration, loud manifesto copy, bright flat color, first-person voice.
- UX: the Screener approves first-time senders; Imbox, Feed and Paper Trail split mail by type; "Reply Later" batches replies. Triage by default.
- Fits: products with a strong point of view. Don't copy: the anger, if you have nothing to fight.

**Gumroad** ([gumroad.com](https://gumroad.com)) †
- Visual: neo-brutalism with pink, thick black borders, hard offset shadows (no blur), chunky type.
- UX: a product goes live in minutes, with a single-page checkout.
- Fits: indie creators and marketplaces. Don't copy: the style itself, which now reads as a template.

**Poolsuite** ([poolsuite.net](https://poolsuite.net)) †
- Visual and UX: a full fake Mac OS 9 desktop with draggable windows, pixel fonts, summer pastels and music throughout. A brand experience instead of pages.
- Fits: nostalgia, music, entertainment. Don't copy: retro chrome on serious work tools.

## Hardware and consumer

**Arc / The Browser Company** ([arc.net](https://arc.net))
- Visual: a personal, warm voice; historically playful gradients, a custom serif and sans pairing, bouncy motion†.
- UX: sidebar spaces, a command bar and split view rethought browser chrome†. The company has since moved on to its new browser, Dia.
- Fits: consumer products with a strong point of view. Don't copy: whimsy that slows core tasks.

**Teenage Engineering** ([teenage.engineering](https://teenage.engineering))
- Visual: lots of white space, lowercase nav, small product grids, jokey mixed-case copy. It reads like an instrument manual.
- UX: product pages carry dense specs with calm scrolling instead of heavy animation†. It respects technical buyers while staying playful.
- Fits: physical objects and tools for makers. Don't copy: the case quirks without the humour.

**Nothing** ([nothing.tech](https://nothing.tech))
- Visual: dot-matrix display type, monochrome with a red accent, a transparent-hardware feel†.
- UX: OS, hardware lights and website share one visual language; launches are teased; the community feeds back into the product†.
- Fits: tech with its own hardware or OS layer. Don't copy: dot fonts for body text.

**Family** ([family.co](https://family.co), [design write-up](https://benji.org/family-values)) †
- Visual: soft 3D, rounded friendly type.
- UX: trays that change height so actions stay in context, springy physics motion, gentle haptics, plain-language transaction signing. Crypto that feels like a consumer app.
- Fits: mobile-first apps where feel matters. Don't copy: motion that slows tasks down.

## Public service

**GOV.UK Design System** ([design-system.service.gov.uk](https://design-system.service.gov.uk))
- Visual: GDS Transport, black and white, yellow focus states, plain English†.
- UX: one question per page, an error summary that links to each field, "Check your answers" before submit, progressive disclosure, WCAG 2.2 AA, works without JavaScript†. Its start-page-plus-transaction pattern is copied by governments worldwide.
- Fits: forms, high-stakes tasks, an audience of everyone. Don't copy: the crown and branding, which are restricted. The patterns are free to use.

More systems with public docs: [Shopify Polaris](https://polaris.shopify.com), [IBM Carbon](https://carbondesignsystem.com), [Monzo](https://monzo.com) (voice and tone).

## Principles that transfer
- **Generate, don't hand-pick:** derive palettes from a few inputs in a perceptual space (LCH/OKLCH), so themes and elevation stay consistent.
- **Color carries meaning:** one accent for action, status colors only for status.
- **Structure before decoration:** grid, borders and type hierarchy first; effects last.
- **The signature comes from the product's truth:** Railway's graph, Raycast's keyboard, HEY's triage. Find the equivalent in your subject.
- **UX is part of the identity:** Zerodha's calm, Things' focus and GOV.UK's one-question-per-page are as recognisable as any palette.
- **Voice is part of the system:** Arc, Fly.io and HEY are recognisable from copy alone.

## How UX expectations are evolving (2024–2026)

Table stakes now: missing these reads as dated.
- **Instant, optimistic UI:** routine actions update immediately; a spinner on a simple action feels broken.
- **Keyboard and command palette** in any tool people use daily (cmd-K is spreading from dev tools into finance and docs).
- **Accessibility as a legal floor:** the European Accessibility Act applies from 28 June 2025, with WCAG 2.2 AA as the practical target.
- **System theming:** dark mode, `prefers-reduced-motion` and `prefers-color-scheme` respected.
- **Lighter sign-in:** passkeys and magic links instead of password plus OTP†.
- **AI inline, not bolted on:** suggestions appear in context with clear accept and reject controls, rather than a separate chat page†.
- **Motion as feedback:** native view transitions and scroll-driven animation that explain a change, not decoration†.

What still sets a product apart: a distinct brand world (Panic, Nothing), a calm or anti-engagement stance (Zerodha, Are.na, HEY), and tactile, physics-based mobile motion (Family).
