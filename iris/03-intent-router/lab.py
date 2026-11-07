"""Intent Router on the free database: define intents with targets, then route queries.
usage: .venv/bin/python lab.py [define] [match] [threshold]
"""
import os
import sys
import time
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip())
from redis_iris.intent_router import IntentRouter, Target  # noqa: E402

router = IntentRouter.from_env()

INTENTS = {
    "billing": (["Why was I charged this month?", "How do I download my invoice?", "Change the credit card on my account"],
                Target("tool", "billing_api.lookup")),
    "tls_question": (["Can I turn on TLS for my database?", "How do I enable encryption in transit?", "Does the free plan support TLS?"],
                     Target("model", "small-model")),
    "outage": (["My database is not responding", "I get connection timeouts since this morning", "Is Redis Cloud down?"],
               Target("agent", "incident-agent")),
    "off_topic": (["Tell me a joke", "What is the weather today?", "Write me a poem"],
                  Target("guardrail", "polite-refusal")),
}
QUERIES = [
    "I was billed twice, can you check?",
    "is encryption available on the free tier",
    "connections keep timing out on my prod database",
    "tell me something funny",
    "무료 플랜에서 TLS를 켤 수 있나요?",
    "청구서를 어디서 받나요?",
    "How many shards should a 50 GB cluster have?",
    "Can you recommend a good restaurant?",
]


def define():
    for name, (examples, target) in INTENTS.items():
        i = router.define(name, examples=examples, target=target, description=f"{name} requests")
        print(f"defined {i.name} -> {target.type}:{target.ref}")
    print("intents now:", [i.name for i in router.intents()])


def match(min_score=None):
    ts = []
    for q in QUERIES:
        t0 = time.perf_counter(); m = router.match(q, min_score=min_score); ts.append((time.perf_counter() - t0) * 1000)
        best = list(m)[0] if list(m) else None
        what = f"{best.name} ({best.score:.2f}) -> {best.target.type}:{best.target.ref}" if best else "no match (fallback)"
        print(f"{ts[-1]:6.0f} ms  {q!r:58} {what}")
    ts.sort(); print(f"median {ts[len(ts) // 2]:.0f} ms over {len(ts)} queries")


def korean():
    """Add Korean phrasings (not the test queries) and match again at 0.5."""
    router.add_examples("billing", ["인보이스는 어떻게 내려받나요", "이번 달 요금 청구 내역을 보고 싶어요"])
    router.add_examples("off_topic", ["맛집 추천해 줘", "오늘 날씨 어때"])
    print("billing examples:", [e.text for e in router.examples("billing")])
    match(0.5)


def threshold():
    print("-- min_score 0.5 for the same queries")
    match(0.5)


if __name__ == "__main__":
    print("health:", router.health())
    for step in sys.argv[1:] or ["define", "match", "threshold"]:
        print(f"\n== {step}")
        globals()[step]()
