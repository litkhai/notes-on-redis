# Data types tour

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (Docker `redis:8.10.3`), 2026-11-07.**

One command per data type, each showing what the type is for: String, Hash (with per-field expiry), List, Set, Sorted set, Stream, Geo, Bitmap, HyperLogLog, JSON, Time series, Bloom filter, Top-k, Array, Vector set, Search. Everything runs in the
stock image with no configuration, because the image loads its modules at start
(see [`local/01`](../01-redis-8-docker)).

### Run

```bash
(cd ../../setup && docker compose up -d redis)
./tour.sh            # flushes the container first, then prints each command and its reply
./probabilistic.sh   # count-min sketch, cuckoo filter, t-digest; its own container
```

Output as it appeared (2026-11-07):

```text
> FLUSHALL
OK

== String — counters and cached values
> SET page:home:views 41
OK

> INCR page:home:views
(integer) 42

== Hash — one object, many fields; fields can expire on their own (7.4+)
> HSET session:42 user kee cart 3
(integer) 2

> HEXPIRE session:42 60 FIELDS 1 cart
1) (integer) 1

> HTTL session:42 FIELDS 2 cart user
1) (integer) 60
2) (integer) -1

== List — a queue
> RPUSH jobs a b c
(integer) 3

> LPOP jobs
"a"

== Set — membership
> SADD tags:post:1 redis cache db
(integer) 3

> SISMEMBER tags:post:1 cache
(integer) 1

== Sorted set — a leaderboard
> ZADD board 120 ann 95 bob 150 cy
(integer) 3

> ZREVRANGE board 0 1 WITHSCORES
1) "cy"
2) "150"
3) "ann"
4) "120"

== Stream — an append-only log with consumer groups
> XADD orders * item book qty 1
"1794034471246-0"

> XGROUP CREATE orders shipping 0
OK

> XREADGROUP GROUP shipping w1 COUNT 1 STREAMS orders >
1) 1) "orders"
   2) 1) 1) "1794034471246-0"
         2) 1) "item"
            2) "book"
            3) "qty"
            4) "1"

== Geo — nearby search
> GEOADD shops 126.9780 37.5665 cityhall 127.0276 37.4979 gangnam
(integer) 2

> GEOSEARCH shops FROMLONLAT 126.98 37.57 BYRADIUS 5 km ASC WITHDIST
1) 1) "cityhall"
   2) "0.4274"

== Bitmap — one bit per user per day
> SETBIT active:2026-11-07 1001 1
(integer) 0

> BITCOUNT active:2026-11-07
(integer) 1

== HyperLogLog — approximate distinct count in 12 kB
> PFADD visitors u1 u2 u3 u2
(integer) 1

> PFCOUNT visitors
(integer) 3

== JSON — documents with path access
> JSON.SET user:1 $ {"name":"Ann","langs":["ko","en"]}
OK

> JSON.ARRAPPEND user:1 $.langs "th"
1) (integer) 3

> JSON.GET user:1 $.langs
"[[\"ko\",\"en\",\"th\"]]"

== Time series — samples with retention and downsampling
> TS.CREATE temp:seoul RETENTION 86400000
OK

> TS.ADD temp:seoul 1762473600000 11.5
(integer) 1762473600000

> TS.ADD temp:seoul 1762477200000 12.0
(integer) 1762477200000

> TS.RANGE temp:seoul - + AGGREGATION avg 7200000
1) 1) (integer) 1762473600000
   2) 11.75

== Bloom filter — have we seen this before?
> BF.ADD seen:urls https://redis.io
(integer) 1

> BF.EXISTS seen:urls https://valkey.io
(integer) 0

== Count-min sketch, top-k — frequencies in fixed memory
> TOPK.RESERVE hot 2
OK

> TOPK.ADD hot a b a c a b
1) (nil)
2) (nil)
3) (nil)
4) "b"
5) (nil)
6) "c"

> TOPK.LIST hot
1) "a"
2) "b"

== Array (8.8) — values by integer index, sparse
> ARSET readings 0 10 11 12
(integer) 3

> ARSET readings 1000 99
(integer) 1

> ARLEN readings
(integer) 1001

> ARGET readings 1
"11"

> ARSCAN readings 0 2000
1) 1) (integer) 0
   2) "10"
2) 1) (integer) 1
   2) "11"
3) 1) (integer) 2
   2) "12"
4) 1) (integer) 1000
   2) "99"

== Vector set (beta) — similarity search on a native type
> VADD emb VALUES 3 0.1 0.2 0.3 doc:a
(integer) 1

> VADD emb VALUES 3 0.9 0.8 0.7 doc:b
(integer) 1

> VSIM emb VALUES 3 0.1 0.2 0.25 COUNT 1 WITHSCORES
1) "doc:a"
2) "0.9991111159324646"

== Search — secondary index and query over hashes
> HSET item:1 name lamp price 30
(integer) 2

> HSET item:2 name desk price 120
(integer) 2

> FT.CREATE idx:items ON HASH PREFIX 1 item: SCHEMA name TEXT price NUMERIC
OK

> FT.SEARCH idx:items @price:[0 50] RETURN 1 name
1) (integer) 1
2) "item:1"
3) 1) "name"
   2) "lamp"
```

`probabilistic.sh` output as it appeared (2026-11-07):

```text
== count-min sketch: 100,000 page views over 1,000 pages, page:1 is hot
> CMS.INITBYPROB views 0.001 0.01
OK

exact counts: page:1 10000, page:2 91, page:999 99, page:5000 0
> CMS.QUERY views page:1 page:2 page:999 page:5000
1) (integer) 10000
2) (integer) 91
3) (integer) 99
4) (integer) 0

> CMS.INFO views
1) width
2) (integer) 2000
3) depth
4) (integer) 7
5) count
6) (integer) 100000

== cuckoo filter: like Bloom, but an item can be deleted
> CF.RESERVE users 100000
OK

> CF.EXISTS users user:42
(integer) 1

> CF.DEL users user:42
(integer) 1

> CF.EXISTS users user:42
(integer) 0

   false positives among 10,000 users never added:
69
> CF.INFO users
 1) Size
 2) (integer) 131128
 3) Number of buckets
 4) (integer) 65536
 5) Number of filters
 6) (integer) 1
 7) Number of items inserted
 8) (integer) 49999
 9) Number of items deleted
10) (integer) 1
11) Bucket size
12) (integer) 2
13) Expansion rate
14) (integer) 1
15) Max iterations
16) (integer) 20

== t-digest: 100,000 latencies, mostly 1-20 ms with a slow tail
> TDIGEST.CREATE lat COMPRESSION 100
OK

exact p50 10.58 p99 256.59 p99.9 1832.39
> TDIGEST.QUANTILE lat 0.5 0.99 0.999
1) "10.510366111018635"
2) "325.1077325508102"
3) "1831.3768790853658"

> TDIGEST.CDF lat 20 200
1) "0.9819669508388275"
2) "0.9891392540197896"

== memory per structure
   views: 56056 bytes
   users: 131152 bytes
   lat: 9864 bytes
```

### What was observed

- Every command returned without an error on the stock image, including the module types (JSON,
  Time series, Bloom, Top-k, Search) and the two newest native types: **Array** (since 8.8.0, per
  `COMMAND DOCS`) and **vector sets** (beta).
- `ARLEN` reports max index + 1 (1001 after writing indexes 0–2 and 1000) while `ARSCAN`
  returns only the four indexes that exist: arrays are sparse.
- Per-field expiry on a hash (`HEXPIRE`) leaves the other fields alone: `HTTL` shows 60 for
  `cart` and -1 for `user`.
- Redis Insight lists these keys with their own type labels (ARRAY, VECTOR SET, TOPK-TYPE); see
  the Setup page.
- **Count-min sketch counts without storing keys.** 100,000 page views over 1,000 pages went into a 2,000 × 7 sketch (`CMS.INITBYPROB views 0.001 0.01`) of 56 KB. Its counts for `page:1`, `page:2`, `page:999` and a page never seen matched the exact counts (10,000, 91, 99, 0). The sketch can only overestimate, never underestimate.
- **Cuckoo filter can forget.** After 50,000 users, `CF.DEL` removed `user:42` and `CF.EXISTS` turned 0, which a Bloom filter cannot do. 69 of 10,000 users never added were reported present: a 0.69% false-positive rate, in 131 KB.
- **t-digest estimates percentiles in 10 KB.** For 100,000 latencies with a slow 1% tail, the median (10.51 vs exact 10.58) and p99.9 (1,831 vs 1,832) were close, but p99 was 325 against an exact 257: it falls where the data jumps from 20 ms to 200 ms and few points sit, which is where a digest is least precise.

### Not run / caveats

- One command per type is a tour, not a reference; the Search and vector material has its own lab (`local/03`).

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3, Docker image `redis:8.10.3`, 2026-11-07 |

## 한국어

**확인: Redis 8.10.3(Docker `redis:8.10.3`), 2026-11-07.**

자료형마다 용도를 보여 주는 명령 하나씩: String, Hash(필드별 만료), List, Set, Sorted set, Stream,
Geo, Bitmap, HyperLogLog, JSON, Time series, Bloom filter, Top-k, Array, Vector set, Search.
이미지가 시작할 때 모듈을 싣기 때문에 기본 이미지에서 설정 없이 모두 돈다
([`local/01`](../01-redis-8-docker) 참고).

### 실행

```bash
(cd ../../setup && docker compose up -d redis)
./tour.sh            # 먼저 컨테이너를 비우고, 명령과 응답을 차례로 출력한다
```

출력은 영문 절과 같다(2026-11-07).

`probabilistic.sh`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- 기본 이미지에서 모든 명령이 오류 없이 응답했다. 모듈 자료형(JSON, Time series, Bloom, Top-k,
  Search)과 가장 새로운 내장 자료형 둘, **Array**(`COMMAND DOCS` 기준 8.8.0부터)와 **벡터 셋**(베타) 포함.
- `ARLEN`은 최대 인덱스 + 1을 돌려준다(인덱스 0–2와 1000을 쓴 뒤 1001). `ARSCAN`은 실제로 있는
  인덱스 네 개만 돌려준다. 배열은 희소하다.
- 해시의 필드별 만료(`HEXPIRE`)는 다른 필드에 영향을 주지 않는다. `HTTL`이 `cart`는 60, `user`는 -1.
- Redis Insight는 이 키들을 각자의 유형(ARRAY, VECTOR SET, TOPK-TYPE)으로 보여 준다. Setup 페이지 참고.
- **Count-min sketch는 키를 저장하지 않고 센다.** 페이지 1,000개에 걸친 조회 100,000건을 56 KB짜리 2,000 × 7 스케치(`CMS.INITBYPROB views 0.001 0.01`)에 넣었다. `page:1`, `page:2`, `page:999`, 본 적 없는 페이지의 값이 정확한 횟수(10,000, 91, 99, 0)와 같았다. 이 스케치는 실제보다 크게 셀 수는 있어도 작게 세지는 않는다.
- **Cuckoo filter는 지울 수 있다.** 사용자 50,000명을 넣은 뒤 `CF.DEL`로 `user:42`를 지우자 `CF.EXISTS`가 0이 됐다. Bloom filter로는 못 하는 일이다. 넣지 않은 사용자 10,000명 중 69명을 있다고 답했다. 131 KB에서 오탐률 0.69%.
- **t-digest는 10 KB로 백분위를 추정한다.** 느린 꼬리 1%가 있는 지연 100,000건에서 중앙값(10.51 대 실제 10.58)과 p99.9(1,831 대 1,832)는 가까웠지만, p99는 실제 257에 325였다. 데이터가 20 ms에서 200 ms로 건너뛰어 점이 거의 없는 구간이라, digest가 가장 부정확한 곳이다.

### 미실행 / 주의

- 자료형마다 명령 하나는 둘러보기일 뿐 레퍼런스가 아니다. Search와 벡터는 별도 실습(`local/03`)이 있다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3, Docker 이미지 `redis:8.10.3`, 2026-11-07 |
