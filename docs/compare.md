---
layout: default
title: Compare
permalink: /compare/
---

# Compare

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: partly run.** The local Redis and Valkey comparison, the feature matrix and the ElastiCache section below were run or sourced on 2026-11-07; the licence timeline and the alternatives are still the plan in [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Open Source 8.x, Redis Cloud / Software, Valkey 9.x, ElastiCache for Valkey and for Redis OSS (≤ 7.1), Azure Managed Redis (Redis Enterprise inside), Memorystore for Valkey — a matrix with a source per cell (licence, modules, Active-Active, tiering, SLA, pricing model), the licence timeline (BSD-3 → RSALv2/SSPL at 7.4 → AGPLv3 added at 8.0; Valkey forked 7.2.4 under BSD-3), and the same workload run on Redis 8.10 and Valkey 9.1 side by side. Dragonfly, KeyDB and Garnet in a paragraph each.

### Redis 8.10 and Valkey 9.1, locally

**Verified on Redis 8.10.3, Valkey 9.1.3 and the Valkey bundle 9.1, 2026-11-07,** in Docker on one 24-core host with defaults and no persistence. Source and full output: [`compare/01-valkey-vs-redis-local`](https://github.com/litkhai/notes-on-redis/tree/main/compare/01-valkey-vs-redis-local).

| | Redis 8.10.3 | Valkey 9.1.3 | Valkey bundle 9.1 |
|---|---|---|---|
| `INFO` version fields | `redis_version:8.10.3` | `redis_version:7.2.4`, `valkey_version:9.1.3` | same as Valkey |
| Modules loaded | Search, JSON, Bloom, Time series, vector sets | `lua` only | `json`, `bf`, `search`, `ldap`, `lua` |
| Commands in `COMMAND LIST` | 669 | 399 | 450 |
| JSON, Bloom, Search | yes | no | yes (subsets) |
| Time series, top-k, vector sets, Array | yes | no | no |
| Hash field expiration | yes | yes | yes |
| 1 M small strings | 62.1 B/key | 57.5 B/key | 57.5 B/key |
| SET/GET, defaults, req/s | 119,197–124,797 | 120,992–122,978 | 124,766–126,783 |
| SET/GET, `io-threads 4`, req/s | 342,427–352,568 | 315,391–342,349 | not run |

Only in Valkey: `CLUSTERSCAN`, atomic slot migration (`CLUSTER MIGRATESLOTS`), `COMMANDLOG`, `DELIFEQ`. Only in Redis besides the module families: `BACKUP`, `HOTKEYS`, `HIMPORT`, `DIGEST`, stream additions such as `XACKDEL`. On the bundle, `FT.SEARCH` right after `FT.CREATE` found nothing and found the documents a second later: existing keys are indexed in the background. The throughput rows are measurements on one machine; through Docker's published ports all three stopped at about 83,000 req/s, which is the port-forwarding path.

**Availability, side by side** (`compare/01-valkey-vs-redis-local/ha.py`). The same script ran both engines: a 3 s cluster node timeout promoted a replica after 4.2 s on each, Sentinel named a new master after 4.3 s (Redis) and 4.4 s (Valkey), and AOF with `appendfsync everysec` reloaded about 632,000 keys in 1.3 s on both. Only the binary names differed; the cluster and Sentinel commands are the same.

### Feature matrix

One table across Redis Open Source 8, Redis Cloud, Valkey 9, ElastiCache for Valkey and for Redis OSS, Azure Managed Redis and Memorystore for Valkey, every cell with a source: measured here on 2026-11-07, or vendor documentation read that day, or marked "not confirmed". It lives in the repository so it can grow cell by cell: [`compare/matrix.md`](https://github.com/litkhai/notes-on-redis/blob/main/compare/matrix.md).

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
**상태: 일부 실행.** 아래 로컬 Redis·Valkey 비교, 기능 매트릭스, ElastiCache 절은 2026-11-07에 실행하거나 출처를 달았다. 라이선스 연표와 대안은 아직 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)의 계획이다.
</div>

Redis Open Source 8.x, Redis Cloud / Software, Valkey 9.x, ElastiCache for Valkey와 for Redis OSS(≤ 7.1), Azure Managed Redis(안은 Redis Enterprise), Memorystore for Valkey — 셀마다 출처가 있는 매트릭스(라이선스, 모듈, Active-Active, 티어링, SLA, 가격 모델), 라이선스 연표(BSD-3 → 7.4에서 RSALv2/SSPL → 8.0에서 AGPLv3 추가; Valkey는 7.2.4를 BSD-3로 포크), 그리고 Redis 8.10과 Valkey 9.1에 같은 워크로드를 나란히. Dragonfly, KeyDB, Garnet은 한 문단씩.

### Redis 8.10과 Valkey 9.1, 로컬에서

**확인: Redis 8.10.3, Valkey 9.1.3, Valkey 번들 9.1, 2026-11-07.** 24코어 호스트 하나의 Docker, 기본 설정, 영속성 없음. 소스와 전체 출력: [`compare/01-valkey-vs-redis-local`](https://github.com/litkhai/notes-on-redis/tree/main/compare/01-valkey-vs-redis-local).

| | Redis 8.10.3 | Valkey 9.1.3 | Valkey 번들 9.1 |
|---|---|---|---|
| `INFO` 버전 항목 | `redis_version:8.10.3` | `redis_version:7.2.4`, `valkey_version:9.1.3` | Valkey와 같음 |
| 실린 모듈 | Search, JSON, Bloom, Time series, 벡터 셋 | `lua`만 | `json`, `bf`, `search`, `ldap`, `lua` |
| `COMMAND LIST`의 명령 수 | 669 | 399 | 450 |
| JSON, Bloom, Search | 있음 | 없음 | 있음(일부) |
| Time series, top-k, 벡터 셋, Array | 있음 | 없음 | 없음 |
| 해시 필드 만료 | 있음 | 있음 | 있음 |
| 작은 문자열 100만 개 | 키당 62.1 B | 키당 57.5 B | 키당 57.5 B |
| SET/GET, 기본 설정, 초당 요청 | 119,197–124,797 | 120,992–122,978 | 124,766–126,783 |
| SET/GET, `io-threads 4`, 초당 요청 | 342,427–352,568 | 315,391–342,349 | 미실행 |

Valkey에만 있는 것: `CLUSTERSCAN`, 원자적 슬롯 이전(`CLUSTER MIGRATESLOTS`), `COMMANDLOG`, `DELIFEQ`. 모듈 계열 외에 Redis에만 있는 것: `BACKUP`, `HOTKEYS`, `HIMPORT`, `DIGEST`, `XACKDEL` 같은 스트림 추가 명령. 번들에서는 `FT.CREATE` 직후의 `FT.SEARCH`가 아무것도 찾지 못하고 1초 뒤에 찾았다. 기존 키는 백그라운드로 색인된다. 처리량 행은 기계 한 대에서 잰 값이다. Docker의 공개 포트를 거치면 셋 모두 초당 약 83,000에서 멈췄는데, 이는 포트 포워딩 경로의 한계다.

**가용성 나란히 보기**(`compare/01-valkey-vs-redis-local/ha.py`). 같은 스크립트로 두 엔진을 돌렸다. 클러스터 노드 타임아웃 3초에서 둘 다 4.2초에 복제본이 승격됐고, Sentinel은 4.3초(Redis)와 4.4초(Valkey)에 새 마스터를 지목했으며, `appendfsync everysec`의 AOF는 둘 다 키 약 632,000개를 1.3초에 다시 읽었다. 다른 것은 바이너리 이름뿐이고 클러스터와 Sentinel 명령은 같다.

### 기능 매트릭스

Redis Open Source 8, Redis Cloud, Valkey 9, ElastiCache for Valkey와 for Redis OSS, Azure Managed Redis, Memorystore for Valkey를 한 표에 담았다. 칸마다 출처가 있다. 2026-11-07에 여기서 잰 값, 그날 읽은 공급사 문서, 또는 "확인 안 됨" 표시. 칸 단위로 늘려 가도록 저장소에 둔다: [`compare/matrix.md`](https://github.com/litkhai/notes-on-redis/blob/main/compare/matrix.md).

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
**状态：部分已运行。** 下面的本地 Redis 与 Valkey 对比、功能矩阵和 ElastiCache 一节已于 2026-11-07 运行或查证；许可证时间线和替代方案仍是 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) 中的计划。
</div>

Redis Open Source 8.x、Redis Cloud / Software、Valkey 9.x、ElastiCache for Valkey 与 for Redis OSS（≤ 7.1）、Azure Managed Redis（内核为 Redis Enterprise）、Memorystore for Valkey — 每格有来源的矩阵（许可证、模块、Active-Active、分层、SLA、定价模型）、许可证时间线（BSD-3 → 7.4 起 RSALv2/SSPL → 8.0 加入 AGPLv3；Valkey 自 7.2.4 以 BSD-3 分叉），以及在 Redis 8.10 与 Valkey 9.1 上并排运行同一负载。Dragonfly、KeyDB、Garnet 各一段。

### 在本地运行 Redis 8.10 与 Valkey 9.1

**已于 2026-11-07 在 Redis 8.10.3、Valkey 9.1.3 和 Valkey bundle 9.1 上验证，** 在一台 24 核主机上用 Docker 运行，使用默认配置，不启用持久化。源码与完整输出：[`compare/01-valkey-vs-redis-local`](https://github.com/litkhai/notes-on-redis/tree/main/compare/01-valkey-vs-redis-local)。

| | Redis 8.10.3 | Valkey 9.1.3 | Valkey bundle 9.1 |
|---|---|---|---|
| `INFO` 版本字段 | `redis_version:8.10.3` | `redis_version:7.2.4`, `valkey_version:9.1.3` | 与 Valkey 相同 |
| 已加载的模块 | Search, JSON, Bloom, Time series, vector sets | `lua` only | `json`, `bf`, `search`, `ldap`, `lua` |
| `COMMAND LIST` 中的命令数 | 669 | 399 | 450 |
| JSON, Bloom, Search | 是 | 否 | 是 (子集) |
| Time series, top-k, vector sets, Array | 是 | 否 | 否 |
| 哈希字段过期 | 是 | 是 | 是 |
| 100 万个小字符串 | 62.1 B/key | 57.5 B/key | 57.5 B/key |
| SET/GET, 默认配置, req/s | 119,197–124,797 | 120,992–122,978 | 124,766–126,783 |
| SET/GET, `io-threads 4`, req/s | 342,427–352,568 | 315,391–342,349 | 未运行 |

仅 Valkey 有：`CLUSTERSCAN`、原子槽位迁移（`CLUSTER MIGRATESLOTS`）、`COMMANDLOG`、`DELIFEQ`。除模块系列外仅 Redis 有：`BACKUP`、`HOTKEYS`、`HIMPORT`、`DIGEST`，以及 `XACKDEL` 之类的 stream 新增命令。在 bundle 上，紧接 `FT.CREATE` 之后执行 `FT.SEARCH` 什么也没找到，一秒后才找到文档：已有的键是在后台建立索引的。吞吐量各行是在一台机器上的测量值；通过 Docker 发布的端口，三者都停在约 83,000 req/s，这是端口转发路径的上限。

**可用性并排对比**（`compare/01-valkey-vs-redis-local/ha.py`）。同一个脚本运行了两个引擎：集群节点超时设为 3 秒时，两者都在 4.2 秒后提升了副本；Sentinel 分别在 4.3 秒（Redis）和 4.4 秒（Valkey）后指定了新的 master；使用 `appendfsync everysec` 的 AOF 在两者上都用 1.3 秒重新加载了约 632,000 个键。只有二进制文件的名称不同，集群和 Sentinel 的命令是一样的。

### 功能矩阵

一张表涵盖 Redis Open Source 8、Redis Cloud、Valkey 9、ElastiCache for Valkey 与 for Redis OSS、Azure Managed Redis 和 Memorystore for Valkey，每个单元格都有来源：2026-11-07 在此实测，或当天读取的厂商文档，或标为“未确认”。它放在仓库中，因此可以逐格扩充：[`compare/matrix.md`](https://github.com/litkhai/notes-on-redis/blob/main/compare/matrix.md)。

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
**状態: 一部実行済み。** 下のローカルでの Redis と Valkey の比較、機能マトリクス、ElastiCache の節は 2026-11-07 に実行または出典確認を行った。ライセンスの年表と代替製品は、まだ [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) の計画である。
</div>

Redis Open Source 8.x、Redis Cloud / Software、Valkey 9.x、ElastiCache for Valkey と for Redis OSS（≤ 7.1）、Azure Managed Redis（中身は Redis Enterprise）、Memorystore for Valkey — セルごとに出典のあるマトリクス（ライセンス、モジュール、Active-Active、階層化、SLA、価格モデル）、ライセンスの年表（BSD-3 → 7.4 で RSALv2/SSPL → 8.0 で AGPLv3 追加、Valkey は 7.2.4 を BSD-3 でフォーク）、そして Redis 8.10 と Valkey 9.1 で同じワークロードを並べて実行。Dragonfly、KeyDB、Garnet は一段落ずつ。

### Redis 8.10 と Valkey 9.1 をローカルで

**2026-11-07 に Redis 8.10.3、Valkey 9.1.3、Valkey bundle 9.1 で検証済み。** 24 コアのホスト 1 台で Docker を使い、デフォルト設定、永続化なしで実行した。ソースと全出力: [`compare/01-valkey-vs-redis-local`](https://github.com/litkhai/notes-on-redis/tree/main/compare/01-valkey-vs-redis-local)。

| | Redis 8.10.3 | Valkey 9.1.3 | Valkey bundle 9.1 |
|---|---|---|---|
| `INFO` のバージョンフィールド | `redis_version:8.10.3` | `redis_version:7.2.4`, `valkey_version:9.1.3` | Valkey と同じ |
| 読み込まれたモジュール | Search, JSON, Bloom, Time series, vector sets | `lua` のみ | `json`, `bf`, `search`, `ldap`, `lua` |
| `COMMAND LIST` のコマンド数 | 669 | 399 | 450 |
| JSON, Bloom, Search | はい | いいえ | はい (一部) |
| Time series, top-k, vector sets, Array | はい | いいえ | いいえ |
| ハッシュフィールドの有効期限 | はい | はい | はい |
| 小さい文字列 1 M 個 | 62.1 B/key | 57.5 B/key | 57.5 B/key |
| SET/GET, デフォルト, req/s | 119,197–124,797 | 120,992–122,978 | 124,766–126,783 |
| SET/GET, `io-threads 4`, req/s | 342,427–352,568 | 315,391–342,349 | 未実行 |

Valkey のみにあるもの: `CLUSTERSCAN`、アトミックなスロット移行（`CLUSTER MIGRATESLOTS`）、`COMMANDLOG`、`DELIFEQ`。モジュール群のほかに Redis のみにあるもの: `BACKUP`、`HOTKEYS`、`HIMPORT`、`DIGEST`、`XACKDEL` などのストリーム追加分。bundle では、`FT.CREATE` の直後の `FT.SEARCH` は何も見つけず、1 秒後にはドキュメントを見つけた。既存のキーはバックグラウンドでインデックスされる。スループットの行は 1 台のマシンでの測定値である。Docker の公開ポート経由では、3 つとも約 83,000 req/s で頭打ちになった。これはポート転送経路の上限である。

**可用性の比較**（`compare/01-valkey-vs-redis-local/ha.py`）。同じスクリプトで両方のエンジンを動かした。クラスターのノードタイムアウト 3 秒では、どちらも 4.2 秒でレプリカが昇格し、Sentinel は 4.3 秒（Redis）と 4.4 秒（Valkey）で新しいマスターを指名し、`appendfsync everysec` の AOF は、どちらも約 632,000 個のキーを 1.3 秒で再読み込みした。違ったのはバイナリ名だけで、クラスターと Sentinel のコマンドは同じである。

### 機能マトリクス

Redis Open Source 8、Redis Cloud、Valkey 9、ElastiCache for Valkey と for Redis OSS、Azure Managed Redis、Memorystore for Valkey を 1 つの表にまとめ、すべてのセルに出典を付けた。ここで 2026-11-07 に測定したもの、その日に読んだベンダーのドキュメント、または「未確認」と記したもののいずれかである。リポジトリに置いてあるので、セルごとに増やしていける: [`compare/matrix.md`](https://github.com/litkhai/notes-on-redis/blob/main/compare/matrix.md)。

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

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: รันแล้วบางส่วน** การเปรียบเทียบ Redis กับ Valkey บนเครื่อง ตารางคุณสมบัติ และส่วน ElastiCache ด้านล่างได้รันหรืออ้างอิงแหล่งที่มาเมื่อ 2026-11-07 ส่วนลำดับเหตุการณ์ด้านไลเซนส์และทางเลือกอื่นยังเป็นแผนใน [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)
</div>

Redis Open Source 8.x, Redis Cloud / Software, Valkey 9.x, ElastiCache for Valkey และ for Redis OSS (≤ 7.1), Azure Managed Redis (Redis Enterprise อยู่ภายใน), Memorystore for Valkey — ตารางเปรียบเทียบที่มีแหล่งอ้างอิงในทุกช่อง (ใบอนุญาต, โมดูล, Active-Active, tiering, SLA, รูปแบบราคา), ไทม์ไลน์ใบอนุญาต (BSD-3 → RSALv2/SSPL ที่ 7.4 → เพิ่ม AGPLv3 ที่ 8.0; Valkey แยกจาก 7.2.4 ภายใต้ BSD-3) และเวิร์กโหลดเดียวกันที่รันบน Redis 8.10 และ Valkey 9.1 เทียบกัน ส่วน Dragonfly, KeyDB และ Garnet อธิบายอย่างละหนึ่งย่อหน้า

### Redis 8.10 และ Valkey 9.1 บนเครื่อง

**ตรวจสอบแล้วบน Redis 8.10.3, Valkey 9.1.3 และ Valkey bundle 9.1 เมื่อ 2026-11-07** ใน Docker บนโฮสต์ 24 คอร์หนึ่งเครื่อง ใช้ค่าเริ่มต้นและไม่เปิดการเก็บข้อมูลถาวร ซอร์สและผลลัพธ์ทั้งหมด: [`compare/01-valkey-vs-redis-local`](https://github.com/litkhai/notes-on-redis/tree/main/compare/01-valkey-vs-redis-local)

| | Redis 8.10.3 | Valkey 9.1.3 | Valkey bundle 9.1 |
|---|---|---|---|
| ฟิลด์เวอร์ชันของ `INFO` | `redis_version:8.10.3` | `redis_version:7.2.4`, `valkey_version:9.1.3` | เหมือน Valkey |
| โมดูลที่โหลด | Search, JSON, Bloom, Time series, vector sets | `lua` เท่านั้น | `json`, `bf`, `search`, `ldap`, `lua` |
| คำสั่งใน `COMMAND LIST` | 669 | 399 | 450 |
| JSON, Bloom, Search | ใช่ | ไม่ | ใช่ (บางส่วน) |
| Time series, top-k, vector sets, Array | ใช่ | ไม่ | ไม่ |
| การหมดอายุของฟิลด์ใน hash | ใช่ | ใช่ | ใช่ |
| สตริงขนาดเล็ก 1 M รายการ | 62.1 B/key | 57.5 B/key | 57.5 B/key |
| SET/GET, ค่าเริ่มต้น, req/s | 119,197–124,797 | 120,992–122,978 | 124,766–126,783 |
| SET/GET, `io-threads 4`, req/s | 342,427–352,568 | 315,391–342,349 | ไม่ได้รัน |

มีเฉพาะใน Valkey: `CLUSTERSCAN`, การย้าย slot แบบ atomic (`CLUSTER MIGRATESLOTS`), `COMMANDLOG`, `DELIFEQ` มีเฉพาะใน Redis นอกจากกลุ่มโมดูล: `BACKUP`, `HOTKEYS`, `HIMPORT`, `DIGEST` และคำสั่งที่เพิ่มใน stream เช่น `XACKDEL` บน bundle การรัน `FT.SEARCH` ทันทีหลัง `FT.CREATE` ไม่พบอะไรเลย และพบเอกสารหลังจากผ่านไปหนึ่งวินาที เพราะคีย์ที่มีอยู่แล้วถูกทำดัชนีในเบื้องหลัง แถวของปริมาณงานเป็นผลการวัดบนเครื่องเดียว เมื่อผ่านพอร์ตที่ Docker เปิดให้ ทั้งสามตัวหยุดอยู่ที่ประมาณ 83,000 req/s ซึ่งเป็นเพดานของเส้นทางการส่งต่อพอร์ต

**ความพร้อมใช้งาน เทียบกันแบบเคียงข้างกัน** (`compare/01-valkey-vs-redis-local/ha.py`) รันสคริปต์เดียวกันกับทั้งสองเอนจิน: เมื่อตั้ง node timeout ของคลัสเตอร์ที่ 3 วินาที ทั้งคู่เลื่อนระดับเรพลิกาหลังผ่านไป 4.2 วินาที, Sentinel ระบุ master ใหม่หลังผ่านไป 4.3 วินาที (Redis) และ 4.4 วินาที (Valkey) และ AOF ที่ใช้ `appendfsync everysec` โหลดคีย์ราว 632,000 คีย์กลับเข้ามาใน 1.3 วินาทีเท่ากันทั้งคู่ ที่ต่างกันมีแค่ชื่อไบนารี คำสั่งของคลัสเตอร์และ Sentinel เหมือนกัน

### ตารางคุณสมบัติ

ตารางเดียวครอบคลุม Redis Open Source 8, Redis Cloud, Valkey 9, ElastiCache for Valkey และ for Redis OSS, Azure Managed Redis และ Memorystore for Valkey ทุกเซลล์มีแหล่งที่มา คือวัดจริงที่นี่เมื่อ 2026-11-07 หรือเอกสารของผู้ให้บริการที่อ่านในวันนั้น หรือทำเครื่องหมายว่า "ยังไม่ยืนยัน" ตารางอยู่ในรีโพซิทอรี จึงเพิ่มทีละเซลล์ได้: [`compare/matrix.md`](https://github.com/litkhai/notes-on-redis/blob/main/compare/matrix.md)

### ElastiCache Serverless for Valkey เทียบกับฐานข้อมูลฟรีของ Redis Cloud

**รันเมื่อ 2026-11-07 ใน AWS ap-northeast-2 (โซล)** แคชแบบ serverless หนึ่งตัว Valkey 9.0 สร้างและลบผ่านคอนโซล มีอายุประมาณ 31 นาที ใช้สคริปต์ probe เดียวกันและเครื่องไคลเอนต์เครื่องเดิมในเกาหลีเหมือนกับ[แล็บฐานข้อมูลฟรีของ Redis Cloud]({{ '/cloud/' | relative_url }}) ราคามาจากรายการราคา AWS สำหรับโซลที่เผยแพร่เมื่อ 2026-10-28 และอ่านเมื่อ 2026-11-07 ข้อมูลที่ปกปิด: account ID และ alias, ARN, endpoint

#### สิ่งที่แตกต่าง

| | ฐานข้อมูลฟรีของ Redis Cloud | ElastiCache Serverless for Valkey |
|---|---|---|
| ค่าใช้จ่าย | $0 สำหรับ 30 MB | $0.101 ต่อ GB-hour ของข้อมูล (ขั้นต่ำ 100 MB, ประมาณ $7.4 ต่อเดือนเมื่อไม่ได้ใช้งาน) บวก $0.0027 ต่อหนึ่งล้าน ECPU |
| จากสร้างถึงใช้งานได้ | ไม่กี่วินาที | 58 วินาที |
| เอนจิน | Redis 8.6.2 | Valkey 9.0 (มีให้เลือก 9, 8 และ 7); `INFO` รายงาน `redis_version:7.2` |
| เครือข่าย | public endpoint; allow list แบบ CIDR, ค่าเริ่มต้น 0.0.0.0/0 | ค่าเริ่มต้นเป็น VPC; มีชนิดการเชื่อมต่อ Public ที่ต้องใช้การยืนยันตัวตนแบบ IAM |
| การยืนยันตัวตน | ผู้ใช้ default และรหัสผ่าน | IAM: โทเค็น SigV4 ที่ใช้ได้ 15 นาที, ผู้ใช้ `default.iam-user` |
| TLS | ปิดเป็นค่าเริ่มต้น | เปิดตลอด |
| คำสั่งหลายคีย์ | `MGET` กับคีย์ใดก็ได้ใช้งานได้ | `MGET` ข้าม slot ถูกปฏิเสธ: `Keys in request don't hash to the same slot` |
| การเชื่อมต่อ | การเชื่อมต่อที่ 31 ถูกปฏิเสธ | เปิดได้ 40 รายการโดยไม่มีข้อผิดพลาด |
| หน่วยความจำ | การเขียนถูกปฏิเสธที่ประมาณ 28 MB | การเขียนถูกปฏิเสธหลังจากประมาณ 1.77 GB ของค่าขนาด 10 kB โดยตั้งขีดจำกัดพื้นที่จัดเก็บไว้ที่ 1 GB |
| การสำรองข้อมูล | ไม่มีในแผนฟรี | การสำรองอัตโนมัติปิดเป็นค่าเริ่มต้น; กล่องโต้ตอบการลบมีค่าเริ่มต้นเป็นการสำรองครั้งสุดท้าย |
| เมตริก | 16 กราฟในคอนโซล, 5 นาทีถึง 3 เดือน | CloudWatch; 16 จาก 50 เมตริกในหน้าแคช |
| การเข้าถึงด้วยโปรแกรม | REST API พร้อมคีย์ระดับบัญชีและผู้ใช้, Terraform และ Pulumi | AWS API, CLI, CloudFormation; MCP server สำหรับ ElastiCache |

#### ผลการวัดฝั่งไคลเอนต์

| Probe | Redis Cloud ฟรี, TCP ธรรมดา | ElastiCache Serverless, TLS + IAM |
|---|---|---|
| ไป-กลับ, ค่าเฉลี่ยของ `PING` 50 ครั้ง | 2.6 ms | 5.1 ms |
| 1 การเชื่อมต่อ, ไม่มี pipeline | 249 ops/s | 287 ops/s |
| 8 การเชื่อมต่อ, ไม่มี pipeline | 2,363 ops/s | 2,419 ops/s |
| 1 การเชื่อมต่อ, pipeline 100 | 24,671 ops/s | 4,960 ops/s |
| 8 การเชื่อมต่อ, pipeline 100 | 103,920 ops/s | 24,893 ops/s ในช่วง 15 วินาที; 45,600–54,300 INCR/s ในการรันแบบรายวินาที |
| ต่อเนื่อง 60 วินาที, 8 × pipeline 100 | 100,840–108,780 INCR/s, คงที่ | 0–45,785 INCR/s ต่อ 5 วินาที; สามช่วง 5 วินาทีเป็นศูนย์, ไม่มีข้อผิดพลาด |

แถวของ throughput ไม่ใช่คำตัดสินของบริการใดบริการหนึ่ง: ฝั่งหนึ่งเป็น TCP ธรรมดาและอีกฝั่งเป็น TLS, ไคลเอนต์เป็นโปรเซส Python เดียวในเกาหลี และแคช serverless ถูกจำกัดไว้ที่ 200,000 ECPU/s (ช่วงที่เป็นศูนย์เกิดขึ้นที่ประมาณ 40,000 INCR/s ซึ่งต่ำกว่าขีดจำกัดนั้น และยังไม่มีคำอธิบาย) ตัวเลขที่ไม่ใช้ pipeline ถูกจำกัดด้วยเวลาไป-กลับทั้งสองฝั่ง

#### คอนโซลทีละหน้าจอ

<p class="shot"><img src="{{ '/assets/img/elasticache-console/01-elasticache-dashboard.webp' | relative_url }}" width="1440" height="765" alt="แดชบอร์ด ElastiCache ในโซลที่ไม่มีทรัพยากร" loading="lazy" decoding="async"></p>

แดชบอร์ด ElastiCache: แคช Valkey, Memcached และ Redis OSS, global datastore, reserved node, การสำรองข้อมูล, subnet group และ parameter group, การจัดการผู้ใช้, การย้ายข้อมูล <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/02-valkey-caches-empty.webp' | relative_url }}" width="1440" height="765" alt="รายการแคช Valkey ที่ว่างเปล่า" loading="lazy" decoding="async"></p>

Valkey caches เป็นรายการที่มีปุ่ม Create cache <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/03-create-valkey-serverless-default.webp' | relative_url }}" width="1440" height="1520" alt="ฟอร์มสร้างแคช Valkey พร้อมเอนจิน ตัวเลือกการปรับใช้ วิธีการสร้าง ชื่อ เวอร์ชันเอนจิน และชนิดการเชื่อมต่อ" loading="lazy" decoding="async"></p>

ฟอร์มเดียว: เอนจิน (แนะนำ Valkey, Memcached, Redis OSS), การปรับใช้ (Serverless หรือคลัสเตอร์แบบใช้โหนด), สร้างใหม่หรือกู้คืนจากไฟล์ .rdb, เวอร์ชันเอนจิน 9, ชนิดการเชื่อมต่อ VPC <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/04-create-valkey-serverless-customize.webp' | relative_url }}" width="1440" height="2404" alt="การตั้งค่าแบบกำหนดเอง: ชนิดเครือข่าย การเข้ารหัส user group default.iam-user-group การสำรองข้อมูล ขีดจำกัดการใช้งาน" loading="lazy" decoding="async"></p>

เมื่อเลือก Public ฟอร์มระบุว่า user group ต้องมีเฉพาะผู้ใช้ที่ยืนยันตัวตนด้วย IAM และกรอก default.iam-user-group ให้ การเข้ารหัสระหว่างส่งข้อมูลเปิดอยู่และปิดไม่ได้ที่นี่ การสำรองข้อมูลอัตโนมัติไม่ได้ถูกเลือก <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/05-create-valkey-serverless-filled.webp' | relative_url }}" width="1440" height="2604" alt="ฟอร์มที่กรอกแล้ว: ชื่อ notes-on-redis-valkey, Public, พื้นที่จัดเก็บสูงสุด 1 GB, สูงสุด 200,000 ECPU ต่อวินาที" loading="lazy" decoding="async"></p>

ใช้ขีดจำกัดการใช้งานเป็นเพดานค่าใช้จ่าย: พื้นที่จัดเก็บข้อมูลสูงสุด 1 GB (ฟอร์มอนุญาต 1 ถึง 5,000 GB) และสูงสุด 200,000 ECPU ต่อวินาที (1,000 ถึง 15,000,000) <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/06-valkey-cache-details.webp' | relative_url }}" width="1440" height="1236" alt="รายละเอียดแคช: available, Valkey 9.0, Public, แสดงขีดจำกัด" loading="lazy" decoding="async"></p>

รายละเอียดหลังสร้าง: สถานะ Available, เวอร์ชันเอนจิน 9.0, ชนิดการเชื่อมต่อ Public, ขีดจำกัดทั้งสองรายการ, endpoint บนพอร์ต 6379 <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/07-valkey-connect-cloudshell.webp' | relative_url }}" width="1440" height="2267" alt="ส่วน Connect to your cache พร้อมคำแนะนำ CloudShell และ CLI" loading="lazy" decoding="async"></p>

คำแนะนำการเชื่อมต่อ: สร้างโทเค็น SigV4 ด้วย Developer Toolkit แล้วใช้ valkey-cli -c --tls --user โทเค็นใช้ได้ 15 นาที แท็บอื่น: MCP integration, Valkey GLIDE (แนะนำ), client library <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/08-valkey-iam-user-group.webp' | relative_url }}" width="1440" height="800" alt="default.iam-user-group ที่มีผู้ใช้หนึ่งราย คือ default.iam-user" loading="lazy" decoding="async"></p>

IAM user group เริ่มต้นมีผู้ใช้หนึ่งราย คือ default.iam-user, access string เป็น ~* +@all, ใช้ได้ทั้งผ่าน Public และ VPC <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/09-valkey-users.webp' | relative_url }}" width="1440" height="765" alt="รายการผู้ใช้: default (เฉพาะ VPC) และ default.iam-user (Public และ VPC)" loading="lazy" decoding="async"></p>

มีผู้ใช้สองราย: ผู้ใช้ default ที่ไม่มีรหัสผ่าน (เฉพาะ VPC) และผู้ใช้ IAM <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/10-valkey-events.webp' | relative_url }}" width="1440" height="998" alt="แท็บ Events ที่มีหนึ่งเหตุการณ์: สร้างแคชแล้วและพร้อมใช้งาน" loading="lazy" decoding="async"></p>

สร้างเมื่อ 14:36:59 KST, พร้อมใช้งานเมื่อ 14:37:57 <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/11-valkey-monitoring.webp' | relative_url }}" width="1440" height="1800" alt="แท็บ Monitoring: ข้อมูลที่จัดเก็บ ECPU ที่ใช้ เวลาแฝงการอ่านและเขียน คำสั่งทั้งหมด อัตรา cache hit" loading="lazy" decoding="async"></p>

Monitoring หลังการทดสอบ: ข้อมูลที่จัดเก็บสูงสุด 649 MB ในจุดข้อมูล 5 นาที; เวลาแฝงการอ่านสูงสุด 2.4 ms, เวลาแฝงการเขียนสูงสุด 1.4 ms ฝั่งเซิร์ฟเวอร์ <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/12-valkey-delete-dialog.webp' | relative_url }}" width="1440" height="765" alt="กล่องโต้ตอบการลบที่ตั้งการสำรองครั้งสุดท้ายเป็น No และพิมพ์ชื่อแล้ว" loading="lazy" decoding="async"></p>

การลบต้องพิมพ์ชื่อแคชและมีค่าเริ่มต้นเป็นการสร้างการสำรองครั้งสุดท้าย; เลือก No แคชหายไปจากรายการหลังจากนั้นประมาณ 3 นาที <small>จับภาพเมื่อ 2026-11-07, AWS ap-northeast-2.</small>

#### ค่าใช้จ่าย

แคชมีอายุประมาณ 31 นาที ตามรายการราคา: พื้นที่จัดเก็บประมาณ 0.2 GB-hour (ขั้นต่ำ 100 MB บวกการทดสอบหน่วยความจำ) และประมาณ 5 ล้าน ECPU รวมกันราว $0.05 ขณะเขียนนี้ใบเรียกเก็บเงินของ AWS ยังไม่แสดงรายการนี้ เมื่อแสดงแล้ว จำนวนเงินที่เรียกเก็บจะบันทึกลงใน `STATUS.md`

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: sebagian sudah dijalankan.** Perbandingan Redis dan Valkey secara lokal, matriks fitur, dan bagian ElastiCache di bawah ini dijalankan atau bersumber pada 2026-11-07; linimasa lisensi dan alternatifnya masih berupa rencana di [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Open Source 8.x, Redis Cloud / Software, Valkey 9.x, ElastiCache for Valkey dan for Redis OSS (≤ 7.1), Azure Managed Redis (berisi Redis Enterprise), Memorystore for Valkey — sebuah matriks dengan sumber pada setiap sel (lisensi, modul, Active-Active, tiering, SLA, model harga), linimasa lisensi (BSD-3 → RSALv2/SSPL pada 7.4 → AGPLv3 ditambahkan pada 8.0; Valkey di-fork dari 7.2.4 di bawah BSD-3), dan beban kerja yang sama dijalankan berdampingan pada Redis 8.10 dan Valkey 9.1. Dragonfly, KeyDB, dan Garnet masing-masing satu paragraf.

### Redis 8.10 dan Valkey 9.1 secara lokal

**Diverifikasi pada Redis 8.10.3, Valkey 9.1.3, dan Valkey bundle 9.1, 2026-11-07,** di Docker pada satu host 24 core dengan pengaturan bawaan dan tanpa persistensi. Sumber dan keluaran lengkap: [`compare/01-valkey-vs-redis-local`](https://github.com/litkhai/notes-on-redis/tree/main/compare/01-valkey-vs-redis-local).

| | Redis 8.10.3 | Valkey 9.1.3 | Valkey bundle 9.1 |
|---|---|---|---|
| Bidang versi `INFO` | `redis_version:8.10.3` | `redis_version:7.2.4`, `valkey_version:9.1.3` | sama seperti Valkey |
| Modul yang dimuat | Search, JSON, Bloom, Time series, vector sets | `lua` saja | `json`, `bf`, `search`, `ldap`, `lua` |
| Perintah di `COMMAND LIST` | 669 | 399 | 450 |
| JSON, Bloom, Search | ya | tidak | ya (subset) |
| Time series, top-k, vector sets, Array | ya | tidak | tidak |
| Kedaluwarsa field hash | ya | ya | ya |
| 1 M string kecil | 62.1 B/key | 57.5 B/key | 57.5 B/key |
| SET/GET, pengaturan bawaan, req/s | 119,197–124,797 | 120,992–122,978 | 124,766–126,783 |
| SET/GET, `io-threads 4`, req/s | 342,427–352,568 | 315,391–342,349 | tidak dijalankan |

Hanya ada di Valkey: `CLUSTERSCAN`, migrasi slot atomik (`CLUSTER MIGRATESLOTS`), `COMMANDLOG`, `DELIFEQ`. Hanya ada di Redis selain keluarga modul: `BACKUP`, `HOTKEYS`, `HIMPORT`, `DIGEST`, serta tambahan stream seperti `XACKDEL`. Pada bundle, `FT.SEARCH` tepat setelah `FT.CREATE` tidak menemukan apa pun dan baru menemukan dokumen satu detik kemudian: key yang sudah ada diindeks di latar belakang. Baris throughput adalah hasil pengukuran pada satu mesin; melalui port yang dipublikasikan Docker, ketiganya berhenti di sekitar 83,000 req/s, yaitu batas jalur penerusan port.

**Ketersediaan, berdampingan** (`compare/01-valkey-vs-redis-local/ha.py`). Skrip yang sama dijalankan pada kedua mesin: dengan node timeout klaster 3 dtk, replika dipromosikan setelah 4.2 dtk pada keduanya, Sentinel menunjuk master baru setelah 4.3 dtk (Redis) dan 4.4 dtk (Valkey), dan AOF dengan `appendfsync everysec` memuat ulang sekitar 632,000 key dalam 1.3 dtk pada keduanya. Hanya nama binernya yang berbeda; perintah klaster dan Sentinel sama.

### Matriks fitur

Satu tabel yang mencakup Redis Open Source 8, Redis Cloud, Valkey 9, ElastiCache for Valkey dan for Redis OSS, Azure Managed Redis, dan Memorystore for Valkey, dengan sumber di setiap sel: diukur di sini pada 2026-11-07, atau dokumentasi vendor yang dibaca pada hari itu, atau ditandai "belum terkonfirmasi". Tabel ini disimpan di repositori sehingga dapat bertambah sel demi sel: [`compare/matrix.md`](https://github.com/litkhai/notes-on-redis/blob/main/compare/matrix.md).

### ElastiCache Serverless for Valkey, dibandingkan dengan database gratis Redis Cloud

**Dijalankan pada 2026-11-07 di AWS ap-northeast-2 (Seoul).** Satu cache serverless, Valkey 9.0, dibuat dan dihapus melalui konsol; umurnya sekitar 31 menit. Skrip probe yang sama dan host klien yang sama di Korea seperti pada [lab database gratis Redis Cloud]({{ '/cloud/' | relative_url }}). Harga dari daftar harga AWS untuk Seoul yang terbit pada 2026-10-28, dibaca pada 2026-11-07. Disamarkan: ID dan alias akun, ARN, endpoint.

#### Yang berbeda

| | Database gratis Redis Cloud | ElastiCache Serverless for Valkey |
|---|---|---|
| Biaya | $0 untuk 30 MB | $0.101 per GB-hour data (minimum 100 MB, sekitar $7.4 sebulan saat idle) ditambah $0.0027 per sejuta ECPU |
| Dari dibuat hingga dapat dipakai | hitungan detik | 58 dtk |
| Engine | Redis 8.6.2 | Valkey 9.0 (tersedia 9, 8, dan 7); `INFO` melaporkan `redis_version:7.2` |
| Jaringan | endpoint publik; allow list CIDR, 0.0.0.0/0 secara default | VPC secara default; tipe koneksi Public yang mewajibkan autentikasi IAM |
| Autentikasi | pengguna default dan kata sandi | IAM: token SigV4 berlaku 15 menit, pengguna `default.iam-user` |
| TLS | nonaktif secara default | selalu aktif |
| Perintah multi-key | `MGET` atas sembarang key berhasil | `MGET` lintas slot ditolak: `Keys in request don't hash to the same slot` |
| Koneksi | koneksi ke-31 ditolak | 40 dibuka tanpa error |
| Memori | penulisan ditolak pada sekitar 28 MB | penulisan ditolak setelah sekitar 1.77 GB nilai 10 kB, dengan batas penyimpanan 1 GB |
| Backup | tidak ada di paket gratis | backup otomatis nonaktif secara default; dialog hapus secara default membuat backup akhir |
| Metrik | 16 grafik di konsol, 5 menit hingga 3 bulan | CloudWatch; 16 dari 50 metrik di halaman cache |
| Akses terprogram | REST API dengan key akun dan pengguna, Terraform dan Pulumi | AWS API, CLI, CloudFormation; sebuah MCP server untuk ElastiCache |

#### Pengukuran klien

| Probe | Redis Cloud gratis, TCP biasa | ElastiCache Serverless, TLS + IAM |
|---|---|---|
| Round trip, rata-rata 50 `PING` | 2.6 ms | 5.1 ms |
| 1 koneksi, tanpa pipeline | 249 ops/s | 287 ops/s |
| 8 koneksi, tanpa pipeline | 2,363 ops/s | 2,419 ops/s |
| 1 koneksi, pipeline 100 | 24,671 ops/s | 4,960 ops/s |
| 8 koneksi, pipeline 100 | 103,920 ops/s | 24,893 ops/s selama 15 dtk; 45,600–54,300 INCR/s pada uji per detik |
| 60 dtk berkelanjutan, 8 × pipeline 100 | 100,840–108,780 INCR/s, stabil | 0–45,785 INCR/s per 5 dtk; tiga jendela 5 detik bernilai nol, tanpa error |

Baris throughput bukan vonis untuk salah satu layanan: satu sisi memakai TCP biasa dan sisi lain TLS, klien adalah satu proses Python di Korea, dan cache serverless dibatasi pada 200,000 ECPU/s (jendela nol terjadi pada sekitar 40,000 INCR/s, di bawah batas itu; penyebabnya belum dijelaskan). Angka tanpa pipeline dibatasi oleh round trip di kedua sisi.

#### Konsol, layar demi layar

<p class="shot"><img src="{{ '/assets/img/elasticache-console/01-elasticache-dashboard.webp' | relative_url }}" width="1440" height="765" alt="Dasbor ElastiCache di Seoul tanpa sumber daya" loading="lazy" decoding="async"></p>

Dasbor ElastiCache: cache Valkey, Memcached, dan Redis OSS, global datastore, reserved node, backup, subnet group dan parameter group, manajemen pengguna, migrasi. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/02-valkey-caches-empty.webp' | relative_url }}" width="1440" height="765" alt="Daftar cache Valkey yang kosong" loading="lazy" decoding="async"></p>

Valkey caches adalah daftar dengan tombol Create cache. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/03-create-valkey-serverless-default.webp' | relative_url }}" width="1440" height="1520" alt="Formulir pembuatan cache Valkey dengan engine, opsi deployment, metode pembuatan, nama, versi engine, dan tipe koneksi" loading="lazy" decoding="async"></p>

Satu formulir: engine (Valkey direkomendasikan, Memcached, Redis OSS), deployment (Serverless atau cluster berbasis node), baru atau dipulihkan dari .rdb, versi engine 9, tipe koneksi VPC. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/04-create-valkey-serverless-customize.webp' | relative_url }}" width="1440" height="2404" alt="Pengaturan kustom: tipe jaringan, enkripsi, user group default.iam-user-group, backup, batas penggunaan" loading="lazy" decoding="async"></p>

Dengan Public dipilih, formulir menyatakan bahwa user group hanya boleh berisi pengguna dengan autentikasi IAM dan mengisi default.iam-user-group. Enkripsi saat transit aktif dan tidak dapat dimatikan di sini; backup otomatis tidak dicentang. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/05-create-valkey-serverless-filled.webp' | relative_url }}" width="1440" height="2604" alt="Formulir terisi: nama notes-on-redis-valkey, Public, penyimpanan maksimum 1 GB, maksimum 200,000 ECPU per detik" loading="lazy" decoding="async"></p>

Batas penggunaan dipakai sebagai plafon pengeluaran: penyimpanan data maksimum 1 GB (formulir mengizinkan 1 hingga 5,000 GB) dan maksimum 200,000 ECPU per detik (1,000 hingga 15,000,000). <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/06-valkey-cache-details.webp' | relative_url }}" width="1440" height="1236" alt="Detail cache: available, Valkey 9.0, Public, batas ditampilkan" loading="lazy" decoding="async"></p>

Detail setelah pembuatan: status Available, versi engine 9.0, tipe koneksi Public, kedua batas, endpoint pada port 6379. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/07-valkey-connect-cloudshell.webp' | relative_url }}" width="1440" height="2267" alt="Bagian Connect to your cache dengan petunjuk CloudShell dan CLI" loading="lazy" decoding="async"></p>

Petunjuk koneksi: buat token SigV4 dengan Developer Toolkit, lalu valkey-cli -c --tls --user. Token berlaku 15 menit. Tab lain: MCP integration, Valkey GLIDE (direkomendasikan), pustaka klien. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/08-valkey-iam-user-group.webp' | relative_url }}" width="1440" height="800" alt="default.iam-user-group dengan satu pengguna default.iam-user" loading="lazy" decoding="async"></p>

User group IAM default berisi satu pengguna, default.iam-user, access string ~* +@all, dapat dipakai melalui Public dan VPC. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/09-valkey-users.webp' | relative_url }}" width="1440" height="765" alt="Daftar pengguna: default (hanya VPC) dan default.iam-user (Public dan VPC)" loading="lazy" decoding="async"></p>

Ada dua pengguna: pengguna default tanpa kata sandi (hanya VPC) dan pengguna IAM. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/10-valkey-events.webp' | relative_url }}" width="1440" height="998" alt="Tab Events dengan satu event: cache dibuat dan siap digunakan" loading="lazy" decoding="async"></p>

Dibuat pada 14:36:59 KST, siap pada 14:37:57. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/11-valkey-monitoring.webp' | relative_url }}" width="1440" height="1800" alt="Tab Monitoring: data tersimpan, ECPU terpakai, latensi baca dan tulis, total perintah, cache hit rate" loading="lazy" decoding="async"></p>

Monitoring setelah pengujian: data tersimpan mencapai puncak 649 MB pada satu datapoint 5 menit; latensi baca hingga 2.4 ms, latensi tulis hingga 1.4 ms di sisi server. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/12-valkey-delete-dialog.webp' | relative_url }}" width="1440" height="765" alt="Dialog hapus dengan backup akhir diatur ke No dan nama sudah diketik" loading="lazy" decoding="async"></p>

Penghapusan meminta nama cache dan secara default membuat backup akhir; dipilih No. Cache hilang dari daftar sekitar 3 menit kemudian. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

#### Biaya

Cache hidup sekitar 31 menit. Menurut daftar harga: sekitar 0.2 GB-hour penyimpanan (minimum 100 MB, ditambah uji memori) dan sekitar 5 juta ECPU, totalnya kira-kira $0.05. Tagihan AWS belum menampilkannya saat ini ditulis; jumlah yang ditagih akan dimasukkan ke `STATUS.md` ketika sudah muncul.

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: sebahagian sudah dijalankan.** Perbandingan Redis dan Valkey secara setempat, matriks ciri dan bahagian ElastiCache di bawah dijalankan atau diperoleh sumbernya pada 2026-11-07; garis masa lesen dan alternatif masih merupakan rancangan dalam [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Open Source 8.x, Redis Cloud / Software, Valkey 9.x, ElastiCache for Valkey dan for Redis OSS (≤ 7.1), Azure Managed Redis (mengandungi Redis Enterprise), Memorystore for Valkey — satu matriks dengan sumber bagi setiap sel (lesen, modul, Active-Active, tiering, SLA, model harga), garis masa lesen (BSD-3 → RSALv2/SSPL pada 7.4 → AGPLv3 ditambah pada 8.0; Valkey dipecahkan daripada 7.2.4 di bawah BSD-3), dan beban kerja yang sama dijalankan secara bersebelahan pada Redis 8.10 dan Valkey 9.1. Dragonfly, KeyDB dan Garnet masing-masing satu perenggan.

### Redis 8.10 dan Valkey 9.1 secara setempat

**Disahkan pada Redis 8.10.3, Valkey 9.1.3 dan Valkey bundle 9.1, 2026-11-07,** dalam Docker pada satu hos 24 teras dengan tetapan lalai dan tanpa kegigihan data. Sumber dan output penuh: [`compare/01-valkey-vs-redis-local`](https://github.com/litkhai/notes-on-redis/tree/main/compare/01-valkey-vs-redis-local).

| | Redis 8.10.3 | Valkey 9.1.3 | Valkey bundle 9.1 |
|---|---|---|---|
| Medan versi `INFO` | `redis_version:8.10.3` | `redis_version:7.2.4`, `valkey_version:9.1.3` | sama seperti Valkey |
| Modul yang dimuatkan | Search, JSON, Bloom, Time series, vector sets | `lua` sahaja | `json`, `bf`, `search`, `ldap`, `lua` |
| Arahan dalam `COMMAND LIST` | 669 | 399 | 450 |
| JSON, Bloom, Search | ya | tidak | ya (subset) |
| Time series, top-k, vector sets, Array | ya | tidak | tidak |
| Tamat tempoh medan hash | ya | ya | ya |
| 1 M rentetan kecil | 62.1 B/key | 57.5 B/key | 57.5 B/key |
| SET/GET, tetapan lalai, req/s | 119,197–124,797 | 120,992–122,978 | 124,766–126,783 |
| SET/GET, `io-threads 4`, req/s | 342,427–352,568 | 315,391–342,349 | tidak dijalankan |

Hanya ada dalam Valkey: `CLUSTERSCAN`, pemindahan slot atomik (`CLUSTER MIGRATESLOTS`), `COMMANDLOG`, `DELIFEQ`. Hanya ada dalam Redis selain keluarga modul: `BACKUP`, `HOTKEYS`, `HIMPORT`, `DIGEST`, serta tambahan stream seperti `XACKDEL`. Pada bundle, `FT.SEARCH` sejurus selepas `FT.CREATE` tidak menemui apa-apa dan menemui dokumen sesaat kemudian: kunci yang sedia ada diindeks di latar belakang. Baris truput ialah ukuran pada satu mesin; melalui port yang diterbitkan Docker, ketiga-tiganya berhenti pada sekitar 83,000 req/s, iaitu had laluan pemajuan port.

**Ketersediaan, bersebelahan** (`compare/01-valkey-vs-redis-local/ha.py`). Skrip yang sama dijalankan pada kedua-dua enjin: dengan tamat masa nod kluster 3 s, replika dinaikkan taraf selepas 4.2 s pada kedua-duanya, Sentinel menamakan master baharu selepas 4.3 s (Redis) dan 4.4 s (Valkey), dan AOF dengan `appendfsync everysec` memuat semula kira-kira 632,000 kunci dalam 1.3 s pada kedua-duanya. Hanya nama binari yang berbeza; perintah kluster dan Sentinel adalah sama.

### Matriks ciri

Satu jadual merangkumi Redis Open Source 8, Redis Cloud, Valkey 9, ElastiCache for Valkey dan for Redis OSS, Azure Managed Redis dan Memorystore for Valkey, dengan sumber pada setiap sel: diukur di sini pada 2026-11-07, atau dokumentasi vendor yang dibaca pada hari itu, atau ditandakan "belum disahkan". Jadual ini disimpan dalam repositori supaya boleh bertambah sel demi sel: [`compare/matrix.md`](https://github.com/litkhai/notes-on-redis/blob/main/compare/matrix.md).

### ElastiCache Serverless for Valkey, bersebelahan dengan pangkalan data percuma Redis Cloud

**Dijalankan pada 2026-11-07 di AWS ap-northeast-2 (Seoul).** Satu cache serverless, Valkey 9.0, dicipta dan dipadam melalui konsol; hayatnya kira-kira 31 minit. Skrip probe yang sama dan hos klien yang sama di Korea seperti dalam [makmal pangkalan data percuma Redis Cloud]({{ '/cloud/' | relative_url }}). Harga daripada senarai harga AWS untuk Seoul yang diterbitkan pada 2026-10-28, dibaca pada 2026-11-07. Disamarkan: ID dan alias akaun, ARN, endpoint.

#### Perbezaannya

| | Pangkalan data percuma Redis Cloud | ElastiCache Serverless for Valkey |
|---|---|---|
| Kos | $0 untuk 30 MB | $0.101 setiap GB-hour data (minimum 100 MB, kira-kira $7.4 sebulan ketika melahu) ditambah $0.0027 setiap sejuta ECPU |
| Dicipta hingga boleh digunakan | beberapa saat | 58 s |
| Enjin | Redis 8.6.2 | Valkey 9.0 (9, 8 dan 7 ditawarkan); `INFO` melaporkan `redis_version:7.2` |
| Rangkaian | endpoint awam; senarai benar CIDR, 0.0.0.0/0 secara lalai | VPC secara lalai; jenis sambungan Public yang memerlukan pengesahan IAM |
| Pengesahan | pengguna default dan kata laluan | IAM: token SigV4 sah selama 15 minit, pengguna `default.iam-user` |
| TLS | dimatikan secara lalai | sentiasa hidup |
| Perintah berbilang kunci | `MGET` ke atas sebarang kunci berjaya | `MGET` merentas slot ditolak: `Keys in request don't hash to the same slot` |
| Sambungan | sambungan ke-31 ditolak | 40 dibuka tanpa ralat |
| Memori | penulisan ditolak pada kira-kira 28 MB | penulisan ditolak selepas kira-kira 1.77 GB nilai 10 kB, dengan had storan 1 GB ditetapkan |
| Sandaran | tiada pada pelan percuma | sandaran automatik dimatikan secara lalai; dialog pemadaman secara lalai mencipta sandaran akhir |
| Metrik | 16 carta dalam konsol, 5 minit hingga 3 bulan | CloudWatch; 16 daripada 50 metrik pada halaman cache |
| Akses secara atur cara | REST API dengan kunci akaun dan pengguna, Terraform dan Pulumi | AWS API, CLI, CloudFormation; sebuah pelayan MCP untuk ElastiCache |

#### Ukuran klien

| Probe | Redis Cloud percuma, TCP biasa | ElastiCache Serverless, TLS + IAM |
|---|---|---|
| Pergi balik, purata 50 `PING` | 2.6 ms | 5.1 ms |
| 1 sambungan, tanpa pipeline | 249 ops/s | 287 ops/s |
| 8 sambungan, tanpa pipeline | 2,363 ops/s | 2,419 ops/s |
| 1 sambungan, pipeline 100 | 24,671 ops/s | 4,960 ops/s |
| 8 sambungan, pipeline 100 | 103,920 ops/s | 24,893 ops/s dalam 15 s; 45,600–54,300 INCR/s dalam larian setiap saat |
| 60 s berterusan, 8 × pipeline 100 | 100,840–108,780 INCR/s, stabil | 0–45,785 INCR/s setiap 5 s; tiga tetingkap 5 saat pada sifar, tiada ralat |

Baris throughput bukan penentu bagi mana-mana perkhidmatan: satu pihak menggunakan TCP biasa dan satu lagi TLS, klien ialah satu proses Python di Korea, dan cache serverless dihadkan pada 200,000 ECPU/s (tetingkap sifar berlaku pada kira-kira 40,000 INCR/s, di bawah had itu; puncanya tidak dapat dijelaskan). Angka tanpa pipeline dihadkan oleh pergi balik pada kedua-dua pihak.

#### Konsol, skrin demi skrin

<p class="shot"><img src="{{ '/assets/img/elasticache-console/01-elasticache-dashboard.webp' | relative_url }}" width="1440" height="765" alt="Papan pemuka ElastiCache di Seoul tanpa sumber" loading="lazy" decoding="async"></p>

Papan pemuka ElastiCache: cache Valkey, Memcached dan Redis OSS, global datastore, reserved node, sandaran, subnet group dan parameter group, pengurusan pengguna, migrasi. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/02-valkey-caches-empty.webp' | relative_url }}" width="1440" height="765" alt="Senarai cache Valkey yang kosong" loading="lazy" decoding="async"></p>

Valkey caches ialah senarai dengan butang Create cache. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/03-create-valkey-serverless-default.webp' | relative_url }}" width="1440" height="1520" alt="Borang cipta cache Valkey dengan enjin, pilihan penempatan, kaedah penciptaan, nama, versi enjin dan jenis sambungan" loading="lazy" decoding="async"></p>

Satu borang: enjin (Valkey disyorkan, Memcached, Redis OSS), penempatan (Serverless atau kluster berasaskan nod), baharu atau dipulihkan daripada .rdb, versi enjin 9, jenis sambungan VPC. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/04-create-valkey-serverless-customize.webp' | relative_url }}" width="1440" height="2404" alt="Tetapan tersuai: jenis rangkaian, penyulitan, user group default.iam-user-group, sandaran, had penggunaan" loading="lazy" decoding="async"></p>

Apabila Public dipilih, borang menyatakan bahawa user group mesti hanya mengandungi pengguna yang disahkan IAM dan mengisi default.iam-user-group. Penyulitan semasa transit dihidupkan dan tidak boleh dimatikan di sini; sandaran automatik tidak ditandakan. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/05-create-valkey-serverless-filled.webp' | relative_url }}" width="1440" height="2604" alt="Borang yang diisi: nama notes-on-redis-valkey, Public, storan maksimum 1 GB, maksimum 200,000 ECPU sesaat" loading="lazy" decoding="async"></p>

Had penggunaan digunakan sebagai siling perbelanjaan: storan data maksimum 1 GB (borang membenarkan 1 hingga 5,000 GB) dan maksimum 200,000 ECPU sesaat (1,000 hingga 15,000,000). <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/06-valkey-cache-details.webp' | relative_url }}" width="1440" height="1236" alt="Butiran cache: available, Valkey 9.0, Public, had dipaparkan" loading="lazy" decoding="async"></p>

Butiran selepas penciptaan: status Available, versi enjin 9.0, jenis sambungan Public, kedua-dua had, endpoint pada port 6379. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/07-valkey-connect-cloudshell.webp' | relative_url }}" width="1440" height="2267" alt="Bahagian Connect to your cache dengan arahan CloudShell dan CLI" loading="lazy" decoding="async"></p>

Arahan sambungan: jana token SigV4 dengan Developer Toolkit, kemudian valkey-cli -c --tls --user. Token sah selama 15 minit. Tab lain: MCP integration, Valkey GLIDE (disyorkan), pustaka klien. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/08-valkey-iam-user-group.webp' | relative_url }}" width="1440" height="800" alt="default.iam-user-group dengan satu pengguna default.iam-user" loading="lazy" decoding="async"></p>

User group IAM lalai mengandungi satu pengguna, default.iam-user, access string ~* +@all, boleh digunakan melalui Public dan VPC. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/09-valkey-users.webp' | relative_url }}" width="1440" height="765" alt="Senarai pengguna: default (VPC sahaja) dan default.iam-user (Public dan VPC)" loading="lazy" decoding="async"></p>

Terdapat dua pengguna: pengguna default tanpa kata laluan (VPC sahaja) dan pengguna IAM. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/10-valkey-events.webp' | relative_url }}" width="1440" height="998" alt="Tab Events dengan satu peristiwa: cache dicipta dan sedia digunakan" loading="lazy" decoding="async"></p>

Dicipta pada 14:36:59 KST, sedia pada 14:37:57. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/11-valkey-monitoring.webp' | relative_url }}" width="1440" height="1800" alt="Tab Monitoring: data disimpan, ECPU digunakan, kependaman baca dan tulis, jumlah arahan, kadar cache hit" loading="lazy" decoding="async"></p>

Monitoring selepas ujian: data disimpan memuncak pada 649 MB dalam satu titik data 5 minit; kependaman baca sehingga 2.4 ms, kependaman tulis sehingga 1.4 ms di sebelah pelayan. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

<p class="shot"><img src="{{ '/assets/img/elasticache-console/12-valkey-delete-dialog.webp' | relative_url }}" width="1440" height="765" alt="Dialog pemadaman dengan sandaran akhir ditetapkan kepada No dan nama telah ditaip" loading="lazy" decoding="async"></p>

Pemadaman meminta nama cache dan secara lalai mencipta sandaran akhir; No dipilih. Cache hilang daripada senarai kira-kira 3 minit kemudian. <small>Ditangkap 2026-11-07, AWS ap-northeast-2.</small>

#### Kos

Cache hidup kira-kira 31 minit. Mengikut senarai harga: kira-kira 0.2 GB-hour storan (minimum 100 MB, ditambah ujian memori) dan kira-kira 5 juta ECPU, jumlahnya lebih kurang $0.05. Bil AWS belum menunjukkannya ketika ini ditulis; jumlah yang dibilkan akan dimasukkan ke dalam `STATUS.md` apabila ia muncul.

</div>
