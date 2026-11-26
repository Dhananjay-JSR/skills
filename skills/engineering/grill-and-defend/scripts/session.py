#!/usr/bin/env python3
"""Session page: a calm local reading view for the agent's explanations and questions.

The agent writes markdown to .grill/session.md; this serves it as a live page and collects answers.

  python3 session.py serve [--dir .grill] [--port 4711]   # start (run in background); prints the URL
                                                          # the page is the workspace: notes, board, questions, research
                                                          # first run downloads the pinned libraries in vendor.json
                                                          # research needs OPENROUTER_API_KEY (env or <dir>/.env)
  python3 session.py url    [--dir .grill] [--at D20]      # URL of the running page, optionally a deep link
  python3 session.py wait-ask [--dir .grill]                # block until the user asks something the server didn't answer itself
  python3 session.py reply ID [--dir .grill] < answer.md     # post the agent's full answer to an ask
  python3 session.py wait   [--dir .grill] [ID ...] [--timeout 900]
                                                          # block until those questions (or any new one) are answered,
                                                          # then print the answers as JSON lines

Questions in session.md are fenced blocks:

  ```question id=retries
  How many retries before alerting?
  - A: 3, fail fast
  - B: 5, ride out short outages
  ```
"""
import argparse, hashlib, ipaddress, json, mimetypes, os, re, secrets, shutil, socket, subprocess, sys, threading, time, urllib.error, urllib.request, webbrowser
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs

HERE = Path(__file__).parent
VENDOR = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "grill-workspace"


def read_json(p, default):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return default


MANIFEST = read_json(HERE / "vendor.json", {})
MODELS_CACHE = {"at": 0, "data": []}


def vendor_file(name: str):
    """A pinned library from vendor.json: downloaded once into the cache, kept only if its SHA-256 matches."""
    entry = MANIFEST.get(name)
    if not entry:
        return None
    f = VENDOR / entry["sha256"][:16] / name
    if not f.is_file():
        with urllib.request.urlopen(entry["url"], timeout=60) as r:
            data = r.read()
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise OSError(f"{name}: download doesn't match its pinned SHA-256, refusing it")
        f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(f.suffix + ".part")
        tmp.write_bytes(data)
        tmp.replace(f)
    return f


def fetch_vendor(board: bool):
    """Everything the page needs at start; the Excalidraw board's files only when the board is on."""
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(vendor_file, [n for n, e in MANIFEST.items() if board or not e.get("board")]))


KC_SERVICE, KC_ACCOUNT = "grill-workspace", "openrouter"


def keychain(op: str, secret: str = ""):
    """OpenRouter key in the OS keychain (encrypted at rest): macOS Keychain or Linux Secret Service."""
    try:
        if sys.platform == "darwin":
            cmd = {"get": ["security", "find-generic-password", "-s", KC_SERVICE, "-a", KC_ACCOUNT, "-w"],
                   # shortcut: `security` only takes the secret as an argument, so it's briefly visible to local `ps`
                   "set": ["security", "add-generic-password", "-U", "-s", KC_SERVICE, "-a", KC_ACCOUNT, "-w", secret],
                   "del": ["security", "delete-generic-password", "-s", KC_SERVICE, "-a", KC_ACCOUNT]}[op]
            r = subprocess.run(cmd, capture_output=True, text=True)
        elif shutil.which("secret-tool"):
            attrs = ["service", KC_SERVICE, "account", KC_ACCOUNT]
            cmd = {"get": ["secret-tool", "lookup", *attrs], "set": ["secret-tool", "store", "--label=grill workspace OpenRouter", *attrs],
                   "del": ["secret-tool", "clear", *attrs]}[op]
            r = subprocess.run(cmd, input=secret if op == "set" else None, capture_output=True, text=True)
        else:
            return None if op == "get" else False
    except OSError:
        return None if op == "get" else False
    if op == "get":
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    return r.returncode == 0


def api_key(d: Path):
    """Optional, Research only: env var, then the OS keychain (set from the page), then <dir>/.env."""
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    k = keychain("get")
    if k:
        return k
    env = d / ".env"
    if env.exists():
        m = re.search(r"^OPENROUTER_API_KEY=(\S+)", env.read_text(), re.M)
        return m.group(1) if m else None
    return None


def models():
    """OpenRouter text models, free first then cheapest; cached for an hour."""
    if time.time() - MODELS_CACHE["at"] > 3600:
        with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as r:
            data = json.load(r)["data"]
        rows = []
        for m in data:
            if m.get("architecture", {}).get("output_modalities", ["text"]) != ["text"]:  # chat models only
                continue
            p = m.get("pricing", {})
            price = float(p.get("prompt") or 0) * 1e6 + float(p.get("completion") or 0) * 1e6
            rows.append({"id": m["id"], "name": m.get("name", m["id"]), "price": round(price, 3), "free": price == 0})
        MODELS_CACHE.update(at=time.time(), data=sorted(rows, key=lambda r: (not r["free"], r["price"], r["id"])))
    return MODELS_CACHE["data"]


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"


class _Text(HTMLParser):
    """Visible text and <title> of a page, skipping scripts, styles and page chrome."""
    SKIP = {"script", "style", "noscript", "svg", "nav", "header", "footer", "form", "iframe"}

    def __init__(self):
        super().__init__()
        self.depth, self.parts, self.title, self.in_title = 0, [], "", False

    def handle_starttag(self, tag, attrs):
        self.depth += tag in self.SKIP
        self.in_title = tag == "title"

    def handle_endtag(self, tag):
        self.depth -= tag in self.SKIP and self.depth > 0
        self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.depth:
            self.parts.append(data)


def public_url(url: str):
    """Only fetch public http(s) hosts: never localhost or private networks (the server runs on the user's machine)."""
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        return False
    try:
        return all(ipaddress.ip_address(ai[4][0]).is_global for ai in socket.getaddrinfo(u.hostname, None))
    except (OSError, ValueError):
        return False


def fetch_page(url: str, limit=6000):
    if not public_url(url):
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/plain"})
        with urllib.request.urlopen(req, timeout=12) as r:
            if not public_url(r.geturl()):  # redirects too
                return None
            raw = r.read(2_000_000).decode(r.headers.get_content_charset() or "utf-8", errors="replace")
    except (OSError, ValueError):
        return None
    p = _Text()
    p.feed(raw)
    text = re.sub(r"\s+", " ", " ".join(p.parts)).strip()
    return {"url": url, "title": p.title.strip() or url, "text": text[:limit]} if len(text) > 200 else None


def web_search(query: str, n=5):
    """Free search via DuckDuckGo's HTML results page (no API key)."""
    req = urllib.request.Request("https://html.duckduckgo.com/html/?" + urlencode({"q": query}), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode(errors="replace")
    out = []
    for href, title in re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
        url = parse_qs(urlparse(href).query).get("uddg", [href])[0] if "duckduckgo.com/l/" in href else href
        if url.startswith("http") and "duckduckgo.com" not in url and url not in [o["url"] for o in out]:
            out.append({"url": url, "title": re.sub(r"<[^>]+>", "", title).strip()})
    return out[:n]


def research(d: Path, question: str, model: str):
    key = api_key(d)
    if not key:
        return {"error": "Research needs an OpenRouter key. Add it above; it's stored encrypted in your OS keychain."}
    urls = re.findall(r"https?://\S+", question)
    try:
        hits = [{"url": u.rstrip(").,"), "title": u} for u in urls] if urls else web_search(question)
    except OSError as e:
        return {"error": f"Search failed ({e}). Check your connection, or paste URLs into the question to read them directly."}
    with ThreadPoolExecutor(4) as ex:
        pages = [p for p in ex.map(fetch_page, [h["url"] for h in hits[:4]]) if p][:3]
    if not pages:
        return {"error": "Couldn't read any pages for that question. Try rephrasing, or paste a URL."}
    context = "\n\n".join(f"[{i + 1}] {p['title']} ({p['url']})\n{p['text']}" for i, p in enumerate(pages))
    body = json.dumps({"model": model, "max_tokens": 4000, "reasoning": {"effort": "low"},
                       "messages": [{"role": "system", "content": "Answer concisely for a software engineer: a 1-2 sentence answer first, then the key details. Use only the numbered sources below and cite them like [1]. If they don't answer the question, say so."},
                                    {"role": "user", "content": f"Question: {question}\n\nSources:\n{context}"}]})
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body.encode(),
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        for _ in range(3):  # openrouter/free may route to a reasoning model that runs out of tokens: retry
            with urllib.request.urlopen(req, timeout=180) as r:
                resp = json.load(r)
            if (resp["choices"][0]["message"].get("content") or "").strip():
                break
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            detail = json.loads(detail)["error"].get("metadata", {}).get("raw") or json.loads(detail)["error"]["message"]
        except (ValueError, KeyError, AttributeError, TypeError):
            pass
        hint = " This free model is busy right now: pick another model and ask again." if e.code == 429 else ""
        return {"error": f"{model} couldn't answer ({e.code}).{hint} Details: {str(detail)[:160]}"}
    except OSError as e:
        return {"error": f"Couldn't reach OpenRouter: {e}"}
    msg = resp["choices"][0]["message"]
    if not (msg.get("content") or "").strip():
        return {"error": f"{model} returned an empty answer three times. Pick another model and ask again."}
    sources = [{"title": p["title"], "url": p["url"]} for p in pages]
    item = {"q": question, "model": model, "answer": msg.get("content") or "", "sources": sources,
            "cost": resp.get("usage", {}).get("cost"), "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with LOCK:
        log = d / "research.json"
        items = read_json(log, [])
        items.append(item)
        log.write_text(json.dumps(items, indent=1, ensure_ascii=False))
    return item


def repo_root(d: Path):
    r = subprocess.run(["git", "-C", str(d.resolve().parent), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return Path(r.stdout.strip()) if r.returncode == 0 else None


def challenge_files(d: Path, root: Path):
    """Files the agent opened as code challenges in session.md: the only files the page may write."""
    md = (d / "session.md").read_text() if (d / "session.md").exists() else ""
    out = {}
    for m in re.finditer(r"```challenge\s+([^\n]*)\n", md):
        attrs = dict(re.findall(r"(\w+)=(\S+)", m.group(1)))
        if "file" in attrs:
            f = (root / attrs["file"]).resolve()
            if root.resolve() in f.parents:  # never outside the repo
                out[attrs["file"]] = f
    return out


def save_session(d: Path, svg: str):
    """Copy the session into <repo>/sessions/<date>-<name>/, and commit it if the user chose git storage."""
    cfg = read_json(d / "config.json", {})
    if "commit_sessions" not in cfg:
        return {"ask": True}
    root = repo_root(d) if cfg["commit_sessions"] else None
    base = root or d.resolve().parent
    name = re.sub(r"[^\w-]+", "-", (d.resolve().parent.name if d.name == ".grill" else d.resolve().name)).strip("-") or "session"
    dest = base / "sessions" / f"{time.strftime('%Y-%m-%d')}-{name}"
    dest.mkdir(parents=True, exist_ok=True)
    for f in ("notes.md", "board.json", "session.md", "answers.json", "research.json"):
        if (d / f).exists():
            shutil.copy2(d / f, dest / f)
    if svg.startswith("<svg"):
        (dest / "board.svg").write_text(svg)
    if not root:
        note = "Saved locally (sessions aren't stored in git)." if not cfg["commit_sessions"] else "Not a git repo, so the files were saved but not committed."
        return {"saved": str(dest), "commit": None, "note": note}
    rel = str(dest.relative_to(root))
    subprocess.run(["git", "-C", str(root), "add", "--", rel], capture_output=True, text=True)
    c = subprocess.run(["git", "-C", str(root), "commit", "-m", f"Session: {dest.name}", "--", rel], capture_output=True, text=True)
    if c.returncode != 0:
        return {"saved": rel, "commit": None, "note": "Nothing new to commit." if "nothing" in c.stdout + c.stderr else c.stderr[-300:]}
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    return {"saved": rel, "commit": sha}


def add_ask(d: Path, quote: str, question: str, card: str, status="pending"):
    with LOCK:
        asks = read_json(d / "asks.json", [])
        item = {"id": f"a{len(asks) + 1}", "quote": quote, "question": question, "card": card,
                "status": status, "reply": "", "at": time.strftime("%Y-%m-%d %H:%M:%S")}
        asks.append(item)
        (d / "asks.json").write_text(json.dumps(asks, indent=1, ensure_ascii=False))
    return item


def take_pending(d: Path):
    """Hand new asks to the agent once: pending -> delivered."""
    with LOCK:
        asks = read_json(d / "asks.json", [])
        out = [a for a in asks if a["status"] == "pending"]
        for a in out:
            a["status"] = "delivered"
        if out:
            (d / "asks.json").write_text(json.dumps(asks, indent=1, ensure_ascii=False))
    return out


def update_ask(d: Path, aid: str, text: str, done=False, replace=False):
    with LOCK:
        asks = read_json(d / "asks.json", [])
        a = next((x for x in asks if x["id"] == aid), None)
        if not a:
            return False
        a["reply"] = text if replace else a["reply"] + text
        a["status"] = "done" if done else "streaming"
        (d / "asks.json").write_text(json.dumps(asks, indent=1, ensure_ascii=False))
    return True


def can_fork():
    """Inside Claude Code the server answers page questions itself, from a copy of the agent's session."""
    return bool(os.environ.get("CLAUDE_CODE_SESSION_ID")) and shutil.which("claude") is not None


FORK_LOCK = threading.Lock()  # one side answer at a time


def session_cwd(sid: str):
    """`claude --resume` only finds a session from the folder it started in, which the transcript records."""
    for f in (Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects").glob(f"*/{sid}.jsonl"):
        with f.open() as fh:
            for line in fh:
                cwd = read_cwd(line)
                if cwd:
                    return cwd
    return None


def read_cwd(line: str):
    try:
        cwd = json.loads(line).get("cwd")
    except (ValueError, AttributeError):
        return None
    return cwd if cwd and Path(cwd).is_dir() else None


def fork_answer(d: Path, ask: dict):
    """Side question, like /btw: a tool-less fork of the session answers and streams into the page.
    The main chat never sees it. On any failure the ask falls back to the agent (`wait-ask` / `reply`)."""
    prompt = (f"Side question from the session page, about this passage of the card \"{ask['card']}\":\n\n> {ask['quote']}\n\n"
              f"{ask['question']}\n\nAnswer it directly and briefly in markdown, from what this session already knows. "
              "Don't continue any other work.")
    cmd = ["claude", "-p", prompt, "--resume", os.environ["CLAUDE_CODE_SESSION_ID"], "--fork-session",
           "--no-session-persistence", "--tools", "", "--output-format", "stream-json", "--include-partial-messages", "--verbose"]
    ok = False
    with FORK_LOCK:
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True,
                                 cwd=session_cwd(os.environ["CLAUDE_CODE_SESSION_ID"]))
            timer = threading.Timer(300, p.kill)
            timer.start()
            for line in p.stdout:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("type") == "stream_event" and e["event"].get("type") == "content_block_delta":
                    update_ask(d, ask["id"], e["event"]["delta"].get("text", ""))
                elif e.get("type") == "result":
                    ok = not e.get("is_error") and bool((e.get("result") or "").strip())
                    if ok:
                        update_ask(d, ask["id"], e["result"], done=True, replace=True)
            p.wait()
            timer.cancel()
        except OSError:
            ok = False
    if not ok:  # hand it to the agent instead
        with LOCK:
            asks = read_json(d / "asks.json", [])
            for a in asks:
                if a["id"] == ask["id"]:
                    a.update(status="pending", reply="")
            (d / "asks.json").write_text(json.dumps(asks, indent=1, ensure_ascii=False))


def make_handler(d: Path, token: str):
    session, answers = d / "session.md", d / "answers.json"
    files = {"notes": (d / "notes.md", 2_000_000), "board": (d / "board.json", 20_000_000)}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype="text/plain; charset=utf-8"):
            b = body.encode() if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b)

        def authed(self):
            return parse_qs(urlparse(self.path).query).get("t", [""])[0] == token

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/tokens.css":
                return self.send(200, (HERE / "tokens.css").read_bytes(), "text/css")
            if path.startswith("/vendor/"):  # only names listed in vendor.json, so no path traversal
                try:
                    f = vendor_file(path[len("/vendor/"):])
                except OSError as e:
                    return self.send(502, str(e))
                if not f:
                    return self.send(404, "not found")
                return self.send(200, f.read_bytes(), mimetypes.guess_type(f.name)[0] or "application/octet-stream")
            if not self.authed():  # token keeps other local pages/sites from reading the session
                return self.send(403, "forbidden")
            if path == "/":
                return self.send(200, (HERE / "workspace.html").read_text(), "text/html; charset=utf-8")
            if path.lstrip("/") in files:
                f = files[path.lstrip("/")][0]
                return self.send(200, f.read_bytes() if f.exists() else b"", "text/plain; charset=utf-8")
            if path == "/models":
                try:
                    return self.send(200, json.dumps({"models": models(), "has_key": bool(api_key(d))}), "application/json")
                except OSError as e:
                    return self.send(502, json.dumps({"error": str(e)}), "application/json")
            if path == "/research":
                return self.send(200, json.dumps(read_json(d / "research.json", [])), "application/json")
            if path == "/state":
                md = session.read_text() if session.exists() else ""
                board = d / "board.json"
                return self.send(200, json.dumps({
                    "md": md, "answers": read_json(answers, {}),
                    "name": d.resolve().parent.name if d.name == ".grill" else d.resolve().name,
                    "board_rev": board.stat().st_mtime_ns if board.exists() else 0,
                    "board_add": read_json(d / "board-add.json", None),  # shapes the agent wants drawn
                    "asks": read_json(d / "asks.json", []),
                }), "application/json")
            if path == "/asks/pending":  # `session.py wait-ask` takes asks the server didn't answer itself
                return self.send(200, json.dumps(take_pending(d)), "application/json")
            if path == "/file":
                root = repo_root(d) or d.resolve().parent
                rel = parse_qs(urlparse(self.path).query).get("path", [""])[0]
                f = challenge_files(d, root).get(rel)
                if not f:
                    return self.send(403, "not a challenge file")
                return self.send(200, f.read_text() if f.exists() else "", "text/plain; charset=utf-8")
            if path == "/config":
                return self.send(200, json.dumps(read_json(d / "config.json", {})), "application/json")
            if path in ("/study", "/decisions"):
                root = repo_root(d) or d.resolve().parent
                f = root / ("STUDY.md" if path == "/study" else "DECISIONS.md")
                return self.send(200, f.read_text() if f.exists() else "", "text/plain; charset=utf-8")
            self.send(404, "not found")

        def do_PUT(self):
            name = urlparse(self.path).path.lstrip("/")
            if name == "file" and self.authed():  # code challenge submit: write into the real file
                root = repo_root(d) or d.resolve().parent
                rel = parse_qs(urlparse(self.path).query).get("path", [""])[0]
                f = challenge_files(d, root).get(rel)
                n = int(self.headers.get("Content-Length", 0))
                if not f or n > 2_000_000:
                    return self.send(403, "not a challenge file")
                f.write_bytes(self.rfile.read(n))
                return self.send(200, "written")
            if name not in files or not self.authed():
                return self.send(403, "forbidden")
            f, limit = files[name]
            n = int(self.headers.get("Content-Length", 0))
            if n > limit:
                return self.send(413, "too large")
            data = self.rfile.read(n)
            tmp = f.with_suffix(".tmp")
            tmp.write_bytes(data)
            tmp.replace(f)  # atomic, so the agent never reads half a file
            self.send(200, str(f.stat().st_mtime_ns))

        def do_POST(self):
            path = urlparse(self.path).path
            if path not in ("/answer", "/research", "/save", "/board-add-done", "/config", "/key", "/ask", "/asks/chunk", "/asks/done") or not self.authed():
                return self.send(403, "forbidden")
            n = int(self.headers.get("Content-Length", 0))
            if n > 100_000:
                return self.send(413, "too large")
            if path == "/config":
                cfg = read_json(d / "config.json", {})
                cfg["commit_sessions"] = bool(json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}").get("commit_sessions"))
                (d / "config.json").write_text(json.dumps(cfg, indent=1))
                root = repo_root(d)
                if root and not cfg["commit_sessions"]:  # keep saved sessions out of git
                    gi = root / ".gitignore"
                    lines = gi.read_text().splitlines() if gi.exists() else []
                    if "sessions/" not in lines:
                        gi.write_text("\n".join(lines + ["sessions/"]) + "\n")
                return self.send(200, json.dumps(cfg), "application/json")
            if path in ("/ask", "/asks/chunk", "/asks/done"):
                n = int(self.headers.get("Content-Length", 0))
                if n > 200_000:
                    return self.send(413, "too large")
                raw = self.rfile.read(n).decode(errors="replace")
                if path == "/ask":
                    try:
                        a = json.loads(raw)
                        item = add_ask(d, str(a.get("quote", ""))[:4000], str(a["question"])[:4000], str(a.get("card", ""))[:200],
                                       "thinking" if can_fork() else "pending")
                    except (ValueError, KeyError, TypeError):
                        return self.send(400, "bad ask")
                    if item["status"] == "thinking":
                        threading.Thread(target=fork_answer, args=(d, item), daemon=True).start()
                    return self.send(200, json.dumps(item), "application/json")
                aid = parse_qs(urlparse(self.path).query).get("id", [""])[0]
                return self.send(200 if update_ask(d, aid, raw if path == "/asks/chunk" else "", done=path == "/asks/done") else 404, "ok")
            if path == "/key":  # set or remove the research key; it never goes back to the browser
                n = int(self.headers.get("Content-Length", 0))
                k = str(json.loads(self.rfile.read(min(n, 10_000)) or b"{}").get("key", "")).strip()
                if k and not re.fullmatch(r"sk-or-[\w-]{20,200}", k):
                    return self.send(400, json.dumps({"error": "That doesn't look like an OpenRouter key (sk-or-…)."}), "application/json")
                ok = keychain("set", k) if k else keychain("del")
                if k and not ok:
                    return self.send(500, json.dumps({"error": "No OS keychain available here. Set OPENROUTER_API_KEY in your environment instead."}), "application/json")
                return self.send(200, json.dumps({"has_key": bool(api_key(d))}), "application/json")
            if path == "/board-add-done":
                (d / "board-add.json").unlink(missing_ok=True)
                return self.send(200, "ok")
            if path == "/save":
                n = int(self.headers.get("Content-Length", 0))
                if n > 20_000_000:
                    return self.send(413, "too large")
                svg = json.loads(self.rfile.read(n) or b"{}").get("svg", "")
                return self.send(200, json.dumps(save_session(d, svg)), "application/json")
            if path == "/research":
                try:
                    a = json.loads(self.rfile.read(n))
                    q, model = str(a["q"])[:4000].strip(), str(a["model"])[:200]
                except (ValueError, KeyError, TypeError):
                    return self.send(400, "bad request")
                return self.send(200, json.dumps(research(d, q, model), ensure_ascii=False), "application/json")
            try:
                a = json.loads(self.rfile.read(n))
                qid, choice, note = str(a["id"])[:100], str(a.get("choice", ""))[:200], str(a.get("note", ""))[:5000]
            except (ValueError, KeyError, TypeError):
                return self.send(400, "bad answer")
            with LOCK:
                cur = read_json(answers, {})
                cur[qid] = {"choice": choice, "note": note, "at": time.strftime("%Y-%m-%d %H:%M:%S")}
                tmp = answers.with_suffix(".tmp")
                tmp.write_text(json.dumps(cur, indent=1, ensure_ascii=False))
                tmp.replace(answers)  # atomic, so `wait` never reads half a file
            self.send(200, "ok")

    return H


LOCK = threading.Lock()


def free_port(start):
    for p in range(start, start + 50):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    sys.exit("no free port")


def serve(d: Path, port: int, open_browser: bool):
    d.mkdir(parents=True, exist_ok=True)
    (d / "session.md").touch()
    try:
        fetch_vendor(board=read_json(d / "config.json", {}).get("board", False))
    except OSError as e:
        print(f"Couldn't download the workspace libraries ({e}). Connect once to cache them, or use chat.", file=sys.stderr)
        return 3
    token = secrets.token_urlsafe(16)
    port = free_port(port)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(d, token))
    url = f"http://localhost:{port}/?t={token}"
    (d / "server.json").write_text(json.dumps({"url": url, "pid": os.getpid()}))
    print(url, flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    finally:
        (d / "server.json").unlink(missing_ok=True)


def wait(d: Path, ids, timeout):
    answers = d / "answers.json"
    seen = set(read_json(answers, {}))
    end = time.time() + timeout
    while time.time() < end:
        cur = read_json(answers, {})
        done = [i for i in ids if i in cur] if ids else [i for i in cur if i not in seen]
        if (ids and len(done) == len(ids)) or (not ids and done):
            for i in done:
                print(json.dumps({"id": i, **cur[i]}, ensure_ascii=False))
            return 0
        time.sleep(1)
    print(json.dumps({"timeout": True, "waiting_for": ids or "any"}))
    return 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["serve", "url", "wait", "wait-ask", "reply"])
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--dir", default=".grill")
    ap.add_argument("--port", type=int, default=4711)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--at", default="", help="url: deep link to a card heading, q-<id>, ask-<id>, D20, diagram-<name> or a tab")
    a = ap.parse_args()
    d = Path(a.dir)
    if a.cmd == "serve":
        return serve(d, a.port, not a.no_open)
    if a.cmd == "url":
        info = read_json(d / "server.json", None)
        print(info["url"] + (f"#{a.at.lstrip('#')}" if a.at else "") if info else "not running: start with `python3 session.py serve &`")
        return 0 if info else 1
    if a.cmd == "wait-ask":  # asks the server couldn't answer itself (outside Claude Code, or the fork failed)
        end = time.time() + a.timeout
        while time.time() < end:
            got = take_pending(d)
            if got:
                for x in got:
                    print(json.dumps(x, ensure_ascii=False))
                return 0
            time.sleep(1)
        print(json.dumps({"timeout": True}))
        return 2
    if a.cmd == "reply":  # `session.py reply a3 --dir .grill < answer.md`
        return 0 if update_ask(d, a.ids[0], sys.stdin.read(), done=True, replace=True) else 1
    return wait(d, a.ids, a.timeout)


if __name__ == "__main__":
    sys.exit(main())
