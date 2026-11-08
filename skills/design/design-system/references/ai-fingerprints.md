# AI-default fingerprints

Patterns that make a UI read as generic AI output. Severity: **3** = an instant tell, **2** = a strong tell, **1** = a tell in combination with others. A hit is allowed only with a written reason in `DESIGN.md` under `Deliberate exceptions`.

## Classic defaults
| Sev | Fingerprint | Instead |
|---|---|---|
| 3 | Indigo, violet or purple-to-blue gradients, especially on white (Tailwind `indigo-500` and its neighbours) | A palette derived from the subject's world, with one accent |
| 3 | Gradient text (`background-clip: text`) on headlines | Hierarchy from scale, weight or a real type treatment |
| 3 | Centered hero (headline, subline, two buttons) followed by 3 identical icon-topped feature cards | A layout driven by the content: asymmetric, editorial, list, timeline, product-first |
| 3 | Neon or cyan glow on near-black, glassmorphism (`backdrop-filter: blur`) everywhere | Depth from value steps and material, glass only where it means something |
| 3 | **Stock AI landing-page copy.** It describes the page or product metadata instead of speaking to the user's problem: a pill above the hero ("Open source", "MIT licensed", "v2.0 is here →", "Now in beta ✨", "Backed by …"), section titles that only name the section type ("Features", "How it works", "Why choose us", "Testimonials", "Get started"), tech-stack bragging ("Built with Next.js & Tailwind"), and invented stats, logos or testimonials ("10k+ developers", "99.9% uptime") | Headlines and section titles that say something specific about the user's job or the product's real behaviour. Real proof only (actual numbers, quotes, artefacts), otherwise leave proof out. Metadata like license and version belongs in the footer or docs |
| 2 | Fonts nobody chose: Inter, Roboto, Arial, Open Sans, Lato, Poppins, Montserrat, or the bare system stack as the brand face | A face picked for character, with a stated reason |
| 2 | One radius and one soft grey shadow on every element, cards nested in cards | A shape and elevation scale that follows the direction |
| 2 | Hero metric block: a big number, a small label, a row of stats, a gradient accent | Evidence shown in context (quotes, real artefacts, specifics) |
| 2 | Fade-and-slide-up on every section, hover lift on every card, bounce or elastic easing | One intentional entrance at most; motion that explains a change |
| 2 | Every section the same: centered, equal padding, the same width | Varied rhythm and alignment with a reason |
| 1 | Monospace used only to look "techy", all-caps eyebrow label above every heading | Mono only for real code or data |
| 1 | Highlighting one word in the headline in the accent color, arrows appended to every button | Emphasis that the copy earns |
| 1 | Every button styled primary, pure `#000`/`#fff` backgrounds | One primary action per view, tinted neutrals |
| 1 | Generic stock icons dropped above every heading, emoji as icons | Icons only where they aid scanning, one consistent set |
| 3 | **Wall of text front page**: headline, paragraph, buttons, then more text sections with no visual anchor | An image strategy: a real visual on the first screen, alternating text and visual moments |
| 2 | Generic visuals standing in for real ones: unDraw-style flat people, isometric 3D blobs, "person smiling at laptop" stock photos, a fake dashboard full of lorem data | Visuals from the subject's world: its objects, places, artefacts, real product UI with realistic content |

## New defaults (what models drift to when told to avoid the above)
| Sev | Fingerprint |
|---|---|
| 2 | Warm cream background with a terracotta or rust accent (around `#D97757`) |
| 2 | Near-black with an acid green or lime accent |
| 2 | "Editorial broadsheet": serif headline, hairline rules, small caps, newspaper columns, on a product that isn't editorial |
| 2 | Space Grotesk, DM Sans, Instrument Serif or Fraunces as the automatic "interesting" choice |
| 1 | Grain or noise overlay plus a blurred gradient blob as decoration |

If a direction lands in this table, it is still a default. Go back to the subject's own world for the idea.

Sources: [Anthropic, Improving frontend design through skills](https://www.claude.com/blog/improving-frontend-design-through-skills); [anthropics/skills frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design); [pixelslop pattern catalog](https://cdn.jsdelivr.net/npm/pixelslop@0.3.8/dist/skill/resources/ai-slop-patterns.md); [Why every AI site is purple](https://prg.sh/ramblings/Why-Your-AI-Keeps-Building-the-Same-Purple-Gradient-Website).
