---
layout: default
title: Overview
permalink: /
---

# Notes on Redis

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
| [Setup]({{ '/setup/' | relative_url }}) | Run 2026-11-07 | Redis 8 in Docker, `redis-cli`, Redis Insight, clients, a free Redis Cloud database |
| [Architecture]({{ '/architecture/' | relative_url }}) | Written 2026-11-07 from this site's runs | Where Redis and Iris sit in a system, and why they are strong there |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | Free parts run 2026-11-07 | The console from sign-up to every menu; free and paid plans; REST API; Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 01–03 run 2026-11-07 | What Redis Software and Cloud Pro add, each tied to a lab or marked doc-only |
| [Iris]({{ '/iris/' | relative_url }}) | 01–06 run 2026-11-07 (Lens: SDK only) | The Iris services, one lab each, on the free plan |
| [Compare]({{ '/compare/' | relative_url }}) | Valkey locally and ElastiCache run 2026-11-07 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 01–08 run 2026-11-07 | Threading, persistence, replication, Cluster, eviction, caching, Streams, Functions, ACL |

<div class="warn" markdown="1">
**Cost warning.** A paid Redis Cloud Essentials database bills monthly from the moment it is created; Pro has a $200/month minimum ("first $200 free", terms unpublished). Iris starts with 5,000 free messages. Prices read 2026-11-07 at [redis.io/pricing](https://redis.io/pricing/).
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
| [Setup]({{ '/setup/' | relative_url }}) | 실행 2026-11-07 | Docker의 Redis 8, `redis-cli`, Redis Insight, 클라이언트, 무료 Redis Cloud DB |
| [Architecture]({{ '/architecture/' | relative_url }}) | 2026-11-07 이 사이트의 실행 결과로 작성 | 시스템에서 Redis와 Iris가 놓이는 자리와 거기서 강한 이유 |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | 무료 부분 실행 2026-11-07 | 가입부터 콘솔 메뉴 전체; 무료·유료 플랜; REST API; Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 01–03 실행 2026-11-07 | Redis Software와 Cloud Pro가 더해 주는 것, 랩 또는 문서만으로 구분 |
| [Iris]({{ '/iris/' | relative_url }}) | 01–06 실행 2026-11-07(Lens는 SDK만) | Iris 서비스마다 랩 하나, 무료 플랜으로 |
| [Compare]({{ '/compare/' | relative_url }}) | 로컬 Valkey와 ElastiCache 실행 2026-11-07 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 01–08 실행 2026-11-07 | 스레딩, 영속성, 복제, Cluster, 축출, 캐시, Streams, Functions, ACL |

<div class="warn" markdown="1">
**비용 경고.** 유료 Redis Cloud Essentials DB는 만든 순간부터 월 단위로 과금된다. Pro는 최소 월 $200("첫 $200 무료", 조건 미공개). Iris는 무료 5,000 메시지로 시작한다. 가격은 2026-11-07 [redis.io/pricing](https://redis.io/pricing/)에서 읽음.
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
| [Setup]({{ '/setup/' | relative_url }}) | 已运行 2026-11-07 | Docker 中的 Redis 8、`redis-cli`、Redis Insight、客户端、免费 Redis Cloud 数据库 |
| [Architecture]({{ '/architecture/' | relative_url }}) | 2026-11-07 依据本站运行结果编写 | Redis 与 Iris 在系统中的位置，以及它们在那里的优势 |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | 免费部分已运行 2026-11-07 | 从注册到控制台每个菜单；免费与付费方案；REST API；Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 01–03 已运行 2026-11-07 | Redis Software 与 Cloud Pro 的增强功能，各自对应实验或仅文档 |
| [Iris]({{ '/iris/' | relative_url }}) | 01–06 已运行 2026-11-07（Lens 仅 SDK） | 每个 Iris 服务一个实验，使用免费方案 |
| [Compare]({{ '/compare/' | relative_url }}) | 本地 Valkey 与 ElastiCache 已运行 2026-11-07 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 01–08 已运行 2026-11-07 | 线程、持久化、复制、Cluster、淘汰、缓存、Streams、Functions、ACL |

<div class="warn" markdown="1">
**费用提醒。** 付费 Redis Cloud Essentials 数据库自创建起按月计费；Pro 最低每月 $200（"首 $200 免费"，条款未公布）。Iris 提供 5,000 条免费消息。价格于 2026-11-07 读取自 [redis.io/pricing](https://redis.io/pricing/)。
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
| [Setup]({{ '/setup/' | relative_url }}) | 実行済み 2026-11-07 | Docker の Redis 8、`redis-cli`、Redis Insight、クライアント、無料の Redis Cloud DB |
| [Architecture]({{ '/architecture/' | relative_url }}) | 2026-11-07 本サイトの実行結果から作成 | システムの中で Redis と Iris が置かれる場所と、そこで強い理由 |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | 無料部分を実行 2026-11-07 | サインアップからコンソールの全メニュー、無料・有料プラン、REST API、Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 01–03 実行済み 2026-11-07 | Redis Software と Cloud Pro が加えるもの、ラボまたはドキュメントのみを明示 |
| [Iris]({{ '/iris/' | relative_url }}) | 01–06 実行済み 2026-11-07（Lens は SDK のみ） | Iris サービスごとにラボひとつ、無料プランで |
| [Compare]({{ '/compare/' | relative_url }}) | ローカル Valkey と ElastiCache を実行 2026-11-07 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 01–08 実行済み 2026-11-07 | スレッド、永続化、レプリケーション、Cluster、エビクション、キャッシュ、Streams、Functions、ACL |

<div class="warn" markdown="1">
**コストの注意。** 有料の Redis Cloud Essentials DB は作成した瞬間から月額課金される。Pro は最低月 $200（「最初の $200 は無料」、条件未公開）。Iris は無料 5,000 メッセージから。価格は 2026-11-07 に [redis.io/pricing](https://redis.io/pricing/) で読んだ。
</div>

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: มีเฉพาะการออกแบบ** ยังไม่ได้รันสิ่งใดในหน้านี้ แผนอยู่ใน [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)
</div>

แล็บภาคปฏิบัติสำหรับ [Redis](https://redis.io) ครอบคลุม Redis Open Source, Redis Cloud, Redis Software และ **Redis Iris** ซึ่งเป็น context engine สำหรับ AI agent ทุกอย่างที่ขึ้นเว็บไซต์นี้ผ่านการรันตรวจสอบจริง และทุกราคา ขีดจำกัด และเวอร์ชันจะระบุวันที่ที่อ่านข้อมูลนั้น

### Redis ในปี 2026 คืออะไร

ตั้งแต่เวอร์ชัน 8.0 (GA 2025-05-01) มีการแจกจ่ายเพียงแบบเดียวคือ Redis Open Source ประกอบด้วยโครงสร้างข้อมูลหลัก พร้อม Search, JSON, Time series, ชนิดข้อมูลเชิงความน่าจะเป็นห้าชนิด และ vector sets (beta) โดยเลือกใช้สัญญาอนุญาตได้ระหว่าง RSALv2, SSPLv1 หรือ AGPLv3 เวอร์ชัน GA ล่าสุดที่อ่านเมื่อ 2026-11-07 คือ 8.10.3 ([releases](https://github.com/redis/redis/releases)) มีสามวิธีในการรัน:

| | Redis Open Source | Redis Software | Redis Cloud |
|---|---|---|---|
| ผู้ดำเนินการ | คุณเอง | คุณเอง บนโฮสต์หรือ Kubernetes ของคุณ | Redis Ltd. บน AWS, GCP, Azure |
| สัญญาอนุญาต | RSALv2 / SSPLv1 / AGPLv3 | เชิงพาณิชย์ | Essentials (เริ่มที่ $5/เดือน) · Pro (ขั้นต่ำ $200/เดือน) |
| สิ่งที่เพิ่ม | — | Active-Active, Flex, DMC proxy, RBAC/LDAP, RDI, operator | เหมือนกัน แต่มีผู้ให้บริการจัดการให้ พร้อมบริการ Iris |
| ใช้โดย | `local/`, `deep-dive/`, `compare/01` | `enterprise/` | `cloud/`, `iris/` |

### แทร็ก

| แทร็ก | สถานะ | เนื้อหา |
|---|---|---|
| [Setup]({{ '/setup/' | relative_url }}) | รันแล้ว 2026-11-07 | Redis 8 ใน Docker, `redis-cli`, Redis Insight, ไคลเอนต์ และฐานข้อมูล Redis Cloud แบบฟรี |
| [Architecture]({{ '/architecture/' | relative_url }}) | เขียนเมื่อ 2026-11-07 จากผลการรันของไซต์นี้ | ตำแหน่งของ Redis และ Iris ในระบบ และจุดแข็งในตำแหน่งนั้น |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | ส่วนที่ฟรีรันเมื่อ 2026-11-07 | คอนโซลตั้งแต่การสมัครไปจนถึงทุกเมนู แผนฟรีและแผนเสียเงิน REST API และ Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 01–03 รันแล้ว 2026-11-07 | สิ่งที่ Redis Software และ Cloud Pro เพิ่มเข้ามา โดยแต่ละรายการผูกกับแล็บหรือระบุว่าเป็นเอกสารเท่านั้น |
| [Iris]({{ '/iris/' | relative_url }}) | 01–06 รันแล้ว 2026-11-07 (Lens เฉพาะ SDK) | บริการของ Iris หนึ่งแล็บต่อหนึ่งบริการ บนแผนฟรี |
| [Compare]({{ '/compare/' | relative_url }}) | Valkey แบบโลคัลและ ElastiCache รันแล้ว 2026-11-07 | Redis เทียบกับ Valkey, ElastiCache, Memorystore และ Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 01–08 รันแล้ว 2026-11-07 | Threading, persistence, replication, Cluster, eviction, caching, Streams, Functions, ACL |

<div class="warn" markdown="1">
**คำเตือนเรื่องค่าใช้จ่าย** ฐานข้อมูล Redis Cloud Essentials แบบเสียเงินจะคิดค่าบริการรายเดือนตั้งแต่ขณะที่สร้าง ส่วน Pro มีขั้นต่ำ $200/เดือน ("first $200 free" ยังไม่เผยแพร่เงื่อนไข) Iris เริ่มต้นด้วยข้อความฟรี 5,000 ข้อความ ราคาอ่านเมื่อ 2026-11-07 ที่ [redis.io/pricing](https://redis.io/pricing/)
</div>

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: baru desain.** Belum ada isi halaman ini yang dijalankan. Rencananya ada di [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Lab praktik untuk [Redis](https://redis.io): Redis Open Source, Redis Cloud, Redis Software, dan **Redis Iris**, context engine untuk agen AI. Semua yang masuk ke situs ini diverifikasi dengan menjalankannya; setiap harga, batas, dan versi mencantumkan tanggal saat dibaca.

### Redis pada 2026

Sejak 8.0 (GA 2025-05-01) hanya ada satu distribusi, yaitu Redis Open Source: struktur data inti ditambah Search, JSON, Time series, lima tipe probabilistik, dan vector sets (beta), dengan pilihan lisensi RSALv2, SSPLv1, atau AGPLv3. GA terbaru yang dibaca pada 2026-11-07: 8.10.3 ([releases](https://github.com/redis/redis/releases)). Ada tiga cara menjalankannya:

| | Redis Open Source | Redis Software | Redis Cloud |
|---|---|---|---|
| Pengelola | Anda | Anda, di host atau Kubernetes Anda | Redis Ltd. di AWS, GCP, Azure |
| Lisensi | RSALv2 / SSPLv1 / AGPLv3 | Komersial | Essentials (mulai $5/bln) · Pro (min $200/bln) |
| Tambahan | — | Active-Active, Flex, DMC proxy, RBAC/LDAP, RDI, operator | sama, dikelola penyedia; layanan Iris |
| Dipakai oleh | `local/`, `deep-dive/`, `compare/01` | `enterprise/` | `cloud/`, `iris/` |

### Jalur

| Jalur | Status | Isi |
|---|---|---|
| [Setup]({{ '/setup/' | relative_url }}) | Dijalankan 2026-11-07 | Redis 8 di Docker, `redis-cli`, Redis Insight, klien, dan database Redis Cloud gratis |
| [Architecture]({{ '/architecture/' | relative_url }}) | Ditulis 2026-11-07 dari hasil situs ini | Posisi Redis dan Iris dalam sistem, dan mengapa kuat di sana |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | Bagian gratis dijalankan 2026-11-07 | Konsol dari pendaftaran hingga setiap menu; paket gratis dan berbayar; REST API; Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 01–03 dijalankan 2026-11-07 | Yang ditambahkan Redis Software dan Cloud Pro, masing-masing terkait satu lab atau ditandai hanya dokumentasi |
| [Iris]({{ '/iris/' | relative_url }}) | 01–06 dijalankan 2026-11-07 (Lens: hanya SDK) | Layanan Iris, satu lab per layanan, pada paket gratis |
| [Compare]({{ '/compare/' | relative_url }}) | Valkey lokal dan ElastiCache dijalankan 2026-11-07 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 01–08 dijalankan 2026-11-07 | Threading, persistence, replication, Cluster, eviction, caching, Streams, Functions, ACL |

<div class="warn" markdown="1">
**Peringatan biaya.** Database Redis Cloud Essentials berbayar ditagih bulanan sejak dibuat; Pro memiliki minimum $200/bulan ("first $200 free", ketentuan belum dipublikasikan). Iris dimulai dengan 5.000 pesan gratis. Harga dibaca 2026-11-07 di [redis.io/pricing](https://redis.io/pricing/).
</div>

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: reka bentuk sahaja.** Belum ada kandungan halaman ini yang dijalankan. Pelannya terdapat dalam [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Makmal amali untuk [Redis](https://redis.io): Redis Open Source, Redis Cloud, Redis Software dan **Redis Iris**, context engine untuk ejen AI. Semua yang sampai ke tapak ini disahkan dengan menjalankannya; setiap harga, had dan versi mencatatkan tarikh ia dibaca.

### Redis pada 2026

Sejak 8.0 (GA 2025-05-01) hanya ada satu pengedaran, iaitu Redis Open Source: struktur data teras ditambah Search, JSON, Time series, lima jenis kebarangkalian dan vector sets (beta), dengan pilihan lesen RSALv2, SSPLv1 atau AGPLv3. GA terkini yang dibaca pada 2026-11-07: 8.10.3 ([releases](https://github.com/redis/redis/releases)). Terdapat tiga cara untuk menjalankannya:

| | Redis Open Source | Redis Software | Redis Cloud |
|---|---|---|---|
| Siapa yang mengendalikan | Anda | Anda, pada hos atau Kubernetes anda | Redis Ltd. di AWS, GCP, Azure |
| Lesen | RSALv2 / SSPLv1 / AGPLv3 | Komersial | Essentials (bermula $5/bln) · Pro (min $200/bln) |
| Tambahan | — | Active-Active, Flex, DMC proxy, RBAC/LDAP, RDI, operator | sama, diurus oleh penyedia; perkhidmatan Iris |
| Digunakan oleh | `local/`, `deep-dive/`, `compare/01` | `enterprise/` | `cloud/`, `iris/` |

### Trek

| Trek | Status | Kandungan |
|---|---|---|
| [Setup]({{ '/setup/' | relative_url }}) | Dijalankan 2026-11-07 | Redis 8 dalam Docker, `redis-cli`, Redis Insight, klien dan pangkalan data Redis Cloud percuma |
| [Architecture]({{ '/architecture/' | relative_url }}) | Ditulis 2026-11-07 daripada keputusan laman ini | Kedudukan Redis dan Iris dalam sistem, dan sebab ia kukuh di situ |
| [Redis Cloud]({{ '/cloud/' | relative_url }}) | Bahagian percuma dijalankan 2026-11-07 | Konsol dari pendaftaran hingga setiap menu; pelan percuma dan berbayar; REST API; Active-Active |
| [Enterprise]({{ '/enterprise/' | relative_url }}) | 01–03 dijalankan 2026-11-07 | Apa yang ditambah oleh Redis Software dan Cloud Pro, setiap satu dikaitkan dengan satu makmal atau ditanda sebagai dokumentasi sahaja |
| [Iris]({{ '/iris/' | relative_url }}) | 01–06 dijalankan 2026-11-07 (Lens: SDK sahaja) | Perkhidmatan Iris, satu makmal bagi setiap perkhidmatan, pada pelan percuma |
| [Compare]({{ '/compare/' | relative_url }}) | Valkey setempat dan ElastiCache dijalankan 2026-11-07 | Redis vs Valkey vs ElastiCache vs Memorystore vs Azure Managed Redis |
| [Deep Dive]({{ '/deep-dive/' | relative_url }}) | 01–08 dijalankan 2026-11-07 | Threading, persistence, replication, Cluster, eviction, caching, Streams, Functions, ACL |

<div class="warn" markdown="1">
**Amaran kos.** Pangkalan data Redis Cloud Essentials berbayar dibilkan setiap bulan sejak ia dicipta; Pro mempunyai minimum $200/bulan ("first $200 free", terma belum diterbitkan). Iris bermula dengan 5,000 mesej percuma. Harga dibaca 2026-11-07 di [redis.io/pricing](https://redis.io/pricing/).
</div>

</div>
