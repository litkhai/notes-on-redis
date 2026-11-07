# Agent guide — how to pick up an issue in notes-on-redis

[English](#english) | [한국어](#한국어)

Read [`AGENTS.md`](../AGENTS.md) first (rules), then this (procedure), then the issue.
The design that every issue points at is [`DESIGN.md`](./DESIGN.md); the facts behind it are
the two `research-*.md` files next to it.

## English

### 1. Before anything

```bash
git clone https://github.com/litkhai/notes-on-redis && cd notes-on-redis
git config core.hooksPath .githooks        # gitleaks + docs checks on commit
python3 scripts/check-docs.py -v           # must pass before you start, and before you push
```

Pick one issue. Issues are numbered in the order of work (DESIGN §7): #1 skeleton (done by the
first PR), #2 setup + local, #3 Iris getting started, #4 Cloud free DB + console captures,
#5 compare locally, #6 deep dives 1–4, #7 Iris 2–5, #8 Essentials (budget), #9 enterprise,
#10 deep dives 5–8, #11 Iris 6, #12 Pro + AWS (budget), #13 site deployment, #14 language decision.
Earlier numbers first unless the issue says it is independent.

### 2. Flow

1. Comment on the issue that you are taking it and what you will touch.
2. Branch from `main`: `git checkout -b <track>-<nn>-<slug>` (e.g. `local-01-redis-8-docker`).
3. Work inside the lab directory. Each lab is self-contained: its own `compose.yaml`,
   scripts, `.venv` (`python3 -m venv .venv && .venv/bin/pip install …`), `.env.example`.
4. Run it end to end. Paste real output into the README — the command, the output, the
   version it came from, the date. If a step did not run, write "not run" and why.
5. Update `STATUS.md` — the lab's row and, if money was spent, the *Budget spent* table.
6. `python3 scripts/check-docs.py -v`, then commit (the hook runs gitleaks) and push.
7. Open a PR with `Closes #N` in the body. Do not merge; the user merges.

### 3. The lab README

Keep the stub's shape and fill it in:

```
h1   <Title>
     [English](#english) | [한국어](#한국어)
h2   English
     **Verified on Redis <version> (<image or plan>), <date>.**   ← only after a real end-to-end run
     <what it shows, in one paragraph>
h3   Run            — commands, in order, with the output as it appeared
h3   What was observed — the numbers / behaviours, each with how it was measured
h3   Not run / caveats
     | Plan needed | … |   | Verified on | … |
h2   한국어
     the same, in full — heading count must match; check-docs.py compares h3 counts
```

Rules the checker does not catch: no count in a heading; no "this section covers";
versions and prices always with the date they were read; Redis Ltd., not "Redis Labs".

### 4. Site page

A lab's site page is `docs/<track>.md` (one page per nav item; labs are sections on it).
Seven `.lang` blocks (`en`, `ko`, `zh`, `ja`, `th`, `id`, `ms`; #22) — edit all of them or the
checker fails; everything but `ko` is translated from `en`. Pages with a `page.json` source
(`setup`, `cloud/02-console-tour`, `compare/02-elasticache-valkey`) are edited there and rebuilt with
`scripts/build-lang-page.py`. Status badges and tables on `docs/index.md` change when a lab runs.

Screenshots: `docs/assets/img/<slug>/NN-<name>.webp`, 2x, WebP quality 82, masked
(account ID, endpoints, e-mail, IPs, amounts) before commit. Markup:
`<img src="…" width="W" height="H" alt="<what the screen shows, in that language>" loading="lazy" decoding="async">`
followed by a paragraph with the capture date and version. No `<figure>`.
`scripts/capture-console.mjs <manifest.json>` attaches over CDP to a Chrome you are already logged
into (`--remote-debugging-port=9222`), masks in the DOM and refuses to save a screen with a leak term
still visible. Personal mask terms go in a gitignored `.env` next to the manifest.

### 5. Money and accounts

- Labels: `budget` = do nothing that bills until the user says so on the issue. Everything
  else runs on the free plan, local Docker, or kind.
- The Redis Cloud account is the user's; connection URLs and API keys live in `.env`
  (gitignored, the gitleaks rules `redis-url-password` / `redis-cloud-api-key` catch them).
- Delete what a lab creates. Record the billed amount, even $0, in `STATUS.md`.
- Iris: note the message count before and after each lab; the free allowance is 5,000.

### 6. Traps already known

- Redis has no 9.x; Valkey does. Do not mix the numbering.
- LangCache and Agent Playbooks are two services on this site (research-iris-comparison §1).
- Context Retriever was renamed Context Gateway; old package names still appear in tutorials.
- Essentials plan size includes the replica: a 1 GB plan with replication holds 512 MB.
- Redis 8 moved module commands into `@read`/`@write`; an ACL `+@all -@write` now blocks JSON writes too.
- The Vercel host does not exist until #13 is done; site rendering cannot be checked by fetching it.

## 한국어

### 1. 시작 전

```bash
git clone https://github.com/litkhai/notes-on-redis && cd notes-on-redis
git config core.hooksPath .githooks        # 커밋 시 gitleaks + 문서 검사
python3 scripts/check-docs.py -v           # 시작 전과 푸시 전에 통과해야 함
```

이슈 하나를 고른다. 번호가 작업 순서(DESIGN §7)다: #1 뼈대(첫 PR이 처리), #2 setup + local,
#3 Iris 시작하기, #4 Cloud 무료 DB + 콘솔 캡처, #5 로컬 비교, #6 딥다이브 1–4, #7 Iris 2–5,
#8 Essentials(예산), #9 enterprise, #10 딥다이브 5–8, #11 Iris 6, #12 Pro + AWS(예산),
#13 사이트 배포, #14 언어 결정. 이슈에 독립적이라고 적혀 있지 않으면 작은 번호부터.

### 2. 흐름

1. 이슈에 맡겠다는 댓글과 손댈 범위를 적는다.
2. `main`에서 브랜치: `git checkout -b <track>-<nn>-<slug>` (예 `local-01-redis-8-docker`).
3. 랩 디렉터리 안에서만 작업한다. 랩은 자족적이다: 자체 `compose.yaml`, 스크립트, `.venv`, `.env.example`.
4. 끝까지 실행한다. 실제 출력을 README에 붙인다 — 명령, 출력, 나온 버전, 날짜. 실행 못 한 단계는 "미실행"과 이유.
5. `STATUS.md` 갱신 — 랩의 행, 돈을 썼으면 *Budget spent* 표.
6. `python3 scripts/check-docs.py -v`, 커밋(훅이 gitleaks 실행), 푸시.
7. 본문에 `Closes #N`을 넣어 PR을 연다. 병합하지 않는다. 병합은 사용자가 한다.

### 3. 랩 README

스텁의 모양을 유지하며 채운다(영문 §3의 템플릿). 검사기가 못 잡는 규칙: 제목에 숫자 세기 금지,
"이 절은 … 다룬다" 금지, 버전·가격에는 항상 읽은 날짜, "Redis Labs"가 아니라 Redis Ltd.
영문과 한국어의 h3 개수가 같아야 한다(check-docs.py가 비교).

### 4. 사이트 페이지

랩의 사이트 페이지는 `docs/<track>.md`(네비 항목당 한 페이지, 랩은 그 안의 절). `.lang` 블록
일곱 개(`en`, `ko`, `zh`, `ja`, `th`, `id`, `ms`; #22) — 다 고치지 않으면 검사 실패; `ko` 외에는 `en`에서 번역.
`page.json` 원천이 있는 페이지(`setup`, `cloud/02-console-tour`, `compare/02-elasticache-valkey`)는 거기서 고치고
`scripts/build-lang-page.py`로 다시 만든다. `docs/index.md`의 배지와 표는 랩이 실행되면 바꾼다.

캡처: `docs/assets/img/<slug>/NN-<이름>.webp`, 2x, WebP 품질 82, 커밋 전에 가림(계정 ID,
엔드포인트, 이메일, IP, 금액). 마크업은 `<img … loading="lazy" decoding="async">` 뒤에 촬영
날짜·버전 문단, `<figure>` 없음. `scripts/capture-console.mjs <manifest.json>`은 이미 로그인된 Chrome에
CDP로 붙어(`--remote-debugging-port=9222`) DOM에서 가리고, 누출 문자열이 남은 화면은 저장하지 않는다.
개인 문자열은 매니페스트 옆 gitignore된 `.env`에 둔다.

### 5. 돈과 계정

- `budget` 라벨 = 사용자가 이슈에서 말하기 전엔 과금되는 것을 하지 않는다. 나머지는 무료 플랜, 로컬 Docker, kind.
- Redis Cloud 계정은 사용자 것. 접속 URL과 API 키는 `.env`(gitignore, gitleaks 규칙이 잡음).
- 랩이 만든 것은 지운다. 청구액은 $0이라도 `STATUS.md`에 적는다.
- Iris: 랩 전후의 메시지 수를 적는다. 무료 한도는 5,000.

### 6. 이미 아는 함정

- Redis에 9.x는 없다. Valkey에 있다. 번호를 섞지 않는다.
- LangCache와 Agent Playbooks는 이 사이트에서 별개 서비스(research-iris-comparison §1).
- Context Retriever → Context Gateway로 개명. 옛 패키지 이름이 튜토리얼에 남아 있다.
- Essentials 플랜 크기에 레플리카 포함: 복제 켠 1 GB 플랜의 가용 용량은 512 MB.
- Redis 8은 모듈 명령을 `@read`/`@write`에 넣었다. ACL `+@all -@write`는 이제 JSON 쓰기도 막는다.
- #13 전에는 Vercel 호스트가 없다. 사이트 렌더링을 가져와서 확인할 수 없다.
