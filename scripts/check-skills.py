#!/usr/bin/env python3
"""Repo check: every skill folder is listed in .claude-plugin/plugin.json, and every SKILL.md has valid front matter."""
import json
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
listed = {(root / p).resolve() for p in json.loads((root / ".claude-plugin/plugin.json").read_text())["skills"]}
found = {p.parent.resolve() for p in (root / "skills").rglob("SKILL.md")}
errors = [f"not in plugin.json: {p.relative_to(root)}" for p in sorted(found - listed)]
errors += [f"listed but has no SKILL.md: {p.relative_to(root)}" for p in sorted(listed - found)]
for skill in sorted(found):
    text = (skill / "SKILL.md").read_text()
    head = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = head.group(1) if head else ""
    name = re.search(r"^name:\s*(\S+)", meta, re.M)
    if not name or name.group(1) != skill.name:
        errors.append(f"{skill.name}: front matter name must be {skill.name!r}")
    if not re.search(r"^description:\s*\S", meta, re.M):
        errors.append(f"{skill.name}: missing description")
    if not re.search(r'^\s+version:\s*"\d+\.\d+\.\d+"', meta, re.M):
        errors.append(f"{skill.name}: missing metadata.version")
print("\n".join(errors) or f"ok: {len(found)} skills")
sys.exit(1 if errors else 0)
