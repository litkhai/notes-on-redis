"""Eviction policies side by side on Redis 8.10.3 with maxmemory 16 MB.
Three groups of 5,000 keys: read-hot (read often, never rewritten), write-hot (rewritten often,
never read), cold (left alone). Then 30,000 new keys force eviction; count what survived.
Also HOTKEYS (8.6) and INFO keysizes.
usage: ../../cloud/01-free-database/.venv/bin/python lab.py   (starts and removes container nor-dd-ev)
"""
import subprocess
import time

import redis

IMG = "redis:8.10.3"; C = "nor-dd-ev"; PORT = 16390
VAL = "x" * 500


def start(policy):
    subprocess.run(["docker", "rm", "-f", C], capture_output=True)
    subprocess.run(["docker", "run", "-d", "--name", C, "-p", f"127.0.0.1:{PORT}:6379", IMG, "redis-server", "--save", "",
                    "--appendonly", "no", "--maxmemory", "16mb", "--maxmemory-policy", policy], check=True, capture_output=True)
    r = redis.Redis(port=PORT)
    for _ in range(50):
        try:
            r.ping(); return r
        except redis.ConnectionError:
            time.sleep(0.2)


def load(r, prefix, n):
    p = r.pipeline(transaction=False)
    for i in range(n):
        p.set(f"{prefix}:{i}", VAL)
        if i % 1000 == 999:
            p.execute()
    p.execute()


def run(policy):
    r = start(policy)
    for g in ("read", "write", "cold"):
        load(r, g, 5000)
    for rnd in range(5):                              # make the groups different in access pattern
        p = r.pipeline(transaction=False)
        for i in range(5000):
            p.get(f"read:{i}")
            p.set(f"write:{i}", VAL)
        p.execute()
        time.sleep(0.3)
    before = r.info("memory")["used_memory"]
    try:
        load(r, "new", 30000)
        err = None
    except redis.ResponseError as e:
        err = str(e).split("caused error: ")[-1][:70]
    alive = {g: sum(1 for v in r.mget([f"{g}:{i}" for i in range(5000)]) if v) for g in ("read", "write", "cold", "new")}
    ev = r.info("stats")["evicted_keys"]
    print(f"{policy:16} survived read-hot {alive['read']:5} write-hot {alive['write']:5} cold {alive['cold']:5} "
          f"new(first 5000) {alive['new']:5} evicted {ev:6} {('error: ' + err) if err else ''}")
    return r


print("== which keys survive (5,000 per group, then 30,000 new keys into 16 MB)")
for pol in ("noeviction", "allkeys-lru", "allkeys-lfu", "allkeys-lrm", "allkeys-random"):
    run(pol)

print("\n== HOTKEYS (8.6): top keys by CPU while reading a skewed set")
r = start("noeviction"); load(r, "k", 2000)
print("   start:", r.execute_command("HOTKEYS", "START", "METRICS", "1", "CPU", "COUNT", "5"))
for i in range(20000):
    r.get("k:7" if i % 2 == 0 else ("k:42" if i % 3 == 0 else f"k:{i % 2000}"))
print("   get:", r.execute_command("HOTKEYS", "GET"))
r.execute_command("HOTKEYS", "STOP")
print("\n== INFO keysizes")
r.set("big", "y" * 100_000); r.rpush("list", *range(300))
print("  ", {k: v for k, v in r.info("keysizes").items()})
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
