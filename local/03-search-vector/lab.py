"""Search and vector search on Redis 8.10.3 with 30 short documents from this site (docs.json), embedded
locally with fastembed (BAAI/bge-small-en-v1.5, 384 dimensions, no API key). One index on hashes, one on
JSON; full-text, tag and numeric queries; KNN with and without a filter; FT.HYBRID (8.4+); vector sets.
usage: .venv/bin/python lab.py   (starts and removes container nor-local-search)
"""
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import redis
from fastembed import TextEmbedding

C, PORT = "nor-local-search", 16395
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
subprocess.run(["docker", "run", "-d", "--name", C, "-p", f"127.0.0.1:{PORT}:6379", "redis:8.10.3"], check=True, capture_output=True)
time.sleep(2)
r = redis.Redis(port=PORT)
docs = json.loads((Path(__file__).resolve().parent / "docs.json").read_text())
model = TextEmbedding("BAAI/bge-small-en-v1.5")
t0 = time.perf_counter()
vecs = np.array(list(model.embed([f"{d['title']}. {d['body']}" for d in docs])), dtype=np.float32)
print(f"redis-py {redis.__version__}, protocol {r.execute_command('HELLO')[b'proto'] if isinstance(r.execute_command('HELLO'), dict) else 2}")
print(f"embedded {len(docs)} documents locally in {time.perf_counter() - t0:.2f} s, {vecs.shape[1]} dimensions")
emb = lambda q: np.array(next(model.embed([q])), dtype=np.float32)

print("\n== the same documents as hashes and as JSON")
p = r.pipeline(transaction=False)
for d, v in zip(docs, vecs):
    p.hset(f"doc:{d['id']}", mapping={"title": d["title"], "body": d["body"], "category": d["category"], "year": d["year"], "vec": v.tobytes()})
    p.json().set(f"jdoc:{d['id']}", "$", {**d, "vec": v.tolist()})
p.execute()
print("  ", r.execute_command("FT.CREATE", "idx", "ON", "HASH", "PREFIX", "1", "doc:", "SCHEMA", "title", "TEXT", "WEIGHT", "2",
                            "body", "TEXT", "category", "TAG", "year", "NUMERIC", "SORTABLE",
                            "vec", "VECTOR", "HNSW", "6", "TYPE", "FLOAT32", "DIM", "384", "DISTANCE_METRIC", "COSINE"))
print("  ", r.execute_command("FT.CREATE", "jidx", "ON", "JSON", "PREFIX", "1", "jdoc:", "SCHEMA", "$.title", "AS", "title", "TEXT",
                            "$.category", "AS", "category", "TAG", "$.vec", "AS", "vec", "VECTOR", "FLAT", "6", "TYPE", "FLOAT32",
                            "DIM", "384", "DISTANCE_METRIC", "COSINE"))
def ft_info(name, key):
    reply = r.execute_command("FT.INFO", name)   # redis-py 8 parses it into a dict; older ones return a flat list
    if isinstance(reply, dict):
        return reply.get(key, reply.get(key.decode()))
    return reply[reply.index(key) + 1]


for _ in range(50):
    if float(ft_info("idx", b"percent_indexed")) == 1.0:
        break
    time.sleep(0.1)
print(f"   idx: {int(ft_info('idx', b'num_docs'))} docs, percent_indexed {float(ft_info('idx', b'percent_indexed'))}")


def rows_of(res):
    """FT.SEARCH replies: a RESP3 map (redis-py 8 here) or the RESP2 flat list."""
    if isinstance(res, dict):
        return res[b"total_results"], [x[b"extra_attributes"] for x in res[b"results"]]
    return res[0], [dict(zip(*[iter(res[i + 1])] * 2)) for i in range(1, len(res), 2)]


def show(label, res, field=b"title"):
    n, rows = rows_of(res)
    items = []
    for f in rows:
        score = f.get(b"score") or f.get(b"__vec_score")
        items.append(f"{f.get(field, b'?').decode()}" + (f" ({1 - float(score):.2f})" if score else ""))
    print(f"   {label:44} {n} hit(s): " + "; ".join(items[:5 if 'only' in label else 3]))


print("\n== full text, tag and numeric (FT.SEARCH)")
show("'failover'", r.execute_command("FT.SEARCH", "idx", "failover", "RETURN", "1", "title"))
show("'fail*' (prefix)", r.execute_command("FT.SEARCH", "idx", "fail*", "RETURN", "1", "title"))
show("'@category:{memory}'", r.execute_command("FT.SEARCH", "idx", "@category:{memory}", "RETURN", "1", "title"))
show("'@year:[-inf 2025]'", r.execute_command("FT.SEARCH", "idx", "@year:[-inf 2025]", "RETURN", "1", "title"))
show("'cache in sync with my database' (words)", r.execute_command("FT.SEARCH", "idx", "cache in sync with my database", "RETURN", "1", "title"))

print("\n== KNN: the same question by meaning (cosine; similarity shown as 1 - distance)")
for q in ("How do I keep Redis in sync with my Postgres tables?", "what happens when the free tier runs out of memory",
          "a consumer crashed and left messages unprocessed"):
    show(repr(q)[:44], r.execute_command("FT.SEARCH", "idx", "*=>[KNN 3 @vec $v AS score]", "PARAMS", "2", "v", emb(q).tobytes(),
                                         "SORTBY", "score", "RETURN", "2", "title", "score", "DIALECT", "2"))
q = "how long does a failover take"
show("same KNN on the JSON index", r.execute_command("FT.SEARCH", "jidx", "*=>[KNN 3 @vec $v AS score]", "PARAMS", "2", "v", emb(q).tobytes(),
                                                       "SORTBY", "score", "RETURN", "2", "title", "score", "DIALECT", "2"))
show("KNN 'how long does a failover take'", r.execute_command("FT.SEARCH", "idx", "*=>[KNN 3 @vec $v AS score]", "PARAMS", "2", "v", emb(q).tobytes(),
                                                                "SORTBY", "score", "RETURN", "2", "title", "score", "DIALECT", "2"))
show("... filtered to @category:{cluster}", r.execute_command("FT.SEARCH", "idx", "(@category:{cluster})=>[KNN 3 @vec $v AS score]", "PARAMS", "2", "v",
                                                              emb(q).tobytes(), "SORTBY", "score", "RETURN", "2", "title", "score", "DIALECT", "2"))

print("\n== FT.HYBRID (8.4+): text and vector in one query, fused with RRF")
q = "keep a cache consistent with a relational database"
show("text only: 'database'", r.execute_command("FT.SEARCH", "idx", "database", "RETURN", "1", "title", "LIMIT", "0", "5"))
show(f"vector only: {q[:30]!r}", r.execute_command("FT.SEARCH", "idx", "*=>[KNN 5 @vec $v AS score]", "PARAMS", "2", "v", emb(q).tobytes(),
                                                  "SORTBY", "score", "RETURN", "2", "title", "score", "DIALECT", "2"))
res = r.execute_command("FT.HYBRID", "idx", "SEARCH", "database", "VSIM", "@vec", "$v", "KNN", "2", "K", "5",
                        "COMBINE", "RRF", "2", "CONSTANT", "60", "LOAD", "1", "@title", "LIMIT", "0", "3", "PARAMS", "2", "v", emb(q).tobytes())
print(f"   FT.HYBRID SEARCH 'database' + VSIM, COMBINE RRF: total_results {res[b'total_results']}, top 3 "
      f"{[x[b'title'].decode() for x in res[b'results']]}")

print("\n== vector sets (VADD / VSIM) with the same vectors, no index to declare")
p = r.pipeline(transaction=False)
for d, v in zip(docs, vecs):
    p.execute_command("VADD", "vs", "FP32", v.tobytes(), d["title"], "SETATTR", json.dumps({"category": d["category"]}))
p.execute()
print("   VCARD vs:", r.execute_command("VCARD", "vs"), "| VDIM vs:", r.execute_command("VDIM", "vs"))
q = "how long does a failover take"
print("   VSIM top 3:", [x.decode() for x in r.execute_command("VSIM", "vs", "FP32", emb(q).tobytes(), "COUNT", "3")])
print("   VSIM FILTER .category == \"cluster\":", [x.decode() for x in r.execute_command("VSIM", "vs", "FP32", emb(q).tobytes(), "COUNT", "3",
                                                                                          "FILTER", '.category == "cluster"')])
hash_bytes = sum(r.memory_usage("doc:%d" % d["id"]) for d in docs)
print(f"   memory: vector set {r.memory_usage('vs')} bytes; the 30 hashes {hash_bytes} bytes")
subprocess.run(["docker", "rm", "-f", C], capture_output=True)
