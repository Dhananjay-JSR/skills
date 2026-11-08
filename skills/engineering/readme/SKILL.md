---
name: readme
description: "Write or rewrite a project's README so it is short, accurate and specific to the project: what it is, how to install, use and build it, verified against the repo. Use when asked to create, write, update, rewrite or review a README."
license: MIT
metadata:
  version: "0.1.0"
---

# README

A README is the **entry point** to a project. It answers four things fast: what this is, whether it's for me, how to get it running, and where to go next. Everything in it must be **true for this repo** and specific to it. Depth (tutorials, full reference, design rationale) lives in docs, `CONTRIBUTING.md` or `CHANGELOG.md`, and the README links to it.

## 1. Read the repo first

Before writing a line, collect the facts from the source of truth:
- manifests: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `Dockerfile`, CI config
- entry points: CLI definitions (argparse, clap, commander), exported API, scripts
- real install channels: is it published on npm, PyPI, crates.io, Homebrew? Check, don't assume.
- runtime and versions: `engines`, `requires-python`, `rust-version`, `.nvmrc`
- existing docs, the `LICENSE` file, and any `CONTRIBUTING`, `CHANGELOG` or docs site

If an existing README is present, keep what is accurate and the author's voice. Rewrite only what is wrong, missing or bloated.

## 2. Structure: only sections the project actually has

In this order, skipping any that don't apply:

1. **Name + one sentence:** what it does and for whom. A reader decides relevance from this line.
2. **One example or screenshot** of it working, if that shows more than words (CLI output, UI, API call).
3. **Install:** exact commands for the real channels, plus build-from-source if that's the main path.
4. **Usage:** the smallest copy-pasteable example that works, with its real output.
5. **Configuration:** only the options people actually need. Link to the full reference rather than pasting `--help`.
6. **Development:** how to build, test and run locally, using the repo's real scripts.
7. **Links:** docs, changelog, contributing, only to files and sites that exist.
8. **License:** one line that matches `LICENSE`.

Add a project-specific section only when the project has something the reader must know, e.g. "Architecture" for a system with several services, or "Limitations" for a tool with sharp edges. A table of contents only earns a place in a long README (roughly 150+ lines).

## 3. Voice

Write like a senior engineer explaining the project to a peer: plain, direct, concrete.
- Say it once. Each fact appears in one place, and the reader is trusted to know their tools.
- Show, then tell: a command and its output beat a paragraph about it.
- Use specifics instead of adjectives: "parses 1 GB of logs in 3 s on a laptop" instead of "blazing fast".
- Punctuate with commas, colons, parentheses and full stops. **Never use em dashes (—) or en dashes used as dashes.**
- Keep headings plain words. Emoji only if the project's own brand uses them.

## 4. Cut these on sight

They signal filler or an unedited AI draft:
- Generic adjective features: "robust", "seamless", "powerful", "lightweight", "easy to use", "blazing fast"
- Hype: "revolutionize", "effortlessly", "whether you're a beginner or an expert", "unlock"
- Boilerplate sections with nothing project-specific: "Contributing: PRs welcome!", "Support", "Acknowledgements", "Roadmap", "FAQ"
- Sections for things the project doesn't have: Docker, API, tests, screenshots, deployment
- Badge walls: keep at most real CI and version badges
- Obvious steps: "make sure Git is installed", a separate `cd` explanation, "open your terminal"
- Closings and summaries: "Happy coding!", "In conclusion", a "Why X?" that repeats the opening line
- Placeholders: `yourusername`, `TODO`, a guessed license

## 5. Verify before finishing

Every claim must trace to the repo:
1. Every command maps to a real script, Makefile target, entry point or CLI definition. Run it when you can; otherwise find it in the source.
2. Every flag, env var, config key and path exists (grep it).
3. Versions match the manifests. Install channels match where the package is actually published.
4. Example output comes from a real run, or the output is left out.
5. Links resolve to files or sites that exist. The license matches `LICENSE`.
6. Anything you can't confirm is left out, or listed for the user as an open question. Never guess.

Finish with a scan for em dashes and for every item in §4, then report to the user what you verified and anything you couldn't.
