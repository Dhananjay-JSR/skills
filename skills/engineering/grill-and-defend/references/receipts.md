# Receipts: tools and template

## Pick the measuring tool by claim
| Claim | Tool | Notes |
|---|---|---|
| A command or program is faster | [`hyperfine`](https://github.com/sharkdp/hyperfine) | `--warmup 3 --runs 10`, one command per variant (`IMPL=old cmd`, `IMPL=new cmd`), `--export-json`/`--export-markdown`. Reports mean ± σ and relative speed |
| Go function is faster | `go test -bench=. -count=10` per variant, then [`benchstat old.txt new.txt`](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat) | Median, confidence interval, Mann-Whitney U. `~` means no significant change |
| Rust function is faster | criterion: `cargo bench -- --save-baseline old`, then `--baseline old` | Reports change with confidence interval |
| Python function is faster | `pytest-benchmark` (`--benchmark-save`, `--benchmark-compare`) or hyperfine around a script | |
| JS/TS function is faster | hyperfine around a script, or `mitata` / `tinybench` | |
| Uses less memory | hyperfine ≥ 2.0 (reports peak memory per command), otherwise `/usr/bin/time -l` (macOS: "maximum resident set size") or `-v` (Linux), repeated per variant | Check `hyperfine --version` |
| Smaller binary, bundle or model | `stat`/`du -b`, bundle analyzer, `size-limit` | Deterministic: one run is enough |
| More accurate | the project's eval script on a fixed, held-out test set | Same seed and data. Report the metric plus sample size |
| Fixes a bug | a test that fails on old and passes on new | The red→green run *is* the receipt |
| Web performance | Lighthouse CI (`lhci autorun`), several runs | Same device profile and throttling |

## Rules
- Same input, same machine, same build mode (release or optimised) for both variants.
- Warm up first; measure at least 10 runs; report median and spread, not a single number.
- A significance check decides "win". Within noise is reported as `~ (noise)`.
- State the expected result **before** running, taken from the decision's Hypothesis.
- Read-only: work in `mktemp -d`, clean up with `trap`, no network side effects, print the estimated runtime first.
- Make it portable: detect macOS vs Linux for `time` flags. Fail with a clear message if a tool is missing, and show the install command.

## Script template (flag-based)
```bash
#!/usr/bin/env bash
# Receipt R<n>: "<claim>" (decision D<m>)
# Expected: <hypothesis number>. If <falsified-if signal>, D<m> is wrong. Runtime: ~<N> min.
set -euo pipefail
command -v hyperfine >/dev/null || { echo "needs hyperfine: brew install hyperfine | cargo install hyperfine"; exit 1; }
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
INPUT=<fixed input file>

hyperfine --warmup 3 --runs 10 -N \
  -n old "env IMPL=old <command> $INPUT" \
  -n new "env IMPL=new <command> $INPUT" \
  --export-json receipts/R<n>.json --export-markdown "$tmp/table.md"

if [[ "$(uname)" == Darwin ]]; then mem() { /usr/bin/time -l "$@" 2>&1 >/dev/null | awk '/maximum resident/{print $1/1048576 " MB"}'; }
else mem() { /usr/bin/time -v "$@" 2>&1 >/dev/null | awk -F: '/Maximum resident/{print $2/1024 " MB"}'; }; fi
echo "| peak RAM | $(IMPL=old mem <command> $INPUT) | $(IMPL=new mem <command> $INPUT) |"
cat "$tmp/table.md"
echo "Machine: $(uname -sm) · $(sysctl -n machdep.cpu.brand_string 2>/dev/null || lscpu | awk -F: '/Model name/{print $2}')"
```

For the worktree fallback, replace the `IMPL` flag with two checkouts: `git worktree add "$tmp/old" <baseline-sha>`, build both, run hyperfine against `"$tmp/old/<bin>"` and `./<bin>`, then `git worktree remove "$tmp/old"` in the trap.
