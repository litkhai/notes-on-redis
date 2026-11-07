# Client-side caching

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), redis-py 6.1.1, 2026-11-07.**

The client keeps values in its own memory and the server tells it when they change. redis-py 6.1.1 does this for you with `protocol=3` and a `CacheConfig`; the lab counts how many GETs reach the server and what happens when another client writes. Then it opens a raw RESP3 connection in broadcasting mode and watches the push messages. The docs: "In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." And: "In the broadcasting mode, the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

Official documentation: [Client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/).

### Run

```bash
python3 -m venv .venv && .venv/bin/pip install redis   # 5.1 or later; or reuse another lab's venv
../../cloud/01-free-database/.venv/bin/python lab.py   # starts and removes its own container
```

Output as it appeared (2026-11-07):

```text
== default mode: redis-py cache (RESP3, CLIENT TRACKING on)
   first GET 'Ann' 1.40 ms; next 1000 GETs 'Ann' 33.83 ms in total
   GETs that reached the server: 1
   after another client's SET: 'Bea'; reached the server: 1
   tracking clients on the server: [('12', 't')]

== broadcast mode on a raw RESP3 connection: CLIENT TRACKING ON BCAST PREFIX user:
   +OK
   SET user:2:name  -> pushed to the tracking connection: >2 $10 invalidate *1 $11 user:2:name
   SET order:9      -> pushed to the tracking connection: (nothing)
   SET user:3:cart  -> pushed to the tracking connection: >2 $10 invalidate *1 $11 user:3:cart
```

### What was observed

- **One GET reached the server for 1,001 reads.** The first took 1.40 ms; the next 1,000 came from the client's memory in 33.83 ms in total.
- **Invalidation works without any code.** Another client's `SET` made the cache drop the key; the next read went to the server once and returned the new value `'Bea'`.
- **The server marks the connection.** `CLIENT LIST` shows flag `t` (tracking) on the cached client.
- **Broadcasting mode** sent `invalidate` pushes for `user:2:name` and `user:3:cart` and nothing for `order:9`, which is outside the `user:` prefix. Here the server keeps no per-key table, so it pushes every change under the prefix whether or not the client read it.

### Not run / caveats

- Timings come from one laptop over loopback; over a real network the saving per read is the round trip.
- `OPTIN`/`OPTOUT` and `NOLOOP` were not run.
- The redirect mode for RESP2 clients was not run.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), redis-py 6.1.1, 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), redis-py 6.1.1, 2026-11-07.**

클라이언트가 값을 자기 메모리에 두고, 값이 바뀌면 서버가 알려준다. redis-py 6.1.1은 `protocol=3`과 `CacheConfig`만 주면 이걸 해 준다. 실습은 서버까지 간 GET 수와 다른 클라이언트가 쓸 때 일어나는 일을 센다. 이어서 날 RESP3 연결을 브로드캐스트 모드로 열고 푸시 메시지를 본다. 문서의 표현: "In the default mode, the server remembers what keys a given client accessed, and sends invalidation messages when the same keys are modified." 그리고 "In the broadcasting mode, the server does not attempt to remember what keys a given client accessed, so this mode costs no memory at all in the server side."

공식 문서: [클라이언트 측 캐시 레퍼런스](https://redis.io/docs/latest/develop/reference/client-side-caching/).

### 실행

```bash
python3 -m venv .venv && .venv/bin/pip install redis   # 5.1 or later; or reuse another lab's venv
../../cloud/01-free-database/.venv/bin/python lab.py   # starts and removes its own container
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **읽기 1,001번에 서버까지 간 GET은 1번.** 첫 GET은 1.40 ms, 이후 1,000번은 클라이언트 메모리에서 합계 33.83 ms.
- **무효화는 코드 없이 동작한다.** 다른 클라이언트의 `SET`으로 캐시가 키를 버렸고, 다음 읽기는 서버에 한 번 가서 새 값 `'Bea'`를 받았다.
- **서버가 연결에 표시를 남긴다.** `CLIENT LIST`에서 캐시 클라이언트에 `t`(tracking) 플래그가 보인다.
- **브로드캐스트 모드**는 `user:2:name`과 `user:3:cart`에 `invalidate` 푸시를 보냈고, `user:` 접두사 밖인 `order:9`에는 보내지 않았다. 이 모드에서 서버는 키별 표를 두지 않으므로, 클라이언트가 읽었든 아니든 접두사 아래의 모든 변경을 푸시한다.

### 미실행 / 주의

- 시간은 노트북 한 대의 루프백에서 쟀다. 실제 네트워크에서는 읽기 한 번당 왕복 시간만큼 아낀다.
- `OPTIN`/`OPTOUT`과 `NOLOOP`은 실행하지 않았다.
- RESP2 클라이언트용 리디렉션 모드는 실행하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), redis-py 6.1.1, 2026-11-07 |
