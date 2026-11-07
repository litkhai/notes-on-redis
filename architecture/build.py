"""Write architecture/page.json's diagram blocks from diagrams.py, then build docs/architecture.md.
usage: python3 architecture/build.py
The diagram blocks are the same SVG in every language (component names stay in English);
text blocks are edited in page.json directly.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diagrams  # noqa: E402

page = json.loads((HERE / "page.json").read_text())
for b in page["blocks"]:
    if b.get("diagram"):
        svg = getattr(diagrams, b["diagram"])()
        for lang in ("en", "ko", "zh", "ja", "th", "id", "ms"):
            b[lang] = svg
(HERE / "page.json").write_text(json.dumps(page, ensure_ascii=False, indent=1))
subprocess.run([sys.executable, str(HERE.parent / "scripts" / "build-lang-page.py"), str(HERE / "page.json")], check=True)
