#!/usr/bin/env bash
# One command per data type, each showing what the type is for. Runs against the
# local/01 container (nor-redis8) and prints every command with its reply.
# 자료형마다 용도를 보여 주는 명령 하나씩. local/01 컨테이너(nor-redis8)에서 실행하고
# 명령과 응답을 함께 출력한다.
set -euo pipefail
C=${REDIS_CONTAINER:-nor-redis8}
r() { echo "> $*"; docker exec "$C" redis-cli --no-raw "$@"; echo; }

r FLUSHALL
echo "== String — counters and cached values"
r SET page:home:views 41
r INCR page:home:views
echo "== Hash — one object, many fields; fields can expire on their own (7.4+)"
r HSET session:42 user kee cart 3
r HEXPIRE session:42 60 FIELDS 1 cart
r HTTL session:42 FIELDS 2 cart user
echo "== List — a queue"
r RPUSH jobs a b c
r LPOP jobs
echo "== Set — membership"
r SADD tags:post:1 redis cache db
r SISMEMBER tags:post:1 cache
echo "== Sorted set — a leaderboard"
r ZADD board 120 ann 95 bob 150 cy
r ZREVRANGE board 0 1 WITHSCORES
echo "== Stream — an append-only log with consumer groups"
r XADD orders '*' item book qty 1
r XGROUP CREATE orders shipping 0
r XREADGROUP GROUP shipping w1 COUNT 1 STREAMS orders '>'
echo "== Geo — nearby search"
r GEOADD shops 126.9780 37.5665 cityhall 127.0276 37.4979 gangnam
r GEOSEARCH shops FROMLONLAT 126.98 37.57 BYRADIUS 5 km ASC WITHDIST
echo "== Bitmap — one bit per user per day"
r SETBIT active:2026-11-07 1001 1
r BITCOUNT active:2026-11-07
echo "== HyperLogLog — approximate distinct count in 12 kB"
r PFADD visitors u1 u2 u3 u2
r PFCOUNT visitors
echo "== JSON — documents with path access"
r JSON.SET user:1 '$' '{"name":"Ann","langs":["ko","en"]}'
r JSON.ARRAPPEND user:1 '$.langs' '"th"'
r JSON.GET user:1 '$.langs'
echo "== Time series — samples with retention and downsampling"
r TS.CREATE temp:seoul RETENTION 86400000
r TS.ADD temp:seoul 1762473600000 11.5
r TS.ADD temp:seoul 1762477200000 12.0
r TS.RANGE temp:seoul - + AGGREGATION avg 7200000
echo "== Bloom filter — have we seen this before?"
r BF.ADD seen:urls https://redis.io
r BF.EXISTS seen:urls https://valkey.io
echo "== Count-min sketch, top-k — frequencies in fixed memory"
r TOPK.RESERVE hot 2
r TOPK.ADD hot a b a c a b
r TOPK.LIST hot
echo "== Array (8.8) — values by integer index, sparse"
r ARSET readings 0 10 11 12
r ARSET readings 1000 99
r ARLEN readings
r ARGET readings 1
r ARSCAN readings 0 2000
echo "== Vector set (beta) — similarity search on a native type"
r VADD emb VALUES 3 0.1 0.2 0.3 doc:a
r VADD emb VALUES 3 0.9 0.8 0.7 doc:b
r VSIM emb VALUES 3 0.1 0.2 0.25 COUNT 1 WITHSCORES
echo "== Search — secondary index and query over hashes"
r HSET item:1 name lamp price 30
r HSET item:2 name desk price 120
r FT.CREATE idx:items ON HASH PREFIX 1 item: SCHEMA name TEXT price NUMERIC
r FT.SEARCH idx:items '@price:[0 50]' RETURN 1 name
