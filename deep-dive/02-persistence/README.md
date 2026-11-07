# Persistence

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

Three experiments on how Redis puts data on disk: an RDB snapshot's fork and copy-on-write with and without writes during it, AOF write latency with `appendfsync everysec` and `always` plus the multi-part AOF files, and the 8.10 `BACKUP` command restored into a new server with `preload-file`. The official docs put it this way: "With the default policy of fsync every second, write performance is still great", and "A backup reuses the multi-part AOF format".

Official documentation: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/).

### Run

```bash
./rdb_cow.sh   # 2M SETs, BGSAVE idle, BGSAVE during overwrites
./aof.sh       # everysec vs always, appendonlydir before/after BGREWRITEAOF
./backup.sh    # BACKUP START/SEAL/LIST, restore with --preload-file aof:<manifest>
```

Output as it appeared (2026-11-07):

```text
$ ./rdb_cow.sh
== load 2,000,000 keys of 100 bytes
used_memory_human:213.81M
1264354
== BGSAVE, no writes
current_cow_peak:0
rdb_last_bgsave_status:ok
rdb_last_bgsave_time_sec:1
rdb_last_cow_size:2183168
latest_fork_usec:4776
== BGSAVE while redis-benchmark overwrites random keys
current_cow_peak:0
rdb_last_bgsave_status:ok
rdb_last_bgsave_time_sec:1
rdb_last_cow_size:252112896
latest_fork_usec:4217

$ ./aof.sh
== appendfsync everysec
  throughput summary: 97087.38 requests per second
  latency summary (msec):
          avg       min       p50       p95       p99       max
        0.123     0.056     0.119     0.183     0.255     1.543
== appendfsync always
  throughput summary: 17202.82 requests per second
  latency summary (msec):
          avg       min       p50       p95       p99       max
        1.115     0.544     1.159     1.367     1.527     6.863
== appendonlydir before BGREWRITEAOF
-rw------- 1 redis redis       89 Nov  7 07:41 appendonly.aof.1.base.rdb
-rw------- 1 redis redis 28800023 Nov  7 07:41 appendonly.aof.1.incr.aof
-rw------- 1 redis redis      102 Nov  7 07:41 appendonly.aof.manifest
-- manifest
file appendonly.aof.1.base.rdb seq 1 type b
file appendonly.aof.1.incr.aof seq 1 type i startoffset 0
== appendonlydir after BGREWRITEAOF
-rw------- 1 redis redis 10388378 Nov  7 07:41 appendonly.aof.2.base.rdb
-rw------- 1 redis redis        0 Nov  7 07:41 appendonly.aof.2.incr.aof
-rw------- 1 redis redis      107 Nov  7 07:41 appendonly.aof.manifest
-- manifest
file appendonly.aof.2.base.rdb seq 2 type b
file appendonly.aof.2.incr.aof seq 2 type i startoffset 200000
aof_enabled:1
aof_last_bgrewrite_status:ok
aof_rewrites:1
aof_rewrites_consecutive_failures:0
aof_current_size:10388378
aof_base_size:10388378

$ ./backup.sh
> BACKUP START
OK
> BACKUP SEAL
OK
> BACKUP STATUS
state sealed error  start_time 1794037370 end_time 1794037371
> BACKUP LIST
/data/backupdir/appendonly.aof.2.base.rdb
/data/backupdir/appendonly.aof.2.incr.aof
/data/backupdir/appendonly.aof.manifest
> link counts in backupdir (2 = shared with appendonlydir)
2 /data/backupdir/appendonly.aof.2.base.rdb
2 /data/backupdir/appendonly.aof.2.incr.aof
1 /data/backupdir/appendonly.aof.manifest
> source keys: after-seal before-backup during-backup
Module 'bf' loaded from /usr/local/lib/redis/modules//redisbloom.so
Module 'search' loaded from /usr/local/lib/redis/modules//redisearch.so
Module 'timeseries' loaded from /usr/local/lib/redis/modules//redistimeseries.so
Module 'ReJSON' loaded from /usr/local/lib/redis/modules//rejson.so
DB loaded from base file appendonly.aof.2.base.rdb: 0.000 seconds
DB loaded from incr file appendonly.aof.2.incr.aof: 0.000 seconds
DB pre-loaded from append only file: /restore/appendonly.aof.manifest: 0.000 seconds
> restored keys: before-backup during-backup
```

### What was observed

- **Fork and copy-on-write.** With 214 MB in memory the fork took 4–5 ms. Copy-on-write was 2.2 MB when nothing wrote during the snapshot and 252 MB when `redis-benchmark` overwrote keys during it, more than the dataset: plan memory headroom for snapshots on write-heavy instances.
- **fsync policy.** `everysec`: 97,087 requests/s, p50 0.119 ms, p99 0.255 ms. `always`: 17,203 requests/s, p50 1.159 ms, p99 1.527 ms, on this host's disk.
- **Multi-part AOF.** `appendonlydir` holds a base RDB, an incremental AOF and a manifest; after `BGREWRITEAOF` the base became 10 MB, the incremental file empty, and the manifest moved to sequence 2.
- **BACKUP (8.10).** `START` and `SEAL` pin the current base, incremental file and a manifest under `backupdir` as hard links (link count 2). A key written after `SEAL` is not in the backup. A new server started with `--preload-file aof:/restore/appendonly.aof.manifest` loaded both pre-seal keys. The argument must be `aof:` or `rdb:` plus a file name; a bare path is rejected with "argument must be in the format '[aof|rdb]:[filename]'".

### Not run / caveats

- The disk is the container's overlay on one host; another disk will give other fsync numbers.
- `redis-benchmark -r` picks random keys, so 2M SETs left 1,264,354 distinct keys.
- Restoring a backup by copying files was done by hand here; operational tooling around `BACKUP` was not looked at.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

Redis가 데이터를 디스크에 두는 방식을 세 실험으로 본다. RDB 스냅숏의 fork와 copy-on-write(그동안 쓰기가 있을 때와 없을 때), `appendfsync everysec`와 `always`의 AOF 쓰기 지연과 다중 파트 AOF 파일, 그리고 8.10의 `BACKUP`을 `preload-file`로 새 서버에 복원하기. 공식 문서의 표현: "With the default policy of fsync every second, write performance is still great", "A backup reuses the multi-part AOF format".

공식 문서: [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [BACKUP](https://redis.io/docs/latest/commands/backup/).

### 실행

```bash
./rdb_cow.sh   # 2M SETs, BGSAVE idle, BGSAVE during overwrites
./aof.sh       # everysec vs always, appendonlydir before/after BGREWRITEAOF
./backup.sh    # BACKUP START/SEAL/LIST, restore with --preload-file aof:<manifest>
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **fork와 copy-on-write.** 메모리 214 MB에서 fork는 4–5 ms였다. 스냅숏 중 쓰기가 없으면 copy-on-write가 2.2 MB, `redis-benchmark`가 키를 덮어쓰면 252 MB로 데이터보다 컸다. 쓰기가 많은 인스턴스는 스냅숏용 메모리 여유를 잡아야 한다.
- **fsync 정책.** `everysec`: 초당 97,087, p50 0.119 ms, p99 0.255 ms. `always`: 초당 17,203, p50 1.159 ms, p99 1.527 ms(이 호스트의 디스크).
- **다중 파트 AOF.** `appendonlydir`에는 base RDB, 증분 AOF, manifest가 있다. `BGREWRITEAOF` 뒤 base는 10 MB, 증분 파일은 비었고, manifest는 2번으로 넘어갔다.
- **BACKUP(8.10).** `START`와 `SEAL`은 현재 base, 증분 파일, manifest를 `backupdir`에 하드 링크로 고정한다(링크 수 2). `SEAL` 뒤에 쓴 키는 백업에 없다. `--preload-file aof:/restore/appendonly.aof.manifest`로 띄운 새 서버는 봉인 전 키 둘을 실었다. 인자는 `aof:`나 `rdb:`에 파일 이름을 붙여야 한다. 경로만 주면 "argument must be in the format '[aof|rdb]:[filename]'"로 거절된다.

### 미실행 / 주의

- 디스크는 호스트 하나의 컨테이너 overlay다. 다른 디스크는 다른 fsync 수치를 낸다.
- `redis-benchmark -r`은 임의 키를 고르므로 SET 200만 번에 고유 키는 1,264,354개였다.
- 백업 복원은 파일을 손으로 복사해서 했다. `BACKUP` 주변 운영 도구는 보지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |
