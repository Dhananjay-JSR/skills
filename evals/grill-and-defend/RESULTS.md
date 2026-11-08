# grill-and-defend benchmark

Does the skill make cheaper models act like a mentor (keep the user deciding, reasoning and verifying) instead of just writing code? 6 mid-tier models via OpenRouter, each scenario answered without the skill (**baseline**) and with it as the system prompt (**skill**). Claude Sonnet 5.5 judges each reply blind to the condition: a per-scenario checklist (rubric) and a 1–10 mentor score where 10 also means *not* over-questioning on trivial tasks.

| Scenario | What a good mentor does |
|---|---|
| `fork` | Asks for a design decision (noise suppression approach) with options, mechanism, cost and failure modes, holds back its own pick, explains the technique |
| `no_reason` | The user picks options without reasons: reveal the recommendation and ask a short, pointed "why" |
| `your_call` | The user defers: pick, log it as an assumption with a hypothesis, keep building |
| `trivial` | A variable rename: just do it, no questions |
| `receipt` | "How much faster is it really?": a paste-able old-vs-new command with repeated runs, expected result and a table |
| `quiz` | A module is finished: 5 open questions from the decision log, answers withheld |

Run on 2026-11-08, skill v0.7.2. Generation cost about $0.28 per full run.

| Model | Cond | Mentor score ↑ | Rubric pass ↑ | fork | no_reason | your_call | trivial | receipt | quiz |
|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5.5 | baseline | 5.7 | 38.5% | 3 | 4 | 7 | 9 | 7 | 4 |
| anthropic/claude-haiku-5.5 | skill | 7.7 | 97.2% | 8 | 7 | 8 | 9 | 6 | 8 |
| deepseek/deepseek-v4.1-flash | baseline | 4.3 | 32.4% | 2 | 3 | 4 | 5 | 7 | 5 |
| deepseek/deepseek-v4.1-flash | skill | 7.0 | 93.3% | 8 | 7 | 4 | 7 | 8 | 8 |
| google/gemini-3.8-flash | baseline | 4.0 | 29.0% | 2 | 3 | 4 | 9 | 3 | 3 |
| google/gemini-3.8-flash | skill | 6.7 | 90.6% | 6 | 6 | 5 | 9 | 6 | 8 |
| openai/gpt-6-luna | baseline | 4.2 | 29.0% | 3 | 2 | 5 | 6 | 6 | 3 |
| openai/gpt-6-luna | skill | 6.8 | 82.2% | 8 | 7 | 4 | 6 | 8 | 8 |
| qwen/qwen3.8-omni-flash | baseline | 3.8 | 40.2% | 2 | 2 | 4 | 9 | 3 | 3 |
| qwen/qwen3.8-omni-flash | skill | 7.0 | 91.9% | 6 | 8 | 6 | 9 | 6 | 7 |
| z-ai/glm-5.3-flashx | baseline | 3.8 | 34.6% | 2 | 2 | 4 | 6 | 6 | 3 |
| z-ai/glm-5.3-flashx | skill | 6.0 | 86.9% | 7 | 6 | 5 | 5 | 6 | 7 |
| **all models** | **baseline** | **4.3** | **34.0%** | **2.3** | **2.7** | **4.7** | **7.3** | **5.3** | **3.5** |
| **all models** | **skill** | **6.9** | **90.4%** | **7.2** | **6.8** | **5.3** | **7.5** | **6.7** | **7.7** |

## Findings
- **Mentor behaviour, not just code:** mentor score 4.3 → 6.9 and checklist pass 34% → 90%. Every model improved, and the effect is largest on the fork (2.3 → 7.2) and the end-of-module check (3.5 → 7.7). Without the skill, no model asked the user to decide at the fork (0/6 on every fork criterion). They all just built.
- **No over-triggering:** the trivial rename stays a quiet rename (7.3 → 7.5).
- **Receipts:** with the skill, models give a paste-able old/new command, an expectation and a table far more often (baseline: 1/6 gave a runnable comparison).
- **Weakest score, `your_call` (4.7 → 5.3):** the behaviour does change. Baseline models proceed silently: 0/6 record the decision as an assumption, 1/6 state a hypothesis. With the skill that's 6/6 and 5/6, and 5/6 still make progress on the code. The judge rates deferral modestly in both conditions, since the user opted out of deciding.

## What the benchmark changed in the skill
| Version | Change | Effect |
|---|---|---|
| v0.7.0 | first run | 21/36 replies leaked process words, mostly "viva" via the `VIVA.md` file name |
| v0.7.1 | renamed `VIVA.md` → `STUDY.md`; Voice rule rewritten to name the plain words to use instead of listing banned words; algorithm cards required inside the fork message | leaks 21 → 5; cards at the fork 1/6 → 4/6 |
| v0.7.2 | fixed short shape for the challenge reply (recommendation, difference, 1–2 questions) | "kept it short" 1/6 → 4/6, median reply ~650 → 278 words |

## Limits
- One reply per model × scenario, single judge (same family as one candidate). Judge scores drift by about ±0.5 between identical reruns, so read per-model rows as anecdotes.
- Scenarios are single-turn snapshots of a multi-turn workflow; real sessions with tools and a repo can behave differently.
- The rubric is partly derived from the skill's own rules, so baseline models are judged on behaviour nobody asked them for. The mentor score is the fairer comparison.

## Reproduce
```bash
export OPENROUTER_API_KEY=...
python3 evals/grill-and-defend/run.py      # cached per reply in out/; delete out/skill to rerun the skill side
```
