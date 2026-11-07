"""mcp-redis behind the Gateway: what an agent finds and can do to a throwaway local Redis.
usage (from iris/04-context-gateway): .venv/bin/python mcp-redis/lab.py   (Gateway .env as lab.py)
"""
import json
import os
import subprocess
import time
from pathlib import Path

for line in (Path(__file__).resolve().parents[1] / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k, v.strip())
from redis_iris import ContextGateway  # noqa: E402

gw = ContextGateway.from_env()


def timed(label, fn):
    t0 = time.perf_counter(); out = fn(); print(f"{(time.perf_counter() - t0) * 1000:6.0f} ms  {label}"); return out


def text(r):
    return str(getattr(r, "text", None) or getattr(r, "content", r))[:200]


def local(*cmd):
    return subprocess.run(["docker", "exec", "nor-mcp-redis", "redis-cli", *cmd], capture_output=True, text=True).stdout.strip()


names = [t.name for t in gw.tools()]
print("tools the agent sees:", names)
for q in ("read every field of a Redis hash", "delete a Redis key", "run any Redis command"):
    found = timed(f"search({q!r})", lambda: gw.search(q, limit=4))
    print("   ->", [t.name for t in found])
r = timed("call redis-lab__hgetall ticket:1", lambda: gw.call("redis-lab__hgetall", {"name": "ticket:1"}))
print("   ->", text(r))
r = timed("call redis-lab__set note:from-gateway", lambda: gw.call("redis-lab__set", {"key": "note:from-gateway", "value": "written by an agent"}))
print("   ->", text(r), "| local GET:", local("GET", "note:from-gateway"))
r = timed("call redis-lab__delete counter:visits", lambda: gw.call("redis-lab__delete", {"key": "counter:visits"}))
print("   ->", text(r), "| local EXISTS:", local("EXISTS", "counter:visits"))
