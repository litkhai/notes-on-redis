"""MemoryETL: submit free-plan-limits.md to the plan_limit extractor and list what it extracted.
usage: .venv/bin/python etl.py     (MEMORYETL_EXTRACTOR_ID and the Agent Memory settings in .env)
"""
import base64
import hashlib
import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
for line in (HERE / ".env").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip())
from redis_iris.agent_memory import AgentMemory, AgentMemorySettings  # noqa: E402

api = AgentMemory(AgentMemorySettings.from_env()).client
doc = (HERE / "free-plan-limits.md").read_bytes()
ext = os.environ["MEMORYETL_EXTRACTOR_ID"]
key = hashlib.sha256(b"free-plan-limits|v1|docs|" + ext.encode()).hexdigest()
t0 = time.time()
r = api.create_document_ingestion(document_id="free-plan-limits", revision="v1", content=base64.b64encode(doc).decode(),
                                  media_type="text/markdown", owner_id="docs", extractor_id=ext, idempotency_key=key)
ing = r.result.ingestion_id
print("submitted:", r.result.status.processing.value)
for _ in range(120):
    st = api.get_document_ingestion(ingestion_id=ing).ingestion.status
    if st.processing.value in ("SUCCEEDED", "FAILED", "PARTIAL"):
        break
    time.sleep(5)
print(f"{st.processing.value} after {time.time() - t0:.0f} s: chunks {st.completed_chunks}/{st.total_chunks}, "
      f"created {st.created_count}, filtered {st.filtered_count}, error {st.error}")
ids = api.list_document_ingestion_outputs(ingestion_id=ing).items
print("memories created:", len(ids))
res = api.search_long_term_memory(request={"query": "Redis Cloud free plan limit", "filter_": {"owner_id": {"eq": "docs"}}, "limit": 20})
for m in res.items:
    print(f"  [{m.memory_type}] {m.text}")
