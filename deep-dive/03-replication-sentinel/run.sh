#!/usr/bin/env bash
# Replication and Sentinel on the compose.yaml topology: partial vs full resync, WAIT with a
# paused replica, and a Sentinel failover timed from the primary's stop to a new master.
# compose.yaml 구성에서: 부분 대 전체 재동기화, 복제본을 멈춘 상태의 WAIT, 주 서버를 멈춘
# 순간부터 새 마스터까지의 Sentinel 장애 조치 시간.
set -euo pipefail
P=nor-repl-primary; R1=nor-repl-replica1; R2=nor-repl-replica2; S1=nor-repl-sentinel1
cli() { local c=$1; shift; docker exec "$c" redis-cli "$@"; }
syncs() { cli $P INFO stats | tr -d '\r' | grep -E "^(sync_full|sync_partial_ok|sync_partial_err)" | paste -sd' '; }
docker run --rm --network nor-repl_repl redis:8.10.3 redis-benchmark -h 10.231.77.10 -q -t set -n 200000 -r 100000 -d 100 >/dev/null 2>&1
echo "== after initial load: $(syncs)"
echo "== kill the replicas' connections on the primary (CLIENT KILL TYPE replica)"
cli $P CLIENT KILL TYPE replica; sleep 3
echo "   $(syncs)"
echo "== restart replica1 (no persistence, so it comes back empty)"
docker restart $R1 >/dev/null; sleep 4
echo "   $(syncs)"
echo "== WAIT with both replicas up"
# WAIT counts acknowledgements of this connection's own writes, so SET and WAIT share one
# redis-cli session; a WAIT on a fresh connection has nothing to wait for and returns at once.
w() { local t0 t1 out; t0=$(date +%s%N); out=$(printf 'SET %s x\nWAIT 2 1000\n' "$1" | docker exec -i $P redis-cli | tail -1); t1=$(date +%s%N); echo "WAIT 2 1000 -> $out after $(( (t1-t0)/1000000 )) ms"; }
echo "   $(w w1)"
echo "== WAIT with replica2 paused (docker pause)"
docker pause $R2 >/dev/null; sleep 1
echo "   primary sees: $(cli $P INFO replication | tr -d '\r' | grep -E '^slave[0-9]' | sed 's/,io-thread=0//' | paste -sd' ')"
echo "   $(w w2)"
echo "   same WAIT on a fresh connection -> $(cli $P WAIT 2 1000)"
docker unpause $R2 >/dev/null; sleep 2
echo "== Sentinel failover: stop the primary"
echo "   master before: $(cli $S1 -p 26379 SENTINEL get-master-addr-by-name mymaster | paste -sd:)"
t0=$(date +%s%N); docker stop $P >/dev/null
while true; do
  m=$(cli $S1 -p 26379 SENTINEL get-master-addr-by-name mymaster | head -1)
  [ "$m" != "10.231.77.10" ] && break; sleep 0.2
done; t1=$(date +%s%N)
echo "   new master: $m after $(( (t1-t0)/1000000 )) ms"
sleep 2
case $m in 10.231.77.11) newc=$R1;; 10.231.77.12) newc=$R2;; *) newc=$P;; esac
echo "   $m role: $(cli $newc INFO replication | tr -d '\r' | grep -E '^(role|connected_slaves)' | paste -sd' ')"
echo "   write to new master: $(cli $newc SET after-failover ok)"
echo "== start the old primary again: it rejoins as a replica"
t0=$(date +%s%N); docker start $P >/dev/null
for i in $(seq 1 60); do
  role=$(cli $P INFO replication 2>/dev/null | tr -d '\r' | grep -E '^role' || true)
  [ "$role" = "role:slave" ] && break; sleep 0.5
done; t1=$(date +%s%N)
echo "   after $(( (t1-t0)/1000000 )) ms: $(cli $P INFO replication | tr -d '\r' | grep -E '^(role|master_host|master_link_status)' | paste -sd' ')"
cli $S1 -p 26379 SENTINEL master mymaster | paste - - | grep -E "^(ip|num-slaves|failover-timeout)" | tr '\t' '=' | paste -sd' '
