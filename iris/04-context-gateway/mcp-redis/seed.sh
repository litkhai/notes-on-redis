#!/usr/bin/env bash
# Made-up data for the mcp-redis upstream: a few hashes, a list and a counter in a throwaway local Redis.
set -euo pipefail
c="docker exec -i nor-mcp-redis redis-cli"
for i in 1 2 3; do $c HSET "ticket:$i" title "made-up ticket $i" status open priority "$i" >/dev/null; done
$c RPUSH queue:support ticket:1 ticket:2 ticket:3 >/dev/null
$c SET counter:visits 41 >/dev/null
$c DBSIZE
