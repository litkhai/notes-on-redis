#!/usr/bin/env bash
# Functions and ACL, the remaining parts on Redis 8.10.3: a library replicated to a replica and called
# there; FUNCTION DUMP into another server; an ACL file with ACL SAVE / ACL LOAD (comments allowed
# since 8.8); ACL LOG after a bad password and a denied command.
# 복제본에서의 함수, 다른 서버로 FUNCTION DUMP/RESTORE, ACL 파일과 ACL SAVE/LOAD, ACL LOG.
set -uo pipefail
NET=nor-dd-fa2; P=nor-dd-fa-p; R=nor-dd-fa-r; X=nor-dd-fa-x
docker rm -f $P $R $X >/dev/null 2>&1; docker network rm $NET >/dev/null 2>&1
docker network create $NET >/dev/null
docker run -d --name $P --network $NET redis:8.10.3 sh -c 'touch /data/users.acl && exec redis-server --aclfile /data/users.acl' >/dev/null
docker run -d --name $R --network $NET redis:8.10.3 redis-server --replicaof $P 6379 >/dev/null
docker run -d --name $X --network $NET redis:8.10.3 >/dev/null
until docker exec $R redis-cli INFO replication | grep -q "master_link_status:up"; do sleep 0.5; done
echo "replica link: $(docker exec $R redis-cli INFO replication | tr -d '\r' | grep -E '^(role|master_link_status)' | paste -sd' ')"
r() { local c=$1; shift; echo "[$c]> $*"; docker exec $c redis-cli --no-raw "$@" 2>&1; echo; }
echo "== a library on the primary"
docker exec -i $P redis-cli -x FUNCTION LOAD <<'LUA'
#!lua name=shop
redis.register_function{function_name='stock', callback=function(keys) return redis.call('HGET', keys[1], 'stock') end, flags={'no-writes'}}
redis.register_function('sell', function(keys) return redis.call('HINCRBY', keys[1], 'stock', -1) end)
LUA
r $P HSET item:1 stock 5
sleep 1
echo "== the replica got the library through replication"
r $R FUNCTION LIST LIBRARYNAME shop
r $R FCALL_RO stock 1 item:1
r $R FCALL sell 1 item:1
echo "== FUNCTION DUMP from the primary, FUNCTION RESTORE into an unrelated server"
docker exec $P sh -c 'redis-cli FUNCTION DUMP | head -c -1 > /tmp/f.dump; wc -c < /tmp/f.dump'
docker cp $P:/tmp/f.dump /tmp/nor-f.dump >/dev/null && docker cp /tmp/nor-f.dump $X:/tmp/f.dump >/dev/null && rm -f /tmp/nor-f.dump
echo "[$X]> FUNCTION RESTORE <dump>"; docker exec $X sh -c 'redis-cli -x FUNCTION RESTORE < /tmp/f.dump'; echo
r $X FUNCTION LIST
r $X FUNCTION RESTORE "$(echo -n x)"
echo "== an ACL file: ACL SAVE writes it, ACL LOAD reads it back"
r $P ACL SETUSER reporter on '>pw' '~report:*' '+@read'
r $P ACL SAVE
echo "[$P]$ cat /data/users.acl   (password hashes shortened here)"; docker exec $P cat /data/users.acl | sed -E 's/#([0-9a-f]{8})[0-9a-f]{56}/#\1.../'; echo
docker exec $P sh -c 'printf "# added by hand, comments allowed since Redis 8.8\nuser ops on >pw2 ~* +@all -@dangerous\n" >> /data/users.acl'
r $P ACL LOAD
r $P ACL USERS
docker exec $P sh -c 'echo "user broken on >pw ~* +nosuchcommand" >> /data/users.acl'
r $P ACL LOAD
r $P ACL USERS
echo "== ACL LOG: a wrong password and a denied command"
r $P ACL LOG RESET
docker exec $P redis-cli --user reporter --pass wrong --no-auth-warning PING >/dev/null 2>&1
docker exec $P redis-cli --user reporter --pass pw --no-auth-warning SET report:1 x >/dev/null 2>&1
docker exec $P redis-cli --user reporter --pass pw --no-auth-warning GET secret:1 >/dev/null 2>&1
echo "[$P]> ACL LOG (fields: reason, context, object, username)"
docker exec $P redis-cli ACL LOG | paste -sd' ' | sed 's/ count / \n   count /g' | grep -o -E '(count|reason|context|object|username) [^ ]+' | paste -d' ' - - - - - | sed 's/^/   /'
docker rm -f $P $R $X >/dev/null; docker network rm $NET >/dev/null
