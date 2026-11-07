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
../../cloud/01-free-database/.venv/bin/python failover.py 15000   # kill a primary under writes; default cluster-node-timeout
../../cloud/01-free-database/.venv/bin/python failover.py 3000    # the same with a 3 s timeout
docker compose down
../../cloud/01-free-database/.venv/bin/python partition.py         # cut a primary off the network and write on both sides (5 s node timeout)
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

`failover.py` output as it appeared (2026-11-07), after `run.sh`:

```text
cluster-node-timeout 15000 ms; primaries ['10.231.78.14', '10.231.78.15', '10.231.78.16']; victim nor-cl-node4 (10.231.78.14) holds 'k:0', 'k:3' is on 10.231.78.15
killed nor-cl-node4 (SIGKILL)
key on the killed primary    writes 353, failed 6, longest outage 16.2 s, errors ['ConnectionError', 'TimeoutError']
                             last value 347, successful writes 347, increments lost 0
key on another primary       writes 1229, failed 1, longest outage 1.0 s, errors ['ClusterDownError']
                             last value 1228, successful writes 1228, increments lost 0
cluster_state seen from a replica: ok at 0.3 s, fail at 18.0 s, ok at 19.3 s
replica promoted (seen in CLUSTER NODES) 19.3 s after the kill
after restarting the old primary (7.3 s until it rejoined as a replica):
   10.231.78.14:6379@16379 slave
   10.231.78.13:6379@16379 master
   10.231.78.15:6379@16379 master
   10.231.78.16:6379@16379 master
   10.231.78.12:6379@16379 slave
   10.231.78.11:6379@16379 myself,slave

cluster-node-timeout 3000 ms; primaries ['10.231.78.13', '10.231.78.15', '10.231.78.16']; victim nor-cl-node3 (10.231.78.13) holds 'k:0', 'k:3' is on 10.231.78.15
killed nor-cl-node3 (SIGKILL)
key on the killed primary    writes 309, failed 3, longest outage 4.1 s, errors ['ConnectionError', 'TimeoutError']
                             last value 306, successful writes 306, increments lost 0
key on another primary       writes 545, failed 1, longest outage 1.0 s, errors ['ClusterDownError']
                             last value 544, successful writes 544, increments lost 0
cluster_state seen from a replica: ok at 0.4 s, fail at 4.1 s, ok at 5.3 s
replica promoted (seen in CLUSTER NODES) 5.3 s after the kill
after restarting the old primary (0.7 s until it rejoined as a replica):
   10.231.78.14:6379@16379 master
   10.231.78.13:6379@16379 slave
   10.231.78.15:6379@16379 master
   10.231.78.16:6379@16379 master
   10.231.78.12:6379@16379 slave
   10.231.78.11:6379@16379 myself,slave
```

`partition.py` output as it appeared (2026-11-07):

```text
cluster-node-timeout 5000 ms; victim nor-cl-node1 (10.231.78.11) owns 'p:0'
0.0 s  nor-cl-node1 disconnected from nor-cluster_cl
8.0 s  a replica took over (seen from nor-cl-node4)
isolated old primary (docker exec): 21 writes accepted, last at 6.2 s; 78 refused from 6.6 s ['CLUSTERDOWN The cluster is down']
majority side (cluster client)  : 82 writes accepted, last at 30.1 s; 2 refused from 0.2 s ['TimeoutError']
   highest value on the isolated node: 21; on the majority: 82
reconnected; nor-cl-node1 became a slave after 0.1 s
'p:0' through the cluster now: 82 (the isolated node's 21 writes are gone)
```

### What was observed

- **Slots.** `user:1` → 10778 and `user:2` → 6777; `{user:1}:cart` and `{user:1}:orders` both hash only `user:1` and land in 10778 with it.
- **Redirects.** Asking node 1 for `user:2` returns `MOVED 6777 10.231.78.12:6379`; `redis-cli -c` follows it. Cluster-aware clients do the same and cache the slot map.
- **Multi-key.** `MSET user:1 a user:2 b` → `CROSSSLOT`; the same with a shared hash tag → `OK`.
- **Failover takes the node timeout plus about a second.** A primary killed with SIGKILL under writes every 20 ms: with the default `cluster-node-timeout` of 15 s, a replica of the cluster saw `cluster_state:fail` at 18.0 s and the promotion at 19.3 s. The redis-py cluster client could not write that primary's key for about 16 s. With 3 s, the same took 4.1 s, 5.3 s and about 4 s. No increment was lost either way, but the cluster has no persistence and replication is asynchronous, so that is luck of timing, not a guarantee.
- **The whole cluster refuses writes for a moment.** Keys on the primaries that stayed up got one `ClusterDownError`, about 1 s long, in both runs: between the node being flagged FAIL and its replica taking over, some slots have no owner, and with the default `cluster-require-full-coverage yes` every node answers `CLUSTERDOWN`.
- **The old primary comes back as a replica.** Restarted, it rejoined as a replica of the node that replaced it, within 1–8 s.
- **Atomic slot migration.** `CLUSTER MIGRATION IMPORT 0 999` on the destination moved 1,000 slots from node 1 to node 2 in 44 ms by the task's own start and end times, with `write_pause_ms 0`, while `redis-benchmark --cluster` wrote at about 200,000 requests/s and reported no errors (it follows redirects itself). Slot 0's keys were on node 2 afterwards and `redis-cli --cluster check` agreed on 899,737 keys across three masters.
- **A partitioned primary keeps taking writes for a while, and loses them.** With a 5 s node timeout, the primary cut off the network still accepted 21 increments from a client on its own side until 6.2 s, then answered `CLUSTERDOWN The cluster is down`. Its replica took over at 8.0 s and the majority side carried on to 82. Reconnected, the old primary became a replica at once and the key read 82: the 21 writes on the isolated side were gone. Unlike the SIGKILL runs, nothing here failed loudly on the minority side until the timeout.

### Not run / caveats

- Both failover tests ran on one host; real networks add their own delays.
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
../../cloud/01-free-database/.venv/bin/python failover.py 15000   # kill a primary under writes; default cluster-node-timeout
../../cloud/01-free-database/.venv/bin/python failover.py 3000    # the same with a 3 s timeout
docker compose down
../../cloud/01-free-database/.venv/bin/python partition.py         # cut a primary off the network and write on both sides (5 s node timeout)
```

출력은 영문 절과 같다(2026-11-07). `failover.py`의 출력도 마찬가지다.

`partition.py`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **슬롯.** `user:1` → 10778, `user:2` → 6777. `{user:1}:cart`와 `{user:1}:orders`는 `user:1`만 해시해서 함께 10778에 들어간다.
- **리디렉션.** 노드 1에 `user:2`를 물으면 `MOVED 6777 10.231.78.12:6379`. `redis-cli -c`는 따라간다. 클러스터를 아는 클라이언트도 같고, 슬롯 지도를 캐시한다.
- **여러 키.** `MSET user:1 a user:2 b` → `CROSSSLOT`. 같은 해시 태그를 쓰면 `OK`.
- **장애 조치에는 노드 타임아웃에 약 1초가 더 걸린다.** 20 ms마다 쓰는 중에 주 서버를 SIGKILL로 죽였다. 기본 `cluster-node-timeout` 15초에서는 클러스터의 복제본이 18.0초에 `cluster_state:fail`, 19.3초에 승격을 봤고, redis-py 클러스터 클라이언트는 그 주 서버의 키에 약 16초 동안 쓰지 못했다. 3초로 바꾸면 같은 값이 4.1초, 5.3초, 약 4초. 두 경우 모두 잃은 증가는 없었지만, 이 클러스터는 영속성이 없고 복제는 비동기라 타이밍이 운 좋았던 것이지 보장이 아니다.
- **잠깐 동안 클러스터 전체가 쓰기를 거절한다.** 살아 있는 주 서버의 키도 두 번 모두 약 1초짜리 `ClusterDownError`를 한 번 받았다. 노드가 FAIL로 표시된 뒤 복제본이 넘겨받기 전까지 주인 없는 슬롯이 생기고, 기본값 `cluster-require-full-coverage yes`에서는 모든 노드가 `CLUSTERDOWN`으로 답한다.
- **옛 주 서버는 복제본으로 돌아온다.** 재시작하면 자기를 대신한 노드의 복제본으로 1–8초 안에 다시 들어왔다.
- **원자적 슬롯 이전.** 대상 노드에서 `CLUSTER MIGRATION IMPORT 0 999`가 슬롯 1,000개를 노드 1에서 노드 2로 옮겼다. 작업 자체의 시작·끝 시각으로 44 ms, `write_pause_ms 0`. 그동안 `redis-benchmark --cluster`가 초당 약 200,000으로 쓰며 오류를 보고하지 않았다(리디렉션을 스스로 따라감). 이전 뒤 슬롯 0의 키는 노드 2에 있었고, `redis-cli --cluster check`는 주 서버 셋에 키 899,737개로 일치했다.
- **분할된 주 서버는 한동안 쓰기를 받다가 그 쓰기를 잃는다.** 노드 타임아웃 5초에서, 네트워크에서 떨어진 주 서버는 자기 쪽 클라이언트의 증가를 6.2초까지 21건 받았고 그 뒤 `CLUSTERDOWN The cluster is down`으로 답했다. 복제본이 8.0초에 넘겨받았고 다수 쪽은 82까지 이어 갔다. 다시 연결하자 옛 주 서버는 곧바로 복제본이 됐고 키 값은 82였다. 고립된 쪽의 쓰기 21건은 사라졌다. SIGKILL 실행과 달리, 소수 쪽에서는 타임아웃 전까지 아무것도 크게 실패하지 않았다.

### 미실행 / 주의

- 두 장애 조치 시험 모두 호스트 하나에서 돌렸다. 실제 네트워크는 자체 지연을 더한다.
- 이전한 데이터는 작고 호스트도 하나였다. 큰 슬롯과 호스트 간 연결은 더 오래 걸린다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), six nodes, 2026-11-07 |
