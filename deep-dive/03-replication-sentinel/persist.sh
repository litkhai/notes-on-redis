#!/usr/bin/env bash
# Does a restarted replica resync partially or fully? A primary and a replica on their own network, each run
# five ways: without persistence; with AOF, restarted gracefully or killed; with RDB only, the same two.
# 재시작한 복제본은 부분 재동기화하나 전체 재동기화하나: 영속성 없음, AOF + 정상 재시작, AOF + SIGKILL.
set -uo pipefail
NET=nor-psync; P=nor-psync-p; R=nor-psync-r; IMG=redis:8.10.3
docker rm -f $P $R >/dev/null 2>&1; docker network rm $NET >/dev/null 2>&1; docker network create $NET >/dev/null
syncs() { docker exec $P redis-cli INFO stats | tr -d '\r' | grep -E "^sync_(full|partial_ok|partial_err):" | paste -sd' '; }
up_replica() { docker run -d --name $R --network $NET $IMG redis-server --replicaof $P 6379 "$@" >/dev/null;
  until docker exec $R redis-cli INFO replication 2>/dev/null | grep -q "master_link_status:up"; do sleep 0.3; done; }
docker run -d --name $P --network $NET $IMG redis-server --appendonly yes >/dev/null; sleep 1
for mode in "none" "aof-graceful" "aof-kill" "rdb-graceful" "rdb-kill"; do
  docker rm -f $R >/dev/null 2>&1
  case $mode in
    none) up_replica --save "" --appendonly no ;;
    aof-*) up_replica --appendonly yes ;;
    rdb-*) up_replica --appendonly no --save "3600 1" ;;
  esac
  docker run --rm --network $NET $IMG redis-benchmark -h $P -q -t set -n 100000 -r 50000 -d 100 >/dev/null 2>&1; sleep 1
  b=$(syncs)
  case $mode in
    none|*-graceful) docker restart $R >/dev/null ;;
    *-kill) docker kill $R >/dev/null; docker start $R >/dev/null ;;
  esac
  docker exec $P redis-cli SET during-restart x >/dev/null
  until docker exec $R redis-cli INFO replication 2>/dev/null | grep -q "master_link_status:up"; do sleep 0.3; done
  echo "== replica $mode"
  echo "   primary before: $b"
  echo "   primary after:  $(syncs)"
  echo "   replica log:    $(docker logs $R 2>&1 | grep -E "Partial resynchronization|Full resync|MASTER <-> REPLICA sync started|Successful partial|PSYNC" | tail -3 | sed -E 's/^[0-9]+:[A-Z] [0-9]{2} [A-Za-z]{3} [0-9]{4} [0-9:.]+ //' | paste -sd'|')"
done
docker rm -f $P $R >/dev/null; docker network rm $NET >/dev/null
