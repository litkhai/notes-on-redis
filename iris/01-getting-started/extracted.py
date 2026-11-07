"""After a conversation, wait for background extraction and recall what it produced.
usage: .venv/bin/python extracted.py [seconds-to-wait]
"""
import os
import sys
import time
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip())
from redis_iris.agent_memory import AgentMemory, AgentMemorySettings  # noqa: E402

mem = AgentMemory(AgentMemorySettings.from_env(), assistant_id="notes-on-redis-lab")
wait = int(sys.argv[1]) if len(sys.argv) > 1 else 90
for t in range(0, wait + 1, 30):
    r = mem.recall("Redis Cloud plan, region and TLS", owner="cust-1042", limit=10)
    print(f"t+{t:3d}s: {len(r.memories)} memories")
    for m in r.memories:
        print(f"   [{m.memory_type}] {m.text}")
    if t < wait:
        time.sleep(30)
