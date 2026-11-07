"""Redis 8.10.3 vs Valkey 9.1.3 (core and bundle) on one host, defaults only.

usage: .venv/bin/python compare.py [versions|commands|probes|memory]   (no argument = all)
Targets come from compose.yaml: 16381 Redis, 16382 Valkey, 16383 Valkey bundle.
"""
import sys

import redis

T = {"redis-8.10.3": 16381, "valkey-9.1.3": 16382, "valkey-bundle-9.1": 16383}
C = {k: redis.Redis(port=p, decode_responses=True) for k, p in T.items()}


def versions():
    for k, r in C.items():
        s = r.info("server")
        print(f"{k}: redis_version={s.get('redis_version')} valkey_version={s.get('valkey_version', '-')} "
              f"modules={','.join(sorted(m['name'] for m in r.module_list())) or '-'}")


def commands():
    names = {k: {c.lower() for c in r.command_list()} for k, r in C.items()}
    base = names["redis-8.10.3"]
    print("top-level command count:", {k: len(v) for k, v in names.items()})
    for k in ("valkey-9.1.3", "valkey-bundle-9.1"):
        only_r, only_v = sorted(base - names[k]), sorted(names[k] - base)
        print(f"\nonly in redis vs {k} ({len(only_r)}): {' '.join(only_r)}")
        print(f"only in {k} vs redis ({len(only_v)}): {' '.join(only_v)}")


PROBES = [
    ("hash field TTL", [("HSET", "h", "a", "1", "b", "2"), ("HEXPIRE", "h", "60", "FIELDS", "1", "a"), ("HTTL", "h", "FIELDS", "2", "a", "b")]),
    ("HSETEX / HGETEX", [("HSETEX", "h2", "EX", "60", "FIELDS", "1", "f", "v"), ("HGETEX", "h2", "PERSIST", "FIELDS", "1", "f")]),
    ("JSON", [("JSON.SET", "j", "$", '{"a":[1,2]}'), ("JSON.ARRAPPEND", "j", "$.a", "3"), ("JSON.GET", "j", "$.a")]),
    ("Bloom", [("BF.ADD", "bf", "x"), ("BF.EXISTS", "bf", "y")]),
    ("Top-k", [("TOPK.RESERVE", "tk", "2")]),
    ("Time series", [("TS.CREATE", "ts"), ("TS.ADD", "ts", "1", "1.5")]),
    ("Search: text + numeric", [("HSET", "it:1", "name", "lamp", "price", "30"),
                                ("FT.CREATE", "ix", "ON", "HASH", "PREFIX", "1", "it:", "SCHEMA", "name", "TEXT", "price", "NUMERIC"),
                                ("FT.SEARCH", "ix", "@price:[0 50]")]),
    ("Search: vector", [("FT.CREATE", "vx", "ON", "HASH", "PREFIX", "1", "v:", "SCHEMA", "e", "VECTOR", "HNSW", "6", "TYPE", "FLOAT32", "DIM", "2", "DISTANCE_METRIC", "L2")]),
    ("Vector set", [("VADD", "vs", "VALUES", "2", "0.1", "0.2", "a")]),
    ("Array (8.8)", [("ARSET", "ar", "0", "x")]),
    ("Lua EVAL", [("EVAL", "return 1", "0")]),
    ("Functions", [("FUNCTION", "LIST")]),
]


def probes():
    for k, r in C.items():
        r.flushall()
    width = max(len(p[0]) for p in PROBES)
    print(f"{'probe':<{width}}  " + "  ".join(f"{k:<26}" for k in C))
    for name, cmds in PROBES:
        cells = []
        for k, r in C.items():
            try:
                out = None
                for c in cmds:
                    out = r.execute_command(*c)
                cells.append(("ok " + str(out)[:22]).ljust(26))
            except redis.ResponseError as e:
                cells.append(("ERR " + str(e)[:21]).ljust(26))
        print(f"{name:<{width}}  " + "  ".join(cells))


def memory(n=1_000_000):
    for k, r in C.items():
        r.flushall()
        before = r.info("memory")["used_memory"]
        p = r.pipeline(transaction=False)
        for i in range(n):
            p.set(f"key:{i:07d}", f"val:{i:07d}")
            if i % 10_000 == 9_999:
                p.execute()
        p.execute()
        m = r.info("memory")
        added = m["used_memory"] - before
        print(f"{k}: {r.dbsize()} keys, used_memory +{added / 1e6:.1f} MB = {added / n:.1f} B/key "
              f"(dataset {m.get('used_memory_dataset', 0) / 1e6:.1f} MB, allocator {m.get('mem_allocator')})")
        r.flushall()


if __name__ == "__main__":
    steps = {"versions": versions, "commands": commands, "probes": probes, "memory": memory}
    for s in sys.argv[1:] or steps:
        print(f"\n### {s}")
        steps[s]()
