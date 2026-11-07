# Cluster

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), six nodes, 2026-11-07.**

Six nodes, three primaries with a replica each: how keys map to slots, what a client sees when it asks the wrong node, multi-key commands, and the 8.4 atomic slot migration under write load. The cluster spec: "Each master node in a cluster handles a subset of the 16384 hash slots", `HASH_SLOT = CRC16(key) mod 16384`, and "hash tags ... can be used to force certain keys to be stored in the same hash slot".

Official documentation: [Scaling with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/).

### Run

```bash
docker compose up -d
./run.sh       # creates the cluster on first run
docker compose down
```

Output as it appeared (2026-11-07):

```text
$ ./run.sh
== cluster: cluster_state:ok cluster_known_nodes:6 cluster_size:3
== slot owners
10.231.78.11:6379 (f567137e...) -> 0 keys | 5461 slots | 1 slaves.
10.231.78.12:6379 (eda0c43e...) -> 0 keys | 5462 slots | 1 slaves.
10.231.78.13:6379 (b2f6c3a1...) -> 0 keys | 5461 slots | 1 slaves.
== CLUSTER KEYSLOT (CRC16 mod 16384)
   user:1 -> 10778
   user:2 -> 6777
   {user:1}:cart -> 10778
   {user:1}:orders -> 10778
== a key whose slot is on another node, without and with -c
   node1 GET user:2 -> MOVED 6777 10.231.78.12:6379
   node1 -c SET user:2 v -> OK
== multi-key commands
   MSET user:1 a user:2 b -> CROSSSLOT Keys in request don't hash to the same slot
   MSET {user:1}:cart a {user:1}:orders b -> OK
== atomic slot migration: slots 0-999 from node1 to node2 while redis-benchmark writes
   keys in slot 0 on node1 before: 22; node1 dbsize 97902
   node2> CLUSTER MIGRATION IMPORT 0 999 -> 0076e4a59e545d8560d0808b1774c3a2ea5e9741
   status: id 0076e4a59e545d8560d0808b1774c3a2ea5e9741 slots 0-999 source f567137e5037451029ac029b6ae92a926fdbbaa0 dest eda0c43eb630cfd228ac539258022c03ba68d393 operation import state completed last_error  retries 0 create_time 1794038115322 start_time 1794038115322 end_time 1794038115366 write_pause_ms 0 
   took about 105 ms
   benchmark during migration:   throughput summary: 199933.36 requests per second
   keys in slot 0 now on node2: 57, on node1: 0
10.231.78.11:6379 (f567137e...) -> 268927 keys | 4461 slots | 1 slaves.
10.231.78.12:6379 (eda0c43e...) -> 322627 keys | 6462 slots | 1 slaves.
10.231.78.13:6379 (b2f6c3a1...) -> 308183 keys | 5461 slots | 1 slaves.
[OK] 899737 keys in 3 masters.
```

### What was observed

- **Slots.** `user:1` → 10778 and `user:2` → 6777; `{user:1}:cart` and `{user:1}:orders` both hash only `user:1` and land in 10778 with it.
- **Redirects.** Asking node 1 for `user:2` returns `MOVED 6777 10.231.78.12:6379`; `redis-cli -c` follows it. Cluster-aware clients do the same and cache the slot map.
- **Multi-key.** `MSET user:1 a user:2 b` → `CROSSSLOT`; the same with a shared hash tag → `OK`.
- **Atomic slot migration.** `CLUSTER MIGRATION IMPORT 0 999` on the destination moved 1,000 slots from node 1 to node 2 in 44 ms by the task's own start and end times, with `write_pause_ms 0`, while `redis-benchmark --cluster` wrote at about 200,000 requests/s and reported no errors (it follows redirects itself). Slot 0's keys were on node 2 afterwards and `redis-cli --cluster check` agreed on 899,737 keys across three masters.

### Not run / caveats

- Failover inside the cluster (a primary stopped, its replica promoted) was not run.
- The migration moved a small dataset on one host; large slots and cross-host links will take longer.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), six nodes, 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), six nodes, 2026-11-07.**

노드 6개, 주 서버 셋에 복제본 하나씩. 키가 슬롯에 매핑되는 방식, 잘못된 노드에 물었을 때 클라이언트가 보는 것, 여러 키 명령, 쓰기 부하 중의 8.4 원자적 슬롯 이전을 본다. 클러스터 명세: "Each master node in a cluster handles a subset of the 16384 hash slots", `HASH_SLOT = CRC16(key) mod 16384`, "hash tags ... can be used to force certain keys to be stored in the same hash slot".

공식 문서: [Redis Cluster로 확장](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/), [클러스터 명세](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [CLUSTER MIGRATION](https://redis.io/docs/latest/commands/cluster-migration/).

### 실행

```bash
docker compose up -d
./run.sh       # creates the cluster on first run
docker compose down
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **슬롯.** `user:1` → 10778, `user:2` → 6777. `{user:1}:cart`와 `{user:1}:orders`는 `user:1`만 해시해서 함께 10778에 들어간다.
- **리디렉션.** 노드 1에 `user:2`를 물으면 `MOVED 6777 10.231.78.12:6379`. `redis-cli -c`는 따라간다. 클러스터를 아는 클라이언트도 같고, 슬롯 지도를 캐시한다.
- **여러 키.** `MSET user:1 a user:2 b` → `CROSSSLOT`. 같은 해시 태그를 쓰면 `OK`.
- **원자적 슬롯 이전.** 대상 노드에서 `CLUSTER MIGRATION IMPORT 0 999`가 슬롯 1,000개를 노드 1에서 노드 2로 옮겼다. 작업 자체의 시작·끝 시각으로 44 ms, `write_pause_ms 0`. 그동안 `redis-benchmark --cluster`가 초당 약 200,000으로 쓰며 오류를 보고하지 않았다(리디렉션을 스스로 따라감). 이전 뒤 슬롯 0의 키는 노드 2에 있었고, `redis-cli --cluster check`는 주 서버 셋에 키 899,737개로 일치했다.

### 미실행 / 주의

- 클러스터 안의 장애 조치(주 서버를 멈추고 복제본 승격)는 실행하지 않았다.
- 이전한 데이터는 작고 호스트도 하나였다. 큰 슬롯과 호스트 간 연결은 더 오래 걸린다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), six nodes, 2026-11-07 |
