# Streams

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

A stream `orders` with a consumer group `shipping`. Consumer `c1` reads three entries and dies; `c2` takes them over with `XAUTOCLAIM`. Then the three newer commands: `XACKDEL` (8.2) acknowledges and deletes in one call, `XADD … IDMP` (8.6) makes a producer's retry harmless, and `XNACK` (8.8) hands a message back without acknowledging it. From the command pages: XAUTOCLAIM "transfers ownership to consumer of messages pending for more than min-idle-time milliseconds"; XACKDEL helps "to both acknowledge entry processing and clean up the stream in a single atomic operation"; IDMP "Enables idempotent message processing (at-most-once production) to prevent duplicate entries"; XNACK releases messages that "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

Official documentation: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/).

### Run

```bash
./lab.sh   # starts and removes its own container
./more.sh  # XNACK modes, RETRYCOUNT, FORCE, IDMPAUTO, XCFGSET, XACKDEL with two groups
```

Output as it appeared (2026-11-07):

```text
== a group and two consumers
> XGROUP CREATE orders shipping 0
OK

> XREADGROUP GROUP shipping c1 COUNT 3 STREAMS orders >
1) 1) "orders"
   2) 1) 1) "0-1"
         2) 1) "item"
            2) "book-1"
      2) 1) "0-2"
         2) 1) "item"
            2) "book-2"
      3) 1) "0-3"
         2) 1) "item"
            2) "book-3"

== c1 dies without acknowledging; c2 claims what has been idle for 100 ms
> XPENDING orders shipping
1) (integer) 3
2) "0-1"
3) "0-3"
4) 1) 1) "c1"
      2) "3"

> XAUTOCLAIM orders shipping c2 100 0-0 COUNT 10
1) "0-0"
2) 1) 1) "0-1"
      2) 1) "item"
         2) "book-1"
   2) 1) "0-2"
      2) 1) "item"
         2) "book-2"
   3) 1) "0-3"
      2) 1) "item"
         2) "book-3"
3) (empty array)

> XPENDING orders shipping - + 10
1) 1) "0-1"
   2) "c2"
   3) (integer) 45
   4) (integer) 2
2) 1) "0-2"
   2) "c2"
   3) (integer) 45
   4) (integer) 2
3) 1) "0-3"
   2) "c2"
   3) (integer) 45
   4) (integer) 2

== XACKDEL (8.2): acknowledge and delete in one call
> XLEN orders
(integer) 5

> XACKDEL orders shipping IDS 2 0-1 0-2
1) (integer) 1
2) (integer) 1

> XLEN orders
(integer) 3

== IDMP (8.6): the same producer id and idempotency id twice
> XADD payments IDMP svc-a req-42 * amount 100
"1794043477638-0"

> XADD payments IDMP svc-a req-42 * amount 100
"1794043477638-0"

> XLEN payments
(integer) 1

== XNACK (8.8): give a claimed message back without acknowledging it
> XREADGROUP GROUP shipping c3 COUNT 1 STREAMS orders >
1) 1) "orders"
   2) 1) 1) "0-4"
         2) 1) "item"
            2) "book-4"

> XPENDING orders shipping - + 10
1) 1) "0-3"
   2) "c2"
   3) (integer) 435
   4) (integer) 2
2) 1) "0-4"
   2) "c3"
   3) (integer) 56
   4) (integer) 1

> XNACK orders shipping FAIL IDS 1 0-4
(integer) 1

> XPENDING orders shipping - + 10
1) 1) "0-3"
   2) "c2"
   3) (integer) 546
   4) (integer) 2
2) 1) "0-4"
   2) ""
   3) (integer) -1
   4) (integer) 1

> XREADGROUP GROUP shipping c4 COUNT 2 STREAMS orders >
1) 1) "orders"
   2) 1) 1) "0-5"
         2) 1) "item"
            2) "book-5"

> XPENDING orders shipping - + 10
1) 1) "0-3"
   2) "c2"
   3) (integer) 653
   4) (integer) 2
2) 1) "0-4"
   2) ""
   3) (integer) -1
   4) (integer) 1
3) 1) "0-5"
   2) "c4"
   3) (integer) 49
   4) (integer) 1

> XAUTOCLAIM orders shipping c5 60000 0-0 COUNT 10
1) "0-0"
2) 1) 1) "0-4"
      2) 1) "item"
         2) "book-4"
3) (empty array)

> XPENDING orders shipping - + 10
1) 1) "0-3"
   2) "c2"
   3) (integer) 749
   4) (integer) 2
2) 1) "0-4"
   2) "c5"
   3) (integer) 50
   4) (integer) 2
3) 1) "0-5"
   2) "c4"
   3) (integer) 145
   4) (integer) 1
```

`more.sh` output as it appeared (2026-11-07):

```text
== XNACK modes: one entry per mode, read by c1, then released
> XNACK s g SILENT IDS 1 0-1
(integer) 1

> XNACK s g FAIL IDS 1 0-2
(integer) 1

> XNACK s g FATAL IDS 1 0-3
(integer) 1

> XNACK s g FAIL IDS 1 0-4 RETRYCOUNT 5
(integer) 1

> XPENDING s g - + 10
1) 1) "0-1"
   2) ""
   3) (integer) -1
   4) (integer) 0
2) 1) "0-2"
   2) ""
   3) (integer) -1
   4) (integer) 1
3) 1) "0-3"
   2) ""
   3) (integer) -1
   4) (integer) 9223372036854775807
4) 1) "0-4"
   2) ""
   3) (integer) -1
   4) (integer) 5

== FORCE: an ID that is in the stream but not in the group's pending list
> XNACK s g FAIL IDS 1 0-5
(integer) 0

> XNACK s g FAIL IDS 1 0-5 FORCE
(integer) 1

> XPENDING s g 0-5 0-5 1
1) 1) "0-5"
   2) ""
   3) (integer) -1
   4) (integer) 0

== IDMPAUTO: the producer id only; the server derives the idempotent id
> XADD a IDMPAUTO svc-a * amount 100
"1794051592536-0"

> XADD a IDMPAUTO svc-a * amount 100
"1794051592536-0"

> XADD a IDMPAUTO svc-a * amount 200
"1794051592645-0"

> XLEN a
(integer) 2

== XCFGSET: IDMP-DURATION 1 s, then the same IDMP id after 2 s
> XCFGSET p IDMP-DURATION 1
OK

> XADD p IDMP svc-a req-1 * x 1
"1794051592871-0"

> XADD p IDMP svc-a req-1 * x 1
"1794051594928-0"

> XLEN p
(integer) 3

== XCFGSET: IDMP-MAXSIZE 2, three ids, then the first again
> XCFGSET m IDMP-DURATION 600 IDMP-MAXSIZE 2
OK

> XLEN m
(integer) 4

> XADD m IDMP svc-b r1 * x 1
"1794051595348-0"

> XLEN m
(integer) 5

== XACKDEL KEEPREF with two groups (g1 and g2 both read entry 0-1)
> XACKDEL t g1 KEEPREF IDS 1 0-1
1) (integer) 1

   XLEN t: 0; pending in g1: 0; pending in g2: 1
> XCLAIM t g2 c2 0 0-1
(empty array)

== XACKDEL DELREF with two groups (g1 and g2 both read entry 0-1)
> XACKDEL t g1 DELREF IDS 1 0-1
1) (integer) 1

   XLEN t: 0; pending in g1: 0; pending in g2: 0
== XACKDEL ACKED with two groups (g1 and g2 both read entry 0-1)
> XACKDEL t g1 ACKED IDS 1 0-1
1) (integer) 2

   XLEN t: 1; pending in g1: 0; pending in g2: 1
> XACKDEL t g2 ACKED IDS 1 0-1
1) (integer) 1

   XLEN t after g2 also acknowledged: 0
```

### What was observed

- **XAUTOCLAIM.** `c1` read 0-1 to 0-3 and never acknowledged them. After 100 ms idle, `XAUTOCLAIM … c2 100` moved all three to `c2`; the delivery count went from 1 to 2. Without it those entries stay with a dead consumer forever.
- **XACKDEL (8.2).** `XACKDEL orders shipping IDS 2 0-1 0-2` returned `1, 1` and `XLEN` dropped from 5 to 3. Before 8.2 this took `XACK` then `XDEL`, two calls with a window between them.
- **IDMP (8.6).** Two `XADD payments IDMP svc-a req-42 …` returned the same ID and `XLEN` stayed at 1. A producer that times out and resends no longer writes a duplicate.
- **XNACK (8.8).** After `XNACK … FAIL IDS 1 0-4` the entry stays in the pending list with no owner (consumer `""`, idle -1) and its delivery count unchanged at 1. A new `XREADGROUP … >` did **not** return it; it only reads new entries. `XAUTOCLAIM … c5 60000` claimed it at once even with a 60-second minimum idle time, while 0-3 and 0-5, idle for well under a second, stayed with their owners.
- **XNACK modes, measured.** After one delivery each: `SILENT` left the count at 0, `FAIL` at 1, `FATAL` at 9223372036854775807, and `RETRYCOUNT 5` set it to 5. All four entries were left unowned.
- **FORCE puts an entry into the pending list.** For an entry that no consumer had read, `XNACK` returned 0; with `FORCE` it returned 1 and the entry appeared unowned with count 0, ready for `XAUTOCLAIM`.
- **IDMPAUTO works from the content.** The same producer sending the same fields twice got the same ID; different fields got a new one.
- **`XCFGSET` forgets.** "Calling `XCFGSET` clears all existing producer IDMP maps", and it did: a retry sent right after it was accepted as new. With `IDMP-DURATION 1` the same idempotent ID was accepted again after 2 s, and with `IDMP-MAXSIZE 2` the oldest of three IDs was forgotten.
- **XACKDEL with two groups.** `KEEPREF` (the default) deleted the entry although the other group had not acknowledged it; that group kept a pending reference to an entry that no longer exists, and `XCLAIM` on it returned nothing. `DELREF` removed that reference too. `ACKED` returned 2 (acknowledged, not deleted) until the second group acknowledged as well, and only then deleted the entry.

### Not run / caveats

- IDMP across a primary and its replica was not looked at.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

스트림 `orders`와 소비자 그룹 `shipping`. 소비자 `c1`이 항목 셋을 읽고 죽는다. `c2`가 `XAUTOCLAIM`으로 넘겨받는다. 이어서 새 명령 셋: `XACKDEL`(8.2)은 확인과 삭제를 한 번에 하고, `XADD … IDMP`(8.6)는 생산자의 재시도를 무해하게 만들고, `XNACK`(8.8)은 메시지를 확인하지 않고 돌려준다. 명령 페이지의 표현: XAUTOCLAIM은 "transfers ownership to consumer of messages pending for more than min-idle-time milliseconds", XACKDEL은 "to both acknowledge entry processing and clean up the stream in a single atomic operation", IDMP는 "Enables idempotent message processing (at-most-once production) to prevent duplicate entries", XNACK으로 놓은 메시지는 "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

공식 문서: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/).

### 실행

```bash
./lab.sh   # starts and removes its own container
./more.sh  # XNACK modes, RETRYCOUNT, FORCE, IDMPAUTO, XCFGSET, XACKDEL with two groups
```

출력은 영문 절과 같다(2026-11-07).

`more.sh`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **XAUTOCLAIM.** `c1`이 0-1부터 0-3까지 읽고 확인하지 않았다. 100 ms가 지나자 `XAUTOCLAIM … c2 100`이 셋을 모두 `c2`로 옮겼고 전달 횟수는 1에서 2가 됐다. 이것이 없으면 그 항목들은 죽은 소비자에게 영원히 남는다.
- **XACKDEL (8.2).** `XACKDEL orders shipping IDS 2 0-1 0-2`가 `1, 1`을 돌려주고 `XLEN`은 5에서 3으로 줄었다. 8.2 전에는 `XACK` 뒤 `XDEL`, 사이에 틈이 있는 두 번의 호출이었다.
- **IDMP (8.6).** `XADD payments IDMP svc-a req-42 …` 두 번이 같은 ID를 돌려주고 `XLEN`은 1 그대로였다. 시간 초과로 다시 보낸 생산자가 더는 중복을 쓰지 않는다.
- **XNACK (8.8).** `XNACK … FAIL IDS 1 0-4` 뒤 항목은 주인 없이(consumer `""`, idle -1) 대기 목록에 남고 전달 횟수는 1 그대로다. 새 `XREADGROUP … >`는 이것을 돌려주지 **않았다**. `>`는 새 항목만 읽는다. `XAUTOCLAIM … c5 60000`은 최소 유휴 60초를 줬는데도 이것을 바로 가져갔고, 1초도 안 쉰 0-3과 0-5는 주인에게 남았다.
- **XNACK 모드를 실제로 쟀다.** 한 번씩 전달한 뒤: `SILENT`는 횟수를 0으로, `FAIL`은 1 그대로, `FATAL`은 9223372036854775807로, `RETRYCOUNT 5`는 5로 만들었다. 네 항목 모두 주인 없이 남았다.
- **FORCE는 항목을 대기 목록에 넣는다.** 아무 소비자도 읽지 않은 항목에 `XNACK`은 0을 돌려줬다. `FORCE`를 붙이면 1을 돌려주고, 항목이 주인 없이 횟수 0으로 나타나 `XAUTOCLAIM`을 기다린다.
- **IDMPAUTO는 내용으로 판단한다.** 같은 생산자가 같은 필드를 두 번 보내면 같은 ID, 필드가 다르면 새 ID였다.
- **`XCFGSET`은 잊어버린다.** "Calling `XCFGSET` clears all existing producer IDMP maps"라고 하고, 실제로 그 직후의 재시도는 새 항목으로 받아들여졌다. `IDMP-DURATION 1`이면 2초 뒤 같은 멱등 ID가 다시 받아들여졌고, `IDMP-MAXSIZE 2`면 세 ID 중 가장 오래된 것이 잊혔다.
- **두 그룹에서의 XACKDEL.** `KEEPREF`(기본값)는 다른 그룹이 확인하지 않았는데도 항목을 지웠다. 그 그룹에는 이미 없는 항목을 가리키는 대기 참조가 남았고, 그것에 `XCLAIM`하면 아무것도 돌아오지 않았다. `DELREF`는 그 참조까지 지웠다. `ACKED`는 두 번째 그룹도 확인할 때까지 2(확인함, 지우지 않음)를 돌려주고, 그다음에야 항목을 지웠다.

### 미실행 / 주의

- 주 서버와 복제본 사이의 IDMP는 보지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |
