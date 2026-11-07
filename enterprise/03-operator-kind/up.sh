#!/usr/bin/env bash
# kind cluster, Redis Enterprise operator and cluster (REC) from the Helm chart, two databases (REDB),
# and a third database that asks for more shards than the trial licence allows.
# kind 클러스터, Helm 차트로 operator와 REC, DB 둘, 체험 라이선스를 넘는 세 번째 DB.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
CHART=8.2.6-21
s() { date +%s; }
t=$(s); kind create cluster --config kind.yaml >/dev/null 2>&1; echo "kind cluster up in $(( $(s) - t )) s"
kubectl config use-context kind-nor-rec >/dev/null
kubectl get nodes --no-headers | awk '{print "  ", $1, $2, $5}'
helm repo add redis https://helm.redis.io >/dev/null 2>&1 || true
kubectl create namespace rec >/dev/null
t=$(s); helm install rec-op redis/redis-enterprise-operator --version $CHART -n rec --values values.yaml >/dev/null
until [ "$(kubectl -n rec get rec rec -o jsonpath='{.status.state}' 2>/dev/null)" = Running ]; do sleep 5; done
echo "operator chart $CHART installed, REC Running after $(( $(s) - t )) s"
kubectl -n rec get rec rec
t=$(s); kubectl -n rec apply -f redb.yaml >/dev/null
until [ "$(kubectl -n rec get redb -o jsonpath='{range .items[*]}{.status.status}{" "}{end}')" = "active active " ]; do sleep 2; done
echo "databases active after $(( $(s) - t )) s"
kubectl -n rec get redb
kubectl -n rec exec rec-0 -c redis-enterprise-node -- rladmin status shards
echo "== a database that needs two more shards"
kubectl -n rec apply -f redb-over-license.yaml 2>&1 || true
