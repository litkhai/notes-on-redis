---
layout: default
title: Enterprise
permalink: /enterprise/
---

# Enterprise

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: partly run.** Redis Software in Docker was run on 2026-11-07 (below). RDI and the Kubernetes operator are still the plan in [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
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
| RDI (change data capture into Redis) | Software; managed on Cloud Pro | not run yet |
| Kubernetes operator | Software | not run yet |
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

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="Cluster Manager UI databases list with db-b, 4 shards" loading="lazy" decoding="async"></p>

Cluster Manager UI: the databases list after re-sharding. <small>Captured 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="Cluster overview: version 8.2.6-25, license usage, storage, one node" loading="lazy" decoding="async"></p>

Overview: software version, licence expiry in 29 days, storage and nodes. <small>Captured 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="Cluster configuration: Redis database versions 8.8.0 to 8.0.2, used shards 4 of 4" loading="lazy" decoding="async"></p>

The cluster page lists the database versions on offer and the shard usage against the licence. <small>Captured 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="Database db-b configuration: 4 shards, proxy all primary shards, capabilities Search, JSON, Time Series, Probabilistic" loading="lazy" decoding="async"></p>

Database settings: sharding, OSS Cluster API off, proxy policy, capabilities and durability in one place. <small>Captured 2026-11-07, Redis Software 8.2.6-25.</small>

### Not run yet

RDI from Postgres and the Kubernetes operator need a Kubernetes cluster on this host (kind) and the RDI Helm chart; both are tracked in the repository issues.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 일부 실행.** Docker의 Redis Software를 2026-11-07에 실행했다(아래). RDI와 Kubernetes operator는 아직 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)의 계획이다.
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
| RDI(Redis로의 변경 데이터 캡처) | Software, Cloud Pro는 관리형 | 아직 미실행 |
| Kubernetes operator | Software | 아직 미실행 |
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

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="샤드 4개인 db-b가 있는 Cluster Manager UI의 DB 목록" loading="lazy" decoding="async"></p>

Cluster Manager UI: 재샤딩 뒤의 DB 목록. <small>2026-11-07 캡처, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="클러스터 개요: 버전 8.2.6-25, 라이선스 사용량, 저장 공간, 노드 하나" loading="lazy" decoding="async"></p>

개요: 소프트웨어 버전, 29일 뒤 라이선스 만료, 저장 공간과 노드. <small>2026-11-07 캡처, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="클러스터 설정: Redis DB 버전 8.8.0부터 8.0.2, 사용 샤드 4/4" loading="lazy" decoding="async"></p>

클러스터 화면은 고를 수 있는 DB 버전과 라이선스 대비 샤드 사용량을 보여 준다. <small>2026-11-07 캡처, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="DB db-b 설정: 4샤드, 프록시 모든 주 샤드, 기능 Search·JSON·Time Series·확률형" loading="lazy" decoding="async"></p>

DB 설정: 샤딩, OSS Cluster API 꺼짐, 프록시 정책, 기능, 내구성이 한곳에 있다. <small>2026-11-07 캡처, Redis Software 8.2.6-25.</small>

### 아직 실행하지 않은 것

Postgres에서 RDI, Kubernetes operator는 이 호스트의 Kubernetes 클러스터(kind)와 RDI Helm 차트가 필요하다. 둘 다 저장소 이슈로 추적한다.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：部分已运行。** 已于 2026-11-07 运行 Docker 中的 Redis Software（见下）。RDI 与 Kubernetes operator 仍只是计划，见 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)。
</div>

Redis Software 与 Redis Cloud Pro 相对 Redis Open Source 的增强 — Active-Active（CRDT）、Redis Flex（RAM + SSD）、DMC 代理与分片策略、99.999 % SLA、RBAC/LDAP/TLS、RDI、Kubernetes operator、Redis Insight、多租户。先列表：功能、所在产品、有实验还是仅文档。厂商声明与实测结果分开记录。

### Redis Software 与 Cloud Pro 增加了什么，以及运行了什么

| 功能 | 存在于 | 本站情况 |
|---|---|---|
| DMC 代理、分片、代理策略、重新分片 | Software, Cloud | 已运行：见下 |
| 单节点上的多个数据库（多租户） | Software | 已运行：见下 |
| Active-Active (CRDT) | Software, Cloud Pro | 仅有设计，见 [Architecture 页]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | 仅有文档：需要本地 NVMe |
| 99.999% SLA | Cloud Pro 搭配 Active-Active | 仅有文档：无法在实验中测量 |
| RBAC、LDAP、全程 TLS | Software, Cloud | RBAC 界面见 [Redis Cloud 页]({{ '/cloud/' | relative_url }})；LDAP 与 TLS 未运行 |
| RDI（把变更数据捕获到 Redis） | Software；Cloud Pro 上为托管 | 尚未运行 |
| Kubernetes operator | Software | 尚未运行 |
| Redis Insight | 全部 | 在 [Setup 页]({{ '/setup/' | relative_url }})上运行 |

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

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="Cluster Manager UI 的数据库列表，其中 db-b 有 4 个分片" loading="lazy" decoding="async"></p>

Cluster Manager UI：重新分片之后的数据库列表。 <small>2026-11-07 截取，Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="集群概览：版本 8.2.6-25、许可证用量、存储、一个节点" loading="lazy" decoding="async"></p>

概览：软件版本、29 天后许可证到期、存储与节点。 <small>2026-11-07 截取，Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="集群配置：Redis 数据库版本 8.8.0 至 8.0.2，已用分片 4/4" loading="lazy" decoding="async"></p>

集群页面列出可选的数据库版本，以及相对许可证的分片用量。 <small>2026-11-07 截取，Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="数据库 db-b 配置：4 个分片、代理为所有主分片、功能 Search、JSON、Time Series、概率型" loading="lazy" decoding="async"></p>

数据库设置：分片、OSS Cluster API 关闭、代理策略、功能与持久性集中在一处。 <small>2026-11-07 截取，Redis Software 8.2.6-25。</small>

### 尚未运行

基于 Postgres 的 RDI 与 Kubernetes operator 需要本机上的 Kubernetes 集群（kind）和 RDI Helm chart；两者都已记录在仓库的 issue 中。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**状況: 一部実行済み。** Docker 上の Redis Software は 2026-11-07 に実行しました（下記）。RDI と Kubernetes operator は引き続き [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) の計画段階です。
</div>

Redis Software と Redis Cloud Pro が Redis Open Source に加えるもの — Active-Active（CRDT）、Redis Flex（RAM + SSD）、DMC プロキシとシャーディングポリシー、99.999 % SLA、RBAC/LDAP/TLS、RDI、Kubernetes オペレーター、Redis Insight、マルチテナンシー。まず表: 機能、どこにあるか、ラボで示すかドキュメントのみか。ベンダーの主張と測定結果は分けて書く。

### Redis Software と Cloud Pro が加えるもの、そして実行したもの

| 機能 | 提供先 | このサイトでは |
|---|---|---|
| DMC プロキシ、シャーディング、プロキシポリシー、リシャーディング | Software, Cloud | 実行済み: 下記 |
| 1 ノード上の複数データベース（マルチテナンシー） | Software | 実行済み: 下記 |
| Active-Active (CRDT) | Software, Cloud Pro | 設計のみ。[Architecture ページ]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | ドキュメントのみ: ローカル NVMe が必要 |
| 99.999% SLA | Active-Active を使う Cloud Pro | ドキュメントのみ: ラボでは測定できない |
| RBAC、LDAP、全面 TLS | Software, Cloud | RBAC の画面は [Redis Cloud ページ]({{ '/cloud/' | relative_url }})。LDAP と TLS は未実行 |
| RDI（変更データキャプチャで Redis へ） | Software。Cloud Pro ではマネージド | 未実行 |
| Kubernetes operator | Software | 未実行 |
| Redis Insight | すべて | [ Setup ページ]({{ '/setup/' | relative_url }})で実行済み |

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

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="シャード 4 つの db-b がある Cluster Manager UI のデータベース一覧" loading="lazy" decoding="async"></p>

Cluster Manager UI: リシャーディング後のデータベース一覧。 <small>2026-11-07 取得、Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="クラスター概要: バージョン 8.2.6-25、ライセンス使用量、ストレージ、ノード 1 つ" loading="lazy" decoding="async"></p>

概要: ソフトウェアバージョン、29 日後のライセンス期限、ストレージとノード。 <small>2026-11-07 取得、Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="クラスター設定: Redis データベースのバージョン 8.8.0 から 8.0.2、使用シャード 4/4" loading="lazy" decoding="async"></p>

クラスターページには、選べるデータベースバージョンと、ライセンスに対するシャード使用量が表示される。 <small>2026-11-07 取得、Redis Software 8.2.6-25。</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="データベース db-b の設定: 4 シャード、プロキシは全プライマリシャード、機能は Search、JSON、Time Series、確率的データ構造" loading="lazy" decoding="async"></p>

データベース設定: シャーディング、OSS Cluster API オフ、プロキシポリシー、機能、永続性が 1 か所にある。 <small>2026-11-07 取得、Redis Software 8.2.6-25。</small>

### まだ実行していないもの

Postgres からの RDI と Kubernetes operator には、このホスト上の Kubernetes クラスター（kind）と RDI Helm チャートが必要。どちらもリポジトリの issue で管理している。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: รันแล้วบางส่วน** รัน Redis Software ใน Docker เมื่อ 2026-11-07 แล้ว (ด้านล่าง) ส่วน RDI และ Kubernetes operator ยังเป็นแผนใน [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

สิ่งที่ Redis Software และ Redis Cloud Pro เพิ่มขึ้นจาก Redis Open Source ได้แก่ Active-Active (CRDT), Redis Flex (RAM + SSD), พร็อกซี DMC และนโยบายการทำ sharding, SLA 99.999 %, RBAC/LDAP/TLS, RDI, Kubernetes operator, Redis Insight และ multi-tenancy เริ่มด้วยตารางก่อน: ฟีเจอร์ มีอยู่ที่ใด และมีแล็บแสดงให้ดูหรือเป็นเพียงเอกสารอย่างเดียว ข้อกล่าวอ้างของผู้ขายและผลที่วัดได้จริงแยกออกจากกัน

### สิ่งที่ Redis Software และ Cloud Pro เพิ่มเข้ามา และสิ่งที่รันแล้ว

| ฟีเจอร์ | มีที่ไหน | บนไซต์นี้ |
|---|---|---|
| DMC proxy, sharding, proxy policy, re-sharding | Software, Cloud | รันแล้ว: ด้านล่าง |
| หลายฐานข้อมูลบนโหนดเดียว (multi-tenancy) | Software | รันแล้ว: ด้านล่าง |
| Active-Active (CRDT) | Software, Cloud Pro | เป็นแค่ดีไซน์ ดู [หน้า Architecture]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | มีแค่เอกสาร: ต้องใช้ NVMe ในเครื่อง |
| 99.999% SLA | Cloud Pro ที่ใช้ Active-Active | มีแค่เอกสาร: วัดในแล็บไม่ได้ |
| RBAC, LDAP, TLS ทุกจุด | Software, Cloud | หน้าจอ RBAC อยู่ใน [หน้า Redis Cloud]({{ '/cloud/' | relative_url }}); LDAP และ TLS ยังไม่ได้รัน |
| RDI (change data capture เข้า Redis) | Software; แบบ managed บน Cloud Pro | ยังไม่ได้รัน |
| Kubernetes operator | Software | ยังไม่ได้รัน |
| Redis Insight | ทุกแบบ | รันใน [หน้า Setup]({{ '/setup/' | relative_url }}) |

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

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="รายการฐานข้อมูลใน Cluster Manager UI โดย db-b มี 4 shard" loading="lazy" decoding="async"></p>

Cluster Manager UI: รายการฐานข้อมูลหลัง re-sharding <small>จับภาพเมื่อ 2026-11-07, Redis Software 8.2.6-25</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="ภาพรวมคลัสเตอร์: เวอร์ชัน 8.2.6-25, การใช้ไลเซนส์, พื้นที่เก็บข้อมูล, หนึ่งโหนด" loading="lazy" decoding="async"></p>

ภาพรวม: เวอร์ชันซอฟต์แวร์, ไลเซนส์หมดอายุในอีก 29 วัน, พื้นที่เก็บข้อมูลและโหนด <small>จับภาพเมื่อ 2026-11-07, Redis Software 8.2.6-25</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="การตั้งค่าคลัสเตอร์: เวอร์ชันฐานข้อมูล Redis 8.8.0 ถึง 8.0.2, shard ที่ใช้ 4 จาก 4" loading="lazy" decoding="async"></p>

หน้าคลัสเตอร์แสดงเวอร์ชันฐานข้อมูลที่เลือกได้ และการใช้ shard เทียบกับไลเซนส์ <small>จับภาพเมื่อ 2026-11-07, Redis Software 8.2.6-25</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="การตั้งค่าฐานข้อมูล db-b: 4 shard, proxy ทุก primary shard, ความสามารถ Search, JSON, Time Series, Probabilistic" loading="lazy" decoding="async"></p>

การตั้งค่าฐานข้อมูล: sharding, OSS Cluster API ปิด, proxy policy, ความสามารถ และ durability อยู่ในที่เดียว <small>จับภาพเมื่อ 2026-11-07, Redis Software 8.2.6-25</small>

### ยังไม่ได้รัน

RDI จาก Postgres และ Kubernetes operator ต้องใช้คลัสเตอร์ Kubernetes บนโฮสต์นี้ (kind) และ RDI Helm chart ทั้งสองอย่างติดตามอยู่ใน issue ของรีโพซิทอรี

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: sebagian sudah dijalankan.** Redis Software di Docker dijalankan pada 2026-11-07 (di bawah). RDI dan Kubernetes operator masih berupa rencana di [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Apa yang ditambahkan Redis Software dan Redis Cloud Pro dibandingkan Redis Open Source: Active-Active (CRDT), Redis Flex (RAM + SSD), proksi DMC dan kebijakan sharding, SLA 99,999 %, RBAC/LDAP/TLS, RDI, operator Kubernetes, Redis Insight, dan multi-tenancy. Diawali tabel: fitur, di mana fitur itu tersedia, dan apakah ada lab yang menunjukkannya atau halaman ini hanya berisi dokumentasi. Klaim vendor dan hasil pengukuran dipisahkan.

### Apa yang ditambahkan Redis Software dan Cloud Pro, dan apa yang dijalankan

| Fitur | Tersedia di | Di situs ini |
|---|---|---|
| DMC proxy, sharding, kebijakan proxy, re-sharding | Software, Cloud | dijalankan: di bawah |
| Beberapa database pada satu node (multi-tenancy) | Software | dijalankan: di bawah |
| Active-Active (CRDT) | Software, Cloud Pro | hanya desain; lihat [halaman Architecture]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | hanya dokumentasi: perlu NVMe lokal |
| 99.999% SLA | Cloud Pro dengan Active-Active | hanya dokumentasi: tidak dapat diukur di lab |
| RBAC, LDAP, TLS di mana-mana | Software, Cloud | layar RBAC ada di [halaman Redis Cloud]({{ '/cloud/' | relative_url }}); LDAP dan TLS belum dijalankan |
| RDI (change data capture ke Redis) | Software; terkelola di Cloud Pro | belum dijalankan |
| Kubernetes operator | Software | belum dijalankan |
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

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="Daftar database Cluster Manager UI dengan db-b, 4 shard" loading="lazy" decoding="async"></p>

Cluster Manager UI: daftar database setelah re-sharding. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="Ikhtisar klaster: versi 8.2.6-25, penggunaan lisensi, penyimpanan, satu node" loading="lazy" decoding="async"></p>

Ikhtisar: versi perangkat lunak, lisensi kedaluwarsa dalam 29 hari, penyimpanan dan node. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="Konfigurasi klaster: versi database Redis 8.8.0 hingga 8.0.2, shard terpakai 4 dari 4" loading="lazy" decoding="async"></p>

Halaman klaster mencantumkan versi database yang tersedia dan penggunaan shard terhadap lisensi. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="Konfigurasi database db-b: 4 shard, proxy semua shard primer, kapabilitas Search, JSON, Time Series, Probabilistic" loading="lazy" decoding="async"></p>

Pengaturan database: sharding, OSS Cluster API nonaktif, kebijakan proxy, kapabilitas dan durabilitas di satu tempat. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

### Belum dijalankan

RDI dari Postgres dan Kubernetes operator memerlukan klaster Kubernetes di host ini (kind) dan Helm chart RDI; keduanya dilacak di issue repositori.

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: sebahagian telah dijalankan.** Redis Software dalam Docker dijalankan pada 2026-11-07 (di bawah). RDI dan Kubernetes operator masih lagi dalam pelan di [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Apa yang ditambah oleh Redis Software dan Redis Cloud Pro berbanding Redis Open Source: Active-Active (CRDT), Redis Flex (RAM + SSD), proksi DMC dan dasar sharding, SLA 99.999 %, RBAC/LDAP/TLS, RDI, operator Kubernetes, Redis Insight dan multi-tenancy. Bermula dengan jadual: ciri, di mana ia wujud, dan sama ada ada makmal yang menunjukkannya atau halaman ini hanya dokumentasi. Dakwaan vendor dan keputusan yang diukur diasingkan.

### Apa yang ditambah oleh Redis Software dan Cloud Pro, dan apa yang dijalankan

| Ciri | Terdapat di | Di tapak ini |
|---|---|---|
| DMC proxy, sharding, dasar proxy, re-sharding | Software, Cloud | dijalankan: di bawah |
| Beberapa pangkalan data pada satu nod (multi-tenancy) | Software | dijalankan: di bawah |
| Active-Active (CRDT) | Software, Cloud Pro | reka bentuk sahaja; lihat [halaman Architecture]({{ '/architecture/' | relative_url }}) |
| Redis Flex (RAM + SSD) | Software, Cloud | dokumen sahaja: perlukan NVMe tempatan |
| 99.999% SLA | Cloud Pro dengan Active-Active | dokumen sahaja: tidak dapat diukur dalam makmal |
| RBAC, LDAP, TLS di mana-mana | Software, Cloud | skrin RBAC ada di [halaman Redis Cloud]({{ '/cloud/' | relative_url }}); LDAP dan TLS belum dijalankan |
| RDI (change data capture ke dalam Redis) | Software; terurus di Cloud Pro | belum dijalankan |
| Kubernetes operator | Software | belum dijalankan |
| Redis Insight | semua | dijalankan di [halaman Setup]({{ '/setup/' | relative_url }}) |

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

<p class="shot"><img src="{{ '/assets/img/enterprise/01-rs-databases.webp' | relative_url }}" width="1440" height="765" alt="Senarai pangkalan data Cluster Manager UI dengan db-b, 4 shard" loading="lazy" decoding="async"></p>

Cluster Manager UI: senarai pangkalan data selepas re-sharding. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/02-rs-overview.webp' | relative_url }}" width="1440" height="765" alt="Gambaran keseluruhan kluster: versi 8.2.6-25, penggunaan lesen, storan, satu nod" loading="lazy" decoding="async"></p>

Gambaran keseluruhan: versi perisian, lesen tamat tempoh dalam 29 hari, storan dan nod. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/03-rs-cluster.webp' | relative_url }}" width="1440" height="765" alt="Konfigurasi kluster: versi pangkalan data Redis 8.8.0 hingga 8.0.2, shard digunakan 4 daripada 4" loading="lazy" decoding="async"></p>

Halaman kluster menyenaraikan versi pangkalan data yang ditawarkan dan penggunaan shard berbanding lesen. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

<p class="shot"><img src="{{ '/assets/img/enterprise/05-rs-database-config.webp' | relative_url }}" width="1440" height="1800" alt="Konfigurasi pangkalan data db-b: 4 shard, proxy semua shard primer, keupayaan Search, JSON, Time Series, Probabilistic" loading="lazy" decoding="async"></p>

Tetapan pangkalan data: sharding, OSS Cluster API dimatikan, dasar proxy, keupayaan dan ketahanan di satu tempat. <small>Ditangkap 2026-11-07, Redis Software 8.2.6-25.</small>

### Belum dijalankan

RDI daripada Postgres dan Kubernetes operator memerlukan kluster Kubernetes pada hos ini (kind) dan carta Helm RDI; kedua-duanya dijejaki dalam isu repositori.

</div>
