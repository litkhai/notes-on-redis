"""Agent Playbooks at runtime: discover published FAQs for paraphrased and Korean questions,
propose an FAQ for an uncovered one. FAQs are authored in faqs/ and synced with the iris CLI.
usage: .venv/bin/python lab.py [discover] [propose]
"""
import os
import sys
import time
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip())
from redis_iris.agent_playbooks import AgentPlaybooks  # noqa: E402

pb = AgentPlaybooks.from_env()
QUESTIONS = [
    "is encryption in transit available on the free tier?",
    "how many clients can connect to the free database",
    "MSET fails with a slot error on my cluster",
    "무료 DB에서 TLS 켤 수 있어?",
    "How do I configure Active-Active between Seoul and Tokyo?",
]


def discover():
    for q in QUESTIONS:
        t0 = time.perf_counter(); d = pb.discover(q, limit=2); ms = (time.perf_counter() - t0) * 1000
        top = [(getattr(e, "entry_key", None) or getattr(e, "key", None), round(getattr(e, "score", 0) or 0, 2), getattr(e, "version", None)) for e in d.entries]
        print(f"{ms:5.0f} ms  {q!r:60} {top}")


def propose():
    p = pb.propose_faq(key="active-active-seoul-tokyo", question="How do I configure Active-Active between Seoul and Tokyo?",
                       answer="Draft: Active-Active needs Redis Cloud Pro; not run on this site yet.", intents=["active-active"])
    print("proposal:", getattr(p, "proposal_id", None) and "created", getattr(p, "status", None))


if __name__ == "__main__":
    for step in sys.argv[1:] or ["discover"]:
        print(f"\n== {step}")
        globals()[step]()
