#!/usr/bin/env bash
# Run the pipeline as a replication-only Postgres user instead of the superuser up.sh uses, following the
# "replication group" steps on RDI's PostgreSQL page, then rerun cdc.sh. Run after up.sh.
# up.sh의 슈퍼유저 대신 복제 전용 사용자로 파이프라인을 돌린다(RDI PostgreSQL 페이지의 replication group 절차).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
psql() { kubectl -n source exec deploy/postgres -- psql -U rdi -d shop -v ON_ERROR_STOP=1 -qtAc "$1"; }
echo "== create the user and the replication group"
psql "DO \$\$BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='rdi_cdc') THEN CREATE ROLE rdi_cdc LOGIN REPLICATION PASSWORD 'cdc-lab-pw'; END IF; END\$\$"
psql "DO \$\$BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='replication_group') THEN CREATE ROLE replication_group; END IF; END\$\$"
psql "GRANT replication_group TO rdi"
psql "GRANT replication_group TO rdi_cdc"
psql "ALTER TABLE customer OWNER TO replication_group"
psql "GRANT CREATE ON DATABASE shop TO rdi_cdc"
psql "SELECT rolname || ': superuser=' || rolsuper || ', replication=' || rolreplication || ', createdb=' || rolcreatedb FROM pg_roles WHERE rolname IN ('rdi','rdi_cdc') ORDER BY 1"
echo "== what rdi_cdc cannot do"
kubectl -n source exec deploy/postgres -- env PGPASSWORD=cdc-lab-pw psql -h 127.0.0.1 -U rdi_cdc -d shop -qtAc "CREATE ROLE intruder" 2>&1 | head -1 || true
kubectl -n source exec deploy/postgres -- env PGPASSWORD=cdc-lab-pw psql -h 127.0.0.1 -U rdi_cdc -d shop -qtAc "SELECT count(*) FROM customer"
export RDI_API_URL=http://127.0.0.1:28080
RDI_PASSWORD=$(kubectl -n rec get secret redb-rdi-state -o jsonpath='{.data.password}' | base64 -d); export RDI_PASSWORD
R() { .rdi/redis-di --user default "$@"; }
echo "== switch the pipeline's source secrets to rdi_cdc and reset it (new snapshot as that user)"
R set-secret USERNAME --db postgresql rdi_cdc --wait=false >/dev/null
R set-secret PASSWORD --db postgresql cdc-lab-pw >/dev/null
t=$(date +%s); R reset --help >/dev/null 2>&1 && yes | R reset 2>&1 | tail -1 || true
until R describe 2>/dev/null | awk '/postgresql.public.customer/{found=1; exit !($4 >= 1000)} END{if(!found) exit 1}'; do sleep 3; [ $(( $(date +%s) - t )) -gt 300 ] && break; done
echo "snapshot as rdi_cdc done after $(( $(date +%s) - t )) s"
R describe | sed -n '/^Sources:/,/^$/p;/^Statistics:/,/^$/p'
kubectl -n source exec deploy/postgres -- psql -U rdi -d shop -qtAc "SELECT 'replication connection as ' || usename || ', ' || state FROM pg_stat_replication; SELECT 'replication slot ' || slot_name || ' active=' || active FROM pg_replication_slots; SELECT 'publication ' || pubname || ' owner ' || pg_get_userbyid(pubowner) FROM pg_publication"
./cdc.sh
