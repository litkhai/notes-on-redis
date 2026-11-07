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
python3 modes.py   # OPTIN, OPTOUT, NOLOOP and the RESP2 redirect mode, on raw connections
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

`modes.py` output as it appeared (2026-11-07):

```text
== OPTIN: only reads after CLIENT CACHING YES are tracked
OPTIN, GET k:a, then CACHING YES + GET k:b     invalidations received for: ['k:b']
== OPTOUT: every read is tracked except after CLIENT CACHING NO
OPTOUT, GET k:c, then CACHING NO + GET k:d     invalidations received for: ['k:c']
== NOLOOP: the tracking connection writes the key it read
default, GET k:e, then its own SET k:e         invalidations received for: ['k:e']
NOLOOP, GET k:f, then its own SET k:f          invalidations received for: none
== RESP2 redirect: invalidations go to another connection subscribed to __redis__:invalidate
   subscriber: *3 $9 subscribe $20 __redis__:invalidate :1
   data connection: +OK | GET k:g -> $-1
   after another client's SET k:g, the subscriber got: *3 $7 message $20 __redis__:invalidate *1 $3 k:g
   the data connection itself got: nothing
```

### What was observed

- **One GET reached the server for 1,001 reads.** The first took 1.40 ms; the next 1,000 came from the client's memory in 33.83 ms in total.
- **Invalidation works without any code.** Another client's `SET` made the cache drop the key; the next read went to the server once and returned the new value `'Bea'`.
- **The server marks the connection.** `CLIENT LIST` shows flag `t` (tracking) on the cached client.
- **Broadcasting mode** sent `invalidate` pushes for `user:2:name` and `user:3:cart` and nothing for `order:9`, which is outside the `user:` prefix. Here the server keeps no per-key table, so it pushes every change under the prefix whether or not the client read it.
- **OPTIN and OPTOUT choose reads one by one.** With `OPTIN`, only the read after `CLIENT CACHING YES` was tracked: a change to `k:b` was pushed, a change to `k:a` was not. With `OPTOUT` it was the reverse: everything was tracked except the read after `CLIENT CACHING NO`.
- **NOLOOP stops echoes of your own writes.** In the default mode the connection that read `k:e` and then wrote it got an invalidation for its own write; with `NOLOOP` it got none.
- **RESP2 clients use a second connection.** A RESP2 connection cannot receive pushes, so `CLIENT TRACKING ON REDIRECT <id>` sends the invalidations to another connection subscribed to `__redis__:invalidate`, as a normal Pub/Sub `message` naming `k:g`. The data connection itself received nothing.

### Not run / caveats

- Timings come from one laptop over loopback; over a real network the saving per read is the round trip.

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
python3 modes.py   # OPTIN, OPTOUT, NOLOOP and the RESP2 redirect mode, on raw connections
```

출력은 영문 절과 같다(2026-11-07).

`modes.py`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **읽기 1,001번에 서버까지 간 GET은 1번.** 첫 GET은 1.40 ms, 이후 1,000번은 클라이언트 메모리에서 합계 33.83 ms.
- **무효화는 코드 없이 동작한다.** 다른 클라이언트의 `SET`으로 캐시가 키를 버렸고, 다음 읽기는 서버에 한 번 가서 새 값 `'Bea'`를 받았다.
- **서버가 연결에 표시를 남긴다.** `CLIENT LIST`에서 캐시 클라이언트에 `t`(tracking) 플래그가 보인다.
- **브로드캐스트 모드**는 `user:2:name`과 `user:3:cart`에 `invalidate` 푸시를 보냈고, `user:` 접두사 밖인 `order:9`에는 보내지 않았다. 이 모드에서 서버는 키별 표를 두지 않으므로, 클라이언트가 읽었든 아니든 접두사 아래의 모든 변경을 푸시한다.
- **OPTIN과 OPTOUT은 읽기를 하나씩 고른다.** `OPTIN`에서는 `CLIENT CACHING YES` 다음의 읽기만 추적됐다. `k:b`의 변경은 푸시됐고 `k:a`의 변경은 안 됐다. `OPTOUT`은 반대로, `CLIENT CACHING NO` 다음의 읽기만 빼고 모두 추적됐다.
- **NOLOOP은 자기 쓰기의 메아리를 막는다.** 기본 모드에서는 `k:e`를 읽고 쓴 연결이 자기 쓰기에 대한 무효화를 받았다. `NOLOOP`에서는 받지 않았다.
- **RESP2 클라이언트는 연결을 하나 더 쓴다.** RESP2 연결은 푸시를 받을 수 없으므로, `CLIENT TRACKING ON REDIRECT <id>`가 무효화를 `__redis__:invalidate`를 구독한 다른 연결로 보낸다. `k:g`를 담은 평범한 Pub/Sub `message`로 왔다. 데이터 연결 자체는 아무것도 받지 않았다.

### 미실행 / 주의

- 시간은 노트북 한 대의 루프백에서 쟀다. 실제 네트워크에서는 읽기 한 번당 왕복 시간만큼 아낀다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), redis-py 6.1.1, 2026-11-07 |
