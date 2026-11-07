"""Agent Memory on the Redis Cloud free database: health, write one memory, a conversation,
recall. Reads IRIS_AGENT_MEMORY_URL / _STORE_ID / _API_KEY from .env (gitignored).

usage: .venv/bin/python first_memory.py [health|remember|converse|recall|forget]   (no argument = all)
"""
import os
import sys
import time
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip())

from redis_iris.agent_memory import AgentMemory  # noqa: E402

from redis_iris.agent_memory import AgentMemorySettings  # noqa: E402

mem = AgentMemory(AgentMemorySettings.from_env(), assistant_id="notes-on-redis-lab")
OWNER = "cust-1042"


def health():
    h = mem.health()
    print("health:", h)


def remember():
    m = mem.remember("Prefers answers in Korean, with code examples in Python.", owner=OWNER, topics=["preferences"])
    print("remembered:", m)


def converse():
    conv = mem.conversation(OWNER)
    conv.user("My Redis Cloud database is on the free plan in Seoul. Can I turn on TLS?")
    conv.assistant("Not on the free plan: the API refuses enableTls there. A paid plan can.")
    print("session:", conv.session_id if hasattr(conv, "session_id") else conv)


def recall():
    t0 = time.perf_counter()
    r = mem.recall("How does this customer want answers?", owner=OWNER)
    print(f"recall in {(time.perf_counter() - t0) * 1000:.0f} ms:")
    print(r)


def forget():
    print("forgotten:", mem.forget(OWNER))


if __name__ == "__main__":
    steps = {"health": health, "remember": remember, "converse": converse, "recall": recall, "forget": forget}
    for s in sys.argv[1:] or ["health", "remember", "converse", "recall"]:
        print(f"\n== {s}")
        try:
            steps[s]()
        except Exception as e:  # show the service's answer, not a traceback
            print(f"{type(e).__name__}: {str(e)[:400]}")
