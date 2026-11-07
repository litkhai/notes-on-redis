"""The volatile-* eviction policies and maxmemory-samples on Redis 8.10.3, maxmemory 16 MB.
Groups of 4,000 keys x 500 B: 'persist' (no TTL), 'soon' (TTL 600 s), 'later' (TTL 3600 s, never read),
'hot' (TTL 3600 s, read five times). Then 14,000 new keys with TTL 3600 s; count what survived.
Second part: allkeys-lru with maxmemory-samples 1 / 5 / 10, and how many recently read keys it keeps.
usage: ../../cloud/01-free-database/.venv/bin/python volatile.py   (starts and removes container nor-dd-ev2)
"""
import subprocess
import time

import redis

C, PORT, VAL = "nor-dd-ev2", 16393, "x" * 500


def start(*args):
    subprocess.run(["docker", "rm", "-f", C], capture_output=True)
    subprocess.run(["docker", "run", "-d", "--name", C, "-p", f"127.0.0.1:{PORT}:6379", "redis:8.10.3", "redis-server",
                    "--save", "", "--appendonly", "no", "--maxmemory", "16mb", *args], check=True, capture_output=True)
    r = redis.Redis(port=PORT)
    for _ in range(50):
        try:
            r.ping(); return r
        except redis.ConnectionError:
            time.sleep(0.2)


def load(r, prefix, n, ttl=None):
    p = r.pipeline(transaction=False)
    for i in range(n):
        p.set(f"{prefix}:{i}", VAL, ex=ttl)
        if i % 1000 == 999:
            p.execute()
    p.execute()


def alive(r, prefix, n):
    return sum(1 for v in r.mget([f"{prefix}:{i}" for i in range(n)]) if v)


print("== volatile policies: only keys with a TTL can be evicted (16,000 keys, then 14,000 new with a TTL)")
for pol in ("volatile-lru", "volatile-lfu", "volatile-lrm", "volatile-ttl", "volatile-random"):
    r = start("--maxmemory-policy", pol)
    load(r, "persist", 4000); load(r, "soon", 4000, 600); load(r, "later", 4000, 3600); load(r, "hot", 4000, 3600)
    for _ in range(5):
        p = r.pipeline(transaction=False)
        for i in range(4000):
            p.get(f"hot:{i}")
        p.execute(); time.sleep(0.2)
    err = None
    try:
        load(r, "new", 14000, 3600)
    except redis.ResponseError as e:
        err = str(e).split("caused error: ")[-1][:60]
    a = {g: alive(r, g, 4000) for g in ("persist", "soon", "later", "hot")}
    print(f"{pol:16} persist {a['persist']:4} soon {a['soon']:4} later {a['later']:4} hot {a['hot']:4} "
          f"evicted {r.info('stats')['evicted_keys']:6} {('error: ' + err) if err else ''}")

print("\n== when no key has a TTL, a volatile policy cannot free anything")
r = start("--maxmemory-policy", "volatile-lru")
try:
    load(r, "plain", 40000)
    print("   no error")
except redis.ResponseError as e:
    print(f"   writes refused after {r.dbsize()} keys: {str(e).split('caused error: ')[-1][:70]}")

print("\n== allkeys-lru accuracy by maxmemory-samples: 10,000 old keys, the first 5,000 read again, then 30,000 new")
for samples in (1, 5, 10):
    kept = []
    for rep in range(3):
        r = start("--maxmemory-policy", "allkeys-lru", "--maxmemory-samples", str(samples))
        load(r, "old", 10000)
        time.sleep(1.1)                       # LRU clock resolution is about a second
        p = r.pipeline(transaction=False)
        for i in range(5000):
            p.get(f"old:{i}")
        p.execute(); time.sleep(1.1)
        err = ""
        try:
            load(r, "new", 30000)
        except redis.ResponseError as e:
            err = f" OOM after {r.dbsize()} keys"
        mg = r.mget([f"old:{i}" for i in range(10000)])
        kept.append((sum(1 for v in mg[:5000] if v), sum(1 for v in mg[5000:] if v), err))
    print(f"   samples {samples:2}: recently read kept {[k[0] for k in kept]}, not read kept {[k[1] for k in kept]}"
          f"{'; ' + ','.join(k[2] for k in kept if k[2]) if any(k[2] for k in kept) else ''} (three runs)")
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
