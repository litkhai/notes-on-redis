# Setup

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (Docker `redis:8.10.3`) and Redis Cloud free plan (Redis 8.6.2), 2026-11-07.**

A local Redis Open Source 8 and Redis Insight in Docker, `redis-cli`, the Python and Node
clients, and a smoke test against both the local container and the Redis Cloud free database.
Host ports are 16379 and 15540 so the stack does not collide with anything else on a shared host.

### Run

```bash
docker compose up -d                       # nor-redis8 on 127.0.0.1:16379, nor-insight on 127.0.0.1:15540
docker exec -it nor-redis8 redis-cli PING
cp .env.example .env                       # REDIS_URL from the Redis Cloud console's Connect drawer
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python smoke.py
npm install && node smoke.mjs
set -a; . ./.env; set +a; docker run --rm redis:8.10.3 redis-cli -u "$REDIS_URL" --no-auth-warning PING
```

Output as it appeared (2026-11-07):

```text
$ .venv/bin/python smoke.py
redis-py 6.1.1
local: PING=True GET=ok version=8.10.3
cloud-free: PING=True GET=ok version=8.6.2

$ node smoke.mjs
node-redis 6.3.1
local: PING=PONG GET=ok version=8.10.3
cloud-free: PING=PONG GET=ok version=8.6.2

$ docker run --rm redis:8.10.3 redis-cli -u "$REDIS_URL" --no-auth-warning PING
PONG
```

Redis Insight 3.8.0 runs from the `redis/redisinsight` image at http://127.0.0.1:15540. The
`RI_REDIS_*` variables in `compose.yaml` register the local database at start, and
`RI_ACCEPT_TERMS_AND_CONDITIONS` skips the first-run dialog.

### What was observed

- **No TLS on the free plan.** Turning TLS on through the REST API
  (`PUT /v1/fixed/subscriptions/{id}/databases/{id}` with `{"enableTls": true}`) failed with
  `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`: "Selected subscription plan does
  not support database 'enableTls'". The smoke test against the free database is plain TCP.
- `redis:latest` and `redis:8` pointed at the same digest as `8.10.3` on 2026-11-07; the compose
  file pins `8.10.3`.
- Redis Insight recognises the 8.x types: the key list shows ARRAY, VECTOR SET and TOPK keys
  from `local/02` with their own type labels.

### Not run / caveats

- Redis Insight desktop was not installed; the Docker image is the same application.
- Clients other than redis-py and node-redis were not tried.

| | |
|---|---|
| Plan needed | Free |
| Verified on | Redis 8.10.3 (Docker), Redis Cloud free plan (Redis 8.6.2), Redis Insight 3.8.0, 2026-11-07 |

## 한국어

**확인: Redis 8.10.3(Docker `redis:8.10.3`)과 Redis Cloud 무료 플랜(Redis 8.6.2), 2026-11-07.**

Docker로 로컬 Redis Open Source 8과 Redis Insight를 띄우고, `redis-cli`, Python·Node 클라이언트로
로컬 컨테이너와 Redis Cloud 무료 DB에 스모크 테스트를 한다. 공용 호스트에서 다른 것과 겹치지 않게
호스트 포트는 16379, 15540을 쓴다.

### 실행

```bash
docker compose up -d                       # nor-redis8는 127.0.0.1:16379, nor-insight는 127.0.0.1:15540
docker exec -it nor-redis8 redis-cli PING
cp .env.example .env                       # Redis Cloud 콘솔 Connect 패널의 REDIS_URL
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python smoke.py
npm install && node smoke.mjs
set -a; . ./.env; set +a; docker run --rm redis:8.10.3 redis-cli -u "$REDIS_URL" --no-auth-warning PING
```

출력은 영문 절과 같다(2026-11-07). Redis Insight 3.8.0은 `redis/redisinsight` 이미지로
http://127.0.0.1:15540 에서 돈다. `compose.yaml`의 `RI_REDIS_*` 변수가 시작할 때 로컬 DB를 등록하고,
`RI_ACCEPT_TERMS_AND_CONDITIONS`가 첫 실행 창을 건너뛴다.

### 관찰한 것

- **무료 플랜에는 TLS가 없다.** REST API로 TLS를 켜려 하자
  (`PUT /v1/fixed/subscriptions/{id}/databases/{id}`, `{"enableTls": true}`)
  `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`으로 실패했다. 무료 DB 스모크 테스트는 평문 TCP다.
- 2026-11-07에 `redis:latest`와 `redis:8`은 `8.10.3`과 같은 digest였다. compose 파일은 `8.10.3`으로 고정한다.
- Redis Insight는 8.x 자료형을 알아본다. 키 목록에 `local/02`의 ARRAY, VECTOR SET, TOPK 키가 각자의 유형으로 표시된다.

### 미실행 / 주의

- Redis Insight 데스크톱은 설치하지 않았다. Docker 이미지가 같은 애플리케이션이다.
- redis-py, node-redis 외의 클라이언트는 시험하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free |
| 확인한 버전 | Redis 8.10.3(Docker), Redis Cloud 무료 플랜(Redis 8.6.2), Redis Insight 3.8.0, 2026-11-07 |
