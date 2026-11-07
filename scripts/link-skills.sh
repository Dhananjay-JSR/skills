#!/usr/bin/env bash
set -euo pipefail

# Symlinks every skill in this repo into each agent's user-level skill dir,
# so `git pull` keeps installed skills up to date.
#   ~/.claude/skills  Claude Code
#   ~/.agents/skills  Codex, OpenCode and other Agent Skills-compatible agents
# Pass dirs as args to override, e.g. `scripts/link-skills.sh ~/.agents/skills`.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
if [ "$#" -gt 0 ]; then DESTS=("$@"); else DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills"); fi

for DEST in "${DESTS[@]}"; do
  mkdir -p "$DEST"
  while IFS= read -r -d '' skill_md; do
    src="$(dirname "$skill_md")"
    target="$DEST/$(basename "$src")"
    # never clobber a real (non-symlink) skill dir the user made themselves
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "skip $target: exists and is not a symlink" >&2
      continue
    fi
    ln -sfn "$src" "$target"
    echo "linked $(basename "$src") -> $DEST"
  done < <(find "$REPO/skills" -name SKILL.md -print0)
done
