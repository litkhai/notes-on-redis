# notes-on-redis — site and repository design (v0)

[English](#english) | [한국어](#한국어)

Status: **proposal, nothing deployed.** Facts come from
[`research-core-enterprise-pricing.md`](./research-core-enterprise-pricing.md) and
[`research-iris-comparison.md`](./research-iris-comparison.md) (public pages read 2026-11-07);
no lab in this design has been run yet.

---

## English

### 1. What this is

A hands-on-lab site for Redis in the mould of [runpod-hols](https://github.com/litkhai/runpod-hols)
(Jekyll, hand-written layout, four-language page blocks, everything verified by running it),
served at **redis.litkhai.dev** by Vercel with the GitHub Pages address kept as redirect stubs.
From [notes-on-clickhouse](https://github.com/litkhai/notes-on-clickhouse) it borrows the
"console walkthrough" article: a *verified-on* paragraph up top, the console followed menu by
menu with a masked screenshot per screen, and a first-week checklist at the end.

The site has to carry five things the user named, in this order of weight:

| Weight | Topic | Site section |
|---|---|---|
| ★★★ | **Redis Iris** — the context engine for agents (6 services, 4 GA + 2 beta as of 2026-11-04) | `/iris/` |
| ★★ | Redis introduction — what it is in 2026 (Redis Open Source 8.x, one distribution, AGPLv3 option) | `/` and `/setup/` |
| ★★ | Enterprise strengths — Active-Active, Flex, proxy/sharding, 99.999 %, RDI, operator, Insight | `/enterprise/` and `/cloud/` |
| ★★ | Comparison — Redis vs Valkey vs ElastiCache (Valkey / Redis OSS) vs Memorystore / Azure Managed Redis | `/compare/` |
| ★ | Deep dives — threading, persistence, replication / Sentinel / Cluster, eviction, client-side caching, Streams, Functions, ACL | `/deep-dive/` |

### 2. Site map (nav order)

```
Overview        /                 what Redis is now; three ways to run it; cards per track
Setup           /setup/           Redis 8 in Docker, redis-cli, Redis Insight, clients, Redis Cloud free DB
─────────────
Redis Cloud     /cloud/           "Redis Cloud, sign-up to every console menu" (screenshot walkthrough) + labs
Enterprise      /enterprise/      what Redis Software / Cloud Pro add, each tied to a lab or marked doc-only
Iris            /iris/            the six services; getting-started lab; one lab per GA service
─────────────
Compare         /compare/         feature matrix + same-workload labs (Redis 8 vs Valkey 9 locally; ElastiCache)
─────────────
Deep Dive       /deep-dive/       one page per mechanism, each with a reproducible experiment
  ├ Threading & event loop
  ├ Persistence (RDB, AOF, BACKUP)
  ├ Replication, Sentinel, Cluster
  ├ Eviction & memory
  ├ Client-side caching
  ├ Streams
  └ Functions & ACL
─────────────
About           /about/
```

Nav labels are English only; the language toggle switches page content (runpod-hols rule).
Every `docs/*.md` page carries `en / ko / zh / ja` blocks and `scripts/check-docs.py` enforces it.

### 3. Repository layout

```
notes-on-redis/
├── setup/                      API-free start: Docker Redis 8, redis-cli, Insight, clients, Cloud free DB
├── local/                      Redis Open Source on this machine
│   ├── 01-redis-8-docker/      run 8.x, redis-full.conf, io-threads, INFO
│   ├── 02-data-types-tour/     strings … streams, JSON, TS, probabilistic, Array (8.8), vector sets (beta)
│   └── 03-search-vector/       FT.CREATE, FT.SEARCH, FT.HYBRID (8.4+), KNN over hashes/JSON
├── cloud/                      Redis Cloud (console + REST API)
│   ├── 01-free-database/       30 MB free DB, connect over TLS, limits hit on purpose (100 ops/s, 30 conns)
│   ├── 02-console-tour/        screenshot walkthrough source (manifest + masked captures)
│   ├── 03-essentials-ha/       paid Essentials in Seoul: replication, persistence, backups, RBAC — then delete
│   ├── 04-rest-api/            account/subscription/database via REST (paid plans only)
│   └── 05-pro-active-active/   Pro: two-region Active-Active, conflict demo — needs budget decision
├── enterprise/                 Redis Software (self-managed) — what can be run without a licence
│   ├── 01-redis-software-docker/  single-node cluster in Docker (trial terms to confirm), DMC proxy, REDB
│   ├── 02-rdi/                 RDI from Postgres (Docker) into Redis — version to confirm at run time
│   └── 03-operator-kind/       Redis Enterprise operator on kind: REC + REDB
├── compare/
│   ├── 01-valkey-vs-redis-local/  Redis 8.10 vs Valkey 9.1 in Docker: command parity, modules, memory
│   ├── 02-elasticache-valkey/     ElastiCache Serverless for Valkey from Terraform — AWS cost, needs go-ahead
│   └── matrix.md               the feature/licence/pricing matrix with a source per cell
├── iris/
│   ├── 01-getting-started/     redis-iris SDK + free DB + 5,000 free messages; iris CLI
│   ├── 02-agent-memory/        session + long-term memory, MemoryETL, forgetting
│   ├── 03-intent-router/       intents → targets without an LLM call at match time
│   ├── 04-context-gateway/     one MCP endpoint over several MCP servers; Context Surfaces
│   ├── 05-agent-playbooks/     versioned FAQs/skills; the LangCache relation, stated carefully
│   └── 06-lens-and-mesh/       both beta: OTel tracing; resumable SSE / A2A task store
├── deep-dive/                  one directory per mechanism; each has a script that produces the numbers
│   ├── 01-threading/ 02-persistence/ 03-replication-sentinel/ 04-cluster/
│   ├── 05-eviction/ 06-client-side-caching/ 07-streams/ 08-functions-acl/
├── docs/                       site (Jekyll) — one page per nav item, four languages
│   └── assets/img/<slug>/NN-name.webp   screenshots (notes-on-clickhouse convention)
├── scripts/
│   ├── check-docs.py           copied from runpod-hols
│   ├── pages-redirect.py       copied from runpod-hols
│   └── capture-console.mjs     attaches to a logged-in Chrome over CDP, masks, captures from a manifest
├── design/                     this file and the research notes
├── AGENTS.md (CLAUDE.md →)     harness core + repo rules
├── STATUS.md                   what has been run, with dates and versions
└── README.md
```

Top level stays flat (runpod-hols rule). Each lab is self-contained with its own `.venv` and
`README.md` (`## English` / `## 한국어`), and a `lab.yaml` (`web: true`) so notes-on-clickhouse-style
sync could pick it up later if this ever grows into an article site — not now.

### 4. Page designs

#### 4.1 Overview `/`
- One paragraph: Redis in 2026 = one distribution (Search, JSON, Time series, probabilistic,
  vector sets) with an AGPLv3 option since 8.0; three ways to run it: Redis Open Source,
  Redis Software (self-managed), Redis Cloud. Versions stated with "read 2026-11-07".
- Cards: Setup · Redis Cloud · Enterprise · Iris · Compare · Deep Dive, each with a status badge
  from `STATUS.md` (`Not run` until it is).
- "Which Redis" table: Open Source vs Software vs Cloud (Essentials / Pro) — licence, who runs it,
  what you get, where the labs use it.
- Cost warning box: Essentials bills monthly from creation; Pro has a $200/month minimum and
  "first $200 free"; Iris gives 5,000 free messages; delete what you create.

#### 4.2 Setup `/setup/`
Docker `redis:8.x` (image tag read at run time), `redis-cli`, Redis Insight (desktop, SSPL),
Python `redis` / Node `redis` clients, Redis Cloud sign-up → free 30 MB database (no card),
`.env` with the connection URL (gitleaks rule `redis-url-password` covers it), `redis-cli -u`
smoke test. Same shape as runpod-hols `setup/`.

#### 4.3 Redis Cloud `/cloud/` — the notes-on-clickhouse-style walkthrough
Title: **"Redis Cloud, from sign-up to every console menu"**. Structure copied from
*ClickHouse Cloud 시작하기*:

1. *Verified on* paragraph — date, plan (free → Essentials), region (AWS ap-northeast-2), DB
   version; "read-only; forms opened and captured, not saved"; masked items (account ID,
   endpoints, e-mail, amounts).
2. At a glance — the left sidebar top to bottom.
3. Create database — Essentials vs Pro form, size presets, replication, persistence, modules
   (all included since 8.0), eviction policy, TLS, default-user password.
4. Database screen — Configuration, Metrics (each chart named), Slowlog, Security (RBAC roles,
   ACL rules, source IP), Backups/import, Redis Insight launch, Connect snippets.
5. Subscription screen — plan, region, payment, upgrade path to Pro.
6. Account menu — Users, API keys (REST API; works on the free plan, checked 2026-11-07), SSO/SAML, Billing & payments
   (cost report CSV), Usage, Audit/logs, Notifications.
7. First-week checklist.
8. Screenshots: `docs/assets/img/cloud-console/NN-name.webp`, 2x, WebP q82, `<img src width height alt loading="lazy" decoding="async">`
   followed by a paragraph with the capture date and version; no `<figure>`; one file for all four languages, alt text per language.

Labs on the same page: 01 free DB (hit the 100 ops/s and 30-connection limits on purpose),
03 Essentials HA in Seoul (create → replicate → persist → backup → RBAC → delete, with the
billed amount recorded), 04 REST API, 05 Pro Active-Active (gated on budget, §6).

#### 4.4 Enterprise `/enterprise/`
A table first — feature · what it is · where it exists (Software / Cloud Essentials / Cloud Pro)
· lab or doc-only — then one section per feature:

| Feature | Lab | Note |
|---|---|---|
| Active-Active (CRDT) | `cloud/05` | Pro only; up to 10 regions; JSON + Search only on A-A; memory up to 4× |
| Redis Flex (RAM + SSD) | doc-only | needs local NVMe; Cloud Flex not listed for Seoul |
| DMC proxy, sharding policies, re-sharding | `enterprise/01` | `single` / `all-master-shards` / `all-nodes` |
| 99.999 % SLA (A-A, Pro/Annual) | doc-only | SLA text quoted; cannot be measured in a lab |
| RBAC, LDAP, TLS everywhere | `cloud/03`, `enterprise/01` | |
| RDI (CDC into Redis) | `enterprise/02` | Postgres → Redis in Docker; Cloud managed RDI is Pro |
| Kubernetes operator | `enterprise/03` | kind; REC + REDB |
| Redis Insight | `setup/` | v3.8.0 (July 2026), SSPL |
| Multi-tenancy | `enterprise/01` | several REDBs on one node |

The page says plainly which rows are vendor claims and which were run.

#### 4.5 Iris `/iris/` — the important one
- What it is, in Redis's words and the CEO's "not a database" framing; timeline (2026-05-18 launch,
  2026-11-04 six services); where it runs (Redis Cloud managed; self-managed Helm chart needs a licence).
- The six-service table (GA / beta) with the docs link per row.
- The **naming trap** called out: Context Retriever → Context Gateway; LangCache vs Agent Playbooks
  (redis.io contradicts itself — the site treats them as two services and says why).
- Labs, one per service, all on the free Redis Cloud DB and the 5,000 free messages, with the
  message count after each lab recorded so the budget section is real:
  `01` getting started (`pip install 'redis-iris>=1.0.0'`, `iris` CLI, console service creation),
  `02` Agent Memory (session + long-term; MemoryETL; PII forgetting), `03` Intent Router,
  `04` Context Gateway (two MCP servers behind one endpoint; `mcp-redis` as one of them),
  `05` Agent Playbooks, `06` Lens + Agent Mesh (beta; Mesh needs Redis 8.6.2+ — run against local 8.10).
- Agent Memory on Cloud limits quoted: no Flex, no PrivateLink, no Active-Active, default user must stay on.
- "What a message is" — open question on the page until measured.

#### 4.6 Compare `/compare/`
- Licence timeline (BSD-3 → RSALv2/SSPL 7.4 → +AGPLv3 8.0; Valkey fork 7.2.4 BSD-3).
- The matrix from the research (Redis OSS 8.x / Redis Cloud·Software / Valkey 9.x / ElastiCache
  Valkey / ElastiCache Redis OSS ≤7.1 / Azure Managed Redis / Memorystore for Valkey), one source
  per cell; cells the research could not confirm are marked so.
- Lab `01`: Redis 8.10 and Valkey 9.1 side by side in Docker — command parity script
  (`COMMAND LIST` diff), modules (`JSON.*`, `FT.*`, `BF.*`, `TS.*` present?), hash field
  expiration both ways, memory for 1 M small strings, `redis-benchmark` with the same args
  (numbers reported as measured on this host, not as a verdict).
- Lab `02`: ElastiCache Serverless for Valkey via Terraform, from a Redis Cloud–shaped client
  — only after the AWS cost go-ahead; 100 MB minimum storage, "as low as $6/month" (AWS claim).
- Redis's own compare page vs Valkey quoted, with the rows the Valkey modules contradict.
- Dragonfly / KeyDB / Garnet: one paragraph each, licence and last release.

#### 4.7 Deep Dive `/deep-dive/`
One page per mechanism; each has (a) the mechanism in plain words with the official doc link,
(b) a script in `deep-dive/NN-*/` that produces a number or an observable, (c) the output as run.

| Page | Experiment |
|---|---|
| Threading & event loop | `io-threads 1` vs `N` with `redis-benchmark`; `INFO threads`; the 8.0 rewrite |
| Persistence | RDB fork/COW with `INFO persistence`; AOF `everysec` vs `always` latency; multi-part AOF files; `BACKUP START/SEAL` (8.10) and restore via `preload-file` |
| Replication, Sentinel, Cluster | 1 primary + 2 replicas in Compose; `PSYNC` partial vs full; `WAIT`; 3 Sentinels failover; 6-node cluster: `CRC16 mod 16384`, `-MOVED`, `CLUSTER MIGRATION` (8.4) |
| Eviction & memory | `maxmemory` with `allkeys-lru` vs `lfu` vs `lrm` (8.6); `maxmemory-samples`; `HOTKEYS`; key memory histograms |
| Client-side caching | `CLIENT TRACKING` default vs broadcast; invalidation seen from redis-py 5.1+ |
| Streams | consumer groups, `XAUTOCLAIM`, `XACKDEL` (8.2), `IDMP` idempotency (8.6), `XNACK` (8.8) |
| Functions & ACL | `FUNCTION LOAD` + `FCALL_RO`; ACL selectors, `%R~`/`%W~`, Redis 8 module categories and the `+@all -@write` surprise |

### 5. Site mechanics (inherited)

- Jekyll, hand-written `_layouts/default.html`, `assets/style.css` with the palette swapped to
  redis.io's own `#FF4438` / `#091A23` / `#F3F3F3` (read from the live page 2026-11-07); dark default.
- `docs/vercel.json`: framework jekyll, root `docs/`, security headers; root `vercel.json`: `regions: ["icn1"]`.
- `.github/workflows/checks.yml` (docs conventions, syntax, gitleaks, hygiene) on pull requests;
  `pages.yml` publishes redirect stubs to `litkhai.github.io/notes-on-redis` once the Vercel host is live.
- `.gitleaks.toml` adds `redis-url-password` and `redis-cloud-api-key` rules.
- Deployment steps (not done): Vercel project `notes-on-redis` in team `litkhai` (root `docs/`),
  domain `redis.litkhai.dev`, user adds the CNAME in Cloudflare (DNS only) as for runpod/quantum.

### 6. Budget

All figures from redis.io pricing page / docs read 2026-11-07; AWS from aws.amazon.com.

| Phase | What it enables | Monthly cost | Notes |
|---|---|---|---|
| **0 — Free** | setup, `local/*`, `deep-dive/*`, `compare/01`, `cloud/01`, `cloud/02` walkthrough (free parts), **all of `iris/*`** (free 30 MB DB + 5,000 free messages) | **$0** | Free DB: 30 MB, 30 connections, 100 ops/s, no replication, one per account; no card needed |
| **1 — Essentials, Seoul** | `cloud/03` (replication, persistence, backups, RBAC), `cloud/04` REST API, the paid parts of the console walkthrough | **$22–27** (1 GB) or **$6–10** (250 MB) | Billed monthly from creation; delete after the lab. Plan size includes the replica (1 GB plan → 512 MB usable). Multi-zone not priced for Seoul on the page |
| **2 — Pro** | `cloud/05` Active-Active, private connectivity, managed RDI, Flex | **$200/month minimum; "first $200 free"** | One month inside the credit is plausible but the credit terms are not published — treat $200 as the exposure; per-RBU Seoul rates only in the calculator |
| **3 — AWS** | `compare/02` ElastiCache Serverless for Valkey | AWS: 100 MB minimum, "as low as $6/month" (AWS claim); a few hours ≈ cents | Needs the usual go-ahead before `terraform apply` |
| Iris beyond free | if 5,000 messages run out | **unknown** — no rate card published; "message" undefined | Measured message consumption per lab goes on the Iris page |

Recommendation: start with phase 0 (everything important, Iris included, is free); do phase 1 for
one month (~$27) to make the Cloud walkthrough and the HA lab real; decide phase 2 only after the
Iris and Enterprise pages exist, since Active-Active is the one enterprise feature that cannot be
shown any other way. Redis Software self-managed pricing is quote-only; the Docker trial terms are
read at run time, not assumed.

### 7. Order of work (issues)

1. Repo skeleton, site shell, nav, four-language stubs, CI green — this PR.
2. `setup/` + `local/01` + `local/02` — first real `STATUS.md` rows.
3. `iris/01` getting started on the free DB — the headline page gets content first.
4. `cloud/01` + console walkthrough captures (free parts) — `capture-console.mjs` verified.
5. `compare/01` Valkey vs Redis local + `compare/matrix.md`.
6. `deep-dive/01–04`.
7. `iris/02–05`.
8. Phase 1 budget: `cloud/03`, `cloud/04`, walkthrough paid parts.
9. `enterprise/01–03`, `deep-dive/05–08`, `iris/06`.
10. Budget decision for Pro and AWS; `cloud/05`, `compare/02`.

### 8. Open decisions for the user

1. Phase 1 now (Essentials 1 GB Seoul, ~$27 for a month) or free-only until the Iris pages exist?
2. Pro ($200 credit / $200 minimum) — yes, later, or never?
3. ElastiCache lab on the personal AWS account — yes or skip (matrix only)?
4. Create the Vercel project and send the CNAME now, or after the first content lands?
5. Languages: four (en/ko/zh/ja, as runpod-hols) or two (en/ko)? Four is wired in; two halves the translation load.

---

## 한국어

### 1. 무엇을 만드는가

[runpod-hols](https://github.com/litkhai/runpod-hols)와 같은 틀(Jekyll, 자체 레이아웃, 페이지마다
4개 언어 블록, 실제로 실행해 확인한 것만 적음)의 Redis 핸즈온 랩 사이트. Vercel이
**redis.litkhai.dev**로 서비스하고 GitHub Pages 주소는 리다이렉트 스텁으로 유지한다.
[notes-on-clickhouse](https://github.com/litkhai/notes-on-clickhouse)에서는 "콘솔 안내" 글의
형식을 가져온다 — 머리에 *확인 조건* 문단, 콘솔 메뉴 순서대로 화면마다 가린 캡처 한 장,
끝에 첫 주 체크리스트.

담아야 할 다섯 가지와 무게:

| 무게 | 주제 | 섹션 |
|---|---|---|
| ★★★ | **Redis Iris** — 에이전트용 컨텍스트 엔진(서비스 6개, 2026-11-04 기준 GA 4 + 베타 2) | `/iris/` |
| ★★ | Redis 소개 — 2026년의 Redis(Open Source 8.x, 단일 배포판, AGPLv3 선택지) | `/`, `/setup/` |
| ★★ | Enterprise 특장점 — Active-Active, Flex, 프록시/샤딩, 99.999 %, RDI, 오퍼레이터, Insight | `/enterprise/`, `/cloud/` |
| ★★ | 비교 — Redis vs Valkey vs ElastiCache(Valkey / Redis OSS) vs Memorystore / Azure Managed Redis | `/compare/` |
| ★ | 딥다이브 — 스레딩, 영속성, 복제/Sentinel/Cluster, 축출, 클라이언트 캐시, Streams, Functions, ACL | `/deep-dive/` |

### 2. 사이트 맵

영문 §2와 같다. 네비게이션 라벨은 영문만, 언어 토글은 본문만 바꾼다(runpod-hols 규칙).
모든 `docs/*.md`는 `en / ko / zh / ja` 블록을 갖고 `scripts/check-docs.py`가 검사한다.

### 3. 저장소 구조

영문 §3의 트리와 같다. 최상위는 평평하게(`setup / local / cloud / enterprise / compare / iris /
deep-dive`), 랩마다 자체 `.venv`와 `README.md`(`## English` / `## 한국어`), 그리고 나중에
notes-on-clickhouse 식 카드 동기화가 가능하도록 `lab.yaml`(`web: true`)을 둔다 — 지금은 쓰지 않는다.

### 4. 페이지 설계 요약

- **Overview** — 2026년의 Redis 한 문단(단일 배포판 + AGPLv3), 실행 방식 셋(Open Source /
  Software / Cloud), 트랙 카드와 `STATUS.md` 배지, "어떤 Redis" 표, 비용 경고 박스.
- **Setup** — Docker `redis:8.x`, `redis-cli`, Redis Insight, Python/Node 클라이언트, Redis Cloud
  가입 → 무료 30 MB DB(카드 불필요), `.env`에 접속 URL, 스모크 테스트.
- **Redis Cloud** — **"Redis Cloud 시작하기: 가입부터 콘솔 메뉴 전체까지"**. *확인 조건*
  (날짜·플랜·리전 AWS 서울·DB 버전, 읽기만 함, 가린 항목) → 한눈에 보기 → 데이터베이스 만들기
  (Essentials/Pro 폼, 크기, 복제, 영속성, 모듈은 8.0부터 전부 포함, 축출 정책, TLS) →
  데이터베이스 화면(Configuration, Metrics 차트 이름별, Slowlog, Security/RBAC, Backups,
  Insight, Connect) → 구독 화면 → 계정 메뉴(Users, API keys, SSO, Billing 비용 CSV, Usage,
  Audit, Notifications) → 첫 주 체크리스트. 캡처는 `docs/assets/img/cloud-console/NN-이름.webp`
  (2x, WebP q82), `<img …>` 뒤에 촬영 날짜·버전 문단, figure 없음, 4개 언어가 같은 파일.
  같은 페이지의 랩: 01 무료 DB(100 ops/s·30 커넥션 한도를 일부러 넘겨 봄), 03 서울 Essentials
  HA(만들고 → 복제 → 영속 → 백업 → RBAC → 삭제, 청구액 기록), 04 REST API, 05 Pro Active-Active(예산 결정 후).
- **Enterprise** — 기능 · 설명 · 어디에 있나(Software / Essentials / Pro) · 랩 또는 문서만 — 표를
  먼저 두고 기능별 절. 벤더 주장과 실행한 것을 구분해 적는다(영문 §4.4 표).
- **Iris** — Redis의 정의와 CEO의 "데이터베이스가 아니다" 프레이밍, 타임라인(05-18 출시,
  11-04 6개 서비스), 실행 위치(Cloud 관리형 / 자체 Helm은 라이선스 필요), 6개 서비스 표(GA/베타),
  **이름 함정**(Context Retriever → Context Gateway; LangCache vs Agent Playbooks — redis.io가
  서로 모순이라 둘을 별개 서비스로 다룸), 서비스별 랩 6개를 모두 무료 DB + 무료 5,000 메시지로
  하고 **랩마다 소비한 메시지 수를 기록**해 예산 절을 실제 값으로 채운다. Cloud Agent Memory
  제약(Flex·PrivateLink·Active-Active 불가, default 사용자 유지) 인용. "메시지가 무엇인가"는 측정 전까지 미해결로 표시.
- **Compare** — 라이선스 연표, 리서치의 매트릭스(셀마다 출처, 미확인은 표시), 랩 01 Redis 8.10
  vs Valkey 9.1 Docker 나란히(`COMMAND LIST` 차이, 모듈 유무, hash field expiration, 1 M 문자열
  메모리, 같은 인자의 `redis-benchmark` — 이 호스트의 측정값으로만 보고), 랩 02 ElastiCache
  Serverless for Valkey(Terraform, AWS 비용 승인 후), Redis의 Valkey 비교 페이지 인용과 Valkey
  모듈이 반박하는 행, Dragonfly / KeyDB / Garnet 한 문단씩.
- **Deep Dive** — 메커니즘당 한 페이지: 평이한 설명 + 공식 문서 링크, 숫자나 관찰을 만드는 스크립트,
  실행 결과(영문 §4.7 표).

### 5. 사이트 메커니즘(상속)

Jekyll + 자체 레이아웃, 팔레트는 redis.io 페이지의 `#FF4438` / `#091A23` / `#F3F3F3`(2026-11-07
확인)로 교체, 다크 기본. `docs/vercel.json`(jekyll, 보안 헤더), 루트 `vercel.json`(`icn1`).
CI `checks.yml`(문서 규칙·문법·gitleaks·위생), `pages.yml`은 Vercel 호스트가 살아난 뒤 스텁 게시.
`.gitleaks.toml`에 `redis-url-password`, `redis-cloud-api-key` 규칙 추가. 배포 절차(미실행):
litkhai 팀에 Vercel 프로젝트 `notes-on-redis`(루트 `docs/`), 도메인 `redis.litkhai.dev`, 사용자가
Cloudflare에 CNAME(DNS only) 추가 — runpod/quantum과 같은 방식.

### 6. 예산

redis.io 가격 페이지·문서(2026-11-07 확인), AWS는 aws.amazon.com.

| 단계 | 가능해지는 것 | 월 비용 | 비고 |
|---|---|---|---|
| **0 — 무료** | setup, `local/*`, `deep-dive/*`, `compare/01`, `cloud/01`, 콘솔 안내의 무료 부분, **`iris/*` 전부**(무료 30 MB DB + 무료 5,000 메시지) | **$0** | 무료 DB: 30 MB, 30 커넥션, 100 ops/s, 복제 없음, 계정당 1개, 카드 불필요 |
| **1 — Essentials 서울** | `cloud/03`(복제·영속·백업·RBAC), `cloud/04` REST API, 콘솔 안내의 유료 부분 | **$22–27**(1 GB) 또는 **$6–10**(250 MB) | 생성 시점부터 월 과금, 랩 뒤 삭제. 플랜 크기에 복제본 포함(1 GB → 가용 512 MB). 서울은 멀티존 가격이 페이지에 없음 |
| **2 — Pro** | `cloud/05` Active-Active, 프라이빗 연결, 관리형 RDI, Flex | **최소 $200/월, "첫 $200 무료"** | 크레딧 안에서 한 달은 가능해 보이나 크레딧 조건이 미공개 — 노출액은 $200으로 봄. 서울 RBU 단가는 계산기에서만 |
| **3 — AWS** | `compare/02` ElastiCache Serverless for Valkey | 최소 100 MB, "월 $6부터"(AWS 주장); 몇 시간이면 몇 센트 | `terraform apply` 전 평소처럼 승인 필요 |
| Iris 무료 초과 | 5,000 메시지 소진 시 | **미공개** — 단가표 없음, "메시지" 정의 없음 | 랩별 메시지 소비량을 Iris 페이지에 기록 |

권고: 0단계부터(중요한 것 — Iris 포함 — 은 전부 무료). 1단계는 한 달(~$27)만 돌려 Cloud 안내와
HA 랩을 실제로 만든다. 2단계는 Iris·Enterprise 페이지가 생긴 뒤 결정 — Active-Active는 다른
방법으로 보여줄 수 없는 유일한 기능이다. Redis Software 자체 운영 가격은 견적 전용이고, Docker
트라이얼 조건은 실행 시점에 읽는다(가정하지 않음).

### 7. 작업 순서(이슈)

영문 §7과 같다: ① 뼈대·사이트 셸·CI → ② setup + local/01·02 → ③ iris/01 → ④ cloud/01 + 콘솔
캡처(무료 부분) → ⑤ compare/01 + matrix → ⑥ deep-dive/01–04 → ⑦ iris/02–05 → ⑧ 1단계 예산:
cloud/03·04 → ⑨ enterprise/01–03, deep-dive/05–08, iris/06 → ⑩ Pro·AWS 결정 뒤 cloud/05, compare/02.

### 8. 사용자가 정할 것

1. 1단계(서울 Essentials 1 GB, 한 달 ~$27)를 지금 할지, Iris 페이지가 생길 때까지 무료만 할지.
2. Pro($200 크레딧 / 최소 $200) — 예, 나중에, 안 함.
3. 개인 AWS 계정으로 ElastiCache 랩 — 예 / 매트릭스만.
4. Vercel 프로젝트 생성과 CNAME 전달 — 지금 / 첫 콘텐츠 뒤.
5. 언어: 4개(en/ko/zh/ja, runpod-hols와 같음) 또는 2개(en/ko). 4개가 연결돼 있고, 2개면 번역 부담이 반.
