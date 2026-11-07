# ElastiCache for Valkey

[English](#english) | [한국어](#한국어)

## English

**Verified on Valkey 9.0 (ElastiCache Serverless, AWS ap-northeast-2, Public connection type), 2026-11-07.**

One ElastiCache Serverless cache for Valkey, created in the console with the Public connection
type and usage limits as a spending cap (1 GB data storage, 200,000 ECPUs per second), probed
from the same host in Korea with the same script as
[`cloud/01-free-database`](../../cloud/01-free-database), then deleted. It lived about 31
minutes. The site's [Compare page](../../docs/compare.md) has the console walkthrough and the
side-by-side table.

### Run

```bash
# in CloudShell, same region (it has your console credentials):
python3 gen_token.py notes-on-redis-valkey            # prints a token valid for 15 minutes
# here:
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # endpoint from the cache details page, the token from CloudShell
.venv/bin/python limits.py info
.venv/bin/python limits.py ops
.venv/bin/python long_ops.py 60
.venv/bin/python limits.py conns
.venv/bin/python limits.py memory
```

Output as it appeared (2026-11-07, 05:49–05:59 UTC):

```text
$ limits.py info
redis_version: 7.2 valkey_version: 9.0 server_name: valkey
PING: True
used_memory_human: None
maxmemory_human: None
maxmemory_policy: None
CONFIG GET maxclients -> error: unknown command 'config', with args beginning with: GET
connected_clients: None
PING round trip, mean of 50: 5.1 ms

$ limits.py ops
connections=1 pipeline=off: 4301 ops in 15.0 s = 287 ops/s; errors=none
connections=8 pipeline=off: 36290 ops in 15.0 s = 2419 ops/s; errors=none
connections=1 pipeline=100: 74400 ops in 15.0 s = 4960 ops/s; errors=none
connections=8 pipeline=100: 595800 ops in 23.9 s = 24893 ops/s; errors=none

$ long_ops.py 60          (8 connections, pipeline 100, sampled every 5 s)
t=   5s     38320 INCR/s
t=  10s         0 INCR/s
t=  15s     18891 INCR/s
t=  20s     44232 INCR/s
t=  25s     19597 INCR/s
t=  30s         0 INCR/s
t=  35s     38966 INCR/s
t=  40s     35234 INCR/s
t=  45s         0 INCR/s
t=  50s     31140 INCR/s
t=  55s     45785 INCR/s
t=  60s     33775 INCR/s
t=  65s       100 INCR/s
errors: none
t=  70s        20 INCR/s

$ limits.py conns
40 connections opened without error
connections held by this script: 40
server connected_clients: None

$ limits.py memory        (10 kB values, pipelines of 50)
after 176850 keys of 10 kB (56.8 s): OutOfMemoryError: Command # 38 (SET lab:limits:mem:176887...) of pipeline caused error: command not allowed when used memory > 'maxmemory'.
used_memory_human: None maxmemory_human: None
evicted_keys: None
SET with EX after OOM: OutOfMemoryError command not allowed when used memory > 'maxmemory'.
```

The first run of `long_ops.py` used `MGET` to read the eight counters and failed with
`ClusterCrossSlotError: Keys in request don't hash to the same slot`; the script now reads
them with one `GET` each. The data was removed with `FLUSHALL` before the cache was deleted
(a key-by-key cleanup over TLS was too slow).

### What was observed

- **Cluster semantics:** the serverless endpoint behaves as a cluster. A multi-key command over
  keys in different slots is refused; the same `MGET` worked on the Redis Cloud free database.
- **Connections:** 40 connections opened without error (the free Redis Cloud database refused
  the 31st). Higher counts were not tried.
- **Memory:** writes were refused after 176,850 keys of 10 kB (about 1.77 GB of values) with the
  maximum data storage set to 1 GB; the console's Data Stored chart peaked at 649 MB in a
  5-minute datapoint. The gap between these numbers was not explained.
- **Throughput:** about 45,000–54,000 INCR/s in short runs; in the 60 s run three 5-second
  windows showed no progress at all, without client errors, at about 40,000 INCR/s, well below
  the 200,000 ECPUs/s cap.
- **Admin surface:** `CONFIG` is not available, and `INFO` leaves the memory and client fields empty.
- **Created to available:** 58 s (14:36:59 to 14:37:57 KST, from the Events tab).

### Not run / caveats

- TLS here, plain TCP on the Redis Cloud side: the throughput rows are not comparable.
- VPC connection type, node-based clusters, Redis OSS engine, backups and Global Datastore: not run.
- Cost by the price list is about $0.05; the billed amount was not visible yet.

| | |
|---|---|
| Plan needed | AWS account; about $0.05 for this run (price list for Seoul, published 2026-10-28) |
| Verified on | Valkey 9.0, ElastiCache Serverless, ap-northeast-2, 2026-11-07 |

## 한국어

**확인: Valkey 9.0(ElastiCache Serverless, AWS ap-northeast-2, Public 접속), 2026-11-07.**

콘솔에서 Public 접속 방식과 지출 상한용 사용량 한도(저장 1 GB, 초당 ECPU 200,000)를 걸고
ElastiCache Serverless for Valkey 캐시 하나를 만들었다.
[`cloud/01-free-database`](../../cloud/01-free-database)와 같은 한국의 호스트에서 같은
스크립트로 측정한 뒤 지웠다. 약 31분 살아 있었다. 콘솔 안내와 비교표는 사이트의
[Compare 페이지](../../docs/compare.md)에 있다.

### 실행

```bash
# 같은 리전의 CloudShell에서(콘솔 자격 증명이 있음):
python3 gen_token.py notes-on-redis-valkey            # 15분 유효한 토큰 출력
# 여기서:
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # 캐시 상세 화면의 엔드포인트, CloudShell의 토큰
.venv/bin/python limits.py info
.venv/bin/python limits.py ops
.venv/bin/python long_ops.py 60
.venv/bin/python limits.py conns
.venv/bin/python limits.py memory
```

출력은 영문 절과 같다(2026-11-07, 05:49–05:59 UTC). 처음 `long_ops.py`는 카운터 여덟 개를
`MGET`으로 읽다가 `ClusterCrossSlotError`로 실패했고, 지금은 `GET`으로 하나씩 읽는다.
데이터는 캐시를 지우기 전에 `FLUSHALL`로 비웠다(TLS로 키를 하나씩 지우기는 너무 느렸다).

### 관찰한 것

- **클러스터 의미론:** 서버리스 엔드포인트는 클러스터처럼 동작한다. 슬롯이 다른 키에 대한
  여러 키 명령은 거절된다. 같은 `MGET`이 Redis Cloud 무료 DB에서는 됐다.
- **커넥션:** 40개가 오류 없이 열렸다(Redis Cloud 무료 DB는 31번째를 거절). 더 많이는 시험하지 않았다.
- **메모리:** 저장 최대를 1 GB로 걸었는데 10 kB 키 176,850개(값 약 1.77 GB) 뒤에 쓰기가
  거절됐다. 콘솔 Data Stored 차트는 5분 데이터포인트 기준 최고 649 MB였다. 두 수치의 차이는 밝히지 못했다.
- **처리량:** 짧은 측정에서 초당 약 45,000–54,000 INCR. 60초 측정에서는 초당 약 40,000 INCR에서
  5초 구간 세 번이 클라이언트 오류 없이 전혀 진행되지 않았다. 초당 200,000 ECPU 상한보다 한참 낮다.
- **관리 기능:** `CONFIG`는 쓸 수 없고, `INFO`의 메모리·클라이언트 항목은 비어 있다.
- **만들기부터 사용 가능까지:** 58초(14:36:59–14:37:57 KST, Events 탭 기준).

### 미실행 / 주의

- 이쪽은 TLS, Redis Cloud 쪽은 평문 TCP다. 처리량 행은 비교할 수 없다.
- VPC 접속 방식, 노드 기반 클러스터, Redis OSS 엔진, 백업, Global Datastore는 실행하지 않았다.
- 가격표로 계산한 비용은 약 $0.05다. 청구액은 아직 보이지 않았다.

| | |
|---|---|
| 필요한 플랜 | AWS 계정. 이번 실행 약 $0.05(서울 가격표, 2026-10-28 게시) |
| 확인한 버전 | Valkey 9.0, ElastiCache Serverless, ap-northeast-2, 2026-11-07 |
