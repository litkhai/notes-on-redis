---
layout: default
title: Iris
permalink: /iris/
---

# Iris

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: partly run.** Agent Memory was run on the Redis Cloud free plan on 2026-11-07 (below). The other services are still the plan in [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Iris is, in Redis's words, "a production-ready context engine for AI agents" — a suite of services, not a database; Redis is the database underneath. Launched 2026-05-18; on 2026-11-04 it became six services: Intent Router, Agent Playbooks, Agent Memory and Context Gateway (GA), Lens and Agent Mesh (beta). Managed on Redis Cloud; self-managed via a Helm chart that needs a licence. One lab per service, all on the free database and the 5,000 free messages, with the messages consumed per lab recorded. The naming trap — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — gets its own section. Read 2026-11-07 at [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

### Is Iris usable on the free plan?

**Yes, as of 2026-11-07.** On a free account every Iris service in the sidebar offers a create button (Agent Memory, Agent Playbooks, Context Gateway, Intent Router, Lens); Agent Mesh is a library that runs in your own app. One Agent Memory service was created on the free 30 MB database, given two API keys, and used from the `redis-iris` 1.0.1 SDK and the `iris` CLI: health, writing a memory, a conversation, background extraction and recall all worked. The "5,000 free messages" were not shown anywhere in the console (Iris pages, Usage, Billing), so how many this lab used is unknown.

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

### Not covered yet

Agent Playbooks, Intent Router, Context Gateway, Lens and Agent Mesh have their own labs in the repository issues. Message consumption stays an open question until the console or the bill shows it.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 일부 실행.** Agent Memory를 2026-11-07에 Redis Cloud 무료 플랜에서 실행했다(아래). 나머지 서비스는 아직 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)의 계획이다.
</div>

Redis Iris는 Redis의 표현으로 "AI 에이전트를 위한 프로덕션 준비 컨텍스트 엔진" — 서비스 묶음이지 데이터베이스가 아니고, 밑에 있는 데이터베이스가 Redis다. 2026-05-18 출시, 2026-11-04에 서비스 여섯이 됨: Intent Router, Agent Playbooks, Agent Memory, Context Gateway(GA), Lens, Agent Mesh(베타). Redis Cloud 관리형, 자체 운영은 라이선스가 필요한 Helm 차트. 서비스마다 랩 하나, 모두 무료 DB와 무료 5,000 메시지로, 랩마다 소비한 메시지 수를 기록. 이름 함정 — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — 은 별도 절. 2026-11-07 [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)에서 읽음.

### 무료 플랜에서 Iris를 쓸 수 있나?

**2026-11-07 기준으로 그렇다.** 무료 계정에서도 사이드바의 Iris 서비스마다 만들기 버튼이 있다(Agent Memory, Agent Playbooks, Context Gateway, Intent Router, Lens). Agent Mesh는 내 앱 안에서 도는 라이브러리다. 무료 30 MB DB에 Agent Memory 서비스를 하나 만들고 API 키 두 개를 발급해 `redis-iris` 1.0.1 SDK와 `iris` CLI로 썼다. 상태 확인, 기억 쓰기, 대화, 백그라운드 추출, 회상이 모두 됐다. "무료 메시지 5,000개"는 콘솔 어디에도(Iris 화면, Usage, Billing) 보이지 않아, 이 실습이 몇 개를 썼는지는 모른다.

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

### 아직 다루지 않은 것

Agent Playbooks, Intent Router, Context Gateway, Lens, Agent Mesh는 저장소 이슈에 각자의 실습이 있다. 메시지 사용량은 콘솔이나 청구서에 나타날 때까지 열린 질문으로 둔다.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：部分已运行。** Agent Memory 于 2026-11-07 在 Redis Cloud 免费计划上运行过（见下文）。其他服务仍是 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) 中的计划。
</div>

Redis Iris 按 Redis 的说法是"面向 AI 代理的生产级上下文引擎" — 一组服务而非数据库，底层数据库是 Redis。2026-05-18 发布，2026-11-04 扩展为六项服务：Intent Router、Agent Playbooks、Agent Memory、Context Gateway（GA），Lens、Agent Mesh（beta）。Redis Cloud 托管；自管理需带许可证的 Helm chart。每项服务一个实验，全部使用免费数据库和 5,000 条免费消息，并记录每个实验消耗的消息数。命名陷阱 — Context Retriever → Context Gateway、LangCache 与 Agent Playbooks — 单独成节。2026-11-07 读取自 [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)。

### 免费计划能用 Iris 吗？

**能，截至 2026-11-07。** 在免费账户上，侧边栏中的每项 Iris 服务都有创建按钮（Agent Memory、Agent Playbooks、Context Gateway、Intent Router、Lens）；Agent Mesh 是在你自己的应用中运行的库。在免费的 30 MB 数据库上创建了一个 Agent Memory 服务，生成两个 API 密钥，并通过 `redis-iris` 1.0.1 SDK 和 `iris` CLI 使用：健康检查、写入记忆、对话、后台提取和召回都正常。控制台的任何位置（Iris 页面、Usage、Billing）都没有显示“5,000 条免费消息”，因此本实验用了多少条未知。

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

### 尚未涵盖

Agent Playbooks、Intent Router、Context Gateway、Lens 和 Agent Mesh 在仓库的 issue 中各有自己的实验。消息消耗量仍是未解问题，直到控制台或账单显示出来。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**状況：一部実行済み。** Agent Memory を 2026-11-07 に Redis Cloud の無料プランで実行した（下記）。ほかのサービスは引き続き [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) の計画である。
</div>

Redis Iris は Redis の言葉では「AI エージェント向けの本番対応コンテキストエンジン」 — サービス群でありデータベースではなく、その下にあるデータベースが Redis。2026-05-18 公開、2026-11-04 に六つのサービスに: Intent Router、Agent Playbooks、Agent Memory、Context Gateway（GA）、Lens、Agent Mesh（ベータ）。Redis Cloud のマネージド、セルフマネージドはライセンスが必要な Helm チャート。サービスごとにラボ一つ、すべて無料 DB と無料 5,000 メッセージで行い、ラボごとの消費メッセージ数を記録。名前の罠 — Context Retriever → Context Gateway、LangCache と Agent Playbooks — は別の節。2026-11-07 に [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/) で読んだ。

### 無料プランで Iris は使えるか？

**使える（2026-11-07 時点）。** 無料アカウントでも、サイドバーの Iris サービスにはそれぞれ作成ボタンがある（Agent Memory、Agent Playbooks、Context Gateway、Intent Router、Lens）。Agent Mesh は自分のアプリ内で動くライブラリである。無料の 30 MB データベースに Agent Memory サービスを一つ作り、API キーを二つ発行して、`redis-iris` 1.0.1 SDK と `iris` CLI で使った。ヘルスチェック、記憶の書き込み、会話、バックグラウンド抽出、想起がすべて動いた。「無料 5,000 メッセージ」はコンソールのどこにも（Iris 画面、Usage、Billing）表示されなかったため、この実習で何件使ったかは不明である。

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

### まだ扱っていないもの

Agent Playbooks、Intent Router、Context Gateway、Lens、Agent Mesh は、リポジトリの issue にそれぞれの実習がある。メッセージ消費量は、コンソールか請求書に表示されるまで未解決の問いとして残す。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: รันแล้วบางส่วน** Agent Memory ถูกรันบนแผนฟรีของ Redis Cloud เมื่อ 2026-11-07 (ด้านล่าง) บริการอื่นยังเป็นแผนใน [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)
</div>

Redis Iris ตามคำของ Redis คือ "a production-ready context engine for AI agents" เป็นชุดบริการ ไม่ใช่ฐานข้อมูล โดยมี Redis เป็นฐานข้อมูลอยู่ข้างใต้ เปิดตัวเมื่อ 2026-05-18 และเมื่อ 2026-11-04 กลายเป็นหกบริการ ได้แก่ Intent Router, Agent Playbooks, Agent Memory และ Context Gateway (GA) รวมถึง Lens และ Agent Mesh (beta) ให้บริการแบบจัดการให้บน Redis Cloud ส่วนแบบดูแลเองใช้ Helm chart ซึ่งต้องมีใบอนุญาต มีหนึ่งแล็บต่อหนึ่งบริการ ทั้งหมดใช้ฐานข้อมูลฟรีและข้อความฟรี 5,000 ข้อความ โดยบันทึกจำนวนข้อความที่แต่ละแล็บใช้ไป กับดักเรื่องชื่อ คือ Context Retriever → Context Gateway และ LangCache เทียบกับ Agent Playbooks มีหัวข้อแยกต่างหาก อ่านเมื่อ 2026-11-07 ที่ [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)

### ใช้ Iris บนแผนฟรีได้หรือไม่?

**ได้ ณ วันที่ 2026-11-07** บนบัญชีฟรี ทุกบริการ Iris ในแถบด้านข้างมีปุ่มสร้าง (Agent Memory, Agent Playbooks, Context Gateway, Intent Router, Lens) ส่วน Agent Mesh เป็นไลบรารีที่รันในแอปของคุณเอง ได้สร้างบริการ Agent Memory หนึ่งรายการบนฐานข้อมูลฟรีขนาด 30 MB ออก API key สองตัว และใช้งานผ่าน SDK `redis-iris` 1.0.1 และ `iris` CLI ตรวจสถานะ เขียนหน่วยความจำ สนทนา การสกัดเบื้องหลัง และการเรียกคืนทำงานได้ทั้งหมด "5,000 ข้อความฟรี" ไม่แสดงที่ใดในคอนโซล (หน้า Iris, Usage, Billing) จึงไม่ทราบว่าแล็บนี้ใช้ไปกี่ข้อความ

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

### ยังไม่ครอบคลุม

Agent Playbooks, Intent Router, Context Gateway, Lens และ Agent Mesh มีแล็บของตนเองใน issue ของรีโพสิทอรี การใช้ข้อความยังเป็นคำถามที่เปิดอยู่ จนกว่าคอนโซลหรือใบแจ้งหนี้จะแสดงให้เห็น

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: sebagian dijalankan.** Agent Memory dijalankan pada paket gratis Redis Cloud pada 2026-11-07 (di bawah). Layanan lainnya masih berupa rencana di [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Iris, menurut Redis, adalah "a production-ready context engine for AI agents", yaitu kumpulan layanan, bukan basis data; Redis adalah basis data di bawahnya. Diluncurkan 2026-05-18; pada 2026-11-04 menjadi enam layanan: Intent Router, Agent Playbooks, Agent Memory dan Context Gateway (GA), Lens dan Agent Mesh (beta). Dikelola di Redis Cloud; untuk dikelola sendiri tersedia Helm chart yang memerlukan lisensi. Satu lab per layanan, semuanya memakai basis data gratis dan 5.000 pesan gratis, dengan jumlah pesan yang terpakai per lab dicatat. Jebakan penamaan, yaitu Context Retriever → Context Gateway serta LangCache vs Agent Playbooks, dibahas di bagian tersendiri. Dibaca 2026-11-07 di [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

### Apakah Iris dapat digunakan pada paket gratis?

**Ya, per 2026-11-07.** Pada akun gratis, setiap layanan Iris di bilah sisi memiliki tombol buat (Agent Memory, Agent Playbooks, Context Gateway, Intent Router, Lens); Agent Mesh adalah pustaka yang berjalan di aplikasi Anda sendiri. Satu layanan Agent Memory dibuat pada basis data gratis 30 MB, diberi dua kunci API, dan digunakan dari SDK `redis-iris` 1.0.1 serta CLI `iris`: pemeriksaan kesehatan, penulisan memori, percakapan, ekstraksi latar belakang, dan pemanggilan kembali semuanya berfungsi. "5.000 pesan gratis" tidak ditampilkan di mana pun di konsol (halaman Iris, Usage, Billing), sehingga jumlah yang dipakai lab ini tidak diketahui.

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

### Belum dibahas

Agent Playbooks, Intent Router, Context Gateway, Lens, dan Agent Mesh memiliki lab masing-masing di issue repositori. Konsumsi pesan tetap menjadi pertanyaan terbuka sampai konsol atau tagihan menunjukkannya.

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: sebahagian dijalankan.** Agent Memory dijalankan pada pelan percuma Redis Cloud pada 2026-11-07 (di bawah). Perkhidmatan lain masih berupa rancangan dalam [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Iris, menurut Redis, ialah "a production-ready context engine for AI agents", iaitu suite perkhidmatan, bukan pangkalan data; Redis ialah pangkalan data di bawahnya. Dilancarkan 2026-05-18; pada 2026-11-04 ia menjadi enam perkhidmatan: Intent Router, Agent Playbooks, Agent Memory dan Context Gateway (GA), Lens dan Agent Mesh (beta). Diurus di Redis Cloud; untuk diurus sendiri tersedia Helm chart yang memerlukan lesen. Satu makmal bagi setiap perkhidmatan, kesemuanya menggunakan pangkalan data percuma dan 5,000 mesej percuma, dengan bilangan mesej yang digunakan setiap makmal direkodkan. Perangkap penamaan, iaitu Context Retriever → Context Gateway serta LangCache vs Agent Playbooks, diberi bahagian tersendiri. Dibaca 2026-11-07 di [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

### Bolehkah Iris digunakan pada pelan percuma?

**Ya, setakat 2026-11-07.** Pada akaun percuma, setiap perkhidmatan Iris di bar sisi mempunyai butang cipta (Agent Memory, Agent Playbooks, Context Gateway, Intent Router, Lens); Agent Mesh ialah pustaka yang berjalan dalam aplikasi anda sendiri. Satu perkhidmatan Agent Memory dicipta pada pangkalan data percuma 30 MB, diberi dua kunci API, dan digunakan daripada SDK `redis-iris` 1.0.1 serta CLI `iris`: semakan kesihatan, penulisan memori, perbualan, pengekstrakan latar belakang dan ingatan semula semuanya berfungsi. "5,000 mesej percuma" tidak dipaparkan di mana-mana dalam konsol (halaman Iris, Usage, Billing), jadi bilangan yang digunakan oleh makmal ini tidak diketahui.

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

### Belum diliputi

Agent Playbooks, Intent Router, Context Gateway, Lens dan Agent Mesh mempunyai makmal masing-masing dalam isu repositori. Penggunaan mesej kekal sebagai soalan terbuka sehingga konsol atau bil menunjukkannya.

</div>
