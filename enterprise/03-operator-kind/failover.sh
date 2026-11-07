#!/usr/bin/env bash
# Delete the pod that holds the target database's primary shard while a client writes every 50 ms,
# then report the longest run of failed writes and whether the counter lost anything.
# 대상 DB의 주 샤드가 있는 파드를 지우고, 50 ms마다 쓰는 클라이언트의 최장 실패 구간과 손실 여부를 본다.
set -euo pipefail
NS=rec
PW=$(kubectl -n $NS get secret redb-target -o jsonpath='{.data.password}' | base64 -d)
PORT=$(kubectl -n $NS get redb target -o jsonpath='{.status.internalEndpoints[0].port}')
node_of_master() { kubectl -n $NS exec rec-0 -c redis-enterprise-node -- rladmin status shards db target 2>/dev/null | awk '$5=="master"{print $4}'; }
echo "== before"; kubectl -n $NS exec rec-0 -c redis-enterprise-node -- rladmin status shards db target | tail -n +2
kubectl -n $NS exec rec-0 -c redis-enterprise-node -- rladmin status endpoints db target | tail -n +2
M=$(node_of_master); POD=rec-$(( ${M#node:} - 1 ))
echo "primary shard on $M -> pod $POD"
kubectl -n $NS delete pod writer --ignore-not-found --wait >/dev/null
kubectl -n $NS run writer --image=redis:8.10.3 --restart=Never --env="PW=$PW" --command -- sh -c "
  redis-cli -h target -p $PORT -a \"\$PW\" --no-auth-warning SET c 0 >/dev/null
  i=0; while [ \$i -lt 1600 ]; do
    r=\$(timeout 1 redis-cli -h target -p $PORT -a \"\$PW\" --no-auth-warning INCR c 2>&1 | tr -d '\r'); t=\$(date +%s.%N | cut -c1-14)
    echo \"\$t \$r\"; i=\$((i+1)); sleep 0.05; done" >/dev/null
kubectl -n $NS wait --for=condition=Ready pod/writer --timeout=60s >/dev/null
sleep 10
UID0=$(kubectl -n $NS get pod $POD -o jsonpath='{.metadata.uid}')
echo "== deleting $POD at $(date +%T)"
kubectl -n $NS delete pod $POD --wait=false
t0=$(date +%s)
until [ "$(kubectl -n $NS get pod $POD -o jsonpath='{.metadata.uid}' 2>/dev/null)" != "$UID0" ] && [ -n "$(kubectl -n $NS get pod $POD -o jsonpath='{.metadata.uid}' 2>/dev/null)" ]; do sleep 1; done
echo "replacement $POD created after $(( $(date +%s) - t0 )) s"
kubectl -n $NS wait --for=condition=Ready pod/$POD --timeout=900s >/dev/null && echo "replacement $POD ready after $(( $(date +%s) - t0 )) s"
kubectl -n $NS wait --for=jsonpath='{.status.phase}'=Succeeded pod/writer --timeout=600s >/dev/null || true
kubectl -n $NS logs writer > writer.log
python3 - <<'PY'
rows = [l.split(" ", 1) for l in open("writer.log").read().splitlines() if " " in l]
ok = [(float(t), r) for t, r in rows if r.strip().isdigit()]
bad = [(float(t), r) for t, r in rows if not r.strip().isdigit()]
gap, cur, start, prev = 0.0, 0.0, None, None
for t, r in [(float(t), r) for t, r in rows]:
    if r.strip().isdigit():
        if start is not None:
            gap = max(gap, t - start); start = None
    elif start is None:
        start = prev if prev else t
    prev = t
print(f"writes attempted {len(rows)}, succeeded {len(ok)}, failed {len(bad)}")
print("failure messages:", sorted({r.strip()[:70] for _, r in bad}) or "none")
print(f"longest stretch without a successful write: {gap:.1f} s")
vals = [int(r) for _, r in ok]
print(f"counter: last value {vals[-1]}, successful writes {len(vals)}, values strictly increasing: {all(b > a for a, b in zip(vals, vals[1:]))}")
PY
rm -f writer.log
echo "== after"; kubectl -n $NS exec rec-0 -c redis-enterprise-node -- rladmin status shards db target | tail -n +2
kubectl -n $NS exec rec-0 -c redis-enterprise-node -- rladmin status endpoints db target | tail -n +2
kubectl -n $NS get rec rec -o jsonpath='{.status.state}{"\n"}'
kubectl -n $NS delete pod writer --wait=false >/dev/null
