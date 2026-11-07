"""Ten minutes of steady load on the free database from ONE connection (pipeline 100), sampled every 30 s
from a second connection: does the 100 ops/s on the pricing page show up over a longer window?
The Iris services hold most of the 30 connections, so this uses two. Keys are deleted at the end.
usage: .venv/bin/python long_window.py [seconds]
"""
import sys
import threading
import time

from limits import PREFIX, client

secs = int(sys.argv[1]) if len(sys.argv) > 1 else 600
key = f"{PREFIX}win:counter"
sampler, worker = client(), client()
sampler.delete(key)
stop = time.perf_counter() + secs
errors = {}


def work():
    p = worker.pipeline(transaction=False)
    while time.perf_counter() < stop:
        for _ in range(100):
            p.incr(key)
        try:
            p.execute()
        except Exception as e:
            errors[type(e).__name__] = errors.get(type(e).__name__, 0) + 1
            time.sleep(0.5)


print(f"connected clients before: {sampler.info('clients')['connected_clients']} of 30")
th = threading.Thread(target=work); th.start()
t0 = time.perf_counter(); prev = 0; rates = []
while th.is_alive():
    time.sleep(30)
    cur = int(sampler.get(key) or 0); rate = (cur - prev) / 30; prev = cur; rates.append(rate)
    print(f"t={time.perf_counter() - t0:4.0f}s  {rate:8.0f} INCR/s", flush=True)
th.join()
print(f"total {prev:,} INCR in {secs} s; per-sample min {min(rates):,.0f}, max {max(rates):,.0f} INCR/s; errors {errors or 'none'}")
sampler.delete(key)
