---
layout: default
title: Overview
permalink: /
---

# Redis Hands-On Labs

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: design only.** Nothing on this page has been run yet. The plan is in [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Practical labs for [Redis](https://redis.io) — Redis Open Source, Redis Cloud, Redis Software, and **Redis Iris**, the context engine for AI agents. Everything that reaches this site is verified by running it; every price, limit and version carries the date it was read.

### What Redis is in 2026

Since 8.0 (GA 2025-05-01) there is one distribution, Redis Open Source: the core data structures plus Search, JSON, Time series, five probabilistic types and vector sets (beta), under a choice of RSALv2, SSPLv1 or AGPLv3. Latest GA read 2026-11-07: 8.10.3 ([releases](https://github.com/redis/redis/releases)). Three ways to run it:

| | Redis Open Source | Redis Software | Redis Cloud |
|---|---|---|---|
| Who runs it | You | You, on your hosts or Kubernetes | Redis Ltd. on AWS, GCP, Azure |
| Licence | RSALv2 / SSPLv1 / AGPLv3 | Commercial | Essentials (from $5/mo) · Pro (min $200/mo) |
| Adds | — | Active-Active, Flex, DMC proxy, RBAC/LDAP, RDI, operator | the same, managed; Iris services |
| Used by | `local/`, `deep-dive/`, `compare/01` | `enterprise/` | `cloud/`, `iris/` |

### Tracks

| Track | Status | What |
|---|---|---|
| [Setup]({{ '/setup/' | relative_url }}) | Not started | Redis 8 in Docker, `redis-cli`, Redis Insight, clients, a free Redis Cloud database |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | Free parts run 2026-11-07 | The console from sign-up to every menu; free and paid plans; REST API; Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | Not started | What Redis Software and Cloud Pro add, each tied to a lab or marked doc-only |
| [Iris]({{ '/iris/' | relative_url }}) | Not started | The Iris services, one lab each, on the free plan |
| [Compare]({{ '/compare/' | relative_url }}) | Not started | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | Not started | Threading, persistence, replication, Cluster, eviction, caching, Streams, Functions, ACL |

<div class="warn" markdown="1">
**Cost warning.** A paid Redis Cloud Essentials database bills monthly from the moment it is created; Pro has a $200/month minimum ("first $200 free", terms unpublished). Iris starts with 5,000 free messages. Delete what a lab creates. Prices read 2026-11-07 at [redis.io/pricing](https://redis.io/pricing/).
</div>

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 설계만.** 이 페이지의 내용은 아직 아무것도 실행하지 않았다. 계획은 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)에 있다.
</div>

[Redis](https://redis.io)를 손으로 익히는 실습 — Redis Open Source, Redis Cloud, Redis Software, 그리고 AI 에이전트용 컨텍스트 엔진 **Redis Iris**. 이 사이트에 올라오는 것은 모두 실행해 확인한 것이고, 가격·한도·버전에는 읽은 날짜가 붙는다.

### 2026년의 Redis

8.0(GA 2025-05-01)부터 배포판은 하나, Redis Open Source다. 핵심 자료형에 Search, JSON, Time series, 확률형 자료구조 다섯, 벡터 셋(베타)이 들어 있고 RSALv2 / SSPLv1 / AGPLv3 중 고른다. 2026-11-07에 읽은 최신 GA는 8.10.3([releases](https://github.com/redis/redis/releases)). 실행 방식은 셋:

| | Redis Open Source | Redis Software | Redis Cloud |
|---|---|---|---|
| 누가 운영 | 나 | 나, 내 호스트나 Kubernetes에서 | Redis Ltd., AWS·GCP·Azure에서 |
| 라이선스 | RSALv2 / SSPLv1 / AGPLv3 | 상용 | Essentials(월 $5부터) · Pro(최소 월 $200) |
| 더해 주는 것 | — | Active-Active, Flex, DMC 프록시, RBAC/LDAP, RDI, 오퍼레이터 | 같은 것을 관리형으로; Iris 서비스 |
| 쓰는 트랙 | `local/`, `deep-dive/`, `compare/01` | `enterprise/` | `cloud/`, `iris/` |

### 트랙

| 트랙 | 상태 | 내용 |
|---|---|---|
| [Setup]({{ '/setup/' | relative_url }}) | 미착수 | Docker의 Redis 8, `redis-cli`, Redis Insight, 클라이언트, 무료 Redis Cloud DB |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | 무료 부분 실행 2026-11-07 | 가입부터 콘솔 메뉴 전체; 무료·유료 플랜; REST API; Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 미착수 | Redis Software와 Cloud Pro가 더해 주는 것, 랩 또는 문서만으로 구분 |
| [Iris]({{ '/iris/' | relative_url }}) | 미착수 | Iris 서비스마다 랩 하나, 무료 플랜으로 |
| [Compare]({{ '/compare/' | relative_url }}) | 미착수 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 미착수 | 스레딩, 영속성, 복제, Cluster, 축출, 캐시, Streams, Functions, ACL |

<div class="warn" markdown="1">
**비용 경고.** 유료 Redis Cloud Essentials DB는 만든 순간부터 월 단위로 과금된다. Pro는 최소 월 $200("첫 $200 무료", 조건 미공개). Iris는 무료 5,000 메시지로 시작한다. 랩이 만든 것은 지운다. 가격은 2026-11-07 [redis.io/pricing](https://redis.io/pricing/)에서 읽음.
</div>

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：仅有设计。** 本页内容尚未实际运行。计划见 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)。
</div>

[Redis](https://redis.io) 动手实验 — Redis Open Source、Redis Cloud、Redis Software，以及面向 AI 代理的上下文引擎 **Redis Iris**。本站内容均经实际运行验证；每个价格、限制和版本都标注读取日期。

### 2026 年的 Redis

自 8.0（2025-05-01 GA）起只有一个发行版 Redis Open Source：核心数据结构加 Search、JSON、Time series、五种概率型结构和向量集（beta），许可证可选 RSALv2 / SSPLv1 / AGPLv3。2026-11-07 读取的最新 GA 为 8.10.3。三种运行方式：自己运行 Open Source、自己运行 Redis Software（商业许可，增加 Active-Active、Flex、DMC 代理、RDI、operator），或由 Redis Ltd. 托管的 Redis Cloud（Essentials 每月 $5 起，Pro 最低每月 $200；Iris 服务在此）。

### 实验分类

| 分类 | 状态 | 内容 |
|---|---|---|
| [Setup]({{ '/setup/' | relative_url }}) | 未开始 | Docker 中的 Redis 8、`redis-cli`、Redis Insight、客户端、免费 Redis Cloud 数据库 |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | 免费部分已运行 2026-11-07 | 从注册到控制台每个菜单；免费与付费方案；REST API；Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 未开始 | Redis Software 与 Cloud Pro 的增强功能，各自对应实验或仅文档 |
| [Iris]({{ '/iris/' | relative_url }}) | 未开始 | 每个 Iris 服务一个实验，使用免费方案 |
| [Compare]({{ '/compare/' | relative_url }}) | 未开始 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 未开始 | 线程、持久化、复制、Cluster、淘汰、缓存、Streams、Functions、ACL |

<div class="warn" markdown="1">
**费用提醒。** 付费 Redis Cloud Essentials 数据库自创建起按月计费；Pro 最低每月 $200（"首 $200 免费"，条款未公布）。Iris 提供 5,000 条免费消息。实验结束请删除所创建的资源。价格于 2026-11-07 读取自 [redis.io/pricing](https://redis.io/pricing/)。
</div>

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**状態: 設計のみ。** このページの内容はまだ何も実行していない。計画は [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) にある。
</div>

[Redis](https://redis.io) のハンズオンラボ — Redis Open Source、Redis Cloud、Redis Software、そして AI エージェント向けコンテキストエンジン **Redis Iris**。このサイトの内容はすべて実行して確認したもので、価格・上限・バージョンには読んだ日付が付く。

### 2026 年の Redis

8.0（2025-05-01 GA）以降、ディストリビューションは Redis Open Source ひとつ。コアのデータ型に Search、JSON、Time series、確率的データ構造 5 種、ベクトルセット（ベータ）が含まれ、ライセンスは RSALv2 / SSPLv1 / AGPLv3 から選ぶ。2026-11-07 に読んだ最新 GA は 8.10.3。実行方法は三つ: Open Source を自分で、Redis Software を自分のホストや Kubernetes で（商用ライセンス、Active-Active・Flex・DMC プロキシ・RDI・オペレーターを追加）、Redis Ltd. が運用する Redis Cloud（Essentials 月 $5 から、Pro 最低月 $200、Iris サービスはここ）。

### トラック

| トラック | 状態 | 内容 |
|---|---|---|
| [Setup]({{ '/setup/' | relative_url }}) | 未着手 | Docker の Redis 8、`redis-cli`、Redis Insight、クライアント、無料の Redis Cloud DB |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | 無料部分を実行 2026-11-07 | サインアップからコンソールの全メニュー、無料・有料プラン、REST API、Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 未着手 | Redis Software と Cloud Pro が加えるもの、ラボまたはドキュメントのみを明示 |
| [Iris]({{ '/iris/' | relative_url }}) | 未着手 | Iris サービスごとにラボひとつ、無料プランで |
| [Compare]({{ '/compare/' | relative_url }}) | 未着手 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 未着手 | スレッド、永続化、レプリケーション、Cluster、エビクション、キャッシュ、Streams、Functions、ACL |

<div class="warn" markdown="1">
**コストの注意。** 有料の Redis Cloud Essentials DB は作成した瞬間から月額課金される。Pro は最低月 $200（「最初の $200 は無料」、条件未公開）。Iris は無料 5,000 メッセージから。ラボが作ったものは削除する。価格は 2026-11-07 に [redis.io/pricing](https://redis.io/pricing/) で読んだ。
</div>

</div>
