#!/usr/bin/env python3
"""Give every non-English heading on a site page a stable id derived from English (#64).

kramdown builds heading ids from ASCII letters only, so a Korean, Chinese, Japanese or
Thai heading gets `section-3` or `iris---`: an id that moves when a heading is added and
means nothing in a link. This writes `{#<lang>-<english id>}` on each non-English h2–h4,
taking the English id of the heading in the same position (heading parity is enforced by
check-docs.py). English headings keep kramdown's own ids, so existing links stay valid.
The layout maps a link to `#<id>` onto the shown language (`#ko-<id>` and back).

    python3 scripts/lang-heading-ids.py            # rewrite docs/*.md in place
    python3 scripts/lang-heading-ids.py --check    # exit 1 if a page is out of date
    python3 scripts/lang-heading-ids.py --ids F    # print the English ids kramdown makes for F

build-lang-page.py runs it on every page it writes; check-docs.py runs --check.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG_NAMES = ["English", "한국어", "简体中文", "日本語", "ภาษาไทย", "Bahasa Indonesia", "Bahasa Melayu"]
BLOCK = re.compile(r'^<div class="lang" data-lang="(\w+)" markdown="1">\s*$')
HEADING = re.compile(r"^(#{1,4}) (.+?)\s*$")
EXPLICIT = re.compile(r"\s*\{#[^}]*\}\s*$")


def kramdown_id(raw, used):
    """kramdown's Converter::Base#generate_id on the heading's raw text."""
    gen = re.sub(r"^[^a-zA-Z]+", "", raw)
    gen = re.sub(r"[^a-zA-Z0-9 -]", "", gen).replace(" ", "-").lower() or "section"
    if gen in used:
        used[gen] += 1
        return f"{gen}-{used[gen]}"
    used[gen] = 0
    return gen


def scan(lines):
    """Yield (index, level, text, lang) for each heading outside code fences."""
    lang, fence = None, False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = BLOCK.match(line)
        if m:
            lang = m.group(1)
            continue
        m = HEADING.match(line)
        if m:
            yield i, len(m.group(1)), EXPLICIT.sub("", m.group(2)), lang


def english_ids(lines):
    """Ids kramdown gives the h1 and the English block's headings, in order (language h2 excluded)."""
    used, out = {}, []
    for i, level, text, lang in scan(lines):
        if lang not in (None, "en"):
            break                      # English comes first; later explicit ids do not count
        hid = kramdown_id(text, used)
        if lang == "en" and level > 1 and text not in LANG_NAMES:
            out.append(hid)
    return out


def rewrite(text):
    lines = text.split("\n")
    en = english_ids(lines)
    pos = {}
    for i, level, body, lang in scan(lines):
        if lang in (None, "en") or level == 1 or body in LANG_NAMES:
            continue
        k = pos.get(lang, 0)
        pos[lang] = k + 1
        if k >= len(en):
            raise SystemExit(f"{lang}: more headings than English")
        lines[i] = f"{'#' * level} {body} {{#{lang}-{en[k]}}}"
    return "\n".join(lines)


def pages():
    for p in sorted((ROOT / "docs").glob("*.md")):
        t = p.read_text()
        if "layout: null" not in t.split("---", 2)[1] and 'class="lang"' in t:
            yield p, t


def main(argv):
    if argv[:1] == ["--ids"]:
        print("\n".join(english_ids(Path(argv[1]).read_text().split("\n"))))
        return 0
    targets = [(Path(a), Path(a).read_text()) for a in argv if not a.startswith("--")] or list(pages())
    stale = []
    for p, t in targets:
        new = rewrite(t)
        if new != t:
            if "--check" in argv:
                stale.append(p.name)
            else:
                p.write_text(new)
                print("ids written:", p.relative_to(ROOT))
    if stale:
        print("heading ids out of date (run scripts/lang-heading-ids.py):", ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
