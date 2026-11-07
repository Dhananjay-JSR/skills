# Dex's Skills

Agent skills for engineers who want to **own** the code their AI writes.

AI agents can build a whole module before you've thought about it once. These skills flip that around: you stay the decision-maker, and you come out of every session able to defend each choice, algorithm and assumption, as if in a thesis viva.

They work in **Claude Code, Codex, OpenCode**, and any agent that supports the open [Agent Skills](https://agentskills.io) `SKILL.md` format.

```bash
npx skills@latest add Dhananjay-JSR/skills
```

## Skills

### [`grill-and-defend`](skills/engineering/grill-and-defend/SKILL.md)
Viva mode for building. Once installed, it applies to any coding task. Small changes pass through quietly, because grilling only kicks in at real design forks (interface, data format, dependency, algorithm or model changes, or anything more than ~1 hour to reverse).

| What happens | Why |
|---|---|
| **Grilling at design forks:** forks are batched into one message, and you commit to an answer *before* seeing the agent's pick. You can skip a fork, but only with a stated reason | Avoids being anchored by the agent's suggestion. Every decision ends up with your own reasoning |
| **Algorithm cards:** for each technique outside standard software engineering, the agent gives its family (e.g. "LoRA: a PEFT fine-tuning method"), what it does, why it was chosen here, where it lives in the code, and terms to search | You know what every piece of the system is, and where to read more |
| **Decision log** (`DECISIONS.md`, or your existing ADR folder): each entry has a one-sentence trade-off summary, the options with pros and cons, a hypothesis, what would prove it wrong, and a pre-mortem. The agent's own assumptions are marked `assumed` | Decisions survive across sessions, and the agent's silent assumptions become visible debts |
| **Viva quiz** after each module: 4 questions on decisions and assumptions, plus 1 code-failure question ("if this hypothesis is wrong, what happens?"). Answers are withheld until you reply, then graded | Recall beats re-reading. Missed questions go into `VIVA.md` and come back in later sessions |
| **Opt-in modes:** *hands-on* (you write the core logic, in real code or pseudocode) and *debugging drill* (say "drill me" and the agent plants a bug for you to find) | Practice the skills that weaken when an AI does all the work |

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
```
When adding a skill, also list it in `.claude-plugin/plugin.json`.

## License
MIT
