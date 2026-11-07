# Streams

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

A stream `orders` with a consumer group `shipping`. Consumer `c1` reads three entries and dies; `c2` takes them over with `XAUTOCLAIM`. Then the three newer commands: `XACKDEL` (8.2) acknowledges and deletes in one call, `XADD … IDMP` (8.6) makes a producer's retry harmless, and `XNACK` (8.8) hands a message back without acknowledging it. From the command pages: XAUTOCLAIM "transfers ownership to consumer of messages pending for more than min-idle-time milliseconds"; XACKDEL helps "to both acknowledge entry processing and clean up the stream in a single atomic operation"; IDMP "Enables idempotent message processing (at-most-once production) to prevent duplicate entries"; XNACK releases messages that "become immediately available for re-delivery to other consumers in the group, eliminating the idle-timeout delay normally required for message recovery."

Official documentation: [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [XACKDEL](https://redis.io/docs/latest/commands/xackdel/), [XADD](https://redis.io/docs/latest/commands/xadd/), [XNACK](https://redis.io/docs/latest/commands/xnack/).

### Run

```bash
./lab.sh   # starts and removes its own container
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

### What was observed

- **XAUTOCLAIM.** `c1` read 0-1 to 0-3 and never acknowledged them. After 100 ms idle, `XAUTOCLAIM … c2 100` moved all three to `c2`; the delivery count went from 1 to 2. Without it those entries stay with a dead consumer forever.
- **XACKDEL (8.2).** `XACKDEL orders shipping IDS 2 0-1 0-2` returned `1, 1` and `XLEN` dropped from 5 to 3. Before 8.2 this took `XACK` then `XDEL`, two calls with a window between them.
- **IDMP (8.6).** Two `XADD payments IDMP svc-a req-42 …` returned the same ID and `XLEN` stayed at 1. A producer that times out and resends no longer writes a duplicate.
- **XNACK (8.8).** After `XNACK … FAIL IDS 1 0-4` the entry stays in the pending list with no owner (consumer `""`, idle -1) and its delivery count unchanged at 1. A new `XREADGROUP … >` did **not** return it; it only reads new entries. `XAUTOCLAIM … c5 60000` claimed it at once even with a 60-second minimum idle time, while 0-3 and 0-5, idle for well under a second, stayed with their owners.
- **XNACK modes.** `SILENT` takes the delivery back (count −1), `FAIL` keeps the count, `FATAL` sets it to the maximum so the message is treated as poison.

### Not run / caveats

- `XNACK` modes `SILENT` and `FATAL`, `RETRYCOUNT` and `FORCE` were not run; their behaviour above is from the command page.
- `IDMPAUTO` and the IDMP retention settings (`XCFGSET`) were not run.
- `XACKDEL` with several groups (`KEEPREF`, `DELREF`, `ACKED`) was not run.

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
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **XAUTOCLAIM.** `c1`이 0-1부터 0-3까지 읽고 확인하지 않았다. 100 ms가 지나자 `XAUTOCLAIM … c2 100`이 셋을 모두 `c2`로 옮겼고 전달 횟수는 1에서 2가 됐다. 이것이 없으면 그 항목들은 죽은 소비자에게 영원히 남는다.
- **XACKDEL (8.2).** `XACKDEL orders shipping IDS 2 0-1 0-2`가 `1, 1`을 돌려주고 `XLEN`은 5에서 3으로 줄었다. 8.2 전에는 `XACK` 뒤 `XDEL`, 사이에 틈이 있는 두 번의 호출이었다.
- **IDMP (8.6).** `XADD payments IDMP svc-a req-42 …` 두 번이 같은 ID를 돌려주고 `XLEN`은 1 그대로였다. 시간 초과로 다시 보낸 생산자가 더는 중복을 쓰지 않는다.
- **XNACK (8.8).** `XNACK … FAIL IDS 1 0-4` 뒤 항목은 주인 없이(consumer `""`, idle -1) 대기 목록에 남고 전달 횟수는 1 그대로다. 새 `XREADGROUP … >`는 이것을 돌려주지 **않았다**. `>`는 새 항목만 읽는다. `XAUTOCLAIM … c5 60000`은 최소 유휴 60초를 줬는데도 이것을 바로 가져갔고, 1초도 안 쉰 0-3과 0-5는 주인에게 남았다.
- **XNACK 모드.** `SILENT`는 전달을 되돌리고(횟수 −1), `FAIL`은 횟수를 유지하고, `FATAL`은 최댓값으로 올려 독 메시지로 취급하게 한다.

### 미실행 / 주의

- `XNACK`의 `SILENT`·`FATAL` 모드, `RETRYCOUNT`, `FORCE`는 실행하지 않았다. 위 설명은 명령 페이지 기준이다.
- `IDMPAUTO`와 IDMP 보관 설정(`XCFGSET`)은 실행하지 않았다.
- 여러 그룹에서의 `XACKDEL`(`KEEPREF`, `DELREF`, `ACKED`)은 실행하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |
