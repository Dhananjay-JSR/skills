"""Smoke test: libraries download and verify, serve, token, answers, and page questions (side answer and agent fallback).

Run: python3 test_session.py   (needs network the first time, to fill the library cache)
"""
import hashlib, json, os, stat, subprocess, sys, tempfile, time, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import session  # noqa: E402

# A download that doesn't match its pinned hash is refused and never cached.
tmp = Path(tempfile.mkdtemp())
(tmp / "lib.js").write_text("tampered")
session.VENDOR = tmp / "cache"
session.MANIFEST = {"lib.js": {"url": (tmp / "lib.js").as_uri(), "sha256": hashlib.sha256(b"original").hexdigest()}}
try:
    session.vendor_file("lib.js"); raise AssertionError("hash mismatch accepted")
except OSError as e:
    assert "SHA-256" in str(e)
assert not list((tmp / "cache").rglob("lib.js"))
session.MANIFEST["lib.js"]["sha256"] = hashlib.sha256(b"tampered").hexdigest()
assert session.vendor_file("lib.js").read_text() == "tampered"
assert session.vendor_file("../session.py") is None  # only manifest names are served

# Fake `claude`: streams two chunks, or fails when the question says so.
bin_dir = tmp / "bin"
bin_dir.mkdir()
fake = bin_dir / "claude"
fake.write_text("""#!/usr/bin/env python3
import json, sys
if "FAIL" in sys.argv[2]:
    print(json.dumps({"type": "result", "is_error": True, "result": ""})); sys.exit(1)
for t in ["Side ", "answer."]:
    print(json.dumps({"type": "stream_event", "event": {"type": "content_block_delta", "delta": {"type": "text_delta", "text": t}}}), flush=True)
print(json.dumps({"type": "result", "is_error": False, "result": "Side answer."}))
""")
fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "CLAUDE_CODE_SESSION_ID": "test-session"}

d = Path(tempfile.mkdtemp())
(d / "session.md").write_text("## Plan\nShort summary.\n\nDetails.\n\n```question id=q1\nPick one?\n- A: first\n- B: second\n```\n")
srv = subprocess.Popen([sys.executable, HERE / "session.py", "serve", "--dir", d, "--port", "4790", "--no-open"],
                       stdout=subprocess.PIPE, text=True, env=env)
try:
    url = srv.stdout.readline().strip()
    assert url.startswith("http"), "serve didn't start (offline on first run?)"
    base, tok = url.split("/?t=")
    assert b"marked" in urllib.request.urlopen(f"{base}/vendor/marked.min.js").read()[:2000]
    state = json.load(urllib.request.urlopen(f"{base}/state?t={tok}"))
    assert "question id=q1" in state["md"] and state["answers"] == {}
    try:
        urllib.request.urlopen(f"{base}/state?t=wrong"); raise AssertionError("token not enforced")
    except urllib.error.HTTPError as e:
        assert e.code == 403
    waiter = subprocess.Popen([sys.executable, HERE / "session.py", "wait", "q1", "--dir", d, "--timeout", "20"], stdout=subprocess.PIPE, text=True)
    time.sleep(1.5)
    urllib.request.urlopen(urllib.request.Request(f"{base}/answer?t={tok}", json.dumps({"id": "q1", "choice": "B: second", "note": "why not"}).encode(), method="POST"))
    out = json.loads(waiter.communicate(timeout=20)[0].strip())
    assert out["id"] == "q1" and out["choice"] == "B: second" and out["note"] == "why not", out

    def ask(q):
        req = urllib.request.Request(f"{base}/ask?t={tok}", json.dumps({"quote": "Short summary.", "question": q, "card": "Plan"}).encode(), method="POST")
        return json.load(urllib.request.urlopen(req))["id"]

    def settled(aid):
        for _ in range(50):
            a = next(x for x in json.load(urllib.request.urlopen(f"{base}/state?t={tok}"))["asks"] if x["id"] == aid)
            if a["status"] in ("done", "pending"):
                return a
            time.sleep(0.2)
        raise AssertionError(f"{aid} stuck: {a}")

    a = settled(ask("What does this mean?"))
    assert a["status"] == "done" and a["reply"] == "Side answer.", a
    b = settled(ask("FAIL please"))
    assert b["status"] == "pending" and b["reply"] == "", b  # falls back to the agent
    got = subprocess.run([sys.executable, HERE / "session.py", "wait-ask", "--dir", d, "--timeout", "5"], capture_output=True, text=True)
    assert json.loads(got.stdout)["id"] == b["id"], got.stdout
    subprocess.run([sys.executable, HERE / "session.py", "reply", b["id"], "--dir", d], input="Agent answer.", text=True, check=True)
    final = next(x for x in json.load(urllib.request.urlopen(f"{base}/state?t={tok}"))["asks"] if x["id"] == b["id"])
    assert final["status"] == "done" and final["reply"] == "Agent answer.", final
    print("ok", url.split("?")[0])
finally:
    srv.terminate()
