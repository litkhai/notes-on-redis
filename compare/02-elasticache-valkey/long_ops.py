"""60-second sustained load: does the service throttle after a while? usage: .venv/bin/python long_ops.py [seconds]"""
import sys, time, threading
from limits import client, _hammer, PREFIX
secs = int(sys.argv[1]) if len(sys.argv) > 1 else 60
r = client()
keys = [f"{PREFIX}ops:{i}" for i in range(8)]
# one GET per key: a cluster-mode endpoint (ElastiCache Serverless) refuses a cross-slot MGET
read = lambda: sum(int(r.get(k) or 0) for k in keys)
th = threading.Thread(target=lambda: print("errors:", _hammer(8, secs, 100)[2] or "none"))
prev = read(); th.start(); t0 = time.perf_counter()
while th.is_alive():
    time.sleep(5)
    cur = read(); print(f"t={time.perf_counter() - t0:4.0f}s  {(cur - prev) / 5:8.0f} INCR/s"); prev = cur
th.join()
