# Redis Software in Docker

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis Software 8.2.6-25 (`redislabs/redis:8.2.6-25.21`), databases at Redis 8.8, 2026-11-07.**

A single-node Redis Software cluster in one container: the trial licence read from the cluster
itself, databases behind the DMC proxy with different proxy policies, two tenants on one node,
multi-key commands on a sharded database, the licence's shard limit, and re-sharding with data in place.

Official documentation: [Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

### Run

```bash
cp .env.example .env               # admin user and password for the new cluster
docker compose up -d               # UI on https://127.0.0.1:18443, REST API on 19443, databases 12000-12009
set -a; . ./.env; set +a
curl -sk -X POST https://127.0.0.1:19443/v1/bootstrap/create_cluster -H 'Content-Type: application/json'   -d "{"action":"create_cluster","cluster":{"name":"nor-rs.local"},"credentials":{"username":"$RS_USER","password":"$RS_PASS"}}"
../../cloud/01-free-database/.venv/bin/python lab.py
```

Output as it appeared (2026-11-07):

```text
== licence (read at run time)
   {'features': ['trial', 'bigstore'], 'activation_date': '2026-11-07T09:08:08Z', 'expiration_date': '2026-12-07T09:08:08Z', 'shards_limit': 4, 'expired': False}
== db-a: one shard, proxy policy single
   create: 200
   db-a: active after 1.0 s
   bdb 1 db-a: shards 1, replication False, proxy_policy single, sharding False, memory 100 MB, port 12000, version 8.8
== db-b: two shards, proxy policy all-master-shards
   create: 200 
   db-b: active after 1.0 s
   bdb 2 db-b: shards 2, replication False, proxy_policy all-master-shards, sharding True, memory 200 MB, port 12001, version 8.8
== two databases on one node, each its own endpoint
   db-a tenant = b'a' | db-b tenant = b'b'
== multi-key commands on the two-shard database (through the DMC proxy)
   dbsize via proxy: 10001
   MGET k:1 k:2 k:3 k:4 -> [b'1', b'2', b'3', b'4']
   MSET across shards -> True
   MULTI/EXEC across shards -> Command # 2 (SET y:2 2) of pipeline caused error: Keys in request don't hash to the same slot (context='within MULTI', command='set', original-slot='2741', wrong-slot='15062', first-key='y:1', violating-key='y:2')
   MULTI/EXEC with a shared hash tag -> [True, True]
== licence limit: db-c with replication (2 more shards; 1 + 2 + 2 = 5 > 4)
   create: 406 {"description": "Not enough nodes to perform replication", "error_code": "invalid_replication"}
== re-shard db-b from 2 to 4 shards with 10,000 keys in place (db-a deleted first to stay within 4)
   delete db-a: 200
   reshard request: 200 
   db-b after re-shard: active after 6.1 s
   bdb 2 db-b: shards 4, replication False, proxy_policy all-master-shards, sharding True, memory 200 MB, port 12001, version 8.8
   keys after re-shard: 10005, k:4242 = b'4242', total 8.1 s
== licence limit: db-d with one shard while db-b already uses 4 (limit 4)
   create: 400 {"description": "Total shards count exceeds amount of total shards permitted by license. License permits 4 total shards, but there are 5 total shards in use.", "error_code": "invalid_license", "error_details": {"violation": "2"}}
   shards in use: 4 of 4
```

### What was observed

- **Trial terms, read from `/v1/license`:** features `trial` and `bigstore`, 30 days from cluster creation (2026-11-07 to 2026-12-07), at most 4 shards. A fifth shard was refused: "License permits 4 total shards, but there are 5 total shards in use."
- **Start-up:** the API answered 10 s after the container started, bootstrap took about 10 s, and each database was active about 1 s after the request.
- **Versions:** software 8.2.6-25 creates databases at Redis 8.8 by default; the cluster page offers 8.8.0, 8.6.2, 8.4.0, 8.2.1, 8.0.2 and older.
- **Multi-tenancy:** two databases on one node, each with its own endpoint and port, kept their own value for the same key.
- **Behind the DMC proxy:** on the two-shard database `MGET` and `MSET` over keys in different shards worked; `MULTI`/`EXEC` over different slots was refused with "Keys in request don't hash to the same slot"; with a shared hash tag it worked.
- **Replication needs nodes:** a replicated database on one node was refused with "Not enough nodes to perform replication", before any licence check.
- **Re-sharding in place:** 2 → 4 shards with 10,000 keys took about 6 s; all keys were still there afterwards.
- The cluster page shows "Cluster degraded" for a one-node cluster.

### Not run / caveats

- LDAP, TLS on the database endpoints and Active-Active need more than one node or more setup; not run.
- Redis Flex (RAM + SSD) needs local NVMe configuration; not run.

| | |
|---|---|
| Plan needed | Free (30-day trial licence in the container) |
| Verified on | Redis Software 8.2.6-25, Redis 8.8 databases, 2026-11-07 |

## 한국어

**확인: Redis Software 8.2.6-25(`redislabs/redis:8.2.6-25.21`), DB는 Redis 8.8, 2026-11-07.**

컨테이너 하나의 단일 노드 Redis Software 클러스터. 클러스터에서 직접 읽은 체험 라이선스, 프록시 정책이
다른 DMC 프록시 뒤의 DB, 한 노드의 테넌트 둘, 샤드가 나뉜 DB의 여러 키 명령, 라이선스 샤드 한도,
데이터를 둔 채 재샤딩을 본다.

공식 문서: [Redis Software](https://redis.io/docs/latest/operate/rs/), [Proxy policies](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [Database clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/).

### 실행

```bash
cp .env.example .env               # 새 클러스터의 관리자 계정과 비밀번호
docker compose up -d               # UI는 https://127.0.0.1:18443, REST API는 19443, DB는 12000-12009
set -a; . ./.env; set +a
curl -sk -X POST https://127.0.0.1:19443/v1/bootstrap/create_cluster -H 'Content-Type: application/json'   -d "{"action":"create_cluster","cluster":{"name":"nor-rs.local"},"credentials":{"username":"$RS_USER","password":"$RS_PASS"}}"
../../cloud/01-free-database/.venv/bin/python lab.py
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **체험 조건(`/v1/license`에서 읽음):** 기능 `trial`, `bigstore`, 클러스터 생성부터 30일(2026-11-07–2026-12-07), 최대 4샤드. 5번째 샤드는 "License permits 4 total shards, but there are 5 total shards in use."로 거절됐다.
- **시작:** 컨테이너가 뜨고 10초 뒤 API가 응답했고, 부트스트랩은 약 10초, DB는 요청 약 1초 뒤 활성화됐다.
- **버전:** 소프트웨어 8.2.6-25는 기본으로 Redis 8.8 DB를 만든다. 클러스터 화면은 8.8.0, 8.6.2, 8.4.0, 8.2.1, 8.0.2와 그 이전을 고르게 한다.
- **멀티 테넌시:** 한 노드의 DB 둘이 각자의 엔드포인트와 포트를 갖고, 같은 키에 각자의 값을 지켰다.
- **DMC 프록시 뒤:** 2샤드 DB에서 샤드가 다른 키에 대한 `MGET`, `MSET`이 됐다. 슬롯이 다른 `MULTI`/`EXEC`는 "Keys in request don't hash to the same slot"으로 거절됐고, 해시 태그를 공유하면 됐다.
- **복제에는 노드가 필요하다:** 노드 하나에서 복제 DB는 라이선스 검사 전에 "Not enough nodes to perform replication"으로 거절됐다.
- **데이터를 둔 채 재샤딩:** 키 10,000개로 2 → 4샤드에 약 6초, 키는 모두 남아 있었다.
- 노드 하나짜리 클러스터는 클러스터 화면에 "Cluster degraded"로 표시된다.

### 미실행 / 주의

- LDAP, DB 엔드포인트의 TLS, Active-Active는 노드가 더 있거나 설정이 더 필요해 실행하지 않았다.
- Redis Flex(RAM + SSD)는 로컬 NVMe 설정이 필요해 실행하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(컨테이너의 30일 체험 라이선스) |
| 확인한 버전 | Redis Software 8.2.6-25, Redis 8.8 DB, 2026-11-07 |
