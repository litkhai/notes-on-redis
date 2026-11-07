---
layout: default
title: Deep Dive
permalink: /deep-dive/
---

# Deep Dive

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: partly run.** Threading, persistence, replication with Sentinel, and cluster were run on 2026-11-07 (below). Eviction, client-side caching, Streams, and Functions with ACL are still the plan in [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

One page per mechanism, each with the mechanism in plain words, the official doc link, a script that produces a number or an observable, and the output as run: threading and the event loop (`io-threads`), persistence (RDB, AOF, `BACKUP` since 8.10), replication / Sentinel / Cluster (`PSYNC`, failover, 16384 slots, `CLUSTER MIGRATION`), eviction and memory (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer groups, `IDMP`, `XNACK`), Functions and ACL.

### Threading and the event loop

**Verified on Redis 8.10.3, 2026-11-07.** Commands run on one main thread; `io-threads` hands request reading and reply writing to helper threads. Same `redis-benchmark` load (SET/GET, 64-byte values, 400 clients, 12 benchmark threads) on a 24-core host:

| `io-threads` | SET/GET requests/s | What `INFO threads` showed |
|---|---|---|
| 1 | 134,523–136,097 | one thread does everything |
| 2 | 126,072–131,596 | the main thread did no client I/O; one helper took it all |
| 4 | 342,349–352,485 | reads and writes spread over three helpers |
| 8 | 498,753–520,472 | spread over seven helpers |

Two threads gave nothing because the main thread stops doing client I/O once helpers exist. Docs: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). Lab: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

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

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 일부 실행.** 스레딩, 영속성, Sentinel을 곁들인 복제, 클러스터를 2026-11-07에 실행했다(아래). 축출, 클라이언트 측 캐시, Streams, Functions와 ACL은 아직 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)의 계획이다.
</div>

메커니즘당 한 페이지 — 평이한 설명, 공식 문서 링크, 숫자나 관찰을 만드는 스크립트, 실행한 출력: 스레딩과 이벤트 루프(`io-threads`), 영속성(RDB, AOF, 8.10의 `BACKUP`), 복제 / Sentinel / Cluster(`PSYNC`, 페일오버, 16384 슬롯, `CLUSTER MIGRATION`), 축출과 메모리(LRU / LFU / LRM, `HOTKEYS`), 클라이언트 캐시(`CLIENT TRACKING`), Streams(컨슈머 그룹, `IDMP`, `XNACK`), Functions와 ACL.

### 스레딩과 이벤트 루프

**확인: Redis 8.10.3, 2026-11-07.** 명령은 메인 스레드 하나에서 실행된다. `io-threads`는 요청 읽기와 응답 쓰기를 보조 스레드에 넘긴다. 24코어 호스트에서 같은 `redis-benchmark` 부하(SET/GET, 64바이트 값, 클라이언트 400, 벤치마크 스레드 12):

| `io-threads` | SET/GET 초당 요청 | `INFO threads`가 보인 것 |
|---|---|---|
| 1 | 134,523–136,097 | 스레드 하나가 전부 처리 |
| 2 | 126,072–131,596 | 메인 스레드는 클라이언트 I/O를 안 하고 보조 하나가 전부 맡음 |
| 4 | 342,349–352,485 | 보조 셋에 읽기·쓰기 분산 |
| 8 | 498,753–520,472 | 보조 일곱에 분산 |

스레드 둘이 효과가 없던 이유는 보조 스레드가 생기면 메인 스레드가 클라이언트 I/O를 그만두기 때문이다. 문서: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). 실습: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

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

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：部分已运行。** 线程、持久化、带 Sentinel 的复制和集群已于 2026-11-07 运行（见下）。淘汰、客户端缓存、Streams，以及带 ACL 的 Functions 仍是 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) 中的计划。
</div>

每个机制一页 — 通俗说明、官方文档链接、产生数字或可观察结果的脚本、实际运行输出：线程与事件循环（`io-threads`）、持久化（RDB、AOF、8.10 的 `BACKUP`）、复制 / Sentinel / Cluster（`PSYNC`、故障转移、16384 个槽、`CLUSTER MIGRATION`）、淘汰与内存（LRU / LFU / LRM、`HOTKEYS`）、客户端缓存（`CLIENT TRACKING`）、Streams（消费者组、`IDMP`、`XNACK`）、Functions 与 ACL。

### 线程与事件循环

**已在 Redis 8.10.3 上验证，2026-11-07。** 命令在一个主线程上执行；`io-threads` 把读取请求和写回响应交给辅助线程。相同的 `redis-benchmark` 负载（SET/GET，64 字节的值，400 个客户端，12 个基准测试线程），在 24 核主机上：

| `io-threads` | SET/GET 每秒请求数 | `INFO threads` 显示的情况 |
|---|---|---|
| 1 | 134,523–136,097 | 一个线程包办所有工作 |
| 2 | 126,072–131,596 | 主线程不做任何客户端 I/O；一个辅助线程全部承担 |
| 4 | 342,349–352,485 | 读写分散到三个辅助线程 |
| 8 | 498,753–520,472 | 分散到七个辅助线程 |

两个线程没有任何提升，因为一旦有了辅助线程，主线程就不再做客户端 I/O。 文档: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). 实验: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

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

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**状況：一部実行済み。** スレッド、永続化、Sentinel 付きレプリケーション、クラスターは 2026-11-07 に実行した（下記）。エビクション、クライアントサイドキャッシュ、Streams、ACL 付き Functions は、まだ [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) の計画段階である。
</div>

仕組みごとに一ページ — 平易な説明、公式ドキュメントへのリンク、数値や観察結果を生むスクリプト、実行した出力: スレッドとイベントループ（`io-threads`）、永続化（RDB、AOF、8.10 の `BACKUP`）、レプリケーション / Sentinel / Cluster（`PSYNC`、フェイルオーバー、16384 スロット、`CLUSTER MIGRATION`）、エビクションとメモリ（LRU / LFU / LRM、`HOTKEYS`）、クライアントサイドキャッシュ（`CLIENT TRACKING`）、Streams（コンシューマーグループ、`IDMP`、`XNACK`）、Functions と ACL。

### スレッドとイベントループ

**Redis 8.10.3 で検証、2026-11-07。** コマンドは 1 本のメインスレッドで実行される。`io-threads` はリクエストの読み取りと応答の書き込みをヘルパースレッドに任せる。24 コアのホストで、同じ `redis-benchmark` 負荷（SET/GET、64 バイトの値、400 クライアント、ベンチマークスレッド 12 本）をかけた結果：

| `io-threads` | SET/GET リクエスト/秒 | `INFO threads` の表示 |
|---|---|---|
| 1 | 134,523–136,097 | 1 本のスレッドがすべてを処理 |
| 2 | 126,072–131,596 | メインスレッドはクライアント I/O を行わず、ヘルパー 1 本がすべて担当 |
| 4 | 342,349–352,485 | 読み書きが 3 本のヘルパーに分散 |
| 8 | 498,753–520,472 | 7 本のヘルパーに分散 |

2 スレッドでは何も得られなかった。ヘルパーがあるとメインスレッドがクライアント I/O をやめるためである。 ドキュメント: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). ラボ: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

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

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: รันแล้วบางส่วน** เธรด การคงอยู่ของข้อมูล การทำ replication ร่วมกับ Sentinel และคลัสเตอร์ รันเมื่อ 2026-11-07 (ด้านล่าง) ส่วน eviction, client-side caching, Streams และ Functions ร่วมกับ ACL ยังเป็นแผนใน [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)
</div>

หนึ่งหน้าต่อหนึ่งกลไก แต่ละหน้ามีคำอธิบายกลไกด้วยภาษาง่ายๆ ลิงก์เอกสารทางการ สคริปต์ที่ให้ตัวเลขหรือสิ่งที่สังเกตได้ และผลลัพธ์จากการรันจริง ได้แก่ threading และ event loop (`io-threads`), persistence (RDB, AOF, `BACKUP` ตั้งแต่ 8.10), replication / Sentinel / Cluster (`PSYNC`, failover, 16384 slots, `CLUSTER MIGRATION`), eviction และหน่วยความจำ (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer groups, `IDMP`, `XNACK`), Functions และ ACL

### เธรดและ event loop

**ตรวจสอบบน Redis 8.10.3, 2026-11-07** คำสั่งทำงานบนเธรดหลักเธรดเดียว `io-threads` ส่งการอ่านคำขอและการเขียนคำตอบให้เธรดช่วย โหลด `redis-benchmark` เดียวกัน (SET/GET, ค่าขนาด 64 ไบต์, 400 ไคลเอนต์, เธรดเบนช์มาร์ก 12 เธรด) บนโฮสต์ 24 คอร์:

| `io-threads` | คำขอ SET/GET ต่อวินาที | สิ่งที่ `INFO threads` แสดง |
|---|---|---|
| 1 | 134,523–136,097 | เธรดเดียวทำทุกอย่าง |
| 2 | 126,072–131,596 | เธรดหลักไม่ทำ I/O ของไคลเอนต์เลย เธรดช่วยหนึ่งเธรดรับไปทั้งหมด |
| 4 | 342,349–352,485 | การอ่านและเขียนกระจายไปยังเธรดช่วยสามเธรด |
| 8 | 498,753–520,472 | กระจายไปยังเธรดช่วยเจ็ดเธรด |

สองเธรดไม่ได้ผลอะไรเลย เพราะเมื่อมีเธรดช่วยแล้ว เธรดหลักจะหยุดทำ I/O ของไคลเอนต์ เอกสาร: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). แล็บ: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

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

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: sebagian sudah dijalankan.** Threading, persistensi, replikasi dengan Sentinel, dan cluster dijalankan pada 2026-11-07 (di bawah). Eviction, client-side caching, Streams, serta Functions dengan ACL masih berupa rencana di [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Satu halaman per mekanisme, masing-masing berisi penjelasan mekanisme dengan kata-kata sederhana, tautan dokumen resmi, skrip yang menghasilkan angka atau hal yang dapat diamati, dan keluaran dari hasil eksekusi: threading dan event loop (`io-threads`), persistence (RDB, AOF, `BACKUP` sejak 8.10), replication / Sentinel / Cluster (`PSYNC`, failover, 16384 slot, `CLUSTER MIGRATION`), eviction dan memori (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer groups, `IDMP`, `XNACK`), Functions dan ACL.

### Threading dan event loop

**Diverifikasi pada Redis 8.10.3, 2026-11-07.** Perintah dijalankan pada satu thread utama; `io-threads` menyerahkan pembacaan permintaan dan penulisan balasan kepada thread pembantu. Beban `redis-benchmark` yang sama (SET/GET, nilai 64 byte, 400 klien, 12 thread benchmark) pada host 24 core:

| `io-threads` | Permintaan SET/GET per detik | Yang ditampilkan `INFO threads` |
|---|---|---|
| 1 | 134,523–136,097 | satu thread mengerjakan semuanya |
| 2 | 126,072–131,596 | thread utama tidak melakukan I/O klien; satu thread pembantu mengambil semuanya |
| 4 | 342,349–352,485 | pembacaan dan penulisan tersebar ke tiga thread pembantu |
| 8 | 498,753–520,472 | tersebar ke tujuh thread pembantu |

Dua thread tidak memberi hasil apa pun karena thread utama berhenti melakukan I/O klien begitu ada thread pembantu. Dokumentasi: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). Lab: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

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

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: sebahagian telah dijalankan.** Threading, kegigihan data, replikasi dengan Sentinel dan cluster telah dijalankan pada 2026-11-07 (di bawah). Eviction, client-side caching, Streams, serta Functions dengan ACL masih merupakan rancangan dalam [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Satu halaman bagi setiap mekanisme, setiap satu mengandungi penerangan mekanisme dalam bahasa mudah, pautan dokumen rasmi, skrip yang menghasilkan nombor atau sesuatu yang boleh diperhatikan, dan output hasil larian: threading dan event loop (`io-threads`), persistence (RDB, AOF, `BACKUP` sejak 8.10), replication / Sentinel / Cluster (`PSYNC`, failover, 16384 slot, `CLUSTER MIGRATION`), eviction dan memori (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer groups, `IDMP`, `XNACK`), Functions dan ACL.

### Threading dan event loop

**Disahkan pada Redis 8.10.3, 2026-11-07.** Arahan dijalankan pada satu thread utama; `io-threads` menyerahkan pembacaan permintaan dan penulisan balasan kepada thread pembantu. Beban `redis-benchmark` yang sama (SET/GET, nilai 64 bait, 400 klien, 12 thread penanda aras) pada hos 24 teras:

| `io-threads` | Permintaan SET/GET sesaat | Apa yang dipaparkan `INFO threads` |
|---|---|---|
| 1 | 134,523–136,097 | satu thread melakukan semuanya |
| 2 | 126,072–131,596 | thread utama tidak melakukan I/O klien; satu thread pembantu mengambil alih semuanya |
| 4 | 342,349–352,485 | bacaan dan tulisan diagihkan kepada tiga thread pembantu |
| 8 | 498,753–520,472 | diagihkan kepada tujuh thread pembantu |

Dua thread tidak memberi apa-apa kerana thread utama berhenti melakukan I/O klien sebaik sahaja thread pembantu wujud. Dokumentasi: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). Makmal: [`deep-dive/01-threading`](https://github.com/litkhai/notes-on-redis/tree/main/deep-dive/01-threading).

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

</div>
