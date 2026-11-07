"""Custom detector and semantic exclusion on Agent Memory (configured in the console, see README):
detector lab-account-id, pattern ACCT-[0-9]{6}, on match Drop memory; exclusion prompt about passwords,
one-time codes, recovery codes and API keys. A direct write and an extracted conversation; made-up data.
usage: .venv/bin/python detectors.py
"""
import os
import time
import uuid
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k, v.strip())
from redis_iris.agent_memory import AgentMemory, AgentMemorySettings  # noqa: E402

mem = AgentMemory(AgentMemorySettings.from_env(), assistant_id="notes-on-redis-lab")
owner = f"cust-det-{uuid.uuid4().hex[:6]}"
print("== direct writes (remember)")
for text in ("Customer account ACCT-654321 is on the support plan.", "The customer prefers invoices by email."):
    try:
        m = mem.remember(text, owner=owner)
        print(f"   remember({text!r}) -> stored: {getattr(m, 'text', m)!r}")
    except Exception as e:
        print(f"   remember({text!r}) -> {type(e).__name__}: {str(e)[:120]}")
print("   memories now:", [m.text for m in mem.memories(owner)])

owner2 = f"cust-det-{uuid.uuid4().hex[:6]}"
print("\n== a conversation, extracted in the background")
conv = mem.conversation(owner2)
conv.user("Hi, my account is ACCT-123456 and I want all invoices sent by email.")
conv.assistant("Noted, invoices will go to your email.")
conv.user("For the record, my recovery code is 7F3K-99QX-AB12. Also, please create new databases in the Seoul region.")
conv.assistant("Understood: new databases go to Seoul.")
conv.user("I usually deploy on Friday evenings, so keep maintenance away from then.")
conv.assistant("Got it, no maintenance on Friday evenings.")
t0 = time.time()
while time.time() - t0 < 600:
    time.sleep(30)
    texts = [m.text for m in mem.memories(owner2)]
    if texts:
        time.sleep(30); texts = [m.text for m in mem.memories(owner2)]
        print(f"   after {time.time() - t0:.0f} s, long-term memories for this owner:")
        for t in texts:
            print("    -", t)
        break
    print(f"   {time.time() - t0:4.0f} s: nothing extracted yet")
mem.forget(owner); mem.forget(owner2)
print("\nboth test owners forgotten")
