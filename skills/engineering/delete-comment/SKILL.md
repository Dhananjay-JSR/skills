---
name: delete-comment
description: "Audit every code comment in a codebase or path: delete tautologies and stale comments, turn excuses into issues, move decision records into ADRs, then add a ratcheting lint rule so comments can't grow back, and estimate the lines shed. Use when asked to delete, clean up, audit or ban code comments, or run /delete-comment."
license: MIT
metadata:
  version: "0.1.0"
---

# Delete comments

Comments rot. A comment that repeats the code doubles what a reader must check. A comment that excuses a hack lets the hack spread, because the next agent reads it as permission. A comment that is no longer true misleads. The few comments worth keeping record a **decision**, and a decision belongs in an ADR, where it has context, options and a date, and is found when someone revisits it.

Scope is the user's: the whole repo, or a path they name. Default to the repo.

## 1. Inventory and estimate

Run the bundled script from the repo root (`scripts/comments.py`, Python stdlib only):

```bash
python3 <skill>/scripts/comments.py estimate <path>            # counts, and lines shed if every comment goes
python3 <skill>/scripts/comments.py list <path> > comments.jsonl  # one JSON line per comment block
```

- It reads tracked files, skips `node_modules`, `vendor`, `dist`, `build`, `*.min.*`, and takes `--exclude 'glob'` for generated code.
- **Not comments, never touched:** tool directives (`eslint-disable`, `@ts-expect-error`, `noqa`, `type: ignore`, `//go:build`, `prettier-ignore`), shebangs, licence and copyright headers, Python docstrings.
- Languages: Python, C-like (JS/TS, Go, Rust, Java, Kotlin, C/C++, C#, Swift, PHP, SCSS), CSS, and `#` languages (shell, Ruby, YAML, TOML, Dockerfile, Makefile). For other languages (HTML, SQL, Lua, ...), find comments by reading the files and say which types the script didn't cover.
- **API doc comments** (JSDoc, rustdoc `///`, Javadoc, Go doc comments): if the project publishes docs or a library API from them, ask before deleting them, and exclude those paths.

Show the estimate before changing anything: comment blocks, lines shed if all go (whole-line comments only; deleting a trailing comment shortens a line but removes none), and the share of total lines.

## 2. Classify each comment

Read each comment **with the code around it**. Put it in exactly one category:

| Category | Test | Examples |
|---|---|---|
| **Tautology** | The code already says it: a name, a type or the next line | `// increment i`, `# loop over users`, a docstring restating the signature |
| **Excuse** | It admits the code is worse than it should be, or asks for leniency | `TODO`, `FIXME`, `HACK`, `XXX`, "workaround", "for now", "temporary", "quick fix", "shortcut:", "should be refactored" |
| **Stale** | It's false now: names a symbol, file, flag, behaviour or version that no longer exists or no longer matches. Commented-out code is stale | `// calls fetchUser()` where `fetchUser` was renamed, `// see v1 API` |
| **Decision record** | It explains a non-obvious **why** the code can't show: a constraint, an external quirk, a rejected alternative, a number's origin | `// Stripe retries for 3 days, so keys must outlive that`, `// O(n²) is fine: n ≤ 20 by schema` |

Check staleness, don't guess it: grep every symbol, path and flag a comment names. When a comment is two categories (a decision with a stale detail), the more useful one wins: record the decision, corrected. When unsure, ask the user in one batch with the comment, its location and your best guess.

## 3. Act on each category

- **Tautology, Stale:** delete. Delete the blank line left behind when it leaves two in a row.
- **Excuse:** delete, and file an issue to fix the hack. One issue per hack, not per comment. Each issue has the location (`path:line`, plus a permalink at the current commit), what the code does now, what it should do, and the deleted comment quoted. Filing is outward-facing, so **list the drafted issues and get a yes first**, then file with `gh issue create` (or the tracker the repo uses). With no tracker, write them to `docs/issues-from-comments.md`.
- **Decision record:** move into an ADR. Use the repo's ADR folder, template and numbering if it has one (`docs/adr`, `doc/adr`, `adr`, `docs/decisions`); otherwise create `docs/adr/NNNN-<slug>.md` with **Context, Decision, Consequences**, plus the code location by `path` and symbol name (not line number, which drifts). Merge comments about the same decision into one ADR. If a name or a test would make the why obvious instead, do that and skip the ADR.

Not every comment has to go in one PR. Do the easy, high-volume ones (tautologies, stale) first; whatever stays is held by the ratchet.

After deleting, run the project's build, type-check and tests. A comment deletion that breaks the build hit a directive or a doc-generation input the script missed: restore it and add its pattern to the exclusions.

## 4. Lint rule with a ratchet

Ban comments in the scope, but don't demand zero today: the **ratchet** freezes the current count per file, and it can only go down.

1. Copy `scripts/comments.py` into the repo (e.g. `scripts/comments.py`), so the check doesn't depend on this skill being installed.
2. Write the baseline after this PR's deletions: `python3 scripts/comments.py baseline <scope> [--exclude ...]`. Commit `.comment-baseline.json`.
3. Wire `python3 scripts/comments.py check` into what already runs on every change, in this order of preference: the existing lint script (`"lint": "... && python3 scripts/comments.py check"`), the pre-commit config, then a CI step. One place is enough.
4. When someone deletes comments, `check --tighten` lowers their files' allowances. Tell the user to run it in the same PR, so the lower number becomes the new ceiling.

`check` fails when any file has more comment lines than its baseline, naming the file and the three ways out (ADR, issue, delete). New files start at zero.

If the project's own linter has a rule that covers part of this, also turn it on, e.g. ESLint `no-warning-comments` (TODO/FIXME) or Ruff `ERA001` (commented-out code). Neither bans all comments, so the ratchet stays.

## 5. Report

End with:
- comments found per category, and what happened to each (deleted, issue #, ADR file)
- lines shed: the estimate from step 1, and the actual `git diff --shortstat` of this PR
- comment lines left, with the baseline committed and where `check` runs
- anything not covered: file types the script skipped, comments you asked the user about

To repeat the process later, run this skill again: the baseline shows where comments remain.
