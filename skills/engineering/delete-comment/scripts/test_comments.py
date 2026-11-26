#!/usr/bin/env python3
"""Self-check for comments.py: python3 test_comments.py"""
import os
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from comments import comments, main  # noqa: E402


def texts(name, src):
    return [(b["line"], b["end"], b["own_line"], b["text"]) for b in comments(pathlib.Path(name), src)]


js = """// header line one
// header line two
const url = "http://x.dev/*not*/"; // trailing
const t = `a // b
/* c */`;
/* block
   two */
// eslint-disable-next-line no-console
console.log(1)
"""
assert texts("a.ts", js) == [
    (1, 2, True, "// header line one\n// header line two"),
    (3, 3, False, "// trailing"),
    (6, 7, True, "/* block\n   two */"),
], texts("a.ts", js)

py = '''#!/usr/bin/env python3
"""Docstring is not a comment."""
x = "# not a comment"  # real one
# own line
y = 1  # type: ignore
'''
assert texts("a.py", py) == [(3, 3, False, "# real one"), (4, 4, True, "# own line")], texts("a.py", py)

sh = """#!/bin/sh
echo "$#" '# no' ${#x}
# yes
"""
assert texts("a.sh", sh) == [(3, 3, True, "# yes")], texts("a.sh", sh)
assert texts("a.css", 'a { background: url(http://x) } /* c */') == [(1, 1, False, "/* c */")]

with tempfile.TemporaryDirectory() as d:
    os.chdir(d)
    subprocess.run(["git", "init", "-q"], check=True)
    pathlib.Path("src").mkdir()
    pathlib.Path("src/a.ts").write_text("// one\n// two\nlet a = 1\n")
    subprocess.run(["git", "add", "."], check=True)
    assert main(["baseline", "src"]) == 0
    assert main(["check"]) == 0
    pathlib.Path("src/a.ts").write_text("// one\n// two\n// three\nlet a = 1\n")
    assert main(["check"]) == 1, "a new comment line must fail"
    pathlib.Path("src/a.ts").write_text("// one\nlet a = 1\n")
    assert main(["check", "--tighten"]) == 0
    pathlib.Path("src/a.ts").write_text("// one\n// back\nlet a = 1\n")
    assert main(["check"]) == 1, "the baseline must not rise back after tightening"
print("ok")
