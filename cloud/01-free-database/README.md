# Free database

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.6.2 (Redis Cloud free plan, AWS ap-northeast-2), 2026-11-07.**

The free 30 MB database, created in the console in Seoul, probed from a client in Korea with
redis-py 6.1.1 over plain TCP (the free plan has no TLS: turning it on is refused, see `setup/`). The plan advertises
30 MB, 30 connections and 100 ops/s; the first two were enforced, the third was not.

### Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # paste the URL from the console's Connect drawer (eye icon shows the password)
.venv/bin/python limits.py info
.venv/bin/python limits.py ops
.venv/bin/python long_ops.py 60
.venv/bin/python limits.py conns
.venv/bin/python limits.py memory
.venv/bin/python limits.py cleanup
```

Output as it appeared (2026-11-07, 04:47–04:51 UTC):

```text
$ limits.py info
redis_version: 8.6.2
PING: True
used_memory_human: 1.93M
maxmemory_human: None
maxmemory_policy: volatile-lru
CONFIG GET maxclients: {}
connected_clients: 0
PING round trip, mean of 50: 2.6 ms

$ limits.py ops
connections=1 pipeline=off: 3738 ops in 15.0 s = 249 ops/s; errors=none
connections=8 pipeline=off: 35459 ops in 15.0 s = 2363 ops/s; errors=none
connections=1 pipeline=100: 370100 ops in 15.0 s = 24671 ops/s; errors=none
connections=8 pipeline=100: 1559200 ops in 15.0 s = 103920 ops/s; errors=none

$ long_ops.py 60          (8 connections, pipeline 100, sampled every 5 s)
t=   5s    100840 INCR/s
t=  30s    107660 INCR/s
t=  55s    103540 INCR/s
errors: none
t=  60s    102100 INCR/s

$ limits.py conns
connection #31: ConnectionError: max number of clients reached
connections held by this script: 30
server connected_clients: 24

$ limits.py memory        (10 kB values, pipelines of 50)
after 2800 keys of 10 kB (0.6 s): OutOfMemoryError: Command # 18 (SET lab:limits:mem:2817...) of pipeline caused error: command not allowed when used memory > 'maxmemory'.
used_memory_human: 2.4M maxmemory_human: None
evicted_keys: 0
SET with EX after OOM: OutOfMemoryError command not allowed when used memory > 'maxmemory'.

$ limits.py cleanup
deleted keys: 2826 dbsize: 0
```

`long_ops.py` printed twelve samples; the middle ones (104,440–108,780 INCR/s) are omitted above.

### What was observed

- **Connections:** the 31st connection is refused with `max number of clients reached`.
  `INFO clients` is not a reliable count here: it reported 24 while the script held 30.
- **Memory:** writes stop at about 28 MB of values (2,817 keys of 10,000 bytes) with
  `OOM command not allowed`. The eviction policy is `volatile-lru` and no key had a TTL, so
  nothing could be evicted; even a `SET … EX` is refused once the limit is reached.
  `INFO memory` does not report the dataset (`used_memory_human` stayed at 2.4M and
  `maxmemory` is empty); the console's Metrics tab showed 21.77 MB used.
- **Throughput:** no throttling at 60 s and about 104,000 ops/s. The console's Configuration
  tab showed "61,806 / 100 Ops/sec" with a warning, so the 100 ops/s figure is reported
  against, not enforced, at least on this day. A single connection without pipelining is
  bound by the 2.6 ms round trip (249 ops/s), not by the plan.
- `CONFIG GET` returns nothing: configuration is managed by the service, not the client.

### Not run / caveats

- The free plan cannot use TLS; the numbers are for plain TCP from one host in Korea.
- Throttling may exist over longer windows or be introduced later; only 60 s was tested.
- The database is kept for the Iris labs; the test keys were deleted.

| | |
|---|---|
| Plan needed | Free |
| Verified on | Redis 8.6.2, Redis Cloud free plan, AWS ap-northeast-2, 2026-11-07 |

## 한국어

**확인: Redis 8.6.2(Redis Cloud 무료 플랜, AWS ap-northeast-2), 2026-11-07.**

서울에 콘솔로 만든 무료 30 MB DB를, 한국의 클라이언트에서 redis-py 6.1.1과 평문 TCP로
시험했다(무료 플랜에는 TLS가 없다. 켜려 하면 거절된다, `setup/` 참고). 플랜은 30 MB, 커넥션 30개, 100 ops/s를 안내한다.
앞의 둘은 실제로 걸렸고 세 번째는 걸리지 않았다.

### 실행

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # 콘솔 Connect 패널의 URL을 붙여 넣는다(눈 아이콘을 누르면 비밀번호가 보임)
.venv/bin/python limits.py info
.venv/bin/python limits.py ops
.venv/bin/python long_ops.py 60
.venv/bin/python limits.py conns
.venv/bin/python limits.py memory
.venv/bin/python limits.py cleanup
```

출력은 영문 절과 같다(2026-11-07, 04:47–04:51 UTC). 같은 출력을 두 번 싣지 않는다.

### 관찰한 것

- **커넥션:** 31번째 연결이 `max number of clients reached`로 거절된다. `INFO clients`는
  믿을 만한 수가 아니다. 스크립트가 30개를 잡고 있을 때 24로 나왔다.
- **메모리:** 값 약 28 MB(10,000바이트 키 2,817개)에서 `OOM command not allowed`로 쓰기가
  멈춘다. 축출 정책이 `volatile-lru`인데 TTL 있는 키가 없어서 아무것도 축출되지 않았다.
  한도에 닿은 뒤에는 `SET … EX`도 거절된다. `INFO memory`는 데이터 크기를 보여 주지 않는다
  (`used_memory_human`은 2.4M, `maxmemory`는 비어 있음). 콘솔 Metrics 탭은 21.77 MB를 보였다.
- **처리량:** 60초 동안 초당 약 104,000 연산에서도 제한이 없었다. 콘솔 Configuration 탭은
  경고와 함께 "61,806 / 100 Ops/sec"를 표시했다. 적어도 이날 100 ops/s는 강제가 아니라
  비교 표시용이었다. 파이프라인 없는 연결 하나는 플랜이 아니라 2.6 ms 왕복에 묶인다(249 ops/s).
- `CONFIG GET`은 아무것도 돌려주지 않는다. 설정은 클라이언트가 아니라 서비스가 관리한다.

### 미실행 / 주의

- 무료 플랜은 TLS를 쓸 수 없다. 수치는 한국의 호스트 하나에서 평문 TCP로 잰 것이다.
- 더 긴 구간에서 제한이 있거나 나중에 생길 수 있다. 60초만 시험했다.
- DB는 Iris 실습에 쓰려고 남겨 둔다. 시험 키는 지웠다.

| | |
|---|---|
| 필요한 플랜 | Free |
| 확인한 버전 | Redis 8.6.2, Redis Cloud 무료 플랜, AWS ap-northeast-2, 2026-11-07 |
