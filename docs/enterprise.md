---
layout: default
title: Enterprise
permalink: /enterprise/
---

# Enterprise

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: run.** Redis Software in Docker, the Kubernetes operator on kind, and RDI from Postgres were run on 2026-11-07 (below).
</div>

What Redis Software and Redis Cloud Pro add over Redis Open Source — Active-Active (CRDT), Redis Flex (RAM + SSD), the DMC proxy and sharding policies, the 99.999 % SLA, RBAC/LDAP/TLS, RDI, the Kubernetes operator, Redis Insight, multi-tenancy. A table first: feature, where it exists, and whether a lab shows it or the page is doc-only. Vendor claims and measured results are kept apart.

### What Redis Software and Cloud Pro add, and what was run

| Feature | Where | On this site |
|---|---|---|
| DMC proxy, sharding, proxy policies, re-sharding | Software, Cloud | run: below |
| Several databases on one node (multi-tenancy) | Software | run: below |
| Active-Active (CRDT) | Software, Cloud Pro | design only; see [Architecture]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | doc only: needs local NVMe |
| 99.999% SLA | Cloud Pro with Active-Active | doc only: cannot be measured in a lab |
| RBAC, LDAP, TLS everywhere | Software, Cloud | RBAC screens on the [Redis Cloud page]({{ '/cloud/' | relative_url }}); LDAP and TLS not run |
| RDI (change data capture into Redis) | Software; managed on Cloud Pro | run: below, on kind |
| Kubernetes operator | Software | run: below, on kind |
| Redis Insight | all | run on the [Setup page]({{ '/setup/' | relative_url }}) |

### Lab: Redis Software in one container

**Verified on Redis Software 8.2.6-25, Redis 8.8 databases, 2026-11-07.** A single-node cluster from `redislabs/redis:8.2.6-25.21`, driven through its REST API. Source and output: [`enterprise/01-redis-software-docker`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/01-redis-software-docker). Docs: [Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

| Experiment | Result |
|---|---|
| Trial licence, read from `/v1/license` | 30 days from cluster creation, at most 4 shards |
| A fifth shard | refused: "License permits 4 total shards, but there are 5 total shards in use." |
| Container start → API → cluster → database | about 10 s, 10 s, 1 s |
| Two databases on one node | separate endpoints, separate data |
| `MGET` / `MSET` across shards behind the proxy | worked |
| `MULTI`/`EXEC` across slots | refused; worked with a shared hash tag |
| Replication on one node | refused: "Not enough nodes to perform replication" |
| Re-shard 2 → 4 with 10,000 keys | about 6 s, all keys kept |

The proxy is what makes a sharded database look like one Redis to a plain client: multi-key reads and writes cross shards, transactions do not.

**Modules and TLS** (`tls.py`). The cluster ships JSON, Bloom, Search and time series in several versions each, and no RedisGears. A database with `tls_mode: enabled` closed plain TCP connections; a client connected only with the cluster's proxy certificate (`GET /v1/cluster/certificates`) as its CA, and a PING round trip on that connection took 0.13 ms.

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="Cluster Manager UI databases list with db-b, 4 shards" loading="lazy" decoding="async"></p>

Cluster Manager UI: the databases list after re-sharding. <small>Captured 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="Cluster overview: version 8.2.6-25, license usage, storage, one node" loading="lazy" decoding="async"></p>

Overview: software version, licence expiry in 29 days, storage and nodes. <small>Captured 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="Cluster configuration: Redis database versions 8.8.0 to 8.0.2, used shards 4 of 4" loading="lazy" decoding="async"></p>

The cluster page lists the database versions on offer and the shard usage against the licence. <small>Captured 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="Database db-b configuration: 4 shards, proxy all primary shards, capabilities Search, JSON, Time Series, Probabilistic" loading="lazy" decoding="async"></p>

Database settings: sharding, OSS Cluster API off, proxy policy, capabilities and durability in one place. <small>Captured 2026-11-07, Redis Software 8.2.6-25.</small>

### Lab: the Kubernetes operator on kind

**Verified on Redis Enterprise operator 8.2.6-21 (cluster 8.2.6-25) on kind v0.33.0, Kubernetes v1.34.11, 2026-11-07.** From the docs: "You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." One `helm install` created the operator and a three-node cluster (REC); databases are `RedisEnterpriseDatabase` (REDB) resources.

| Step | Result |
|---|---|
| `helm install` with `cluster.create: true` | REC `Running` after 257 s; trial licence valid 30 days, 4 shards |
| Two REDBs (`rdi-state`, `target` with a replica) | `active` after 13 s, three shards in use |
| A REDB that needs two more shards | refused at `kubectl apply` by the admission webhook: "License permits 4 total shards, but there are 5 total shards in use." |
| Delete the pod with `target`'s primary shard while writing every 50 ms | replica promoted; 1.3 s of refused connections, no lost writes; pod back as replica after 73–82 s |

**On a cgroup v1 host, pin an older kind node image.** Kubernetes 1.35 and later refuse cgroup v1 by default (`failCgroupV1`), so kind's default v1.37.0 image failed on this Ubuntu 20.04 host; v1.34.11 works. Docs: [Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/). Lab: [`enterprise/03-operator-kind`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/03-operator-kind).

### Lab: RDI from Postgres

**Verified on RDI 2.2.1 (Debezium 3.5.0, Flink processor), Postgres 17.11, Redis Enterprise 8.2.6-25 on kind, 2026-11-07.** From the docs: "Redis Data Integration (RDI) keeps your Redis cache in sync with a primary system-of-record database in near real time." The source is 1,000 made-up customers in Postgres. One job adds a `tier` field from `credit_limit`, drops `email`, and writes JSON under `customer:<id>`. RDI keeps its state in the non-clustered `rdi-state` database from the operator lab.

| Step | Result |
|---|---|
| RDI Helm chart | installed in 32 s: API, operator, reloader pods |
| `redis-di deploy` | 67 s; collector (Debezium) and Flink job and task managers start; 1,000 rows in Redis 1 s later, transformed |
| One-row UPDATE / INSERT / DELETE, three runs | visible in Redis after 0.2–1.5 s / 0.8–1.1 s / 0.4–1.1 s |
| UPDATE of all 1,000 rows in one transaction | visible after 0.8–1.5 s |

The latencies include about 0.11 s of `kubectl exec` and come from one host, so read them as an order of magnitude. With no processor type set, the pipeline ran on Flink, the default since RDI 2.0. `redis-di describe` showed the target as "Connected: no" while rows were arriving; that was not investigated. Docs: [RDI overview](https://redis.io/docs/latest/integrate/redis-data-integration/), [Install on Kubernetes](https://redis.io/docs/latest/integrate/redis-data-integration/installation/install-k8s/), [Pipeline configuration](https://redis.io/docs/latest/integrate/redis-data-integration/data-pipelines/pipeline-config/). Lab: [`enterprise/02-rdi`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/02-rdi).

**Classic processor and write-behind** (`classic.sh`). With `processors.type: classic` the same pipeline ran in one `processor` pod instead of Flink's job and task managers, with changes visible in 0.2–1.1 s. Write-behind (Redis to a database) is not in the RDI 2.2 documentation; the older write-behind engine needs RedisGears Python 1.2.6, which Redis Software 8.2.6 does not ship, so it could not be run.

### Not run yet

Active-Active needs Redis Cloud Pro or several Redis Software clusters, and Redis Flex needs local NVMe; both stay doc-only here. Managed RDI on Redis Cloud is Pro only.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 실행함.** Docker의 Redis Software, kind 위의 Kubernetes operator, Postgres에서의 RDI를 2026-11-07에 실행했다(아래).
</div>

Redis Software와 Redis Cloud Pro가 Redis Open Source에 더해 주는 것 — Active-Active(CRDT), Redis Flex(RAM + SSD), DMC 프록시와 샤딩 정책, 99.999 % SLA, RBAC/LDAP/TLS, RDI, Kubernetes 오퍼레이터, Redis Insight, 멀티테넌시. 표를 먼저: 기능, 어디에 있나, 랩으로 보이는지 문서만인지. 벤더 주장과 측정 결과는 구분한다.

### Redis Software와 Cloud Pro가 더하는 것, 그리고 실행한 것

| 기능 | 어디에 | 이 사이트에서 |
|---|---|---|
| DMC 프록시, 샤딩, 프록시 정책, 재샤딩 | Software, Cloud | 실행: 아래 |
| 한 노드에 DB 여러 개(멀티 테넌시) | Software | 실행: 아래 |
| Active-Active(CRDT) | Software, Cloud Pro | 설계만. [Architecture]({{ '/architecture/' | relative_url }}) 참고 |
| Redis Flex(RAM + SSD) | Software, Cloud | 문서만: 로컬 NVMe 필요 |
| 99.999% SLA | Active-Active를 쓰는 Cloud Pro | 문서만: 실습으로 잴 수 없음 |
| RBAC, LDAP, 어디서나 TLS | Software, Cloud | RBAC 화면은 [Redis Cloud 페이지]({{ '/cloud/' | relative_url }}), LDAP과 TLS는 미실행 |
| RDI(Redis로의 변경 데이터 캡처) | Software, Cloud Pro는 관리형 | 실행: 아래, kind에서 |
| Kubernetes operator | Software | 실행: 아래, kind에서 |
| Redis Insight | 전부 | [Setup 페이지]({{ '/setup/' | relative_url }})에서 실행 |

### 실습: 컨테이너 하나의 Redis Software

**확인: Redis Software 8.2.6-25, Redis 8.8 DB, 2026-11-07.** `redislabs/redis:8.2.6-25.21`의 단일 노드 클러스터를 REST API로 다뤘다. 소스와 출력: [`enterprise/01-redis-software-docker`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/01-redis-software-docker). 문서: [Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

| 실험 | 결과 |
|---|---|
| 체험 라이선스, `/v1/license`에서 읽음 | 클러스터 생성부터 30일, 최대 4샤드 |
| 5번째 샤드 | 거절: "License permits 4 total shards, but there are 5 total shards in use." |
| 컨테이너 시작 → API → 클러스터 → DB | 약 10초, 10초, 1초 |
| 한 노드에 DB 둘 | 엔드포인트도 데이터도 따로 |
| 프록시 뒤에서 샤드를 넘는 `MGET` / `MSET` | 됨 |
| 슬롯을 넘는 `MULTI`/`EXEC` | 거절. 해시 태그를 공유하면 됨 |
| 노드 하나에서 복제 | 거절: "Not enough nodes to perform replication" |
| 키 10,000개로 2 → 4샤드 재샤딩 | 약 6초, 키 모두 유지 |

샤드가 나뉜 DB가 일반 클라이언트에게 Redis 하나처럼 보이게 하는 것이 프록시다. 여러 키 읽기·쓰기는 샤드를 넘지만 트랜잭션은 넘지 않는다.

**모듈과 TLS**(`tls.py`). 클러스터에는 JSON, Bloom, Search, time series가 버전 여러 개씩 들어 있고 RedisGears는 없다. `tls_mode: enabled`인 DB는 평문 TCP 연결을 끊었고, 클라이언트는 클러스터 프록시 인증서(`GET /v1/cluster/certificates`)를 CA로 줬을 때만 연결됐다. 그 연결에서 PING 왕복은 0.13 ms.

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="샤드 4개인 db-b가 있는 Cluster Manager UI의 DB 목록" loading="lazy" decoding="async"></p>

Cluster Manager UI: 재샤딩 뒤의 DB 목록. <small>2026-11-07 캡처, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="클러스터 개요: 버전 8.2.6-25, 라이선스 사용량, 저장 공간, 노드 하나" loading="lazy" decoding="async"></p>

개요: 소프트웨어 버전, 29일 뒤 라이선스 만료, 저장 공간과 노드. <small>2026-11-07 캡처, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="클러스터 설정: Redis DB 버전 8.8.0부터 8.0.2, 사용 샤드 4/4" loading="lazy" decoding="async"></p>

클러스터 화면은 고를 수 있는 DB 버전과 라이선스 대비 샤드 사용량을 보여 준다. <small>2026-11-07 캡처, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="DB db-b 설정: 4샤드, 프록시 모든 주 샤드, 기능 Search·JSON·Time Series·확률형" loading="lazy" decoding="async"></p>

DB 설정: 샤딩, OSS Cluster API 꺼짐, 프록시 정책, 기능, 내구성이 한곳에 있다. <small>2026-11-07 캡처, Redis Software 8.2.6-25.</small>

### 실습: kind 위의 Kubernetes operator

**확인: Redis Enterprise operator 8.2.6-21(클러스터 8.2.6-25), kind v0.33.0, Kubernetes v1.34.11, 2026-11-07.** 문서의 표현: "You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." `helm install` 한 번이 operator와 노드 셋짜리 클러스터(REC)를 만들었다. DB는 `RedisEnterpriseDatabase`(REDB) 리소스다.

| 단계 | 결과 |
|---|---|
| `cluster.create: true`로 `helm install` | 257초 뒤 REC `Running`. 체험 라이선스 30일, 샤드 4개 |
| REDB 둘(`rdi-state`, 복제본 있는 `target`) | 13초 뒤 `active`, 샤드 3개 사용 |
| 샤드가 둘 더 필요한 REDB | admission webhook이 `kubectl apply`에서 거절: "License permits 4 total shards, but there are 5 total shards in use." |
| 50 ms마다 쓰는 중에 `target`의 주 샤드가 있는 파드 삭제 | 복제본 승격. 1.3초 연결 거절, 잃은 쓰기 없음. 파드는 73–82초 뒤 복제본으로 복귀 |

**cgroup v1 호스트에서는 이전 kind 노드 이미지를 고정한다.** Kubernetes 1.35부터 기본으로 cgroup v1을 거부하므로(`failCgroupV1`) kind의 기본 v1.37.0 이미지는 이 Ubuntu 20.04 호스트에서 실패했다. v1.34.11은 동작한다. 문서: [Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/). 실습: [`enterprise/03-operator-kind`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/03-operator-kind).

### 실습: Postgres에서 RDI

**확인: RDI 2.2.1(Debezium 3.5.0, Flink 프로세서), Postgres 17.11, kind 위 Redis Enterprise 8.2.6-25, 2026-11-07.** 문서의 표현: "Redis Data Integration (RDI) keeps your Redis cache in sync with a primary system-of-record database in near real time." 원천은 Postgres의 가상 고객 1,000명이다. 작업 하나가 `credit_limit`에서 `tier` 필드를 만들고 `email`을 빼고 `customer:<id>`에 JSON으로 쓴다. RDI는 operator 실습의 클러스터가 아닌(non-clustered) `rdi-state` DB에 상태를 둔다.

| 단계 | 결과 |
|---|---|
| RDI Helm 차트 | 32초에 설치: API, operator, reloader 파드 |
| `redis-di deploy` | 67초. collector(Debezium)와 Flink job·task manager 시작. 1초 뒤 1,000행이 변환된 채 Redis에 |
| 한 행 UPDATE / INSERT / DELETE, 세 번 실행 | Redis에 보이기까지 0.2–1.5초 / 0.8–1.1초 / 0.4–1.1초 |
| 한 트랜잭션으로 1,000행 전부 UPDATE | 0.8–1.5초 뒤 보임 |

지연에는 `kubectl exec` 약 0.11초가 들어 있고 호스트 하나에서 쟀으므로 규모로만 읽는다. 프로세서 종류를 정하지 않으면 RDI 2.0부터의 기본값인 Flink로 돈다. 행이 들어오는 동안에도 `redis-di describe`는 대상을 "Connected: no"로 표시했다. 조사하지 않았다. 문서: [RDI overview](https://redis.io/docs/latest/integrate/redis-data-integration/), [Install on Kubernetes](https://redis.io/docs/latest/integrate/redis-data-integration/installation/install-k8s/), [Pipeline configuration](https://redis.io/docs/latest/integrate/redis-data-integration/data-pipelines/pipeline-config/). 실습: [`enterprise/02-rdi`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/02-rdi).

**classic 프로세서와 write-behind**(`classic.sh`). `processors.type: classic`이면 같은 파이프라인이 Flink의 job·task manager 대신 `processor` 파드 하나로 돌았고, 변경은 0.2–1.1초 안에 보였다. write-behind(Redis에서 DB로)는 RDI 2.2 문서에 없다. 예전 write-behind 엔진은 RedisGears Python 1.2.6이 필요한데 Redis Software 8.2.6에는 없어서 실행할 수 없었다.

### 아직 실행하지 않은 것

Active-Active는 Redis Cloud Pro나 Redis Software 클러스터 여러 개가, Redis Flex는 로컬 NVMe가 필요하다. 둘 다 여기서는 문서만으로 다룬다. Redis Cloud의 관리형 RDI는 Pro 전용이다.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：已运行。** Docker 中的 Redis Software、kind 上的 Kubernetes operator，以及从 Postgres 到 Redis 的 RDI，均已于 2026-11-07 运行（见下文）。
</div>

Redis Software 和 Redis Cloud Pro 在 Redis Open Source 之上增加了什么——Active-Active（CRDT）、Redis Flex（RAM + SSD）、DMC 代理与分片策略、99.999 % SLA、RBAC/LDAP/TLS、RDI、Kubernetes operator、Redis Insight、多租户。先给出一张表：功能、存在于何处，以及是有实验演示，还是仅有文档。厂商的说法与实测结果分开列出。

### Redis Software 与 Cloud Pro 增加了什么，以及运行了什么

| 功能 | 位置 | 本站情况 |
|---|---|---|
| DMC 代理、分片、代理策略、重新分片 | Software、Cloud | 已运行：见下 |
| 同一节点上的多个数据库（多租户） | Software | 已运行：见下 |
| Active-Active（CRDT） | Software、Cloud Pro | 仅有设计；见 [架构]({{ '/architecture/' | relative_url }}) |
| Redis Flex（RAM + SSD） | Software、Cloud | 仅有文档：需要本地 NVMe |
| 99.999% SLA | 带 Active-Active 的 Cloud Pro | 仅有文档：无法在实验中测量 |
| RBAC、LDAP、全程 TLS | Software、Cloud | RBAC 界面见 [Redis Cloud 页面]({{ '/cloud/' | relative_url }})；LDAP 和 TLS 未运行 |
| RDI（将变更数据捕获写入 Redis） | Software；Cloud Pro 上为托管 | 已运行：见下，在 kind 上 |
| Kubernetes operator | Software | 已运行：见下，在 kind 上 |
| Redis Insight | 全部 | 已在 [安装页面]({{ '/setup/' | relative_url }}) 运行 |

### 实验：一个容器中的 Redis Software

**在 Redis Software 8.2.6-25、Redis 8.8 数据库上验证，2026-11-07。** 单节点集群，来自 `redislabs/redis:8.2.6-25.21`，通过其 REST API 驱动。源码与输出：[`enterprise/01-redis-software-docker`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/01-redis-software-docker). 文档：[Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

| 实验 | 结果 |
|---|---|
| 试用许可证，从 `/v1/license` 读取 | 自集群创建起 30 天，最多 4 个分片 |
| 第五个分片 | 被拒绝："License permits 4 total shards, but there are 5 total shards in use." |
| 容器启动 → API → 集群 → 数据库 | 约 10 秒、10 秒、1 秒 |
| 一个节点上的两个数据库 | 端点各自独立，数据各自独立 |
| 代理之后跨分片的 `MGET` / `MSET` | 正常 |
| 跨槽的 `MULTI`/`EXEC` | 被拒绝；使用共享哈希标签后正常 |
| 单节点上的复制 | 被拒绝："Not enough nodes to perform replication" |
| 用 10,000 个键从 2 个分片重新分片到 4 个 | 约 6 秒，所有键保留 |

代理让分片数据库在普通客户端看来就像一个 Redis：多键读写可以跨分片，事务则不行。

**模块与 TLS**（`tls.py`）。集群自带 JSON、Bloom、Search 和 time series，每个都有多个版本，没有 RedisGears。`tls_mode: enabled` 的数据库关闭了明文 TCP 连接；客户端只有把集群的代理证书（`GET /v1/cluster/certificates`）作为 CA 才能连上，该连接上一次 PING 往返耗时 0.13 ms。

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="Cluster Manager UI 的数据库列表，其中 db-b 有 4 个分片" loading="lazy" decoding="async"></p>

Cluster Manager UI：重新分片之后的数据库列表。 <small>2026-11-07 截取，Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="集群概览：版本 8.2.6-25、许可证用量、存储、一个节点" loading="lazy" decoding="async"></p>

概览：软件版本、29 天后许可证到期、存储与节点。 <small>2026-11-07 截取，Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="集群配置：Redis 数据库版本 8.8.0 至 8.0.2，已用分片 4/4" loading="lazy" decoding="async"></p>

集群页面列出可选的数据库版本，以及相对许可证的分片用量。 <small>2026-11-07 截取，Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="数据库 db-b 配置：4 个分片、代理为所有主分片、功能 Search、JSON、Time Series、概率型" loading="lazy" decoding="async"></p>

数据库设置：分片、OSS Cluster API 关闭、代理策略、功能与持久性集中在一处。 <small>2026-11-07 截取，Redis Software 8.2.6-25。</small>

### 实验：kind 上的 Kubernetes operator

**在 Redis Enterprise operator 8.2.6-21（集群 8.2.6-25）、kind v0.33.0、Kubernetes v1.34.11 上验证，2026-11-07。** 文档中写道："You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." 一次 `helm install` 创建了 operator 和一个三节点集群（REC）；数据库是 `RedisEnterpriseDatabase`（REDB）资源。

| 步骤 | 结果 |
|---|---|
| 使用 `cluster.create: true` 执行 `helm install` | REC 在 257 秒后 `Running`；试用许可证有效期 30 天，4 个分片 |
| 两个 REDB（`rdi-state`，以及带副本的 `target`） | 13 秒后 `active`，使用了三个分片 |
| 一个还需要两个分片的 REDB | 在 `kubectl apply` 时被准入 webhook 拒绝："License permits 4 total shards, but there are 5 total shards in use." |
| 在每 50 毫秒写入一次的同时，删除承载 `target` 主分片的 pod | 副本被提升；连接被拒绝 1.3 秒，没有丢失写入；pod 在 73–82 秒后作为副本回归 |

**在 cgroup v1 主机上，请固定较旧的 kind 节点镜像。** Kubernetes 1.35 及更高版本默认拒绝 cgroup v1（`failCgroupV1`），因此 kind 默认的 v1.37.0 镜像在这台 Ubuntu 20.04 主机上失败；v1.34.11 可以正常工作。 文档：[Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/). 实验：[`enterprise/03-operator-kind`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/03-operator-kind).

### 实验：从 Postgres 到 RDI

**在 RDI 2.2.1（Debezium 3.5.0、Flink processor）、Postgres 17.11、kind 上的 Redis Enterprise 8.2.6-25 上验证，2026-11-07。** 文档中写道："Redis Data Integration (RDI) keeps your Redis cache in sync with a primary system-of-record database in near real time." 数据源是 Postgres 中 1,000 条虚构的客户记录。一个 job 根据 `credit_limit` 添加 `tier` 字段，丢弃 `email`，并把 JSON 写到 `customer:<id>` 之下。RDI 将其状态保存在 operator 实验中的非集群数据库 `rdi-state` 里。

| 步骤 | 结果 |
|---|---|
| RDI Helm chart | 32 秒完成安装：API、operator、reloader 三个 pod |
| `redis-di deploy` | 67 秒；collector（Debezium）、Flink 作业以及 task manager 启动；1 秒后 Redis 中出现 1,000 行，且已转换 |
| 单行 UPDATE / INSERT / DELETE，各运行三次 | 分别在 0.2–1.5 秒 / 0.8–1.1 秒 / 0.4–1.1 秒后在 Redis 中可见 |
| 在一个事务中 UPDATE 全部 1,000 行 | 0.8–1.5 秒后可见 |

这些延迟包含约 0.11 秒的 `kubectl exec`，且来自同一台主机，因此只应视为数量级。未设置 processor 类型时，管道在 Flink 上运行，这是自 RDI 2.0 起的默认值。管道在接收行的同时，`redis-di describe` 却把目标显示为 "Connected: no"；对此没有深入调查。 文档：[RDI overview](https://redis.io/docs/latest/integrate/redis-data-integration/), [Install on Kubernetes](https://redis.io/docs/latest/integrate/redis-data-integration/installation/install-k8s/), [Pipeline configuration](https://redis.io/docs/latest/integrate/redis-data-integration/data-pipelines/pipeline-config/). 实验：[`enterprise/02-rdi`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/02-rdi).

**classic 处理器与 write-behind**（`classic.sh`）。设置 `processors.type: classic` 后，同一条管道在一个 `processor` pod 中运行，而不是 Flink 的 job 和 task manager，变更在 0.2–1.1 秒内可见。write-behind（从 Redis 写到数据库）不在 RDI 2.2 文档中；旧的 write-behind 引擎需要 RedisGears Python 1.2.6，而 Redis Software 8.2.6 并未提供，所以无法运行。

### 尚未运行

Active-Active 需要 Redis Cloud Pro 或多个 Redis Software 集群，Redis Flex 需要本地 NVMe；两者在这里都只有文档。Redis Cloud 上的托管 RDI 仅限 Pro。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**ステータス: 実行済み。** Docker 上の Redis Software、kind 上の Kubernetes operator、Postgres からの RDI を 2026-11-07 に実行した（下記）。
</div>

Redis Software と Redis Cloud Pro が Redis Open Source に加えるもの — Active-Active（CRDT）、Redis Flex（RAM + SSD）、DMC プロキシとシャーディングポリシー、99.999 % の SLA、RBAC/LDAP/TLS、RDI、Kubernetes operator、Redis Insight、マルチテナンシー。最初に表を示す。機能、それがどこにあるか、ラボで確認したのかドキュメントのみなのか。ベンダーの主張と実測結果は分けて記す。

### Redis Software と Cloud Pro が加えるものと、実行したもの

| 機能 | 提供先 | このサイトでは |
|---|---|---|
| DMC プロキシ、シャーディング、プロキシポリシー、リシャーディング | Software、Cloud | 実行済み: 下記 |
| 1 ノード上の複数データベース（マルチテナンシー） | Software | 実行済み: 下記 |
| Active-Active（CRDT） | Software、Cloud Pro | 設計のみ。[アーキテクチャ]({{ '/architecture/' | relative_url }}) を参照 |
| Redis Flex（RAM + SSD） | Software、Cloud | ドキュメントのみ: ローカル NVMe が必要 |
| 99.999% SLA | Active-Active を使う Cloud Pro | ドキュメントのみ: ラボでは測定できない |
| RBAC、LDAP、すべての通信での TLS | Software、Cloud | RBAC の画面は [Redis Cloud のページ]({{ '/cloud/' | relative_url }}) に。LDAP と TLS は未実行 |
| RDI（変更データキャプチャを Redis へ） | Software。Cloud Pro ではマネージド | 実行済み: 下記、kind 上 |
| Kubernetes operator | Software | 実行済み: 下記、kind 上 |
| Redis Insight | すべて | [セットアップのページ]({{ '/setup/' | relative_url }}) で実行済み |

### ラボ: 1 つのコンテナで動く Redis Software

**Redis Software 8.2.6-25、Redis 8.8 データベースで確認、2026-11-07。** `redislabs/redis:8.2.6-25.21` による単一ノードのクラスター。REST API で操作した。ソースと出力: [`enterprise/01-redis-software-docker`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/01-redis-software-docker). ドキュメント: [Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

| 実験 | 結果 |
|---|---|
| 試用ライセンス（`/v1/license` から読み取り） | クラスター作成から 30 日、シャードは最大 4 つ |
| 5 つ目のシャード | 拒否された: "License permits 4 total shards, but there are 5 total shards in use." |
| コンテナ起動 → API → クラスター → データベース | 約 10 秒、10 秒、1 秒 |
| 1 ノード上の 2 つのデータベース | エンドポイントもデータも別々 |
| プロキシ越しのシャード間 `MGET` / `MSET` | 動作した |
| スロットをまたぐ `MULTI`/`EXEC` | 拒否された。共有ハッシュタグを使うと動作した |
| 1 ノードでのレプリケーション | 拒否された: "Not enough nodes to perform replication" |
| 10,000 キーで 2 → 4 にリシャード | 約 6 秒、全キー保持 |

プロキシのおかげで、シャーディングされたデータベースは通常のクライアントからは 1 つの Redis に見える。複数キーの読み書きはシャードをまたげるが、トランザクションはまたげない。

**モジュールと TLS**（`tls.py`）。クラスターには JSON、Bloom、Search、time series がそれぞれ複数のバージョンで入っていて、RedisGears はない。`tls_mode: enabled` のデータベースは平文の TCP 接続を切断し、クライアントはクラスターのプロキシ証明書（`GET /v1/cluster/certificates`）を CA として渡したときだけ接続できた。その接続での PING の往復は 0.13 ms だった。

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="シャード 4 つの db-b がある Cluster Manager UI のデータベース一覧" loading="lazy" decoding="async"></p>

Cluster Manager UI: リシャーディング後のデータベース一覧。 <small>2026-11-07 取得、Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="クラスター概要: バージョン 8.2.6-25、ライセンス使用量、ストレージ、ノード 1 つ" loading="lazy" decoding="async"></p>

概要: ソフトウェアバージョン、29 日後のライセンス期限、ストレージとノード。 <small>2026-11-07 取得、Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="クラスター設定: Redis データベースのバージョン 8.8.0 から 8.0.2、使用シャード 4/4" loading="lazy" decoding="async"></p>

クラスターページには、選べるデータベースバージョンと、ライセンスに対するシャード使用量が表示される。 <small>2026-11-07 取得、Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="データベース db-b の設定: 4 シャード、プロキシは全プライマリシャード、機能は Search、JSON、Time Series、確率的データ構造" loading="lazy" decoding="async"></p>

データベース設定: シャーディング、OSS Cluster API オフ、プロキシポリシー、機能、永続性が 1 か所にある。 <small>2026-11-07 取得、Redis Software 8.2.6-25。</small>

### ラボ: kind 上の Kubernetes operator

**Redis Enterprise operator 8.2.6-21（クラスター 8.2.6-25）、kind v0.33.0、Kubernetes v1.34.11 で確認、2026-11-07。** ドキュメントより: "You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." 1 回の `helm install` で operator と 3 ノードのクラスター（REC）が作られた。データベースは `RedisEnterpriseDatabase`（REDB）リソースである。

| 手順 | 結果 |
|---|---|
| `cluster.create: true` を付けた `helm install` | REC が 257 秒後に `Running`。試用ライセンスは 30 日有効、シャードは 4 つ |
| 2 つの REDB（`rdi-state` と、レプリカ付きの `target`） | 13 秒後に `active`、3 つのシャードを使用 |
| さらに 2 つのシャードが必要な REDB | `kubectl apply` の時点でアドミッション webhook に拒否された: "License permits 4 total shards, but there are 5 total shards in use." |
| 50 ms ごとに書き込みながら、`target` のプライマリシャードを持つ pod を削除 | レプリカが昇格。接続拒否は 1.3 秒、書き込みの損失なし。pod は 73–82 秒後にレプリカとして復帰 |

**cgroup v1 のホストでは、古い kind ノードイメージを固定すること。** Kubernetes 1.35 以降はデフォルトで cgroup v1 を拒否する（`failCgroupV1`）ため、kind のデフォルトである v1.37.0 イメージはこの Ubuntu 20.04 ホストで失敗した。v1.34.11 なら動作する。 ドキュメント: [Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/). ラボ: [`enterprise/03-operator-kind`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/03-operator-kind).

### ラボ: Postgres からの RDI

**RDI 2.2.1（Debezium 3.5.0、Flink processor）、Postgres 17.11、kind 上の Redis Enterprise 8.2.6-25 で確認、2026-11-07。** ドキュメントより: "Redis Data Integration (RDI) keeps your Redis cache in sync with a primary system-of-record database in near real time." ソースは Postgres 上の 1,000 件の架空の顧客。1 つのジョブが `credit_limit` から `tier` フィールドを追加し、`email` を削除して、`customer:<id>` の下に JSON を書き込む。RDI は自身の状態を、operator ラボの非クラスターデータベース `rdi-state` に保持する。

| 手順 | 結果 |
|---|---|
| RDI Helm チャート | 32 秒でインストール: API、operator、reloader の pod |
| `redis-di deploy` | 67 秒。collector（Debezium）と Flink ジョブ、task manager が起動。1 秒後に Redis に 1,000 行、変換済み |
| 1 行の UPDATE / INSERT / DELETE を各 3 回 | Redis で見えるまで 0.2–1.5 秒 / 0.8–1.1 秒 / 0.4–1.1 秒 |
| 1,000 行すべてを 1 トランザクションで UPDATE | 0.8–1.5 秒後に見える |

レイテンシには約 0.11 秒の `kubectl exec` が含まれ、1 台のホストでの結果なので、桁の目安として読むこと。processor の種類を指定しなかった場合、パイプラインは RDI 2.0 以降のデフォルトである Flink 上で動いた。行が届いている間も、`redis-di describe` はターゲットを "Connected: no" と表示した。これは調べていない。 ドキュメント: [RDI overview](https://redis.io/docs/latest/integrate/redis-data-integration/), [Install on Kubernetes](https://redis.io/docs/latest/integrate/redis-data-integration/installation/install-k8s/), [Pipeline configuration](https://redis.io/docs/latest/integrate/redis-data-integration/data-pipelines/pipeline-config/). ラボ: [`enterprise/02-rdi`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/02-rdi).

**classic プロセッサーと write-behind**（`classic.sh`）。`processors.type: classic` にすると、同じパイプラインが Flink の job・task manager の代わりに `processor` pod 一つで動き、変更は 0.2–1.1 秒で見えた。write-behind（Redis からデータベースへ）は RDI 2.2 のドキュメントにない。以前の write-behind エンジンには RedisGears Python 1.2.6 が必要だが、Redis Software 8.2.6 には含まれていないため、実行できなかった。

### 未実行

Active-Active には Redis Cloud Pro か複数の Redis Software クラスターが必要で、Redis Flex にはローカル NVMe が必要。どちらもここではドキュメントのみとする。Redis Cloud でのマネージド RDI は Pro 限定。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: รันแล้ว** Redis Software ใน Docker, Kubernetes operator บน kind และ RDI จาก Postgres ถูกรันเมื่อ 2026-11-07 (ด้านล่าง)
</div>

สิ่งที่ Redis Software และ Redis Cloud Pro เพิ่มให้เหนือ Redis Open Source — Active-Active (CRDT), Redis Flex (RAM + SSD), DMC proxy และ sharding policy, SLA 99.999 %, RBAC/LDAP/TLS, RDI, Kubernetes operator, Redis Insight, multi-tenancy เริ่มด้วยตาราง: ฟีเจอร์ มีอยู่ที่ไหน และมีแล็บแสดงหรือมีเพียงเอกสาร คำกล่าวอ้างของผู้จำหน่ายกับผลที่วัดได้จริงถูกแยกจากกัน

### สิ่งที่ Redis Software และ Cloud Pro เพิ่มให้ และสิ่งที่รันแล้ว

| ฟีเจอร์ | มีที่ไหน | บนเว็บไซต์นี้ |
|---|---|---|
| DMC proxy, sharding, proxy policy, re-sharding | Software, Cloud | รันแล้ว: ดูด้านล่าง |
| หลายฐานข้อมูลบนโหนดเดียว (multi-tenancy) | Software | รันแล้ว: ดูด้านล่าง |
| Active-Active (CRDT) | Software, Cloud Pro | เป็นเพียงการออกแบบ; ดู [สถาปัตยกรรม]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | มีเพียงเอกสาร: ต้องใช้ NVMe ในเครื่อง |
| SLA 99.999% | Cloud Pro ที่ใช้ Active-Active | มีเพียงเอกสาร: วัดในแล็บไม่ได้ |
| RBAC, LDAP, TLS ทุกจุด | Software, Cloud | หน้าจอ RBAC อยู่ใน[หน้า Redis Cloud]({{ '/cloud/' | relative_url }}); LDAP และ TLS ยังไม่ได้รัน |
| RDI (change data capture เข้า Redis) | Software; แบบ managed บน Cloud Pro | รันแล้ว: ดูด้านล่าง บน kind |
| Kubernetes operator | Software | รันแล้ว: ดูด้านล่าง บน kind |
| Redis Insight | ทั้งหมด | รันแล้วใน[หน้า Setup]({{ '/setup/' | relative_url }}) |

### แล็บ: Redis Software ในคอนเทนเนอร์เดียว

**ตรวจสอบบน Redis Software 8.2.6-25, ฐานข้อมูล Redis 8.8, 2026-11-07** คลัสเตอร์โหนดเดียวจาก `redislabs/redis:8.2.6-25.21` ควบคุมผ่าน REST API ซอร์สและผลลัพธ์: [`enterprise/01-redis-software-docker`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/01-redis-software-docker). เอกสาร: [Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

| การทดลอง | ผลลัพธ์ |
|---|---|
| ไลเซนส์ทดลอง อ่านจาก `/v1/license` | 30 วันนับจากสร้างคลัสเตอร์ มีได้สูงสุด 4 shard |
| shard ที่ห้า | ถูกปฏิเสธ: "License permits 4 total shards, but there are 5 total shards in use." |
| เริ่มคอนเทนเนอร์ → API → คลัสเตอร์ → ฐานข้อมูล | ประมาณ 10 วินาที, 10 วินาที, 1 วินาที |
| สองฐานข้อมูลบนโหนดเดียว | endpoint แยกกัน ข้อมูลแยกกัน |
| `MGET` / `MSET` ข้าม shard หลัง proxy | ใช้งานได้ |
| `MULTI`/`EXEC` ข้าม slot | ถูกปฏิเสธ; ใช้ได้เมื่อใช้ hash tag ร่วมกัน |
| replication บนโหนดเดียว | ถูกปฏิเสธ: "Not enough nodes to perform replication" |
| re-shard จาก 2 → 4 ด้วย 10,000 คีย์ | ประมาณ 6 วินาที คีย์ครบทั้งหมด |

proxy คือสิ่งที่ทำให้ฐานข้อมูลแบบ sharded ดูเป็น Redis ตัวเดียวสำหรับไคลเอนต์ทั่วไป: การอ่านและเขียนหลายคีย์ข้าม shard ได้ แต่ transaction ข้ามไม่ได้

**โมดูลและ TLS** (`tls.py`) คลัสเตอร์มาพร้อม JSON, Bloom, Search และ time series อย่างละหลายเวอร์ชัน และไม่มี RedisGears ฐานข้อมูลที่ตั้ง `tls_mode: enabled` ตัดการเชื่อมต่อ TCP แบบข้อความล้วน ไคลเอนต์เชื่อมต่อได้เฉพาะเมื่อใช้ใบรับรองพร็อกซีของคลัสเตอร์ (`GET /v1/cluster/certificates`) เป็น CA และ PING ไปกลับบนการเชื่อมต่อนั้นใช้เวลา 0.13 ms

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="รายการฐานข้อมูลใน Cluster Manager UI โดย db-b มี 4 shard" loading="lazy" decoding="async"></p>

Cluster Manager UI: รายการฐานข้อมูลหลัง re-sharding <small>จับภาพเมื่อ 2026-11-07, Redis Software 8.2.6-25</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="ภาพรวมคลัสเตอร์: เวอร์ชัน 8.2.6-25, การใช้ไลเซนส์, พื้นที่เก็บข้อมูล, หนึ่งโหนด" loading="lazy" decoding="async"></p>

ภาพรวม: เวอร์ชันซอฟต์แวร์, ไลเซนส์หมดอายุในอีก 29 วัน, พื้นที่เก็บข้อมูลและโหนด <small>จับภาพเมื่อ 2026-11-07, Redis Software 8.2.6-25</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="การตั้งค่าคลัสเตอร์: เวอร์ชันฐานข้อมูล Redis 8.8.0 ถึง 8.0.2, shard ที่ใช้ 4 จาก 4" loading="lazy" decoding="async"></p>

หน้าคลัสเตอร์แสดงเวอร์ชันฐานข้อมูลที่เลือกได้ และการใช้ shard เทียบกับไลเซนส์ <small>จับภาพเมื่อ 2026-11-07, Redis Software 8.2.6-25</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="การตั้งค่าฐานข้อมูล db-b: 4 shard, proxy ทุก primary shard, ความสามารถ Search, JSON, Time Series, Probabilistic" loading="lazy" decoding="async"></p>

การตั้งค่าฐานข้อมูล: sharding, OSS Cluster API ปิด, proxy policy, ความสามารถ และ durability อยู่ในที่เดียว <small>จับภาพเมื่อ 2026-11-07, Redis Software 8.2.6-25</small>

### แล็บ: Kubernetes operator บน kind

**ตรวจสอบบน Redis Enterprise operator 8.2.6-21 (คลัสเตอร์ 8.2.6-25) บน kind v0.33.0, Kubernetes v1.34.11, 2026-11-07** จากเอกสาร: "You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." `helm install` ครั้งเดียวสร้าง operator และคลัสเตอร์สามโหนด (REC); ฐานข้อมูลคือทรัพยากร `RedisEnterpriseDatabase` (REDB)

| ขั้นตอน | ผลลัพธ์ |
|---|---|
| `helm install` พร้อม `cluster.create: true` | REC เป็น `Running` หลัง 257 วินาที; ไลเซนส์ทดลองใช้ได้ 30 วัน มี 4 shard |
| สอง REDB (`rdi-state` และ `target` ที่มี replica) | `active` หลัง 13 วินาที ใช้ shard สามตัว |
| REDB ที่ต้องใช้ shard เพิ่มอีกสองตัว | ถูก admission webhook ปฏิเสธตอน `kubectl apply`: "License permits 4 total shards, but there are 5 total shards in use." |
| ลบ pod ที่มี primary shard ของ `target` ขณะเขียนทุก 50 มิลลิวินาที | replica ถูกเลื่อนขั้น; การเชื่อมต่อถูกปฏิเสธ 1.3 วินาที ไม่มีการเขียนสูญหาย; pod กลับมาเป็น replica หลัง 73–82 วินาที |

**บนโฮสต์ที่ใช้ cgroup v1 ให้ตรึงอิมเมจโหนด kind รุ่นเก่า** Kubernetes 1.35 ขึ้นไปปฏิเสธ cgroup v1 โดยค่าเริ่มต้น (`failCgroupV1`) อิมเมจ v1.37.0 ที่เป็นค่าเริ่มต้นของ kind จึงล้มเหลวบนโฮสต์ Ubuntu 20.04 เครื่องนี้; v1.34.11 ใช้ได้ เอกสาร: [Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/). แล็บ: [`enterprise/03-operator-kind`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/03-operator-kind).

### แล็บ: RDI จาก Postgres

**ตรวจสอบบน RDI 2.2.1 (Debezium 3.5.0, Flink processor), Postgres 17.11, Redis Enterprise 8.2.6-25 บน kind, 2026-11-07** จากเอกสาร: "Redis Data Integration (RDI) keeps your Redis cache in sync with a primary system-of-record database in near real time." แหล่งข้อมูลคือลูกค้าสมมติ 1,000 รายใน Postgres งาน (job) หนึ่งเพิ่มฟิลด์ `tier` จาก `credit_limit` ตัด `email` ออก และเขียน JSON ไว้ใต้ `customer:<id>` RDI เก็บสถานะของตัวเองไว้ในฐานข้อมูลที่ไม่ใช่คลัสเตอร์ชื่อ `rdi-state` จากแล็บ operator

| ขั้นตอน | ผลลัพธ์ |
|---|---|
| RDI Helm chart | ติดตั้งใน 32 วินาที: pod ของ API, operator และ reloader |
| `redis-di deploy` | 67 วินาที; collector (Debezium), Flink job และ task manager เริ่มทำงาน; 1 วินาทีต่อมามี 1,000 แถวใน Redis ที่แปลงแล้ว |
| UPDATE / INSERT / DELETE หนึ่งแถว รันสามรอบ | เห็นใน Redis หลัง 0.2–1.5 วินาที / 0.8–1.1 วินาที / 0.4–1.1 วินาที |
| UPDATE ทั้ง 1,000 แถวในทรานแซกชันเดียว | เห็นหลัง 0.8–1.5 วินาที |

ค่าความหน่วงรวม `kubectl exec` ราว 0.11 วินาทีและมาจากโฮสต์เดียว จึงควรอ่านเป็นลำดับขนาดเท่านั้น เมื่อไม่ได้ตั้งชนิด processor ไปป์ไลน์รันบน Flink ซึ่งเป็นค่าเริ่มต้นตั้งแต่ RDI 2.0 `redis-di describe` แสดงเป้าหมายเป็น "Connected: no" ทั้งที่แถวกำลังเข้ามา เรื่องนี้ไม่ได้ตรวจสอบ เอกสาร: [RDI overview](https://redis.io/docs/latest/integrate/redis-data-integration/), [Install on Kubernetes](https://redis.io/docs/latest/integrate/redis-data-integration/installation/install-k8s/), [Pipeline configuration](https://redis.io/docs/latest/integrate/redis-data-integration/data-pipelines/pipeline-config/). แล็บ: [`enterprise/02-rdi`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/02-rdi).

**classic processor และ write-behind** (`classic.sh`) เมื่อตั้ง `processors.type: classic` ไปป์ไลน์เดียวกันรันใน `processor` pod ตัวเดียว แทน job และ task manager ของ Flink โดยเห็นการเปลี่ยนแปลงภายใน 0.2–1.1 วินาที write-behind (จาก Redis ไปยังฐานข้อมูล) ไม่อยู่ในเอกสาร RDI 2.2 เอนจิน write-behind รุ่นเก่าต้องใช้ RedisGears Python 1.2.6 ซึ่ง Redis Software 8.2.6 ไม่ได้ให้มา จึงรันไม่ได้

### ยังไม่ได้รัน

Active-Active ต้องใช้ Redis Cloud Pro หรือ Redis Software หลายคลัสเตอร์ และ Redis Flex ต้องใช้ NVMe ในเครื่อง ทั้งสองอย่างจึงมีเพียงเอกสารที่นี่ RDI แบบ managed บน Redis Cloud มีเฉพาะ Pro

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: dijalankan.** Redis Software di Docker, Kubernetes operator di kind, dan RDI dari Postgres dijalankan pada 2026-11-07 (di bawah).
</div>

Apa yang ditambahkan Redis Software dan Redis Cloud Pro di atas Redis Open Source — Active-Active (CRDT), Redis Flex (RAM + SSD), proxy DMC dan kebijakan sharding, SLA 99,999 %, RBAC/LDAP/TLS, RDI, Kubernetes operator, Redis Insight, multi-tenancy. Tabel dulu: fitur, di mana fitur itu ada, dan apakah ada lab yang menunjukkannya atau hanya dokumentasi. Klaim vendor dan hasil terukur dipisahkan.

### Apa yang ditambahkan Redis Software dan Cloud Pro, dan apa yang dijalankan

| Fitur | Di mana | Di situs ini |
|---|---|---|
| Proxy DMC, sharding, kebijakan proxy, re-sharding | Software, Cloud | dijalankan: di bawah |
| Beberapa database pada satu node (multi-tenancy) | Software | dijalankan: di bawah |
| Active-Active (CRDT) | Software, Cloud Pro | hanya desain; lihat [Arsitektur]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | hanya dokumentasi: butuh NVMe lokal |
| SLA 99,999% | Cloud Pro dengan Active-Active | hanya dokumentasi: tidak dapat diukur di lab |
| RBAC, LDAP, TLS di mana-mana | Software, Cloud | layar RBAC ada di [halaman Redis Cloud]({{ '/cloud/' | relative_url }}); LDAP dan TLS tidak dijalankan |
| RDI (change data capture ke Redis) | Software; terkelola di Cloud Pro | dijalankan: di bawah, di kind |
| Kubernetes operator | Software | dijalankan: di bawah, di kind |
| Redis Insight | semua | dijalankan di [halaman Setup]({{ '/setup/' | relative_url }}) |

### Lab: Redis Software dalam satu kontainer

**Diverifikasi pada Redis Software 8.2.6-25, database Redis 8.8, 2026-11-07.** Klaster satu node dari `redislabs/redis:8.2.6-25.21`, dijalankan melalui REST API-nya. Sumber dan keluaran: [`enterprise/01-redis-software-docker`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/01-redis-software-docker). Dokumentasi: [Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

| Eksperimen | Hasil |
|---|---|
| Lisensi uji coba, dibaca dari `/v1/license` | 30 hari sejak klaster dibuat, maksimal 4 shard |
| Shard kelima | ditolak: "License permits 4 total shards, but there are 5 total shards in use." |
| Kontainer mulai → API → klaster → database | sekitar 10 dtk, 10 dtk, 1 dtk |
| Dua database pada satu node | endpoint terpisah, data terpisah |
| `MGET` / `MSET` lintas shard di balik proxy | berhasil |
| `MULTI`/`EXEC` lintas slot | ditolak; berhasil dengan hash tag bersama |
| Replikasi pada satu node | ditolak: "Not enough nodes to perform replication" |
| Re-shard 2 → 4 dengan 10,000 key | sekitar 6 dtk, semua key tetap ada |

Proxy-lah yang membuat database ter-shard tampak sebagai satu Redis bagi klien biasa: baca dan tulis multi-key dapat lintas shard, transaksi tidak.

**Modul dan TLS** (`tls.py`). Klaster menyertakan JSON, Bloom, Search, dan time series dalam beberapa versi masing-masing, serta tidak ada RedisGears. Basis data dengan `tls_mode: enabled` menutup koneksi TCP polos; klien hanya bisa terhubung dengan sertifikat proxy klaster (`GET /v1/cluster/certificates`) sebagai CA-nya, dan satu kali bolak-balik PING pada koneksi itu memakan waktu 0.13 ms.

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="Daftar database Cluster Manager UI dengan db-b, 4 shard" loading="lazy" decoding="async"></p>

Cluster Manager UI: daftar database setelah re-sharding. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="Ikhtisar klaster: versi 8.2.6-25, penggunaan lisensi, penyimpanan, satu node" loading="lazy" decoding="async"></p>

Ikhtisar: versi perangkat lunak, lisensi kedaluwarsa dalam 29 hari, penyimpanan dan node. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="Konfigurasi klaster: versi database Redis 8.8.0 hingga 8.0.2, shard terpakai 4 dari 4" loading="lazy" decoding="async"></p>

Halaman klaster mencantumkan versi database yang tersedia dan penggunaan shard terhadap lisensi. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="Konfigurasi database db-b: 4 shard, proxy semua shard primer, kapabilitas Search, JSON, Time Series, Probabilistic" loading="lazy" decoding="async"></p>

Pengaturan database: sharding, OSS Cluster API nonaktif, kebijakan proxy, kapabilitas dan durabilitas di satu tempat. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

### Lab: Kubernetes operator di kind

**Diverifikasi pada Redis Enterprise operator 8.2.6-21 (klaster 8.2.6-25) di kind v0.33.0, Kubernetes v1.34.11, 2026-11-07.** Dari dokumentasi: "You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." Satu `helm install` membuat operator dan klaster tiga node (REC); database berupa resource `RedisEnterpriseDatabase` (REDB).

| Langkah | Hasil |
|---|---|
| `helm install` dengan `cluster.create: true` | REC `Running` setelah 257 dtk; lisensi uji coba berlaku 30 hari, 4 shard |
| Dua REDB (`rdi-state`, `target` dengan replika) | `active` setelah 13 dtk, tiga shard terpakai |
| REDB yang butuh dua shard lagi | ditolak saat `kubectl apply` oleh admission webhook: "License permits 4 total shards, but there are 5 total shards in use." |
| Hapus pod dengan shard primer `target` sambil menulis setiap 50 md | replika dipromosikan; koneksi ditolak selama 1,3 dtk, tidak ada tulisan yang hilang; pod kembali sebagai replika setelah 73–82 dtk |

**Pada host cgroup v1, kunci image node kind yang lebih lama.** Kubernetes 1.35 ke atas menolak cgroup v1 secara bawaan (`failCgroupV1`), sehingga image bawaan kind v1.37.0 gagal di host Ubuntu 20.04 ini; v1.34.11 berfungsi. Dokumentasi: [Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/). Lab: [`enterprise/03-operator-kind`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/03-operator-kind).

### Lab: RDI dari Postgres

**Diverifikasi pada RDI 2.2.1 (Debezium 3.5.0, Flink processor), Postgres 17.11, Redis Enterprise 8.2.6-25 di kind, 2026-11-07.** Dari dokumentasi: "Redis Data Integration (RDI) keeps your Redis cache in sync with a primary system-of-record database in near real time." Sumbernya adalah 1.000 pelanggan fiktif di Postgres. Satu job menambahkan field `tier` dari `credit_limit`, membuang `email`, dan menulis JSON di bawah `customer:<id>`. RDI menyimpan state-nya di database non-klaster `rdi-state` dari lab operator.

| Langkah | Hasil |
|---|---|
| Helm chart RDI | terpasang dalam 32 dtk: pod API, operator, reloader |
| `redis-di deploy` | 67 dtk; collector (Debezium), job Flink, dan task manager mulai; 1,000 baris di Redis 1 dtk kemudian, sudah ditransformasi |
| UPDATE / INSERT / DELETE satu baris, tiga kali jalan | terlihat di Redis setelah 0,2–1,5 dtk / 0,8–1,1 dtk / 0,4–1,1 dtk |
| UPDATE seluruh 1,000 baris dalam satu transaksi | terlihat setelah 0,8–1,5 dtk |

Latensi itu sudah termasuk sekitar 0,11 dtk untuk `kubectl exec` dan berasal dari satu host, jadi bacalah sebagai orde besarnya saja. Tanpa tipe processor yang ditetapkan, pipeline berjalan di Flink, yang menjadi bawaan sejak RDI 2.0. `redis-di describe` menampilkan target sebagai "Connected: no" saat baris sedang berdatangan; hal itu tidak diselidiki. Dokumentasi: [RDI overview](https://redis.io/docs/latest/integrate/redis-data-integration/), [Install on Kubernetes](https://redis.io/docs/latest/integrate/redis-data-integration/installation/install-k8s/), [Pipeline configuration](https://redis.io/docs/latest/integrate/redis-data-integration/data-pipelines/pipeline-config/). Lab: [`enterprise/02-rdi`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/02-rdi).

**Prosesor classic dan write-behind** (`classic.sh`). Dengan `processors.type: classic`, pipeline yang sama berjalan dalam satu pod `processor`, bukan job dan task manager milik Flink, dengan perubahan terlihat dalam 0.2–1.1 detik. Write-behind (dari Redis ke basis data) tidak ada dalam dokumentasi RDI 2.2; mesin write-behind yang lama membutuhkan RedisGears Python 1.2.6, yang tidak disertakan Redis Software 8.2.6, sehingga tidak bisa dijalankan.

### Belum dijalankan

Active-Active membutuhkan Redis Cloud Pro atau beberapa klaster Redis Software, dan Redis Flex membutuhkan NVMe lokal; keduanya tetap hanya dokumentasi di sini. RDI terkelola di Redis Cloud hanya tersedia di Pro.

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: dijalankan.** Redis Software dalam Docker, Kubernetes operator pada kind, dan RDI daripada Postgres telah dijalankan pada 2026-11-07 (di bawah).
</div>

Apa yang ditambah oleh Redis Software dan Redis Cloud Pro berbanding Redis Open Source — Active-Active (CRDT), Redis Flex (RAM + SSD), proksi DMC dan dasar sharding, SLA 99.999 %, RBAC/LDAP/TLS, RDI, Kubernetes operator, Redis Insight, berbilang penyewa. Jadual dahulu: ciri, di mana ia wujud, dan sama ada makmal menunjukkannya atau hanya dokumentasi. Dakwaan vendor dan hasil yang diukur diasingkan.

### Apa yang ditambah oleh Redis Software dan Cloud Pro, dan apa yang dijalankan

| Ciri | Di mana | Di tapak ini |
|---|---|---|
| Proksi DMC, sharding, dasar proksi, re-sharding | Software, Cloud | dijalankan: di bawah |
| Beberapa pangkalan data pada satu nod (berbilang penyewa) | Software | dijalankan: di bawah |
| Active-Active (CRDT) | Software, Cloud Pro | reka bentuk sahaja; lihat [Seni bina]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | dokumen sahaja: perlukan NVMe tempatan |
| SLA 99.999% | Cloud Pro dengan Active-Active | dokumen sahaja: tidak dapat diukur di makmal |
| RBAC, LDAP, TLS di mana-mana | Software, Cloud | skrin RBAC pada [halaman Redis Cloud]({{ '/cloud/' | relative_url }}); LDAP dan TLS tidak dijalankan |
| RDI (change data capture ke dalam Redis) | Software; terurus pada Cloud Pro | dijalankan: di bawah, pada kind |
| Kubernetes operator | Software | dijalankan: di bawah, pada kind |
| Redis Insight | semua | dijalankan pada [halaman Setup]({{ '/setup/' | relative_url }}) |

### Makmal: Redis Software dalam satu kontena

**Disahkan pada Redis Software 8.2.6-25, pangkalan data Redis 8.8, 2026-11-07.** Satu kluster satu nod daripada `redislabs/redis:8.2.6-25.21`, dikendalikan melalui REST API-nya. Sumber dan output: [`enterprise/01-redis-software-docker`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/01-redis-software-docker). Dokumen: [Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

| Eksperimen | Keputusan |
|---|---|
| Lesen percubaan, dibaca daripada `/v1/license` | 30 hari sejak kluster dicipta, paling banyak 4 shard |
| Shard kelima | ditolak: "License permits 4 total shards, but there are 5 total shards in use." |
| Kontena bermula → API → kluster → pangkalan data | kira-kira 10 s, 10 s, 1 s |
| Dua pangkalan data pada satu nod | endpoint berasingan, data berasingan |
| `MGET` / `MSET` merentasi shard di sebalik proxy | berjaya |
| `MULTI`/`EXEC` merentasi slot | ditolak; berjaya dengan hash tag yang dikongsi |
| Replikasi pada satu nod | ditolak: "Not enough nodes to perform replication" |
| Re-shard 2 → 4 dengan 10,000 key | kira-kira 6 s, semua key kekal |

Proxy yang menjadikan pangkalan data ter-shard kelihatan seperti satu Redis kepada klien biasa: bacaan dan tulisan berbilang key boleh merentasi shard, transaksi tidak boleh.

**Modul dan TLS** (`tls.py`). Kluster menyertakan JSON, Bloom, Search dan time series dalam beberapa versi setiap satu, dan tiada RedisGears. Pangkalan data dengan `tls_mode: enabled` menutup sambungan TCP biasa; klien hanya berjaya bersambung dengan sijil proksi kluster (`GET /v1/cluster/certificates`) sebagai CA-nya, dan satu pusingan PING pada sambungan itu mengambil masa 0.13 ms.

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="Senarai pangkalan data Cluster Manager UI dengan db-b, 4 shard" loading="lazy" decoding="async"></p>

Cluster Manager UI: senarai pangkalan data selepas re-sharding. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="Gambaran keseluruhan kluster: versi 8.2.6-25, penggunaan lesen, storan, satu nod" loading="lazy" decoding="async"></p>

Gambaran keseluruhan: versi perisian, lesen tamat tempoh dalam 29 hari, storan dan nod. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="Konfigurasi kluster: versi pangkalan data Redis 8.8.0 hingga 8.0.2, shard digunakan 4 daripada 4" loading="lazy" decoding="async"></p>

Halaman kluster menyenaraikan versi pangkalan data yang ditawarkan dan penggunaan shard berbanding lesen. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="Konfigurasi pangkalan data db-b: 4 shard, proxy semua shard primer, keupayaan Search, JSON, Time Series, Probabilistic" loading="lazy" decoding="async"></p>

Tetapan pangkalan data: sharding, OSS Cluster API dimatikan, dasar proxy, keupayaan dan ketahanan di satu tempat. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

### Makmal: Kubernetes operator pada kind

**Disahkan pada Redis Enterprise operator 8.2.6-21 (kluster 8.2.6-25) pada kind v0.33.0, Kubernetes v1.34.11, 2026-11-07.** Daripada dokumen: "You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." Satu `helm install` mencipta operator dan kluster tiga nod (REC); pangkalan data ialah sumber `RedisEnterpriseDatabase` (REDB).

| Langkah | Keputusan |
|---|---|
| `helm install` dengan `cluster.create: true` | REC `Running` selepas 257 s; lesen percubaan sah 30 hari, 4 shard |
| Dua REDB (`rdi-state`, `target` dengan replika) | `active` selepas 13 s, tiga shard digunakan |
| REDB yang memerlukan dua lagi shard | ditolak pada `kubectl apply` oleh admission webhook: "License permits 4 total shards, but there are 5 total shards in use." |
| Padam pod dengan shard utama `target` sambil menulis setiap 50 ms | replika dinaikkan taraf; 1.3 s sambungan ditolak, tiada tulisan hilang; pod kembali sebagai replika selepas 73–82 s |

**Pada hos cgroup v1, tetapkan imej nod kind yang lebih lama.** Kubernetes 1.35 dan ke atas menolak cgroup v1 secara lalai (`failCgroupV1`), jadi imej lalai kind v1.37.0 gagal pada hos Ubuntu 20.04 ini; v1.34.11 berfungsi. Dokumen: [Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/). Makmal: [`enterprise/03-operator-kind`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/03-operator-kind).

### Makmal: RDI daripada Postgres

**Disahkan pada RDI 2.2.1 (Debezium 3.5.0, Flink processor), Postgres 17.11, Redis Enterprise 8.2.6-25 pada kind, 2026-11-07.** Daripada dokumen: "Redis Data Integration (RDI) keeps your Redis cache in sync with a primary system-of-record database in near real time." Sumbernya ialah 1,000 pelanggan rekaan dalam Postgres. Satu job menambah medan `tier` daripada `credit_limit`, menggugurkan `email`, dan menulis JSON di bawah `customer:<id>`. RDI menyimpan keadaannya dalam pangkalan data bukan kluster `rdi-state` daripada makmal operator.

| Langkah | Keputusan |
|---|---|
| Carta Helm RDI | dipasang dalam 32 s: pod API, operator, reloader |
| `redis-di deploy` | 67 s; collector (Debezium), job Flink dan task manager bermula; 1,000 baris dalam Redis 1 s kemudian, telah diubah |
| UPDATE / INSERT / DELETE satu baris, tiga kali jalan | kelihatan dalam Redis selepas 0.2–1.5 s / 0.8–1.1 s / 0.4–1.1 s |
| UPDATE kesemua 1,000 baris dalam satu transaksi | kelihatan selepas 0.8–1.5 s |

Kependaman itu termasuk kira-kira 0.11 s untuk `kubectl exec` dan datang daripada satu hos, jadi bacalah sebagai anggaran magnitud sahaja. Tanpa jenis processor ditetapkan, saluran paip berjalan pada Flink, iaitu lalai sejak RDI 2.0. `redis-di describe` menunjukkan sasaran sebagai "Connected: no" semasa baris sedang tiba; perkara itu tidak disiasat. Dokumen: [RDI overview](https://redis.io/docs/latest/integrate/redis-data-integration/), [Install on Kubernetes](https://redis.io/docs/latest/integrate/redis-data-integration/installation/install-k8s/), [Pipeline configuration](https://redis.io/docs/latest/integrate/redis-data-integration/data-pipelines/pipeline-config/). Makmal: [`enterprise/02-rdi`](https://github.com/litkhai/notes-on-redis/tree/main/enterprise/02-rdi).

**Pemproses classic dan write-behind** (`classic.sh`). Dengan `processors.type: classic`, pipeline yang sama berjalan dalam satu pod `processor`, bukan job dan task manager milik Flink, dengan perubahan kelihatan dalam 0.2–1.1 saat. Write-behind (daripada Redis ke pangkalan data) tiada dalam dokumentasi RDI 2.2; enjin write-behind yang lama memerlukan RedisGears Python 1.2.6, yang tidak disertakan oleh Redis Software 8.2.6, jadi ia tidak dapat dijalankan.

### Belum dijalankan

Active-Active memerlukan Redis Cloud Pro atau beberapa kluster Redis Software, dan Redis Flex memerlukan NVMe tempatan; kedua-duanya kekal sebagai dokumen sahaja di sini. RDI terurus pada Redis Cloud hanya untuk Pro.

</div>
