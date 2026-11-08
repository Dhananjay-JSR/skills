# design-system benchmark

A/B test: the same 3 briefs (coffee roaster, B2B fintech, music lessons) given to 6 mid-tier models via OpenRouter, once with a plain prompt (**baseline**) and once with the `design-system` skill as the system prompt (**skill**). Each page is scored three ways:

- **Slop score:** severity-weighted hits from `references/ai-fingerprints.md` that can be detected in code (lower is better).
- **UX issues (of 7):** measured in headless Chromium at 320, 390 and 1440 px: horizontal overflow at 320 px, touch targets under 24 px, input text under 16 px, unlabeled inputs, no `:focus-visible`, no viewport meta, no `lang`.
- **img/svg ≥15%:** pages whose first screen is at least 15% images or SVG. This misses visuals built from HTML/CSS, so read it together with the judge's visual richness.
- **Judge:** Claude Sonnet 5.5 rates phone and desktop screenshots 1–10, blind to the condition: distinctiveness, hierarchy, mobile UX, desktop composition, fit to brief, visual richness.

Run on 2026-11-08 with skill v0.2.1. Each model gets an 8k-token reasoning budget and a 64k-token output cap.

| Model | Cond | Slop score ↓ | UX issues ↓ (of 7) | img/svg ≥15% (phone · desktop) | Distinct fonts (of briefs) | Default font used | Judge: distinct ↑ | hierarchy | mobile | desktop | fit | visual richness ↑ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5.5 | baseline | 5 | 2.7 | 1/3 · 1/3 | 2/3 | 2/3 | 5.7 | 7.7 | 6.7 | 7.3 | 7.7 | 4.7 |
| anthropic/claude-haiku-5.5 | skill | 1.3 | 1.7 | 1/3 · 0/3 | 3/3 | 0/3 | 7 | 7.7 | 6.3 | 7.3 | 8.3 | 6.3 |
| deepseek/deepseek-v4.1-flash | baseline | 6.3 | 2 | 1/3 · 1/3 | 2/3 | 3/3 | 5.7 | 7.7 | 6.7 | 6.7 | 7.7 | 5.7 |
| deepseek/deepseek-v4.1-flash | skill | 1.7 | 1 | 2/3 · 2/3 | 3/3 | 0/3 | 7.3 | 6.3 | 5.3 | 6.7 | 7.7 | 6 |
| google/gemini-3.8-flash | baseline | 6.3 | 4 | 0/3 · 1/3 | 2/3 | 0/3 | 4 | 6.7 | 5 | 6.3 | 6 | 2.7 |
| google/gemini-3.8-flash | skill | 5 | 2.7 | 0/3 · 1/3 | 3/3 | 0/3 | 6 | 6.7 | 4.7 | 7 | 7 | 3.7 |
| openai/gpt-6-luna | baseline | 2.7 | 3.3 | 2/3 · 2/3 | 2/3 | 0/3 | 5.3 | 8 | 7 | 7.7 | 7.7 | 6.3 |
| openai/gpt-6-luna | skill | 1 | 0.7 | 1/3 · 2/3 | 3/3 | 0/3 | 6 | 8 | 7.7 | 7 | 8 | 7 |
| qwen/qwen3.8-omni-flash | baseline | 7.7 | 2 | 0/3 · 1/3 | 2/3 | 2/3 | 6 | 7.3 | 5.7 | 6.7 | 7.7 | 4.7 |
| qwen/qwen3.8-omni-flash | skill | 4 | 1.3 | 0/3 · 1/3 | 2/3 | 0/3 | 6.3 | 7.7 | 6.7 | 6.3 | 8 | 5.3 |
| z-ai/glm-5.3-flashx | baseline | 3 | 3 | 0/3 · 0/3 | 1/3 | 3/3 | 4.7 | 7.3 | 6.3 | 6 | 6.7 | 3.3 |
| z-ai/glm-5.3-flashx | skill | 3 | 1.3 | 0/3 · 1/3 | 3/3 | 0/3 | 6 | 7.3 | 6.3 | 5.7 | 7.7 | 4 |
| **all models** | **baseline** | **5.2** | **2.8** | **4/18 · 6/18** | | | **5.2** | | **6.2** | **6.8** | | **4.6** |
| **all models** | **skill** | **2.7** | **1.4** | **4/18 · 7/18** | | | **6.4** | | **6.2** | **6.7** | | **5.4** |

## Findings (v0.2.1)
- **Fewer AI tells:** slop score 5.2 → 2.7. Purple gradients and gradient text 7 → 0, glassmorphism 8 → 2, uppercase eyebrows 16 → 8, 3-column card grids 17 → 12.
- **Fonts get chosen:** default display fonts in 10/18 baseline pages → 0/18 with the skill.
- **Measured UX improves:** UX issues 2.8 → 1.4. Missing `:focus-visible` 10 → 0, inputs under 16 px on mobile 17 → 2. Overflow at 320 px did not improve (6 → 7), mostly from wide inline SVG illustrations.
- **Judge:** distinctiveness 5.2 → 6.4 and visual richness 4.6 → 5.4. Mobile UX (6.2) and desktop composition (6.8 → 6.7) are flat. The gains hold on all three briefs (distinctiveness: coffee 5.0 → 6.3, fintech 4.8 → 6.2, music 5.8 → 6.8).
- **Front pages are richer but not yet rich:** 5.4/10 visual richness means many first screens still lean on text. In this benchmark the models can only draw with SVG/HTML. Real projects with photography or an image-generation tool should do better.

## Contamination found and fixed
v0.2.0 used a coffee-roaster example inside the skill ("roasted Tuesday, at your door Friday", kraft paper, roast curves), and coffee is one of the benchmark briefs. One model copied the example headline almost verbatim. v0.2.1 moved every example to a domain the benchmark doesn't use (a bicycle repair shop), and the numbers above come from that clean version. Keep skill examples out of the benchmark domains.

## History
| Version | Slop ↓ | UX issues ↓ | Distinct ↑ | Visual richness ↑ | Note |
|---|---|---|---|---|---|
| baseline | 5.2 | 2.8 | 5.2 | 4.6 | |
| v0.1.0 | 2.1 | 1.1 | 6.2 | n/a | judge scale before the visual-richness score was added |
| v0.2.0 | 2.8 | 1.3 | 6.7 | 5.5 | contaminated by a coffee example |
| v0.2.1 | 2.7 | 1.4 | 6.4 | 5.4 | clean |

## Limits
- Small sample: 3 briefs × 6 models, one sample each. Treat the per-model rows as anecdotes, and the all-model rows as directional. Judge scores move by about ±0.5 between identical reruns.
- One judge, from the same family as one candidate (Claude Haiku).
- The touch-target probe counts inline text links, which WCAG 2.5.8 exempts, so it over-reports.
- The fingerprint lint is regex-based and can't see composition. "New defaults" such as a warm cream base are mostly caught by the judge.

## Reproduce
```bash
export OPENROUTER_API_KEY=...
python3 evals/design-system/run.py
uv run --with playwright python -m playwright install chromium   # once
uv run --with playwright evals/design-system/evaluate.py
open evals/design-system/out/gallery.html
```
