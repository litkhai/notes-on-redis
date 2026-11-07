# Eviction and memory

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

`maxmemory 16mb` and three groups of 5,000 keys of 500 bytes: *read-hot* (read five times, never rewritten), *write-hot* (rewritten five times, never read) and *cold* (left alone). Then 30,000 new keys go in and the lab counts what survived under each policy. Then `HOTKEYS` (8.6) finds the keys that used the most CPU, and `INFO keysizes` shows the key size histogram. The eviction docs: "allkeys-lrm : Evict the least recently modified (LRM) keys", and "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently." On the sampling: "It samples a small number of keys at random and then evicts the ones with the longest time since last access."

Official documentation: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/).

### Run

```bash
python3 -m venv .venv && .venv/bin/pip install redis   # or reuse another lab's venv
../../cloud/01-free-database/.venv/bin/python lab.py   # starts and removes its own container
```

Output as it appeared (2026-11-07):

```text
== which keys survive (5,000 per group, then 30,000 new keys into 16 MB)
noeviction       survived read-hot  5000 write-hot  5000 cold  5000 new(first 5000)  5000 evicted      0 error: command not allowed when used memory > 'maxmemory'.
allkeys-lru      survived read-hot   621 write-hot   614 cold   356 new(first 5000)  4287 evicted  18321 
allkeys-lfu      survived read-hot  5000 write-hot  5000 cold  2117 new(first 5000)  1993 evicted  18249 
allkeys-lrm      survived read-hot   368 write-hot  3318 cold   431 new(first 5000)  3386 evicted  18307 
allkeys-random   survived read-hot  2595 write-hot  2568 cold  2636 new(first 5000)  2597 evicted  18303 

== HOTKEYS (8.6): top keys by CPU while reading a skewed set
   start: b'OK'
   get: [[b'tracking-active', 1, b'sample-ratio', 1, b'selected-slots', [[0, 16383]], b'all-commands-all-slots-us', 11435, b'net-bytes-all-commands-all-slots', 10619635, b'collection-start-time-unix-ms', 1794043633764, b'collection-duration-ms', 1840, b'total-cpu-time-user-ms', 69, b'total-cpu-time-sys-ms', 364, b'by-cpu-time-us', [b'k:7', 4684, b'k:42', 1712, b'k:395', 9, b'k:1073', 9, b'k:853', 9]]]

== INFO keysizes
   {'db0_distrib_strings_sizes': {'256': 2000, '64K': 1}, 'db0_distrib_lists_items': {'256': 1}}
```

### What was observed

- **noeviction** refuses the write once memory is full: `command not allowed when used memory > 'maxmemory'`. Reads keep working; nothing was evicted.
- **allkeys-lfu** kept every read-hot and write-hot key and evicted among cold and new keys. Frequency counts reads and writes alike.
- **allkeys-lrm** kept write-hot keys (3,318 of 5,000) and evicted read-hot ones (368 left) as readily as cold ones (431). Reading a key does not protect it; only a write does.
- **allkeys-lru** protects keys by last access, read or write. Read-hot and write-hot were touched in the same rounds, so it treated them alike. The newest keys survived best.
- **allkeys-random** left about half of every group.
- **HOTKEYS** tracked by CPU for 1.8 s and ranked `k:7` (half of all reads) first and `k:42` second, as the read pattern intended.
- **INFO keysizes** reports a power-of-two histogram per type: 2,000 strings in the 256-byte bucket, one in the 64K bucket, one list in the 256-item bucket.

### Not run / caveats

- LRU and LRM are sampled approximations, so their counts move between runs. An earlier run of the same script kept 3,251 read-hot and 3,214 write-hot keys under `allkeys-lru`; the LFU and LRM patterns held both times.
- `maxmemory-samples` was left at its default of 5.
- The volatile policies were not run: no key here has a TTL.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), 2026-11-07.**

`maxmemory 16mb`에 500바이트 키 5,000개짜리 그룹 셋을 넣는다. *read-hot*(다섯 번 읽고 다시 쓰지 않음), *write-hot*(다섯 번 다시 쓰고 읽지 않음), *cold*(손대지 않음). 그다음 새 키 30,000개를 넣고 정책별로 살아남은 키를 센다. 이어서 `HOTKEYS`(8.6)로 CPU를 가장 많이 쓴 키를 찾고, `INFO keysizes`로 키 크기 히스토그램을 본다. 축출 문서의 표현: "allkeys-lrm : Evict the least recently modified (LRM) keys", "Use allkeys-lrm when you want to preserve frequently read data but evict data that hasn't been modified recently." 샘플링에 대해서는 "It samples a small number of keys at random and then evicts the ones with the longest time since last access."

공식 문서: [Key eviction](https://redis.io/docs/latest/develop/reference/eviction/), [HOTKEYS](https://redis.io/docs/latest/commands/hotkeys/).

### 실행

```bash
python3 -m venv .venv && .venv/bin/pip install redis   # or reuse another lab's venv
../../cloud/01-free-database/.venv/bin/python lab.py   # starts and removes its own container
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **noeviction**은 메모리가 차면 쓰기를 거절한다: `command not allowed when used memory > 'maxmemory'`. 읽기는 계속 되고 축출된 키는 없다.
- **allkeys-lfu**는 read-hot과 write-hot을 모두 남기고 cold와 새 키 사이에서 축출했다. 빈도는 읽기와 쓰기를 똑같이 센다.
- **allkeys-lrm**은 write-hot을 남기고(5,000개 중 3,318개) read-hot을 cold만큼 쉽게 축출했다(368개 대 431개). 읽기는 키를 보호하지 않고 쓰기만 보호한다.
- **allkeys-lru**는 읽기든 쓰기든 마지막 접근으로 키를 보호한다. read-hot과 write-hot은 같은 라운드에서 접근했으므로 비슷하게 다뤘다. 가장 새 키가 가장 많이 살아남았다.
- **allkeys-random**은 그룹마다 절반 정도를 남겼다.
- **HOTKEYS**는 CPU 기준으로 1.8초 추적해 `k:7`(전체 읽기의 절반)을 1위, `k:42`를 2위로 꼽았다. 의도한 읽기 패턴 그대로다.
- **INFO keysizes**는 자료형별 2의 거듭제곱 히스토그램을 준다: 256바이트 구간에 문자열 2,000개, 64K 구간에 1개, 256개 항목 구간에 리스트 1개.

### 미실행 / 주의

- LRU와 LRM은 샘플링 근사라서 실행마다 수가 달라진다. 같은 스크립트의 이전 실행에서 `allkeys-lru`는 read-hot 3,251개, write-hot 3,214개를 남겼다. LFU와 LRM의 패턴은 두 번 모두 같았다.
- `maxmemory-samples`는 기본값 5 그대로 두었다.
- volatile 정책은 실행하지 않았다. 여기 키에는 TTL이 없다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), 2026-11-07 |
