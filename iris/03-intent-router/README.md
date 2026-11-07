# Intent Router

[English](#english) | [한국어](#한국어)

## English

**Verified on redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07.**

A Router on the free database with the managed OpenAI `text-embedding-3-small` embedder (no key of our own was asked for). Four intents with three examples each, each pointing at a target of a different type: a tool, a model, an agent, a guardrail. Then eight queries in English and Korean, at the Router's default threshold and at 0.5, and again after adding Korean examples.

Official documentation: [Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/)

### Run

```bash
.venv/bin/python lab.py            # health, define, match (default 0.70), threshold (0.5)
.venv/bin/python lab.py korean     # add Korean phrasings, match at 0.5
```

Output as it appeared (2026-11-07; service ids and endpoints removed):

```text
health: Health(ok=True, checks=(HealthCheck(name='router', ok=True, message=None), HealthCheck(name='embedder', ok=True, message=None), HealthCheck(name='store', ok=True, message=None), HealthCheck(name='index', ok=True, message=None)))

== define
defined billing -> tool:billing_api.lookup
defined tls_question -> model:small-model
defined outage -> agent:incident-agent
defined off_topic -> guardrail:polite-refusal
intents now: ['billing', 'tls_question', 'outage', 'off_topic']

== match
   895 ms  'I was billed twice, can you check?'                       no match (fallback)
   592 ms  'is encryption available on the free tier'                 no match (fallback)
   573 ms  'connections keep timing out on my prod database'          no match (fallback)
   834 ms  'tell me something funny'                                  off_topic (0.71) -> guardrail:polite-refusal
   756 ms  '무료 플랜에서 TLS를 켤 수 있나요?'                                    no match (fallback)
   729 ms  '청구서를 어디서 받나요?'                                            no match (fallback)
   583 ms  'How many shards should a 50 GB cluster have?'             no match (fallback)
   880 ms  'Can you recommend a good restaurant?'                     no match (fallback)
median 756 ms over 8 queries

== threshold
-- min_score 0.5 for the same queries
   863 ms  'I was billed twice, can you check?'                       billing (0.52) -> tool:billing_api.lookup
   622 ms  'is encryption available on the free tier'                 tls_question (0.59) -> model:small-model
   672 ms  'connections keep timing out on my prod database'          outage (0.51) -> agent:incident-agent
   720 ms  'tell me something funny'                                  off_topic (0.71) -> guardrail:polite-refusal
   807 ms  '무료 플랜에서 TLS를 켤 수 있나요?'                                    tls_question (0.61) -> model:small-model
   560 ms  '청구서를 어디서 받나요?'                                            no match (fallback)
   571 ms  'How many shards should a 50 GB cluster have?'             no match (fallback)
  1086 ms  'Can you recommend a good restaurant?'                     no match (fallback)
median 720 ms over 8 queries

$ lab.py korean
health: Health(ok=True, checks=(HealthCheck(name='router', ok=True, message=None), HealthCheck(name='embedder', ok=True, message=None), HealthCheck(name='store', ok=True, message=None), HealthCheck(name='index', ok=True, message=None)))

== korean
billing examples: ['Why was I charged this month?', 'How do I download my invoice?', 'Change the credit card on my account', '인보이스는 어떻게 내려받나요', '이번 달 요금 청구 내역을 보고 싶어요']
   777 ms  'I was billed twice, can you check?'                       billing (0.52) -> tool:billing_api.lookup
   765 ms  'is encryption available on the free tier'                 tls_question (0.59) -> model:small-model
   797 ms  'connections keep timing out on my prod database'          outage (0.51) -> agent:incident-agent
   564 ms  'tell me something funny'                                  off_topic (0.71) -> guardrail:polite-refusal
   778 ms  '무료 플랜에서 TLS를 켤 수 있나요?'                                    tls_question (0.61) -> model:small-model
   566 ms  '청구서를 어디서 받나요?'                                            no match (fallback)
   717 ms  'How many shards should a 50 GB cluster have?'             no match (fallback)
   600 ms  'Can you recommend a good restaurant?'                     off_topic (0.59) -> guardrail:polite-refusal
median 765 ms over 8 queries
```

### What was observed

- **The default threshold is strict.** At the Router's 0.70 only one of eight queries matched ("tell me something funny", 0.71). At 0.5 the three English support questions and the Korean TLS question (0.61) went to the right targets; the shard-sizing question and the restaurant question fell through to the fallback.
- **Examples cross languages, unevenly.** After adding "맛집 추천해 줘" to `off_topic`, the English restaurant question matched it (0.59). Two Korean billing examples did not make the Korean invoice question reach 0.5.
- **What a match returns.** The intent, its score and the target you attached (`tool:billing_api.lookup`, `model:small-model` ...): routing happens before any generation; the query is embedded, not sent to a chat model.
- **Latency.** 560–1,090 ms per match from Korea; the Router endpoint is in us-east-1. The Router created its own Search index in the free database.

### Not run / caveats

- Templates other than Custom (Model selection, Guardrails, Agent routing) were not tried.
- Per-intent thresholds were not set; only the Router default and a per-call `min_score`.

| | |
|---|---|
| Plan needed | Free (Redis Cloud free database; Iris free messages) |
| Verified on | redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07 |

## 한국어

**확인: redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07.**

무료 DB 위의 Router. 임베딩은 관리형 OpenAI `text-embedding-3-small`(내 키는 요구하지 않았다). 예시 셋씩인 의도 네 개, 각각 다른 유형의 대상(도구, 모델, 에이전트, 가드레일). 영어·한국어 질문 여덟 개를 Router 기본 임계값과 0.5로, 그리고 한국어 예시를 더한 뒤 다시 맞춘다.

공식 문서: [Intent Router](https://redis.io/docs/latest/operate/iris/intent-router/)

### 실행

```bash
.venv/bin/python lab.py            # health, define, match (default 0.70), threshold (0.5)
.venv/bin/python lab.py korean     # add Korean phrasings, match at 0.5
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **기본 임계값이 엄격하다.** Router의 0.70에서는 여덟 개 중 하나만 맞았다("tell me something funny", 0.71). 0.5에서는 영어 지원 질문 셋과 한국어 TLS 질문(0.61)이 맞는 대상으로 갔고, 샤드 크기 질문과 식당 질문은 대체 경로로 빠졌다.
- **예시는 언어를 넘지만 고르지 않다.** `off_topic`에 "맛집 추천해 줘"를 더하자 영어 식당 질문이 거기에 맞았다(0.59). 한국어 청구 예시 둘을 넣어도 한국어 청구서 질문은 0.5에 닿지 않았다.
- **매칭이 돌려주는 것.** 의도, 점수, 붙여 둔 대상(`tool:billing_api.lookup`, `model:small-model` 등). 라우팅은 생성 전에 일어난다. 질의는 임베딩될 뿐 채팅 모델로 가지 않는다.
- **지연.** 한국에서 매칭마다 560–1,090 ms. Router 엔드포인트는 us-east-1이다. Router는 무료 DB에 자체 Search 인덱스를 만들었다.

### 미실행 / 주의

- Custom 외의 템플릿(Model selection, Guardrails, Agent routing)은 시험하지 않았다.
- 의도별 임계값은 정하지 않았다. Router 기본값과 호출별 `min_score`만 썼다.

| | |
|---|---|
| 필요한 플랜 | Free(Redis Cloud 무료 DB, Iris 무료 메시지) |
| 확인한 버전 | redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07 |
