# REST API

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis Cloud REST API v1, free plan (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07.**

The REST API works on the free plan: turn on **Enable API** under **API Keys & Team**, create a user key, and send both keys on every call. From the docs: the account key (`x-api-key`) is an "Account-level key assigned to all users of an account", and the user key (`x-api-secret-key`) is a "Personal key associated with a specific user and possibly limited to certain IP ranges". Writes are asynchronous: "All create, update, and delete API operations (`POST`, `PUT`, and `DELETE`) and some query operations (`GET`) run asynchronously". The script reads the account, the subscription and the database, lists the Seoul plans with prices, changes one database setting through a task and restores it, and tries to add a second database.

Official documentation: [REST API](https://redis.io/docs/latest/operate/rc/api/), [Authenticate and authorize](https://redis.io/docs/latest/operate/rc/api/get-started/), [Enable the API](https://redis.io/docs/latest/operate/rc/api/get-started/enable-the-api/), [Manage API keys](https://redis.io/docs/latest/operate/rc/api/get-started/manage-api-keys/), [API lifecycle](https://redis.io/docs/latest/operate/rc/api/get-started/process-lifecycle/).

### Run

```bash
cp .env.example .env && chmod 600 .env   # fill in the account key and a user key
python3 rest.py                           # standard library only; about 30 s
```

Output as it appeared (2026-11-07). The script prints no IDs, names, endpoints, IP addresses or e-mail; the account endpoint returns the caller's public IP (`httpSourceIp`), which is why only field names are printed for it.

```text
== GET /  (who is calling)
   HTTP 200 in 247 ms; fields: ['createdTimestamp', 'id', 'key', 'name', 'updatedTimestamp']; key fields: ['accountId', 'accountName', 'allowedSourceIps', 'httpSourceIp', 'name', 'owner', 'userAccountId']

== GET /fixed/subscriptions  (free and Essentials live under /fixed; Pro under /subscriptions)
   HTTP 200; subscriptions: 1
   {'status': 'active', 'size': 30.0, 'sizeMeasurementUnit': 'MB', 'region': 'ap-northeast-2', 'price': 0, 'pricePeriod': 'Month', 'maximumDatabases': 1, 'availability': 'No replication', 'connections': '30', 'supportDataPersistence': False, 'supportInstantAndDailyBackups': False, 'supportReplication': False, 'supportClustering': False}
   GET /subscriptions (Pro) -> HTTP 200, 0 subscriptions

== GET /fixed/subscriptions/{id}/databases
   {'status': 'active', 'redisVersionCompliance': '8.6.2', 'respVersion': 'resp3', 'protocol': 'stack', 'planMemoryLimit': 30.0, 'memoryUsedInMb': 17.0, 'dataPersistence': 'none', 'replication': False, 'dataEvictionPolicy': 'volatile-lru', 'memoryStorage': 'ram'}
   modules: [('RedisBloom', '8.6.4'), ('search', '8.6.12'), ('RedisJSON', '8.6.6'), ('RedisTimeSeries', '8.6.12')]
   security: {'enableTls': False, 'defaultUserEnabled': True}
   alerts: {'datasets-size': 80, 'connections-limit': 80}

== GET /fixed/plans?provider=AWS  (Seoul only)
   HTTP 200; 618 AWS plans, 21 in ap-northeast-2
     30.0 MB  $   0/Month  No replication   persistence=False backups=False replication=False
    250.0 MB  $   6/Month  No replication   persistence=False backups=True  replication=False
    250.0 MB  $   7/Month  No replication   persistence=True  backups=True  replication=False
    250.0 MB  $   8/Month  Single-zone      persistence=False backups=True  replication=True
    250.0 MB  $  10/Month  Single-zone      persistence=True  backups=True  replication=True
      1.0 GB  $  22/Month  No replication   persistence=False backups=True  replication=False
      1.0 GB  $  24/Month  No replication   persistence=True  backups=True  replication=False
      1.0 GB  $  24/Month  Single-zone      persistence=False backups=True  replication=True
      1.0 GB  $  27/Month  Single-zone      persistence=True  backups=True  replication=True
      2.5 GB  $  44/Month  No replication   persistence=False backups=True  replication=False
      2.5 GB  $  48/Month  No replication   persistence=True  backups=True  replication=False
      2.5 GB  $  48/Month  Single-zone      persistence=False backups=True  replication=True
      2.5 GB  $  53/Month  Single-zone      persistence=True  backups=True  replication=True
      5.0 GB  $  85/Month  No replication   persistence=False backups=True  replication=False
      5.0 GB  $  93/Month  No replication   persistence=True  backups=True  replication=False
      5.0 GB  $  93/Month  Single-zone      persistence=False backups=True  replication=True
      5.0 GB  $ 103/Month  Single-zone      persistence=True  backups=True  replication=True
     12.0 GB  $ 212/Month  No replication   persistence=False backups=True  replication=False
     12.0 GB  $ 218/Month  Single-zone      persistence=False backups=True  replication=True
     12.0 GB  $ 234/Month  No replication   persistence=True  backups=True  replication=False
     12.0 GB  $ 240/Month  Single-zone      persistence=True  backups=True  replication=True

== PUT a database setting: the connections alert 80% -> 95%, through a task, then back
   PUT connections-limit=95 -> HTTP 202 in 325 ms, task fields ['commandType', 'description', 'links', 'status', 'taskId', 'timestamp'], status 'received'
   task states: processing-in-progress -> processing-completed; response: {}
   read back: {'datasets-size': 80, 'connections-limit': 95}
   PUT connections-limit=80 -> HTTP 202 in 319 ms, task fields ['commandType', 'description', 'links', 'status', 'taskId', 'timestamp'], status 'received'
   task states: processing-in-progress -> processing-completed; response: {}
   read back: {'datasets-size': 80, 'connections-limit': 80}

== POST a second database into the free subscription (maximumDatabases is 1)
   HTTP 202, status 'received'
   task states: processing-error; response: {'error': {'type': 'FIXED_DATABASE_FIXED_SUBSCRIPTION_REACHED_MAX_DATABASES_COUNT', 'status': '400 BAD_REQUEST', 'description': 'The provided Essentials subscription has reached the max databases count and cannot add another database to it'}}
   databases in the subscription afterwards: 1
```

### What was observed

- **Read calls are synchronous and quick:** about 300 ms each from Seoul. Free and Essentials subscriptions are under `/v1/fixed`, Pro under `/v1/subscriptions`, which returned an empty list here.
- **The free plan as the API sees it:** 30 MB, 30 connections, one database, no replication, persistence, backups or clustering. The 100 ops/s on the pricing page does not appear in the API.
- **The database:** Redis 8.6.2 with Bloom, Search, JSON and time series modules, RESP3, `volatile-lru`, TLS off. Two alerts are set by default at 80%: `datasets-size` and `connections-limit`. The connections alert is the one that e-mailed when the Iris services held 28 of 30 connections ([`iris/`](../../iris/)).
- **Prices from the API, 2026-11-07:** 21 Seoul plans from 30 MB at $0 to 12 GB at $240 a month. A 1 GB plan is $22 with nothing, $24 with persistence or replication, $27 with both.
- **A write is a task.** `PUT` returned HTTP 202 with a `taskId`. Polling `/v1/tasks/{id}` showed `processing-in-progress` then `processing-completed`, and reading the database back showed the new value. The alert went 80 → 95 → 80.
- **`alerts` replaces the whole list.** The first version of this script sent only `connections-limit`. The system log then showed "Datasets size alert is changed: active - false": the alert that was left out had been switched off. It was restored at once, and the script now sends every alert with one value changed.
- **Errors arrive in the task, not the HTTP status.** The `POST` for a second database also returned 202. The task then ended in `processing-error` with `FIXED_DATABASE_FIXED_SUBSCRIPTION_REACHED_MAX_DATABASES_COUNT`. A client that only checks the HTTP status would think it worked. The error text calls the free subscription an "Essentials subscription".
- **TLS:** the API refused `enableTls` on this plan with `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN` ([`cloud/01`](../01-free-database/README.md)).
- **The console logs every call.** **Logs → System log** listed each alert change with the key name `notes-on-redis-lab`, and the earlier 93.33% connections alert as a System entry.

### Not run / caveats

- Creating and deleting a database or a subscription was not run: the free subscription allows one database and it holds the Iris data. With an Essentials subscription ([#8](https://github.com/litkhai/notes-on-redis/issues/8)) the same calls apply.
- Backups, imports, cost estimates (`dryRun`) and the Pro endpoints were not run.
- Delete the user key in the console when you are done with the lab.

| | |
|---|---|
| Plan needed | Free |
| Verified on | Redis Cloud REST API v1, free plan (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07 |

## 한국어

**확인: Redis Cloud REST API v1, free plan (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07.**

REST API는 무료 플랜에서도 된다. **API Keys & Team**에서 **Enable API**를 켜고 사용자 키를 만든 뒤, 호출마다 키 둘을 함께 보낸다. 문서의 표현: 계정 키(`x-api-key`)는 "Account-level key assigned to all users of an account", 사용자 키(`x-api-secret-key`)는 "Personal key associated with a specific user and possibly limited to certain IP ranges". 쓰기는 비동기다: "All create, update, and delete API operations (`POST`, `PUT`, and `DELETE`) and some query operations (`GET`) run asynchronously". 스크립트는 계정·구독·DB를 읽고, 서울 플랜과 가격을 나열하고, DB 설정 하나를 태스크로 바꿨다 되돌리고, 두 번째 DB 추가를 시도한다.

공식 문서: [REST API](https://redis.io/docs/latest/operate/rc/api/), [Authenticate and authorize](https://redis.io/docs/latest/operate/rc/api/get-started/), [Enable the API](https://redis.io/docs/latest/operate/rc/api/get-started/enable-the-api/), [Manage API keys](https://redis.io/docs/latest/operate/rc/api/get-started/manage-api-keys/), [API lifecycle](https://redis.io/docs/latest/operate/rc/api/get-started/process-lifecycle/).

### 실행

```bash
cp .env.example .env && chmod 600 .env   # fill in the account key and a user key
python3 rest.py                           # standard library only; about 30 s
```

출력은 영문 절과 같다(2026-11-07). 스크립트는 ID, 이름, 엔드포인트, IP 주소, 이메일을 출력하지 않는다. 계정 엔드포인트는 호출한 쪽의 공인 IP(`httpSourceIp`)를 돌려주므로 거기서는 필드 이름만 출력한다.

### 관찰한 것

- **읽기 호출은 동기이고 빠르다.** 서울에서 호출마다 약 300 ms. 무료와 Essentials 구독은 `/v1/fixed` 아래, Pro는 `/v1/subscriptions` 아래이고 여기서는 빈 목록이었다.
- **API가 보는 무료 플랜:** 30 MB, 커넥션 30개, DB 하나, 복제·영속·백업·클러스터링 없음. 가격 페이지의 100 ops/s는 API에 나오지 않는다.
- **DB:** Redis 8.6.2, Bloom·Search·JSON·time series 모듈, RESP3, `volatile-lru`, TLS 꺼짐. 기본 알림 둘이 80%로 걸려 있다: `datasets-size`와 `connections-limit`. Iris 서비스가 커넥션 30개 중 28개를 잡았을 때 메일을 보낸 것이 이 커넥션 알림이다([`iris/`](../../iris/)).
- **API로 읽은 가격, 2026-11-07:** 서울 플랜 21개, 30 MB $0부터 12 GB 월 $240까지. 1 GB는 아무것도 없으면 $22, 영속이나 복제 중 하나면 $24, 둘 다면 $27.
- **쓰기는 태스크다.** `PUT`은 `taskId`와 함께 HTTP 202를 돌려줬다. `/v1/tasks/{id}`를 조회하니 `processing-in-progress` 다음 `processing-completed`였고, DB를 다시 읽으니 새 값이었다. 알림은 80 → 95 → 80.
- **`alerts`는 목록 전체를 바꾼다.** 이 스크립트의 첫 버전은 `connections-limit`만 보냈다. 그러자 시스템 로그에 "Datasets size alert is changed: active - false"가 남았다. 빠진 알림이 꺼진 것이다. 바로 되돌렸고, 지금 스크립트는 알림 전부를 보내면서 값 하나만 바꾼다.
- **오류는 HTTP 상태가 아니라 태스크에 온다.** 두 번째 DB를 만드는 `POST`도 202였다. 태스크가 `processing-error`, `FIXED_DATABASE_FIXED_SUBSCRIPTION_REACHED_MAX_DATABASES_COUNT`로 끝났다. HTTP 상태만 보는 클라이언트는 성공한 줄 안다. 오류 문구는 무료 구독을 "Essentials subscription"이라 부른다.
- **TLS:** 이 플랜에서 API는 `enableTls`를 `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`으로 거절했다([`cloud/01`](../01-free-database/README.md)).
- **콘솔은 모든 호출을 남긴다.** **Logs → System log**에 알림 변경마다 키 이름 `notes-on-redis-lab`이 남았고, 앞서의 93.33% 커넥션 알림은 System 항목으로 남았다.

### 미실행 / 주의

- DB나 구독의 생성·삭제는 실행하지 않았다. 무료 구독은 DB 하나만 허용하고 그 DB에 Iris 데이터가 있다. Essentials 구독([#8](https://github.com/litkhai/notes-on-redis/issues/8))에서는 같은 호출을 쓴다.
- 백업, 가져오기, 비용 추정(`dryRun`), Pro 엔드포인트는 실행하지 않았다.
- 실습을 마치면 콘솔에서 사용자 키를 지운다.

| | |
|---|---|
| 필요한 플랜 | Free |
| 확인한 버전 | Redis Cloud REST API v1, free plan (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07 |
