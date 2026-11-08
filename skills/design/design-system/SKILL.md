---
name: design-system
description: "Create a distinctive design system before building web UI, so the result has its own taste instead of the generic AI look. Use when building or restyling a website, landing page or web app UI and the project has no DESIGN.md or design tokens yet, or when the user asks for a design system, visual direction, rebrand or better taste."
license: MIT
metadata:
  version: "0.3.0"
---

# Design system

Generic AI UI comes from **unchosen defaults**: the font, color, layout and motion a model reaches for when nobody decided. Your job is to make every one of those a deliberate decision rooted in *this* product, write the decisions down as a design system, and only then build UI from it. Taste here means **specific and consistent**: every choice traces back to the brief, and the same choices hold on every page.

## 0. Existing system first

If the project already has a `DESIGN.md`, design tokens or a theme file, read it and build within it. Extend it only where it lacks something, and record the extension in it. Start the steps below only when there is no system.

## 1. Brief

Extract from the request and the repo: audience, purpose, the main action users should take, real content, constraints (stack, brand assets, accessibility needs), and **3–5 brand attributes** (e.g. "calm, precise, warm").

If attributes or references are missing, ask in one batch, at most 5 questions: who it's for, 3–5 words it should feel like, sites or objects they admire (and what exactly about them), anything they dislike, and light, dark or both. In a non-interactive run, infer the answers from the subject, mark them `assumed` in `DESIGN.md`, and continue.

## 2. Three directions

Propose 3 directions that differ on at least 3 dials: color temperature and value, type genre, layout structure, density, shape, motion. Each direction gets:
- a name and a one-line concept rooted in the subject's own world: its materials, tools, vernacular, era or place. A bicycle repair shop's world is chain grease, torque specs, chalkboard job lists and exploded parts diagrams, not "modern and clean".
- palette idea, font idea, layout idea
- **one signature move**: the single place where boldness is spent (a type treatment, a layout quirk, a texture, a color moment)
- 1–2 real references and what is taken from each. For how strong systems connect visual and UX choices to their product, see [`references/exemplars.md`](references/exemplars.md) (20 products across dev tools, fintech, creative tools, editorial, hardware and public service). Borrow their reasoning, not their surface.

Then **audit each direction** against [`references/ai-fingerprints.md`](references/ai-fingerprints.md), including its *new defaults* section. Ask of each: "Would a generic prompt for this category produce this?" Replace any direction where the answer is yes.

The user picks one or mixes them. In a non-interactive run, choose the direction most specific to the brief and note the runners-up in `DESIGN.md`.

## 3. Write the system

Write `DESIGN.md` at the repo root, plus a tokens file in the project's stack: CSS custom properties, Tailwind v4 `@theme`, or DTCG JSON if asked. Every value states the reason it serves the direction.

- **Principles:** 3–4 rules that settle trade-offs ("density over decoration", "type carries hierarchy, color carries action").
- **Tokens in three tiers:** primitives (raw scales), then semantic roles (`--color-bg`, `--color-surface`, `--color-text`, `--color-text-muted`, `--color-accent`, `--color-border`, status colors), then component tokens only where a component needs its own knob. Components consume semantic tokens only.
- **Color:** build scales in OKLCH. Mostly neutrals tinted toward the direction, one accent reserved for primary action, and status colors only where they carry meaning. Use no pure `#000`/`#fff` surfaces. Derive dark mode by re-mapping the semantic roles (lighter surfaces for depth, slightly lower chroma), not by inverting. Check contrast: WCAG 2.2 AA, 4.5:1 body text, 3:1 large text, UI parts and focus rings.
- **Type:** at most 2 families, chosen for character with a one-line reason. Fonts on the fingerprint list need a written justification. Sources: Google Fonts, Fontshare, Fontsource. Use a modular scale whose ratio fits the genre (~1.2 for dense UI, 1.333–1.5+ for editorial), fluid sizes with `clamp()`, body measure 45–75ch, body leading 1.4–1.6, headings 1.05–1.2, and tighter tracking on large sizes.
- **Space and layout:** a 4px base with a named scale. Use less space inside a group than between groups. Name a grid, a max content width, and the density. Vary section rhythm on purpose rather than repeating one stacked pattern.
- **Responsive (mobile and desktop are both first-class):** design mobile-first, then compose desktop deliberately rather than just stretching mobile. Name breakpoint tokens (e.g. 360, 768, 1024, 1440) and for each key section state its mobile and desktop layouts: what stacks, reorders, collapses or hides. Use fluid type and spacing (`clamp()`) between breakpoints. On mobile: a nav pattern that fits thumbs, primary actions within thumb reach, ≥16px input text (prevents iOS zoom), and no horizontal scroll at 320px. On desktop: compose with the width. Pick a first-screen pattern and a section rhythm from [`references/composition.md`](references/composition.md), with an asymmetric grid, at least one deliberate overlap or grid break, and no empty half. Every column of the first screen carries content.
- **Shape, elevation, motion, icons:** one radius scale (nested radius = outer radius − padding); either 3–4 shadow levels or flat with borders, not both; motion durations and easing with one intentional entrance at most, honouring `prefers-reduced-motion`; one icon set at one stroke weight.
- **Components:** button (primary, secondary, quiet), input with label/help/error, surface or card, navigation, plus whatever the brief needs. Specify every state: default, hover, `:focus-visible`, active, disabled, loading, empty, error, success.
- **Imagery and visual anchor:** a front page is a visual experience, not a document. Decide the image strategy and write it down: what kind of visuals (photography, illustration, product UI, diagrams, data, texture or pattern, motion), its art direction (subject, crop, light, color treatment, line weight) and where it comes from, in this order:
  1. the user's real assets
  2. an image-generation tool, if the agent has one, prompted with the art direction
  3. visuals built from the system itself: inline SVG illustration, pattern or diagram drawn in the palette; a real product UI or artefact rendered in HTML (a job ticket, a receipt, a schedule, a parts diagram) with realistic, not lorem, content; data visualisation; type set as image
  4. openly licensed photography with credit
  
  Every visual comes from the subject's world. Plan the page as an alternation of text and visual moments, so no two text-only sections sit back to back. Name the hero pattern (composition.md) and the visual's share of the first screen: at least ~40% on desktop and ~30% on phone.
- **Signature move:** where it appears and where it must not.
- **Copy voice:** 3 do/don't pairs. Copy is part of the design. Write from the user's world and the product's real behaviour: headlines and section titles make a specific claim, not a label ("Brakes bled while you wait", not "Features"). Use only real content and proof. Mark missing facts as placeholders for the user to fill (`[real customer quote]`) rather than inventing stats, logos or testimonials.

## 4. Specimen before pages

Build one specimen page showing the type scale, the palette with contrast ratios, spacing, and every component in every state, in light and dark if both are planned. Review it at a phone width (~390px) **and** a desktop width (~1440px), with screenshots if you can, against the principles and the fingerprint list, fix what fails, and get the user's approval before building real pages. In a non-interactive run, self-review and continue.

## 5. Build from the system

Pages use tokens only, with no raw hex or pixel values outside the tokens file. Meet the current table stakes in [`references/exemplars.md`](references/exemplars.md#how-ux-expectations-are-evolving-20242026) (instant feedback, keyboard paths, system theming). Every page meets these:
- The first screen has a visual anchor that isn't text (image, illustration, product artefact, diagram, data, motion), taking a meaningful share of the viewport on both phone and desktop. A card or table of text styled as an artefact still counts as text: the anchor needs shape, image, illustration or graphic at its core. On phone, keep the anchor inside the first screen. Mechanics: put the visual before the headline in source order (or `order: -1` at the phone breakpoint), size it between `30svh` and `45svh` so the headline and primary action still fit in the same first screen, and re-crop it for portrait; keep it visible on phones rather than `display: none` or shrinking it to an icon. On desktop, size the visual's box to at least ~40% of a 1440×900 first screen. The page alternates text with visual moments, per the image strategy.
- Works and looks intentional at 320–430px (phones), 768px (tablet) and 1280–1920px (desktop). Check the layout at each width, never only the one you happened to build at.
- No horizontal scroll at 320px. Build it in rather than hiding it with `overflow-x: hidden`:
  - grid tracks `minmax(0, 1fr)` and `min-width: 0` on grid/flex children
  - button and tag rows `flex-wrap: wrap`
  - no fixed widths, only `max-width`
  - `overflow-wrap: anywhere` on long words and URLs
  - inline SVGs with a `viewBox`, `width: 100%` / `max-width: 100%` and `height: auto`
  - decorative layers positioned inside a parent with `overflow: clip`
  
  If you can run a browser, at 320px this lists the offenders: `[...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > innerWidth)`.
- One primary action per view, reachable without hunting on mobile. Hierarchy comes from size, weight, space and color, in that order.
- Visible `:focus-visible` (≥2px, 3:1 contrast, never hidden behind sticky UI). Touch targets ≥24×24px, aiming for 44px.
- Forms: visible labels (never placeholder-only), inline errors next to the field, correct `autocomplete` and `inputmode`, paste allowed.
- Loading, empty and error states designed, not left blank.
- Semantic HTML, a `lang` attribute, alt text, and a logical heading order.
- Performance: `font-display: swap`, at most 2 font families and only the weights used, sized images, no layout shift.

## 6. Fingerprint check after building

Re-run [`references/ai-fingerprints.md`](references/ai-fingerprints.md) against the built UI, at both phone and desktop widths. List each hit with its severity. Fix it, or justify it in `DESIGN.md` under `Deliberate exceptions`. Report the remaining hits to the user.
