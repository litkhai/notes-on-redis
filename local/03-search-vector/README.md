# Search and vector search

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis 8.10.3 (`redis:8.10.3`), redis-py 8.1.0, fastembed 0.9.1 with BAAI/bge-small-en-v1.5, 2026-11-07.**

Thirty one-line notes taken from this site's own findings ([`docs.json`](./docs.json)) are stored twice, as hashes and as JSON, and indexed with `FT.CREATE`. They are embedded on the same machine with a small open model, so no API key is involved. Then the same questions are asked by words (full text, tag, numeric), by meaning (KNN), by both at once (`FT.HYBRID`, 8.4+), and against a vector set, which needs no index at all. From the docs: `FT.HYBRID` "Performs hybrid search combining text search and vector similarity with configurable fusion methods", and "Vector sets are a data type similar to sorted sets, but instead of a score, vector set elements have a string representation of a vector."

Official documentation: [Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/), [Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/), [FT.SEARCH](https://redis.io/docs/latest/commands/ft.search/), [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/).

### Run

```bash
python3 -m venv .venv && .venv/bin/pip install fastembed redis numpy   # the lab used uv with Python 3.12
.venv/bin/python lab.py   # downloads the 384-dimension embedding model once (65 MB in the fastembed cache), starts and removes its own container
.venv/bin/python extras.py   # FT.AGGREGATE, synonyms, spellcheck, vector types and SVS-VAMANA, Korean with a multilingual model (about 240 MB more in the fastembed cache)
```

Output as it appeared (2026-11-07):

```text
redis-py 8.1.0, protocol 3
embedded 30 documents locally in 0.09 s, 384 dimensions

== the same documents as hashes and as JSON
   b'OK'
   b'OK'
   idx: 30 docs, percent_indexed 1.0

== full text, tag and numeric (FT.SEARCH)
   'failover'                                   3 hit(s): CLUSTERDOWN during failover; Sentinel failover time; Cluster failover and node timeout
   'fail*' (prefix)                             3 hit(s): CLUSTERDOWN during failover; Sentinel failover time; Cluster failover and node timeout
   '@category:{memory}'                         3 hit(s): Volatile policies need TTLs; LRM evicts read-only keys; LFU keeps hot keys
   '@year:[-inf 2025]'                          2 hit(s): Claiming stuck stream messages; Atomic slot migration
   'cache in sync with my database' (words)     0 hit(s): 

== KNN: the same question by meaning (cosine; similarity shown as 1 - distance)
   'How do I keep Redis in sync with my Postgre 3 hit(s): Change data capture from Postgres (0.83); Client-side caching (0.69); Free plan memory limit (0.68)
   'what happens when the free tier runs out of 3 hit(s): Free plan memory limit (0.72); Client-side caching (0.67); Atomic slot migration (0.67)
   'a consumer crashed and left messages unproc 3 hit(s): Claiming stuck stream messages (0.75); Giving a message back (0.70); Client-side caching (0.59)
   same KNN on the JSON index                   3 hit(s): Cluster failover and node timeout (0.78); CLUSTERDOWN during failover (0.74); Sentinel failover time (0.72)
   KNN 'how long does a failover take'          3 hit(s): Cluster failover and node timeout (0.78); CLUSTERDOWN during failover (0.74); Sentinel failover time (0.72)
   ... filtered to @category:{cluster}          3 hit(s): Cluster failover and node timeout (0.78); CLUSTERDOWN during failover (0.74); Atomic slot migration (0.58)

== FT.HYBRID (8.4+): text and vector in one query, fused with RRF
   text only: 'database'                        5 hit(s): Free plan connections; No TLS on the free plan; Free plan memory limit; Trial licence shard limit; Alerts replace the whole list
   vector only: 'keep a cache consistent with a' 5 hit(s): Client-side caching (0.68); Persistence and fsync (0.66); Volatile policies need TTLs (0.63); Atomic slot migration (0.63); Broadcast tracking (0.62)
   FT.HYBRID SEARCH 'database' + VSIM, COMBINE RRF: total_results 10, top 3 ['Free plan connections', 'Client-side caching', 'Persistence and fsync']

== vector sets (VADD / VSIM) with the same vectors, no index to declare
   VCARD vs: 30 | VDIM vs: 384
   VSIM top 3: ['Cluster failover and node timeout', 'CLUSTERDOWN during failover', 'Sentinel failover time']
   VSIM FILTER .category == "cluster": ['Cluster failover and node timeout', 'CLUSTERDOWN during failover', 'Atomic slot migration']
   memory: vector set 35878 bytes; the 30 hashes 66237 bytes
```

`extras.py` output as it appeared (2026-11-07):

```text
== FT.AGGREGATE: notes per category, newest year, sorted
   [{'category': 'cloud', 'n': '5', 'newest': '2026'}, {'category': 'cluster', 'n': '4', 'newest': '2026'}, {'category': 'memory', 'n': '3', 'newest': '2026'}, {'category': 'ai', 'n': '3', 'newest': '2026'}, {'category': 'replication', 'n': '3', 'newest': '2026'}]
   cluster|replication titles by length: [{'title': 'Cluster failover and node timeout', 'len': '33'}, {'title': 'Hash tags keep keys together', 'len': '28'}, {'title': 'CLUSTERDOWN during failover', 'len': '27'}, {'title': 'WAIT counts one connection', 'len': '26'}, {'title': 'Old primary stays master', 'len': '24'}, {'title': 'Sentinel failover time', 'len': '22'}, {'title': 'Atomic slot migration', 'len': '21'}]

== synonyms: 'switchover' appears in no note
   before: []
   FT.SYNUPDATE idx ha switchover failover promotion -> b'OK'
   right after: ['CLUSTERDOWN during failover', 'Sentinel failover time', 'Cluster failover and node timeout']
   after 0.0 s: ['CLUSTERDOWN during failover', 'Sentinel failover time', 'Cluster failover and node timeout']
   a note added after the update, 'Planned promotion': found
   FT.SYNDUMP: [b'failover', [b'ha'], b'switchover', [b'ha'], b'promotion', [b'ha']]

== spelling correction: FT.SPELLCHECK idx 'failovr evicton replca'
   failovr   -> [('+failov', 0.194), ('failover', 0.194)]
   evicton   -> [('eviction', 0.129), ('evicts', 0.065)]
   replca    -> [('replica', 0.258), ('replicas', 0.065), ('replace', 0.065)]
   the query itself finds: nothing

== vector types and SVS-VAMANA compression: the same 30 vectors, memory per index (FT.INFO vector_index_sz_mb)
   f32-hnsw  HNSW       FLOAT32                  top 3 ['Cluster failover and node timeout', 'CLUSTERDOWN during failover', 'Sentinel failover time']  index 1726.0 KB
   f16-hnsw  HNSW       FLOAT16                  top 3 ['Cluster failover and node timeout', 'CLUSTERDOWN during failover', 'Sentinel failover time']  index 953.9 KB
   i8-flat   FLAT       INT8                     top 3 ['Cluster failover and node timeout', 'CLUSTERDOWN during failover', 'Sentinel failover time']  index 405.6 KB
   svs-lvq8  SVS-VAMANA FLOAT32 COMPRESSION LVQ8 top 3 ['Cluster failover and node timeout', 'CLUSTERDOWN during failover', 'Sentinel failover time']  index 1556.0 KB

== Korean questions against the English notes
   '장애 조치에 얼마나 걸리나요?'                   multilingual: ['Cluster failover and node timeout', 'Old primary stays master', 'Sentinel failover time']
                                        English-only model: ['Giving a message back', 'Agent memory for AI agents', 'Kubernetes operator']
   '무료 플랜에서 메모리가 다 차면 어떻게 되나요?'         multilingual: ['Free plan memory limit', 'Agent memory for AI agents', 'Client-side caching']
                                        English-only model: ['Idempotent producers', 'LFU keeps hot keys', 'Giving a message back']
   '포스트그레스 테이블을 레디스와 동기화하고 싶어요'         multilingual: ['Claiming stuck stream messages', 'Old primary stays master', 'CLUSTERDOWN during failover']
                                        English-only model: ['Broadcast tracking', 'LFU keeps hot keys', 'Atomic slot migration']
   full text for '장애 조치': nothing (the notes are English)
```

### What was observed

- **Indexing is instant at this size.** Both indexes were complete (`percent_indexed 1.0`) right after `FT.CREATE`; embedding the 30 notes took 0.1 s on the CPU.
- **Full text matches words, not meaning.** `failover` and the prefix `fail*` found the three failover notes, tags and numeric ranges filtered as expected, but `cache in sync with my database` found nothing: by default every term must appear, and no note has them all.
- **KNN matches meaning.** "How do I keep Redis in sync with my Postgres tables?" found the change data capture note first (similarity 0.83); "a consumer crashed and left messages unprocessed" found `XAUTOCLAIM` and `XNACK`. The JSON index with a `FLAT` vector field returned the same top 3 as the hash index with `HNSW`.
- **A filter narrows KNN.** `(@category:{cluster})=>[KNN 3 ...]` replaced the Sentinel note with a cluster note.
- **FT.HYBRID fuses two ranked lists.** For text `database` and the vector of "keep a cache consistent with a relational database", text alone and vector alone returned different top 5s. `COMBINE RRF` returned the union of both (10 results) and put the first of each list on top. The result depends strongly on the text part.
- **Vector sets give the same neighbours without an index.** `VADD` with the same vectors and `VSIM` returned the same top 3 as KNN, and `FILTER '.category == "cluster"'` over a JSON attribute did what the tag filter did. The vector set took 35,878 bytes; the 30 hashes with their vectors took 66,237.
- **redis-py 8.1.0 talks RESP3.** `HELLO` reported protocol 3, and `FT.SEARCH` and `FT.INFO` came back as maps, not the flat lists older examples parse. The lab handles both.
- **FT.AGGREGATE groups and computes.** `GROUPBY @category REDUCE COUNT ... REDUCE MAX @year` returned notes per category with their newest year; `APPLY strlen(@title)` added a computed field to sort by.
- **Synonyms rewrite the query side only after a rescan.** "switchover" is in no note. After `FT.SYNUPDATE idx ha switchover failover promotion` it found the three failover notes, and a note added afterwards with "promotion" was found too. In a first run the search issued right after the update returned nothing: existing documents are rescanned in the background.
- **FT.SPELLCHECK suggests from the index's own terms.** `failovr evicton replca` got `failover`, `eviction` and `replica` as top suggestions, while searching `failovr` as typed found nothing.
- **Smaller vector types gave the same answer here.** `FLOAT32` and `FLOAT16` HNSW, `INT8` FLAT and `SVS-VAMANA` with `COMPRESSION LVQ8` all returned the same top 3. The index sizes in `FT.INFO` (1,724, 956, 406 and 1,556 KB) mostly reflect the initial allocation for 30 vectors, not a per-vector cost. The docs add that "Intel's proprietary LVQ and LeanVec optimizations are not available in Redis Open Source".
- **Korean needs a multilingual model, and still misses.** With `paraphrase-multilingual-MiniLM-L12-v2`, the Korean questions about failover time and a full free database found the right English notes first. The English-only model returned unrelated notes for all three. Neither found the change data capture note for a Korean question about syncing Postgres tables. Full-text search for Korean words found nothing, since the notes are English.

### Not run / caveats

- Thirty documents say nothing about recall or latency at scale, and similarities from one small English model are not a quality measure.
- Korean text itself was not indexed; only Korean questions against English notes were tried.

| | |
|---|---|
| Plan needed | Free (local Docker) |
| Verified on | Redis 8.10.3 (`redis:8.10.3`), redis-py 8.1.0, fastembed 0.9.1 with BAAI/bge-small-en-v1.5, 2026-11-07 |

## 한국어

**확인: Redis 8.10.3 (`redis:8.10.3`), redis-py 8.1.0, fastembed 0.9.1 with BAAI/bge-small-en-v1.5, 2026-11-07.**

이 사이트의 측정 결과에서 뽑은 한 줄짜리 메모 30개([`docs.json`](./docs.json))를 해시와 JSON으로 두 번 저장하고 `FT.CREATE`로 색인한다. 임베딩은 같은 기계에서 작은 공개 모델로 만들므로 API 키가 필요 없다. 그다음 같은 질문을 단어로(전문, 태그, 숫자), 의미로(KNN), 둘을 한꺼번에(`FT.HYBRID`, 8.4+), 그리고 색인이 아예 필요 없는 벡터 셋에 묻는다. 문서의 표현: `FT.HYBRID`는 "Performs hybrid search combining text search and vector similarity with configurable fusion methods", 그리고 "Vector sets are a data type similar to sorted sets, but instead of a score, vector set elements have a string representation of a vector."

공식 문서: [Search and query](https://redis.io/docs/latest/develop/ai/search-and-query/), [Vector search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/), [FT.SEARCH](https://redis.io/docs/latest/commands/ft.search/), [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/), [Vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/).

### 실행

```bash
python3 -m venv .venv && .venv/bin/pip install fastembed redis numpy   # the lab used uv with Python 3.12
.venv/bin/python lab.py   # downloads the 384-dimension embedding model once (65 MB in the fastembed cache), starts and removes its own container
.venv/bin/python extras.py   # FT.AGGREGATE, synonyms, spellcheck, vector types and SVS-VAMANA, Korean with a multilingual model (about 240 MB more in the fastembed cache)
```

출력은 영문 절과 같다(2026-11-07).

`extras.py`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **이 규모에서 색인은 즉시 끝난다.** `FT.CREATE` 직후 두 색인 모두 완료(`percent_indexed 1.0`)였다. 메모 30개 임베딩은 CPU에서 0.1초.
- **전문 검색은 의미가 아니라 단어를 맞춘다.** `failover`와 접두어 `fail*`는 장애 조치 메모 셋을 찾았고 태그와 숫자 범위도 예상대로 걸렀지만, `cache in sync with my database`는 아무것도 못 찾았다. 기본적으로 모든 단어가 들어 있어야 하는데 그런 메모가 없다.
- **KNN은 의미를 맞춘다.** "How do I keep Redis in sync with my Postgres tables?"는 변경 데이터 캡처 메모를 1위로 찾았고(유사도 0.83), "a consumer crashed and left messages unprocessed"는 `XAUTOCLAIM`과 `XNACK` 메모를 찾았다. `FLAT` 벡터 필드의 JSON 색인은 `HNSW`의 해시 색인과 같은 상위 3개를 돌려줬다.
- **필터는 KNN을 좁힌다.** `(@category:{cluster})=>[KNN 3 ...]`는 Sentinel 메모를 클러스터 메모로 바꿨다.
- **FT.HYBRID는 순위 목록 둘을 합친다.** 텍스트 `database`와 "keep a cache consistent with a relational database"의 벡터로 물으니, 텍스트만과 벡터만의 상위 5개가 서로 달랐다. `COMBINE RRF`는 둘의 합집합(결과 10개)을 돌려주고 각 목록의 1위를 맨 위에 뒀다. 결과는 텍스트 부분에 크게 좌우된다.
- **벡터 셋은 색인 없이 같은 이웃을 준다.** 같은 벡터로 `VADD`한 뒤 `VSIM`은 KNN과 같은 상위 3개를 돌려줬고, JSON 속성에 대한 `FILTER '.category == "cluster"'`는 태그 필터와 같은 일을 했다. 벡터 셋은 35,878바이트, 벡터를 담은 해시 30개는 66,237바이트였다.
- **redis-py 8.1.0은 RESP3로 말한다.** `HELLO`가 프로토콜 3을 보고했고, `FT.SEARCH`와 `FT.INFO`가 예전 예제가 파싱하는 평평한 목록이 아니라 맵으로 돌아왔다. 실습은 둘 다 처리한다.
- **FT.AGGREGATE는 묶고 계산한다.** `GROUPBY @category REDUCE COUNT ... REDUCE MAX @year`가 분류별 메모 수와 가장 최근 연도를 돌려줬고, `APPLY strlen(@title)`이 정렬에 쓸 계산 필드를 더했다.
- **동의어는 재검사 뒤에 질의에 반영된다.** "switchover"는 어느 메모에도 없다. `FT.SYNUPDATE idx ha switchover failover promotion` 뒤에는 장애 조치 메모 셋을 찾았고, 그 뒤에 추가한 "promotion" 메모도 찾았다. 첫 실행에서는 등록 직후 보낸 검색이 아무것도 돌려주지 않았다. 기존 문서는 백그라운드에서 다시 검사된다.
- **FT.SPELLCHECK는 색인의 단어로 제안한다.** `failovr evicton replca`에 `failover`, `eviction`, `replica`가 1순위 제안이었고, `failovr`를 그대로 검색하면 아무것도 나오지 않았다.
- **여기서는 작은 벡터 형식도 같은 답을 줬다.** `FLOAT32`·`FLOAT16` HNSW, `INT8` FLAT, `COMPRESSION LVQ8`의 `SVS-VAMANA` 모두 같은 상위 3개를 돌려줬다. `FT.INFO`의 색인 크기(1,724, 956, 406, 1,556 KB)는 벡터 30개에 대한 초기 할당이 대부분이라 벡터당 비용이 아니다. 문서는 "Intel's proprietary LVQ and LeanVec optimizations are not available in Redis Open Source"라고 덧붙인다.
- **한국어는 다국어 모델이 필요하고, 그래도 빗나간다.** `paraphrase-multilingual-MiniLM-L12-v2`로는 장애 조치 시간과 가득 찬 무료 DB에 관한 한국어 질문이 맞는 영어 메모를 1위로 찾았다. 영어 전용 모델은 세 질문 모두 상관없는 메모를 돌려줬다. Postgres 테이블 동기화에 관한 한국어 질문에는 둘 다 변경 데이터 캡처 메모를 찾지 못했다. 메모가 영어라 한국어 단어의 전문 검색은 아무것도 찾지 못했다.

### 미실행 / 주의

- 문서 30개로는 큰 규모의 재현율이나 지연을 말할 수 없고, 작은 영어 모델 하나의 유사도는 품질 지표가 아니다.
- 한국어 텍스트 자체는 색인하지 않았다. 영어 메모에 한국어로 묻는 것만 시험했다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 Docker) |
| 확인한 버전 | Redis 8.10.3 (`redis:8.10.3`), redis-py 8.1.0, fastembed 0.9.1 with BAAI/bge-small-en-v1.5, 2026-11-07 |
