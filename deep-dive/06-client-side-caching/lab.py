"""Client-side caching on Redis 8.10.3: redis-py's built-in cache (default tracking mode) and the
broadcast mode seen on a raw RESP3 connection.
usage: ../../cloud/01-free-database/.venv/bin/python lab.py   (starts and removes container nor-dd-csc)
"""
import socket
import subprocess
import time

import redis
from redis.cache import CacheConfig

IMG = "redis:8.10.3"; C = "nor-dd-csc"; PORT = 16391
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
subprocess.run(["docker", "run", "-d", "--name", C, "-p", f"127.0.0.1:{PORT}:6379", IMG], check=True, capture_output=True)
time.sleep(2)
admin = redis.Redis(port=PORT, decode_responses=True)


def server_gets():
    return admin.info("commandstats").get("cmdstat_get", {}).get("calls", 0)


print("== default mode: redis-py cache (RESP3, CLIENT TRACKING on)")
cached = redis.Redis(port=PORT, protocol=3, cache_config=CacheConfig(), decode_responses=True)
admin.set("user:1:name", "Ann")
g0 = server_gets()
t0 = time.perf_counter(); v1 = cached.get("user:1:name"); t1 = time.perf_counter()
v2 = [cached.get("user:1:name") for _ in range(1000)][-1]; t2 = time.perf_counter()
print(f"   first GET {v1!r} {1000 * (t1 - t0):.2f} ms; next 1000 GETs {v2!r} {1000 * (t2 - t1):.2f} ms in total")
print(f"   GETs that reached the server: {server_gets() - g0}")
admin.set("user:1:name", "Bea")                 # another client changes the key
time.sleep(0.05)
g1 = server_gets(); v3 = cached.get("user:1:name")
print(f"   after another client's SET: {v3!r}; reached the server: {server_gets() - g1}")
info = [c for c in admin.client_list() if "t" in c.get("flags", "")]
print("   tracking clients on the server:", [(c["id"], c["flags"]) for c in info])


def resp(sock):
    sock.settimeout(1.0)
    try:
        return sock.recv(4096).decode(errors="replace")
    except socket.timeout:
        return ""


print("\n== broadcast mode on a raw RESP3 connection: CLIENT TRACKING ON BCAST PREFIX user:")
s = socket.create_connection(("127.0.0.1", PORT))
s.sendall(b"HELLO 3\r\n"); resp(s)
s.sendall(b"CLIENT TRACKING ON BCAST PREFIX user:\r\n"); print("  ", resp(s).strip())
for key in ("user:2:name", "order:9", "user:3:cart"):
    admin.set(key, "v")
    got = resp(s).replace("\r\n", " ").strip()
    print(f"   SET {key:12} -> pushed to the tracking connection: {got or '(nothing)'}")
s.close()
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
