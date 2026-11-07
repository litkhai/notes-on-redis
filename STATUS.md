# STATUS.md

## Tracks

| Track | Run against a real account or container? |
|---|---|
| [`design/`](./design) | n/a — design v0 and two research notes, public pages read 2026-11-07; nothing run |
| `setup/` | Run 2026-11-07: Redis 8.10.3 + Redis Insight 3.8.0 in Docker (ports 16379/15540), redis-py 6.1.1 and node-redis 6.3.1 smoke tests against local and the Redis Cloud free DB. The free plan cannot enable TLS (API error recorded) |
| `local/` | `01` (image contents, io-threads) and `02` (data types tour incl. Array and vector sets) run 2026-11-07 on Redis 8.10.3; `03` search/vector not started |
| `cloud/` | `01` free database run 2026-11-07 (Redis 8.6.2, Seoul): connection and memory limits enforced, 100 ops/s not; `02` console walkthrough captured (31 screens, masked). Free database `notes-on-redis-free` kept for Iris; `04` REST API run 2026-11-07 on the free plan (reads, a database update through a task, the max-databases refusal arriving as a task error); API user key `notes-on-redis-lab` still exists, delete it when no longer needed. Open: [#8](https://github.com/litkhai/notes-on-redis/issues/8) budget, [#12](https://github.com/litkhai/notes-on-redis/issues/12) budget |
| `enterprise/` | `01` run 2026-11-07: Redis Software 8.2.6-25 single node in Docker (trial: 30 days, 4 shards, read from `/v1/license`), proxy policies, multi-key behind the DMC proxy, shard limit, re-sharding 2→4 in ~6 s. `02` RDI and `03` operator wait for permission to install kind and the RDI Helm chart ([#9](https://github.com/litkhai/notes-on-redis/issues/9)) |
| `iris/` | `01`–`05` run 2026-11-07 on the free plan: Agent Memory (`notes-on-redis-memory`: summaries, shared namespace, PII detectors on, MemoryETL extractor, forget), Intent Router (`notes-on-redis-router`), Context Gateway (`notes-on-redis-gateway`: Context Surface over `product:*` + DeepWiki MCP), Agent Playbooks (`notes-on-redis-support`, 4 FAQs). All endpoints in us-east-1; keys expire 2026-12-07. Message count not shown anywhere. `06` run 2026-11-07: Agent Mesh on local Redis 8.10.3 (SSE and A2A resumed on a second replica; with SDK defaults a dead producer is never reported because redis-py 8.1.0's 5 s socket timeout is shorter than the 15 s blocking read: set `REDIS_SOCKET_TIMEOUT`), Lens SDK against a loopback receiver. Lens itself needs an Essentials or Pro records database: **New Lens** is disabled on the free plan ([#8](https://github.com/litkhai/notes-on-redis/issues/8)). **The Iris services hold 28 of the free DB's 30 connections** (Redis alert email at 93.33%, 2026-11-07) and 16.7 of its 30 MB. |
| `compare/` | `01` run 2026-11-07: Redis 8.10.3 vs Valkey 9.1.3 and valkey-bundle 9.1 (commands, data types, memory, benchmarks); `matrix.md` rebuilt with a source per cell; `02` ElastiCache Serverless for Valkey run 2026-11-07 and deleted. Licence timeline and alternatives still planned |
| `deep-dive/` | `01`–`04` run 2026-11-07 on Redis 8.10.3: io-threads 1/2/4/8, RDB fork/COW, AOF fsync, multi-part AOF, BACKUP + preload-file restore, partial/full resync, WAIT per connection, Sentinel failover (4.4 s with IPs, 284 s with container names), six-node cluster and atomic slot migration. `05`–`08` run 2026-11-07 on Redis 8.10.3: eviction policies at 16 MB (LFU kept both hot groups, LRM kept only the rewritten keys), `HOTKEYS`, client-side caching with redis-py 6.1.1 (1 server GET for 1,001 reads) and broadcast mode, Streams (`XAUTOCLAIM`, `XACKDEL`, `IDMP`, `XNACK`), Functions with `FCALL_RO`, ACL `%R~`/`%W~`, selectors, and module commands inside `@write`. |
| [`docs/`](./docs) | Live at https://redis.litkhai.dev (Vercel, deploys on push to `main`); seven languages (#22); `/cloud/` and the ElastiCache part of `/compare/` have content, the rest are stubs. Pages redirect stubs not added yet: [#13](https://github.com/litkhai/notes-on-redis/issues/13) |

## CI

`checks` on pull requests: `docs` (`scripts/check-docs.py`), `syntax`, `secrets`
(gitleaks with `.gitleaks.toml`, full history), `hygiene`. The same checks run on staged
files in `.githooks/pre-commit` — enable once per clone with `git config core.hooksPath .githooks`.
`pages.yml` is not added until the Vercel host exists.

## Budget spent

| Date | What | Amount |
|---|---|---|
| 2026-11-07 | Redis Cloud free database, Seoul (`cloud/01`, `cloud/02`) | $0 |
| 2026-11-07 | ElastiCache Serverless for Valkey, Seoul, ~31 min (`compare/02`) | ≈ $0.05 by the price list; billed amount not visible yet |

## Open decisions

[`design/DESIGN.md`](./design/DESIGN.md) §8 — Essentials now or later ([#8](https://github.com/litkhai/notes-on-redis/issues/8)), Pro and ElastiCache ([#12](https://github.com/litkhai/notes-on-redis/issues/12)), Vercel timing ([#13](https://github.com/litkhai/notes-on-redis/issues/13)), Skeleton with every lab directory: [#1](https://github.com/litkhai/notes-on-redis/issues/1).

How an agent picks up an issue: [`design/AGENT-GUIDE.md`](./design/AGENT-GUIDE.md).
