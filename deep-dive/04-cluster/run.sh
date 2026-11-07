#!/usr/bin/env bash
# Cluster on the compose.yaml nodes: create (3 primaries + 3 replicas), hash slots and hash
# tags, -MOVED, CROSSSLOT, and an atomic slot migration (CLUSTER MIGRATION, 8.4) under write load.
# compose.yaml 노드로 클러스터 생성(주 3 + 복제 3), 해시 슬롯과 해시 태그, -MOVED, CROSSSLOT,
# 쓰기 부하 중의 원자적 슬롯 이전(CLUSTER MIGRATION, 8.4).
set -euo pipefail
N1=nor-cl-node1; IMG=redis:8.10.3; NET=nor-cluster_cl
c1() { docker exec $N1 redis-cli "$@"; }
if [ "$(c1 CLUSTER INFO | tr -d '\r' | grep cluster_known_nodes | cut -d: -f2)" != 6 ]; then
  docker exec $N1 sh -c 'yes yes | redis-cli --cluster create 10.231.78.11:6379 10.231.78.12:6379 10.231.78.13:6379 10.231.78.14:6379 10.231.78.15:6379 10.231.78.16:6379 --cluster-replicas 1' >/dev/null
fi
until [ "$(c1 CLUSTER INFO | tr -d '\r' | grep cluster_state | cut -d: -f2)" = ok ]; do sleep 1; done
echo "== cluster: $(c1 CLUSTER INFO | tr -d '\r' | grep -E '^(cluster_state|cluster_size|cluster_known_nodes)' | paste -sd' ')"
echo "== slot owners"
docker exec $N1 redis-cli --cluster check 10.231.78.11:6379 2>/dev/null | grep -E "^10\." | head -3
echo "== CLUSTER KEYSLOT (CRC16 mod 16384)"
for k in user:1 user:2 '{user:1}:cart' '{user:1}:orders'; do echo "   $k -> $(c1 CLUSTER KEYSLOT "$k")"; done
echo "== a key whose slot is on another node, without and with -c"
echo "   node1 GET user:2 -> $(c1 GET user:2 2>&1)"
echo "   node1 -c SET user:2 v -> $(docker exec $N1 redis-cli -c SET user:2 v)"
echo "== multi-key commands"
echo "   MSET user:1 a user:2 b -> $(docker exec $N1 redis-cli -c MSET user:1 a user:2 b 2>&1)"
echo "   MSET {user:1}:cart a {user:1}:orders b -> $(docker exec $N1 redis-cli -c MSET '{user:1}:cart' a '{user:1}:orders' b)"
echo "== atomic slot migration: slots 0-999 from node1 to node2 while redis-benchmark writes"
docker run --rm --network $NET $IMG redis-benchmark -h 10.231.78.11 --cluster -q -t set -n 300000 -r 100000 -d 100 -c 50 >/dev/null 2>&1
echo "   keys in slot 0 on node1 before: $(c1 CLUSTER COUNTKEYSINSLOT 0); node1 dbsize $(c1 DBSIZE)"
( docker run --rm --network $NET $IMG redis-benchmark -h 10.231.78.11 --cluster -t set -n 600000 -r 100000 -d 100 -c 50 2>&1 \
    | tr '\r' '\n' | grep -E "throughput summary|errors|ERR|MOVED|ASK" | tail -3 > /tmp/nor-bench.out ) &
sleep 1
t0=$(date +%s%N)
echo "   node2> CLUSTER MIGRATION IMPORT 0 999 -> $(docker exec nor-cl-node2 redis-cli CLUSTER MIGRATION IMPORT 0 999)"
for i in $(seq 1 120); do
  st=$(docker exec nor-cl-node2 redis-cli CLUSTER MIGRATION STATUS ALL | tr '\n' ' ')
  echo "$st" | grep -q -i -E "completed|done|success|finished" && break
  sleep 0.5
done; t1=$(date +%s%N)
echo "   status: $(echo "$st" | cut -c1-400)"
echo "   took about $(( (t1-t0)/1000000 )) ms"
wait
echo "   benchmark during migration: $(paste -sd' ' /tmp/nor-bench.out)"
echo "   keys in slot 0 now on node2: $(docker exec nor-cl-node2 redis-cli CLUSTER COUNTKEYSINSLOT 0), on node1: $(c1 CLUSTER COUNTKEYSINSLOT 0)"
docker exec $N1 redis-cli --cluster check 10.231.78.11:6379 2>/dev/null | grep -E "^10\.|\[OK\] .* keys|ERR" | head -4
