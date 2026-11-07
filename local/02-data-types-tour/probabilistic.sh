#!/usr/bin/env bash
# The probabilistic types the tour skipped, on Redis 8.10.3: count-min sketch (how often?), cuckoo
# filter (seen before, and can forget), t-digest (percentiles). 100,000 made-up events each.
# 투어에서 빠진 확률형: count-min sketch(몇 번?), cuckoo filter(본 적 있나, 지울 수 있음), t-digest(백분위).
set -euo pipefail
C=nor-local-prob
docker rm -f $C >/dev/null 2>&1; docker run -d --name $C redis:8.10.3 >/dev/null; sleep 2
r() { echo "> $*"; docker exec $C redis-cli --no-raw "$@"; echo; }
py() { docker exec -i $C sh -c 'redis-cli --pipe >/dev/null'; }
echo "== count-min sketch: 100,000 page views over 1,000 pages, page:1 is hot"
r CMS.INITBYPROB views 0.001 0.01
python3 - <<'PY' | py
import random, collections; random.seed(1); n = collections.Counter()
for i in range(100000):
    p = 1 if i % 10 == 0 else random.randint(2, 1000)
    n[p] += 1; print(f"CMS.INCRBY views page:{p} 1")
open("/dev/stderr", "w").write(f"exact counts: page:1 {n[1]}, page:2 {n[2]}, page:999 {n[999]}, page:5000 {n[5000]}\n")
PY
r CMS.QUERY views page:1 page:2 page:999 page:5000
r CMS.INFO views
echo "== cuckoo filter: like Bloom, but an item can be deleted"
r CF.RESERVE users 100000
python3 - <<'PY' | py
for i in range(50000): print(f"CF.ADD users user:{i}")
PY
r CF.EXISTS users user:42
r CF.DEL users user:42
r CF.EXISTS users user:42
echo "   false positives among 10,000 users never added:"
python3 - <<'PY' | docker exec -i $C redis-cli | grep -c '^1$' || true
for i in range(50000, 60000): print(f"CF.EXISTS users user:{i}")
PY
r CF.INFO users
echo "== t-digest: 100,000 latencies, mostly 1-20 ms with a slow tail"
r TDIGEST.CREATE lat COMPRESSION 100
python3 - <<'PY' | py
import random; random.seed(2)
vals = [random.uniform(1, 20) if random.random() < 0.99 else random.uniform(200, 2000) for _ in range(100000)]
for i in range(0, len(vals), 1000):
    print("TDIGEST.ADD lat " + " ".join(f"{v:.3f}" for v in vals[i:i+1000]))
open("/dev/stderr", "w").write("exact p50 %.2f p99 %.2f p99.9 %.2f\n" % tuple(sorted(vals)[int(len(vals) * q)] for q in (0.5, 0.99, 0.999)))
PY
r TDIGEST.QUANTILE lat 0.5 0.99 0.999
r TDIGEST.CDF lat 20 200
echo "== memory per structure"
for k in views users lat; do echo "   $k: $(docker exec $C redis-cli MEMORY USAGE $k) bytes"; done
docker rm -f $C >/dev/null
