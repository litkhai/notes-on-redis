"""Redis Software single node: databases behind the DMC proxy, proxy policies, multi-key commands on a
sharded database, the trial licence's shard limit, and re-sharding with data in place.
usage: ../../cloud/01-free-database/.venv/bin/python lab.py      (RS_USER / RS_PASS in .env)
"""
import base64
import json
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

import redis

HERE = Path(__file__).resolve().parent
ENV = dict(l.split("=", 1) for l in (HERE / ".env").read_text().splitlines() if "=" in l)
API = "https://127.0.0.1:19443"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE   # self-signed lab cert
AUTH = "Basic " + base64.b64encode(f"{ENV['RS_USER']}:{ENV['RS_PASS']}".encode()).decode()


def api(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": AUTH, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
            raw = r.read(); return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def wait_active(uid, label):
    t0 = time.time()
    while True:
        s, d = api("GET", f"/v1/bdbs/{uid}")
        if d and d.get("status") == "active" and not d.get("action_uid"):
            print(f"   {label}: active after {time.time() - t0:.1f} s"); return d
        time.sleep(1)


def show(uid):
    s, d = api("GET", f"/v1/bdbs/{uid}")
    ep = d["endpoints"][0]
    print(f"   bdb {uid} {d['name']}: shards {d['shards_count']}, replication {d['replication']}, proxy_policy {d['proxy_policy']}, "
          f"sharding {d['sharding']}, memory {d['memory_size'] // 2**20} MB, port {ep['port']}, version {d.get('redis_version')}")


print("== licence (read at run time)")
s, lic = api("GET", "/v1/license")
print("  ", {k: lic[k] for k in ("features", "activation_date", "expiration_date", "shards_limit", "expired")})

print("== db-a: one shard, proxy policy single")
s, a = api("POST", "/v1/bdbs", {"name": "db-a", "memory_size": 100 * 2**20, "port": 12000, "proxy_policy": "single"})
print("   create:", s); wait_active(a["uid"], "db-a"); show(a["uid"])

print("== db-b: two shards, proxy policy all-master-shards")
s, b = api("POST", "/v1/bdbs", {"name": "db-b", "memory_size": 200 * 2**20, "port": 12001, "sharding": True, "shards_count": 2,
                                "shard_key_regex": [{"regex": ".*\\{(?<tag>.*)\\}.*"}, {"regex": "(?<tag>.*)"}],
                                "proxy_policy": "all-master-shards"})
print("   create:", s, (b or {}).get("error_code", "")); wait_active(b["uid"], "db-b"); show(b["uid"])

print("== two databases on one node, each its own endpoint")
ra, rb = redis.Redis(port=12000), redis.Redis(port=12001)
ra.set("tenant", "a"); rb.set("tenant", "b")
print("   db-a tenant =", ra.get("tenant"), "| db-b tenant =", rb.get("tenant"))

print("== multi-key commands on the two-shard database (through the DMC proxy)")
p = rb.pipeline(transaction=False)
for i in range(10000):
    p.set(f"k:{i}", i)
p.execute()
print("   dbsize via proxy:", rb.dbsize())
print("   MGET k:1 k:2 k:3 k:4 ->", rb.mget("k:1", "k:2", "k:3", "k:4"))
try:
    print("   MSET across shards ->", rb.mset({"x:1": 1, "x:2": 2}))
except redis.ResponseError as e:
    print("   MSET across shards ->", e)
try:
    print("   MULTI/EXEC across shards ->", rb.pipeline(transaction=True).set("y:1", 1).set("y:2", 2).execute())
except redis.ResponseError as e:
    print("   MULTI/EXEC across shards ->", e)
print("   MULTI/EXEC with a shared hash tag ->", rb.pipeline(transaction=True).set("{u1}:a", 1).set("{u1}:b", 2).execute())

print("== licence limit: db-c with replication (2 more shards; 1 + 2 + 2 = 5 > 4)")
s, c = api("POST", "/v1/bdbs", {"name": "db-c", "memory_size": 100 * 2**20, "port": 12002, "replication": True})
print("   create:", s, json.dumps(c)[:300])

print("== re-shard db-b from 2 to 4 shards with 10,000 keys in place (db-a deleted first to stay within 4)")
s, _ = api("DELETE", f"/v1/bdbs/{a['uid']}"); print("   delete db-a:", s); time.sleep(5)
t0 = time.time()
s, r = api("PUT", f"/v1/bdbs/{b['uid']}", {"shards_count": 4})
print("   reshard request:", s, json.dumps(r)[:200] if s >= 400 else "")
time.sleep(2); wait_active(b["uid"], "db-b after re-shard"); show(b["uid"])
print(f"   keys after re-shard: {rb.dbsize()}, k:4242 = {rb.get('k:4242')}, total {time.time() - t0:.1f} s")

print("== licence limit: db-d with one shard while db-b already uses 4 (limit 4)")
s, dd = api("POST", "/v1/bdbs", {"name": "db-d", "memory_size": 100 * 2**20, "port": 12003})
print("   create:", s, json.dumps(dd)[:300])
s, st = api("GET", "/v1/license"); print("   shards in use:", st.get("ram_shards_in_use"), "of", st.get("shards_limit"))
