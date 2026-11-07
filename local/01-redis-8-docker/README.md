# Redis 8 in Docker

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (Docker `redis:8.10.3`), 2026-11-07.**

What the official image actually runs: the version, the modules it loads and how, the absence of
a config file, and what `io-threads` changes on one host. Uses the `nor-redis8` container from
[`setup/compose.yaml`](../../setup/compose.yaml).

### Run

```bash
(cd ../../setup && docker compose up -d redis)
docker exec nor-redis8 redis-server --version
docker exec nor-redis8 redis-cli INFO server | grep -E "redis_version|redis_mode|config_file|io_threads"
docker exec nor-redis8 redis-cli MODULE LIST
docker exec nor-redis8 grep -n "loadmodule" /usr/local/bin/docker-entrypoint.sh
docker run -d --name nor-redis8-io4 -p 127.0.0.1:16380:6379 redis:8.10.3 \
  redis-server --save "" --appendonly no --io-threads 4
for c in nor-redis8 nor-redis8-io4; do
  docker exec $c redis-benchmark -q -t set,get -n 1000000 -c 200 -P 1 -d 64 --threads 4
done
docker rm -f nor-redis8-io4
```

Output as it appeared (2026-11-07):

```text
$ redis-server --version
Redis server v=8.10.3 sha=00000000:1 malloc=jemalloc-5.3.0 bits=64 build=fa199f3d245589d0

$ redis-cli INFO server
redis_version:8.10.3
redis_mode:standalone
config_file:
io_threads_active:0

$ redis-cli MODULE LIST        (condensed: name, ver, path)
search      81001  /usr/local/lib/redis/modules//redisearch.so
vectorset   1      (built in)
timeseries  81001  /usr/local/lib/redis/modules//redistimeseries.so
bf          81001  /usr/local/lib/redis/modules//redisbloom.so
ReJSON      81000  /usr/local/lib/redis/modules//rejson.so

$ grep -n loadmodule docker-entrypoint.sh
179:			set -- "$@" --loadmodule "$module"

$ redis-benchmark ... --threads 4    (two runs each)
== nor-redis8 run 1
SET: 124906.33 requests per second, p50=1.447 msec
GET: 121021.43 requests per second, p50=1.495 msec
== nor-redis8 run 2
SET: 124828.37 requests per second, p50=1.479 msec
GET: 124921.92 requests per second, p50=1.447 msec
== nor-redis8-io4 run 1
SET: 285144.00 requests per second, p50=0.423 msec
GET: 285225.31 requests per second, p50=0.407 msec
== nor-redis8-io4 run 2
SET: 285225.31 requests per second, p50=0.407 msec
GET: 285225.31 requests per second, p50=0.407 msec

$ redis-benchmark -n 2000000 -c 400 ... --threads 8
== nor-redis8, benchmark --threads 8
SET: 117405.34 requests per second, p50=3.247 msec
GET: 126686.52 requests per second, p50=2.999 msec
== nor-redis8-io4, benchmark --threads 8
SET: 332944.91 requests per second, p50=1.015 msec
GET: 347403.16 requests per second, p50=0.983 msec
```

### What was observed

- **No config file.** `config_file` is empty; the server runs on defaults plus command-line
  arguments. The entrypoint adds one `--loadmodule` per `.so` in
  `/usr/local/lib/redis/modules/`, which is how Search, JSON, Time series and Bloom arrive
  without any configuration. Vector sets are built into the server.
- **io-threads.** With `--io-threads 4` the server reports `io_threads_active:1`. On this
  24-core host SET/GET went from about 121,000–125,000 to 285,000 requests/s with a 4-thread
  benchmark client. The io-threads 4 numbers were identical in every run, so the client was the
  limit: with 8 client threads io-threads 4 reached 332,945–347,403 while io-threads 1 stayed at
  117,405–126,687. Server and client share the host; these are measurements on one machine, not
  a statement about Redis in general.

### Not run / caveats

- Persistence is off in this container (`--save ""`, `--appendonly no`); persistence has its own deep-dive lab.
- The benchmark ran inside the server's container, so client and server compete for the same CPUs.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3, Docker image `redis:8.10.3`, 2026-11-07 |

## 한국어

**확인: Redis 8.10.3(Docker `redis:8.10.3`), 2026-11-07.**

공식 이미지가 실제로 무엇을 돌리는지 본다. 버전, 싣는 모듈과 그 방법, 설정 파일이 없다는 것,
호스트 하나에서 `io-threads`가 바꾸는 것. [`setup/compose.yaml`](../../setup/compose.yaml)의
`nor-redis8` 컨테이너를 쓴다.

### 실행

```bash
(cd ../../setup && docker compose up -d redis)
docker exec nor-redis8 redis-server --version
docker exec nor-redis8 redis-cli INFO server | grep -E "redis_version|redis_mode|config_file|io_threads"
docker exec nor-redis8 redis-cli MODULE LIST
docker exec nor-redis8 grep -n "loadmodule" /usr/local/bin/docker-entrypoint.sh
docker run -d --name nor-redis8-io4 -p 127.0.0.1:16380:6379 redis:8.10.3 \
  redis-server --save "" --appendonly no --io-threads 4
for c in nor-redis8 nor-redis8-io4; do
  docker exec $c redis-benchmark -q -t set,get -n 1000000 -c 200 -P 1 -d 64 --threads 4
done
docker rm -f nor-redis8-io4
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **설정 파일이 없다.** `config_file`이 비어 있고, 서버는 기본값과 명령줄 인자로 돈다.
  진입점이 `/usr/local/lib/redis/modules/`의 `.so`마다 `--loadmodule`을 하나씩 붙인다.
  그래서 Search, JSON, Time series, Bloom이 아무 설정 없이 실린다. 벡터 셋은 서버에 내장돼 있다.
- **io-threads.** `--io-threads 4`로 띄우면 `io_threads_active:1`이 된다. 24코어 호스트에서
  4스레드 벤치마크로 SET/GET이 초당 약 121,000–125,000에서 285,000으로 올랐다. io-threads 4의
  수치가 매번 똑같아서 클라이언트가 한계였다. 클라이언트 스레드를 8로 늘리자 io-threads 4는
  332,945–347,403, io-threads 1은 117,405–126,687이었다. 서버와 클라이언트가 같은 호스트에 있다.
  기계 한 대에서 잰 값이지 Redis 일반에 대한 주장이 아니다.

### 미실행 / 주의

- 이 컨테이너는 영속성이 꺼져 있다(`--save ""`, `--appendonly no`). 영속성은 별도 딥다이브 실습에서 다룬다.
- 벤치마크를 서버 컨테이너 안에서 돌려 클라이언트와 서버가 같은 CPU를 나눠 썼다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3, Docker 이미지 `redis:8.10.3`, 2026-11-07 |
