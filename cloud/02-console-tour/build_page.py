"""Build docs/cloud.md from page.json (four .lang blocks, one shared set of screenshots).

usage: python3 cloud/02-console-tour/build_page.py
Image width/height come from the WebP files (half the pixel size: captures are 2x).
"""
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
IMG = ROOT / "docs" / "assets" / "img" / "cloud-console"
LANGS = [("en", "English"), ("ko", "한국어"), ("zh", "简体中文"), ("ja", "日本語")]
CAPTURED = {
    "en": "Captured 2026-11-07, Redis Cloud free plan.",
    "ko": "2026-11-07 캡처, Redis Cloud 무료 플랜.",
    "zh": "2026-11-07 截图，Redis Cloud 免费计划。",
    "ja": "2026-11-07 キャプチャ、Redis Cloud 無料プラン。",
}

page = json.loads((HERE / "page.json").read_text())
out = ["---", "layout: default", f"title: {page['title']}", "permalink: /cloud/", "---", "", f"# {page['title']}", ""]
for lang, label in LANGS:
    out += [f'<div class="lang" data-lang="{lang}" markdown="1">', "", f"## {label}", ""]
    for b in page["blocks"]:
        if b["type"] == "md":
            out += [b[lang], ""]
        else:
            w, h = Image.open(IMG / b["file"]).size
            src = "{{ '/assets/img/cloud-console/" + b["file"] + "' | relative_url }}"
            alt = b["alt"][lang].replace('"', "&quot;")
            out += [
                f'<p class="shot"><img src="{src}" width="{w // 2}" height="{h // 2}" alt="{alt}" loading="lazy" decoding="async"></p>',
                "",
                f"{b['cap'][lang]} <small>{CAPTURED[lang]}</small>",
                "",
            ]
    out += ["</div>", ""]
(ROOT / "docs" / "cloud.md").write_text("\n".join(out))
print("wrote docs/cloud.md")
