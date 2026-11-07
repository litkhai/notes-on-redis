"""Build a four-language site page (docs/<page>.md) from a page.json source.

usage: python3 scripts/build-lang-page.py <page.json>
page.json carries "title", "permalink", "out" (e.g. docs/cloud.md), "img" (e.g. cloud-console)
and "blocks". Image width/height come from the WebP files (half the pixel size: captures are 2x).
"""
import json
from pathlib import Path

from PIL import Image

import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]).resolve()
LANGS = [("en", "English"), ("ko", "한국어"), ("zh", "简体中文"), ("ja", "日本語")]


page = json.loads(SRC.read_text())
IMG = ROOT / "docs" / "assets" / "img" / page["img"]
out = ["---", "layout: default", f"title: {page['title']}", f"permalink: {page['permalink']}", "---", "", f"# {page['title']}", ""]
for lang, label in LANGS:
    out += [f'<div class="lang" data-lang="{lang}" markdown="1">', "", f"## {label}", ""]
    for b in page["blocks"]:
        if b["type"] == "md":
            out += [b[lang], ""]
        else:
            w, h = Image.open(IMG / b["file"]).size
            src = "{{ '/assets/img/" + page["img"] + "/" + b["file"] + "' | relative_url }}"
            alt = b["alt"][lang].replace('"', "&quot;")
            out += [
                f'<p class="shot"><img src="{src}" width="{w // 2}" height="{h // 2}" alt="{alt}" loading="lazy" decoding="async"></p>',
                "",
                f"{b['cap'][lang]} <small>{page['captured'][lang]}</small>",
                "",
            ]
    out += ["</div>", ""]
(ROOT / page["out"]).write_text("\n".join(out))
print("wrote", page["out"])
