"""Network partition in Redis Cluster: cut a primary off the network (docker network disconnect) instead of
killing it. Writes go on both sides: inside the isolated node (docker exec) and through the majority. Then
the node is reconnected and we see which writes survived. Run after run.sh; cluster-node-timeout 5 s here.
usage: ../../cloud/01-free-database/.venv/bin/python partition.py
"""
import subprocess
import threading
import time

from redis.cluster import RedisCluster

NET = "nor-cluster_cl"
NODES = {f"10.231.78.1{i}": f"nor-cl-node{i}" for i in range(1, 7)}
TIMEOUT_MS = 5000


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout.strip()


def cli(c, *a):
    return sh("docker", "exec", c, "redis-cli", *a)


for name in NODES.values():
    cli(name, "CONFIG", "SET", "cluster-node-timeout", str(TIMEOUT_MS))
primaries = sorted(l.split()[1].split(":")[0] for l in cli("nor-cl-node1", "CLUSTER", "NODES").splitlines() if "master" in l and "fail" not in l)
victim_ip = primaries[0]; victim = NODES[victim_ip]
watch = next(n for ip, n in NODES.items() if ip not in primaries)
rc = RedisCluster(host=primaries[1], port=6379, socket_timeout=1, socket_connect_timeout=1)
key = next(f"p:{i}" for i in range(100000) if rc.get_node_from_key(f"p:{i}").host == victim_ip)
rc.set(key, 0)
print(f"cluster-node-timeout {TIMEOUT_MS} ms; victim {victim} ({victim_ip}) owns '{key}'")

minority, majority, stop = [], [], False


def write_minority():
    while not stop:
        t = time.time(); r = cli(victim, "INCR", key)
        minority.append((t, r)); time.sleep(0.25)


def write_majority():
    while not stop:
        t = time.time()
        try:
            majority.append((t, rc.incr(key)))
        except Exception as e:
            majority.append((t, type(e).__name__))
        time.sleep(0.25)


t0 = time.time()
sh("docker", "network", "disconnect", NET, victim)
print(f"0.0 s  {victim} disconnected from {NET}")
ths = [threading.Thread(target=f) for f in (write_minority, write_majority)]
for th in ths:
    th.start()
promoted = None
while time.time() - t0 < 30:
    st = cli(watch, "CLUSTER", "NODES")
    if victim_ip not in [l.split()[1].split(":")[0] for l in st.splitlines() if "master" in l and "fail" not in l] and promoted is None:
        promoted = time.time() - t0; print(f"{promoted:.1f} s  a replica took over (seen from {watch})")
    time.sleep(0.5)
stop = True
for th in ths:
    th.join()


def summary(rows, label):
    ok = [(t - t0, r) for t, r in rows if str(r).lstrip("-").isdigit()]
    bad = [(t - t0, r) for t, r in rows if not str(r).lstrip("-").isdigit()]
    last_ok = max((t for t, _ in ok), default=None)
    first_bad = min((t for t, _ in bad), default=None)
    kinds = sorted({str(r)[:40] for _, r in bad})
    print(f"{label}: {len(ok)} writes accepted" + (f", last at {last_ok:.1f} s" if last_ok is not None else "") +
          f"; {len(bad)} refused" + (f" from {first_bad:.1f} s" if first_bad is not None else "") + f" {kinds}")
    return ok


mi = summary(minority, "isolated old primary (docker exec)")
ma = summary(majority, "majority side (cluster client)  ")
print(f"   highest value on the isolated node: {max((int(r) for _, r in mi), default=None)}; on the majority: {max((int(r) for _, r in ma), default=None)}")
sh("docker", "network", "connect", "--ip", victim_ip, NET, victim)
t1 = time.time()
while time.time() - t1 < 60:
    role = cli(victim, "ROLE").splitlines()[0]
    if role == "slave":
        break
    time.sleep(0.5)
print(f"reconnected; {victim} became a {role} after {time.time() - t1:.1f} s")
time.sleep(2)
print(f"'{key}' through the cluster now: {rc.get(key).decode()} (the isolated node's {len(mi)} writes are gone)" if mi else f"'{key}' now {rc.get(key)}")
