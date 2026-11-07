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
docker compose down
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

### What was observed

- **Partial vs full.** Killing the replicas' connections led to two partial resyncs (`sync_partial_ok` 0 → 2); restarting a replica without persistence forced a full sync (`sync_full` 2 → 3, `sync_partial_err` 1).
- **WAIT is per connection.** With `SET` and `WAIT 2 1000` on one connection: 2 with both replicas up; 1 after the 1-second timeout with one replica paused. The same `WAIT` on a fresh connection returned 2 at once: it has no writes of its own to wait for. A first version of this script sent them on separate connections and wrongly showed 2.
- **Failover.** Stopping the primary to Sentinel naming a replica as master: 4,402 ms (3 s of that is `down-after-milliseconds`). The new master accepted writes; the old primary, started again, was a replica of it after 11.3 s.
- **Do not point Sentinel at container names.** In a first run Sentinel monitored `primary` by hostname. Once that container stopped, Docker's DNS could not resolve the name, the Sentinels stalled on the lookups and marked each other down, and the failover took 284,103 ms. With fixed IPs it took 4.4 s.

### Not run / caveats

- Clients that discover the master through Sentinel (`SENTINEL get-master-addr-by-name` in a client library) were not tested; the script asks Sentinel directly.
- No persistence on any node; with persistence a restarted replica can partially resync.

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
docker compose down
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **부분 대 전체.** 복제본 연결을 끊자 부분 재동기화가 두 번 일어났다(`sync_partial_ok` 0 → 2). 영속성 없는 복제본을 재시작하자 전체 동기화가 됐다(`sync_full` 2 → 3, `sync_partial_err` 1).
- **WAIT은 연결 단위다.** 한 연결에서 `SET`과 `WAIT 2 1000`: 복제본 둘이 살아 있으면 2, 하나를 멈추면 1초 타임아웃 뒤 1. 같은 `WAIT`을 새 연결에서 보내면 바로 2가 나온다. 기다릴 자기 쓰기가 없기 때문이다. 이 스크립트의 첫 버전은 둘을 다른 연결로 보내 잘못된 2를 보였다.
- **장애 조치.** 주 서버를 멈춘 뒤 Sentinel이 복제본을 마스터로 지목하기까지 4,402 ms(그중 3초가 `down-after-milliseconds`). 새 마스터는 쓰기를 받았고, 다시 켠 옛 주 서버는 11.3초 뒤 그 복제본이 됐다.
- **Sentinel에 컨테이너 이름을 주지 말 것.** 첫 실행에서 Sentinel은 `primary`를 호스트 이름으로 감시했다. 그 컨테이너가 멈추자 Docker DNS가 이름을 풀지 못했고, Sentinel들이 조회에 묶여 서로를 다운으로 표시했으며 장애 조치에 284,103 ms가 걸렸다. 고정 IP로는 4.4초였다.

### 미실행 / 주의

- Sentinel을 통해 마스터를 찾는 클라이언트(클라이언트 라이브러리의 `SENTINEL get-master-addr-by-name`)는 시험하지 않았다. 스크립트가 Sentinel에 직접 묻는다.
- 모든 노드에 영속성이 없다. 영속성이 있으면 재시작한 복제본도 부분 재동기화할 수 있다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), Sentinel from the same image, 2026-11-07 |
