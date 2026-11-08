# Dex's Skills

Agent skills for engineers who want to **own** the code their AI writes.

AI agents can build a whole module before you've thought about it once. These skills flip that around: you stay the decision-maker, and you come out of every session able to defend each choice, algorithm and assumption, as if in a thesis viva.

They work in **Claude Code, Codex, OpenCode**, and any agent that supports the open [Agent Skills](https://agentskills.io) `SKILL.md` format.

```bash
npx skills@latest add Dhananjay-JSR/skills
```

## Skills

### [`grill-and-defend`](skills/engineering/grill-and-defend/SKILL.md)
Build mode where you stay the decision-maker. It activates automatically on real design work (multi-file features, architecture, algorithms, models, data formats), not on one-line fixes.

| What happens | Why |
|---|---|
| **Grilling at design forks:** forks are batched into one message, and you commit to an answer *before* seeing the agent's pick. You can skip a fork, but only with a stated reason | Avoids being anchored by the agent's suggestion. Every decision ends up with your own reasoning |
| **Algorithm cards:** for each technique outside standard software engineering, the agent gives its family (e.g. "LoRA: a PEFT fine-tuning method"), what it does, why it was chosen here, where it lives in the code, and terms to search | You know what every piece of the system is, and where to read more |
| **Decision log** (`DECISIONS.md`, or your existing ADR folder): each entry has a one-sentence trade-off summary, the options with pros and cons, a hypothesis, what would prove it wrong, and a pre-mortem. The agent's own assumptions are marked `assumed` | Decisions survive across sessions, and the agent's silent assumptions become visible debts |
| **Module quiz** after each module: 4 questions on decisions and assumptions, plus 1 code-failure question ("if this hypothesis is wrong, what happens?"). Answers are withheld until you reply, then graded | Recall beats re-reading. Missed questions go into `STUDY.md` and come back in later sessions |
| **Receipts** for every major claim (optimisations, algorithm or dependency swaps, performance or accuracy claims, hot-path changes): a command you paste to run old vs new side by side (≥10 runs, significance check, noise labelled as noise), printing a fixed table next to the expected result. Critical claims need your own run before they're accepted | Claims become checkable instead of trusted, and stay re-runnable on other machines later |
| **Opt-in modes:** *hands-on* (you write the core logic, in real code or pseudocode) and *debugging drill* (say "drill me" and the agent plants a bug for you to find) | Practice the skills that weaken when an AI does all the work |

Benchmarked on 6 mid-tier models: mentor score 4.3 → 6.9 and mentoring checklist 34% → 90%, with trivial tasks left alone. [Results and limits](evals/grill-and-defend/RESULTS.md).

### [`design-system`](skills/design/design-system/SKILL.md)
Gives every web UI its own design system before any page is built, so it doesn't come out as the generic AI look.
- Takes a brief (audience, 3–5 brand attributes, references), proposes 3 clearly different directions rooted in the product's own world, and audits them against a list of [AI-default fingerprints](skills/design/design-system/references/ai-fingerprints.md), including the *new* defaults models drift to.
- Writes `DESIGN.md` plus three-tier tokens (OKLCH color, a modular fluid type scale, spacing, shape, motion), with every component in every state.
- Mobile and desktop are both first-class: breakpoint tokens and a stated layout per section for each.
- Builds a specimen page for review, then pages from tokens only, against UX rules (focus, touch targets, forms, contrast, states). Finishes with a fingerprint check at phone and desktop widths.
- Learns from [20 exemplar systems](skills/design/design-system/references/exemplars.md) (dev tools, fintech including CRED and Zerodha, creative tools, hardware, GOV.UK), covering both visual and UX choices, and borrows their reasoning, not their look.
- **Benchmarked** on 6 mid-tier models (DeepSeek, GLM, Qwen, Gemini Flash, GPT Luna, Claude Haiku): AI-look score 5.2 → 2.7, measured UX issues 2.8 → 1.4, blind-judged distinctiveness 5.2 → 6.4 and visual richness 4.6 → 5.4. [Results and limits](evals/design-system/RESULTS.md).

### [`readme`](skills/engineering/readme/SKILL.md)
Writes READMEs that are short, specific to the project, and verified against the repo: only the sections the project actually has, no em dashes, no filler, and every command, flag, version and link checked against the source.

## Install

Pick **one** route per agent, or the same skill loads twice.

### Claude Code (plugin, updates itself)
```bash
claude plugin marketplace add Dhananjay-JSR/skills
claude plugin install dex-skills@dex
```

### Codex (plugin)
```bash
codex plugin marketplace add Dhananjay-JSR/skills
codex plugin add dex-skills@dex
```

### OpenCode, Cursor, or any other agent: [skills CLI](https://skills.sh) (manual updates)
```bash
npx skills@latest add Dhananjay-JSR/skills -a <agent>   # e.g. opencode, cursor, windsurf; omit -a to pick interactively
npx skills@latest add Dhananjay-JSR/skills --skill=grill-and-defend   # just one skill
npx skills@latest update                                # pull updates; re-run `add` for new skills
```

### Contributors: symlink install (update with `git pull`)
```bash
git clone https://github.com/Dhananjay-JSR/skills.git ~/dex-skills
~/dex-skills/scripts/link-skills.sh                    # links into ~/.claude/skills and ~/.agents/skills
~/dex-skills/scripts/link-skills.sh ~/.agents/skills   # or pick specific dirs
```
- Codex reads `~/.agents/skills`.
- Claude Code reads `~/.claude/skills`.
- OpenCode reads `~/.config/opencode/skills`, `~/.claude/skills` **and** `~/.agents/skills`. If you use OpenCode, link into only one of those dirs.

## Disabling `grill-and-defend`

To stop the skill, disable or remove the installed skill in your agent:

| Agent | How |
|---|---|
| Claude Code (plugin) | `claude plugin disable dex-skills@dex` (or `enable`). Add `--scope user\|project\|local` to choose where. Disables every skill in this plugin |
| Claude Code (`~/.claude/skills`) | In `settings.json`: `"permissions": { "deny": ["Skill(grill-and-defend)"] }` |
| Codex | In `~/.codex/config.toml`: `[[skills.config]]`, then `name = "grill-and-defend"` and `enabled = false`. Restart Codex |
| OpenCode | In `opencode.jsonc`: `"permissions": [{ "action": "skill", "resource": "grill-and-defend", "effect": "deny" }]` |
| skills CLI installs | `npx skills@latest remove grill-and-defend` |

## Repo layout
```
skills/<category>/<skill-name>/SKILL.md   # one folder per skill, Agent Skills format
.claude-plugin/                           # marketplace + plugin manifests (Claude Code, Codex)
scripts/link-skills.sh                    # symlink installer
evals/<skill>/                            # benchmarks (run.py, evaluate.py, RESULTS.md)
```
When adding a skill, also list it in `.claude-plugin/plugin.json`.

## License
MIT
