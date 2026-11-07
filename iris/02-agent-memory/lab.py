"""Agent Memory beyond the first call: session summarisation, a shared namespace, sensitive data,
and forgetting an owner. Same store and keys as iris/01 (.env, gitignored).

usage: .venv/bin/python lab.py sessions|namespace|pii|forget|stats
All owners and personal data below are made up for the lab.
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
api = mem.client


def sessions():
    """24 messages in one session: the store summarises after 20 and keeps the last 10."""
    conv = mem.conversation("cust-2001")
    for i in range(12):
        conv.user(f"Question {i + 1}: how do I size a Redis Cloud database for {100 * (i + 1)} MB of sessions?")
        conv.assistant(f"Answer {i + 1}: pick the next plan above {100 * (i + 1)} MB and remember the replica doubles it.")
    sid = conv.session_id
    print("session:", sid)
    for wait in (0, 30, 60, 90):
        time.sleep(wait if wait == 0 else 30)
        s = api.get_session_memory(session_id=sid)
        summ = (s.summary.text if s.summary and getattr(s.summary, "text", None) else None) if s.summary else None
        print(f"t+{wait:2d}s: events kept {len(s.events)}; summary: {summ[:160] + '…' if summ and len(summ) > 160 else summ}")
        if summ:
            break
    full = api.get_session_memory(session_id=sid, include_summarised_events=True)
    print("with summarised events included:", len(full.events))


def namespace():
    """A shared namespace every owner may read, written once."""
    try:
        ns = api.create_namespace(request={"name": "team-kb", "scope": "SHARED"})
        nsid = ns.namespace.namespace_id
        print("namespace created:", nsid)
    except Exception as e:
        print("create_namespace:", type(e).__name__, str(e)[:200])
        nss = api.list_namespaces()
        items = getattr(nss, "items", None) or getattr(nss, "namespaces", [])
        nsid = next((n.namespace_id for n in items if n.name == "team-kb"), None)
        print("existing namespace:", nsid)
    m = mem.remember("Support policy: Redis Cloud free databases cannot enable TLS; recommend Essentials for production.",
                     owner="support-team", namespace_id=nsid, topics=["policy"])
    print("shared memory:", m.text)
    time.sleep(3)
    for owner, shared in (("cust-3001", ()), ("cust-3001", (nsid,))):
        r = mem.recall("Can a free database use TLS?", owner=owner, shared=shared)
        print(f"recall as {owner} with shared={list(shared) or 'none'}: {[x.text for x in r.memories]}")


def pii():
    """A conversation carrying made-up personal data; then what reached long-term memory."""
    tag = os.environ.get("PII_RUN", "run")
    owner = f"cust-pii-{tag}"
    conv = mem.conversation(owner)
    conv.user("My email is jane.doe@example.com and my phone is +82-10-0000-0000. I prefer to be contacted by email about my Redis Cloud invoices.")
    conv.assistant("Noted: you prefer email for invoice questions.")
    print("owner:", owner, "session:", conv.session_id)
    for t in range(0, 481, 30):
        r = api.search_long_term_memory(request={"query": "contact email phone", "filter_": {"owner_id": {"eq": owner}}, "limit": 10})
        print(f"t+{t:3d}s: {[x.text for x in r.items]}")
        if r.items:
            break
        time.sleep(30)


def forget():
    for owner in ("cust-2001", "cust-pii-off", "cust-pii-on"):
        before = len(mem.recall("anything about this customer", owner=owner, limit=20).memories)
        f = mem.forget(owner)
        after = len(mem.recall("anything about this customer", owner=owner, limit=20).memories)
        print(f"{owner}: memories {before} -> {after}; {f}")


def stats():
    s = api.list_sessions(include_all=True)
    rows = getattr(s, "items", None) or getattr(s, "sessions", [])
    print("sessions:", [(getattr(r, "session_id", None), getattr(r, "owner_id", None)) for r in rows])


if __name__ == "__main__":
    for step in sys.argv[1:]:
        print(f"\n== {step}")
        try:
            globals()[step]()
        except Exception as e:
            print(f"{type(e).__name__}: {str(e)[:400]}")
