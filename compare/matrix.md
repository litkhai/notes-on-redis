# Feature matrix

[English](#english) | [한국어](#한국어)

## English

**Every cell carries a source number.** M = measured in this repository on 2026-11-07; D = vendor
documentation read on 2026-11-07. "not confirmed" means neither a run nor a document settled it.

| | Redis Open Source 8 | Redis Cloud | Valkey 9 | ElastiCache for Valkey | ElastiCache for Redis OSS | Azure Managed Redis | Memorystore for Valkey |
|---|---|---|---|---|---|---|---|
| Licence | RSALv2 / SSPLv1 / AGPLv3 [D1] | commercial service [D1] | BSD-3 [D2] | managed service [D3] | managed service, engine up to 7.1 [D3] | managed, Redis Enterprise inside [D5] | managed service [D6] |
| Version seen | 8.10.3 [M1] | 8.6.2 on the free plan [M3] | 9.1.3 [M1] | 9.0 serverless [M2] | not run | not run | not run |
| JSON | built in [M1] | yes, used by Agent Memory [M4] | `valkey-json` in the bundle, not in the core image [M1] | not confirmed | yes [D3] | in-memory tiers [D5] | not confirmed |
| Search: text and numeric | built in [M1] | yes, Agent Memory creates indexes [M4] | `valkey-search` in the bundle; existing keys indexed in the background [M1] | full-text and hybrid from 9.0 [D3] | not listed [D3] | in-memory tiers [D5] | not confirmed |
| Search: vector | built in [M1] | not run | `valkey-search` in the bundle [M1] | from 8.2 [D3] | not listed [D3] | in-memory tiers [D5] | not confirmed |
| Vector sets | built in (beta) [M1] | not run | no [M1] | not confirmed | no: engine up to 7.1 predates them [D3] | not confirmed | not confirmed |
| Array type | yes, since 8.8.0 [M1] | not run | no [M1] | not confirmed | no: engine up to 7.1 predates it [D3] | not confirmed | not confirmed |
| Time series | built in [M1] | not run | none in core or bundle [M1] | not listed [D3] | not listed [D3] | in-memory tiers [D5] | not confirmed |
| Probabilistic | Bloom, cuckoo, count-min, top-k, t-digest [M1] | RedisBloom listed on the free DB [M3] | Bloom only, in the bundle [M1] | Bloom from 8.1 [D3] | not listed [D3] | in-memory tiers [D5] | not confirmed |
| Hash field expiration | yes [M1] | not run | yes [M1] | not run | not confirmed | not confirmed | not confirmed |
| Cross-slot multi-key commands | single node, any keys [M1] | `MGET` over any keys worked [M2] | single node, any keys [M1] | refused on serverless: `CROSSSLOT` [M2] | not run | not run | not run |
| TLS | your choice | not available on the free plan [M3] | your choice | always on (serverless) [M2] | not run | not run | not run |
| Public endpoint | your choice | yes, with a CIDR allow list [M3] | your choice | VPC by default; Public needs IAM auth [M2] | not run | not run | not run |
| Active-Active | no: Redis Software and Cloud only [D4] | Pro plan [D4] | no | not confirmed (Global Datastore is cross-region replication) [D3] | not confirmed | active geo-replication [D5] | not confirmed |
| Pricing model | free | free 30 MB; Essentials from $5/month; Pro from $200/month [M3] | free | serverless: GB-hours + ECPUs; nodes: per hour [D7] | same, higher rates [D7] | per SKU per hour [D5] | not confirmed |

### Sources

- **M1** `compare/01-valkey-vs-redis-local`, 2026-11-07: `redis:8.10.3`, `valkey/valkey:9.1.3`, `valkey/valkey-bundle:9.1`.
- **M2** `compare/02-elasticache-valkey`, 2026-11-07: ElastiCache Serverless for Valkey 9.0 in ap-northeast-2, and the Redis Cloud free database probed the same way.
- **M3** `cloud/01-free-database`, `cloud/02-console-tour`, `setup/`, 2026-11-07: Redis Cloud free plan, console prices read that day, the REST API refusing `enableTls`.
- **M4** `iris/01-getting-started`, 2026-11-07: Agent Memory stores JSON documents and four Search indexes in the free database.
- **D1** [redis.io/legal/licenses](https://redis.io/legal/licenses/) and [AGPLv3 announcement](https://redis.io/blog/agplv3/).
- **D2** [Valkey COPYING](https://github.com/valkey-io/valkey/blob/unstable/COPYING).
- **D3** [ElastiCache engine versions](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/engine-versions.html).
- **D4** [redis.io/pricing](https://redis.io/pricing/).
- **D5** [Azure Managed Redis overview](https://learn.microsoft.com/en-us/azure/redis/overview).
- **D6** [Memorystore for Valkey overview](https://docs.cloud.google.com/memorystore/docs/valkey/product-overview).
- **D7** [ElastiCache pricing](https://aws.amazon.com/elasticache/pricing/) and the AWS price list for ap-northeast-2 published 2026-10-28.

## 한국어

**셀마다 출처 번호가 붙는다.** M = 이 저장소에서 2026-11-07에 측정, D = 2026-11-07에 읽은 공급사 문서.
"확인 안 됨"은 실행으로도 문서로도 정하지 못했다는 뜻이다.

| | Redis Open Source 8 | Redis Cloud | Valkey 9 | ElastiCache for Valkey | ElastiCache for Redis OSS | Azure Managed Redis | Memorystore for Valkey |
|---|---|---|---|---|---|---|---|
| 라이선스 | RSALv2 / SSPLv1 / AGPLv3 [D1] | 상용 서비스 [D1] | BSD-3 [D2] | 관리형 서비스 [D3] | 관리형 서비스, 엔진 7.1까지 [D3] | 관리형, 내부는 Redis Enterprise [D5] | 관리형 서비스 [D6] |
| 확인한 버전 | 8.10.3 [M1] | 무료 플랜 8.6.2 [M3] | 9.1.3 [M1] | 서버리스 9.0 [M2] | 미실행 | 미실행 | 미실행 |
| JSON | 내장 [M1] | 있음, Agent Memory가 사용 [M4] | 번들의 `valkey-json`, 기본 이미지에는 없음 [M1] | 확인 안 됨 | 있음 [D3] | 인메모리 티어 [D5] | 확인 안 됨 |
| Search: 텍스트·숫자 | 내장 [M1] | 있음, Agent Memory가 인덱스 생성 [M4] | 번들의 `valkey-search`, 기존 키는 백그라운드 색인 [M1] | 9.0부터 전문·하이브리드 [D3] | 목록에 없음 [D3] | 인메모리 티어 [D5] | 확인 안 됨 |
| Search: 벡터 | 내장 [M1] | 미실행 | 번들의 `valkey-search` [M1] | 8.2부터 [D3] | 목록에 없음 [D3] | 인메모리 티어 [D5] | 확인 안 됨 |
| 벡터 셋 | 내장(베타) [M1] | 미실행 | 없음 [M1] | 확인 안 됨 | 없음: 엔진 7.1까지라 그 이전 [D3] | 확인 안 됨 | 확인 안 됨 |
| Array 자료형 | 있음, 8.8.0부터 [M1] | 미실행 | 없음 [M1] | 확인 안 됨 | 없음: 엔진 7.1까지라 그 이전 [D3] | 확인 안 됨 | 확인 안 됨 |
| Time series | 내장 [M1] | 미실행 | 기본·번들 모두 없음 [M1] | 목록에 없음 [D3] | 목록에 없음 [D3] | 인메모리 티어 [D5] | 확인 안 됨 |
| 확률형 | Bloom, cuckoo, count-min, top-k, t-digest [M1] | 무료 DB에 RedisBloom 표시 [M3] | 번들에 Bloom만 [M1] | 8.1부터 Bloom [D3] | 목록에 없음 [D3] | 인메모리 티어 [D5] | 확인 안 됨 |
| 해시 필드 만료 | 있음 [M1] | 미실행 | 있음 [M1] | 미실행 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 슬롯이 다른 여러 키 명령 | 단일 노드, 아무 키나 [M1] | 아무 키나 `MGET` 가능 [M2] | 단일 노드, 아무 키나 [M1] | 서버리스에서 거절: `CROSSSLOT` [M2] | 미실행 | 미실행 | 미실행 |
| TLS | 직접 결정 | 무료 플랜에서는 불가 [M3] | 직접 결정 | 항상 켜짐(서버리스) [M2] | 미실행 | 미실행 | 미실행 |
| 공개 엔드포인트 | 직접 결정 | 있음, CIDR 허용 목록 [M3] | 직접 결정 | 기본 VPC, Public은 IAM 인증 필수 [M2] | 미실행 | 미실행 | 미실행 |
| Active-Active | 없음: Redis Software와 Cloud만 [D4] | Pro 플랜 [D4] | 없음 | 확인 안 됨(Global Datastore는 리전 간 복제) [D3] | 확인 안 됨 | 액티브 지역 복제 [D5] | 확인 안 됨 |
| 가격 모델 | 무료 | 30 MB 무료, Essentials 월 $5부터, Pro 월 $200부터 [M3] | 무료 | 서버리스: GB-시간 + ECPU, 노드: 시간당 [D7] | 같은 방식, 더 높은 요율 [D7] | SKU별 시간당 [D5] | 확인 안 됨 |

### 출처

출처 목록(M1–M4, D1–D7)은 영문 절과 같다.
