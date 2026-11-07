---
layout: default
title: Setup
permalink: /setup/
---

# Setup

<div class="lang" data-lang="en" markdown="1">

## English

**A local Redis 8 and a free cloud database, both answering from Python and Node.** Run on 2026-11-07: Redis Open Source 8.10.3 and Redis Insight 3.8.0 in Docker, `redis-cli`, redis-py 6.1.1 and node-redis 6.3.1, and the Redis Cloud free database from the [Redis Cloud page]({{ '/cloud/' | relative_url }}). Source: [`setup/`](https://github.com/litkhai/notes-on-redis/tree/main/setup), [`local/01`](https://github.com/litkhai/notes-on-redis/tree/main/local/01-redis-8-docker), [`local/02`](https://github.com/litkhai/notes-on-redis/tree/main/local/02-data-types-tour).

### The local stack

One compose file starts both containers. Host ports are 16379 and 15540 rather than the defaults, so the stack can share a Docker host.

```bash
cd setup && docker compose up -d
docker exec -it nor-redis8 redis-cli PING        # PONG
```

`redis:latest`, `redis:8` and `redis:8.10.3` had the same digest on 2026-11-07; the compose file pins `8.10.3`. The image has no config file: its entrypoint adds `--loadmodule` for every module in `/usr/local/lib/redis/modules/`, so Search, JSON, Time series and Bloom are there from the start, and vector sets are built in.

**More clients** (`go/`, `java/`). go-redis 9.23.0 (needs Go 1.26) and Jedis 8.0.2 connected to both servers with a `redis://` URL; go-redis negotiated RESP3. Jedis with `RedisProtocol.RESP3` and a `CacheConfig` sent one GET for 1,001 reads, like redis-py's client-side cache.

### Redis Insight

<p class="shot"><img src="{{ '/assets/img/setup/01-insight-databases.webp' | relative_url }}" width="1440" height="765" alt="Redis Insight database list with local-redis-8 registered" loading="lazy" decoding="async"></p>

The `RI_REDIS_*` variables in the compose file register the local database when Insight starts; `RI_ACCEPT_TERMS_AND_CONDITIONS` skips the first-run dialog. "Create free Cloud database" links to the same free plan as the Redis Cloud page. <small>Captured 2026-11-07, Redis Insight 3.8.0, local Redis 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/02-insight-browser.webp' | relative_url }}" width="1440" height="765" alt="Insight Browse view listing keys by type: sorted set, vector set, top-k, list, stream, array" loading="lazy" decoding="async"></p>

Browse after the data types tour: keys grouped by prefix, each with its type. ARRAY and VECTOR SET, the newest native types, get their own labels. <small>Captured 2026-11-07, Redis Insight 3.8.0, local Redis 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/03-insight-json-key.webp' | relative_url }}" width="1440" height="765" alt="JSON key user:1 open in Insight with its fields" loading="lazy" decoding="async"></p>

A JSON key opens as a tree; "Make searchable" offers to create a Search index over it. <small>Captured 2026-11-07, Redis Insight 3.8.0, local Redis 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/04-insight-workbench.webp' | relative_url }}" width="1440" height="765" alt="Workbench running FT.SEARCH with one matched document" loading="lazy" decoding="async"></p>

Workbench runs commands and renders Search results as a table; it ships tutorials for search and vector search. <small>Captured 2026-11-07, Redis Insight 3.8.0, local Redis 8.10.3.</small>

### Clients and the cloud database

`smoke.py` and `smoke.mjs` run PING, SET/GET and read the server version against both targets; the cloud URL comes from a gitignored `.env`.

| Client | Local container | Redis Cloud free database |
|---|---|---|
| redis-py 6.1.1 | PING True, version 8.10.3 | PING True, version 8.6.2 |
| node-redis 6.3.1 | PONG, version 8.10.3 | PONG, version 8.6.2 |
| `redis-cli -u` (8.10.3 image) | PONG | PONG |

**The free plan has no TLS.** Turning it on through the REST API failed with `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN` ("Selected subscription plan does not support database 'enableTls'"), so the cloud smoke test is plain TCP. Keep only test data on the free database.

### Lab: what the image runs, and io-threads

**Verified on Redis 8.10.3, 2026-11-07.** `redis-benchmark` inside the container, SET/GET, 64-byte values, on a 24-core host:

| Server | 4 client threads | 8 client threads |
|---|---|---|
| `io-threads 1` (default) | 121,021–124,922 req/s | 117,405–126,687 req/s |
| `io-threads 4` | 285,144–285,225 req/s | 332,945–347,403 req/s |

With 4 client threads the io-threads 4 numbers were the same in every run: the client was the limit, and 8 client threads moved it up. Server and client share one machine, so read these as measurements on that machine, not as a rule.

### Lab: one command per data type

**Verified on Redis 8.10.3, 2026-11-07.** `local/02-data-types-tour/tour.sh` runs one command per type on the stock image, all without an error:

| Type | What the command shows |
|---|---|
| String | `INCR` a page counter |
| Hash | `HEXPIRE` one field; `HTTL` shows 60 for it and -1 for the other |
| List, Set, Sorted set | a queue, membership, a leaderboard |
| Stream | `XADD`, a consumer group, `XREADGROUP` |
| Geo | shops within 5 km of Seoul City Hall |
| Bitmap, HyperLogLog | daily active bits, distinct count |
| JSON | append to an array inside a document |
| Time series | samples averaged into 2-hour buckets |
| Bloom, Top-k | seen-before check, most frequent items |
| Array (8.8) | sparse: `ARLEN` 1001 after writing indexes 0–2 and 1000; `ARSCAN` returns four |
| Vector set (beta) | nearest neighbour with `VSIM` |
| Search | `FT.CREATE` over hashes, then a numeric range query |

**The other probabilistic types** (`local/02-data-types-tour/probabilistic.sh`). A count-min sketch of 56 KB counted 100,000 page views exactly for the pages checked (10,000, 91, 99, 0). A cuckoo filter, unlike Bloom, deleted an item, with a 0.69% false-positive rate over 10,000 absent users. A t-digest of 10 KB gave the median and p99.9 within 1% but p99 as 325 ms against an exact 257 ms, where the data jumps and few points sit.

### Lab: search and vector search

**Verified on Redis 8.10.3, 2026-11-07.** `local/03-search-vector/lab.py` indexes 30 one-line notes from this site as hashes and as JSON, embedded locally with a small open model (no API key).

| Query | What came back |
|---|---|
| Full text `failover`, tag `{memory}`, numeric `[-inf 2025]` | the matching notes |
| Full text `cache in sync with my database` | nothing: every word must appear |
| KNN "How do I keep Redis in sync with my Postgres tables?" | the change data capture note first (similarity 0.83) |
| KNN with `(@category:{cluster})` as a filter | only cluster notes |
| `FT.HYBRID` (8.4+), text plus vector, `COMBINE RRF` | the union of both lists, the first of each on top |
| Vector set: `VADD` the same vectors, `VSIM` | the same top 3 as KNN, with no index declared |

redis-py 8.1.0 negotiated RESP3, so `FT.SEARCH` replies arrived as maps rather than the flat lists older examples parse. Docs: [Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/), [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/). Lab: [`local/03-search-vector`](https://github.com/litkhai/notes-on-redis/tree/main/local/03-search-vector).

**More search features** (`extras.py`). `FT.AGGREGATE` grouped and computed; synonyms made "switchover" find the failover notes once the background rescan finished; `FT.SPELLCHECK` suggested `failover`, `eviction` and `replica` for misspellings; `FLOAT16`, `INT8` and `SVS-VAMANA` with `LVQ8` returned the same top 3 as `FLOAT32`. Korean questions found the right English notes only with a multilingual model, and not for every question.

### Not covered yet

Redis Insight desktop (the Docker image is the same application) and clients other than redis-py and node-redis.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

**로컬 Redis 8과 무료 클라우드 DB, 둘 다 Python과 Node에서 응답한다.** 2026-11-07 실행: Docker의 Redis Open Source 8.10.3과 Redis Insight 3.8.0, `redis-cli`, redis-py 6.1.1과 node-redis 6.3.1, 그리고 [Redis Cloud 페이지]({{ '/cloud/' | relative_url }})의 무료 DB. 소스: [`setup/`](https://github.com/litkhai/notes-on-redis/tree/main/setup), [`local/01`](https://github.com/litkhai/notes-on-redis/tree/main/local/01-redis-8-docker), [`local/02`](https://github.com/litkhai/notes-on-redis/tree/main/local/02-data-types-tour).

### 로컬 스택

compose 파일 하나로 두 컨테이너를 띄운다. 호스트 포트는 기본값 대신 16379와 15540이라 Docker 호스트를 함께 쓸 수 있다.

```bash
cd setup && docker compose up -d
docker exec -it nor-redis8 redis-cli PING        # PONG
```

2026-11-07에 `redis:latest`, `redis:8`, `redis:8.10.3`은 같은 digest였다. compose 파일은 `8.10.3`으로 고정한다. 이미지에는 설정 파일이 없다. 진입점이 `/usr/local/lib/redis/modules/`의 모듈마다 `--loadmodule`을 붙이므로 Search, JSON, Time series, Bloom이 처음부터 있고, 벡터 셋은 서버에 내장돼 있다.

**다른 클라이언트**(`go/`, `java/`). go-redis 9.23.0(Go 1.26 필요)과 Jedis 8.0.2가 `redis://` URL로 두 서버에 붙었고, go-redis는 RESP3로 협상했다. `RedisProtocol.RESP3`와 `CacheConfig`를 준 Jedis는 redis-py의 클라이언트 캐시처럼 읽기 1,001번에 GET 1번만 보냈다.

### Redis Insight

<p class="shot"><img src="{{ '/assets/img/setup/01-insight-databases.webp' | relative_url }}" width="1440" height="765" alt="local-redis-8이 등록된 Redis Insight DB 목록" loading="lazy" decoding="async"></p>

compose 파일의 `RI_REDIS_*` 변수가 Insight가 시작할 때 로컬 DB를 등록하고, `RI_ACCEPT_TERMS_AND_CONDITIONS`가 첫 실행 창을 건너뛴다. "Create free Cloud database"는 Redis Cloud 페이지와 같은 무료 플랜으로 이어진다. <small>2026-11-07 캡처, Redis Insight 3.8.0, 로컬 Redis 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/02-insight-browser.webp' | relative_url }}" width="1440" height="765" alt="유형별 키 목록이 있는 Insight Browse 화면: sorted set, vector set, top-k, list, stream, array" loading="lazy" decoding="async"></p>

자료형 둘러보기 뒤의 Browse: 접두사로 묶인 키와 각 유형. 가장 새로운 내장 자료형인 ARRAY와 VECTOR SET도 각자의 표시가 있다. <small>2026-11-07 캡처, Redis Insight 3.8.0, 로컬 Redis 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/03-insight-json-key.webp' | relative_url }}" width="1440" height="765" alt="필드가 보이는 JSON 키 user:1을 연 Insight" loading="lazy" decoding="async"></p>

JSON 키는 트리로 열린다. "Make searchable"은 그 위에 Search 인덱스를 만들어 준다. <small>2026-11-07 캡처, Redis Insight 3.8.0, 로컬 Redis 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/04-insight-workbench.webp' | relative_url }}" width="1440" height="765" alt="FT.SEARCH가 문서 하나를 찾은 Workbench" loading="lazy" decoding="async"></p>

Workbench는 명령을 실행하고 Search 결과를 표로 보여 준다. 검색과 벡터 검색 튜토리얼이 들어 있다. <small>2026-11-07 캡처, Redis Insight 3.8.0, 로컬 Redis 8.10.3.</small>

### 클라이언트와 클라우드 DB

`smoke.py`와 `smoke.mjs`는 두 대상에 PING, SET/GET을 하고 서버 버전을 읽는다. 클라우드 URL은 gitignore된 `.env`에서 읽는다.

| 클라이언트 | 로컬 컨테이너 | Redis Cloud 무료 DB |
|---|---|---|
| redis-py 6.1.1 | PING True, 버전 8.10.3 | PING True, 버전 8.6.2 |
| node-redis 6.3.1 | PONG, 버전 8.10.3 | PONG, 버전 8.6.2 |
| `redis-cli -u`(8.10.3 이미지) | PONG | PONG |

**무료 플랜에는 TLS가 없다.** REST API로 켜려 하자 `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`("Selected subscription plan does not support database 'enableTls'")으로 실패했다. 그래서 클라우드 스모크 테스트는 평문 TCP다. 무료 DB에는 시험 데이터만 둔다.

### 실습: 이미지가 돌리는 것과 io-threads

**확인: Redis 8.10.3, 2026-11-07.** 컨테이너 안의 `redis-benchmark`, SET/GET, 64바이트 값, 24코어 호스트:

| 서버 | 클라이언트 스레드 4 | 클라이언트 스레드 8 |
|---|---|---|
| `io-threads 1`(기본) | 초당 121,021–124,922 | 초당 117,405–126,687 |
| `io-threads 4` | 초당 285,144–285,225 | 초당 332,945–347,403 |

클라이언트 스레드 4에서는 io-threads 4의 수치가 매번 같았다. 클라이언트가 한계였고, 스레드 8로 늘리자 올라갔다. 서버와 클라이언트가 같은 기계에 있으므로 그 기계에서 잰 값으로 읽어야 한다. 규칙이 아니다.

### 실습: 자료형마다 명령 하나

**확인: Redis 8.10.3, 2026-11-07.** `local/02-data-types-tour/tour.sh`가 기본 이미지에서 자료형마다 명령 하나를 돌린다. 모두 오류 없이 응답했다.

| 자료형 | 명령이 보여 주는 것 |
|---|---|
| String | 페이지 카운터 `INCR` |
| Hash | 필드 하나에 `HEXPIRE`. `HTTL`은 그 필드 60, 다른 필드 -1 |
| List, Set, Sorted set | 큐, 소속 여부, 순위표 |
| Stream | `XADD`, 컨슈머 그룹, `XREADGROUP` |
| Geo | 서울시청 5 km 안의 가게 |
| Bitmap, HyperLogLog | 일별 활성 비트, 고유 개수 |
| JSON | 문서 안 배열에 추가 |
| Time series | 2시간 단위 평균 |
| Bloom, Top-k | 본 적 있는지 확인, 가장 잦은 항목 |
| Array(8.8) | 희소: 인덱스 0–2와 1000을 쓰면 `ARLEN` 1001, `ARSCAN`은 네 개 |
| Vector set(베타) | `VSIM`으로 최근접 이웃 |
| Search | 해시 위에 `FT.CREATE`, 이어서 숫자 범위 질의 |

**나머지 확률형 자료형**(`local/02-data-types-tour/probabilistic.sh`). 56 KB짜리 count-min sketch가 조회 100,000건을 확인한 페이지들에 대해 정확히 셌다(10,000, 91, 99, 0). Cuckoo filter는 Bloom과 달리 항목을 지울 수 있었고, 없는 사용자 10,000명에 대해 오탐률 0.69%였다. 10 KB짜리 t-digest는 중앙값과 p99.9를 1% 안으로 맞혔지만, p99는 실제 257 ms에 325 ms였다. 데이터가 건너뛰어 점이 거의 없는 구간이다.

### 실습: 검색과 벡터 검색

**확인: Redis 8.10.3, 2026-11-07.** `local/03-search-vector/lab.py`는 이 사이트의 한 줄 메모 30개를 해시와 JSON으로 색인한다. 임베딩은 작은 공개 모델로 로컬에서 만든다(API 키 없음).

| 질의 | 돌아온 것 |
|---|---|
| 전문 `failover`, 태그 `{memory}`, 숫자 `[-inf 2025]` | 해당하는 메모 |
| 전문 `cache in sync with my database` | 없음: 모든 단어가 들어 있어야 한다 |
| KNN "How do I keep Redis in sync with my Postgres tables?" | 변경 데이터 캡처 메모가 1위(유사도 0.83) |
| `(@category:{cluster})` 필터를 건 KNN | 클러스터 메모만 |
| `FT.HYBRID`(8.4+), 텍스트와 벡터, `COMBINE RRF` | 두 목록의 합집합, 각 목록의 1위가 맨 위 |
| 벡터 셋: 같은 벡터를 `VADD`, `VSIM` | 색인을 선언하지 않고도 KNN과 같은 상위 3개 |

redis-py 8.1.0은 RESP3로 협상했고, 그래서 `FT.SEARCH` 응답이 예전 예제가 파싱하는 평평한 목록이 아니라 맵으로 왔다. 문서: [Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/), [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/). 실습: [`local/03-search-vector`](https://github.com/litkhai/notes-on-redis/tree/main/local/03-search-vector).

**검색 부가 기능**(`extras.py`). `FT.AGGREGATE`는 묶고 계산했다. 동의어는 백그라운드 재검사가 끝나자 "switchover"로 장애 조치 메모를 찾게 했다. `FT.SPELLCHECK`는 오타에 `failover`, `eviction`, `replica`를 제안했다. `FLOAT16`, `INT8`, `LVQ8`의 `SVS-VAMANA`도 `FLOAT32`와 같은 상위 3개를 돌려줬다. 한국어 질문은 다국어 모델일 때만, 그것도 일부 질문만 맞는 영어 메모를 찾았다.

### 아직 다루지 않은 것

Redis Insight 데스크톱(Docker 이미지가 같은 애플리케이션)과 redis-py·node-redis 외의 클라이언트.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

**本地 Redis 8 和免费云数据库，都能从 Python 和 Node 得到响应。** 运行于 2026-11-07：Docker 中的 Redis Open Source 8.10.3 和 Redis Insight 3.8.0、`redis-cli`、redis-py 6.1.1 和 node-redis 6.3.1，以及 [Redis Cloud 页面]({{ '/cloud/' | relative_url }})中的 Redis Cloud 免费数据库。源码：[`setup/`](https://github.com/litkhai/notes-on-redis/tree/main/setup), [`local/01`](https://github.com/litkhai/notes-on-redis/tree/main/local/01-redis-8-docker), [`local/02`](https://github.com/litkhai/notes-on-redis/tree/main/local/02-data-types-tour)。

### 本地环境

一个 compose 文件启动两个容器。主机端口用 16379 和 15540 而不是默认值，这样该环境可以与其他服务共用同一台 Docker 主机。

```bash
cd setup && docker compose up -d
docker exec -it nor-redis8 redis-cli PING        # PONG
```

2026-11-07 当天 `redis:latest`、`redis:8` 和 `redis:8.10.3` 的 digest 相同；compose 文件固定为 `8.10.3`。镜像中没有配置文件：入口脚本会为 `/usr/local/lib/redis/modules/` 中的每个模块添加 `--loadmodule`，因此 Search、JSON、Time series 和 Bloom 一开始就可用，而 Vector set 是内置的。

**更多客户端**（`go/`、`java/`）。go-redis 9.23.0（需要 Go 1.26）和 Jedis 8.0.2 都通过 `redis://` URL 连接到两台服务器；go-redis 协商使用了 RESP3。使用 `RedisProtocol.RESP3` 和 `CacheConfig` 的 Jedis，对 1,001 次读取只发送了一次 GET，与 redis-py 的客户端缓存一样。

### Redis Insight

<p class="shot"><img src="{{ '/assets/img/setup/01-insight-databases.webp' | relative_url }}" width="1440" height="765" alt="已注册 local-redis-8 的 Redis Insight 数据库列表" loading="lazy" decoding="async"></p>

compose 文件中的 `RI_REDIS_*` 变量会在 Insight 启动时注册本地数据库；`RI_ACCEPT_TERMS_AND_CONDITIONS` 会跳过首次运行的对话框。“Create free Cloud database”链接到与 Redis Cloud 页面相同的免费方案。 <small>2026-11-07 截图，Redis Insight 3.8.0，本地 Redis 8.10.3。</small>

<p class="shot"><img src="{{ '/assets/img/setup/02-insight-browser.webp' | relative_url }}" width="1440" height="765" alt="Insight 的 Browse 视图，按类型列出键：sorted set、vector set、top-k、list、stream、array" loading="lazy" decoding="async"></p>

完成数据类型之旅后的 Browse：键按前缀分组，每个键都标有类型。最新的原生类型 ARRAY 和 VECTOR SET 有各自的标签。 <small>2026-11-07 截图，Redis Insight 3.8.0，本地 Redis 8.10.3。</small>

<p class="shot"><img src="{{ '/assets/img/setup/03-insight-json-key.webp' | relative_url }}" width="1440" height="765" alt="在 Insight 中打开的 JSON 键 user:1 及其字段" loading="lazy" decoding="async"></p>

JSON 键以树形展开；“Make searchable”可以为它创建 Search 索引。 <small>2026-11-07 截图，Redis Insight 3.8.0，本地 Redis 8.10.3。</small>

<p class="shot"><img src="{{ '/assets/img/setup/04-insight-workbench.webp' | relative_url }}" width="1440" height="765" alt="Workbench 运行 FT.SEARCH，匹配到一个文档" loading="lazy" decoding="async"></p>

Workbench 可以运行命令，并把 Search 结果显示为表格；它自带搜索和向量搜索的教程。 <small>2026-11-07 截图，Redis Insight 3.8.0，本地 Redis 8.10.3。</small>

### 客户端和云数据库

`smoke.py` 和 `smoke.mjs` 对两个目标执行 PING、SET/GET 并读取服务器版本；云数据库的 URL 来自被 gitignore 的 `.env`。

| 客户端 | 本地容器 | Redis Cloud 免费数据库 |
|---|---|---|
| redis-py 6.1.1 | PING True，版本 8.10.3 | PING True，版本 8.6.2 |
| node-redis 6.3.1 | PONG，版本 8.10.3 | PONG，版本 8.6.2 |
| `redis-cli -u`（8.10.3 镜像） | PONG | PONG |

**免费方案不支持 TLS。** 通过 REST API 开启时失败，返回 `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`（"Selected subscription plan does not support database 'enableTls'"），因此云端冒烟测试使用明文 TCP。免费数据库中只放测试数据。

### 实验：镜像运行的内容与 io-threads

**已在 Redis 8.10.3 上验证，2026-11-07。** 在容器内运行 `redis-benchmark`，SET/GET，64 字节的值，24 核主机：

| 服务器 | 4 个客户端线程 | 8 个客户端线程 |
|---|---|---|
| `io-threads 1`（默认） | 121,021–124,922 req/s | 117,405–126,687 req/s |
| `io-threads 4` | 285,144–285,225 req/s | 332,945–347,403 req/s |

使用 4 个客户端线程时，io-threads 4 的数值每次运行都相同：瓶颈在客户端，改用 8 个客户端线程后数值上升。服务器和客户端在同一台机器上，所以请把这些数字当作该机器上的测量结果，而不是通用规律。

### 实验：每种数据类型一条命令

**已在 Redis 8.10.3 上验证，2026-11-07。** `local/02-data-types-tour/tour.sh` 在原版镜像上为每种类型运行一条命令，全部没有报错：

| 类型 | 命令展示的内容 |
|---|---|
| String | 对页面计数器执行 `INCR` |
| Hash | 对一个字段执行 `HEXPIRE`；`HTTL` 对该字段显示 60，对另一个字段显示 -1 |
| List, Set, Sorted set | 队列、成员关系、排行榜 |
| Stream | `XADD`、消费者组、`XREADGROUP` |
| Geo | 首尔市政厅 5 km 范围内的商店 |
| Bitmap, HyperLogLog | 每日活跃位、去重计数 |
| JSON | 向文档内的数组追加元素 |
| Time series | 按 2 小时分桶求平均的样本 |
| Bloom, Top-k | 是否见过的检查、出现最频繁的项 |
| Array (8.8) | 稀疏：写入索引 0–2 和 1000 后 `ARLEN` 为 1001；`ARSCAN` 返回四个 |
| Vector set (beta) | 用 `VSIM` 查找最近邻 |
| Search | 在 hash 上执行 `FT.CREATE`，然后进行数值范围查询 |

**其他概率型数据类型**（`local/02-data-types-tour/probabilistic.sh`）。一个 56 KB 的 count-min sketch 对检查过的页面精确统计了 100,000 次浏览（10,000、91、99、0）。与 Bloom 不同，cuckoo filter 可以删除一个条目，对 10,000 个不存在的用户，误报率为 0.69%。一个 10 KB 的 t-digest 给出的中位数和 p99.9 误差在 1% 以内，但 p99 为 325 ms，而精确值是 257 ms，这是数据出现跳变、点很少的区间。

### 实验：搜索与向量搜索

**已在 Redis 8.10.3 上验证，2026-11-07。** `local/03-search-vector/lab.py` 将本站的 30 条单行笔记分别以 hash 和 JSON 形式建立索引，并使用一个小型开源模型在本地生成嵌入（无需 API key）。

| 查询 | 返回结果 |
|---|---|
| 全文 `failover`，标签 `{memory}`，数值 `[-inf 2025]` | 匹配的笔记 |
| 全文 `cache in sync with my database` | 无结果：每个词都必须出现 |
| KNN "How do I keep Redis in sync with my Postgres tables?" | 变更数据捕获（change data capture）笔记排在第一（相似度 0.83） |
| 以 `(@category:{cluster})` 作为过滤条件的 KNN | 只有 cluster 笔记 |
| `FT.HYBRID`（8.4+），文本加向量，`COMBINE RRF` | 两个列表的并集，各自的第一名排在最前 |
| Vector set：用 `VADD` 写入同样的向量，再用 `VSIM` | 与 KNN 相同的前 3 名，无需声明索引 |

redis-py 8.1.0 协商使用了 RESP3，因此 `FT.SEARCH` 的回复以 map 形式到达，而不是旧示例所解析的扁平列表。文档：[Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/)、[FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/)、[Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/)。实验：[`local/03-search-vector`](https://github.com/litkhai/notes-on-redis/tree/main/local/03-search-vector)。

**更多搜索功能**（`extras.py`）。`FT.AGGREGATE` 完成了分组和计算；同义词让 "switchover" 在后台重新扫描完成后能找到 failover 笔记；`FT.SPELLCHECK` 针对拼写错误建议了 `failover`、`eviction` 和 `replica`；`FLOAT16`、`INT8` 以及带 `LVQ8` 的 `SVS-VAMANA` 返回的前 3 名与 `FLOAT32` 相同。韩语问题只有使用多语言模型才能找到正确的英文笔记，而且并非每个问题都能找到。

### 尚未涵盖

Redis Insight 桌面版（Docker 镜像是同一个应用），以及 redis-py 和 node-redis 之外的客户端。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

**ローカルの Redis 8 と無料のクラウドデータベースは、どちらも Python と Node から応答する。** 2026-11-07 に実行：Docker 上の Redis Open Source 8.10.3 と Redis Insight 3.8.0、`redis-cli`、redis-py 6.1.1、node-redis 6.3.1、そして [Redis Cloud ページ]({{ '/cloud/' | relative_url }})の Redis Cloud 無料データベース。ソース：[`setup/`](https://github.com/litkhai/notes-on-redis/tree/main/setup), [`local/01`](https://github.com/litkhai/notes-on-redis/tree/main/local/01-redis-8-docker), [`local/02`](https://github.com/litkhai/notes-on-redis/tree/main/local/02-data-types-tour)。

### ローカル環境

compose ファイル 1 つで 2 つのコンテナを起動する。ホストのポートはデフォルトではなく 16379 と 15540 を使うので、Docker ホストを他と共有できる。

```bash
cd setup && docker compose up -d
docker exec -it nor-redis8 redis-cli PING        # PONG
```

2026-11-07 時点で `redis:latest`、`redis:8`、`redis:8.10.3` は同じ digest だった。compose ファイルは `8.10.3` に固定している。イメージには設定ファイルがない。エントリポイントが `/usr/local/lib/redis/modules/` 内のモジュールごとに `--loadmodule` を追加するため、Search、JSON、Time series、Bloom は最初から使え、Vector set は組み込みである。

**さらに多くのクライアント**（`go/`、`java/`）。go-redis 9.23.0（Go 1.26 が必要）と Jedis 8.0.2 は、どちらも `redis://` URL で両方のサーバーに接続できた。go-redis は RESP3 をネゴシエートした。`RedisProtocol.RESP3` と `CacheConfig` を指定した Jedis は、redis-py のクライアントサイドキャッシュと同じく、1,001 回の読み取りに対して GET を 1 回だけ送った。

### Redis Insight

<p class="shot"><img src="{{ '/assets/img/setup/01-insight-databases.webp' | relative_url }}" width="1440" height="765" alt="local-redis-8 が登録された Redis Insight のデータベース一覧" loading="lazy" decoding="async"></p>

compose ファイルの `RI_REDIS_*` 変数は、Insight の起動時にローカルデータベースを登録する。`RI_ACCEPT_TERMS_AND_CONDITIONS` は初回起動のダイアログを省略する。「Create free Cloud database」は Redis Cloud ページと同じ無料プランにつながる。 <small>2026-11-07 取得、Redis Insight 3.8.0、ローカル Redis 8.10.3。</small>

<p class="shot"><img src="{{ '/assets/img/setup/02-insight-browser.webp' | relative_url }}" width="1440" height="765" alt="型ごとにキーを一覧表示する Insight の Browse ビュー：sorted set、vector set、top-k、list、stream、array" loading="lazy" decoding="async"></p>

データ型ツアーの後の Browse：キーはプレフィックスごとにまとめられ、それぞれに型が表示される。最も新しいネイティブ型である ARRAY と VECTOR SET には専用のラベルがある。 <small>2026-11-07 取得、Redis Insight 3.8.0、ローカル Redis 8.10.3。</small>

<p class="shot"><img src="{{ '/assets/img/setup/03-insight-json-key.webp' | relative_url }}" width="1440" height="765" alt="フィールドが表示された JSON キー user:1 を開いた Insight" loading="lazy" decoding="async"></p>

JSON キーはツリーとして開く。「Make searchable」を使うと、その上に Search インデックスを作成できる。 <small>2026-11-07 取得、Redis Insight 3.8.0、ローカル Redis 8.10.3。</small>

<p class="shot"><img src="{{ '/assets/img/setup/04-insight-workbench.webp' | relative_url }}" width="1440" height="765" alt="FT.SEARCH を実行し、1 件のドキュメントに一致した Workbench" loading="lazy" decoding="async"></p>

Workbench はコマンドを実行し、Search の結果を表として表示する。検索とベクトル検索のチュートリアルが付属している。 <small>2026-11-07 取得、Redis Insight 3.8.0、ローカル Redis 8.10.3。</small>

### クライアントとクラウドデータベース

`smoke.py` と `smoke.mjs` は両方の対象に対して PING と SET/GET を実行し、サーバーのバージョンを読み取る。クラウドの URL は gitignore 済みの `.env` から取得する。

| クライアント | ローカルコンテナ | Redis Cloud 無料データベース |
|---|---|---|
| redis-py 6.1.1 | PING True、バージョン 8.10.3 | PING True、バージョン 8.6.2 |
| node-redis 6.3.1 | PONG、バージョン 8.10.3 | PONG、バージョン 8.6.2 |
| `redis-cli -u`（8.10.3 イメージ） | PONG | PONG |

**無料プランには TLS がない。** REST API で有効にしようとすると `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`（"Selected subscription plan does not support database 'enableTls'"）で失敗したため、クラウドのスモークテストは平文の TCP で行っている。無料データベースにはテストデータだけを置くこと。

### ラボ：イメージが実行する内容と io-threads

**Redis 8.10.3 で確認、2026-11-07。** コンテナ内で `redis-benchmark` を実行、SET/GET、64 バイトの値、24 コアのホスト：

| サーバー | クライアントスレッド 4 | クライアントスレッド 8 |
|---|---|---|
| `io-threads 1`（デフォルト） | 121,021–124,922 req/s | 117,405–126,687 req/s |
| `io-threads 4` | 285,144–285,225 req/s | 332,945–347,403 req/s |

クライアントスレッド 4 では、io-threads 4 の値はどの実行でも同じだった。限界はクライアント側にあり、クライアントスレッドを 8 にすると上がった。サーバーとクライアントは同じマシンにあるため、この数値はそのマシンでの測定値として読み、一般的な規則とは考えないこと。

### ラボ：データ型ごとにコマンド 1 つ

**Redis 8.10.3 で確認、2026-11-07。** `local/02-data-types-tour/tour.sh` は標準イメージ上で型ごとにコマンドを 1 つ実行し、すべてエラーなしで終わった：

| 型 | コマンドが示すこと |
|---|---|
| String | ページカウンターに `INCR` |
| Hash | 1 つのフィールドに `HEXPIRE`。`HTTL` はそのフィールドで 60、もう一方で -1 を返す |
| List, Set, Sorted set | キュー、所属判定、リーダーボード |
| Stream | `XADD`、コンシューマーグループ、`XREADGROUP` |
| Geo | ソウル市庁から 5 km 以内の店 |
| Bitmap, HyperLogLog | 日次アクティブのビット、ユニーク数 |
| JSON | ドキュメント内の配列に追加 |
| Time series | サンプルを 2 時間のバケットで平均 |
| Bloom, Top-k | 既出チェック、最頻出の項目 |
| Array (8.8) | スパース：インデックス 0–2 と 1000 を書き込むと `ARLEN` は 1001、`ARSCAN` は 4 件を返す |
| Vector set (beta) | `VSIM` による最近傍検索 |
| Search | ハッシュに対して `FT.CREATE`、続いて数値範囲クエリ |

**そのほかの確率的データ型**（`local/02-data-types-tour/probabilistic.sh`）。56 KB の count-min sketch は、確認したページについて 100,000 件のページビューを正確に数えた（10,000、91、99、0）。Cuckoo filter は Bloom と違って項目を削除でき、存在しないユーザー 10,000 人に対する偽陽性率は 0.69% だった。10 KB の t-digest は中央値と p99.9 を 1% 以内で示したが、p99 は正確な値 257 ms に対して 325 ms だった。データが飛んでいて点が少ない区間である。

### ラボ：検索とベクトル検索

**Redis 8.10.3 で確認、2026-11-07。** `local/03-search-vector/lab.py` は、このサイトの 1 行ノート 30 件をハッシュと JSON の両方でインデックスし、小さなオープンモデルでローカルに埋め込みを作成する（API キー不要）。

| クエリ | 返ってきたもの |
|---|---|
| 全文 `failover`、タグ `{memory}`、数値 `[-inf 2025]` | 一致したノート |
| 全文 `cache in sync with my database` | 何も返らない：すべての語が含まれている必要がある |
| KNN "How do I keep Redis in sync with my Postgres tables?" | 変更データキャプチャ（change data capture）のノートが先頭（類似度 0.83） |
| `(@category:{cluster})` をフィルターにした KNN | cluster のノートだけ |
| `FT.HYBRID`（8.4+）、テキストとベクトル、`COMBINE RRF` | 両方のリストの和集合で、それぞれの先頭が上位に来る |
| Vector set：同じベクトルを `VADD` して `VSIM` | KNN と同じ上位 3 件。インデックスの宣言は不要 |

redis-py 8.1.0 は RESP3 をネゴシエートしたため、`FT.SEARCH` の応答は、古い例がパースするフラットなリストではなくマップで届いた。ドキュメント：[Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/)、[FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/)、[Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/)。ラボ：[`local/03-search-vector`](https://github.com/litkhai/notes-on-redis/tree/main/local/03-search-vector)。

**さらに多くの検索機能**（`extras.py`）。`FT.AGGREGATE` はグループ化と計算ができた。同義語により、バックグラウンドの再スキャンが終わると "switchover" で failover のノートが見つかった。`FT.SPELLCHECK` は綴りの誤りに対して `failover`、`eviction`、`replica` を提案した。`FLOAT16`、`INT8`、そして `LVQ8` 付きの `SVS-VAMANA` は、`FLOAT32` と同じ上位 3 件を返した。韓国語の質問で正しい英語のノートが見つかったのは多言語モデルを使った場合だけで、すべての質問で見つかったわけではない。

### まだ扱っていないこと

Redis Insight デスクトップ版（Docker イメージは同じアプリケーション）と、redis-py と node-redis 以外のクライアント。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

**Redis 8 ในเครื่องและฐานข้อมูลคลาวด์ฟรี ตอบสนองได้ทั้งจาก Python และ Node** รันเมื่อ 2026-11-07: Redis Open Source 8.10.3 และ Redis Insight 3.8.0 ใน Docker, `redis-cli`, redis-py 6.1.1 และ node-redis 6.3.1 รวมถึงฐานข้อมูลฟรีของ Redis Cloud จาก[หน้า Redis Cloud]({{ '/cloud/' | relative_url }}) ซอร์ส: [`setup/`](https://github.com/litkhai/notes-on-redis/tree/main/setup), [`local/01`](https://github.com/litkhai/notes-on-redis/tree/main/local/01-redis-8-docker), [`local/02`](https://github.com/litkhai/notes-on-redis/tree/main/local/02-data-types-tour)

### สแตกในเครื่อง

ไฟล์ compose ไฟล์เดียวเริ่มคอนเทนเนอร์ทั้งสองตัว พอร์ตของโฮสต์คือ 16379 และ 15540 แทนค่าเริ่มต้น เพื่อให้สแตกนี้ใช้โฮสต์ Docker ร่วมกับงานอื่นได้

```bash
cd setup && docker compose up -d
docker exec -it nor-redis8 redis-cli PING        # PONG
```

เมื่อ 2026-11-07 `redis:latest`, `redis:8` และ `redis:8.10.3` มี digest เดียวกัน ไฟล์ compose ปักหมุดไว้ที่ `8.10.3` อิมเมจไม่มีไฟล์คอนฟิก: entrypoint จะเพิ่ม `--loadmodule` ให้ทุกโมดูลใน `/usr/local/lib/redis/modules/` จึงมี Search, JSON, Time series และ Bloom ตั้งแต่เริ่มต้น และ Vector set ถูกสร้างไว้ในตัวอยู่แล้ว

**ไคลเอนต์เพิ่มเติม** (`go/`, `java/`) go-redis 9.23.0 (ต้องใช้ Go 1.26) และ Jedis 8.0.2 เชื่อมต่อกับเซิร์ฟเวอร์ทั้งสองด้วย URL แบบ `redis://` โดย go-redis เจรจาใช้ RESP3 ส่วน Jedis ที่ใช้ `RedisProtocol.RESP3` และ `CacheConfig` ส่ง GET เพียงครั้งเดียวสำหรับการอ่าน 1,001 ครั้ง เหมือน client-side cache ของ redis-py

### Redis Insight

<p class="shot"><img src="{{ '/assets/img/setup/01-insight-databases.webp' | relative_url }}" width="1440" height="765" alt="รายการฐานข้อมูลของ Redis Insight ที่ลงทะเบียน local-redis-8 แล้ว" loading="lazy" decoding="async"></p>

ตัวแปร `RI_REDIS_*` ในไฟล์ compose จะลงทะเบียนฐานข้อมูลในเครื่องเมื่อ Insight เริ่มทำงาน ส่วน `RI_ACCEPT_TERMS_AND_CONDITIONS` จะข้ามกล่องข้อความของการเปิดใช้ครั้งแรก "Create free Cloud database" ลิงก์ไปยังแผนฟรีเดียวกับหน้า Redis Cloud <small>บันทึกเมื่อ 2026-11-07, Redis Insight 3.8.0, Redis ในเครื่อง 8.10.3</small>

<p class="shot"><img src="{{ '/assets/img/setup/02-insight-browser.webp' | relative_url }}" width="1440" height="765" alt="มุมมอง Browse ของ Insight ที่แสดงคีย์ตามชนิด: sorted set, vector set, top-k, list, stream, array" loading="lazy" decoding="async"></p>

Browse หลังจากทัวร์ชนิดข้อมูล: คีย์ถูกจัดกลุ่มตามพรีฟิกซ์ และแต่ละคีย์แสดงชนิดของตัวเอง ARRAY และ VECTOR SET ซึ่งเป็นชนิดเนทีฟใหม่ล่าสุดมีป้ายกำกับของตัวเอง <small>บันทึกเมื่อ 2026-11-07, Redis Insight 3.8.0, Redis ในเครื่อง 8.10.3</small>

<p class="shot"><img src="{{ '/assets/img/setup/03-insight-json-key.webp' | relative_url }}" width="1440" height="765" alt="คีย์ JSON user:1 ที่เปิดใน Insight พร้อมฟิลด์ของมัน" loading="lazy" decoding="async"></p>

คีย์ JSON จะเปิดเป็นแบบต้นไม้ "Make searchable" ช่วยสร้างดัชนี Search บนคีย์นั้น <small>บันทึกเมื่อ 2026-11-07, Redis Insight 3.8.0, Redis ในเครื่อง 8.10.3</small>

<p class="shot"><img src="{{ '/assets/img/setup/04-insight-workbench.webp' | relative_url }}" width="1440" height="765" alt="Workbench ที่รัน FT.SEARCH และพบเอกสารที่ตรงกันหนึ่งรายการ" loading="lazy" decoding="async"></p>

Workbench รันคำสั่งและแสดงผลลัพธ์ของ Search เป็นตาราง มีบทเรียนสำหรับการค้นหาและการค้นหาเวกเตอร์มาให้ในตัว <small>บันทึกเมื่อ 2026-11-07, Redis Insight 3.8.0, Redis ในเครื่อง 8.10.3</small>

### ไคลเอนต์และฐานข้อมูลคลาวด์

`smoke.py` และ `smoke.mjs` รัน PING, SET/GET และอ่านเวอร์ชันของเซิร์ฟเวอร์กับทั้งสองเป้าหมาย URL ของคลาวด์มาจากไฟล์ `.env` ที่ถูก gitignore

| ไคลเอนต์ | คอนเทนเนอร์ในเครื่อง | ฐานข้อมูลฟรีของ Redis Cloud |
|---|---|---|
| redis-py 6.1.1 | PING True, เวอร์ชัน 8.10.3 | PING True, เวอร์ชัน 8.6.2 |
| node-redis 6.3.1 | PONG, เวอร์ชัน 8.10.3 | PONG, เวอร์ชัน 8.6.2 |
| `redis-cli -u` (อิมเมจ 8.10.3) | PONG | PONG |

**แผนฟรีไม่มี TLS** การเปิดใช้ผ่าน REST API ล้มเหลวพร้อมข้อผิดพลาด `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN` ("Selected subscription plan does not support database 'enableTls'") ดังนั้นการทดสอบ smoke บนคลาวด์จึงใช้ TCP แบบไม่เข้ารหัส ให้เก็บเฉพาะข้อมูลทดสอบไว้ในฐานข้อมูลฟรี

### แล็บ: อิมเมจรันอะไร และ io-threads

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** รัน `redis-benchmark` ภายในคอนเทนเนอร์, SET/GET, ค่าขนาด 64 ไบต์, บนโฮสต์ 24 คอร์:

| เซิร์ฟเวอร์ | เธรดไคลเอนต์ 4 | เธรดไคลเอนต์ 8 |
|---|---|---|
| `io-threads 1` (ค่าเริ่มต้น) | 121,021–124,922 req/s | 117,405–126,687 req/s |
| `io-threads 4` | 285,144–285,225 req/s | 332,945–347,403 req/s |

เมื่อใช้เธรดไคลเอนต์ 4 ตัว ตัวเลขของ io-threads 4 เท่ากันทุกครั้งที่รัน: ไคลเอนต์เป็นขีดจำกัด และเมื่อใช้เธรดไคลเอนต์ 8 ตัวก็สูงขึ้น เซิร์ฟเวอร์และไคลเอนต์อยู่บนเครื่องเดียวกัน จึงควรอ่านตัวเลขเหล่านี้เป็นผลวัดบนเครื่องนั้น ไม่ใช่กฎทั่วไป

### แล็บ: หนึ่งคำสั่งต่อหนึ่งชนิดข้อมูล

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** `local/02-data-types-tour/tour.sh` รันหนึ่งคำสั่งต่อหนึ่งชนิดบนอิมเมจมาตรฐาน โดยไม่มีข้อผิดพลาดเลย:

| ชนิด | สิ่งที่คำสั่งแสดง |
|---|---|
| String | `INCR` ตัวนับหน้าเว็บ |
| Hash | `HEXPIRE` หนึ่งฟิลด์; `HTTL` แสดง 60 สำหรับฟิลด์นั้นและ -1 สำหรับอีกฟิลด์ |
| List, Set, Sorted set | คิว, การเป็นสมาชิก, อันดับคะแนน |
| Stream | `XADD`, consumer group, `XREADGROUP` |
| Geo | ร้านค้าในรัศมี 5 km จากศาลาว่าการกรุงโซล |
| Bitmap, HyperLogLog | บิตผู้ใช้งานรายวัน, จำนวนที่ไม่ซ้ำ |
| JSON | เพิ่มข้อมูลต่อท้ายอาร์เรย์ภายในเอกสาร |
| Time series | ค่าเฉลี่ยของตัวอย่างในช่วงละ 2 ชั่วโมง |
| Bloom, Top-k | การตรวจว่าเคยพบแล้วหรือไม่, รายการที่พบบ่อยที่สุด |
| Array (8.8) | แบบกระจัดกระจาย: `ARLEN` เป็น 1001 หลังเขียนดัชนี 0–2 และ 1000; `ARSCAN` คืนค่าสี่รายการ |
| Vector set (beta) | เพื่อนบ้านที่ใกล้ที่สุดด้วย `VSIM` |
| Search | `FT.CREATE` บน hash แล้วตามด้วยคิวรีช่วงตัวเลข |

**ชนิดข้อมูลเชิงความน่าจะเป็นอื่น ๆ** (`local/02-data-types-tour/probabilistic.sh`) count-min sketch ขนาด 56 KB นับการดูหน้า 100,000 ครั้งได้ตรงเป๊ะสำหรับหน้าที่ตรวจสอบ (10,000, 91, 99, 0) cuckoo filter ต่างจาก Bloom ตรงที่ลบรายการได้ โดยมีอัตราผลบวกลวง 0.69% จากผู้ใช้ที่ไม่มีอยู่จริง 10,000 คน t-digest ขนาด 10 KB ให้ค่ามัธยฐานและ p99.9 คลาดเคลื่อนไม่เกิน 1% แต่ p99 ได้ 325 ms เทียบกับค่าจริง 257 ms ซึ่งเป็นช่วงที่ข้อมูลกระโดดและมีจุดอยู่น้อย

### แล็บ: การค้นหาและการค้นหาเวกเตอร์

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** `local/03-search-vector/lab.py` สร้างดัชนีโน้ตหนึ่งบรรทัดจำนวน 30 รายการจากไซต์นี้ทั้งแบบ hash และ JSON โดยสร้าง embedding ในเครื่องด้วยโมเดลโอเพนขนาดเล็ก (ไม่ต้องใช้ API key)

| คิวรี | ผลลัพธ์ที่ได้ |
|---|---|
| ข้อความเต็ม `failover`, แท็ก `{memory}`, ตัวเลข `[-inf 2025]` | โน้ตที่ตรงกัน |
| ข้อความเต็ม `cache in sync with my database` | ไม่ได้อะไรเลย: ทุกคำต้องปรากฏ |
| KNN "How do I keep Redis in sync with my Postgres tables?" | โน้ตเรื่อง change data capture มาเป็นอันดับแรก (ความคล้าย 0.83) |
| KNN โดยใช้ `(@category:{cluster})` เป็นตัวกรอง | เฉพาะโน้ตของ cluster |
| `FT.HYBRID` (8.4+), ข้อความรวมกับเวกเตอร์, `COMBINE RRF` | ยูเนียนของทั้งสองลิสต์ โดยอันดับแรกของแต่ละลิสต์อยู่บนสุด |
| Vector set: `VADD` เวกเตอร์ชุดเดียวกัน แล้ว `VSIM` | 3 อันดับแรกเหมือน KNN โดยไม่ต้องประกาศดัชนี |

redis-py 8.1.0 เจรจาใช้ RESP3 ดังนั้นการตอบกลับของ `FT.SEARCH` จึงมาเป็น map ไม่ใช่ลิสต์แบบแบนที่ตัวอย่างรุ่นเก่าแยกวิเคราะห์ เอกสาร: [Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/), [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/) Lab: [`local/03-search-vector`](https://github.com/litkhai/notes-on-redis/tree/main/local/03-search-vector)

**ฟีเจอร์ค้นหาเพิ่มเติม** (`extras.py`) `FT.AGGREGATE` จัดกลุ่มและคำนวณได้ ส่วน synonym ทำให้ "switchover" ค้นเจอโน้ตเรื่อง failover เมื่อการสแกนใหม่เบื้องหลังเสร็จสิ้น `FT.SPELLCHECK` แนะนำ `failover`, `eviction` และ `replica` สำหรับคำที่สะกดผิด `FLOAT16`, `INT8` และ `SVS-VAMANA` กับ `LVQ8` คืน 3 อันดับแรกเหมือนกับ `FLOAT32` คำถามภาษาเกาหลีค้นเจอโน้ตภาษาอังกฤษที่ถูกต้องเฉพาะเมื่อใช้โมเดลหลายภาษา และไม่ใช่กับทุกคำถาม

### ยังไม่ครอบคลุม

Redis Insight เวอร์ชันเดสก์ท็อป (อิมเมจ Docker เป็นแอปพลิเคชันเดียวกัน) และไคลเอนต์อื่นนอกเหนือจาก redis-py และ node-redis

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

**Redis 8 lokal dan basis data cloud gratis, keduanya menjawab dari Python dan Node.** Dijalankan pada 2026-11-07: Redis Open Source 8.10.3 dan Redis Insight 3.8.0 di Docker, `redis-cli`, redis-py 6.1.1 dan node-redis 6.3.1, serta basis data gratis Redis Cloud dari [halaman Redis Cloud]({{ '/cloud/' | relative_url }}). Sumber: [`setup/`](https://github.com/litkhai/notes-on-redis/tree/main/setup), [`local/01`](https://github.com/litkhai/notes-on-redis/tree/main/local/01-redis-8-docker), [`local/02`](https://github.com/litkhai/notes-on-redis/tree/main/local/02-data-types-tour).

### Stack lokal

Satu berkas compose menjalankan kedua kontainer. Port host adalah 16379 dan 15540, bukan port bawaan, sehingga stack ini dapat berbagi host Docker dengan layanan lain.

```bash
cd setup && docker compose up -d
docker exec -it nor-redis8 redis-cli PING        # PONG
```

Pada 2026-11-07, `redis:latest`, `redis:8`, dan `redis:8.10.3` memiliki digest yang sama; berkas compose menetapkan `8.10.3`. Image tidak memiliki berkas konfigurasi: entrypoint-nya menambahkan `--loadmodule` untuk setiap modul di `/usr/local/lib/redis/modules/`, sehingga Search, JSON, Time series, dan Bloom sudah tersedia sejak awal, dan Vector set sudah bawaan.

**Klien lainnya** (`go/`, `java/`). go-redis 9.23.0 (membutuhkan Go 1.26) dan Jedis 8.0.2 terhubung ke kedua server dengan URL `redis://`; go-redis menegosiasikan RESP3. Jedis dengan `RedisProtocol.RESP3` dan `CacheConfig` mengirim satu GET untuk 1,001 pembacaan, seperti client-side cache milik redis-py.

### Redis Insight

<p class="shot"><img src="{{ '/assets/img/setup/01-insight-databases.webp' | relative_url }}" width="1440" height="765" alt="Daftar basis data Redis Insight dengan local-redis-8 terdaftar" loading="lazy" decoding="async"></p>

Variabel `RI_REDIS_*` di berkas compose mendaftarkan basis data lokal saat Insight dimulai; `RI_ACCEPT_TERMS_AND_CONDITIONS` melewati dialog saat pertama kali dijalankan. "Create free Cloud database" mengarah ke paket gratis yang sama dengan halaman Redis Cloud. <small>Diambil 2026-11-07, Redis Insight 3.8.0, Redis lokal 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/02-insight-browser.webp' | relative_url }}" width="1440" height="765" alt="Tampilan Browse Insight yang mencantumkan key menurut tipe: sorted set, vector set, top-k, list, stream, array" loading="lazy" decoding="async"></p>

Browse setelah tur tipe data: key dikelompokkan menurut prefiks, masing-masing dengan tipenya. ARRAY dan VECTOR SET, tipe native terbaru, mendapat label sendiri. <small>Diambil 2026-11-07, Redis Insight 3.8.0, Redis lokal 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/03-insight-json-key.webp' | relative_url }}" width="1440" height="765" alt="Key JSON user:1 dibuka di Insight beserta field-nya" loading="lazy" decoding="async"></p>

Key JSON terbuka sebagai pohon; "Make searchable" menawarkan pembuatan indeks Search di atasnya. <small>Diambil 2026-11-07, Redis Insight 3.8.0, Redis lokal 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/04-insight-workbench.webp' | relative_url }}" width="1440" height="765" alt="Workbench menjalankan FT.SEARCH dengan satu dokumen yang cocok" loading="lazy" decoding="async"></p>

Workbench menjalankan perintah dan menampilkan hasil Search sebagai tabel; tersedia tutorial untuk pencarian dan pencarian vektor. <small>Diambil 2026-11-07, Redis Insight 3.8.0, Redis lokal 8.10.3.</small>

### Klien dan basis data cloud

`smoke.py` dan `smoke.mjs` menjalankan PING, SET/GET, dan membaca versi server pada kedua target; URL cloud berasal dari `.env` yang di-gitignore.

| Klien | Kontainer lokal | Basis data gratis Redis Cloud |
|---|---|---|
| redis-py 6.1.1 | PING True, versi 8.10.3 | PING True, versi 8.6.2 |
| node-redis 6.3.1 | PONG, versi 8.10.3 | PONG, versi 8.6.2 |
| `redis-cli -u` (image 8.10.3) | PONG | PONG |

**Paket gratis tidak memiliki TLS.** Mengaktifkannya melalui REST API gagal dengan `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN` ("Selected subscription plan does not support database 'enableTls'"), sehingga smoke test cloud menggunakan TCP biasa. Simpan hanya data uji di basis data gratis.

### Lab: apa yang dijalankan image, dan io-threads

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** `redis-benchmark` di dalam kontainer, SET/GET, nilai 64 byte, pada host 24 core:

| Server | 4 thread klien | 8 thread klien |
|---|---|---|
| `io-threads 1` (bawaan) | 121,021–124,922 req/s | 117,405–126,687 req/s |
| `io-threads 4` | 285,144–285,225 req/s | 332,945–347,403 req/s |

Dengan 4 thread klien, angka io-threads 4 sama pada setiap kali dijalankan: klien menjadi batasnya, dan 8 thread klien menaikkannya. Server dan klien berada pada satu mesin, jadi baca angka ini sebagai hasil pengukuran pada mesin tersebut, bukan sebagai aturan umum.

### Lab: satu perintah per tipe data

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** `local/02-data-types-tour/tour.sh` menjalankan satu perintah per tipe pada image bawaan, semuanya tanpa error:

| Tipe | Yang ditunjukkan perintah |
|---|---|
| String | `INCR` pada penghitung halaman |
| Hash | `HEXPIRE` pada satu field; `HTTL` menunjukkan 60 untuk field itu dan -1 untuk yang lain |
| List, Set, Sorted set | antrean, keanggotaan, papan peringkat |
| Stream | `XADD`, consumer group, `XREADGROUP` |
| Geo | toko dalam radius 5 km dari Balai Kota Seoul |
| Bitmap, HyperLogLog | bit aktif harian, jumlah unik |
| JSON | menambahkan ke array di dalam dokumen |
| Time series | sampel dirata-ratakan ke dalam bucket 2 jam |
| Bloom, Top-k | pemeriksaan pernah terlihat, item paling sering |
| Array (8.8) | jarang (sparse): `ARLEN` 1001 setelah menulis indeks 0–2 dan 1000; `ARSCAN` mengembalikan empat |
| Vector set (beta) | tetangga terdekat dengan `VSIM` |
| Search | `FT.CREATE` pada hash, lalu kueri rentang numerik |

**Tipe probabilistik lainnya** (`local/02-data-types-tour/probabilistic.sh`). Count-min sketch sebesar 56 KB menghitung 100.000 tayangan halaman secara persis untuk halaman yang diperiksa (10.000, 91, 99, 0). Cuckoo filter, tidak seperti Bloom, dapat menghapus sebuah item, dengan tingkat positif palsu 0,69% pada 10.000 pengguna yang tidak ada. T-digest sebesar 10 KB memberikan median dan p99.9 dengan selisih dalam 1%, tetapi p99 sebesar 325 ms dibandingkan nilai persis 257 ms, di rentang tempat data melompat dan hanya sedikit titik.

### Lab: pencarian dan pencarian vektor

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** `local/03-search-vector/lab.py` mengindeks 30 catatan satu baris dari situs ini sebagai hash dan sebagai JSON, dengan embedding yang dibuat secara lokal memakai model terbuka kecil (tanpa API key).

| Kueri | Yang dikembalikan |
|---|---|
| Teks penuh `failover`, tag `{memory}`, numerik `[-inf 2025]` | catatan yang cocok |
| Teks penuh `cache in sync with my database` | tidak ada: setiap kata harus muncul |
| KNN "How do I keep Redis in sync with my Postgres tables?" | catatan change data capture di urutan pertama (kemiripan 0,83) |
| KNN dengan `(@category:{cluster})` sebagai filter | hanya catatan cluster |
| `FT.HYBRID` (8.4+), teks plus vektor, `COMBINE RRF` | gabungan kedua daftar, yang pertama dari masing-masing di atas |
| Vector set: `VADD` vektor yang sama, `VSIM` | 3 teratas yang sama dengan KNN, tanpa mendeklarasikan indeks |

redis-py 8.1.0 menegosiasikan RESP3, sehingga balasan `FT.SEARCH` tiba sebagai map, bukan daftar datar yang di-parse contoh-contoh lama. Dokumentasi: [Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/), [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/). Lab: [`local/03-search-vector`](https://github.com/litkhai/notes-on-redis/tree/main/local/03-search-vector).

**Fitur pencarian lainnya** (`extras.py`). `FT.AGGREGATE` mengelompokkan dan menghitung; sinonim membuat "switchover" menemukan catatan failover setelah pemindaian ulang di latar belakang selesai; `FT.SPELLCHECK` menyarankan `failover`, `eviction` dan `replica` untuk salah ketik; `FLOAT16`, `INT8` dan `SVS-VAMANA` dengan `LVQ8` mengembalikan 3 teratas yang sama seperti `FLOAT32`. Pertanyaan berbahasa Korea menemukan catatan bahasa Inggris yang benar hanya dengan model multibahasa, dan tidak untuk setiap pertanyaan.

### Belum dibahas

Redis Insight desktop (image Docker adalah aplikasi yang sama) dan klien selain redis-py dan node-redis.

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

**Redis 8 tempatan dan pangkalan data awan percuma, kedua-duanya memberi respons daripada Python dan Node.** Dijalankan pada 2026-11-07: Redis Open Source 8.10.3 dan Redis Insight 3.8.0 dalam Docker, `redis-cli`, redis-py 6.1.1 dan node-redis 6.3.1, serta pangkalan data percuma Redis Cloud daripada [halaman Redis Cloud]({{ '/cloud/' | relative_url }}). Sumber: [`setup/`](https://github.com/litkhai/notes-on-redis/tree/main/setup), [`local/01`](https://github.com/litkhai/notes-on-redis/tree/main/local/01-redis-8-docker), [`local/02`](https://github.com/litkhai/notes-on-redis/tree/main/local/02-data-types-tour).

### Tindanan tempatan

Satu fail compose memulakan kedua-dua kontena. Port hos ialah 16379 dan 15540, bukan port lalai, supaya tindanan ini boleh berkongsi hos Docker dengan perkhidmatan lain.

```bash
cd setup && docker compose up -d
docker exec -it nor-redis8 redis-cli PING        # PONG
```

Pada 2026-11-07, `redis:latest`, `redis:8` dan `redis:8.10.3` mempunyai digest yang sama; fail compose menetapkan `8.10.3`. Imej tiada fail konfigurasi: entrypoint menambah `--loadmodule` untuk setiap modul dalam `/usr/local/lib/redis/modules/`, jadi Search, JSON, Time series dan Bloom sedia ada sejak awal, dan Vector set terbina dalam.

**Lebih banyak klien** (`go/`, `java/`). go-redis 9.23.0 (memerlukan Go 1.26) dan Jedis 8.0.2 bersambung ke kedua-dua pelayan dengan URL `redis://`; go-redis merundingkan RESP3. Jedis dengan `RedisProtocol.RESP3` dan `CacheConfig` menghantar satu GET untuk 1,001 bacaan, seperti client-side cache milik redis-py.

### Redis Insight

<p class="shot"><img src="{{ '/assets/img/setup/01-insight-databases.webp' | relative_url }}" width="1440" height="765" alt="Senarai pangkalan data Redis Insight dengan local-redis-8 didaftarkan" loading="lazy" decoding="async"></p>

Pemboleh ubah `RI_REDIS_*` dalam fail compose mendaftarkan pangkalan data tempatan apabila Insight bermula; `RI_ACCEPT_TERMS_AND_CONDITIONS` melangkau dialog larian pertama. "Create free Cloud database" memaut ke pelan percuma yang sama dengan halaman Redis Cloud. <small>Dirakam 2026-11-07, Redis Insight 3.8.0, Redis tempatan 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/02-insight-browser.webp' | relative_url }}" width="1440" height="765" alt="Paparan Browse Insight yang menyenaraikan kunci mengikut jenis: sorted set, vector set, top-k, list, stream, array" loading="lazy" decoding="async"></p>

Browse selepas lawatan jenis data: kunci dikumpulkan mengikut awalan, setiap satu dengan jenisnya. ARRAY dan VECTOR SET, jenis natif terbaharu, mendapat label tersendiri. <small>Dirakam 2026-11-07, Redis Insight 3.8.0, Redis tempatan 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/03-insight-json-key.webp' | relative_url }}" width="1440" height="765" alt="Kunci JSON user:1 dibuka dalam Insight bersama medannya" loading="lazy" decoding="async"></p>

Kunci JSON dibuka sebagai pepohon; "Make searchable" menawarkan pembuatan indeks Search di atasnya. <small>Dirakam 2026-11-07, Redis Insight 3.8.0, Redis tempatan 8.10.3.</small>

<p class="shot"><img src="{{ '/assets/img/setup/04-insight-workbench.webp' | relative_url }}" width="1440" height="765" alt="Workbench menjalankan FT.SEARCH dengan satu dokumen yang sepadan" loading="lazy" decoding="async"></p>

Workbench menjalankan arahan dan memaparkan hasil Search sebagai jadual; ia disertakan dengan tutorial untuk carian dan carian vektor. <small>Dirakam 2026-11-07, Redis Insight 3.8.0, Redis tempatan 8.10.3.</small>

### Klien dan pangkalan data awan

`smoke.py` dan `smoke.mjs` menjalankan PING, SET/GET dan membaca versi pelayan pada kedua-dua sasaran; URL awan datang daripada `.env` yang di-gitignore.

| Klien | Kontena tempatan | Pangkalan data percuma Redis Cloud |
|---|---|---|
| redis-py 6.1.1 | PING True, versi 8.10.3 | PING True, versi 8.6.2 |
| node-redis 6.3.1 | PONG, versi 8.10.3 | PONG, versi 8.6.2 |
| `redis-cli -u` (imej 8.10.3) | PONG | PONG |

**Pelan percuma tiada TLS.** Mengaktifkannya melalui REST API gagal dengan `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN` ("Selected subscription plan does not support database 'enableTls'"), jadi ujian asap awan menggunakan TCP biasa. Simpan data ujian sahaja dalam pangkalan data percuma.

### Makmal: apa yang dijalankan imej, dan io-threads

**Disahkan pada Redis 8.10.3, 2026-11-07.** `redis-benchmark` di dalam kontena, SET/GET, nilai 64 bait, pada hos 24 teras:

| Pelayan | 4 thread klien | 8 thread klien |
|---|---|---|
| `io-threads 1` (lalai) | 121,021–124,922 req/s | 117,405–126,687 req/s |
| `io-threads 4` | 285,144–285,225 req/s | 332,945–347,403 req/s |

Dengan 4 thread klien, angka io-threads 4 sama dalam setiap larian: klien menjadi had, dan 8 thread klien menaikkannya. Pelayan dan klien berkongsi satu mesin, jadi baca angka ini sebagai ukuran pada mesin itu, bukan sebagai peraturan umum.

### Makmal: satu arahan setiap jenis data

**Disahkan pada Redis 8.10.3, 2026-11-07.** `local/02-data-types-tour/tour.sh` menjalankan satu arahan bagi setiap jenis pada imej asal, semuanya tanpa ralat:

| Jenis | Apa yang ditunjukkan arahan |
|---|---|
| String | `INCR` pada kaunter halaman |
| Hash | `HEXPIRE` pada satu medan; `HTTL` menunjukkan 60 untuk medan itu dan -1 untuk yang lain |
| List, Set, Sorted set | baris gilir, keahlian, papan pendahulu |
| Stream | `XADD`, kumpulan pengguna (consumer group), `XREADGROUP` |
| Geo | kedai dalam lingkungan 5 km dari Dewan Bandaran Seoul |
| Bitmap, HyperLogLog | bit aktif harian, kiraan unik |
| JSON | menambah pada tatasusunan dalam dokumen |
| Time series | sampel dipurata ke dalam baldi 2 jam |
| Bloom, Top-k | semakan pernah dilihat, item paling kerap |
| Array (8.8) | jarang (sparse): `ARLEN` 1001 selepas menulis indeks 0–2 dan 1000; `ARSCAN` memulangkan empat |
| Vector set (beta) | jiran terdekat dengan `VSIM` |
| Search | `FT.CREATE` pada hash, kemudian pertanyaan julat berangka |

**Jenis kebarangkalian yang lain** (`local/02-data-types-tour/probabilistic.sh`). Count-min sketch sebesar 56 KB mengira 100,000 paparan halaman dengan tepat bagi halaman yang disemak (10,000, 91, 99, 0). Cuckoo filter, tidak seperti Bloom, dapat memadam satu item, dengan kadar positif palsu 0.69% pada 10,000 pengguna yang tidak wujud. T-digest sebesar 10 KB memberikan median dan p99.9 dalam lingkungan 1%, tetapi p99 sebanyak 325 ms berbanding nilai tepat 257 ms, di rentang tempat data melompat dan hanya sedikit titik.

### Makmal: carian dan carian vektor

**Disahkan pada Redis 8.10.3, 2026-11-07.** `local/03-search-vector/lab.py` mengindeks 30 nota satu baris daripada tapak ini sebagai hash dan sebagai JSON, dengan benaman (embedding) dijana secara setempat menggunakan model terbuka yang kecil (tanpa API key).

| Pertanyaan | Apa yang dikembalikan |
|---|---|
| Teks penuh `failover`, tag `{memory}`, berangka `[-inf 2025]` | nota yang sepadan |
| Teks penuh `cache in sync with my database` | tiada: setiap perkataan mesti muncul |
| KNN "How do I keep Redis in sync with my Postgres tables?" | nota change data capture di tempat pertama (persamaan 0.83) |
| KNN dengan `(@category:{cluster})` sebagai penapis | hanya nota cluster |
| `FT.HYBRID` (8.4+), teks serta vektor, `COMBINE RRF` | gabungan kedua-dua senarai, yang pertama bagi setiap satu di atas |
| Vector set: `VADD` vektor yang sama, `VSIM` | 3 teratas yang sama seperti KNN, tanpa mengisytiharkan indeks |

redis-py 8.1.0 merundingkan RESP3, jadi balasan `FT.SEARCH` tiba sebagai map, bukan senarai rata yang dihuraikan oleh contoh lama. Dokumentasi: [Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/), [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/). Makmal: [`local/03-search-vector`](https://github.com/litkhai/notes-on-redis/tree/main/local/03-search-vector).

**Lebih banyak ciri carian** (`extras.py`). `FT.AGGREGATE` mengumpulkan dan mengira; sinonim membuat "switchover" menemui nota failover selepas imbasan semula di latar belakang selesai; `FT.SPELLCHECK` mencadangkan `failover`, `eviction` dan `replica` bagi ejaan yang salah; `FLOAT16`, `INT8` dan `SVS-VAMANA` dengan `LVQ8` memulangkan 3 teratas yang sama seperti `FLOAT32`. Soalan bahasa Korea menemui nota bahasa Inggeris yang betul hanya dengan model berbilang bahasa, dan tidak bagi setiap soalan.

### Belum diliputi

Redis Insight desktop (imej Docker ialah aplikasi yang sama) dan klien selain redis-py dan node-redis.

</div>
