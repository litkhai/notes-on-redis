# Threading and the event loop

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

Commands still execute on one main thread; `io-threads` moves reading requests and writing replies to helper threads. This lab runs the same `redis-benchmark` load against `io-threads` 1, 2, 4 and 8 and reads `INFO threads` after each run to see how the clients were spread.

Official documentation: [INFO](https://redis.io/docs/latest/commands/info/), [Benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/).

### Run

```bash
./run.sh      # starts nor-dd-thr four times; the benchmark runs in the server's network namespace
./more.sh     # io-threads 1/4/8 with pipelining (-P 16) and with TLS
./values.sh    # io-threads 1/4/8 with 4 KB values
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

`more.sh` output as it appeared (2026-11-07):

```text
== io-threads 1
-- plain TCP, pipeline 16
   SET: 1139384.75 requests per second, p50=5.207 msec
   GET: 1259710.25 requests per second, p50=4.591 msec
-- TLS, no pipelining
   SET: 90326.08 requests per second, p50=4.199 msec
   GET: 90481.36 requests per second, p50=4.135 msec
== io-threads 4
-- plain TCP, pipeline 16
   SET: 2660753.75 requests per second, p50=2.391 msec
   GET: 3424657.50 requests per second, p50=1.623 msec
-- TLS, no pipelining
   SET: 220896.84 requests per second, p50=1.519 msec
   GET: 219683.66 requests per second, p50=1.527 msec
== io-threads 8
-- plain TCP, pipeline 16
   SET: 2398081.50 requests per second, p50=2.367 msec
   GET: 3420752.75 requests per second, p50=1.743 msec
-- TLS, no pipelining
   SET: 392310.72 requests per second, p50=0.807 msec
   GET: 357142.88 requests per second, p50=0.767 msec
```

`values.sh` output as it appeared (2026-11-07):

```text
== io-threads 1, 4096-byte values
   SET: 110840.16 requests per second, p50=3.375 msec
   GET: 110889.34 requests per second, p50=3.439 msec
== io-threads 4, 4096-byte values
   SET: 285144.00 requests per second, p50=1.167 msec
   GET: 307219.66 requests per second, p50=1.191 msec
== io-threads 8, 4096-byte values
   SET: 443066.03 requests per second, p50=0.567 msec
   GET: 442477.88 requests per second, p50=0.559 msec
```

### What was observed

- `io-threads 2` was no faster than 1 (126,072–131,596 vs 134,523–136,097 requests/s). `INFO threads` shows why: thread 0, the main thread, handled no client I/O and the single extra thread took everything.
- `io-threads 4` reached 342,349–352,485 and `io-threads 8` 498,753–520,472 requests/s, with reads and writes spread almost evenly over the I/O threads.
- `io_threads_active` turns 1 as soon as more than one thread is configured.
- These are numbers from one 24-core host with the client on the same machine (12 benchmark threads), not a general scaling law.
- **With pipelining, four threads were the ceiling.** At `-P 16`, one thread did 1.14–1.26 M requests/s, four did 2.66–3.42 M, and eight no more than four (2.40–3.42 M). Pipelining already cuts the per-request I/O, so the main thread becomes the limit sooner.
- **With TLS the threads matter most.** Without pipelining, TLS on one thread did about 90,000 requests/s, a third less than plain TCP (about 135,000). Four threads gave about 220,000 and eight 357,000–392,000, because the I/O threads also do the encryption.
- **Larger values scale the same way.** With 4,096-byte values and no pipelining, one thread did about 111,000 requests/s, four 285,000–307,000 and eight about 443,000: per request a little below the 64-byte runs, with the same shape across thread counts.

### Not run / caveats

- TLS used a self-signed certificate and no client certificates.
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
./more.sh     # io-threads 1/4/8 with pipelining (-P 16) and with TLS
./values.sh    # io-threads 1/4/8 with 4 KB values
```

출력은 영문 절과 같다(2026-11-07).

`more.sh`의 출력도 영문 절과 같다(2026-11-07).

`values.sh`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- `io-threads 2`는 1보다 빠르지 않았다(초당 126,072–131,596 대 134,523–136,097). `INFO threads`가 이유를 보여 준다. 메인 스레드인 thread 0은 클라이언트 I/O를 하나도 처리하지 않았고, 추가 스레드 하나가 전부 맡았다.
- `io-threads 4`는 초당 342,349–352,485, `io-threads 8`은 498,753–520,472였다. 읽기·쓰기가 I/O 스레드들에 거의 고르게 나뉘었다.
- 스레드를 둘 이상 설정하면 `io_threads_active`가 1이 된다.
- 24코어 호스트 하나에서 클라이언트(벤치마크 스레드 12개)도 같은 기계에 둔 수치다. 일반적인 확장 법칙이 아니다.
- **파이프라이닝을 켜면 스레드 넷이 상한이었다.** `-P 16`에서 스레드 하나가 초당 114만–126만, 넷이 266만–342만, 여덟은 넷보다 많지 않았다(240만–342만). 파이프라이닝이 이미 요청당 I/O를 줄여서 메인 스레드가 더 빨리 한계가 된다.
- **TLS에서는 스레드가 가장 크게 효과를 낸다.** 파이프라이닝 없이 스레드 하나의 TLS는 초당 약 90,000으로 평문 TCP(약 135,000)보다 3분의 1 적었다. 넷이면 약 220,000, 여덟이면 357,000–392,000. I/O 스레드가 암호화도 맡기 때문이다.
- **큰 값도 같은 모양으로 늘어난다.** 4,096바이트 값, 파이프라이닝 없이 스레드 하나가 초당 약 111,000, 넷이 285,000–307,000, 여덟이 약 443,000. 요청 수로는 64바이트 실행보다 조금 낮지만 스레드 수에 따른 모양은 같다.

### 미실행 / 주의

- TLS는 자체 서명 인증서로, 클라이언트 인증서 없이 쟀다.
- 8.0의 I/O 스레딩 재작성은 릴리스 노트에 있다. 이 실습은 8.10.3만 잰다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |
