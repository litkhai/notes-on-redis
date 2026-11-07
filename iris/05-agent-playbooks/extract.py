"""Automatic FAQ extraction: record one support conversation in Agent Memory (iris/02 store), let it go idle,
and watch this playbook's proposal inbox. Needs the extraction job turned on in the console (README).
usage: .venv/bin/python extract.py [minutes-to-wait]
"""
import os
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
for env in (HERE / ".env", HERE.parent / "02-agent-memory" / ".env"):
    for line in env.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1); os.environ.setdefault(k, v.strip())
from redis_agent_playbook import models  # noqa: E402
from redis_iris.agent_memory import AgentMemory, AgentMemorySettings  # noqa: E402
from redis_iris.agent_playbooks import AgentPlaybooks  # noqa: E402

pb = AgentPlaybooks.from_env()
mem = AgentMemory(AgentMemorySettings.from_env(), assistant_id="notes-on-redis-support")
before = {p.proposal_id for p in pb.client.list_proposals(view=models.ProposalView.INBOX).items}
owner = f"cust-extract-{uuid.uuid4().hex[:6]}"
conv = mem.conversation(owner)
conv.user("My Redis Cloud free database started refusing writes with an OOM error. It says 30 MB, but I only stored about 28 MB. Why?")
conv.assistant("The free database's 30 MB is the memory limit, and Redis needs part of it for its own overhead, so writes are "
               "refused at about 28 MB of values. Nothing is evicted automatically when keys have no TTL. Delete keys, set TTLs, "
               "or move to a paid plan for more memory.")
conv.user("Got it, so setting TTLs on old keys would let the database free space again?")
conv.assistant("Yes. With the default volatile-lru policy only keys that have a TTL can be evicted, so setting TTLs lets Redis free space.")
t0 = time.time()
print(f"recorded 4 events for {owner} in session {conv.session_id[:8]}…; inbox had {len(before)} open proposal(s)")
limit = float(sys.argv[1]) if len(sys.argv) > 1 else 20
while time.time() - t0 < limit * 60:
    time.sleep(30)
    new = [p for p in pb.client.list_proposals(view=models.ProposalView.INBOX).items if p.proposal_id not in before]
    if new:
        for p in new:
            full = pb.client.get_proposal(proposal_id=p.proposal_id)
            faq = full.action.add.candidate.content.payload.faq if full.action.add else None
            print(f"{time.time() - t0:5.0f} s  new proposal, state {full.state}, evidence {full.evidence_count if hasattr(full, 'evidence_count') else '?'}")
            if faq:
                print(f"         question: {faq.question}\n         answer:   {faq.answer}")
        break
    print(f"{time.time() - t0:5.0f} s  no new proposal yet")
else:
    print(f"no proposal within {limit:.0f} minutes")
