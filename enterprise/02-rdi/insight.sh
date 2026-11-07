#!/usr/bin/env bash
# Redis Insight's Redis Data Integration view: start Redis Insight 3.8.0 on the host network and register
# the RDI API that up.sh forwards to 127.0.0.1:28080. Then open http://127.0.0.1:25540/integrate.
# Redis Insight 3.8.0을 띄우고 up.sh가 127.0.0.1:28080으로 포워딩한 RDI API를 등록한다.
set -euo pipefail
docker rm -f nor-insight-rdi >/dev/null 2>&1 || true
docker run -d --name nor-insight-rdi --network host -e RI_APP_PORT=25540 -e RI_ACCEPT_TERMS_AND_CONDITIONS=true redis/redisinsight:3.8.0 >/dev/null
until curl -sf http://127.0.0.1:25540/api/health >/dev/null; do sleep 2; done
RDIPW=$(kubectl -n rec get secret redb-rdi-state -o jsonpath='{.data.password}' | base64 -d)
curl -s -X POST http://127.0.0.1:25540/api/rdi -H 'Content-Type: application/json' \
  -d "{\"name\":\"nor-rdi-lab\",\"url\":\"http://127.0.0.1:28080\",\"username\":\"default\",\"password\":\"$RDIPW\"}" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print('registered', d['name'], 'RDI version', d.get('version'))"
echo "open http://127.0.0.1:25540/integrate   (docker rm -f nor-insight-rdi when done)"
