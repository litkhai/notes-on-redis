# Agent Playbooks

[English](#english) | [한국어](#한국어)

## English

**Verified on redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07.**

A Playbook on the free database with four FAQs written from this site's own findings, authored as JSON files and synced with the `iris` CLI; discovery at runtime with the SDK; a proposal for a question nothing covers; and a second version that stays a draft until it is published.

Official documentation: [Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/)

### Run

```bash
set -a; . ./.env; set +a
.venv/bin/iris agent-playbooks faqs validate faqs
.venv/bin/iris agent-playbooks faqs plan faqs
.venv/bin/iris agent-playbooks faqs sync faqs --publish all
.venv/bin/python lab.py discover
.venv/bin/python lab.py propose
# edit faqs/free-plan-limits.json, then
.venv/bin/iris agent-playbooks faqs sync faqs          # new version, not published
.venv/bin/iris agent-playbooks faqs publish free-plan-limits --version 2
```

Output as it appeared (2026-11-07; service ids and endpoints removed):

```text
$ iris agent-playbooks faqs sync faqs --publish all   (4 entries CREATE + PUBLISH, version 1)

$ lab.py discover
== discover
 1217 ms  'is encryption in transit available on the free tier?'       [('free-plan-tls', 0.75, 1)]
  614 ms  'how many clients can connect to the free database'          [('free-plan-limits', 0.76, 1), ('free-plan-tls', 0.71, 1)]
  587 ms  'MSET fails with a slot error on my cluster'                 [('crossslot-error', 0.85, 1)]
  581 ms  '무료 DB에서 TLS 켤 수 있어?'                                        [('free-plan-tls', 0.78, 1)]
  776 ms  'How do I configure Active-Active between Seoul and Tokyo?'  []

== propose
proposal: created None

$ iris agent-playbooks proposals list --view inbox
PROPOSAL ID                           STATE  REV  EVIDENCE  SCORE  CANDIDATE                                                
------------------------------------  -----  ---  --------  -----  ---------------------------------------------------------
<id>  OPEN   1    0         -      How do I configure Active-Active between Seoul and Tokyo?

$ iris agent-playbooks faqs sync faqs        (no --publish: the new version stays a draft)
APPLIED  APPEND  free-plan-limits  2              
NOOP     NOOP    free-plan-tls     1              
NOOP     NOOP    wait-semantics    1              
$ iris agent-playbooks faqs versions free-plan-limits
free-plan-limits  version 2
free-plan-limits  version 1
-- discover before publishing v2
free-plan-limits version 1 |  test on 2026-11-07. No replication, persistence or backups.
$ iris agent-playbooks faqs publish free-plan-limits --version 2
published free-plan-limits version 2
-- discover after publishing v2
free-plan-limits version 2 | rsistence or backups. TLS is not available on the free plan.
```

### What was observed

- **Discovery.** Paraphrased English questions found the right FAQ at 0.75–0.85; the Korean "무료 DB에서 TLS 켤 수 있어?" found the English TLS FAQ at 0.78. The Active-Active question, which no FAQ covers, returned nothing rather than a weak match.
- **Proposals.** `propose_faq` put the uncovered question in the review inbox as OPEN; nothing reaches agents until a person accepts and publishes it.
- **Versions.** Editing an FAQ and syncing without `--publish` appended version 2 as a draft; discovery kept serving version 1 until `faqs publish --version 2`, then served version 2. The key's actions follow the same split: read, write, propose, publish, full.
- **Latency.** 580–1,220 ms per discovery from Korea; the agent endpoint is in us-east-1.
- **LangCache.** The console on 2026-11-07 lists Agent Playbooks and no LangCache entry; this site keeps treating them as two products (see the research notes).

### Not run / caveats

- Skills (packaged procedures) and automatic FAQ extraction from an Agent Memory store were not tried.
- Accepting a proposal in the console was not done; it stays OPEN.

| | |
|---|---|
| Plan needed | Free (Redis Cloud free database; Iris free messages) |
| Verified on | redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07 |

## 한국어

**확인: redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07.**

이 사이트의 발견으로 쓴 FAQ 네 개가 든 무료 DB 위의 Playbook. JSON 파일로 쓰고 `iris` CLI로 동기화한다. 실행 시에는 SDK로 찾고, 아무것도 다루지 않는 질문은 제안으로 넘기며, 두 번째 버전은 공개 전까지 초안으로 남는다.

공식 문서: [Agent Playbooks](https://redis.io/docs/latest/operate/iris/agent-playbook/)

### 실행

```bash
set -a; . ./.env; set +a
.venv/bin/iris agent-playbooks faqs validate faqs
.venv/bin/iris agent-playbooks faqs plan faqs
.venv/bin/iris agent-playbooks faqs sync faqs --publish all
.venv/bin/python lab.py discover
.venv/bin/python lab.py propose
# edit faqs/free-plan-limits.json, then
.venv/bin/iris agent-playbooks faqs sync faqs          # new version, not published
.venv/bin/iris agent-playbooks faqs publish free-plan-limits --version 2
```

출력은 영문 절과 같다(2026-11-07).

### 관찰한 것

- **검색.** 바꿔 말한 영어 질문이 0.75–0.85로 맞는 FAQ를 찾았다. 한국어 "무료 DB에서 TLS 켤 수 있어?"는 영어 TLS FAQ를 0.78로 찾았다. 어떤 FAQ도 다루지 않는 Active-Active 질문은 약한 매칭 대신 빈 결과였다.
- **제안.** `propose_faq`가 다루지 않는 질문을 검토함에 OPEN으로 넣었다. 사람이 받아들이고 공개하기 전에는 에이전트에 닿지 않는다.
- **버전.** FAQ를 고쳐 `--publish` 없이 동기화하자 버전 2가 초안으로 붙었다. `faqs publish --version 2` 전까지 검색은 버전 1을 냈고, 그 뒤 버전 2를 냈다. 키의 동작도 같은 구분을 따른다: read, write, propose, publish, full.
- **지연.** 한국에서 검색마다 580–1,220 ms. 에이전트 엔드포인트는 us-east-1이다.
- **LangCache.** 2026-11-07 콘솔에는 Agent Playbooks가 있고 LangCache 항목은 없다. 이 사이트는 둘을 계속 별개 제품으로 다룬다(조사 노트 참고).

### 미실행 / 주의

- 스킬(패키지된 절차)과 Agent Memory 스토어에서의 자동 FAQ 추출은 시험하지 않았다.
- 콘솔에서 제안을 받아들이지 않았다. OPEN으로 남아 있다.

| | |
|---|---|
| 필요한 플랜 | Free(Redis Cloud 무료 DB, Iris 무료 메시지) |
| 확인한 버전 | redis-iris 1.0.1 against Redis Cloud free plan services (endpoints in us-east-1, database in ap-northeast-2), 2026-11-07 |
