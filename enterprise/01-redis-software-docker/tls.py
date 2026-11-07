"""Redis Software single node, two more things: the modules the cluster ships (is RedisGears there, which the
old RDI write-behind needs?), and a database endpoint with TLS (one-way: server certificate, no client cert).
Run after the cluster is bootstrapped (README). usage: ../../cloud/01-free-database/.venv/bin/python tls.py
"""
import base64
import json
import os
import ssl
import tempfile
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


print("== modules shipped with the cluster (GET /v1/modules)")
s, mods = api("GET", "/v1/modules")
for m in sorted(mods, key=lambda m: m["module_name"]):
    print(f"   {m['module_name']:14} {m.get('semantic_version')}")
print("   RedisGears present:", any("gears" in m["module_name"].lower() for m in mods))

print("== a database with TLS on its endpoint")
s, d = api("POST", "/v1/bdbs", {"name": "db-tls", "memory_size": 100 * 2**20, "port": 12005,
                                "tls_mode": "enabled", "enforce_client_authentication": "disabled"})
print("   create:", s, (d or {}).get("error_code", ""))
uid = d["uid"]
while True:
    s, info = api("GET", f"/v1/bdbs/{uid}")
    if info.get("status") == "active" and not info.get("action_uid"):
        break
    time.sleep(1)
print(f"   tls_mode {info.get('tls_mode')}, enforce_client_authentication {info.get('enforce_client_authentication')}, port {info['endpoints'][0]['port']}")
s, certs = api("GET", "/v1/cluster/certificates")
ca = tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False); ca.write(certs["proxy_cert"]); ca.close()
print("   proxy certificate from GET /v1/cluster/certificates:", certs["proxy_cert"].splitlines()[0], f"({len(certs['proxy_cert'])} bytes)")
for label, kw in (("plain TCP", {}),
                  ("TLS, proxy cert as CA, hostname not checked", {"ssl": True, "ssl_ca_certs": ca.name, "ssl_check_hostname": False}),
                  ("TLS, no CA given (system store)", {"ssl": True, "ssl_check_hostname": False})):
    try:
        r = redis.Redis(port=12005, socket_timeout=3, **kw)
        r.set("k", "v"); print(f"   {label:46} -> SET ok, GET {r.get('k')!r}")
    except Exception as e:
        print(f"   {label:46} -> {type(e).__name__}: {str(e)[:90]}")
r = redis.Redis(port=12005, ssl=True, ssl_ca_certs=ca.name, ssl_check_hostname=False)
t = [time.perf_counter()] + [(r.ping(), time.perf_counter())[1] for _ in range(500)]
print(f"   500 PINGs over TLS on one connection: {1000 * (t[-1] - t[0]) / 500:.3f} ms each")
api("DELETE", f"/v1/bdbs/{uid}"); os.unlink(ca.name)
print("   db-tls deleted")
