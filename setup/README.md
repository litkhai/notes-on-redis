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
docker run --rm --network host -e REDIS_URL -v "$PWD/go:/src" -w /src golang:1.26 go run .          # go-redis
docker run --rm --network host -e REDIS_URL -v "$PWD/java:/src" -w /src maven:3-eclipse-temurin-21 \
  mvn -q compile org.codehaus.mojo:exec-maven-plugin:3.5.0:java -Dexec.mainClass=Smoke                    # Jedis
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

`go-redis and Jedis` output as it appeared (2026-11-07):

```text
$ docker run --rm --network host -e REDIS_URL -v "$PWD/go:/src" -w /src golang:1.26 go run .
go version go1.26.10 linux/amd64
go-redis 9.23.0
local: PING=PONG GET=ok version=8.10.3 protocol=3
cloud-free: PING=PONG GET=ok version=8.6.2 protocol=3

$ docker run --rm --network host -e REDIS_URL -v "$PWD/java:/src" -w /src maven:3-eclipse-temurin-21 mvn -q compile exec:java -Dexec.mainClass=Smoke
jedis 8.0.2
local: PING=PONG GET=ok version=8.10.3
cloud-free: PING=PONG GET=ok version=8.6.2
-- client-side caching (RESP3 + CacheConfig), local
first GET Ann 6.00 ms; next 1000 GETs Ann 16.13 ms in total; GETs that reached the server: 1
after another client's SET: Bea; reached the server: 1
```

### What was observed

- **No TLS on the free plan.** Turning TLS on through the REST API
  (`PUT /v1/fixed/subscriptions/{id}/databases/{id}` with `{"enableTls": true}`) failed with
  `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`: "Selected subscription plan does
  not support database 'enableTls'". The smoke test against the free database is plain TCP.
- `redis:latest` and `redis:8` pointed at the same digest as `8.10.3` on 2026-11-07; the compose
  file pins `8.10.3`.
- Redis Insight recognises the 8.x types: the key list shows ARRAY, VECTOR SET and TOPK keys
  from `local/02` with their own type labels.
- **go-redis and Jedis connect the same way.** go-redis 9.23.0 (it needs Go 1.26; the Go 1.24 image refused it) and Jedis 8.0.2 both reached the local server and the free database with a plain `redis://` URL. go-redis negotiated RESP3 with both, as redis-py 8.1 does in `local/03`.
- **Jedis caches on the client too.** With `RedisProtocol.RESP3` and a `CacheConfig`, 1,001 reads of one key sent one GET to the server, and another client's `SET` made the next read fetch the new value once: the same result as redis-py in `deep-dive/06`. Jedis 7.2 replaced `UnifiedJedis` and `JedisPooled` with `RedisClient`, which these examples use. The Jedis docs note that opt-in, opt-out and broadcasting modes "are not currently implemented by Jedis".
- **Pick versions from the registry, not a search page.** Maven Central's search API reported Jedis 6.0.0 as latest, while the repository metadata listed 8.0.2 as the newest stable release and 8.1.0-beta2 as the newest of all.

### Not run / caveats

- Redis Insight desktop was not installed; the Docker image is the same application.
- Other clients (Lettuce, StackExchange.Redis, redis-rs, ...) were not tried.

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

`go-redis and Jedis`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **무료 플랜에는 TLS가 없다.** REST API로 TLS를 켜려 하자
  (`PUT /v1/fixed/subscriptions/{id}/databases/{id}`, `{"enableTls": true}`)
  `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`으로 실패했다. 무료 DB 스모크 테스트는 평문 TCP다.
- 2026-11-07에 `redis:latest`와 `redis:8`은 `8.10.3`과 같은 digest였다. compose 파일은 `8.10.3`으로 고정한다.
- Redis Insight는 8.x 자료형을 알아본다. 키 목록에 `local/02`의 ARRAY, VECTOR SET, TOPK 키가 각자의 유형으로 표시된다.
- **go-redis와 Jedis도 같은 방식으로 붙는다.** go-redis 9.23.0(Go 1.26이 필요하고 Go 1.24 이미지는 거절했다)과 Jedis 8.0.2 모두 평범한 `redis://` URL로 로컬 서버와 무료 DB에 붙었다. go-redis는 두 곳 모두 RESP3로 협상했다. `local/03`의 redis-py 8.1과 같다.
- **Jedis도 클라이언트 측 캐시를 한다.** `RedisProtocol.RESP3`와 `CacheConfig`를 주자 한 키를 1,001번 읽는 동안 서버에 간 GET은 1번이었고, 다른 클라이언트의 `SET` 뒤 다음 읽기는 새 값을 한 번 가져왔다. `deep-dive/06`의 redis-py와 같은 결과다. Jedis 7.2는 `UnifiedJedis`, `JedisPooled`를 `RedisClient`로 대체했고, 이 예제가 그것을 쓴다. Jedis 문서는 opt-in, opt-out, 브로드캐스트 모드가 "are not currently implemented by Jedis"라고 적는다.
- **버전은 검색 페이지가 아니라 저장소에서 고른다.** Maven Central 검색 API는 Jedis 최신을 6.0.0으로 보고했지만, 저장소 메타데이터는 최신 안정판 8.0.2, 전체 최신 8.1.0-beta2를 보여 줬다.

### 미실행 / 주의

- Redis Insight 데스크톱은 설치하지 않았다. Docker 이미지가 같은 애플리케이션이다.
- 다른 클라이언트(Lettuce, StackExchange.Redis, redis-rs 등)는 시험하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free |
| 확인한 버전 | Redis 8.10.3(Docker), Redis Cloud 무료 플랜(Redis 8.6.2), Redis Insight 3.8.0, 2026-11-07 |
