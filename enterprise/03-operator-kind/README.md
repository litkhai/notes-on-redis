# Kubernetes operator on kind

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis Enterprise operator 8.2.6-21 (cluster 8.2.6-25, databases Redis 8.8.0) on kind v0.33.0 with Kubernetes v1.34.11, 2026-11-07.**

The Redis Enterprise operator on a local kind cluster: one `helm install` creates the operator and a three-node Redis Enterprise cluster (REC), and two `RedisEnterpriseDatabase` (REDB) resources create databases. Then a database that needs more shards than the trial licence allows, and a pod deletion under write load. From the overview: "You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." The Helm page lists "At least three worker nodes" as a prerequisite, so `kind.yaml` has three workers. The two databases are the ones RDI needs in [`02-rdi`](../02-rdi/README.md).

Official documentation: [Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/), [Quick start](https://redis.io/docs/latest/operate/kubernetes/deployment/quick-start/), [Database controller](https://redis.io/docs/latest/operate/kubernetes/re-databases/db-controller/).

### Run

```bash
./up.sh          # kind cluster, operator + REC from the Helm chart, two databases, the over-licence request (~5 min)
./failover.sh    # delete the pod with the target database's primary shard while a client writes
../02-rdi/up.sh  # optional: RDI on the same cluster
./down.sh        # delete the kind cluster and everything in it
```

`up.sh` output as it appeared (2026-11-07):

```text
kind cluster up in 16 s
   nor-rec-control-plane NotReady v1.34.11
   nor-rec-worker NotReady v1.34.11
   nor-rec-worker2 NotReady v1.34.11
   nor-rec-worker3 NotReady v1.34.11
operator chart 8.2.6-21 installed, REC Running after 257 s
NAME   NODES   SHARDS   VERSION       STATE     SPEC STATUS   LICENSE STATE   LICENSE EXPIRATION DATE   AGE
rec    3       0/4      8.2.6-25.21   Running   Valid         Valid           2026-12-07T10:36:35Z      3m5s
databases active after 13 s
NAME        VERSION   PORT    CLUSTER   SHARDS   STATUS   SPEC STATUS   AGE
rdi-state   8.8.0     11626   rec       1        active   Valid         13s
target      8.8.0     13007   rec       2        active   Valid         12s
SHARDS:
DB:ID        NAME        ID       NODE    ROLE    SLOTS    USED_MEMORY   STATUS 
db:1         rdi-state   redis:1  node:1  master  0-16383  1.92MB        OK     
db:2         target      redis:2  node:2  master  0-16383  2MB           OK     
db:2         target      redis:3  node:3  slave   0-16383  1.62MB        OK     
== a database that needs two more shards
Error from server: error when creating "redb-over-license.yaml": admission webhook "redisenterprise.admission.redislabs" denied the request: Total shards count exceeds amount of total shards permitted by license. License permits 4 total shards, but there are 5 total shards in use.
```

`failover.sh` output as it appeared (2026-11-07), the third of three runs:

```text
== before
DB:ID      NAME     ID        NODE     ROLE     SLOTS     USED_MEMORY    STATUS 
db:2       target   redis:2   node:2   slave    0-16383   1.63MB         OK     
db:2       target   redis:3   node:3   master   0-16383   2.14MB         OK     
DB:ID      NAME        ID                     NODE        ROLE        SSL       
db:2       target      endpoint:2:1           node:3      single      No        
primary shard on node:3 -> pod rec-2
== deleting rec-2 at 19:41:05
pod "rec-2" deleted
replacement rec-2 created after 37 s
replacement rec-2 ready after 82 s
writes attempted 1600, succeeded 1596, failed 4
failure messages: ['', 'Could not connect to Redis at target:13007: Connection refused']
longest stretch without a successful write: 1.3 s
counter: last value 1596, successful writes 1596, values strictly increasing: True
== after
DB:ID      NAME     ID        NODE     ROLE     SLOTS     USED_MEMORY    STATUS 
db:2       target   redis:2   node:2   master   0-16383   2.12MB         OK     
db:2       target   redis:3   node:3   slave    0-16383   1.62MB         OK     
DB:ID      NAME        ID                     NODE        ROLE        SSL       
db:2       target      endpoint:2:1           node:2      single      No        
Running
```

### What was observed

- **kind on a cgroup v1 host needs an older node image.** kind v0.33.0's default image, Kubernetes v1.37.0, failed in `kubeadm init`. Its kubelet refused to start with "kubelet is configured to not run on a host using cgroup v1" (`failCgroupV1: true`). The host is Ubuntu 20.04 on cgroup v1. kind's v1.34.11 image works, and `kind.yaml` pins it.
- **One Helm release, a running cluster in about four minutes.** With `cluster.create: true` in `values.yaml` the chart created the REC too. It reached `Running` 257 s after `helm install`, with a valid licence expiring 30 days later and `0/4` shards in use. Each node got a 10 GiB volume from kind's `standard` storage class.
- **Databases are quick.** Both REDBs were `active` 13 s after `kubectl apply`, each with its own Kubernetes service. Ports are assigned by the cluster and change between runs, so the scripts read them from the REDB status.
- **The trial licence is enforced at admission.** The third database would have made five shards, and `kubectl apply` was refused straight away by the operator's admission webhook: "License permits 4 total shards, but there are 5 total shards in use."
- **Deleting the pod with the primary shard.** The replica on another node became primary. The client saw 4 refused connections over 1.3 s and no lost or repeated increments: the counter equalled the number of successful writes. The database endpoint (proxy policy `single`) moved to the node of the new primary. The operator recreated the pod, and it was Ready after 73–82 s, rejoining as replica.
- **The same test, three runs.** Two runs on this cluster both showed 1.3 s of refused connections. One run on an earlier cluster showed no failed writes at all; the endpoint placement was not recorded for it.

### Not run / caveats

- One host: all three "nodes" share its disk and network, so the failover numbers say nothing about real node loss.
- Active-Active, Redis Flex and TLS between client and database were not run.
- The trial licence lasts 30 days from the cluster's creation and allows four shards; a cluster rebuilt with `up.sh` starts a new trial.

| | |
|---|---|
| Plan needed | Free (local kind, trial licence) |
| Verified on | Redis Enterprise operator 8.2.6-21 (cluster 8.2.6-25, databases Redis 8.8.0) on kind v0.33.0 with Kubernetes v1.34.11, 2026-11-07 |

## 한국어

**확인: Redis Enterprise operator 8.2.6-21 (cluster 8.2.6-25, databases Redis 8.8.0) on kind v0.33.0 with Kubernetes v1.34.11, 2026-11-07.**

로컬 kind 클러스터 위의 Redis Enterprise operator. `helm install` 한 번이 operator와 노드 셋짜리 Redis Enterprise 클러스터(REC)를 만들고, `RedisEnterpriseDatabase`(REDB) 리소스 둘이 DB를 만든다. 이어서 체험 라이선스가 허용하는 것보다 샤드가 많은 DB를 요청하고, 쓰기 부하 중에 파드를 지운다. 개요의 표현: "You can deploy, scale, and manage Redis Enterprise clusters and databases by using native Kubernetes resources and workflows." Helm 페이지가 전제 조건으로 "At least three worker nodes"를 적으므로 `kind.yaml`에 워커가 셋이다. 두 DB는 [`02-rdi`](../02-rdi/README.md)에서 RDI가 쓰는 것이다.

공식 문서: [Redis Enterprise for Kubernetes](https://redis.io/docs/latest/operate/kubernetes/), [Install with Helm](https://redis.io/docs/latest/operate/kubernetes/deployment/helm/), [Quick start](https://redis.io/docs/latest/operate/kubernetes/deployment/quick-start/), [Database controller](https://redis.io/docs/latest/operate/kubernetes/re-databases/db-controller/).

### 실행

```bash
./up.sh          # kind cluster, operator + REC from the Helm chart, two databases, the over-licence request (~5 min)
./failover.sh    # delete the pod with the target database's primary shard while a client writes
../02-rdi/up.sh  # optional: RDI on the same cluster
./down.sh        # delete the kind cluster and everything in it
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **cgroup v1 호스트의 kind는 이전 노드 이미지가 필요하다.** kind v0.33.0의 기본 이미지인 Kubernetes v1.37.0은 `kubeadm init`에서 실패했다. kubelet이 "kubelet is configured to not run on a host using cgroup v1"(`failCgroupV1: true`)로 시작을 거부했다. 호스트는 cgroup v1인 Ubuntu 20.04다. kind의 v1.34.11 이미지는 동작하고, `kind.yaml`이 그것을 고정한다.
- **Helm 릴리스 하나, 약 4분이면 클러스터가 돈다.** `values.yaml`에 `cluster.create: true`를 두면 차트가 REC도 만든다. `helm install` 뒤 257초에 `Running`이 됐고, 라이선스는 유효, 만료는 30일 뒤, 사용 샤드 `0/4`. 노드마다 kind의 `standard` 스토리지 클래스에서 10 GiB 볼륨을 받았다.
- **DB는 빠르다.** 두 REDB 모두 `kubectl apply` 뒤 13초에 `active`였고, 각자 Kubernetes 서비스가 생겼다. 포트는 클러스터가 정하고 실행마다 바뀌므로, 스크립트는 REDB 상태에서 읽는다.
- **체험 라이선스는 admission 단계에서 막힌다.** 세 번째 DB는 샤드를 다섯으로 만들었을 것이고, operator의 admission webhook이 `kubectl apply`를 바로 거절했다: "License permits 4 total shards, but there are 5 total shards in use."
- **주 샤드가 있는 파드 지우기.** 다른 노드의 복제본이 주 샤드가 됐다. 클라이언트는 1.3초 동안 연결 거절 4번을 겪었고, 잃거나 중복된 증가는 없었다: 카운터 값이 성공한 쓰기 수와 같았다. DB 엔드포인트(프록시 정책 `single`)는 새 주 샤드의 노드로 옮겨 갔다. operator가 파드를 다시 만들었고 73–82초 뒤 Ready가 되어 복제본으로 돌아왔다.
- **같은 시험 세 번.** 이 클러스터에서 두 번은 모두 1.3초의 연결 거절. 이전 클러스터에서 한 번은 쓰기 실패가 전혀 없었다. 그때의 엔드포인트 위치는 기록하지 않았다.

### 미실행 / 주의

- 호스트 하나다. "노드" 셋이 디스크와 네트워크를 공유하므로 장애 조치 숫자는 실제 노드 손실에 대해 말해 주지 않는다.
- Active-Active, Redis Flex, 클라이언트와 DB 사이 TLS는 실행하지 않았다.
- 체험 라이선스는 클러스터 생성부터 30일, 샤드 넷. `up.sh`로 다시 만든 클러스터는 새 체험으로 시작한다.

| | |
|---|---|
| 필요한 플랜 | Free(로컬 kind, 체험 라이선스) |
| 확인한 버전 | Redis Enterprise operator 8.2.6-21 (cluster 8.2.6-25, databases Redis 8.8.0) on kind v0.33.0 with Kubernetes v1.34.11, 2026-11-07 |
