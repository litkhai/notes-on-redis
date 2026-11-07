# Research: Redis Iris, Redis vs Valkey / ElastiCache / cloud offerings, alternatives

Public sources only. Every claim read 2026-11-07 unless noted. Collected by a research
agent for the site design; nothing here was run. Figures from vendor blogs are marked as such.

## 1. Redis Iris

### What it is
"Redis Iris" is a **Redis Ltd. product line** — "a suite of managed and self-managed services that give your customers accurate, consistent experiences with your AI agents by providing memories, approved answers, governed access to business data, and turn-by-turn tracing"; "a production-ready context engine for AI agents". [docs](https://redis.io/docs/latest/develop/ai/context-engine/)

- CEO framing: "Iris is a context engine … sits between an agent and the data it needs to act"; "it's not a database. Redis is the database underneath." [launch blog](https://redis.io/blog/context-is-all-you-need/), [Blocks & Files](https://www.blocksandfiles.com/ai-ml/2026/05/18/redis-agentic-ai-flowers-with-iris/5241795)
- Name collisions (unrelated): InterSystems IRIS, a third-party MCP repo "iris-legacy".

### Timeline
- **2026-05-18** — launch blog "Context is all you need: Introducing Redis Iris" (Rowan Trollope). Launch set: Context Gateway (press called it "Context Retriever"), Agent Memory, RDI, Agent Playbooks (described then as semantic caching = LangCache), Redis Search. Context Gateway and Agent Memory "now available in preview". [blog](https://redis.io/blog/context-is-all-you-need/), [May recap](https://redis.io/blog/whats-new-in-two-may-2026-edition/)
- **2026-06-16** — "Getting Started with Redis Iris" tutorial (updated 2026-11-04). [tutorial](https://redis.io/tutorials/getting-started-with-redis-iris/), [GitHub](https://github.com/redis-developer/getting-started-with-redis-iris/)
- **2026-11-04** — "next chapter": six capabilities. [CEO blog](https://redis.io/blog/agents-are-software-introducing-the-next-chapter-of-redis-iris/), [Khadder blog](https://redis.io/blog/the-next-chapter-of-redis-iris-what-agents-need-to-work-in-the-real-world/), [press release (syndicated)](https://www.manilatimes.net/2026/11/05/tmt-newswire/pr-newswire/redis-expands-redis-iris-to-give-ai-agents-the-memory-context-and-messaging-they-need-to-get-to-production/2462106)
- Webinar "Redis Iris Full Spectrum" 2026-11-12 09:00 PST. [product page](https://redis.io/iris/)

### The six capabilities (status = Redis's own label, 2026-11-04)
| Capability | Status | What it does | Docs |
|---|---|---|---|
| Intent Router | GA | embeds query, vector-matches against user-defined intents, returns a target (tool/agent/model); no LLM call at match time | [link](https://redis.io/docs/latest/develop/ai/context-engine/intent-router/) |
| Agent Playbooks | GA | registry of versioned FAQs and Agent Skills agents retrieve semantically; "learning loop" | [link](https://redis.io/docs/latest/develop/ai/context-engine/agent-playbooks/) |
| Agent Memory | GA | session + long-term memory, MemoryETL from docs, hierarchies, audit/provenance, PII forgetting | [link](https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/) |
| Context Gateway | GA | single MCP endpoint over many MCP servers + "Context Surfaces" that turn Redis data into tools; credential mgmt; tool search mode; result cache/compression | [link](https://redis.io/docs/latest/develop/ai/context-engine/context-gateway/) |
| Lens | beta | OpenTelemetry-based turn-by-turn tracing of retrievals, memory recalls, prompt assembly, model/tool calls | [link](https://redis.io/docs/latest/develop/ai/context-engine/lens/) |
| Agent Mesh | beta | resumable event streams (durable SSE, A2A task store) on Redis; needs Redis 8.6.2+ and Python 3.11+; "Cloud, Enterprise, failover recovery, and sustained capacity remain unqualified for this beta" | [link](https://redis.io/docs/latest/develop/ai/context-engine/agent-mesh/) |

Third-party confirmation of 4 GA / 2 beta: [Unite.ai](https://www.unite.ai/redis-broadens-iris-with-agent-routing-observability-and-messaging/).

### Where it runs
- Managed on Redis Cloud; every service also self-managed on Kubernetes via one `redis-iris` Helm chart (1.0.0, `https://helm.redis.io/ai`), which needs "a Redis Iris suite license" from sales; Helm 4 and FIPS not supported in 1.0 (planned 1.1). [operate](https://redis.io/docs/latest/operate/iris/), [self-managed](https://redis.io/docs/latest/operate/iris/self-managed/)
- Services run against a Redis database; the console flow defaults to the Redis Cloud free 30 MB DB. Agent Memory on Redis Cloud "doesn't support Redis Flex databases, databases using AWS PrivateLink connectivity, Active-Active databases, or databases with the default user turned off". [create service](https://redis.io/docs/latest/operate/iris/agent-memory/create-service/)
- Platforms listed on the product page: Redis Cloud, Redis Software, Redis Open Source ("Redis 8.8"); AWS, Azure (via Azure Managed Redis), Google Cloud marketplace. [iris page](https://redis.io/iris/)

### Relationship to LangCache / Agent Memory Server / RDI
- AI docs index: "Context Engine (Redis Iris) includes four services": LangCache, Redis Agent Memory, Context Gateway, Data Integration. [docs](https://redis.io/docs/latest/develop/ai/)
- **LangCache vs Agent Playbooks is muddled on redis.io**: the May blog describes "Agent Playbooks" as semantic caching; the June tutorial's Playbooks row links to `redis.io/langcache/` and installs `pip install langcache`; the November Playbooks docs describe a FAQ/skills registry, while LangCache docs still exist and say "currently in preview: Public preview on Redis Cloud; Self-managed … private preview". Treat as two services. [LangCache docs](https://redis.io/docs/latest/develop/ai/langcache/), [LangCache on Redis Cloud](https://redis.io/docs/latest/operate/rc/langcache/create-service/)
- `redis/agent-memory-server` (Apache-2.0) is the OSS research foundation (V0) and "serves as an audit surface for the shipping Redis Agent Memory REST API". [GitHub](https://github.com/redis/agent-memory-server)
- RDI 1.18 (May 2026): Flink-based processor ("up to 3.4x higher throughput" — vendor figure), Snowflake source preview. [May recap](https://redis.io/blog/whats-new-in-two-may-2026-edition/)
- The June tutorial installs `redis-context-retriever` → confirms the Context Retriever → Context Gateway rename.

### SDKs / APIs
- Python: `pip install 'redis-iris>=1.0.0'` — one package per Iris product plus the `iris` CLI. PyPI latest 1.0.1 (2026-11-04), Apache-2.0, Python ≥3.11. Modules `redis_iris.agent_memory`, `.agent_playbooks`, `.intent_router`, `.lens`, `.agent_mesh.{a2a,fastapi_sse}`, `redis_iris.ContextGateway`. [PyPI](https://pypi.org/project/redis-iris/)
- JS: `@redis-iris/intent-router`, `@redis-iris/context-gateway` (names from redis.io docs; npm returned 403 today).
- REST API for all services (`/iris/data/v1/agent-memory/stores/{id}/...`, `/iris/data/v1/intent/routers/{id}/...`), `iris` CLI, MCP endpoints for Agent Memory, Agent Playbooks, Context Gateway. [docs](https://redis.io/docs/latest/develop/ai/context-engine/)
- Older per-service packages in the June tutorial: `langcache`, `redis-agent-memory`, `redis-context-retriever`.

### Pricing / availability
- "Get started with 5,000 free messages" (`redis.io/try-free/?rcplan=iris`). [CEO blog](https://redis.io/blog/agents-are-software-introducing-the-next-chapter-of-redis-iris/)
- Product page → `/pricing/#iris` and "Talk to sales"; the pricing page exposed no Iris rate card. [pricing](https://redis.io/pricing/)
- Self-managed = license from sales. No waitlist seen for GA services.

### Redis for AI outside Iris
- Redis 8.0 (GA 2025-05-01): vector sets added as beta; modules merged into one "Redis Open Source" distribution. [8.0](https://redis.io/docs/latest/develop/whats-new/8-0/), [AGPL blog](https://redis.io/blog/agplv3/), [vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/)
- Redis Open Source 8.8 GA (May 2026): Array data type, INCREX, XNACK, hash field notifications, FT.HYBRID improvements, JSON FP precision. [8.8](https://redis.io/docs/latest/develop/whats-new/8-8/)
- Official MCP server `redis/mcp-redis` (MIT, stdio only today). [GitHub](https://github.com/redis/mcp-redis), [docs](https://redis.io/docs/latest/integrate/redis-mcp/)
- RedisVL MCP: `pip install redisvl[mcp]`, tools `search-records`/`upsert-records`. [blog](https://redis.io/blog/connect-your-redis-index-to-ai-agents-with-redisvl-mcp/)
- Vector search in Redis Search: FLAT and HNSW, KNN/range/filters, over hashes or JSON. [AI docs](https://redis.io/docs/latest/develop/ai/)

## 2. Redis vs Valkey vs ElastiCache vs cloud offerings

### Licensing history (Redis)
- 2024-03-20: dual RSALv2 / SSPLv1 "starting with Redis 7.4"; neither OSI-approved; ≤7.2 stays BSD-3. [blog](https://redis.io/blog/redis-adopts-dual-source-available-licensing/)
- 2025-05-01: AGPLv3 added "starting with Redis 8". [blog](https://redis.io/blog/agplv3/), [The Register](https://www.theregister.com/2025/05/01/redis_returns_to_open_source/)
- Matrix: Redis Open Source ≥8.0 tri-licensed RSALv2 / SSPLv1 / AGPLv3; 7.4.x RSALv2 or SSPLv1; ≤7.2 BSD-3; modules tri-licensed from 8; Redis Software/Cloud commercial; Redis Insight SSPLv1; redis-vl-python MIT. [licenses](https://redis.io/legal/licenses/)

### Valkey
- Linux Foundation, announced 2024-03-28, fork of Redis 7.2.4, BSD-3; backers AWS, Google Cloud, Oracle, Ericsson, Snap. [LF](https://www.linuxfoundation.org/press/linux-foundation-launches-open-source-valkey-community), [COPYING](https://github.com/valkey-io/valkey/blob/unstable/COPYING)
- Versions (valkey.io/download): 9.1.3 (2026-10-26), 9.0.7, 8.1.11, 8.0.12, 7.2.15; 9.2.0-rc1 (2026-09-16). [download](https://valkey.io/download/)
- 9.0 (2025-10-21): atomic slot migration, hash field expiration, numbered DBs in cluster mode, 2,000-node clusters (vendor figures). [blog](https://valkey.io/blog/introducing-valkey-9/)
- 9.1 (2026-05-19): new IO threading model, Lua as a module, per-database ACLs, CLUSTERSCAN, JSON logging. [blog](https://valkey.io/blog/valkey-9-1-delivers-improvements-in-security-performance-and-more/)
- Modules (BSD-3): [valkey-json](https://github.com/valkey-io/valkey-json), [valkey-bloom](https://github.com/valkey-io/valkey-bloom), [valkey-search](https://github.com/valkey-io/valkey-search/releases) (1.2.1 stable 2026-07-07 needs core 9.0.1+; 1.3.0-rc2 adds FT.HYBRID, BM25STD).
- Governance post "Nobody Owns Valkey" (2026-10-15). [blog index](https://valkey.io/blog/)

### Amazon ElastiCache / MemoryDB
- Engines: Valkey, Redis OSS, Memcached. Valkey versions 7.2.6 → 9.1 (8.2 adds vector search; 9.0 adds Multi-AZ transactional-log durability, full-text/hybrid search). Redis OSS capped at 7.1; v4/v5 standard support ended 2026-01-31, v6 ends 2027-01-31. [engine versions](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/engine-versions.html)
- Valkey pricing: serverless "33% lower", node-based "20% lower" than Redis OSS; minimum serverless storage 100 MB vs 1 GB. [announcement](https://aws.amazon.com/about-aws/whats-new/2024/10/amazon-elasticache-valkey/), [pricing](https://aws.amazon.com/elasticache/pricing/)
- MemoryDB: durable Multi-AZ transaction log, 99.99%, vector search; Valkey flavour 30% cheaper. [MemoryDB](https://aws.amazon.com/memorydb/)

### Google Memorystore
- Memorystore for Valkey: 7.2, 8.0, 9.0, 9.1 (default 9.1); subset of commands. [versions](https://docs.cloud.google.com/memorystore/docs/valkey/supported-versions), [overview](https://docs.cloud.google.com/memorystore/docs/valkey/product-overview)
- Memorystore for Redis: 7.2 default, down to 3.2. [versions](https://docs.cloud.google.com/memorystore/docs/redis/supported-versions)

### Azure
- Azure Managed Redis: "based on the Redis Enterprise software"; Redis 7.4.x; tiers Memory/Balanced/Compute/Flash Optimized; active geo-replication; JSON/Search/Bloom/TimeSeries on in-memory tiers. [overview](https://learn.microsoft.com/en-us/azure/redis/overview)
- Azure Cache for Redis retirement: Basic/Standard/Premium 2028-09-30; Enterprise tiers 2027-03-31. [FAQ](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/retirement-faq)

### Redis's own compare page vs Valkey
Claims Valkey lacks query engine/vector/time series, Active-Active, Flex tiering, 99.999% SLA; concedes "comparable performance since Valkey 8.0". Several claims are contradicted by the Valkey modules above. [compare](https://redis.io/compare/valkey/)

### Feature matrix (draft for the site)
| | Redis Open Source 8.x | Redis Cloud / Software | Valkey 9.x | ElastiCache for Valkey | ElastiCache for Redis OSS | Azure Managed Redis | Memorystore for Valkey |
|---|---|---|---|---|---|---|---|
| Vendor | Redis Ltd. | Redis Ltd. | Linux Foundation | AWS | AWS | Microsoft (Redis Enterprise inside) | Google |
| License | RSALv2 / SSPLv1 / AGPLv3 | Commercial | BSD-3 | managed | managed (engine ≤7.1) | managed | managed |
| JSON | built-in | yes | valkey-json | not explicit for Valkey | yes (6.2+) | yes | not stated |
| Search / vector | built-in + vector sets (beta) | yes | valkey-search | vector 8.2+, hybrid 9.0+ | not listed | yes (in-memory tiers) | not stated |
| TimeSeries | built-in | yes | none found | none | none | yes | none |
| Probabilistic | built-in | yes | valkey-bloom | Bloom (8.1+) | none | yes | none |
| Active-Active | no | yes (Pro) | no | no (Global Datastore = cross-region replica; not verified) | — | active geo-replication | no |
| Auto-tiering / SSD | no | Redis Flex / Auto Tiering | no | data tiering (6.2 doc) | yes | Flash Optimized | not stated |
| SLA | none | 99.999% Pro; 99.99% Essentials | none | AWS SLA (not fetched) | same | Azure SLA (not fetched) | not fetched |
| Multi-cloud | n/a | AWS, GCP, Azure | n/a | AWS | AWS | Azure | GCP |
| Pricing model | free | hourly tiers | free | nodes or serverless | nodes or serverless | SKU hourly | GB-month (unverified) |

## 3. Alternatives
- **Dragonfly** — thread-per-core, ~185 commands (≈Redis 5 API), Dragonfly Source-Available License (DSAL) from v2.1. [GitHub](https://github.com/dragonflydb/dragonfly), [LICENSE](https://github.com/dragonflydb/dragonfly/blob/main/LICENSE.md)
- **KeyDB** — Snap fork, multithreaded, BSD-3; last release 6.3.4 on 2024-10-30. [repo](https://github.com/Snapchat/KeyDB), [releases](https://github.com/Snapchat/KeyDB/releases)
- **Garnet** — Microsoft Research, .NET, MIT, RESP-compatible, Tsavorite tiered storage. [repo](https://github.com/microsoft/garnet)

## Open questions
1. ElastiCache Serverless Redis OSS rates — two fetches of the pricing page disagreed; verify the table directly.
2. Iris per-message pricing beyond "5,000 free messages" — no rate card found; "message" undefined.
3. LangCache vs Agent Playbooks — redis.io contradicts itself; treat as two services.
4. GA wording — per-service docs carry no "GA" badge; GA comes from the CEO blog and press release.
5. Garnet / Dragonfly latest versions — GitHub release pages gave partial data.
6. Azure first-party Valkey — only third-party sources say none.
7. Memorystore for Valkey SLA and pricing — not on fetched Google pages.
8. Redis marketing figures ("43% of enterprise AI agent stacks", "90% token savings") are unverified vendor claims.
