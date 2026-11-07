# Research: Redis Open Source, Redis Software / Redis Cloud, Redis Cloud pricing

Public sources only. Every claim read 2026-11-07. Collected by a research agent for the site
design; nothing here was run. Vendor performance figures are marked as such.

## 1. Redis Open Source

### Version / release train
- Latest GA **8.10.3** (2026-10-26); same-day patches 8.8.4, 8.6.8, 8.4.8, 8.2.11, 7.4.12, 7.2.17 (cluster-bus PUBLISH >4 GB overflow). Pre-release **8.12-rc2** (2026-11-01). **No 9.x exists.** [GitHub releases](https://api.github.com/repos/redis/redis/releases?per_page=15), [what's new index](https://redis.io/docs/latest/develop/whats-new/)
- Release notes live on GitHub only. [note](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/)

### License
- 8.x tri-licensed RSALv2 / SSPLv1 / AGPLv3; modules are "integral components" under the same tri-license and share the Redis version number since 8. [licenses](https://redis.io/legal/licenses/)
- "Redis Community Edition" → "Redis Open Source" with 8.0 GA (2025-05-01). [8.0 GA blog](https://redis.io/blog/redis-8-ga/)

### Bundled in Redis 8 ("One Redis")
- 8.0.0 merged Redis Stack + CE: Search (Query Engine), JSON, Time series, five probabilistic types (Bloom, Cuckoo, CMS, Top-k, t-digest), **Vector set [beta]**; `redis-full.conf`; new ACL categories `@search @json @timeseries @bloom @cuckoo @cms @topk @tdigest` (also folded into `@read/@write` — can break `+@all -@write` rules); new I/O threading; `HGETDEL/HGETEX/HSETEX`. [8.0 release notes](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/)
- 8.0 vendor figures: up to 87% lower command latency, 18% faster replication, 35% replica memory saving; io-threads default 1, 8 threads on multi-core Intel "up to 112%". [8.0 what's new](https://redis.io/docs/latest/develop/whats-new/8-0/), [GA blog](https://redis.io/blog/redis-8-ga/)
- Vector sets still beta: `VADD VSIM VREM VEMB VCARD VDIM VINFO VLINKS VRANDMEMBER VGETATTR VSETATTR`, HNSW, `VSIM … FILTER`. [vector sets](https://redis.io/docs/latest/develop/data-types/vector-sets/)

### Per-minor changes (official what's-new pages)
- **8.2** — `XDELEX`, `XACKDEL`, `CLUSTER SLOT-STATS`, `VSIM … IN`, new `BITOP` ops, OVERWRITTEN/TYPE_CHANGED keyspace events, SVS-VAMANA vector compression. [8.2](https://redis.io/docs/latest/develop/whats-new/8-2/)
- **8.4** — `CLUSTER MIGRATION` atomic slot migration, `DELEX`, `DIGEST`, SET CAS extensions, `MSETEX`, `XREADGROUP … CLAIM`, `FT.HYBRID` (RRF/linear), AOF auto-repair, SIMD for BITCOUNT/HLL/VADD/VSIM, command `lookahead` prefetch, BM25STD default, `search-io-threads`. [8.4](https://redis.io/docs/latest/develop/whats-new/8-4/)
- **8.6** — stream idempotency (`XADD … IDMP/IDMPAUTO`), `volatile-lrm`/`allkeys-lrm` eviction, `HOTKEYS`, TLS cert-based client auth, TS NaN support, key memory histograms, per-slot stats, diskless replication without RDB compression. [8.6](https://redis.io/docs/latest/develop/whats-new/8-6/)
- **8.8** — **Array** type, hash field keyspace notifications, `INCREX`, `XNACK`, ZUNION/ZINTER `COUNT`, `JSON.SET FPHA`, `FT.PROFILE HYBRID`, five RCE CVEs fixed. [8.8](https://redis.io/docs/latest/develop/whats-new/8-8/)
- **8.10** — compact hashes + `HIMPORT`, **`BACKUP` command family** (online backup/restore on multi-part AOF; restore via `preload-file aof:<manifest>`), `LMOVEM/BLMOVEM`, `SUNIONCARD/SDIFFCARD`, `XREAD MAXCOUNT/MAXSIZE`, `FT.ALIASLIST`, `TS.NRANGE/TS.READ/TS.QUERYLABELS`, standalone redis-cli, `--cluster reshard/rebalance` via atomic slot migration. [8.10](https://redis.io/docs/latest/develop/whats-new/8-10/), [persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- **8.12 (RC)** — roaring bitmaps, per-member set expiration (`SEXPIRE`, `STTL`), `BLESS` pin from eviction, SQ8 vector compression. [GitHub releases](https://api.github.com/repos/redis/redis/releases?per_page=15)

### Architecture facts for the deep-dive pages
- **Threading**: "Redis is mostly single threaded"; `io-threads` for socket I/O and parsing; enable only with ≥4 cores, leave one spare (4→3, 8→7). Defaults `maxmemory-policy noeviction`, `appendfsync everysec`. [redis.conf](https://raw.githubusercontent.com/redis/redis/unstable/redis.conf)
- **Persistence**: RDB fork/COW snapshot (`save 60 1000`, `BGSAVE`, `dump.rdb`); AOF `always/everysec/no`; multi-part AOF since 7.0 (`appenddirname`); AOF wins at restart when both on; `BACKUP` since 8.10. [persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- **Replication**: async; replication ID + offset; `PSYNC` partial from backlog else full RDB; diskless (`repl-diskless-sync`); `replica-read-only`; `WAIT` ≠ CP; `min-replicas-to-write/max-lag`; replicas ignore `maxmemory`. [replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
- **Sentinel**: port 26379; ≥3 instances; `sentinel monitor <name> <ip> <port> <quorum>`; quorum detects, majority fails over. [sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
- **Cluster**: 16384 slots, `CRC16(key) mod 16384`, hash tags, bus port +10000, `-MOVED`/`-ASK`, `NODE_TIMEOUT`, minority stops writes. [cluster spec](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- **Eviction**: `maxmemory`; policies noeviction / allkeys-{lru,lrm,lfu,random} / volatile-{lru,lrm,lfu,random,ttl}; approximated LRU `maxmemory-samples 5`; LFU since 4.0; LRM since 8.6. [eviction](https://redis.io/docs/latest/develop/reference/eviction/)
- **Client-side caching**: server tracking + invalidation push; redis-py 5.1.0, Jedis 5.2.0, node-redis 5.1.0, go-redis 9.22.0; not for FT.*/TS/probabilistic. [client-side caching](https://redis.io/docs/latest/develop/clients/client-side-caching/)
- **Streams**: IDs `<ms>-<seq>`; consumer groups XGROUP/XREADGROUP/XACK/XPENDING/XAUTOCLAIM; MAXLEN/MINID `~`. [streams](https://redis.io/docs/latest/develop/data-types/streams/)
- **Functions**: since 7.0, `FUNCTION LOAD` (`#!lua name=mylib`), `FCALL/FCALL_RO`, persisted + replicated, Lua 5.1 only, load on every master in Cluster. [functions](https://redis.io/docs/latest/develop/programmability/functions-intro/)
- **ACL**: since 6; `user default on nopass ~* &* +@all`; `%R~ %W~` (7.0), `&` pub/sub (6.2, `resetchannels` default 7.0), selectors (7.0), `+config|get`, SHA-256 passwords, `aclfile`; 8.8 allows `#` comments. [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/)

## 2. Redis Software (self-managed) and Redis Cloud — differentiators
- **Redis Software 8.2.x** — 8.2.0-25 GA July 2026 (database-scoped management roles, data-path command auditing, FIPS 140-3); 8.2.6-25 (Oct 2026) adds Redis DB 8.8, Search on Flex (preview), SSE-C. Supports DB versions 8.8 … 6.2. [8.2 release notes](https://redis.io/docs/latest/operate/rs/release-notes/rs-8-2-releases/), [index](https://redis.io/docs/latest/operate/rs/release-notes/)
- **Active-Active (CRDT)** — multi-primary across ≥2 clusters, syncer + backlog, strong eventual consistency with vector clocks, optional causal consistency; data only (no config/Lua). [RS](https://redis.io/docs/latest/operate/rs/databases/active-active/). On Redis Cloud **Pro only**, ≤10 regions, memory up to 4× dataset, eviction at 80%, 99.999% with ≥3-AZ regions; only JSON and Search supported on A-A. [RC](https://redis.io/docs/latest/operate/rc/databases/active-active/), [advanced capabilities](https://redis.io/docs/latest/operate/rc/databases/configuration/advanced-capabilities/)
- **Redis Flex / Auto Tiering** — Flex (successor to Auto Tiering / Redis on Flash) GA in RS 8.0.2; tiers keys and values to SSD; Speedb engine; RAM ≥10% (recommend ≥20%); local NVMe/SATA only, ~3× flex memory; no Active-Active or Time series on Flex; Cloud needs 8.2+. [flash](https://redis.io/docs/latest/operate/rs/databases/flash/), [solutions/flex](https://redis.io/solutions/flex/), [calculator](https://redis.io/pricing/calculator/)
- **SLA** — Redis Cloud SLA: Active-Active 99.999% (Pro/Annual), Multi-AZ 99.99% (Pro/Annual), Standard 99.9%; replication required, ≥24 h deployed; RDI API 99.9%. [SLA](https://redis.io/legal/redis-cloud-service-level-agreement/), [pricing](https://redis.io/pricing/), [architecture](https://redis.io/technology/redis-enterprise-cluster-architecture/)
- **Proxy / sharding** — one multi-threaded DMC proxy per node, single endpoint; policies `single` / `all-master-shards` / `all-nodes`; min 2 shards, multiples only; standard or regex hashing (≤32 rules); recommend clustering above 25 GB; cross-slot only for DEL/MSET/MGET/EXISTS/UNLINK/TOUCH. [proxy policy](https://redis.io/docs/latest/operate/rs/databases/configure/proxy-policy/), [clustering](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering/)
- **Multi-tenancy / HA** — many databases per cluster and node, isolated; rack-zone awareness; Sentinel-compatible discovery service. [architecture](https://redis.io/technology/redis-enterprise-cluster-architecture/), [durability-ha](https://redis.io/docs/latest/operate/rs/databases/durability-ha/)
- **RBAC / LDAP / TLS** — cluster vs database roles; LDAP groups → roles; TLS client, Replica Of, A-A sync, internode. [access control](https://redis.io/docs/latest/operate/rs/security/access-control/), [LDAP](https://redis.io/docs/latest/operate/rs/security/access-control/ldap/), [TLS](https://redis.io/docs/latest/operate/rs/security/encryption/tls/)
- **Redis Insight** — v3.8.0 (July 2026), SSPL; Browser, Profiler, CLI, Workbench, DB analysis, Streams UI, Slow log, RDI, Copilot. [insight](https://redis.io/docs/latest/develop/tools/insight/), [release notes](https://redis.io/docs/latest/develop/tools/insight/release-notes/)
- **RDI** — CDC into Redis, at-least-once, ~10k rec/s per core (vendor); sources Oracle, MariaDB, MongoDB, MySQL, PostgreSQL, Supabase, SQL Server, Spanner, AlloyDB, Aurora, Neon, Snowflake (preview); managed RDI on Redis Cloud targets **Pro**. Latest **2.2.1 (Nov 2026)**; 2.0.0 (Sep 2026) multi-source, Flink processor. [RDI](https://redis.io/docs/latest/integrate/redis-data-integration/), [release notes](https://redis.io/docs/latest/integrate/redis-data-integration/release-notes/)
- **Kubernetes operator** — CRDs REC, REDB, REAADB, RERC; Helm / OLM; operator 8.2.6 train. [k8s](https://redis.io/docs/latest/operate/kubernetes/), [release notes](https://redis.io/docs/latest/operate/kubernetes/release-notes/)
- **Plan comparison** — Essentials free 30 MB / 30 connections; paid Essentials 250 MB–12 GB; Essentials Flex 1–100 GB; Pro up to 50 TB. Free: RBAC+password+TLS in transit; paid Essentials adds TLS auth; Pro adds encryption at rest + private connectivity. REST API not on free. Pro-only: dedicated accounts, Active-Active. [subscriptions](https://redis.io/docs/latest/operate/rc/subscriptions/)

## 3. Redis Cloud pricing (budget)

### Headline ([pricing page](https://redis.io/pricing/))
- Free $0, 30 MB, shared, one DB, community support.
- Essentials from $0.007/h, "$5/month" minimum, 250 MB–100 GB, SAML SSO, RBAC, encryption in transit and at rest, Flex "at 10% RAM cost", up to 99.99%, basic support.
- Pro from $0.014/h, **minimum $200/month**, **"First $200 free"**, unlimited RAM, multiple DBs, dedicated, Active-Active, private connectivity, RDI, Flex, up to 99.999%.

### Essentials monthly, AWS (pricing page embedded data)
Columns: no replication / +persistence / single-zone replication / single-zone + persistence / multi-zone / multi-zone + persistence.

**us-east-1**
| Size | No rep | +Persist | 1-zone rep | 1-zone+persist | Multi-zone | Multi-zone+persist |
|---|---|---|---|---|---|---|
| 250 MB | $5 | $6 | $7 | $8 | $9 | $10 |
| 1 GB | $18 | $20 | $20 | $22 | $22 | $25 |
| 2.5 GB | $36 | $40 | $40 | $44 | $52 | $58 |
| 5 GB | $70 | $77 | $77 | $85 | $100 | $110 |
| 12 GB | $175 | $193 | $180 | $198 | $234 | $258 |

**ap-northeast-2 (Seoul)** — multi-zone columns empty on the page
| Size | No rep | +Persist | 1-zone rep | 1-zone+persist |
|---|---|---|---|---|
| 250 MB | $6 | $7 | $8 | $10 |
| 1 GB | $22 | $24 | $24 | $27 |
| 2.5 GB | $44 | $48 | $48 | $53 |
| 5 GB | $85 | $93 | $93 | $103 |
| 12 GB | $212 | $234 | $218 | $240 |

**Essentials Flex** — six AWS regions only (us-east-1, eu-west-1, ap-south-1, us-west-2, eu-central-1, ap-southeast-1); **Seoul not listed**. Singapore no-rep / 1-zone+persist: 1 GB $7/$8, 2.5 GB $17/$19, 5 GB $32/$38, 12 GB $75/$90, 25 GB $157/$188, 50 GB $313/$375, 100 GB $625/$750.

Plan size **includes replication**: with replication on, usable dataset is half (1 GB plan → 512 MB). [HA doc](https://redis.io/docs/latest/operate/rc/databases/configuration/high-availability/)

### Essentials limits ("updated December 2025")
| Plan | 30 MB free | 250 MB | 1 GB | 2.5 GB | 5 GB | 12 GB |
|---|---|---|---|---|---|---|
| Connections | 30 | 256 | 1024 | 2500 | 5000 | 10000 |
| Bandwidth/mo | 5 GB | 100 GB | 200 GB | 400 GB | 800 GB | 2000 GB |
| Max ops/s | 100 | 1000 | 2000 | 4000 | 8000 | 16000 |
[plan details](https://redis.io/docs/latest/operate/rc/subscriptions/view-essentials-subscription/essentials-plan-details/). Free: no replication, one free DB per account, no payment step; paid needs card + business address. [quickstart](https://redis.io/docs/latest/operate/rc/rc-quickstart/), [create Essentials](https://redis.io/docs/latest/operate/rc/databases/create-database/create-essentials-database/)

### Pro model
- Pay-as-you-go by dataset (min 0.1 GB), ops/s, HA (doubles memory), Flex RAM 10–50%, optional query performance factor. Billed in RBUs: Pico 100 MB/100 ops … XLarge 50 GB/10K, Flex-10…Flex-50. "Prices vary according to the cloud provider and region. Minimum prices apply." Provisioning 10–15 min. [create Pro](https://redis.io/docs/latest/operate/rc/databases/create-database/create-pro-database-new/)
- Per-RBU hourly prices (incl. Seoul) **not published in static HTML**; calculator is JS-only. Third-party example: 10 GB HA Frankfurt ≈ $549/month (Upstash blog 2026-08-04, competitor). [calculator](https://redis.io/pricing/calculator/), [Upstash](https://upstash.com/blog/redis-cloud-pricing-in-2026-plans-costs-and-real-examples)
- Cost report CSV per RBU; sub-minimum subscriptions show the difference from the minimum; charges generally non-refundable. [billing](https://redis.io/docs/latest/operate/rc/billing-and-payments/)
- Trial credit: only "First $200 free" on the Pro card; third parties describe a one-time credit consumed by Pro usage. [pricing](https://redis.io/pricing/)

### Gating: Essentials vs Pro
- VPC peering / Transit Gateway / PrivateLink / PSC: **Pro only**. [VPC peering](https://redis.io/docs/latest/operate/rc/security/vpc-peering/), [regions](https://redis.io/docs/latest/operate/rc/supported-regions/)
- Active-Active: **Pro only**.
- Flex: Essentials (RAM fixed 10%, HA none/single-zone, AWS only) and Pro (10–50%); no Time series on Flex; Search on Flex Pro-only beta. [create Flex](https://redis.io/docs/latest/operate/rc/databases/create-database/create-flex-database/)
- SAML SSO: listed under Essentials; no plan restriction in the doc. [SAML](https://redis.io/docs/latest/operate/rc/security/access-control/saml-sso/)
- Multi-zone replication: paid Essentials and Pro; free has none.
- RBAC: console-managed roles/ACLs; `ACL SETUSER/DELUSER/LOAD/SAVE/LOG/GENPASS` not supported. [RBAC](https://redis.io/docs/latest/operate/rc/security/access-control/data-access-control/role-based-access-control/)
- **Modules / vector search on Essentials and free: yes** — "Starting with Redis 8.0, all advanced capabilities … are included in Redis by default". [advanced capabilities](https://redis.io/docs/latest/operate/rc/databases/configuration/advanced-capabilities/)
- Seoul: in the Essentials price list; the official regions table is shortcode-rendered and could not be parsed.
- Azure: Essentials only directly; Pro via Azure Managed Redis.

## Open questions
1. Pro per-RBU hourly price in Seoul — calculator/console only.
2. $200 Pro credit terms — only "First $200 free" is official.
3. Official regions table for Seoul plan types (Multi-AZ) — unreadable by fetch; no multi-zone Essentials prices for Seoul suggests not offered (inference).
4. Flex Essentials in Seoul — not listed.
5. Exact GA date of 8.10.0 — what's-new places it in Q3 2026.
6. Vector sets GA — still beta on fetched pages.
7. Redis Software (self-managed) price list — quote only.
