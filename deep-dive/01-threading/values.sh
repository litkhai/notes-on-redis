#!/usr/bin/env bash
# io-threads 1, 4, 8 with 4 KB values instead of 64 bytes, no pipelining; same client placement as run.sh.
# 64바이트 대신 4 KB 값으로 io-threads 1, 4, 8.
set -euo pipefail
IMG=redis:8.10.3
for n in 1 4 8; do
  docker rm -f nor-dd-thr3 >/dev/null 2>&1 || true
  docker run -d --name nor-dd-thr3 $IMG redis-server --save "" --appendonly no --io-threads $n >/dev/null
  sleep 2
  echo "== io-threads $n, 4096-byte values"
  docker run --rm --network container:nor-dd-thr3 $IMG redis-benchmark -q -t set,get -n 1000000 -c 400 -P 1 -d 4096 -r 100000 --threads 12 2>&1 \
    | tr '\r' '\n' | grep -E "requests per second" | sed 's/^/   /'
done
docker rm -f nor-dd-thr3 >/dev/null
