---
name: review-spec
description: "Write a review spec: the contract a human or AI reviewer checks a PR or PR stack against (numbered rules with where each is enforced and which test proves it, the complete list of intended behaviour changes, accepted limitations, already-resolved findings, verification commands, and Mermaid diagrams rendered and linked to Mermaid Live). Use when asked for a review doc, reviewer guide, review spec or PR handover for a change that is ready for review."
license: MIT
metadata:
  version: "0.1.0"
---

# Review spec

A review spec is a **contract**, not a tour. Reviewers, often agents, don't read the code front to back; they check it against claims. So every claim must be checkable:
- a rule with an ID;
- the exact place the rule is enforced;
- the test or command that proves it.

Write for that reader:
- no persuasion, no open questions, no "please look at";
- an open question is a decision to settle before writing, not a section;
- anything the reviewer must ignore is listed explicitly, so it isn't reported.

The layout is in [references/template.md](references/template.md). Follow it section by section.

## Steps

### 1. Collect the facts from the change itself

Run against the head of the change (the top branch of a stack):
- **The stack map:** for each PR, its branch, base, code lines changed versus test lines (`git diff --shortstat <base> <branch> -- . ':!tests'`), and its commits.
- **Every public surface the change touches:** request fields, response shape, webhooks, CLI flags, env vars, migrations, queues, infra.
- **Line references:** `grep -n` for each function a rule will point at. References are taken at the head commit; say so in the doc.
- **Test names:** list them all (`grep -n "def test_\|it(\|describe("`) so each rule can cite one.
- **Evidence:** CI status per PR, plus any live runs, migration runs or exports you did. Each with its real output.

Done when every surface in the diff is either covered by a rule (step 2) or is an intended change (section 4 of the template).

### 2. Write the rules

One table row per rule: `ID | Rule | Enforced at | Proved by`.
- **ID:** a short prefix per group plus a number (BC-1 for backward compatibility, SEC-2 for security). Reviewers cite IDs in findings.
- **Rule:** one observable statement that can be true or false. "A request without `engine` is queued on `QUEUE_NAME`", not "routing works".
- **Enforced at:** `path:line` plus the function name, at the head commit.
- **Proved by:** an exact test name, a command, or "Read the code". Where nothing proves it, write **No direct test** in bold; never leave the reviewer to discover the gap.

Always include a **backward-compatibility** group: what existing callers, workers, deploys and old code running mid-deploy rely on, and why each still holds. This is the group reviewers need most.

### 3. Write the boundaries

- **Intended behaviour changes:** a numbered, *complete* list. State that anything else changing behaviour is a finding.
- **Accepted limitations:** each with its reason (a product decision, an external constraint, pending access). These are not to be reported.
- **Already-resolved findings:** from bots, CI or earlier reviews, each with its fix. These are not to be reported again.
- **Not yet verified:** each with why, and when it will be.

### 4. Draw the diagrams

Draw only diagrams that carry a rule or a flow the reader needs:
- a sequence diagram for the main request flow;
- a flowchart for each state machine or safety net (timeouts, retries, fallbacks).

Rules that keep Mermaid rendering:
- quote any label containing parentheses, colons or slashes: `A["GET /result (1 h)"]`;
- use `<br/>` for line breaks in labels;
- keep `;` out of sequence-diagram messages.

Then render and link every diagram:

```bash
python3 scripts/mermaid.py <doc.md> --render   # renders each block with mermaid-cli; non-zero exit on a syntax error
python3 scripts/mermaid.py <doc.md>            # prints a Mermaid Live edit link per diagram
```

Put each diagram's Mermaid Live link directly under it ("Open in Mermaid Live"), so a reader can zoom or edit it. Rendering needs Node (`npx` fetches `@mermaid-js/mermaid-cli`).

### 5. Verify the spec against the code

Re-check every rule before publishing; a reviewer agent will, and one false rule discredits the rest.
- `grep` each **Enforced at** reference and confirm the line still matches (rebases move lines).
- Run each "only here" or "never" claim as a search. For example, "every final status goes through `finish()`" means grepping for status assignments and listing any exception in the rule itself.
- Run the verification commands from the doc exactly as written.

Done when every rule has been checked against the head commit and every command in the doc has run clean.

### 6. Publish

Write the spec as Markdown (in the repo's docs or next to the PRs). If it also goes to Google Docs or another editor:
- leave a blank line before every list, or converters merge the bullets into the paragraph;
- before replacing an existing doc, check for edits and comments made since your last version, and edit those sections in place instead of overwriting;
- read the published doc back and check the lists, tables and images.

## Voice

- Use present-tense facts: "The callback returns 401 when...".
- Put names exactly as they appear in the code, in backticks.
- Write numbers with units and sources: "about 6,500 calls a day (production DB, 13 to 23 Nov)".
