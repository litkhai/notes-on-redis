# Functions and ACL

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

A Lua library `shop` with a read-only function and a writing one, called with `FCALL` and `FCALL_RO`. Then three ACL users: key permissions split into read-only and write-only patterns, a selector that adds a narrow second rule set, and the Redis 8 change that put module commands into `@read` and `@write`. The functions page: "Functions provide the same core functionality as scripts but are first-class software artifacts of the database." The ACL page on selectors: "If a command matches either the user permissions or any selector, it is allowed." And on `%R~`: it "only grants permission to read from keys that match the given pattern."

Official documentation: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/).

### Run

```bash
./lab.sh   # starts and removes its own container
```

Output as it appeared (2026-11-07):

```text
== a function library
shop

> HSET item:1 name lamp stock 1
(integer) 2

> FCALL_RO stock 1 item:1
"1"

> FCALL sell 1 item:1
(integer) 0

> FCALL sell 1 item:1
(error) sold out

> FCALL_RO sell 1 item:1
(error) ERR Can not execute a script with write flag using *_ro command.

== key permissions: %R~ read-only keys, %W~ write-only keys
> ACL SETUSER app on >pw %R~catalog:* %W~events:* +@all
OK

> SET catalog:1 lamp
OK

[app]> GET catalog:1
"lamp"

[app]> SET catalog:1 chair
(error) NOPERM No permissions to access a key

[app]> XADD events:clicks * item 1
"1794043711705-0"

[app]> XRANGE events:clicks - +
(error) NOPERM No permissions to access a key

== a selector: base rules plus a second, narrower set
> ACL SETUSER rep on >pw ~report:* +@read (~audit:* +xadd)
OK

[rep]> GET report:1
(nil)

[rep]> XADD audit:log * who rep
"1794043711902-0"

[rep]> SET report:1 x
(error) NOPERM User rep has no permissions to run the 'set' command

[rep]> XADD report:log * who rep
(error) NOPERM No permissions to access a key

== +@all -@write in Redis 8: module write commands are in @write too
> ACL SETUSER ro on >pw ~* +@all -@write
OK

> JSON.SET doc $ {"a":1}
OK

[ro]> JSON.GET doc
"{\"a\":1}"

[ro]> JSON.SET doc $.a 2
(error) NOPERM User ro has no permissions to run the 'json.set' command

[ro]> TS.ADD temp * 1
(error) NOPERM User ro has no permissions to run the 'ts.add' command

== +@read alone: do module read commands come with it?
> ACL SETUSER rd on >pw ~* +@read
OK

[rd]> JSON.GET doc
"{\"a\":1}"

[rd]> TS.RANGE temp - +
(error) ERR TSDB: the key does not exist

== module commands in @write: names starting json. ts. bf. cf. cms. topk. tdigest. ft.
> ACL CAT write | grep -c -E '^(json|ts|bf|cf|cms|topk|tdigest|ft)\.'
47
```

### What was observed

- **Functions.** `sell` decremented stock to 0, then refused with its own `sold out` error. `stock` is registered with `no-writes` and runs under `FCALL_RO`. `FCALL_RO sell` is refused: `Can not execute a script with write flag using *_ro command`. That is what lets read-only functions run on replicas.
- **`%R~` and `%W~`.** User `app` could `GET catalog:1` but not `SET` it, and could `XADD events:clicks` but not `XRANGE` it. The permission follows each command's key specification, so one rule set can describe a reader of one keyspace and a writer of another.
- **Selector.** User `rep` reads `report:*`; the selector `(~audit:* +xadd)` adds exactly one thing, `XADD` on `audit:*`. `XADD report:log` failed because neither rule set allows both the command and the key.
- **`+@all -@write` blocks module writes.** User `ro` could `JSON.GET` but not `JSON.SET`, and `TS.ADD` was refused too. A user with only `+@read` could run `JSON.GET`. `ACL CAT write` lists 47 commands from JSON, time series, Bloom, cuckoo, count-min, top-k and t-digest; no `FT.*` command is among them.
- **The ACL page disagrees.** It still says "command categories, with the exception of +@all, never include module commands." On Redis 8.10.3 that is no longer true, as the two results above show. An ACL written for Redis 7 that relied on it now grants or blocks more than before.

### Not run / caveats

- `FUNCTION DUMP`/`RESTORE` and functions on a replica were not run.
- ACL files (`ACL SAVE`, `ACL LOAD`) and `ACL LOG` were not run.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

읽기 전용 함수 하나와 쓰는 함수 하나를 담은 Lua 라이브러리 `shop`을 `FCALL`과 `FCALL_RO`로 호출한다. 이어서 ACL 사용자 셋: 키 권한을 읽기 전용·쓰기 전용 패턴으로 나눈 사용자, 좁은 두 번째 규칙 묶음을 더한 셀렉터, 모듈 명령을 `@read`·`@write`에 넣은 Redis 8의 변화. 함수 페이지의 표현: "Functions provide the same core functionality as scripts but are first-class software artifacts of the database." ACL 페이지의 셀렉터 설명: "If a command matches either the user permissions or any selector, it is allowed." `%R~`는 "only grants permission to read from keys that match the given pattern."

공식 문서: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/).

### 실행

```bash
./lab.sh   # starts and removes its own container
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **Functions.** `sell`이 재고를 0으로 줄인 뒤 자체 오류 `sold out`으로 거절했다. `stock`은 `no-writes`로 등록돼 `FCALL_RO`로 돈다. `FCALL_RO sell`은 거절된다: `Can not execute a script with write flag using *_ro command`. 그래서 읽기 전용 함수를 복제본에서 돌릴 수 있다.
- **`%R~`와 `%W~`.** 사용자 `app`은 `GET catalog:1`은 되고 `SET`은 안 됐다. `XADD events:clicks`는 되고 `XRANGE`는 안 됐다. 권한은 명령마다의 키 명세를 따르므로, 규칙 묶음 하나로 한 키 공간의 독자이자 다른 키 공간의 작성자를 표현할 수 있다.
- **셀렉터.** 사용자 `rep`은 `report:*`를 읽는다. 셀렉터 `(~audit:* +xadd)`는 딱 하나, `audit:*`에 대한 `XADD`를 더한다. `XADD report:log`는 실패했다. 명령과 키를 함께 허락하는 규칙 묶음이 없기 때문이다.
- **`+@all -@write`는 모듈 쓰기도 막는다.** 사용자 `ro`는 `JSON.GET`은 되고 `JSON.SET`은 안 됐고, `TS.ADD`도 거절됐다. `+@read`만 가진 사용자도 `JSON.GET`을 실행했다. `ACL CAT write`에는 JSON, time series, Bloom, cuckoo, count-min, top-k, t-digest 명령 47개가 있고 `FT.*` 명령은 없다.
- **ACL 페이지는 다르게 말한다.** 여전히 "command categories, with the exception of +@all, never include module commands"라고 적혀 있다. 위 두 결과대로 Redis 8.10.3에서는 더 이상 사실이 아니다. 그 문장에 기대 Redis 7용으로 쓴 ACL은 이제 전보다 더 허락하거나 더 막는다.

### 미실행 / 주의

- `FUNCTION DUMP`/`RESTORE`와 복제본에서의 함수 실행은 하지 않았다.
- ACL 파일(`ACL SAVE`, `ACL LOAD`)과 `ACL LOG`는 실행하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |
