# Valkey vs Redis, locally

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), Valkey 9.1.3 (`valkey/valkey:9.1.3`) and the Valkey bundle (`valkey/valkey-bundle:9.1`, Valkey 9.1.3), 2026-11-07.**

The three servers side by side in Docker with defaults and no persistence: what they report,
which commands each has, which data types work, memory for one million small strings, and the
same `redis-benchmark` run against each. Measurements on one 24-core host, not a verdict.

### Run

```bash
docker compose up -d                                   # ports 16381 Redis, 16382 Valkey, 16383 bundle
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python compare.py                            # versions, commands, probes, memory
for c in nor-cmp-redis nor-cmp-valkey nor-cmp-bundle; do   # client in each server's network namespace
  docker run --rm --network container:$c redis:8.10.3 \
    redis-benchmark -q -t set,get -n 2000000 -c 200 -P 1 -d 64 --threads 8
done
../../cloud/01-free-database/.venv/bin/python ha.py     # cluster and Sentinel failover, AOF, the same script for both engines
```

Full output, including every command name that differs: [`results/`](./results).

```text
redis-8.10.3: redis_version=8.10.3 valkey_version=- modules=ReJSON,bf,search,timeseries,vectorset
valkey-9.1.3: redis_version=7.2.4 valkey_version=9.1.3 modules=lua
valkey-bundle-9.1: redis_version=7.2.4 valkey_version=9.1.3 modules=bf,json,ldap,lua,search

probe                   redis-8.10.3                valkey-9.1.3                valkey-bundle-9.1         
hash field TTL          ok [60, -1]                 ok [60, -1]                 ok [60, -1]               
HSETEX / HGETEX         ok ['v']                    ok ['v']                    ok ['v']                  
JSON                    ok [[1,2,3]]                ERR unknown command 'JSON   ok [[1,2,3]]              
Bloom                   ok 0                        ERR unknown command 'BF.A   ok 0                      
Top-k                   ok OK                       ERR unknown command 'TOPK   ERR unknown command 'TOPK 
Time series             ok 1                        ERR unknown command 'TS.C   ERR unknown command 'TS.C 
Search: text + numeric  ok [1, 'it:1', ['name', '   ERR unknown command 'FT.C   ok [0]                    
Search: vector          ok OK                       ERR unknown command 'FT.C   ok OK                     
Vector set              ok 1                        ERR unknown command 'VADD   ERR unknown command 'VADD 
Array (8.8)             ok 1                        ERR unknown command 'ARSE   ERR unknown command 'ARSE 
Lua EVAL                ok 1                        ok 1                        ok 1                      
Functions               ok []                       ok []                       ok []

redis-8.10.3: 1000000 keys, used_memory +62.1 MB = 62.1 B/key (dataset 22.3 MB, allocator jemalloc-5.3.0)
valkey-9.1.3: 1000000 keys, used_memory +57.5 MB = 57.5 B/key (dataset 24.3 MB, allocator jemalloc-5.3.0)
valkey-bundle-9.1: 1000000 keys, used_memory +57.5 MB = 57.5 B/key (dataset 24.5 MB, allocator jemalloc-5.3.0)
```

`ha.py` output as it appeared (2026-11-07):

```text
== redis (redis:8.10.3, 8.10.3)
   cluster, node timeout 3 s: replica promoted after 4.2 s; failed writes 3, longest failing stretch 0.0 s, slowest single write 4.0 s
   Sentinel, down-after 3 s: new master named after 4.3 s
   AOF everysec: 606428.12 SET/s (pipeline 16); 631990 keys; restart to loaded 1.3 s; keys after restart 631990
== valkey (valkey/valkey:9.1.3, 9.1.3)
   cluster, node timeout 3 s: replica promoted after 4.2 s; failed writes 4, longest failing stretch 0.0 s, slowest single write 4.0 s
   Sentinel, down-after 3 s: new master named after 4.4 s
   AOF everysec: 568181.81 SET/s (pipeline 16); 632364 keys; restart to loaded 1.3 s; keys after restart 632364
```

### What was observed

- **Identity.** Valkey reports `redis_version:7.2.4` (the fork point) next to `valkey_version:9.1.3`.
  Neither image ships a config file. The Valkey core image loads only `lua` (Lua is a module in
  9.1); the bundle adds `json`, `bf`, `search` and `ldap`.
- **Commands** (top-level plus subcommands, from `COMMAND LIST`): Redis 669, Valkey 399, bundle 450.
  Only in Redis: the module families Search (`FT.*`), JSON, Bloom/cuckoo/count-min/top-k/t-digest,
  Time series; vector sets (`V*`) and Array (`AR*`); `BACKUP`, `HOTKEYS`, `HIMPORT`, `DIGEST`,
  `DELEX`, `INCREX`, `LMOVEM`/`BLMOVEM`, `SDIFFCARD`/`SUNIONCARD`, stream additions (`XACKDEL`,
  `XDELEX`, `XNACK`, `XCFGSET`, `XIDMPRECORD`), `TRIMSLOTS`. Only in Valkey: `CLUSTERSCAN`,
  atomic slot migration (`CLUSTER MIGRATESLOTS` and friends), `COMMANDLOG`, `DELIFEQ`,
  `CLIENT CAPA`, `CLIENT IMPORT-SOURCE`, `SCRIPT SHOW`. The bundle brings back JSON (without
  `JSON.MERGE` and `JSON.NUMPOWBY`), Bloom filters (not cuckoo, count-min, top-k or t-digest) and
  part of Search (no `FT.HYBRID`, `FT.ALTER`, aliases, cursors, spellcheck, suggestions or synonyms).
- **Data types.** Hash field expiration (`HEXPIRE`, `HSETEX`, `HGETEX`) behaved the same on all
  three. Time series, top-k, vector sets and Array exist only on Redis.
- **Search indexing.** On the bundle an `FT.SEARCH` right after `FT.CREATE` found nothing; one
  second later it found the documents (`backfill_in_progress` back to 0). Existing keys are
  indexed in the background. Redis returned the match immediately in this small case.
- **Memory.** One million `key:NNNNNNN` → `val:NNNNNNN` strings: Redis +62.1 MB (62.1 B/key),
  Valkey and bundle +57.5 MB (57.5 B/key), both jemalloc 5.3.0.
- **Throughput** (SET/GET, 64-byte values, 200 clients, 8 benchmark threads, client inside each
  server's network namespace): Redis 119,197–124,797, Valkey 120,992–122,978, bundle
  124,766–126,783 requests/s. With `--io-threads 4` on both and 400 clients: Redis
  342,427–352,568, Valkey 315,391–342,349. Through the published host ports all three stopped at
  about 78,000–84,000, which is the port-forwarding path, not the servers.
- **Failover behaves the same.** With the same script, a 3 s `cluster-node-timeout` promoted a replica after 4.2 s on both engines, and the cluster client saw 3 and 4 failed writes and one write that took 4.0 s on each. Sentinel named a new master after 4.3 s on Redis and 4.4 s on Valkey. Valkey 9.1 kept the Redis OSS 7.2 commands for this: `valkey-cli --cluster create`, `valkey-server --sentinel`, the same `CLUSTER NODES` and `SENTINEL get-master-addr-by-name`.
- **AOF with `appendfsync everysec`.** Redis wrote about 606,000 SET/s with a pipeline of 16 and Valkey about 568,000; with one run each on a shared host, read that as close, not as a ranking. Both reloaded about 632,000 keys in 1.3 s after a restart, with no key lost.
- **One script, two binaries.** Only the binary names changed (`redis-*` and `valkey-*`); redis-py talked to both without a setting.

### Not run / caveats

- One host, client and servers sharing CPUs; small differences here are within run-to-run noise.
- The availability tests ran once per engine on one host; real clusters add network delays.
- Search was probed with one text field, one numeric field and one vector index, not for relevance or speed.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3, Valkey 9.1.3, valkey-bundle 9.1 (Valkey 9.1.3), 2026-11-07 |

## 한국어

**확인: Redis 8.10.3(`redis:8.10.3`), Valkey 9.1.3(`valkey/valkey:9.1.3`), Valkey 번들(`valkey/valkey-bundle:9.1`, Valkey 9.1.3), 2026-11-07.**

세 서버를 기본 설정·영속성 없이 Docker로 나란히 띄웠다. 각자 보고하는 것, 가진 명령, 동작하는 자료형,
작은 문자열 100만 개의 메모리, 같은 `redis-benchmark` 결과를 본다. 24코어 호스트 하나에서 잰 값이지 판정이 아니다.

### 실행

```bash
docker compose up -d                                   # 포트 16381 Redis, 16382 Valkey, 16383 번들
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python compare.py                            # versions, commands, probes, memory
for c in nor-cmp-redis nor-cmp-valkey nor-cmp-bundle; do   # 클라이언트를 각 서버의 네트워크 네임스페이스에서
  docker run --rm --network container:$c redis:8.10.3 \
    redis-benchmark -q -t set,get -n 2000000 -c 200 -P 1 -d 64 --threads 8
done
```

출력은 영문 절과 같다. 서로 다른 명령 이름 전체는 [`results/`](./results)에 있다.

`ha.py`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **정체.** Valkey는 `valkey_version:9.1.3`과 함께 `redis_version:7.2.4`(포크 시점)를 보고한다. 두 이미지 모두
  설정 파일이 없다. Valkey 기본 이미지는 `lua`만 싣고(9.1에서 Lua는 모듈), 번들은 `json`, `bf`, `search`, `ldap`을 더한다.
- **명령**(`COMMAND LIST`의 최상위와 하위 명령): Redis 669, Valkey 399, 번들 450. Redis에만 있는 것: 모듈 계열
  Search(`FT.*`), JSON, Bloom/cuckoo/count-min/top-k/t-digest, Time series, 벡터 셋(`V*`)과 Array(`AR*`), `BACKUP`,
  `HOTKEYS`, `HIMPORT`, `DIGEST`, `DELEX`, `INCREX`, `LMOVEM`/`BLMOVEM`, `SDIFFCARD`/`SUNIONCARD`, 스트림 추가 명령
  (`XACKDEL`, `XDELEX`, `XNACK`, `XCFGSET`, `XIDMPRECORD`), `TRIMSLOTS`. Valkey에만 있는 것: `CLUSTERSCAN`,
  원자적 슬롯 이전(`CLUSTER MIGRATESLOTS` 등), `COMMANDLOG`, `DELIFEQ`, `CLIENT CAPA`, `CLIENT IMPORT-SOURCE`,
  `SCRIPT SHOW`. 번들은 JSON(`JSON.MERGE`, `JSON.NUMPOWBY` 제외), Bloom 필터(cuckoo, count-min, top-k, t-digest 없음),
  Search 일부(`FT.HYBRID`, `FT.ALTER`, 별칭, 커서, 맞춤법, 자동 완성, 동의어 없음)를 되돌려 준다.
- **자료형.** 해시 필드 만료(`HEXPIRE`, `HSETEX`, `HGETEX`)는 셋 모두 같게 동작했다. Time series, top-k, 벡터 셋,
  Array는 Redis에만 있다.
- **Search 색인.** 번들에서는 `FT.CREATE` 직후의 `FT.SEARCH`가 아무것도 찾지 못했고 1초 뒤에는 찾았다
  (`backfill_in_progress`가 0으로 돌아옴). 기존 키는 백그라운드로 색인된다. 이 작은 경우 Redis는 바로 찾았다.
- **메모리.** `key:NNNNNNN` → `val:NNNNNNN` 문자열 100만 개: Redis +62.1 MB(키당 62.1 B), Valkey와 번들
  +57.5 MB(키당 57.5 B). 둘 다 jemalloc 5.3.0.
- **처리량**(SET/GET, 64바이트 값, 클라이언트 200, 벤치마크 스레드 8, 각 서버의 네트워크 네임스페이스 안):
  Redis 초당 119,197–124,797, Valkey 120,992–122,978, 번들 124,766–126,783. 양쪽 모두 `--io-threads 4`, 클라이언트 400:
  Redis 342,427–352,568, Valkey 315,391–342,349. 호스트 포트를 거치면 셋 모두 약 78,000–84,000에서 멈췄다.
  서버가 아니라 포트 포워딩 경로의 한계다.
- **장애 조치는 똑같이 동작한다.** 같은 스크립트에서 `cluster-node-timeout` 3초면 두 엔진 모두 4.2초에 복제본이 승격됐고, 클러스터 클라이언트는 각각 실패한 쓰기 3건과 4건, 4.0초 걸린 쓰기 한 건을 봤다. Sentinel은 Redis에서 4.3초, Valkey에서 4.4초에 새 마스터를 지목했다. Valkey 9.1은 이 부분에서 Redis OSS 7.2의 명령을 그대로 유지한다: `valkey-cli --cluster create`, `valkey-server --sentinel`, 같은 `CLUSTER NODES`와 `SENTINEL get-master-addr-by-name`.
- **`appendfsync everysec`의 AOF.** 파이프라인 16으로 Redis는 초당 약 606,000, Valkey는 약 568,000 SET. 공유 호스트에서 한 번씩 돌린 값이라 순위가 아니라 비슷한 수준으로 읽는다. 둘 다 재시작 뒤 키 약 632,000개를 1.3초에 다시 읽었고 잃은 키는 없었다.
- **스크립트 하나, 바이너리 둘.** 바뀐 것은 바이너리 이름(`redis-*`와 `valkey-*`)뿐이고, redis-py는 설정 없이 둘 다와 통신했다.

### 미실행 / 주의

- 호스트 하나에서 클라이언트와 서버가 CPU를 나눠 썼다. 작은 차이는 실행마다의 흔들림 안에 있다.
- 가용성 시험은 엔진마다 한 번, 호스트 하나에서 돌렸다. 실제 클러스터는 네트워크 지연이 더해진다.
- Search는 텍스트 필드 하나, 숫자 필드 하나, 벡터 인덱스 하나로만 시험했다. 정확도나 속도는 보지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3, Valkey 9.1.3, valkey-bundle 9.1(Valkey 9.1.3), 2026-11-07 |
