#!/usr/bin/env bash
# Postgres source, RDI 2.2.1 from its Helm chart into the kind cluster of ../03-operator-kind (run its up.sh first),
# secrets, and the pipeline in ./pipeline. Downloads the chart and the redis-di CLI into ./.rdi (gitignored).
# Postgres 원천, RDI 2.2.1 Helm 설치, 시크릿, 파이프라인 배포. 먼저 ../03-operator-kind/up.sh.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
V=2.2.1; B=https://redis-enterprise-software-downloads.s3.amazonaws.com/redis-di
mkdir -p .rdi
[ -f .rdi/rdi-$V.tgz ] || curl -sSLo .rdi/rdi-$V.tgz $B/rdi-$V.tgz
[ -x .rdi/redis-di ] || { curl -sSLo .rdi/redis-di $B/cli/$V/bin/linux-amd64/redis-di; chmod +x .rdi/redis-di; }
s() { date +%s; }
kubectl config use-context kind-nor-rec >/dev/null
t=$(s); kubectl apply -f postgres.yaml >/dev/null; kubectl -n source rollout status deploy/postgres --timeout=300s >/dev/null
until kubectl -n source exec deploy/postgres -- psql -U rdi -d shop -tAc "SELECT count(*) FROM customer" >/dev/null 2>&1; do sleep 2; done
echo "postgres ready after $(( $(s) - t )) s: $(kubectl -n source exec deploy/postgres -- psql -U rdi -d shop -tAc "SELECT 'wal_level=' || current_setting('wal_level') || ', rows=' || count(*) FROM customer")"
RDIPW=$(kubectl -n rec get secret redb-rdi-state -o jsonpath='{.data.password}' | base64 -d)
TPW=$(kubectl -n rec get secret redb-target -o jsonpath='{.data.password}' | base64 -d)
RPORT=$(kubectl -n rec get redb rdi-state -o jsonpath='{.status.internalEndpoints[0].port}')
t=$(s); helm upgrade --install rdi .rdi/rdi-$V.tgz -f rdi-values.yaml -n rdi --create-namespace \
  --set connection.port=$RPORT --set connection.password="$RDIPW" --set api.jwtKey="$(head -c 32 /dev/urandom | base64)" --wait --timeout 10m >/dev/null
echo "RDI $V installed after $(( $(s) - t )) s"; kubectl -n rdi get pods --no-headers | awk '{print "  ", $1, $3}'
pkill -f "port-forward --address 127.0.0.1 svc/rdi-api" 2>/dev/null || true
kubectl -n rdi port-forward --address 127.0.0.1 svc/rdi-api 28080:8080 >/dev/null 2>&1 &
sleep 3
export RDI_API_URL=http://127.0.0.1:28080 RDI_PASSWORD="$RDIPW"
R() { .rdi/redis-di --user default "$@"; }
R info
R set-secret USERNAME --db postgresql rdi --wait=false >/dev/null
R set-secret PASSWORD --db postgresql rdi-lab-pw --wait=false >/dev/null
R set-secret PASSWORD --db target "$TPW" >/dev/null
TPORT=$(kubectl -n rec get redb target -o jsonpath='{.status.internalEndpoints[0].port}')
sed "s/__TARGET_PORT__/$TPORT/" pipeline/config.yaml.in > pipeline/config.yaml
t=$(s); R deploy --dir pipeline; echo "pipeline deployed after $(( $(s) - t )) s"
until R describe 2>/dev/null | grep -q -E "postgresql.public.customer +1000 "; do sleep 3; done
echo "initial snapshot done after $(( $(s) - t )) s"
R describe
