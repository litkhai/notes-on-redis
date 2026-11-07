#!/usr/bin/env bash
# Change rows in Postgres and time how long each change takes to appear in the target database.
# A watcher pod polls Redis every 20 ms; kind nodes share the host clock, so host and pod timestamps compare.
# Postgres에서 행을 바꾸고 대상 DB에 나타나기까지 걸린 시간을 잰다.
set -euo pipefail
PORT=$(kubectl -n rec get redb target -o jsonpath='{.status.internalEndpoints[0].port}')
PW=$(kubectl -n rec get secret redb-target -o jsonpath='{.data.password}' | base64 -d)
psql() { kubectl -n source exec deploy/postgres -- psql -U rdi -d shop -qtAc "$1"; }
now() { date +%s.%N; }
# wait_for <redis-cli args> <expected output>: poll inside the cluster, print the pod's timestamp when it matches
wait_for() {
  kubectl -n rec exec cli -- sh -c "while :; do v=\$(redis-cli -h target -p $PORT -a \"\$PW\" --no-auth-warning $1); [ \"\$v\" = '$2' ] && { date +%s.%N; break; }; sleep 0.02; done"
}
lag() { python3 -c "print(f'{($2 - $1) * 1000:.0f} ms')"; }
kubectl -n rec get pod cli >/dev/null 2>&1 || { kubectl -n rec run cli --image=redis:8.10.3 --restart=Never --env="PW=$PW" --command -- sleep 3600 >/dev/null; kubectl -n rec wait --for=condition=Ready pod/cli --timeout=60s >/dev/null; }

N=$(psql "SELECT max(id) FROM customer"); NEW=$((N + 1)); OLD=$(psql "SELECT min(id) FROM customer")
echo "== UPDATE one row: customer 7 credit_limit -> 9000 + run number (tier gold)"
v=$(( 9000 + NEW )); t0=$(now); psql "UPDATE customer SET credit_limit = $v WHERE id = 7"; t1=$(wait_for "JSON.GET customer:7 .credit_limit" "$v"); echo "   visible after $(lag $t0 $t1)"
echo "== INSERT one row: customer $NEW"
t0=$(now); psql "INSERT INTO customer VALUES ($NEW, 'customer-$NEW', 'x@example.com', 'KR', 2000)"; t1=$(wait_for "EXISTS customer:$NEW" 1); echo "   visible after $(lag $t0 $t1)"
echo "== DELETE one row: customer $OLD"
t0=$(now); psql "DELETE FROM customer WHERE id = $OLD"; t1=$(wait_for "EXISTS customer:$OLD" 0); echo "   gone after $(lag $t0 $t1)"
ROWS=$(psql "SELECT count(*) FROM customer")
echo "== UPDATE every row in one transaction ($ROWS rows): credit_limit + 1, watching customer $NEW"
want=$(( $(psql "SELECT credit_limit FROM customer WHERE id = $NEW") + 1 ))
t0=$(now); psql "UPDATE customer SET credit_limit = credit_limit + 1"; t1=$(wait_for "JSON.GET customer:$NEW .credit_limit" "$want"); echo "   all updates visible after $(lag $t0 $t1)"
echo "== the overhead in these numbers: one kubectl exec of psql that changes nothing"
t0=$(now); psql "SELECT 1" >/dev/null; t1=$(now); echo "   $(lag $t0 $t1)"
echo "== the transformation on the new row"
kubectl -n rec exec cli -- sh -c "redis-cli -h target -p $PORT -a \"\$PW\" --no-auth-warning JSON.GET customer:$NEW"
