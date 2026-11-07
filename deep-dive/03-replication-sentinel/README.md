# Replication and Sentinel

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), Sentinel from the same image, 2026-11-07.**

One primary, two replicas and three Sentinels (quorum 2, `down-after-milliseconds` 3000) in Compose: partial vs full resynchronisation, what `WAIT` actually counts, and a failover timed from stopping the primary to Sentinel naming a new one. The `WAIT` docs: it "will always return the number of replicas that acknowledged the write commands sent by the current client", and "WAIT does not make Redis a strongly consistent store".

Official documentation: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/).

### Run

```bash
docker compose up -d
./run.sh
../../cloud/01-free-database/.venv/bin/python sentinel_client.py   # on a fresh 'docker compose up': a redis-py Sentinel client across a failover
docker compose down
./persist.sh            # does a restarted replica resync partially? five persistence and restart combinations
node sentinel_client.mjs  # on a fresh 'docker compose up': node-redis's createSentinel() across a failover
```

Output as it appeared (2026-11-07):

```text
$ ./run.sh        (fixed-IP topology from compose.yaml)
== after initial load: sync_full:2 sync_partial_ok:0 sync_partial_err:0
== kill the replicas' connections on the primary (CLIENT KILL TYPE replica)
2
   sync_full:2 sync_partial_ok:2 sync_partial_err:0
== restart replica1 (no persistence, so it comes back empty)
   sync_full:3 sync_partial_ok:2 sync_partial_err:1
== WAIT with both replicas up
   WAIT 2 1000 -> 2 after 823 ms
== WAIT with replica2 paused (docker pause)
   primary sees: slave0:ip=10.231.77.12,port=6379,state=online,offset=28803827,lag=2 slave1:ip=10.231.77.11,port=6379,state=online,offset=28803864,lag=1
   WAIT 2 1000 -> 1 after 1131 ms
   same WAIT on a fresh connection -> 2
== Sentinel failover: stop the primary
   master before: 10.231.77.10:6379
   new master: 10.231.77.12 after 4402 ms
   10.231.77.12 role: role:master connected_slaves:1
   write to new master: OK
== start the old primary again: it rejoins as a replica
   after 11324 ms: role:slave master_host:10.231.77.12 master_link_status:down
ip=10.231.77.12 num-slaves=2 failover-timeout=10000
```

`sentinel_client.py` output as it appeared (2026-11-07), on a fresh `docker compose up`:

```text
master from the Sentinels: ('10.231.77.10', 6379) = nor-repl-primary
killed nor-repl-primary (SIGKILL)
Sentinels report the new master ('10.231.77.12', 6379) = nor-repl-replica2 after 4.5 s
writes 364, failed 64, errors ['ConnectionError', 'MasterNotFoundError', 'TimeoutError']
first successful write on the new master 4.4 s after the kill
last value 300, successful writes 300, increments lost 0
restarted nor-repl-primary; its role over time: ConnectionError at 0.0 s, master at 0.2 s, slave->10.231.77.12 at 11.0 s
```

`persist.sh` and `sentinel_client.mjs` output as it appeared (2026-11-07):

```text
== replica none
   primary before: sync_full:1 sync_partial_ok:0 sync_partial_err:0
   primary after:  sync_full:2 sync_partial_ok:0 sync_partial_err:1
   replica log:    * PSYNC is not possible, initialize RDB channel.|* MASTER <-> REPLICA sync started|* PSYNC is not possible, initialize RDB channel.
== replica aof-graceful
   primary before: sync_full:3 sync_partial_ok:0 sync_partial_err:1
   primary after:  sync_full:4 sync_partial_ok:0 sync_partial_err:1
   replica log:    * MASTER <-> REPLICA sync started|* Partial resynchronization not possible (no cached master)|* PSYNC is not possible, initialize RDB channel.
== replica aof-kill
   primary before: sync_full:5 sync_partial_ok:0 sync_partial_err:1
   primary after:  sync_full:6 sync_partial_ok:0 sync_partial_err:1
   replica log:    * MASTER <-> REPLICA sync started|* Partial resynchronization not possible (no cached master)|* PSYNC is not possible, initialize RDB channel.
== replica rdb-graceful
   primary before: sync_full:7 sync_partial_ok:0 sync_partial_err:1
   primary after:  sync_full:7 sync_partial_ok:1 sync_partial_err:1
   replica log:    * PSYNC is not possible, initialize RDB channel.|* MASTER <-> REPLICA sync started|* Successful partial resynchronization with master.
== replica rdb-kill
   primary before: sync_full:8 sync_partial_ok:1 sync_partial_err:1
   primary after:  sync_full:9 sync_partial_ok:1 sync_partial_err:2
   replica log:    * PSYNC is not possible, initialize RDB channel.|* MASTER <-> REPLICA sync started|* PSYNC is not possible, initialize RDB channel.

$ node sentinel_client.mjs
node-redis 6.3.1; master from the Sentinels: 10.231.77.10 = nor-repl-primary
killed nor-repl-primary (SIGKILL)
Sentinels report the new master 10.231.77.11 = nor-repl-replica1 after 4.2 s
writes 190, failed 0, errors thrown [], error events {}
longest stretch without a successful write 0.0 s; first write after the kill succeeded at 0.3 s
slowest write: issued 0.3 s after the kill, took 6.1 s (node-redis queued it until the new master answered)
last value 190, successful writes 190, increments lost 0
```

### What was observed

- **Partial vs full.** Killing the replicas' connections led to two partial resyncs (`sync_partial_ok` 0 → 2); restarting a replica without persistence forced a full sync (`sync_full` 2 → 3, `sync_partial_err` 1).
- **WAIT is per connection.** With `SET` and `WAIT 2 1000` on one connection: 2 with both replicas up; 1 after the 1-second timeout with one replica paused. The same `WAIT` on a fresh connection returned 2 at once: it has no writes of its own to wait for. A first version of this script sent them on separate connections and wrongly showed 2.
- **Failover.** Stopping the primary to Sentinel naming a replica as master: 4,402 ms (3 s of that is `down-after-milliseconds`). The new master accepted writes; the old primary, started again, was a replica of it after 11.3 s.
- **A Sentinel-aware client follows on its own.** redis-py's `Sentinel(...).master_for("mymaster")` asked the Sentinels for the master and, after the kill, wrote to the new one 4.4 s later with no code change; the Sentinels named it at 4.5 s. In between the client got `ConnectionError`, `TimeoutError` and `MasterNotFoundError`, so the application still needs a retry.
- **The old primary is a master again for about 11 s.** Restarted, it answered as `master` from 0.2 s and became a replica of the new master only at 11.0 s, when Sentinel reconfigured it. A client that connects to it directly, not through Sentinel, can write there in that window and lose those writes.
- **Do not point Sentinel at container names.** In a first run Sentinel monitored `primary` by hostname. Once that container stopped, Docker's DNS could not resolve the name, the Sentinels stalled on the lookups and marked each other down, and the failover took 284,103 ms. With fixed IPs it took 4.4 s.
- **Only RDB plus a graceful shutdown gives a partial resync after restart.** Five ways of restarting a replica: without persistence, with AOF (graceful or killed), with RDB only (graceful or killed). Only the RDB replica restarted with `docker restart` came back with "Successful partial resynchronization with master" (`sync_partial_ok` 0 → 1). The AOF replicas logged "Partial resynchronization not possible (no cached master)" and took a full sync, as did the killed RDB replica. The replication page says the same: replicas "when powered off gently and restarted - are able to store in the `RDB` file the information needed to resync", and "It is not possible to partially sync a replica that restarted via the AOF file."
- **node-redis waits instead of failing.** `createSentinel()` in node-redis 6.3.1 threw no error during the same failover: a write issued 0.3 s after the kill simply took 6.1 s, held until the new master answered, and every increment arrived. redis-py instead raised errors for about 4 s. Both followed the new master with no code change; they differ in whether the application sees errors or latency.

### Not run / caveats

- Only redis-py and node-redis were tried as Sentinel clients.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), Sentinel from the same image, 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), Sentinel from the same image, 2026-11-07.**

Compose로 주 서버 하나, 복제본 둘, Sentinel 셋(quorum 2, `down-after-milliseconds` 3000)을 띄운다. 부분 대 전체 재동기화, `WAIT`이 실제로 세는 것, 주 서버를 멈춘 순간부터 Sentinel이 새 주 서버를 지목할 때까지의 장애 조치 시간을 본다. `WAIT` 문서: "will always return the number of replicas that acknowledged the write commands sent by the current client", "WAIT does not make Redis a strongly consistent store".

공식 문서: [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [WAIT](https://redis.io/docs/latest/commands/wait/).

### 실행

```bash
docker compose up -d
./run.sh
../../cloud/01-free-database/.venv/bin/python sentinel_client.py   # on a fresh 'docker compose up': a redis-py Sentinel client across a failover
docker compose down
./persist.sh            # does a restarted replica resync partially? five persistence and restart combinations
node sentinel_client.mjs  # on a fresh 'docker compose up': node-redis's createSentinel() across a failover
```

출력은 영문 절과 같다(2026-11-07). `sentinel_client.py`의 출력도 마찬가지다.

`persist.sh`와 `sentinel_client.mjs`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **부분 대 전체.** 복제본 연결을 끊자 부분 재동기화가 두 번 일어났다(`sync_partial_ok` 0 → 2). 영속성 없는 복제본을 재시작하자 전체 동기화가 됐다(`sync_full` 2 → 3, `sync_partial_err` 1).
- **WAIT은 연결 단위다.** 한 연결에서 `SET`과 `WAIT 2 1000`: 복제본 둘이 살아 있으면 2, 하나를 멈추면 1초 타임아웃 뒤 1. 같은 `WAIT`을 새 연결에서 보내면 바로 2가 나온다. 기다릴 자기 쓰기가 없기 때문이다. 이 스크립트의 첫 버전은 둘을 다른 연결로 보내 잘못된 2를 보였다.
- **장애 조치.** 주 서버를 멈춘 뒤 Sentinel이 복제본을 마스터로 지목하기까지 4,402 ms(그중 3초가 `down-after-milliseconds`). 새 마스터는 쓰기를 받았고, 다시 켠 옛 주 서버는 11.3초 뒤 그 복제본이 됐다.
- **Sentinel을 아는 클라이언트는 알아서 따라간다.** redis-py의 `Sentinel(...).master_for("mymaster")`는 Sentinel에 마스터를 묻고, 죽인 뒤 4.4초에 코드 변경 없이 새 마스터에 썼다. Sentinel이 새 마스터를 지목한 것은 4.5초. 그 사이 클라이언트는 `ConnectionError`, `TimeoutError`, `MasterNotFoundError`를 받으므로 애플리케이션에 재시도는 여전히 필요하다.
- **옛 주 서버는 약 11초 동안 다시 마스터다.** 재시작하면 0.2초부터 `master`로 답했고, Sentinel이 재설정한 11.0초에야 새 마스터의 복제본이 됐다. Sentinel을 거치지 않고 직접 붙는 클라이언트는 그 사이 거기에 쓰고 그 쓰기를 잃을 수 있다.
- **Sentinel에 컨테이너 이름을 주지 말 것.** 첫 실행에서 Sentinel은 `primary`를 호스트 이름으로 감시했다. 그 컨테이너가 멈추자 Docker DNS가 이름을 풀지 못했고, Sentinel들이 조회에 묶여 서로를 다운으로 표시했으며 장애 조치에 284,103 ms가 걸렸다. 고정 IP로는 4.4초였다.
- **재시작 후 부분 재동기화는 RDB와 정상 종료일 때만 된다.** 복제본을 다섯 가지로 재시작했다: 영속성 없음, AOF(정상 종료 또는 강제 종료), RDB만(정상 종료 또는 강제 종료). `docker restart`로 재시작한 RDB 복제본만 "Successful partial resynchronization with master"로 돌아왔다(`sync_partial_ok` 0 → 1). AOF 복제본은 "Partial resynchronization not possible (no cached master)"를 남기고 전체 동기화를 했고, 강제 종료한 RDB 복제본도 마찬가지였다. 복제 페이지도 같은 말을 한다: 복제본은 "when powered off gently and restarted - are able to store in the `RDB` file the information needed to resync", 그리고 "It is not possible to partially sync a replica that restarted via the AOF file."
- **node-redis는 실패하지 않고 기다린다.** 같은 장애 조치에서 node-redis 6.3.1의 `createSentinel()`은 오류를 하나도 던지지 않았다. 죽인 지 0.3초에 보낸 쓰기가 새 마스터가 답할 때까지 붙잡혀 6.1초 걸렸을 뿐이고, 증가는 모두 반영됐다. redis-py는 약 4초 동안 오류를 냈다. 둘 다 코드 변경 없이 새 마스터를 따라갔고, 애플리케이션이 오류를 보느냐 지연을 보느냐가 다르다.

### 미실행 / 주의

- Sentinel 클라이언트로는 redis-py와 node-redis만 시험했다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), Sentinel from the same image, 2026-11-07 |
