---
layout: default
title: Compare
permalink: /compare/
---

# Compare

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: partly run.** The ElastiCache section below was run on 2026-11-07; the rest of this page is still the plan in [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Open Source 8.x, Redis Cloud / Software, Valkey 9.x, ElastiCache for Valkey and for Redis OSS (≤ 7.1), Azure Managed Redis (Redis Enterprise inside), Memorystore for Valkey — a matrix with a source per cell (licence, modules, Active-Active, tiering, SLA, pricing model), the licence timeline (BSD-3 → RSALv2/SSPL at 7.4 → AGPLv3 added at 8.0; Valkey forked 7.2.4 under BSD-3), and the same workload run on Redis 8.10 and Valkey 9.1 side by side. Dragonfly, KeyDB and Garnet in a paragraph each.

### ElastiCache Serverless for Valkey, next to the Redis Cloud free database

**Run on 2026-11-07 in AWS ap-northeast-2 (Seoul).** One serverless cache, Valkey 9.0, created and deleted in the console; it lived about 31 minutes. Same probe script and same client host in Korea as the [Redis Cloud free database lab]({{ '/cloud/' | relative_url }}). Prices from the AWS price list for Seoul published 2026-10-28, read 2026-11-07. Masked: account ID and alias, ARNs, endpoints.

#### What differed

| | Redis Cloud free database | ElastiCache Serverless for Valkey |
|---|---|---|
| Cost | $0 for 30 MB | $0.101 per GB-hour of data (100 MB minimum, about $7.4 a month idle) plus $0.0027 per million ECPUs |
| Created to usable | seconds | 58 s |
| Engine | Redis 8.6.2 | Valkey 9.0 (9, 8 and 7 offered); `INFO` reports `redis_version:7.2` |
| Network | public endpoint; CIDR allow list, 0.0.0.0/0 by default | VPC by default; a Public connection type that requires IAM authentication |
| Authentication | default user and password | IAM: a SigV4 token valid 15 minutes, user `default.iam-user` |
| TLS | off by default | always on |
| Multi-key commands | `MGET` over any keys worked | cross-slot `MGET` refused: `Keys in request don't hash to the same slot` |
| Connections | connection 31 refused | 40 opened without error |
| Memory | writes refused at about 28 MB | writes refused after about 1.77 GB of 10 kB values, with a 1 GB storage limit set |
| Backups | none on the free plan | automatic backups off by default; the delete dialog defaults to a final backup |
| Metrics | 16 charts in the console, 5 minutes to 3 months | CloudWatch; 16 of 50 metrics on the cache page |
| Programmatic access | REST API with account and user keys, Terraform and Pulumi | AWS API, CLI, CloudFormation; an MCP server for ElastiCache |

#### Client measurements

| Probe | Redis Cloud free, plain TCP | ElastiCache Serverless, TLS + IAM |
|---|---|---|
| Round trip, mean of 50 `PING` | 2.6 ms | 5.1 ms |
| 1 connection, no pipeline | 249 ops/s | 287 ops/s |
| 8 connections, no pipeline | 2,363 ops/s | 2,419 ops/s |
| 1 connection, pipeline 100 | 24,671 ops/s | 4,960 ops/s |
| 8 connections, pipeline 100 | 103,920 ops/s | 24,893 ops/s over 15 s; 45,600–54,300 INCR/s in the per-second run |
| 60 s sustained, 8 × pipeline 100 | 100,840–108,780 INCR/s, steady | 0–45,785 INCR/s per 5 s; three 5-second windows at zero, no errors |

The throughput rows are not a verdict on either service: one side is plain TCP and the other TLS, the client is a single Python process in Korea, and the serverless cache was capped at 200,000 ECPUs/s (the zero windows came at about 40,000 INCR/s, below that cap; they were not explained). Unpipelined numbers are bound by the round trip on both sides.

#### The console, screen by screen

<p class="shot"><img src="{{ '/assets/img/elasticache-console/01-elasticache-dashboard.webp' | relative_url }}" width="1440" height="765" alt="ElastiCache dashboard in Seoul with no resources" loading="lazy" decoding="async"></p>

The ElastiCache dashboard: Valkey, Memcached and Redis OSS caches, global datastores, reserved nodes, backups, subnet and parameter groups, user management, migrations. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/02-valkey-caches-empty.webp' | relative_url }}" width="1440" height="765" alt="Empty Valkey caches list" loading="lazy" decoding="async"></p>

Valkey caches is a list with a Create cache button. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/03-create-valkey-serverless-default.webp' | relative_url }}" width="1440" height="1520" alt="Create Valkey cache form with engine, deployment option, creation method, name, engine version and connection type" loading="lazy" decoding="async"></p>

One form: engine (Valkey recommended, Memcached, Redis OSS), deployment (Serverless or node-based cluster), new or restored from an .rdb, engine version 9, connection type VPC. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/04-create-valkey-serverless-customize.webp' | relative_url }}" width="1440" height="2404" alt="Customized settings: network type, encryption, user group default.iam-user-group, backups, usage limits" loading="lazy" decoding="async"></p>

With Public selected the form says the user group must contain only IAM-authenticated users and fills in default.iam-user-group. Encryption in transit is enabled and cannot be turned off here; automatic backups are unchecked. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/05-create-valkey-serverless-filled.webp' | relative_url }}" width="1440" height="2604" alt="Filled form: name notes-on-redis-valkey, Public, maximum storage 1 GB, maximum 200,000 ECPUs per second" loading="lazy" decoding="async"></p>

Usage limits used as a spending cap: data storage 1 GB maximum (the form allows 1 to 5,000 GB) and 200,000 ECPUs per second maximum (1,000 to 15,000,000). <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/06-valkey-cache-details.webp' | relative_url }}" width="1440" height="1236" alt="Cache details: available, Valkey 9.0, Public, limits shown" loading="lazy" decoding="async"></p>

Details after creation: status Available, engine version 9.0, connection type Public, the two limits, endpoint on port 6379. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/07-valkey-connect-cloudshell.webp' | relative_url }}" width="1440" height="2267" alt="Connect to your cache section with CloudShell and CLI instructions" loading="lazy" decoding="async"></p>

Connect instructions: generate a SigV4 token with the Developer Toolkit, then valkey-cli -c --tls --user. Tokens last 15 minutes. Other tabs: MCP integration, Valkey GLIDE (recommended), client libraries. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/08-valkey-iam-user-group.webp' | relative_url }}" width="1440" height="800" alt="default.iam-user-group with one user default.iam-user" loading="lazy" decoding="async"></p>

The default IAM user group holds one user, default.iam-user, access string on ~* +@all, usable over Public and VPC. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/09-valkey-users.webp' | relative_url }}" width="1440" height="765" alt="Users list: default (VPC only) and default.iam-user (Public and VPC)" loading="lazy" decoding="async"></p>

Two users exist: the password-less default user (VPC only) and the IAM user. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/10-valkey-events.webp' | relative_url }}" width="1440" height="998" alt="Events tab with one event: cache created and ready to use" loading="lazy" decoding="async"></p>

Created at 14:36:59 KST, ready at 14:37:57. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/11-valkey-monitoring.webp' | relative_url }}" width="1440" height="1800" alt="Monitoring tab: data stored, ECPUs consumed, read and write latency, total commands, cache hit rate" loading="lazy" decoding="async"></p>

Monitoring after the tests: data stored peaked at 649 MB in a 5-minute datapoint; read latency up to 2.4 ms, write latency up to 1.4 ms on the server side. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/12-valkey-delete-dialog.webp' | relative_url }}" width="1440" height="765" alt="Delete dialog with final backup set to No and the name typed" loading="lazy" decoding="async"></p>

Deleting asks for the cache name and defaults to creating a final backup; No was chosen. The cache was gone from the list about 3 minutes later. <small>Captured 2026-11-07, AWS ap-northeast-2.</small>

#### Cost

The cache lived about 31 minutes. By the price list: about 0.2 GB-hours of storage (the 100 MB minimum, plus the memory test) and about 5 million ECPUs, together roughly $0.05. The AWS bill had not shown it yet when this was written; the billed amount goes into `STATUS.md` when it does.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 일부 실행.** 아래 ElastiCache 절은 2026-11-07에 실행했다. 나머지는 아직 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)의 계획이다.
</div>

Redis Open Source 8.x, Redis Cloud / Software, Valkey 9.x, ElastiCache for Valkey와 for Redis OSS(≤ 7.1), Azure Managed Redis(안은 Redis Enterprise), Memorystore for Valkey — 셀마다 출처가 있는 매트릭스(라이선스, 모듈, Active-Active, 티어링, SLA, 가격 모델), 라이선스 연표(BSD-3 → 7.4에서 RSALv2/SSPL → 8.0에서 AGPLv3 추가; Valkey는 7.2.4를 BSD-3로 포크), 그리고 Redis 8.10과 Valkey 9.1에 같은 워크로드를 나란히. Dragonfly, KeyDB, Garnet은 한 문단씩.

### ElastiCache Serverless for Valkey, Redis Cloud 무료 DB와 나란히

**2026-11-07, AWS ap-northeast-2(서울)에서 실행.** 서버리스 캐시 하나(Valkey 9.0)를 콘솔에서 만들고 지웠다. 약 31분 살아 있었다. [Redis Cloud 무료 DB 실습]({{ '/cloud/' | relative_url }})과 같은 측정 스크립트, 같은 한국의 클라이언트 호스트를 썼다. 가격은 2026-10-28에 게시된 서울 리전 AWS 가격표를 2026-11-07에 읽었다. 가린 것: 계정 ID와 별칭, ARN, 엔드포인트.

#### 다른 점

| | Redis Cloud 무료 DB | ElastiCache Serverless for Valkey |
|---|---|---|
| 비용 | 30 MB에 $0 | 데이터 GB-시간당 $0.101(최소 100 MB, 놀려 두면 월 약 $7.4)과 100만 ECPU당 $0.0027 |
| 만들기부터 사용 가능까지 | 몇 초 | 58초 |
| 엔진 | Redis 8.6.2 | Valkey 9.0(9, 8, 7 선택 가능). `INFO`는 `redis_version:7.2`로 보고 |
| 네트워크 | 공개 엔드포인트. CIDR 허용 목록, 기본 0.0.0.0/0 | 기본 VPC. Public 접속 방식은 IAM 인증 필수 |
| 인증 | 기본 사용자와 비밀번호 | IAM: 15분 유효한 SigV4 토큰, 사용자 `default.iam-user` |
| TLS | 기본 꺼짐 | 항상 켜짐 |
| 여러 키 명령 | 아무 키나 `MGET` 가능 | 슬롯이 다른 `MGET` 거절: `Keys in request don't hash to the same slot` |
| 커넥션 | 31번째 연결 거절 | 40개 오류 없이 연결 |
| 메모리 | 약 28 MB에서 쓰기 거절 | 저장 한도 1 GB를 걸었는데 10 kB 값 약 1.77 GB 뒤에 쓰기 거절 |
| 백업 | 무료 플랜에는 없음 | 자동 백업 기본 꺼짐. 삭제 창은 기본으로 마지막 백업을 만든다 |
| 지표 | 콘솔 차트 16개, 5분부터 3개월 | CloudWatch. 캐시 화면에 지표 50개 중 16개 |
| 프로그램 접근 | 계정 키와 사용자 키로 REST API, Terraform과 Pulumi | AWS API, CLI, CloudFormation. ElastiCache용 MCP 서버 |

#### 클라이언트 측정

| 측정 | Redis Cloud 무료, 평문 TCP | ElastiCache Serverless, TLS + IAM |
|---|---|---|
| 왕복, `PING` 50회 평균 | 2.6 ms | 5.1 ms |
| 연결 1개, 파이프라인 없음 | 249 ops/s | 287 ops/s |
| 연결 8개, 파이프라인 없음 | 2,363 ops/s | 2,419 ops/s |
| 연결 1개, 파이프라인 100 | 24,671 ops/s | 4,960 ops/s |
| 연결 8개, 파이프라인 100 | 103,920 ops/s | 15초 동안 24,893 ops/s. 초 단위 측정에서는 45,600–54,300 INCR/s |
| 60초 지속, 8 × 파이프라인 100 | 100,840–108,780 INCR/s, 고름 | 5초마다 0–45,785 INCR/s. 0인 5초 구간 세 번, 오류 없음 |

처리량 행은 어느 서비스에 대한 판정도 아니다. 한쪽은 평문 TCP, 다른 쪽은 TLS이고, 클라이언트는 한국의 파이썬 프로세스 하나이며, 서버리스 캐시는 초당 200,000 ECPU로 상한을 걸었다(0 구간은 그 상한보다 낮은 초당 약 40,000 INCR에서 나왔고 원인은 밝히지 못했다). 파이프라인 없는 수치는 양쪽 모두 왕복 시간에 묶인다.

#### 콘솔, 화면 순서대로

<p class="shot"><img src="{{ '/assets/img/elasticache-console/01-elasticache-dashboard.webp' | relative_url }}" width="1440" height="765" alt="리소스가 없는 서울 리전 ElastiCache 대시보드" loading="lazy" decoding="async"></p>

ElastiCache 대시보드: Valkey·Memcached·Redis OSS 캐시, 글로벌 데이터 스토어, 예약 노드, 백업, 서브넷·파라미터 그룹, 사용자 관리, 마이그레이션. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/02-valkey-caches-empty.webp' | relative_url }}" width="1440" height="765" alt="비어 있는 Valkey caches 목록" loading="lazy" decoding="async"></p>

Valkey caches는 Create cache 버튼이 있는 목록이다. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/03-create-valkey-serverless-default.webp' | relative_url }}" width="1440" height="1520" alt="엔진, 배포 방식, 생성 방식, 이름, 엔진 버전, 접속 방식이 있는 Create Valkey cache 양식" loading="lazy" decoding="async"></p>

양식 하나: 엔진(Valkey 권장, Memcached, Redis OSS), 배포(서버리스 또는 노드 기반 클러스터), 새로 만들기 또는 .rdb 복원, 엔진 버전 9, 접속 방식 VPC. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/04-create-valkey-serverless-customize.webp' | relative_url }}" width="1440" height="2404" alt="사용자화 설정: 네트워크 유형, 암호화, 사용자 그룹 default.iam-user-group, 백업, 사용량 한도" loading="lazy" decoding="async"></p>

Public을 고르면 사용자 그룹에 IAM 인증 사용자만 있어야 한다는 안내와 함께 default.iam-user-group이 채워진다. 전송 중 암호화는 켜져 있고 여기서 끌 수 없다. 자동 백업은 꺼져 있다. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/05-create-valkey-serverless-filled.webp' | relative_url }}" width="1440" height="2604" alt="채운 양식: 이름 notes-on-redis-valkey, Public, 최대 저장 1 GB, 초당 최대 200,000 ECPU" loading="lazy" decoding="async"></p>

사용량 한도를 지출 상한으로 썼다. 저장 최대 1 GB(양식은 1–5,000 GB 허용), 초당 ECPU 최대 200,000(1,000–15,000,000). <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/06-valkey-cache-details.webp' | relative_url }}" width="1440" height="1236" alt="캐시 상세: Available, Valkey 9.0, Public, 한도 표시" loading="lazy" decoding="async"></p>

생성 뒤 상세: 상태 Available, 엔진 버전 9.0, 접속 방식 Public, 한도 두 개, 6379 포트 엔드포인트. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/07-valkey-connect-cloudshell.webp' | relative_url }}" width="1440" height="2267" alt="CloudShell과 CLI 안내가 있는 Connect to your cache 절" loading="lazy" decoding="async"></p>

접속 안내: Developer Toolkit으로 SigV4 토큰을 만든 뒤 valkey-cli -c --tls --user. 토큰은 15분 유효. 다른 탭: MCP integration, Valkey GLIDE(권장), 클라이언트 라이브러리. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/08-valkey-iam-user-group.webp' | relative_url }}" width="1440" height="800" alt="사용자 default.iam-user 하나가 든 default.iam-user-group" loading="lazy" decoding="async"></p>

기본 IAM 사용자 그룹에는 사용자 default.iam-user 하나가 있다. 접근 문자열 on ~* +@all, Public과 VPC 모두 사용 가능. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/09-valkey-users.webp' | relative_url }}" width="1440" height="765" alt="사용자 목록: default(VPC 전용)와 default.iam-user(Public과 VPC)" loading="lazy" decoding="async"></p>

사용자는 둘이다. 비밀번호 없는 default 사용자(VPC 전용)와 IAM 사용자. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/10-valkey-events.webp' | relative_url }}" width="1440" height="998" alt="이벤트 하나가 있는 Events 탭: 캐시 생성 완료" loading="lazy" decoding="async"></p>

14:36:59(KST)에 만들기 시작, 14:37:57에 준비 완료. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/11-valkey-monitoring.webp' | relative_url }}" width="1440" height="1800" alt="Monitoring 탭: 저장 데이터, 소비 ECPU, 읽기·쓰기 지연, 전체 명령 수, 캐시 적중률" loading="lazy" decoding="async"></p>

시험 뒤 Monitoring: 저장 데이터는 5분 데이터포인트 기준 최고 649 MB. 서버 쪽 읽기 지연 최대 2.4 ms, 쓰기 지연 최대 1.4 ms. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/12-valkey-delete-dialog.webp' | relative_url }}" width="1440" height="765" alt="마지막 백업을 No로 두고 이름을 입력한 삭제 창" loading="lazy" decoding="async"></p>

삭제는 캐시 이름 입력을 요구하고 기본으로 마지막 백업을 만든다. No를 골랐다. 약 3분 뒤 목록에서 사라졌다. <small>2026-11-07 캡처, AWS ap-northeast-2.</small>

#### 비용

캐시는 약 31분 살아 있었다. 가격표로 계산하면 저장 약 0.2 GB-시간(최소 100 MB와 메모리 시험)과 ECPU 약 500만 개, 합쳐 약 $0.05다. 이 글을 쓸 때는 AWS 청구서에 아직 나타나지 않았다. 나타나면 청구액을 `STATUS.md`에 적는다.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：部分已运行。** 下面的 ElastiCache 一节于 2026-11-07 运行；本页其余部分仍是 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) 中的计划。
</div>

Redis Open Source 8.x、Redis Cloud / Software、Valkey 9.x、ElastiCache for Valkey 与 for Redis OSS（≤ 7.1）、Azure Managed Redis（内核为 Redis Enterprise）、Memorystore for Valkey — 每格有来源的矩阵（许可证、模块、Active-Active、分层、SLA、定价模型）、许可证时间线（BSD-3 → 7.4 起 RSALv2/SSPL → 8.0 加入 AGPLv3；Valkey 自 7.2.4 以 BSD-3 分叉），以及在 Redis 8.10 与 Valkey 9.1 上并排运行同一负载。Dragonfly、KeyDB、Garnet 各一段。

### ElastiCache Serverless for Valkey 与 Redis Cloud 免费数据库的对比

**2026-11-07 在 AWS ap-northeast-2（首尔）运行。** 在控制台创建并删除了一个 Serverless 缓存，Valkey 9.0，存续约 31 分钟。使用与 [Redis Cloud 免费数据库实验]({{ '/cloud/' | relative_url }}) 相同的探测脚本和位于韩国的同一台客户端主机。价格取自 2026-10-28 发布的 AWS 首尔价格表，2026-11-07 读取。已隐去：账户 ID 和别名、ARN、端点。

#### 差异

| | Redis Cloud free database | ElastiCache Serverless for Valkey |
|---|---|---|
| 费用 | 30 MB 为 $0 | 每 GB 小时数据 $0.101（最低 100 MB，空闲时每月约 $7.4），另加每百万 ECPU $0.0027 |
| 从创建到可用 | 数秒 | 58 秒 |
| 引擎 | Redis 8.6.2 | Valkey 9.0（提供 9、8、7）；`INFO` 报告 `redis_version:7.2` |
| 网络 | 公共端点；CIDR 允许列表，默认 0.0.0.0/0 | 默认 VPC；Public 连接类型，要求 IAM 认证 |
| 认证 | default 用户和密码 | IAM：有效期 15 分钟的 SigV4 令牌，用户 `default.iam-user` |
| TLS | 默认关闭 | 始终开启 |
| 多键命令 | 对任意键的 `MGET` 均可执行 | 跨槽 `MGET` 被拒绝：`Keys in request don't hash to the same slot` |
| 连接数 | 第 31 个连接被拒绝 | 打开 40 个，无错误 |
| 内存 | 约 28 MB 时拒绝写入 | 设置 1 GB 存储上限后，写入约 1.77 GB 的 10 kB 值后被拒绝 |
| 备份 | 免费计划无 | 自动备份默认关闭；删除对话框默认创建最终备份 |
| 指标 | 控制台 16 张图表，5 分钟到 3 个月 | CloudWatch；缓存页面显示 50 项指标中的 16 项 |
| 编程访问 | 使用账户密钥和用户密钥的 REST API，Terraform 和 Pulumi | AWS API、CLI、CloudFormation；ElastiCache 的 MCP 服务器 |

#### 客户端测量

| Probe | Redis Cloud free, plain TCP | ElastiCache Serverless, TLS + IAM |
|---|---|---|
| 往返时间，50 次 `PING` 的平均值 | 2.6 ms | 5.1 ms |
| 1 个连接，无 pipeline | 249 ops/s | 287 ops/s |
| 8 个连接，无 pipeline | 2,363 ops/s | 2,419 ops/s |
| 1 个连接，pipeline 100 | 24,671 ops/s | 4,960 ops/s |
| 8 个连接，pipeline 100 | 103,920 ops/s | 15 秒内 24,893 ops/s；按秒运行时为 45,600–54,300 INCR/s |
| 持续 60 秒，8 × pipeline 100 | 100,840–108,780 INCR/s，稳定 | 每 5 秒 0–45,785 INCR/s；三个 5 秒窗口为零，无错误 |

吞吐量各行不是对任一服务的结论：一方是明文 TCP，另一方是 TLS，客户端是位于韩国的单个 Python 进程，且 Serverless 缓存被限制在 200,000 ECPUs/s（为零的窗口出现在约 40,000 INCR/s 时，低于该上限；原因未能解释）。未使用 pipeline 的数值在两侧都受往返时间限制。

#### 控制台，逐屏查看

<p class="shot"><img src="{{ '/assets/img/elasticache-console/01-elasticache-dashboard.webp' | relative_url }}" width="1440" height="765" alt="首尔区域中没有资源的 ElastiCache 控制面板" loading="lazy" decoding="async"></p>

ElastiCache 控制面板：Valkey、Memcached 和 Redis OSS 缓存、全局数据存储、预留节点、备份、子网组和参数组、用户管理、迁移。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/02-valkey-caches-empty.webp' | relative_url }}" width="1440" height="765" alt="空的 Valkey caches 列表" loading="lazy" decoding="async"></p>

Valkey caches 是一个带有 Create cache 按钮的列表。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/03-create-valkey-serverless-default.webp' | relative_url }}" width="1440" height="1520" alt="包含引擎、部署选项、创建方式、名称、引擎版本和连接类型的 Create Valkey cache 表单" loading="lazy" decoding="async"></p>

一个表单：引擎（推荐 Valkey，另有 Memcached、Redis OSS）、部署（Serverless 或基于节点的集群）、新建或从 .rdb 恢复、引擎版本 9、连接类型 VPC。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/04-create-valkey-serverless-customize.webp' | relative_url }}" width="1440" height="2404" alt="自定义设置：网络类型、加密、用户组 default.iam-user-group、备份、使用量限制" loading="lazy" decoding="async"></p>

选择 Public 后，表单提示用户组只能包含使用 IAM 认证的用户，并自动填入 default.iam-user-group。传输中加密已启用，在此无法关闭；自动备份未勾选。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/05-create-valkey-serverless-filled.webp' | relative_url }}" width="1440" height="2604" alt="填写后的表单：名称 notes-on-redis-valkey、Public、最大存储 1 GB、每秒最多 200,000 ECPU" loading="lazy" decoding="async"></p>

将使用量限制用作支出上限：数据存储最大 1 GB（表单允许 1 到 5,000 GB），每秒最多 200,000 ECPU（1,000 到 15,000,000）。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/06-valkey-cache-details.webp' | relative_url }}" width="1440" height="1236" alt="缓存详情：Available、Valkey 9.0、Public，显示限制" loading="lazy" decoding="async"></p>

创建后的详情：状态 Available，引擎版本 9.0，连接类型 Public，两项限制，6379 端口上的端点。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/07-valkey-connect-cloudshell.webp' | relative_url }}" width="1440" height="2267" alt="包含 CloudShell 和 CLI 说明的 Connect to your cache 部分" loading="lazy" decoding="async"></p>

连接说明：用 Developer Toolkit 生成 SigV4 令牌，然后执行 valkey-cli -c --tls --user。令牌有效期 15 分钟。其他标签页：MCP integration、Valkey GLIDE（推荐）、客户端库。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/08-valkey-iam-user-group.webp' | relative_url }}" width="1440" height="800" alt="包含一个用户 default.iam-user 的 default.iam-user-group" loading="lazy" decoding="async"></p>

默认 IAM 用户组包含一个用户 default.iam-user，访问字符串为 on ~* +@all，可通过 Public 和 VPC 使用。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/09-valkey-users.webp' | relative_url }}" width="1440" height="765" alt="用户列表：default（仅 VPC）和 default.iam-user（Public 和 VPC）" loading="lazy" decoding="async"></p>

存在两个用户：无密码的 default 用户（仅 VPC）和 IAM 用户。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/10-valkey-events.webp' | relative_url }}" width="1440" height="998" alt="只有一个事件的 Events 标签页：缓存已创建并可使用" loading="lazy" decoding="async"></p>

14:36:59（KST）开始创建，14:37:57 准备就绪。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/11-valkey-monitoring.webp' | relative_url }}" width="1440" height="1800" alt="Monitoring 标签页：存储的数据、消耗的 ECPU、读写延迟、命令总数、缓存命中率" loading="lazy" decoding="async"></p>

测试后的 Monitoring：存储数据在 5 分钟数据点中峰值为 649 MB；服务器端读取延迟最高 2.4 ms，写入延迟最高 1.4 ms。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/12-valkey-delete-dialog.webp' | relative_url }}" width="1440" height="765" alt="最终备份设为 No 并已输入名称的删除对话框" loading="lazy" decoding="async"></p>

删除时需要输入缓存名称，且默认创建最终备份；此处选择了 No。约 3 分钟后缓存从列表中消失。 <small>2026-11-07 截图，AWS ap-northeast-2。</small>

#### 费用

缓存存续约 31 分钟。按价格表计算：约 0.2 GB 小时的存储（最低 100 MB，加上内存测试）和约 500 万 ECPU，合计约 $0.05。撰写本文时 AWS 账单尚未显示该费用；显示后，实际计费金额会记入 `STATUS.md`。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**状態: 一部実行済み。** 下の ElastiCache の節は 2026-11-07 に実行した。このページの残りはまだ [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) の計画である。
</div>

Redis Open Source 8.x、Redis Cloud / Software、Valkey 9.x、ElastiCache for Valkey と for Redis OSS（≤ 7.1）、Azure Managed Redis（中身は Redis Enterprise）、Memorystore for Valkey — セルごとに出典のあるマトリクス（ライセンス、モジュール、Active-Active、階層化、SLA、価格モデル）、ライセンスの年表（BSD-3 → 7.4 で RSALv2/SSPL → 8.0 で AGPLv3 追加、Valkey は 7.2.4 を BSD-3 でフォーク）、そして Redis 8.10 と Valkey 9.1 で同じワークロードを並べて実行。Dragonfly、KeyDB、Garnet は一段落ずつ。

### ElastiCache Serverless for Valkey と Redis Cloud 無料データベースの比較

**2026-11-07 に AWS ap-northeast-2（ソウル）で実施。** コンソールで Serverless キャッシュを 1 つ、Valkey 9.0 で作成して削除した。存続時間は約 31 分。[Redis Cloud 無料データベースのラボ]({{ '/cloud/' | relative_url }}) と同じプローブスクリプト、同じ韓国内のクライアントホストを使った。価格は 2026-10-28 公開の AWS ソウル価格表によるもので、2026-11-07 に確認した。マスク済み：アカウント ID とエイリアス、ARN、エンドポイント。

#### 異なった点

| | Redis Cloud free database | ElastiCache Serverless for Valkey |
|---|---|---|
| 費用 | 30 MB まで $0 | データ 1 GB 時間あたり $0.101（最低 100 MB、アイドル時は月約 $7.4）に加え、100 万 ECPU あたり $0.0027 |
| 作成から利用可能まで | 数秒 | 58 秒 |
| エンジン | Redis 8.6.2 | Valkey 9.0（9、8、7 を提供）。`INFO` は `redis_version:7.2` と報告 |
| ネットワーク | パブリックエンドポイント。CIDR 許可リスト、既定は 0.0.0.0/0 | 既定は VPC。IAM 認証を必須とする Public 接続タイプ |
| 認証 | default ユーザーとパスワード | IAM：有効期間 15 分の SigV4 トークン、ユーザー `default.iam-user` |
| TLS | 既定でオフ | 常にオン |
| 複数キーコマンド | 任意のキーへの `MGET` が成功 | スロットをまたぐ `MGET` は拒否：`Keys in request don't hash to the same slot` |
| 接続数 | 31 本目の接続が拒否された | エラーなしで 40 本を開けた |
| メモリ | 約 28 MB で書き込みが拒否された | ストレージ上限を 1 GB に設定し、10 kB の値を約 1.77 GB 書き込んだ後に拒否された |
| バックアップ | 無料プランにはなし | 自動バックアップは既定でオフ。削除ダイアログは既定で最終バックアップを作成 |
| メトリクス | コンソールに 16 チャート、5 分から 3 か月 | CloudWatch。キャッシュページには 50 メトリクスのうち 16 を表示 |
| プログラムからのアクセス | アカウントキーとユーザーキーを使う REST API、Terraform と Pulumi | AWS API、CLI、CloudFormation。ElastiCache 用の MCP サーバー |

#### クライアント側の測定

| Probe | Redis Cloud free, plain TCP | ElastiCache Serverless, TLS + IAM |
|---|---|---|
| ラウンドトリップ、`PING` 50 回の平均 | 2.6 ms | 5.1 ms |
| 1 接続、パイプラインなし | 249 ops/s | 287 ops/s |
| 8 接続、パイプラインなし | 2,363 ops/s | 2,419 ops/s |
| 1 接続、pipeline 100 | 24,671 ops/s | 4,960 ops/s |
| 8 接続、pipeline 100 | 103,920 ops/s | 15 秒間で 24,893 ops/s。秒ごとの実行では 45,600–54,300 INCR/s |
| 60 秒持続、8 × pipeline 100 | 100,840–108,780 INCR/s、安定 | 5 秒ごとに 0–45,785 INCR/s。5 秒ウィンドウ 3 つがゼロ、エラーなし |

スループットの各行はどちらのサービスの優劣を示すものではない。片方は平文 TCP、もう片方は TLS であり、クライアントは韓国内の単一の Python プロセスで、Serverless キャッシュは 200,000 ECPUs/s に制限されていた（ゼロのウィンドウは約 40,000 INCR/s のときに発生し、この上限を下回っていた。原因は説明できていない）。パイプラインなしの数値は、どちら側もラウンドトリップで律速される。

#### コンソールを画面ごとに見る

<p class="shot"><img src="{{ '/assets/img/elasticache-console/01-elasticache-dashboard.webp' | relative_url }}" width="1440" height="765" alt="リソースがないソウルリージョンの ElastiCache ダッシュボード" loading="lazy" decoding="async"></p>

ElastiCache ダッシュボード：Valkey、Memcached、Redis OSS のキャッシュ、グローバルデータストア、リザーブドノード、バックアップ、サブネットグループとパラメータグループ、ユーザー管理、移行。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/02-valkey-caches-empty.webp' | relative_url }}" width="1440" height="765" alt="空の Valkey caches 一覧" loading="lazy" decoding="async"></p>

Valkey caches は Create cache ボタンのある一覧である。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/03-create-valkey-serverless-default.webp' | relative_url }}" width="1440" height="1520" alt="エンジン、デプロイオプション、作成方法、名前、エンジンバージョン、接続タイプを含む Create Valkey cache フォーム" loading="lazy" decoding="async"></p>

1 つのフォーム：エンジン（Valkey 推奨、ほかに Memcached、Redis OSS）、デプロイ（Serverless またはノードベースのクラスター）、新規作成または .rdb からの復元、エンジンバージョン 9、接続タイプ VPC。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/04-create-valkey-serverless-customize.webp' | relative_url }}" width="1440" height="2404" alt="カスタマイズ設定：ネットワークタイプ、暗号化、ユーザーグループ default.iam-user-group、バックアップ、使用量の上限" loading="lazy" decoding="async"></p>

Public を選ぶと、ユーザーグループには IAM 認証ユーザーのみを含める必要があるという案内が表示され、default.iam-user-group が入力される。転送中の暗号化は有効で、ここではオフにできない。自動バックアップはチェックなし。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/05-create-valkey-serverless-filled.webp' | relative_url }}" width="1440" height="2604" alt="入力済みのフォーム：名前 notes-on-redis-valkey、Public、最大ストレージ 1 GB、毎秒最大 200,000 ECPU" loading="lazy" decoding="async"></p>

使用量の上限を支出の上限として使った。データストレージは最大 1 GB（フォームは 1〜5,000 GB を許可）、ECPU は毎秒最大 200,000（1,000〜15,000,000）。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/06-valkey-cache-details.webp' | relative_url }}" width="1440" height="1236" alt="キャッシュの詳細：Available、Valkey 9.0、Public、上限を表示" loading="lazy" decoding="async"></p>

作成後の詳細：ステータス Available、エンジンバージョン 9.0、接続タイプ Public、2 つの上限、ポート 6379 のエンドポイント。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/07-valkey-connect-cloudshell.webp' | relative_url }}" width="1440" height="2267" alt="CloudShell と CLI の案内がある Connect to your cache セクション" loading="lazy" decoding="async"></p>

接続の案内：Developer Toolkit で SigV4 トークンを生成し、続けて valkey-cli -c --tls --user を実行する。トークンの有効期間は 15 分。ほかのタブ：MCP integration、Valkey GLIDE（推奨）、クライアントライブラリ。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/08-valkey-iam-user-group.webp' | relative_url }}" width="1440" height="800" alt="ユーザー default.iam-user を 1 つ含む default.iam-user-group" loading="lazy" decoding="async"></p>

既定の IAM ユーザーグループにはユーザー default.iam-user が 1 つあり、アクセス文字列は on ~* +@all で、Public と VPC の両方で使用できる。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/09-valkey-users.webp' | relative_url }}" width="1440" height="765" alt="ユーザー一覧：default（VPC のみ）と default.iam-user（Public と VPC）" loading="lazy" decoding="async"></p>

ユーザーは 2 つある。パスワードなしの default ユーザー（VPC のみ）と IAM ユーザー。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/10-valkey-events.webp' | relative_url }}" width="1440" height="998" alt="イベントが 1 つだけの Events タブ：キャッシュの作成が完了し利用可能" loading="lazy" decoding="async"></p>

14:36:59（KST）に作成を開始し、14:37:57 に準備が完了した。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/11-valkey-monitoring.webp' | relative_url }}" width="1440" height="1800" alt="Monitoring タブ：保存データ、消費 ECPU、読み取りと書き込みのレイテンシ、総コマンド数、キャッシュヒット率" loading="lazy" decoding="async"></p>

テスト後の Monitoring：保存データは 5 分間のデータポイントで最大 649 MB。サーバー側の読み取りレイテンシは最大 2.4 ms、書き込みレイテンシは最大 1.4 ms。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/12-valkey-delete-dialog.webp' | relative_url }}" width="1440" height="765" alt="最終バックアップを No にし、名前を入力した削除ダイアログ" loading="lazy" decoding="async"></p>

削除ではキャッシュ名の入力が求められ、既定で最終バックアップが作成される。ここでは No を選んだ。約 3 分後にキャッシュが一覧から消えた。 <small>2026-11-07 キャプチャ、AWS ap-northeast-2。</small>

#### 費用

キャッシュは約 31 分存続した。価格表で計算すると、ストレージは約 0.2 GB 時間（最低 100 MB とメモリテスト分）、ECPU は約 500 万で、合計およそ $0.05 になる。本稿の執筆時点では AWS の請求にまだ表示されていなかった。表示された時点で、請求額を `STATUS.md` に記録する。

</div>
