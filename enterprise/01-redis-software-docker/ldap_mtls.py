"""Redis Software single node, access control: LDAP users for a database (role-based LDAP against an
OpenLDAP container, see README) and mutual TLS (the database requires a client certificate).
Run after the cluster is bootstrapped and nor-ldap is seeded. usage: ../../cloud/01-free-database/.venv/bin/python ldap_mtls.py
"""
import base64
import json
import os
import ssl
import subprocess
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
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": AUTH, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
            raw = r.read(); return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def wait_active(uid):
    while True:
        s, d = api("GET", f"/v1/bdbs/{uid}")
        if d and d.get("status") == "active" and not d.get("action_uid"):
            return d
        time.sleep(1)


def try_user(port, user, pw, label):
    try:
        r = redis.Redis(port=port, username=user, password=pw, socket_timeout=5)
        g = r.get("report:1")
        try:
            r.set("report:1", "changed"); w = "SET allowed"
        except redis.ResponseError as e:
            w = f"SET refused: {str(e)[:60]}"
        print(f"   {label:34} -> GET {g!r}; {w}")
    except Exception as e:
        print(f"   {label:34} -> {type(e).__name__}: {str(e)[:80]}")


print("== role-based LDAP for a database")
s, _ = api("PUT", "/v1/cluster/ldap", {
    "uris": ["ldap://nor-ldap:389"], "bind_dn": "cn=admin,dc=example,dc=org", "bind_pass": "ldap-lab-pw",
    "user_dn_query": {"base": "ou=users,dc=example,dc=org", "filter": "(cn=%u)", "scope": "subtree"},
    "dn_group_query": {"base": "ou=groups,dc=example,dc=org", "filter": "(member=%D)", "scope": "subtree"},
    "data_plane": True, "control_plane": False})
print("   PUT /v1/cluster/ldap ->", s)
s, acl = api("POST", "/v1/redis_acls", {"name": "lab-read", "acl": "+@read ~*"}); print("   redis ACL lab-read ->", s)
s, role = api("POST", "/v1/roles", {"name": "lab-reader", "management": "none"}); print("   role lab-reader ->", s)
s, m = api("POST", "/v1/ldap_mappings", {"name": "redis-readers", "dn": "cn=redis-readers,ou=groups,dc=example,dc=org", "role_uids": [role["uid"]]})
print("   LDAP mapping cn=redis-readers -> role lab-reader ->", s)
s, db = api("POST", "/v1/bdbs", {"name": "db-ldap", "memory_size": 100 * 2**20, "port": 12006,
                                 "roles_permissions": [{"role_uid": role["uid"], "redis_acl_uid": acl["uid"]}]})
print("   database db-ldap ->", s, (db or {}).get("error_code", "")); wait_active(db["uid"])
s, info = api("GET", f"/v1/bdbs/{db['uid']}")
admin_pw = info.get("authentication_redis_pass", "")
redis.Redis(port=12006, password=admin_pw or None).set("report:1", "q3")
try_user(12006, "alice", "alice-pw", "alice (in cn=redis-readers)")
try_user(12006, "alice", "wrong", "alice, wrong password")
try_user(12006, "bob", "bob-pw", "bob (no mapped group)")

print("\n== mutual TLS: the database requires a client certificate")
d = Path(tempfile.mkdtemp())
sh = lambda *a: subprocess.run(a, cwd=d, capture_output=True, check=True)
sh("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=lab-client-ca", "-keyout", "ca.key", "-out", "ca.pem")
sh("openssl", "req", "-newkey", "rsa:2048", "-nodes", "-subj", "/CN=lab-app", "-keyout", "client.key", "-out", "client.csr")
sh("openssl", "x509", "-req", "-in", "client.csr", "-CA", "ca.pem", "-CAkey", "ca.key", "-CAcreateserial", "-days", "1", "-out", "client.pem")
sh("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=someone-else", "-keyout", "other.key", "-out", "other.pem")
s, db2 = api("POST", "/v1/bdbs", {"name": "db-mtls", "memory_size": 100 * 2**20, "port": 12007, "tls_mode": "enabled",
                                  "enforce_client_authentication": "enabled",
                                  "authentication_ssl_client_certs": [{"client_cert": (d / "client.pem").read_text()}]})
print("   database db-mtls ->", s, (db2 or {}).get("error_code", "")); info2 = wait_active(db2["uid"])
print(f"   tls_mode {info2['tls_mode']}, enforce_client_authentication {info2['enforce_client_authentication']}")
proxy = d / "proxy.pem"; proxy.write_text(api("GET", "/v1/cluster/certificates")[1]["proxy_cert"])
for label, kw in (("TLS, no client certificate", {}),
                  ("TLS, a certificate the database does not know", {"ssl_certfile": str(d / "other.pem"), "ssl_keyfile": str(d / "other.key")}),
                  ("TLS, the registered client certificate", {"ssl_certfile": str(d / "client.pem"), "ssl_keyfile": str(d / "client.key")})):
    try:
        r = redis.Redis(port=12007, ssl=True, ssl_ca_certs=str(proxy), ssl_check_hostname=False, socket_timeout=5, **kw)
        r.set("k", "v"); print(f"   {label:46} -> SET ok, GET {r.get('k')!r}")
    except Exception as e:
        print(f"   {label:46} -> {type(e).__name__}: {str(e)[:80]}")
for uid in (db["uid"], db2["uid"]):
    api("DELETE", f"/v1/bdbs/{uid}")
print("\nboth databases deleted")
