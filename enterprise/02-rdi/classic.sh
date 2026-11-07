#!/usr/bin/env bash
# The same pipeline on the classic processor instead of Flink (the default since RDI 2.0): redeploy with
# processors.type classic, compare the pods, and rerun cdc.sh. Run after up.sh.
# 같은 파이프라인을 Flink 대신 classic 프로세서로: 다시 배포하고 파드를 비교하고 cdc.sh를 다시 돈다.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
export RDI_API_URL=http://127.0.0.1:28080
RDI_PASSWORD=$(kubectl -n rec get secret redb-rdi-state -o jsonpath='{.data.password}' | base64 -d); export RDI_PASSWORD
R() { .rdi/redis-di --user default "$@"; }
echo "== pods with the Flink processor"; kubectl -n rdi get pods --no-headers | awk '{print "  ", $1}' | sed -E 's/-[a-z0-9]{8,10}-[a-z0-9]{5}$//'
mkdir -p .classic/jobs; cp pipeline/jobs/*.yaml .classic/jobs/
sed 's/^processors:$/processors:\n  type: classic/' pipeline/config.yaml > .classic/config.yaml
grep -A2 "^processors:" .classic/config.yaml | sed 's/^/   /'
t=$(date +%s); R deploy --dir .classic; echo "redeployed after $(( $(date +%s) - t )) s"
sleep 10
echo "== pods with the classic processor"; kubectl -n rdi get pods --no-headers | awk '$3=="Running"{print "  ", $1}' | sed -E 's/-[a-z0-9]{8,10}-[a-z0-9]{5}$//'
R describe | sed -n '/^Processor:/,/^Jobs:/p;/^Statistics:/,/^$/p'
for i in 1 2; do echo "##### cdc.sh run $i"; ./cdc.sh; done
