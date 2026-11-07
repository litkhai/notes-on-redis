# Getting started

[English](#english) | [한국어](#한국어)

## English

**Verified on redis-iris 1.0.1 (Python 3.12) against Agent Memory on the Redis Cloud free plan (Redis 8.6.2, AWS ap-northeast-2), 2026-11-07.**

Is Iris usable on a free account? Yes: one Agent Memory service was created in the console on
the free 30 MB database, two API keys were issued in Access & Identity (one read, one write), and
the `redis-iris` SDK and `iris` CLI used it end to end.

### Run

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt   # needs Python >= 3.11
cp .env.example .env      # endpoint and store id from the service's Connect dialog; key from Access & Identity
.venv/bin/python first_memory.py        # health, remember, converse, recall
.venv/bin/python extracted.py 120       # waits for background extraction, recalls what it produced
set -a; . ./.env; set +a
.venv/bin/iris agent-memory health
.venv/bin/iris agent-memory memories search "answer format" --owner cust-1042
```

Output as it appeared (2026-11-07, 07:19–07:30 UTC; endpoint, store id and memory ids replaced):

```text
$ first_memory.py            (read key, first)
== health
health: Health(status='HEALTHY', features={'background_jobs': 'HEALTHY', 'long_term_memory': 'HEALTHY', 'session_memory': 'HEALTHY', 'source_link': 'HEALTHY', 'store_db': 'HEALTHY'})
== remember
ForbiddenErrorResponseContent: {"detail":"Unauthorized to perform this operation on this resource. Please check your identity permissions.","status":403,"title":"Unauthorized","type":"/errors/insufficient-permissions"}
== recall
recall in 2322 ms:
Recall(memories=())

$ first_memory.py            (write key)
== health
health: Health(status='HEALTHY', features={'background_jobs': 'HEALTHY', 'long_term_memory': 'HEALTHY', 'session_memory': 'HEALTHY', 'source_link': 'HEALTHY', 'store_db': 'HEALTHY'})

== remember
remembered: Memory(id='mem-<id>', text='Prefers answers in Korean, with code examples in Python.', owner='cust-1042', shared=False, topics=('preferences',), memory_type=None)

== converse
session: cust-1042-20261107071957

== recall
recall in 748 ms:
Recall(memories=(Memory(id='mem-<id>', text='Prefers answers in Korean, with code examples in Python.', owner='cust-1042', shared=False, topics=('preferences',), memory_type='semantic'),))

$ extracted.py 120
t+  0s: 2 memories
   [semantic] User has a Redis Cloud database on the Free plan in the Seoul region.
   [semantic] Prefers answers in Korean, with code examples in Python.

$ iris agent-memory health
status: HEALTHY
background_jobs: HEALTHY
long_term_memory: HEALTHY
session_memory: HEALTHY
source_link: HEALTHY
store_db: HEALTHY

$ iris agent-memory memories search "answer format" --owner cust-1042
ID                                SCOPE      TOPICS       TEXT
mem-<id>      cust-1042  preferences  Prefers answers in Korean, with code examples in Python.
<id>  cust-1042               Assistant stated on November 7, 2026 that the Redis Cloud Free plan rejects the `enableTls` API option, while a paid plan supports it.
<id>  cust-1042               User has a Redis Cloud database on the Free plan in the Seoul region.

$ iris agent-memory sessions --help | head
Usage: iris agent-memory sessions [OPTIONS] COMMAND [ARGS]...

  Inspect sessions and their transcripts (read only).

    iris agent-memory sessions list --owner user-123
    iris agent-memory sessions show support-session-1

Options:
  --help  Show this message and exit.

Commands:
  list  Session ids for an owner, or every session with its owner and...

$ recall x10
recall x10 ms: [1254, 695, 595, 589, 1312, 611, 561, 559, 604, 614]
median 611 ms, min 559, max 1312; memories returned 3
```

### What was observed

- **Keys are scoped.** A key grants one action (read, write, full) on a resource. The read key
  could check health and recall but got 403 `insufficient-permissions` on writes.
- **Extraction is fast and goes beyond the user.** About 15 s after a two-turn conversation the
  store held "User has a Redis Cloud database on the Free plan in the Seoul region"; a few minutes
  later it added a memory made from the assistant's answer.
- **It runs in us-east-1.** The service page lists its endpoint region as us-east-1 while the
  database is in Seoul. Recall from Korea took a median 611 ms (559–1,312 ms over ten calls).
- **It writes into your database.** Seven keys (JSON documents and hashes) and four Search indexes
  (`…:ltm`, `…:session_memory`, `…:source_link`, `…:namespace:`) appeared in the free database.
- **Message count not visible.** Neither the Iris pages nor Usage or Billing showed the 5,000 free
  messages or their use.
- The SDK reads settings through `AgentMemorySettings.from_env()`; a bare `AgentMemory()`
  raised `ConfigurationError` even with the variables set.

### Not run / caveats

- Sensitive-data exclusions, custom memory types, MemoryETL and `forget()` were not exercised; the Agent Memory lab (`iris/02`) covers them.
- Keys `notes-on-redis-lab` (read) and `notes-on-redis-lab-write` expire on 2026-12-07; delete them earlier if the lab is done.

| | |
|---|---|
| Plan needed | Free (Redis Cloud free database; Iris free messages) |
| Verified on | redis-iris 1.0.1, Agent Memory on Redis Cloud free plan, 2026-11-07 |

## 한국어

**확인: redis-iris 1.0.1(Python 3.12), Redis Cloud 무료 플랜(Redis 8.6.2, AWS ap-northeast-2)의 Agent Memory, 2026-11-07.**

무료 계정에서 Iris를 쓸 수 있나? 쓸 수 있다. 무료 30 MB DB에 콘솔로 Agent Memory 서비스를 하나 만들고,
Access & Identity에서 API 키 두 개(read 하나, write 하나)를 발급해 `redis-iris` SDK와 `iris` CLI로 끝까지 썼다.

### 실행

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt   # Python 3.11 이상 필요
cp .env.example .env      # 엔드포인트와 Store ID는 서비스 Connect 창, 키는 Access & Identity
.venv/bin/python first_memory.py        # health, remember, converse, recall
.venv/bin/python extracted.py 120       # 백그라운드 추출을 기다렸다가 결과를 회상
set -a; . ./.env; set +a
.venv/bin/iris agent-memory health
.venv/bin/iris agent-memory memories search "answer format" --owner cust-1042
```

출력은 영문 절과 같다(2026-11-07, 07:19–07:30 UTC).

### 관찰한 것

- **키는 범위가 있다.** 키는 리소스 하나에 동작 하나(read, write, full)를 준다. read 키는 상태 확인과
  회상은 됐지만 쓰기는 403 `insufficient-permissions`로 거절됐다.
- **추출이 빠르고 사용자 말만 보지 않는다.** 두 턴 대화 뒤 약 15초 만에 "User has a Redis Cloud database
  on the Free plan in the Seoul region"이 저장됐다. 몇 분 뒤에는 어시스턴트 답변에서 만든 기억이 추가됐다.
- **us-east-1에서 돈다.** 서비스 화면의 엔드포인트 리전은 us-east-1이고 DB는 서울이다. 한국에서 회상은
  10회 중앙값 611 ms(559–1,312 ms)였다.
- **내 DB에 쓴다.** 무료 DB에 키 7개(JSON 문서와 해시)와 Search 인덱스 4개
  (`…:ltm`, `…:session_memory`, `…:source_link`, `…:namespace:`)가 생겼다.
- **메시지 수는 보이지 않는다.** Iris 화면, Usage, Billing 어디에도 무료 메시지 5,000개나 사용량이 없었다.
- SDK는 `AgentMemorySettings.from_env()`로 설정을 읽는다. 변수를 넣어도 `AgentMemory()`만으로는 `ConfigurationError`가 났다.

### 미실행 / 주의

- 민감 데이터 제외, 사용자 정의 기억 유형, MemoryETL, `forget()`은 시험하지 않았다. Agent Memory 실습(`iris/02`)에서 다룬다.
- 키 `notes-on-redis-lab`(read)와 `notes-on-redis-lab-write`는 2026-12-07에 만료된다. 실습이 끝나면 먼저 지운다.

| | |
|---|---|
| 필요한 플랜 | Free(Redis Cloud 무료 DB, Iris 무료 메시지) |
| 확인한 버전 | redis-iris 1.0.1, Redis Cloud 무료 플랜의 Agent Memory, 2026-11-07 |
