"""Does grill-and-defend make models mentor instead of just coding? A/B over 6 scenarios.

For every model x scenario, get the next assistant turn without the skill (baseline) and with it (skill),
then a blind judge scores the rubric and a 1-10 mentor score. Writes out/results.json and out/summary.md.

  OPENROUTER_API_KEY=... python3 evals/grill-and-defend/run.py
"""
import json, os, re, statistics, sys, time, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "out"
SKILL = HERE.parent.parent / "skills/engineering/grill-and-defend"
MODELS = ["deepseek/deepseek-v4.1-flash", "z-ai/glm-5.3-flashx", "qwen/qwen3.8-omni-flash",
          "google/gemini-3.8-flash", "openai/gpt-6-luna", "anthropic/claude-haiku-5.5"]
JUDGE = "anthropic/claude-sonnet-5.5"
BASE_SYS = "You are an expert software engineer working as a coding assistant on the user's project."
SKILL_SYS = (BASE_SYS + "\n\nFollow this skill:\n\n" + (SKILL / "SKILL.md").read_text()
             + "\n\n" + (SKILL / "references/receipts.md").read_text()
             + "\n\nYou have no tools in this conversation: reply in text, and show any file you would write.")


def chat(model, messages, key, max_tokens=12000, tries=3):
    body = json.dumps({"model": model, "max_tokens": max_tokens, "reasoning": {"max_tokens": 4000}, "messages": messages})
    for i in range(tries):
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body.encode(),
                                         {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            text = d["choices"][0]["message"]["content"] or ""
            if not text.strip():
                raise ValueError("empty response")
            return text, d.get("usage", {})
        except Exception:  # network/5xx/rate limit/empty: back off and retry
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def judge(key, sc, transcript, reply):
    rubric = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(sc["rubric"]))
    prompt = (f"You are evaluating an AI coding assistant's latest reply.\n\nConversation so far:\n{transcript}\n\n"
              f"Assistant's latest reply:\n<<<\n{reply}\n>>>\n\nFor each criterion, answer true or false:\n{rubric}\n\n"
              "Also rate mentor_score 1-10: 10 = behaves like a senior mentor who keeps the user deciding, reasoning and "
              "verifying, appropriate to the situation (including NOT over-questioning on trivial tasks); "
              "1 = just writes code or answers without engaging the user's judgement.\n"
              'Reply with JSON only: {"criteria":[true,false,...],"mentor_score":n,"note":"one sentence"}')
    text, _ = chat(JUDGE, [{"role": "user", "content": prompt}], key, max_tokens=800)
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))


def job(cond, model, sc, ctx, key):
    f = OUT / cond / model.replace("/", "__") / f"{sc['id']}.json"
    if f.exists():
        return json.loads(f.read_text())
    turns = [{"role": t["role"], "content": t["content"].replace("{context}", ctx)} for t in sc["turns"]]
    msgs = [{"role": "system", "content": SKILL_SYS if cond == "skill" else BASE_SYS}] + turns
    try:
        reply, usage = chat(model, msgs, key)
        transcript = "\n\n".join(f"[{t['role']}]\n{t['content']}" for t in turns)
        j = judge(key, sc, transcript, reply)
    except Exception as e:
        return {"cond": cond, "model": model, "scenario": sc["id"], "error": str(e)}
    r = {"cond": cond, "model": model, "scenario": sc["id"], "reply": reply, "judge": j,
         "pass": sum(map(bool, j["criteria"])) / len(sc["rubric"]), "cost": usage.get("cost", 0)}
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(r, indent=1, ensure_ascii=False))
    return r


def main():
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("set OPENROUTER_API_KEY")
    spec = json.loads((HERE / "scenarios.json").read_text())
    jobs = [(c, m, sc, spec["context"], key) for c in ("baseline", "skill") for m in MODELS for sc in spec["scenarios"]]
    with ThreadPoolExecutor(10) as ex:
        results = list(ex.map(lambda j: job(*j), jobs))
    for r in results:
        if "error" in r:
            print("ERROR", r["cond"], r["model"], r["scenario"], r["error"])
    ok = [r for r in results if "judge" in r]
    (OUT / "results.json").write_text(json.dumps(ok, indent=1, ensure_ascii=False))
    ids = [sc["id"] for sc in spec["scenarios"]]
    mean = lambda xs: f"{statistics.mean(xs):.1f}" if xs else "-"
    g = defaultdict(list)
    for r in ok:
        g[(r["model"], r["cond"])].append(r)
    rows = ["| Model | Cond | Mentor score ↑ | Rubric pass ↑ | " + " | ".join(ids) + " |", "|---|---|---|---|" + "---|" * len(ids)]
    for (m, c), rs in sorted(g.items()):
        by = {r["scenario"]: r for r in rs}
        rows.append(f"| {m} | {c} | {mean([r['judge']['mentor_score'] for r in rs])} | {mean([100 * r['pass'] for r in rs])}% | "
                    + " | ".join(f"{by[i]['judge']['mentor_score']}" if i in by else "-" for i in ids) + " |")
    for c in ("baseline", "skill"):
        rs = [r for r in ok if r["cond"] == c]
        per = [mean([r["judge"]["mentor_score"] for r in rs if r["scenario"] == i]) for i in ids]
        rows.append(f"| **all models** | **{c}** | **{mean([r['judge']['mentor_score'] for r in rs])}** | "
                    f"**{mean([100 * r['pass'] for r in rs])}%** | " + " | ".join(f"**{p}**" for p in per) + " |")
    (OUT / "summary.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))
    print(f"cost (generation): ${sum(r['cost'] for r in ok):.2f}")


if __name__ == "__main__":
    main()
