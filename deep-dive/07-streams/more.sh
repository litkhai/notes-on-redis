#!/usr/bin/env bash
# Streams, the remaining options on Redis 8.10.3: XNACK modes, RETRYCOUNT and FORCE; IDMPAUTO;
# XCFGSET (IDMP retention); XACKDEL KEEPREF / DELREF / ACKED with two consumer groups.
# XNACK 모드·RETRYCOUNT·FORCE, IDMPAUTO, XCFGSET, 두 그룹에서의 XACKDEL KEEPREF/DELREF/ACKED.
set -uo pipefail
C=nor-dd-st2
docker rm -f $C >/dev/null 2>&1; docker run -d --name $C redis:8.10.3 >/dev/null; sleep 2
r() { echo "> $*"; docker exec $C redis-cli --no-raw "$@"; echo; }
q() { docker exec $C redis-cli "$@" >/dev/null; }
count() { docker exec $C redis-cli XPENDING s g - + 10 | paste -sd' '; }
echo "== XNACK modes: one entry per mode, read by c1, then released"
for i in 1 2 3 4; do q XADD s "0-$i" n "$i"; done
q XGROUP CREATE s g 0
q XREADGROUP GROUP g c1 COUNT 4 STREAMS s '>'
r XNACK s g SILENT IDS 1 0-1
r XNACK s g FAIL IDS 1 0-2
r XNACK s g FATAL IDS 1 0-3
r XNACK s g FAIL IDS 1 0-4 RETRYCOUNT 5
r XPENDING s g - + 10
echo "== FORCE: an ID that is in the stream but not in the group's pending list"
q XADD s 0-5 n 5
r XNACK s g FAIL IDS 1 0-5
r XNACK s g FAIL IDS 1 0-5 FORCE
r XPENDING s g 0-5 0-5 1
echo "== IDMPAUTO: the producer id only; the server derives the idempotent id"
r XADD a IDMPAUTO svc-a '*' amount 100
r XADD a IDMPAUTO svc-a '*' amount 100
r XADD a IDMPAUTO svc-a '*' amount 200
r XLEN a
echo "== XCFGSET: IDMP-DURATION 1 s, then the same IDMP id after 2 s"
q XADD p IDMP svc-a req-1 '*' x 1
r XCFGSET p IDMP-DURATION 1
r XADD p IDMP svc-a req-1 '*' x 1
sleep 2
r XADD p IDMP svc-a req-1 '*' x 1
r XLEN p
echo "== XCFGSET: IDMP-MAXSIZE 2, three ids, then the first again"
q DEL m; q XADD m '*' init 1
r XCFGSET m IDMP-DURATION 600 IDMP-MAXSIZE 2
for id in r1 r2 r3; do q XADD m IDMP svc-b $id '*' x 1; done
r XLEN m
r XADD m IDMP svc-b r1 '*' x 1
r XLEN m
for mode in KEEPREF DELREF ACKED; do
  echo "== XACKDEL $mode with two groups (g1 and g2 both read entry 0-1)"
  q DEL t; q XADD t 0-1 v 1; q XGROUP CREATE t g1 0; q XGROUP CREATE t g2 0
  q XREADGROUP GROUP g1 c STREAMS t '>'; q XREADGROUP GROUP g2 c STREAMS t '>'
  r XACKDEL t g1 $mode IDS 1 0-1
  echo "   XLEN t: $(docker exec $C redis-cli XLEN t); pending in g1: $(docker exec $C redis-cli XPENDING t g1 | head -1); pending in g2: $(docker exec $C redis-cli XPENDING t g2 | head -1)"
  if [ $mode = ACKED ]; then r XACKDEL t g2 ACKED IDS 1 0-1; echo "   XLEN t after g2 also acknowledged: $(docker exec $C redis-cli XLEN t)"; fi
  if [ $mode = KEEPREF ]; then r XCLAIM t g2 c2 0 0-1; fi
done
docker rm -f $C >/dev/null
