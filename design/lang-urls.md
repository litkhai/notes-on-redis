# Per-language URLs — design (v0)

[English](#english) | [한국어](#한국어)

Status: **decided 2026-11-26 (D1–D3 below); built in #68's pull request, 2026-11-27.** Sizes measured on https://redis.litkhai.dev on 2026-11-26;
search-engine guidance read the same day from Google Search Central
([multi-regional sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites),
[localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions); neither page shows an update date).

---

## English

### 1. Problem

Every page is one URL that carries all seven languages; a script hides six of them.

| Page | HTML today | Chrome (header, nav, footer) | Largest language block | One-language page (estimate) |
|---|---|---|---|---|
| `/iris/` | 231 KB | 15 KB | 35 KB | ~51 KB |
| `/deep-dive/` | 221 KB | 15 KB | 32 KB | ~48 KB |
| `/architecture/` | 188 KB | 15 KB | 26 KB | ~42 KB |
| `/cloud/` | 156 KB | 15 KB | 23 KB | ~39 KB |
| `/compare/` | 121 KB | 15 KB | 16 KB | ~32 KB |
| `/enterprise/` | 111 KB | 15 KB | 15 KB | ~31 KB |
| `/setup/` | 105 KB | 15 KB | 14 KB | ~30 KB |

Measured: uncompressed HTML from `curl`, split at the `.lang` blocks. The last column is
chrome + largest block, a hypothesis until a page is built.

What this costs beyond bytes, by Google's own guidance:

- **Language is read from visible content**, not from `lang` or the URL. A page whose source holds
  seven languages side by side is the case Google advises against ("avoid side-by-side translations").
- **No per-language URL means nothing to index per language.** Google "recommends using different
  URLs for each language version"; content switched by cookies or browser settings may not be crawled.
- **No `hreflang`**, so a Korean search cannot be pointed at a Korean page — there is none.

### 2. Goals and non-goals

Goals: one language per URL; every page reachable in all seven; existing English links keep
working; authors still edit one source per page; checks catch a page that is out of sync.

Not in scope: translating the nav or footer (labels stay English, as now); per-region variants
(`ko-KR` vs `ko`); splitting long pages into sub-pages (a separate design).

### 3. URL scheme

| Language | Path | `hreflang` / `<html lang>` |
|---|---|---|
| English | `/iris/` (unchanged) | `en`, also `x-default` |
| 한국어 | `/ko/iris/` | `ko` |
| 简体中文 | `/zh/iris/` | `zh-Hans` |
| 日本語 | `/ja/iris/` | `ja` |
| ภาษาไทย | `/th/iris/` | `th` |
| Bahasa Indonesia | `/id/iris/` | `id` |
| Bahasa Melayu | `/ms/iris/` | `ms` |

English stays at the root so every link, bookmark and redirect stub that exists keeps its
meaning (decision D1). The overview is `/` and `/ko/` and so on.

### 4. Sources and generation

Today seven pages are built from a `page.json` by `scripts/build-lang-page.py`; the overview
(`docs/index.md`) is hand-written. Both already hold all seven languages in one file.

Proposal:

1. **The overview gets a `page.json` too** (`site/overview/page.json`), so every page has one source.
2. **`build-lang-page.py` writes seven files instead of one:** `docs/iris.md` (English) and
   `docs/ko/iris.md`, `docs/zh/iris.md`, … Each carries front matter `lang`, `ref: iris` (the page
   key shared by its translations) and its own `permalink`.
3. **Internal links are rewritten per language.** `{{ '/iris/' | relative_url }}` in the Korean
   text becomes `/ko/iris/` in `docs/ko/…`. The generator knows the permalinks from `_config.yml`'s nav.
4. **Every language uses the English heading ids** (`#intent-router` on all seven pages), so
   switching language keeps the reader at the same section by keeping the fragment.
   `lang-heading-ids.py` folds into the generator; the `#ko-…` ids from #64 go away (§9).
5. **Generated files are committed**, as today. `check-docs.py` fails when a generated file differs
   from what its source would produce (decision D3). The total size of `docs/` barely changes: the
   same text, split into files.

### 5. Layout

- `<html lang>` comes from `page.lang`, server-side; the head script no longer rewrites it.
- `<link rel="alternate" hreflang>` for all seven versions plus `x-default` → English, built by
  looping over `site.pages` with the same `ref`. Every version lists itself and the others, which
  is what Google requires for the annotations to count.
- `<link rel="canonical">` to the page itself; `og:locale` per language.
- **The language menu becomes links** to the same page in each language, keeping `location.hash`.
- **Nav links get the page's language prefix** (`/ko/cloud/` from a Korean page). Labels stay English.
- The sidebar table of contents keeps its script; there is only one block left to read.
- The `.lang` show/hide code and the `data-lang-ready` CSS from #64 are removed.

### 6. Choosing a language

Google says to avoid "automatically redirecting" by guessed language and to link to the other
versions instead. Options (decision D2):

| Option | First visit, browser in Korean | Visitor picked Korean before |
|---|---|---|
| **A. Banner only** (recommended) | English page with a one-line banner: "이 페이지는 한국어로도 있습니다 →" | the same banner, pre-filled from the saved choice |
| B. Redirect a saved choice | banner, as in A | client-side redirect from `/iris/` to `/ko/iris/` |
| C. Nothing | English page; the menu is the only way | same |

A matches the guidance and never surprises a reader who followed an English link on purpose.
B is closer to today's behaviour (the toggle remembered the language) and invisible to crawlers,
which carry no saved choice; it costs a redirect on every English link a Korean reader opens.

### 7. Sitemap, robots, 404

- `sitemap.xml` lists every URL with `xhtml:link` alternates (the same set as the HTML head;
  Google treats the two as equivalent, so both is redundant but harmless and keeps one template).
- `robots.txt` is unchanged.
- `404.html` stays one page in all seven languages: Vercel serves one 404 for every path.

### 8. Checks

`check-docs.py`:

- site pages: each `docs/<lang>/<page>.md` exists for each source, front matter `lang`, `ref`, `permalink` present;
- generated files in sync with their `page.json` (replaces the heading-id check);
- nav: every nav permalink exists in all seven languages;
- internal links in `docs/<lang>/` point into the same language.

The bilingual heading-parity check stays on the sources.

### 9. Compatibility

| What exists today | After |
|---|---|
| `/iris/` and the other English URLs | unchanged |
| A link to `/iris/#ko-intent-router` (ids from #64) | a small script on English pages sends `#<lang>-<id>` to `/<lang>/iris/#<id>` |
| A reader whose saved toggle was Korean | sees the banner (A) or is redirected (B) |
| `litkhai.github.io/notes-on-redis/...` stubs | `pages-redirect.py` stubs every built HTML page, so the new paths get stubs too |

### 10. Work split

| Step | What | Verified by |
|---|---|---|
| 1 | Generator: seven outputs per page, link rewriting, shared ids; overview `page.json` | local diff of generated files; `check-docs.py` |
| 2 | Layout: `lang`, `hreflang`, canonical, menu links, nav prefix, banner (D2) | Vercel preview: view-source per language, menu keeps the hash |
| 3 | Sitemap alternates; checks in §8, each fault injected once | preview `sitemap.xml`; checker fails on a missing translation and a stale file |
| 4 | Remove the toggle code; update `AGENTS.md`, `DESIGN.md` §5, `README.md` | production: page sizes, `hreflang` set, 404 |

Steps 1–3 land as one pull request: a half-done split serves broken links.

### 11. Decisions

| # | Decision | Decided 2026-11-26 |
|---|---|---|
| D1 | English at the root, or under `/en/` too | **Root** — no existing URL changes |
| D2 | Banner only, redirect a saved choice, or nothing (§6) | **A, banner only** |
| D3 | Commit generated files, or generate at Vercel build time | **Commit** — Python on Vercel's Jekyll build image is unverified, and committed output can be checked locally |

---

## 한국어

### 1. 문제

모든 페이지가 URL 하나에 일곱 언어를 다 담고, 스크립트가 여섯 개를 숨긴다.

| 페이지 | 지금 HTML | 크롬(헤더·내비·푸터) | 가장 큰 언어 블록 | 한 언어 페이지(추정) |
|---|---|---|---|---|
| `/iris/` | 231 KB | 15 KB | 35 KB | ~51 KB |
| `/deep-dive/` | 221 KB | 15 KB | 32 KB | ~48 KB |
| `/architecture/` | 188 KB | 15 KB | 26 KB | ~42 KB |
| `/cloud/` | 156 KB | 15 KB | 23 KB | ~39 KB |
| `/compare/` | 121 KB | 15 KB | 16 KB | ~32 KB |
| `/enterprise/` | 111 KB | 15 KB | 15 KB | ~31 KB |
| `/setup/` | 105 KB | 15 KB | 14 KB | ~30 KB |

측정: `curl`로 받은 비압축 HTML을 `.lang` 블록 경계로 나눴다. 마지막 열은 크롬 + 가장 큰 블록이며,
페이지를 실제로 만들기 전까지는 가설이다.

바이트 말고 드는 비용(Google 자체 가이드 기준):

- **언어는 보이는 본문으로 판단한다.** `lang`이나 URL이 아니다. 소스에 일곱 언어가 나란히 있는 페이지는
  Google이 피하라는 경우다("avoid side-by-side translations").
- **언어별 URL이 없으면 언어별로 색인할 대상이 없다.** Google은 언어 버전마다 다른 URL을 권하고,
  쿠키나 브라우저 설정으로 바꾸는 콘텐츠는 크롤링되지 않을 수 있다고 한다.
- **`hreflang`이 없다.** 한국어 검색을 한국어 페이지로 보낼 수 없다. 한국어 페이지가 없으니까.

### 2. 목표와 비목표

목표: URL 하나에 언어 하나, 모든 페이지를 일곱 언어로 접근 가능, 기존 영어 링크 유지,
작성자는 페이지당 소스 하나만 편집, 동기화가 어긋난 페이지는 검사가 잡는다.

범위 밖: 내비·푸터 번역(지금처럼 영어 라벨), 지역 변형(`ko-KR`과 `ko`), 긴 페이지 분할(별도 설계).

### 3. URL 체계

| 언어 | 경로 | `hreflang` / `<html lang>` |
|---|---|---|
| English | `/iris/`(그대로) | `en`, `x-default`도 |
| 한국어 | `/ko/iris/` | `ko` |
| 简体中文 | `/zh/iris/` | `zh-Hans` |
| 日本語 | `/ja/iris/` | `ja` |
| ภาษาไทย | `/th/iris/` | `th` |
| Bahasa Indonesia | `/id/iris/` | `id` |
| Bahasa Melayu | `/ms/iris/` | `ms` |

영어는 루트에 둔다. 지금 있는 링크, 북마크, 리다이렉트 스텁의 뜻이 바뀌지 않는다(결정 D1).
개요는 `/`, `/ko/` 등이다.

### 4. 소스와 생성

지금 일곱 페이지는 `page.json`에서 `scripts/build-lang-page.py`로 만들고, 개요(`docs/index.md`)만
손으로 쓴다. 둘 다 이미 한 파일에 일곱 언어를 담는다.

제안:

1. **개요도 `page.json`을 가진다**(`site/overview/page.json`). 모든 페이지의 소스가 하나가 된다.
2. **`build-lang-page.py`가 파일 하나 대신 일곱 개를 쓴다.** `docs/iris.md`(영어)와
   `docs/ko/iris.md`, `docs/zh/iris.md`, … 각각 front matter에 `lang`, `ref: iris`(번역끼리 공유하는
   페이지 키), 자기 `permalink`를 둔다.
3. **내부 링크를 언어별로 바꾼다.** 한국어 본문의 `{{ '/iris/' | relative_url }}`는 `docs/ko/…`에서
   `/ko/iris/`가 된다. 생성기는 `_config.yml` 내비에서 permalink를 안다.
4. **모든 언어가 영어 제목 id를 쓴다**(일곱 페이지 모두 `#intent-router`). 언어를 바꿀 때 fragment를
   그대로 붙이면 같은 절에 머문다. `lang-heading-ids.py`는 생성기에 합치고, #64의 `#ko-…` id는 없앤다(§9).
5. **생성된 파일은 지금처럼 커밋한다.** 생성 결과가 소스와 다르면 `check-docs.py`가 실패한다(결정 D3).
   `docs/` 전체 크기는 거의 그대로다. 같은 글을 파일로 나눌 뿐이다.

### 5. 레이아웃

- `<html lang>`은 서버에서 `page.lang`으로 정한다. head 스크립트가 더는 바꾸지 않는다.
- 일곱 버전과 `x-default`(영어)에 대한 `<link rel="alternate" hreflang>`. 같은 `ref`를 가진
  `site.pages`를 돌며 만든다. 모든 버전이 자기 자신과 나머지를 나열해야 Google이 주석을 인정한다.
- 자기 자신을 가리키는 `<link rel="canonical">`, 언어별 `og:locale`.
- **언어 메뉴는 링크가 된다.** 같은 페이지의 각 언어로, `location.hash`를 유지한다.
- **내비 링크에 페이지의 언어 접두어를 붙인다**(한국어 페이지에서 `/ko/cloud/`). 라벨은 영어 그대로.
- 사이드바 목차는 스크립트를 유지한다. 읽을 블록이 하나뿐이다.
- `.lang` 보이기·숨기기 코드와 #64의 `data-lang-ready` CSS는 지운다.

### 6. 언어 고르기

Google은 추정한 언어로 "automatically redirecting"하지 말고 다른 버전으로 가는 링크를 두라고 한다.
선택지(결정 D2):

| 선택지 | 첫 방문, 브라우저 한국어 | 전에 한국어를 고른 방문자 |
|---|---|---|
| **A. 배너만**(권장) | 영어 페이지에 한 줄 배너: "이 페이지는 한국어로도 있습니다 →" | 같은 배너, 저장된 선택 기준 |
| B. 저장된 선택은 리다이렉트 | A와 같은 배너 | `/iris/`에서 `/ko/iris/`로 클라이언트 리다이렉트 |
| C. 아무것도 안 함 | 영어 페이지, 메뉴로만 이동 | 같음 |

A는 가이드에 맞고, 일부러 영어 링크를 연 독자를 놀라게 하지 않는다. B는 지금 동작(토글이 언어를
기억)에 가깝고, 저장된 선택이 없는 크롤러에는 보이지 않는다. 대신 한국어 독자가 영어 링크를 열 때마다
리다이렉트가 한 번 생긴다.

### 7. 사이트맵, robots, 404

- `sitemap.xml`은 모든 URL을 `xhtml:link` 대체 링크와 함께 나열한다(HTML head와 같은 집합. Google은
  둘을 같게 취급하므로 둘 다 두는 건 중복이지만 해가 없고 템플릿 하나로 유지된다).
- `robots.txt`는 그대로.
- `404.html`은 일곱 언어를 담은 한 페이지로 둔다. Vercel은 모든 경로에 404 하나를 쓴다.

### 8. 검사

`check-docs.py`:

- 사이트 페이지: 소스마다 `docs/<lang>/<page>.md`가 있고 front matter에 `lang`, `ref`, `permalink`가 있다.
- 생성 파일이 `page.json`과 일치한다(제목 id 검사를 대체).
- 내비: 내비 permalink가 일곱 언어 모두에 있다.
- `docs/<lang>/`의 내부 링크가 같은 언어를 가리킨다.

이중 언어 제목 개수 검사는 소스에 그대로 둔다.

### 9. 호환성

| 지금 있는 것 | 이후 |
|---|---|
| `/iris/` 등 영어 URL | 그대로 |
| `/iris/#ko-intent-router` 링크(#64의 id) | 영어 페이지의 작은 스크립트가 `#<lang>-<id>`를 `/<lang>/iris/#<id>`로 보낸다 |
| 토글에 한국어가 저장된 독자 | 배너를 본다(A) 또는 리다이렉트(B) |
| `litkhai.github.io/notes-on-redis/...` 스텁 | `pages-redirect.py`가 빌드된 모든 HTML에 스텁을 만들므로 새 경로도 스텁이 생긴다 |

### 10. 작업 나누기

| 단계 | 내용 | 확인 방법 |
|---|---|---|
| 1 | 생성기: 페이지당 출력 일곱 개, 링크 바꾸기, 공통 id, 개요 `page.json` | 생성 파일 로컬 diff, `check-docs.py` |
| 2 | 레이아웃: `lang`, `hreflang`, canonical, 메뉴 링크, 내비 접두어, 배너(D2) | Vercel 프리뷰: 언어별 소스 보기, 메뉴가 hash 유지 |
| 3 | 사이트맵 대체 링크, §8 검사(각각 결함을 한 번 주입) | 프리뷰 `sitemap.xml`, 번역 누락과 오래된 파일에서 검사 실패 |
| 4 | 토글 코드 제거, `AGENTS.md`·`DESIGN.md` §5·`README.md` 갱신 | 운영: 페이지 크기, `hreflang` 집합, 404 |

1–3단계는 PR 하나로 낸다. 반쯤 나눈 상태는 깨진 링크를 낸다.

### 11. 결정

| # | 결정 | 2026-11-26 결정 |
|---|---|---|
| D1 | 영어를 루트에, 아니면 `/en/`에도 | **루트** — 기존 URL이 바뀌지 않는다 |
| D2 | 배너만, 저장된 선택 리다이렉트, 아무것도 안 함(§6) | **A, 배너만** |
| D3 | 생성 파일 커밋, 아니면 Vercel 빌드 때 생성 | **커밋** — Vercel Jekyll 빌드 이미지의 Python은 확인 안 됨, 커밋된 출력은 로컬에서 검사 가능 |
