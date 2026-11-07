"""Search, the features the first pass skipped, on Redis 8.10.3 with the same 30 notes (docs.json):
FT.AGGREGATE, synonyms, spelling correction, vector types and SVS-VAMANA compression, and Korean questions
against the English notes with a multilingual embedding model (paraphrase-multilingual-MiniLM-L12-v2).
usage: .venv/bin/python extras.py   (starts and removes container nor-local-search2)
"""
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import redis
from fastembed import TextEmbedding

C, PORT = "nor-local-search2", 16397
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
subprocess.run(["docker", "run", "-d", "--name", C, "-p", f"127.0.0.1:{PORT}:6379", "redis:8.10.3"], check=True, capture_output=True)
time.sleep(2)
r = redis.Redis(port=PORT, protocol=2)        # RESP2 so replies are the flat lists the docs show
docs = json.loads((Path(__file__).resolve().parent / "docs.json").read_text())
for d in docs:
    r.hset(f"doc:{d['id']}", mapping={k: d[k] for k in ("title", "body", "category", "year")})
r.execute_command("FT.CREATE", "idx", "ON", "HASH", "PREFIX", "1", "doc:", "SCHEMA", "title", "TEXT", "body", "TEXT",
                  "category", "TAG", "SORTABLE", "year", "NUMERIC", "SORTABLE")
time.sleep(0.5)
titles = lambda res: [dict(zip(*[iter(res[i + 1])] * 2)).get(b"title", b"?").decode() for i in range(1, len(res), 2)]

print("== FT.AGGREGATE: notes per category, newest year, sorted")
res = r.execute_command("FT.AGGREGATE", "idx", "*", "GROUPBY", "1", "@category", "REDUCE", "COUNT", "0", "AS", "n",
                        "REDUCE", "MAX", "1", "@year", "AS", "newest", "SORTBY", "2", "@n", "DESC", "LIMIT", "0", "5")
print("  ", [dict(zip(*[iter([x.decode() for x in row])] * 2)) for row in res[1:]])
res = r.execute_command("FT.AGGREGATE", "idx", "@category:{cluster|replication}", "LOAD", "1", "@title",
                        "APPLY", "strlen(@title)", "AS", "len", "SORTBY", "2", "@len", "DESC")
print("   cluster|replication titles by length:", [dict(zip(*[iter([x.decode() for x in row])] * 2)) for row in res[1:]])

print("\n== synonyms: 'switchover' appears in no note")
print("   before:", titles(r.execute_command("FT.SEARCH", "idx", "switchover", "RETURN", "1", "title")))
print("   FT.SYNUPDATE idx ha switchover failover promotion ->", r.execute_command("FT.SYNUPDATE", "idx", "ha", "switchover", "failover", "promotion"))
print("   right after:", titles(r.execute_command("FT.SEARCH", "idx", "switchover", "RETURN", "1", "title")))
t0 = time.time()
while time.time() - t0 < 10 and not titles(r.execute_command("FT.SEARCH", "idx", "switchover", "RETURN", "1", "title")):
    time.sleep(0.2)
print(f"   after {time.time() - t0:.1f} s:", titles(r.execute_command("FT.SEARCH", "idx", "switchover", "RETURN", "1", "title")))
r.hset("doc:31", mapping={"title": "Planned promotion", "body": "A planned promotion moves the primary role on purpose.", "category": "replication", "year": 2026})
print("   a note added after the update, 'Planned promotion':", "found" if "Planned promotion" in titles(r.execute_command("FT.SEARCH", "idx", "switchover", "RETURN", "1", "title")) else "not found")
print("   FT.SYNDUMP:", r.execute_command("FT.SYNDUMP", "idx"))

print("\n== spelling correction: FT.SPELLCHECK idx 'failovr evicton replca'")
for term in r.execute_command("FT.SPELLCHECK", "idx", "failovr evicton replca", "DISTANCE", "2"):
    print(f"   {term[1].decode():9} -> {[(s[1].decode(), round(float(s[0]), 3)) for s in term[2][:3]]}")
print("   the query itself finds:", titles(r.execute_command("FT.SEARCH", "idx", "failovr", "RETURN", "1", "title")) or "nothing")

print("\n== vector types and SVS-VAMANA compression: the same 30 vectors, memory per index (FT.INFO vector_index_sz_mb)")
model = TextEmbedding("BAAI/bge-small-en-v1.5")
vecs = np.array(list(model.embed([f"{d['title']}. {d['body']}" for d in docs])), dtype=np.float32)
q = np.array(next(model.embed(["how long does a failover take"])), dtype=np.float32)
for name, algo, vtype, extra, conv in (("f32-hnsw", "HNSW", "FLOAT32", [], np.float32), ("f16-hnsw", "HNSW", "FLOAT16", [], np.float16),
                                       ("i8-flat", "FLAT", "INT8", [], None), ("svs-lvq8", "SVS-VAMANA", "FLOAT32", ["COMPRESSION", "LVQ8"], np.float32)):
    prefix = f"{name}:"
    p = r.pipeline(transaction=False)
    for d, v in zip(docs, vecs):
        blob = (np.clip(np.round(v * 127 / np.abs(vecs).max()), -127, 127).astype(np.int8) if conv is None else v.astype(conv)).tobytes()
        p.hset(f"{prefix}{d['id']}", mapping={"title": d["title"], "vec": blob})
    p.execute()
    args = ["TYPE", vtype, "DIM", "384", "DISTANCE_METRIC", "COSINE", *extra]
    try:
        r.execute_command("FT.CREATE", f"v-{name}", "ON", "HASH", "PREFIX", "1", prefix, "SCHEMA", "title", "TEXT",
                          "vec", "VECTOR", algo, str(len(args)), *args)
        time.sleep(1)
        qb = (np.clip(np.round(q * 127 / np.abs(vecs).max()), -127, 127).astype(np.int8) if conv is None else q.astype(conv)).tobytes()
        res = r.execute_command("FT.SEARCH", f"v-{name}", "*=>[KNN 3 @vec $v AS s]", "PARAMS", "2", "v", qb, "SORTBY", "s", "RETURN", "1", "title", "DIALECT", "2")
        info = r.execute_command("FT.INFO", f"v-{name}"); info = dict(zip(*[iter(info)] * 2))
        print(f"   {name:9} {algo:10} {vtype:7} {' '.join(extra):16} top 3 {titles(res)}  index {float(info[b'vector_index_sz_mb']) * 1024:.1f} KB")
    except redis.ResponseError as e:
        print(f"   {name:9} {algo:10} {vtype:7} {' '.join(extra):16} -> {e}")

print("\n== Korean questions against the English notes")
ml = TextEmbedding("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
mv = np.array(list(ml.embed([f"{d['title']}. {d['body']}" for d in docs])), dtype=np.float32)
p = r.pipeline(transaction=False)
for d, v in zip(docs, mv):
    p.hset(f"ml:{d['id']}", mapping={"title": d["title"], "vec": v.tobytes()})
p.execute()
r.execute_command("FT.CREATE", "v-ml", "ON", "HASH", "PREFIX", "1", "ml:", "SCHEMA", "title", "TEXT",
                  "vec", "VECTOR", "HNSW", "6", "TYPE", "FLOAT32", "DIM", str(mv.shape[1]), "DISTANCE_METRIC", "COSINE")
time.sleep(1)
for kq in ("장애 조치에 얼마나 걸리나요?", "무료 플랜에서 메모리가 다 차면 어떻게 되나요?", "포스트그레스 테이블을 레디스와 동기화하고 싶어요"):
    for label, mdl, idxname in (("multilingual", ml, "v-ml"), ("English model", model, None)):
        if idxname is None:
            continue
        res = r.execute_command("FT.SEARCH", idxname, "*=>[KNN 3 @vec $v AS s]", "PARAMS", "2", "v",
                                np.array(next(mdl.embed([kq])), dtype=np.float32).tobytes(), "SORTBY", "s", "RETURN", "1", "title", "DIALECT", "2")
        print(f"   {kq!r:36} {label}: {titles(res)}")
    res = r.execute_command("FT.SEARCH", "v-f32-hnsw", "*=>[KNN 3 @vec $v AS s]", "PARAMS", "2", "v", np.array(next(model.embed([kq])), dtype=np.float32).tobytes(),
                            "SORTBY", "s", "RETURN", "1", "title", "DIALECT", "2")
    print(f"   {'':36} English-only model: {titles(res)}")
print("   full text for '장애 조치':", titles(r.execute_command("FT.SEARCH", "idx", "장애 조치", "RETURN", "1", "title")) or "nothing (the notes are English)")
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
