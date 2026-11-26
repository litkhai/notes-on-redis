"""Build one site page per language from a page.json source (#68, design/lang-urls.md).

usage: python3 scripts/build-lang-page.py <page.json> [...]

page.json carries "title", "permalink", "out" (e.g. docs/cloud.md), optionally "img"
(e.g. cloud-console) and "captured", and "blocks" ("md" blocks with one text per language,
"img" blocks with "file", "alt" and "cap" per language). Image width/height come from the
WebP headers (half the pixel size: captures are 2x).

Writes English to `out` at `permalink`, and every other language to docs/<lang>/<name> at
/<lang><permalink>. Each file names its language (`lang`) and the page it translates (`ref`).
In the non-English files:
  - links to another site page ({{ '/iris/' | relative_url }}) point into the same language;
  - headings carry the English heading's id, so #intent-router names the same section in all
    seven, and switching language keeps the fragment.
check-docs.py calls render() and fails when a committed file differs from its output.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
LANGS = ["en", "ko", "zh", "ja", "th", "id", "ms"]
HEADING = re.compile(r"^(#{1,4}) (.+?)\s*$")
LINK = re.compile(r"\{\{ '(/[^'#]*)(#[^']*)?' \| relative_url \}\}")


def nav_urls():
    """Permalinks of the English pages, read from the nav in _config.yml."""
    return set(re.findall(r"url: (/[^ ,}]*)", (DOCS / "_config.yml").read_text()))


def kramdown_id(raw, used):
    """kramdown's Converter::Base#generate_id on a heading's raw text."""
    gen = re.sub(r"^[^a-zA-Z]+", "", raw)
    gen = re.sub(r"[^a-zA-Z0-9 -]", "", gen).replace(" ", "-").lower() or "section"
    if gen in used:
        used[gen] += 1
        return f"{gen}-{used[gen]}"
    used[gen] = 0
    return gen


def headings(lines):
    """(index, level, text) for each heading outside code fences."""
    fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        m = None if fence else HEADING.match(line)
        if m:
            yield i, len(m.group(1)), m.group(2)


def webp_size(path):
    """(width, height) from a WebP header — no Pillow, so CI can render pages to compare."""
    d = Path(path).read_bytes()[:30]
    if d[:4] != b"RIFF" or d[8:12] != b"WEBP":
        raise SystemExit(f"{path}: not a WebP file")
    kind = d[12:16]
    if kind == b"VP8 ":
        return int.from_bytes(d[26:28], "little") & 0x3FFF, int.from_bytes(d[28:30], "little") & 0x3FFF
    if kind == b"VP8L":
        bits = int.from_bytes(d[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if kind == b"VP8X":
        return int.from_bytes(d[24:27], "little") + 1, int.from_bytes(d[27:30], "little") + 1
    raise SystemExit(f"{path}: unknown WebP chunk {kind!r}")


def lang_path(page, lang):
    out = ROOT / page["out"]
    return out if lang == "en" else DOCS / lang / out.name


def lang_permalink(page, lang):
    return page["permalink"] if lang == "en" else f"/{lang}{page['permalink']}"


def body(page, lang):
    out = [f"# {page['title']}", ""]
    for b in page["blocks"]:
        if b["type"] == "md":
            out += [b[lang], ""]
        else:
            w, h = webp_size(DOCS / "assets" / "img" / page["img"] / b["file"])
            src = "{{ '/assets/img/" + page["img"] + "/" + b["file"] + "' | relative_url }}"
            alt = b["alt"][lang].replace('"', "&quot;")
            out += [
                f'<p class="shot"><img src="{src}" width="{w // 2}" height="{h // 2}" alt="{alt}" loading="lazy" decoding="async"></p>',
                "",
                f"{b['cap'][lang]} <small>{page['captured'][lang]}</small>",
                "",
            ]
    return "\n".join(out).split("\n")     # md blocks hold many lines; headings are found per line


def render(src):
    """{output path: text} for every language of the page.json at `src`."""
    src = Path(src).resolve()
    page = json.loads(src.read_text())
    ref = Path(page["out"]).stem
    urls = nav_urls()

    en_lines = body(page, "en")
    used, en_ids = {}, []
    for _, level, text in headings(en_lines):
        hid = kramdown_id(text, used)          # the h1 counts towards kramdown's de-duplication
        if level > 1:
            en_ids.append(hid)

    files = {}
    for lang in LANGS:
        lines = en_lines if lang == "en" else body(page, lang)
        if lang != "en":
            subs = [(i, lv, t) for i, lv, t in headings(lines) if lv > 1]
            if len(subs) != len(en_ids):
                raise SystemExit(f"{src.relative_to(ROOT)} [{lang}]: {len(subs)} headings vs {len(en_ids)} in English")
            for (i, lv, t), hid in zip(subs, en_ids):
                lines[i] = f"{'#' * lv} {t} {{#{hid}}}"

            def relink(m):
                path, frag = m.group(1), m.group(2) or ""
                if path in urls:
                    path = f"/{lang}{path}"
                return "{{ '" + path + frag + "' | relative_url }}"

            lines = [LINK.sub(relink, l) for l in lines]
        front = ["---", f"# Generated by scripts/build-lang-page.py from {src.relative_to(ROOT)}; edit that file.",
                 "layout: default", f"title: {page['title']}",
                 f"permalink: {lang_permalink(page, lang)}", f"lang: {lang}", f"ref: {ref}", "---", ""]
        files[lang_path(page, lang)] = "\n".join(front + lines).rstrip("\n") + "\n"
    return files


def sources():
    """Every page.json that builds a site page."""
    for p in sorted(ROOT.rglob("page.json")):
        if ".git" in p.parts or "node_modules" in p.parts:
            continue
        if '"permalink"' in p.read_text():
            yield p


def main(argv):
    if not argv:
        sys.exit(__doc__)
    for a in argv:
        for path, text in render(a).items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
