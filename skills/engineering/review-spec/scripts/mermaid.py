#!/usr/bin/env python3
"""Mermaid Live links for every ```mermaid block in a Markdown file, and optionally a render check.

Usage:
  mermaid.py <doc.md>            print one Mermaid Live edit link per diagram
  mermaid.py <doc.md> --render   also render each diagram to <doc>-assets/diagram-NN.svg with mermaid-cli;
                                 exits non-zero on the first diagram that fails to render
"""
import base64
import json
import pathlib
import re
import subprocess
import sys
import zlib

BLOCK = re.compile(r"^```mermaid\s*\n(.*?)^```", re.M | re.S)


def live_link(source):
    """mermaid.live edit link with the diagram packed into the URL (pako: zlib deflate, url-safe base64)."""
    state = {"code": source, "mermaid": json.dumps({"theme": "default"}), "autoSync": True, "updateDiagram": True}
    packed = base64.urlsafe_b64encode(zlib.compress(json.dumps(state).encode(), 9)).decode().rstrip("=")
    return f"https://mermaid.live/edit#pako:{packed}"


def render(source, target):
    """Renders one diagram with mermaid-cli; returns the error text, or None on success."""
    source_file = target.with_suffix(".mmd")
    source_file.write_text(source)
    result = subprocess.run(
        ["npx", "-y", "@mermaid-js/mermaid-cli", "-i", str(source_file), "-o", str(target), "-q"],
        capture_output=True, text=True,
    )
    source_file.unlink()
    return None if result.returncode == 0 else (result.stderr or result.stdout).strip()


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if len(argv) >= 2 else 2
    doc = pathlib.Path(argv[1])
    diagrams = BLOCK.findall(doc.read_text())
    if not diagrams:
        print(f"no mermaid blocks in {doc}", file=sys.stderr)
        return 1

    assets = doc.with_name(f"{doc.stem}-assets")
    for number, source in enumerate(diagrams, 1):
        print(f"diagram {number}: {live_link(source)}")
        if "--render" in argv:
            assets.mkdir(exist_ok=True)
            target = assets / f"diagram-{number:02d}.svg"
            error = render(source, target)
            if error:
                print(f"diagram {number} failed to render:\n{error}", file=sys.stderr)
                return 1
            print(f"  rendered {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
