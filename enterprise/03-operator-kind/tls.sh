#!/usr/bin/env bash
# TLS on an operator-managed database: create REDB "secure" with tlsMode enabled, fetch the cluster's proxy
# certificate through the REC API, then connect from a pod with and without TLS. Run after up.sh.
# operator가 관리하는 DB의 TLS: tlsMode enabled인 REDB, REC API로 프록시 인증서, TLS 유무로 접속.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
NS=rec
kubectl -n $NS apply -f redb-tls.yaml >/dev/null
until [ "$(kubectl -n $NS get redb secure -o jsonpath='{.status.status}' 2>/dev/null)" = active ]; do sleep 2; done
PORT=$(kubectl -n $NS get redb secure -o jsonpath='{.status.internalEndpoints[0].port}')
PW=$(kubectl -n $NS get secret redb-secure -o jsonpath='{.data.password}' | base64 -d)
echo "secure: active, port $PORT, spec.tlsMode $(kubectl -n $NS get redb secure -o jsonpath='{.spec.tlsMode}')"
U=$(kubectl -n $NS get secret rec -o jsonpath='{.data.username}' | base64 -d); P=$(kubectl -n $NS get secret rec -o jsonpath='{.data.password}' | base64 -d)
kubectl -n $NS port-forward --address 127.0.0.1 svc/rec 29443:9443 >/dev/null 2>&1 & PF=$!; sleep 3
curl -sk -u "$U:$P" https://127.0.0.1:29443/v1/cluster/certificates | python3 -c "import json,sys;print(json.load(sys.stdin)['proxy_cert'],end='')" > proxy.pem
kill $PF
openssl x509 -in proxy.pem -noout -subject -ext subjectAltName 2>/dev/null | tr '\n' ' ' | sed 's/^/proxy certificate: /'; echo
kubectl -n $NS get pod cli >/dev/null 2>&1 || { kubectl -n $NS run cli --image=redis:8.10.3 --restart=Never --command -- sleep 3600 >/dev/null; kubectl -n $NS wait --for=condition=Ready pod/cli --timeout=60s >/dev/null; }
kubectl -n $NS cp proxy.pem cli:/tmp/proxy.pem; rm -f proxy.pem
c() { kubectl -n $NS exec cli -- sh -c "$1" 2>&1 | head -2 | tr '\n' ' '; echo; }
echo "plain TCP:                           $(c "redis-cli -h secure -p $PORT -a '$PW' --no-auth-warning PING")"
echo "TLS, proxy cert as CA, name secure:  $(c "redis-cli -h secure -p $PORT -a '$PW' --no-auth-warning --tls --cacert /tmp/proxy.pem PING")"
echo "TLS, proxy cert as CA, full name:    $(c "redis-cli -h secure.rec.svc.cluster.local -p $PORT -a '$PW' --no-auth-warning --tls --cacert /tmp/proxy.pem PING")"
echo "TLS, no CA:                          $(c "redis-cli -h secure -p $PORT -a '$PW' --no-auth-warning --tls PING")"
kubectl -n $NS delete -f redb-tls.yaml --wait=false >/dev/null; echo "secure deleted"
