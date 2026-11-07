"""Smoke test: PING, a round trip of SET/GET, and the server version, against the local
container and the Redis Cloud free database (URL from .env). Never prints the URL.
usage: .venv/bin/python smoke.py
"""
import os
from pathlib import Path

import redis

HERE = Path(__file__).resolve().parent
env = dict(l.split("=", 1) for l in (HERE / ".env").read_text().splitlines() if "=" in l)
targets = {"local": "redis://127.0.0.1:16379", "cloud-free": env["REDIS_URL"].strip()}
print("redis-py", redis.__version__)
for name, url in targets.items():
    r = redis.Redis.from_url(url, socket_timeout=10)
    r.set("smoke:py", "ok", ex=60)
    print(f"{name}: PING={r.ping()} GET={r.get('smoke:py').decode()} version={r.info('server')['redis_version']}")
