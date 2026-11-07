#!/usr/bin/env bash
# io-threads 1, 4, 8 again, two ways the base run did not cover: pipelining (-P 16) and TLS
# (where the I/O threads also do the encryption). Same client placement as run.sh.
# 기본 실행에 없던 두 경우로 io-threads 1, 4, 8: 파이프라이닝(-P 16)과 TLS(I/O 스레드가 암호화도 맡음).
set -euo pipefail
IMG=redis:8.10.3
D=$(mktemp -d -p "$HOME" nor-tls.XXXX); trap 'rm -rf "$D"; docker rm -f nor-dd-thr2 >/dev/null 2>&1' EXIT
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=nor-lab" -keyout "$D/key.pem" -out "$D/cert.pem" 2>/dev/null
chmod 755 "$D"; chmod 644 "$D"/*.pem   # the server runs as the redis user
bench() { docker run --rm --network container:nor-dd-thr2 -v "$D:/tls:ro" $IMG redis-benchmark -q -t set,get -n "$1" -c 400 -d 64 --threads 12 "${@:2}" 2>&1 | tr '\r' '\n' | grep -E "requests per second" | sed 's/^/   /'; }
for n in 1 4 8; do
  docker rm -f nor-dd-thr2 >/dev/null 2>&1 || true
  docker run -d --name nor-dd-thr2 -v "$D:/tls:ro" $IMG redis-server --save "" --appendonly no --io-threads $n \
    --port 6379 --tls-port 6380 --tls-cert-file /tls/cert.pem --tls-key-file /tls/key.pem --tls-ca-cert-file /tls/cert.pem --tls-auth-clients no >/dev/null
  sleep 2; docker exec nor-dd-thr2 redis-cli PING >/dev/null || { docker logs nor-dd-thr2 | tail -3; exit 1; }
  echo "== io-threads $n"
  echo "-- plain TCP, pipeline 16"
  bench 6000000 -P 16
  echo "-- TLS, no pipelining"
  bench 1000000 -P 1 -p 6380 --tls --cacert /tls/cert.pem
done
