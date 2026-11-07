# Functions and ACL

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

A Lua library `shop` with a read-only function and a writing one, called with `FCALL` and `FCALL_RO`. Then three ACL users: key permissions split into read-only and write-only patterns, a selector that adds a narrow second rule set, and the Redis 8 change that put module commands into `@read` and `@write`. The functions page: "Functions provide the same core functionality as scripts but are first-class software artifacts of the database." The ACL page on selectors: "If a command matches either the user permissions or any selector, it is allowed." And on `%R~`: it "only grants permission to read from keys that match the given pattern."

Official documentation: [Redis functions](https://redis.io/docs/latest/develop/programmability/functions-intro/), [FCALL_RO](https://redis.io/docs/latest/commands/fcall_ro/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/).

### Run

```bash
./lab.sh   # starts and removes its own container
./more.sh  # functions on a replica, FUNCTION DUMP/RESTORE, an ACL file, ACL LOG
./acl_replica.sh   # do ACL users created on a primary reach its replica?
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

`more.sh` output as it appeared (2026-11-07):

```text
replica link: role:slave master_link_status:up
== a library on the primary
shop
[nor-dd-fa-p]> HSET item:1 stock 5
(integer) 1

== the replica got the library through replication
[nor-dd-fa-r]> FUNCTION LIST LIBRARYNAME shop
1) 1) "library_name"
   2) "shop"
   3) "engine"
   4) "LUA"
   5) "functions"
   6) 1) 1) "name"
         2) "stock"
         3) "description"
         4) (nil)
         5) "flags"
         6) 1) no-writes
      2) 1) "name"
         2) "sell"
         3) "description"
         4) (nil)
         5) "flags"
         6) (empty array)

[nor-dd-fa-r]> FCALL_RO stock 1 item:1
"5"

[nor-dd-fa-r]> FCALL sell 1 item:1
(error) READONLY You can't write against a read only replica.

== FUNCTION DUMP from the primary, FUNCTION RESTORE into an unrelated server
189
[nor-dd-fa-x]> FUNCTION RESTORE <dump>
OK

[nor-dd-fa-x]> FUNCTION LIST
1) 1) "library_name"
   2) "shop"
   3) "engine"
   4) "LUA"
   5) "functions"
   6) 1) 1) "name"
         2) "sell"
         3) "description"
         4) (nil)
         5) "flags"
         6) (empty array)
      2) 1) "name"
         2) "stock"
         3) "description"
         4) (nil)
         5) "flags"
         6) 1) no-writes

[nor-dd-fa-x]> FUNCTION RESTORE x
(error) ERR DUMP payload version or checksum are wrong

== an ACL file: ACL SAVE writes it, ACL LOAD reads it back
[nor-dd-fa-p]> ACL SETUSER reporter on >pw ~report:* +@read
OK

[nor-dd-fa-p]> ACL SAVE
OK

[nor-dd-fa-p]$ cat /data/users.acl   (password hashes shortened here)
user default on nopass sanitize-payload ~* &* +@all
user reporter on sanitize-payload #30c952fa... ~report:* resetchannels -@all +@read

[nor-dd-fa-p]> ACL LOAD
OK

[nor-dd-fa-p]> ACL USERS
1) "default"
2) "ops"
3) "reporter"

[nor-dd-fa-p]> ACL LOAD
(error) ERR /data/users.acl:5: Error in applying operation '+nosuchcommand': Unknown command or category name in ACL. WARNING: ACL errors detected, no change to the previously active ACL rules was performed

[nor-dd-fa-p]> ACL USERS
1) "default"
2) "ops"
3) "reporter"

== ACL LOG: a wrong password and a denied command
[nor-dd-fa-p]> ACL LOG RESET
OK

[nor-dd-fa-p]> ACL LOG (fields: reason, context, object, username)
   count 1 reason key context toplevel object secret:1 username reporter
   count 1 reason command context toplevel object set username reporter
   count 1 reason auth context toplevel object AUTH username reporter
```

`acl_replica.sh` output as it appeared (2026-11-07):

```text
[nor-aclr-p]> ACL SETUSER reporter on >pw ~report:* +@read
OK

[nor-aclr-p]> SET report:1 x
OK

[nor-aclr-r]> ACL USERS
1) "default"

[nor-aclr-r]> GET report:1
"x"

[nor-aclr-r]> GET report:1 as reporter
AUTH failed: WRONGPASS invalid username-password pair or user is disabled.
x
```

### What was observed

- **Functions.** `sell` decremented stock to 0, then refused with its own `sold out` error. `stock` is registered with `no-writes` and runs under `FCALL_RO`. `FCALL_RO sell` is refused: `Can not execute a script with write flag using *_ro command`. That is what lets read-only functions run on replicas.
- **`%R~` and `%W~`.** User `app` could `GET catalog:1` but not `SET` it, and could `XADD events:clicks` but not `XRANGE` it. The permission follows each command's key specification, so one rule set can describe a reader of one keyspace and a writer of another.
- **Selector.** User `rep` reads `report:*`; the selector `(~audit:* +xadd)` adds exactly one thing, `XADD` on `audit:*`. `XADD report:log` failed because neither rule set allows both the command and the key.
- **`+@all -@write` blocks module writes.** User `ro` could `JSON.GET` but not `JSON.SET`, and `TS.ADD` was refused too. A user with only `+@read` could run `JSON.GET`. `ACL CAT write` lists 47 commands from JSON, time series, Bloom, cuckoo, count-min, top-k and t-digest; no `FT.*` command is among them.
- **The ACL page disagrees.** It still says "command categories, with the exception of +@all, never include module commands." On Redis 8.10.3 that is no longer true, as the two results above show. An ACL written for Redis 7 that relied on it now grants or blocks more than before.
- **Functions replicate.** A library loaded on the primary appeared on the replica once the link was up. There `FCALL_RO stock` ran and returned `"5"`; `FCALL sell` was refused with `READONLY You can't write against a read only replica`.
- **FUNCTION DUMP moves libraries between servers.** A 189-byte dump from the primary restored into an unrelated server with both functions and their flags. A corrupt payload was refused: `DUMP payload version or checksum are wrong`.
- **ACL files.** `ACL SAVE` wrote the users with SHA-256 password hashes. A hand-added user under a `#` comment line loaded with `ACL LOAD`; comment lines are accepted since Redis 8.8. A line with an unknown command made `ACL LOAD` fail as a whole: "no change to the previously active ACL rules was performed".
- **ACL LOG says who was refused and why.** One wrong password, one denied command and one denied key produced three entries with reasons `auth`, `command` (`set`) and `key` (`secret:1`), all for `reporter`.
- **ACL users are not replicated.** `reporter`, created on the primary, did not exist on the replica: `ACL USERS` listed only `default`, and logging in as `reporter` failed with `WRONGPASS`, while the data itself had replicated. Each server needs the same users, through the same ACL file or the same `ACL SETUSER` commands. (redis-cli printed the auth error and then ran the command as the default user, which is why `x` still appears.)

### Not run / caveats

- Comment lines in the ACL file are stripped on load and not written back by `ACL SAVE` (ACL page); keep hand-written notes elsewhere.

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
./more.sh  # functions on a replica, FUNCTION DUMP/RESTORE, an ACL file, ACL LOG
./acl_replica.sh   # do ACL users created on a primary reach its replica?
```

출력은 영문 절과 같다(2026-11-07).

`more.sh`의 출력도 영문 절과 같다(2026-11-07).

`acl_replica.sh`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **Functions.** `sell`이 재고를 0으로 줄인 뒤 자체 오류 `sold out`으로 거절했다. `stock`은 `no-writes`로 등록돼 `FCALL_RO`로 돈다. `FCALL_RO sell`은 거절된다: `Can not execute a script with write flag using *_ro command`. 그래서 읽기 전용 함수를 복제본에서 돌릴 수 있다.
- **`%R~`와 `%W~`.** 사용자 `app`은 `GET catalog:1`은 되고 `SET`은 안 됐다. `XADD events:clicks`는 되고 `XRANGE`는 안 됐다. 권한은 명령마다의 키 명세를 따르므로, 규칙 묶음 하나로 한 키 공간의 독자이자 다른 키 공간의 작성자를 표현할 수 있다.
- **셀렉터.** 사용자 `rep`은 `report:*`를 읽는다. 셀렉터 `(~audit:* +xadd)`는 딱 하나, `audit:*`에 대한 `XADD`를 더한다. `XADD report:log`는 실패했다. 명령과 키를 함께 허락하는 규칙 묶음이 없기 때문이다.
- **`+@all -@write`는 모듈 쓰기도 막는다.** 사용자 `ro`는 `JSON.GET`은 되고 `JSON.SET`은 안 됐고, `TS.ADD`도 거절됐다. `+@read`만 가진 사용자도 `JSON.GET`을 실행했다. `ACL CAT write`에는 JSON, time series, Bloom, cuckoo, count-min, top-k, t-digest 명령 47개가 있고 `FT.*` 명령은 없다.
- **ACL 페이지는 다르게 말한다.** 여전히 "command categories, with the exception of +@all, never include module commands"라고 적혀 있다. 위 두 결과대로 Redis 8.10.3에서는 더 이상 사실이 아니다. 그 문장에 기대 Redis 7용으로 쓴 ACL은 이제 전보다 더 허락하거나 더 막는다.
- **함수는 복제된다.** 주 서버에 올린 라이브러리가 복제 연결이 맺어진 뒤 복제본에 나타났다. 거기서 `FCALL_RO stock`은 돌아 `"5"`를 돌려줬고, `FCALL sell`은 `READONLY You can't write against a read only replica`로 거절됐다.
- **FUNCTION DUMP로 서버 사이에 라이브러리를 옮긴다.** 주 서버의 189바이트 덤프가 상관없는 서버에 두 함수와 플래그까지 그대로 복원됐다. 깨진 페이로드는 거절됐다: `DUMP payload version or checksum are wrong`.
- **ACL 파일.** `ACL SAVE`는 사용자를 SHA-256 비밀번호 해시와 함께 썼다. `#` 주석 줄 아래 손으로 추가한 사용자는 `ACL LOAD`로 올라왔다. 주석 줄은 Redis 8.8부터 허용된다. 모르는 명령이 든 줄이 있으면 `ACL LOAD` 전체가 실패했다: "no change to the previously active ACL rules was performed".
- **ACL LOG는 누가 왜 거절됐는지 알려 준다.** 틀린 비밀번호, 거절된 명령, 거절된 키 한 번씩이 사유 `auth`, `command`(`set`), `key`(`secret:1`)인 항목 셋으로 남았다. 모두 `reporter`였다.
- **ACL 사용자는 복제되지 않는다.** 주 서버에서 만든 `reporter`는 복제본에 없었다. `ACL USERS`에는 `default`뿐이었고 `reporter` 로그인은 `WRONGPASS`로 실패했다. 데이터는 복제됐는데도 그렇다. 서버마다 같은 ACL 파일이나 같은 `ACL SETUSER` 명령으로 같은 사용자를 둬야 한다. (redis-cli는 인증 오류를 출력한 뒤 기본 사용자로 명령을 실행해서 `x`가 여전히 보인다.)

### 미실행 / 주의

- ACL 파일의 주석 줄은 읽을 때 지워지고 `ACL SAVE`로 다시 써지지 않는다(ACL 페이지). 손으로 쓴 메모는 다른 곳에 둔다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |
