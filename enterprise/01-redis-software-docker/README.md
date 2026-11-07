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
curl -sk -X POST https://127.0.0.1:19443/v1/bootstrap/create_cluster -H 'Content-Type: application/json' \
  -d '{"action":"create_cluster","cluster":{"name":"nor-rs.local"},"credentials":{"username":"'"$RS_USER"'","password":"'"$RS_PASS"'"}}'
sleep 60                           # the cluster finishes bootstrapping in the background
../../cloud/01-free-database/.venv/bin/python lab.py
../../cloud/01-free-database/.venv/bin/python tls.py           # modules shipped with the cluster, and a database with TLS on its endpoint
docker run -d --name nor-ldap --network nor-rs_default -e LDAP_ORGANISATION=lab -e LDAP_DOMAIN=example.org \
  -e LDAP_ADMIN_PASSWORD=ldap-lab-pw osixia/openldap:1.5.0
sleep 15; docker exec -i nor-ldap ldapadd -x -D cn=admin,dc=example,dc=org -w ldap-lab-pw < ldap-seed.ldif
../../cloud/01-free-database/.venv/bin/python ldap_mtls.py     # role-based LDAP for a database, and a database that requires a client certificate
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

`tls.py` output as it appeared (2026-11-07):

```text
== modules shipped with the cluster (GET /v1/modules)
   ReJSON         8.8.2
   ReJSON         8.6.6
   ReJSON         8.4.7
   ReJSON         8.2.12
   ReJSON         8.0.7
   ReJSON         2.8.20
   ReJSON         2.6.25
   ReJSON         2.4.20
   bf             8.8.1
   bf             8.6.4
   bf             8.4.7
   bf             8.2.14
   bf             8.0.10
   bf             2.8.22
   bf             2.6.30
   search         8.8.8
   search         8.6.12
   search         8.4.14
   search         8.2.17
   search         8.0.3
   search         2.10.33
   search         2.8.39
   timeseries     8.8.8
   timeseries     8.6.12
   timeseries     8.4.19
   timeseries     8.2.17
   timeseries     8.0.7
   timeseries     1.12.19
   timeseries     1.10.29
   timeseries     1.8.28
   RedisGears present: False
== a database with TLS on its endpoint
   create: 200 
   tls_mode enabled, enforce_client_authentication disabled, port 12005
   proxy certificate from GET /v1/cluster/certificates: -----BEGIN CERTIFICATE----- (1627 bytes)
   plain TCP                                      -> ConnectionError: Connection closed by server.
   TLS, proxy cert as CA, hostname not checked    -> SET ok, GET b'v'
   TLS, no CA given (system store)                -> ConnectionError: Error 1 connecting to localhost:12005. [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify
   500 PINGs over TLS on one connection: 0.132 ms each
   db-tls deleted
```

`ldap_mtls.py` output as it appeared (2026-11-07):

```text
== role-based LDAP for a database
   PUT /v1/cluster/ldap -> 200
   redis ACL lab-read -> 200
   role lab-reader -> 200
   LDAP mapping cn=redis-readers -> role lab-reader -> 200
   database db-ldap -> 200 
   alice (in cn=redis-readers)        -> GET b'q3'; SET refused: User ldap_mapping:1 has no permissions to run the 'set' comm
   alice, wrong password              -> AuthenticationError: invalid username-password pair
   bob (no mapped group)              -> ResponseError: problem with LDAP service

== mutual TLS: the database requires a client certificate
   database db-mtls -> 200 
   tls_mode enabled, enforce_client_authentication enabled
   TLS, no client certificate                     -> ConnectionError: Error while reading from localhost:12007 : (1, '[SSL: TLSV13_ALERT_CERTIFICATE_R
   TLS, a certificate the database does not know  -> ConnectionError: Error while reading from localhost:12007 : (1, '[SSL: TLSV1_ALERT_UNKNOWN_CA] tl
   TLS, the registered client certificate         -> SET ok, GET b'v'

both databases deleted
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
- **Modules shipped with 8.2.6-25.** `GET /v1/modules` lists JSON, Bloom (`bf`), Search and time series, several versions of each so databases of older Redis versions keep working. **RedisGears is not there**, so the old RDI write-behind, which needs RedisGears Python 1.2.6, cannot run on this release (see [`02-rdi`](../02-rdi/README.md)).
- **TLS on a database endpoint.** A database created with `tls_mode: enabled` and `enforce_client_authentication: disabled` closed plain TCP connections at once. A redis-py client with `ssl=True` connected only when given the cluster's proxy certificate from `GET /v1/cluster/certificates` as its CA; with the system store it failed `CERTIFICATE_VERIFY_FAILED`. Hostname checking was off because the self-signed certificate names the cluster, not `localhost`. A PING round trip on one TLS connection took 0.13 ms.
- **The bootstrap command in an earlier version of this README was broken.** Its JSON was in double quotes inside double quotes, so the shell stripped them. It is fixed above.
- **LDAP users reach a database through a role.** The chain is: cluster LDAP settings (`PUT /v1/cluster/ldap` with a bind user, a user query `(cn=%u)` and a group query `(member=%D)`, `data_plane` on), a Redis ACL `+@read ~*`, a role, an LDAP mapping from `cn=redis-readers` to that role, and the database's `roles_permissions` joining role and ACL. `alice`, in the group, could `GET` and was refused `SET` under the user name `ldap_mapping:1`. A wrong password got `invalid username-password pair`. `bob`, who exists in LDAP but is in no mapped group, got the less helpful `problem with LDAP service`.
- **Mutual TLS checks the client too.** A database with `enforce_client_authentication: enabled` and one registered client certificate refused a TLS client with no certificate (`CERTIFICATE_REQUIRED`) and one with a certificate it did not know (`UNKNOWN_CA`), and accepted the registered one.

### Not run / caveats

- Active-Active needs more than one cluster; not run. LDAP ran over plain `ldap://`, not LDAPS.
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
curl -sk -X POST https://127.0.0.1:19443/v1/bootstrap/create_cluster -H 'Content-Type: application/json' \
  -d '{"action":"create_cluster","cluster":{"name":"nor-rs.local"},"credentials":{"username":"'"$RS_USER"'","password":"'"$RS_PASS"'"}}'
sleep 60                           # the cluster finishes bootstrapping in the background
../../cloud/01-free-database/.venv/bin/python lab.py
```

출력은 영문 절과 같다(2026-11-07).

`tls.py`의 출력도 영문 절과 같다(2026-11-07).

`ldap_mtls.py`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **체험 조건(`/v1/license`에서 읽음):** 기능 `trial`, `bigstore`, 클러스터 생성부터 30일(2026-11-07–2026-12-07), 최대 4샤드. 5번째 샤드는 "License permits 4 total shards, but there are 5 total shards in use."로 거절됐다.
- **시작:** 컨테이너가 뜨고 10초 뒤 API가 응답했고, 부트스트랩은 약 10초, DB는 요청 약 1초 뒤 활성화됐다.
- **버전:** 소프트웨어 8.2.6-25는 기본으로 Redis 8.8 DB를 만든다. 클러스터 화면은 8.8.0, 8.6.2, 8.4.0, 8.2.1, 8.0.2와 그 이전을 고르게 한다.
- **멀티 테넌시:** 한 노드의 DB 둘이 각자의 엔드포인트와 포트를 갖고, 같은 키에 각자의 값을 지켰다.
- **DMC 프록시 뒤:** 2샤드 DB에서 샤드가 다른 키에 대한 `MGET`, `MSET`이 됐다. 슬롯이 다른 `MULTI`/`EXEC`는 "Keys in request don't hash to the same slot"으로 거절됐고, 해시 태그를 공유하면 됐다.
- **복제에는 노드가 필요하다:** 노드 하나에서 복제 DB는 라이선스 검사 전에 "Not enough nodes to perform replication"으로 거절됐다.
- **데이터를 둔 채 재샤딩:** 키 10,000개로 2 → 4샤드에 약 6초, 키는 모두 남아 있었다.
- 노드 하나짜리 클러스터는 클러스터 화면에 "Cluster degraded"로 표시된다.
- **8.2.6-25에 들어 있는 모듈.** `GET /v1/modules`는 JSON, Bloom(`bf`), Search, time series를 버전 여러 개씩 보여 준다. 이전 Redis 버전의 DB가 계속 돌게 하려는 것이다. **RedisGears는 없다.** 그래서 RedisGears Python 1.2.6이 필요한 예전 RDI write-behind는 이 릴리스에서 돌 수 없다([`02-rdi`](../02-rdi/README.md) 참고).
- **DB 엔드포인트의 TLS.** `tls_mode: enabled`, `enforce_client_authentication: disabled`로 만든 DB는 평문 TCP 연결을 바로 끊었다. `ssl=True`인 redis-py 클라이언트는 `GET /v1/cluster/certificates`의 클러스터 프록시 인증서를 CA로 줬을 때만 연결됐고, 시스템 인증서 저장소로는 `CERTIFICATE_VERIFY_FAILED`로 실패했다. 자체 서명 인증서에 `localhost`가 아니라 클러스터 이름이 들어 있어 호스트 이름 검사는 껐다. TLS 연결 하나에서 PING 왕복은 0.13 ms.
- **이 README 이전 버전의 부트스트랩 명령은 깨져 있었다.** JSON을 큰따옴표 안에 큰따옴표로 넣어서 셸이 따옴표를 지웠다. 위에서 고쳤다.
- **LDAP 사용자는 역할을 거쳐 DB에 닿는다.** 연결 고리는 이렇다: 클러스터 LDAP 설정(바인드 사용자, 사용자 조회 `(cn=%u)`, 그룹 조회 `(member=%D)`, `data_plane` 켬을 담은 `PUT /v1/cluster/ldap`), Redis ACL `+@read ~*`, 역할 하나, `cn=redis-readers`에서 그 역할로의 LDAP 매핑, 역할과 ACL을 잇는 DB의 `roles_permissions`. 그룹에 든 `alice`는 `GET`이 됐고 `SET`은 `ldap_mapping:1`이라는 사용자 이름으로 거절됐다. 틀린 비밀번호는 `invalid username-password pair`. LDAP에는 있지만 매핑된 그룹이 없는 `bob`은 원인을 알기 어려운 `problem with LDAP service`를 받았다.
- **상호 TLS는 클라이언트도 확인한다.** `enforce_client_authentication: enabled`이고 클라이언트 인증서 하나를 등록한 DB는 인증서 없는 TLS 클라이언트(`CERTIFICATE_REQUIRED`)와 모르는 인증서의 클라이언트(`UNKNOWN_CA`)를 거절하고, 등록한 인증서는 받아들였다.

### 미실행 / 주의

- Active-Active는 클러스터가 여럿 필요해 실행하지 않았다. LDAP은 LDAPS가 아니라 평문 `ldap://`로 돌렸다.
- Redis Flex(RAM + SSD)는 로컬 NVMe 설정이 필요해 실행하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(컨테이너의 30일 체험 라이선스) |
| 확인한 버전 | Redis Software 8.2.6-25, Redis 8.8 DB, 2026-11-07 |
