"""Failover inside Redis Cluster: kill a primary while a cluster client writes, time the outage.
Run after run.sh has created the cluster. The host reaches the compose network's fixed addresses directly.
usage: ../../cloud/01-free-database/.venv/bin/python failover.py [cluster-node-timeout-ms]
"""
import subprocess
import sys
import threading
import time

from redis.cluster import RedisCluster

TIMEOUT_MS = int(sys.argv[1]) if len(sys.argv) > 1 else 15000
NODES = {f"10.231.78.1{i}": f"nor-cl-node{i}" for i in range(1, 7)}


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


def cli(container, *a):
    return sh("docker", "exec", container, "redis-cli", *a).strip()


for ip, name in NODES.items():
    cli(name, "CONFIG", "SET", "cluster-node-timeout", str(TIMEOUT_MS))
rc = RedisCluster(host="10.231.78.12", port=6379, socket_timeout=1, socket_connect_timeout=1)


WATCH = "nor-cl-node2"   # the node asked for CLUSTER NODES; switched away from the victim below


def primaries():
    return {n.split()[1].split("@")[0].split(":")[0]: n.split()[0][:8]
            for n in cli(WATCH, "CLUSTER", "NODES").splitlines() if "master" in n and "fail" not in n}


prim = primaries()
victim_ip = sorted(prim)[0]
victim = NODES[victim_ip]
WATCH = next(name for ip, name in NODES.items() if ip not in prim)   # a replica that stays up
other_ip = sorted(prim)[1]
# one key whose slot lives on the victim, one on another primary
def key_on(ip):
    for i in range(100000):
        k = f"k:{i}"
        if rc.get_node_from_key(k).host == ip:
            return k
kv, ko = key_on(victim_ip), key_on(other_ip)
rc.set(kv, 0); rc.set(ko, 0)
print(f"cluster-node-timeout {TIMEOUT_MS} ms; primaries {sorted(prim)}; victim {victim} ({victim_ip}) holds '{kv}', '{ko}' is on {other_ip}")

log = {kv: [], ko: []}
stop = False


def writer(key):
    while not stop:
        t = time.time()
        try:
            v = rc.incr(key); log[key].append((t, True, v))
        except Exception as e:
            log[key].append((t, False, type(e).__name__))
        time.sleep(0.02)


ths = [threading.Thread(target=writer, args=(k,)) for k in (kv, ko)]
for th in ths:
    th.start()
time.sleep(3)
t_kill = time.time()
sh("docker", "kill", victim)
print(f"killed {victim} (SIGKILL)")
state_log = []
promoted = None
while time.time() - t_kill < 90:
    p = primaries()
    st = cli(WATCH, "CLUSTER", "INFO").split("cluster_state:")[1].split()[0]
    if not state_log or state_log[-1][1] != st:
        state_log.append((time.time() - t_kill, st))
    if victim_ip not in p and len(p) == 3:
        promoted = time.time() - t_kill; break
    time.sleep(0.2)
time.sleep(4)
stop = True
for th in ths:
    th.join()


def outage(rows):
    worst, start = 0.0, None
    for t, ok, _ in rows:
        if not ok and start is None:
            start = t
        elif ok and start is not None:
            worst = max(worst, t - start); start = None
    return worst, sum(1 for r in rows if not r[1]), sorted({r[2] for r in rows if not r[1]})


for key, label in ((kv, "key on the killed primary"), (ko, "key on another primary")):
    worst, fails, kinds = outage(log[key])
    ok = [r[2] for r in log[key] if r[1]]
    print(f"{label:28} writes {len(log[key])}, failed {fails}, longest outage {worst:.1f} s, errors {kinds or 'none'}")
    print(f"{'':28} last value {ok[-1]}, successful writes {len(ok)}, increments lost {len(ok) - ok[-1]}")
print("cluster_state seen from a replica:", ", ".join(f"{st} at {t:.1f} s" for t, st in state_log))
print(f"replica promoted (seen in CLUSTER NODES) {promoted:.1f} s after the kill" if promoted else "no promotion seen within 90 s")
sh("docker", "start", victim)
t_start = time.time()
while time.time() - t_start < 60 and ("fail" in cli(WATCH, "CLUSTER", "NODES")
                                      or cli(WATCH, "CLUSTER", "NODES").count("master") != 3):
    time.sleep(0.5)
print(f"after restarting the old primary ({time.time() - t_start:.1f} s until it rejoined as a replica):")
print("\n".join("   " + " ".join(l.split()[1:3]) for l in cli(WATCH, "CLUSTER", "NODES").splitlines()))
