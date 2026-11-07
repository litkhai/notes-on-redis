#!/usr/bin/env bash
# Do ACL users created on a primary reach its replica?  주 서버에서 만든 ACL 사용자가 복제본에 전달되나?
set -uo pipefail
NET=nor-aclr; P=nor-aclr-p; R=nor-aclr-r; IMG=redis:8.10.3
docker rm -f $P $R >/dev/null 2>&1; docker network rm $NET >/dev/null 2>&1; docker network create $NET >/dev/null
docker run -d --name $P --network $NET $IMG >/dev/null
docker run -d --name $R --network $NET $IMG redis-server --replicaof $P 6379 >/dev/null
until docker exec $R redis-cli INFO replication | grep -q "master_link_status:up"; do sleep 0.3; done
r() { local c=$1; shift; echo "[$c]> $*"; docker exec $c redis-cli --no-raw "$@" 2>&1; echo; }
r $P ACL SETUSER reporter on '>pw' '~report:*' '+@read'
r $P SET report:1 x
sleep 0.5
r $R ACL USERS
r $R GET report:1
echo "[$R]> GET report:1 as reporter"; docker exec $R redis-cli --user reporter --pass pw --no-auth-warning GET report:1 2>&1; echo
docker rm -f $P $R >/dev/null; docker network rm $NET >/dev/null
