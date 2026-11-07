#!/usr/bin/env bash
# Streams on Redis 8.10.3: consumer group, a consumer that dies, XAUTOCLAIM, XACKDEL (8.2),
# IDMP idempotent XADD (8.6) and XNACK (8.8). Prints each command and its reply.
# 소비자 그룹, 죽은 소비자, XAUTOCLAIM, XACKDEL(8.2), IDMP(8.6), XNACK(8.8).
set -uo pipefail
C=nor-dd-st
docker rm -f $C >/dev/null 2>&1; docker run -d --name $C redis:8.10.3 >/dev/null; sleep 2
r() { echo "> $*"; docker exec $C redis-cli --no-raw "$@"; echo; }
echo "== a group and two consumers"
for i in 1 2 3 4 5; do docker exec $C redis-cli XADD orders "0-$i" item "book-$i" >/dev/null; done
r XGROUP CREATE orders shipping 0
r XREADGROUP GROUP shipping c1 COUNT 3 STREAMS orders '>'
echo "== c1 dies without acknowledging; c2 claims what has been idle for 100 ms"
sleep 0.2
r XPENDING orders shipping
r XAUTOCLAIM orders shipping c2 100 0-0 COUNT 10
r XPENDING orders shipping - + 10
echo "== XACKDEL (8.2): acknowledge and delete in one call"
r XLEN orders
r XACKDEL orders shipping IDS 2 0-1 0-2
r XLEN orders
echo "== IDMP (8.6): the same producer id and idempotency id twice"
r XADD payments IDMP svc-a req-42 '*' amount 100
r XADD payments IDMP svc-a req-42 '*' amount 100
r XLEN payments
echo "== XNACK (8.8): give a claimed message back without acknowledging it"
r XREADGROUP GROUP shipping c3 COUNT 1 STREAMS orders '>'
r XPENDING orders shipping - + 10
r XNACK orders shipping FAIL IDS 1 0-4
r XPENDING orders shipping - + 10
r XREADGROUP GROUP shipping c4 COUNT 2 STREAMS orders '>'
r XPENDING orders shipping - + 10
r XAUTOCLAIM orders shipping c5 60000 0-0 COUNT 10
r XPENDING orders shipping - + 10
docker rm -f $C >/dev/null
