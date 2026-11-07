---
layout: default
title: Iris
permalink: /iris/
---

# Iris

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: run, except Lens on Redis Cloud.** Agent Memory, Intent Router, Context Gateway and Agent Playbooks were run on the Redis Cloud free plan on 2026-11-07, and Agent Mesh on local Redis 8.10.3 (below). Lens needs an Essentials or Pro database, so only its SDK was run.
</div>

Redis Iris is, in Redis's words, "a production-ready context engine for AI agents" — a suite of services, not a database; Redis is the database underneath. Launched 2026-05-18; on 2026-11-04 it became six services: Intent Router, Agent Playbooks, Agent Memory and Context Gateway (GA), Lens and Agent Mesh (beta). Managed on Redis Cloud; self-managed via a Helm chart that needs a licence. One lab per service, all on the free database and the 5,000 free messages, with the messages consumed per lab recorded. The naming trap — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — gets its own section. Read 2026-11-07 at [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

### Is Iris usable on the free plan?

**Yes, as of 2026-11-07.** On a free account four Iris services offer a create button (Agent Memory, Agent Playbooks, Context Gateway, Intent Router). **New Lens** is greyed out, because Lens needs an Essentials or Pro records database. Agent Mesh is a library that runs in your own app. One Agent Memory service was created on the free 30 MB database, given two API keys, and used from the `redis-iris` 1.0.1 SDK and the `iris` CLI: health, writing a memory, a conversation, background extraction and recall all worked. The "5,000 free messages" were not shown anywhere in the console (Iris pages, Usage, Billing), so how many this lab used is unknown.

### Lab: Agent Memory on the free database

**Verified on redis-iris 1.0.1 (Python 3.12), Redis Cloud free plan (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07.** Source and output: [`iris/01-getting-started`](https://github.com/litkhai/notes-on-redis/tree/main/iris/01-getting-started).

<p class="shot"><img src="{{ '/assets/img/iris/01-agent-memory-landing.webp' | relative_url }}" width="1440" height="1054" alt="Agent Memory landing page with a Create Agent Memory service button" loading="lazy" decoding="async"></p>

The Agent Memory landing page on a free account. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/02-agent-memory-create-form.webp' | relative_url }}" width="1440" height="765" alt="Create Agent Memory service dialog: name, database notes-on-redis-free, default settings" loading="lazy" decoding="async"></p>

Creating a service asks for a name and a database; the free database is preselected. Defaults: short-term memory 1 day, long-term 365 days, session summary on. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/03-agent-memory-connect.webp' | relative_url }}" width="1440" height="765" alt="Connect dialog with endpoint, store ID and quick-connect tabs for agents, SDK and CLI" loading="lazy" decoding="async"></p>

The service is ready at once. Connect gives an endpoint and a store ID, and a prompt to paste into a coding agent that installs the add-agent-memory skill. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/04-api-key-form.webp' | relative_url }}" width="1440" height="765" alt="Create API key page: name, 30-day expiry, Agent Memory store with read, write, full" loading="lazy" decoding="async"></p>

Keys live in Access & Identity, across all Iris products. Each grant is one resource plus an action: read, write or full. The default for a ticked store is read. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/05-api-keys-list.webp' | relative_url }}" width="1440" height="765" alt="Access & Identity key list with two keys for Agent Memory, expiring in 30 days" loading="lazy" decoding="async"></p>

Two keys: a read key and a write key. The token is shown once, at creation. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

| Step | What happened |
|---|---|
| `health()` with the read key | `HEALTHY`: background jobs, long-term memory, session memory, source link, store database |
| `remember()` with the read key | refused: 403 `insufficient-permissions` |
| `remember()` with the write key | memory stored, topic `preferences` |
| a two-turn conversation | session `cust-1042-<timestamp>` |
| background extraction | within about 15 s: "User has a Redis Cloud database on the Free plan in the Seoul region"; a few minutes later a second memory from the assistant's answer |
| `recall()` ×10 from Korea | median 611 ms (559–1,312 ms) |
| `iris agent-memory memories search` | the same three memories, with ids and topics |

**Where it runs.** The service page lists the endpoint region as **us-east-1** while the database is in Seoul; the recall times above include that distance. **What it writes into your database:** seven keys (JSON documents and hashes) and four Search indexes (long-term memory, session memory, source links, namespaces) appeared in the free database.

<p class="shot"><img src="{{ '/assets/img/iris/06-agent-memory-services.webp' | relative_url }}" width="1440" height="765" alt="Agent Memory services list with one service on notes-on-redis-free" loading="lazy" decoding="async"></p>

The services list ties each store to its Redis Cloud database. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/07-agent-memory-service.webp' | relative_url }}" width="1440" height="1704" alt="Service configuration: endpoint region us-east-1, TTLs, summarization, memory types, sensitive-data exclusions, danger zone" loading="lazy" decoding="async"></p>

Configuration: TTLs, summarization after 20 messages keeping 10, custom memory types, sensitive-data exclusions (built-in detectors off by default). Deleting the service keeps long-term memories in your database. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/08-agent-memory-inspector.webp' | relative_url }}" width="1440" height="765" alt="Memory Inspector listing the lab's session for owner cust-1042" loading="lazy" decoding="async"></p>

Memory Inspector browses sessions and long-term memories by owner or namespace. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Agent Memory, further

**Verified on redis-iris 1.0.1, 2026-11-07.** Lab: [`iris/02-agent-memory`](https://github.com/litkhai/notes-on-redis/tree/main/iris/02-agent-memory).

| Experiment | Result |
|---|---|
| 24 messages in one session | 14 events kept plus a summary (summarise after 20, keep 10); all 24 still readable |
| Long-term memories from that session | 25 for one owner, mostly one per assistant answer |
| Memory in a `SHARED` namespace | returned to another owner only when the namespace is passed as `shared` |
| Fake email and phone, detectors off | stored verbatim as memories |
| Same with email, phone and card detectors on, "Redact match" | stored as `[REDACTED]`; the +82 number was caught too |
| MemoryETL: custom type `plan_limit`, a 9-line document | 8 typed memories in 183 s, prices left out as the prompt asked |
| `forget(owner)` | sessions and memories gone in one call (25, 3, 3) |

Extraction took 4–5 minutes in these runs against about 15 s in the first lab: it runs in the background on its own schedule.

<p class="shot"><img src="{{ '/assets/img/iris/09-agent-memory-detectors.webp' | relative_url }}" width="1440" height="765" alt="Sensitive-data exclusions with credit card, email and phone detectors set to Redact match" loading="lazy" decoding="async"></p>

Built-in detectors: credit card, email, IP, phone (US, CA, UK, DE, IL, IN, BR) and US SSN; each one redacts the match or drops the memory. When detectors disagree, dropping wins. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/11-agent-memory-extractor.webp' | relative_url }}" width="1440" height="765" alt="MemoryETL new extractor form using the plan_limit memory type" loading="lazy" decoding="async"></p>

MemoryETL (beta): an extractor copies a custom memory type's prompt and turns uploaded or API-submitted documents into memories of that type. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Intent Router

**Verified on redis-iris 1.0.1, 2026-11-07.** Four intents with three examples each, targets of four kinds; eight English and Korean queries. The embedder is the managed OpenAI `text-embedding-3-small`; no key of our own was asked for. Lab: [`iris/03-intent-router`](https://github.com/litkhai/notes-on-redis/tree/main/iris/03-intent-router).

| Query | Router default (0.70) | `min_score` 0.5 |
|---|---|---|
| I was billed twice, can you check? | fallback | billing 0.52 → tool |
| is encryption available on the free tier | fallback | tls_question 0.59 → model |
| connections keep timing out on my prod database | fallback | outage 0.51 → agent |
| tell me something funny | off_topic 0.71 → guardrail | off_topic 0.71 → guardrail |
| 무료 플랜에서 TLS를 켤 수 있나요? | fallback | tls_question 0.61 → model |
| 청구서를 어디서 받나요? | fallback | fallback, even after Korean billing examples |
| Can you recommend a good restaurant? | fallback | fallback; off_topic 0.59 after adding "맛집 추천해 줘" |

With three examples per intent the default threshold is too strict; more examples or a lower threshold is the first tuning step. Each match took 560–1,090 ms from Korea.

**Thresholds** (`thresholds.py`). A per-intent `minScore` overrides the Router's 0.70, and a per-call `min_score` overrides both, as the docs order them. With `tls_question` at 0.60 the Korean TLS question (0.61) matched; with `off_topic` at 0.85 a joke request (0.71) no longer did; a per-call 0.5 brought all five back. Router templates (`CUSTOM`, `MODEL`, `GUARDRAILS`, `AGENT`) are labels: "Every template serves the same way."

<p class="shot"><img src="{{ '/assets/img/iris/24-intent-router-intents.webp' | relative_url }}" width="1440" height="765" alt="Intent Router intents list with targets tool, model, agent and guardrail, and a Try a query box" loading="lazy" decoding="async"></p>

Intents with their targets and example counts; Try a query matches from the console. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Context Gateway

**Verified on redis-iris 1.0.1, 2026-11-07.** One Gateway in search mode with two upstreams: a Context Surface over 30 made-up products in the free database, and the public DeepWiki MCP server. Lab: [`iris/04-context-gateway`](https://github.com/litkhai/notes-on-redis/tree/main/iris/04-context-gateway).

| Step | Result |
|---|---|
| Tools the agent sees | `search_tools`, `run_tool` |
| search "black lamps under 100 dollars" | `products__filter_product` |
| Surface from one entity, six fields | ten generated tools (count, filter, text search, set operations, expand) |
| Filter: lamp, black, price ≤ 100 | the same 3 products a direct scan found; 2.4 s |
| Wrong argument shape | refused with `invalid_arguments`, tool not called |
| `deepwiki__read_wiki_structure` redis/redis | page list through the Gateway; 1.5 s |

`mcp-redis` was not used: an upstream has to be reachable from Redis Cloud, and this host does not serve one publicly. The Surface covers Redis data as tools.

<p class="shot"><img src="{{ '/assets/img/iris/19-context-surface-fields.webp' | relative_url }}" width="1440" height="1284" alt="Context Surface fields: id as primary key, name text index, category and colour tag indexes, price and stock numeric" loading="lazy" decoding="async"></p>

A Context Surface is a data model: entities mapped to key templates, fields typed and indexed. The Gateway builds the search tools from it. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/25-context-gateway-upstreams.webp' | relative_url }}" width="1440" height="765" alt="Gateway upstreams: products Context Surface with 10 tools and deepwiki MCP server with 3" loading="lazy" decoding="async"></p>

Both upstreams behind one endpoint, each switchable on or off. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Agent Playbooks

**Verified on redis-iris 1.0.1, 2026-11-07.** Four FAQs written from this site's findings, authored as JSON and synced with the `iris` CLI. Lab: [`iris/05-agent-playbooks`](https://github.com/litkhai/notes-on-redis/tree/main/iris/05-agent-playbooks).

| Question | Found |
|---|---|
| is encryption in transit available on the free tier? | free-plan-tls 0.75 |
| how many clients can connect to the free database | free-plan-limits 0.76 |
| MSET fails with a slot error on my cluster | crossslot-error 0.85 |
| 무료 DB에서 TLS 켤 수 있어? | free-plan-tls 0.78 |
| How do I configure Active-Active between Seoul and Tokyo? | nothing; proposed for review instead |

A second version of an FAQ stayed a draft and discovery kept serving version 1 until `faqs publish --version 2`. Keys follow the same workflow: read, write, propose, publish, full. The console lists Agent Playbooks and no LangCache entry.

**Skills and proposals** (`more.py`). A skill is a zipped folder with `SKILL.md` and reference files; this one checks a workload against the free plan's measured limits. Once published, `discover` returned it for an English sizing question and an agent loaded its steps and reference file on demand. The open proposal was edited, accepted into an unpublished FAQ, and found by `discover` only after `publish_faq`.

<p class="shot"><img src="{{ '/assets/img/iris/27-playbook-registry.webp' | relative_url }}" width="1440" height="765" alt="Playbook registry with four published FAQs, one at version 2" loading="lazy" decoding="async"></p>

The registry shows publication state and latest version per FAQ. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/28-playbook-proposals.webp' | relative_url }}" width="1440" height="765" alt="Proposals inbox with one open proposal about Active-Active" loading="lazy" decoding="async"></p>

Proposals wait in an inbox until someone accepts and publishes them. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Agent Mesh and Lens (beta)

**Verified on redis-iris 1.0.1 with Redis 8.10.3 in local Docker, 2026-11-07.** Agent Mesh keeps an agent's progress events in a Redis stream, so a client that disconnects can come back to any server and receive what it missed. From the docs: "When the client reconnects, it can receive retained updates after its last event cursor." It needs Redis 8.6.2+ for `XADD IDMP` ([Deep Dive]({{ '/deep-dive/' | relative_url }})), and "Cloud, Enterprise, failover recovery, and sustained capacity remain unqualified for this beta." The lab ran each integration as two replicas and moved the client from one to the other.

| Experiment | Result |
|---|---|
| FastAPI SSE: read steps 1–5 from replica A, away 3 s, reconnect to replica B with `Last-Event-ID` | B replayed 6–11, then 12–20 live; all 20 exactly once |
| Reconnect at the final cursor / malformed cursor / unknown run | HTTP 204 / 422 `invalid_cursor` / 404 |
| What one run leaves in Redis | one stream, `XLEN 22`, IDMP on, TTL 120 s after completion |
| Replica A killed mid-run, SDK defaults | no final event: B closed and reopened the connection every 35 s |
| Same, with `REDIS_SOCKET_TIMEOUT=30` | `stream.end` `producer_lost` after the silence timeout |
| A2A: Task versions 1–4 from A, reconnect to B with `Last-Event-ID: 4` | versions 5–12 and the completed status; ten artifacts, each once |

**The one trap found:** redis-py 8.1.0 sets a 5 s socket timeout by default, shorter than the SDK's 15 s blocking read. The SDK takes each timeout for a Redis outage, so it never declares the producer lost. Set `REDIS_SOCKET_TIMEOUT` above the heartbeat interval.

Lens traces agent turns over OpenTelemetry. On Redis Cloud its records database must be "A Redis Cloud Essentials or Pro database", so on the free plan **New Lens** is disabled. Pointed at a loopback receiver instead, the SDK sent one OTLP/HTTP request per turn. The turn's spans included the Agent Memory search, recorded with no extra code, plus the app's own retrieval and a custom step. With `IRIS_LENS_CAPTURE_CONTENT=false` the query and document texts were dropped, leaving IDs, scores and hashes. Docs: [Agent Mesh](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/), [FastAPI SSE SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/fastapi-sse-sdk/), [A2A SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/a2a-sdk/), [Lens](https://redis.io/docs/latest/develop/ai/context-engine/lens/), [Create Lens](https://redis.io/docs/latest/operate/iris/lens/create-lens/). Lab: [`iris/06-lens-and-mesh`](https://github.com/litkhai/notes-on-redis/tree/main/iris/06-lens-and-mesh).

**Handing off a task** (`mesh_takeover.py`). With `takeover=True`, a task whose process was killed after three of six steps was refused on another replica while the dead process's heartbeat lease lasted (a refusal still returns HTTP 200; only the Task history shows it), then claimed at 15.1 s; the new process skipped the finished steps and completed the rest. With the default `takeover=False`, a reader marked the same task failed with `producer_lost` after 12.1 s, and it could not be resumed.

<p class="shot"><img src="{{ '/assets/img/iris/29-lens-free-plan.webp' | relative_url }}" width="1440" height="1351" alt="The Lens page in the Redis Cloud console with the New Lens button greyed out on a free-plan account" loading="lazy" decoding="async"></p>

On the free plan, New Lens is disabled. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/iris/30-agent-mesh.webp' | relative_url }}" width="1440" height="1121" alt="The Agent Mesh page in the console: a library for resumable SSE and A2A streams on Redis, with no create button" loading="lazy" decoding="async"></p>

Agent Mesh has a page but nothing to create: it runs inside your own app. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### What Iris costs the free database

The services keep their data and their connection pools in the database you pick. With Agent Memory, Intent Router, a Context Surface and a Playbook all on the free database, nothing of ours running, on 2026-11-07:

| Resource | Used | How it was seen |
|---|---|---|
| Connections | 28 of 30 | `CLIENT LIST`: 28 `go-redis` clients from AWS us-east-1 addresses, plus our one check |
| Data | 16.7 MB of 30 MB, 111 keys | console Configuration card; keys `iris:intent:*` 25, `memory:*` 44, `iris:playbook:*` 12, plus 30 lab products |
| Alert | email from Redis | "The number of connections for your database has reached 93.33% of the connections limit" |

On the free plan that leaves two connections for an application. Give Iris its own database, or a plan with more connections, before putting real traffic next to it.

### Not covered yet

Lens on Redis Cloud waits for the Essentials budget in [#8](https://github.com/litkhai/notes-on-redis/issues/8): creating it, the Lens UI, reading turns back and model-call tracing. Message consumption stays an open question until the console or the bill shows it.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: Redis Cloud의 Lens만 빼고 실행.** Agent Memory, Intent Router, Context Gateway, Agent Playbooks는 2026-11-07에 Redis Cloud 무료 플랜에서, Agent Mesh는 로컬 Redis 8.10.3에서 실행했다(아래). Lens는 Essentials나 Pro DB가 필요해 SDK만 실행했다.
</div>

Redis Iris는 Redis의 표현으로 "AI 에이전트를 위한 프로덕션 준비 컨텍스트 엔진" — 서비스 묶음이지 데이터베이스가 아니고, 밑에 있는 데이터베이스가 Redis다. 2026-05-18 출시, 2026-11-04에 서비스 여섯이 됨: Intent Router, Agent Playbooks, Agent Memory, Context Gateway(GA), Lens, Agent Mesh(베타). Redis Cloud 관리형, 자체 운영은 라이선스가 필요한 Helm 차트. 서비스마다 랩 하나, 모두 무료 DB와 무료 5,000 메시지로, 랩마다 소비한 메시지 수를 기록. 이름 함정 — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — 은 별도 절. 2026-11-07 [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)에서 읽음.

### 무료 플랜에서 Iris를 쓸 수 있나?

**2026-11-07 기준으로 그렇다.** 무료 계정에서도 Iris 서비스 넷에 만들기 버튼이 있다(Agent Memory, Agent Playbooks, Context Gateway, Intent Router). **New Lens**는 회색으로 비활성이다. Lens는 기록용 DB가 Essentials나 Pro여야 하기 때문이다. Agent Mesh는 내 앱 안에서 도는 라이브러리다. 무료 30 MB DB에 Agent Memory 서비스를 하나 만들고 API 키 두 개를 발급해 `redis-iris` 1.0.1 SDK와 `iris` CLI로 썼다. 상태 확인, 기억 쓰기, 대화, 백그라운드 추출, 회상이 모두 됐다. "무료 메시지 5,000개"는 콘솔 어디에도(Iris 화면, Usage, Billing) 보이지 않아, 이 실습이 몇 개를 썼는지는 모른다.

### 실습: 무료 DB 위의 Agent Memory

**확인: redis-iris 1.0.1(Python 3.12), Redis Cloud 무료 플랜(Redis 8.6.2, AWS ap-northeast-2), 2026-11-07.** 소스와 출력: [`iris/01-getting-started`](https://github.com/litkhai/notes-on-redis/tree/main/iris/01-getting-started).

<p class="shot"><img src="{{ '/assets/img/iris/01-agent-memory-landing.webp' | relative_url }}" width="1440" height="1054" alt="Create Agent Memory service 버튼이 있는 Agent Memory 첫 화면" loading="lazy" decoding="async"></p>

무료 계정의 Agent Memory 첫 화면. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/02-agent-memory-create-form.webp' | relative_url }}" width="1440" height="765" alt="Create Agent Memory service 창: 이름, DB notes-on-redis-free, 기본 설정" loading="lazy" decoding="async"></p>

서비스를 만들 때는 이름과 DB만 묻는다. 무료 DB가 미리 선택돼 있다. 기본값: 단기 기억 1일, 장기 기억 365일, 세션 요약 켬. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/03-agent-memory-connect.webp' | relative_url }}" width="1440" height="765" alt="엔드포인트, Store ID, 에이전트·SDK·CLI 빠른 연결 탭이 있는 Connect 창" loading="lazy" decoding="async"></p>

서비스는 바로 준비된다. Connect는 엔드포인트와 Store ID, 그리고 코딩 에이전트에 붙여 넣으면 add-agent-memory 스킬을 설치하는 프롬프트를 준다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/04-api-key-form.webp' | relative_url }}" width="1440" height="765" alt="API 키 만들기 화면: 이름, 30일 만료, read·write·full이 있는 Agent Memory 스토어" loading="lazy" decoding="async"></p>

키는 Iris 전체 제품에 걸친 Access & Identity에 있다. 권한 하나는 리소스 하나와 동작(read, write, full)이다. 스토어를 고르면 기본은 read다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/05-api-keys-list.webp' | relative_url }}" width="1440" height="765" alt="30일 뒤 만료되는 Agent Memory 키 두 개가 있는 Access & Identity 목록" loading="lazy" decoding="async"></p>

키 두 개: read 키와 write 키. 토큰은 만들 때 한 번만 보인다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

| 단계 | 결과 |
|---|---|
| read 키로 `health()` | `HEALTHY`: 백그라운드 작업, 장기 기억, 세션 기억, 소스 링크, 저장 DB |
| read 키로 `remember()` | 거절: 403 `insufficient-permissions` |
| write 키로 `remember()` | 기억 저장, 주제 `preferences` |
| 두 턴짜리 대화 | 세션 `cust-1042-<시각>` |
| 백그라운드 추출 | 약 15초 안에 "User has a Redis Cloud database on the Free plan in the Seoul region". 몇 분 뒤 어시스턴트 답변에서 두 번째 기억 |
| 한국에서 `recall()` 10회 | 중앙값 611 ms(559–1,312 ms) |
| `iris agent-memory memories search` | 같은 기억 세 개, ID와 주제 포함 |

**어디서 도나.** 서비스 화면의 엔드포인트 리전은 **us-east-1**이고 DB는 서울이다. 위 회상 시간에는 그 거리가 들어 있다. **내 DB에 쓰는 것:** 무료 DB에 키 7개(JSON 문서와 해시)와 Search 인덱스 4개(장기 기억, 세션 기억, 소스 링크, 네임스페이스)가 생겼다.

<p class="shot"><img src="{{ '/assets/img/iris/06-agent-memory-services.webp' | relative_url }}" width="1440" height="765" alt="notes-on-redis-free 위의 서비스 하나가 있는 Agent Memory 서비스 목록" loading="lazy" decoding="async"></p>

서비스 목록은 스토어마다 연결된 Redis Cloud DB를 보여 준다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/07-agent-memory-service.webp' | relative_url }}" width="1440" height="1704" alt="서비스 설정: 엔드포인트 리전 us-east-1, TTL, 요약, 기억 유형, 민감 데이터 제외, 위험 구역" loading="lazy" decoding="async"></p>

설정: TTL, 메시지 20개마다 요약하고 10개 유지, 사용자 정의 기억 유형, 민감 데이터 제외(내장 탐지기는 기본 꺼짐). 서비스를 지워도 장기 기억은 내 DB에 남는다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/08-agent-memory-inspector.webp' | relative_url }}" width="1440" height="765" alt="소유자 cust-1042의 실습 세션이 보이는 Memory Inspector" loading="lazy" decoding="async"></p>

Memory Inspector는 소유자나 네임스페이스로 세션과 장기 기억을 살펴본다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### Agent Memory 더 깊이

**확인: redis-iris 1.0.1, 2026-11-07.** 실습: [`iris/02-agent-memory`](https://github.com/litkhai/notes-on-redis/tree/main/iris/02-agent-memory).

| 실험 | 결과 |
|---|---|
| 한 세션에 메시지 24개 | 이벤트 14개와 요약(20개에서 요약, 10개 유지). 24개 모두 읽을 수 있음 |
| 그 세션의 장기 기억 | 소유자 한 명에게 25개, 대부분 어시스턴트 답마다 하나 |
| `SHARED` 네임스페이스의 기억 | 다른 소유자가 그 네임스페이스를 `shared`로 넘길 때만 돌아옴 |
| 가짜 이메일·전화, 탐지기 끔 | 그대로 기억으로 저장 |
| 이메일·전화·카드 탐지기 켬, "Redact match" | `[REDACTED]`로 저장. +82 번호도 잡힘 |
| MemoryETL: 사용자 정의 유형 `plan_limit`, 9줄 문서 | 183초에 유형 있는 기억 8개, 프롬프트대로 가격 제외 |
| `forget(owner)` | 세션과 기억이 한 번에 사라짐(25, 3, 3) |

이번 실행의 추출은 첫 실습의 약 15초와 달리 4–5분이 걸렸다. 백그라운드에서 자체 일정으로 돈다.

<p class="shot"><img src="{{ '/assets/img/iris/09-agent-memory-detectors.webp' | relative_url }}" width="1440" height="765" alt="신용카드·이메일·전화 탐지기를 Redact match로 둔 민감 데이터 제외 설정" loading="lazy" decoding="async"></p>

내장 탐지기: 신용카드, 이메일, IP, 전화(US, CA, UK, DE, IL, IN, BR), 미국 SSN. 각각 일치 부분을 가리거나 기억을 버린다. 탐지기끼리 다르면 버리는 쪽이 이긴다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/11-agent-memory-extractor.webp' | relative_url }}" width="1440" height="765" alt="plan_limit 기억 유형을 쓰는 MemoryETL 새 extractor 양식" loading="lazy" decoding="async"></p>

MemoryETL(베타): extractor는 사용자 정의 기억 유형의 프롬프트를 복사해, 올리거나 API로 보낸 문서를 그 유형의 기억으로 바꾼다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### Intent Router

**확인: redis-iris 1.0.1, 2026-11-07.** 예시 셋씩인 의도 네 개, 대상 네 종류, 영어·한국어 질문 여덟 개. 임베딩은 관리형 OpenAI `text-embedding-3-small`이고 내 키는 요구하지 않았다. 실습: [`iris/03-intent-router`](https://github.com/litkhai/notes-on-redis/tree/main/iris/03-intent-router).

| 질문 | Router 기본값(0.70) | `min_score` 0.5 |
|---|---|---|
| I was billed twice, can you check? | 대체 경로 | billing 0.52 → 도구 |
| is encryption available on the free tier | 대체 경로 | tls_question 0.59 → 모델 |
| connections keep timing out on my prod database | 대체 경로 | outage 0.51 → 에이전트 |
| tell me something funny | off_topic 0.71 → 가드레일 | off_topic 0.71 → 가드레일 |
| 무료 플랜에서 TLS를 켤 수 있나요? | 대체 경로 | tls_question 0.61 → 모델 |
| 청구서를 어디서 받나요? | 대체 경로 | 한국어 청구 예시를 넣어도 대체 경로 |
| Can you recommend a good restaurant? | 대체 경로 | 대체 경로, "맛집 추천해 줘" 추가 뒤 off_topic 0.59 |

의도마다 예시 셋이면 기본 임계값이 너무 엄격하다. 예시를 늘리거나 임계값을 낮추는 것이 첫 조정이다. 매칭은 한국에서 건마다 560–1,090 ms였다.

**임계값**(`thresholds.py`). 의도별 `minScore`는 Router의 0.70을 덮어쓰고, 호출별 `min_score`는 둘 다 덮어쓴다. 문서의 순서 그대로다. `tls_question`을 0.60으로 두자 한국어 TLS 질문(0.61)이 매칭됐고, `off_topic`을 0.85로 두자 농담 요청(0.71)은 더는 매칭되지 않았다. 호출별 0.5는 다섯 질의를 모두 되살렸다. Router 템플릿(`CUSTOM`, `MODEL`, `GUARDRAILS`, `AGENT`)은 라벨이다: "Every template serves the same way."

<p class="shot"><img src="{{ '/assets/img/iris/24-intent-router-intents.webp' | relative_url }}" width="1440" height="765" alt="도구·모델·에이전트·가드레일 대상이 있는 Intent Router 의도 목록과 질의 시험 칸" loading="lazy" decoding="async"></p>

의도와 대상, 예시 수. Try a query로 콘솔에서 바로 맞춰 볼 수 있다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### Context Gateway

**확인: redis-iris 1.0.1, 2026-11-07.** 검색 모드 게이트웨이 하나에 업스트림 둘. 무료 DB의 가짜 상품 30개로 만든 Context Surface와 공개 DeepWiki MCP 서버. 실습: [`iris/04-context-gateway`](https://github.com/litkhai/notes-on-redis/tree/main/iris/04-context-gateway).

| 단계 | 결과 |
|---|---|
| 에이전트에게 보이는 도구 | `search_tools`, `run_tool` |
| "black lamps under 100 dollars" 검색 | `products__filter_product` |
| 필드 여섯 개짜리 엔티티 하나로 만든 Surface | 도구 열 개 자동 생성(개수, 필터, 텍스트 검색, 집합 연산, 확장) |
| 필터: lamp, black, 가격 ≤ 100 | DB를 직접 훑은 결과와 같은 상품 3개, 2.4초 |
| 인자 형식이 틀림 | `invalid_arguments`로 거절, 도구 호출 안 됨 |
| `deepwiki__read_wiki_structure` redis/redis | 게이트웨이를 거쳐 페이지 목록, 1.5초 |

`mcp-redis`는 쓰지 않았다. 업스트림은 Redis Cloud에서 닿아야 하는데 이 호스트는 공개로 띄우지 않는다. Redis 데이터를 도구로 쓰는 것은 Surface가 맡는다.

<p class="shot"><img src="{{ '/assets/img/iris/19-context-surface-fields.webp' | relative_url }}" width="1440" height="1284" alt="Context Surface 필드: 기본 키 id, 텍스트 색인 name, 태그 색인 category·colour, 숫자 price·stock" loading="lazy" decoding="async"></p>

Context Surface는 데이터 모델이다. 엔티티를 키 템플릿에 대응시키고 필드에 유형과 색인을 준다. 게이트웨이가 여기서 검색 도구를 만든다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/25-context-gateway-upstreams.webp' | relative_url }}" width="1440" height="765" alt="게이트웨이 업스트림: 도구 10개인 products Context Surface와 도구 3개인 deepwiki MCP 서버" loading="lazy" decoding="async"></p>

두 업스트림이 엔드포인트 하나 뒤에 있고, 각각 켜고 끌 수 있다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### Agent Playbooks

**확인: redis-iris 1.0.1, 2026-11-07.** 이 사이트의 발견으로 쓴 FAQ 네 개를 JSON으로 작성해 `iris` CLI로 동기화했다. 실습: [`iris/05-agent-playbooks`](https://github.com/litkhai/notes-on-redis/tree/main/iris/05-agent-playbooks).

| 질문 | 찾은 것 |
|---|---|
| is encryption in transit available on the free tier? | free-plan-tls 0.75 |
| how many clients can connect to the free database | free-plan-limits 0.76 |
| MSET fails with a slot error on my cluster | crossslot-error 0.85 |
| 무료 DB에서 TLS 켤 수 있어? | free-plan-tls 0.78 |
| How do I configure Active-Active between Seoul and Tokyo? | 없음. 대신 검토용으로 제안 |

FAQ의 두 번째 버전은 초안으로 남았고, `faqs publish --version 2` 전까지 검색은 버전 1을 냈다. 키도 같은 흐름을 따른다: read, write, propose, publish, full. 콘솔에는 Agent Playbooks가 있고 LangCache 항목은 없다.

**Skill과 제안**(`more.py`). Skill은 `SKILL.md`와 참조 파일을 담은 압축 폴더다. 이 skill은 무료 플랜의 측정 한도로 워크로드를 판정한다. 게시 뒤 영어 용량 질문에 `discover`가 이것을 돌려줬고, 에이전트는 단계와 참조 파일을 필요할 때 불러왔다. 열린 제안은 고쳐 쓴 뒤 게시되지 않은 FAQ로 수락됐고, `publish_faq` 뒤에야 `discover`에 나왔다.

<p class="shot"><img src="{{ '/assets/img/iris/27-playbook-registry.webp' | relative_url }}" width="1440" height="765" alt="FAQ 네 개가 공개됐고 하나는 버전 2인 Playbook 레지스트리" loading="lazy" decoding="async"></p>

레지스트리는 FAQ마다 공개 상태와 최신 버전을 보여 준다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/28-playbook-proposals.webp' | relative_url }}" width="1440" height="765" alt="Active-Active에 관한 열린 제안 하나가 있는 제안함" loading="lazy" decoding="async"></p>

제안은 누군가 받아들이고 공개할 때까지 제안함에서 기다린다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### Agent Mesh와 Lens(베타)

**확인: redis-iris 1.0.1, 로컬 Docker의 Redis 8.10.3, 2026-11-07.** Agent Mesh는 에이전트의 진행 이벤트를 Redis 스트림에 담아, 끊긴 클라이언트가 어느 서버로 돌아오든 놓친 것을 받게 한다. 문서의 표현: "When the client reconnects, it can receive retained updates after its last event cursor." `XADD IDMP`([Deep Dive]({{ '/deep-dive/' | relative_url }})) 때문에 Redis 8.6.2 이상이 필요하고, "Cloud, Enterprise, failover recovery, and sustained capacity remain unqualified for this beta." 실습은 통합 방식마다 복제본 둘을 띄우고 클라이언트를 한쪽에서 다른 쪽으로 옮겼다.

| 실험 | 결과 |
|---|---|
| FastAPI SSE: 복제본 A에서 1–5단계를 읽고 3초 떠났다가 `Last-Event-ID`로 복제본 B에 재연결 | B가 6–11을 재생하고 12–20을 실시간으로. 20단계 모두 정확히 한 번 |
| 마지막 커서 / 잘못된 커서 / 모르는 실행으로 재연결 | HTTP 204 / 422 `invalid_cursor` / 404 |
| 실행 하나가 Redis에 남기는 것 | 스트림 하나, `XLEN 22`, IDMP 사용, 완료 뒤 TTL 120초 |
| 실행 중 복제본 A를 죽임, SDK 기본 설정 | 최종 이벤트 없음: B가 35초마다 연결을 닫고 다시 열기를 반복 |
| 같은 상황, `REDIS_SOCKET_TIMEOUT=30` | 침묵 제한 뒤 `stream.end` `producer_lost` |
| A2A: A에서 Task 버전 1–4, `Last-Event-ID: 4`로 B에 재연결 | 버전 5–12와 완료 상태. 아티팩트 10개 각각 한 번 |

**찾은 함정 하나:** redis-py 8.1.0은 소켓 제한 시간 기본값이 5초로, SDK의 15초 블로킹 읽기보다 짧다. SDK는 시간 초과를 매번 Redis 장애로 여겨 생산자 유실을 선언하지 않는다. `REDIS_SOCKET_TIMEOUT`을 하트비트 간격보다 길게 둔다.

Lens는 OpenTelemetry로 에이전트 턴을 추적한다. Redis Cloud에서는 기록용 DB가 "A Redis Cloud Essentials or Pro database"여야 해서 무료 플랜에서는 **New Lens**가 비활성이다. 대신 루프백 수신기를 가리키게 하자 SDK는 턴마다 OTLP/HTTP 요청 하나를 보냈다. 턴의 스팬에는 코드를 더하지 않아도 기록된 Agent Memory 검색, 앱 자체 검색, 사용자 정의 단계가 있었다. `IRIS_LENS_CAPTURE_CONTENT=false`면 질의와 문서 텍스트가 빠지고 ID, 점수, 해시만 남았다. 문서: [Agent Mesh](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/), [FastAPI SSE SDK 가이드](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/fastapi-sse-sdk/), [A2A SDK 가이드](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/a2a-sdk/), [Lens](https://redis.io/docs/latest/develop/ai/context-engine/lens/), [Create Lens](https://redis.io/docs/latest/operate/iris/lens/create-lens/). 실습: [`iris/06-lens-and-mesh`](https://github.com/litkhai/notes-on-redis/tree/main/iris/06-lens-and-mesh).

**태스크 넘기기**(`mesh_takeover.py`). `takeover=True`에서는 여섯 단계 중 셋을 마치고 프로세스가 죽은 태스크를, 죽은 프로세스의 하트비트 임대가 남아 있는 동안 다른 복제본이 거절당했다(거절도 HTTP 200을 돌려주고, Task 기록으로만 알 수 있다). 15.1초에 넘겨받았고, 새 프로세스는 끝난 단계를 건너뛰고 나머지를 마쳤다. 기본값 `takeover=False`에서는 리더가 12.1초 뒤 같은 태스크를 `producer_lost`로 실패 처리했고, 다시 재개할 수 없었다.

<p class="shot"><img src="{{ '/assets/img/iris/29-lens-free-plan.webp' | relative_url }}" width="1440" height="1351" alt="Redis Cloud 콘솔의 Lens 페이지. 무료 플랜 계정이라 New Lens 버튼이 회색으로 비활성" loading="lazy" decoding="async"></p>

무료 플랜에서는 New Lens가 비활성이다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/iris/30-agent-mesh.webp' | relative_url }}" width="1440" height="1121" alt="콘솔의 Agent Mesh 페이지: Redis 위의 재개 가능한 SSE·A2A 스트림용 라이브러리, 만들기 버튼 없음" loading="lazy" decoding="async"></p>

Agent Mesh는 페이지만 있고 만들 것은 없다. 내 앱 안에서 돈다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### Iris가 무료 DB에서 쓰는 것

서비스들은 고른 DB에 데이터와 커넥션 풀을 둔다. Agent Memory, Intent Router, Context Surface, Playbook을 모두 무료 DB에 두고 우리 쪽은 아무것도 돌리지 않은 2026-11-07 상태:

| 자원 | 사용량 | 확인 방법 |
|---|---|---|
| 커넥션 | 30개 중 28개 | `CLIENT LIST`: AWS us-east-1 주소의 `go-redis` 클라이언트 28개와 우리 확인용 연결 1개 |
| 데이터 | 30 MB 중 16.7 MB, 키 111개 | 콘솔 Configuration 카드. 키 `iris:intent:*` 25, `memory:*` 44, `iris:playbook:*` 12, 실습 상품 30 |
| 알림 | Redis의 이메일 | "The number of connections for your database has reached 93.33% of the connections limit" |

무료 플랜이면 애플리케이션에 남는 커넥션은 두 개다. 실제 트래픽을 옆에 두기 전에 Iris에 별도 DB나 커넥션이 더 많은 플랜을 준다.

### 아직 다루지 않은 것

Redis Cloud의 Lens는 [#8](https://github.com/litkhai/notes-on-redis/issues/8)의 Essentials 예산을 기다린다: 생성, Lens UI, 턴 읽기, 모델 호출 추적. 메시지 사용량은 콘솔이나 청구서에 나타날 때까지 열린 질문으로 둔다.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：除 Redis Cloud 上的 Lens 外均已运行。** Agent Memory、Intent Router、Context Gateway 和 Agent Playbooks 于 2026-11-07 在 Redis Cloud 免费计划上运行，Agent Mesh 在本地 Redis 8.10.3 上运行（见下）。Lens 需要 Essentials 或 Pro 数据库，所以只运行了它的 SDK。
</div>

Redis Iris 用 Redis 自己的话说是 "a production-ready context engine for AI agents" —— 它是一组服务，不是数据库；底层的数据库是 Redis。2026-05-18 发布，2026-11-04 变为六项服务：Intent Router、Agent Playbooks、Agent Memory 和 Context Gateway（GA），以及 Lens 和 Agent Mesh（beta）。在 Redis Cloud 上托管；自行部署则通过需要许可证的 Helm chart。每项服务一个实验，全部使用免费数据库和 5,000 条免费消息，并记录每个实验消耗的消息数。命名陷阱 —— Context Retriever → Context Gateway，LangCache 与 Agent Playbooks —— 单独成节。2026-11-07 阅读于 [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)。

### Iris 能在免费计划上使用吗？

**能，截至 2026-11-07。** 免费账户上有四项 Iris 服务提供创建按钮（Agent Memory、Agent Playbooks、Context Gateway、Intent Router）。**New Lens** 是灰色的，因为 Lens 需要 Essentials 或 Pro 的记录数据库。Agent Mesh 是在你自己的应用中运行的库。在免费的 30 MB 数据库上创建了一个 Agent Memory 服务，发放了两个 API 密钥，并通过 `redis-iris` 1.0.1 SDK 和 `iris` CLI 使用：健康检查、写入记忆、对话、后台提取和召回都正常。“5,000 条免费消息”在控制台的任何地方（Iris 页面、Usage、Billing）都没有显示，所以这个实验用了多少条未知。

### 实验：免费数据库上的 Agent Memory

**已在 redis-iris 1.0.1（Python 3.12）、Redis Cloud 免费计划（Redis 8.6.2，AWS ap-northeast-2）上验证，2026-11-07。** 源码和输出：[`iris/01-getting-started`](https://github.com/litkhai/notes-on-redis/tree/main/iris/01-getting-started)。

<p class="shot"><img src="{{ '/assets/img/iris/01-agent-memory-landing.webp' | relative_url }}" width="1440" height="1054" alt="Agent Memory 落地页，带有 Create Agent Memory service 按钮" loading="lazy" decoding="async"></p>

免费账户上的 Agent Memory 落地页。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/02-agent-memory-create-form.webp' | relative_url }}" width="1440" height="765" alt="Create Agent Memory service 对话框：名称、数据库 notes-on-redis-free、默认设置" loading="lazy" decoding="async"></p>

创建服务需要名称和数据库；免费数据库已预先选中。默认值：短期记忆 1 天，长期记忆 365 天，会话摘要开启。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/03-agent-memory-connect.webp' | relative_url }}" width="1440" height="765" alt="Connect 对话框，含端点、store ID 以及用于 agents、SDK 和 CLI 的快速连接标签页" loading="lazy" decoding="async"></p>

服务立即就绪。Connect 提供端点和 store ID，以及一段可粘贴到编码代理中的提示词，用于安装 add-agent-memory skill。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/04-api-key-form.webp' | relative_url }}" width="1440" height="765" alt="Create API key 页面：名称、30 天有效期、Agent Memory store，权限 read、write、full" loading="lazy" decoding="async"></p>

密钥位于 Access & Identity，覆盖所有 Iris 产品。每项授权是一个资源加一个操作：read、write 或 full。勾选 store 时默认是 read。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/05-api-keys-list.webp' | relative_url }}" width="1440" height="765" alt="Access & Identity 密钥列表，有两个 Agent Memory 密钥，30 天后到期" loading="lazy" decoding="async"></p>

两个密钥：一个 read 密钥和一个 write 密钥。令牌只在创建时显示一次。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

| 步骤 | 结果 |
|---|---|
| 用 read 密钥调用 `health()` | `HEALTHY`：后台任务、长期记忆、会话记忆、来源链接、存储数据库 |
| 用 read 密钥调用 `remember()` | 被拒绝：403 `insufficient-permissions` |
| 用 write 密钥调用 `remember()` | 记忆已存储，主题 `preferences` |
| 两轮对话 | 会话 `cust-1042-<timestamp>` |
| 后台提取 | 约 15 秒内："User has a Redis Cloud database on the Free plan in the Seoul region"；几分钟后从助手的回答中得到第二条记忆 |
| 在韩国调用 `recall()` ×10 | 中位数 611 ms（559–1,312 ms） |
| `iris agent-memory memories search` | 同样的三条记忆，含 ID 和主题 |

**运行位置。** 服务页面显示端点区域为 **us-east-1**，而数据库在首尔；上面的召回时间包含这段距离。**它会写入你的数据库的内容：** 免费数据库中出现了七个键（JSON 文档和哈希）和四个 Search 索引（长期记忆、会话记忆、来源链接、命名空间）。

<p class="shot"><img src="{{ '/assets/img/iris/06-agent-memory-services.webp' | relative_url }}" width="1440" height="765" alt="Agent Memory 服务列表，有一个服务位于 notes-on-redis-free" loading="lazy" decoding="async"></p>

服务列表把每个 store 与其 Redis Cloud 数据库关联起来。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/07-agent-memory-service.webp' | relative_url }}" width="1440" height="1704" alt="服务配置：端点区域 us-east-1、TTL、摘要、记忆类型、敏感数据排除、危险操作区" loading="lazy" decoding="async"></p>

配置：TTL、20 条消息后摘要并保留 10 条、自定义记忆类型、敏感数据排除（内置检测器默认关闭）。删除服务后，长期记忆仍保留在你的数据库中。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/08-agent-memory-inspector.webp' | relative_url }}" width="1440" height="765" alt="Memory Inspector 列出本实验中所有者 cust-1042 的会话" loading="lazy" decoding="async"></p>

Memory Inspector 可按所有者或命名空间浏览会话和长期记忆。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Agent Memory 补充

**已在 redis-iris 1.0.1 上验证，2026-11-07。** 实验： [`iris/02-agent-memory`](https://github.com/litkhai/notes-on-redis/tree/main/iris/02-agent-memory)。

| 实验 | 结果 |
|---|---|
| 一个会话中的 24 条消息 | 保留 14 个事件加一份摘要（20 条后摘要，保留 10 条）；24 条仍可全部读取 |
| 该会话产生的长期记忆 | 一个所有者 25 条，大多是每个助手回答一条 |
| `SHARED` 命名空间中的记忆 | 只有把命名空间作为 `shared` 传入时，才返回给另一个所有者 |
| 假邮箱和电话，检测器关闭 | 原样存为记忆 |
| 同样内容，开启邮箱、电话和银行卡检测器，“Redact match” | 存为 `[REDACTED]`；+82 号码也被识别 |
| MemoryETL：自定义类型 `plan_limit`，一份 9 行文档 | 183 秒内得到 8 条带类型的记忆，按提示要求略去了价格 |
| `forget(owner)` | 一次调用清除会话和记忆（25、3、3） |

在这些运行中，提取耗时 4–5 分钟，而第一个实验约为 15 秒：它在后台按自己的计划运行。

<p class="shot"><img src="{{ '/assets/img/iris/09-agent-memory-detectors.webp' | relative_url }}" width="1440" height="765" alt="敏感数据排除设置：信用卡、邮箱和电话检测器均设为 Redact match" loading="lazy" decoding="async"></p>

内置检测器：信用卡、邮箱、IP、电话（US、CA、UK、DE、IL、IN、BR）和美国 SSN；每个检测器要么遮蔽匹配内容，要么丢弃该记忆。检测器结论不一致时，丢弃优先。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/11-agent-memory-extractor.webp' | relative_url }}" width="1440" height="765" alt="使用 plan_limit 记忆类型的 MemoryETL 新建 extractor 表单" loading="lazy" decoding="async"></p>

MemoryETL（beta）：extractor 复制自定义记忆类型的提示，把上传或通过 API 提交的文档转换成该类型的记忆。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Intent Router

**已在 redis-iris 1.0.1 上验证，2026-11-07。** 四个 intent，每个三条示例，目标共四类；八条英文和韩文查询。嵌入器是托管的 OpenAI `text-embedding-3-small`；没有要求提供我们自己的密钥。实验： [`iris/03-intent-router`](https://github.com/litkhai/notes-on-redis/tree/main/iris/03-intent-router)。

| 查询 | Router 默认值 (0.70) | `min_score` 0.5 |
|---|---|---|
| I was billed twice, can you check? | fallback | billing 0.52 → tool |
| is encryption available on the free tier | fallback | tls_question 0.59 → model |
| connections keep timing out on my prod database | fallback | outage 0.51 → agent |
| tell me something funny | off_topic 0.71 → guardrail | off_topic 0.71 → guardrail |
| 무료 플랜에서 TLS를 켤 수 있나요? | fallback | tls_question 0.61 → model |
| 청구서를 어디서 받나요? | fallback | fallback，即使加入韩文账单示例后也一样 |
| Can you recommend a good restaurant? | fallback | fallback；加入“맛집 추천해 줘”后为 off_topic 0.59 |

每个 intent 只有三条示例时，默认阈值过严；增加示例或降低阈值是调优的第一步。每次匹配在韩国耗时 560–1,090 ms。

**阈值**（`thresholds.py`）。每个 intent 的 `minScore` 会覆盖 Router 的 0.70，每次调用的 `min_score` 又会覆盖两者，与文档给出的顺序一致。把 `tls_question` 设为 0.60 后，韩语的 TLS 问题（0.61）匹配上了；把 `off_topic` 设为 0.85 后，一条讲笑话的请求（0.71）不再匹配；每次调用设为 0.5，则五个查询全部恢复。Router 模板（`CUSTOM`、`MODEL`、`GUARDRAILS`、`AGENT`）只是标签："Every template serves the same way."

<p class="shot"><img src="{{ '/assets/img/iris/24-intent-router-intents.webp' | relative_url }}" width="1440" height="765" alt="Intent Router 意图列表，目标有 tool、model、agent 和 guardrail，下方有 Try a query 输入框" loading="lazy" decoding="async"></p>

各 intent 及其目标和示例数；用 Try a query 可直接在控制台中匹配。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Context Gateway

**已在 redis-iris 1.0.1 上验证，2026-11-07。** 一个搜索模式的 Gateway，带两个上游：基于免费数据库中 30 件虚构商品的 Context Surface，以及公共 DeepWiki MCP 服务器。实验： [`iris/04-context-gateway`](https://github.com/litkhai/notes-on-redis/tree/main/iris/04-context-gateway)。

| 步骤 | 结果 |
|---|---|
| agent 看到的工具 | `search_tools`、`run_tool` |
| 搜索 "black lamps under 100 dollars" | `products__filter_product` |
| 由一个实体、六个字段生成 Surface | 生成十个工具（计数、过滤、文本搜索、集合运算、展开） |
| 过滤：lamp、black、价格 ≤ 100 | 与直接扫描找到的相同的 3 件商品；2.4 秒 |
| 参数形状错误 | 以 `invalid_arguments` 拒绝，未调用工具 |
| `deepwiki__read_wiki_structure` redis/redis | 通过 Gateway 得到页面列表；1.5 秒 |

未使用 `mcp-redis`：上游必须能从 Redis Cloud 访问，而这台主机没有公开提供。Surface 把 Redis 数据作为工具提供。

<p class="shot"><img src="{{ '/assets/img/iris/19-context-surface-fields.webp' | relative_url }}" width="1440" height="1284" alt="Context Surface 字段：id 为主键，name 为文本索引，category 和 colour 为标签索引，price 和 stock 为数值" loading="lazy" decoding="async"></p>

Context Surface 是一个数据模型：实体映射到键模板，字段有类型并建立索引。Gateway 据此生成搜索工具。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/25-context-gateway-upstreams.webp' | relative_url }}" width="1440" height="765" alt="Gateway 的上游：带 10 个工具的 products Context Surface，以及带 3 个工具的 deepwiki MCP 服务器" loading="lazy" decoding="async"></p>

两个上游在同一个端点之后，每个都可单独开关。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Agent Playbooks

**已在 redis-iris 1.0.1 上验证，2026-11-07。** 根据本站的发现撰写了四条 FAQ，以 JSON 编写并用 `iris` CLI 同步。实验： [`iris/05-agent-playbooks`](https://github.com/litkhai/notes-on-redis/tree/main/iris/05-agent-playbooks)。

| 问题 | 命中 |
|---|---|
| is encryption in transit available on the free tier? | free-plan-tls 0.75 |
| how many clients can connect to the free database | free-plan-limits 0.76 |
| MSET fails with a slot error on my cluster | crossslot-error 0.85 |
| 무료 DB에서 TLS 켤 수 있어? | free-plan-tls 0.78 |
| How do I configure Active-Active between Seoul and Tokyo? | 无；改为提交供审阅 |

某条 FAQ 的第二个版本一直是草稿，发现服务持续返回版本 1，直到执行 `faqs publish --version 2`。密钥遵循同样的流程：read、write、propose、publish、full。控制台列出了 Agent Playbooks，没有 LangCache 条目。

**Skill 与提案**（`more.py`）。Skill 是一个压缩文件夹，里面有 `SKILL.md` 和参考文件；这个 skill 用免费计划的实测上限来检查工作负载。发布之后，`discover` 为一个英文的容量规划问题返回了它，agent 按需加载了它的步骤和参考文件。那个未处理的提案经过修改后被接受为一个未发布的 FAQ，直到 `publish_faq` 之后才被 `discover` 找到。

<p class="shot"><img src="{{ '/assets/img/iris/27-playbook-registry.webp' | relative_url }}" width="1440" height="765" alt="Playbook 注册表，四条 FAQ 已发布，其中一条为版本 2" loading="lazy" decoding="async"></p>

注册表显示每条 FAQ 的发布状态和最新版本。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/28-playbook-proposals.webp' | relative_url }}" width="1440" height="765" alt="提案收件箱，有一条关于 Active-Active 的待处理提案" loading="lazy" decoding="async"></p>

提案会留在收件箱中，直到有人接受并发布。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Agent Mesh 和 Lens（beta）

**已在 redis-iris 1.0.1、本地 Docker 中的 Redis 8.10.3 上验证，2026-11-07。** Agent Mesh 把 agent 的进度事件保存在 Redis stream 中，因此断开连接的客户端可以回到任意服务器，收到错过的内容。文档中写道："When the client reconnects, it can receive retained updates after its last event cursor." `XADD IDMP` 需要 Redis 8.6.2 及以上（[Deep Dive]({{ '/deep-dive/' | relative_url }})），并且 "Cloud, Enterprise, failover recovery, and sustained capacity remain unqualified for this beta." 实验对每种集成都运行两个副本，并把客户端从一个副本切换到另一个。

| 实验 | 结果 |
|---|---|
| FastAPI SSE：从副本 A 读取第 1–5 步，离开 3 秒，用 `Last-Event-ID` 重连到副本 B | B 重放第 6–11 步，然后实时发送第 12–20 步；20 步各恰好一次 |
| 在最终游标处重连 / 格式错误的游标 / 未知的运行 | HTTP 204 / 422 `invalid_cursor` / 404 |
| 一次运行在 Redis 中留下什么 | 一个 stream，`XLEN 22`，IDMP 开启，完成后 TTL 120 秒 |
| 运行中途杀掉副本 A，SDK 默认设置 | 没有最终事件：B 每 35 秒关闭并重新打开一次连接 |
| 同样情况，`REDIS_SOCKET_TIMEOUT=30` | 沉默超时后 `stream.end` `producer_lost` |
| A2A：从 A 获取 Task 版本 1–4，用 `Last-Event-ID: 4` 重连到 B | 版本 5–12 和已完成状态；十个 artifact，各一次 |

**发现的唯一陷阱：** redis-py 8.1.0 默认设置 5 秒的套接字超时，比 SDK 的 15 秒阻塞读取更短。SDK 把每次超时都当作 Redis 故障，因此永远不会宣告生产者丢失。请把 `REDIS_SOCKET_TIMEOUT` 设置为大于心跳间隔。

Lens 通过 OpenTelemetry 追踪 agent 的每一轮。在 Redis Cloud 上，它的记录数据库必须是 "A Redis Cloud Essentials or Pro database"，所以在免费计划上 **New Lens** 是禁用的。改为指向回环接收器后，SDK 每轮发送一个 OTLP/HTTP 请求。该轮的 span 包括无需额外代码就被记录的 Agent Memory 搜索，以及应用自己的检索和一个自定义步骤。设置 `IRIS_LENS_CAPTURE_CONTENT=false` 后，查询和文档文本被丢弃，只剩 ID、分数和哈希。文档： [Agent Mesh](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/)、[FastAPI SSE SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/fastapi-sse-sdk/)、[A2A SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/a2a-sdk/)、[Lens](https://redis.io/docs/latest/develop/ai/context-engine/lens/)、[Create Lens](https://redis.io/docs/latest/operate/iris/lens/create-lens/)。实验： [`iris/06-lens-and-mesh`](https://github.com/litkhai/notes-on-redis/tree/main/iris/06-lens-and-mesh)。

**移交任务**（`mesh_takeover.py`）。使用 `takeover=True` 时，一个任务在六个步骤中完成三个后进程被杀；只要已死进程的心跳租约还在，另一个副本接手就被拒绝（拒绝仍然返回 HTTP 200，只有 Task 历史里能看到），随后在 15.1 秒时被接手；新进程跳过了已完成的步骤并完成了其余部分。使用默认的 `takeover=False` 时，读取方在 12.1 秒后把同一个任务标记为失败，原因为 `producer_lost`，并且无法恢复。

<p class="shot"><img src="{{ '/assets/img/iris/29-lens-free-plan.webp' | relative_url }}" width="1440" height="1351" alt="Redis Cloud 控制台中的 Lens 页面，免费计划账户上的 New Lens 按钮为灰色" loading="lazy" decoding="async"></p>

在免费计划上，New Lens 是禁用的。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/iris/30-agent-mesh.webp' | relative_url }}" width="1440" height="1121" alt="控制台中的 Agent Mesh 页面：一个在 Redis 上实现可恢复 SSE 和 A2A 流的库，没有创建按钮" loading="lazy" decoding="async"></p>

Agent Mesh 有页面，但没有可创建的东西：它在你自己的应用内运行。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Iris 对免费数据库的占用

这些服务把数据和连接池放在你所选的数据库中。2026-11-07，Agent Memory、Intent Router、Context Surface 和 Playbook 全部放在免费数据库上，我们这边没有运行任何东西：

| 资源 | 使用量 | 查看方式 |
|---|---|---|
| 连接数 | 30 个中的 28 个 | `CLIENT LIST`：28 个来自 AWS us-east-1 地址的 `go-redis` 客户端，外加我们自己的一个检查连接 |
| 数据 | 30 MB 中的 16.7 MB，111 个键 | 控制台 Configuration 卡片；键 `iris:intent:*` 25 个、`memory:*` 44 个、`iris:playbook:*` 12 个，另有 30 个实验用商品 |
| 告警 | 来自 Redis 的电子邮件 | "The number of connections for your database has reached 93.33% of the connections limit" |

在免费计划上，这只给应用程序留下两个连接。在让真实流量与它并存之前，请为 Iris 单独准备一个数据库，或选择连接数更多的计划。

### 尚未涉及的内容

Redis Cloud 上的 Lens 在等待 [#8](https://github.com/litkhai/notes-on-redis/issues/8) 中的 Essentials 预算：创建它、Lens UI、回读各轮以及模型调用追踪。在控制台或账单显示出来之前，消息消耗量仍是一个未解的问题。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**ステータス：Redis Cloud 上の Lens を除いて実行済み。** Agent Memory、Intent Router、Context Gateway、Agent Playbooks は 2026-11-07 に Redis Cloud の無料プランで、Agent Mesh はローカルの Redis 8.10.3 で実行した（下記）。Lens は Essentials か Pro のデータベースが必要なため、SDK だけを実行した。
</div>

Redis Iris は、Redis 自身の言葉では "a production-ready context engine for AI agents" — サービスの集まりでありデータベースではなく、その下にあるデータベースが Redis である。2026-05-18 にリリースされ、2026-11-04 に六つのサービスになった：Intent Router、Agent Playbooks、Agent Memory、Context Gateway（GA）、Lens、Agent Mesh（ベータ）。Redis Cloud ではマネージド、セルフマネージドはライセンスが必要な Helm チャート。サービスごとに実習を一つ、すべて無料データベースと無料の 5,000 メッセージで行い、実習ごとに消費したメッセージ数を記録した。名前の落とし穴 — Context Retriever → Context Gateway、LangCache と Agent Playbooks — は別の節で扱う。2026-11-07 に [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/) で読んだ。

### Iris は無料プランで使えるか？

**使える（2026-11-07 時点）。** 無料アカウントでも Iris の四つのサービスに作成ボタンがある（Agent Memory、Agent Playbooks、Context Gateway、Intent Router）。**New Lens** はグレーで無効になっている。Lens は記録用データベースが Essentials か Pro である必要があるからだ。Agent Mesh は自分のアプリの中で動くライブラリである。無料の 30 MB データベースに Agent Memory サービスを一つ作り、API キーを二つ発行して、`redis-iris` 1.0.1 SDK と `iris` CLI で使った。ヘルスチェック、記憶の書き込み、会話、バックグラウンド抽出、想起がすべて動いた。「無料メッセージ 5,000 件」はコンソールのどこにも（Iris 画面、Usage、Billing）表示されないため、この実習で何件使ったかは分からない。

### 実習：無料データベース上の Agent Memory

**確認：redis-iris 1.0.1（Python 3.12）、Redis Cloud 無料プラン（Redis 8.6.2、AWS ap-northeast-2）、2026-11-07。** ソースと出力：[`iris/01-getting-started`](https://github.com/litkhai/notes-on-redis/tree/main/iris/01-getting-started)。

<p class="shot"><img src="{{ '/assets/img/iris/01-agent-memory-landing.webp' | relative_url }}" width="1440" height="1054" alt="Agent Memory のランディングページ。Create Agent Memory service ボタンがある" loading="lazy" decoding="async"></p>

無料アカウントでの Agent Memory のランディングページ。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/02-agent-memory-create-form.webp' | relative_url }}" width="1440" height="765" alt="Create Agent Memory service ダイアログ：名前、データベース notes-on-redis-free、デフォルト設定" loading="lazy" decoding="async"></p>

サービスの作成には名前とデータベースが必要で、無料データベースは最初から選択されている。デフォルト：短期記憶 1 日、長期記憶 365 日、セッション要約オン。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/03-agent-memory-connect.webp' | relative_url }}" width="1440" height="765" alt="Connect ダイアログ。エンドポイント、store ID、agents・SDK・CLI 用のクイック接続タブ" loading="lazy" decoding="async"></p>

サービスはすぐに使える状態になる。Connect はエンドポイントと store ID、そしてコーディングエージェントに貼り付けて add-agent-memory スキルをインストールさせるプロンプトを示す。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/04-api-key-form.webp' | relative_url }}" width="1440" height="765" alt="Create API key ページ：名前、30 日の有効期限、Agent Memory store、read・write・full" loading="lazy" decoding="async"></p>

キーは Access & Identity にあり、すべての Iris 製品にまたがる。各権限はリソース一つとアクション一つで、read、write、full のいずれか。チェックした store のデフォルトは read。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/05-api-keys-list.webp' | relative_url }}" width="1440" height="765" alt="Access & Identity のキー一覧。Agent Memory 用のキーが二つ、30 日後に期限切れ" loading="lazy" decoding="async"></p>

キーは二つ：read キーと write キー。トークンは作成時に一度だけ表示される。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

| 手順 | 結果 |
|---|---|
| read キーで `health()` | `HEALTHY`：バックグラウンドジョブ、長期記憶、セッション記憶、ソースリンク、保存先データベース |
| read キーで `remember()` | 拒否：403 `insufficient-permissions` |
| write キーで `remember()` | 記憶を保存、トピック `preferences` |
| 二ターンの会話 | セッション `cust-1042-<timestamp>` |
| バックグラウンド抽出 | 約 15 秒以内に「User has a Redis Cloud database on the Free plan in the Seoul region」。数分後にアシスタントの回答から二つ目の記憶 |
| 韓国から `recall()` ×10 | 中央値 611 ms（559–1,312 ms） |
| `iris agent-memory memories search` | 同じ三つの記憶、ID とトピック付き |

**どこで動くか。** サービス画面のエンドポイントのリージョンは **us-east-1** で、データベースはソウルにある。上の想起時間にはその距離が含まれる。**自分のデータベースに書き込まれるもの：** 無料データベースにキー七つ（JSON ドキュメントとハッシュ）と Search インデックス四つ（長期記憶、セッション記憶、ソースリンク、ネームスペース）ができた。

<p class="shot"><img src="{{ '/assets/img/iris/06-agent-memory-services.webp' | relative_url }}" width="1440" height="765" alt="Agent Memory サービス一覧。notes-on-redis-free 上のサービスが一つ" loading="lazy" decoding="async"></p>

サービス一覧は、各 store を Redis Cloud のデータベースに結び付けている。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/07-agent-memory-service.webp' | relative_url }}" width="1440" height="1704" alt="サービス設定：エンドポイントのリージョン us-east-1、TTL、要約、メモリタイプ、機密データの除外、危険な操作の領域" loading="lazy" decoding="async"></p>

設定：TTL、20 メッセージ後に要約して 10 件を保持、カスタムメモリタイプ、機密データの除外（組み込み検出器はデフォルトでオフ）。サービスを削除しても長期記憶は自分のデータベースに残る。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/08-agent-memory-inspector.webp' | relative_url }}" width="1440" height="765" alt="Memory Inspector がこの実習の所有者 cust-1042 のセッションを一覧表示している" loading="lazy" decoding="async"></p>

Memory Inspector は、所有者またはネームスペースごとにセッションと長期記憶を閲覧できる。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

### Agent Memory の補足

**確認：redis-iris 1.0.1、2026-11-07。** 実習： [`iris/02-agent-memory`](https://github.com/litkhai/notes-on-redis/tree/main/iris/02-agent-memory)。

| 実験 | 結果 |
|---|---|
| 一つのセッションでの 24 メッセージ | 14 件のイベントと要約を保持（20 件で要約、10 件を保持）。24 件とも引き続き読める |
| そのセッションから得た長期記憶 | 一人の所有者に 25 件、ほぼアシスタントの回答ごとに一件 |
| `SHARED` ネームスペースの記憶 | ネームスペースを `shared` として渡したときだけ別の所有者に返る |
| 偽のメールと電話、検出器オフ | そのまま記憶として保存 |
| 同じ内容でメール・電話・カードの検出器をオン、「Redact match」 | `[REDACTED]` として保存。+82 の番号も検出された |
| MemoryETL：カスタムタイプ `plan_limit`、9 行のドキュメント | 183 秒で型付き記憶 8 件、プロンプトの指示どおり価格は除外 |
| `forget(owner)` | 一回の呼び出しでセッションと記憶が消えた（25、3、3） |

これらの実行では抽出に 4〜5 分かかった。最初の実習では約 15 秒だった。抽出はバックグラウンドで独自のスケジュールで動く。

<p class="shot"><img src="{{ '/assets/img/iris/09-agent-memory-detectors.webp' | relative_url }}" width="1440" height="765" alt="信用卡、メール、電話の検出器を Redact match にした機密データ除外の設定" loading="lazy" decoding="async"></p>

内蔵の検出器：クレジットカード、メール、IP、電話（US、CA、UK、DE、IL、IN、BR）、米国 SSN。それぞれ一致部分を伏せるか、記憶を破棄する。検出器の判断が分かれたときは破棄が優先される。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/11-agent-memory-extractor.webp' | relative_url }}" width="1440" height="765" alt="plan_limit 記憶タイプを使う MemoryETL の新規 extractor フォーム" loading="lazy" decoding="async"></p>

MemoryETL（beta）：extractor はカスタム記憶タイプのプロンプトをコピーし、アップロードまたは API で送られたドキュメントをそのタイプの記憶に変える。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

### Intent Router

**確認：redis-iris 1.0.1、2026-11-07。** 四つの intent、それぞれ例三つ、ターゲットは四種類。英語と韓国語のクエリ八件。埋め込みはマネージドの OpenAI `text-embedding-3-small` で、自前のキーは求められなかった。実習： [`iris/03-intent-router`](https://github.com/litkhai/notes-on-redis/tree/main/iris/03-intent-router)。

| クエリ | Router の既定値 (0.70) | `min_score` 0.5 |
|---|---|---|
| I was billed twice, can you check? | fallback | billing 0.52 → tool |
| is encryption available on the free tier | fallback | tls_question 0.59 → model |
| connections keep timing out on my prod database | fallback | outage 0.51 → agent |
| tell me something funny | off_topic 0.71 → guardrail | off_topic 0.71 → guardrail |
| 무료 플랜에서 TLS를 켤 수 있나요? | fallback | tls_question 0.61 → model |
| 청구서를 어디서 받나요? | fallback | fallback、韓国語の請求の例を足した後も同じ |
| Can you recommend a good restaurant? | fallback | fallback。「맛집 추천해 줘」を足した後は off_topic 0.59 |

intent ごとの例が三つだと既定のしきい値は厳しすぎる。例を増やすかしきい値を下げるのが最初の調整である。一回のマッチは韓国から 560〜1,090 ms かかった。

**しきい値**（`thresholds.py`）。インテントごとの `minScore` は Router の 0.70 を上書きし、呼び出しごとの `min_score` はその両方を上書きする。ドキュメントの順序どおりである。`tls_question` を 0.60 にすると韓国語の TLS の質問（0.61）がマッチし、`off_topic` を 0.85 にすると冗談を頼む依頼（0.71）はもうマッチしなくなった。呼び出しごとに 0.5 を指定すると、五つのクエリがすべて戻った。Router のテンプレート（`CUSTOM`、`MODEL`、`GUARDRAILS`、`AGENT`）はラベルである："Every template serves the same way."

<p class="shot"><img src="{{ '/assets/img/iris/24-intent-router-intents.webp' | relative_url }}" width="1440" height="765" alt="ターゲットが tool、model、agent、guardrail の Intent Router の intent 一覧と Try a query 欄" loading="lazy" decoding="async"></p>

intent とそのターゲット、例の数。Try a query でコンソールから直接マッチを試せる。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

### Context Gateway

**確認：redis-iris 1.0.1、2026-11-07。** 検索モードの Gateway 一つに上流が二つ。無料データベース上の架空の商品 30 件に対する Context Surface と、公開の DeepWiki MCP サーバー。実習： [`iris/04-context-gateway`](https://github.com/litkhai/notes-on-redis/tree/main/iris/04-context-gateway)。

| 手順 | 結果 |
|---|---|
| agent に見えるツール | `search_tools`、`run_tool` |
| 検索 "black lamps under 100 dollars" | `products__filter_product` |
| 一つのエンティティ、六つのフィールドから作った Surface | 生成されたツール十個（カウント、フィルタ、テキスト検索、集合演算、展開） |
| フィルタ：lamp、black、価格 ≤ 100 | 直接スキャンで見つかったのと同じ 3 商品、2.4 秒 |
| 引数の形が誤り | `invalid_arguments` で拒否、ツールは呼ばれず |
| `deepwiki__read_wiki_structure` redis/redis | Gateway 経由でページ一覧を取得、1.5 秒 |

`mcp-redis` は使わなかった。上流は Redis Cloud から到達できる必要があるが、このホストは公開していない。Surface が Redis のデータをツールとして扱う。

<p class="shot"><img src="{{ '/assets/img/iris/19-context-surface-fields.webp' | relative_url }}" width="1440" height="1284" alt="Context Surface のフィールド：主キーの id、テキストインデックスの name、タグインデックスの category と colour、数値の price と stock" loading="lazy" decoding="async"></p>

Context Surface はデータモデルである。エンティティをキーのテンプレートに対応させ、フィールドに型とインデックスを付ける。Gateway はここから検索ツールを作る。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/25-context-gateway-upstreams.webp' | relative_url }}" width="1440" height="765" alt="Gateway の上流：ツール 10 個の products Context Surface と、ツール 3 個の deepwiki MCP サーバー" loading="lazy" decoding="async"></p>

二つの上流が一つのエンドポイントの後ろにあり、それぞれオン・オフを切り替えられる。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

### Agent Playbooks

**確認：redis-iris 1.0.1、2026-11-07。** このサイトの知見から FAQ を四件書き、JSON で作成して `iris` CLI で同期した。実習： [`iris/05-agent-playbooks`](https://github.com/litkhai/notes-on-redis/tree/main/iris/05-agent-playbooks)。

| 質問 | 見つかったもの |
|---|---|
| is encryption in transit available on the free tier? | free-plan-tls 0.75 |
| how many clients can connect to the free database | free-plan-limits 0.76 |
| MSET fails with a slot error on my cluster | crossslot-error 0.85 |
| 무료 DB에서 TLS 켤 수 있어? | free-plan-tls 0.78 |
| How do I configure Active-Active between Seoul and Tokyo? | なし。代わりにレビュー用に提案された |

FAQ の二つ目のバージョンは下書きのままで、`faqs publish --version 2` を実行するまで discovery はバージョン 1 を返し続けた。キーも同じ流れで、read、write、propose、publish、full の順になる。コンソールには Agent Playbooks が並び、LangCache の項目はない。

**Skill と提案**（`more.py`）。Skill は `SKILL.md` と参照ファイルを入れた zip 圧縮のフォルダである。この skill は、無料プランの実測した上限に照らしてワークロードを判定する。公開後、`discover` は英語の容量見積もりの質問にこれを返し、エージェントは手順と参照ファイルを必要なときに読み込んだ。未処理の提案は編集してから未公開の FAQ として承認され、`publish_faq` の後でようやく `discover` で見つかった。

<p class="shot"><img src="{{ '/assets/img/iris/27-playbook-registry.webp' | relative_url }}" width="1440" height="765" alt="公開済みの FAQ 四件を並べた Playbook レジストリ。うち一件はバージョン 2" loading="lazy" decoding="async"></p>

レジストリは FAQ ごとに公開状態と最新バージョンを示す。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/28-playbook-proposals.webp' | relative_url }}" width="1440" height="765" alt="Active-Active に関する未処理の提案が一件ある提案トレイ" loading="lazy" decoding="async"></p>

提案は、誰かが受け入れて公開するまでトレイで待つ。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

### Agent Mesh と Lens（ベータ）

**確認：redis-iris 1.0.1、ローカル Docker の Redis 8.10.3、2026-11-07。** Agent Mesh はエージェントの進捗イベントを Redis ストリームに保持するので、切断されたクライアントはどのサーバーに戻っても、取りこぼした分を受け取れる。ドキュメントにはこうある："When the client reconnects, it can receive retained updates after its last event cursor." `XADD IDMP` のために Redis 8.6.2 以上が必要で（[Deep Dive]({{ '/deep-dive/' | relative_url }})）、"Cloud, Enterprise, failover recovery, and sustained capacity remain unqualified for this beta." 実習では統合ごとにレプリカを二つ動かし、クライアントを一方から他方へ移した。

| 実験 | 結果 |
|---|---|
| FastAPI SSE：レプリカ A でステップ 1–5 を読み、3 秒離れ、`Last-Event-ID` でレプリカ B に再接続 | B が 6–11 を再生し、12–20 をライブで送信。20 ステップすべてがちょうど一回ずつ |
| 最終カーソル / 不正なカーソル / 未知の実行で再接続 | HTTP 204 / 422 `invalid_cursor` / 404 |
| 一回の実行が Redis に残すもの | ストリーム一つ、`XLEN 22`、IDMP 有効、完了後 TTL 120 秒 |
| 実行中にレプリカ A を停止、SDK 既定値 | 最終イベントなし：B が 35 秒ごとに接続を閉じて開き直した |
| 同じ状況で `REDIS_SOCKET_TIMEOUT=30` | 無通信タイムアウト後に `stream.end` `producer_lost` |
| A2A：A から Task バージョン 1–4、`Last-Event-ID: 4` で B に再接続 | バージョン 5–12 と完了ステータス。アーティファクト十個が各一回 |

**見つかった罠は一つ：** redis-py 8.1.0 はソケットのタイムアウトを既定で 5 秒にしており、SDK の 15 秒のブロッキング読み取りより短い。SDK はタイムアウトのたびに Redis の障害とみなすので、プロデューサー喪失を宣言しない。`REDIS_SOCKET_TIMEOUT` はハートビート間隔より長く設定する。

Lens は OpenTelemetry でエージェントのターンをトレースする。Redis Cloud では記録用データベースが "A Redis Cloud Essentials or Pro database" でなければならないため、無料プランでは **New Lens** は無効になる。代わりにループバックの受信側を指定すると、SDK はターンごとに OTLP/HTTP リクエストを一つ送った。ターンのスパンには、追加コードなしで記録された Agent Memory の検索、アプリ自身の検索、カスタムステップが含まれていた。`IRIS_LENS_CAPTURE_CONTENT=false` にするとクエリと文書のテキストが落とされ、ID、スコア、ハッシュだけが残った。ドキュメント： [Agent Mesh](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/)、[FastAPI SSE SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/fastapi-sse-sdk/)、[A2A SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/a2a-sdk/)、[Lens](https://redis.io/docs/latest/develop/ai/context-engine/lens/)、[Create Lens](https://redis.io/docs/latest/operate/iris/lens/create-lens/)。実習： [`iris/06-lens-and-mesh`](https://github.com/litkhai/notes-on-redis/tree/main/iris/06-lens-and-mesh)。

**タスクの引き継ぎ**（`mesh_takeover.py`）。`takeover=True` では、六つのステップのうち三つを終えたところでプロセスが kill されたタスクは、死んだプロセスのハートビートのリースが残っている間、別のレプリカからの引き継ぎを拒否され（拒否でも HTTP 200 が返り、Task の履歴にだけ表れる）、15.1 秒で引き継がれた。新しいプロセスは終わったステップを飛ばして残りを完了した。デフォルトの `takeover=False` では、リーダーが 12.1 秒後に同じタスクを `producer_lost` で失敗にし、再開はできなかった。

<p class="shot"><img src="{{ '/assets/img/iris/29-lens-free-plan.webp' | relative_url }}" width="1440" height="1351" alt="Redis Cloud コンソールの Lens ページ。無料プランのアカウントなので New Lens ボタンがグレーで無効" loading="lazy" decoding="async"></p>

無料プランでは New Lens は無効になっている。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/iris/30-agent-mesh.webp' | relative_url }}" width="1440" height="1121" alt="コンソールの Agent Mesh ページ：Redis 上で再開可能な SSE と A2A のストリームを扱うライブラリ、作成ボタンなし" loading="lazy" decoding="async"></p>

Agent Mesh にはページがあるが、作るものはない。自分のアプリの中で動く。 <small>2026-11-07 にキャプチャ、Redis Cloud 無料プラン。</small>

### Iris が無料データベースに与える負荷

サービスは、選んだデータベースにデータとコネクションプールを置きます。Agent Memory、Intent Router、Context Surface、Playbook をすべて無料データベースに置き、こちらでは何も動かしていない 2026-11-07 の状態です。

| リソース | 使用量 | 確認方法 |
|---|---|---|
| 接続数 | 30 件中 28 件 | `CLIENT LIST`：AWS us-east-1 のアドレスからの `go-redis` クライアント 28 件と、こちらの確認用の 1 件 |
| データ | 30 MB 中 16.7 MB、キー 111 個 | コンソールの Configuration カード。キーは `iris:intent:*` 25、`memory:*` 44、`iris:playbook:*` 12、ほかに実習用の商品 30 |
| アラート | Redis からのメール | "The number of connections for your database has reached 93.33% of the connections limit" |

無料プランでは、アプリケーションに残る接続は 2 件です。実際のトラフィックをそばに置く前に、Iris 専用のデータベースか、接続数の多いプランを用意してください。

### まだ扱っていないこと

Redis Cloud の Lens は [#8](https://github.com/litkhai/notes-on-redis/issues/8) の Essentials の予算を待っている：作成、Lens UI、ターンの読み戻し、モデル呼び出しのトレース。メッセージの消費量は、コンソールか請求書に表示されるまで未解決の問いのままである。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: รันแล้ว ยกเว้น Lens บน Redis Cloud** Agent Memory, Intent Router, Context Gateway และ Agent Playbooks รันบนแผนฟรีของ Redis Cloud เมื่อ 2026-11-07 ส่วน Agent Mesh รันบน Redis 8.10.3 ในเครื่อง (ด้านล่าง) Lens ต้องใช้ฐานข้อมูล Essentials หรือ Pro จึงรันได้เฉพาะ SDK
</div>

Redis Iris คือ "a production-ready context engine for AI agents" ตามคำของ Redis เอง — เป็นชุดของบริการ ไม่ใช่ฐานข้อมูล โดยฐานข้อมูลที่อยู่ข้างใต้คือ Redis เปิดตัว 2026-05-18 และเมื่อ 2026-11-04 กลายเป็นหกบริการ: Intent Router, Agent Playbooks, Agent Memory และ Context Gateway (GA) กับ Lens และ Agent Mesh (เบต้า) จัดการบน Redis Cloud หรือติดตั้งเองผ่าน Helm chart ที่ต้องมีไลเซนส์ หนึ่งแล็บต่อหนึ่งบริการ ทั้งหมดใช้ฐานข้อมูลฟรีและ 5,000 ข้อความฟรี พร้อมบันทึกจำนวนข้อความที่แต่ละแล็บใช้ กับดักเรื่องชื่อ — Context Retriever → Context Gateway, LangCache เทียบกับ Agent Playbooks — มีหัวข้อของตัวเอง อ่านเมื่อ 2026-11-07 ที่ [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)

### ใช้ Iris บนแผนฟรีได้ไหม

**ได้ ณ วันที่ 2026-11-07** บนบัญชีฟรี บริการ Iris สี่ตัวมีปุ่มสร้าง (Agent Memory, Agent Playbooks, Context Gateway, Intent Router) ส่วน **New Lens** เป็นสีเทากดไม่ได้ เพราะ Lens ต้องใช้ฐานข้อมูลบันทึกแบบ Essentials หรือ Pro Agent Mesh เป็นไลบรารีที่รันในแอปของคุณเอง มีการสร้างบริการ Agent Memory หนึ่งบริการบนฐานข้อมูลฟรีขนาด 30 MB ออก API key สองชุด และใช้ผ่าน SDK `redis-iris` 1.0.1 กับ CLI `iris` ได้แก่ การตรวจสถานะ การเขียนหน่วยความจำ การสนทนา การสกัดเบื้องหลัง และการเรียกคืน ซึ่งทำงานได้ทั้งหมด "5,000 ข้อความฟรี" ไม่ปรากฏที่ใดในคอนโซล (หน้า Iris, Usage, Billing) จึงไม่ทราบว่าแล็บนี้ใช้ไปกี่ข้อความ

### แล็บ: Agent Memory บนฐานข้อมูลฟรี

**ตรวจสอบบน redis-iris 1.0.1 (Python 3.12), Redis Cloud แผนฟรี (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07** ซอร์สและผลลัพธ์: [`iris/01-getting-started`](https://github.com/litkhai/notes-on-redis/tree/main/iris/01-getting-started)

<p class="shot"><img src="{{ '/assets/img/iris/01-agent-memory-landing.webp' | relative_url }}" width="1440" height="1054" alt="หน้าแรกของ Agent Memory พร้อมปุ่ม Create Agent Memory service" loading="lazy" decoding="async"></p>

หน้าแรกของ Agent Memory บนบัญชีฟรี <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/02-agent-memory-create-form.webp' | relative_url }}" width="1440" height="765" alt="กล่องโต้ตอบ Create Agent Memory service: ชื่อ, ฐานข้อมูล notes-on-redis-free, ค่าเริ่มต้น" loading="lazy" decoding="async"></p>

การสร้างบริการต้องระบุชื่อและฐานข้อมูล โดยฐานข้อมูลฟรีถูกเลือกไว้ล่วงหน้า ค่าเริ่มต้น: หน่วยความจำระยะสั้น 1 วัน ระยะยาว 365 วัน เปิดการสรุปเซสชัน <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/03-agent-memory-connect.webp' | relative_url }}" width="1440" height="765" alt="กล่องโต้ตอบ Connect พร้อม endpoint, store ID และแท็บเชื่อมต่อด่วนสำหรับ agents, SDK และ CLI" loading="lazy" decoding="async"></p>

บริการพร้อมใช้งานทันที Connect ให้ endpoint และ store ID พร้อมพรอมต์สำหรับวางในโค้ดดิ้งเอเจนต์เพื่อติดตั้งสกิล add-agent-memory <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/04-api-key-form.webp' | relative_url }}" width="1440" height="765" alt="หน้า Create API key: ชื่อ, หมดอายุใน 30 วัน, Agent Memory store พร้อมสิทธิ์ read, write, full" loading="lazy" decoding="async"></p>

key อยู่ใน Access & Identity ครอบคลุมทุกผลิตภัณฑ์ Iris แต่ละสิทธิ์คือหนึ่งทรัพยากรกับหนึ่งการกระทำ: read, write หรือ full ค่าเริ่มต้นของ store ที่เลือกคือ read <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/05-api-keys-list.webp' | relative_url }}" width="1440" height="765" alt="รายการ key ใน Access & Identity มีสองตัวสำหรับ Agent Memory หมดอายุใน 30 วัน" loading="lazy" decoding="async"></p>

สอง key: key แบบ read และ key แบบ write โทเค็นแสดงเพียงครั้งเดียวตอนสร้าง <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

| ขั้นตอน | ผลลัพธ์ |
|---|---|
| `health()` ด้วย key แบบ read | `HEALTHY`: งานเบื้องหลัง, หน่วยความจำระยะยาว, หน่วยความจำเซสชัน, ลิงก์แหล่งที่มา, ฐานข้อมูลที่จัดเก็บ |
| `remember()` ด้วย key แบบ read | ถูกปฏิเสธ: 403 `insufficient-permissions` |
| `remember()` ด้วย key แบบ write | จัดเก็บหน่วยความจำแล้ว หัวข้อ `preferences` |
| การสนทนาสองรอบ | เซสชัน `cust-1042-<timestamp>` |
| การสกัดเบื้องหลัง | ภายในประมาณ 15 วินาที: "User has a Redis Cloud database on the Free plan in the Seoul region" และอีกไม่กี่นาทีต่อมามีหน่วยความจำที่สองจากคำตอบของผู้ช่วย |
| `recall()` ×10 จากเกาหลี | ค่ามัธยฐาน 611 ms (559–1,312 ms) |
| `iris agent-memory memories search` | หน่วยความจำสามรายการเดิม พร้อม id และหัวข้อ |

**รันที่ไหน** หน้าบริการแสดงภูมิภาคของ endpoint เป็น **us-east-1** ขณะที่ฐานข้อมูลอยู่ที่โซล เวลาเรียกคืนข้างต้นรวมระยะทางนี้ไว้แล้ว **สิ่งที่เขียนลงในฐานข้อมูลของคุณ:** ในฐานข้อมูลฟรีปรากฏคีย์เจ็ดรายการ (เอกสาร JSON และแฮช) และดัชนี Search สี่รายการ (หน่วยความจำระยะยาว, หน่วยความจำเซสชัน, ลิงก์แหล่งที่มา, เนมสเปซ)

<p class="shot"><img src="{{ '/assets/img/iris/06-agent-memory-services.webp' | relative_url }}" width="1440" height="765" alt="รายการบริการ Agent Memory มีหนึ่งบริการบน notes-on-redis-free" loading="lazy" decoding="async"></p>

รายการบริการผูกแต่ละ store เข้ากับฐานข้อมูล Redis Cloud ของมัน <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/07-agent-memory-service.webp' | relative_url }}" width="1440" height="1704" alt="การตั้งค่าบริการ: ภูมิภาคของ endpoint us-east-1, TTL, การสรุป, ประเภทหน่วยความจำ, การยกเว้นข้อมูลอ่อนไหว, โซนอันตราย" loading="lazy" decoding="async"></p>

การตั้งค่า: TTL, สรุปหลังจาก 20 ข้อความโดยเก็บไว้ 10, ประเภทหน่วยความจำแบบกำหนดเอง, การยกเว้นข้อมูลอ่อนไหว (ตัวตรวจจับในตัวปิดไว้เป็นค่าเริ่มต้น) การลบบริการจะไม่ลบหน่วยความจำระยะยาวในฐานข้อมูลของคุณ <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/08-agent-memory-inspector.webp' | relative_url }}" width="1440" height="765" alt="Memory Inspector แสดงรายการเซสชันของแล็บนี้สำหรับเจ้าของ cust-1042" loading="lazy" decoding="async"></p>

Memory Inspector เรียกดูเซสชันและหน่วยความจำระยะยาวตามเจ้าของหรือเนมสเปซ <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### Agent Memory เพิ่มเติม

**ตรวจสอบบน redis-iris 1.0.1, 2026-11-07** แล็บ: [`iris/02-agent-memory`](https://github.com/litkhai/notes-on-redis/tree/main/iris/02-agent-memory)

| การทดลอง | ผลลัพธ์ |
|---|---|
| 24 ข้อความในเซสชันเดียว | เก็บ 14 เหตุการณ์พร้อมสรุปหนึ่งรายการ (สรุปหลัง 20 เก็บ 10) และยังอ่านได้ครบทั้ง 24 |
| หน่วยความจำระยะยาวจากเซสชันนั้น | 25 รายการสำหรับเจ้าของหนึ่งราย ส่วนใหญ่หนึ่งรายการต่อหนึ่งคำตอบของผู้ช่วย |
| หน่วยความจำใน namespace แบบ `SHARED` | ส่งกลับให้เจ้าของรายอื่นเฉพาะเมื่อส่ง namespace เป็น `shared` |
| อีเมลและเบอร์โทรปลอม ปิดตัวตรวจจับ | จัดเก็บเป็นหน่วยความจำตามต้นฉบับ |
| เหมือนกัน แต่เปิดตัวตรวจจับอีเมล เบอร์โทร และบัตร "Redact match" | จัดเก็บเป็น `[REDACTED]` เบอร์ +82 ก็ถูกจับได้เช่นกัน |
| MemoryETL: ประเภทกำหนดเอง `plan_limit`, เอกสาร 9 บรรทัด | 8 หน่วยความจำที่มีประเภทใน 183 วินาที ไม่รวมราคาตามที่ prompt สั่ง |
| `forget(owner)` | เซสชันและหน่วยความจำหายไปในการเรียกครั้งเดียว (25, 3, 3) |

ในการรันเหล่านี้การสกัดใช้เวลา 4–5 นาที เทียบกับประมาณ 15 วินาทีในแล็บแรก เพราะทำงานเบื้องหลังตามกำหนดเวลาของตัวเอง

<p class="shot"><img src="{{ '/assets/img/iris/09-agent-memory-detectors.webp' | relative_url }}" width="1440" height="765" alt="การยกเว้นข้อมูลอ่อนไหวที่ตั้งตัวตรวจจับบัตรเครดิต อีเมล และเบอร์โทรเป็น Redact match" loading="lazy" decoding="async"></p>

ตัวตรวจจับในตัว: บัตรเครดิต, อีเมล, IP, เบอร์โทร (US, CA, UK, DE, IL, IN, BR) และ SSN ของสหรัฐฯ แต่ละตัวจะปกปิดส่วนที่ตรงหรือทิ้งหน่วยความจำนั้น เมื่อตัวตรวจจับขัดแย้งกัน การทิ้งจะมีผลเหนือกว่า <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/11-agent-memory-extractor.webp' | relative_url }}" width="1440" height="765" alt="ฟอร์ม extractor ใหม่ของ MemoryETL ที่ใช้หน่วยความจำประเภท plan_limit" loading="lazy" decoding="async"></p>

MemoryETL (beta): extractor คัดลอก prompt ของประเภทหน่วยความจำที่กำหนดเอง แล้วแปลงเอกสารที่อัปโหลดหรือส่งผ่าน API เป็นหน่วยความจำประเภทนั้น <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### Intent Router

**ตรวจสอบบน redis-iris 1.0.1, 2026-11-07** intent สี่รายการ รายการละสามตัวอย่าง เป้าหมายสี่ชนิด และคิวรีภาษาอังกฤษกับเกาหลีแปดรายการ ตัวฝังข้อความคือ OpenAI `text-embedding-3-small` แบบมีผู้ให้บริการจัดการให้ ไม่มีการขอ key ของเราเอง แล็บ: [`iris/03-intent-router`](https://github.com/litkhai/notes-on-redis/tree/main/iris/03-intent-router)

| คิวรี | ค่าเริ่มต้นของ Router (0.70) | `min_score` 0.5 |
|---|---|---|
| I was billed twice, can you check? | fallback | billing 0.52 → tool |
| is encryption available on the free tier | fallback | tls_question 0.59 → model |
| connections keep timing out on my prod database | fallback | outage 0.51 → agent |
| tell me something funny | off_topic 0.71 → guardrail | off_topic 0.71 → guardrail |
| 무료 플랜에서 TLS를 켤 수 있나요? | fallback | tls_question 0.61 → model |
| 청구서를 어디서 받나요? | fallback | fallback แม้หลังเพิ่มตัวอย่างเรื่องบิลภาษาเกาหลี |
| Can you recommend a good restaurant? | fallback | fallback; หลังเพิ่ม "맛집 추천해 줘" ได้ off_topic 0.59 |

เมื่อมีสามตัวอย่างต่อ intent เกณฑ์เริ่มต้นเข้มงวดเกินไป การเพิ่มตัวอย่างหรือลดเกณฑ์คือขั้นแรกของการปรับจูน การจับคู่แต่ละครั้งใช้เวลา 560–1,090 ms จากเกาหลี

**ค่าเกณฑ์** (`thresholds.py`) `minScore` ต่อ intent จะแทนที่ 0.70 ของ Router และ `min_score` ต่อการเรียกจะแทนที่ทั้งสองค่า ตามลำดับที่เอกสารระบุ เมื่อตั้ง `tls_question` ที่ 0.60 คำถามเรื่อง TLS ภาษาเกาหลี (0.61) จับคู่ได้ เมื่อตั้ง `off_topic` ที่ 0.85 คำขอให้เล่าเรื่องตลก (0.71) ก็ไม่จับคู่อีกต่อไป และการตั้งค่า 0.5 ต่อการเรียกทำให้ทั้งห้าคำค้นกลับมาจับคู่ได้ เทมเพลตของ Router (`CUSTOM`, `MODEL`, `GUARDRAILS`, `AGENT`) เป็นเพียงป้ายกำกับ: "Every template serves the same way."

<p class="shot"><img src="{{ '/assets/img/iris/24-intent-router-intents.webp' | relative_url }}" width="1440" height="765" alt="รายการ intent ของ Intent Router ที่มีเป้าหมาย tool, model, agent และ guardrail พร้อมช่อง Try a query" loading="lazy" decoding="async"></p>

intent พร้อมเป้าหมายและจำนวนตัวอย่าง; Try a query ใช้จับคู่จากคอนโซลได้ทันที <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### Context Gateway

**ตรวจสอบบน redis-iris 1.0.1, 2026-11-07** Gateway หนึ่งตัวในโหมดค้นหา มี upstream สองตัว: Context Surface บนสินค้าสมมติ 30 รายการในฐานข้อมูลฟรี และเซิร์ฟเวอร์ DeepWiki MCP สาธารณะ แล็บ: [`iris/04-context-gateway`](https://github.com/litkhai/notes-on-redis/tree/main/iris/04-context-gateway)

| ขั้นตอน | ผลลัพธ์ |
|---|---|
| เครื่องมือที่ agent มองเห็น | `search_tools`, `run_tool` |
| ค้นหา "black lamps under 100 dollars" | `products__filter_product` |
| Surface จากหนึ่งเอนทิตี หกฟิลด์ | สร้างเครื่องมือสิบตัว (นับ, กรอง, ค้นหาข้อความ, การดำเนินการเซต, ขยาย) |
| กรอง: lamp, black, ราคา ≤ 100 | ได้สินค้า 3 รายการเดียวกับที่สแกนตรง ๆ พบ; 2.4 วินาที |
| รูปแบบอาร์กิวเมนต์ผิด | ถูกปฏิเสธด้วย `invalid_arguments` ไม่ได้เรียกเครื่องมือ |
| `deepwiki__read_wiki_structure` redis/redis | รายการหน้าผ่าน Gateway; 1.5 วินาที |

ไม่ได้ใช้ `mcp-redis`: upstream ต้องเข้าถึงได้จาก Redis Cloud แต่โฮสต์นี้ไม่ได้เปิดให้บริการสาธารณะ ส่วน Surface ครอบคลุมข้อมูล Redis ในรูปแบบเครื่องมือ

<p class="shot"><img src="{{ '/assets/img/iris/19-context-surface-fields.webp' | relative_url }}" width="1440" height="1284" alt="ฟิลด์ของ Context Surface: id เป็นคีย์หลัก, name เป็นดัชนีข้อความ, category และ colour เป็นดัชนีแท็ก, price และ stock เป็นตัวเลข" loading="lazy" decoding="async"></p>

Context Surface คือโมเดลข้อมูล: เอนทิตีถูกแมปกับเทมเพลตคีย์ ฟิลด์มีชนิดและดัชนี Gateway สร้างเครื่องมือค้นหาจากโมเดลนี้ <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/25-context-gateway-upstreams.webp' | relative_url }}" width="1440" height="765" alt="upstream ของ Gateway: products Context Surface ที่มี 10 เครื่องมือ และเซิร์ฟเวอร์ deepwiki MCP ที่มี 3 เครื่องมือ" loading="lazy" decoding="async"></p>

upstream ทั้งสองอยู่หลัง endpoint เดียว และเปิดหรือปิดได้แยกกัน <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### Agent Playbooks

**ตรวจสอบบน redis-iris 1.0.1, 2026-11-07** เขียน FAQ สี่รายการจากข้อค้นพบของไซต์นี้ เขียนเป็น JSON และซิงก์ด้วย `iris` CLI แล็บ: [`iris/05-agent-playbooks`](https://github.com/litkhai/notes-on-redis/tree/main/iris/05-agent-playbooks)

| คำถาม | ที่พบ |
|---|---|
| is encryption in transit available on the free tier? | free-plan-tls 0.75 |
| how many clients can connect to the free database | free-plan-limits 0.76 |
| MSET fails with a slot error on my cluster | crossslot-error 0.85 |
| 무료 DB에서 TLS 켤 수 있어? | free-plan-tls 0.78 |
| How do I configure Active-Active between Seoul and Tokyo? | ไม่พบ; ส่งเป็นข้อเสนอให้ตรวจสอบแทน |

FAQ เวอร์ชันที่สองยังเป็นฉบับร่าง และ discovery ยังคงให้บริการเวอร์ชัน 1 จนกว่าจะรัน `faqs publish --version 2` key ก็ใช้ลำดับเดียวกัน: read, write, propose, publish, full คอนโซลแสดง Agent Playbooks และไม่มีรายการ LangCache

**Skill และข้อเสนอ** (`more.py`) Skill คือโฟลเดอร์ที่บีบอัดเป็น zip ซึ่งมี `SKILL.md` และไฟล์อ้างอิง skill นี้ตรวจเวิร์กโหลดเทียบกับขีดจำกัดของแผนฟรีที่วัดได้ หลังเผยแพร่แล้ว `discover` ส่งคืน skill นี้เมื่อถามเรื่องการประเมินขนาดเป็นภาษาอังกฤษ และเอเจนต์โหลดขั้นตอนกับไฟล์อ้างอิงของมันตามต้องการ ข้อเสนอที่ยังเปิดอยู่ถูกแก้ไข ยอมรับเข้าเป็น FAQ ที่ยังไม่เผยแพร่ และ `discover` พบก็ต่อเมื่อหลัง `publish_faq`

<p class="shot"><img src="{{ '/assets/img/iris/27-playbook-registry.webp' | relative_url }}" width="1440" height="765" alt="ทะเบียน Playbook ที่มี FAQ ที่เผยแพร่แล้วสี่รายการ หนึ่งในนั้นเป็นเวอร์ชัน 2" loading="lazy" decoding="async"></p>

ทะเบียนแสดงสถานะการเผยแพร่และเวอร์ชันล่าสุดของแต่ละ FAQ <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/28-playbook-proposals.webp' | relative_url }}" width="1440" height="765" alt="กล่องข้อเสนอที่มีข้อเสนอเกี่ยวกับ Active-Active ค้างอยู่หนึ่งรายการ" loading="lazy" decoding="async"></p>

ข้อเสนอจะรออยู่ในกล่องจนกว่าจะมีคนรับและเผยแพร่ <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### Agent Mesh และ Lens (เบต้า)

**ตรวจสอบบน redis-iris 1.0.1 กับ Redis 8.10.3 ใน Docker ในเครื่อง, 2026-11-07** Agent Mesh เก็บอีเวนต์ความคืบหน้าของเอเจนต์ไว้ใน Redis stream ทำให้ไคลเอนต์ที่หลุดการเชื่อมต่อกลับมาที่เซิร์ฟเวอร์ตัวไหนก็ได้และรับสิ่งที่พลาดไป จากเอกสาร: "When the client reconnects, it can receive retained updates after its last event cursor." ต้องใช้ Redis 8.6.2 ขึ้นไปสำหรับ `XADD IDMP` ([Deep Dive]({{ '/deep-dive/' | relative_url }})) และ "Cloud, Enterprise, failover recovery, and sustained capacity remain unqualified for this beta." แล็บรันแต่ละการเชื่อมต่อเป็นสองเรพลิกา และย้ายไคลเอนต์จากตัวหนึ่งไปอีกตัว

| การทดลอง | ผลลัพธ์ |
|---|---|
| FastAPI SSE: อ่านขั้นที่ 1–5 จากเรพลิกา A หายไป 3 วินาที แล้วต่อใหม่ไปเรพลิกา B ด้วย `Last-Event-ID` | B ส่งซ้ำขั้นที่ 6–11 แล้วส่งขั้นที่ 12–20 แบบสด ครบ 20 ขั้น ขั้นละหนึ่งครั้งพอดี |
| ต่อใหม่ที่เคอร์เซอร์สุดท้าย / เคอร์เซอร์ผิดรูปแบบ / run ที่ไม่รู้จัก | HTTP 204 / 422 `invalid_cursor` / 404 |
| สิ่งที่หนึ่ง run ทิ้งไว้ใน Redis | stream หนึ่งรายการ, `XLEN 22`, เปิด IDMP, TTL 120 วินาทีหลังเสร็จสิ้น |
| ปิดเรพลิกา A กลางการรัน ใช้ค่าเริ่มต้นของ SDK | ไม่มีอีเวนต์สุดท้าย: B ปิดแล้วเปิดการเชื่อมต่อใหม่ทุก 35 วินาที |
| เหมือนกัน แต่ใช้ `REDIS_SOCKET_TIMEOUT=30` | `stream.end` `producer_lost` หลังหมดเวลาเงียบ |
| A2A: Task เวอร์ชัน 1–4 จาก A แล้วต่อใหม่ไป B ด้วย `Last-Event-ID: 4` | เวอร์ชัน 5–12 และสถานะเสร็จสิ้น; อาร์ทิแฟกต์สิบรายการ รายการละหนึ่งครั้ง |

**กับดักข้อเดียวที่พบ:** redis-py 8.1.0 ตั้ง socket timeout เริ่มต้นไว้ 5 วินาที สั้นกว่าการอ่านแบบบล็อกของ SDK ที่ 15 วินาที SDK ถือว่าทุก timeout คือ Redis ล่ม จึงไม่เคยประกาศว่าผู้ผลิตหายไป ให้ตั้ง `REDIS_SOCKET_TIMEOUT` ให้มากกว่าช่วง heartbeat

Lens ติดตามเทิร์นของเอเจนต์ผ่าน OpenTelemetry บน Redis Cloud ฐานข้อมูลบันทึกของมันต้องเป็น "A Redis Cloud Essentials or Pro database" ดังนั้นบนแผนฟรี **New Lens** จึงถูกปิดใช้งาน เมื่อชี้ไปยังตัวรับแบบ loopback แทน SDK ส่งคำขอ OTLP/HTTP หนึ่งรายการต่อเทิร์น span ของเทิร์นประกอบด้วยการค้นหา Agent Memory ที่ถูกบันทึกโดยไม่ต้องเขียนโค้ดเพิ่ม บวกกับการดึงข้อมูลของแอปเองและขั้นตอนแบบกำหนดเอง เมื่อตั้ง `IRIS_LENS_CAPTURE_CONTENT=false` ข้อความของคำค้นและเอกสารจะถูกตัดออก เหลือเพียง ID คะแนน และแฮช เอกสาร: [Agent Mesh](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/), [FastAPI SSE SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/fastapi-sse-sdk/), [A2A SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/a2a-sdk/), [Lens](https://redis.io/docs/latest/develop/ai/context-engine/lens/), [Create Lens](https://redis.io/docs/latest/operate/iris/lens/create-lens/) แล็บ: [`iris/06-lens-and-mesh`](https://github.com/litkhai/notes-on-redis/tree/main/iris/06-lens-and-mesh)

**การส่งต่องาน** (`mesh_takeover.py`) เมื่อใช้ `takeover=True` งานที่โพรเซสถูก kill หลังทำเสร็จสามจากหกขั้นตอน ถูกปฏิเสธบนเรพลิกาอีกตัวตราบที่ heartbeat lease ของโพรเซสที่ตายแล้วยังไม่หมด (การปฏิเสธยังคืน HTTP 200 และเห็นได้จากประวัติ Task เท่านั้น) จากนั้นถูกรับช่วงที่ 15.1 วินาที โพรเซสใหม่ข้ามขั้นตอนที่เสร็จแล้วและทำส่วนที่เหลือจนครบ เมื่อใช้ค่าเริ่มต้น `takeover=False` ตัวอ่านทำเครื่องหมายงานเดียวกันว่าล้มเหลวด้วย `producer_lost` หลังผ่านไป 12.1 วินาที และไม่สามารถกลับมาทำต่อได้

<p class="shot"><img src="{{ '/assets/img/iris/29-lens-free-plan.webp' | relative_url }}" width="1440" height="1351" alt="หน้า Lens ในคอนโซล Redis Cloud ที่ปุ่ม New Lens เป็นสีเทาบนบัญชีแผนฟรี" loading="lazy" decoding="async"></p>

บนแผนฟรี New Lens ถูกปิดใช้งาน <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/iris/30-agent-mesh.webp' | relative_url }}" width="1440" height="1121" alt="หน้า Agent Mesh ในคอนโซล: ไลบรารีสำหรับสตรีม SSE และ A2A ที่กลับมาต่อได้บน Redis ไม่มีปุ่มสร้าง" loading="lazy" decoding="async"></p>

Agent Mesh มีหน้าของตัวเองแต่ไม่มีอะไรให้สร้าง: มันรันอยู่ในแอปของคุณเอง <small>บันทึกภาพหน้าจอเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### Iris ใช้อะไรจากฐานข้อมูลฟรี

บริการเหล่านี้เก็บข้อมูลและ connection pool ไว้ในฐานข้อมูลที่คุณเลือก เมื่อวางทั้ง Agent Memory, Intent Router, Context Surface และ Playbook ไว้บนฐานข้อมูลฟรี โดยฝั่งเราไม่ได้รันอะไรเลย ณ วันที่ 2026-11-07:

| ทรัพยากร | ที่ใช้ | วิธีที่เห็น |
|---|---|---|
| การเชื่อมต่อ | 28 จาก 30 | `CLIENT LIST`: ไคลเอนต์ `go-redis` 28 รายการจากแอดเดรสของ AWS us-east-1 บวกการเชื่อมต่อสำหรับตรวจสอบของเราอีก 1 รายการ |
| ข้อมูล | 16.7 MB จาก 30 MB, 111 คีย์ | การ์ด Configuration ในคอนโซล; คีย์ `iris:intent:*` 25, `memory:*` 44, `iris:playbook:*` 12, บวกสินค้าทดลอง 30 รายการ |
| Alert | อีเมลจาก Redis | "The number of connections for your database has reached 93.33% of the connections limit" |

บนแผนฟรี จะเหลือการเชื่อมต่อให้แอปพลิเคชันเพียงสองรายการ ควรให้ Iris มีฐานข้อมูลของตัวเอง หรือใช้แผนที่มีการเชื่อมต่อมากกว่านี้ ก่อนนำทราฟฟิกจริงมาวางไว้ข้างกัน

### สิ่งที่ยังไม่ได้ครอบคลุม

Lens บน Redis Cloud รองบประมาณ Essentials ใน [#8](https://github.com/litkhai/notes-on-redis/issues/8) ได้แก่ การสร้าง, UI ของ Lens, การอ่านเทิร์นย้อนกลับ และการติดตามการเรียกโมเดล ปริมาณการใช้ข้อความยังเป็นคำถามที่เปิดอยู่จนกว่าคอนโซลหรือใบเรียกเก็บเงินจะแสดงให้เห็น

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: dijalankan, kecuali Lens di Redis Cloud.** Agent Memory, Intent Router, Context Gateway, dan Agent Playbooks dijalankan pada paket gratis Redis Cloud pada 2026-11-07, dan Agent Mesh pada Redis 8.10.3 lokal (di bawah). Lens memerlukan basis data Essentials atau Pro, jadi hanya SDK-nya yang dijalankan.
</div>

Redis Iris, dalam kata-kata Redis sendiri, adalah "a production-ready context engine for AI agents" — sekumpulan layanan, bukan basis data; Redis adalah basis data di bawahnya. Diluncurkan 2026-05-18; pada 2026-11-04 menjadi enam layanan: Intent Router, Agent Playbooks, Agent Memory, dan Context Gateway (GA), serta Lens dan Agent Mesh (beta). Dikelola di Redis Cloud; dikelola sendiri lewat Helm chart yang memerlukan lisensi. Satu lab per layanan, semuanya pada basis data gratis dan 5.000 pesan gratis, dengan pesan yang terpakai per lab dicatat. Jebakan penamaan — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — mendapat bagiannya sendiri. Dibaca 2026-11-07 di [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

### Apakah Iris bisa dipakai di paket gratis?

**Ya, per 2026-11-07.** Pada akun gratis, empat layanan Iris menyediakan tombol buat (Agent Memory, Agent Playbooks, Context Gateway, Intent Router). **New Lens** berwarna abu-abu dan nonaktif, karena Lens membutuhkan basis data pencatatan Essentials atau Pro. Agent Mesh adalah pustaka yang berjalan di aplikasi Anda sendiri. Satu layanan Agent Memory dibuat pada basis data gratis 30 MB, diberi dua kunci API, dan dipakai dari SDK `redis-iris` 1.0.1 serta CLI `iris`: pemeriksaan kesehatan, penulisan memori, percakapan, ekstraksi latar belakang, dan pemanggilan kembali semuanya berfungsi. "5.000 pesan gratis" tidak ditampilkan di mana pun di konsol (halaman Iris, Usage, Billing), sehingga jumlah yang dipakai lab ini tidak diketahui.

### Lab: Agent Memory pada basis data gratis

**Diverifikasi pada redis-iris 1.0.1 (Python 3.12), paket gratis Redis Cloud (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07.** Sumber dan keluaran: [`iris/01-getting-started`](https://github.com/litkhai/notes-on-redis/tree/main/iris/01-getting-started).

<p class="shot"><img src="{{ '/assets/img/iris/01-agent-memory-landing.webp' | relative_url }}" width="1440" height="1054" alt="Halaman awal Agent Memory dengan tombol Create Agent Memory service" loading="lazy" decoding="async"></p>

Halaman awal Agent Memory pada akun gratis. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/02-agent-memory-create-form.webp' | relative_url }}" width="1440" height="765" alt="Dialog Create Agent Memory service: nama, basis data notes-on-redis-free, pengaturan bawaan" loading="lazy" decoding="async"></p>

Pembuatan layanan meminta nama dan basis data; basis data gratis sudah terpilih. Bawaan: memori jangka pendek 1 hari, jangka panjang 365 hari, ringkasan sesi aktif. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/03-agent-memory-connect.webp' | relative_url }}" width="1440" height="765" alt="Dialog Connect dengan endpoint, store ID, dan tab koneksi cepat untuk agents, SDK, dan CLI" loading="lazy" decoding="async"></p>

Layanan langsung siap. Connect memberikan endpoint dan store ID, serta prompt untuk ditempelkan ke agen pengodean yang memasang skill add-agent-memory. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/04-api-key-form.webp' | relative_url }}" width="1440" height="765" alt="Halaman Create API key: nama, kedaluwarsa 30 hari, Agent Memory store dengan read, write, full" loading="lazy" decoding="async"></p>

Kunci berada di Access & Identity, mencakup semua produk Iris. Setiap hak akses terdiri dari satu sumber daya dan satu aksi: read, write, atau full. Bawaan untuk store yang dicentang adalah read. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/05-api-keys-list.webp' | relative_url }}" width="1440" height="765" alt="Daftar kunci Access & Identity dengan dua kunci untuk Agent Memory, kedaluwarsa dalam 30 hari" loading="lazy" decoding="async"></p>

Dua kunci: kunci read dan kunci write. Token hanya ditampilkan sekali, saat pembuatan. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

| Langkah | Hasil |
|---|---|
| `health()` dengan kunci read | `HEALTHY`: tugas latar belakang, memori jangka panjang, memori sesi, tautan sumber, basis data penyimpanan |
| `remember()` dengan kunci read | ditolak: 403 `insufficient-permissions` |
| `remember()` dengan kunci write | memori tersimpan, topik `preferences` |
| percakapan dua giliran | sesi `cust-1042-<timestamp>` |
| ekstraksi latar belakang | dalam sekitar 15 detik: "User has a Redis Cloud database on the Free plan in the Seoul region"; beberapa menit kemudian memori kedua dari jawaban asisten |
| `recall()` ×10 dari Korea | median 611 ms (559–1.312 ms) |
| `iris agent-memory memories search` | tiga memori yang sama, dengan id dan topik |

**Tempat berjalannya.** Halaman layanan mencantumkan wilayah endpoint **us-east-1** sementara basis data berada di Seoul; waktu pemanggilan di atas mencakup jarak itu. **Yang ditulis ke basis data Anda:** tujuh kunci (dokumen JSON dan hash) dan empat indeks Search (memori jangka panjang, memori sesi, tautan sumber, namespace) muncul di basis data gratis.

<p class="shot"><img src="{{ '/assets/img/iris/06-agent-memory-services.webp' | relative_url }}" width="1440" height="765" alt="Daftar layanan Agent Memory dengan satu layanan pada notes-on-redis-free" loading="lazy" decoding="async"></p>

Daftar layanan mengaitkan setiap store dengan basis data Redis Cloud-nya. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/07-agent-memory-service.webp' | relative_url }}" width="1440" height="1704" alt="Konfigurasi layanan: wilayah endpoint us-east-1, TTL, perangkuman, tipe memori, pengecualian data sensitif, zona berbahaya" loading="lazy" decoding="async"></p>

Konfigurasi: TTL, perangkuman setelah 20 pesan dengan mempertahankan 10, tipe memori khusus, pengecualian data sensitif (detektor bawaan nonaktif secara bawaan). Menghapus layanan tetap menyimpan memori jangka panjang di basis data Anda. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/08-agent-memory-inspector.webp' | relative_url }}" width="1440" height="765" alt="Memory Inspector menampilkan sesi lab ini untuk pemilik cust-1042" loading="lazy" decoding="async"></p>

Memory Inspector menelusuri sesi dan memori jangka panjang berdasarkan pemilik atau namespace. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

### Agent Memory, lanjutan

**Diverifikasi pada redis-iris 1.0.1, 2026-11-07.** Lab: [`iris/02-agent-memory`](https://github.com/litkhai/notes-on-redis/tree/main/iris/02-agent-memory).

| Eksperimen | Hasil |
|---|---|
| 24 pesan dalam satu sesi | 14 peristiwa disimpan beserta satu ringkasan (meringkas setelah 20, menyimpan 10); ke-24 pesan masih dapat dibaca |
| Memori jangka panjang dari sesi itu | 25 untuk satu pemilik, sebagian besar satu per jawaban asisten |
| Memori di namespace `SHARED` | dikembalikan ke pemilik lain hanya jika namespace diberikan sebagai `shared` |
| Email dan telepon palsu, detektor nonaktif | tersimpan apa adanya sebagai memori |
| Sama, dengan detektor email, telepon, dan kartu aktif, "Redact match" | tersimpan sebagai `[REDACTED]`; nomor +82 juga terdeteksi |
| MemoryETL: tipe kustom `plan_limit`, dokumen 9 baris | 8 memori bertipe dalam 183 detik, harga dikecualikan sesuai perintah prompt |
| `forget(owner)` | sesi dan memori hilang dalam satu panggilan (25, 3, 3) |

Ekstraksi memakan waktu 4–5 menit pada proses ini, dibandingkan sekitar 15 detik pada lab pertama: ekstraksi berjalan di latar belakang sesuai jadwalnya sendiri.

<p class="shot"><img src="{{ '/assets/img/iris/09-agent-memory-detectors.webp' | relative_url }}" width="1440" height="765" alt="Pengecualian data sensitif dengan detektor kartu kredit, email, dan telepon diatur ke Redact match" loading="lazy" decoding="async"></p>

Detektor bawaan: kartu kredit, email, IP, telepon (US, CA, UK, DE, IL, IN, BR), dan SSN AS; masing-masing menyamarkan bagian yang cocok atau membuang memori. Jika detektor berbeda hasil, pembuangan yang menang. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/11-agent-memory-extractor.webp' | relative_url }}" width="1440" height="765" alt="Formulir extractor baru MemoryETL yang memakai tipe memori plan_limit" loading="lazy" decoding="async"></p>

MemoryETL (beta): extractor menyalin prompt tipe memori kustom dan mengubah dokumen yang diunggah atau dikirim lewat API menjadi memori bertipe itu. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

### Intent Router

**Diverifikasi pada redis-iris 1.0.1, 2026-11-07.** Empat intent dengan masing-masing tiga contoh, target dari empat jenis; delapan kueri berbahasa Inggris dan Korea. Embedder-nya adalah OpenAI `text-embedding-3-small` terkelola; tidak diminta kunci milik sendiri. Lab: [`iris/03-intent-router`](https://github.com/litkhai/notes-on-redis/tree/main/iris/03-intent-router).

| Kueri | Bawaan Router (0.70) | `min_score` 0.5 |
|---|---|---|
| I was billed twice, can you check? | fallback | billing 0.52 → tool |
| is encryption available on the free tier | fallback | tls_question 0.59 → model |
| connections keep timing out on my prod database | fallback | outage 0.51 → agent |
| tell me something funny | off_topic 0.71 → guardrail | off_topic 0.71 → guardrail |
| 무료 플랜에서 TLS를 켤 수 있나요? | fallback | tls_question 0.61 → model |
| 청구서를 어디서 받나요? | fallback | fallback, bahkan setelah contoh tagihan berbahasa Korea ditambahkan |
| Can you recommend a good restaurant? | fallback | fallback; off_topic 0.59 setelah menambahkan "맛집 추천해 줘" |

Dengan tiga contoh per intent, ambang bawaan terlalu ketat; menambah contoh atau menurunkan ambang adalah langkah penyetelan pertama. Setiap pencocokan memakan waktu 560–1,090 ms dari Korea.

**Ambang batas** (`thresholds.py`). `minScore` per intent menggantikan 0.70 milik Router, dan `min_score` per panggilan menggantikan keduanya, sesuai urutan dalam dokumentasi. Dengan `tls_question` di 0.60, pertanyaan TLS berbahasa Korea (0.61) cocok; dengan `off_topic` di 0.85, permintaan lelucon (0.71) tidak lagi cocok; 0.5 per panggilan mengembalikan kelima kueri. Template Router (`CUSTOM`, `MODEL`, `GUARDRAILS`, `AGENT`) hanyalah label: "Every template serves the same way."

<p class="shot"><img src="{{ '/assets/img/iris/24-intent-router-intents.webp' | relative_url }}" width="1440" height="765" alt="Daftar intent Intent Router dengan target tool, model, agent, dan guardrail, serta kotak Try a query" loading="lazy" decoding="async"></p>

Intent beserta target dan jumlah contohnya; Try a query mencocokkan langsung dari konsol. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

### Context Gateway

**Diverifikasi pada redis-iris 1.0.1, 2026-11-07.** Satu Gateway dalam mode pencarian dengan dua upstream: Context Surface atas 30 produk rekaan di basis data gratis, dan server DeepWiki MCP publik. Lab: [`iris/04-context-gateway`](https://github.com/litkhai/notes-on-redis/tree/main/iris/04-context-gateway).

| Langkah | Hasil |
|---|---|
| Alat yang terlihat oleh agent | `search_tools`, `run_tool` |
| pencarian "black lamps under 100 dollars" | `products__filter_product` |
| Surface dari satu entitas, enam bidang | sepuluh alat yang dihasilkan (hitung, filter, pencarian teks, operasi himpunan, perluas) |
| Filter: lamp, black, harga ≤ 100 | 3 produk yang sama dengan hasil pemindaian langsung; 2.4 detik |
| Bentuk argumen salah | ditolak dengan `invalid_arguments`, alat tidak dipanggil |
| `deepwiki__read_wiki_structure` redis/redis | daftar halaman lewat Gateway; 1.5 detik |

`mcp-redis` tidak dipakai: upstream harus dapat dijangkau dari Redis Cloud, dan host ini tidak menyediakannya secara publik. Surface mencakup data Redis sebagai alat.

<p class="shot"><img src="{{ '/assets/img/iris/19-context-surface-fields.webp' | relative_url }}" width="1440" height="1284" alt="Bidang Context Surface: id sebagai kunci primer, name indeks teks, category dan colour indeks tag, price dan stock numerik" loading="lazy" decoding="async"></p>

Context Surface adalah model data: entitas dipetakan ke templat kunci, bidang diberi tipe dan indeks. Gateway membangun alat pencarian dari model ini. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/25-context-gateway-upstreams.webp' | relative_url }}" width="1440" height="765" alt="Upstream Gateway: products Context Surface dengan 10 alat dan server deepwiki MCP dengan 3 alat" loading="lazy" decoding="async"></p>

Kedua upstream berada di balik satu endpoint, masing-masing dapat diaktifkan atau dinonaktifkan. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

### Agent Playbooks

**Diverifikasi pada redis-iris 1.0.1, 2026-11-07.** Empat FAQ ditulis dari temuan situs ini, disusun sebagai JSON dan disinkronkan dengan CLI `iris`. Lab: [`iris/05-agent-playbooks`](https://github.com/litkhai/notes-on-redis/tree/main/iris/05-agent-playbooks).

| Pertanyaan | Ditemukan |
|---|---|
| is encryption in transit available on the free tier? | free-plan-tls 0.75 |
| how many clients can connect to the free database | free-plan-limits 0.76 |
| MSET fails with a slot error on my cluster | crossslot-error 0.85 |
| 무료 DB에서 TLS 켤 수 있어? | free-plan-tls 0.78 |
| How do I configure Active-Active between Seoul and Tokyo? | tidak ada; diusulkan untuk ditinjau |

Versi kedua sebuah FAQ tetap berstatus draf dan discovery terus menyajikan versi 1 sampai `faqs publish --version 2` dijalankan. Kunci mengikuti alur yang sama: read, write, propose, publish, full. Konsol menampilkan Agent Playbooks dan tidak ada entri LangCache.

**Skill dan proposal** (`more.py`). Skill adalah folder terkompresi yang berisi `SKILL.md` dan file referensi; skill ini memeriksa beban kerja terhadap batas terukur paket gratis. Setelah dipublikasikan, `discover` mengembalikannya untuk pertanyaan perencanaan kapasitas berbahasa Inggris dan agen memuat langkah serta file referensinya sesuai kebutuhan. Proposal yang masih terbuka diedit, diterima ke dalam FAQ yang belum dipublikasikan, dan baru ditemukan oleh `discover` setelah `publish_faq`.

<p class="shot"><img src="{{ '/assets/img/iris/27-playbook-registry.webp' | relative_url }}" width="1440" height="765" alt="Registri Playbook dengan empat FAQ yang diterbitkan, satu di antaranya versi 2" loading="lazy" decoding="async"></p>

Registri menampilkan status penerbitan dan versi terbaru setiap FAQ. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/28-playbook-proposals.webp' | relative_url }}" width="1440" height="765" alt="Kotak masuk usulan dengan satu usulan terbuka tentang Active-Active" loading="lazy" decoding="async"></p>

Usulan menunggu di kotak masuk sampai seseorang menerima dan menerbitkannya. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

### Agent Mesh dan Lens (beta)

**Diverifikasi pada redis-iris 1.0.1 dengan Redis 8.10.3 di Docker lokal, 2026-11-07.** Agent Mesh menyimpan peristiwa kemajuan agen dalam stream Redis, sehingga klien yang terputus dapat kembali ke server mana pun dan menerima apa yang terlewat. Dari dokumentasi: "When the client reconnects, it can receive retained updates after its last event cursor." Ia memerlukan Redis 8.6.2+ untuk `XADD IDMP` ([Deep Dive]({{ '/deep-dive/' | relative_url }})), dan "Cloud, Enterprise, failover recovery, and sustained capacity remain unqualified for this beta." Lab menjalankan setiap integrasi sebagai dua replika dan memindahkan klien dari satu ke yang lain.

| Eksperimen | Hasil |
|---|---|
| FastAPI SSE: baca langkah 1–5 dari replika A, pergi 3 detik, sambung ulang ke replika B dengan `Last-Event-ID` | B memutar ulang 6–11, lalu 12–20 secara langsung; ke-20 langkah tepat satu kali |
| Sambung ulang pada kursor terakhir / kursor tidak valid / run tidak dikenal | HTTP 204 / 422 `invalid_cursor` / 404 |
| Yang ditinggalkan satu run di Redis | satu stream, `XLEN 22`, IDMP aktif, TTL 120 detik setelah selesai |
| Replika A dimatikan di tengah run, bawaan SDK | tanpa peristiwa akhir: B menutup dan membuka ulang koneksi setiap 35 detik |
| Sama, dengan `REDIS_SOCKET_TIMEOUT=30` | `stream.end` `producer_lost` setelah batas waktu hening |
| A2A: Task versi 1–4 dari A, sambung ulang ke B dengan `Last-Event-ID: 4` | versi 5–12 dan status selesai; sepuluh artefak, masing-masing sekali |

**Satu jebakan yang ditemukan:** redis-py 8.1.0 menetapkan batas waktu soket 5 detik secara bawaan, lebih pendek daripada pembacaan pemblokiran 15 detik milik SDK. SDK menganggap setiap batas waktu sebagai gangguan Redis, sehingga tidak pernah menyatakan produsen hilang. Atur `REDIS_SOCKET_TIMEOUT` lebih besar dari interval heartbeat.

Lens melacak giliran agen lewat OpenTelemetry. Di Redis Cloud, basis data pencatatnya harus "A Redis Cloud Essentials or Pro database", sehingga pada paket gratis **New Lens** dinonaktifkan. Setelah diarahkan ke penerima loopback, SDK mengirim satu permintaan OTLP/HTTP per giliran. Span giliran itu mencakup pencarian Agent Memory yang tercatat tanpa kode tambahan, ditambah pengambilan milik aplikasi sendiri dan satu langkah kustom. Dengan `IRIS_LENS_CAPTURE_CONTENT=false`, teks kueri dan dokumen dibuang, menyisakan ID, skor, dan hash. Dokumentasi: [Agent Mesh](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/), [FastAPI SSE SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/fastapi-sse-sdk/), [A2A SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/a2a-sdk/), [Lens](https://redis.io/docs/latest/develop/ai/context-engine/lens/), [Create Lens](https://redis.io/docs/latest/operate/iris/lens/create-lens/). Lab: [`iris/06-lens-and-mesh`](https://github.com/litkhai/notes-on-redis/tree/main/iris/06-lens-and-mesh).

**Menyerahkan tugas** (`mesh_takeover.py`). Dengan `takeover=True`, sebuah tugas yang prosesnya dimatikan setelah tiga dari enam langkah ditolak di replika lain selama lease heartbeat proses yang mati masih berlaku (penolakan tetap mengembalikan HTTP 200; hanya riwayat Task yang menunjukkannya), lalu diambil alih pada 15.1 detik; proses baru melewati langkah yang sudah selesai dan menyelesaikan sisanya. Dengan `takeover=False` bawaan, seorang pembaca menandai tugas yang sama gagal dengan `producer_lost` setelah 12.1 detik, dan tugas itu tidak bisa dilanjutkan.

<p class="shot"><img src="{{ '/assets/img/iris/29-lens-free-plan.webp' | relative_url }}" width="1440" height="1351" alt="Halaman Lens di konsol Redis Cloud dengan tombol New Lens berwarna abu-abu pada akun paket gratis" loading="lazy" decoding="async"></p>

Pada paket gratis, New Lens dinonaktifkan. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/30-agent-mesh.webp' | relative_url }}" width="1440" height="1121" alt="Halaman Agent Mesh di konsol: pustaka untuk aliran SSE dan A2A yang dapat dilanjutkan di Redis, tanpa tombol buat" loading="lazy" decoding="async"></p>

Agent Mesh punya halaman tetapi tidak ada yang dibuat: ia berjalan di dalam aplikasi Anda sendiri. <small>Ditangkap 2026-11-07, paket gratis Redis Cloud.</small>

### Biaya Iris pada database gratis

Layanan menyimpan data dan connection pool-nya di database yang Anda pilih. Dengan Agent Memory, Intent Router, Context Surface, dan Playbook semuanya di database gratis, tanpa ada yang kami jalankan sendiri, pada 2026-11-07:

| Sumber daya | Terpakai | Cara melihatnya |
|---|---|---|
| Koneksi | 28 dari 30 | `CLIENT LIST`: 28 klien `go-redis` dari alamat AWS us-east-1, ditambah satu koneksi pemeriksaan kami |
| Data | 16.7 MB dari 30 MB, 111 key | kartu Configuration di konsol; key `iris:intent:*` 25, `memory:*` 44, `iris:playbook:*` 12, ditambah 30 produk latihan |
| Alert | email dari Redis | "The number of connections for your database has reached 93.33% of the connections limit" |

Pada paket gratis, itu menyisakan dua koneksi untuk aplikasi. Berikan Iris database tersendiri, atau paket dengan lebih banyak koneksi, sebelum menempatkan lalu lintas nyata di sampingnya.

### Yang belum dicakup

Lens di Redis Cloud menunggu anggaran Essentials di [#8](https://github.com/litkhai/notes-on-redis/issues/8): pembuatannya, UI Lens, membaca kembali giliran, dan pelacakan panggilan model. Konsumsi pesan tetap menjadi pertanyaan terbuka sampai konsol atau tagihan menunjukkannya.

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: dijalankan, kecuali Lens di Redis Cloud.** Agent Memory, Intent Router, Context Gateway dan Agent Playbooks dijalankan pada pelan percuma Redis Cloud pada 2026-11-07, dan Agent Mesh pada Redis 8.10.3 setempat (di bawah). Lens memerlukan pangkalan data Essentials atau Pro, jadi hanya SDK-nya yang dijalankan.
</div>

Redis Iris, dalam kata-kata Redis sendiri, ialah "a production-ready context engine for AI agents" — satu set perkhidmatan, bukan pangkalan data; Redis ialah pangkalan data di bawahnya. Dilancarkan 2026-05-18; pada 2026-11-04 ia menjadi enam perkhidmatan: Intent Router, Agent Playbooks, Agent Memory dan Context Gateway (GA), serta Lens dan Agent Mesh (beta). Diurus di Redis Cloud; urus sendiri melalui Helm chart yang memerlukan lesen. Satu makmal bagi setiap perkhidmatan, semuanya pada pangkalan data percuma dan 5,000 mesej percuma, dengan mesej yang digunakan bagi setiap makmal direkodkan. Perangkap penamaan — Context Retriever → Context Gateway, LangCache lwn Agent Playbooks — diberi bahagiannya sendiri. Dibaca 2026-11-07 di [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

### Adakah Iris boleh digunakan pada pelan percuma?

**Ya, setakat 2026-11-07.** Pada akaun percuma, empat perkhidmatan Iris menawarkan butang cipta (Agent Memory, Agent Playbooks, Context Gateway, Intent Router). **New Lens** berwarna kelabu dan dilumpuhkan, kerana Lens memerlukan pangkalan data rekod Essentials atau Pro. Agent Mesh ialah pustaka yang berjalan dalam aplikasi anda sendiri. Satu perkhidmatan Agent Memory dicipta pada pangkalan data percuma 30 MB, diberi dua kunci API, dan digunakan daripada SDK `redis-iris` 1.0.1 serta CLI `iris`: pemeriksaan kesihatan, penulisan memori, perbualan, pengekstrakan latar belakang dan ingatan semula semuanya berfungsi. "5,000 mesej percuma" tidak dipaparkan di mana-mana dalam konsol (halaman Iris, Usage, Billing), jadi bilangan yang digunakan makmal ini tidak diketahui.

### Makmal: Agent Memory pada pangkalan data percuma

**Disahkan pada redis-iris 1.0.1 (Python 3.12), pelan percuma Redis Cloud (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07.** Sumber dan output: [`iris/01-getting-started`](https://github.com/litkhai/notes-on-redis/tree/main/iris/01-getting-started).

<p class="shot"><img src="{{ '/assets/img/iris/01-agent-memory-landing.webp' | relative_url }}" width="1440" height="1054" alt="Halaman utama Agent Memory dengan butang Create Agent Memory service" loading="lazy" decoding="async"></p>

Halaman utama Agent Memory pada akaun percuma. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/02-agent-memory-create-form.webp' | relative_url }}" width="1440" height="765" alt="Dialog Create Agent Memory service: nama, pangkalan data notes-on-redis-free, tetapan lalai" loading="lazy" decoding="async"></p>

Mencipta perkhidmatan memerlukan nama dan pangkalan data; pangkalan data percuma sudah dipilih. Lalai: memori jangka pendek 1 hari, jangka panjang 365 hari, ringkasan sesi dihidupkan. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/03-agent-memory-connect.webp' | relative_url }}" width="1440" height="765" alt="Dialog Connect dengan endpoint, store ID dan tab sambungan pantas untuk agents, SDK dan CLI" loading="lazy" decoding="async"></p>

Perkhidmatan siap serta-merta. Connect memberikan endpoint dan store ID, serta gesaan untuk ditampal ke ejen pengekodan yang memasang skill add-agent-memory. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/04-api-key-form.webp' | relative_url }}" width="1440" height="765" alt="Halaman Create API key: nama, tamat tempoh 30 hari, Agent Memory store dengan read, write, full" loading="lazy" decoding="async"></p>

Kunci berada dalam Access & Identity, merentasi semua produk Iris. Setiap kebenaran ialah satu sumber ditambah satu tindakan: read, write atau full. Lalai untuk store yang ditandakan ialah read. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/05-api-keys-list.webp' | relative_url }}" width="1440" height="765" alt="Senarai kunci Access & Identity dengan dua kunci untuk Agent Memory, tamat tempoh dalam 30 hari" loading="lazy" decoding="async"></p>

Dua kunci: kunci read dan kunci write. Token dipaparkan sekali sahaja, semasa penciptaan. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

| Langkah | Hasil |
|---|---|
| `health()` dengan kunci read | `HEALTHY`: tugas latar belakang, memori jangka panjang, memori sesi, pautan sumber, pangkalan data storan |
| `remember()` dengan kunci read | ditolak: 403 `insufficient-permissions` |
| `remember()` dengan kunci write | memori disimpan, topik `preferences` |
| perbualan dua giliran | sesi `cust-1042-<timestamp>` |
| pengekstrakan latar belakang | dalam masa lebih kurang 15 saat: "User has a Redis Cloud database on the Free plan in the Seoul region"; beberapa minit kemudian memori kedua daripada jawapan pembantu |
| `recall()` ×10 dari Korea | median 611 ms (559–1,312 ms) |
| `iris agent-memory memories search` | tiga memori yang sama, dengan id dan topik |

**Tempat ia berjalan.** Halaman perkhidmatan menyenaraikan wilayah endpoint sebagai **us-east-1** manakala pangkalan data berada di Seoul; masa ingatan semula di atas termasuk jarak itu. **Apa yang ditulis ke dalam pangkalan data anda:** tujuh kunci (dokumen JSON dan hash) dan empat indeks Search (memori jangka panjang, memori sesi, pautan sumber, namespace) muncul dalam pangkalan data percuma.

<p class="shot"><img src="{{ '/assets/img/iris/06-agent-memory-services.webp' | relative_url }}" width="1440" height="765" alt="Senarai perkhidmatan Agent Memory dengan satu perkhidmatan pada notes-on-redis-free" loading="lazy" decoding="async"></p>

Senarai perkhidmatan mengaitkan setiap store dengan pangkalan data Redis Cloud-nya. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/07-agent-memory-service.webp' | relative_url }}" width="1440" height="1704" alt="Konfigurasi perkhidmatan: wilayah endpoint us-east-1, TTL, ringkasan, jenis memori, pengecualian data sensitif, zon bahaya" loading="lazy" decoding="async"></p>

Konfigurasi: TTL, ringkasan selepas 20 mesej dengan mengekalkan 10, jenis memori tersuai, pengecualian data sensitif (pengesan terbina dalam dimatikan secara lalai). Memadam perkhidmatan mengekalkan memori jangka panjang dalam pangkalan data anda. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/08-agent-memory-inspector.webp' | relative_url }}" width="1440" height="765" alt="Memory Inspector menyenaraikan sesi makmal ini untuk pemilik cust-1042" loading="lazy" decoding="async"></p>

Memory Inspector menyemak imbas sesi dan memori jangka panjang mengikut pemilik atau namespace. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

### Agent Memory, lanjutan

**Disahkan pada redis-iris 1.0.1, 2026-11-07.** Makmal: [`iris/02-agent-memory`](https://github.com/litkhai/notes-on-redis/tree/main/iris/02-agent-memory).

| Eksperimen | Keputusan |
|---|---|
| 24 mesej dalam satu sesi | 14 peristiwa disimpan beserta satu ringkasan (meringkaskan selepas 20, simpan 10); kesemua 24 masih boleh dibaca |
| Memori jangka panjang daripada sesi itu | 25 untuk satu pemilik, kebanyakannya satu bagi setiap jawapan pembantu |
| Memori dalam ruang nama `SHARED` | dikembalikan kepada pemilik lain hanya apabila ruang nama diberikan sebagai `shared` |
| E-mel dan telefon palsu, pengesan dimatikan | disimpan seadanya sebagai memori |
| Sama, dengan pengesan e-mel, telefon dan kad dihidupkan, "Redact match" | disimpan sebagai `[REDACTED]`; nombor +82 turut dikesan |
| MemoryETL: jenis tersuai `plan_limit`, dokumen 9 baris | 8 memori bertaip dalam 183 saat, harga ditinggalkan seperti yang diminta prompt |
| `forget(owner)` | sesi dan memori hilang dalam satu panggilan (25, 3, 3) |

Pengekstrakan mengambil masa 4–5 minit dalam larian ini berbanding kira-kira 15 saat dalam makmal pertama: ia berjalan di latar belakang mengikut jadualnya sendiri.

<p class="shot"><img src="{{ '/assets/img/iris/09-agent-memory-detectors.webp' | relative_url }}" width="1440" height="765" alt="Pengecualian data sensitif dengan pengesan kad kredit, e-mel dan telefon ditetapkan kepada Redact match" loading="lazy" decoding="async"></p>

Pengesan terbina dalam: kad kredit, e-mel, IP, telefon (US, CA, UK, DE, IL, IN, BR) dan SSN AS; setiap satu menyamarkan padanan atau membuang memori. Apabila pengesan tidak sepakat, pembuangan diutamakan. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/11-agent-memory-extractor.webp' | relative_url }}" width="1440" height="765" alt="Borang extractor baharu MemoryETL yang menggunakan jenis memori plan_limit" loading="lazy" decoding="async"></p>

MemoryETL (beta): extractor menyalin prompt jenis memori tersuai dan menukar dokumen yang dimuat naik atau dihantar melalui API kepada memori berjenis itu. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

### Intent Router

**Disahkan pada redis-iris 1.0.1, 2026-11-07.** Empat intent dengan tiga contoh setiap satu, sasaran daripada empat jenis; lapan pertanyaan dalam bahasa Inggeris dan Korea. Embedder ialah OpenAI `text-embedding-3-small` terurus; tiada kunci sendiri diminta. Makmal: [`iris/03-intent-router`](https://github.com/litkhai/notes-on-redis/tree/main/iris/03-intent-router).

| Pertanyaan | Lalai Router (0.70) | `min_score` 0.5 |
|---|---|---|
| I was billed twice, can you check? | fallback | billing 0.52 → tool |
| is encryption available on the free tier | fallback | tls_question 0.59 → model |
| connections keep timing out on my prod database | fallback | outage 0.51 → agent |
| tell me something funny | off_topic 0.71 → guardrail | off_topic 0.71 → guardrail |
| 무료 플랜에서 TLS를 켤 수 있나요? | fallback | tls_question 0.61 → model |
| 청구서를 어디서 받나요? | fallback | fallback, walaupun selepas contoh bil dalam bahasa Korea ditambah |
| Can you recommend a good restaurant? | fallback | fallback; off_topic 0.59 selepas menambah "맛집 추천해 줘" |

Dengan tiga contoh bagi setiap intent, ambang lalai terlalu ketat; menambah contoh atau menurunkan ambang ialah langkah penalaan pertama. Setiap padanan mengambil masa 560–1,090 ms dari Korea.

**Ambang** (`thresholds.py`). `minScore` bagi setiap intent menggantikan 0.70 milik Router, dan `min_score` bagi setiap panggilan menggantikan kedua-duanya, mengikut susunan dalam dokumentasi. Dengan `tls_question` pada 0.60, soalan TLS dalam bahasa Korea (0.61) dipadankan; dengan `off_topic` pada 0.85, permintaan jenaka (0.71) tidak lagi dipadankan; 0.5 bagi setiap panggilan memulihkan kelima-lima pertanyaan. Templat Router (`CUSTOM`, `MODEL`, `GUARDRAILS`, `AGENT`) ialah label: "Every template serves the same way."

<p class="shot"><img src="{{ '/assets/img/iris/24-intent-router-intents.webp' | relative_url }}" width="1440" height="765" alt="Senarai intent Intent Router dengan sasaran tool, model, agent dan guardrail, serta kotak Try a query" loading="lazy" decoding="async"></p>

Intent beserta sasaran dan bilangan contohnya; Try a query memadankan terus dari konsol. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

### Context Gateway

**Disahkan pada redis-iris 1.0.1, 2026-11-07.** Satu Gateway dalam mod carian dengan dua upstream: Context Surface ke atas 30 produk rekaan dalam pangkalan data percuma, dan pelayan DeepWiki MCP awam. Makmal: [`iris/04-context-gateway`](https://github.com/litkhai/notes-on-redis/tree/main/iris/04-context-gateway).

| Langkah | Keputusan |
|---|---|
| Alat yang dilihat oleh agent | `search_tools`, `run_tool` |
| carian "black lamps under 100 dollars" | `products__filter_product` |
| Surface daripada satu entiti, enam medan | sepuluh alat dijana (kira, tapis, carian teks, operasi set, kembangkan) |
| Tapis: lamp, black, harga ≤ 100 | 3 produk yang sama seperti hasil imbasan terus; 2.4 saat |
| Bentuk argumen salah | ditolak dengan `invalid_arguments`, alat tidak dipanggil |
| `deepwiki__read_wiki_structure` redis/redis | senarai halaman melalui Gateway; 1.5 saat |

`mcp-redis` tidak digunakan: upstream mesti boleh dicapai dari Redis Cloud, dan hos ini tidak menyediakannya secara awam. Surface merangkumi data Redis sebagai alat.

<p class="shot"><img src="{{ '/assets/img/iris/19-context-surface-fields.webp' | relative_url }}" width="1440" height="1284" alt="Medan Context Surface: id sebagai kunci utama, name indeks teks, category dan colour indeks tag, price dan stock berangka" loading="lazy" decoding="async"></p>

Context Surface ialah model data: entiti dipetakan kepada templat kunci, medan diberi jenis dan indeks. Gateway membina alat carian daripadanya. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/25-context-gateway-upstreams.webp' | relative_url }}" width="1440" height="765" alt="Upstream Gateway: products Context Surface dengan 10 alat dan pelayan deepwiki MCP dengan 3 alat" loading="lazy" decoding="async"></p>

Kedua-dua upstream berada di sebalik satu endpoint, masing-masing boleh dihidupkan atau dimatikan. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

### Agent Playbooks

**Disahkan pada redis-iris 1.0.1, 2026-11-07.** Empat FAQ ditulis daripada penemuan tapak ini, disusun sebagai JSON dan diselaraskan dengan CLI `iris`. Makmal: [`iris/05-agent-playbooks`](https://github.com/litkhai/notes-on-redis/tree/main/iris/05-agent-playbooks).

| Soalan | Dijumpai |
|---|---|
| is encryption in transit available on the free tier? | free-plan-tls 0.75 |
| how many clients can connect to the free database | free-plan-limits 0.76 |
| MSET fails with a slot error on my cluster | crossslot-error 0.85 |
| 무료 DB에서 TLS 켤 수 있어? | free-plan-tls 0.78 |
| How do I configure Active-Active between Seoul and Tokyo? | tiada; dicadangkan untuk semakan sebaliknya |

Versi kedua sesuatu FAQ kekal sebagai draf dan discovery terus menyajikan versi 1 sehingga `faqs publish --version 2` dijalankan. Kunci mengikuti aliran kerja yang sama: read, write, propose, publish, full. Konsol menyenaraikan Agent Playbooks dan tiada entri LangCache.

**Skill dan cadangan** (`more.py`). Skill ialah folder termampat yang mengandungi `SKILL.md` dan fail rujukan; skill ini menyemak beban kerja berdasarkan had terukur pelan percuma. Selepas diterbitkan, `discover` mengembalikannya untuk soalan pengiraan saiz dalam bahasa Inggeris dan ejen memuatkan langkah serta fail rujukannya apabila diperlukan. Cadangan yang masih terbuka disunting, diterima ke dalam FAQ yang belum diterbitkan, dan hanya ditemui oleh `discover` selepas `publish_faq`.

<p class="shot"><img src="{{ '/assets/img/iris/27-playbook-registry.webp' | relative_url }}" width="1440" height="765" alt="Daftar Playbook dengan empat FAQ yang diterbitkan, satu daripadanya versi 2" loading="lazy" decoding="async"></p>

Daftar ini memaparkan status penerbitan dan versi terkini bagi setiap FAQ. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/28-playbook-proposals.webp' | relative_url }}" width="1440" height="765" alt="Peti masuk cadangan dengan satu cadangan terbuka tentang Active-Active" loading="lazy" decoding="async"></p>

Cadangan menunggu dalam peti masuk sehingga seseorang menerima dan menerbitkannya. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

### Agent Mesh dan Lens (beta)

**Disahkan pada redis-iris 1.0.1 dengan Redis 8.10.3 dalam Docker setempat, 2026-11-07.** Agent Mesh menyimpan peristiwa kemajuan ejen dalam stream Redis, supaya klien yang terputus sambungan boleh kembali ke mana-mana pelayan dan menerima apa yang terlepas. Daripada dokumentasi: "When the client reconnects, it can receive retained updates after its last event cursor." Ia memerlukan Redis 8.6.2+ untuk `XADD IDMP` ([Deep Dive]({{ '/deep-dive/' | relative_url }})), dan "Cloud, Enterprise, failover recovery, and sustained capacity remain unqualified for this beta." Makmal menjalankan setiap integrasi sebagai dua replika dan memindahkan klien dari satu ke yang lain.

| Eksperimen | Hasil |
|---|---|
| FastAPI SSE: baca langkah 1–5 dari replika A, pergi 3 saat, sambung semula ke replika B dengan `Last-Event-ID` | B memainkan semula 6–11, kemudian 12–20 secara langsung; kesemua 20 langkah tepat sekali |
| Sambung semula pada kursor akhir / kursor tidak sah / run tidak dikenali | HTTP 204 / 422 `invalid_cursor` / 404 |
| Apa yang ditinggalkan satu run dalam Redis | satu stream, `XLEN 22`, IDMP hidup, TTL 120 saat selepas selesai |
| Replika A dimatikan di tengah run, lalai SDK | tiada peristiwa akhir: B menutup dan membuka semula sambungan setiap 35 saat |
| Sama, dengan `REDIS_SOCKET_TIMEOUT=30` | `stream.end` `producer_lost` selepas had masa senyap |
| A2A: Task versi 1–4 dari A, sambung semula ke B dengan `Last-Event-ID: 4` | versi 5–12 dan status selesai; sepuluh artifak, setiap satu sekali |

**Satu perangkap yang ditemui:** redis-py 8.1.0 menetapkan had masa soket 5 saat secara lalai, lebih pendek daripada bacaan menyekat 15 saat milik SDK. SDK menganggap setiap had masa sebagai gangguan Redis, jadi ia tidak pernah mengisytiharkan pengeluar hilang. Tetapkan `REDIS_SOCKET_TIMEOUT` melebihi sela heartbeat.

Lens menjejak giliran ejen melalui OpenTelemetry. Di Redis Cloud, pangkalan data rekodnya mesti "A Redis Cloud Essentials or Pro database", jadi pada pelan percuma **New Lens** dilumpuhkan. Setelah diarahkan ke penerima loopback, SDK menghantar satu permintaan OTLP/HTTP bagi setiap giliran. Span giliran itu termasuk carian Agent Memory yang direkodkan tanpa kod tambahan, serta pengambilan milik aplikasi sendiri dan satu langkah tersuai. Dengan `IRIS_LENS_CAPTURE_CONTENT=false`, teks pertanyaan dan dokumen dibuang, meninggalkan ID, skor dan hash. Dokumentasi: [Agent Mesh](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/), [FastAPI SSE SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/fastapi-sse-sdk/), [A2A SDK guide](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/a2a-sdk/), [Lens](https://redis.io/docs/latest/develop/ai/context-engine/lens/), [Create Lens](https://redis.io/docs/latest/operate/iris/lens/create-lens/). Makmal: [`iris/06-lens-and-mesh`](https://github.com/litkhai/notes-on-redis/tree/main/iris/06-lens-and-mesh).

**Menyerahkan tugas** (`mesh_takeover.py`). Dengan `takeover=True`, sesuatu tugas yang prosesnya dimatikan selepas tiga daripada enam langkah ditolak pada replika lain selagi lease heartbeat proses yang mati masih berlaku (penolakan masih memulangkan HTTP 200; hanya sejarah Task menunjukkannya), kemudian diambil alih pada 15.1 saat; proses baharu melangkau langkah yang sudah selesai dan melengkapkan bakinya. Dengan `takeover=False` lalai, seorang pembaca menandakan tugas yang sama gagal dengan `producer_lost` selepas 12.1 saat, dan ia tidak boleh disambung semula.

<p class="shot"><img src="{{ '/assets/img/iris/29-lens-free-plan.webp' | relative_url }}" width="1440" height="1351" alt="Halaman Lens dalam konsol Redis Cloud dengan butang New Lens berwarna kelabu pada akaun pelan percuma" loading="lazy" decoding="async"></p>

Pada pelan percuma, New Lens dilumpuhkan. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/iris/30-agent-mesh.webp' | relative_url }}" width="1440" height="1121" alt="Halaman Agent Mesh dalam konsol: pustaka untuk aliran SSE dan A2A yang boleh disambung semula pada Redis, tanpa butang cipta" loading="lazy" decoding="async"></p>

Agent Mesh mempunyai halaman tetapi tiada apa yang perlu dicipta: ia berjalan di dalam aplikasi anda sendiri. <small>Ditangkap 2026-11-07, pelan percuma Redis Cloud.</small>

### Kos Iris pada pangkalan data percuma

Perkhidmatan menyimpan data dan connection pool mereka dalam pangkalan data yang anda pilih. Dengan Agent Memory, Intent Router, Context Surface dan Playbook semuanya pada pangkalan data percuma, tanpa sebarang perkara kami berjalan sendiri, pada 2026-11-07:

| Sumber | Digunakan | Cara ia dilihat |
|---|---|---|
| Sambungan | 28 daripada 30 | `CLIENT LIST`: 28 klien `go-redis` dari alamat AWS us-east-1, ditambah satu sambungan semakan kami |
| Data | 16.7 MB daripada 30 MB, 111 kunci | kad Configuration di konsol; kunci `iris:intent:*` 25, `memory:*` 44, `iris:playbook:*` 12, ditambah 30 produk latihan |
| Alert | e-mel daripada Redis | "The number of connections for your database has reached 93.33% of the connections limit" |

Pada pelan percuma, itu hanya meninggalkan dua sambungan untuk aplikasi. Berikan Iris pangkalan data sendiri, atau pelan dengan lebih banyak sambungan, sebelum meletakkan trafik sebenar di sebelahnya.

### Yang belum diliputi

Lens di Redis Cloud menunggu bajet Essentials di [#8](https://github.com/litkhai/notes-on-redis/issues/8): mencipta, UI Lens, membaca semula giliran dan penjejakan panggilan model. Penggunaan mesej kekal sebagai soalan terbuka sehingga konsol atau bil menunjukkannya.

</div>
