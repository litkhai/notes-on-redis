#!/usr/bin/env bash
# RDB snapshot: fork time and copy-on-write, with and without writes during BGSAVE.
# RDB 스냅숏: BGSAVE 중 쓰기가 있을 때와 없을 때의 fork 시간과 copy-on-write.
set -euo pipefail
IMG=redis:8.10.3; C=nor-dd-rdb
docker rm -f $C >/dev/null 2>&1 || true
docker run -d --name $C $IMG redis-server --save "" --appendonly no >/dev/null; sleep 2
cli() { docker exec $C redis-cli "$@"; }
bench() { docker run --rm --network container:$C $IMG redis-benchmark "$@" >/dev/null 2>&1; }
echo "== load 2,000,000 keys of 100 bytes"
bench -t set -n 2000000 -r 2000000 -d 100 -c 50 -P 50 --threads 4
cli INFO memory | grep -E "^used_memory_human" ; cli DBSIZE
snap() {
  cli BGSAVE >/dev/null
  while [ "$(cli INFO persistence | tr -d '\r' | grep rdb_bgsave_in_progress | cut -d: -f2)" = 1 ]; do sleep 0.2; done
  cli INFO persistence | tr -d '\r' | grep -E "^(rdb_last_bgsave_status|rdb_last_bgsave_time_sec|rdb_last_cow_size|current_cow_peak)" || true
  cli INFO stats | tr -d '\r' | grep -E "^latest_fork_usec"
}
echo "== BGSAVE, no writes"
snap
echo "== BGSAVE while redis-benchmark overwrites random keys"
( bench -t set -n 3000000 -r 2000000 -d 100 -c 50 -P 20 --threads 4 ) &
sleep 1; snap; wait
docker rm -f $C >/dev/null
