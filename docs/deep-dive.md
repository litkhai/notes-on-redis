---
layout: default
title: Deep Dive
permalink: /deep-dive/
---

# Deep Dive

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: run.** All eight mechanisms were run on Redis 8.10.3 in local Docker on 2026-11-07 (below).
</div>

One section per mechanism, each with the mechanism in plain words, the official doc link, a script that produces a number or an observable, and the output as run: threading and the event loop (`io-threads`), persistence (RDB, AOF, `BACKUP` since 8.10), replication / Sentinel / Cluster (`PSYNC`, failover, 16384 slots, `CLUSTER MIGRATION`), eviction and memory (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer groups, `IDMP`, `XNACK`), Functions and ACL.

### Threading and the event loop

**Verified on Redis 8.10.3, 2026-11-07.** Commands run on one main thread; `io-threads` hands request reading and reply writing to helper threads. Same `redis-benchmark` load (SET/GET, 64-byte values, 400 clients, 12 benchmark threads) on a 24-core host:

| `io-threads` | SET/GET requests/s | What `INFO threads` showed |
|---|---|---|
| 1 | 134,523–136,097 | one thread does everything |
| 2 | 126,072–131,596 | the main thread did no client I/O; one helper took it all |
| 4 | 342,349–352,485 | reads and writes spread over three helpers |
| 8 | 498,753–520,472 | spread over seven helpers |

Two threads gave nothing because the main thread stops doing client I/O once helpers exist. Docs: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). Lab: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

**Pipelining and TLS** (`more.sh`). At `-P 16` four I/O threads were already the ceiling: 1.14–1.26 M requests/s on one thread, 2.66–3.42 M on four, no more on eight. With TLS and no pipelining the threads mattered most: about 90,000 requests/s on one thread (a third below plain TCP), about 220,000 on four, 357,000–392,000 on eight, because the I/O threads also do the encryption.

**4 KB values** (`values.sh`): about 111,000, 285,000–307,000 and 443,000 requests/s on 1, 4 and 8 threads, the same shape as with 64-byte values.

### Persistence

**Verified on Redis 8.10.3, 2026-11-07.** From the docs: "With the default policy of fsync every second, write performance is still great", and "A backup reuses the multi-part AOF format".

| Experiment | Result |
|---|---|
| RDB fork, 214 MB in memory | 4–5 ms |
| Copy-on-write during BGSAVE, no writes | 2.2 MB |
| Copy-on-write during BGSAVE, keys overwritten | 252 MB, more than the dataset |
| `appendfsync everysec` | 97,087 req/s, p50 0.119 ms, p99 0.255 ms |
| `appendfsync always` | 17,203 req/s, p50 1.159 ms, p99 1.527 ms |
| `BGREWRITEAOF` | base RDB 10 MB, empty incremental file, manifest sequence 2 |
| `BACKUP START` / `SEAL` (8.10) | base, incremental and manifest pinned as hard links in `backupdir` |
| Restore with `--preload-file aof:<manifest>` | both pre-seal keys back; the key written after `SEAL` absent |

A write-heavy instance needs memory headroom for snapshots. `preload-file` wants `aof:` or `rdb:` in front of the file name and rejects a bare path. Docs: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/). Lab: [`deep-dive/02-persistence`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/02-persistence).

### Replication and Sentinel

**Verified on Redis 8.10.3, 2026-11-07.** One primary, two replicas, three Sentinels (quorum 2, `down-after-milliseconds` 3000). From the docs: `WAIT` "will always return the number of replicas that acknowledged the write commands sent by the current client", and "WAIT does not make Redis a strongly consistent store".

| Experiment | Result |
|---|---|
| Replica connections killed | two partial resyncs |
| Replica restarted without persistence | one full sync |
| `SET` + `WAIT 2 1000` on one connection, both replicas up | 2 |
| Same, one replica paused | 1, after the 1 s timeout |
| `WAIT 2 1000` on a fresh connection | 2 at once: nothing of its own to wait for |
| Primary stopped → Sentinel names a new master | 4,402 ms |
| Old primary started again | replica of the new master after 11.3 s |
| Same failover with Sentinel watching a container name | 284,103 ms |

The last row is the trap: with a hostname, the stopped container's name no longer resolved in Docker's DNS, the Sentinels stalled on the lookups and marked each other down. Give Sentinel addresses that stay resolvable. Docs: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/). Lab: [`deep-dive/03-replication-sentinel`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/03-replication-sentinel).

**A Sentinel-aware client** (`sentinel_client.py`). redis-py's `Sentinel(...).master_for()` wrote to the new master 4.4 s after the old one was killed, with no code change, but returned `ConnectionError`, `TimeoutError` and `MasterNotFoundError` in between, so keep a retry. The old primary, restarted, answered as `master` for 11 s until Sentinel turned it into a replica: a client connecting to it directly can write there and lose those writes.

**Restarts and another client** (`persist.sh`, `sentinel_client.mjs`). A restarted replica resynced partially only with RDB persistence and a graceful shutdown; with AOF, or after SIGKILL, it took a full sync, as the replication page says ("It is not possible to partially sync a replica that restarted via the AOF file"). node-redis's `createSentinel()` threw no errors during a failover: it held a write for 6.1 s until the new master answered, where redis-py raised errors for about 4 s.

### Cluster

**Verified on Redis 8.10.3, 2026-11-07.** Six nodes, three primaries with one replica each. From the spec: "Each master node in a cluster handles a subset of the 16384 hash slots", with `HASH_SLOT = CRC16(key) mod 16384`; hash tags "force certain keys to be stored in the same hash slot".

| Experiment | Result |
|---|---|
| `CLUSTER KEYSLOT user:1`, `user:2` | 10778, 6777 |
| `{user:1}:cart`, `{user:1}:orders` | both 10778 |
| `GET user:2` on the wrong node | `MOVED 6777 10.231.78.12:6379` |
| `MSET user:1 a user:2 b` | `CROSSSLOT` |
| `MSET` with a shared hash tag | `OK` |
| `CLUSTER MIGRATION IMPORT 0 999` (8.4) under ~200,000 writes/s | 1,000 slots moved in 44 ms, `write_pause_ms 0`, no client errors |

The same `CROSSSLOT` refusal is what ElastiCache Serverless returned on the [Compare page]({{ '/compare/' | relative_url }}): plan keys that are used together with a shared hash tag. Docs: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/). Lab: [`deep-dive/04-cluster`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/04-cluster).

**Failover inside the cluster** (`failover.py`). A primary killed under writes: with the default `cluster-node-timeout` of 15 s the replica took over at 19.3 s and the client could not write that primary's keys for about 16 s; with 3 s, 5.3 s and about 4 s. In both runs keys on the other primaries also got one `ClusterDownError` for about 1 s: until the replica takes over, some slots have no owner, and with `cluster-require-full-coverage yes` the whole cluster refuses. Compare the 1.3 s of the Redis Enterprise operator on the [Enterprise page]({{ '/enterprise/' | relative_url }}).

**Network partition** (`partition.py`). A primary cut off the network kept accepting writes from its own side until the 5 s node timeout, then answered `CLUSTERDOWN`; after its replica took over and the node rejoined, those 21 writes were gone and the majority's value stood.

### Eviction and memory

**Verified on Redis 8.10.3, 2026-11-07.** `maxmemory 16mb`, three groups of 5,000 keys, then 30,000 new keys. *Read-hot* keys were read five times and never rewritten; *write-hot* keys were rewritten five times and never read. From the docs: "allkeys-lrm : Evict the least recently modified (LRM) keys", and "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently."

| Policy | Read-hot left | Write-hot left | Cold left | What it means |
|---|---|---|---|---|
| `noeviction` | 5,000 | 5,000 | 5,000 | writes refused: `command not allowed when used memory > 'maxmemory'` |
| `allkeys-lru` | 621 | 614 | 356 | last access, read or write; the newest keys win |
| `allkeys-lfu` | 5,000 | 5,000 | 2,117 | frequency of reads and writes protects both hot groups |
| `allkeys-lrm` (8.6) | 368 | 3,318 | 431 | only writes protect a key; reads do not |
| `allkeys-random` | 2,595 | 2,568 | 2,636 | about half of each |

LRU and LRM sample keys, so their counts move between runs; an earlier run kept about 3,200 of each hot group under LRU. `HOTKEYS START METRICS 1 CPU` (8.6) ranked the two keys the script read most in first and second place. `INFO keysizes` gives a power-of-two size histogram per type. Docs: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/). Lab: [`deep-dive/05-eviction`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/05-eviction).

**Volatile policies and `maxmemory-samples`** (`volatile.py`). Volatile policies never evicted keys without a TTL; with only such keys, writes were refused as under `noeviction`. Among TTL keys, `volatile-lfu` and `volatile-lru` kept the read ones and `volatile-ttl` took the shortest-lived first. More samples made LRU keep recently read keys more clearly (10 samples: about 320 read vs 95 unread kept, 5 samples: 840 vs 630). With 1 sample eviction fell behind and writes were refused with OOM.

### Client-side caching

**Verified on Redis 8.10.3 with redis-py 6.1.1, 2026-11-07.** From the docs: "In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." In broadcasting mode, "the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

| Experiment | Result |
|---|---|
| redis-py `protocol=3`, `CacheConfig()`, 1,001 reads of one key | 1 GET reached the server; the other 1,000 took 33.83 ms in total |
| Another client's `SET` on that key | cache dropped it; the next read fetched the new value once |
| `CLIENT LIST` | flag `t` on the caching connection |
| `CLIENT TRACKING ON BCAST PREFIX user:`, then `SET` on `user:2:name`, `order:9`, `user:3:cart` | `invalidate` pushes for the two `user:` keys, nothing for `order:9` |

No application code handles invalidation: turning on the cache in the client is the whole change. Docs: [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/). Lab: [`deep-dive/06-client-side-caching`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/06-client-side-caching).

**OPTIN, OPTOUT, NOLOOP, RESP2** (`modes.py`). `OPTIN` tracked only the read after `CLIENT CACHING YES`; `OPTOUT` tracked everything except the read after `CLIENT CACHING NO`. Without `NOLOOP` a connection is told about its own writes; with it, not. A RESP2 client cannot receive pushes, so `CLIENT TRACKING ON REDIRECT <id>` delivers invalidations as Pub/Sub messages on `__redis__:invalidate` to another connection.

### Streams

**Verified on Redis 8.10.3, 2026-11-07.** A stream `orders`, a consumer group `shipping`, and a consumer `c1` that reads three entries and dies. From the command pages: XACKDEL acts "to both acknowledge entry processing and clean up the stream in a single atomic operation"; IDMP "Enables idempotent message processing (at-most-once production) to prevent duplicate entries"; NACKed messages "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

| Command | What it solves | Result |
|---|---|---|
| `XAUTOCLAIM orders shipping c2 100 0-0` (6.2) | entries stuck with a dead consumer | `c2` took all three of `c1`'s entries; delivery count 1 → 2 |
| `XACKDEL orders shipping IDS 2 0-1 0-2` (8.2) | `XACK` then `XDEL`, two calls with a gap | replies `1, 1`; `XLEN` 5 → 3 |
| `XADD payments IDMP svc-a req-42 * …` twice (8.6) | a producer retry writing a duplicate | same ID both times; `XLEN` stays 1 |
| `XNACK orders shipping FAIL IDS 1 0-4` (8.8) | a consumer giving a message back before its idle timeout | entry left unowned, count kept at 1 |

After `XNACK`, a new `XREADGROUP … >` did not return the entry: `>` only reads new entries. `XAUTOCLAIM` with a 60-second minimum idle time claimed it at once and left the other pending entries with their owners. So XNACK speeds up recovery, and recovery still goes through `XAUTOCLAIM` or `XCLAIM`. Docs: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/). Lab: [`deep-dive/07-streams`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/07-streams).

**The remaining options** (`more.sh`). `XNACK` after one delivery: `SILENT` count 0, `FAIL` 1, `FATAL` 9223372036854775807, `RETRYCOUNT 5` 5; `FORCE` adds an entry no one has read to the pending list. `IDMPAUTO` deduplicates by content. `XCFGSET` clears the IDMP history, so a retry sent right after it is accepted; `IDMP-DURATION` and `IDMP-MAXSIZE` bound how long and how many IDs are remembered. With two groups, `XACKDEL KEEPREF` deletes the entry and leaves the other group a reference to nothing, `DELREF` removes that reference, and `ACKED` deletes only when every group has acknowledged.

**IDMP and failover** (`idmp_replica.sh`). The idempotency map replicates: after the primary was killed and the replica promoted, a producer's retry still returned the original entry ID.

### Functions and ACL

**Verified on Redis 8.10.3, 2026-11-07.** From the functions page: "Functions provide the same core functionality as scripts but are first-class software artifacts of the database." From the ACL page on selectors: "If a command matches either the user permissions or any selector, it is allowed."

| Experiment | Result |
|---|---|
| `FCALL_RO stock` (registered with `no-writes`) | runs |
| `FCALL_RO sell` (writes) | `Can not execute a script with write flag using *_ro command` |
| `%R~catalog:* %W~events:*`: `GET` / `SET catalog:1` | allowed / `NOPERM` |
| same user: `XADD` / `XRANGE events:clicks` | allowed / `NOPERM` |
| `~report:* +@read (~audit:* +xadd)`: `XADD audit:log` / `XADD report:log` | allowed / `NOPERM` |
| `+@all -@write`: `JSON.GET` / `JSON.SET` / `TS.ADD` | allowed / `NOPERM` / `NOPERM` |
| `+@read` only: `JSON.GET` | allowed |

The ACL page still says "command categories, with the exception of +@all, never include module commands." On Redis 8.10.3 that is no longer so: `ACL CAT write` lists 47 JSON, time series and probabilistic commands. An ACL written for Redis 7 can grant or block more after an upgrade. Docs: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/). Lab: [`deep-dive/08-functions-acl`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/08-functions-acl).

**Replicas, dumps, ACL files and the log** (`more.sh`). A library loaded on the primary reached the replica; there `FCALL_RO` ran and `FCALL` of a writing function got `READONLY`. `FUNCTION DUMP` and `FUNCTION RESTORE` moved the library to another server with its flags. `ACL SAVE` and `ACL LOAD` round-tripped an ACL file, `#` comments included (Redis 8.8), and one bad line made the whole `ACL LOAD` fail without changing anything. `ACL LOG` recorded a wrong password, a denied command and a denied key, each with its reason and user.

**ACL users do not replicate** (`acl_replica.sh`). A user created on the primary did not exist on the replica (`WRONGPASS`), although the data did; keep the same ACL file on every server.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 실행함.** 메커니즘 여덟 가지를 모두 2026-11-07에 로컬 Docker의 Redis 8.10.3에서 실행했다(아래).
</div>

메커니즘마다 절 하나 — 평이한 설명, 공식 문서 링크, 숫자나 관찰을 만드는 스크립트, 실행한 출력: 스레딩과 이벤트 루프(`io-threads`), 영속성(RDB, AOF, 8.10의 `BACKUP`), 복제 / Sentinel / Cluster(`PSYNC`, 페일오버, 16384 슬롯, `CLUSTER MIGRATION`), 축출과 메모리(LRU / LFU / LRM, `HOTKEYS`), 클라이언트 캐시(`CLIENT TRACKING`), Streams(컨슈머 그룹, `IDMP`, `XNACK`), Functions와 ACL.

### 스레딩과 이벤트 루프

**확인: Redis 8.10.3, 2026-11-07.** 명령은 메인 스레드 하나에서 실행된다. `io-threads`는 요청 읽기와 응답 쓰기를 보조 스레드에 넘긴다. 24코어 호스트에서 같은 `redis-benchmark` 부하(SET/GET, 64바이트 값, 클라이언트 400, 벤치마크 스레드 12):

| `io-threads` | SET/GET 초당 요청 | `INFO threads`가 보인 것 |
|---|---|---|
| 1 | 134,523–136,097 | 스레드 하나가 전부 처리 |
| 2 | 126,072–131,596 | 메인 스레드는 클라이언트 I/O를 안 하고 보조 하나가 전부 맡음 |
| 4 | 342,349–352,485 | 보조 셋에 읽기·쓰기 분산 |
| 8 | 498,753–520,472 | 보조 일곱에 분산 |

스레드 둘이 효과가 없던 이유는 보조 스레드가 생기면 메인 스레드가 클라이언트 I/O를 그만두기 때문이다. 문서: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). 실습: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

**파이프라이닝과 TLS**(`more.sh`). `-P 16`에서는 I/O 스레드 넷이 이미 상한이었다: 스레드 하나 초당 114만–126만, 넷 266만–342만, 여덟도 그 이상은 아니었다. 파이프라이닝 없는 TLS에서는 스레드가 가장 크게 효과를 냈다: 하나 약 90,000(평문 TCP보다 3분의 1 적음), 넷 약 220,000, 여덟 357,000–392,000. I/O 스레드가 암호화도 맡기 때문이다.

**4 KB 값**(`values.sh`): 스레드 1, 4, 8에서 초당 약 111,000, 285,000–307,000, 443,000. 64바이트 값과 같은 모양이다.

### 영속성

**확인: Redis 8.10.3, 2026-11-07.** 문서의 표현: "With the default policy of fsync every second, write performance is still great", "A backup reuses the multi-part AOF format".

| 실험 | 결과 |
|---|---|
| RDB fork, 메모리 214 MB | 4–5 ms |
| BGSAVE 중 copy-on-write, 쓰기 없음 | 2.2 MB |
| BGSAVE 중 copy-on-write, 키 덮어쓰기 | 252 MB, 데이터보다 큼 |
| `appendfsync everysec` | 초당 97,087, p50 0.119 ms, p99 0.255 ms |
| `appendfsync always` | 초당 17,203, p50 1.159 ms, p99 1.527 ms |
| `BGREWRITEAOF` | base RDB 10 MB, 빈 증분 파일, manifest 2번 |
| `BACKUP START` / `SEAL`(8.10) | base, 증분, manifest를 `backupdir`에 하드 링크로 고정 |
| `--preload-file aof:<manifest>`로 복원 | 봉인 전 키 둘이 돌아옴, `SEAL` 뒤에 쓴 키는 없음 |

쓰기가 많은 인스턴스는 스냅숏용 메모리 여유가 필요하다. `preload-file`은 파일 이름 앞에 `aof:`나 `rdb:`를 요구하고 경로만 주면 거절한다. 문서: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/). 실습: [`deep-dive/02-persistence`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/02-persistence).

### 복제와 Sentinel

**확인: Redis 8.10.3, 2026-11-07.** 주 서버 하나, 복제본 둘, Sentinel 셋(quorum 2, `down-after-milliseconds` 3000). 문서의 표현: `WAIT`은 "will always return the number of replicas that acknowledged the write commands sent by the current client", "WAIT does not make Redis a strongly consistent store".

| 실험 | 결과 |
|---|---|
| 복제본 연결 끊기 | 부분 재동기화 두 번 |
| 영속성 없는 복제본 재시작 | 전체 동기화 한 번 |
| 한 연결에서 `SET` + `WAIT 2 1000`, 복제본 둘 정상 | 2 |
| 같은 조건, 복제본 하나 멈춤 | 1초 타임아웃 뒤 1 |
| 새 연결에서 `WAIT 2 1000` | 바로 2: 기다릴 자기 쓰기가 없음 |
| 주 서버 정지 → Sentinel이 새 마스터 지목 | 4,402 ms |
| 옛 주 서버 재시작 | 11.3초 뒤 새 마스터의 복제본 |
| Sentinel이 컨테이너 이름을 감시할 때 같은 장애 조치 | 284,103 ms |

마지막 행이 함정이다. 호스트 이름을 쓰면 멈춘 컨테이너의 이름이 Docker DNS에서 풀리지 않고, Sentinel들이 조회에 묶여 서로를 다운으로 표시한다. Sentinel에는 계속 풀리는 주소를 준다. 문서: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/). 실습: [`deep-dive/03-replication-sentinel`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/03-replication-sentinel).

**Sentinel을 아는 클라이언트**(`sentinel_client.py`). redis-py의 `Sentinel(...).master_for()`는 옛 마스터를 죽인 뒤 4.4초에 코드 변경 없이 새 마스터에 썼다. 그 사이에는 `ConnectionError`, `TimeoutError`, `MasterNotFoundError`를 돌려주므로 재시도는 둔다. 재시작한 옛 주 서버는 Sentinel이 복제본으로 바꿀 때까지 11초 동안 `master`로 답했다. 직접 붙는 클라이언트는 그 사이 거기에 쓰고 그 쓰기를 잃을 수 있다.

**재시작과 다른 클라이언트**(`persist.sh`, `sentinel_client.mjs`). 재시작한 복제본은 RDB 영속성과 정상 종료일 때만 부분 재동기화했다. AOF이거나 SIGKILL 뒤에는 전체 동기화였고, 복제 페이지도 그렇게 적는다("It is not possible to partially sync a replica that restarted via the AOF file"). node-redis의 `createSentinel()`은 장애 조치 중 오류를 던지지 않고 새 마스터가 답할 때까지 쓰기 하나를 6.1초 붙잡았다. redis-py는 약 4초 동안 오류를 냈다.

### 클러스터

**확인: Redis 8.10.3, 2026-11-07.** 노드 6개, 주 서버 셋에 복제본 하나씩. 명세의 표현: "Each master node in a cluster handles a subset of the 16384 hash slots", `HASH_SLOT = CRC16(key) mod 16384`. 해시 태그는 "force certain keys to be stored in the same hash slot".

| 실험 | 결과 |
|---|---|
| `CLUSTER KEYSLOT user:1`, `user:2` | 10778, 6777 |
| `{user:1}:cart`, `{user:1}:orders` | 둘 다 10778 |
| 잘못된 노드에 `GET user:2` | `MOVED 6777 10.231.78.12:6379` |
| `MSET user:1 a user:2 b` | `CROSSSLOT` |
| 같은 해시 태그로 `MSET` | `OK` |
| 초당 약 200,000 쓰기 중 `CLUSTER MIGRATION IMPORT 0 999`(8.4) | 슬롯 1,000개 44 ms에 이전, `write_pause_ms 0`, 클라이언트 오류 없음 |

[Compare 페이지]({{ '/compare/' | relative_url }})의 ElastiCache Serverless가 돌려준 것도 같은 `CROSSSLOT` 거절이다. 함께 쓰는 키는 해시 태그를 공유하도록 설계한다. 문서: [Redis Cluster로 확장](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [클러스터 명세](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/). 실습: [`deep-dive/04-cluster`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/04-cluster).

**클러스터 안의 장애 조치**(`failover.py`). 쓰기 중에 주 서버를 죽였다. 기본 `cluster-node-timeout` 15초에서는 복제본이 19.3초에 넘겨받았고, 클라이언트는 그 주 서버의 키에 약 16초 동안 쓰지 못했다. 3초에서는 5.3초와 약 4초. 두 번 모두 다른 주 서버의 키도 약 1초짜리 `ClusterDownError`를 한 번 받았다. 복제본이 넘겨받기 전까지 주인 없는 슬롯이 생기고, `cluster-require-full-coverage yes`에서는 클러스터 전체가 거절한다. [Enterprise 페이지]({{ '/enterprise/' | relative_url }})의 Redis Enterprise operator 1.3초와 비교해 보자.

**네트워크 분할**(`partition.py`). 네트워크에서 떨어진 주 서버는 노드 타임아웃 5초까지 자기 쪽의 쓰기를 받다가 `CLUSTERDOWN`으로 답했다. 복제본이 넘겨받고 노드가 다시 붙자 그 쓰기 21건은 사라지고 다수 쪽의 값이 남았다.

### 축출과 메모리

**확인: Redis 8.10.3, 2026-11-07.** `maxmemory 16mb`에 키 5,000개짜리 그룹 셋, 그다음 새 키 30,000개. *read-hot*은 다섯 번 읽고 다시 쓰지 않았고, *write-hot*은 다섯 번 다시 쓰고 읽지 않았다. 문서의 표현: "allkeys-lrm : Evict the least recently modified (LRM) keys", "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently."

| 정책 | 남은 read-hot | 남은 write-hot | 남은 cold | 뜻 |
|---|---|---|---|---|
| `noeviction` | 5,000 | 5,000 | 5,000 | 쓰기 거절: `command not allowed when used memory > 'maxmemory'` |
| `allkeys-lru` | 621 | 614 | 356 | 읽기든 쓰기든 마지막 접근. 가장 새 키가 이긴다 |
| `allkeys-lfu` | 5,000 | 5,000 | 2,117 | 읽기·쓰기 빈도가 두 hot 그룹을 모두 보호 |
| `allkeys-lrm`(8.6) | 368 | 3,318 | 431 | 쓰기만 키를 보호하고 읽기는 보호하지 않음 |
| `allkeys-random` | 2,595 | 2,568 | 2,636 | 그룹마다 절반 정도 |

LRU와 LRM은 키를 샘플링하므로 실행마다 수가 달라진다. 이전 실행에서 LRU는 hot 그룹마다 약 3,200개를 남겼다. `HOTKEYS START METRICS 1 CPU`(8.6)는 스크립트가 가장 많이 읽은 두 키를 1위와 2위로 꼽았다. `INFO keysizes`는 자료형별 2의 거듭제곱 크기 히스토그램을 준다. 문서: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/). 실습: [`deep-dive/05-eviction`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/05-eviction).

**volatile 정책과 `maxmemory-samples`**(`volatile.py`). volatile 정책은 TTL 없는 키를 한 번도 축출하지 않았다. 그런 키만 있으면 `noeviction`처럼 쓰기가 거절됐다. TTL 있는 키 중에서는 `volatile-lfu`와 `volatile-lru`가 읽은 키를 남겼고, `volatile-ttl`은 수명이 짧은 키부터 지웠다. 샘플이 많을수록 LRU는 최근 읽은 키를 더 분명히 남겼다(10개: 읽은 키 약 320 대 안 읽은 키 95, 5개: 840 대 630). 샘플 1개에서는 축출이 따라가지 못해 OOM으로 쓰기가 거절됐다.

### 클라이언트 측 캐시

**확인: Redis 8.10.3, redis-py 6.1.1, 2026-11-07.** 문서의 표현: "In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." 브로드캐스트 모드에서는 "the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

| 실험 | 결과 |
|---|---|
| redis-py `protocol=3`, `CacheConfig()`, 한 키를 1,001번 읽기 | 서버까지 간 GET 1번. 나머지 1,000번은 합계 33.83 ms |
| 다른 클라이언트가 그 키에 `SET` | 캐시가 키를 버리고, 다음 읽기가 새 값을 한 번 가져옴 |
| `CLIENT LIST` | 캐시 연결에 `t` 플래그 |
| `CLIENT TRACKING ON BCAST PREFIX user:` 뒤 `user:2:name`, `order:9`, `user:3:cart`에 `SET` | `user:` 키 둘에 `invalidate` 푸시, `order:9`에는 없음 |

무효화를 처리하는 애플리케이션 코드는 없다. 클라이언트에서 캐시를 켜는 것이 바뀐 전부다. 문서: [클라이언트 측 캐시 레퍼런스](https://redis.io/docs/latest/develop/reference/client-side-caching/). 실습: [`deep-dive/06-client-side-caching`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/06-client-side-caching).

**OPTIN, OPTOUT, NOLOOP, RESP2**(`modes.py`). `OPTIN`은 `CLIENT CACHING YES` 다음의 읽기만 추적했고, `OPTOUT`은 `CLIENT CACHING NO` 다음의 읽기만 빼고 모두 추적했다. `NOLOOP`이 없으면 연결이 자기 쓰기에 대한 알림도 받고, 있으면 받지 않는다. RESP2 클라이언트는 푸시를 받을 수 없으므로 `CLIENT TRACKING ON REDIRECT <id>`가 무효화를 `__redis__:invalidate`의 Pub/Sub 메시지로 다른 연결에 보낸다.

### Streams

**확인: Redis 8.10.3, 2026-11-07.** 스트림 `orders`, 소비자 그룹 `shipping`, 항목 셋을 읽고 죽는 소비자 `c1`. 명령 페이지의 표현: XACKDEL은 "to both acknowledge entry processing and clean up the stream in a single atomic operation", IDMP는 "Enables idempotent message processing (at-most-once production) to prevent duplicate entries", NACK한 메시지는 "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

| 명령 | 푸는 문제 | 결과 |
|---|---|---|
| `XAUTOCLAIM orders shipping c2 100 0-0`(6.2) | 죽은 소비자에게 묶인 항목 | `c2`가 `c1`의 항목 셋을 모두 가져감. 전달 횟수 1 → 2 |
| `XACKDEL orders shipping IDS 2 0-1 0-2`(8.2) | `XACK` 뒤 `XDEL`, 틈이 있는 두 번의 호출 | 응답 `1, 1`, `XLEN` 5 → 3 |
| `XADD payments IDMP svc-a req-42 * …` 두 번(8.6) | 생산자 재시도가 중복을 씀 | 두 번 모두 같은 ID, `XLEN`은 1 그대로 |
| `XNACK orders shipping FAIL IDS 1 0-4`(8.8) | 유휴 시간이 차기 전에 메시지를 돌려주기 | 항목은 주인 없이 남고 횟수는 1 유지 |

`XNACK` 뒤 새 `XREADGROUP … >`는 그 항목을 돌려주지 않았다. `>`는 새 항목만 읽는다. 최소 유휴 60초를 준 `XAUTOCLAIM`이 그것을 바로 가져갔고, 다른 대기 항목은 주인에게 남겼다. XNACK은 회수를 빠르게 할 뿐이고, 회수 자체는 여전히 `XAUTOCLAIM`이나 `XCLAIM`으로 한다. 문서: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/). 실습: [`deep-dive/07-streams`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/07-streams).

**나머지 옵션**(`more.sh`). 한 번 전달한 뒤 `XNACK`: `SILENT` 횟수 0, `FAIL` 1, `FATAL` 9223372036854775807, `RETRYCOUNT 5`는 5. `FORCE`는 아무도 읽지 않은 항목을 대기 목록에 넣는다. `IDMPAUTO`는 내용으로 중복을 거른다. `XCFGSET`은 IDMP 기록을 지우므로 그 직후의 재시도는 받아들여진다. `IDMP-DURATION`과 `IDMP-MAXSIZE`가 ID를 얼마나 오래, 몇 개까지 기억할지 정한다. 그룹이 둘이면 `XACKDEL KEEPREF`는 항목을 지우고 다른 그룹에 없는 항목을 가리키는 참조를 남기고, `DELREF`는 그 참조까지 지우고, `ACKED`는 모든 그룹이 확인했을 때만 지운다.

**IDMP와 장애 조치**(`idmp_replica.sh`). 멱등성 맵은 복제된다. 주 서버를 죽이고 복제본을 승격한 뒤에도 생산자의 재시도는 원래 항목 ID를 돌려받았다.

### Functions와 ACL

**확인: Redis 8.10.3, 2026-11-07.** 함수 페이지의 표현: "Functions provide the same core functionality as scripts but are first-class software artifacts of the database." ACL 페이지의 셀렉터 설명: "If a command matches either the user permissions or any selector, it is allowed."

| 실험 | 결과 |
|---|---|
| `FCALL_RO stock`(`no-writes`로 등록) | 실행됨 |
| `FCALL_RO sell`(쓰기) | `Can not execute a script with write flag using *_ro command` |
| `%R~catalog:* %W~events:*`: `GET` / `SET catalog:1` | 허용 / `NOPERM` |
| 같은 사용자: `XADD` / `XRANGE events:clicks` | 허용 / `NOPERM` |
| `~report:* +@read (~audit:* +xadd)`: `XADD audit:log` / `XADD report:log` | 허용 / `NOPERM` |
| `+@all -@write`: `JSON.GET` / `JSON.SET` / `TS.ADD` | 허용 / `NOPERM` / `NOPERM` |
| `+@read`만: `JSON.GET` | 허용 |

ACL 페이지에는 여전히 "command categories, with the exception of +@all, never include module commands"라고 적혀 있다. Redis 8.10.3에서는 더 이상 그렇지 않다. `ACL CAT write`에 JSON, time series, 확률형 명령 47개가 있다. Redis 7용으로 쓴 ACL은 업그레이드 뒤 더 허락하거나 더 막을 수 있다. 문서: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/). 실습: [`deep-dive/08-functions-acl`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/08-functions-acl).

**복제본, 덤프, ACL 파일, 로그**(`more.sh`). 주 서버에 올린 라이브러리가 복제본에 전달됐다. 거기서 `FCALL_RO`는 돌았고 쓰는 함수의 `FCALL`은 `READONLY`를 받았다. `FUNCTION DUMP`와 `FUNCTION RESTORE`가 라이브러리를 플래그까지 다른 서버로 옮겼다. `ACL SAVE`와 `ACL LOAD`가 `#` 주석까지(Redis 8.8) ACL 파일을 주고받았고, 잘못된 줄 하나가 있으면 `ACL LOAD` 전체가 아무것도 바꾸지 않고 실패했다. `ACL LOG`는 틀린 비밀번호, 거절된 명령, 거절된 키를 사유와 사용자와 함께 남겼다.

**ACL 사용자는 복제되지 않는다**(`acl_replica.sh`). 주 서버에서 만든 사용자는 복제본에 없었다(`WRONGPASS`). 데이터는 복제됐는데도 그렇다. 서버마다 같은 ACL 파일을 둔다.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：已运行。** 全部八种机制均已于 2026-11-07 在本地 Docker 中的 Redis 8.10.3 上运行（见下文）。
</div>

每种机制一节，包含：用通俗语言讲的机制、官方文档链接、能产出数字或可观察现象的脚本，以及实际运行的输出：线程与事件循环（`io-threads`）、持久化（RDB、AOF、8.10 起的 `BACKUP`）、复制 / Sentinel / Cluster（`PSYNC`、故障转移、16384 个槽、`CLUSTER MIGRATION`）、淘汰与内存（LRU / LFU / LRM、`HOTKEYS`）、客户端缓存（`CLIENT TRACKING`）、Streams（消费者组、`IDMP`、`XNACK`）、Functions 与 ACL。

### 线程与事件循环

**已在 Redis 8.10.3 上验证，2026-11-07。** 命令在一个主线程上执行；`io-threads` 把读取请求和写回响应交给辅助线程。相同的 `redis-benchmark` 负载（SET/GET，64 字节的值，400 个客户端，12 个基准测试线程），在 24 核主机上：

| `io-threads` | SET/GET 每秒请求数 | `INFO threads` 显示的情况 |
|---|---|---|
| 1 | 134,523–136,097 | 一个线程包办所有工作 |
| 2 | 126,072–131,596 | 主线程不做任何客户端 I/O；一个辅助线程全部承担 |
| 4 | 342,349–352,485 | 读写分散到三个辅助线程 |
| 8 | 498,753–520,472 | 分散到七个辅助线程 |

两个线程没有任何提升，因为一旦有了辅助线程，主线程就不再做客户端 I/O。 文档: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). 实验: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

**管道化与 TLS**（`more.sh`）。在 `-P 16` 时，四个 I/O 线程已是上限：一个线程为 1.14–1.26 M 请求/秒，四个线程为 2.66–3.42 M，八个线程没有更多。使用 TLS 且不使用管道化时，线程数影响最大：一个线程约 90,000 请求/秒（比普通 TCP 低三分之一），四个线程约 220,000，八个线程 357,000–392,000，因为 I/O 线程还要负责加密。

**4 KB 的值**（`values.sh`）：一个、四个和八个线程分别约为 111,000、285,000–307,000 和 443,000 请求/秒，与 64 字节的值趋势相同。

### 持久化

**已在 Redis 8.10.3 上验证，2026-11-07。** 文档原文："With the default policy of fsync every second, write performance is still great"，以及 "A backup reuses the multi-part AOF format"。

| 实验 | 结果 |
|---|---|
| RDB fork，内存中 214 MB | 4–5 ms |
| BGSAVE 期间的写时复制，无写入 | 2.2 MB |
| BGSAVE 期间的写时复制，键被覆盖 | 252 MB，超过数据集大小 |
| `appendfsync everysec` | 97,087 req/s，p50 0.119 ms，p99 0.255 ms |
| `appendfsync always` | 17,203 req/s，p50 1.159 ms，p99 1.527 ms |
| `BGREWRITEAOF` | 基础 RDB 10 MB，增量文件为空，清单序号 2 |
| `BACKUP START` / `SEAL` (8.10) | 基础文件、增量文件和清单以硬链接形式固定在 `backupdir` 中 |
| 用 `--preload-file aof:<manifest>` 恢复 | `SEAL` 之前的两个键都回来了；`SEAL` 之后写入的键不存在 |

写入密集的实例需要为快照预留内存余量。`preload-file` 要求文件名前带 `aof:` 或 `rdb:`，裸路径会被拒绝。 文档: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/). 实验: [`deep-dive/02-persistence`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/02-persistence).

### 复制与 Sentinel

**已在 Redis 8.10.3 上验证，2026-11-07。** 一个主节点、两个副本、三个 Sentinel（quorum 2，`down-after-milliseconds` 3000）。 文档原文：`WAIT` "will always return the number of replicas that acknowledged the write commands sent by the current client"，以及 "WAIT does not make Redis a strongly consistent store"。

| 实验 | 结果 |
|---|---|
| 副本连接被断开 | 两次部分重同步 |
| 副本在无持久化的情况下重启 | 一次全量同步 |
| 在同一连接上 `SET` + `WAIT 2 1000`，两个副本都在线 | 2 |
| 同上，一个副本被暂停 | 1，在 1 秒超时之后 |
| 在新连接上 `WAIT 2 1000` | 立即返回 2：该连接自己没有要等待的写入 |
| 主节点停止 → Sentinel 指定新的 master | 4,402 ms |
| 旧主节点重新启动 | 11.3 s 后成为新 master 的副本 |
| 同样的故障转移，但 Sentinel 监视的是容器名 | 284,103 ms |

最后一行是陷阱：使用主机名时，已停止容器的名字在 Docker 的 DNS 中不再能解析，Sentinel 卡在这些查询上，并互相标记为下线。请给 Sentinel 提供始终可解析的地址。 文档: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/). 实验: [`deep-dive/03-replication-sentinel`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/03-replication-sentinel).

**感知 Sentinel 的客户端**（`sentinel_client.py`）。在旧主节点被杀掉 4.4 秒后，redis-py 的 `Sentinel(...).master_for()` 就写入了新的主节点，无需修改任何代码，但期间返回了 `ConnectionError`、`TimeoutError` 和 `MasterNotFoundError`，所以要保留重试。重启后的旧主节点在 Sentinel 把它变成副本之前，有 11 秒仍以 `master` 的身份应答：直接连接它的客户端可以在那里写入，并丢失这些写入。

**重启与另一个客户端**（`persist.sh`、`sentinel_client.mjs`）。重启后的副本只有在使用 RDB 持久化并且正常关闭时才会部分重同步；使用 AOF，或在 SIGKILL 之后，则会进行全量同步，正如复制页面所说（"It is not possible to partially sync a replica that restarted via the AOF file"）。node-redis 的 `createSentinel()` 在故障转移期间没有抛出任何错误：它把一次写入挂起了 6.1 秒，直到新的主节点应答，而 redis-py 则抛出了约 4 秒的错误。

### 集群

**已在 Redis 8.10.3 上验证，2026-11-07。** 六个节点，三个主节点，每个主节点一个副本。 文档原文（规范）："Each master node in a cluster handles a subset of the 16384 hash slots"，其中 `HASH_SLOT = CRC16(key) mod 16384`；hash tag "force certain keys to be stored in the same hash slot"。

| 实验 | 结果 |
|---|---|
| `CLUSTER KEYSLOT user:1`, `user:2` | 10778, 6777 |
| `{user:1}:cart`, `{user:1}:orders` | 都是 10778 |
| 在错误的节点上 `GET user:2` | `MOVED 6777 10.231.78.12:6379` |
| `MSET user:1 a user:2 b` | `CROSSSLOT` |
| 使用共同 hash tag 的 `MSET` | `OK` |
| `CLUSTER MIGRATION IMPORT 0 999` (8.4)，约 200,000 次写入/秒的负载下 | 1,000 个槽在 44 ms 内迁移完成，`write_pause_ms 0`，客户端无错误 |

ElastiCache Serverless 在 [Compare 页面]({{ '/compare/' | relative_url }}) 上返回的正是同样的 `CROSSSLOT` 拒绝：把需要一起使用的键规划为共用同一个 hash tag。 文档: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/). 实验: [`deep-dive/04-cluster`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/04-cluster).

**集群内的故障转移**（`failover.py`）。在写入过程中杀掉一个主节点：使用默认的 `cluster-node-timeout` 15 秒时，副本在 19.3 秒接管，客户端约有 16 秒无法写入该主节点的键；设为 3 秒时，分别是 5.3 秒和约 4 秒。两次运行中，其他主节点上的键也都遇到过一次约 1 秒的 `ClusterDownError`：在副本接管之前，有些槽没有所属节点，而在 `cluster-require-full-coverage yes` 下整个集群都会拒绝请求。可与 [Enterprise 页面]({{ '/enterprise/' | relative_url }})上 Redis Enterprise operator 的 1.3 秒对比。

**网络分区**（`partition.py`）。与网络断开的主节点在其自身一侧继续接受写入，直到 5 秒的节点超时，然后应答 `CLUSTERDOWN`；在其副本接管、该节点重新加入之后，这 21 次写入丢失了，多数派一侧的值得以保留。

### 淘汰与内存

**已在 Redis 8.10.3 上验证，2026-11-07。** `maxmemory 16mb`，三组各 5,000 个键，然后再写入 30,000 个新键。*读热点*键被读取五次且从未被改写；*写热点*键被改写五次且从未被读取。文档原文："allkeys-lrm : Evict the least recently modified (LRM) keys"，以及 "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently."

| 策略 | 剩余的读热点 | 剩余的写热点 | 剩余的冷数据 | 含义 |
|---|---|---|---|---|
| `noeviction` | 5,000 | 5,000 | 5,000 | 写入被拒绝：`command not allowed when used memory > 'maxmemory'` |
| `allkeys-lru` | 621 | 614 | 356 | 最近一次访问，无论读或写；最新的键胜出 |
| `allkeys-lfu` | 5,000 | 5,000 | 2,117 | 读写频率保护了两组热点键 |
| `allkeys-lrm` (8.6) | 368 | 3,318 | 431 | 只有写入能保护键；读取不能 |
| `allkeys-random` | 2,595 | 2,568 | 2,636 | 每组大约留下一半 |

LRU 和 LRM 采用采样，所以每次运行的数量会有变化；较早的一次运行中，LRU 下每个热点组保留了约 3,200 个。`HOTKEYS START METRICS 1 CPU` (8.6) 把脚本读取最多的两个键排在了第一和第二位。`INFO keysizes` 按类型给出以 2 的幂为分档的大小直方图。 文档: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/). 实验: [`deep-dive/05-eviction`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/05-eviction).

**volatile 策略与 `maxmemory-samples`**（`volatile.py`）。volatile 策略从不淘汰没有 TTL 的键；当只有这类键时，写入像在 `noeviction` 下一样被拒绝。在带 TTL 的键中，`volatile-lfu` 和 `volatile-lru` 保留了被读取过的键，`volatile-ttl` 先淘汰剩余寿命最短的键。采样数越多，LRU 越明显地保留最近被读取的键（10 个样本：约保留 320 个已读键对 95 个未读键；5 个样本：840 对 630）。只有 1 个样本时，淘汰跟不上，写入因 OOM 被拒绝。

### 客户端缓存

**已在 Redis 8.10.3 和 redis-py 6.1.1 上验证，2026-11-07。** 文档原文："In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." 在广播模式下，"the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

| 实验 | 结果 |
|---|---|
| redis-py `protocol=3`，`CacheConfig()`，对同一个键读取 1,001 次 | 只有 1 次 GET 到达服务器；其余 1,000 次总共耗时 33.83 ms |
| 另一个客户端对该键执行 `SET` | 缓存丢弃了它；下一次读取只重新获取了一次新值 |
| `CLIENT LIST` | 带缓存的连接上有标志 `t` |
| `CLIENT TRACKING ON BCAST PREFIX user:`，然后对 `user:2:name`、`order:9`、`user:3:cart` 执行 `SET` | 两个 `user:` 键收到了 `invalidate` 推送，`order:9` 没有 |

无需应用代码处理失效：在客户端打开缓存就是全部改动。 文档: [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/). 实验: [`deep-dive/06-client-side-caching`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/06-client-side-caching).

**OPTIN、OPTOUT、NOLOOP、RESP2**（`modes.py`）。`OPTIN` 只跟踪 `CLIENT CACHING YES` 之后的那次读取；`OPTOUT` 跟踪除 `CLIENT CACHING NO` 之后那次读取以外的所有读取。没有 `NOLOOP` 时，连接会被告知它自己的写入；有 `NOLOOP` 则不会。RESP2 客户端无法接收推送，所以 `CLIENT TRACKING ON REDIRECT <id>` 会把失效通知作为 Pub/Sub 消息，通过 `__redis__:invalidate` 发送给另一个连接。

### Streams

**已在 Redis 8.10.3 上验证，2026-11-07。** 一个流 `orders`，一个消费者组 `shipping`，以及读取三个条目后死亡的消费者 `c1`。命令页面中的原文：XACKDEL 的作用是 "to both acknowledge entry processing and clean up the stream in a single atomic operation"；IDMP "Enables idempotent message processing (at-most-once production) to prevent duplicate entries"；被 NACK 的消息 "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

| 命令 | 解决的问题 | 结果 |
|---|---|---|
| `XAUTOCLAIM orders shipping c2 100 0-0` (6.2) | 卡在已死亡消费者手中的条目 | `c2` 拿走了 `c1` 的全部三个条目；投递次数 1 → 2 |
| `XACKDEL orders shipping IDS 2 0-1 0-2` (8.2) | `XACK` 再 `XDEL`，两次调用之间有空隙 | 回复 `1, 1`；`XLEN` 5 → 3 |
| `XADD payments IDMP svc-a req-42 * …` 两次 (8.6) | 生产者重试写入了重复条目 | 两次返回相同的 ID；`XLEN` 保持 1 |
| `XNACK orders shipping FAIL IDS 1 0-4` (8.8) | 消费者在空闲超时之前把消息还回去 | 条目变为无主，计数保持 1 |

`XNACK` 之后，新的 `XREADGROUP … >` 并没有返回该条目：`>` 只读取新条目。最小空闲时间为 60 秒的 `XAUTOCLAIM` 立刻认领了它，并让其他待处理条目留在原持有者手里。所以 XNACK 加快了恢复，但恢复仍然要经过 `XAUTOCLAIM` 或 `XCLAIM`。 文档: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/). 实验: [`deep-dive/07-streams`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/07-streams).

**其余选项**（`more.sh`）。一次投递之后执行 `XNACK`：`SILENT` 的计数为 0，`FAIL` 为 1，`FATAL` 为 9223372036854775807，`RETRYCOUNT 5` 为 5；`FORCE` 会向待处理列表中添加一个无人读取过的条目。`IDMPAUTO` 按内容去重。`XCFGSET` 会清除 IDMP 历史，所以紧接其后发送的重试会被接受；`IDMP-DURATION` 和 `IDMP-MAXSIZE` 限制记住 ID 的时长和数量。对于两个消费者组，`XACKDEL KEEPREF` 删除条目，并让另一个组留下一个指向空无的引用，`DELREF` 移除该引用，而 `ACKED` 只在每个组都已确认时才删除。

**IDMP 与故障转移**（`idmp_replica.sh`）。幂等映射会被复制：主节点被杀掉、副本被提升之后，生产者的重试仍然返回原来的条目 ID。

### Functions 与 ACL

**已在 Redis 8.10.3 上验证，2026-11-07。** Functions 页面原文："Functions provide the same core functionality as scripts but are first-class software artifacts of the database." ACL 页面中关于 selector 的原文："If a command matches either the user permissions or any selector, it is allowed."

| 实验 | 结果 |
|---|---|
| `FCALL_RO stock`（以 `no-writes` 注册） | 运行 |
| `FCALL_RO sell`（会写入） | `Can not execute a script with write flag using *_ro command` |
| `%R~catalog:* %W~events:*`：`GET` / `SET catalog:1` | 允许 / `NOPERM` |
| 同一用户：`XADD` / `XRANGE events:clicks` | 允许 / `NOPERM` |
| `~report:* +@read (~audit:* +xadd)`：`XADD audit:log` / `XADD report:log` | 允许 / `NOPERM` |
| `+@all -@write`：`JSON.GET` / `JSON.SET` / `TS.ADD` | 允许 / `NOPERM` / `NOPERM` |
| 仅 `+@read`：`JSON.GET` | 允许 |

ACL 页面仍然写着 "command categories, with the exception of +@all, never include module commands." 在 Redis 8.10.3 上已不再如此：`ACL CAT write` 列出了 47 个 JSON、时间序列和概率型数据结构的命令。为 Redis 7 编写的 ACL 在升级后可能授予或拦截更多的命令。 文档: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/). 实验: [`deep-dive/08-functions-acl`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/08-functions-acl).

**副本、转储、ACL 文件与日志**（`more.sh`）。在主节点上加载的库传到了副本；在副本上 `FCALL_RO` 可以运行，而对写入型函数执行 `FCALL` 得到 `READONLY`。`FUNCTION DUMP` 和 `FUNCTION RESTORE` 把库连同其标志移到了另一台服务器。`ACL SAVE` 和 `ACL LOAD` 完整往返了一个 ACL 文件，包括 `#` 注释（Redis 8.8），而且只要有一行错误，整个 `ACL LOAD` 就会失败，且不改变任何东西。`ACL LOG` 记录了错误密码、被拒绝的命令和被拒绝的键，每条都带有原因和用户。

**ACL 用户不会被复制**（`acl_replica.sh`）。在主节点上创建的用户在副本上并不存在（`WRONGPASS`），尽管数据是存在的；请在每台服务器上使用同一个 ACL 文件。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**ステータス：実行済み。** 8 つのメカニズムをすべて 2026-11-07 にローカル Docker の Redis 8.10.3 で実行した（以下）。
</div>

メカニズムごとに 1 節。平易な説明、公式ドキュメントへのリンク、数値や観察結果を出すスクリプト、実行した出力を載せている：スレッドとイベントループ（`io-threads`）、永続化（RDB、AOF、8.10 の `BACKUP`）、レプリケーション / Sentinel / Cluster（`PSYNC`、フェイルオーバー、16384 スロット、`CLUSTER MIGRATION`）、エビクションとメモリ（LRU / LFU / LRM、`HOTKEYS`）、クライアントサイドキャッシュ（`CLIENT TRACKING`）、Streams（コンシューマーグループ、`IDMP`、`XNACK`）、Functions と ACL。

### スレッドとイベントループ

**Redis 8.10.3 で検証、2026-11-07。** コマンドは 1 本のメインスレッドで実行される。`io-threads` はリクエストの読み取りと応答の書き込みをヘルパースレッドに任せる。24 コアのホストで、同じ `redis-benchmark` 負荷（SET/GET、64 バイトの値、400 クライアント、ベンチマークスレッド 12 本）をかけた結果：

| `io-threads` | SET/GET リクエスト/秒 | `INFO threads` の表示 |
|---|---|---|
| 1 | 134,523–136,097 | 1 本のスレッドがすべてを処理 |
| 2 | 126,072–131,596 | メインスレッドはクライアント I/O を行わず、ヘルパー 1 本がすべて担当 |
| 4 | 342,349–352,485 | 読み書きが 3 本のヘルパーに分散 |
| 8 | 498,753–520,472 | 7 本のヘルパーに分散 |

2 スレッドでは何も得られなかった。ヘルパーがあるとメインスレッドがクライアント I/O をやめるためである。 ドキュメント: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). ラボ: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

**パイプライン処理と TLS**（`more.sh`）。`-P 16` では I/O スレッド 4 本がすでに上限だった：1 スレッドで 1.14–1.26 M リクエスト/秒、4 スレッドで 2.66–3.42 M、8 スレッドでもそれ以上は伸びなかった。TLS を使いパイプライン処理をしない場合は、スレッド数の影響が最も大きかった：1 スレッドで約 90,000 リクエスト/秒（通常の TCP より 3 分の 1 低い）、4 スレッドで約 220,000、8 スレッドで 357,000–392,000。I/O スレッドが暗号化も担当するためである。

**4 KB の値**（`values.sh`）：1、4、8 スレッドでそれぞれ約 111,000、285,000–307,000、443,000 リクエスト/秒で、64 バイトの値のときと同じ傾向だった。

### 永続化

**Redis 8.10.3 で検証、2026-11-07。** ドキュメントより："With the default policy of fsync every second, write performance is still great"、および "A backup reuses the multi-part AOF format"。

| 実験 | 結果 |
|---|---|
| RDB fork、メモリ上 214 MB | 4–5 ms |
| BGSAVE 中のコピーオンライト、書き込みなし | 2.2 MB |
| BGSAVE 中のコピーオンライト、キーを上書き | 252 MB、データセットより大きい |
| `appendfsync everysec` | 97,087 req/s、p50 0.119 ms、p99 0.255 ms |
| `appendfsync always` | 17,203 req/s、p50 1.159 ms、p99 1.527 ms |
| `BGREWRITEAOF` | ベース RDB 10 MB、インクリメンタルファイルは空、マニフェストのシーケンス 2 |
| `BACKUP START` / `SEAL` (8.10) | ベース、インクリメンタル、マニフェストが `backupdir` にハードリンクとして固定された |
| `--preload-file aof:<manifest>` でリストア | `SEAL` 前の 2 つのキーは戻った。`SEAL` 後に書いたキーは存在しない |

書き込みの多いインスタンスには、スナップショット用のメモリの余裕が必要である。`preload-file` はファイル名の前に `aof:` か `rdb:` を要求し、パスだけの指定は拒否する。 ドキュメント: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/). ラボ: [`deep-dive/02-persistence`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/02-persistence).

### レプリケーションと Sentinel

**Redis 8.10.3 で検証、2026-11-07。** プライマリ 1 台、レプリカ 2 台、Sentinel 3 台（quorum 2、`down-after-milliseconds` 3000）。 ドキュメントより：`WAIT` "will always return the number of replicas that acknowledged the write commands sent by the current client"、および "WAIT does not make Redis a strongly consistent store"。

| 実験 | 結果 |
|---|---|
| レプリカの接続を切断 | 部分再同期が 2 回 |
| レプリカを永続化なしで再起動 | フル同期が 1 回 |
| 同じ接続で `SET` + `WAIT 2 1000`、レプリカ 2 台とも稼働 | 2 |
| 同上、レプリカ 1 台を一時停止 | 1、タイムアウトの 1 秒後 |
| 新しい接続で `WAIT 2 1000` | すぐに 2：その接続には待つべき自身の書き込みがない |
| プライマリ停止 → Sentinel が新しい master を指名 | 4,402 ms |
| 旧プライマリを再起動 | 11.3 秒後に新しい master のレプリカになった |
| 同じフェイルオーバーで、Sentinel がコンテナ名を監視 | 284,103 ms |

最後の行が落とし穴である。ホスト名を使うと、停止したコンテナの名前が Docker の DNS で解決できなくなり、Sentinel は名前解決で止まって互いをダウンと判定した。Sentinel には解決可能なままのアドレスを与えること。 ドキュメント: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/). ラボ: [`deep-dive/03-replication-sentinel`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/03-replication-sentinel).

**Sentinel 対応クライアント**（`sentinel_client.py`）。redis-py の `Sentinel(...).master_for()` は、古いプライマリを停止させてから 4.4 秒後に、コードを変更しなくても新しいプライマリへ書き込んだ。ただしその間は `ConnectionError`、`TimeoutError`、`MasterNotFoundError` が返るので、リトライは残しておくこと。再起動した古いプライマリは、Sentinel がレプリカに変えるまでの 11 秒間 `master` として応答した：そこへ直接接続しているクライアントは書き込めてしまい、その書き込みを失う。

**再起動と別のクライアント**（`persist.sh`、`sentinel_client.mjs`）。再起動したレプリカが部分再同期できたのは、RDB 永続化を使い、かつ正常にシャットダウンした場合だけだった。AOF を使った場合や SIGKILL の後はフル同期になり、レプリケーションのページにもこうある（"It is not possible to partially sync a replica that restarted via the AOF file"）。node-redis の `createSentinel()` はフェイルオーバー中にエラーを出さなかった。新しいプライマリが応答するまで書き込みを 6.1 秒保留したが、redis-py は約 4 秒間エラーを返した。

### クラスター

**Redis 8.10.3 で検証、2026-11-07。** 6 ノード、プライマリ 3 台、それぞれレプリカ 1 台。 仕様より："Each master node in a cluster handles a subset of the 16384 hash slots"。`HASH_SLOT = CRC16(key) mod 16384` である。ハッシュタグは "force certain keys to be stored in the same hash slot"。

| 実験 | 結果 |
|---|---|
| `CLUSTER KEYSLOT user:1`, `user:2` | 10778, 6777 |
| `{user:1}:cart`, `{user:1}:orders` | どちらも 10778 |
| 誤ったノードで `GET user:2` | `MOVED 6777 10.231.78.12:6379` |
| `MSET user:1 a user:2 b` | `CROSSSLOT` |
| 共通のハッシュタグを使った `MSET` | `OK` |
| `CLUSTER MIGRATION IMPORT 0 999` (8.4)、約 200,000 書き込み/秒の負荷下 | 1,000 スロットを 44 ms で移動、`write_pause_ms 0`、クライアントエラーなし |

[Compare ページ]({{ '/compare/' | relative_url }})で ElastiCache Serverless が返したのも同じ `CROSSSLOT` の拒否だった。一緒に使うキーは、共通のハッシュタグを付けて設計すること。 ドキュメント: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/). ラボ: [`deep-dive/04-cluster`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/04-cluster).

**クラスター内のフェイルオーバー**（`failover.py`）。書き込み中にプライマリを停止した場合：既定の `cluster-node-timeout` 15 秒ではレプリカが 19.3 秒で引き継ぎ、クライアントはそのプライマリのキーに約 16 秒間書き込めなかった。3 秒にすると 5.3 秒と約 4 秒だった。どちらの実行でも、他のプライマリのキーにも約 1 秒間の `ClusterDownError` が 1 回出た：レプリカが引き継ぐまでは持ち主のいないスロットがあり、`cluster-require-full-coverage yes` ではクラスター全体が要求を拒否するためである。[Enterprise ページ]({{ '/enterprise/' | relative_url }})にある Redis Enterprise operator の 1.3 秒と比べてほしい。

**ネットワーク分断**（`partition.py`）。ネットワークから切り離されたプライマリは、5 秒のノードタイムアウトまで自分側からの書き込みを受け付け続け、その後 `CLUSTERDOWN` を返した。レプリカが引き継ぎ、ノードが復帰した後には、その 21 件の書き込みは失われ、過半数側の値が残った。

### エビクションとメモリ

**Redis 8.10.3 で検証、2026-11-07。** `maxmemory 16mb`、5,000 キーずつ 3 グループ、そこへ新しいキーを 30,000 個書き込んだ。*読み取りホット*のキーは 5 回読み取り、一度も書き換えていない。*書き込みホット*のキーは 5 回書き換え、一度も読んでいない。ドキュメントより："allkeys-lrm : Evict the least recently modified (LRM) keys"、および "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently."

| ポリシー | 残った読み取りホット | 残った書き込みホット | 残ったコールド | 意味 |
|---|---|---|---|---|
| `noeviction` | 5,000 | 5,000 | 5,000 | 書き込みは拒否される：`command not allowed when used memory > 'maxmemory'` |
| `allkeys-lru` | 621 | 614 | 356 | 最後のアクセス（読み取りでも書き込みでも）。新しいキーが勝つ |
| `allkeys-lfu` | 5,000 | 5,000 | 2,117 | 読み書きの頻度が 2 つのホットグループを両方守る |
| `allkeys-lrm` (8.6) | 368 | 3,318 | 431 | 書き込みだけがキーを守る。読み取りは守らない |
| `allkeys-random` | 2,595 | 2,568 | 2,636 | 各グループとも約半分 |

LRU と LRM はキーをサンプリングするため、件数は実行ごとに変わる。以前の実行では、LRU で各ホットグループが約 3,200 個残った。`HOTKEYS START METRICS 1 CPU` (8.6) は、スクリプトが最も多く読んだ 2 つのキーを 1 位と 2 位に並べた。`INFO keysizes` は、型ごとに 2 のべき乗刻みのサイズのヒストグラムを返す。 ドキュメント: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/). ラボ: [`deep-dive/05-eviction`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/05-eviction).

**volatile ポリシーと `maxmemory-samples`**（`volatile.py`）。volatile ポリシーは TTL のないキーを一度もエビクションしなかった。そのようなキーだけの場合、書き込みは `noeviction` と同じように拒否された。TTL 付きのキーの中では、`volatile-lfu` と `volatile-lru` は読み取られたキーを残し、`volatile-ttl` は残り寿命の短いものから先に取り除いた。サンプル数を増やすと、LRU は最近読み取られたキーをよりはっきり残した（サンプル 10 個：読み取り済み約 320 対 未読 95 が残った、サンプル 5 個：840 対 630）。サンプル 1 個ではエビクションが追いつかず、書き込みは OOM で拒否された。

### クライアントサイドキャッシュ

**Redis 8.10.3 と redis-py 6.1.1 で検証、2026-11-07。** ドキュメントより："In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." ブロードキャストモードでは、"the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

| 実験 | 結果 |
|---|---|
| redis-py `protocol=3`、`CacheConfig()`、同じキーを 1,001 回読み取り | サーバーに届いた GET は 1 回。残り 1,000 回の合計は 33.83 ms |
| 別のクライアントがそのキーに `SET` | キャッシュがそれを破棄し、次の読み取りで新しい値を 1 回取得した |
| `CLIENT LIST` | キャッシュ用の接続にフラグ `t` |
| `CLIENT TRACKING ON BCAST PREFIX user:` のあと、`user:2:name`、`order:9`、`user:3:cart` に `SET` | `user:` の 2 つのキーには `invalidate` プッシュが届き、`order:9` には届かなかった |

アプリケーションコードで無効化を扱う必要はない。クライアントでキャッシュを有効にするだけで済む。 ドキュメント: [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/). ラボ: [`deep-dive/06-client-side-caching`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/06-client-side-caching).

**OPTIN、OPTOUT、NOLOOP、RESP2**（`modes.py`）。`OPTIN` は `CLIENT CACHING YES` の直後の読み取りだけを追跡し、`OPTOUT` は `CLIENT CACHING NO` の直後の読み取りを除くすべてを追跡した。`NOLOOP` がないと、接続は自分自身の書き込みについて通知を受ける。あれば受けない。RESP2 クライアントはプッシュを受け取れないため、`CLIENT TRACKING ON REDIRECT <id>` は無効化通知を Pub/Sub メッセージとして `__redis__:invalidate` 経由で別の接続に届ける。

### Streams

**Redis 8.10.3 で検証、2026-11-07。** ストリーム `orders`、コンシューマーグループ `shipping`、3 エントリを読んで死ぬコンシューマー `c1`。コマンドページより：XACKDEL は "to both acknowledge entry processing and clean up the stream in a single atomic operation" ためのもの。IDMP は "Enables idempotent message processing (at-most-once production) to prevent duplicate entries"。NACK されたメッセージは "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

| コマンド | 解決する問題 | 結果 |
|---|---|---|
| `XAUTOCLAIM orders shipping c2 100 0-0` (6.2) | 死んだコンシューマーが抱えたままのエントリ | `c2` が `c1` の 3 エントリすべてを引き取った。配信回数 1 → 2 |
| `XACKDEL orders shipping IDS 2 0-1 0-2` (8.2) | `XACK` の後に `XDEL`、2 回の呼び出しの間にすき間がある | 応答は `1, 1`。`XLEN` 5 → 3 |
| `XADD payments IDMP svc-a req-42 * …` 2 回 (8.6) | プロデューサーのリトライによる重複書き込み | どちらも同じ ID。`XLEN` は 1 のまま |
| `XNACK orders shipping FAIL IDS 1 0-4` (8.8) | アイドルタイムアウトより前に、コンシューマーがメッセージを返す | エントリは持ち主なしになり、回数は 1 のまま |

`XNACK` の後、新しい `XREADGROUP … >` はそのエントリを返さなかった。`>` は新しいエントリだけを読むからである。最小アイドル時間 60 秒の `XAUTOCLAIM` はそれをすぐに引き取り、他の保留エントリは持ち主のもとに残した。つまり XNACK は復旧を早めるが、復旧はやはり `XAUTOCLAIM` か `XCLAIM` を通る。 ドキュメント: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/). ラボ: [`deep-dive/07-streams`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/07-streams).

**残りのオプション**（`more.sh`）。1 回配信した後の `XNACK`：`SILENT` のカウントは 0、`FAIL` は 1、`FATAL` は 9223372036854775807、`RETRYCOUNT 5` は 5。`FORCE` は誰も読んでいないエントリを保留リストに追加する。`IDMPAUTO` は内容で重複を排除する。`XCFGSET` は IDMP の履歴を消すので、その直後に送ったリトライは受理される。`IDMP-DURATION` と `IDMP-MAXSIZE` は、ID を記憶する期間と個数を制限する。2 つのグループがある場合、`XACKDEL KEEPREF` はエントリを削除し、もう一方のグループには何も指さない参照が残る。`DELREF` はその参照を取り除き、`ACKED` はすべてのグループが確認応答したときだけ削除する。

**IDMP とフェイルオーバー**（`idmp_replica.sh`）。冪等性マップはレプリケートされる。プライマリを停止してレプリカを昇格させた後も、プロデューサーのリトライは元のエントリ ID を返した。

### Functions と ACL

**Redis 8.10.3 で検証、2026-11-07。** Functions のページより："Functions provide the same core functionality as scripts but are first-class software artifacts of the database." ACL のページの selector の項より："If a command matches either the user permissions or any selector, it is allowed."

| 実験 | 結果 |
|---|---|
| `FCALL_RO stock`（`no-writes` で登録） | 実行できる |
| `FCALL_RO sell`（書き込みあり） | `Can not execute a script with write flag using *_ro command` |
| `%R~catalog:* %W~events:*`：`GET` / `SET catalog:1` | 許可 / `NOPERM` |
| 同じユーザー：`XADD` / `XRANGE events:clicks` | 許可 / `NOPERM` |
| `~report:* +@read (~audit:* +xadd)`：`XADD audit:log` / `XADD report:log` | 許可 / `NOPERM` |
| `+@all -@write`：`JSON.GET` / `JSON.SET` / `TS.ADD` | 許可 / `NOPERM` / `NOPERM` |
| `+@read` のみ：`JSON.GET` | 許可 |

ACL のページには今も "command categories, with the exception of +@all, never include module commands." とある。Redis 8.10.3 ではもうそうではない。`ACL CAT write` は JSON、時系列、確率的データ構造の 47 個のコマンドを列挙する。Redis 7 向けに書いた ACL は、アップグレード後に許可や拒否の対象が増えることがある。 ドキュメント: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/). ラボ: [`deep-dive/08-functions-acl`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/08-functions-acl).

**レプリカ、ダンプ、ACL ファイル、ログ**（`more.sh`）。プライマリにロードしたライブラリはレプリカに届いた。レプリカでは `FCALL_RO` が実行でき、書き込みを行う関数の `FCALL` は `READONLY` になった。`FUNCTION DUMP` と `FUNCTION RESTORE` は、ライブラリをフラグごと別のサーバーに移した。`ACL SAVE` と `ACL LOAD` は、`#` コメントを含めて ACL ファイルを往復できた（Redis 8.8）。また、1 行でも不正な行があると `ACL LOAD` 全体が失敗し、何も変更されなかった。`ACL LOG` は、誤ったパスワード、拒否されたコマンド、拒否されたキーを、それぞれの理由とユーザーとともに記録した。

**ACL ユーザーはレプリケートされない**（`acl_replica.sh`）。プライマリで作成したユーザーはレプリカには存在せず（`WRONGPASS`）、データは存在していた。すべてのサーバーで同じ ACL ファイルを使うこと。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: รันแล้ว** กลไกทั้งแปดอย่างถูกรันบน Redis 8.10.3 ใน Docker ในเครื่องเมื่อ 2026-11-07 (ด้านล่าง)
</div>

หนึ่งหัวข้อต่อหนึ่งกลไก แต่ละหัวข้อมีคำอธิบายกลไกด้วยภาษาง่าย ๆ ลิงก์เอกสารทางการ สคริปต์ที่ให้ตัวเลขหรือสิ่งที่สังเกตได้ และผลลัพธ์ตามที่รันจริง: เธรดและ event loop (`io-threads`), การคงอยู่ของข้อมูล (RDB, AOF, `BACKUP` ตั้งแต่ 8.10), replication / Sentinel / Cluster (`PSYNC`, failover, 16384 สล็อต, `CLUSTER MIGRATION`), eviction และหน่วยความจำ (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer group, `IDMP`, `XNACK`), Functions และ ACL

### เธรดและ event loop

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** คำสั่งทำงานบนเธรดหลักเธรดเดียว `io-threads` ส่งการอ่านคำขอและการเขียนคำตอบให้เธรดช่วย โหลด `redis-benchmark` เดียวกัน (SET/GET, ค่าขนาด 64 ไบต์, 400 ไคลเอนต์, เธรดเบนช์มาร์ก 12 เธรด) บนโฮสต์ 24 คอร์:

| `io-threads` | คำขอ SET/GET ต่อวินาที | สิ่งที่ `INFO threads` แสดง |
|---|---|---|
| 1 | 134,523–136,097 | เธรดเดียวทำทุกอย่าง |
| 2 | 126,072–131,596 | เธรดหลักไม่ทำ I/O ของไคลเอนต์เลย เธรดช่วยหนึ่งเธรดรับไปทั้งหมด |
| 4 | 342,349–352,485 | การอ่านและเขียนกระจายไปยังเธรดช่วยสามเธรด |
| 8 | 498,753–520,472 | กระจายไปยังเธรดช่วยเจ็ดเธรด |

สองเธรดไม่ได้ผลอะไรเลย เพราะเมื่อมีเธรดช่วยแล้ว เธรดหลักจะหยุดทำ I/O ของไคลเอนต์ เอกสาร: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). แล็บ: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

**Pipelining และ TLS** (`more.sh`) ที่ `-P 16` เธรด I/O สี่ตัวก็ถึงเพดานแล้ว: 1.14–1.26 M คำขอ/วินาทีบนเธรดเดียว 2.66–3.42 M บนสี่เธรด และไม่เพิ่มอีกบนแปดเธรด เมื่อใช้ TLS โดยไม่ใช้ pipelining จำนวนเธรดส่งผลมากที่สุด: ประมาณ 90,000 คำขอ/วินาทีบนเธรดเดียว (ต่ำกว่า TCP ธรรมดาหนึ่งในสาม) ประมาณ 220,000 บนสี่เธรด และ 357,000–392,000 บนแปดเธรด เพราะเธรด I/O ต้องเข้ารหัสด้วย

**ค่าขนาด 4 KB** (`values.sh`) ประมาณ 111,000, 285,000–307,000 และ 443,000 คำขอ/วินาทีบน 1, 4 และ 8 เธรด ตามลำดับ รูปแบบเดียวกับค่าขนาด 64 ไบต์

### การคงอยู่ของข้อมูล

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** จากเอกสาร: "With the default policy of fsync every second, write performance is still great" และ "A backup reuses the multi-part AOF format"

| การทดลอง | ผลลัพธ์ |
|---|---|
| RDB fork, ใช้หน่วยความจำ 214 MB | 4–5 ms |
| copy-on-write ระหว่าง BGSAVE, ไม่มีการเขียน | 2.2 MB |
| copy-on-write ระหว่าง BGSAVE, เขียนทับคีย์ | 252 MB มากกว่าชุดข้อมูล |
| `appendfsync everysec` | 97,087 req/s, p50 0.119 ms, p99 0.255 ms |
| `appendfsync always` | 17,203 req/s, p50 1.159 ms, p99 1.527 ms |
| `BGREWRITEAOF` | RDB ฐาน 10 MB, ไฟล์ incremental ว่าง, ลำดับ manifest 2 |
| `BACKUP START` / `SEAL` (8.10) | ไฟล์ฐาน ไฟล์ incremental และ manifest ถูกตรึงเป็น hard link ใน `backupdir` |
| กู้คืนด้วย `--preload-file aof:<manifest>` | คีย์สองตัวก่อน seal กลับมา ส่วนคีย์ที่เขียนหลัง `SEAL` ไม่มี |

อินสแตนซ์ที่เขียนหนักต้องเผื่อหน่วยความจำไว้สำหรับสแนปช็อต `preload-file` ต้องมี `aof:` หรือ `rdb:` นำหน้าชื่อไฟล์ และปฏิเสธพาธเปล่า เอกสาร: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/). แล็บ: [`deep-dive/02-persistence`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/02-persistence).

### Replication และ Sentinel

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** primary หนึ่งตัว replica สองตัว Sentinel สามตัว (quorum 2, `down-after-milliseconds` 3000) จากเอกสาร: `WAIT` "will always return the number of replicas that acknowledged the write commands sent by the current client" และ "WAIT does not make Redis a strongly consistent store"

| การทดลอง | ผลลัพธ์ |
|---|---|
| ตัดการเชื่อมต่อของ replica | partial resync สองครั้ง |
| รีสตาร์ต replica โดยไม่มีการคงอยู่ของข้อมูล | full sync หนึ่งครั้ง |
| `SET` + `WAIT 2 1000` บนการเชื่อมต่อเดียวกัน, replica ทั้งสองทำงานอยู่ | 2 |
| เหมือนกัน, หยุด replica หนึ่งตัวชั่วคราว | 1, หลังหมดเวลา 1 วินาที |
| `WAIT 2 1000` บนการเชื่อมต่อใหม่ | 2 ทันที: ไม่มีการเขียนของตัวเองให้รอ |
| หยุด primary → Sentinel ระบุ master ตัวใหม่ | 4,402 ms |
| เริ่ม primary ตัวเก่าอีกครั้ง | เป็น replica ของ master ตัวใหม่หลังผ่านไป 11.3 วินาที |
| failover แบบเดียวกัน แต่ให้ Sentinel เฝ้าดูชื่อคอนเทนเนอร์ | 284,103 ms |

แถวสุดท้ายคือกับดัก: เมื่อใช้ชื่อโฮสต์ ชื่อของคอนเทนเนอร์ที่หยุดไปไม่สามารถ resolve ใน DNS ของ Docker ได้อีก Sentinel ค้างอยู่ที่การค้นหาและทำเครื่องหมายว่าอีกฝ่ายล่ม ควรให้ที่อยู่แก่ Sentinel ที่ยัง resolve ได้ตลอด เอกสาร: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/). แล็บ: [`deep-dive/03-replication-sentinel`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/03-replication-sentinel).

**ไคลเอนต์ที่รู้จัก Sentinel** (`sentinel_client.py`) `Sentinel(...).master_for()` ของ redis-py เขียนไปยัง primary ตัวใหม่ได้หลังจากฆ่า primary ตัวเก่า 4.4 วินาที โดยไม่ต้องแก้โค้ด แต่ระหว่างนั้นคืน `ConnectionError`, `TimeoutError` และ `MasterNotFoundError` จึงควรคง retry ไว้ primary ตัวเก่าที่รีสตาร์ตตอบเป็น `master` อยู่ 11 วินาทีจนกว่า Sentinel จะเปลี่ยนให้เป็น replica: ไคลเอนต์ที่เชื่อมต่อกับมันโดยตรงอาจเขียนลงไปและสูญเสียการเขียนเหล่านั้น

**การรีสตาร์ตและไคลเอนต์อีกตัว** (`persist.sh`, `sentinel_client.mjs`) replica ที่รีสตาร์ตทำ partial resync ได้เฉพาะเมื่อใช้การคงอยู่ของข้อมูลแบบ RDB และปิดระบบอย่างเรียบร้อย ส่วนเมื่อใช้ AOF หรือหลัง SIGKILL จะต้องทำ full sync ตามที่หน้า replication ระบุไว้ ("It is not possible to partially sync a replica that restarted via the AOF file") `createSentinel()` ของ node-redis ไม่โยนข้อผิดพลาดใด ๆ ระหว่าง failover โดยพักการเขียนไว้ 6.1 วินาทีจนกว่า primary ตัวใหม่จะตอบ ขณะที่ redis-py ส่งข้อผิดพลาดประมาณ 4 วินาที

### Cluster

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** หกโหนด primary สามตัว แต่ละตัวมี replica หนึ่งตัว จากสเปก: "Each master node in a cluster handles a subset of the 16384 hash slots" โดย `HASH_SLOT = CRC16(key) mod 16384` และ hash tag "force certain keys to be stored in the same hash slot"

| การทดลอง | ผลลัพธ์ |
|---|---|
| `CLUSTER KEYSLOT user:1`, `user:2` | 10778, 6777 |
| `{user:1}:cart`, `{user:1}:orders` | ทั้งคู่ 10778 |
| `GET user:2` บนโหนดที่ไม่ถูกต้อง | `MOVED 6777 10.231.78.12:6379` |
| `MSET user:1 a user:2 b` | `CROSSSLOT` |
| `MSET` ที่ใช้ hash tag ร่วมกัน | `OK` |
| `CLUSTER MIGRATION IMPORT 0 999` (8.4) ภายใต้การเขียนราว 200,000 ครั้ง/วินาที | ย้าย 1,000 สล็อตใน 44 ms, `write_pause_ms 0`, ไคลเอนต์ไม่มีข้อผิดพลาด |

ElastiCache Serverless ก็ตอบปฏิเสธด้วย `CROSSSLOT` แบบเดียวกันนี้บน[หน้า Compare]({{ '/compare/' | relative_url }}): ให้วางแผนคีย์ที่ใช้ร่วมกันโดยใช้ hash tag ร่วมกัน เอกสาร: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/). แล็บ: [`deep-dive/04-cluster`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/04-cluster).

**Failover ภายในคลัสเตอร์** (`failover.py`) เมื่อฆ่า primary ระหว่างที่กำลังเขียน: ด้วยค่าเริ่มต้น `cluster-node-timeout` 15 วินาที replica เข้ารับช่วงที่ 19.3 วินาที และไคลเอนต์เขียนคีย์ของ primary ตัวนั้นไม่ได้ประมาณ 16 วินาที ส่วนเมื่อตั้งเป็น 3 วินาที คือ 5.3 วินาทีและประมาณ 4 วินาที ในทั้งสองการรัน คีย์บน primary ตัวอื่นก็พบ `ClusterDownError` หนึ่งครั้งประมาณ 1 วินาทีเช่นกัน: จนกว่า replica จะเข้ารับช่วง บาง slot ไม่มีเจ้าของ และเมื่อ `cluster-require-full-coverage yes` ทั้งคลัสเตอร์จะปฏิเสธคำขอ เปรียบเทียบกับ 1.3 วินาทีของ Redis Enterprise operator ใน[หน้า Enterprise]({{ '/enterprise/' | relative_url }})

**network partition** (`partition.py`) primary ที่ถูกตัดออกจากเครือข่ายยังคงรับการเขียนจากฝั่งของตัวเองต่อไปจนถึง node timeout 5 วินาที แล้วจึงตอบ `CLUSTERDOWN` หลังจาก replica เข้ารับช่วงและโหนดกลับเข้าร่วม การเขียน 21 รายการนั้นหายไป และค่าของฝั่งเสียงข้างมากยังคงอยู่

### Eviction และหน่วยความจำ

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** `maxmemory 16mb` คีย์สามกลุ่มกลุ่มละ 5,000 คีย์ จากนั้นเขียนคีย์ใหม่ 30,000 คีย์ คีย์ *read-hot* ถูกอ่านห้าครั้งและไม่เคยถูกเขียนทับ คีย์ *write-hot* ถูกเขียนทับห้าครั้งและไม่เคยถูกอ่าน จากเอกสาร: "allkeys-lrm : Evict the least recently modified (LRM) keys" และ "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently."

| นโยบาย | Read-hot ที่เหลือ | Write-hot ที่เหลือ | Cold ที่เหลือ | ความหมาย |
|---|---|---|---|---|
| `noeviction` | 5,000 | 5,000 | 5,000 | การเขียนถูกปฏิเสธ: `command not allowed when used memory > 'maxmemory'` |
| `allkeys-lru` | 621 | 614 | 356 | การเข้าถึงครั้งล่าสุด ทั้งอ่านหรือเขียน คีย์ใหม่ที่สุดเป็นฝ่ายชนะ |
| `allkeys-lfu` | 5,000 | 5,000 | 2,117 | ความถี่ของการอ่านและเขียนปกป้องทั้งสองกลุ่มที่ร้อน |
| `allkeys-lrm` (8.6) | 368 | 3,318 | 431 | มีเพียงการเขียนที่ปกป้องคีย์ การอ่านไม่ช่วย |
| `allkeys-random` | 2,595 | 2,568 | 2,636 | เหลือราวครึ่งหนึ่งของแต่ละกลุ่ม |

LRU และ LRM สุ่มตัวอย่างคีย์ จำนวนที่เหลือจึงเปลี่ยนไปในแต่ละรอบ การรันครั้งก่อนหน้าเหลือราว 3,200 คีย์ต่อกลุ่มร้อนภายใต้ LRU `HOTKEYS START METRICS 1 CPU` (8.6) จัดอันดับสองคีย์ที่สคริปต์อ่านมากที่สุดไว้ที่อันดับหนึ่งและสอง `INFO keysizes` ให้ฮิสโตแกรมขนาดแบบยกกำลังสองต่อชนิด เอกสาร: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/). แล็บ: [`deep-dive/05-eviction`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/05-eviction).

**นโยบาย volatile และ `maxmemory-samples`** (`volatile.py`) นโยบาย volatile ไม่เคย evict คีย์ที่ไม่มี TTL เลย เมื่อมีแต่คีย์แบบนั้น การเขียนถูกปฏิเสธเหมือนภายใต้ `noeviction` ในบรรดาคีย์ที่มี TTL นั้น `volatile-lfu` และ `volatile-lru` เก็บคีย์ที่ถูกอ่านไว้ ส่วน `volatile-ttl` เอาคีย์ที่อายุสั้นที่สุดออกก่อน ยิ่งสุ่มตัวอย่างมาก LRU ก็ยิ่งเก็บคีย์ที่เพิ่งถูกอ่านไว้ได้ชัดเจนขึ้น (10 ตัวอย่าง: เหลือคีย์ที่ถูกอ่านประมาณ 320 ต่อคีย์ที่ไม่ถูกอ่าน 95, 5 ตัวอย่าง: 840 ต่อ 630) เมื่อใช้ 1 ตัวอย่าง eviction ตามไม่ทันและการเขียนถูกปฏิเสธด้วย OOM

### Client-side caching

**ตรวจสอบบน Redis 8.10.3 กับ redis-py 6.1.1, 2026-11-07** จากเอกสาร: "In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." ในโหมด broadcasting "the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

| การทดลอง | ผลลัพธ์ |
|---|---|
| redis-py `protocol=3`, `CacheConfig()`, อ่านคีย์เดียว 1,001 ครั้ง | GET ถึงเซิร์ฟเวอร์ 1 ครั้ง อีก 1,000 ครั้งใช้เวลารวม 33.83 ms |
| `SET` บนคีย์นั้นจากไคลเอนต์อื่น | แคชทิ้งคีย์นั้น การอ่านครั้งถัดไปดึงค่าใหม่หนึ่งครั้ง |
| `CLIENT LIST` | แฟล็ก `t` บนการเชื่อมต่อที่ใช้แคช |
| `CLIENT TRACKING ON BCAST PREFIX user:` แล้ว `SET` บน `user:2:name`, `order:9`, `user:3:cart` | ได้รับ push `invalidate` สำหรับคีย์ `user:` สองคีย์ ไม่มีสำหรับ `order:9` |

ไม่มีโค้ดของแอปพลิเคชันที่ต้องจัดการ invalidation: การเปิดแคชในไคลเอนต์คือการเปลี่ยนแปลงทั้งหมด เอกสาร: [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/). แล็บ: [`deep-dive/06-client-side-caching`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/06-client-side-caching).

**OPTIN, OPTOUT, NOLOOP, RESP2** (`modes.py`) `OPTIN` ติดตามเฉพาะการอ่านที่ตามหลัง `CLIENT CACHING YES` ส่วน `OPTOUT` ติดตามทุกอย่างยกเว้นการอ่านที่ตามหลัง `CLIENT CACHING NO` หากไม่มี `NOLOOP` การเชื่อมต่อจะได้รับแจ้งเกี่ยวกับการเขียนของตัวเอง แต่ถ้ามีจะไม่ได้รับ ไคลเอนต์ RESP2 รับ push ไม่ได้ ดังนั้น `CLIENT TRACKING ON REDIRECT <id>` จึงส่ง invalidation เป็นข้อความ Pub/Sub บน `__redis__:invalidate` ไปยังอีกการเชื่อมต่อหนึ่ง

### Streams

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** stream `orders` consumer group `shipping` และ consumer `c1` ที่อ่านสามเอนทรีแล้วตาย จากหน้าคำสั่ง: XACKDEL ทำงาน "to both acknowledge entry processing and clean up the stream in a single atomic operation"; IDMP "Enables idempotent message processing (at-most-once production) to prevent duplicate entries"; ข้อความที่ถูก NACK "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

| คำสั่ง | แก้ปัญหาอะไร | ผลลัพธ์ |
|---|---|---|
| `XAUTOCLAIM orders shipping c2 100 0-0` (6.2) | เอนทรีที่ค้างอยู่กับ consumer ที่ตายแล้ว | `c2` รับเอนทรีทั้งสามของ `c1` ไป จำนวนการส่งมอบ 1 → 2 |
| `XACKDEL orders shipping IDS 2 0-1 0-2` (8.2) | `XACK` แล้วตามด้วย `XDEL` สองคำสั่งที่มีช่องว่างระหว่างกัน | ตอบกลับ `1, 1` `XLEN` 5 → 3 |
| `XADD payments IDMP svc-a req-42 * …` สองครั้ง (8.6) | producer retry แล้วเขียนเอนทรีซ้ำ | ได้ ID เดียวกันทั้งสองครั้ง `XLEN` คงที่ที่ 1 |
| `XNACK orders shipping FAIL IDS 1 0-4` (8.8) | consumer คืนข้อความก่อนหมด idle timeout | เอนทรีไม่มีเจ้าของ จำนวนคงที่ที่ 1 |

หลัง `XNACK` คำสั่ง `XREADGROUP … >` ใหม่ไม่คืนเอนทรีนั้น: `>` อ่านเฉพาะเอนทรีใหม่ `XAUTOCLAIM` ที่กำหนด idle time ขั้นต่ำ 60 วินาทีรับเอนทรีนั้นไปทันทีและปล่อยเอนทรีที่ค้างอื่น ๆ ไว้กับเจ้าของเดิม ดังนั้น XNACK ช่วยให้กู้คืนเร็วขึ้น แต่การกู้คืนยังต้องผ่าน `XAUTOCLAIM` หรือ `XCLAIM` เอกสาร: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/). แล็บ: [`deep-dive/07-streams`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/07-streams).

**ตัวเลือกที่เหลือ** (`more.sh`) `XNACK` หลังส่งมอบหนึ่งครั้ง: `SILENT` ให้ count เป็น 0, `FAIL` เป็น 1, `FATAL` เป็น 9223372036854775807, `RETRYCOUNT 5` เป็น 5; `FORCE` เพิ่มเอนทรีที่ยังไม่มีใครอ่านเข้าไปใน pending list `IDMPAUTO` กรองรายการซ้ำตามเนื้อหา `XCFGSET` ล้างประวัติ IDMP ดังนั้นการลองใหม่ที่ส่งทันทีหลังจากนั้นจึงถูกยอมรับ; `IDMP-DURATION` และ `IDMP-MAXSIZE` จำกัดว่าจำ ID ไว้นานแค่ไหนและกี่รายการ เมื่อมีสองกลุ่ม `XACKDEL KEEPREF` ลบเอนทรีและทิ้งให้อีกกลุ่มมีการอ้างอิงที่ไม่ชี้ไปยังอะไรเลย `DELREF` ลบการอ้างอิงนั้น และ `ACKED` ลบเฉพาะเมื่อทุกกลุ่มได้ acknowledge แล้ว

**IDMP และ failover** (`idmp_replica.sh`) idempotency map ถูก replicate: หลังจากฆ่า primary และเลื่อน replica ขึ้นมา การลองใหม่ของ producer ยังคงคืน ID ของเอนทรีเดิม

### Functions และ ACL

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** จากหน้า functions: "Functions provide the same core functionality as scripts but are first-class software artifacts of the database." จากหน้า ACL เรื่อง selector: "If a command matches either the user permissions or any selector, it is allowed."

| การทดลอง | ผลลัพธ์ |
|---|---|
| `FCALL_RO stock` (ลงทะเบียนด้วย `no-writes`) | ทำงานได้ |
| `FCALL_RO sell` (เขียนข้อมูล) | `Can not execute a script with write flag using *_ro command` |
| `%R~catalog:* %W~events:*`: `GET` / `SET catalog:1` | อนุญาต / `NOPERM` |
| ผู้ใช้เดียวกัน: `XADD` / `XRANGE events:clicks` | อนุญาต / `NOPERM` |
| `~report:* +@read (~audit:* +xadd)`: `XADD audit:log` / `XADD report:log` | อนุญาต / `NOPERM` |
| `+@all -@write`: `JSON.GET` / `JSON.SET` / `TS.ADD` | อนุญาต / `NOPERM` / `NOPERM` |
| เฉพาะ `+@read`: `JSON.GET` | อนุญาต |

หน้า ACL ยังคงเขียนว่า "command categories, with the exception of +@all, never include module commands." บน Redis 8.10.3 ไม่เป็นเช่นนั้นอีกต่อไป: `ACL CAT write` แสดงคำสั่งของ JSON, time series และ probabilistic 47 คำสั่ง ACL ที่เขียนไว้สำหรับ Redis 7 อาจอนุญาตหรือบล็อกมากขึ้นหลังอัปเกรด เอกสาร: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/). แล็บ: [`deep-dive/08-functions-acl`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/08-functions-acl).

**Replica, dump, ไฟล์ ACL และ log** (`more.sh`) ไลบรารีที่โหลดบน primary ไปถึง replica; ที่นั่น `FCALL_RO` รันได้ ส่วน `FCALL` ของฟังก์ชันที่เขียนได้รับ `READONLY` `FUNCTION DUMP` และ `FUNCTION RESTORE` ย้ายไลบรารีไปยังเซิร์ฟเวอร์อื่นพร้อม flag `ACL SAVE` และ `ACL LOAD` ทำงานไปกลับกับไฟล์ ACL ได้ รวมถึงคอมเมนต์ `#` (Redis 8.8) และบรรทัดที่ผิดเพียงบรรทัดเดียวทำให้ `ACL LOAD` ทั้งคำสั่งล้มเหลวโดยไม่เปลี่ยนอะไรเลย `ACL LOG` บันทึกรหัสผ่านผิด คำสั่งที่ถูกปฏิเสธ และคีย์ที่ถูกปฏิเสธ พร้อมเหตุผลและผู้ใช้ของแต่ละรายการ

**ผู้ใช้ ACL ไม่ถูก replicate** (`acl_replica.sh`) ผู้ใช้ที่สร้างบน primary ไม่มีอยู่บน replica (`WRONGPASS`) ทั้งที่ข้อมูลมีอยู่ ให้ใช้ไฟล์ ACL เดียวกันบนทุกเซิร์ฟเวอร์

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: dijalankan.** Kedelapan mekanisme dijalankan pada Redis 8.10.3 di Docker lokal pada 2026-11-07 (di bawah).
</div>

Satu bagian per mekanisme, masing-masing berisi mekanisme dalam bahasa sederhana, tautan dokumentasi resmi, skrip yang menghasilkan angka atau hal yang dapat diamati, dan output hasil eksekusi: threading dan event loop (`io-threads`), persistensi (RDB, AOF, `BACKUP` sejak 8.10), replikasi / Sentinel / Cluster (`PSYNC`, failover, 16384 slot, `CLUSTER MIGRATION`), eviction dan memori (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer group, `IDMP`, `XNACK`), Functions dan ACL.

### Threading dan event loop

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** Perintah dijalankan pada satu thread utama; `io-threads` menyerahkan pembacaan permintaan dan penulisan balasan kepada thread pembantu. Beban `redis-benchmark` yang sama (SET/GET, nilai 64 byte, 400 klien, 12 thread benchmark) pada host 24 core:

| `io-threads` | Permintaan SET/GET per detik | Yang ditampilkan `INFO threads` |
|---|---|---|
| 1 | 134,523–136,097 | satu thread mengerjakan semuanya |
| 2 | 126,072–131,596 | thread utama tidak melakukan I/O klien; satu thread pembantu mengambil semuanya |
| 4 | 342,349–352,485 | pembacaan dan penulisan tersebar ke tiga thread pembantu |
| 8 | 498,753–520,472 | tersebar ke tujuh thread pembantu |

Dua thread tidak memberi hasil apa pun karena thread utama berhenti melakukan I/O klien begitu ada thread pembantu. Dokumentasi: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). Lab: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

**Pipelining dan TLS** (`more.sh`). Pada `-P 16`, empat thread I/O sudah menjadi batasnya: 1.14–1.26 M request/detik pada satu thread, 2.66–3.42 M pada empat, dan tidak bertambah pada delapan. Dengan TLS tanpa pipelining, jumlah thread paling berpengaruh: sekitar 90,000 request/detik pada satu thread (sepertiga lebih rendah daripada TCP biasa), sekitar 220,000 pada empat, 357,000–392,000 pada delapan, karena thread I/O juga mengerjakan enkripsi.

**Nilai 4 KB** (`values.sh`): sekitar 111,000, 285,000–307,000 dan 443,000 request/detik pada 1, 4 dan 8 thread, dengan pola yang sama seperti nilai 64 byte.

### Persistensi

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** Dari dokumentasi: "With the default policy of fsync every second, write performance is still great", dan "A backup reuses the multi-part AOF format".

| Eksperimen | Hasil |
|---|---|
| RDB fork, 214 MB di memori | 4–5 ms |
| Copy-on-write selama BGSAVE, tanpa penulisan | 2.2 MB |
| Copy-on-write selama BGSAVE, key ditimpa | 252 MB, lebih besar dari dataset |
| `appendfsync everysec` | 97,087 req/s, p50 0.119 ms, p99 0.255 ms |
| `appendfsync always` | 17,203 req/s, p50 1.159 ms, p99 1.527 ms |
| `BGREWRITEAOF` | RDB dasar 10 MB, file inkremental kosong, urutan manifest 2 |
| `BACKUP START` / `SEAL` (8.10) | file dasar, file inkremental, dan manifest dipatok sebagai hard link di `backupdir` |
| Restore dengan `--preload-file aof:<manifest>` | kedua key sebelum seal kembali; key yang ditulis setelah `SEAL` tidak ada |

Instance dengan banyak penulisan memerlukan ruang memori cadangan untuk snapshot. `preload-file` menghendaki `aof:` atau `rdb:` di depan nama file dan menolak path polos. Dokumentasi: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/). Lab: [`deep-dive/02-persistence`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/02-persistence).

### Replikasi dan Sentinel

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** Satu primary, dua replica, tiga Sentinel (quorum 2, `down-after-milliseconds` 3000). Dari dokumentasi: `WAIT` "will always return the number of replicas that acknowledged the write commands sent by the current client", dan "WAIT does not make Redis a strongly consistent store".

| Eksperimen | Hasil |
|---|---|
| Koneksi replica diputus | dua partial resync |
| Replica di-restart tanpa persistensi | satu full sync |
| `SET` + `WAIT 2 1000` pada satu koneksi, kedua replica aktif | 2 |
| Sama, satu replica dijeda | 1, setelah timeout 1 detik |
| `WAIT 2 1000` pada koneksi baru | 2 seketika: tidak ada penulisan miliknya yang perlu ditunggu |
| Primary dihentikan → Sentinel menunjuk master baru | 4,402 ms |
| Primary lama dijalankan kembali | menjadi replica dari master baru setelah 11.3 detik |
| Failover yang sama dengan Sentinel memantau nama container | 284,103 ms |

Baris terakhir adalah jebakannya: dengan hostname, nama container yang dihentikan tidak lagi dapat di-resolve di DNS Docker, Sentinel tersangkut pada pencarian itu dan saling menandai down. Berikan alamat yang tetap dapat di-resolve kepada Sentinel. Dokumentasi: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/). Lab: [`deep-dive/03-replication-sentinel`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/03-replication-sentinel).

**Klien yang sadar Sentinel** (`sentinel_client.py`). `Sentinel(...).master_for()` dari redis-py menulis ke primary baru 4.4 detik setelah primary lama dimatikan, tanpa perubahan kode, tetapi di antaranya mengembalikan `ConnectionError`, `TimeoutError` dan `MasterNotFoundError`, jadi pertahankan retry. Primary lama yang dihidupkan kembali menjawab sebagai `master` selama 11 detik sampai Sentinel mengubahnya menjadi replica: klien yang terhubung langsung ke sana dapat menulis dan kehilangan tulisan tersebut.

**Restart dan klien lain** (`persist.sh`, `sentinel_client.mjs`). Replica yang di-restart hanya melakukan partial resync dengan persistensi RDB dan shutdown yang normal; dengan AOF, atau setelah SIGKILL, replica melakukan full sync, seperti yang dikatakan halaman replikasi ("It is not possible to partially sync a replica that restarted via the AOF file"). `createSentinel()` dari node-redis tidak melempar error apa pun selama failover: ia menahan sebuah penulisan selama 6.1 detik sampai primary baru menjawab, sedangkan redis-py mengeluarkan error selama sekitar 4 detik.

### Cluster

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** Enam node, tiga primary dengan satu replica masing-masing. Dari spesifikasi: "Each master node in a cluster handles a subset of the 16384 hash slots", dengan `HASH_SLOT = CRC16(key) mod 16384`; hash tag "force certain keys to be stored in the same hash slot".

| Eksperimen | Hasil |
|---|---|
| `CLUSTER KEYSLOT user:1`, `user:2` | 10778, 6777 |
| `{user:1}:cart`, `{user:1}:orders` | keduanya 10778 |
| `GET user:2` pada node yang salah | `MOVED 6777 10.231.78.12:6379` |
| `MSET user:1 a user:2 b` | `CROSSSLOT` |
| `MSET` dengan hash tag bersama | `OK` |
| `CLUSTER MIGRATION IMPORT 0 999` (8.4) di bawah ~200,000 penulisan/detik | 1,000 slot dipindahkan dalam 44 ms, `write_pause_ms 0`, tanpa error klien |

Penolakan `CROSSSLOT` yang sama juga dikembalikan ElastiCache Serverless pada [halaman Compare]({{ '/compare/' | relative_url }}): rencanakan key yang digunakan bersama dengan hash tag yang sama. Dokumentasi: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/). Lab: [`deep-dive/04-cluster`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/04-cluster).

**Failover di dalam cluster** (`failover.py`). Sebuah primary dimatikan saat ada penulisan: dengan `cluster-node-timeout` default 15 detik, replica mengambil alih pada 19.3 detik dan klien tidak dapat menulis key milik primary itu selama sekitar 16 detik; dengan 3 detik, hasilnya 5.3 detik dan sekitar 4 detik. Pada kedua run, key di primary lain juga mendapat satu `ClusterDownError` selama sekitar 1 detik: sebelum replica mengambil alih, sebagian slot tidak punya pemilik, dan dengan `cluster-require-full-coverage yes` seluruh cluster menolak permintaan. Bandingkan dengan 1.3 detik pada operator Redis Enterprise di [halaman Enterprise]({{ '/enterprise/' | relative_url }}).

**Partisi jaringan** (`partition.py`). Sebuah primary yang terputus dari jaringan tetap menerima penulisan dari sisinya sendiri sampai node timeout 5 detik, lalu menjawab `CLUSTERDOWN`; setelah replica-nya mengambil alih dan node itu bergabung kembali, 21 penulisan tersebut hilang dan nilai milik mayoritas yang bertahan.

### Eviction dan memori

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** `maxmemory 16mb`, tiga grup masing-masing 5,000 key, lalu 30,000 key baru. Key *read-hot* dibaca lima kali dan tidak pernah ditulis ulang; key *write-hot* ditulis ulang lima kali dan tidak pernah dibaca. Dari dokumentasi: "allkeys-lrm : Evict the least recently modified (LRM) keys", dan "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently."

| Kebijakan | Read-hot tersisa | Write-hot tersisa | Cold tersisa | Artinya |
|---|---|---|---|---|
| `noeviction` | 5,000 | 5,000 | 5,000 | penulisan ditolak: `command not allowed when used memory > 'maxmemory'` |
| `allkeys-lru` | 621 | 614 | 356 | akses terakhir, baca atau tulis; key terbaru menang |
| `allkeys-lfu` | 5,000 | 5,000 | 2,117 | frekuensi baca dan tulis melindungi kedua grup panas |
| `allkeys-lrm` (8.6) | 368 | 3,318 | 431 | hanya penulisan yang melindungi key; pembacaan tidak |
| `allkeys-random` | 2,595 | 2,568 | 2,636 | sekitar setengah dari masing-masing |

LRU dan LRM mengambil sampel key, sehingga jumlahnya berubah antar-run; run sebelumnya menyisakan sekitar 3,200 dari setiap grup panas di bawah LRU. `HOTKEYS START METRICS 1 CPU` (8.6) menempatkan dua key yang paling sering dibaca skrip di peringkat pertama dan kedua. `INFO keysizes` memberikan histogram ukuran per tipe dengan kelipatan pangkat dua. Dokumentasi: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/). Lab: [`deep-dive/05-eviction`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/05-eviction).

**Kebijakan volatile dan `maxmemory-samples`** (`volatile.py`). Kebijakan volatile tidak pernah meng-evict key tanpa TTL; bila hanya ada key semacam itu, penulisan ditolak seperti pada `noeviction`. Di antara key ber-TTL, `volatile-lfu` dan `volatile-lru` mempertahankan key yang dibaca, sedangkan `volatile-ttl` mengambil yang paling singkat umurnya lebih dulu. Semakin banyak sampel, LRU semakin jelas mempertahankan key yang baru dibaca (10 sampel: sekitar 320 key terbaca berbanding 95 tidak terbaca yang bertahan, 5 sampel: 840 berbanding 630). Dengan 1 sampel, eviction tidak terkejar dan penulisan ditolak dengan OOM.

### Client-side caching

**Diverifikasi pada Redis 8.10.3 dengan redis-py 6.1.1, 2026-11-07.** Dari dokumentasi: "In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." Pada mode broadcasting, "the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

| Eksperimen | Hasil |
|---|---|
| redis-py `protocol=3`, `CacheConfig()`, 1,001 pembacaan satu key | 1 GET sampai ke server; 1,000 lainnya memakan 33.83 ms secara total |
| `SET` dari klien lain pada key itu | cache membuangnya; pembacaan berikutnya mengambil nilai baru satu kali |
| `CLIENT LIST` | flag `t` pada koneksi yang melakukan caching |
| `CLIENT TRACKING ON BCAST PREFIX user:`, lalu `SET` pada `user:2:name`, `order:9`, `user:3:cart` | push `invalidate` untuk dua key `user:`, tidak ada untuk `order:9` |

Tidak ada kode aplikasi yang menangani invalidasi: mengaktifkan cache di klien adalah seluruh perubahannya. Dokumentasi: [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/). Lab: [`deep-dive/06-client-side-caching`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/06-client-side-caching).

**OPTIN, OPTOUT, NOLOOP, RESP2** (`modes.py`). `OPTIN` hanya melacak pembacaan setelah `CLIENT CACHING YES`; `OPTOUT` melacak semuanya kecuali pembacaan setelah `CLIENT CACHING NO`. Tanpa `NOLOOP`, sebuah koneksi diberi tahu tentang penulisannya sendiri; dengan `NOLOOP`, tidak. Klien RESP2 tidak dapat menerima push, sehingga `CLIENT TRACKING ON REDIRECT <id>` mengirimkan invalidasi sebagai pesan Pub/Sub pada `__redis__:invalidate` ke koneksi lain.

### Streams

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** Sebuah stream `orders`, sebuah consumer group `shipping`, dan consumer `c1` yang membaca tiga entri lalu mati. Dari halaman perintah: XACKDEL bekerja "to both acknowledge entry processing and clean up the stream in a single atomic operation"; IDMP "Enables idempotent message processing (at-most-once production) to prevent duplicate entries"; pesan yang di-NACK "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

| Perintah | Masalah yang diselesaikan | Hasil |
|---|---|---|
| `XAUTOCLAIM orders shipping c2 100 0-0` (6.2) | entri yang tersangkut pada consumer yang sudah mati | `c2` mengambil ketiga entri milik `c1`; jumlah pengiriman 1 → 2 |
| `XACKDEL orders shipping IDS 2 0-1 0-2` (8.2) | `XACK` lalu `XDEL`, dua panggilan dengan celah di antaranya | membalas `1, 1`; `XLEN` 5 → 3 |
| `XADD payments IDMP svc-a req-42 * …` dua kali (8.6) | retry producer yang menulis entri duplikat | ID yang sama kedua kalinya; `XLEN` tetap 1 |
| `XNACK orders shipping FAIL IDS 1 0-4` (8.8) | consumer mengembalikan pesan sebelum idle timeout-nya habis | entri tidak lagi dimiliki siapa pun, hitungan tetap 1 |

Setelah `XNACK`, `XREADGROUP … >` yang baru tidak mengembalikan entri itu: `>` hanya membaca entri baru. `XAUTOCLAIM` dengan idle time minimum 60 detik langsung mengklaimnya dan membiarkan entri pending lainnya tetap pada pemiliknya. Jadi XNACK mempercepat pemulihan, dan pemulihan tetap lewat `XAUTOCLAIM` atau `XCLAIM`. Dokumentasi: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/). Lab: [`deep-dive/07-streams`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/07-streams).

**Opsi lainnya** (`more.sh`). `XNACK` setelah satu pengiriman: count `SILENT` 0, `FAIL` 1, `FATAL` 9223372036854775807, `RETRYCOUNT 5` 5; `FORCE` menambahkan entri yang belum dibaca siapa pun ke pending list. `IDMPAUTO` mendeduplikasi berdasarkan isi. `XCFGSET` menghapus riwayat IDMP, sehingga percobaan ulang yang dikirim tepat sesudahnya diterima; `IDMP-DURATION` dan `IDMP-MAXSIZE` membatasi berapa lama dan berapa banyak ID yang diingat. Dengan dua group, `XACKDEL KEEPREF` menghapus entri dan meninggalkan referensi ke ketiadaan bagi group lainnya, `DELREF` menghapus referensi itu, dan `ACKED` hanya menghapus bila setiap group telah mengakui.

**IDMP dan failover** (`idmp_replica.sh`). Idempotency map direplikasi: setelah primary dimatikan dan replica dipromosikan, retry dari producer tetap mengembalikan ID entri yang asli.

### Functions dan ACL

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** Dari halaman functions: "Functions provide the same core functionality as scripts but are first-class software artifacts of the database." Dari halaman ACL tentang selector: "If a command matches either the user permissions or any selector, it is allowed."

| Eksperimen | Hasil |
|---|---|
| `FCALL_RO stock` (didaftarkan dengan `no-writes`) | berjalan |
| `FCALL_RO sell` (menulis) | `Can not execute a script with write flag using *_ro command` |
| `%R~catalog:* %W~events:*`: `GET` / `SET catalog:1` | diizinkan / `NOPERM` |
| pengguna yang sama: `XADD` / `XRANGE events:clicks` | diizinkan / `NOPERM` |
| `~report:* +@read (~audit:* +xadd)`: `XADD audit:log` / `XADD report:log` | diizinkan / `NOPERM` |
| `+@all -@write`: `JSON.GET` / `JSON.SET` / `TS.ADD` | diizinkan / `NOPERM` / `NOPERM` |
| hanya `+@read`: `JSON.GET` | diizinkan |

Halaman ACL masih menyatakan "command categories, with the exception of +@all, never include module commands." Pada Redis 8.10.3 hal itu tidak lagi berlaku: `ACL CAT write` mencantumkan 47 perintah JSON, time series, dan probabilistik. ACL yang ditulis untuk Redis 7 dapat mengizinkan atau memblokir lebih banyak setelah upgrade. Dokumentasi: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/). Lab: [`deep-dive/08-functions-acl`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/08-functions-acl).

**Replica, dump, file ACL, dan log** (`more.sh`). Library yang dimuat di primary sampai ke replica; di sana `FCALL_RO` berjalan dan `FCALL` untuk fungsi yang menulis mendapat `READONLY`. `FUNCTION DUMP` dan `FUNCTION RESTORE` memindahkan library ke server lain beserta flag-nya. `ACL SAVE` dan `ACL LOAD` bolak-balik dengan file ACL, termasuk komentar `#` (Redis 8.8), dan satu baris yang salah membuat seluruh `ACL LOAD` gagal tanpa mengubah apa pun. `ACL LOG` mencatat password yang salah, perintah yang ditolak, dan key yang ditolak, masing-masing dengan alasan dan user-nya.

**User ACL tidak direplikasi** (`acl_replica.sh`). User yang dibuat di primary tidak ada di replica (`WRONGPASS`), padahal datanya ada; gunakan file ACL yang sama di setiap server.

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: dijalankan.** Kesemua lapan mekanisme dijalankan pada Redis 8.10.3 dalam Docker setempat pada 2026-11-07 (di bawah).
</div>

Satu bahagian bagi setiap mekanisme, masing-masing mengandungi mekanisme dalam bahasa mudah, pautan dokumentasi rasmi, skrip yang menghasilkan nombor atau perkara yang boleh diperhatikan, dan output seperti yang dijalankan: threading dan event loop (`io-threads`), kegigihan data (RDB, AOF, `BACKUP` sejak 8.10), replikasi / Sentinel / Cluster (`PSYNC`, failover, 16384 slot, `CLUSTER MIGRATION`), eviction dan memori (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer group, `IDMP`, `XNACK`), Functions dan ACL.

### Threading dan event loop

**Disahkan pada Redis 8.10.3, 2026-11-07.** Arahan dijalankan pada satu thread utama; `io-threads` menyerahkan pembacaan permintaan dan penulisan balasan kepada thread pembantu. Beban `redis-benchmark` yang sama (SET/GET, nilai 64 bait, 400 klien, 12 thread penanda aras) pada hos 24 teras:

| `io-threads` | Permintaan SET/GET sesaat | Apa yang dipaparkan `INFO threads` |
|---|---|---|
| 1 | 134,523–136,097 | satu thread melakukan semuanya |
| 2 | 126,072–131,596 | thread utama tidak melakukan I/O klien; satu thread pembantu mengambil alih semuanya |
| 4 | 342,349–352,485 | bacaan dan tulisan diagihkan kepada tiga thread pembantu |
| 8 | 498,753–520,472 | diagihkan kepada tujuh thread pembantu |

Dua thread tidak memberi apa-apa kerana thread utama berhenti melakukan I/O klien sebaik sahaja thread pembantu wujud. Dokumentasi: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). Makmal: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

**Pipelining dan TLS** (`more.sh`). Pada `-P 16`, empat thread I/O sudah menjadi had atasnya: 1.14–1.26 M permintaan/saat pada satu thread, 2.66–3.42 M pada empat, dan tidak bertambah pada lapan. Dengan TLS tanpa pipelining, bilangan thread paling berpengaruh: kira-kira 90,000 permintaan/saat pada satu thread (satu pertiga lebih rendah daripada TCP biasa), kira-kira 220,000 pada empat, 357,000–392,000 pada lapan, kerana thread I/O turut melakukan penyulitan.

**Nilai 4 KB** (`values.sh`): kira-kira 111,000, 285,000–307,000 dan 443,000 permintaan/saat pada 1, 4 dan 8 thread, dengan corak yang sama seperti nilai 64 bait.

### Kegigihan data

**Disahkan pada Redis 8.10.3, 2026-11-07.** Daripada dokumentasi: "With the default policy of fsync every second, write performance is still great", dan "A backup reuses the multi-part AOF format".

| Eksperimen | Keputusan |
|---|---|
| RDB fork, 214 MB dalam memori | 4–5 ms |
| Copy-on-write semasa BGSAVE, tiada penulisan | 2.2 MB |
| Copy-on-write semasa BGSAVE, kunci ditulis ganti | 252 MB, lebih besar daripada set data |
| `appendfsync everysec` | 97,087 req/s, p50 0.119 ms, p99 0.255 ms |
| `appendfsync always` | 17,203 req/s, p50 1.159 ms, p99 1.527 ms |
| `BGREWRITEAOF` | RDB asas 10 MB, fail incremental kosong, jujukan manifest 2 |
| `BACKUP START` / `SEAL` (8.10) | fail asas, fail incremental dan manifest dikunci sebagai hard link dalam `backupdir` |
| Pulihkan dengan `--preload-file aof:<manifest>` | kedua-dua kunci sebelum seal kembali; kunci yang ditulis selepas `SEAL` tiada |

Instance yang banyak menulis memerlukan ruang memori lebihan untuk snapshot. `preload-file` mahu `aof:` atau `rdb:` di hadapan nama fail dan menolak laluan kosong. Dokumentasi: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/). Makmal: [`deep-dive/02-persistence`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/02-persistence).

### Replikasi dan Sentinel

**Disahkan pada Redis 8.10.3, 2026-11-07.** Satu primary, dua replica, tiga Sentinel (quorum 2, `down-after-milliseconds` 3000). Daripada dokumentasi: `WAIT` "will always return the number of replicas that acknowledged the write commands sent by the current client", dan "WAIT does not make Redis a strongly consistent store".

| Eksperimen | Keputusan |
|---|---|
| Sambungan replica diputuskan | dua partial resync |
| Replica dimulakan semula tanpa kegigihan data | satu full sync |
| `SET` + `WAIT 2 1000` pada satu sambungan, kedua-dua replica aktif | 2 |
| Sama, satu replica dijeda | 1, selepas tamat masa 1 saat |
| `WAIT 2 1000` pada sambungan baharu | 2 serta-merta: tiada penulisan sendiri untuk ditunggu |
| Primary dihentikan → Sentinel menamakan master baharu | 4,402 ms |
| Primary lama dimulakan semula | menjadi replica kepada master baharu selepas 11.3 saat |
| Failover yang sama dengan Sentinel memantau nama container | 284,103 ms |

Baris terakhir ialah perangkapnya: dengan nama hos, nama container yang dihentikan tidak lagi dapat diselesaikan dalam DNS Docker, Sentinel tersekat pada carian itu dan saling menandakan down. Berikan alamat yang kekal boleh diselesaikan kepada Sentinel. Dokumentasi: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/). Makmal: [`deep-dive/03-replication-sentinel`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/03-replication-sentinel).

**Klien yang peka Sentinel** (`sentinel_client.py`). `Sentinel(...).master_for()` daripada redis-py menulis ke primary baharu 4.4 saat selepas primary lama dimatikan, tanpa perubahan kod, tetapi di antaranya mengembalikan `ConnectionError`, `TimeoutError` dan `MasterNotFoundError`, jadi kekalkan percubaan semula. Primary lama yang dimulakan semula menjawab sebagai `master` selama 11 saat sehingga Sentinel menukarnya menjadi replica: klien yang bersambung terus kepadanya boleh menulis di situ dan kehilangan tulisan tersebut.

**Mulakan semula dan klien lain** (`persist.sh`, `sentinel_client.mjs`). Replica yang dimulakan semula hanya melakukan partial resync dengan kegigihan data RDB dan penutupan yang teratur; dengan AOF, atau selepas SIGKILL, ia melakukan full sync, seperti yang dinyatakan halaman replikasi ("It is not possible to partially sync a replica that restarted via the AOF file"). `createSentinel()` daripada node-redis tidak melemparkan sebarang ralat semasa failover: ia menahan satu penulisan selama 6.1 saat sehingga primary baharu menjawab, manakala redis-py mengeluarkan ralat selama kira-kira 4 saat.

### Cluster

**Disahkan pada Redis 8.10.3, 2026-11-07.** Enam nod, tiga primary dengan satu replica setiap satu. Daripada spesifikasi: "Each master node in a cluster handles a subset of the 16384 hash slots", dengan `HASH_SLOT = CRC16(key) mod 16384`; hash tag "force certain keys to be stored in the same hash slot".

| Eksperimen | Keputusan |
|---|---|
| `CLUSTER KEYSLOT user:1`, `user:2` | 10778, 6777 |
| `{user:1}:cart`, `{user:1}:orders` | kedua-duanya 10778 |
| `GET user:2` pada nod yang salah | `MOVED 6777 10.231.78.12:6379` |
| `MSET user:1 a user:2 b` | `CROSSSLOT` |
| `MSET` dengan hash tag yang dikongsi | `OK` |
| `CLUSTER MIGRATION IMPORT 0 999` (8.4) di bawah ~200,000 penulisan/saat | 1,000 slot dipindahkan dalam 44 ms, `write_pause_ms 0`, tiada ralat klien |

Penolakan `CROSSSLOT` yang sama juga dikembalikan oleh ElastiCache Serverless pada [halaman Compare]({{ '/compare/' | relative_url }}): rancang kunci yang digunakan bersama dengan hash tag yang dikongsi. Dokumentasi: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/). Makmal: [`deep-dive/04-cluster`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/04-cluster).

**Failover di dalam cluster** (`failover.py`). Sebuah primary dimatikan semasa penulisan: dengan `cluster-node-timeout` lalai 15 saat, replica mengambil alih pada 19.3 saat dan klien tidak dapat menulis kunci milik primary itu selama kira-kira 16 saat; dengan 3 saat, hasilnya 5.3 saat dan kira-kira 4 saat. Dalam kedua-dua larian, kunci pada primary lain juga mendapat satu `ClusterDownError` selama kira-kira 1 saat: sebelum replica mengambil alih, sesetengah slot tiada pemilik, dan dengan `cluster-require-full-coverage yes` seluruh cluster menolak permintaan. Bandingkan dengan 1.3 saat bagi operator Redis Enterprise pada [halaman Enterprise]({{ '/enterprise/' | relative_url }}).

**Partition rangkaian** (`partition.py`). Sebuah primary yang terputus daripada rangkaian terus menerima penulisan dari sisinya sendiri sehingga node timeout 5 saat, kemudian menjawab `CLUSTERDOWN`; selepas replica-nya mengambil alih dan nod itu menyertai semula, 21 penulisan itu hilang dan nilai pihak majoriti kekal.

### Eviction dan memori

**Disahkan pada Redis 8.10.3, 2026-11-07.** `maxmemory 16mb`, tiga kumpulan masing-masing 5,000 kunci, kemudian 30,000 kunci baharu. Kunci *read-hot* dibaca lima kali dan tidak pernah ditulis semula; kunci *write-hot* ditulis semula lima kali dan tidak pernah dibaca. Daripada dokumentasi: "allkeys-lrm : Evict the least recently modified (LRM) keys", dan "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently."

| Dasar | Read-hot berbaki | Write-hot berbaki | Cold berbaki | Maksudnya |
|---|---|---|---|---|
| `noeviction` | 5,000 | 5,000 | 5,000 | penulisan ditolak: `command not allowed when used memory > 'maxmemory'` |
| `allkeys-lru` | 621 | 614 | 356 | capaian terakhir, baca atau tulis; kunci terbaharu menang |
| `allkeys-lfu` | 5,000 | 5,000 | 2,117 | kekerapan baca dan tulis melindungi kedua-dua kumpulan panas |
| `allkeys-lrm` (8.6) | 368 | 3,318 | 431 | hanya penulisan yang melindungi kunci; bacaan tidak |
| `allkeys-random` | 2,595 | 2,568 | 2,636 | kira-kira separuh bagi setiap satu |

LRU dan LRM mengambil sampel kunci, jadi bilangannya berubah antara larian; satu larian terdahulu mengekalkan kira-kira 3,200 bagi setiap kumpulan panas di bawah LRU. `HOTKEYS START METRICS 1 CPU` (8.6) meletakkan dua kunci yang paling banyak dibaca skrip di tempat pertama dan kedua. `INFO keysizes` memberikan histogram saiz kuasa dua bagi setiap jenis. Dokumentasi: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/). Makmal: [`deep-dive/05-eviction`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/05-eviction).

**Dasar volatile dan `maxmemory-samples`** (`volatile.py`). Dasar volatile tidak pernah menyingkirkan kunci tanpa TTL (eviction); apabila hanya ada kunci sebegitu, penulisan ditolak seperti pada `noeviction`. Dalam kalangan kunci ber-TTL, `volatile-lfu` dan `volatile-lru` mengekalkan kunci yang dibaca, manakala `volatile-ttl` mengambil yang paling singkat hayatnya dahulu. Semakin banyak sampel, LRU semakin jelas mengekalkan kunci yang baru dibaca (10 sampel: kira-kira 320 kunci terbaca berbanding 95 tidak terbaca yang kekal, 5 sampel: 840 berbanding 630). Dengan 1 sampel, eviction tidak sempat mengejar dan penulisan ditolak dengan OOM.

### Client-side caching

**Disahkan pada Redis 8.10.3 dengan redis-py 6.1.1, 2026-11-07.** Daripada dokumentasi: "In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." Dalam mod broadcasting, "the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

| Eksperimen | Keputusan |
|---|---|
| redis-py `protocol=3`, `CacheConfig()`, 1,001 bacaan satu kunci | 1 GET sampai ke pelayan; 1,000 yang lain mengambil 33.83 ms secara keseluruhan |
| `SET` daripada klien lain pada kunci itu | cache membuangnya; bacaan seterusnya mengambil nilai baharu sekali |
| `CLIENT LIST` | bendera `t` pada sambungan yang melakukan caching |
| `CLIENT TRACKING ON BCAST PREFIX user:`, kemudian `SET` pada `user:2:name`, `order:9`, `user:3:cart` | push `invalidate` untuk dua kunci `user:`, tiada untuk `order:9` |

Tiada kod aplikasi yang mengendalikan invalidasi: menghidupkan cache pada klien ialah keseluruhan perubahannya. Dokumentasi: [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/). Makmal: [`deep-dive/06-client-side-caching`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/06-client-side-caching).

**OPTIN, OPTOUT, NOLOOP, RESP2** (`modes.py`). `OPTIN` hanya menjejak bacaan selepas `CLIENT CACHING YES`; `OPTOUT` menjejak semuanya kecuali bacaan selepas `CLIENT CACHING NO`. Tanpa `NOLOOP`, sesuatu sambungan diberitahu tentang tulisannya sendiri; dengan `NOLOOP`, tidak. Klien RESP2 tidak dapat menerima push, jadi `CLIENT TRACKING ON REDIRECT <id>` menghantar invalidasi sebagai mesej Pub/Sub pada `__redis__:invalidate` ke sambungan lain.

### Streams

**Disahkan pada Redis 8.10.3, 2026-11-07.** Satu stream `orders`, satu consumer group `shipping`, dan consumer `c1` yang membaca tiga entri lalu mati. Daripada halaman arahan: XACKDEL bertindak "to both acknowledge entry processing and clean up the stream in a single atomic operation"; IDMP "Enables idempotent message processing (at-most-once production) to prevent duplicate entries"; mesej yang di-NACK "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

| Arahan | Masalah yang diselesaikan | Keputusan |
|---|---|---|
| `XAUTOCLAIM orders shipping c2 100 0-0` (6.2) | entri yang tersangkut pada consumer yang sudah mati | `c2` mengambil ketiga-tiga entri milik `c1`; kiraan penghantaran 1 → 2 |
| `XACKDEL orders shipping IDS 2 0-1 0-2` (8.2) | `XACK` kemudian `XDEL`, dua panggilan dengan jurang di antaranya | membalas `1, 1`; `XLEN` 5 → 3 |
| `XADD payments IDMP svc-a req-42 * …` dua kali (8.6) | percubaan semula producer yang menulis entri pendua | ID yang sama kedua-dua kali; `XLEN` kekal 1 |
| `XNACK orders shipping FAIL IDS 1 0-4` (8.8) | consumer memulangkan mesej sebelum idle timeout tamat | entri tidak dimiliki sesiapa, kiraan kekal 1 |

Selepas `XNACK`, `XREADGROUP … >` yang baharu tidak mengembalikan entri itu: `>` hanya membaca entri baharu. `XAUTOCLAIM` dengan idle time minimum 60 saat menuntutnya serta-merta dan membiarkan entri pending yang lain kekal pada pemiliknya. Jadi XNACK mempercepat pemulihan, dan pemulihan masih melalui `XAUTOCLAIM` atau `XCLAIM`. Dokumentasi: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/). Makmal: [`deep-dive/07-streams`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/07-streams).

**Pilihan selebihnya** (`more.sh`). `XNACK` selepas satu penghantaran: kiraan `SILENT` 0, `FAIL` 1, `FATAL` 9223372036854775807, `RETRYCOUNT 5` 5; `FORCE` menambah entri yang belum dibaca sesiapa ke dalam pending list. `IDMPAUTO` menyahduplikasi mengikut kandungan. `XCFGSET` memadam sejarah IDMP, jadi percubaan semula yang dihantar sejurus selepasnya diterima; `IDMP-DURATION` dan `IDMP-MAXSIZE` mengehadkan berapa lama dan berapa banyak ID yang diingat. Dengan dua group, `XACKDEL KEEPREF` memadam entri dan meninggalkan rujukan kepada ketiadaan bagi group yang lain, `DELREF` membuang rujukan itu, dan `ACKED` hanya memadam apabila setiap group telah mengakui.

**IDMP dan failover** (`idmp_replica.sh`). Idempotency map direplikasi: selepas primary dimatikan dan replica dinaikkan taraf, percubaan semula producer masih memulangkan ID entri yang asal.

### Functions dan ACL

**Disahkan pada Redis 8.10.3, 2026-11-07.** Daripada halaman functions: "Functions provide the same core functionality as scripts but are first-class software artifacts of the database." Daripada halaman ACL tentang selector: "If a command matches either the user permissions or any selector, it is allowed."

| Eksperimen | Keputusan |
|---|---|
| `FCALL_RO stock` (didaftarkan dengan `no-writes`) | berjalan |
| `FCALL_RO sell` (menulis) | `Can not execute a script with write flag using *_ro command` |
| `%R~catalog:* %W~events:*`: `GET` / `SET catalog:1` | dibenarkan / `NOPERM` |
| pengguna yang sama: `XADD` / `XRANGE events:clicks` | dibenarkan / `NOPERM` |
| `~report:* +@read (~audit:* +xadd)`: `XADD audit:log` / `XADD report:log` | dibenarkan / `NOPERM` |
| `+@all -@write`: `JSON.GET` / `JSON.SET` / `TS.ADD` | dibenarkan / `NOPERM` / `NOPERM` |
| hanya `+@read`: `JSON.GET` | dibenarkan |

Halaman ACL masih menyatakan "command categories, with the exception of +@all, never include module commands." Pada Redis 8.10.3 perkara itu tidak lagi benar: `ACL CAT write` menyenaraikan 47 arahan JSON, time series dan probabilistik. ACL yang ditulis untuk Redis 7 boleh membenarkan atau menyekat lebih banyak selepas peningkatan. Dokumentasi: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/). Makmal: [`deep-dive/08-functions-acl`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/08-functions-acl).

**Replica, dump, fail ACL dan log** (`more.sh`). Pustaka yang dimuatkan pada primary sampai ke replica; di sana `FCALL_RO` berjalan dan `FCALL` bagi fungsi yang menulis mendapat `READONLY`. `FUNCTION DUMP` dan `FUNCTION RESTORE` memindahkan pustaka ke pelayan lain bersama bendera-nya. `ACL SAVE` dan `ACL LOAD` pergi-balik dengan fail ACL, termasuk ulasan `#` (Redis 8.8), dan satu baris yang salah menyebabkan seluruh `ACL LOAD` gagal tanpa mengubah apa-apa. `ACL LOG` merekod kata laluan yang salah, perintah yang ditolak dan kunci yang ditolak, masing-masing dengan sebab dan penggunanya.

**Pengguna ACL tidak direplikasi** (`acl_replica.sh`). Pengguna yang dicipta pada primary tidak wujud pada replica (`WRONGPASS`), walaupun datanya wujud; gunakan fail ACL yang sama pada setiap pelayan.

</div>
