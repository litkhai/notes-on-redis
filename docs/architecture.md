---
layout: default
title: Architecture
permalink: /architecture/
---

# Architecture

<div class="lang" data-lang="en" markdown="1">

## English

**Where Redis goes in a system, and why it is good there.** Six layouts, from a cache in front of a database to the context layer of an AI agent. Each has a diagram, where Redis sits, what makes it strong there backed by a measurement on this site where one exists, what to watch, and the official documentation with its key sentence quoted. Layouts this site has not run end to end are marked as designs.

| Layout | Redis is | Run on this site |
|---|---|---|
| Cache in front of a database | a fast copy of hot reads | partly: throughput and limits |
| Hot state with high availability | the system of record for sessions, counters, queues | yes: persistence, replicas, Sentinel |
| Scale-out with Redis Cluster | data split across shards by hash slot | yes: six-node cluster, slot migration |
| Managed on Redis Cloud | a service, from one database to Active-Active | free plan only; Active-Active is a design |
| Context layer for AI agents (Iris) | memory, routing, approved answers and tools around an LLM | Agent Memory yes; other services not yet |
| Search and vectors next to the data | the index and the records in one place | probes only |

### 1. Cache in front of a database

The application asks Redis first; on a miss it reads the database and writes the result to Redis with a TTL. Redis holds a copy, the database stays the source of truth.

<div class="arch" markdown="0"><svg viewBox="0 0 760 250" role="img" aria-label="Cache-aside: the application reads Redis first and fills it from the database on a miss"><title>Cache-aside: the application reads Redis first and fills it from the database on a miss</title><rect class="box" x="20" y="95" width="130" height="60" rx="7"/><text x="85.0" y="129.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="170" height="60" rx="7"/><text x="385.0" y="47.0" text-anchor="middle">Redis</text><text class="sm" x="385.0" y="63.0" text-anchor="middle">cache, TTL + eviction</text><rect class="box" x="300" y="170" width="170" height="60" rx="7"/><text x="385.0" y="197.0" text-anchor="middle">Primary database</text><text class="sm" x="385.0" y="213.0" text-anchor="middle">source of truth</text><line class="ln" x1="150" y1="105" x2="298" y2="38"/><polygon class="hd" points="298.0,38.0 293.5,43.4 291.0,37.8"/><text class="sm" x="224.0" y="65.5" text-anchor="middle">1 GET</text><line class="ln" x1="150" y1="145" x2="298" y2="205"/><polygon class="hd" points="298.0,205.0 291.0,205.5 293.3,199.8"/><text class="sm" x="224.0" y="169.0" text-anchor="middle">2 on miss: read</text><line class="ln dash" x1="150" y1="125" x2="298" y2="66"/><polygon class="hd" points="298.0,66.0 293.3,71.2 291.0,65.5"/><text class="sm" x="246" y="112" text-anchor="middle">3 SET with TTL</text><rect class="box" x="560" y="95" width="180" height="60" rx="7"/><text x="650.0" y="122.0" text-anchor="middle">Other app servers</text><text class="sm" x="650.0" y="138.0" text-anchor="middle">client-side cache</text><line class="ln dash" x1="470" y1="50" x2="558" y2="112"/><polygon class="hd" points="558.0,112.0 551.1,110.9 554.6,105.9"/><text class="sm" x="514.0" y="75.0" text-anchor="middle">invalidations</text></svg></div>

| Strong because | Evidence |
|---|---|
| Reads come from memory on one event loop | 134,523–136,097 SET/GET per second on one node with defaults; 498,753–520,472 with `io-threads 8` ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Data structures, not just strings | hashes with per-field TTL, sorted sets, JSON in the stock image ([Setup]({{ '/setup/' | relative_url }})) |
| Clients can cache too, and be told when to drop it | server-assisted client-side caching (docs below) |

**Watch:** invalidation is the hard part; the docs say "A problem with the above pattern is how to invalidate the information that the application is holding". The eviction policy decides what happens when memory is full: under `volatile-lru` keys without a TTL are never evicted and writes fail with `OOM` ([Redis Cloud free database]({{ '/cloud/' | relative_url }})).

Docs: [Client-side caching](https://redis.io/docs/latest/develop/reference/client-side-caching/), [Eviction](https://redis.io/docs/latest/develop/reference/eviction/).

### 2. Hot state with high availability

Sessions, carts, rate-limit counters and queues live in Redis as the system of record. A primary writes an append-only file, two replicas follow it, and three Sentinels promote a replica when the primary fails.

<div class="arch" markdown="0"><svg viewBox="0 0 700 290" role="img" aria-label="Primary with two replicas and three Sentinels for failover"><title>Primary with two replicas and three Sentinels for failover</title><rect class="box" x="20" y="100" width="130" height="56" rx="7"/><text x="85.0" y="132.0" text-anchor="middle">Application</text><rect class="rd" x="250" y="90" width="160" height="76" rx="7"/><text x="330.0" y="125.0" text-anchor="middle">Redis primary</text><text class="sm" x="330.0" y="141.0" text-anchor="middle">AOF everysec</text><rect class="rd" x="520" y="30" width="150" height="52" rx="7"/><text x="595.0" y="60.0" text-anchor="middle">Replica 1</text><rect class="rd" x="520" y="170" width="150" height="52" rx="7"/><text x="595.0" y="200.0" text-anchor="middle">Replica 2</text><line class="ln" x1="150" y1="128" x2="248" y2="128"/><polygon class="hd" points="248.0,128.0 241.7,131.0 241.7,125.0"/><text class="sm" x="199.0" y="122.0" text-anchor="middle">writes, WAIT</text><line class="ln" x1="410" y1="112" x2="518" y2="60"/><polygon class="hd" points="518.0,60.0 513.6,65.5 511.0,60.0"/><text class="sm" x="464.0" y="80.0" text-anchor="middle">replication</text><line class="ln" x1="410" y1="145" x2="518" y2="192"/><polygon class="hd" points="518.0,192.0 511.0,192.3 513.4,186.7"/><rect class="box" x="250" y="236" width="420" height="40" rx="7"/><text x="460.0" y="260.0" text-anchor="middle">Sentinel ×3  ·  quorum 2  ·  promotes a replica on failure</text><line class="ln dash" x1="330" y1="236" x2="330" y2="168"/><polygon class="hd" points="330.0,168.0 333.0,174.3 327.0,174.3"/></svg></div>

| Strong because | Evidence |
|---|---|
| Durability without giving up speed | AOF `everysec` 97,087 req/s, p99 0.255 ms; `always` 17,203 req/s ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Fast, automatic failover | primary stopped → new master named in 4,402 ms; the old primary rejoined as a replica |
| Point-in-time backups without stopping | `BACKUP START`/`SEAL` (8.10) restored into a new server with `preload-file` |

**Watch:** replication is asynchronous. The docs: "WAIT does not make Redis a strongly consistent store", and `WAIT` only counts the acknowledgements of the calling connection's own writes. Snapshots copy memory on write: 252 MB of copy-on-write for a 214 MB dataset under overwrites. Give Sentinel addresses that stay resolvable: watching a container name stretched the same failover to 284 s.

Docs: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/).

### 3. Scale-out with Redis Cluster

When one node's memory or CPU is not enough, Redis Cluster splits the keyspace into 16,384 hash slots across primaries, each with replicas. Clients learn the slot map and talk to the right node directly.

<div class="arch" markdown="0"><svg viewBox="0 0 760 260" role="img" aria-label="Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot"><title>Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot</title><rect class="box" x="20" y="105" width="150" height="60" rx="7"/><text x="95.0" y="132.0" text-anchor="middle">Cluster-aware client</text><text class="sm" x="95.0" y="148.0" text-anchor="middle">caches slot map</text><rect class="rd" x="250" y="40" width="150" height="56" rx="7"/><text x="325.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="325.0" y="81.0" text-anchor="middle">slots 0–5460</text><rect class="rd" x="250" y="165" width="150" height="50" rx="7"/><text x="325.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="325" y1="96" x2="325" y2="163"/><polygon class="hd" points="325.0,163.0 322.0,156.7 328.0,156.7"/><rect class="rd" x="420" y="40" width="150" height="56" rx="7"/><text x="495.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="495.0" y="81.0" text-anchor="middle">5461–10922</text><rect class="rd" x="420" y="165" width="150" height="50" rx="7"/><text x="495.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="495" y1="96" x2="495" y2="163"/><polygon class="hd" points="495.0,163.0 492.0,156.7 498.0,156.7"/><rect class="rd" x="590" y="40" width="150" height="56" rx="7"/><text x="665.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="665.0" y="81.0" text-anchor="middle">10923–16383</text><rect class="rd" x="590" y="165" width="150" height="50" rx="7"/><text x="665.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="665" y1="96" x2="665" y2="163"/><polygon class="hd" points="665.0,163.0 662.0,156.7 668.0,156.7"/><line class="ln" x1="170" y1="125" x2="248" y2="70"/><polygon class="hd" points="248.0,70.0 244.6,76.1 241.1,71.1"/><text class="sm" x="209.0" y="91.5" text-anchor="middle">key → CRC16 mod 16384</text><text class="sm" x="495" y="245" text-anchor="middle">CLUSTER MIGRATION moves slot ranges between primaries atomically</text></svg></div>

| Strong because | Evidence |
|---|---|
| Resharding without stopping writes | `CLUSTER MIGRATION IMPORT 0 999` moved 1,000 slots in 44 ms with `write_pause_ms 0` under ~200,000 writes/s ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Predictable routing | `HASH_SLOT = CRC16(key) mod 16384`; a wrong node answers `MOVED` with the right one |

**Watch:** multi-key commands must stay in one slot. `MSET user:1 a user:2 b` returns `CROSSSLOT`; a shared hash tag (`{user:1}:cart`, `{user:1}:orders`) keeps related keys together. ElastiCache Serverless behaves the same way ([Compare]({{ '/compare/' | relative_url }})). The spec: "Each master node in a cluster handles a subset of the 16384 hash slots".

Docs: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/).

### 4. Managed on Redis Cloud

The same engine as a service. Essentials is one database on shared infrastructure with optional replication; Pro is dedicated, holds many databases, and adds Active-Active copies in several regions that all accept writes.

<div class="arch" markdown="0"><svg viewBox="0 0 760 255" role="img" aria-label="Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro"><title>Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro</title><rect class="box" x="20" y="40" width="160" height="60" rx="7"/><text x="100.0" y="74.0" text-anchor="middle">App, region A</text><rect class="box" x="20" y="160" width="160" height="60" rx="7"/><text x="100.0" y="194.0" text-anchor="middle">App, region B</text><rect class="box" x="270" y="20" width="230" height="100" rx="7"/><text x="385.0" y="74.0" text-anchor="middle"></text><text x="385" y="44" text-anchor="middle">Redis Cloud · Essentials</text><rect class="rd" x="290" y="58" width="190" height="46" rx="7"/><text x="385.0" y="78.0" text-anchor="middle">one database</text><text class="sm" x="385.0" y="94.0" text-anchor="middle">replica in-zone or multi-AZ</text><rect class="box" x="270" y="140" width="470" height="100" rx="7"/><text x="505.0" y="194.0" text-anchor="middle"></text><text x="505" y="163" text-anchor="middle">Redis Cloud · Pro · Active-Active</text><rect class="rd" x="290" y="178" width="190" height="46" rx="7"/><text x="385.0" y="198.0" text-anchor="middle">copy in region A</text><text class="sm" x="385.0" y="214.0" text-anchor="middle">read + write</text><rect class="rd" x="530" y="178" width="190" height="46" rx="7"/><text x="625.0" y="198.0" text-anchor="middle">copy in region B</text><text class="sm" x="625.0" y="214.0" text-anchor="middle">read + write</text><line class="ln" x1="480" y1="201" x2="528" y2="201"/><polygon class="hd" points="528.0,201.0 521.7,204.0 521.7,198.0"/><polygon class="hd" points="480.0,201.0 486.3,198.0 486.3,204.0"/><text class="sm" x="504.0" y="195.0" text-anchor="middle">CRDT sync</text><line class="ln" x1="180" y1="70" x2="288" y2="80"/><polygon class="hd" points="288.0,80.0 281.4,82.5 282.0,76.4"/><line class="ln" x1="180" y1="190" x2="288" y2="200"/><polygon class="hd" points="288.0,200.0 281.4,202.5 282.0,196.4"/></svg></div>

| Strong because | Evidence |
|---|---|
| A database in seconds, modules included | free database ready seconds after the form, Search and JSON available ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| Automation from day one | the REST API works on the free plan ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| Writes in every region (Pro) | design only here; the docs: "Active-Active databases allow read and write operations in each copy", synchronised by CRDTs |

**Watch:** the free plan is for trying things: 30 MB, 30 connections, no TLS (the API refuses `enableTls`). Prices read in the console on 2026-11-07: Essentials from $5 a month, Pro from $200 a month.

Docs: [Redis Cloud](https://redis.io/docs/latest/operate/rc/), [High availability](https://redis.io/docs/latest/operate/rc/databases/configuration/high-availability/), [Active-Active](https://redis.io/docs/latest/operate/rc/databases/active-active/).

### 5. Context layer for AI agents: Redis Iris

Iris puts services around an agent so it does not rebuild context on every turn. The docs: "Redis Iris is a production-ready context engine for AI agents" that "adds persistent memory", "answers recurring questions without a model call", gives agents "one MCP endpoint for the tools of any MCP server and your Redis data", and "routes each message". Agent Memory keeps its data in a Redis database you own.

<div class="arch" markdown="0"><svg viewBox="0 0 780 320" role="img" aria-label="Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database"><title>Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database</title><rect class="box" x="20" y="110" width="110" height="56" rx="7"/><text x="75.0" y="142.0" text-anchor="middle">User</text><rect class="box" x="180" y="100" width="170" height="76" rx="7"/><text x="265.0" y="135.0" text-anchor="middle">Agent app</text><text class="sm" x="265.0" y="151.0" text-anchor="middle">LLM + your code</text><line class="ln" x1="130" y1="138" x2="178" y2="138"/><polygon class="hd" points="178.0,138.0 171.7,141.0 171.7,135.0"/><rect class="rd" x="430" y="20" width="190" height="48" rx="7"/><text x="525.0" y="41.0" text-anchor="middle">Intent Router</text><text class="sm" x="525.0" y="57.0" text-anchor="middle">route before the LLM</text><line class="ln" x1="350" y1="138" x2="428" y2="44"/><polygon class="hd" points="428.0,44.0 426.3,50.8 421.6,46.9"/><rect class="rd" x="430" y="80" width="190" height="48" rx="7"/><text x="525.0" y="101.0" text-anchor="middle">Agent Memory</text><text class="sm" x="525.0" y="117.0" text-anchor="middle">remember · recall</text><line class="ln" x1="350" y1="138" x2="428" y2="104"/><polygon class="hd" points="428.0,104.0 423.4,109.3 421.0,103.7"/><rect class="rd" x="430" y="140" width="190" height="48" rx="7"/><text x="525.0" y="161.0" text-anchor="middle">Agent Playbooks</text><text class="sm" x="525.0" y="177.0" text-anchor="middle">approved answers</text><line class="ln" x1="350" y1="138" x2="428" y2="164"/><polygon class="hd" points="428.0,164.0 421.1,164.9 423.0,159.1"/><rect class="rd" x="430" y="200" width="190" height="48" rx="7"/><text x="525.0" y="221.0" text-anchor="middle">Context Gateway</text><text class="sm" x="525.0" y="237.0" text-anchor="middle">one MCP endpoint</text><line class="ln" x1="350" y1="138" x2="428" y2="224"/><polygon class="hd" points="428.0,224.0 421.5,221.4 426.0,217.3"/><rect class="rd" x="430" y="260" width="190" height="48" rx="7"/><text x="525.0" y="281.0" text-anchor="middle">Lens</text><text class="sm" x="525.0" y="297.0" text-anchor="middle">trace each turn</text><line class="ln" x1="350" y1="138" x2="428" y2="284"/><polygon class="hd" points="428.0,284.0 422.3,279.9 427.7,277.0"/><rect class="rd" x="660" y="100" width="100" height="70" rx="7"/><text x="710.0" y="132.0" text-anchor="middle">Redis DB</text><text class="sm" x="710.0" y="148.0" text-anchor="middle">JSON + Search</text><line class="ln dash" x1="620" y1="104" x2="658" y2="125"/><polygon class="hd" points="658.0,125.0 651.0,124.6 654.0,119.3"/><line class="ln dash" x1="620" y1="216" x2="658" y2="150"/><polygon class="hd" points="658.0,150.0 657.5,157.0 652.2,153.9"/><rect class="box" x="660" y="230" width="100" height="56" rx="7"/><text x="710.0" y="255.0" text-anchor="middle">MCP servers</text><text class="sm" x="710.0" y="271.0" text-anchor="middle">your tools</text><line class="ln dash" x1="620" y1="232" x2="658" y2="252"/><polygon class="hd" points="658.0,252.0 651.0,251.8 653.8,246.4"/></svg></div>

| Strong because | Evidence |
|---|---|
| Memory that builds itself | a fact from a two-turn conversation was extracted about 15 s later ([Iris]({{ '/iris/' | relative_url }})) |
| Your data stays in your database | Agent Memory wrote JSON documents and four Search indexes into the free database ([Iris]({{ '/iris/' | relative_url }})) |
| Scoped keys per product and resource | a read key could recall but got 403 on writes ([Iris]({{ '/iris/' | relative_url }})) |
| Cheaper turns | Intent Router and Agent Playbooks answer or route before a model call: design only here |

**Watch:** where the service runs: the Agent Memory endpoint was in us-east-1 while the database was in Seoul, and recall from Korea took a median 611 ms. Message metering was not visible anywhere in the console. Intent Router, Playbooks, Context Gateway and Lens have not been run yet.

Docs: [Redis Iris](https://redis.io/docs/latest/develop/ai/context-engine/), [Agent Memory](https://redis.io/docs/latest/operate/iris/agent-memory/), [Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/), [Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/), [Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/), [Lens](https://redis.io/docs/latest/operate/iris/lens/).

### 6. Search and vectors next to the data

Records, their secondary index and their embeddings live in the same Redis database, so a query does not cross to another system.

<div class="arch" markdown="0"><svg viewBox="0 0 760 215" role="img" aria-label="Search and vectors in the same Redis database as the records"><title>Search and vectors in the same Redis database as the records</title><rect class="box" x="20" y="80" width="150" height="60" rx="7"/><text x="95.0" y="114.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="420" height="180" rx="7"/><text x="510.0" y="114.0" text-anchor="middle"></text><text x="510" y="44" text-anchor="middle">one Redis 8 database</text><rect class="box" x="320" y="60" width="170" height="52" rx="7"/><text x="405.0" y="83.0" text-anchor="middle">Hashes / JSON</text><text class="sm" x="405.0" y="99.0" text-anchor="middle">the records</text><rect class="box" x="530" y="60" width="170" height="52" rx="7"/><text x="615.0" y="83.0" text-anchor="middle">Search index</text><text class="sm" x="615.0" y="99.0" text-anchor="middle">text · numeric · vector</text><rect class="box" x="320" y="128" width="380" height="52" rx="7"/><text x="510.0" y="151.0" text-anchor="middle">Vector set (beta)</text><text class="sm" x="510.0" y="167.0" text-anchor="middle">VADD · VSIM, no index to define</text><line class="ln" x1="490" y1="86" x2="528" y2="86"/><polygon class="hd" points="528.0,86.0 521.7,89.0 521.7,83.0"/><line class="ln" x1="170" y1="110" x2="298" y2="110"/><polygon class="hd" points="298.0,110.0 291.7,113.0 291.7,107.0"/><text class="sm" x="234.0" y="104.0" text-anchor="middle">FT.SEARCH / VSIM</text></svg></div>

| Strong because | Evidence |
|---|---|
| Built in, no configuration | Search, JSON and vector sets load with the stock Redis 8 image ([Setup]({{ '/setup/' | relative_url }})) |
| One query language for text, numbers and vectors | `FT.CREATE` over hashes, numeric range and vector index probes ran on Redis 8.10.3 ([Compare]({{ '/compare/' | relative_url }})) |
| A native vector type | `VADD` and `VSIM` work without defining an index |

**Watch:** vector sets are beta. Relevance and speed at scale were not measured here; the local Search lab is still planned.

Docs: [Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/).

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

**시스템에서 Redis가 놓이는 자리, 그리고 거기서 강한 이유.** 데이터베이스 앞의 캐시부터 AI 에이전트의 컨텍스트 계층까지 배치 여섯 가지. 각각 다이어그램, Redis의 자리, 그 자리에서 강한 점(이 사이트에 측정이 있으면 그 근거), 주의할 점, 핵심 문장을 인용한 공식 문서를 담았다. 이 사이트에서 끝까지 실행하지 않은 배치는 설계로 표시한다.

| 배치 | Redis의 역할 | 이 사이트에서 실행 |
|---|---|---|
| 데이터베이스 앞의 캐시 | 자주 읽는 데이터의 빠른 사본 | 일부: 처리량과 한도 |
| 고가용성을 갖춘 핫 상태 | 세션·카운터·큐의 원본 저장소 | 예: 영속성, 복제본, Sentinel |
| Redis Cluster로 확장 | 해시 슬롯으로 샤드에 나뉜 데이터 | 예: 노드 6개 클러스터, 슬롯 이전 |
| Redis Cloud 관리형 | DB 하나부터 Active-Active까지의 서비스 | 무료 플랜만. Active-Active는 설계 |
| AI 에이전트 컨텍스트 계층(Iris) | LLM 주위의 기억, 라우팅, 승인된 답, 도구 | Agent Memory는 예, 나머지는 아직 |
| 데이터 옆의 검색과 벡터 | 인덱스와 레코드를 한곳에 | 기능 확인만 |

### 1. 데이터베이스 앞의 캐시

애플리케이션은 먼저 Redis에 묻는다. 없으면 데이터베이스에서 읽어 TTL과 함께 Redis에 쓴다. Redis는 사본을 들고, 원본은 데이터베이스에 있다.

<div class="arch" markdown="0"><svg viewBox="0 0 760 250" role="img" aria-label="Cache-aside: the application reads Redis first and fills it from the database on a miss"><title>Cache-aside: the application reads Redis first and fills it from the database on a miss</title><rect class="box" x="20" y="95" width="130" height="60" rx="7"/><text x="85.0" y="129.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="170" height="60" rx="7"/><text x="385.0" y="47.0" text-anchor="middle">Redis</text><text class="sm" x="385.0" y="63.0" text-anchor="middle">cache, TTL + eviction</text><rect class="box" x="300" y="170" width="170" height="60" rx="7"/><text x="385.0" y="197.0" text-anchor="middle">Primary database</text><text class="sm" x="385.0" y="213.0" text-anchor="middle">source of truth</text><line class="ln" x1="150" y1="105" x2="298" y2="38"/><polygon class="hd" points="298.0,38.0 293.5,43.4 291.0,37.8"/><text class="sm" x="224.0" y="65.5" text-anchor="middle">1 GET</text><line class="ln" x1="150" y1="145" x2="298" y2="205"/><polygon class="hd" points="298.0,205.0 291.0,205.5 293.3,199.8"/><text class="sm" x="224.0" y="169.0" text-anchor="middle">2 on miss: read</text><line class="ln dash" x1="150" y1="125" x2="298" y2="66"/><polygon class="hd" points="298.0,66.0 293.3,71.2 291.0,65.5"/><text class="sm" x="246" y="112" text-anchor="middle">3 SET with TTL</text><rect class="box" x="560" y="95" width="180" height="60" rx="7"/><text x="650.0" y="122.0" text-anchor="middle">Other app servers</text><text class="sm" x="650.0" y="138.0" text-anchor="middle">client-side cache</text><line class="ln dash" x1="470" y1="50" x2="558" y2="112"/><polygon class="hd" points="558.0,112.0 551.1,110.9 554.6,105.9"/><text class="sm" x="514.0" y="75.0" text-anchor="middle">invalidations</text></svg></div>

| 강한 이유 | 근거 |
|---|---|
| 읽기가 이벤트 루프 하나에서 메모리로 처리된다 | 기본 설정 노드 하나에서 초당 SET/GET 134,523–136,097, `io-threads 8`로 498,753–520,472([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 문자열만이 아니라 자료 구조 | 필드별 TTL이 있는 해시, sorted set, JSON이 기본 이미지에 있다([Setup]({{ '/setup/' | relative_url }})) |
| 클라이언트도 캐시하고, 버릴 때를 통보받는다 | 서버가 돕는 클라이언트 측 캐시(아래 문서) |

**주의:** 어려운 것은 무효화다. 문서의 표현: "A problem with the above pattern is how to invalidate the information that the application is holding". 메모리가 차면 축출 정책이 결과를 정한다. `volatile-lru`에서는 TTL 없는 키가 축출되지 않고 쓰기가 `OOM`으로 실패한다([Redis Cloud 무료 DB]({{ '/cloud/' | relative_url }})).

문서: [Client-side caching](https://redis.io/docs/latest/develop/reference/client-side-caching/), [Eviction](https://redis.io/docs/latest/develop/reference/eviction/).

### 2. 고가용성을 갖춘 핫 상태

세션, 장바구니, 요청 제한 카운터, 큐를 Redis에 원본으로 둔다. 주 서버가 AOF를 쓰고, 복제본 둘이 따라가며, Sentinel 셋이 주 서버 장애 때 복제본을 승격한다.

<div class="arch" markdown="0"><svg viewBox="0 0 700 290" role="img" aria-label="Primary with two replicas and three Sentinels for failover"><title>Primary with two replicas and three Sentinels for failover</title><rect class="box" x="20" y="100" width="130" height="56" rx="7"/><text x="85.0" y="132.0" text-anchor="middle">Application</text><rect class="rd" x="250" y="90" width="160" height="76" rx="7"/><text x="330.0" y="125.0" text-anchor="middle">Redis primary</text><text class="sm" x="330.0" y="141.0" text-anchor="middle">AOF everysec</text><rect class="rd" x="520" y="30" width="150" height="52" rx="7"/><text x="595.0" y="60.0" text-anchor="middle">Replica 1</text><rect class="rd" x="520" y="170" width="150" height="52" rx="7"/><text x="595.0" y="200.0" text-anchor="middle">Replica 2</text><line class="ln" x1="150" y1="128" x2="248" y2="128"/><polygon class="hd" points="248.0,128.0 241.7,131.0 241.7,125.0"/><text class="sm" x="199.0" y="122.0" text-anchor="middle">writes, WAIT</text><line class="ln" x1="410" y1="112" x2="518" y2="60"/><polygon class="hd" points="518.0,60.0 513.6,65.5 511.0,60.0"/><text class="sm" x="464.0" y="80.0" text-anchor="middle">replication</text><line class="ln" x1="410" y1="145" x2="518" y2="192"/><polygon class="hd" points="518.0,192.0 511.0,192.3 513.4,186.7"/><rect class="box" x="250" y="236" width="420" height="40" rx="7"/><text x="460.0" y="260.0" text-anchor="middle">Sentinel ×3  ·  quorum 2  ·  promotes a replica on failure</text><line class="ln dash" x1="330" y1="236" x2="330" y2="168"/><polygon class="hd" points="330.0,168.0 333.0,174.3 327.0,174.3"/></svg></div>

| 강한 이유 | 근거 |
|---|---|
| 속도를 크게 잃지 않는 내구성 | AOF `everysec` 초당 97,087, p99 0.255 ms. `always`는 초당 17,203([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 빠른 자동 장애 조치 | 주 서버 정지 → 4,402 ms 만에 새 마스터 지목, 옛 주 서버는 복제본으로 복귀 |
| 멈추지 않는 시점 백업 | `BACKUP START`/`SEAL`(8.10)을 `preload-file`로 새 서버에 복원 |

**주의:** 복제는 비동기다. 문서의 표현: "WAIT does not make Redis a strongly consistent store". `WAIT`은 호출한 연결이 쓴 내용의 확인만 센다. 스냅숏은 쓰기 때 메모리를 복사한다. 214 MB 데이터를 덮어쓰는 동안 copy-on-write가 252 MB였다. Sentinel에는 계속 풀리는 주소를 준다. 컨테이너 이름을 감시하자 같은 장애 조치가 284초로 늘었다.

문서: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/).

### 3. Redis Cluster로 확장

노드 하나의 메모리나 CPU로 부족하면 Redis Cluster가 키 공간을 16,384개 해시 슬롯으로 나눠 주 서버들에 배분한다. 주 서버마다 복제본이 있다. 클라이언트는 슬롯 지도를 받아 맞는 노드와 직접 통신한다.

<div class="arch" markdown="0"><svg viewBox="0 0 760 260" role="img" aria-label="Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot"><title>Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot</title><rect class="box" x="20" y="105" width="150" height="60" rx="7"/><text x="95.0" y="132.0" text-anchor="middle">Cluster-aware client</text><text class="sm" x="95.0" y="148.0" text-anchor="middle">caches slot map</text><rect class="rd" x="250" y="40" width="150" height="56" rx="7"/><text x="325.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="325.0" y="81.0" text-anchor="middle">slots 0–5460</text><rect class="rd" x="250" y="165" width="150" height="50" rx="7"/><text x="325.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="325" y1="96" x2="325" y2="163"/><polygon class="hd" points="325.0,163.0 322.0,156.7 328.0,156.7"/><rect class="rd" x="420" y="40" width="150" height="56" rx="7"/><text x="495.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="495.0" y="81.0" text-anchor="middle">5461–10922</text><rect class="rd" x="420" y="165" width="150" height="50" rx="7"/><text x="495.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="495" y1="96" x2="495" y2="163"/><polygon class="hd" points="495.0,163.0 492.0,156.7 498.0,156.7"/><rect class="rd" x="590" y="40" width="150" height="56" rx="7"/><text x="665.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="665.0" y="81.0" text-anchor="middle">10923–16383</text><rect class="rd" x="590" y="165" width="150" height="50" rx="7"/><text x="665.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="665" y1="96" x2="665" y2="163"/><polygon class="hd" points="665.0,163.0 662.0,156.7 668.0,156.7"/><line class="ln" x1="170" y1="125" x2="248" y2="70"/><polygon class="hd" points="248.0,70.0 244.6,76.1 241.1,71.1"/><text class="sm" x="209.0" y="91.5" text-anchor="middle">key → CRC16 mod 16384</text><text class="sm" x="495" y="245" text-anchor="middle">CLUSTER MIGRATION moves slot ranges between primaries atomically</text></svg></div>

| 강한 이유 | 근거 |
|---|---|
| 쓰기를 멈추지 않는 재샤딩 | 초당 약 200,000 쓰기 중 `CLUSTER MIGRATION IMPORT 0 999`가 슬롯 1,000개를 44 ms에 이전, `write_pause_ms 0`([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 예측 가능한 라우팅 | `HASH_SLOT = CRC16(key) mod 16384`. 잘못된 노드는 맞는 노드를 담아 `MOVED`로 답한다 |

**주의:** 여러 키 명령은 한 슬롯 안에 있어야 한다. `MSET user:1 a user:2 b`는 `CROSSSLOT`. 해시 태그를 공유하면(`{user:1}:cart`, `{user:1}:orders`) 관련 키가 함께 놓인다. ElastiCache Serverless도 같다([Compare]({{ '/compare/' | relative_url }})). 명세의 표현: "Each master node in a cluster handles a subset of the 16384 hash slots".

문서: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/).

### 4. Redis Cloud 관리형

같은 엔진을 서비스로 쓴다. Essentials는 공유 인프라 위의 DB 하나와 선택적 복제, Pro는 전용 인프라에 DB 여러 개, 그리고 여러 리전의 사본이 모두 쓰기를 받는 Active-Active를 더한다.

<div class="arch" markdown="0"><svg viewBox="0 0 760 255" role="img" aria-label="Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro"><title>Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro</title><rect class="box" x="20" y="40" width="160" height="60" rx="7"/><text x="100.0" y="74.0" text-anchor="middle">App, region A</text><rect class="box" x="20" y="160" width="160" height="60" rx="7"/><text x="100.0" y="194.0" text-anchor="middle">App, region B</text><rect class="box" x="270" y="20" width="230" height="100" rx="7"/><text x="385.0" y="74.0" text-anchor="middle"></text><text x="385" y="44" text-anchor="middle">Redis Cloud · Essentials</text><rect class="rd" x="290" y="58" width="190" height="46" rx="7"/><text x="385.0" y="78.0" text-anchor="middle">one database</text><text class="sm" x="385.0" y="94.0" text-anchor="middle">replica in-zone or multi-AZ</text><rect class="box" x="270" y="140" width="470" height="100" rx="7"/><text x="505.0" y="194.0" text-anchor="middle"></text><text x="505" y="163" text-anchor="middle">Redis Cloud · Pro · Active-Active</text><rect class="rd" x="290" y="178" width="190" height="46" rx="7"/><text x="385.0" y="198.0" text-anchor="middle">copy in region A</text><text class="sm" x="385.0" y="214.0" text-anchor="middle">read + write</text><rect class="rd" x="530" y="178" width="190" height="46" rx="7"/><text x="625.0" y="198.0" text-anchor="middle">copy in region B</text><text class="sm" x="625.0" y="214.0" text-anchor="middle">read + write</text><line class="ln" x1="480" y1="201" x2="528" y2="201"/><polygon class="hd" points="528.0,201.0 521.7,204.0 521.7,198.0"/><polygon class="hd" points="480.0,201.0 486.3,198.0 486.3,204.0"/><text class="sm" x="504.0" y="195.0" text-anchor="middle">CRDT sync</text><line class="ln" x1="180" y1="70" x2="288" y2="80"/><polygon class="hd" points="288.0,80.0 281.4,82.5 282.0,76.4"/><line class="ln" x1="180" y1="190" x2="288" y2="200"/><polygon class="hd" points="288.0,200.0 281.4,202.5 282.0,196.4"/></svg></div>

| 강한 이유 | 근거 |
|---|---|
| 몇 초 만에 DB, 모듈 포함 | 양식 제출 몇 초 뒤 무료 DB 준비, Search와 JSON 사용 가능([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| 첫날부터 자동화 | REST API가 무료 플랜에서도 동작([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| 모든 리전에서 쓰기(Pro) | 여기서는 설계만. 문서의 표현: "Active-Active databases allow read and write operations in each copy", CRDT로 동기화 |

**주의:** 무료 플랜은 시험용이다. 30 MB, 커넥션 30개, TLS 없음(API가 `enableTls`를 거절). 2026-11-07 콘솔에서 읽은 가격: Essentials 월 $5부터, Pro 월 $200부터.

문서: [Redis Cloud](https://redis.io/docs/latest/operate/rc/), [High availability](https://redis.io/docs/latest/operate/rc/databases/configuration/high-availability/), [Active-Active](https://redis.io/docs/latest/operate/rc/databases/active-active/).

### 5. AI 에이전트의 컨텍스트 계층: Redis Iris

Iris는 에이전트 주위에 서비스를 두어 매 턴 컨텍스트를 다시 만들지 않게 한다. 문서의 표현: "Redis Iris is a production-ready context engine for AI agents", 그리고 "adds persistent memory", "answers recurring questions without a model call", 에이전트에게 "one MCP endpoint for the tools of any MCP server and your Redis data"를 주고 "routes each message". Agent Memory는 내가 가진 Redis DB에 데이터를 둔다.

<div class="arch" markdown="0"><svg viewBox="0 0 780 320" role="img" aria-label="Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database"><title>Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database</title><rect class="box" x="20" y="110" width="110" height="56" rx="7"/><text x="75.0" y="142.0" text-anchor="middle">User</text><rect class="box" x="180" y="100" width="170" height="76" rx="7"/><text x="265.0" y="135.0" text-anchor="middle">Agent app</text><text class="sm" x="265.0" y="151.0" text-anchor="middle">LLM + your code</text><line class="ln" x1="130" y1="138" x2="178" y2="138"/><polygon class="hd" points="178.0,138.0 171.7,141.0 171.7,135.0"/><rect class="rd" x="430" y="20" width="190" height="48" rx="7"/><text x="525.0" y="41.0" text-anchor="middle">Intent Router</text><text class="sm" x="525.0" y="57.0" text-anchor="middle">route before the LLM</text><line class="ln" x1="350" y1="138" x2="428" y2="44"/><polygon class="hd" points="428.0,44.0 426.3,50.8 421.6,46.9"/><rect class="rd" x="430" y="80" width="190" height="48" rx="7"/><text x="525.0" y="101.0" text-anchor="middle">Agent Memory</text><text class="sm" x="525.0" y="117.0" text-anchor="middle">remember · recall</text><line class="ln" x1="350" y1="138" x2="428" y2="104"/><polygon class="hd" points="428.0,104.0 423.4,109.3 421.0,103.7"/><rect class="rd" x="430" y="140" width="190" height="48" rx="7"/><text x="525.0" y="161.0" text-anchor="middle">Agent Playbooks</text><text class="sm" x="525.0" y="177.0" text-anchor="middle">approved answers</text><line class="ln" x1="350" y1="138" x2="428" y2="164"/><polygon class="hd" points="428.0,164.0 421.1,164.9 423.0,159.1"/><rect class="rd" x="430" y="200" width="190" height="48" rx="7"/><text x="525.0" y="221.0" text-anchor="middle">Context Gateway</text><text class="sm" x="525.0" y="237.0" text-anchor="middle">one MCP endpoint</text><line class="ln" x1="350" y1="138" x2="428" y2="224"/><polygon class="hd" points="428.0,224.0 421.5,221.4 426.0,217.3"/><rect class="rd" x="430" y="260" width="190" height="48" rx="7"/><text x="525.0" y="281.0" text-anchor="middle">Lens</text><text class="sm" x="525.0" y="297.0" text-anchor="middle">trace each turn</text><line class="ln" x1="350" y1="138" x2="428" y2="284"/><polygon class="hd" points="428.0,284.0 422.3,279.9 427.7,277.0"/><rect class="rd" x="660" y="100" width="100" height="70" rx="7"/><text x="710.0" y="132.0" text-anchor="middle">Redis DB</text><text class="sm" x="710.0" y="148.0" text-anchor="middle">JSON + Search</text><line class="ln dash" x1="620" y1="104" x2="658" y2="125"/><polygon class="hd" points="658.0,125.0 651.0,124.6 654.0,119.3"/><line class="ln dash" x1="620" y1="216" x2="658" y2="150"/><polygon class="hd" points="658.0,150.0 657.5,157.0 652.2,153.9"/><rect class="box" x="660" y="230" width="100" height="56" rx="7"/><text x="710.0" y="255.0" text-anchor="middle">MCP servers</text><text class="sm" x="710.0" y="271.0" text-anchor="middle">your tools</text><line class="ln dash" x1="620" y1="232" x2="658" y2="252"/><polygon class="hd" points="658.0,252.0 651.0,251.8 653.8,246.4"/></svg></div>

| 강한 이유 | 근거 |
|---|---|
| 스스로 쌓이는 기억 | 두 턴 대화의 사실이 약 15초 뒤 추출됐다([Iris]({{ '/iris/' | relative_url }})) |
| 데이터가 내 DB에 남는다 | Agent Memory가 무료 DB에 JSON 문서와 Search 인덱스 4개를 썼다([Iris]({{ '/iris/' | relative_url }})) |
| 제품·리소스별 키 범위 | read 키는 회상은 되고 쓰기는 403([Iris]({{ '/iris/' | relative_url }})) |
| 더 싼 턴 | Intent Router와 Agent Playbooks가 모델 호출 전에 답하거나 라우팅: 여기서는 설계만 |

**주의:** 서비스가 도는 곳. Agent Memory 엔드포인트는 us-east-1, DB는 서울이었고, 한국에서 회상은 중앙값 611 ms였다. 메시지 사용량은 콘솔 어디에도 보이지 않았다. Intent Router, Playbooks, Context Gateway, Lens는 아직 실행하지 않았다.

문서: [Redis Iris](https://redis.io/docs/latest/develop/ai/context-engine/), [Agent Memory](https://redis.io/docs/latest/operate/iris/agent-memory/), [Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/), [Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/), [Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/), [Lens](https://redis.io/docs/latest/operate/iris/lens/).

### 6. 데이터 옆의 검색과 벡터

레코드, 보조 인덱스, 임베딩이 같은 Redis DB에 있어 질의가 다른 시스템으로 건너가지 않는다.

<div class="arch" markdown="0"><svg viewBox="0 0 760 215" role="img" aria-label="Search and vectors in the same Redis database as the records"><title>Search and vectors in the same Redis database as the records</title><rect class="box" x="20" y="80" width="150" height="60" rx="7"/><text x="95.0" y="114.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="420" height="180" rx="7"/><text x="510.0" y="114.0" text-anchor="middle"></text><text x="510" y="44" text-anchor="middle">one Redis 8 database</text><rect class="box" x="320" y="60" width="170" height="52" rx="7"/><text x="405.0" y="83.0" text-anchor="middle">Hashes / JSON</text><text class="sm" x="405.0" y="99.0" text-anchor="middle">the records</text><rect class="box" x="530" y="60" width="170" height="52" rx="7"/><text x="615.0" y="83.0" text-anchor="middle">Search index</text><text class="sm" x="615.0" y="99.0" text-anchor="middle">text · numeric · vector</text><rect class="box" x="320" y="128" width="380" height="52" rx="7"/><text x="510.0" y="151.0" text-anchor="middle">Vector set (beta)</text><text class="sm" x="510.0" y="167.0" text-anchor="middle">VADD · VSIM, no index to define</text><line class="ln" x1="490" y1="86" x2="528" y2="86"/><polygon class="hd" points="528.0,86.0 521.7,89.0 521.7,83.0"/><line class="ln" x1="170" y1="110" x2="298" y2="110"/><polygon class="hd" points="298.0,110.0 291.7,113.0 291.7,107.0"/><text class="sm" x="234.0" y="104.0" text-anchor="middle">FT.SEARCH / VSIM</text></svg></div>

| 강한 이유 | 근거 |
|---|---|
| 내장, 설정 없음 | Search, JSON, 벡터 셋이 기본 Redis 8 이미지에서 실린다([Setup]({{ '/setup/' | relative_url }})) |
| 텍스트·숫자·벡터를 한 질의 언어로 | 해시 위 `FT.CREATE`, 숫자 범위, 벡터 인덱스 확인이 Redis 8.10.3에서 돌았다([Compare]({{ '/compare/' | relative_url }})) |
| 내장 벡터 자료형 | `VADD`, `VSIM`은 인덱스를 정의하지 않아도 동작 |

**주의:** 벡터 셋은 베타다. 규모에서의 정확도와 속도는 여기서 재지 않았다. 로컬 Search 실습은 아직 계획 단계다.

문서: [Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/).

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

**Redis 在系统中的位置，以及它为何适合那里。** 共六种布局，从数据库前面的缓存到 AI agent 的上下文层。每种布局都有一张图，说明 Redis 所处的位置、它在那里的优势（本站有测量数据的则附上）、需要注意的事项，以及官方文档及其关键句引文。本站尚未端到端运行过的布局标注为设计。

| 布局 | Redis 的角色 | 在本站的运行情况 |
|---|---|---|
| 数据库前面的缓存 | 热点读取的快速副本 | 部分：吞吐量与限制 |
| 具备高可用的热状态 | 会话、计数器、队列的系统记录 | 是：持久化、副本、Sentinel |
| 用 Redis Cluster 横向扩展 | 按哈希槽把数据分到各分片 | 是：六节点集群、槽迁移 |
| 托管于 Redis Cloud | 一项服务，从单个数据库到 Active-Active | 仅免费方案；Active-Active 为设计 |
| AI agent 的上下文层 (Iris) | 围绕 LLM 的记忆、路由、已批准的答案和工具 | Agent Memory 已运行；其他服务尚未 |
| 数据旁边的搜索与向量 | 索引和记录在同一处 | 仅做过探测 |

### 1. 数据库前面的缓存

应用先向 Redis 查询；未命中时读取数据库，并把结果连同 TTL 写入 Redis。Redis 保存一份副本，数据库仍是事实来源。

<div class="arch" markdown="0"><svg viewBox="0 0 760 250" role="img" aria-label="Cache-aside: the application reads Redis first and fills it from the database on a miss"><title>Cache-aside: the application reads Redis first and fills it from the database on a miss</title><rect class="box" x="20" y="95" width="130" height="60" rx="7"/><text x="85.0" y="129.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="170" height="60" rx="7"/><text x="385.0" y="47.0" text-anchor="middle">Redis</text><text class="sm" x="385.0" y="63.0" text-anchor="middle">cache, TTL + eviction</text><rect class="box" x="300" y="170" width="170" height="60" rx="7"/><text x="385.0" y="197.0" text-anchor="middle">Primary database</text><text class="sm" x="385.0" y="213.0" text-anchor="middle">source of truth</text><line class="ln" x1="150" y1="105" x2="298" y2="38"/><polygon class="hd" points="298.0,38.0 293.5,43.4 291.0,37.8"/><text class="sm" x="224.0" y="65.5" text-anchor="middle">1 GET</text><line class="ln" x1="150" y1="145" x2="298" y2="205"/><polygon class="hd" points="298.0,205.0 291.0,205.5 293.3,199.8"/><text class="sm" x="224.0" y="169.0" text-anchor="middle">2 on miss: read</text><line class="ln dash" x1="150" y1="125" x2="298" y2="66"/><polygon class="hd" points="298.0,66.0 293.3,71.2 291.0,65.5"/><text class="sm" x="246" y="112" text-anchor="middle">3 SET with TTL</text><rect class="box" x="560" y="95" width="180" height="60" rx="7"/><text x="650.0" y="122.0" text-anchor="middle">Other app servers</text><text class="sm" x="650.0" y="138.0" text-anchor="middle">client-side cache</text><line class="ln dash" x1="470" y1="50" x2="558" y2="112"/><polygon class="hd" points="558.0,112.0 551.1,110.9 554.6,105.9"/><text class="sm" x="514.0" y="75.0" text-anchor="middle">invalidations</text></svg></div>

| 强在哪里 | 依据 |
|---|---|
| 读取来自内存，由单个事件循环处理 | 单节点默认配置下每秒 134,523–136,097 次 SET/GET；使用 `io-threads 8` 时为 498,753–520,472 ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 提供数据结构，而不只是字符串 | 支持字段级 TTL 的 hash、sorted set，官方镜像内置 JSON ([Setup]({{ '/setup/' | relative_url }})) |
| 客户端也可以缓存，并在需要丢弃时收到通知 | 服务器辅助的客户端缓存（见下方文档） |

**注意：** 失效处理是难点；文档写道："A problem with the above pattern is how to invalidate the information that the application is holding"。淘汰策略决定内存写满时的行为：在 `volatile-lru` 下，没有 TTL 的键永远不会被淘汰，写入会因 `OOM` 失败 ([Redis Cloud free database]({{ '/cloud/' | relative_url }}))。

文档：[Client-side caching](https://redis.io/docs/latest/develop/reference/client-side-caching/)、[Eviction](https://redis.io/docs/latest/develop/reference/eviction/)。

### 2. 具备高可用的热状态

会话、购物车、限流计数器和队列以系统记录的身份存放在 Redis 中。一个主节点写入 append-only 文件，两个副本跟随它，主节点故障时由三个 Sentinel 提升一个副本。

<div class="arch" markdown="0"><svg viewBox="0 0 700 290" role="img" aria-label="Primary with two replicas and three Sentinels for failover"><title>Primary with two replicas and three Sentinels for failover</title><rect class="box" x="20" y="100" width="130" height="56" rx="7"/><text x="85.0" y="132.0" text-anchor="middle">Application</text><rect class="rd" x="250" y="90" width="160" height="76" rx="7"/><text x="330.0" y="125.0" text-anchor="middle">Redis primary</text><text class="sm" x="330.0" y="141.0" text-anchor="middle">AOF everysec</text><rect class="rd" x="520" y="30" width="150" height="52" rx="7"/><text x="595.0" y="60.0" text-anchor="middle">Replica 1</text><rect class="rd" x="520" y="170" width="150" height="52" rx="7"/><text x="595.0" y="200.0" text-anchor="middle">Replica 2</text><line class="ln" x1="150" y1="128" x2="248" y2="128"/><polygon class="hd" points="248.0,128.0 241.7,131.0 241.7,125.0"/><text class="sm" x="199.0" y="122.0" text-anchor="middle">writes, WAIT</text><line class="ln" x1="410" y1="112" x2="518" y2="60"/><polygon class="hd" points="518.0,60.0 513.6,65.5 511.0,60.0"/><text class="sm" x="464.0" y="80.0" text-anchor="middle">replication</text><line class="ln" x1="410" y1="145" x2="518" y2="192"/><polygon class="hd" points="518.0,192.0 511.0,192.3 513.4,186.7"/><rect class="box" x="250" y="236" width="420" height="40" rx="7"/><text x="460.0" y="260.0" text-anchor="middle">Sentinel ×3  ·  quorum 2  ·  promotes a replica on failure</text><line class="ln dash" x1="330" y1="236" x2="330" y2="168"/><polygon class="hd" points="330.0,168.0 333.0,174.3 327.0,174.3"/></svg></div>

| 强在哪里 | 依据 |
|---|---|
| 不牺牲速度的持久性 | AOF `everysec` 97,087 req/s，p99 0.255 ms；`always` 17,203 req/s ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 快速、自动的故障转移 | 主节点停止后，4,402 ms 内选出新的 master；旧主节点以副本身份重新加入 |
| 无需停机的时间点备份 | `BACKUP START`/`SEAL` (8.10) 使用 `preload-file` 恢复到新服务器 |

**注意：** 复制是异步的。文档写道："WAIT does not make Redis a strongly consistent store"，而且 `WAIT` 只统计调用连接自己写入的确认数。快照采用写时复制：在覆盖写入下，214 MB 的数据集产生了 252 MB 的写时复制开销。请给 Sentinel 提供始终可解析的地址：监视容器名称会让同一次故障转移拉长到 284 s。

文档：[Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)、[Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)、[Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)、[WAIT](https://redis.io/docs/latest/commands/wait/)。

### 3. 用 Redis Cluster 横向扩展

当单个节点的内存或 CPU 不够用时，Redis Cluster 把键空间划分为 16,384 个哈希槽，分布在多个主节点上，每个主节点带有副本。客户端获取槽映射后直接与正确的节点通信。

<div class="arch" markdown="0"><svg viewBox="0 0 760 260" role="img" aria-label="Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot"><title>Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot</title><rect class="box" x="20" y="105" width="150" height="60" rx="7"/><text x="95.0" y="132.0" text-anchor="middle">Cluster-aware client</text><text class="sm" x="95.0" y="148.0" text-anchor="middle">caches slot map</text><rect class="rd" x="250" y="40" width="150" height="56" rx="7"/><text x="325.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="325.0" y="81.0" text-anchor="middle">slots 0–5460</text><rect class="rd" x="250" y="165" width="150" height="50" rx="7"/><text x="325.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="325" y1="96" x2="325" y2="163"/><polygon class="hd" points="325.0,163.0 322.0,156.7 328.0,156.7"/><rect class="rd" x="420" y="40" width="150" height="56" rx="7"/><text x="495.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="495.0" y="81.0" text-anchor="middle">5461–10922</text><rect class="rd" x="420" y="165" width="150" height="50" rx="7"/><text x="495.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="495" y1="96" x2="495" y2="163"/><polygon class="hd" points="495.0,163.0 492.0,156.7 498.0,156.7"/><rect class="rd" x="590" y="40" width="150" height="56" rx="7"/><text x="665.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="665.0" y="81.0" text-anchor="middle">10923–16383</text><rect class="rd" x="590" y="165" width="150" height="50" rx="7"/><text x="665.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="665" y1="96" x2="665" y2="163"/><polygon class="hd" points="665.0,163.0 662.0,156.7 668.0,156.7"/><line class="ln" x1="170" y1="125" x2="248" y2="70"/><polygon class="hd" points="248.0,70.0 244.6,76.1 241.1,71.1"/><text class="sm" x="209.0" y="91.5" text-anchor="middle">key → CRC16 mod 16384</text><text class="sm" x="495" y="245" text-anchor="middle">CLUSTER MIGRATION moves slot ranges between primaries atomically</text></svg></div>

| 强在哪里 | 依据 |
|---|---|
| 重新分片时不停写入 | 在约 200,000 次写入/秒的负载下，`CLUSTER MIGRATION IMPORT 0 999` 以 `write_pause_ms 0` 在 44 ms 内迁移了 1,000 个槽 ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 路由可预测 | `HASH_SLOT = CRC16(key) mod 16384`；访问错误的节点时，它会用 `MOVED` 返回正确的节点 |

**注意：** 多键命令必须位于同一个槽。`MSET user:1 a user:2 b` 会返回 `CROSSSLOT`；使用共同的哈希标签（`{user:1}:cart`、`{user:1}:orders`）可让相关的键保持在一起。ElastiCache Serverless 的行为相同 ([Compare]({{ '/compare/' | relative_url }}))。规范写道："Each master node in a cluster handles a subset of the 16384 hash slots"。

文档：[Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)、[Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)、[CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/)。

### 4. 托管于 Redis Cloud

同一个引擎，以服务形式提供。Essentials 是运行在共享基础设施上的单个数据库，可选复制；Pro 是独享的，可容纳多个数据库，并支持在多个区域建立都能接受写入的 Active-Active 副本。

<div class="arch" markdown="0"><svg viewBox="0 0 760 255" role="img" aria-label="Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro"><title>Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro</title><rect class="box" x="20" y="40" width="160" height="60" rx="7"/><text x="100.0" y="74.0" text-anchor="middle">App, region A</text><rect class="box" x="20" y="160" width="160" height="60" rx="7"/><text x="100.0" y="194.0" text-anchor="middle">App, region B</text><rect class="box" x="270" y="20" width="230" height="100" rx="7"/><text x="385.0" y="74.0" text-anchor="middle"></text><text x="385" y="44" text-anchor="middle">Redis Cloud · Essentials</text><rect class="rd" x="290" y="58" width="190" height="46" rx="7"/><text x="385.0" y="78.0" text-anchor="middle">one database</text><text class="sm" x="385.0" y="94.0" text-anchor="middle">replica in-zone or multi-AZ</text><rect class="box" x="270" y="140" width="470" height="100" rx="7"/><text x="505.0" y="194.0" text-anchor="middle"></text><text x="505" y="163" text-anchor="middle">Redis Cloud · Pro · Active-Active</text><rect class="rd" x="290" y="178" width="190" height="46" rx="7"/><text x="385.0" y="198.0" text-anchor="middle">copy in region A</text><text class="sm" x="385.0" y="214.0" text-anchor="middle">read + write</text><rect class="rd" x="530" y="178" width="190" height="46" rx="7"/><text x="625.0" y="198.0" text-anchor="middle">copy in region B</text><text class="sm" x="625.0" y="214.0" text-anchor="middle">read + write</text><line class="ln" x1="480" y1="201" x2="528" y2="201"/><polygon class="hd" points="528.0,201.0 521.7,204.0 521.7,198.0"/><polygon class="hd" points="480.0,201.0 486.3,198.0 486.3,204.0"/><text class="sm" x="504.0" y="195.0" text-anchor="middle">CRDT sync</text><line class="ln" x1="180" y1="70" x2="288" y2="80"/><polygon class="hd" points="288.0,80.0 281.4,82.5 282.0,76.4"/><line class="ln" x1="180" y1="190" x2="288" y2="200"/><polygon class="hd" points="288.0,200.0 281.4,202.5 282.0,196.4"/></svg></div>

| 强在哪里 | 依据 |
|---|---|
| 数秒内得到数据库，模块已包含 | 提交表单几秒后免费数据库即可使用，Search 和 JSON 可用 ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| 从第一天起就能自动化 | REST API 在免费方案中可用 ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| 每个区域都能写入 (Pro) | 此处仅为设计；文档写道："Active-Active databases allow read and write operations in each copy"，由 CRDT 进行同步 |

**注意：** 免费方案用于试用：30 MB、30 个连接、不支持 TLS（API 拒绝 `enableTls`）。2026-11-07 在控制台读到的价格：Essentials 起价每月 $5，Pro 起价每月 $200。

文档：[Redis Cloud](https://redis.io/docs/latest/operate/rc/)、[High availability](https://redis.io/docs/latest/operate/rc/databases/configuration/high-availability/)、[Active-Active](https://redis.io/docs/latest/operate/rc/databases/active-active/)。

### 5. AI agent 的上下文层：Redis Iris

Iris 在 agent 周围提供一组服务，使它不必每一轮都重建上下文。文档写道："Redis Iris is a production-ready context engine for AI agents"，它 "adds persistent memory"，"answers recurring questions without a model call"，为 agent 提供 "one MCP endpoint for the tools of any MCP server and your Redis data"，并 "routes each message"。Agent Memory 把数据保存在你自己的 Redis 数据库中。

<div class="arch" markdown="0"><svg viewBox="0 0 780 320" role="img" aria-label="Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database"><title>Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database</title><rect class="box" x="20" y="110" width="110" height="56" rx="7"/><text x="75.0" y="142.0" text-anchor="middle">User</text><rect class="box" x="180" y="100" width="170" height="76" rx="7"/><text x="265.0" y="135.0" text-anchor="middle">Agent app</text><text class="sm" x="265.0" y="151.0" text-anchor="middle">LLM + your code</text><line class="ln" x1="130" y1="138" x2="178" y2="138"/><polygon class="hd" points="178.0,138.0 171.7,141.0 171.7,135.0"/><rect class="rd" x="430" y="20" width="190" height="48" rx="7"/><text x="525.0" y="41.0" text-anchor="middle">Intent Router</text><text class="sm" x="525.0" y="57.0" text-anchor="middle">route before the LLM</text><line class="ln" x1="350" y1="138" x2="428" y2="44"/><polygon class="hd" points="428.0,44.0 426.3,50.8 421.6,46.9"/><rect class="rd" x="430" y="80" width="190" height="48" rx="7"/><text x="525.0" y="101.0" text-anchor="middle">Agent Memory</text><text class="sm" x="525.0" y="117.0" text-anchor="middle">remember · recall</text><line class="ln" x1="350" y1="138" x2="428" y2="104"/><polygon class="hd" points="428.0,104.0 423.4,109.3 421.0,103.7"/><rect class="rd" x="430" y="140" width="190" height="48" rx="7"/><text x="525.0" y="161.0" text-anchor="middle">Agent Playbooks</text><text class="sm" x="525.0" y="177.0" text-anchor="middle">approved answers</text><line class="ln" x1="350" y1="138" x2="428" y2="164"/><polygon class="hd" points="428.0,164.0 421.1,164.9 423.0,159.1"/><rect class="rd" x="430" y="200" width="190" height="48" rx="7"/><text x="525.0" y="221.0" text-anchor="middle">Context Gateway</text><text class="sm" x="525.0" y="237.0" text-anchor="middle">one MCP endpoint</text><line class="ln" x1="350" y1="138" x2="428" y2="224"/><polygon class="hd" points="428.0,224.0 421.5,221.4 426.0,217.3"/><rect class="rd" x="430" y="260" width="190" height="48" rx="7"/><text x="525.0" y="281.0" text-anchor="middle">Lens</text><text class="sm" x="525.0" y="297.0" text-anchor="middle">trace each turn</text><line class="ln" x1="350" y1="138" x2="428" y2="284"/><polygon class="hd" points="428.0,284.0 422.3,279.9 427.7,277.0"/><rect class="rd" x="660" y="100" width="100" height="70" rx="7"/><text x="710.0" y="132.0" text-anchor="middle">Redis DB</text><text class="sm" x="710.0" y="148.0" text-anchor="middle">JSON + Search</text><line class="ln dash" x1="620" y1="104" x2="658" y2="125"/><polygon class="hd" points="658.0,125.0 651.0,124.6 654.0,119.3"/><line class="ln dash" x1="620" y1="216" x2="658" y2="150"/><polygon class="hd" points="658.0,150.0 657.5,157.0 652.2,153.9"/><rect class="box" x="660" y="230" width="100" height="56" rx="7"/><text x="710.0" y="255.0" text-anchor="middle">MCP servers</text><text class="sm" x="710.0" y="271.0" text-anchor="middle">your tools</text><line class="ln dash" x1="620" y1="232" x2="658" y2="252"/><polygon class="hd" points="658.0,252.0 651.0,251.8 653.8,246.4"/></svg></div>

| 强在哪里 | 依据 |
|---|---|
| 自行构建的记忆 | 一段两轮对话中的事实在约 15 s 后被提取出来 ([Iris]({{ '/iris/' | relative_url }})) |
| 数据留在你自己的数据库中 | Agent Memory 向免费数据库写入了 JSON 文档和四个 Search 索引 ([Iris]({{ '/iris/' | relative_url }})) |
| 按产品和资源划分范围的密钥 | 读取密钥可以召回，但写入时收到 403 ([Iris]({{ '/iris/' | relative_url }})) |
| 更省的对话轮次 | Intent Router 和 Agent Playbooks 在调用模型之前先回答或路由：此处仅为设计 |

**注意：** 服务运行的位置：Agent Memory 端点在 us-east-1，而数据库在首尔，从韩国召回的中位数为 611 ms。控制台中任何地方都看不到消息计量。Intent Router、Playbooks、Context Gateway 和 Lens 尚未运行过。

文档：[Redis Iris](https://redis.io/docs/latest/develop/ai/context-engine/)、[Agent Memory](https://redis.io/docs/latest/operate/iris/agent-memory/)、[Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/)、[Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/)、[Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/)、[Lens](https://redis.io/docs/latest/operate/iris/lens/)。

### 6. 数据旁边的搜索与向量

记录、它们的二级索引和嵌入向量都存放在同一个 Redis 数据库中，因此查询不必跨到另一个系统。

<div class="arch" markdown="0"><svg viewBox="0 0 760 215" role="img" aria-label="Search and vectors in the same Redis database as the records"><title>Search and vectors in the same Redis database as the records</title><rect class="box" x="20" y="80" width="150" height="60" rx="7"/><text x="95.0" y="114.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="420" height="180" rx="7"/><text x="510.0" y="114.0" text-anchor="middle"></text><text x="510" y="44" text-anchor="middle">one Redis 8 database</text><rect class="box" x="320" y="60" width="170" height="52" rx="7"/><text x="405.0" y="83.0" text-anchor="middle">Hashes / JSON</text><text class="sm" x="405.0" y="99.0" text-anchor="middle">the records</text><rect class="box" x="530" y="60" width="170" height="52" rx="7"/><text x="615.0" y="83.0" text-anchor="middle">Search index</text><text class="sm" x="615.0" y="99.0" text-anchor="middle">text · numeric · vector</text><rect class="box" x="320" y="128" width="380" height="52" rx="7"/><text x="510.0" y="151.0" text-anchor="middle">Vector set (beta)</text><text class="sm" x="510.0" y="167.0" text-anchor="middle">VADD · VSIM, no index to define</text><line class="ln" x1="490" y1="86" x2="528" y2="86"/><polygon class="hd" points="528.0,86.0 521.7,89.0 521.7,83.0"/><line class="ln" x1="170" y1="110" x2="298" y2="110"/><polygon class="hd" points="298.0,110.0 291.7,113.0 291.7,107.0"/><text class="sm" x="234.0" y="104.0" text-anchor="middle">FT.SEARCH / VSIM</text></svg></div>

| 强在哪里 | 依据 |
|---|---|
| 内置，无需配置 | Search、JSON 和 vector set 随官方 Redis 8 镜像一同加载 ([Setup]({{ '/setup/' | relative_url }})) |
| 文本、数字和向量使用同一种查询语言 | 基于 hash 的 `FT.CREATE`、数值范围和向量索引的探测已在 Redis 8.10.3 上运行 ([Compare]({{ '/compare/' | relative_url }})) |
| 原生向量类型 | `VADD` 和 `VSIM` 无需定义索引即可使用 |

**注意：** vector set 仍处于 beta 阶段。大规模下的相关性和速度在此未作测量；本地 Search 实验仍在计划中。

文档：[Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/)、[Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/)。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

**Redis がシステムのどこに入り、なぜそこで強いのか。** データベースの前段のキャッシュから AI エージェントのコンテキスト層まで、6 つの構成を取り上げます。各構成には図があり、Redis の位置、そこでの強み（このサイトに測定がある場合はその裏付け付き）、注意点、そして公式ドキュメントとその要点の引用を載せています。このサイトでエンドツーエンドでは動かしていない構成は、設計として明記しています。

| 構成 | Redis の役割 | このサイトでの実施 |
|---|---|---|
| データベース前段のキャッシュ | 頻繁に読まれるデータの高速なコピー | 一部：スループットと制限 |
| 高可用性を備えたホットステート | セッション、カウンター、キューの正本 | 実施済み：永続化、レプリカ、Sentinel |
| Redis Cluster でスケールアウト | ハッシュスロットでシャードに分割したデータ | 実施済み：6 ノードクラスター、スロット移行 |
| Redis Cloud でのマネージド運用 | 1 つのデータベースから Active-Active までのサービス | 無料プランのみ。Active-Active は設計 |
| AI エージェントのコンテキスト層 (Iris) | LLM を取り巻くメモリ、ルーティング、承認済みの回答とツール | Agent Memory は実施済み。他のサービスは未実施 |
| データの隣での検索とベクトル | インデックスとレコードを同じ場所に置く | 簡易検証のみ |

### 1. データベース前段のキャッシュ

アプリケーションはまず Redis に問い合わせ、ミスしたときはデータベースを読み、結果を TTL 付きで Redis に書き込みます。Redis はコピーを保持し、正本はデータベースのままです。

<div class="arch" markdown="0"><svg viewBox="0 0 760 250" role="img" aria-label="Cache-aside: the application reads Redis first and fills it from the database on a miss"><title>Cache-aside: the application reads Redis first and fills it from the database on a miss</title><rect class="box" x="20" y="95" width="130" height="60" rx="7"/><text x="85.0" y="129.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="170" height="60" rx="7"/><text x="385.0" y="47.0" text-anchor="middle">Redis</text><text class="sm" x="385.0" y="63.0" text-anchor="middle">cache, TTL + eviction</text><rect class="box" x="300" y="170" width="170" height="60" rx="7"/><text x="385.0" y="197.0" text-anchor="middle">Primary database</text><text class="sm" x="385.0" y="213.0" text-anchor="middle">source of truth</text><line class="ln" x1="150" y1="105" x2="298" y2="38"/><polygon class="hd" points="298.0,38.0 293.5,43.4 291.0,37.8"/><text class="sm" x="224.0" y="65.5" text-anchor="middle">1 GET</text><line class="ln" x1="150" y1="145" x2="298" y2="205"/><polygon class="hd" points="298.0,205.0 291.0,205.5 293.3,199.8"/><text class="sm" x="224.0" y="169.0" text-anchor="middle">2 on miss: read</text><line class="ln dash" x1="150" y1="125" x2="298" y2="66"/><polygon class="hd" points="298.0,66.0 293.3,71.2 291.0,65.5"/><text class="sm" x="246" y="112" text-anchor="middle">3 SET with TTL</text><rect class="box" x="560" y="95" width="180" height="60" rx="7"/><text x="650.0" y="122.0" text-anchor="middle">Other app servers</text><text class="sm" x="650.0" y="138.0" text-anchor="middle">client-side cache</text><line class="ln dash" x1="470" y1="50" x2="558" y2="112"/><polygon class="hd" points="558.0,112.0 551.1,110.9 554.6,105.9"/><text class="sm" x="514.0" y="75.0" text-anchor="middle">invalidations</text></svg></div>

| 強みの理由 | 根拠 |
|---|---|
| 読み取りは 1 つのイベントループ上でメモリから行われる | 単一ノード・デフォルト設定で毎秒 134,523–136,097 の SET/GET。`io-threads 8` では 498,753–520,472 ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 文字列だけでなくデータ構造がある | フィールド単位の TTL を持つハッシュ、ソート済みセット、標準イメージに含まれる JSON ([Setup]({{ '/setup/' | relative_url }})) |
| クライアント側でもキャッシュでき、破棄のタイミングを通知してもらえる | サーバー支援のクライアントサイドキャッシュ（下記ドキュメント） |

**注意点:** 無効化が難しい部分です。ドキュメントには次のようにあります。"A problem with the above pattern is how to invalidate the information that the application is holding"。メモリが満杯になったときの動作は退避ポリシーで決まります。`volatile-lru` では TTL のないキーは退避されず、書き込みは `OOM` で失敗します ([Redis Cloud free database]({{ '/cloud/' | relative_url }}))。

ドキュメント: [Client-side caching](https://redis.io/docs/latest/develop/reference/client-side-caching/)、[Eviction](https://redis.io/docs/latest/develop/reference/eviction/)。

### 2. 高可用性を備えたホットステート

セッション、カート、レート制限のカウンター、キューを、正本として Redis に置きます。プライマリが append-only ファイルを書き、2 台のレプリカがそれに追従し、プライマリ障害時には 3 台の Sentinel がレプリカを昇格させます。

<div class="arch" markdown="0"><svg viewBox="0 0 700 290" role="img" aria-label="Primary with two replicas and three Sentinels for failover"><title>Primary with two replicas and three Sentinels for failover</title><rect class="box" x="20" y="100" width="130" height="56" rx="7"/><text x="85.0" y="132.0" text-anchor="middle">Application</text><rect class="rd" x="250" y="90" width="160" height="76" rx="7"/><text x="330.0" y="125.0" text-anchor="middle">Redis primary</text><text class="sm" x="330.0" y="141.0" text-anchor="middle">AOF everysec</text><rect class="rd" x="520" y="30" width="150" height="52" rx="7"/><text x="595.0" y="60.0" text-anchor="middle">Replica 1</text><rect class="rd" x="520" y="170" width="150" height="52" rx="7"/><text x="595.0" y="200.0" text-anchor="middle">Replica 2</text><line class="ln" x1="150" y1="128" x2="248" y2="128"/><polygon class="hd" points="248.0,128.0 241.7,131.0 241.7,125.0"/><text class="sm" x="199.0" y="122.0" text-anchor="middle">writes, WAIT</text><line class="ln" x1="410" y1="112" x2="518" y2="60"/><polygon class="hd" points="518.0,60.0 513.6,65.5 511.0,60.0"/><text class="sm" x="464.0" y="80.0" text-anchor="middle">replication</text><line class="ln" x1="410" y1="145" x2="518" y2="192"/><polygon class="hd" points="518.0,192.0 511.0,192.3 513.4,186.7"/><rect class="box" x="250" y="236" width="420" height="40" rx="7"/><text x="460.0" y="260.0" text-anchor="middle">Sentinel ×3  ·  quorum 2  ·  promotes a replica on failure</text><line class="ln dash" x1="330" y1="236" x2="330" y2="168"/><polygon class="hd" points="330.0,168.0 333.0,174.3 327.0,174.3"/></svg></div>

| 強みの理由 | 根拠 |
|---|---|
| 速度を落とさずに耐久性を確保 | AOF `everysec` は 97,087 req/s、p99 0.255 ms。`always` は 17,203 req/s ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 高速で自動的なフェイルオーバー | プライマリを停止後、4,402 ms で新しいマスターを特定。旧プライマリはレプリカとして再参加 |
| 停止なしのポイントインタイムバックアップ | `BACKUP START`/`SEAL` (8.10) を `preload-file` で新しいサーバーに復元 |

**注意点:** レプリケーションは非同期です。ドキュメントには次のようにあります。"WAIT does not make Redis a strongly consistent store"。また `WAIT` は、呼び出した接続自身の書き込みに対する確認応答だけを数えます。スナップショットは書き込み時にメモリをコピーします。上書きが続く状況で、214 MB のデータセットに対し 252 MB のコピーオンライトが発生しました。名前解決が安定したアドレスを Sentinel に渡してください。コンテナ名を監視させると、同じフェイルオーバーが 284 s に延びました。

ドキュメント: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)、[Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)、[Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)、[WAIT](https://redis.io/docs/latest/commands/wait/)。

### 3. Redis Cluster でスケールアウト

1 ノードのメモリや CPU では足りなくなったとき、Redis Cluster はキー空間を 16,384 個のハッシュスロットに分割して複数のプライマリに配置し、それぞれにレプリカを付けます。クライアントはスロットマップを取得し、適切なノードと直接通信します。

<div class="arch" markdown="0"><svg viewBox="0 0 760 260" role="img" aria-label="Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot"><title>Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot</title><rect class="box" x="20" y="105" width="150" height="60" rx="7"/><text x="95.0" y="132.0" text-anchor="middle">Cluster-aware client</text><text class="sm" x="95.0" y="148.0" text-anchor="middle">caches slot map</text><rect class="rd" x="250" y="40" width="150" height="56" rx="7"/><text x="325.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="325.0" y="81.0" text-anchor="middle">slots 0–5460</text><rect class="rd" x="250" y="165" width="150" height="50" rx="7"/><text x="325.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="325" y1="96" x2="325" y2="163"/><polygon class="hd" points="325.0,163.0 322.0,156.7 328.0,156.7"/><rect class="rd" x="420" y="40" width="150" height="56" rx="7"/><text x="495.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="495.0" y="81.0" text-anchor="middle">5461–10922</text><rect class="rd" x="420" y="165" width="150" height="50" rx="7"/><text x="495.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="495" y1="96" x2="495" y2="163"/><polygon class="hd" points="495.0,163.0 492.0,156.7 498.0,156.7"/><rect class="rd" x="590" y="40" width="150" height="56" rx="7"/><text x="665.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="665.0" y="81.0" text-anchor="middle">10923–16383</text><rect class="rd" x="590" y="165" width="150" height="50" rx="7"/><text x="665.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="665" y1="96" x2="665" y2="163"/><polygon class="hd" points="665.0,163.0 662.0,156.7 668.0,156.7"/><line class="ln" x1="170" y1="125" x2="248" y2="70"/><polygon class="hd" points="248.0,70.0 244.6,76.1 241.1,71.1"/><text class="sm" x="209.0" y="91.5" text-anchor="middle">key → CRC16 mod 16384</text><text class="sm" x="495" y="245" text-anchor="middle">CLUSTER MIGRATION moves slot ranges between primaries atomically</text></svg></div>

| 強みの理由 | 根拠 |
|---|---|
| 書き込みを止めずにリシャーディング | 約 200,000 writes/s の負荷下で、`CLUSTER MIGRATION IMPORT 0 999` が `write_pause_ms 0` で 1,000 スロットを 44 ms で移動 ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| 予測しやすいルーティング | `HASH_SLOT = CRC16(key) mod 16384`。誤ったノードは `MOVED` で正しいノードを返す |

**注意点:** 複数キーのコマンドは同じスロットに収まっている必要があります。`MSET user:1 a user:2 b` は `CROSSSLOT` を返します。共通のハッシュタグ（`{user:1}:cart`、`{user:1}:orders`）を使うと、関連するキーを同じ場所にまとめられます。ElastiCache Serverless も同じ動作です ([Compare]({{ '/compare/' | relative_url }}))。仕様には次のようにあります。"Each master node in a cluster handles a subset of the 16384 hash slots"。

ドキュメント: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)、[Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)、[CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/)。

### 4. Redis Cloud でのマネージド運用

同じエンジンをサービスとして利用します。Essentials は共有インフラ上の 1 つのデータベースで、レプリケーションは任意です。Pro は専有型で複数のデータベースを持て、複数リージョンのすべてが書き込みを受け付ける Active-Active コピーを追加できます。

<div class="arch" markdown="0"><svg viewBox="0 0 760 255" role="img" aria-label="Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro"><title>Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro</title><rect class="box" x="20" y="40" width="160" height="60" rx="7"/><text x="100.0" y="74.0" text-anchor="middle">App, region A</text><rect class="box" x="20" y="160" width="160" height="60" rx="7"/><text x="100.0" y="194.0" text-anchor="middle">App, region B</text><rect class="box" x="270" y="20" width="230" height="100" rx="7"/><text x="385.0" y="74.0" text-anchor="middle"></text><text x="385" y="44" text-anchor="middle">Redis Cloud · Essentials</text><rect class="rd" x="290" y="58" width="190" height="46" rx="7"/><text x="385.0" y="78.0" text-anchor="middle">one database</text><text class="sm" x="385.0" y="94.0" text-anchor="middle">replica in-zone or multi-AZ</text><rect class="box" x="270" y="140" width="470" height="100" rx="7"/><text x="505.0" y="194.0" text-anchor="middle"></text><text x="505" y="163" text-anchor="middle">Redis Cloud · Pro · Active-Active</text><rect class="rd" x="290" y="178" width="190" height="46" rx="7"/><text x="385.0" y="198.0" text-anchor="middle">copy in region A</text><text class="sm" x="385.0" y="214.0" text-anchor="middle">read + write</text><rect class="rd" x="530" y="178" width="190" height="46" rx="7"/><text x="625.0" y="198.0" text-anchor="middle">copy in region B</text><text class="sm" x="625.0" y="214.0" text-anchor="middle">read + write</text><line class="ln" x1="480" y1="201" x2="528" y2="201"/><polygon class="hd" points="528.0,201.0 521.7,204.0 521.7,198.0"/><polygon class="hd" points="480.0,201.0 486.3,198.0 486.3,204.0"/><text class="sm" x="504.0" y="195.0" text-anchor="middle">CRDT sync</text><line class="ln" x1="180" y1="70" x2="288" y2="80"/><polygon class="hd" points="288.0,80.0 281.4,82.5 282.0,76.4"/><line class="ln" x1="180" y1="190" x2="288" y2="200"/><polygon class="hd" points="288.0,200.0 281.4,202.5 282.0,196.4"/></svg></div>

| 強みの理由 | 根拠 |
|---|---|
| 数秒でデータベースが手に入り、モジュールも含まれる | フォーム送信の数秒後に無料データベースが利用可能、Search と JSON も使える ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| 初日から自動化できる | 無料プランでも REST API が使える ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| すべてのリージョンで書き込み (Pro) | ここでは設計のみ。ドキュメントには "Active-Active databases allow read and write operations in each copy" とあり、CRDT で同期される |

**注意点:** 無料プランは試用向けです。30 MB、30 接続、TLS なし（API は `enableTls` を拒否します）。2026-11-07 にコンソールで確認した価格は、Essentials が月額 $5 から、Pro が月額 $200 からです。

ドキュメント: [Redis Cloud](https://redis.io/docs/latest/operate/rc/)、[High availability](https://redis.io/docs/latest/operate/rc/databases/configuration/high-availability/)、[Active-Active](https://redis.io/docs/latest/operate/rc/databases/active-active/)。

### 5. AI エージェントのコンテキスト層：Redis Iris

Iris はエージェントの周りにサービスを置き、毎ターンでコンテキストを作り直さずに済むようにします。ドキュメントには次のようにあります。"Redis Iris is a production-ready context engine for AI agents" で、"adds persistent memory"、"answers recurring questions without a model call"、エージェントに "one MCP endpoint for the tools of any MCP server and your Redis data" を提供し、"routes each message"。Agent Memory はデータを自分が所有する Redis データベースに保存します。

<div class="arch" markdown="0"><svg viewBox="0 0 780 320" role="img" aria-label="Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database"><title>Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database</title><rect class="box" x="20" y="110" width="110" height="56" rx="7"/><text x="75.0" y="142.0" text-anchor="middle">User</text><rect class="box" x="180" y="100" width="170" height="76" rx="7"/><text x="265.0" y="135.0" text-anchor="middle">Agent app</text><text class="sm" x="265.0" y="151.0" text-anchor="middle">LLM + your code</text><line class="ln" x1="130" y1="138" x2="178" y2="138"/><polygon class="hd" points="178.0,138.0 171.7,141.0 171.7,135.0"/><rect class="rd" x="430" y="20" width="190" height="48" rx="7"/><text x="525.0" y="41.0" text-anchor="middle">Intent Router</text><text class="sm" x="525.0" y="57.0" text-anchor="middle">route before the LLM</text><line class="ln" x1="350" y1="138" x2="428" y2="44"/><polygon class="hd" points="428.0,44.0 426.3,50.8 421.6,46.9"/><rect class="rd" x="430" y="80" width="190" height="48" rx="7"/><text x="525.0" y="101.0" text-anchor="middle">Agent Memory</text><text class="sm" x="525.0" y="117.0" text-anchor="middle">remember · recall</text><line class="ln" x1="350" y1="138" x2="428" y2="104"/><polygon class="hd" points="428.0,104.0 423.4,109.3 421.0,103.7"/><rect class="rd" x="430" y="140" width="190" height="48" rx="7"/><text x="525.0" y="161.0" text-anchor="middle">Agent Playbooks</text><text class="sm" x="525.0" y="177.0" text-anchor="middle">approved answers</text><line class="ln" x1="350" y1="138" x2="428" y2="164"/><polygon class="hd" points="428.0,164.0 421.1,164.9 423.0,159.1"/><rect class="rd" x="430" y="200" width="190" height="48" rx="7"/><text x="525.0" y="221.0" text-anchor="middle">Context Gateway</text><text class="sm" x="525.0" y="237.0" text-anchor="middle">one MCP endpoint</text><line class="ln" x1="350" y1="138" x2="428" y2="224"/><polygon class="hd" points="428.0,224.0 421.5,221.4 426.0,217.3"/><rect class="rd" x="430" y="260" width="190" height="48" rx="7"/><text x="525.0" y="281.0" text-anchor="middle">Lens</text><text class="sm" x="525.0" y="297.0" text-anchor="middle">trace each turn</text><line class="ln" x1="350" y1="138" x2="428" y2="284"/><polygon class="hd" points="428.0,284.0 422.3,279.9 427.7,277.0"/><rect class="rd" x="660" y="100" width="100" height="70" rx="7"/><text x="710.0" y="132.0" text-anchor="middle">Redis DB</text><text class="sm" x="710.0" y="148.0" text-anchor="middle">JSON + Search</text><line class="ln dash" x1="620" y1="104" x2="658" y2="125"/><polygon class="hd" points="658.0,125.0 651.0,124.6 654.0,119.3"/><line class="ln dash" x1="620" y1="216" x2="658" y2="150"/><polygon class="hd" points="658.0,150.0 657.5,157.0 652.2,153.9"/><rect class="box" x="660" y="230" width="100" height="56" rx="7"/><text x="710.0" y="255.0" text-anchor="middle">MCP servers</text><text class="sm" x="710.0" y="271.0" text-anchor="middle">your tools</text><line class="ln dash" x1="620" y1="232" x2="658" y2="252"/><polygon class="hd" points="658.0,252.0 651.0,251.8 653.8,246.4"/></svg></div>

| 強みの理由 | 根拠 |
|---|---|
| 自動で育つメモリ | 2 ターンの会話に含まれる事実が約 15 s 後に抽出された ([Iris]({{ '/iris/' | relative_url }})) |
| データは自分のデータベースに残る | Agent Memory が無料データベースに JSON ドキュメントと 4 つの Search インデックスを書き込んだ ([Iris]({{ '/iris/' | relative_url }})) |
| プロダクトとリソースごとのスコープ付きキー | 読み取りキーでは想起できたが、書き込みは 403 だった ([Iris]({{ '/iris/' | relative_url }})) |
| ターンのコストを抑える | Intent Router と Agent Playbooks がモデル呼び出しの前に回答またはルーティングする：ここでは設計のみ |

**注意点:** サービスが動く場所です。Agent Memory のエンドポイントは us-east-1 にあり、データベースはソウルにあったため、韓国からの想起は中央値 611 ms でした。メッセージの従量計測はコンソールのどこにも表示されませんでした。Intent Router、Playbooks、Context Gateway、Lens はまだ実行していません。

ドキュメント: [Redis Iris](https://redis.io/docs/latest/develop/ai/context-engine/)、[Agent Memory](https://redis.io/docs/latest/operate/iris/agent-memory/)、[Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/)、[Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/)、[Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/)、[Lens](https://redis.io/docs/latest/operate/iris/lens/)。

### 6. データの隣での検索とベクトル

レコード、そのセカンダリインデックス、埋め込みベクトルが同じ Redis データベースにあるため、クエリが別のシステムをまたぐ必要がありません。

<div class="arch" markdown="0"><svg viewBox="0 0 760 215" role="img" aria-label="Search and vectors in the same Redis database as the records"><title>Search and vectors in the same Redis database as the records</title><rect class="box" x="20" y="80" width="150" height="60" rx="7"/><text x="95.0" y="114.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="420" height="180" rx="7"/><text x="510.0" y="114.0" text-anchor="middle"></text><text x="510" y="44" text-anchor="middle">one Redis 8 database</text><rect class="box" x="320" y="60" width="170" height="52" rx="7"/><text x="405.0" y="83.0" text-anchor="middle">Hashes / JSON</text><text class="sm" x="405.0" y="99.0" text-anchor="middle">the records</text><rect class="box" x="530" y="60" width="170" height="52" rx="7"/><text x="615.0" y="83.0" text-anchor="middle">Search index</text><text class="sm" x="615.0" y="99.0" text-anchor="middle">text · numeric · vector</text><rect class="box" x="320" y="128" width="380" height="52" rx="7"/><text x="510.0" y="151.0" text-anchor="middle">Vector set (beta)</text><text class="sm" x="510.0" y="167.0" text-anchor="middle">VADD · VSIM, no index to define</text><line class="ln" x1="490" y1="86" x2="528" y2="86"/><polygon class="hd" points="528.0,86.0 521.7,89.0 521.7,83.0"/><line class="ln" x1="170" y1="110" x2="298" y2="110"/><polygon class="hd" points="298.0,110.0 291.7,113.0 291.7,107.0"/><text class="sm" x="234.0" y="104.0" text-anchor="middle">FT.SEARCH / VSIM</text></svg></div>

| 強みの理由 | 根拠 |
|---|---|
| 組み込み済みで設定不要 | Search、JSON、ベクトルセットが標準の Redis 8 イメージで読み込まれる ([Setup]({{ '/setup/' | relative_url }})) |
| テキスト、数値、ベクトルに共通の 1 つのクエリ言語 | ハッシュに対する `FT.CREATE`、数値範囲、ベクトルインデックスの検証を Redis 8.10.3 で実行 ([Compare]({{ '/compare/' | relative_url }})) |
| ネイティブなベクトル型 | `VADD` と `VSIM` はインデックスを定義せずに使える |

**注意点:** ベクトルセットはベータ版です。大規模時の関連性と速度はここでは測定しておらず、ローカルの Search ラボは引き続き計画中です。

ドキュメント: [Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/)、[Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/)。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

**Redis อยู่ตรงไหนในระบบ และเหตุใดจึงเหมาะกับตำแหน่งนั้น** มีหกรูปแบบ ตั้งแต่แคชหน้าฐานข้อมูลไปจนถึงชั้นบริบทของ AI agent แต่ละรูปแบบมีแผนภาพ ตำแหน่งของ Redis จุดแข็งในรูปแบบนั้น (พร้อมผลการวัดบนไซต์นี้หากมี) สิ่งที่ต้องระวัง และเอกสารทางการพร้อมประโยคสำคัญที่อ้างอิงมา รูปแบบที่ไซต์นี้ยังไม่ได้รันตั้งแต่ต้นจนจบจะระบุว่าเป็นดีไซน์

| รูปแบบ | บทบาทของ Redis | ที่รันบนไซต์นี้ |
|---|---|---|
| แคชหน้าฐานข้อมูล | สำเนาที่เร็วของข้อมูลที่อ่านบ่อย | บางส่วน: throughput และขีดจำกัด |
| สถานะที่ใช้งานบ่อยพร้อม high availability | ระบบบันทึกหลักของเซสชัน ตัวนับ และคิว | ครบ: persistence, replica, Sentinel |
| ขยายแนวนอนด้วย Redis Cluster | ข้อมูลที่แบ่งไปยังแต่ละชาร์ดตาม hash slot | ครบ: คลัสเตอร์หกโหนด, การย้าย slot |
| ใช้แบบมีผู้ดูแลบน Redis Cloud | บริการ ตั้งแต่ฐานข้อมูลเดียวไปจนถึง Active-Active | เฉพาะแผนฟรี; Active-Active เป็นดีไซน์ |
| ชั้นบริบทสำหรับ AI agent (Iris) | หน่วยความจำ การกำหนดเส้นทาง คำตอบที่อนุมัติแล้ว และเครื่องมือรอบ LLM | Agent Memory รันแล้ว; บริการอื่นยังไม่ได้รัน |
| การค้นหาและเวกเตอร์ข้างข้อมูล | ดัชนีและเรกคอร์ดอยู่ที่เดียวกัน | ทดสอบเบื้องต้นเท่านั้น |

### 1. แคชหน้าฐานข้อมูล

แอปพลิเคชันถาม Redis ก่อน หากไม่พบจะอ่านจากฐานข้อมูลแล้วเขียนผลลัพธ์ลง Redis พร้อม TTL Redis เก็บสำเนาไว้ ส่วนฐานข้อมูลยังเป็นแหล่งข้อมูลจริง

<div class="arch" markdown="0"><svg viewBox="0 0 760 250" role="img" aria-label="Cache-aside: the application reads Redis first and fills it from the database on a miss"><title>Cache-aside: the application reads Redis first and fills it from the database on a miss</title><rect class="box" x="20" y="95" width="130" height="60" rx="7"/><text x="85.0" y="129.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="170" height="60" rx="7"/><text x="385.0" y="47.0" text-anchor="middle">Redis</text><text class="sm" x="385.0" y="63.0" text-anchor="middle">cache, TTL + eviction</text><rect class="box" x="300" y="170" width="170" height="60" rx="7"/><text x="385.0" y="197.0" text-anchor="middle">Primary database</text><text class="sm" x="385.0" y="213.0" text-anchor="middle">source of truth</text><line class="ln" x1="150" y1="105" x2="298" y2="38"/><polygon class="hd" points="298.0,38.0 293.5,43.4 291.0,37.8"/><text class="sm" x="224.0" y="65.5" text-anchor="middle">1 GET</text><line class="ln" x1="150" y1="145" x2="298" y2="205"/><polygon class="hd" points="298.0,205.0 291.0,205.5 293.3,199.8"/><text class="sm" x="224.0" y="169.0" text-anchor="middle">2 on miss: read</text><line class="ln dash" x1="150" y1="125" x2="298" y2="66"/><polygon class="hd" points="298.0,66.0 293.3,71.2 291.0,65.5"/><text class="sm" x="246" y="112" text-anchor="middle">3 SET with TTL</text><rect class="box" x="560" y="95" width="180" height="60" rx="7"/><text x="650.0" y="122.0" text-anchor="middle">Other app servers</text><text class="sm" x="650.0" y="138.0" text-anchor="middle">client-side cache</text><line class="ln dash" x1="470" y1="50" x2="558" y2="112"/><polygon class="hd" points="558.0,112.0 551.1,110.9 554.6,105.9"/><text class="sm" x="514.0" y="75.0" text-anchor="middle">invalidations</text></svg></div>

| จุดแข็ง | หลักฐาน |
|---|---|
| อ่านจากหน่วยความจำบน event loop เดียว | 134,523–136,097 SET/GET ต่อวินาทีบนโหนดเดียวด้วยค่าเริ่มต้น; 498,753–520,472 เมื่อใช้ `io-threads 8` ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| มีโครงสร้างข้อมูล ไม่ใช่แค่สตริง | hash ที่ตั้ง TTL ระดับฟิลด์ได้ sorted set และ JSON ในอิมเมจมาตรฐาน ([Setup]({{ '/setup/' | relative_url }})) |
| ฝั่งไคลเอนต์แคชได้ด้วย และได้รับแจ้งเมื่อต้องทิ้งแคช | client-side caching ที่เซิร์ฟเวอร์ช่วยดูแล (เอกสารด้านล่าง) |

**ข้อควรระวัง:** การทำให้แคชใช้ไม่ได้ (invalidation) เป็นส่วนที่ยาก เอกสารระบุว่า "A problem with the above pattern is how to invalidate the information that the application is holding" นโยบาย eviction กำหนดว่าจะเกิดอะไรขึ้นเมื่อหน่วยความจำเต็ม: ภายใต้ `volatile-lru` คีย์ที่ไม่มี TTL จะไม่ถูกลบออก และการเขียนจะล้มเหลวด้วย `OOM` ([Redis Cloud free database]({{ '/cloud/' | relative_url }}))

เอกสาร: [Client-side caching](https://redis.io/docs/latest/develop/reference/client-side-caching/), [Eviction](https://redis.io/docs/latest/develop/reference/eviction/)

### 2. สถานะที่ใช้งานบ่อยพร้อม high availability

เซสชัน ตะกร้าสินค้า ตัวนับ rate limit และคิว อยู่ใน Redis ในฐานะระบบบันทึกหลัก primary เขียน append-only file, replica สองตัวตามมา และ Sentinel สามตัวจะเลื่อนระดับ replica ขึ้นเป็น primary เมื่อ primary ล้มเหลว

<div class="arch" markdown="0"><svg viewBox="0 0 700 290" role="img" aria-label="Primary with two replicas and three Sentinels for failover"><title>Primary with two replicas and three Sentinels for failover</title><rect class="box" x="20" y="100" width="130" height="56" rx="7"/><text x="85.0" y="132.0" text-anchor="middle">Application</text><rect class="rd" x="250" y="90" width="160" height="76" rx="7"/><text x="330.0" y="125.0" text-anchor="middle">Redis primary</text><text class="sm" x="330.0" y="141.0" text-anchor="middle">AOF everysec</text><rect class="rd" x="520" y="30" width="150" height="52" rx="7"/><text x="595.0" y="60.0" text-anchor="middle">Replica 1</text><rect class="rd" x="520" y="170" width="150" height="52" rx="7"/><text x="595.0" y="200.0" text-anchor="middle">Replica 2</text><line class="ln" x1="150" y1="128" x2="248" y2="128"/><polygon class="hd" points="248.0,128.0 241.7,131.0 241.7,125.0"/><text class="sm" x="199.0" y="122.0" text-anchor="middle">writes, WAIT</text><line class="ln" x1="410" y1="112" x2="518" y2="60"/><polygon class="hd" points="518.0,60.0 513.6,65.5 511.0,60.0"/><text class="sm" x="464.0" y="80.0" text-anchor="middle">replication</text><line class="ln" x1="410" y1="145" x2="518" y2="192"/><polygon class="hd" points="518.0,192.0 511.0,192.3 513.4,186.7"/><rect class="box" x="250" y="236" width="420" height="40" rx="7"/><text x="460.0" y="260.0" text-anchor="middle">Sentinel ×3  ·  quorum 2  ·  promotes a replica on failure</text><line class="ln dash" x1="330" y1="236" x2="330" y2="168"/><polygon class="hd" points="330.0,168.0 333.0,174.3 327.0,174.3"/></svg></div>

| จุดแข็ง | หลักฐาน |
|---|---|
| ความทนทานของข้อมูลโดยไม่เสียความเร็ว | AOF `everysec` 97,087 req/s, p99 0.255 ms; `always` 17,203 req/s ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| failover อัตโนมัติที่รวดเร็ว | หยุด primary → ระบุ master ใหม่ได้ใน 4,402 ms; primary เดิมกลับเข้ามาเป็น replica |
| สำรองข้อมูล ณ จุดเวลาใดเวลาหนึ่งโดยไม่ต้องหยุดระบบ | `BACKUP START`/`SEAL` (8.10) กู้คืนลงเซิร์ฟเวอร์ใหม่ด้วย `preload-file` |

**ข้อควรระวัง:** การทำ replication เป็นแบบอะซิงโครนัส เอกสารระบุว่า "WAIT does not make Redis a strongly consistent store" และ `WAIT` นับเฉพาะการยืนยันของการเขียนที่มาจากการเชื่อมต่อที่เรียกคำสั่งเองเท่านั้น snapshot ใช้การคัดลอกหน่วยความจำเมื่อมีการเขียน: copy-on-write 252 MB สำหรับชุดข้อมูล 214 MB ภายใต้การเขียนทับ ควรให้ที่อยู่ของ Sentinel เป็นแบบที่ resolve ได้ต่อเนื่อง: การเฝ้าดูด้วยชื่อคอนเทนเนอร์ทำให้ failover เดียวกันยืดไปเป็น 284 s

เอกสาร: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/)

### 3. ขยายแนวนอนด้วย Redis Cluster

เมื่อหน่วยความจำหรือ CPU ของโหนดเดียวไม่พอ Redis Cluster จะแบ่ง keyspace ออกเป็น hash slot 16,384 ช่องกระจายไปตาม primary ซึ่งแต่ละตัวมี replica ไคลเอนต์เรียนรู้แผนที่ slot แล้วคุยกับโหนดที่ถูกต้องโดยตรง

<div class="arch" markdown="0"><svg viewBox="0 0 760 260" role="img" aria-label="Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot"><title>Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot</title><rect class="box" x="20" y="105" width="150" height="60" rx="7"/><text x="95.0" y="132.0" text-anchor="middle">Cluster-aware client</text><text class="sm" x="95.0" y="148.0" text-anchor="middle">caches slot map</text><rect class="rd" x="250" y="40" width="150" height="56" rx="7"/><text x="325.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="325.0" y="81.0" text-anchor="middle">slots 0–5460</text><rect class="rd" x="250" y="165" width="150" height="50" rx="7"/><text x="325.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="325" y1="96" x2="325" y2="163"/><polygon class="hd" points="325.0,163.0 322.0,156.7 328.0,156.7"/><rect class="rd" x="420" y="40" width="150" height="56" rx="7"/><text x="495.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="495.0" y="81.0" text-anchor="middle">5461–10922</text><rect class="rd" x="420" y="165" width="150" height="50" rx="7"/><text x="495.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="495" y1="96" x2="495" y2="163"/><polygon class="hd" points="495.0,163.0 492.0,156.7 498.0,156.7"/><rect class="rd" x="590" y="40" width="150" height="56" rx="7"/><text x="665.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="665.0" y="81.0" text-anchor="middle">10923–16383</text><rect class="rd" x="590" y="165" width="150" height="50" rx="7"/><text x="665.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="665" y1="96" x2="665" y2="163"/><polygon class="hd" points="665.0,163.0 662.0,156.7 668.0,156.7"/><line class="ln" x1="170" y1="125" x2="248" y2="70"/><polygon class="hd" points="248.0,70.0 244.6,76.1 241.1,71.1"/><text class="sm" x="209.0" y="91.5" text-anchor="middle">key → CRC16 mod 16384</text><text class="sm" x="495" y="245" text-anchor="middle">CLUSTER MIGRATION moves slot ranges between primaries atomically</text></svg></div>

| จุดแข็ง | หลักฐาน |
|---|---|
| reshard ได้โดยไม่ต้องหยุดการเขียน | `CLUSTER MIGRATION IMPORT 0 999` ย้าย 1,000 slot ใน 44 ms ด้วย `write_pause_ms 0` ขณะมีการเขียนประมาณ 200,000 ครั้ง/วินาที ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| การกำหนดเส้นทางที่คาดเดาได้ | `HASH_SLOT = CRC16(key) mod 16384`; โหนดที่ไม่ถูกต้องจะตอบ `MOVED` พร้อมโหนดที่ถูกต้อง |

**ข้อควรระวัง:** คำสั่งที่ใช้หลายคีย์ต้องอยู่ใน slot เดียวกัน `MSET user:1 a user:2 b` จะคืนค่า `CROSSSLOT`; hash tag ที่ใช้ร่วมกัน (`{user:1}:cart`, `{user:1}:orders`) ช่วยให้คีย์ที่เกี่ยวข้องอยู่ด้วยกัน ElastiCache Serverless ทำงานแบบเดียวกัน ([Compare]({{ '/compare/' | relative_url }})) ข้อกำหนดระบุว่า "Each master node in a cluster handles a subset of the 16384 hash slots"

เอกสาร: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/)

### 4. ใช้แบบมีผู้ดูแลบน Redis Cloud

เอนจินเดียวกันในรูปแบบบริการ Essentials คือฐานข้อมูลหนึ่งตัวบนโครงสร้างพื้นฐานที่ใช้ร่วมกัน พร้อมการทำ replication แบบเลือกได้ ส่วน Pro เป็นแบบเฉพาะ รองรับหลายฐานข้อมูล และเพิ่มสำเนา Active-Active ในหลายภูมิภาคที่รับการเขียนได้ทั้งหมด

<div class="arch" markdown="0"><svg viewBox="0 0 760 255" role="img" aria-label="Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro"><title>Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro</title><rect class="box" x="20" y="40" width="160" height="60" rx="7"/><text x="100.0" y="74.0" text-anchor="middle">App, region A</text><rect class="box" x="20" y="160" width="160" height="60" rx="7"/><text x="100.0" y="194.0" text-anchor="middle">App, region B</text><rect class="box" x="270" y="20" width="230" height="100" rx="7"/><text x="385.0" y="74.0" text-anchor="middle"></text><text x="385" y="44" text-anchor="middle">Redis Cloud · Essentials</text><rect class="rd" x="290" y="58" width="190" height="46" rx="7"/><text x="385.0" y="78.0" text-anchor="middle">one database</text><text class="sm" x="385.0" y="94.0" text-anchor="middle">replica in-zone or multi-AZ</text><rect class="box" x="270" y="140" width="470" height="100" rx="7"/><text x="505.0" y="194.0" text-anchor="middle"></text><text x="505" y="163" text-anchor="middle">Redis Cloud · Pro · Active-Active</text><rect class="rd" x="290" y="178" width="190" height="46" rx="7"/><text x="385.0" y="198.0" text-anchor="middle">copy in region A</text><text class="sm" x="385.0" y="214.0" text-anchor="middle">read + write</text><rect class="rd" x="530" y="178" width="190" height="46" rx="7"/><text x="625.0" y="198.0" text-anchor="middle">copy in region B</text><text class="sm" x="625.0" y="214.0" text-anchor="middle">read + write</text><line class="ln" x1="480" y1="201" x2="528" y2="201"/><polygon class="hd" points="528.0,201.0 521.7,204.0 521.7,198.0"/><polygon class="hd" points="480.0,201.0 486.3,198.0 486.3,204.0"/><text class="sm" x="504.0" y="195.0" text-anchor="middle">CRDT sync</text><line class="ln" x1="180" y1="70" x2="288" y2="80"/><polygon class="hd" points="288.0,80.0 281.4,82.5 282.0,76.4"/><line class="ln" x1="180" y1="190" x2="288" y2="200"/><polygon class="hd" points="288.0,200.0 281.4,202.5 282.0,196.4"/></svg></div>

| จุดแข็ง | หลักฐาน |
|---|---|
| ได้ฐานข้อมูลในไม่กี่วินาที รวมโมดูลมาให้แล้ว | ฐานข้อมูลฟรีพร้อมใช้ไม่กี่วินาทีหลังกรอกแบบฟอร์ม มี Search และ JSON ให้ใช้ ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| ทำงานอัตโนมัติได้ตั้งแต่วันแรก | REST API ใช้งานได้บนแผนฟรี ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| เขียนได้ในทุกภูมิภาค (Pro) | เป็นดีไซน์เท่านั้นในที่นี้; เอกสารระบุว่า "Active-Active databases allow read and write operations in each copy" โดยซิงโครไนซ์ด้วย CRDT |

**ข้อควรระวัง:** แผนฟรีมีไว้สำหรับทดลอง: 30 MB, 30 การเชื่อมต่อ, ไม่มี TLS (API ปฏิเสธ `enableTls`) ราคาที่อ่านได้จากคอนโซลเมื่อ 2026-11-07: Essentials เริ่มที่ $5 ต่อเดือน, Pro เริ่มที่ $200 ต่อเดือน

เอกสาร: [Redis Cloud](https://redis.io/docs/latest/operate/rc/), [High availability](https://redis.io/docs/latest/operate/rc/databases/configuration/high-availability/), [Active-Active](https://redis.io/docs/latest/operate/rc/databases/active-active/)

### 5. ชั้นบริบทสำหรับ AI agent: Redis Iris

Iris วางบริการไว้รอบ agent เพื่อไม่ให้ต้องสร้างบริบทใหม่ทุกเทิร์น เอกสารระบุว่า "Redis Iris is a production-ready context engine for AI agents" ที่ "adds persistent memory", "answers recurring questions without a model call" ให้ agent มี "one MCP endpoint for the tools of any MCP server and your Redis data" และ "routes each message" Agent Memory เก็บข้อมูลไว้ในฐานข้อมูล Redis ที่คุณเป็นเจ้าของ

<div class="arch" markdown="0"><svg viewBox="0 0 780 320" role="img" aria-label="Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database"><title>Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database</title><rect class="box" x="20" y="110" width="110" height="56" rx="7"/><text x="75.0" y="142.0" text-anchor="middle">User</text><rect class="box" x="180" y="100" width="170" height="76" rx="7"/><text x="265.0" y="135.0" text-anchor="middle">Agent app</text><text class="sm" x="265.0" y="151.0" text-anchor="middle">LLM + your code</text><line class="ln" x1="130" y1="138" x2="178" y2="138"/><polygon class="hd" points="178.0,138.0 171.7,141.0 171.7,135.0"/><rect class="rd" x="430" y="20" width="190" height="48" rx="7"/><text x="525.0" y="41.0" text-anchor="middle">Intent Router</text><text class="sm" x="525.0" y="57.0" text-anchor="middle">route before the LLM</text><line class="ln" x1="350" y1="138" x2="428" y2="44"/><polygon class="hd" points="428.0,44.0 426.3,50.8 421.6,46.9"/><rect class="rd" x="430" y="80" width="190" height="48" rx="7"/><text x="525.0" y="101.0" text-anchor="middle">Agent Memory</text><text class="sm" x="525.0" y="117.0" text-anchor="middle">remember · recall</text><line class="ln" x1="350" y1="138" x2="428" y2="104"/><polygon class="hd" points="428.0,104.0 423.4,109.3 421.0,103.7"/><rect class="rd" x="430" y="140" width="190" height="48" rx="7"/><text x="525.0" y="161.0" text-anchor="middle">Agent Playbooks</text><text class="sm" x="525.0" y="177.0" text-anchor="middle">approved answers</text><line class="ln" x1="350" y1="138" x2="428" y2="164"/><polygon class="hd" points="428.0,164.0 421.1,164.9 423.0,159.1"/><rect class="rd" x="430" y="200" width="190" height="48" rx="7"/><text x="525.0" y="221.0" text-anchor="middle">Context Gateway</text><text class="sm" x="525.0" y="237.0" text-anchor="middle">one MCP endpoint</text><line class="ln" x1="350" y1="138" x2="428" y2="224"/><polygon class="hd" points="428.0,224.0 421.5,221.4 426.0,217.3"/><rect class="rd" x="430" y="260" width="190" height="48" rx="7"/><text x="525.0" y="281.0" text-anchor="middle">Lens</text><text class="sm" x="525.0" y="297.0" text-anchor="middle">trace each turn</text><line class="ln" x1="350" y1="138" x2="428" y2="284"/><polygon class="hd" points="428.0,284.0 422.3,279.9 427.7,277.0"/><rect class="rd" x="660" y="100" width="100" height="70" rx="7"/><text x="710.0" y="132.0" text-anchor="middle">Redis DB</text><text class="sm" x="710.0" y="148.0" text-anchor="middle">JSON + Search</text><line class="ln dash" x1="620" y1="104" x2="658" y2="125"/><polygon class="hd" points="658.0,125.0 651.0,124.6 654.0,119.3"/><line class="ln dash" x1="620" y1="216" x2="658" y2="150"/><polygon class="hd" points="658.0,150.0 657.5,157.0 652.2,153.9"/><rect class="box" x="660" y="230" width="100" height="56" rx="7"/><text x="710.0" y="255.0" text-anchor="middle">MCP servers</text><text class="sm" x="710.0" y="271.0" text-anchor="middle">your tools</text><line class="ln dash" x1="620" y1="232" x2="658" y2="252"/><polygon class="hd" points="658.0,252.0 651.0,251.8 653.8,246.4"/></svg></div>

| จุดแข็ง | หลักฐาน |
|---|---|
| หน่วยความจำที่สร้างตัวเอง | ข้อเท็จจริงจากบทสนทนาสองเทิร์นถูกสกัดออกมาประมาณ 15 s ต่อมา ([Iris]({{ '/iris/' | relative_url }})) |
| ข้อมูลอยู่ในฐานข้อมูลของคุณ | Agent Memory เขียนเอกสาร JSON และดัชนี Search สี่ตัวลงในฐานข้อมูลฟรี ([Iris]({{ '/iris/' | relative_url }})) |
| คีย์ที่จำกัดขอบเขตตามผลิตภัณฑ์และทรัพยากร | คีย์แบบอ่านเรียกคืนข้อมูลได้ แต่เขียนแล้วได้ 403 ([Iris]({{ '/iris/' | relative_url }})) |
| แต่ละเทิร์นถูกลง | Intent Router และ Agent Playbooks ตอบหรือกำหนดเส้นทางก่อนเรียกโมเดล: เป็นดีไซน์เท่านั้นในที่นี้ |

**ข้อควรระวัง:** บริการรันอยู่ที่ไหน: endpoint ของ Agent Memory อยู่ที่ us-east-1 ขณะที่ฐานข้อมูลอยู่ที่โซล และการเรียกคืนจากเกาหลีใช้เวลามัธยฐาน 611 ms ไม่พบการวัดจำนวนข้อความ (metering) ที่ใดในคอนโซล Intent Router, Playbooks, Context Gateway และ Lens ยังไม่ได้รัน

เอกสาร: [Redis Iris](https://redis.io/docs/latest/develop/ai/context-engine/), [Agent Memory](https://redis.io/docs/latest/operate/iris/agent-memory/), [Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/), [Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/), [Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/), [Lens](https://redis.io/docs/latest/operate/iris/lens/)

### 6. การค้นหาและเวกเตอร์ข้างข้อมูล

เรกคอร์ด ดัชนีรอง และ embedding ของข้อมูลอยู่ในฐานข้อมูล Redis เดียวกัน การค้นหาจึงไม่ต้องข้ามไปยังระบบอื่น

<div class="arch" markdown="0"><svg viewBox="0 0 760 215" role="img" aria-label="Search and vectors in the same Redis database as the records"><title>Search and vectors in the same Redis database as the records</title><rect class="box" x="20" y="80" width="150" height="60" rx="7"/><text x="95.0" y="114.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="420" height="180" rx="7"/><text x="510.0" y="114.0" text-anchor="middle"></text><text x="510" y="44" text-anchor="middle">one Redis 8 database</text><rect class="box" x="320" y="60" width="170" height="52" rx="7"/><text x="405.0" y="83.0" text-anchor="middle">Hashes / JSON</text><text class="sm" x="405.0" y="99.0" text-anchor="middle">the records</text><rect class="box" x="530" y="60" width="170" height="52" rx="7"/><text x="615.0" y="83.0" text-anchor="middle">Search index</text><text class="sm" x="615.0" y="99.0" text-anchor="middle">text · numeric · vector</text><rect class="box" x="320" y="128" width="380" height="52" rx="7"/><text x="510.0" y="151.0" text-anchor="middle">Vector set (beta)</text><text class="sm" x="510.0" y="167.0" text-anchor="middle">VADD · VSIM, no index to define</text><line class="ln" x1="490" y1="86" x2="528" y2="86"/><polygon class="hd" points="528.0,86.0 521.7,89.0 521.7,83.0"/><line class="ln" x1="170" y1="110" x2="298" y2="110"/><polygon class="hd" points="298.0,110.0 291.7,113.0 291.7,107.0"/><text class="sm" x="234.0" y="104.0" text-anchor="middle">FT.SEARCH / VSIM</text></svg></div>

| จุดแข็ง | หลักฐาน |
|---|---|
| มีมาในตัว ไม่ต้องตั้งค่า | Search, JSON และ vector set โหลดมาพร้อมอิมเมจ Redis 8 มาตรฐาน ([Setup]({{ '/setup/' | relative_url }})) |
| ภาษาคิวรีเดียวสำหรับข้อความ ตัวเลข และเวกเตอร์ | `FT.CREATE` บน hash, การค้นหาช่วงตัวเลข และการทดสอบดัชนีเวกเตอร์ รันบน Redis 8.10.3 ([Compare]({{ '/compare/' | relative_url }})) |
| ชนิดข้อมูลเวกเตอร์แบบเนทีฟ | `VADD` และ `VSIM` ใช้งานได้โดยไม่ต้องนิยามดัชนี |

**ข้อควรระวัง:** vector set ยังเป็น beta ความเกี่ยวข้องของผลลัพธ์และความเร็วในระดับใหญ่ยังไม่ได้วัดที่นี่ แล็บ Search บนเครื่องยังอยู่ในแผน

เอกสาร: [Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/)

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

**Posisi Redis dalam sebuah sistem, dan mengapa ia kuat di sana.** Ada enam tata letak, dari cache di depan basis data hingga lapisan konteks untuk agen AI. Setiap tata letak punya diagram, posisi Redis, apa yang membuatnya kuat di sana (didukung pengukuran di situs ini bila ada), hal yang perlu diwaspadai, dan dokumentasi resmi dengan kalimat kuncinya yang dikutip. Tata letak yang belum dijalankan end to end di situs ini ditandai sebagai desain.

| Tata letak | Peran Redis | Dijalankan di situs ini |
|---|---|---|
| Cache di depan basis data | salinan cepat dari data yang sering dibaca | sebagian: throughput dan batasan |
| Hot state dengan high availability | sistem pencatatan utama untuk sesi, penghitung, antrean | ya: persistensi, replika, Sentinel |
| Scale-out dengan Redis Cluster | data yang dibagi ke beberapa shard menurut hash slot | ya: klaster enam node, migrasi slot |
| Terkelola di Redis Cloud | sebuah layanan, dari satu basis data hingga Active-Active | hanya paket gratis; Active-Active adalah desain |
| Lapisan konteks untuk agen AI (Iris) | memori, perutean, jawaban yang disetujui, dan alat di sekitar LLM | Agent Memory ya; layanan lain belum |
| Pencarian dan vektor di samping data | indeks dan rekaman di satu tempat | hanya uji coba awal |

### 1. Cache di depan basis data

Aplikasi bertanya ke Redis lebih dulu; jika tidak ada (miss), aplikasi membaca basis data dan menulis hasilnya ke Redis dengan TTL. Redis menyimpan salinan, sedangkan basis data tetap menjadi sumber kebenaran.

<div class="arch" markdown="0"><svg viewBox="0 0 760 250" role="img" aria-label="Cache-aside: the application reads Redis first and fills it from the database on a miss"><title>Cache-aside: the application reads Redis first and fills it from the database on a miss</title><rect class="box" x="20" y="95" width="130" height="60" rx="7"/><text x="85.0" y="129.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="170" height="60" rx="7"/><text x="385.0" y="47.0" text-anchor="middle">Redis</text><text class="sm" x="385.0" y="63.0" text-anchor="middle">cache, TTL + eviction</text><rect class="box" x="300" y="170" width="170" height="60" rx="7"/><text x="385.0" y="197.0" text-anchor="middle">Primary database</text><text class="sm" x="385.0" y="213.0" text-anchor="middle">source of truth</text><line class="ln" x1="150" y1="105" x2="298" y2="38"/><polygon class="hd" points="298.0,38.0 293.5,43.4 291.0,37.8"/><text class="sm" x="224.0" y="65.5" text-anchor="middle">1 GET</text><line class="ln" x1="150" y1="145" x2="298" y2="205"/><polygon class="hd" points="298.0,205.0 291.0,205.5 293.3,199.8"/><text class="sm" x="224.0" y="169.0" text-anchor="middle">2 on miss: read</text><line class="ln dash" x1="150" y1="125" x2="298" y2="66"/><polygon class="hd" points="298.0,66.0 293.3,71.2 291.0,65.5"/><text class="sm" x="246" y="112" text-anchor="middle">3 SET with TTL</text><rect class="box" x="560" y="95" width="180" height="60" rx="7"/><text x="650.0" y="122.0" text-anchor="middle">Other app servers</text><text class="sm" x="650.0" y="138.0" text-anchor="middle">client-side cache</text><line class="ln dash" x1="470" y1="50" x2="558" y2="112"/><polygon class="hd" points="558.0,112.0 551.1,110.9 554.6,105.9"/><text class="sm" x="514.0" y="75.0" text-anchor="middle">invalidations</text></svg></div>

| Kuat karena | Bukti |
|---|---|
| Pembacaan berasal dari memori pada satu event loop | 134,523–136,097 SET/GET per detik pada satu node dengan pengaturan bawaan; 498,753–520,472 dengan `io-threads 8` ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Ada struktur data, bukan hanya string | hash dengan TTL per field, sorted set, JSON dalam image standar ([Setup]({{ '/setup/' | relative_url }})) |
| Klien juga dapat melakukan cache, dan diberi tahu kapan harus membuangnya | client-side caching dengan bantuan server (dokumentasi di bawah) |

**Perhatikan:** invalidasi adalah bagian tersulit; dokumentasi menyebut "A problem with the above pattern is how to invalidate the information that the application is holding". Kebijakan eviksi menentukan apa yang terjadi saat memori penuh: dengan `volatile-lru`, key tanpa TTL tidak pernah dievaksi dan penulisan gagal dengan `OOM` ([Redis Cloud free database]({{ '/cloud/' | relative_url }})).

Dokumentasi: [Client-side caching](https://redis.io/docs/latest/develop/reference/client-side-caching/), [Eviction](https://redis.io/docs/latest/develop/reference/eviction/).

### 2. Hot state dengan high availability

Sesi, keranjang belanja, penghitung pembatasan laju, dan antrean berada di Redis sebagai sistem pencatatan utama. Satu primary menulis append-only file, dua replika mengikutinya, dan tiga Sentinel mempromosikan sebuah replika saat primary gagal.

<div class="arch" markdown="0"><svg viewBox="0 0 700 290" role="img" aria-label="Primary with two replicas and three Sentinels for failover"><title>Primary with two replicas and three Sentinels for failover</title><rect class="box" x="20" y="100" width="130" height="56" rx="7"/><text x="85.0" y="132.0" text-anchor="middle">Application</text><rect class="rd" x="250" y="90" width="160" height="76" rx="7"/><text x="330.0" y="125.0" text-anchor="middle">Redis primary</text><text class="sm" x="330.0" y="141.0" text-anchor="middle">AOF everysec</text><rect class="rd" x="520" y="30" width="150" height="52" rx="7"/><text x="595.0" y="60.0" text-anchor="middle">Replica 1</text><rect class="rd" x="520" y="170" width="150" height="52" rx="7"/><text x="595.0" y="200.0" text-anchor="middle">Replica 2</text><line class="ln" x1="150" y1="128" x2="248" y2="128"/><polygon class="hd" points="248.0,128.0 241.7,131.0 241.7,125.0"/><text class="sm" x="199.0" y="122.0" text-anchor="middle">writes, WAIT</text><line class="ln" x1="410" y1="112" x2="518" y2="60"/><polygon class="hd" points="518.0,60.0 513.6,65.5 511.0,60.0"/><text class="sm" x="464.0" y="80.0" text-anchor="middle">replication</text><line class="ln" x1="410" y1="145" x2="518" y2="192"/><polygon class="hd" points="518.0,192.0 511.0,192.3 513.4,186.7"/><rect class="box" x="250" y="236" width="420" height="40" rx="7"/><text x="460.0" y="260.0" text-anchor="middle">Sentinel ×3  ·  quorum 2  ·  promotes a replica on failure</text><line class="ln dash" x1="330" y1="236" x2="330" y2="168"/><polygon class="hd" points="330.0,168.0 333.0,174.3 327.0,174.3"/></svg></div>

| Kuat karena | Bukti |
|---|---|
| Durabilitas tanpa mengorbankan kecepatan | AOF `everysec` 97,087 req/s, p99 0.255 ms; `always` 17,203 req/s ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Failover otomatis yang cepat | primary dihentikan → master baru ditetapkan dalam 4,402 ms; primary lama bergabung kembali sebagai replika |
| Pencadangan point-in-time tanpa menghentikan layanan | `BACKUP START`/`SEAL` (8.10) dipulihkan ke server baru dengan `preload-file` |

**Perhatikan:** replikasi bersifat asinkron. Dokumentasi menyebut "WAIT does not make Redis a strongly consistent store", dan `WAIT` hanya menghitung konfirmasi untuk penulisan dari koneksi pemanggilnya sendiri. Snapshot menyalin memori saat penulisan: 252 MB copy-on-write untuk dataset 214 MB di bawah penimpaan. Berikan alamat Sentinel yang tetap dapat di-resolve: memantau nama container memperpanjang failover yang sama menjadi 284 s.

Dokumentasi: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/).

### 3. Scale-out dengan Redis Cluster

Saat memori atau CPU satu node tidak cukup, Redis Cluster membagi keyspace menjadi 16,384 hash slot di beberapa primary, masing-masing dengan replika. Klien mempelajari peta slot dan berkomunikasi langsung dengan node yang tepat.

<div class="arch" markdown="0"><svg viewBox="0 0 760 260" role="img" aria-label="Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot"><title>Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot</title><rect class="box" x="20" y="105" width="150" height="60" rx="7"/><text x="95.0" y="132.0" text-anchor="middle">Cluster-aware client</text><text class="sm" x="95.0" y="148.0" text-anchor="middle">caches slot map</text><rect class="rd" x="250" y="40" width="150" height="56" rx="7"/><text x="325.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="325.0" y="81.0" text-anchor="middle">slots 0–5460</text><rect class="rd" x="250" y="165" width="150" height="50" rx="7"/><text x="325.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="325" y1="96" x2="325" y2="163"/><polygon class="hd" points="325.0,163.0 322.0,156.7 328.0,156.7"/><rect class="rd" x="420" y="40" width="150" height="56" rx="7"/><text x="495.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="495.0" y="81.0" text-anchor="middle">5461–10922</text><rect class="rd" x="420" y="165" width="150" height="50" rx="7"/><text x="495.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="495" y1="96" x2="495" y2="163"/><polygon class="hd" points="495.0,163.0 492.0,156.7 498.0,156.7"/><rect class="rd" x="590" y="40" width="150" height="56" rx="7"/><text x="665.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="665.0" y="81.0" text-anchor="middle">10923–16383</text><rect class="rd" x="590" y="165" width="150" height="50" rx="7"/><text x="665.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="665" y1="96" x2="665" y2="163"/><polygon class="hd" points="665.0,163.0 662.0,156.7 668.0,156.7"/><line class="ln" x1="170" y1="125" x2="248" y2="70"/><polygon class="hd" points="248.0,70.0 244.6,76.1 241.1,71.1"/><text class="sm" x="209.0" y="91.5" text-anchor="middle">key → CRC16 mod 16384</text><text class="sm" x="495" y="245" text-anchor="middle">CLUSTER MIGRATION moves slot ranges between primaries atomically</text></svg></div>

| Kuat karena | Bukti |
|---|---|
| Resharding tanpa menghentikan penulisan | `CLUSTER MIGRATION IMPORT 0 999` memindahkan 1,000 slot dalam 44 ms dengan `write_pause_ms 0` di bawah ~200,000 penulisan/detik ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Perutean yang dapat diprediksi | `HASH_SLOT = CRC16(key) mod 16384`; node yang salah menjawab `MOVED` beserta node yang benar |

**Perhatikan:** perintah multi-key harus berada dalam satu slot. `MSET user:1 a user:2 b` mengembalikan `CROSSSLOT`; hash tag bersama (`{user:1}:cart`, `{user:1}:orders`) menjaga key terkait tetap bersama. ElastiCache Serverless berperilaku sama ([Compare]({{ '/compare/' | relative_url }})). Spesifikasinya menyebut "Each master node in a cluster handles a subset of the 16384 hash slots".

Dokumentasi: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/).

### 4. Terkelola di Redis Cloud

Engine yang sama sebagai layanan. Essentials adalah satu basis data pada infrastruktur bersama dengan replikasi opsional; Pro bersifat dedicated, menampung banyak basis data, dan menambahkan salinan Active-Active di beberapa wilayah yang semuanya menerima penulisan.

<div class="arch" markdown="0"><svg viewBox="0 0 760 255" role="img" aria-label="Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro"><title>Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro</title><rect class="box" x="20" y="40" width="160" height="60" rx="7"/><text x="100.0" y="74.0" text-anchor="middle">App, region A</text><rect class="box" x="20" y="160" width="160" height="60" rx="7"/><text x="100.0" y="194.0" text-anchor="middle">App, region B</text><rect class="box" x="270" y="20" width="230" height="100" rx="7"/><text x="385.0" y="74.0" text-anchor="middle"></text><text x="385" y="44" text-anchor="middle">Redis Cloud · Essentials</text><rect class="rd" x="290" y="58" width="190" height="46" rx="7"/><text x="385.0" y="78.0" text-anchor="middle">one database</text><text class="sm" x="385.0" y="94.0" text-anchor="middle">replica in-zone or multi-AZ</text><rect class="box" x="270" y="140" width="470" height="100" rx="7"/><text x="505.0" y="194.0" text-anchor="middle"></text><text x="505" y="163" text-anchor="middle">Redis Cloud · Pro · Active-Active</text><rect class="rd" x="290" y="178" width="190" height="46" rx="7"/><text x="385.0" y="198.0" text-anchor="middle">copy in region A</text><text class="sm" x="385.0" y="214.0" text-anchor="middle">read + write</text><rect class="rd" x="530" y="178" width="190" height="46" rx="7"/><text x="625.0" y="198.0" text-anchor="middle">copy in region B</text><text class="sm" x="625.0" y="214.0" text-anchor="middle">read + write</text><line class="ln" x1="480" y1="201" x2="528" y2="201"/><polygon class="hd" points="528.0,201.0 521.7,204.0 521.7,198.0"/><polygon class="hd" points="480.0,201.0 486.3,198.0 486.3,204.0"/><text class="sm" x="504.0" y="195.0" text-anchor="middle">CRDT sync</text><line class="ln" x1="180" y1="70" x2="288" y2="80"/><polygon class="hd" points="288.0,80.0 281.4,82.5 282.0,76.4"/><line class="ln" x1="180" y1="190" x2="288" y2="200"/><polygon class="hd" points="288.0,200.0 281.4,202.5 282.0,196.4"/></svg></div>

| Kuat karena | Bukti |
|---|---|
| Basis data dalam hitungan detik, modul sudah termasuk | basis data gratis siap beberapa detik setelah formulir, Search dan JSON tersedia ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| Otomatisasi sejak hari pertama | REST API berfungsi di paket gratis ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| Penulisan di setiap wilayah (Pro) | hanya desain di sini; dokumentasi menyebut "Active-Active databases allow read and write operations in each copy", disinkronkan oleh CRDT |

**Perhatikan:** paket gratis untuk mencoba: 30 MB, 30 koneksi, tanpa TLS (API menolak `enableTls`). Harga yang terbaca di konsol pada 2026-11-07: Essentials mulai $5 per bulan, Pro mulai $200 per bulan.

Dokumentasi: [Redis Cloud](https://redis.io/docs/latest/operate/rc/), [High availability](https://redis.io/docs/latest/operate/rc/databases/configuration/high-availability/), [Active-Active](https://redis.io/docs/latest/operate/rc/databases/active-active/).

### 5. Lapisan konteks untuk agen AI: Redis Iris

Iris menempatkan layanan di sekitar agen agar tidak perlu membangun ulang konteks pada setiap giliran. Dokumentasi menyebut "Redis Iris is a production-ready context engine for AI agents" yang "adds persistent memory", "answers recurring questions without a model call", memberi agen "one MCP endpoint for the tools of any MCP server and your Redis data", dan "routes each message". Agent Memory menyimpan datanya di basis data Redis milik Anda.

<div class="arch" markdown="0"><svg viewBox="0 0 780 320" role="img" aria-label="Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database"><title>Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database</title><rect class="box" x="20" y="110" width="110" height="56" rx="7"/><text x="75.0" y="142.0" text-anchor="middle">User</text><rect class="box" x="180" y="100" width="170" height="76" rx="7"/><text x="265.0" y="135.0" text-anchor="middle">Agent app</text><text class="sm" x="265.0" y="151.0" text-anchor="middle">LLM + your code</text><line class="ln" x1="130" y1="138" x2="178" y2="138"/><polygon class="hd" points="178.0,138.0 171.7,141.0 171.7,135.0"/><rect class="rd" x="430" y="20" width="190" height="48" rx="7"/><text x="525.0" y="41.0" text-anchor="middle">Intent Router</text><text class="sm" x="525.0" y="57.0" text-anchor="middle">route before the LLM</text><line class="ln" x1="350" y1="138" x2="428" y2="44"/><polygon class="hd" points="428.0,44.0 426.3,50.8 421.6,46.9"/><rect class="rd" x="430" y="80" width="190" height="48" rx="7"/><text x="525.0" y="101.0" text-anchor="middle">Agent Memory</text><text class="sm" x="525.0" y="117.0" text-anchor="middle">remember · recall</text><line class="ln" x1="350" y1="138" x2="428" y2="104"/><polygon class="hd" points="428.0,104.0 423.4,109.3 421.0,103.7"/><rect class="rd" x="430" y="140" width="190" height="48" rx="7"/><text x="525.0" y="161.0" text-anchor="middle">Agent Playbooks</text><text class="sm" x="525.0" y="177.0" text-anchor="middle">approved answers</text><line class="ln" x1="350" y1="138" x2="428" y2="164"/><polygon class="hd" points="428.0,164.0 421.1,164.9 423.0,159.1"/><rect class="rd" x="430" y="200" width="190" height="48" rx="7"/><text x="525.0" y="221.0" text-anchor="middle">Context Gateway</text><text class="sm" x="525.0" y="237.0" text-anchor="middle">one MCP endpoint</text><line class="ln" x1="350" y1="138" x2="428" y2="224"/><polygon class="hd" points="428.0,224.0 421.5,221.4 426.0,217.3"/><rect class="rd" x="430" y="260" width="190" height="48" rx="7"/><text x="525.0" y="281.0" text-anchor="middle">Lens</text><text class="sm" x="525.0" y="297.0" text-anchor="middle">trace each turn</text><line class="ln" x1="350" y1="138" x2="428" y2="284"/><polygon class="hd" points="428.0,284.0 422.3,279.9 427.7,277.0"/><rect class="rd" x="660" y="100" width="100" height="70" rx="7"/><text x="710.0" y="132.0" text-anchor="middle">Redis DB</text><text class="sm" x="710.0" y="148.0" text-anchor="middle">JSON + Search</text><line class="ln dash" x1="620" y1="104" x2="658" y2="125"/><polygon class="hd" points="658.0,125.0 651.0,124.6 654.0,119.3"/><line class="ln dash" x1="620" y1="216" x2="658" y2="150"/><polygon class="hd" points="658.0,150.0 657.5,157.0 652.2,153.9"/><rect class="box" x="660" y="230" width="100" height="56" rx="7"/><text x="710.0" y="255.0" text-anchor="middle">MCP servers</text><text class="sm" x="710.0" y="271.0" text-anchor="middle">your tools</text><line class="ln dash" x1="620" y1="232" x2="658" y2="252"/><polygon class="hd" points="658.0,252.0 651.0,251.8 653.8,246.4"/></svg></div>

| Kuat karena | Bukti |
|---|---|
| Memori yang membangun dirinya sendiri | sebuah fakta dari percakapan dua giliran diekstrak sekitar 15 s kemudian ([Iris]({{ '/iris/' | relative_url }})) |
| Data tetap di basis data Anda | Agent Memory menulis dokumen JSON dan empat indeks Search ke basis data gratis ([Iris]({{ '/iris/' | relative_url }})) |
| Key dengan cakupan per produk dan sumber daya | key baca dapat melakukan recall tetapi mendapat 403 saat menulis ([Iris]({{ '/iris/' | relative_url }})) |
| Giliran yang lebih murah | Intent Router dan Agent Playbooks menjawab atau merutekan sebelum pemanggilan model: hanya desain di sini |

**Perhatikan:** tempat layanan berjalan: endpoint Agent Memory berada di us-east-1 sementara basis data di Seoul, dan recall dari Korea memakan median 611 ms. Pengukuran pesan (metering) tidak terlihat di mana pun di konsol. Intent Router, Playbooks, Context Gateway, dan Lens belum dijalankan.

Dokumentasi: [Redis Iris](https://redis.io/docs/latest/develop/ai/context-engine/), [Agent Memory](https://redis.io/docs/latest/operate/iris/agent-memory/), [Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/), [Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/), [Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/), [Lens](https://redis.io/docs/latest/operate/iris/lens/).

### 6. Pencarian dan vektor di samping data

Rekaman, indeks sekunder, dan embedding-nya berada di basis data Redis yang sama, sehingga kueri tidak perlu berpindah ke sistem lain.

<div class="arch" markdown="0"><svg viewBox="0 0 760 215" role="img" aria-label="Search and vectors in the same Redis database as the records"><title>Search and vectors in the same Redis database as the records</title><rect class="box" x="20" y="80" width="150" height="60" rx="7"/><text x="95.0" y="114.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="420" height="180" rx="7"/><text x="510.0" y="114.0" text-anchor="middle"></text><text x="510" y="44" text-anchor="middle">one Redis 8 database</text><rect class="box" x="320" y="60" width="170" height="52" rx="7"/><text x="405.0" y="83.0" text-anchor="middle">Hashes / JSON</text><text class="sm" x="405.0" y="99.0" text-anchor="middle">the records</text><rect class="box" x="530" y="60" width="170" height="52" rx="7"/><text x="615.0" y="83.0" text-anchor="middle">Search index</text><text class="sm" x="615.0" y="99.0" text-anchor="middle">text · numeric · vector</text><rect class="box" x="320" y="128" width="380" height="52" rx="7"/><text x="510.0" y="151.0" text-anchor="middle">Vector set (beta)</text><text class="sm" x="510.0" y="167.0" text-anchor="middle">VADD · VSIM, no index to define</text><line class="ln" x1="490" y1="86" x2="528" y2="86"/><polygon class="hd" points="528.0,86.0 521.7,89.0 521.7,83.0"/><line class="ln" x1="170" y1="110" x2="298" y2="110"/><polygon class="hd" points="298.0,110.0 291.7,113.0 291.7,107.0"/><text class="sm" x="234.0" y="104.0" text-anchor="middle">FT.SEARCH / VSIM</text></svg></div>

| Kuat karena | Bukti |
|---|---|
| Bawaan, tanpa konfigurasi | Search, JSON, dan vector set dimuat bersama image Redis 8 standar ([Setup]({{ '/setup/' | relative_url }})) |
| Satu bahasa kueri untuk teks, angka, dan vektor | `FT.CREATE` pada hash, rentang numerik, dan uji coba indeks vektor berjalan di Redis 8.10.3 ([Compare]({{ '/compare/' | relative_url }})) |
| Tipe vektor native | `VADD` dan `VSIM` berfungsi tanpa mendefinisikan indeks |

**Perhatikan:** vector set masih beta. Relevansi dan kecepatan pada skala besar belum diukur di sini; lab Search lokal masih direncanakan.

Dokumentasi: [Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/).

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

**Kedudukan Redis dalam sesebuah sistem, dan sebab ia kukuh di situ.** Terdapat enam susun atur, daripada cache di hadapan pangkalan data hingga lapisan konteks untuk ejen AI. Setiap susun atur mempunyai rajah, kedudukan Redis, apa yang menjadikannya kukuh di situ (disokong pengukuran di laman ini jika ada), perkara yang perlu diberi perhatian, dan dokumentasi rasmi dengan ayat utamanya dipetik. Susun atur yang belum dijalankan hujung ke hujung di laman ini ditandakan sebagai reka bentuk.

| Susun atur | Peranan Redis | Dijalankan di laman ini |
|---|---|---|
| Cache di hadapan pangkalan data | salinan pantas bagi bacaan yang kerap | sebahagian: daya pemprosesan dan had |
| Hot state dengan high availability | sistem rekod untuk sesi, pembilang, baris gilir | ya: ketekunan, replika, Sentinel |
| Scale-out dengan Redis Cluster | data dipecahkan merentas shard mengikut hash slot | ya: kluster enam nod, migrasi slot |
| Terurus di Redis Cloud | satu perkhidmatan, daripada satu pangkalan data hingga Active-Active | pelan percuma sahaja; Active-Active ialah reka bentuk |
| Lapisan konteks untuk ejen AI (Iris) | memori, penghalaan, jawapan yang diluluskan dan alat di sekeliling LLM | Agent Memory ya; perkhidmatan lain belum |
| Carian dan vektor di sebelah data | indeks dan rekod di satu tempat | hanya ujian awal |

### 1. Cache di hadapan pangkalan data

Aplikasi bertanya kepada Redis dahulu; jika tiada (miss), aplikasi membaca pangkalan data dan menulis hasilnya ke Redis dengan TTL. Redis menyimpan salinan, manakala pangkalan data kekal sebagai sumber kebenaran.

<div class="arch" markdown="0"><svg viewBox="0 0 760 250" role="img" aria-label="Cache-aside: the application reads Redis first and fills it from the database on a miss"><title>Cache-aside: the application reads Redis first and fills it from the database on a miss</title><rect class="box" x="20" y="95" width="130" height="60" rx="7"/><text x="85.0" y="129.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="170" height="60" rx="7"/><text x="385.0" y="47.0" text-anchor="middle">Redis</text><text class="sm" x="385.0" y="63.0" text-anchor="middle">cache, TTL + eviction</text><rect class="box" x="300" y="170" width="170" height="60" rx="7"/><text x="385.0" y="197.0" text-anchor="middle">Primary database</text><text class="sm" x="385.0" y="213.0" text-anchor="middle">source of truth</text><line class="ln" x1="150" y1="105" x2="298" y2="38"/><polygon class="hd" points="298.0,38.0 293.5,43.4 291.0,37.8"/><text class="sm" x="224.0" y="65.5" text-anchor="middle">1 GET</text><line class="ln" x1="150" y1="145" x2="298" y2="205"/><polygon class="hd" points="298.0,205.0 291.0,205.5 293.3,199.8"/><text class="sm" x="224.0" y="169.0" text-anchor="middle">2 on miss: read</text><line class="ln dash" x1="150" y1="125" x2="298" y2="66"/><polygon class="hd" points="298.0,66.0 293.3,71.2 291.0,65.5"/><text class="sm" x="246" y="112" text-anchor="middle">3 SET with TTL</text><rect class="box" x="560" y="95" width="180" height="60" rx="7"/><text x="650.0" y="122.0" text-anchor="middle">Other app servers</text><text class="sm" x="650.0" y="138.0" text-anchor="middle">client-side cache</text><line class="ln dash" x1="470" y1="50" x2="558" y2="112"/><polygon class="hd" points="558.0,112.0 551.1,110.9 554.6,105.9"/><text class="sm" x="514.0" y="75.0" text-anchor="middle">invalidations</text></svg></div>

| Kukuh kerana | Bukti |
|---|---|
| Bacaan datang daripada memori pada satu event loop | 134,523–136,097 SET/GET sesaat pada satu nod dengan tetapan lalai; 498,753–520,472 dengan `io-threads 8` ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Ada struktur data, bukan rentetan sahaja | hash dengan TTL bagi setiap medan, sorted set, JSON dalam imej stok ([Setup]({{ '/setup/' | relative_url }})) |
| Klien juga boleh membuat cache, dan dimaklumkan bila perlu membuangnya | client-side caching dibantu pelayan (dokumentasi di bawah) |

**Perhatikan:** pembatalan sah (invalidation) ialah bahagian yang sukar; dokumentasi menyatakan "A problem with the above pattern is how to invalidate the information that the application is holding". Dasar penyingkiran menentukan apa yang berlaku apabila memori penuh: di bawah `volatile-lru`, kunci tanpa TTL tidak pernah disingkirkan dan penulisan gagal dengan `OOM` ([Redis Cloud free database]({{ '/cloud/' | relative_url }})).

Dokumentasi: [Client-side caching](https://redis.io/docs/latest/develop/reference/client-side-caching/), [Eviction](https://redis.io/docs/latest/develop/reference/eviction/).

### 2. Hot state dengan high availability

Sesi, troli, pembilang had kadar dan baris gilir berada dalam Redis sebagai sistem rekod. Satu primary menulis fail append-only, dua replika mengikutinya, dan tiga Sentinel menaik taraf sebuah replika apabila primary gagal.

<div class="arch" markdown="0"><svg viewBox="0 0 700 290" role="img" aria-label="Primary with two replicas and three Sentinels for failover"><title>Primary with two replicas and three Sentinels for failover</title><rect class="box" x="20" y="100" width="130" height="56" rx="7"/><text x="85.0" y="132.0" text-anchor="middle">Application</text><rect class="rd" x="250" y="90" width="160" height="76" rx="7"/><text x="330.0" y="125.0" text-anchor="middle">Redis primary</text><text class="sm" x="330.0" y="141.0" text-anchor="middle">AOF everysec</text><rect class="rd" x="520" y="30" width="150" height="52" rx="7"/><text x="595.0" y="60.0" text-anchor="middle">Replica 1</text><rect class="rd" x="520" y="170" width="150" height="52" rx="7"/><text x="595.0" y="200.0" text-anchor="middle">Replica 2</text><line class="ln" x1="150" y1="128" x2="248" y2="128"/><polygon class="hd" points="248.0,128.0 241.7,131.0 241.7,125.0"/><text class="sm" x="199.0" y="122.0" text-anchor="middle">writes, WAIT</text><line class="ln" x1="410" y1="112" x2="518" y2="60"/><polygon class="hd" points="518.0,60.0 513.6,65.5 511.0,60.0"/><text class="sm" x="464.0" y="80.0" text-anchor="middle">replication</text><line class="ln" x1="410" y1="145" x2="518" y2="192"/><polygon class="hd" points="518.0,192.0 511.0,192.3 513.4,186.7"/><rect class="box" x="250" y="236" width="420" height="40" rx="7"/><text x="460.0" y="260.0" text-anchor="middle">Sentinel ×3  ·  quorum 2  ·  promotes a replica on failure</text><line class="ln dash" x1="330" y1="236" x2="330" y2="168"/><polygon class="hd" points="330.0,168.0 333.0,174.3 327.0,174.3"/></svg></div>

| Kukuh kerana | Bukti |
|---|---|
| Ketahanan data tanpa mengorbankan kelajuan | AOF `everysec` 97,087 req/s, p99 0.255 ms; `always` 17,203 req/s ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Failover automatik yang pantas | primary dihentikan → master baharu dinamakan dalam 4,402 ms; primary lama menyertai semula sebagai replika |
| Sandaran point-in-time tanpa menghentikan perkhidmatan | `BACKUP START`/`SEAL` (8.10) dipulihkan ke pelayan baharu dengan `preload-file` |

**Perhatikan:** replikasi bersifat tak segerak. Dokumentasi menyatakan "WAIT does not make Redis a strongly consistent store", dan `WAIT` hanya mengira pengakuan bagi penulisan daripada sambungan yang memanggilnya sendiri. Snapshot menyalin memori semasa penulisan: 252 MB copy-on-write bagi set data 214 MB di bawah penimpaan. Berikan alamat Sentinel yang kekal boleh diselesaikan: memantau nama kontena memanjangkan failover yang sama kepada 284 s.

Dokumentasi: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/).

### 3. Scale-out dengan Redis Cluster

Apabila memori atau CPU satu nod tidak mencukupi, Redis Cluster membahagikan keyspace kepada 16,384 hash slot merentas beberapa primary, masing-masing dengan replika. Klien mempelajari peta slot dan berhubung terus dengan nod yang betul.

<div class="arch" markdown="0"><svg viewBox="0 0 760 260" role="img" aria-label="Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot"><title>Redis Cluster: three shards, each a primary with a replica, keys routed by hash slot</title><rect class="box" x="20" y="105" width="150" height="60" rx="7"/><text x="95.0" y="132.0" text-anchor="middle">Cluster-aware client</text><text class="sm" x="95.0" y="148.0" text-anchor="middle">caches slot map</text><rect class="rd" x="250" y="40" width="150" height="56" rx="7"/><text x="325.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="325.0" y="81.0" text-anchor="middle">slots 0–5460</text><rect class="rd" x="250" y="165" width="150" height="50" rx="7"/><text x="325.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="325" y1="96" x2="325" y2="163"/><polygon class="hd" points="325.0,163.0 322.0,156.7 328.0,156.7"/><rect class="rd" x="420" y="40" width="150" height="56" rx="7"/><text x="495.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="495.0" y="81.0" text-anchor="middle">5461–10922</text><rect class="rd" x="420" y="165" width="150" height="50" rx="7"/><text x="495.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="495" y1="96" x2="495" y2="163"/><polygon class="hd" points="495.0,163.0 492.0,156.7 498.0,156.7"/><rect class="rd" x="590" y="40" width="150" height="56" rx="7"/><text x="665.0" y="65.0" text-anchor="middle">Primary</text><text class="sm" x="665.0" y="81.0" text-anchor="middle">10923–16383</text><rect class="rd" x="590" y="165" width="150" height="50" rx="7"/><text x="665.0" y="194.0" text-anchor="middle">Replica</text><line class="ln" x1="665" y1="96" x2="665" y2="163"/><polygon class="hd" points="665.0,163.0 662.0,156.7 668.0,156.7"/><line class="ln" x1="170" y1="125" x2="248" y2="70"/><polygon class="hd" points="248.0,70.0 244.6,76.1 241.1,71.1"/><text class="sm" x="209.0" y="91.5" text-anchor="middle">key → CRC16 mod 16384</text><text class="sm" x="495" y="245" text-anchor="middle">CLUSTER MIGRATION moves slot ranges between primaries atomically</text></svg></div>

| Kukuh kerana | Bukti |
|---|---|
| Pensharan semula (resharding) tanpa menghentikan penulisan | `CLUSTER MIGRATION IMPORT 0 999` memindahkan 1,000 slot dalam 44 ms dengan `write_pause_ms 0` di bawah ~200,000 penulisan/saat ([Deep Dive]({{ '/deep-dive/' | relative_url }})) |
| Penghalaan yang boleh diramal | `HASH_SLOT = CRC16(key) mod 16384`; nod yang salah menjawab `MOVED` bersama nod yang betul |

**Perhatikan:** arahan berbilang kunci mesti berada dalam satu slot. `MSET user:1 a user:2 b` memulangkan `CROSSSLOT`; hash tag yang dikongsi (`{user:1}:cart`, `{user:1}:orders`) mengekalkan kunci berkaitan bersama. ElastiCache Serverless berkelakuan sama ([Compare]({{ '/compare/' | relative_url }})). Spesifikasi menyatakan "Each master node in a cluster handles a subset of the 16384 hash slots".

Dokumentasi: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/).

### 4. Terurus di Redis Cloud

Enjin yang sama sebagai perkhidmatan. Essentials ialah satu pangkalan data pada infrastruktur kongsi dengan replikasi pilihan; Pro bersifat dedicated, menampung banyak pangkalan data, dan menambah salinan Active-Active di beberapa wilayah yang semuanya menerima penulisan.

<div class="arch" markdown="0"><svg viewBox="0 0 760 255" role="img" aria-label="Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro"><title>Redis Cloud: one replicated database on Essentials, Active-Active copies across regions on Pro</title><rect class="box" x="20" y="40" width="160" height="60" rx="7"/><text x="100.0" y="74.0" text-anchor="middle">App, region A</text><rect class="box" x="20" y="160" width="160" height="60" rx="7"/><text x="100.0" y="194.0" text-anchor="middle">App, region B</text><rect class="box" x="270" y="20" width="230" height="100" rx="7"/><text x="385.0" y="74.0" text-anchor="middle"></text><text x="385" y="44" text-anchor="middle">Redis Cloud · Essentials</text><rect class="rd" x="290" y="58" width="190" height="46" rx="7"/><text x="385.0" y="78.0" text-anchor="middle">one database</text><text class="sm" x="385.0" y="94.0" text-anchor="middle">replica in-zone or multi-AZ</text><rect class="box" x="270" y="140" width="470" height="100" rx="7"/><text x="505.0" y="194.0" text-anchor="middle"></text><text x="505" y="163" text-anchor="middle">Redis Cloud · Pro · Active-Active</text><rect class="rd" x="290" y="178" width="190" height="46" rx="7"/><text x="385.0" y="198.0" text-anchor="middle">copy in region A</text><text class="sm" x="385.0" y="214.0" text-anchor="middle">read + write</text><rect class="rd" x="530" y="178" width="190" height="46" rx="7"/><text x="625.0" y="198.0" text-anchor="middle">copy in region B</text><text class="sm" x="625.0" y="214.0" text-anchor="middle">read + write</text><line class="ln" x1="480" y1="201" x2="528" y2="201"/><polygon class="hd" points="528.0,201.0 521.7,204.0 521.7,198.0"/><polygon class="hd" points="480.0,201.0 486.3,198.0 486.3,204.0"/><text class="sm" x="504.0" y="195.0" text-anchor="middle">CRDT sync</text><line class="ln" x1="180" y1="70" x2="288" y2="80"/><polygon class="hd" points="288.0,80.0 281.4,82.5 282.0,76.4"/><line class="ln" x1="180" y1="190" x2="288" y2="200"/><polygon class="hd" points="288.0,200.0 281.4,202.5 282.0,196.4"/></svg></div>

| Kukuh kerana | Bukti |
|---|---|
| Pangkalan data dalam beberapa saat, modul disertakan | pangkalan data percuma sedia beberapa saat selepas borang, Search dan JSON tersedia ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| Automasi sejak hari pertama | REST API berfungsi pada pelan percuma ([Redis Cloud]({{ '/cloud/' | relative_url }})) |
| Penulisan di setiap wilayah (Pro) | reka bentuk sahaja di sini; dokumentasi menyatakan "Active-Active databases allow read and write operations in each copy", diselaraskan oleh CRDT |

**Perhatikan:** pelan percuma adalah untuk mencuba: 30 MB, 30 sambungan, tiada TLS (API menolak `enableTls`). Harga yang dibaca di konsol pada 2026-11-07: Essentials bermula $5 sebulan, Pro bermula $200 sebulan.

Dokumentasi: [Redis Cloud](https://redis.io/docs/latest/operate/rc/), [High availability](https://redis.io/docs/latest/operate/rc/databases/configuration/high-availability/), [Active-Active](https://redis.io/docs/latest/operate/rc/databases/active-active/).

### 5. Lapisan konteks untuk ejen AI: Redis Iris

Iris meletakkan perkhidmatan di sekeliling ejen supaya ia tidak perlu membina semula konteks pada setiap giliran. Dokumentasi menyatakan "Redis Iris is a production-ready context engine for AI agents" yang "adds persistent memory", "answers recurring questions without a model call", memberi ejen "one MCP endpoint for the tools of any MCP server and your Redis data", dan "routes each message". Agent Memory menyimpan datanya dalam pangkalan data Redis milik anda.

<div class="arch" markdown="0"><svg viewBox="0 0 780 320" role="img" aria-label="Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database"><title>Redis Iris around an agent: routing, memory, playbooks, tools and tracing, backed by a Redis database</title><rect class="box" x="20" y="110" width="110" height="56" rx="7"/><text x="75.0" y="142.0" text-anchor="middle">User</text><rect class="box" x="180" y="100" width="170" height="76" rx="7"/><text x="265.0" y="135.0" text-anchor="middle">Agent app</text><text class="sm" x="265.0" y="151.0" text-anchor="middle">LLM + your code</text><line class="ln" x1="130" y1="138" x2="178" y2="138"/><polygon class="hd" points="178.0,138.0 171.7,141.0 171.7,135.0"/><rect class="rd" x="430" y="20" width="190" height="48" rx="7"/><text x="525.0" y="41.0" text-anchor="middle">Intent Router</text><text class="sm" x="525.0" y="57.0" text-anchor="middle">route before the LLM</text><line class="ln" x1="350" y1="138" x2="428" y2="44"/><polygon class="hd" points="428.0,44.0 426.3,50.8 421.6,46.9"/><rect class="rd" x="430" y="80" width="190" height="48" rx="7"/><text x="525.0" y="101.0" text-anchor="middle">Agent Memory</text><text class="sm" x="525.0" y="117.0" text-anchor="middle">remember · recall</text><line class="ln" x1="350" y1="138" x2="428" y2="104"/><polygon class="hd" points="428.0,104.0 423.4,109.3 421.0,103.7"/><rect class="rd" x="430" y="140" width="190" height="48" rx="7"/><text x="525.0" y="161.0" text-anchor="middle">Agent Playbooks</text><text class="sm" x="525.0" y="177.0" text-anchor="middle">approved answers</text><line class="ln" x1="350" y1="138" x2="428" y2="164"/><polygon class="hd" points="428.0,164.0 421.1,164.9 423.0,159.1"/><rect class="rd" x="430" y="200" width="190" height="48" rx="7"/><text x="525.0" y="221.0" text-anchor="middle">Context Gateway</text><text class="sm" x="525.0" y="237.0" text-anchor="middle">one MCP endpoint</text><line class="ln" x1="350" y1="138" x2="428" y2="224"/><polygon class="hd" points="428.0,224.0 421.5,221.4 426.0,217.3"/><rect class="rd" x="430" y="260" width="190" height="48" rx="7"/><text x="525.0" y="281.0" text-anchor="middle">Lens</text><text class="sm" x="525.0" y="297.0" text-anchor="middle">trace each turn</text><line class="ln" x1="350" y1="138" x2="428" y2="284"/><polygon class="hd" points="428.0,284.0 422.3,279.9 427.7,277.0"/><rect class="rd" x="660" y="100" width="100" height="70" rx="7"/><text x="710.0" y="132.0" text-anchor="middle">Redis DB</text><text class="sm" x="710.0" y="148.0" text-anchor="middle">JSON + Search</text><line class="ln dash" x1="620" y1="104" x2="658" y2="125"/><polygon class="hd" points="658.0,125.0 651.0,124.6 654.0,119.3"/><line class="ln dash" x1="620" y1="216" x2="658" y2="150"/><polygon class="hd" points="658.0,150.0 657.5,157.0 652.2,153.9"/><rect class="box" x="660" y="230" width="100" height="56" rx="7"/><text x="710.0" y="255.0" text-anchor="middle">MCP servers</text><text class="sm" x="710.0" y="271.0" text-anchor="middle">your tools</text><line class="ln dash" x1="620" y1="232" x2="658" y2="252"/><polygon class="hd" points="658.0,252.0 651.0,251.8 653.8,246.4"/></svg></div>

| Kukuh kerana | Bukti |
|---|---|
| Memori yang membina dirinya sendiri | satu fakta daripada perbualan dua giliran diekstrak kira-kira 15 s kemudian ([Iris]({{ '/iris/' | relative_url }})) |
| Data kekal dalam pangkalan data anda | Agent Memory menulis dokumen JSON dan empat indeks Search ke dalam pangkalan data percuma ([Iris]({{ '/iris/' | relative_url }})) |
| Kunci berskop bagi setiap produk dan sumber | kunci baca boleh membuat recall tetapi mendapat 403 semasa menulis ([Iris]({{ '/iris/' | relative_url }})) |
| Giliran yang lebih murah | Intent Router dan Agent Playbooks menjawab atau menghalakan sebelum panggilan model: reka bentuk sahaja di sini |

**Perhatikan:** tempat perkhidmatan berjalan: titik akhir Agent Memory berada di us-east-1 manakala pangkalan data di Seoul, dan recall dari Korea mengambil median 611 ms. Pengukuran mesej (metering) tidak kelihatan di mana-mana dalam konsol. Intent Router, Playbooks, Context Gateway dan Lens belum dijalankan.

Dokumentasi: [Redis Iris](https://redis.io/docs/latest/develop/ai/context-engine/), [Agent Memory](https://redis.io/docs/latest/operate/iris/agent-memory/), [Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/), [Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/), [Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/), [Lens](https://redis.io/docs/latest/operate/iris/lens/).

### 6. Carian dan vektor di sebelah data

Rekod, indeks sekunder dan embedding berada dalam pangkalan data Redis yang sama, jadi pertanyaan tidak perlu merentasi ke sistem lain.

<div class="arch" markdown="0"><svg viewBox="0 0 760 215" role="img" aria-label="Search and vectors in the same Redis database as the records"><title>Search and vectors in the same Redis database as the records</title><rect class="box" x="20" y="80" width="150" height="60" rx="7"/><text x="95.0" y="114.0" text-anchor="middle">Application</text><rect class="rd" x="300" y="20" width="420" height="180" rx="7"/><text x="510.0" y="114.0" text-anchor="middle"></text><text x="510" y="44" text-anchor="middle">one Redis 8 database</text><rect class="box" x="320" y="60" width="170" height="52" rx="7"/><text x="405.0" y="83.0" text-anchor="middle">Hashes / JSON</text><text class="sm" x="405.0" y="99.0" text-anchor="middle">the records</text><rect class="box" x="530" y="60" width="170" height="52" rx="7"/><text x="615.0" y="83.0" text-anchor="middle">Search index</text><text class="sm" x="615.0" y="99.0" text-anchor="middle">text · numeric · vector</text><rect class="box" x="320" y="128" width="380" height="52" rx="7"/><text x="510.0" y="151.0" text-anchor="middle">Vector set (beta)</text><text class="sm" x="510.0" y="167.0" text-anchor="middle">VADD · VSIM, no index to define</text><line class="ln" x1="490" y1="86" x2="528" y2="86"/><polygon class="hd" points="528.0,86.0 521.7,89.0 521.7,83.0"/><line class="ln" x1="170" y1="110" x2="298" y2="110"/><polygon class="hd" points="298.0,110.0 291.7,113.0 291.7,107.0"/><text class="sm" x="234.0" y="104.0" text-anchor="middle">FT.SEARCH / VSIM</text></svg></div>

| Kukuh kerana | Bukti |
|---|---|
| Terbina dalam, tanpa konfigurasi | Search, JSON dan vector set dimuatkan bersama imej Redis 8 stok ([Setup]({{ '/setup/' | relative_url }})) |
| Satu bahasa pertanyaan untuk teks, nombor dan vektor | `FT.CREATE` ke atas hash, julat berangka dan ujian indeks vektor dijalankan pada Redis 8.10.3 ([Compare]({{ '/compare/' | relative_url }})) |
| Jenis vektor natif | `VADD` dan `VSIM` berfungsi tanpa mentakrifkan indeks |

**Perhatikan:** vector set masih beta. Perkaitan dan kelajuan pada skala besar tidak diukur di sini; makmal Search setempat masih dirancang.

Dokumentasi: [Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/).

</div>
