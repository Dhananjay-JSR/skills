"""Score benchmark outputs: AI-fingerprint lint, measured mobile/desktop UX, blind vision-judge rating.

  uv run --with playwright evals/design-system/evaluate.py [--no-judge]
Writes out/results.json, out/summary.md and out/gallery.html.
"""
import argparse, base64, colorsys, json, os, random, re, statistics, urllib.request
from collections import defaultdict
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "out"
JUDGE = "anthropic/claude-sonnet-5.5"
DEFAULT_FONTS = {"inter", "roboto", "arial", "open sans", "lato", "poppins", "montserrat", "helvetica",
                 "system-ui", "-apple-system", "sans-serif", "segoe ui"}
NEW_DEFAULT_FONTS = {"space grotesk", "dm sans", "instrument serif", "fraunces"}


def hue_sat(color):
    """(hue degrees, saturation 0-1) for hex/rgb/hsl/oklch strings, or None."""
    c = color.strip().lower()
    if m := re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", c):
        h = m.group(1)
        h = "".join(ch * 2 for ch in h) if len(h) == 3 else h
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    elif m := re.match(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)", c):
        r, g, b = (float(x) / 255 for x in m.groups())
    elif m := re.match(r"hsla?\(\s*([\d.]+)(?:deg)?[,\s]+([\d.]+)%", c):
        return float(m.group(1)) % 360, float(m.group(2)) / 100
    elif m := re.match(r"oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+)", c):
        return float(m.group(3)) % 360, min(float(m.group(2)) / 0.25, 1)  # chroma ~0.25 ≈ fully saturated
    else:
        return None
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s if 0.1 < l < 0.95 else 0


assert round(hue_sat("#6366f1")[0]) in range(235, 245)  # tailwind indigo-500
assert hue_sat("oklch(0.6 0.2 30)")[0] == 30


def lint(html):
    """Static AI-fingerprint hits: list of (severity, name)."""
    low = html.lower()
    hits = []
    grads = re.findall(r"(?:linear|radial|conic)-gradient\(([^;{}]*)\)", low)
    colors_in_grads = re.findall(r"#[0-9a-f]{3,6}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|oklch\([^)]*\)", " ".join(grads))
    if any((hs := hue_sat(c)) and 235 <= hs[0] <= 300 and hs[1] > 0.35 for c in colors_in_grads) \
            or re.search(r"(from|via|to)-(indigo|violet|purple)-", low):
        hits.append((3, "purple/indigo gradient"))
    if re.search(r"background-clip:\s*text", low):
        hits.append((3, "gradient text"))
    if low.count("backdrop-filter") >= 2:
        hits.append((2, "glassmorphism"))
    if re.search(r"repeat\(\s*3\s*,|grid-cols-3", low):
        hits.append((2, "3-column card grid"))
    if any("translatey" in k and "opacity" in k for k in re.findall(r"@keyframes[^{]*\{(.*?)\}\s*\}", low, re.S)):
        hits.append((2, "fade-up keyframes"))
    if re.search(r"#d9775\w|#c96a4\w|#e07a5f", low):
        hits.append((2, "cream+terracotta accent"))
    headings = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", low, re.S)]
    if sum(h in {"features", "how it works", "why choose us", "testimonials", "pricing", "faq", "get started",
                 "frequently asked questions", "what our customers say", "our features"} for h in headings) >= 2 \
            or re.search(r">\s*(open[- ]source|mit licensed|now in beta|new:|backed by)[^<]{0,40}<", low):
        hits.append((3, "stock landing-page copy"))
    if low.count("text-transform: uppercase") + low.count("text-transform:uppercase") >= 3:
        hits.append((1, "uppercase eyebrows"))
    return hits


PROBE = """() => {
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const fam = e => getComputedStyle(e).fontFamily.split(',')[0].replace(/["']/g,'').trim().toLowerCase();
  const h = document.querySelector('h1') || document.body;
  const targets = [...document.querySelectorAll('a,button,input,select,textarea,[role=button]')].filter(vis);
  const small = targets.filter(e => { const r = e.getBoundingClientRect(); return r.width < 24 || r.height < 24; });
  const inputs = [...document.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]),select,textarea')];
  const tinyInputs = inputs.filter(e => parseFloat(getComputedStyle(e).fontSize) < 16);
  const unlabeled = inputs.filter(e => !(e.labels && e.labels.length) && !e.getAttribute('aria-label') && !e.getAttribute('aria-labelledby'));
  return { overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
           targets: targets.length, small_targets: small.length, inputs: inputs.length,
           tiny_inputs: tinyInputs.length, unlabeled: unlabeled.length,
           display_font: fam(h), body_font: fam(document.body),
           lang: !!document.documentElement.lang,
           viewport: !!document.querySelector('meta[name=viewport]') };
}"""


def measure(page, path, shots):
    res = {}
    for name, (w, h) in {"phone": (390, 844), "desktop": (1440, 900), "narrow": (320, 640)}.items():
        page.set_viewport_size({"width": w, "height": h})
        page.goto(path.as_uri(), wait_until="networkidle", timeout=60000)
        res[name] = page.evaluate(PROBE)
        if name in shots:
            page.screenshot(path=str(shots[name]), full_page=False)
    return res


def judge(key, phone_png, desktop_png, brief):
    img = lambda p: {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()}}
    prompt = (f"Brief: {brief}\nThese are the first screen of a landing page on a phone (first image) and a desktop "
              "(second image). Rate 1-10 each, as a demanding senior product designer: distinctiveness (10 = clearly "
              "its own identity, 1 = generic AI template), hierarchy, mobile_ux, desktop_composition, fit_to_brief. "
              'Reply with JSON only: {"distinctiveness":n,"hierarchy":n,"mobile_ux":n,"desktop_composition":n,'
              '"fit_to_brief":n,"note":"one sentence"}')
    body = json.dumps({"model": JUDGE, "max_tokens": 400, "messages": [
        {"role": "user", "content": [{"type": "text", "text": prompt}, img(phone_png), img(desktop_png)]}]})
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body.encode(),
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        text = json.load(r)["choices"][0]["message"]["content"]
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-judge", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY")
    briefs = json.loads((HERE / "briefs.json").read_text())
    pages = sorted(OUT.glob("*/*/*.html"))
    random.Random(0).shuffle(pages)  # judge order shouldn't follow condition
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for f in pages:
            cond, model, brief = f.parts[-3], f.parts[-2].replace("__", "/"), f.stem
            shots = {"phone": f.with_suffix(".phone.png"), "desktop": f.with_suffix(".desktop.png")}
            try:
                m = measure(page, f, shots)
            except Exception as e:
                results.append({"cond": cond, "model": model, "brief": brief, "error": str(e)})
                continue
            html = f.read_text()
            r = {"cond": cond, "model": model, "brief": brief, "hits": lint(html), "m": m,
                 "phone": str(shots["phone"].relative_to(OUT)), "desktop": str(shots["desktop"].relative_to(OUT)),
                 "focus_visible": ":focus-visible" in html, "reduced_motion": "prefers-reduced-motion" in html,
                 "css_vars": len(set(re.findall(r"--[\w-]+\s*:", html)))}
            if key and not a.no_judge:
                try:
                    r["judge"] = judge(key, shots["phone"], shots["desktop"], briefs[brief])
                except Exception as e:
                    r["judge_error"] = str(e)
            results.append(r)
            print(cond, model, brief, "slop", sum(s for s, _ in r["hits"]), r.get("judge", {}).get("distinctiveness"), flush=True)
        browser.close()
    (OUT / "results.json").write_text(json.dumps(results, indent=1))
    summarize(results)


def ux_issues(r):
    ph, nw = r["m"]["phone"], r["m"]["narrow"]
    return (nw["overflow"] + (ph["small_targets"] > 0) + (ph["tiny_inputs"] > 0) + (ph["unlabeled"] > 0)
            + (not r["focus_visible"]) + (not ph["viewport"]) + (not ph["lang"]))


def summarize(results):
    ok = [r for r in results if "m" in r]
    groups = defaultdict(list)
    for r in ok:
        groups[(r["model"], r["cond"])].append(r)
    mean = lambda xs: round(statistics.mean(xs), 1) if xs else "-"
    rows = ["| Model | Cond | Slop score ↓ | UX issues ↓ (of 7) | Distinct fonts (of briefs) | Default font used | Judge: distinct ↑ | hierarchy | mobile | desktop | fit |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for (model, cond), rs in sorted(groups.items()):
        fonts = {r["m"]["desktop"]["display_font"] for r in rs}
        default = sum(r["m"]["desktop"]["display_font"] in DEFAULT_FONTS | NEW_DEFAULT_FONTS for r in rs)
        j = lambda k: mean([r["judge"][k] for r in rs if "judge" in r])
        rows.append(f"| {model} | {cond} | {mean([sum(s for s, _ in r['hits']) for r in rs])} | {mean([ux_issues(r) for r in rs])} "
                    f"| {len(fonts)}/{len(rs)} | {default}/{len(rs)} | {j('distinctiveness')} | {j('hierarchy')} | {j('mobile_ux')} "
                    f"| {j('desktop_composition')} | {j('fit_to_brief')} |")
    for cond in ("baseline", "skill"):
        rs = [r for r in ok if r["cond"] == cond]
        rows.append(f"| **all models** | **{cond}** | **{mean([sum(s for s, _ in r['hits']) for r in rs])}** | **{mean([ux_issues(r) for r in rs])}** "
                    f"| | | **{mean([r['judge']['distinctiveness'] for r in rs if 'judge' in r])}** | | **{mean([r['judge']['mobile_ux'] for r in rs if 'judge' in r])}** "
                    f"| **{mean([r['judge']['desktop_composition'] for r in rs if 'judge' in r])}** | |")
    (OUT / "summary.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))
    cells = []
    for r in sorted(ok, key=lambda r: (r["brief"], r["model"], r["cond"])):
        note = r.get("judge", {}).get("note", "")
        cells.append(f"<figure><figcaption><b>{r['brief']}</b> · {r['model']} · <i>{r['cond']}</i> · slop {sum(s for s,_ in r['hits'])}"
                     f" · {', '.join(n for _, n in r['hits'])}<br><small>{note}</small></figcaption>"
                     f"<div class=row><img class=ph src='{r['phone']}'><img class=dt src='{r['desktop']}'></div></figure>")
    (OUT / "gallery.html").write_text(
        "<!doctype html><meta charset=utf-8><title>design-system benchmark</title><style>body{font:14px system-ui;margin:16px}"
        "figure{margin:0 0 28px}.row{display:flex;gap:8px;align-items:flex-start}.ph{width:195px}.dt{width:720px}"
        "img{border:1px solid #ccc}</style>" + "".join(cells))


if __name__ == "__main__":
    main()
