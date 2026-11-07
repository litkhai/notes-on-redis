"""Intent Router per-intent thresholds: the Router default is 0.70; an intent's own minScore overrides it.
Same router and key as lab.py (.env). Restores the intents at the end.
usage: .venv/bin/python thresholds.py
"""
import os
from pathlib import Path

for line in (Path(__file__).resolve().parent / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k, v.strip())
from redis_iris.intent_router import IntentRouter  # noqa: E402

router = IntentRouter.from_env()
QUERIES = ["is encryption available on the free tier", "I was billed twice, can you check?",
           "tell me something funny", "Can you recommend a good restaurant?", "무료 플랜에서 TLS를 켤 수 있나요?"]


def table(title, **kw):
    print(f"-- {title}")
    for q in QUERIES:
        m = list(router.match(q, **kw))
        print(f"   {q!r:46} -> " + (", ".join(f"{x.name} {x.score:.2f}" for x in m) if m else "no match (fallback)"))


table("raw scores, every intent above 0.01", min_score=0.01, limit=2)
table("Router default (0.70), no per-intent thresholds")
print("-- per-intent thresholds: tls_question 0.60 (looser), off_topic 0.85 (stricter)")
for name, s in (("tls_question", 0.60), ("off_topic", 0.85)):
    i = router.update(name, min_score=s); print(f"   {i.name}: min_score {i.min_score}, revision {i.revision}")
table("Router default plus per-intent thresholds")
table("a per-call min_score 0.5 on top", min_score=0.5)
for name in ("tls_question", "off_topic"):
    router.update(name, min_score=None)
print("restored:", [(i.name, i.min_score) for i in router.intents()])
