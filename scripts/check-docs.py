#!/usr/bin/env python3
"""Check the documentation conventions this repository relies on.

Run from anywhere:

    python3 scripts/check-docs.py          # report and exit non-zero on failure
    python3 scripts/check-docs.py -v       # also list what passed

Every check here exists because something actually broke. See AGENTS.md.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "_site", "node_modules", ".venv", ".jekyll-cache"}

# Liquid runs before Markdown, so `{{ '/x/' | relative_url }}` contributes a
# pipe to the source that never reaches the rendered table. Strip Liquid before
# counting columns or four tables read as ragged when they are fine.
LIQUID = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.S)

failures: list[str] = []
passes: list[str] = []


def fail(path, msg):
    failures.append(f"{path}: {msg}")


def ok(msg):
    passes.append(msg)


def md_files():
    for p in sorted(ROOT.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def rel(p):
    return p.relative_to(ROOT).as_posix()


# --------------------------------------------------------------------------
# 1. Bilingual structure
#
# Every README carries a full English section and a full Korean one (site
# pages are checked through their page.json sources, section 2). Sections are meant to mirror each other, so an unequal heading count
# means one language is missing something the other has.
# --------------------------------------------------------------------------
def check_bilingual():
    # Anchored to line start: prose that merely mentions `## English` in
    # backticks — AGENTS.md describing this very convention — is not a section.
    # Site pages also carry Simplified Chinese, Japanese, Thai, Indonesian and
    # Malay (#22); each section is checked against the English one.
    short = {"English": "EN", "한국어": "KO", "简体中文": "ZH", "日本語": "JA",
             "ภาษาไทย": "TH", "Bahasa Indonesia": "ID", "Bahasa Melayu": "MS"}
    names = "|".join(short)
    marker = re.compile(r"^## (?:%s)\s*$" % names, re.M)

    checked = 0
    for p in md_files():
        raw = p.read_text()
        if not marker.search(raw):
            continue
        text = LIQUID.sub("X", raw)
        parts = re.split(r"^## (%s)\s*$" % names, text, flags=re.M)
        sections = dict(zip(parts[1::2], parts[2::2]))
        if "English" not in sections or "한국어" not in sections:
            fail(rel(p), "has one language section but not the other")
            continue
        checked += 1

        en = sections["English"]
        for level in (2, 3):
            pat = re.compile(r"^#{%d} (?!%s)(.+)$" % (level, names), re.M)
            for name, half in sections.items():
                if name == "English":
                    continue
                a, b = pat.findall(en), pat.findall(half)
                if len(a) != len(b):
                    fail(rel(p), f"h{level} count differs: {len(a)} EN vs {len(b)} {short[name]}")

        for full, half in sections.items():
            name = short[full]
            if half.count("```") % 2:
                fail(rel(p), f"[{name}] unbalanced code fence")
            run = []
            for line in half.split("\n"):
                if line.strip().startswith("|"):
                    run.append(line.count("|"))
                else:
                    if len(set(run)) > 1:
                        fail(rel(p), f"[{name}] table with inconsistent columns {sorted(set(run))}")
                    run = []
    ok(f"bilingual structure: {checked} files")


# --------------------------------------------------------------------------
# 2. Site pages
#
# One language per page (#68, design/lang-urls.md): English in docs/, the others
# in docs/<lang>/, all generated from a page.json by scripts/build-lang-page.py.
# Each source must carry every language with the same headings, and each
# committed page must be exactly what its source produces — a hand edit, or a
# source changed without rebuilding, would make the languages drift apart.
# --------------------------------------------------------------------------
SITE_LANGS = ["en", "ko", "zh", "ja", "th", "id", "ms"]


def builder():
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_lang_page", ROOT / "scripts" / "build-lang-page.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def site_pages():
    """Content pages (redirect stubs and non-page files left out)."""
    for p in sorted((ROOT / "docs").rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        text = p.read_text()
        front = text.split("---", 2)[1] if text.startswith("---") else ""
        if "layout: null" in front:
            continue
        yield p, text, front


def check_page_sources():
    import json
    b = builder()
    heading = re.compile(r"^#{2,4} ", re.M)
    n = 0
    for src in b.sources():
        n += 1
        page = json.loads(src.read_text())
        for i, blk in enumerate(page["blocks"]):
            fields = ["alt", "cap"] if blk["type"] == "img" else [None]
            for f in fields:
                d = blk[f] if f else blk
                missing = [l for l in SITE_LANGS if not d.get(l)]
                if missing:
                    fail(rel(src), f"block {i}{'.' + f if f else ''} lacks {', '.join(missing)}")
            if blk["type"] != "md":
                continue
            counts = {l: len(heading.findall(LIQUID.sub("X", blk.get(l, "")))) for l in SITE_LANGS}
            if len(set(counts.values())) > 1:
                fail(rel(src), f"block {i} heading counts differ: {counts}")
            for l in SITE_LANGS:
                txt = LIQUID.sub("X", blk.get(l, ""))
                if txt.count("```") % 2:
                    fail(rel(src), f"block {i} [{l}] unbalanced code fence")
                run = []
                for line in txt.split("\n") + [""]:
                    if line.strip().startswith("|"):
                        run.append(line.count("|"))
                    else:
                        if len(set(run)) > 1:
                            fail(rel(src), f"block {i} [{l}] table with inconsistent columns {sorted(set(run))}")
                        run = []
    ok(f"page sources: {n} page.json files")


def check_site_pages():
    b = builder()
    expected = {}
    for src in b.sources():
        try:
            expected.update(b.render(src))
        except (SystemExit, KeyError) as e:
            fail(rel(src), f"cannot build: {e}")
    checked = 0
    for p, text, front in site_pages():
        checked += 1
        for key in ("layout:", "title:", "permalink:", "lang:", "ref:"):
            if not re.search(r"^" + key, front, re.M):
                fail(rel(p), f"front matter missing `{key}`")
        lang = re.search(r"^lang:\s*(\S+)", front, re.M)
        where = p.parent.name if p.parent != ROOT / "docs" else "en"
        if lang and lang.group(1) != where:
            fail(rel(p), f"`lang: {lang.group(1)}` but the file is under {where}")
        if '<div class="lang"' in text:
            fail(rel(p), "carries a .lang block; pages hold one language now (#68)")
        if p not in expected:
            fail(rel(p), "no page.json produces this file")
        elif expected[p] != text:
            fail(rel(p), "differs from its page.json: run scripts/build-lang-page.py on the source")
    for p in expected:
        if not p.exists():
            fail(rel(p), "missing: run scripts/build-lang-page.py on its source")
    ok(f"site pages: {checked} files, all in sync with their sources")


# --------------------------------------------------------------------------
# 3. Navigation
#
# Every nav entry must resolve to a real page in every language, and every
# content page must be reachable. A page moved without updating _config.yml
# 404s silently.
# --------------------------------------------------------------------------
def check_nav():
    config = (ROOT / "docs" / "_config.yml").read_text()
    nav_block = config.split("nav:", 1)[1]
    nav_urls = re.findall(r"url:\s*(\S+?)\s*[,}]", nav_block)
    nav_parents = set(re.findall(r"parent:\s*([^,}]+?)\s*[,}]", nav_block))
    nav_titles = set(t.strip() for t in re.findall(r"title:\s*([^,}]+?)\s*[,}]", nav_block))

    permalinks = {}
    for p, text, front in site_pages():
        m = re.search(r"^permalink:\s*(\S+)", front, re.M)
        if m:
            permalinks[m.group(1)] = p

    for url in nav_urls:
        for lang in SITE_LANGS:
            want = url if lang == "en" else f"/{lang}{url}"
            if want not in permalinks:
                fail("docs/_config.yml", f"nav points at `{url}` but no page has `{want}`")

    for url, p in permalinks.items():
        m = re.match(r"^/(%s)(/.*)$" % "|".join(SITE_LANGS[1:]), url)
        base = m.group(2) if m else url
        if base not in nav_urls:
            fail(rel(p), f"permalink `{url}` is not in the nav and is not a redirect stub")

    for parent in nav_parents:
        if parent not in nav_titles:
            fail("docs/_config.yml", f"`parent: {parent}` names an item that does not exist")

    ok(f"nav: {len(nav_urls)} entries, {len(permalinks)} pages")


# --------------------------------------------------------------------------
# 4. Internal links
#
# Relative links between repo documents break silently when a file moves.
# --------------------------------------------------------------------------
def check_internal_links():
    count = 0
    for p in md_files():
        for target in re.findall(r"\]\((\.{1,2}/[^)\s#]+)", p.read_text()):
            count += 1
            resolved = (p.parent / target).resolve()
            if not resolved.exists():
                fail(rel(p), f"link to `{target}` does not resolve")
    ok(f"internal links: {count} checked")


# --------------------------------------------------------------------------
# 5. Secrets
#
# .env holds a live API key. It must never be tracked.
# --------------------------------------------------------------------------
def check_secrets():
    try:
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        ok("secrets: skipped, git unavailable")
        return

    for name in tracked:
        if Path(name).name in {".env", ".env.bak"}:
            fail(name, "a secrets file is tracked by git")

    env = ROOT / ".env"
    if env.exists():
        mode = oct(env.stat().st_mode)[-3:]
        if mode != "600":
            fail(".env", f"mode is {mode}, expected 600")
    ok(f"secrets: {len(tracked)} tracked files scanned")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true", help="list checks that passed")
    args = ap.parse_args()

    for check in (check_bilingual, check_page_sources, check_site_pages, check_nav,
                  check_internal_links, check_secrets):
        check()

    if args.verbose:
        for line in passes:
            print(f"  ok    {line}")

    if failures:
        print(f"\n{len(failures)} problem(s):\n", file=sys.stderr)
        for line in failures:
            print(f"  FAIL  {line}", file=sys.stderr)
        return 1

    print(f"All checks passed ({len(passes)} groups).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
