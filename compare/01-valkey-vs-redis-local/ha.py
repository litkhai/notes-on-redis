"""Redis 8.10.3 and Valkey 9.1.3 side by side on the deep-dive's availability tests, same scripts for both:
cluster failover (6 nodes, cluster-node-timeout 3 s, a primary killed under writes), Sentinel failover
(1 primary, 2 replicas, 3 Sentinels, down-after 3 s), and AOF (appendfsync everysec write rate, restart time).
usage: ../../cloud/01-free-database/.venv/bin/python ha.py   (creates and removes its own containers and networks)
"""
import subprocess
import threading
import time

import redis
from redis.cluster import RedisCluster

IMAGES = {"redis": ("redis:8.10.3", "redis"), "valkey": ("valkey/valkey:9.1.3", "valkey")}


def sh(*a, check=False):
    return subprocess.run(a, capture_output=True, text=True, check=check).stdout.strip()


def net(name, subnet):
    sh("docker", "network", "rm", name); sh("docker", "network", "create", "--subnet", subnet, name, check=True)


def cleanup(prefix, network):
    ids = sh("docker", "ps", "-aq", "--filter", f"name={prefix}").split()
    if ids:
        sh("docker", "rm", "-f", *ids)
    sh("docker", "network", "rm", network)


def outage(rows, t_kill):
    worst, start = 0.0, None
    for t, ok, _ in rows:
        if t < t_kill:
            continue
        if not ok and start is None:
            start = t
        elif ok and start is not None:
            worst = max(worst, t - start); start = None
    return worst


def cluster(kind, image, cli, third):
    prefix, network = f"nor-ha-{kind}-cl", f"nor-ha-{kind}-cl"
    cleanup(prefix, network); net(network, f"10.231.{third}.0/24")
    ips = [f"10.231.{third}.{10 + i}" for i in range(1, 7)]
    for i, ip in enumerate(ips, 1):
        sh("docker", "run", "-d", "--name", f"{prefix}{i}", "--network", network, "--ip", ip, image, f"{cli}-server",
           "--cluster-enabled", "yes", "--cluster-node-timeout", "3000", "--cluster-announce-ip", ip, "--save", "", "--appendonly", "no", check=True)
    time.sleep(2)
    sh("docker", "exec", f"{prefix}1", "sh", "-c", f"yes yes | {cli}-cli --cluster create {' '.join(ip + ':6379' for ip in ips)} --cluster-replicas 1")
    for _ in range(60):
        if "cluster_state:ok" in sh("docker", "exec", f"{prefix}1", f"{cli}-cli", "CLUSTER", "INFO"):
            break
        time.sleep(0.5)
    rc = RedisCluster(host=ips[1], port=6379, socket_timeout=1, socket_connect_timeout=1)
    prim = sorted(l.split()[1].split(":")[0] for l in sh("docker", "exec", f"{prefix}1", f"{cli}-cli", "CLUSTER", "NODES").splitlines() if "master" in l)
    victim_ip = prim[0]; victim = f"{prefix}{ips.index(victim_ip) + 1}"
    watch = f"{prefix}{ips.index(next(ip for ip in ips if ip not in prim)) + 1}"
    key = next(f"k:{i}" for i in range(100000) if rc.get_node_from_key(f"k:{i}").host == victim_ip)
    rc.set(key, 0); rows, stop = [], False

    def writer():
        while not stop:
            t = time.time()
            try:
                rc.incr(key); rows.append((t, True, time.time() - t))
            except Exception:
                rows.append((t, False, time.time() - t))
            time.sleep(0.02)
    th = threading.Thread(target=writer); th.start(); time.sleep(2)
    t_kill = time.time(); sh("docker", "kill", victim)
    promoted = None
    while time.time() - t_kill < 60:
        nodes = sh("docker", "exec", watch, f"{cli}-cli", "CLUSTER", "NODES")
        if victim_ip not in [l.split()[1].split(":")[0] for l in nodes.splitlines() if "master" in l and "fail" not in l]:
            promoted = time.time() - t_kill; break
        time.sleep(0.1)
    time.sleep(3); stop = True; th.join()
    cleanup(prefix, network)
    slowest = max((r for r in rows if r[0] >= t_kill - 1), key=lambda r: r[2])
    return promoted, outage(rows, t_kill), slowest[2], sum(1 for r in rows if not r[1])


def sentinel(kind, image, cli, third):
    prefix, network = f"nor-ha-{kind}-sn", f"nor-ha-{kind}-sn"
    cleanup(prefix, network); net(network, f"10.231.{third}.0/24")
    p = f"10.231.{third}.10"
    sh("docker", "run", "-d", "--name", f"{prefix}-p", "--network", network, "--ip", p, image, f"{cli}-server", "--save", "", check=True)
    for i in (1, 2):
        sh("docker", "run", "-d", "--name", f"{prefix}-r{i}", "--network", network, "--ip", f"10.231.{third}.1{i}", image,
           f"{cli}-server", "--save", "", "--replicaof", p, "6379", check=True)
    conf = f"port 26379\\nsentinel monitor m {p} 6379 2\\nsentinel down-after-milliseconds m 3000\\nsentinel failover-timeout m 10000\\n"
    for i in (1, 2, 3):
        sh("docker", "run", "-d", "--name", f"{prefix}-s{i}", "--network", network, "--ip", f"10.231.{third}.2{i}", image,
           "sh", "-c", f"printf '{conf}' > /tmp/s.conf && exec {cli}-server /tmp/s.conf --sentinel", check=True)
    time.sleep(8)
    s1 = f"{prefix}-s1"
    t_kill = time.time(); sh("docker", "kill", f"{prefix}-p")
    new = None
    while time.time() - t_kill < 60:
        addr = sh("docker", "exec", s1, f"{cli}-cli", "-p", "26379", "SENTINEL", "get-master-addr-by-name", "m").splitlines()
        if addr and addr[0] != p:
            new = time.time() - t_kill; break
        time.sleep(0.1)
    cleanup(prefix, network)
    return new


def aof(kind, image, cli):
    name = f"nor-ha-{kind}-aof"
    sh("docker", "rm", "-f", name)
    sh("docker", "run", "-d", "--name", name, image, f"{cli}-server", "--appendonly", "yes", "--appendfsync", "everysec", "--save", "", check=True)
    time.sleep(2)
    out = sh("docker", "exec", name, f"{cli}-benchmark", "-q", "-t", "set", "-n", "1000000", "-r", "1000000", "-d", "100", "-c", "50", "-P", "16")
    rate = [l for l in out.replace("\r", "\n").splitlines() if "requests per second" in l][-1].split()[1]
    keys = sh("docker", "exec", name, f"{cli}-cli", "DBSIZE")
    t0 = time.time(); sh("docker", "restart", name)
    while sh("docker", "exec", name, f"{cli}-cli", "PING") != "PONG":
        time.sleep(0.05)
    while "loading:0" not in sh("docker", "exec", name, f"{cli}-cli", "INFO", "persistence"):
        time.sleep(0.05)
    restart = time.time() - t0
    keys_after = sh("docker", "exec", name, f"{cli}-cli", "DBSIZE")
    sh("docker", "rm", "-f", name)
    return rate, keys, restart, keys_after


for third, (kind, (image, cli)) in zip((80, 81), IMAGES.items()):
    v = next(x.split("=")[1] for x in sh("docker", "run", "--rm", image, f"{cli}-server", "--version").split() if x.startswith("v="))
    print(f"== {kind} ({image}, {v})")
    promoted, out_, slowest, failed = cluster(kind, image, cli, third)
    print(f"   cluster, node timeout 3 s: replica promoted after {promoted:.1f} s; failed writes {failed}, longest failing stretch {out_:.1f} s, slowest single write {slowest:.1f} s")
    print(f"   Sentinel, down-after 3 s: new master named after {sentinel(kind, image, cli, third + 2):.1f} s")
    rate, keys, restart, keys_after = aof(kind, image, cli)
    print(f"   AOF everysec: {rate} SET/s (pipeline 16); {keys} keys; restart to loaded {restart:.1f} s; keys after restart {keys_after}")
