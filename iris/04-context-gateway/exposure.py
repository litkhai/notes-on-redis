"""What an agent sees from the Gateway in its current tool-exposure mode (set in the console: Search or Full).
usage: .venv/bin/python exposure.py   (same .env as lab.py)
"""
import os
import time
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k, v.strip())
from redis_iris import ContextGateway  # noqa: E402

gw = ContextGateway.from_env()
t0 = time.perf_counter(); tools = gw.tools(); ms = (time.perf_counter() - t0) * 1000
print(f"tools() in {ms:.0f} ms: {len(tools)} tool(s)")
for t in tools:
    print(f"   {t.name:42} {(t.description or '').splitlines()[0][:70] if t.description else ''}")
