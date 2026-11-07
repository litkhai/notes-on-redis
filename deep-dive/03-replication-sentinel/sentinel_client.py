"""A redis-py Sentinel client across a failover: it asks the Sentinels for the master, writes every
20 ms, and the master is killed. Run with compose.yaml up; the host reaches the fixed addresses directly.
usage: ../../cloud/01-free-database/.venv/bin/python sentinel_client.py
"""
import subprocess
import threading
import time

import redis
from redis.sentinel import Sentinel

SENTINELS = [("10.231.77.21", 26379), ("10.231.77.22", 26379), ("10.231.77.23", 26379)]
NAMES = {"10.231.77.10": "nor-repl-primary", "10.231.77.11": "nor-repl-replica1", "10.231.77.12": "nor-repl-replica2"}
s = Sentinel(SENTINELS, socket_timeout=0.5)
m = s.master_for("mymaster", socket_timeout=0.5, socket_connect_timeout=0.5)
before = s.discover_master("mymaster")
print("master from the Sentinels:", before, "=", NAMES[before[0]])
m.set("c", 0)
log, stop = [], False


def writer():
    while not stop:
        t = time.time()
        try:
            log.append((t, True, m.incr("c"), m.connection_pool.get_master_address()[0]))
        except Exception as e:
            log.append((t, False, type(e).__name__, None))
        time.sleep(0.02)


th = threading.Thread(target=writer); th.start()
time.sleep(3)
t_kill = time.time()
subprocess.run(["docker", "kill", NAMES[before[0]]], capture_output=True)
print(f"killed {NAMES[before[0]]} (SIGKILL)")
while time.time() - t_kill < 60:
    try:
        now = s.discover_master("mymaster")
        if now != before:
            print(f"Sentinels report the new master {now} = {NAMES[now[0]]} after {time.time() - t_kill:.1f} s"); break
    except Exception:
        pass
    time.sleep(0.2)
time.sleep(3)
stop = True; th.join()
bad = [r for r in log if not r[1]]
first_ok_after = next((r for r in log if r[1] and r[0] > t_kill and r[3] != before[0]), None)
ok = [r[2] for r in log if r[1]]
print(f"writes {len(log)}, failed {len(bad)}, errors {sorted({r[2] for r in bad})}")
print(f"first successful write on the new master {first_ok_after[0] - t_kill:.1f} s after the kill" if first_ok_after else "no write reached a new master")
print(f"last value {ok[-1]}, successful writes {len(ok)}, increments lost {len(ok) - ok[-1]}")
subprocess.run(["docker", "start", NAMES[before[0]]], capture_output=True)
t_start, seen = time.time(), []
r = redis.Redis(host=before[0], socket_timeout=1)
while time.time() - t_start < 60:
    try:
        rep = r.info("replication"); st = (rep["role"], rep.get("master_host"))
    except Exception as e:
        st = (type(e).__name__, None)
    if not seen or seen[-1][1] != st:
        seen.append((time.time() - t_start, st))
    if st[0] == "slave":
        break
    time.sleep(0.2)
print(f"restarted {NAMES[before[0]]}; its role over time: " + ", ".join(f"{st[0]}{'->' + st[1] if st[1] else ''} at {t:.1f} s" for t, st in seen))
