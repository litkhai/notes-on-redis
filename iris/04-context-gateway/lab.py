"""Context Gateway: one MCP endpoint over a Context Surface (products in the free database) and a
public MCP server (DeepWiki). Search-mode tool exposure.
usage: .venv/bin/python lab.py
"""
import json
import os
import time
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip())
from redis_iris import ContextGateway  # noqa: E402

gw = ContextGateway.from_env()


def timed(label, fn):
    t0 = time.perf_counter(); out = fn(); print(f"{(time.perf_counter() - t0) * 1000:6.0f} ms  {label}"); return out


tools = timed("tools()", gw.tools)
print("tools the agent sees:", [t.name for t in tools])
for q in ("black lamps under 100 dollars", "documentation of a GitHub repository"):
    found = timed(f"search({q!r})", lambda: gw.search(q, limit=3))
    print("   ->", [t.name for t in found])
f = next(t for t in gw.search("filter products by category colour price", limit=5) if t.name.endswith("filter_product"))
print("filter_product input schema keys:", list((getattr(f, "input_schema", None) or getattr(f, "inputSchema", {}) or {}).get("properties", {}).keys()))
args = {"tag_conditions": [{"field": "category", "value": "lamp"}, {"field": "colour", "value": "black"}],
        "numeric_conditions": [{"field": "price", "max_value": 100}]}
r = timed("call products__filter_product (black lamps, price <= 100)", lambda: gw.call("products__filter_product", args))
print("   ->", str(getattr(r, "content", r))[:600])
r = timed("call products__count_product (function=count)", lambda: gw.call("products__count_product", {"function": "count"}))
print("   ->", str(getattr(r, "content", r))[:200])
r = timed("call deepwiki__read_wiki_structure redis/redis", lambda: gw.call("deepwiki__read_wiki_structure", {"repoName": "redis/redis"}))
print("   ->", str(getattr(r, "content", r))[:400])
