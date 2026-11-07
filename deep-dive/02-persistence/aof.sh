#!/usr/bin/env bash
# AOF: write latency with appendfsync everysec vs always, then the multi-part AOF files
# before and after BGREWRITEAOF. The data directory is the container's (overlay on the host disk).
# AOF: appendfsync everysec 대 always의 쓰기 지연, 그다음 BGREWRITEAOF 전후의 다중 파트 AOF 파일.
set -euo pipefail
IMG=redis:8.10.3; C=nor-dd-aof
docker rm -f $C >/dev/null 2>&1 || true
docker run -d --name $C $IMG redis-server --save "" --appendonly yes --appendfsync everysec >/dev/null; sleep 2
cli() { docker exec $C redis-cli "$@"; }
lat() { docker run --rm --network container:$C $IMG redis-benchmark -t set -n 100000 -r 100000 -d 100 -c 20 -P 1 2>&1 | tr '\r' '\n' \
        | grep -E "throughput summary|latency summary|avg +min|^ +[0-9.]+ +[0-9.]+ +" | head -4; }
for mode in everysec always; do
  cli CONFIG SET appendfsync $mode >/dev/null
  echo "== appendfsync $(cli CONFIG GET appendfsync | tail -1)"
  lat
done
cli CONFIG SET appendfsync everysec >/dev/null
echo "== appendonlydir before BGREWRITEAOF"
docker exec $C sh -c 'ls -l /data/appendonlydir | tail -n +2; echo "-- manifest"; cat /data/appendonlydir/*.manifest'
cli BGREWRITEAOF >/dev/null; sleep 3
echo "== appendonlydir after BGREWRITEAOF"
docker exec $C sh -c 'ls -l /data/appendonlydir | tail -n +2; echo "-- manifest"; cat /data/appendonlydir/*.manifest'
cli INFO persistence | tr -d '\r' | grep -E "^(aof_enabled|aof_rewrites|aof_last_bgrewrite_status|aof_base_size|aof_current_size)"
