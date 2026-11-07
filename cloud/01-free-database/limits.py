"""Probe the Redis Cloud free database limits from a client's point of view.

usage: .venv/bin/python limits.py info|ops|conns|memory|cleanup
REDIS_URL comes from .env next to this file (gitignored). Output never prints the
host or the password.
"""
import os
import sys
import time
import threading
from pathlib import Path

import redis

HERE = Path(__file__).resolve().parent
for line in (HERE / ".env").read_text().splitlines():
    if line.startswith("REDIS_URL="):
        os.environ.setdefault("REDIS_URL", line.split("=", 1)[1].strip())
URL = os.environ["REDIS_URL"]
PREFIX = "lab:limits:"


def client(**kw):
    return redis.Redis.from_url(URL, socket_timeout=10, **kw)


def info():
    r = client()
    s = r.info("server")
    print("redis_version:", s.get("redis_version"))
    print("PING:", r.ping())
    m = r.info("memory")
    print("used_memory_human:", m.get("used_memory_human"))
    print("maxmemory_human:", m.get("maxmemory_human"))
    print("maxmemory_policy:", m.get("maxmemory_policy"))
    try:
        print("CONFIG GET maxclients:", r.config_get("maxclients"))
    except redis.ResponseError as e:
        print("CONFIG GET maxclients -> error:", e)
    c = r.info("clients")
    print("connected_clients:", c.get("connected_clients"))
    t0 = time.perf_counter()
    for _ in range(50):
        r.ping()
    print(f"PING round trip, mean of 50: {(time.perf_counter() - t0) / 50 * 1000:.1f} ms")


def _hammer(n_conns, seconds, pipeline):
    """Run SET/GET as fast as possible on n_conns connections; return ops done and errors."""
    done = [0] * n_conns
    errs = {}
    stop = time.perf_counter() + seconds

    def work(i):
        r = client()
        k = f"{PREFIX}ops:{i}"
        while time.perf_counter() < stop:
            try:
                if pipeline:
                    p = r.pipeline(transaction=False)
                    for _ in range(pipeline):
                        p.incr(k)
                    p.execute()
                    done[i] += pipeline
                else:
                    r.incr(k)
                    done[i] += 1
            except redis.RedisError as e:
                errs[type(e).__name__ + ": " + str(e)[:80]] = errs.get(type(e).__name__ + ": " + str(e)[:80], 0) + 1
                time.sleep(0.05)
        r.close()

    ts = [threading.Thread(target=work, args=(i,)) for i in range(n_conns)]
    t0 = time.perf_counter()
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return sum(done), time.perf_counter() - t0, errs


def ops():
    for n_conns, pipeline in [(1, 0), (8, 0), (1, 100), (8, 100)]:
        total, el, errs = _hammer(n_conns, 15, pipeline)
        print(f"connections={n_conns} pipeline={pipeline or 'off'}: {total} ops in {el:.1f} s = {total / el:.0f} ops/s; errors={errs or 'none'}")
    # per-second profile for the heaviest case, to see whether the cap is smoothed or bursty
    r = client()
    print("per-second, 8 connections, pipeline 100:")
    base = sum(int(r.get(f"{PREFIX}ops:{i}") or 0) for i in range(8))
    stop = time.perf_counter() + 10
    th = threading.Thread(target=_hammer, args=(8, 10, 100))
    th.start()
    prev = base
    while time.perf_counter() < stop:
        time.sleep(1)
        cur = sum(int(r.get(f"{PREFIX}ops:{i}") or 0) for i in range(8))
        print(f"  +{cur - prev} INCR")
        prev = cur
    th.join()


def conns():
    held = []
    for i in range(1, 41):
        r = client()
        try:
            r.ping()
            held.append(r)
        except redis.RedisError as e:
            print(f"connection #{i}: {type(e).__name__}: {e}")
            break
    else:
        print("40 connections opened without error")
    print("connections held by this script:", len(held))
    if held:
        print("server connected_clients:", held[0].info("clients").get("connected_clients"))
    for r in held:
        r.close()


def memory():
    r = client()
    val = b"x" * 10_000
    n = 0
    t0 = time.perf_counter()
    try:
        while True:
            p = r.pipeline(transaction=False)
            for j in range(50):
                p.set(f"{PREFIX}mem:{n + j}", val)
            p.execute()
            n += 50
            if n % 500 == 0:
                print(f"  {n} keys, used_memory_human={r.info('memory').get('used_memory_human')}")
    except redis.RedisError as e:
        print(f"after {n} keys of 10 kB ({time.perf_counter() - t0:.1f} s): {type(e).__name__}: {e}")
    m = r.info("memory")
    print("used_memory_human:", m.get("used_memory_human"), "maxmemory_human:", m.get("maxmemory_human"))
    print("evicted_keys:", r.info("stats").get("evicted_keys"))
    # keys with a TTL can be evicted under volatile-lru; keys without cannot
    try:
        r.set(f"{PREFIX}ttl-probe", val, ex=3600)
        print("SET with EX after OOM: OK")
    except redis.RedisError as e:
        print("SET with EX after OOM:", type(e).__name__, e)


def cleanup():
    r = client()
    n = 0
    for k in r.scan_iter(f"{PREFIX}*", count=1000):
        r.unlink(k)
        n += 1
    print("deleted keys:", n, "dbsize:", r.dbsize())


if __name__ == "__main__":
    {"info": info, "ops": ops, "conns": conns, "memory": memory, "cleanup": cleanup}[sys.argv[1]]()
