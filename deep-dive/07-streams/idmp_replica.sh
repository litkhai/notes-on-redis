#!/usr/bin/env bash
# IDMP across a primary and its replica: is the idempotency map replicated, and does a producer's retry
# after a failover still deduplicate? The primary is killed and the replica promoted by hand (REPLICAOF NO ONE).
# IDMP 맵이 복제되는지, 장애 조치 뒤 생산자 재시도도 중복을 거르는지.
set -uo pipefail
NET=nor-idmp; P=nor-idmp-p; R=nor-idmp-r; IMG=redis:8.10.3
docker rm -f $P $R >/dev/null 2>&1; docker network rm $NET >/dev/null 2>&1; docker network create $NET >/dev/null
docker run -d --name $P --network $NET $IMG >/dev/null
docker run -d --name $R --network $NET $IMG redis-server --replicaof $P 6379 >/dev/null
until docker exec $R redis-cli INFO replication | grep -q "master_link_status:up"; do sleep 0.3; done
r() { local c=$1; shift; echo "[$c]> $*"; docker exec $c redis-cli --no-raw "$@" 2>&1; echo; }
r $P XADD pay IDMP svc-a req-1 '*' amount 100
r $P XADD pay IDMP svc-a req-1 '*' amount 100
sleep 0.5
echo "== on the replica"
r $R XLEN pay
echo "[$R]> XINFO STREAM pay (idmp fields)"; docker exec $R redis-cli XINFO STREAM pay | paste - - | grep -i idmp; echo
echo "== the primary dies; the replica is promoted; the producer retries req-1, then sends req-2"
docker kill $P >/dev/null
r $R REPLICAOF NO ONE
r $R XADD pay IDMP svc-a req-1 '*' amount 100
r $R XADD pay IDMP svc-a req-2 '*' amount 50
r $R XLEN pay
docker rm -f $P $R >/dev/null; docker network rm $NET >/dev/null
