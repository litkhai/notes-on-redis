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

### What was observed

- **Search mode.** The agent's tool list is just `search_tools` and `run_tool`. "black lamps under 100 dollars" found `products__filter_product`; "documentation of a GitHub repository" found the DeepWiki tools first.
- **Context Surface.** From one entity with six fields the Gateway generated ten tools (count, filter, text search, set operations, relationship expansion and more), each with a JSON Schema the Gateway enforces: wrong argument shapes were refused with `invalid_arguments` and the tool was not called. The filter returned the same three black lamps at or under 00 that a direct scan of the database found. It also added a Search index to the database.
- **MCP server.** DeepWiki's three tools appeared as `deepwiki__*`; `read_wiki_structure` for redis/redis returned its page list through the Gateway.
- **Latency from Korea.** `tools()` 1.1–1.5 s, a search about 1 s, Surface calls about 2.4 s, the DeepWiki call 1.5 s.

### Not run / caveats

- `mcp-redis` was not used: the Gateway needs an upstream it can reach from Redis Cloud, and this host does not serve one publicly. The Context Surface covers the "Redis data as tools" part.
- Result caching and compression were left off; full (non-search) exposure was not tried.

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
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **검색 모드.** 에이전트의 도구 목록은 `search_tools`와 `run_tool`뿐이다. "black lamps under 100 dollars"는 `products__filter_product`를, "documentation of a GitHub repository"는 DeepWiki 도구를 먼저 찾았다.
- **Context Surface.** 필드 여섯 개짜리 엔티티 하나에서 게이트웨이가 도구 열 개를 만들었다(개수, 필터, 텍스트 검색, 집합 연산, 관계 확장 등). 각각 게이트웨이가 강제하는 JSON Schema가 있어, 인자 형식이 틀리면 `invalid_arguments`로 거절되고 도구는 호출되지 않았다. 필터는 DB를 직접 훑은 결과와 같은 검은 램프 3개(100달러 이하)를 돌려줬다. DB에 Search 인덱스도 하나 추가됐다.
- **MCP 서버.** DeepWiki 도구 셋이 `deepwiki__*`로 나타났고, redis/redis의 `read_wiki_structure`가 게이트웨이를 거쳐 페이지 목록을 돌려줬다.
- **한국에서의 지연.** `tools()` 1.1–1.5초, 검색 약 1초, Surface 호출 약 2.4초, DeepWiki 호출 1.5초.

### 미실행 / 주의

- `mcp-redis`는 쓰지 않았다. 게이트웨이는 Redis Cloud에서 닿는 업스트림이 필요한데, 이 호스트는 공개로 띄우지 않는다. "Redis 데이터를 도구로"는 Context Surface가 맡는다.
- 결과 캐시와 압축은 껐다. 전체(비검색) 노출은 시험하지 않았다.

| | |
|---|---|
| 필요한 플랜 | Free(Redis Cloud 무료 DB, Iris 무료 메시지) |
| 확인한 버전 | redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07 |
