"""A/B benchmark: does the design-system skill change what models generate?

For every model x brief, generate one landing page with a plain prompt (baseline) and one with
the skill loaded as system prompt (skill). Outputs go to out/<cond>/<model>/<brief>.html.

  OPENROUTER_API_KEY=... python3 evals/design-system/run.py [--models a,b] [--briefs coffee]
"""
import argparse, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
SKILL = HERE.parent.parent / "skills/design/design-system"
MODELS = ["deepseek/deepseek-v4.1-flash", "z-ai/glm-5.3-flashx", "qwen/qwen3.8-omni-flash",
          "google/gemini-3.8-flash", "openai/gpt-6-luna", "anthropic/claude-haiku-5.5"]
TASK = ("Build a polished single-file landing page (HTML with embedded CSS; Google Fonts allowed; "
        "no JS frameworks) for: {brief}\nOutput only the complete HTML document.")
SKILL_SYS = (
    (SKILL / "SKILL.md").read_text() + "\n\n" + (SKILL / "references/ai-fingerprints.md").read_text()
    + "\n\nThis is a non-interactive run: ask no questions and use no tools. Follow the skill end to end, "
    "and deliver a single HTML file. Put the DESIGN.md content (brief, chosen direction, tokens, deliberate "
    "exceptions) in an HTML comment at the top, then the landing page built from those tokens.")
BASE_SYS = "You are an expert frontend developer."


def call(model, system, user, key, tries=3):
    body = json.dumps({"model": model, "max_tokens": 64000, "reasoning": {"max_tokens": 8000},
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
    for i in range(tries):
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body.encode(),
                                         {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            text = d["choices"][0]["message"]["content"] or ""
            if "</html>" not in text.lower():  # truncated, reasoning ate the budget, or refusal: retry
                raise ValueError(f"no complete HTML in response ({d.get('usage', {}).get('completion_tokens')} tokens)")
            return text, d.get("usage", {})
        except Exception as e:  # network/5xx/rate limit: back off and retry
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def extract_html(text):
    m = re.search(r"```(?:html)?\s*(.*?)```", text, re.S)
    text = m.group(1) if m and "<html" in m.group(1).lower() else text
    i = text.lower().find("<!doctype")
    i = i if i >= 0 else text.lower().find("<html")
    return text[i:] if i >= 0 else text


def job(cond, model, brief_id, brief, key):
    out = HERE / "out" / cond / model.replace("/", "__") / f"{brief_id}.html"
    if out.exists():
        return cond, model, brief_id, "cached", {}
    sys_prompt = SKILL_SYS if cond == "skill" else BASE_SYS
    try:
        text, usage = call(model, sys_prompt, TASK.format(brief=brief), key)
    except Exception as e:
        return cond, model, brief_id, f"error: {e}", {}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(extract_html(text))
    out.with_suffix(".usage.json").write_text(json.dumps(usage))
    return cond, model, brief_id, "ok", usage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--briefs", default="")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("set OPENROUTER_API_KEY")
    briefs = json.loads((HERE / "briefs.json").read_text())
    if a.briefs:
        briefs = {k: v for k, v in briefs.items() if k in a.briefs.split(",")}
    jobs = [(c, m, b, t, key) for c in ("baseline", "skill") for m in a.models.split(",") for b, t in briefs.items()]
    with ThreadPoolExecutor(a.workers) as ex:
        for cond, model, b, status, usage in ex.map(lambda j: job(*j), jobs):
            print(f"{cond:8} {model:32} {b:8} {status} {usage.get('completion_tokens', '')}", flush=True)


if __name__ == "__main__":
    main()
