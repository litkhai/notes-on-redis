#!/usr/bin/env bash
# Functions and ACL on Redis 8.10.3: a library with a read-only and a writing function, FCALL_RO;
# key permissions %R~ / %W~, a selector, and +@all -@write against module commands (JSON).
# Functions와 ACL: 읽기 전용·쓰기 함수, FCALL_RO, 키 권한 %R~/%W~, 셀렉터, 모듈 명령에 대한 +@all -@write.
set -uo pipefail
C=nor-dd-fa
docker rm -f $C >/dev/null 2>&1; docker run -d --name $C redis:8.10.3 >/dev/null; sleep 2
r()  { echo "> $*"; docker exec $C redis-cli --no-raw "$@" 2>&1; echo; }
ru() { local u=$1; shift; echo "[$u]> $*"; docker exec $C redis-cli --no-raw --user "$u" --pass pw --no-auth-warning "$@" 2>&1; echo; }
echo "== a function library"
docker exec -i $C redis-cli -x FUNCTION LOAD REPLACE <<'LUA'
#!lua name=shop
redis.register_function{function_name='stock', callback=function(keys) return redis.call('HGET', keys[1], 'stock') end, flags={'no-writes'}}
redis.register_function('sell', function(keys)
  local left = redis.call('HINCRBY', keys[1], 'stock', -1)
  if left < 0 then redis.call('HINCRBY', keys[1], 'stock', 1) return redis.error_reply('sold out') end
  return left
end)
LUA
echo
r HSET item:1 name lamp stock 1
r FCALL_RO stock 1 item:1
r FCALL sell 1 item:1
r FCALL sell 1 item:1
r FCALL_RO sell 1 item:1
echo "== key permissions: %R~ read-only keys, %W~ write-only keys"
r ACL SETUSER app on '>pw' '%R~catalog:*' '%W~events:*' '+@all'
r SET catalog:1 lamp
ru app GET catalog:1
ru app SET catalog:1 chair
ru app XADD events:clicks '*' item 1
ru app XRANGE events:clicks - +
echo "== a selector: base rules plus a second, narrower set"
r ACL SETUSER rep on '>pw' '~report:*' '+@read' '(~audit:* +xadd)'
ru rep GET report:1
ru rep XADD audit:log '*' who rep
ru rep SET report:1 x
ru rep XADD report:log '*' who rep
echo "== +@all -@write in Redis 8: module write commands are in @write too"
r ACL SETUSER ro on '>pw' '~*' '+@all' '-@write'
r JSON.SET doc '$' '{"a":1}'
ru ro JSON.GET doc
ru ro JSON.SET doc '$.a' 2
ru ro TS.ADD temp '*' 1
echo "== +@read alone: do module read commands come with it?"
r ACL SETUSER rd on '>pw' '~*' '+@read'
ru rd JSON.GET doc
ru rd TS.RANGE temp - +
echo "== module commands in @write: names starting json. ts. bf. cf. cms. topk. tdigest. ft."
echo "> ACL CAT write | grep -c -E '^(json|ts|bf|cf|cms|topk|tdigest|ft)\.'"
docker exec $C redis-cli ACL CAT write | grep -c -E '^(json|ts|bf|cf|cms|topk|tdigest|ft)\.'
echo
docker rm -f $C >/dev/null
