# Workspace design system: Graphite Studio

**Brief.** A local workspace for long agent sessions: notes (markdown source and preview), an Excalidraw board, the agent's questions, and AI research. It's for one engineer, reading and deciding for hours, often at night. Attributes: **calm, focused, low-glare, precise, quiet**. Dark only.

**Direction.** *A quiet editing suite:* neutral graphite, one soft sky-blue light, and a serif for reading. The runners-up were Night Desk (blue slate with lamp amber) and Chalkboard (green slate with mint, Atkinson Hyperlegible).

**Signature move.** Focus lighting: the pane you're working in is lit by a 1px accent edge, and every other pane dims to 55%, so the eye has one place to rest. Hovering or focusing a dimmed pane lights it up. Never apply it inside a pane (no dimmed text within the active pane).

## Principles
1. **Reading comfort over density.** Reading text is 17–18px serif at 1.7 leading, with a 62ch measure.
2. **One light in the room.** Sky blue marks only the active pane, the primary action and links. Status colours appear only for status.
3. **Flat and quiet.** Hairline borders, no shadows, no gradients, no glow.
4. **Calm motion.** Transitions are 120–200ms and only acknowledge an action; nothing animates on its own.

## Tokens
See `tokens.css`. Components use semantic roles only.

| Role | Value | Why |
|---|---|---|
| bg / surface / raised | graphite L 0.20 / 0.235 / 0.27, chroma 0.006 | Near-neutral, so there's no colour cast to tire the eye. Depth comes from lighter surfaces, not shadows |
| text / muted | L 0.92 / 0.68 | Off-white rather than pure white, which cuts glare. Contrast is 14.3:1 for text and 5.8:1 for muted |
| accent / on-accent | sky L 0.79 C 0.085 h 230 / L 0.21 | Soft and low-chroma, not neon. 8.8:1 on surface; button text 9.3:1 |
| border | L 0.32 (1.3:1) | Decorative dividers only. Inputs use the `muted` border (5.8:1) to meet WCAG 1.4.11 |

**Type.**
- Source Serif 4 for notes preview, questions and research answers: an optical-size serif built for screens.
- Hanken Grotesk for UI: a quiet grotesk, so we're not leaning on the default Inter.
- JetBrains Mono for markdown source.
- Scale: 14 / 15 / 17–18 / 20–22.

**Space.** 4px base (4 · 8 · 12 · 16 · 20 · 28 · 40). Spacing is 16px between panes and 18–20px inside cards.

**Shape.** 8px radius outside, 6px inside (nested radius = outer − padding).

## Layout
- **Desktop (≥ 1024px):** `minmax(0,1fr) 380px`. The main pane holds Notes (source and preview split 1:1) and Board tabs; the right rail stacks Questions over Research. The rail hides on demand (`]`), and Notes goes full width.
- **Tablet (768–1023px):** the rail becomes a drawer that opens from a "1 waiting" pill in the top bar.
- **Phone (< 768px):** one column, tabs at the top (Notes · Board · Questions · Research). Notes shows the preview only, with an edit toggle. Inputs are ≥ 16px.

## Components and states
- **Option button:** default raised + border, hover border muted, selected border accent, `:focus-visible` 2px accent ring. Minimum height 44px.
- **Primary button (Send / Ask):** accent fill, on-accent text; hover L −0.04; disabled 45% opacity; loading shows "Asking…" with the button kept the same width.
- **Input / textarea:** raised fill, `muted` 1.5px border, accent on focus. Labels are always visible.
- **Research card:** the answer in serif, sources in UI type with accent links. While loading, a skeleton of 3 muted lines (no spinner). On error, a danger-coloured line plus "Try again".
- **Empty states:** Notes shows "Write here. The agent reads this file too." Board shows a faint hint to press `P` for pen. Questions shows "Nothing waiting."

## Copy voice
| Do | Don't |
|---|---|
| "1 waiting on you" | "You have pending items!" |
| "Asking OpenRouter…" | "Our AI is thinking ✨" |
| "Saved to notes.md" | "Changes saved successfully!" |

## Deliberate exceptions
- No visual anchor or hero imagery. This is a tool, not a front page; the board itself is the visual surface.
