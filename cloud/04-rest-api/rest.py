"""Redis Cloud REST API on the free plan: read the account, the free subscription and its database,
list the Seoul Essentials plans, change a database setting through an asynchronous task and put it back,
and see what the API answers when the free plan's limit is hit.

Prints only fields that identify nothing: no account, subscription or database IDs, names, endpoints,
IP addresses or e-mail. Keys come from .env (gitignored): REDIS_CLOUD_ACCOUNT_KEY, REDIS_CLOUD_USER_KEY.
usage: python3 rest.py        (standard library only)
"""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k, v.strip())
BASE = "https://api.redislabs.com/v1"
HEAD = {"x-api-key": os.environ["REDIS_CLOUD_ACCOUNT_KEY"], "x-api-secret-key": os.environ["REDIS_CLOUD_USER_KEY"],
        "accept": "application/json", "content-type": "application/json",
        "User-Agent": "notes-on-redis-lab/1.0"}       # the default Python-urllib agent gets 403


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, headers=HEAD,
                                 data=json.dumps(body).encode() if body is not None else None)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.load(r), time.perf_counter() - t0
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), time.perf_counter() - t0


def wait(task_id):
    """Poll /tasks/{id} until it leaves the queued/processing states. Returns the final task."""
    seen = []
    for _ in range(60):
        _, t, _ = call("GET", f"/tasks/{task_id}")
        if not seen or seen[-1] != t.get("status"):
            seen.append(t.get("status"))
        if t.get("status") not in ("received", "processing-in-progress"):
            return t, seen
        time.sleep(2)
    return t, seen


print("== GET /  (who is calling)")
st, acct, dt = call("GET", "/")
print(f"   HTTP {st} in {dt * 1000:.0f} ms; fields: {sorted(acct['account'])}; key fields: {sorted(acct['account']['key'])}")

print("\n== GET /fixed/subscriptions  (free and Essentials live under /fixed; Pro under /subscriptions)")
st, subs, _ = call("GET", "/fixed/subscriptions")
sub = subs["subscriptions"][0]; sid = sub["id"]
keep = ("status", "size", "sizeMeasurementUnit", "region", "price", "pricePeriod", "maximumDatabases", "availability",
        "connections", "supportDataPersistence", "supportInstantAndDailyBackups", "supportReplication", "supportClustering")
print(f"   HTTP {st}; subscriptions: {len(subs['subscriptions'])}")
print("  ", {k: sub[k] for k in keep})
st, pro, _ = call("GET", "/subscriptions")
print(f"   GET /subscriptions (Pro) -> HTTP {st}, {len(pro.get('subscriptions', []))} subscriptions")

print("\n== GET /fixed/subscriptions/{id}/databases")
st, dbs, _ = call("GET", f"/fixed/subscriptions/{sid}/databases")
db = dbs["subscription"]["databases"][0] if isinstance(dbs["subscription"], dict) else dbs["subscription"][0]["databases"][0]
dbid = db["databaseId"]
keep = ("status", "redisVersionCompliance", "respVersion", "protocol", "planMemoryLimit", "memoryUsedInMb", "dataPersistence",
        "replication", "dataEvictionPolicy", "memoryStorage")
print("  ", {k: db[k] for k in keep})
print("   modules:", [(m["name"], m["version"]) for m in db["modules"]])
print("   security:", {k: db["security"][k] for k in ("enableTls", "defaultUserEnabled")})
alerts = {a["name"]: a["value"] for a in db["alerts"]}
print("   alerts:", alerts)

print("\n== GET /fixed/plans?provider=AWS  (Seoul only)")
st, plans, _ = call("GET", "/fixed/plans?provider=AWS")
seoul = [p for p in plans["plans"] if p["region"] == "ap-northeast-2"]
print(f"   HTTP {st}; {len(plans['plans'])} AWS plans, {len(seoul)} in ap-northeast-2")
for p in sorted(seoul, key=lambda p: (p["size"] if p["sizeMeasurementUnit"] == "GB" else p["size"] / 1024, p["price"])):
    print(f"   {p['size']:>6} {p['sizeMeasurementUnit']}  ${p['price']:>4}/{p['pricePeriod']:<5}  {p['availability']:<16} "
          f"persistence={p['supportDataPersistence']!s:5} backups={p['supportInstantAndDailyBackups']!s:5} replication={p['supportReplication']}")

print("\n== PUT a database setting: the connections alert 80% -> 95%, through a task, then back")
name = next(n for n in alerts if "connection" in n)
for value in (95, alerts[name]):
    # "alerts" replaces the whole list: an alert left out is switched off. Send every alert, change one.
    body = {"alerts": [{"name": n, "value": value if n == name else v} for n, v in alerts.items()]}
    st, task, dt = call("PUT", f"/fixed/subscriptions/{sid}/databases/{dbid}", body)
    print(f"   PUT {name}={value} -> HTTP {st} in {dt * 1000:.0f} ms, task fields {sorted(task)}, status {task.get('status')!r}")
    done, path = wait(task["taskId"])
    print(f"   task states: {' -> '.join(path)}; response: {({k: v for k, v in done.get('response', {}).items() if not k.lower().endswith('resourceid')})}")
    _, now, _ = call("GET", f"/fixed/subscriptions/{sid}/databases/{dbid}")
    print(f"   read back: { {a['name']: a['value'] for a in now['alerts']} }")

print("\n== POST a second database into the free subscription (maximumDatabases is 1)")
st, task, _ = call("POST", f"/fixed/subscriptions/{sid}/databases", {"name": "rest-api-probe"})
print(f"   HTTP {st}, status {task.get('status')!r}")
if "taskId" in task:
    done, path = wait(task["taskId"])
    print(f"   task states: {' -> '.join(path)}; response: {done.get('response')}")
else:
    print("  ", task)
_, dbs, _ = call("GET", f"/fixed/subscriptions/{sid}/databases")
sub2 = dbs["subscription"] if isinstance(dbs["subscription"], dict) else dbs["subscription"][0]
print(f"   databases in the subscription afterwards: {sub2.get('numberOfDatabases', len(sub2['databases']))}")
