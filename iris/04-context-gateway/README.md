# Context Gateway

[English](#english) | [한국어](#한국어)

## English

**Verified on redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07.**

One Gateway, two upstreams: a Context Surface generated from 30 made-up products in the free database, and the public DeepWiki MCP server. Tool exposure in search mode, so an agent sees two tools and finds the rest by searching.

Official documentation: [Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/)

### Run

```bash
../../cloud/01-free-database/.venv/bin/python seed.py     # 30 product:NNN hashes
# console: New Gateway (Search) > Create Context Surface: entity Product, key product:{id}, Hash,
#   fields id (PK), name (text), category/colour (tag), price/stock (int, numeric)
# console: Add MCP server deepwiki https://mcp.deepwiki.com/mcp, no auth
.venv/bin/python lab.py
# console: Configuration > Edit > Tool exposure: Full, Save; then back to Search
.venv/bin/python exposure.py   # what an agent sees in the current mode
```

Output as it appeared (2026-11-07; service ids and endpoints removed):

```text
1141 ms  tools()
tools the agent sees: ['search_tools', 'run_tool']
  1030 ms  search('black lamps under 100 dollars')
   -> ['products__filter_product']
  1064 ms  search('documentation of a GitHub repository')
   -> ['deepwiki__read_wiki_structure', 'products__expand_results', 'deepwiki__read_wiki_contents']
filter_product input schema keys: ['limit', 'numeric_conditions', 'offset', 'sort_by', 'sort_order', 'tag_conditions']
  2442 ms  call products__filter_product (black lamps, price <= 100)
   -> ToolResult(text='{"count":3,"has_more":false,"limit":10,"offset":0,"results":[{"category":"lamp","colour":"black","name":"black floor lamp","price":29,"stock":23},{"category":"lamp","colour":"black","name":"black desk lamp","price":79,"stock":9},{"category":"lamp","colour":"black","name":"black reading lamp","price":29,"stock":5}],"total_count":3}', data={'count': 3, 'has_more': False, 'limit': 10, 'offset': 0, 'results': [{'category': 'lamp', 'colour': 'black', 'name': 'black floor lamp',
  2390 ms  call products__count_product (function=count)
   -> ToolResult(text='{"function":"count","value":30}', data={'function': 'count', 'value': 30}, is_error=False)
  1505 ms  call deepwiki__read_wiki_structure redis/redis
   -> ToolResult(text='Available pages for redis/redis:\n\n- 1 Overview\n- 2 Redis Core\n  - 2.1 Server Architecture and Lifecycle\n  - 2.2 Event Loop\n  - 2.3 Client Connection Management\n  - 2.4 Networking and Connection Abstraction\n  - 2.5 Command Processing Pipeline\n  - 2.6 Configuration Management\n  - 2.7 Access Control Lists (ACL)\n  - 2.8 Client-Side Caching and Tracking\n- 3 Data Storage and
```

`exposure.py` output as it appeared (2026-11-07):

```text
-- tool exposure: Full
tools() in 1399 ms: 13 tool(s)
   products__count_product                    Count Product records without retrieving individual records. This tool
   products__except_results                   Return the records in the FIRST set that are not in any of the others 
   products__expand_results                   Follow a declared relationship from one set to the related entity and 
   products__filter_product                   Filter Product by one or MORE field conditions in a single call; a rec
   products__get_product_by_id                Get Product by ID using a key lookup. A furniture product. ID field id
   products__intersect_results                Return the records present in EVERY given set (AND) -- the conjunctive
   products__list_product                     List Product, optionally sorted by a numeric field. Valid sort_by fiel
   products__search_product_by_text           Lexical full-text search (not semantic) for Product. By default, resul
   products__summarize_product                Summarize Product numeric fields without retrieving individual records
   products__union_results                    Return the records present in ANY of the given sets (OR), de-duplicate
   deepwiki__ask_wiki_question                Ask any question about a GitHub repository's codebase and get an AI-po
   deepwiki__read_wiki_contents               View documentation about a GitHub repository.
   deepwiki__read_wiki_structure              Get a list of documentation topics for a GitHub repository.

-- tool exposure: Search
tools() in 1531 ms: 2 tool(s)
   search_tools                               Search the managed tools available through this Gateway. Each match is
   run_tool                                   Run one tool returned by search_tools. Identify it by the upstreamId a
```

### What was observed

- **Search mode.** The agent's tool list is just `search_tools` and `run_tool`. "black lamps under 100 dollars" found `products__filter_product`; "documentation of a GitHub repository" found the DeepWiki tools first.
- **Context Surface.** From one entity with six fields the Gateway generated ten tools (count, filter, text search, set operations, relationship expansion and more), each with a JSON Schema the Gateway enforces: wrong argument shapes were refused with `invalid_arguments` and the tool was not called. The filter returned the same three black lamps at or under 00 that a direct scan of the database found. It also added a Search index to the database.
- **MCP server.** DeepWiki's three tools appeared as `deepwiki__*`; `read_wiki_structure` for redis/redis returned its page list through the Gateway.
- **Latency from Korea.** `tools()` 1.1–1.5 s, a search about 1 s, Surface calls about 2.4 s, the DeepWiki call 1.5 s.
- **Full exposure lists every tool.** Switched to **Full** in the console, the Gateway gave the agent 13 tools named `namespace__tool`: ten from the `products` Context Surface and three from DeepWiki. Back in **Search**, the agent saw only `search_tools` and `run_tool`. The console calls Search "Recommended for many tools".
- **Caching and compression are not in the Redis Cloud console.** The Gateway's edit form has name, description and tool exposure only. The docs configure caching and compression with an admin token on the Gateway's administration API, which is how a self-managed deployment is run. Compression would also need a database with JSON and `maxmemory-policy noeviction`, and the free database uses `volatile-lru`.

<img src="../../docs/assets/img/iris/31-gateway-full-exposure.webp" width="1440" height="1040" alt="Context Gateway configuration with tool exposure set to Full: agents see every tool, named namespace__tool" loading="lazy" decoding="async">

Captured 2026-11-07, Redis Cloud free plan.

### Not run / caveats

- `mcp-redis` was not used: the Gateway needs an upstream it can reach from Redis Cloud, and this host does not serve one publicly. The Context Surface covers the "Redis data as tools" part.
- Result caching and compression could not be set from the Redis Cloud console; they were not run.

| | |
|---|---|
| Plan needed | Free (Redis Cloud free database; Iris free messages) |
| Verified on | redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07 |

## 한국어

**확인: redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07.**

게이트웨이 하나에 업스트림 둘. 무료 DB의 가짜 상품 30개로 만든 Context Surface, 그리고 공개 DeepWiki MCP 서버. 도구 노출은 검색 모드라 에이전트는 도구 둘만 보고 나머지는 검색으로 찾는다.

공식 문서: [Context Gateway](https://redis.io/docs/latest/operate/iris/context-gateway/)

### 실행

```bash
../../cloud/01-free-database/.venv/bin/python seed.py     # 30 product:NNN hashes
# console: New Gateway (Search) > Create Context Surface: entity Product, key product:{id}, Hash,
#   fields id (PK), name (text), category/colour (tag), price/stock (int, numeric)
# console: Add MCP server deepwiki https://mcp.deepwiki.com/mcp, no auth
.venv/bin/python lab.py
# console: Configuration > Edit > Tool exposure: Full, Save; then back to Search
.venv/bin/python exposure.py   # what an agent sees in the current mode
```

출력은 영문 절과 같다(2026-11-07).

`exposure.py`의 출력도 영문 절과 같다(2026-11-07).

### 관찰한 것

- **검색 모드.** 에이전트의 도구 목록은 `search_tools`와 `run_tool`뿐이다. "black lamps under 100 dollars"는 `products__filter_product`를, "documentation of a GitHub repository"는 DeepWiki 도구를 먼저 찾았다.
- **Context Surface.** 필드 여섯 개짜리 엔티티 하나에서 게이트웨이가 도구 열 개를 만들었다(개수, 필터, 텍스트 검색, 집합 연산, 관계 확장 등). 각각 게이트웨이가 강제하는 JSON Schema가 있어, 인자 형식이 틀리면 `invalid_arguments`로 거절되고 도구는 호출되지 않았다. 필터는 DB를 직접 훑은 결과와 같은 검은 램프 3개(100달러 이하)를 돌려줬다. DB에 Search 인덱스도 하나 추가됐다.
- **MCP 서버.** DeepWiki 도구 셋이 `deepwiki__*`로 나타났고, redis/redis의 `read_wiki_structure`가 게이트웨이를 거쳐 페이지 목록을 돌려줬다.
- **한국에서의 지연.** `tools()` 1.1–1.5초, 검색 약 1초, Surface 호출 약 2.4초, DeepWiki 호출 1.5초.
- **Full 노출은 모든 도구를 나열한다.** 콘솔에서 **Full**로 바꾸자 게이트웨이가 에이전트에 `namespace__tool` 이름의 도구 13개를 줬다. `products` Context Surface에서 10개, DeepWiki에서 3개. **Search**로 되돌리자 에이전트에는 `search_tools`와 `run_tool`만 보였다. 콘솔은 Search를 "Recommended for many tools"라고 부른다.
- **캐시와 압축은 Redis Cloud 콘솔에 없다.** 게이트웨이 편집 화면에는 이름, 설명, 도구 노출만 있다. 문서는 캐시와 압축을 게이트웨이 관리 API에 관리 토큰으로 설정하는데, 이는 자체 운영 배포의 방식이다. 압축에는 JSON과 `maxmemory-policy noeviction`인 DB도 필요한데, 무료 DB는 `volatile-lru`다.

<img src="../../docs/assets/img/iris/31-gateway-full-exposure.webp" width="1440" height="1040" alt="도구 노출을 Full로 둔 Context Gateway 설정: 에이전트가 namespace__tool 이름의 모든 도구를 본다" loading="lazy" decoding="async">

2026-11-07 캡처, Redis Cloud 무료 플랜.

### 미실행 / 주의

- `mcp-redis`는 쓰지 않았다. 게이트웨이는 Redis Cloud에서 닿는 업스트림이 필요한데, 이 호스트는 공개로 띄우지 않는다. "Redis 데이터를 도구로"는 Context Surface가 맡는다.
- 결과 캐시와 압축은 Redis Cloud 콘솔에서 설정할 수 없어 실행하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(Redis Cloud 무료 DB, Iris 무료 메시지) |
| 확인한 버전 | redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07 |
