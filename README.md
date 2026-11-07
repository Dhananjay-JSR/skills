# dex-skills

Dex's agent skills. They work across **Claude Code, Codex and OpenCode** (and any agent that supports the open [Agent Skills](https://agentskills.io) `SKILL.md` format).

| Skill | What it does |
|---|---|
| [`grill-and-defend`](skills/engineering/grill-and-defend/SKILL.md) | Keeps you the decision-maker. The agent grills you at every design fork, gives an "algorithm card" for every technique, logs decisions and its own assumptions in `DECISIONS.md`, and runs a 5-question viva quiz after each module, so you can defend every line of your project |

## Install

### Claude Code (plugin, updates itself)
```bash
claude plugin marketplace add Dhananjay-JSR/dex-skills
claude plugin install dex-skills@dex
```

### Codex (plugin)
```bash
codex plugin marketplace add Dhananjay-JSR/dex-skills
codex plugin add dex-skills@dex
```

### OpenCode, Cursor, or any other agent: [skills CLI](https://skills.sh) (manual updates)
```bash
npx skills@latest add Dhananjay-JSR/dex-skills -a <agent>   # e.g. opencode, cursor, windsurf; omit -a to pick interactively
npx skills@latest add Dhananjay-JSR/dex-skills --skill=grill-and-defend   # just one skill
npx skills@latest update                                    # pull updates; re-run `add` for new skills
```
This copies editable files into your agent's skills folder.

### Any agent: symlink install for contributors (update with `git pull`)
```bash
git clone git@github.com:Dhananjay-JSR/dex-skills.git ~/dex-skills
~/dex-skills/scripts/link-skills.sh                    # links into ~/.claude/skills and ~/.agents/skills
~/dex-skills/scripts/link-skills.sh ~/.agents/skills   # or pick specific dirs
```
- Codex reads `~/.agents/skills`.
- OpenCode reads `~/.config/opencode/skills`, `~/.claude/skills` **and** `~/.agents/skills`. If you use OpenCode, link into only one of those dirs, so the same skill doesn't load twice.
- Claude Code reads `~/.claude/skills`.

Use only one install method per agent (plugin **or** symlink), or the same skill loads twice.

## Layout
```
skills/<category>/<skill-name>/SKILL.md   # one folder per skill, Agent Skills format
.claude-plugin/                           # marketplace + plugin manifests (Claude Code, Codex)
scripts/link-skills.sh                    # symlink installer
```
When adding a skill, also list it in `.claude-plugin/plugin.json`.

## License
MIT
