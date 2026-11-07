# Threading and the event loop

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

Commands still execute on one main thread; `io-threads` moves reading requests and writing replies to helper threads. This lab runs the same `redis-benchmark` load against `io-threads` 1, 2, 4 and 8 and reads `INFO threads` after each run to see how the clients were spread.

Official documentation: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/).

### Run

```bash
./run.sh      # starts nor-dd-thr four times; the benchmark runs in the server's network namespace
```

Output as it appeared (2026-11-07):

```text
== io-threads 1
io_threads_active:0
SET: 134523.11 requests per second, p50=2.807 msec
GET: 136097.62 requests per second, p50=2.775 msec
SET: 136072.92 requests per second, p50=2.767 msec
GET: 136091.45 requests per second, p50=2.767 msec
-- INFO threads (after load)
io_thread_0:clients=2,reads=12001676,writes=12000072
== io-threads 2
io_threads_active:1
SET: 126071.61 requests per second, p50=2.927 msec
GET: 128760.89 requests per second, p50=2.879 msec
SET: 128860.45 requests per second, p50=2.895 msec
GET: 131596.25 requests per second, p50=2.815 msec
-- INFO threads (after load)
io_thread_0:clients=0,reads=0,writes=0
io_thread_1:clients=2,reads=12001694,writes=12000090
== io-threads 4
io_threads_active:1
SET: 342348.53 requests per second, p50=1.015 msec
GET: 352485.03 requests per second, p50=0.983 msec
SET: 342387.59 requests per second, p50=1.015 msec
GET: 352402.22 requests per second, p50=0.983 msec
-- INFO threads (after load)
io_thread_0:clients=0,reads=0,writes=0
io_thread_1:clients=1,reads=4026882,writes=4026342
io_thread_2:clients=0,reads=4009623,writes=4009088
io_thread_3:clients=1,reads=3965130,writes=3964601
== io-threads 8
io_threads_active:1
SET: 520471.91 requests per second, p50=0.479 msec
GET: 498919.00 requests per second, p50=0.487 msec
SET: 498753.12 requests per second, p50=0.487 msec
GET: 498753.12 requests per second, p50=0.495 msec
-- INFO threads (after load)
io_thread_0:clients=0,reads=0,writes=0
io_thread_1:clients=1,reads=1736347,writes=1736111
io_thread_2:clients=1,reads=1714452,writes=1714224
io_thread_3:clients=0,reads=1727173,writes=1726945
io_thread_4:clients=0,reads=1719343,writes=1719115
io_thread_5:clients=0,reads=1713025,writes=1712797
io_thread_6:clients=0,reads=1698766,writes=1698538
io_thread_7:clients=0,reads=1692519,writes=1692291
```

### What was observed

- `io-threads 2` was no faster than 1 (126,072–131,596 vs 134,523–136,097 requests/s). `INFO threads` shows why: thread 0, the main thread, handled no client I/O and the single extra thread took everything.
- `io-threads 4` reached 342,349–352,485 and `io-threads 8` 498,753–520,472 requests/s, with reads and writes spread almost evenly over the I/O threads.
- `io_threads_active` turns 1 as soon as more than one thread is configured.
- These are numbers from one 24-core host with the client on the same machine (12 benchmark threads), not a general scaling law.

### Not run / caveats

- Pipelining, larger values and TLS (where I/O threads also do the encryption) were not tried.
- Redis 8.0's I/O threading rewrite is described in the release notes; this lab only measures 8.10.3.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

명령은 여전히 메인 스레드 하나에서 실행된다. `io-threads`는 요청 읽기와 응답 쓰기를 보조 스레드로 옮긴다. 이 실습은 같은 `redis-benchmark` 부하를 `io-threads` 1, 2, 4, 8에 걸고, 실행마다 `INFO threads`로 클라이언트가 어떻게 나뉘었는지 본다.

공식 문서: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/).

### 실행

```bash
./run.sh      # starts nor-dd-thr four times; the benchmark runs in the server's network namespace
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- `io-threads 2`는 1보다 빠르지 않았다(초당 126,072–131,596 대 134,523–136,097). `INFO threads`가 이유를 보여 준다. 메인 스레드인 thread 0은 클라이언트 I/O를 하나도 처리하지 않았고, 추가 스레드 하나가 전부 맡았다.
- `io-threads 4`는 초당 342,349–352,485, `io-threads 8`은 498,753–520,472였다. 읽기·쓰기가 I/O 스레드들에 거의 고르게 나뉘었다.
- 스레드를 둘 이상 설정하면 `io_threads_active`가 1이 된다.
- 24코어 호스트 하나에서 클라이언트(벤치마크 스레드 12개)도 같은 기계에 둔 수치다. 일반적인 확장 법칙이 아니다.

### 미실행 / 주의

- 파이프라이닝, 큰 값, TLS(I/O 스레드가 암호화도 맡는 경우)는 시험하지 않았다.
- 8.0의 I/O 스레딩 재작성은 릴리스 노트에 있다. 이 실습은 8.10.3만 잰다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |
