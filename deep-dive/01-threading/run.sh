#!/usr/bin/env bash
# io-threads 1, 2, 4, 8 under the same redis-benchmark load; the client runs in the server's
# network namespace so Docker's port forwarding is not in the path. Prints INFO threads too.
# 같은 redis-benchmark 부하로 io-threads 1, 2, 4, 8을 잰다. 클라이언트는 서버의 네트워크
# 네임스페이스에서 돌려 Docker 포트 포워딩을 거치지 않는다. INFO threads도 출력한다.
set -euo pipefail
IMG=redis:8.10.3
for n in 1 2 4 8; do
  docker rm -f nor-dd-thr >/dev/null 2>&1 || true
  docker run -d --name nor-dd-thr $IMG redis-server --save "" --appendonly no --io-threads $n >/dev/null
  sleep 2
  echo "== io-threads $n"
  docker exec nor-dd-thr redis-cli INFO server | grep -E "^io_threads_active"
  for r in 1 2; do
    docker run --rm --network container:nor-dd-thr $IMG \
      redis-benchmark -q -t set,get -n 3000000 -c 400 -P 1 -d 64 --threads 12 2>&1 | tr '\r' '\n' | grep -E "requests per second"
  done
  echo "-- INFO threads (after load)"
  docker exec nor-dd-thr redis-cli INFO threads | grep -v "^#" | tr -d '\r' | head -12
done
docker rm -f nor-dd-thr >/dev/null
