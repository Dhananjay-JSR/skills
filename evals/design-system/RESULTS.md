# design-system benchmark

A/B test: the same 3 briefs (coffee roaster, B2B fintech, music lessons) given to 6 mid-tier models via OpenRouter, once with a plain prompt (**baseline**) and once with the `design-system` skill as the system prompt (**skill**). Each page is scored three ways:

- **Slop score:** severity-weighted hits from `references/ai-fingerprints.md` that can be detected in code (lower is better).
- **UX issues (of 7):** measured in headless Chromium at 320, 390 and 1440 px: horizontal overflow at 320 px, touch targets under 24 px, input text under 16 px, unlabeled inputs, no `:focus-visible`, no viewport meta, no `lang`.
- **Judge:** Claude Sonnet 5.5 rates phone and desktop screenshots 1–10, blind to the condition.

Run on 2026-11-08 with skill v0.1.0. Generation cost about $0.76.

| Model | Cond | Slop score ↓ | UX issues ↓ (of 7) | Distinct fonts (of briefs) | Default font used | Judge: distinct ↑ | hierarchy | mobile | desktop | fit |
|---|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5.5 | baseline | 5 | 2.7 | 2/3 | 2/3 | 5.3 | 7 | 5.3 | 6.7 | 7 |
| anthropic/claude-haiku-5.5 | skill | 0.7 | 1 | 3/3 | 0/3 | 5.3 | 7.7 | 7 | 5.7 | 7.7 |
| deepseek/deepseek-v4.1-flash | baseline | 6.3 | 2 | 2/3 | 3/3 | 5 | 7.3 | 6.3 | 6.7 | 7.3 |
| deepseek/deepseek-v4.1-flash | skill | 0.3 | 1 | 3/3 | 0/3 | 7 | 7.7 | 7 | 6.3 | 8.3 |
| google/gemini-3.8-flash | baseline | 6.3 | 4 | 2/3 | 0/3 | 4 | 7 | 5.3 | 6.3 | 6.3 |
| google/gemini-3.8-flash | skill | 4.3 | 2 | 2/3 | 0/3 | 6.3 | 7 | 5.3 | 6.7 | 7.7 |
| openai/gpt-6-luna | baseline | 2.7 | 3.3 | 2/3 | 0/3 | 4.7 | 7.7 | 7 | 6.7 | 7.3 |
| openai/gpt-6-luna | skill | 1.7 | 0.7 | 2/3 | 0/3 | 5.7 | 7.7 | 6.7 | 6.7 | 7.3 |
| qwen/qwen3.8-omni-flash | baseline | 7.7 | 2 | 2/3 | 2/3 | 5.3 | 7 | 5.7 | 6 | 7 |
| qwen/qwen3.8-omni-flash | skill | 3.3 | 1 | 3/3 | 0/3 | 7 | 7.7 | 6.7 | 7 | 8 |
| z-ai/glm-5.3-flashx | baseline | 3 | 3 | 1/3 | 3/3 | 4.7 | 7.3 | 7 | 6.3 | 7 |
| z-ai/glm-5.3-flashx | skill | 2.3 | 1 | 3/3 | 0/3 | 6 | 7.3 | 6.3 | 5.7 | 7.3 |
| **all models** | **baseline** | **5.2** | **2.8** | | | **4.8** | | **6.1** | **6.4** | |
| **all models** | **skill** | **2.1** | **1.1** | | | **6.2** | | **6.5** | **6.3** | |

## Findings
- **Fewer AI tells:** slop score 5.2 → 2.1. Purple gradients and gradient text 7 → 0, glassmorphism 8 → 2, uppercase eyebrows 16 → 8, 3-column card grids 17 → 10.
- **Fonts get chosen:** default display fonts in 10/18 baseline pages → 0/18 with the skill. 13 different display faces across the skill pages, vs 6 for baseline.
- **Measured UX improves:** missing `:focus-visible` 10 → 0, inputs under 16 px on mobile 17 → 1, overflow at 320 px 6 → 3.
- **Judge:** distinctiveness 4.8 → 6.2, mobile UX 6.1 → 6.5, desktop composition flat (6.4 → 6.3). The judge's notes on weak skill pages point to empty desktop hero columns and missing imagery. v0.1.1 adds a rule for content-led desktop heroes (not yet re-benchmarked).

## Limits
- Small sample: 3 briefs × 6 models, one sample each. Treat the per-model rows as anecdotes, and the all-model rows as directional.
- One judge, from the same family as one of the candidates (Claude Haiku).
- The touch-target probe counts inline text links, which WCAG 2.5.8 exempts, so it over-reports.
- The fingerprint lint is regex-based and can't see composition, so the "new defaults" (e.g. a warm cream base) are mostly caught by the judge, not the lint.

## Reproduce
```bash
export OPENROUTER_API_KEY=...
python3 evals/design-system/run.py
uv run --with playwright evals/design-system/evaluate.py   # needs: uv run --with playwright python -m playwright install chromium
open evals/design-system/out/gallery.html
```
