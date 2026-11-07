#!/usr/bin/env bash
# BACKUP (8.10): start, write during the backup, seal, list the pinned files, write again;
# then restore the sealed files into a new container with --preload-file aof:<manifest>.
# BACKUP(8.10): 시작, 백업 중 쓰기, 봉인, 고정된 파일 목록, 다시 쓰기. 이어서 봉인된
# 파일을 새 컨테이너에 --preload-file aof:<manifest>로 복원한다.
set -euo pipefail
IMG=redis:8.10.3; C=nor-dd-bk; R=nor-dd-rs
WORK=$(mktemp -d)
trap 'docker rm -f $C $R >/dev/null 2>&1 || true; rm -rf "${WORK:?}"' EXIT
docker rm -f $C $R >/dev/null 2>&1 || true
docker run -d --name $C $IMG redis-server --save "" --appendonly yes >/dev/null; sleep 2
cli() { docker exec $C redis-cli "$@"; }
cli SET before-backup 1 >/dev/null
echo "> BACKUP START";  cli BACKUP START
cli SET during-backup 2 >/dev/null
echo "> BACKUP SEAL";   cli BACKUP SEAL
echo "> BACKUP STATUS"; cli BACKUP STATUS | paste -sd' '
echo "> BACKUP LIST";   cli BACKUP LIST
cli SET after-seal 3 >/dev/null
echo "> link counts in backupdir (2 = shared with appendonlydir)"
docker exec $C sh -c 'stat -c "%h %n" /data/backupdir/*'
echo "> source keys: $(cli KEYS '*' | sort | paste -sd' ')"
docker cp -q $C:/data/backupdir "$WORK/" && chmod -R a+rX "$WORK"
docker run -d --name $R -v "$WORK/backupdir:/restore:ro" $IMG \
  redis-server --save "" --appendonly no --preload-file aof:/restore/appendonly.aof.manifest >/dev/null; sleep 3
docker logs $R 2>&1 | grep -E "pre-loaded|loaded from" | sed 's/^.*\* //'
echo "> restored keys: $(docker exec $R redis-cli KEYS '*' | sort | paste -sd' ')"
