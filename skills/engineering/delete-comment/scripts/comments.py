#!/usr/bin/env python3
"""Find code comments, estimate the lines deleting them sheds, and ratchet the count down in lint.

Usage:
  comments.py list     [PATH ...] [--exclude GLOB ...]   one JSON line per comment block, for classifying
  comments.py estimate [PATH ...] [--exclude GLOB ...]   counts, and lines shed if every comment goes
  comments.py baseline [PATH ...] [--exclude GLOB ...]   write .comment-baseline.json (scope, excludes, per-file counts)
  comments.py check    [--tighten]                       fail if any file has more comment lines than its baseline;
                                                         --tighten lowers the baseline to the new counts (never raises it)

Tool directives (eslint-disable, @ts-expect-error, noqa, type: ignore, //go:build, shebangs, licence headers, ...)
are not comments here: they're never listed or counted. Python docstrings are strings, not comments.
"""
import fnmatch
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tokenize

BASELINE = ".comment-baseline.json"
C_LIKE = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts", ".go", ".rs", ".java", ".kt", ".kts", ".c",
          ".h", ".cc", ".cpp", ".hpp", ".cs", ".swift", ".scala", ".dart", ".php", ".scss", ".less", ".vue", ".svelte"}
BLOCK_ONLY = {".css"}
HASH = {".sh", ".bash", ".zsh", ".rb", ".yaml", ".yml", ".toml", ".r", ".pl", ".tf"}
HASH_NAMES = {"Dockerfile", "Makefile", "Gemfile", "Rakefile"}
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv", "__pycache__", ".next"}
DIRECTIVE = re.compile(
    r"eslint|@ts-|prettier-ignore|biome-ignore|istanbul|c8 ignore|noqa|type:\s*ignore|pyright:|mypy:|pylint:|"
    r"fmt:\s*(on|off|skip)|isort:|nolint|NOLINT|rubocop:|shellcheck|^\W*go:|^\W*\+build|#region|#endregion|"
    r"SPDX-License|Copyright|coding[:=]|swiftlint:|ktlint|@jsx|@vite-ignore|webpackChunkName|/\s*<reference", re.I)


def c_like(src, line_comments=True):
    """Yields (offset, end_offset) of each // and /* */ comment, skipping string and template literals."""
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'`":
            i += 1
            while i < n and src[i] != c:
                if src[i] == "\\":
                    i += 1
                elif src[i] == "\n" and c != "`":
                    break  # shortcut: Rust lifetimes and char literals end at the line break, which is close enough
                i += 1
            i += 1
        elif line_comments and src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            yield i, j
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            yield i, j
            i = j
        else:
            i += 1


def hash_style(src):
    """Yields # comments that start a line or follow whitespace and sit outside ' and " strings (so $# and ${#x} aren't)."""
    pos = 0
    for line in src.splitlines(keepends=True):
        quote, prev = None, " "
        for k, ch in enumerate(line):
            if quote:
                if ch == quote and prev != "\\":
                    quote = None
            elif ch in "'\"":
                quote = ch
            elif ch == "#" and prev.isspace() and not (pos == 0 and line.startswith("#!")):
                yield pos + k, pos + len(line.rstrip("\n"))
                break
            prev = ch
        pos += len(line)


def python(src):
    starts = [0]
    for line in src.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT and not (tok.start[0] == 1 and tok.string.startswith("#!")):
            at = starts[tok.start[0] - 1] + tok.start[1]
            yield at, at + len(tok.string)


def scanner(path):
    ext = path.suffix.lower()
    if ext == ".py":
        return python
    if ext in C_LIKE:
        return c_like
    if ext in BLOCK_ONLY:
        return lambda s: c_like(s, line_comments=False)
    if ext in HASH or path.name in HASH_NAMES:
        return hash_style
    return None


def comments(path, src):
    """Comment blocks in one file: adjacent whole-line comments merge into one block."""
    found = []
    for start, end in scanner(path)(src):
        text = src[start:end]
        if DIRECTIVE.search(text):
            continue
        line_start = src.rfind("\n", 0, start) + 1
        line_end = src.find("\n", end)
        line_end = len(src) if line_end < 0 else line_end
        own_line = not src[line_start:start].strip() and not src[end:line_end].strip()
        first = src.count("\n", 0, start) + 1
        last = first + text.count("\n")
        prev = found[-1] if found else None
        if own_line and prev and prev["own_line"] and prev["end"] == first - 1:
            prev["end"], prev["text"] = last, prev["text"] + "\n" + text
        else:
            found.append({"file": str(path), "line": first, "end": last, "own_line": own_line, "text": text})
    return found


def files(paths, excludes):
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--", *paths], capture_output=True, text=True, check=True).stdout
        candidates = [pathlib.Path(p) for p in out.split("\0") if p]
    except (subprocess.CalledProcessError, FileNotFoundError):
        candidates = []
        for root in paths:
            for d, dirs, names in os.walk(root):
                dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
                candidates += [pathlib.Path(d, x) for x in names]
    for p in sorted(candidates):
        generated = ".min." in p.name or SKIP_DIRS.intersection(p.parts)
        if p.is_file() and scanner(p) and not generated and not any(fnmatch.fnmatch(p.as_posix(), g) for g in excludes):
            yield p


def scan(paths, excludes):
    result = {}
    for p in files(paths, excludes):
        try:
            result[p.as_posix()] = comments(p, p.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, SyntaxError, tokenize.TokenError):
            print(f"skipped (unreadable or doesn't parse): {p}", file=sys.stderr)
    return result


def lines(blocks):
    return sum(b["end"] - b["line"] + 1 for b in blocks)


def main(argv):
    cmd, args = (argv[0] if argv else "help"), argv[1:]
    excludes = [args[i + 1] for i, a in enumerate(args) if a == "--exclude"]
    paths = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] != "--exclude")] or ["."]

    if cmd == "list":
        for blocks in scan(paths, excludes).values():
            for b in blocks:
                print(json.dumps(b))
    elif cmd == "estimate":
        found = scan(paths, excludes)
        blocks = [b for bs in found.values() for b in bs]
        whole = [b for b in blocks if b["own_line"]]
        code = sum(len(pathlib.Path(f).read_text(encoding="utf-8").splitlines()) for f in found)
        shed = lines(whole)
        print(f"files scanned: {len(found)}, with comments: {sum(1 for bs in found.values() if bs)}")
        print(f"comment blocks: {len(blocks)} ({len(whole)} on their own lines, {len(blocks) - len(whole)} trailing code)")
        print(f"lines shed if every comment goes: {shed} of {code} ({100 * shed / max(code, 1):.1f}%)")
        print("trailing comments shorten lines but don't remove any")
    elif cmd == "baseline":
        counts = {f: lines(bs) for f, bs in scan(paths, excludes).items() if bs}
        data = {"scope": paths, "exclude": excludes, "files": counts}
        pathlib.Path(BASELINE).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        print(f"wrote {BASELINE}: {sum(counts.values())} comment lines in {len(counts)} files")
    elif cmd == "check":
        base = json.loads(pathlib.Path(BASELINE).read_text())
        now = {f: lines(bs) for f, bs in scan(base["scope"], base["exclude"]).items() if bs}
        over = {f: n for f, n in now.items() if n > base["files"].get(f, 0)}
        for f, n in over.items():
            print(f"{f}: {n} comment lines, baseline allows {base['files'].get(f, 0)}. "
                  f"Move a decision into an ADR, file an issue for a workaround, or delete it.")
        if "--tighten" in args:
            base["files"] = {f: min(n, base["files"][f]) for f, n in now.items() if f in base["files"]}
            pathlib.Path(BASELINE).write_text(json.dumps(base, indent=2, sort_keys=True) + "\n")
        print(f"comment lines: {sum(now.values())} now, {sum(base['files'].values())} allowed")
        return 1 if over else 0
    else:
        print(__doc__)
        return 0 if cmd == "help" else 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
