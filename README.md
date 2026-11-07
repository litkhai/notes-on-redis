# Redis Hands-On Labs (HOLs)

**📖 [redis.litkhai.dev](https://redis.litkhai.dev)** — not deployed yet; see [STATUS.md](./STATUS.md)

[English](#english) | [한국어](#한국어)

---

## English

Practical, hands-on laboratory exercises for [Redis](https://redis.io) — Redis Open Source,
Redis Cloud, Redis Software, and **Redis Iris**, the context engine for AI agents.

Everything that reaches the site is verified by actually running it. The outputs, limits and
prices in these docs carry the date they were read or measured, not transcribed from vendor
documentation without one.

### 🎯 Purpose

- **Setup** — Redis 8 in Docker, `redis-cli`, Redis Insight, clients, a free Redis Cloud database
- **Local** — Redis Open Source on this machine: data types, Search, JSON, vector
- **Redis Cloud** — the console from sign-up to every menu, free and paid plans, REST API, Active-Active
- **Enterprise** — what Redis Software and Cloud Pro add, each tied to a lab or marked doc-only
- **Iris** — the six Iris services, one lab each, on the free plan
- **Compare** — Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis, with the same workload
- **Deep Dive** — threading, persistence, replication / Sentinel / Cluster, eviction, client-side caching, Streams, Functions, ACL

### 📁 Repository Structure

```
notes-on-redis/
├── setup/           # ← Start here
├── local/           # Redis Open Source in Docker
├── cloud/           # Redis Cloud console, plans, REST API, Active-Active
├── enterprise/      # Redis Software, RDI, Kubernetes operator
├── iris/            # Redis Iris — one lab per service
├── compare/         # Valkey, ElastiCache, the feature matrix
├── deep-dive/       # One directory per mechanism, each with a script
├── docs/            # Site source (Jekyll) → redis.litkhai.dev
├── design/          # Design and the research behind it
└── scripts/         # check-docs.py, pages-redirect.py, capture-console.mjs
```

| Track | Status | Contents |
|---|---|---|
| [`design/`](./design) | ✅ v0 | Site map, page designs, budget, order of work |
| everything else | ⬜ Not started | Directories are created with their first lab — see the design |

### How This Repository Works

Four conventions, inherited from [runpod-hols](https://github.com/litkhai/runpod-hols), each with a reason.

**Everything is verified by running it.** Command output, latency figures, plan limits and
billed amounts in these docs are produced on a real account or a real container. Where
something has *not* been run, the page says so. `STATUS.md` is the ledger.

**Labs are self-contained.** Each lab directory holds everything it needs — Compose file,
scripts, its own `.venv` — so the folder can be lifted out unchanged.

**Docs are bilingual, English first.** Every README carries a full English section and a full
Korean one. Site pages add Chinese and Japanese blocks. Interface text stays English; the
language toggle governs content, not chrome.

**The top level is flat.** `setup / local / cloud / enterprise / iris / compare / deep-dive`
sit side by side, because the repository name already says these are labs.

One convention borrowed from [notes-on-clickhouse](https://github.com/litkhai/notes-on-clickhouse):
the Redis Cloud page is a **console walkthrough** — a *verified-on* paragraph, the console
followed menu by menu with one masked screenshot per screen, and a first-week checklist.

### The Documentation Site

[`docs/`](./docs) is built by Jekyll and will be deployed to [redis.litkhai.dev](https://redis.litkhai.dev)
by Vercel on every push to `main` (project root directory `docs/`, settings in
[`docs/vercel.json`](./docs/vercel.json)). `litkhai.github.io/notes-on-redis` will publish a
redirect stub per page once the host is live.

| Choice | Why |
|---|---|
| Jekyll with a hand-written layout, no remote theme | No upstream gem to break, full control over the language toggle |
| Palette from redis.io's own page styles | `#FF4438` / `#091A23` / `#F3F3F3`, read 2026-11-07, not invented |
| Dark by default, light opt-in | A `<head>` guard applies the saved theme before first paint |
| Sidebar contents built in the browser | Each page holds four languages; a server-rendered list would duplicate every heading |

To preview locally without installing Ruby:

```bash
docker run --rm -v "$PWD/docs":/site -w /site -p 4000:4000 ruby:3.3 \
  bash -c "gem install jekyll -N && jekyll serve --host 0.0.0.0"
```

### Referenced Official Redis Resources

| Resource | Used for |
|---|---|
| [redis.io/docs](https://redis.io/docs/latest/) | Open Source, Redis Cloud, Redis Software, Iris documentation |
| [redis/redis](https://github.com/redis/redis) | Source and release notes (release notes live on GitHub only) |
| [redis.io/docs — Redis Iris](https://redis.io/docs/latest/develop/ai/context-engine/) | The six Iris services |
| [redis-developer/getting-started-with-redis-iris](https://github.com/redis-developer/getting-started-with-redis-iris/) | Iris tutorial code |
| [redis/mcp-redis](https://github.com/redis/mcp-redis) | Official MCP server, used behind Context Gateway |
| [redis.io/pricing](https://redis.io/pricing/) | Redis Cloud plans and prices (dated on every page that quotes them) |
| [valkey.io](https://valkey.io) | The comparison track |

### Getting Started

Nothing to run yet. Read [`design/DESIGN.md`](./design/DESIGN.md); the first labs land per the
order of work in its §7.

### 📄 License

[MIT](./LICENSE). Take anything here and use it.

Unofficial labs, not affiliated with Redis Ltd. Redis is a registered trademark of Redis Ltd.

---

## 한국어

[Redis](https://redis.io)를 손으로 익히는 실습 모음 — Redis Open Source, Redis Cloud, Redis
Software, 그리고 AI 에이전트용 컨텍스트 엔진 **Redis Iris**.

사이트에 올라가는 것은 모두 실제로 실행해 확인한 것이다. 출력, 한도, 가격에는 읽거나 측정한
날짜가 붙는다. 날짜 없는 벤더 문서 전사는 없다.

### 🎯 목적

- **Setup** — Docker의 Redis 8, `redis-cli`, Redis Insight, 클라이언트, 무료 Redis Cloud DB
- **Local** — 이 머신의 Redis Open Source: 자료형, Search, JSON, 벡터
- **Redis Cloud** — 가입부터 콘솔 메뉴 전체, 무료·유료 플랜, REST API, Active-Active
- **Enterprise** — Redis Software와 Cloud Pro가 더해 주는 것, 랩 또는 문서만으로 구분
- **Iris** — Iris 서비스마다 랩 하나, 무료 플랜으로
- **Compare** — Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis, 같은 워크로드로
- **Deep Dive** — 스레딩, 영속성, 복제 / Sentinel / Cluster, 축출, 클라이언트 캐시, Streams, Functions, ACL

### 📁 저장소 구조

영문 절의 트리와 같다. `design/`에 설계와 리서치가 있고, 나머지 디렉터리는 첫 랩과 함께 생긴다.

| 트랙 | 상태 | 내용 |
|---|---|---|
| [`design/`](./design) | ✅ v0 | 사이트 맵, 페이지 설계, 예산, 작업 순서 |
| 나머지 | ⬜ 미착수 | 설계 §7의 순서대로 |

### 이 저장소의 규칙

[runpod-hols](https://github.com/litkhai/runpod-hols)에서 가져온 네 가지.

**실행해서 확인한 것만 적는다.** 명령 출력, 지연 수치, 플랜 한도, 청구액은 실제 계정이나 실제
컨테이너에서 나온 것이다. 실행하지 않은 것은 페이지에 그렇게 적는다. `STATUS.md`가 장부다.

**랩은 자족적이다.** 랩 디렉터리 하나에 Compose 파일, 스크립트, 자체 `.venv`가 다 있어 그대로 들어내 쓸 수 있다.

**문서는 이중 언어, 영어가 먼저.** README마다 영어 절과 한국어 절이 모두 있다. 사이트 페이지는
중국어·일본어 블록을 더한다. UI 문구는 영어만, 언어 토글은 본문만 바꾼다.

**최상위는 평평하다.** 저장소 이름이 이미 랩이라고 말하므로 `labs/` 포장이 없다.

[notes-on-clickhouse](https://github.com/litkhai/notes-on-clickhouse)에서 가져온 하나: Redis
Cloud 페이지는 **콘솔 안내**다 — *확인 조건* 문단, 메뉴 순서대로 화면마다 가린 캡처 한 장, 첫 주 체크리스트.

### 문서 사이트

[`docs/`](./docs)는 Jekyll로 빌드되어 `main`에 푸시할 때마다 Vercel이
[redis.litkhai.dev](https://redis.litkhai.dev)로 배포한다(프로젝트 루트 `docs/`, 설정은
[`docs/vercel.json`](./docs/vercel.json)). 호스트가 살아나면 `litkhai.github.io/notes-on-redis`는
페이지마다 리다이렉트 스텁을 게시한다. 선택과 이유는 영문 절의 표와 같다.

### 참고한 Redis 공식 자료

영문 절의 표와 같다 — redis.io/docs(Open Source·Cloud·Software·Iris), redis/redis(릴리스 노트는 GitHub에만), Iris 튜토리얼 저장소, redis/mcp-redis, redis.io/pricing(인용하는 페이지마다 날짜 표기), valkey.io.

### 시작하기

아직 실행할 것이 없다. [`design/DESIGN.md`](./design/DESIGN.md)를 읽는다. 첫 랩은 §7의 순서로 올라온다.

### 📄 라이선스

[MIT](./LICENSE). 무엇이든 가져다 쓰면 된다.

비공식 랩이며 Redis Ltd.와 무관하다. Redis는 Redis Ltd.의 등록 상표다.
