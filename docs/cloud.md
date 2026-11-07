---
layout: default
title: Redis Cloud
permalink: /cloud/
---

# Redis Cloud

<div class="lang" data-lang="en" markdown="1">

## English

**Redis Cloud, from sign-up to every console menu.** Captured 2026-11-07 on the free plan: one free database (Redis 8.6, AWS ap-northeast-2 Seoul), console in dark mode, nothing paid. The Essentials and Pro forms were opened and captured but not submitted. Masked in every screenshot: name, e-mail, account number, subscription and database IDs, endpoint, port, IP addresses, API keys. Prices on this page were read in the console on 2026-11-07.

### At a glance

The left sidebar, top to bottom: **Databases**, **Subscriptions**, **Redis Search**, **Data Integration**; under *AI services* **Iris** with Agent Playbooks, Agent Memory, Context Gateway, Intent Router, Lens (beta), Agent Mesh (beta) and Access & Identity; under *Reports* **Logs** and **Usage**; under *Account* **API Keys & Team**, **Data Access**, **Billing**, **Integrations**, **Settings**. The top bar holds an app switcher, a tips icon, the theme switch (light, dark, system) and the account menu.

<p class="shot"><img src="{{ '/assets/img/cloud-console/01-databases-empty.webp' | relative_url }}" width="1440" height="765" alt="Empty Databases page with a New database button" loading="lazy" decoding="async"></p>

A new account opens on Databases with nothing in it. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Create a database

**New database** opens one page with two plan cards. **Essentials** is shared infrastructure, from $0.007/hour ($5/month). **Pro** is dedicated infrastructure, from $0.014/hour with a $200/month minimum and a "First $200 free" badge. Below the cards a line reads *Not ready? Try 30 MB for free*; that link is the only way to the free plan.

<p class="shot"><img src="{{ '/assets/img/cloud-console/02-create-essentials-form.webp' | relative_url }}" width="1440" height="2118" alt="Essentials create form: cloud vendor and region, name, version 8.6, size slider, high availability and persistence options, payment method" loading="lazy" decoding="async"></p>

Essentials defaults: AWS us-east-1, Redis 8.6, 250 MB total (125 MB dataset plus 125 MB replica), 1,000 ops/s, single-zone replication and AOF every second, $8/month. Sizes run from 250 MB to 100 GB; RAM+SSD (Flex) is a toggle. A payment method is required before Confirm & pay. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/03-create-pro-form.webp' | relative_url }}" width="1440" height="2338" alt="Pro create form: Easy create or Custom settings, cloud vendor tiles, region, dataset size and throughput steppers, persistence, high availability, price summary" loading="lazy" decoding="async"></p>

Pro starts with a setup method, Easy create or Custom settings. Easy create defaults: 3 GB dataset (6 GB total memory with the replica), 3,000 ops/s, AOF every second, high availability on, $0.274/hour (about $200/month). <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/04-create-free-form.webp' | relative_url }}" width="1440" height="1259" alt="Free plan create form with region Asia Pacific (Seoul), name notes-on-redis-free, and the included limits" loading="lazy" decoding="async"></p>

The free form lists what is included: 1 database, 30 MB RAM, 30 connections, 100 ops/sec, $0/month. Region choice is open (AWS, Google Cloud or Azure; Seoul was picked). This one capture is in light mode; the form cannot be reopened once the account has its free database. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### The database screen

Create database lands on the database page after a few seconds. The page has four tabs: Configuration, Metrics, Alerts, Slowlog. A first-visit dialog offers a guided setup; closing it applies nothing.

<p class="shot"><img src="{{ '/assets/img/cloud-console/05-database-setup-dialog.webp' | relative_url }}" width="1440" height="765" alt="Set up your database dialog over the new database page" loading="lazy" decoding="async"></p>

"No changes are applied until you confirm." The dialog was closed without reviewing. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/06-database-configuration.webp' | relative_url }}" width="1440" height="1977" alt="Configuration tab of the free database: usage cards, plan slider, availability and backup, access, data, security and database info panels" loading="lazy" decoding="async"></p>

Free database defaults as shown: no replication, no persistence, remote backup off, eviction policy volatile-lru, default user on, CIDR allow list off, TLS off (the free plan cannot turn it on), RESP3, Redis 8.6. The Logs page records the allow list as 0.0.0.0/0. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/07-connect-dialog.webp' | relative_url }}" width="1440" height="765" alt="Connect drawer with Redis CLI, Redis Insight and Redis SDK clients sections" loading="lazy" decoding="async"></p>

Connect gives a ready redis-cli command over the public endpoint; the password stays hidden until the eye icon is pressed. The endpoint is a generated host name under db.redis.io. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/08-database-metrics.webp' | relative_url }}" width="1440" height="1587" alt="Metrics tab during the load test: ops per second rising to 82 thousand, latency, connections, keys, memory and network charts" loading="lazy" decoding="async"></p>

Ranges from 5 minutes to 3 months. Charts: ops/sec, latency (also split into reads, writes, other), connections, evicted and expired objects/sec, total keys, reads/sec, writes/sec, other commands/sec, read hit ratio, used memory, network egress and ingress. Captured during the throughput test below. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/09-database-throughput-over-limit.webp' | relative_url }}" width="1440" height="765" alt="Throughput card showing 61,806 of 100 ops per second with a warning icon" loading="lazy" decoding="async"></p>

The throughput card during the test: 61,806 / 100 ops/sec. The console flags the overage; the database kept serving (see the measurements below). <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/10-database-alerts.webp' | relative_url }}" width="1440" height="765" alt="Alerts tab with dataset size and connections alerts, both at 80 percent of plan limit" loading="lazy" decoding="async"></p>

Free plan alerts: dataset size and number of connections, each as a percent of the plan limit, preset to 80%. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/11-database-slowlog.webp' | relative_url }}" width="1440" height="765" alt="Slowlog tab with no entries and a Clear slowlog button" loading="lazy" decoding="async"></p>

Slowlog stayed empty: the test used INCR and SET only. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Databases and subscriptions

Every database belongs to a subscription. The free plan creates one subscription holding one database.

<p class="shot"><img src="{{ '/assets/img/cloud-console/12-databases-list.webp' | relative_url }}" width="1440" height="765" alt="Databases list with one row: notes-on-redis-free, memory usage 7.4 percent of 30 MB, version 8.6" loading="lazy" decoding="async"></p>

Columns: status, database name, subscription, endpoint (a Connect button), memory usage, capabilities, tags, version, actions. Filters for status, subscription, plan, capabilities, version, region and cloud. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/13-subscriptions.webp' | relative_url }}" width="1440" height="765" alt="Subscriptions page with the free subscription card and its database list" loading="lazy" decoding="async"></p>

The free subscription in ap-northeast-2, with a Plan upgrade button and Databases and Overview tabs. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Product menus

Three sidebar entries are entry points to products rather than settings.

<p class="shot"><img src="{{ '/assets/img/cloud-console/14-redis-search.webp' | relative_url }}" width="1440" height="818" alt="Redis Search page pitching vector search for agents, with a database picker" loading="lazy" decoding="async"></p>

Redis Search is a guided start for a first vector index on an existing database. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/15-data-integration.webp' | relative_url }}" width="1440" height="1489" alt="Data Integration page: near real-time sync into Redis, $1.37 per hour, three steps" loading="lazy" decoding="async"></p>

Data Integration is managed RDI: $1.37/hour, about $1,000/month estimated, billed from pipeline creation. Steps: connect a source database, transform, serve reads from Redis. Not created here. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/16-iris.webp' | relative_url }}" width="1440" height="1276" alt="Iris AI Services landing page with a demo video and the list of services" loading="lazy" decoding="async"></p>

Iris landing page. The services listed: Agent Memory, Agent Playbooks, Intent Router, Context Gateway, Agent Mesh; Lens appears in the sidebar. The Iris page of this site walks through them. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Reports

<p class="shot"><img src="{{ '/assets/img/cloud-console/17-logs-system.webp' | relative_url }}" width="1440" height="765" alt="System log: subscription created, database activated, persistence disabled, source IP added, RESP3 enabled, API enabled, API key assigned" loading="lazy" decoding="async"></p>

System log lists every configuration event with time, originator and API key name; Export all downloads it. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/18-logs-sessions.webp' | relative_url }}" width="1440" height="765" alt="Sessions log with two successful logins" loading="lazy" decoding="async"></p>

Sessions: each console login with user agent, IP, role and login type. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/19-usage.webp' | relative_url }}" width="1440" height="765" alt="Usage report, Memory Usage tab, daily chart for November 2026" loading="lazy" decoding="async"></p>

Usage has Memory Usage and RBU Usage tabs and a Cost report download. Right after the database was created it said the report would appear an hour later; by the final capture it showed data. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Account

<p class="shot"><img src="{{ '/assets/img/cloud-console/20-api-keys.webp' | relative_url }}" width="1440" height="765" alt="API Keys tab with the account key hidden and one user key" loading="lazy" decoding="async"></p>

Enable API works on the free plan. A call needs the account key and a user key; one user key was created and GET /v1/fixed/subscriptions returned 200. Free and Essentials subscriptions live under /v1/fixed, Pro under /v1/subscriptions. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/21-team.webp' | relative_url }}" width="1440" height="765" alt="Team tab with one owner signed up through Google" loading="lazy" decoding="async"></p>

Team: console users, their role and sign-up type. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/22-single-sign-on.webp' | relative_url }}" width="1440" height="765" alt="Single Sign-On tab: SSO not enabled, Set up SAML SSO button" loading="lazy" decoding="async"></p>

SAML SSO can be set up or joined from an existing configuration; the tab is present on the free plan. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/23-data-access-users.webp' | relative_url }}" width="1440" height="765" alt="Data Access Control, Users tab, no users defined" loading="lazy" decoding="async"></p>

Data Access is database-level RBAC: users, roles and Redis ACLs. A role must exist before a user can be added. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/24-data-access-roles.webp' | relative_url }}" width="1440" height="765" alt="Roles tab, no roles defined" loading="lazy" decoding="async"></p>

Roles bind ACL rules to databases. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/25-redis-acls.webp' | relative_url }}" width="1440" height="765" alt="Redis ACLs tab with three default rules" loading="lazy" decoding="async"></p>

Three default ACL rules: Full-Access +@all ~*, Read-Write +@all -@dangerous ~*, Read-Only +@read ~*. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/26-billing-history.webp' | relative_url }}" width="1440" height="765" alt="Billing history: no billing history" loading="lazy" decoding="async"></p>

Billing has Billing History, Payment Methods and Credits, plus a Cost report button. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/27-payment-methods.webp' | relative_url }}" width="1440" height="765" alt="Payment methods: no card, Add credit card button" loading="lazy" decoding="async"></p>

No card on file: the free plan does not ask for one. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/28-credits.webp' | relative_url }}" width="1440" height="765" alt="Credits tab with a coupon code field, amount used and remaining both $0" loading="lazy" decoding="async"></p>

Credits: coupon codes and their balance. The Pro "First $200 free" offer does not show here before a Pro subscription exists. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/29-integrations.webp' | relative_url }}" width="1440" height="765" alt="Integrations page: Datadog, Confluent, Grafana and Prometheus" loading="lazy" decoding="async"></p>

Integrations: Datadog and Grafana/Prometheus for metrics, Confluent for Kafka data into Redis. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/30-settings.webp' | relative_url }}" width="1440" height="1248" alt="Account settings: account info, contacts, MFA enforcement off, certificate authority download, time zone UTC" loading="lazy" decoding="async"></p>

Settings: account info, business contacts, MFA enforcement (off by default), the Redis Cloud CA bundle for TLS clients, time zone. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/31-account-menu.webp' | relative_url }}" width="1440" height="765" alt="Account menu open: account switcher, user profile, logout" loading="lazy" decoding="async"></p>

The account menu switches between accounts and opens the user profile. <small>Captured 2026-11-07, Redis Cloud free plan.</small>

### Lab: the free database and its limits

**Verified on Redis 8.6.2 (Redis Cloud free plan, AWS ap-northeast-2), 2026-11-07.** Client: redis-py 6.1.1 from a host in Korea, round trip about 2.6 ms, plain TCP (the free plan has no TLS). Source and full output: [`cloud/01-free-database`](https://github.com/litkhai/notes-on-redis/tree/main/cloud/01-free-database).

| Advertised limit | What the client saw |
|---|---|
| 30 connections | Connection 31 refused: `max number of clients reached` |
| 30 MB | Writes refused at about 28 MB of 10 kB values: `OOM command not allowed when used memory > 'maxmemory'`; no keys evicted (volatile-lru, no key had a TTL) |
| 100 ops/s | Not enforced in this run: about 104,000 INCR/s for 60 s on 8 connections with pipelines of 100, no errors; the console showed 61,806 / 100 and a warning |

One connection without pipelining reached 249 ops/s, which is the round trip, not the plan. The ops/s figure looks like a sizing guide that the console reports against, not a throttle; that may change without notice, so do not build on the overage.

### First-week checklist

- Set a **CIDR allow list**: the free database starts at 0.0.0.0/0. **TLS** cannot be turned on on the free plan (the API refuses with `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`), so keep test data only, or move to a paid plan and turn TLS on there.
- Replace the default user with **Data Access** users and roles, or at least rotate its password.
- Decide the **eviction policy**: volatile-lru refuses writes when no key has a TTL.
- Keep the **alerts** at 80% or lower; the free plan has no replication, persistence or backups to fall back on.
- Turn on **MFA enforcement** in Settings once more people join.
- If you enable the **API**, delete user keys you no longer use; the system log names the key on every call it makes.

### Not covered yet

Essentials in Seoul with replication, persistence, backups and RBAC, the REST API lab, and Pro Active-Active are separate labs with their own issues in the repository.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

**Redis Cloud 시작하기: 가입부터 콘솔 메뉴 전체까지.** 2026-11-07에 무료 플랜으로 캡처했다. 무료 DB 하나(Redis 8.6, AWS ap-northeast-2 서울), 콘솔은 다크 모드, 결제한 것은 없다. Essentials와 Pro 양식은 열어서 캡처만 하고 제출하지 않았다. 모든 캡처에서 가린 것: 이름, 이메일, 계정 번호, 구독·DB ID, 엔드포인트, 포트, IP 주소, API 키. 이 페이지의 가격은 2026-11-07에 콘솔에서 읽었다.

### 한눈에 보기

왼쪽 사이드바를 위에서부터: **Databases**, **Subscriptions**, **Redis Search**, **Data Integration**. *AI services* 아래 **Iris**와 그 하위 Agent Playbooks, Agent Memory, Context Gateway, Intent Router, Lens(베타), Agent Mesh(베타), Access & Identity. *Reports* 아래 **Logs**, **Usage**. *Account* 아래 **API Keys & Team**, **Data Access**, **Billing**, **Integrations**, **Settings**. 위쪽 막대에는 앱 전환, 팁 아이콘, 테마 스위치(밝게·어둡게·시스템), 계정 메뉴가 있다.

<p class="shot"><img src="{{ '/assets/img/cloud-console/01-databases-empty.webp' | relative_url }}" width="1440" height="765" alt="New database 버튼만 있는 빈 Databases 화면" loading="lazy" decoding="async"></p>

새 계정은 비어 있는 Databases 화면에서 시작한다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### DB 만들기

**New database**를 누르면 플랜 카드 두 장이 있는 한 페이지가 열린다. **Essentials**는 공유 인프라로 시간당 $0.007(월 $5)부터. **Pro**는 전용 인프라로 시간당 $0.014부터, 월 최소 $200, "First $200 free" 표시가 붙어 있다. 카드 아래 *Not ready? Try 30 MB for free* 문구의 링크가 무료 플랜으로 가는 유일한 길이다.

<p class="shot"><img src="{{ '/assets/img/cloud-console/02-create-essentials-form.webp' | relative_url }}" width="1440" height="2118" alt="Essentials 생성 양식: 클라우드와 리전, 이름, 버전 8.6, 크기 슬라이더, 고가용성과 영속성 옵션, 결제 수단" loading="lazy" decoding="async"></p>

Essentials 기본값: AWS us-east-1, Redis 8.6, 총 250 MB(데이터 125 MB와 복제본 125 MB), 1,000 ops/s, 단일 존 복제와 1초마다 AOF, 월 $8. 크기는 250 MB부터 100 GB까지, RAM+SSD(Flex)는 토글이다. Confirm & pay 전에 결제 수단이 필요하다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/03-create-pro-form.webp' | relative_url }}" width="1440" height="2338" alt="Pro 생성 양식: Easy create와 Custom settings, 클라우드 타일, 리전, 데이터 크기와 처리량 조절, 영속성, 고가용성, 가격 요약" loading="lazy" decoding="async"></p>

Pro는 설정 방식부터 고른다. Easy create 또는 Custom settings. Easy create 기본값: 데이터 3 GB(복제본 포함 총 메모리 6 GB), 3,000 ops/s, 1초마다 AOF, 고가용성 켬, 시간당 $0.274(월 약 $200). <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/04-create-free-form.webp' | relative_url }}" width="1440" height="1259" alt="무료 플랜 생성 양식: 리전 Asia Pacific (Seoul), 이름 notes-on-redis-free, 포함된 한도" loading="lazy" decoding="async"></p>

무료 양식은 포함된 것을 보여 준다. DB 1개, RAM 30 MB, 커넥션 30개, 100 ops/sec, 월 $0. 리전은 고를 수 있다(AWS, Google Cloud, Azure 중 서울 선택). 이 캡처만 밝은 테마다. 계정에 무료 DB가 생기면 이 양식은 다시 열리지 않는다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### DB 화면

Create database를 누르면 몇 초 뒤 DB 페이지로 넘어간다. 탭은 Configuration, Metrics, Alerts, Slowlog 네 개다. 처음 들어가면 설정 안내 창이 뜨고, 닫아도 아무것도 적용되지 않는다.

<p class="shot"><img src="{{ '/assets/img/cloud-console/05-database-setup-dialog.webp' | relative_url }}" width="1440" height="765" alt="새 DB 페이지 위의 Set up your database 안내 창" loading="lazy" decoding="async"></p>

"확인하기 전에는 아무 변경도 적용되지 않는다." 검토하지 않고 닫았다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/06-database-configuration.webp' | relative_url }}" width="1440" height="1977" alt="무료 DB의 Configuration 탭: 사용량 카드, 플랜 슬라이더, 가용성과 백업, 접속, 데이터, 보안, DB 정보 패널" loading="lazy" decoding="async"></p>

화면에 보이는 무료 DB 기본값: 복제 없음, 영속성 없음, 원격 백업 꺼짐, 축출 정책 volatile-lru, 기본 사용자 켬, CIDR 허용 목록 꺼짐, TLS 꺼짐(무료 플랜에서는 켤 수 없음), RESP3, Redis 8.6. Logs 화면에는 허용 목록이 0.0.0.0/0으로 기록된다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/07-connect-dialog.webp' | relative_url }}" width="1440" height="765" alt="Redis CLI, Redis Insight, Redis SDK clients 항목이 있는 Connect 패널" loading="lazy" decoding="async"></p>

Connect는 공개 엔드포인트로 접속하는 redis-cli 명령을 바로 준다. 비밀번호는 눈 아이콘을 누르기 전까지 가려져 있다. 엔드포인트는 db.redis.io 아래 생성된 호스트 이름이다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/08-database-metrics.webp' | relative_url }}" width="1440" height="1587" alt="부하 시험 중 Metrics 탭: 초당 연산이 8만 2천까지 오르는 차트와 지연, 커넥션, 키, 메모리, 네트워크 차트" loading="lazy" decoding="async"></p>

범위는 5분부터 3개월까지. 차트: ops/sec, 지연(읽기·쓰기·기타로도 나뉨), 커넥션, 초당 축출·만료 객체, 전체 키, 초당 읽기·쓰기·기타 명령, 읽기 적중률, 사용 메모리, 네트워크 송신·수신. 아래 처리량 시험 중에 캡처했다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/09-database-throughput-over-limit.webp' | relative_url }}" width="1440" height="765" alt="처리량 카드에 경고 아이콘과 함께 100 중 61,806 ops/sec 표시" loading="lazy" decoding="async"></p>

시험 중 처리량 카드: 61,806 / 100 ops/sec. 콘솔은 초과를 표시하지만 DB는 계속 응답했다(아래 측정 참조). <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/10-database-alerts.webp' | relative_url }}" width="1440" height="765" alt="데이터 크기와 커넥션 알림이 각각 플랜 한도의 80%로 설정된 Alerts 탭" loading="lazy" decoding="async"></p>

무료 플랜 알림: 데이터 크기와 커넥션 수, 각각 플랜 한도 대비 %로 80%가 미리 설정돼 있다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/11-database-slowlog.webp' | relative_url }}" width="1440" height="765" alt="항목 없는 Slowlog 탭과 Clear slowlog 버튼" loading="lazy" decoding="async"></p>

시험이 INCR과 SET만 써서 Slowlog는 비어 있었다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### DB와 구독

모든 DB는 구독에 속한다. 무료 플랜은 DB 하나를 담은 구독 하나를 만든다.

<p class="shot"><img src="{{ '/assets/img/cloud-console/12-databases-list.webp' | relative_url }}" width="1440" height="765" alt="Databases 목록 한 줄: notes-on-redis-free, 메모리 사용 30 MB 중 7.4%, 버전 8.6" loading="lazy" decoding="async"></p>

열: 상태, DB 이름, 구독, 엔드포인트(Connect 버튼), 메모리 사용, 기능, 태그, 버전, 작업. 상태·구독·플랜·기능·버전·리전·클라우드 필터. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/13-subscriptions.webp' | relative_url }}" width="1440" height="765" alt="무료 구독 카드와 그 DB 목록이 있는 Subscriptions 화면" loading="lazy" decoding="async"></p>

ap-northeast-2의 무료 구독. Plan upgrade 버튼과 Databases, Overview 탭. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### 제품 메뉴

사이드바 세 항목은 설정이 아니라 제품으로 들어가는 입구다.

<p class="shot"><img src="{{ '/assets/img/cloud-console/14-redis-search.webp' | relative_url }}" width="1440" height="818" alt="에이전트용 벡터 검색을 소개하고 DB 선택 칸이 있는 Redis Search 화면" loading="lazy" decoding="async"></p>

Redis Search는 기존 DB에 첫 벡터 인덱스를 만드는 안내 화면이다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/15-data-integration.webp' | relative_url }}" width="1440" height="1489" alt="Data Integration 화면: Redis로의 준실시간 동기화, 시간당 $1.37, 세 단계" loading="lazy" decoding="async"></p>

Data Integration은 관리형 RDI다. 시간당 $1.37, 월 약 $1,000(추정), 파이프라인을 만들 때부터 과금. 단계: 원본 DB 연결, 변환, Redis에서 읽기 제공. 여기서는 만들지 않았다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/16-iris.webp' | relative_url }}" width="1440" height="1276" alt="데모 영상과 서비스 목록이 있는 Iris AI Services 첫 화면" loading="lazy" decoding="async"></p>

Iris 첫 화면. 나열된 서비스: Agent Memory, Agent Playbooks, Intent Router, Context Gateway, Agent Mesh. Lens는 사이드바에 있다. 이 사이트의 Iris 페이지에서 하나씩 다룬다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### 리포트

<p class="shot"><img src="{{ '/assets/img/cloud-console/17-logs-system.webp' | relative_url }}" width="1440" height="765" alt="시스템 로그: 구독 생성, DB 활성화, 영속성 끔, 원본 IP 추가, RESP3 켬, API 켬, API 키 할당" loading="lazy" decoding="async"></p>

시스템 로그는 모든 설정 이벤트를 시각, 실행자, API 키 이름과 함께 보여 준다. Export all로 내려받는다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/18-logs-sessions.webp' | relative_url }}" width="1440" height="765" alt="성공한 로그인 두 건이 있는 Sessions 로그" loading="lazy" decoding="async"></p>

Sessions: 콘솔 로그인마다 사용자 에이전트, IP, 역할, 로그인 방식. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/19-usage.webp' | relative_url }}" width="1440" height="765" alt="Usage 리포트 Memory Usage 탭, 2026년 11월 일별 차트" loading="lazy" decoding="async"></p>

Usage에는 Memory Usage, RBU Usage 탭과 Cost report 내려받기가 있다. DB를 막 만들었을 때는 한 시간 뒤에 리포트가 나온다고 했고, 마지막 캡처 때는 데이터가 보였다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### 계정

<p class="shot"><img src="{{ '/assets/img/cloud-console/20-api-keys.webp' | relative_url }}" width="1440" height="765" alt="계정 키가 가려진 API Keys 탭과 사용자 키 한 개" loading="lazy" decoding="async"></p>

Enable API는 무료 플랜에서도 된다. 호출에는 계정 키와 사용자 키가 함께 필요하다. 사용자 키 하나를 만들었고 GET /v1/fixed/subscriptions가 200을 돌려줬다. 무료와 Essentials 구독은 /v1/fixed 아래, Pro는 /v1/subscriptions 아래에 있다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/21-team.webp' | relative_url }}" width="1440" height="765" alt="Google로 가입한 소유자 한 명이 있는 Team 탭" loading="lazy" decoding="async"></p>

Team: 콘솔 사용자와 역할, 가입 방식. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/22-single-sign-on.webp' | relative_url }}" width="1440" height="765" alt="Single Sign-On 탭: SSO 꺼짐, Set up SAML SSO 버튼" loading="lazy" decoding="async"></p>

SAML SSO를 새로 설정하거나 기존 설정에 합류할 수 있다. 무료 플랜에도 탭이 있다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/23-data-access-users.webp' | relative_url }}" width="1440" height="765" alt="Data Access Control의 Users 탭, 사용자 없음" loading="lazy" decoding="async"></p>

Data Access는 DB 수준 RBAC다. 사용자, 역할, Redis ACL. 사용자를 추가하려면 역할이 먼저 있어야 한다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/24-data-access-roles.webp' | relative_url }}" width="1440" height="765" alt="Roles 탭, 역할 없음" loading="lazy" decoding="async"></p>

역할은 ACL 규칙을 DB에 연결한다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/25-redis-acls.webp' | relative_url }}" width="1440" height="765" alt="기본 규칙 세 개가 있는 Redis ACLs 탭" loading="lazy" decoding="async"></p>

기본 ACL 규칙 세 개: Full-Access +@all ~*, Read-Write +@all -@dangerous ~*, Read-Only +@read ~*. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/26-billing-history.webp' | relative_url }}" width="1440" height="765" alt="Billing History: 청구 내역 없음" loading="lazy" decoding="async"></p>

Billing에는 Billing History, Payment Methods, Credits 탭과 Cost report 버튼이 있다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/27-payment-methods.webp' | relative_url }}" width="1440" height="765" alt="Payment Methods: 카드 없음, Add credit card 버튼" loading="lazy" decoding="async"></p>

등록된 카드 없음. 무료 플랜은 카드를 요구하지 않는다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/28-credits.webp' | relative_url }}" width="1440" height="765" alt="쿠폰 코드 칸과 사용액·잔액 모두 $0인 Credits 탭" loading="lazy" decoding="async"></p>

Credits: 쿠폰 코드와 잔액. Pro의 "First $200 free"는 Pro 구독이 생기기 전에는 여기 보이지 않는다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/29-integrations.webp' | relative_url }}" width="1440" height="765" alt="Integrations 화면: Datadog, Confluent, Grafana와 Prometheus" loading="lazy" decoding="async"></p>

Integrations: 지표용 Datadog과 Grafana/Prometheus, Kafka 데이터를 Redis로 보내는 Confluent. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/30-settings.webp' | relative_url }}" width="1440" height="1248" alt="계정 설정: 계정 정보, 연락처, MFA 강제 꺼짐, 인증 기관 내려받기, 시간대 UTC" loading="lazy" decoding="async"></p>

Settings: 계정 정보, 사업자 연락처, MFA 강제(기본 꺼짐), TLS 클라이언트용 Redis Cloud CA 번들, 시간대. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/31-account-menu.webp' | relative_url }}" width="1440" height="765" alt="계정 메뉴 열림: 계정 전환, 사용자 프로필, 로그아웃" loading="lazy" decoding="async"></p>

계정 메뉴에서 계정을 바꾸고 사용자 프로필을 연다. <small>2026-11-07 캡처, Redis Cloud 무료 플랜.</small>

### 실습: 무료 DB와 그 한도

**확인: Redis 8.6.2(Redis Cloud 무료 플랜, AWS ap-northeast-2), 2026-11-07.** 클라이언트: 한국의 호스트에서 redis-py 6.1.1, 왕복 약 2.6 ms, 평문 TCP(무료 플랜에는 TLS가 없음). 소스와 전체 출력: [`cloud/01-free-database`](https://github.com/litkhai/notes-on-redis/tree/main/cloud/01-free-database).

| 안내된 한도 | 클라이언트가 본 것 |
|---|---|
| 커넥션 30개 | 31번째 연결 거절: `max number of clients reached` |
| 30 MB | 10 kB 값으로 약 28 MB에서 쓰기 거절: `OOM command not allowed when used memory > 'maxmemory'`. 축출된 키 없음(volatile-lru인데 TTL 있는 키가 없음) |
| 100 ops/s | 이번 실행에서는 걸리지 않음: 8개 연결, 파이프라인 100으로 60초 동안 초당 약 104,000 INCR, 오류 없음. 콘솔은 61,806 / 100과 경고를 표시 |

파이프라인 없이 연결 하나로는 249 ops/s였다. 이것은 플랜이 아니라 왕복 시간 때문이다. ops/s 수치는 제한이 아니라 콘솔이 비교해 보여 주는 크기 기준으로 보인다. 예고 없이 바뀔 수 있으니 초과 처리량에 기대어 설계하지 말 것.

### 첫 주 체크리스트

- **CIDR 허용 목록**을 정한다. 무료 DB는 0.0.0.0/0으로 시작한다. 무료 플랜에서는 **TLS**를 켤 수 없으므로(API가 `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`으로 거절) 시험 데이터만 두거나, 유료 플랜으로 옮겨 거기서 TLS를 켠다.
- 기본 사용자 대신 **Data Access**의 사용자와 역할을 쓰거나, 최소한 비밀번호를 바꾼다.
- **축출 정책**을 정한다. volatile-lru는 TTL 있는 키가 없으면 쓰기를 거절한다.
- **알림**은 80% 이하로 둔다. 무료 플랜은 복제, 영속성, 백업이 없다.
- 사람이 늘면 Settings에서 **MFA 강제**를 켠다.
- **API**를 켰다면 안 쓰는 사용자 키를 지운다. 시스템 로그는 호출마다 키 이름을 남긴다.

### 아직 다루지 않은 것

서울 Essentials의 복제·영속·백업·RBAC, REST API 실습, Pro Active-Active는 저장소에 각자의 이슈가 있는 별도 실습이다.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

**Redis Cloud：从注册到控制台的每个菜单。** 2026-11-07 在免费计划上截取：一个免费数据库（Redis 8.6，AWS ap-northeast-2 首尔），控制台为深色模式，未产生任何付费。Essentials 和 Pro 的表单已打开并截图，但没有提交。每张截图中都已遮盖：姓名、电子邮件、账号编号、订阅和数据库 ID、endpoint、端口、IP 地址、API 密钥。本页的价格均于 2026-11-07 在控制台中读取。

### 概览

左侧边栏从上到下：**Databases**、**Subscriptions**、**Redis Search**、**Data Integration**；在 *AI services* 下是 **Iris**，包含 Agent Playbooks、Agent Memory、Context Gateway、Intent Router、Lens (beta)、Agent Mesh (beta) 和 Access & Identity；在 *Reports* 下是 **Logs** 和 **Usage**；在 *Account* 下是 **API Keys & Team**、**Data Access**、**Billing**、**Integrations**、**Settings**。顶部栏包含应用切换器、提示图标、主题切换（浅色、深色、跟随系统）和账户菜单。

<p class="shot"><img src="{{ '/assets/img/cloud-console/01-databases-empty.webp' | relative_url }}" width="1440" height="765" alt="带有 New database 按钮的空 Databases 页面" loading="lazy" decoding="async"></p>

新账户首先进入的是空的 Databases 页面。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### 创建数据库

**New database** 会打开一个带有两张计划卡片的页面。**Essentials** 是共享基础设施，起价 $0.007/小时（$5/月）。**Pro** 是专用基础设施，起价 $0.014/小时，最低 $200/月，并带有 “First $200 free” 标记。卡片下方有一行 *Not ready? Try 30 MB for free*；这个链接是进入免费计划的唯一途径。

<p class="shot"><img src="{{ '/assets/img/cloud-console/02-create-essentials-form.webp' | relative_url }}" width="1440" height="2118" alt="Essentials 创建表单：云厂商和区域、名称、版本 8.6、容量滑块、高可用和持久化选项、支付方式" loading="lazy" decoding="async"></p>

Essentials 默认值：AWS us-east-1，Redis 8.6，总计 250 MB（数据集 125 MB 加副本 125 MB），1,000 ops/s，单可用区复制，每秒 AOF，$8/月。容量范围为 250 MB 到 100 GB；RAM+SSD (Flex) 是一个开关。在 Confirm & pay 之前必须先添加支付方式。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/03-create-pro-form.webp' | relative_url }}" width="1440" height="2338" alt="Pro 创建表单：Easy create 或 Custom settings、云厂商图块、区域、数据集大小和吞吐量调节、持久化、高可用、价格汇总" loading="lazy" decoding="async"></p>

Pro 首先要选择设置方式：Easy create 或 Custom settings。Easy create 默认值：数据集 3 GB（含副本共 6 GB 内存），3,000 ops/s，每秒 AOF，开启高可用，$0.274/小时（约 $200/月）。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/04-create-free-form.webp' | relative_url }}" width="1440" height="1259" alt="免费计划创建表单，区域为 Asia Pacific (Seoul)，名称为 notes-on-redis-free，并列出包含的限制" loading="lazy" decoding="async"></p>

免费表单列出了包含的内容：1 个数据库、30 MB RAM、30 个连接、100 ops/sec、$0/月。区域可以选择（AWS、Google Cloud 或 Azure；这里选了首尔）。只有这张截图是浅色模式；账户有了免费数据库之后，这个表单就无法再次打开。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### 数据库页面

点击 Create database 后，几秒钟内会进入数据库页面。页面有四个标签页：Configuration、Metrics、Alerts、Slowlog。首次访问时会弹出引导设置对话框；关闭它不会应用任何更改。

<p class="shot"><img src="{{ '/assets/img/cloud-console/05-database-setup-dialog.webp' | relative_url }}" width="1440" height="765" alt="新数据库页面上方的 Set up your database 对话框" loading="lazy" decoding="async"></p>

“No changes are applied until you confirm.” 对话框未经查看就被关闭了。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/06-database-configuration.webp' | relative_url }}" width="1440" height="1977" alt="免费数据库的 Configuration 标签页：用量卡片、计划滑块、可用性与备份、访问、数据、安全和数据库信息面板" loading="lazy" decoding="async"></p>

画面所示的免费数据库默认值：无复制、无持久化、远程备份关闭、淘汰策略 volatile-lru、默认用户开启、CIDR allow list 关闭、TLS 关闭（免费计划无法开启）、RESP3、Redis 8.6。Logs 页面将 allow list 记录为 0.0.0.0/0。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/07-connect-dialog.webp' | relative_url }}" width="1440" height="765" alt="Connect 抽屉，包含 Redis CLI、Redis Insight 和 Redis SDK clients 三个部分" loading="lazy" decoding="async"></p>

Connect 直接给出通过公网 endpoint 连接的 redis-cli 命令；密码在点击眼睛图标之前保持隐藏。endpoint 是 db.redis.io 下生成的主机名。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/08-database-metrics.webp' | relative_url }}" width="1440" height="1587" alt="负载测试期间的 Metrics 标签页：每秒操作数升至 8.2 万，另有延迟、连接、键、内存和网络图表" loading="lazy" decoding="async"></p>

范围从 5 分钟到 3 个月。图表：ops/sec、延迟（也按读、写、其他拆分）、连接、每秒被淘汰和过期的对象、总键数、每秒读、每秒写、每秒其他命令、读命中率、已用内存、网络出口和入口。截取于下文的吞吐量测试期间。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/09-database-throughput-over-limit.webp' | relative_url }}" width="1440" height="765" alt="吞吐量卡片显示 100 ops/sec 中的 61,806，并带有警告图标" loading="lazy" decoding="async"></p>

测试期间的吞吐量卡片：61,806 / 100 ops/sec。控制台标出了超额，但数据库仍在继续响应（见下文的测量结果）。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/10-database-alerts.webp' | relative_url }}" width="1440" height="765" alt="Alerts 标签页，数据集大小和连接数两个告警，均为计划限制的 80%" loading="lazy" decoding="async"></p>

免费计划的告警：数据集大小和连接数，均为计划限制的百分比，预设为 80%。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/11-database-slowlog.webp' | relative_url }}" width="1440" height="765" alt="没有条目的 Slowlog 标签页，带有 Clear slowlog 按钮" loading="lazy" decoding="async"></p>

Slowlog 一直为空：测试只使用了 INCR 和 SET。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Databases 与 subscriptions

每个数据库都属于一个 subscription。免费计划会创建一个包含一个数据库的 subscription。

<p class="shot"><img src="{{ '/assets/img/cloud-console/12-databases-list.webp' | relative_url }}" width="1440" height="765" alt="Databases 列表只有一行：notes-on-redis-free，内存使用 30 MB 的 7.4%，版本 8.6" loading="lazy" decoding="async"></p>

列：状态、数据库名称、订阅、endpoint（一个 Connect 按钮）、内存使用、功能、标签、版本、操作。可按状态、订阅、计划、功能、版本、区域和云进行筛选。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/13-subscriptions.webp' | relative_url }}" width="1440" height="765" alt="Subscriptions 页面，显示免费订阅卡片及其数据库列表" loading="lazy" decoding="async"></p>

位于 ap-northeast-2 的免费订阅，带有 Plan upgrade 按钮以及 Databases 和 Overview 标签页。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### 产品菜单

侧边栏中有三个条目是产品的入口，而不是设置项。

<p class="shot"><img src="{{ '/assets/img/cloud-console/14-redis-search.webp' | relative_url }}" width="1440" height="818" alt="Redis Search 页面，介绍面向 agent 的向量搜索，带有数据库选择器" loading="lazy" decoding="async"></p>

Redis Search 是在现有数据库上创建第一个向量索引的引导式入口。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/15-data-integration.webp' | relative_url }}" width="1440" height="1489" alt="Data Integration 页面：近实时同步到 Redis，$1.37 每小时，三个步骤" loading="lazy" decoding="async"></p>

Data Integration 是托管的 RDI：$1.37/小时，预估约 $1,000/月，从创建 pipeline 时开始计费。步骤：连接源数据库、转换、从 Redis 提供读取。这里没有创建。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/16-iris.webp' | relative_url }}" width="1440" height="1276" alt="Iris AI Services 首页，带有演示视频和服务列表" loading="lazy" decoding="async"></p>

Iris 首页。列出的服务：Agent Memory、Agent Playbooks、Intent Router、Context Gateway、Agent Mesh；Lens 出现在侧边栏中。本站的 Iris 页面会逐一介绍它们。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Reports

<p class="shot"><img src="{{ '/assets/img/cloud-console/17-logs-system.webp' | relative_url }}" width="1440" height="765" alt="系统日志：订阅已创建、数据库已激活、持久化已禁用、已添加源 IP、已启用 RESP3、已启用 API、已分配 API 密钥" loading="lazy" decoding="async"></p>

系统日志列出每个配置事件，包括时间、发起者和 API 密钥名称；Export all 可下载它。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/18-logs-sessions.webp' | relative_url }}" width="1440" height="765" alt="Sessions 日志，有两次成功登录" loading="lazy" decoding="async"></p>

Sessions：每次控制台登录，包含 user agent、IP、角色和登录类型。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/19-usage.webp' | relative_url }}" width="1440" height="765" alt="Usage 报告，Memory Usage 标签页，2026 年 11 月的每日图表" loading="lazy" decoding="async"></p>

Usage 有 Memory Usage 和 RBU Usage 两个标签页，以及 Cost report 下载。数据库刚创建后，它提示报告将在一小时后出现；到最后一次截图时已经有数据。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### Account

<p class="shot"><img src="{{ '/assets/img/cloud-console/20-api-keys.webp' | relative_url }}" width="1440" height="765" alt="API Keys 标签页，账户密钥已隐藏，另有一个用户密钥" loading="lazy" decoding="async"></p>

Enable API 在免费计划上可用。调用需要账户密钥和用户密钥；创建了一个用户密钥，GET /v1/fixed/subscriptions 返回了 200。免费和 Essentials 订阅位于 /v1/fixed 下，Pro 位于 /v1/subscriptions 下。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/21-team.webp' | relative_url }}" width="1440" height="765" alt="Team 标签页，有一位通过 Google 注册的所有者" loading="lazy" decoding="async"></p>

Team：控制台用户、他们的角色和注册类型。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/22-single-sign-on.webp' | relative_url }}" width="1440" height="765" alt="Single Sign-On 标签页：SSO 未启用，带有 Set up SAML SSO 按钮" loading="lazy" decoding="async"></p>

SAML SSO 可以新建，也可以加入现有配置；免费计划上也有这个标签页。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/23-data-access-users.webp' | relative_url }}" width="1440" height="765" alt="Data Access Control 的 Users 标签页，未定义用户" loading="lazy" decoding="async"></p>

Data Access 是数据库级别的 RBAC：用户、角色和 Redis ACL。必须先有角色，才能添加用户。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/24-data-access-roles.webp' | relative_url }}" width="1440" height="765" alt="Roles 标签页，未定义角色" loading="lazy" decoding="async"></p>

角色把 ACL 规则绑定到数据库。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/25-redis-acls.webp' | relative_url }}" width="1440" height="765" alt="Redis ACLs 标签页，有三条默认规则" loading="lazy" decoding="async"></p>

三条默认 ACL 规则：Full-Access +@all ~*，Read-Write +@all -@dangerous ~*，Read-Only +@read ~*。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/26-billing-history.webp' | relative_url }}" width="1440" height="765" alt="Billing history：没有账单记录" loading="lazy" decoding="async"></p>

Billing 有 Billing History、Payment Methods 和 Credits 标签页，以及 Cost report 按钮。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/27-payment-methods.webp' | relative_url }}" width="1440" height="765" alt="Payment methods：没有银行卡，带有 Add credit card 按钮" loading="lazy" decoding="async"></p>

没有登记银行卡：免费计划不要求提供。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/28-credits.webp' | relative_url }}" width="1440" height="765" alt="Credits 标签页，有优惠码输入框，已用金额和剩余金额均为 $0" loading="lazy" decoding="async"></p>

Credits：优惠码及其余额。在创建 Pro 订阅之前，这里不会显示 Pro 的 “First $200 free” 优惠。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/29-integrations.webp' | relative_url }}" width="1440" height="765" alt="Integrations 页面：Datadog、Confluent、Grafana 和 Prometheus" loading="lazy" decoding="async"></p>

Integrations：用于指标的 Datadog 和 Grafana/Prometheus，以及把 Kafka 数据送入 Redis 的 Confluent。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/30-settings.webp' | relative_url }}" width="1440" height="1248" alt="账户设置：账户信息、联系人、MFA 强制关闭、证书颁发机构下载、时区 UTC" loading="lazy" decoding="async"></p>

Settings：账户信息、业务联系人、MFA enforcement（默认关闭）、供 TLS 客户端使用的 Redis Cloud CA bundle、时区。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/31-account-menu.webp' | relative_url }}" width="1440" height="765" alt="账户菜单已展开：账户切换、用户资料、退出登录" loading="lazy" decoding="async"></p>

账户菜单可在多个账户之间切换，并打开用户资料。 <small>2026-11-07 截图，Redis Cloud 免费计划。</small>

### 实验：免费数据库及其限制

**已在 Redis 8.6.2 上验证（Redis Cloud 免费计划，AWS ap-northeast-2），2026-11-07。** 客户端：来自韩国主机的 redis-py 6.1.1，往返约 2.6 ms，明文 TCP（免费计划没有 TLS）。源码和完整输出：[`cloud/01-free-database`](https://github.com/litkhai/notes-on-redis/tree/main/cloud/01-free-database)。

| 标称限制 | 客户端实际看到的 |
|---|---|
| 30 个连接 | 第 31 个连接被拒绝：`max number of clients reached` |
| 30 MB | 写入 10 kB 的值，在约 28 MB 时被拒绝：`OOM command not allowed when used memory > 'maxmemory'`；没有键被淘汰（volatile-lru，没有键带 TTL） |
| 100 ops/s | 本次运行中未强制执行：在 8 个连接上以 100 条一批的 pipeline 持续 60 秒，约 104,000 INCR/s，无错误；控制台显示 61,806 / 100 并给出警告 |

不使用 pipeline 的单个连接达到 249 ops/s，这是往返时间决定的，与计划无关。ops/s 的数值更像是控制台用来对照显示的规格参考，而不是限流；这一点可能会在没有通知的情况下改变，所以不要依赖超出限额的行为。

### 第一周检查清单

- 设置 **CIDR allow list**：免费数据库默认为 0.0.0.0/0。免费计划无法开启 **TLS**（API 会以 `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN` 拒绝），所以只放测试数据，或者升级到付费计划并在那里开启 TLS。
- 用 **Data Access** 的用户和角色替换默认用户，或者至少轮换它的密码。
- 确定 **eviction policy**：当没有键带 TTL 时，volatile-lru 会拒绝写入。
- 将 **alerts** 保持在 80% 或更低；免费计划没有复制、持久化或备份可作后备。
- 当有更多人加入时，在 Settings 中开启 **MFA enforcement**。
- 如果启用了 **API**，请删除不再使用的用户密钥；系统日志会记录每次调用所用的密钥名称。

### 尚未涵盖

Essentials 首尔区域的复制、持久化、备份和 RBAC，REST API 实验，以及 Pro Active-Active，都是独立的实验，在仓库中各有自己的 issue。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

**Redis Cloud のサインアップからコンソールの全メニューまで。** 2026-11-07 に無料プランで取得しました。無料データベース 1 つ（Redis 8.6、AWS ap-northeast-2 ソウル）、コンソールはダークモードで、有料のものは使っていません。Essentials と Pro のフォームは開いてキャプチャしましたが、送信していません。すべてのスクリーンショットで、氏名、メールアドレス、アカウント番号、サブスクリプションとデータベースの ID、エンドポイント、ポート、IP アドレス、API キーをマスクしています。このページの価格は 2026-11-07 にコンソールで確認したものです。

### 全体像

左サイドバーは上から順に、**Databases**、**Subscriptions**、**Redis Search**、**Data Integration**。*AI services* の下に **Iris** があり、Agent Playbooks、Agent Memory、Context Gateway、Intent Router、Lens (beta)、Agent Mesh (beta)、Access & Identity が並びます。*Reports* の下は **Logs** と **Usage**、*Account* の下は **API Keys & Team**、**Data Access**、**Billing**、**Integrations**、**Settings** です。トップバーには、アプリスイッチャー、ヒントアイコン、テーマ切り替え（ライト、ダーク、システム）、アカウントメニューがあります。

<p class="shot"><img src="{{ '/assets/img/cloud-console/01-databases-empty.webp' | relative_url }}" width="1440" height="765" alt="New database ボタンだけの空の Databases 画面" loading="lazy" decoding="async"></p>

新しいアカウントは、何もない Databases 画面から始まります。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

### データベースを作成する

**New database** を押すと、2 枚のプランカードがある 1 ページが開きます。**Essentials** は共有インフラで、$0.007/時間（$5/月）から。**Pro** は専用インフラで、$0.014/時間から、最低 $200/月で、「First $200 free」のバッジが付いています。カードの下に *Not ready? Try 30 MB for free* という行があり、このリンクが無料プランへの唯一の入口です。

<p class="shot"><img src="{{ '/assets/img/cloud-console/02-create-essentials-form.webp' | relative_url }}" width="1440" height="2118" alt="Essentials の作成フォーム：クラウドベンダーとリージョン、名前、バージョン 8.6、サイズのスライダー、高可用性と永続化のオプション、支払い方法" loading="lazy" decoding="async"></p>

Essentials のデフォルト：AWS us-east-1、Redis 8.6、合計 250 MB（データセット 125 MB とレプリカ 125 MB）、1,000 ops/s、シングルゾーンのレプリケーション、毎秒 AOF、$8/月。サイズは 250 MB から 100 GB まで。RAM+SSD (Flex) はトグルです。Confirm & pay の前に支払い方法が必要です。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/03-create-pro-form.webp' | relative_url }}" width="1440" height="2338" alt="Pro の作成フォーム：Easy create または Custom settings、クラウドベンダーのタイル、リージョン、データセットサイズとスループットのステッパー、永続化、高可用性、料金サマリー" loading="lazy" decoding="async"></p>

Pro はまずセットアップ方法を選びます。Easy create または Custom settings。Easy create のデフォルト：データセット 3 GB（レプリカを含めメモリ合計 6 GB）、3,000 ops/s、毎秒 AOF、高可用性オン、$0.274/時間（月約 $200）。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/04-create-free-form.webp' | relative_url }}" width="1440" height="1259" alt="無料プランの作成フォーム。リージョンは Asia Pacific (Seoul)、名前は notes-on-redis-free、含まれる制限が表示されている" loading="lazy" decoding="async"></p>

無料フォームには含まれるものが表示されます。データベース 1 つ、RAM 30 MB、30 接続、100 ops/sec、$0/月。リージョンは選べます（AWS、Google Cloud、Azure。ここではソウルを選択）。このキャプチャだけライトモードです。アカウントに無料データベースができると、このフォームは再度開けません。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

### データベース画面

Create database を押すと、数秒でデータベースのページに移ります。ページには Configuration、Metrics、Alerts、Slowlog の 4 つのタブがあります。初回訪問時にはガイド付きセットアップのダイアログが表示されますが、閉じても何も適用されません。

<p class="shot"><img src="{{ '/assets/img/cloud-console/05-database-setup-dialog.webp' | relative_url }}" width="1440" height="765" alt="新しいデータベースのページに重なった Set up your database ダイアログ" loading="lazy" decoding="async"></p>

「No changes are applied until you confirm.」ダイアログは確認せずに閉じました。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/06-database-configuration.webp' | relative_url }}" width="1440" height="1977" alt="無料データベースの Configuration タブ：使用量カード、プランのスライダー、可用性とバックアップ、アクセス、データ、セキュリティ、データベース情報のパネル" loading="lazy" decoding="async"></p>

画面に表示される無料データベースのデフォルト：レプリケーションなし、永続化なし、リモートバックアップオフ、eviction policy は volatile-lru、デフォルトユーザーはオン、CIDR allow list はオフ、TLS オフ（無料プランでは有効にできません）、RESP3、Redis 8.6。Logs 画面では allow list が 0.0.0.0/0 と記録されています。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/07-connect-dialog.webp' | relative_url }}" width="1440" height="765" alt="Redis CLI、Redis Insight、Redis SDK clients の各セクションがある Connect ドロワー" loading="lazy" decoding="async"></p>

Connect は、パブリックエンドポイント経由の redis-cli コマンドをそのまま提示します。パスワードは目のアイコンを押すまで隠れています。エンドポイントは db.redis.io 配下に生成されたホスト名です。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/08-database-metrics.webp' | relative_url }}" width="1440" height="1587" alt="負荷試験中の Metrics タブ：毎秒の操作数が 8 万 2 千まで上昇するグラフと、レイテンシ、接続、キー、メモリ、ネットワークのグラフ" loading="lazy" decoding="async"></p>

範囲は 5 分から 3 か月まで。グラフ：ops/sec、レイテンシ（読み取り・書き込み・その他にも分割）、接続、毎秒の evicted・expired オブジェクト、総キー数、毎秒の読み取り、書き込み、その他のコマンド、読み取りヒット率、使用メモリ、ネットワークの送信と受信。下のスループット試験中にキャプチャしました。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/09-database-throughput-over-limit.webp' | relative_url }}" width="1440" height="765" alt="スループットカードに警告アイコンとともに 100 ops/sec 中 61,806 と表示されている" loading="lazy" decoding="async"></p>

試験中のスループットカード：61,806 / 100 ops/sec。コンソールは超過を表示しますが、データベースは応答し続けました（下の測定結果を参照）。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/10-database-alerts.webp' | relative_url }}" width="1440" height="765" alt="Alerts タブ。データセットサイズと接続数のアラートが、どちらもプラン上限の 80% に設定されている" loading="lazy" decoding="async"></p>

無料プランのアラート：データセットサイズと接続数。それぞれプラン上限に対する % で、80% にプリセットされています。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/11-database-slowlog.webp' | relative_url }}" width="1440" height="765" alt="エントリのない Slowlog タブと Clear slowlog ボタン" loading="lazy" decoding="async"></p>

試験では INCR と SET しか使わなかったため、Slowlog は空のままでした。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

### Databases と subscriptions

すべてのデータベースは subscription に属します。無料プランでは、データベース 1 つを含む subscription が 1 つ作られます。

<p class="shot"><img src="{{ '/assets/img/cloud-console/12-databases-list.webp' | relative_url }}" width="1440" height="765" alt="Databases 一覧の 1 行：notes-on-redis-free、メモリ使用は 30 MB の 7.4%、バージョン 8.6" loading="lazy" decoding="async"></p>

列：ステータス、データベース名、サブスクリプション、エンドポイント（Connect ボタン）、メモリ使用量、機能、タグ、バージョン、アクション。ステータス、サブスクリプション、プラン、機能、バージョン、リージョン、クラウドで絞り込めます。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/13-subscriptions.webp' | relative_url }}" width="1440" height="765" alt="無料サブスクリプションのカードとそのデータベース一覧がある Subscriptions 画面" loading="lazy" decoding="async"></p>

ap-northeast-2 の無料サブスクリプション。Plan upgrade ボタンと、Databases、Overview タブがあります。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

### プロダクトメニュー

サイドバーの 3 つの項目は、設定ではなくプロダクトへの入口です。

<p class="shot"><img src="{{ '/assets/img/cloud-console/14-redis-search.webp' | relative_url }}" width="1440" height="818" alt="エージェント向けのベクトル検索を紹介し、データベース選択欄がある Redis Search 画面" loading="lazy" decoding="async"></p>

Redis Search は、既存のデータベースに最初のベクトルインデックスを作るためのガイド付きの入口です。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/15-data-integration.webp' | relative_url }}" width="1440" height="1489" alt="Data Integration 画面：Redis へのほぼリアルタイムの同期、1 時間あたり $1.37、3 つのステップ" loading="lazy" decoding="async"></p>

Data Integration はマネージド RDI です。$1.37/時間、月約 $1,000（見積もり）、パイプラインの作成時から課金されます。ステップ：ソースデータベースに接続、変換、Redis から読み取りを提供。ここでは作成していません。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/16-iris.webp' | relative_url }}" width="1440" height="1276" alt="デモ動画とサービス一覧がある Iris AI Services のランディングページ" loading="lazy" decoding="async"></p>

Iris のランディングページ。掲載されているサービス：Agent Memory、Agent Playbooks、Intent Router、Context Gateway、Agent Mesh。Lens はサイドバーにあります。このサイトの Iris ページで 1 つずつ取り上げます。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

### Reports

<p class="shot"><img src="{{ '/assets/img/cloud-console/17-logs-system.webp' | relative_url }}" width="1440" height="765" alt="システムログ：サブスクリプション作成、データベース有効化、永続化無効化、ソース IP 追加、RESP3 有効化、API 有効化、API キー割り当て" loading="lazy" decoding="async"></p>

システムログには、すべての設定イベントが時刻、実行者、API キー名とともに並びます。Export all でダウンロードできます。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/18-logs-sessions.webp' | relative_url }}" width="1440" height="765" alt="ログインに成功した 2 件がある Sessions ログ" loading="lazy" decoding="async"></p>

Sessions：コンソールへのログインごとに、ユーザーエージェント、IP、ロール、ログイン方式が記録されます。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/19-usage.webp' | relative_url }}" width="1440" height="765" alt="Usage レポートの Memory Usage タブ、2026 年 11 月の日別グラフ" loading="lazy" decoding="async"></p>

Usage には Memory Usage と RBU Usage のタブと、Cost report のダウンロードがあります。データベースを作成した直後は、レポートが 1 時間後に表示されると案内されていましたが、最後のキャプチャ時にはデータが表示されていました。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

### Account

<p class="shot"><img src="{{ '/assets/img/cloud-console/20-api-keys.webp' | relative_url }}" width="1440" height="765" alt="アカウントキーが隠れていて、ユーザーキーが 1 つある API Keys タブ" loading="lazy" decoding="async"></p>

Enable API は無料プランでも使えます。呼び出しにはアカウントキーとユーザーキーが必要です。ユーザーキーを 1 つ作成し、GET /v1/fixed/subscriptions は 200 を返しました。無料と Essentials のサブスクリプションは /v1/fixed 配下、Pro は /v1/subscriptions 配下にあります。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/21-team.webp' | relative_url }}" width="1440" height="765" alt="Google でサインアップしたオーナーが 1 人いる Team タブ" loading="lazy" decoding="async"></p>

Team：コンソールのユーザー、ロール、サインアップ方式。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/22-single-sign-on.webp' | relative_url }}" width="1440" height="765" alt="Single Sign-On タブ：SSO は無効、Set up SAML SSO ボタン" loading="lazy" decoding="async"></p>

SAML SSO は新規に設定することも、既存の設定に参加することもできます。無料プランにもこのタブがあります。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/23-data-access-users.webp' | relative_url }}" width="1440" height="765" alt="Data Access Control の Users タブ、ユーザー未定義" loading="lazy" decoding="async"></p>

Data Access はデータベースレベルの RBAC です。ユーザー、ロール、Redis ACL。ユーザーを追加するには、先にロールが必要です。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/24-data-access-roles.webp' | relative_url }}" width="1440" height="765" alt="Roles タブ、ロール未定義" loading="lazy" decoding="async"></p>

ロールは ACL ルールをデータベースに結び付けます。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/25-redis-acls.webp' | relative_url }}" width="1440" height="765" alt="3 つのデフォルトルールがある Redis ACLs タブ" loading="lazy" decoding="async"></p>

デフォルトの ACL ルールは 3 つ：Full-Access +@all ~*、Read-Write +@all -@dangerous ~*、Read-Only +@read ~*。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/26-billing-history.webp' | relative_url }}" width="1440" height="765" alt="Billing History：請求履歴なし" loading="lazy" decoding="async"></p>

Billing には Billing History、Payment Methods、Credits のタブと、Cost report ボタンがあります。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/27-payment-methods.webp' | relative_url }}" width="1440" height="765" alt="Payment Methods：カードなし、Add credit card ボタン" loading="lazy" decoding="async"></p>

登録済みのカードなし。無料プランではカードを求められません。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/28-credits.webp' | relative_url }}" width="1440" height="765" alt="クーポンコード欄があり、使用額と残高がどちらも $0 の Credits タブ" loading="lazy" decoding="async"></p>

Credits：クーポンコードとその残高。Pro の「First $200 free」は、Pro サブスクリプションができるまでここには表示されません。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/29-integrations.webp' | relative_url }}" width="1440" height="765" alt="Integrations 画面：Datadog、Confluent、Grafana、Prometheus" loading="lazy" decoding="async"></p>

Integrations：メトリクス用の Datadog と Grafana/Prometheus、Kafka のデータを Redis に取り込む Confluent。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/30-settings.webp' | relative_url }}" width="1440" height="1248" alt="アカウント設定：アカウント情報、連絡先、MFA 強制はオフ、認証局のダウンロード、タイムゾーン UTC" loading="lazy" decoding="async"></p>

Settings：アカウント情報、ビジネス連絡先、MFA enforcement（デフォルトはオフ）、TLS クライアント用の Redis Cloud CA バンドル、タイムゾーン。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/31-account-menu.webp' | relative_url }}" width="1440" height="765" alt="アカウントメニューを開いた状態：アカウント切り替え、ユーザープロフィール、ログアウト" loading="lazy" decoding="async"></p>

アカウントメニューでは、アカウントを切り替えたり、ユーザープロフィールを開いたりできます。 <small>2026-11-07 キャプチャ、Redis Cloud 無料プラン。</small>

### ラボ：無料データベースとその制限

**Redis 8.6.2（Redis Cloud 無料プラン、AWS ap-northeast-2）で検証、2026-11-07。** クライアント：韓国のホストから redis-py 6.1.1、往復約 2.6 ms、平文 TCP（無料プランには TLS がありません）。ソースと全出力：[`cloud/01-free-database`](https://github.com/litkhai/notes-on-redis/tree/main/cloud/01-free-database)。

| 公称の制限 | クライアントで確認した結果 |
|---|---|
| 30 接続 | 31 本目の接続は拒否された：`max number of clients reached` |
| 30 MB | 10 kB の値の書き込みが約 28 MB で拒否された：`OOM command not allowed when used memory > 'maxmemory'`。キーの追い出しはなし（volatile-lru で、TTL を持つキーがなかったため） |
| 100 ops/s | この実行では適用されなかった：8 接続、100 件の pipeline で 60 秒間、約 104,000 INCR/s、エラーなし。コンソールは 61,806 / 100 と警告を表示した |

pipeline を使わない 1 接続では 249 ops/s で、これは往復時間によるもので、プランによるものではありません。ops/s の値は、コンソールが比較表示する目安のサイズ指標であって、スロットルではないようです。予告なく変わる可能性があるため、超過を前提に作らないでください。

### 最初の 1 週間のチェックリスト

- **CIDR allow list** を設定する：無料データベースは 0.0.0.0/0 で始まります。無料プランでは **TLS** をオンにできない（API は `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN` で拒否します）ため、テストデータだけを置くか、有料プランに移ってそこで TLS をオンにします。
- デフォルトユーザーを **Data Access** のユーザーとロールに置き換えるか、少なくともそのパスワードをローテーションする。
- **eviction policy** を決める：TTL を持つキーがないと、volatile-lru は書き込みを拒否します。
- **alerts** は 80% 以下に保つ：無料プランには、頼れるレプリケーション、永続化、バックアップがありません。
- 参加者が増えたら、Settings で **MFA enforcement** をオンにする。
- **API** を有効にした場合、使わなくなったユーザーキーは削除する：システムログには、呼び出しごとにそのキー名が記録されます。

### まだ扱っていないもの

ソウルの Essentials でのレプリケーション、永続化、バックアップ、RBAC、REST API のラボ、Pro Active-Active は、それぞれ別のラボで、リポジトリに個別の issue があります。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

**Redis Cloud ตั้งแต่สมัครใช้งานจนถึงทุกเมนูของคอนโซล** บันทึกเมื่อ 2026-11-07 บนแผนฟรี: ฐานข้อมูลฟรี 1 ฐาน (Redis 8.6, AWS ap-northeast-2 Seoul) คอนโซลในโหมดมืด ไม่มีการชำระเงินใดๆ ฟอร์มของ Essentials และ Pro ถูกเปิดและบันทึกภาพไว้แต่ไม่ได้ส่งข้อมูล ข้อมูลที่ปิดบังในภาพหน้าจอทุกภาพ: ชื่อ อีเมล หมายเลขบัญชี ID ของ subscription และฐานข้อมูล endpoint พอร์ต ที่อยู่ IP และ API keys ราคาในหน้านี้อ่านจากคอนโซลเมื่อ 2026-11-07

### ภาพรวม

แถบด้านซ้าย จากบนลงล่าง: **Databases**, **Subscriptions**, **Redis Search**, **Data Integration** ใต้ *AI services* คือ **Iris** ซึ่งมี Agent Playbooks, Agent Memory, Context Gateway, Intent Router, Lens (beta), Agent Mesh (beta) และ Access & Identity ใต้ *Reports* คือ **Logs** และ **Usage** ใต้ *Account* คือ **API Keys & Team**, **Data Access**, **Billing**, **Integrations**, **Settings** แถบด้านบนมีตัวสลับแอป ไอคอนเคล็ดลับ ตัวสลับธีม (สว่าง มืด ตามระบบ) และเมนูบัญชี

<p class="shot"><img src="{{ '/assets/img/cloud-console/01-databases-empty.webp' | relative_url }}" width="1440" height="765" alt="หน้า Databases ว่างที่มีปุ่ม New database" loading="lazy" decoding="async"></p>

บัญชีใหม่เปิดมาที่ Databases ซึ่งยังไม่มีอะไรอยู่ <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### สร้างฐานข้อมูล

**New database** เปิดหน้าเดียวที่มีการ์ดแผนสองใบ **Essentials** เป็นโครงสร้างพื้นฐานแบบใช้ร่วมกัน เริ่มที่ $0.007/ชั่วโมง ($5/เดือน) **Pro** เป็นโครงสร้างพื้นฐานเฉพาะ เริ่มที่ $0.014/ชั่วโมง โดยมีขั้นต่ำ $200/เดือน และป้าย "First $200 free" ใต้การ์ดมีบรรทัด *Not ready? Try 30 MB for free* ลิงก์นี้เป็นทางเดียวที่นำไปสู่แผนฟรี

<p class="shot"><img src="{{ '/assets/img/cloud-console/02-create-essentials-form.webp' | relative_url }}" width="1440" height="2118" alt="ฟอร์มสร้าง Essentials: cloud vendor และ region, ชื่อ, เวอร์ชัน 8.6, แถบเลื่อนขนาด, ตัวเลือก high availability และ persistence, วิธีชำระเงิน" loading="lazy" decoding="async"></p>

ค่าเริ่มต้นของ Essentials: AWS us-east-1, Redis 8.6, รวม 250 MB (dataset 125 MB บวก replica 125 MB), 1,000 ops/s, single-zone replication และ AOF ทุกวินาที, $8/เดือน ขนาดมีตั้งแต่ 250 MB ถึง 100 GB, RAM+SSD (Flex) เป็นตัวสลับ ต้องมีวิธีชำระเงินก่อนกด Confirm & pay <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/03-create-pro-form.webp' | relative_url }}" width="1440" height="2338" alt="ฟอร์มสร้าง Pro: Easy create หรือ Custom settings, ไทล์ cloud vendor, region, ตัวปรับขนาด dataset และ throughput, persistence, high availability, สรุปราคา" loading="lazy" decoding="async"></p>

Pro เริ่มต้นด้วยการเลือกวิธีตั้งค่า คือ Easy create หรือ Custom settings ค่าเริ่มต้นของ Easy create: dataset 3 GB (หน่วยความจำรวม 6 GB เมื่อรวม replica), 3,000 ops/s, AOF ทุกวินาที, เปิด high availability, $0.274/ชั่วโมง (ประมาณ $200/เดือน) <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/04-create-free-form.webp' | relative_url }}" width="1440" height="1259" alt="ฟอร์มสร้างแผนฟรีที่มี region Asia Pacific (Seoul), ชื่อ notes-on-redis-free และขีดจำกัดที่รวมอยู่" loading="lazy" decoding="async"></p>

ฟอร์มแผนฟรีแสดงสิ่งที่รวมอยู่: 1 ฐานข้อมูล, RAM 30 MB, 30 การเชื่อมต่อ, 100 ops/sec, $0/เดือน เลือก region ได้อิสระ (AWS, Google Cloud หรือ Azure; เลือก Seoul) ภาพนี้เป็นภาพเดียวที่บันทึกในโหมดสว่าง และไม่สามารถเปิดฟอร์มนี้ซ้ำได้เมื่อบัญชีมีฐานข้อมูลฟรีแล้ว <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### หน้าฐานข้อมูล

หลังกด Create database ระบบจะเข้าสู่หน้าฐานข้อมูลภายในไม่กี่วินาที หน้านี้มีสี่แท็บ: Configuration, Metrics, Alerts, Slowlog เมื่อเข้าครั้งแรกจะมีกล่องโต้ตอบเสนอการตั้งค่าแบบนำทาง การปิดกล่องนี้ไม่ได้ใช้การเปลี่ยนแปลงใดๆ

<p class="shot"><img src="{{ '/assets/img/cloud-console/05-database-setup-dialog.webp' | relative_url }}" width="1440" height="765" alt="กล่องโต้ตอบ Set up your database เหนือหน้าฐานข้อมูลใหม่" loading="lazy" decoding="async"></p>

"No changes are applied until you confirm." กล่องโต้ตอบถูกปิดโดยไม่ได้ตรวจสอบ <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/06-database-configuration.webp' | relative_url }}" width="1440" height="1977" alt="แท็บ Configuration ของฐานข้อมูลฟรี: การ์ดการใช้งาน, แถบเลื่อนแผน, แผงความพร้อมใช้งานและการสำรองข้อมูล, การเข้าถึง, ข้อมูล, ความปลอดภัย และข้อมูลฐานข้อมูล" loading="lazy" decoding="async"></p>

ค่าเริ่มต้นของฐานข้อมูลฟรีตามที่แสดง: ไม่มี replication, ไม่มี persistence, ปิด remote backup, eviction policy เป็น volatile-lru, เปิด default user, ปิด CIDR allow list, ปิด TLS (แผนฟรีเปิดไม่ได้), RESP3, Redis 8.6 หน้า Logs บันทึก allow list เป็น 0.0.0.0/0 <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/07-connect-dialog.webp' | relative_url }}" width="1440" height="765" alt="ลิ้นชัก Connect ที่มีส่วนไคลเอนต์ Redis CLI, Redis Insight และ Redis SDK" loading="lazy" decoding="async"></p>

Connect ให้คำสั่ง redis-cli ที่พร้อมใช้ผ่าน endpoint สาธารณะ รหัสผ่านจะถูกซ่อนจนกว่าจะกดไอคอนรูปดวงตา endpoint เป็นชื่อโฮสต์ที่สร้างขึ้นภายใต้ db.redis.io <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/08-database-metrics.webp' | relative_url }}" width="1440" height="1587" alt="แท็บ Metrics ระหว่างการทดสอบโหลด: ops ต่อวินาทีเพิ่มขึ้นถึง 82 พัน, กราฟ latency, การเชื่อมต่อ, key, หน่วยความจำ และเครือข่าย" loading="lazy" decoding="async"></p>

ช่วงเวลาตั้งแต่ 5 นาทีถึง 3 เดือน กราฟ: ops/sec, latency (แยกเป็น reads, writes, other ด้วย), การเชื่อมต่อ, อ็อบเจกต์ที่ถูก evict และหมดอายุ/วินาที, จำนวน key ทั้งหมด, reads/sec, writes/sec, other commands/sec, read hit ratio, หน่วยความจำที่ใช้, network egress และ ingress บันทึกระหว่างการทดสอบ throughput ด้านล่าง <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/09-database-throughput-over-limit.webp' | relative_url }}" width="1440" height="765" alt="การ์ด Throughput แสดง 61,806 จาก 100 ops ต่อวินาที พร้อมไอคอนเตือน" loading="lazy" decoding="async"></p>

การ์ด throughput ระหว่างการทดสอบ: 61,806 / 100 ops/sec คอนโซลแจ้งว่าเกินขีดจำกัด แต่ฐานข้อมูลยังคงให้บริการต่อ (ดูผลการวัดด้านล่าง) <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/10-database-alerts.webp' | relative_url }}" width="1440" height="765" alt="แท็บ Alerts ที่มี alert ขนาด dataset และจำนวนการเชื่อมต่อ ทั้งคู่ที่ 80 เปอร์เซ็นต์ของขีดจำกัดแผน" loading="lazy" decoding="async"></p>

alert ของแผนฟรี: ขนาด dataset และจำนวนการเชื่อมต่อ แต่ละรายการเป็นเปอร์เซ็นต์ของขีดจำกัดแผน ตั้งไว้ล่วงหน้าที่ 80% <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/11-database-slowlog.webp' | relative_url }}" width="1440" height="765" alt="แท็บ Slowlog ที่ไม่มีรายการและมีปุ่ม Clear slowlog" loading="lazy" decoding="async"></p>

Slowlog ยังคงว่าง: การทดสอบใช้เพียง INCR และ SET <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### ฐานข้อมูลและ subscription

ทุกฐานข้อมูลเป็นของ subscription หนึ่ง แผนฟรีสร้าง subscription หนึ่งรายการที่มีฐานข้อมูลหนึ่งฐาน

<p class="shot"><img src="{{ '/assets/img/cloud-console/12-databases-list.webp' | relative_url }}" width="1440" height="765" alt="รายการ Databases ที่มีหนึ่งแถว: notes-on-redis-free, การใช้หน่วยความจำ 7.4 เปอร์เซ็นต์ของ 30 MB, เวอร์ชัน 8.6" loading="lazy" decoding="async"></p>

คอลัมน์: status, ชื่อฐานข้อมูล, subscription, endpoint (ปุ่ม Connect), การใช้หน่วยความจำ, capabilities, tags, เวอร์ชัน, actions ตัวกรองมี status, subscription, plan, capabilities, เวอร์ชัน, region และ cloud <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/13-subscriptions.webp' | relative_url }}" width="1440" height="765" alt="หน้า Subscriptions ที่มีการ์ด subscription ฟรีและรายการฐานข้อมูล" loading="lazy" decoding="async"></p>

subscription ฟรีใน ap-northeast-2 พร้อมปุ่ม Plan upgrade และแท็บ Databases และ Overview <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### เมนูผลิตภัณฑ์

รายการในแถบด้านข้างสามรายการเป็นจุดเริ่มต้นของผลิตภัณฑ์ ไม่ใช่หน้าการตั้งค่า

<p class="shot"><img src="{{ '/assets/img/cloud-console/14-redis-search.webp' | relative_url }}" width="1440" height="818" alt="หน้า Redis Search ที่นำเสนอ vector search สำหรับ agent พร้อมตัวเลือกฐานข้อมูล" loading="lazy" decoding="async"></p>

Redis Search เป็นจุดเริ่มต้นแบบนำทางสำหรับสร้าง vector index แรกบนฐานข้อมูลที่มีอยู่ <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/15-data-integration.webp' | relative_url }}" width="1440" height="1489" alt="หน้า Data Integration: ซิงค์เข้า Redis แบบใกล้เรียลไทม์, $1.37 ต่อชั่วโมง, สามขั้นตอน" loading="lazy" decoding="async"></p>

Data Integration คือ RDI แบบมีผู้ดูแลให้: $1.37/ชั่วโมง ประมาณ $1,000/เดือน คิดค่าบริการตั้งแต่สร้าง pipeline ขั้นตอน: เชื่อมต่อฐานข้อมูลต้นทาง, แปลงข้อมูล, ให้บริการการอ่านจาก Redis ไม่ได้สร้างไว้ในที่นี้ <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/16-iris.webp' | relative_url }}" width="1440" height="1276" alt="หน้า landing ของ Iris AI Services ที่มีวิดีโอสาธิตและรายการบริการ" loading="lazy" decoding="async"></p>

หน้า landing ของ Iris บริการที่แสดง: Agent Memory, Agent Playbooks, Intent Router, Context Gateway, Agent Mesh; Lens ปรากฏในแถบด้านข้าง หน้า Iris ของเว็บไซต์นี้อธิบายแต่ละบริการ <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### รายงาน

<p class="shot"><img src="{{ '/assets/img/cloud-console/17-logs-system.webp' | relative_url }}" width="1440" height="765" alt="System log: สร้าง subscription, เปิดใช้งานฐานข้อมูล, ปิด persistence, เพิ่ม source IP, เปิด RESP3, เปิด API, กำหนด API key" loading="lazy" decoding="async"></p>

System log แสดงทุกเหตุการณ์การตั้งค่าพร้อมเวลา ผู้ดำเนินการ และชื่อ API key ปุ่ม Export all ใช้ดาวน์โหลด <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/18-logs-sessions.webp' | relative_url }}" width="1440" height="765" alt="Sessions log ที่มีการเข้าสู่ระบบสำเร็จสองครั้ง" loading="lazy" decoding="async"></p>

Sessions: การเข้าสู่ระบบคอนโซลแต่ละครั้งพร้อม user agent, IP, บทบาท และประเภทการเข้าสู่ระบบ <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/19-usage.webp' | relative_url }}" width="1440" height="765" alt="รายงาน Usage แท็บ Memory Usage, กราฟรายวันของเดือนพฤศจิกายน 2026" loading="lazy" decoding="async"></p>

Usage มีแท็บ Memory Usage และ RBU Usage และการดาวน์โหลด Cost report ทันทีหลังสร้างฐานข้อมูล ระบบแจ้งว่ารายงานจะปรากฏในอีกหนึ่งชั่วโมง เมื่อถึงการบันทึกภาพครั้งสุดท้ายก็มีข้อมูลแสดงแล้ว <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### บัญชี

<p class="shot"><img src="{{ '/assets/img/cloud-console/20-api-keys.webp' | relative_url }}" width="1440" height="765" alt="แท็บ API Keys ที่ซ่อน account key และมี user key หนึ่งรายการ" loading="lazy" decoding="async"></p>

Enable API ใช้งานได้บนแผนฟรี การเรียกใช้ต้องมี account key และ user key; สร้าง user key หนึ่งรายการ และ GET /v1/fixed/subscriptions ตอบกลับ 200 subscription แบบ Free และ Essentials อยู่ภายใต้ /v1/fixed ส่วน Pro อยู่ภายใต้ /v1/subscriptions <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/21-team.webp' | relative_url }}" width="1440" height="765" alt="แท็บ Team ที่มีเจ้าของหนึ่งคนซึ่งสมัครผ่าน Google" loading="lazy" decoding="async"></p>

Team: ผู้ใช้คอนโซล บทบาท และประเภทการสมัคร <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/22-single-sign-on.webp' | relative_url }}" width="1440" height="765" alt="แท็บ Single Sign-On: ยังไม่เปิดใช้ SSO, ปุ่ม Set up SAML SSO" loading="lazy" decoding="async"></p>

สามารถตั้งค่า SAML SSO ใหม่ หรือเข้าร่วมจากการตั้งค่าที่มีอยู่ได้ แท็บนี้มีอยู่บนแผนฟรี <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/23-data-access-users.webp' | relative_url }}" width="1440" height="765" alt="Data Access Control แท็บ Users ยังไม่มีผู้ใช้ที่กำหนดไว้" loading="lazy" decoding="async"></p>

Data Access คือ RBAC ระดับฐานข้อมูล: ผู้ใช้ บทบาท และ Redis ACLs ต้องมีบทบาทก่อนจึงจะเพิ่มผู้ใช้ได้ <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/24-data-access-roles.webp' | relative_url }}" width="1440" height="765" alt="แท็บ Roles ยังไม่มีบทบาทที่กำหนดไว้" loading="lazy" decoding="async"></p>

Roles ผูกกฎ ACL เข้ากับฐานข้อมูล <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/25-redis-acls.webp' | relative_url }}" width="1440" height="765" alt="แท็บ Redis ACLs ที่มีกฎเริ่มต้นสามข้อ" loading="lazy" decoding="async"></p>

กฎ ACL เริ่มต้นสามข้อ: Full-Access +@all ~*, Read-Write +@all -@dangerous ~*, Read-Only +@read ~* <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/26-billing-history.webp' | relative_url }}" width="1440" height="765" alt="Billing history: ไม่มีประวัติการเรียกเก็บเงิน" loading="lazy" decoding="async"></p>

Billing มี Billing History, Payment Methods และ Credits พร้อมปุ่ม Cost report <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/27-payment-methods.webp' | relative_url }}" width="1440" height="765" alt="Payment methods: ไม่มีบัตร, ปุ่ม Add credit card" loading="lazy" decoding="async"></p>

ไม่มีบัตรในระบบ: แผนฟรีไม่ขอบัตร <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/28-credits.webp' | relative_url }}" width="1440" height="765" alt="แท็บ Credits ที่มีช่องรหัสคูปอง ยอดที่ใช้แล้วและยอดคงเหลือเป็น $0 ทั้งคู่" loading="lazy" decoding="async"></p>

Credits: รหัสคูปองและยอดคงเหลือ ข้อเสนอ "First $200 free" ของ Pro ไม่แสดงที่นี่ก่อนที่จะมี subscription แบบ Pro <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/29-integrations.webp' | relative_url }}" width="1440" height="765" alt="หน้า Integrations: Datadog, Confluent, Grafana และ Prometheus" loading="lazy" decoding="async"></p>

Integrations: Datadog และ Grafana/Prometheus สำหรับ metrics, Confluent สำหรับส่งข้อมูล Kafka เข้า Redis <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/30-settings.webp' | relative_url }}" width="1440" height="1248" alt="Account settings: ข้อมูลบัญชี, ผู้ติดต่อ, ปิด MFA enforcement, ดาวน์โหลด certificate authority, เขตเวลา UTC" loading="lazy" decoding="async"></p>

Settings: ข้อมูลบัญชี ผู้ติดต่อทางธุรกิจ MFA enforcement (ปิดเป็นค่าเริ่มต้น) ชุด CA ของ Redis Cloud สำหรับไคลเอนต์ TLS และเขตเวลา <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/31-account-menu.webp' | relative_url }}" width="1440" height="765" alt="เมนูบัญชีที่เปิดอยู่: ตัวสลับบัญชี, โปรไฟล์ผู้ใช้, logout" loading="lazy" decoding="async"></p>

เมนูบัญชีใช้สลับระหว่างบัญชีและเปิดโปรไฟล์ผู้ใช้ <small>บันทึกเมื่อ 2026-11-07 บนแผนฟรีของ Redis Cloud</small>

### Lab: ฐานข้อมูลฟรีและขีดจำกัด

**ตรวจสอบบน Redis 8.6.2 (แผนฟรีของ Redis Cloud, AWS ap-northeast-2) เมื่อ 2026-11-07** ไคลเอนต์: redis-py 6.1.1 จากโฮสต์ในเกาหลี ใช้เวลาไป-กลับประมาณ 2.6 ms, TCP ธรรมดา (แผนฟรีไม่มี TLS) ซอร์สและผลลัพธ์ฉบับเต็ม: [`cloud/01-free-database`](https://github.com/litkhai/notes-on-redis/tree/main/cloud/01-free-database)

| Advertised limit | What the client saw |
|---|---|
| 30 connections | การเชื่อมต่อที่ 31 ถูกปฏิเสธ: `max number of clients reached` |
| 30 MB | การเขียนถูกปฏิเสธที่ประมาณ 28 MB ของค่าขนาด 10 kB: `OOM command not allowed when used memory > 'maxmemory'` ไม่มี key ถูกลบ (volatile-lru, ไม่มี key ใดมี TTL) |
| 100 ops/s | ไม่ได้บังคับใช้ในการทดสอบนี้: ประมาณ 104,000 INCR/s เป็นเวลา 60 วินาที บน 8 การเชื่อมต่อ ด้วย pipeline ละ 100 คำสั่ง ไม่มีข้อผิดพลาด คอนโซลแสดง 61,806 / 100 และคำเตือน |

การเชื่อมต่อเดียวที่ไม่ใช้ pipeline ได้ 249 ops/s ซึ่งเป็นผลจากเวลาไป-กลับ ไม่ใช่จากแผน ตัวเลข ops/s ดูเป็นแนวทางกำหนดขนาดที่คอนโซลใช้รายงานเทียบ ไม่ใช่ตัวจำกัดอัตรา ซึ่งอาจเปลี่ยนโดยไม่แจ้งล่วงหน้า จึงไม่ควรสร้างระบบโดยพึ่งการใช้เกินขีดจำกัด

### รายการตรวจสอบสัปดาห์แรก

- ตั้ง **CIDR allow list**: ฐานข้อมูลฟรีเริ่มต้นที่ 0.0.0.0/0 แผนฟรีเปิด **TLS** ไม่ได้ (API ปฏิเสธด้วย `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`) จึงควรเก็บเฉพาะข้อมูลทดสอบ หรือย้ายไปใช้แผนแบบชำระเงินแล้วเปิด TLS ที่นั่น
- แทนที่ default user ด้วยผู้ใช้และบทบาทของ **Data Access** หรืออย่างน้อยก็เปลี่ยนรหัสผ่านของมัน
- กำหนด **eviction policy**: volatile-lru จะปฏิเสธการเขียนเมื่อไม่มี key ใดมี TTL
- ตั้ง **alerts** ไว้ที่ 80% หรือต่ำกว่า: แผนฟรีไม่มีการทำ replication, persistence หรือ backup ไว้รองรับ
- เปิด **MFA enforcement** ใน Settings เมื่อมีคนเข้าร่วมมากขึ้น
- หากเปิดใช้ **API** ให้ลบ user key ที่ไม่ใช้แล้ว: system log ระบุชื่อ key ในทุกการเรียกที่ key นั้นทำ

### ที่ยังไม่ครอบคลุม

Essentials ใน Seoul พร้อม replication, persistence, backup และ RBAC, lab ของ REST API และ Pro Active-Active เป็น lab แยกต่างหาก โดยมี issue ของตัวเองใน repository

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

**Redis Cloud, dari pendaftaran hingga setiap menu konsol.** Diambil pada 2026-11-07 di paket gratis: satu database gratis (Redis 8.6, AWS ap-northeast-2 Seoul), konsol dalam mode gelap, tanpa biaya. Formulir Essentials dan Pro dibuka dan diambil tangkapan layarnya, tetapi tidak dikirim. Disamarkan di setiap tangkapan layar: nama, e-mail, nomor akun, ID subscription dan database, endpoint, port, alamat IP, API key. Harga di halaman ini dibaca dari konsol pada 2026-11-07.

### Sekilas

Sidebar kiri, dari atas ke bawah: **Databases**, **Subscriptions**, **Redis Search**, **Data Integration**; di bawah *AI services* terdapat **Iris** dengan Agent Playbooks, Agent Memory, Context Gateway, Intent Router, Lens (beta), Agent Mesh (beta), dan Access & Identity; di bawah *Reports* terdapat **Logs** dan **Usage**; di bawah *Account* terdapat **API Keys & Team**, **Data Access**, **Billing**, **Integrations**, **Settings**. Bilah atas berisi pengalih aplikasi, ikon tips, pengalih tema (terang, gelap, sistem), dan menu akun.

<p class="shot"><img src="{{ '/assets/img/cloud-console/01-databases-empty.webp' | relative_url }}" width="1440" height="765" alt="Halaman Databases kosong dengan tombol New database" loading="lazy" decoding="async"></p>

Akun baru terbuka di Databases tanpa isi apa pun. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

### Membuat database

**New database** membuka satu halaman dengan dua kartu paket. **Essentials** adalah infrastruktur bersama, mulai dari $0.007/jam ($5/bulan). **Pro** adalah infrastruktur khusus, mulai dari $0.014/jam dengan minimum $200/bulan dan lencana "First $200 free". Di bawah kartu ada baris *Not ready? Try 30 MB for free*; tautan itu satu-satunya jalan menuju paket gratis.

<p class="shot"><img src="{{ '/assets/img/cloud-console/02-create-essentials-form.webp' | relative_url }}" width="1440" height="2118" alt="Formulir pembuatan Essentials: cloud vendor dan region, nama, versi 8.6, slider ukuran, opsi high availability dan persistence, metode pembayaran" loading="lazy" decoding="async"></p>

Default Essentials: AWS us-east-1, Redis 8.6, total 250 MB (dataset 125 MB ditambah replica 125 MB), 1,000 ops/s, replikasi single-zone dan AOF setiap detik, $8/bulan. Ukuran berkisar dari 250 MB hingga 100 GB; RAM+SSD (Flex) berupa toggle. Metode pembayaran diperlukan sebelum Confirm & pay. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/03-create-pro-form.webp' | relative_url }}" width="1440" height="2338" alt="Formulir pembuatan Pro: Easy create atau Custom settings, ubin cloud vendor, region, stepper ukuran dataset dan throughput, persistence, high availability, ringkasan harga" loading="lazy" decoding="async"></p>

Pro dimulai dengan metode penyiapan, Easy create atau Custom settings. Default Easy create: dataset 3 GB (total memori 6 GB dengan replica), 3,000 ops/s, AOF setiap detik, high availability aktif, $0.274/jam (sekitar $200/bulan). <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/04-create-free-form.webp' | relative_url }}" width="1440" height="1259" alt="Formulir pembuatan paket gratis dengan region Asia Pacific (Seoul), nama notes-on-redis-free, dan batas yang disertakan" loading="lazy" decoding="async"></p>

Formulir gratis mencantumkan apa yang disertakan: 1 database, RAM 30 MB, 30 koneksi, 100 ops/sec, $0/bulan. Pilihan region bebas (AWS, Google Cloud, atau Azure; Seoul yang dipilih). Hanya tangkapan ini yang berada dalam mode terang; formulir tidak dapat dibuka kembali setelah akun memiliki database gratisnya. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

### Layar database

Create database membawa Anda ke halaman database setelah beberapa detik. Halaman ini memiliki empat tab: Configuration, Metrics, Alerts, Slowlog. Dialog kunjungan pertama menawarkan penyiapan terpandu; menutupnya tidak menerapkan apa pun.

<p class="shot"><img src="{{ '/assets/img/cloud-console/05-database-setup-dialog.webp' | relative_url }}" width="1440" height="765" alt="Dialog Set up your database di atas halaman database baru" loading="lazy" decoding="async"></p>

"No changes are applied until you confirm." Dialog ditutup tanpa ditinjau. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/06-database-configuration.webp' | relative_url }}" width="1440" height="1977" alt="Tab Configuration dari database gratis: kartu penggunaan, slider paket, panel ketersediaan dan backup, akses, data, keamanan, dan info database" loading="lazy" decoding="async"></p>

Default database gratis seperti yang ditampilkan: tanpa replikasi, tanpa persistence, remote backup nonaktif, eviction policy volatile-lru, default user aktif, CIDR allow list nonaktif, TLS nonaktif (paket gratis tidak dapat mengaktifkannya), RESP3, Redis 8.6. Halaman Logs mencatat allow list sebagai 0.0.0.0/0. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/07-connect-dialog.webp' | relative_url }}" width="1440" height="765" alt="Drawer Connect dengan bagian klien Redis CLI, Redis Insight, dan Redis SDK" loading="lazy" decoding="async"></p>

Connect memberikan perintah redis-cli yang siap pakai melalui endpoint publik; kata sandi tetap tersembunyi sampai ikon mata ditekan. Endpoint adalah nama host yang dibuat otomatis di bawah db.redis.io. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/08-database-metrics.webp' | relative_url }}" width="1440" height="1587" alt="Tab Metrics saat uji beban: ops per detik naik hingga 82 ribu, grafik latensi, koneksi, key, memori, dan jaringan" loading="lazy" decoding="async"></p>

Rentang dari 5 menit hingga 3 bulan. Grafik: ops/sec, latensi (juga dipisah menjadi reads, writes, other), koneksi, objek yang di-evict dan kedaluwarsa/detik, total key, reads/sec, writes/sec, other commands/sec, read hit ratio, memori terpakai, network egress dan ingress. Diambil selama uji throughput di bawah. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/09-database-throughput-over-limit.webp' | relative_url }}" width="1440" height="765" alt="Kartu Throughput menampilkan 61,806 dari 100 ops per detik dengan ikon peringatan" loading="lazy" decoding="async"></p>

Kartu throughput selama pengujian: 61,806 / 100 ops/sec. Konsol menandai kelebihan tersebut; database tetap melayani (lihat pengukuran di bawah). <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/10-database-alerts.webp' | relative_url }}" width="1440" height="765" alt="Tab Alerts dengan alert ukuran dataset dan koneksi, keduanya pada 80 persen dari batas paket" loading="lazy" decoding="async"></p>

Alert paket gratis: ukuran dataset dan jumlah koneksi, masing-masing sebagai persentase dari batas paket, diatur awal pada 80%. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/11-database-slowlog.webp' | relative_url }}" width="1440" height="765" alt="Tab Slowlog tanpa entri dan tombol Clear slowlog" loading="lazy" decoding="async"></p>

Slowlog tetap kosong: pengujian hanya menggunakan INCR dan SET. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

### Database dan subscription

Setiap database termasuk dalam sebuah subscription. Paket gratis membuat satu subscription yang berisi satu database.

<p class="shot"><img src="{{ '/assets/img/cloud-console/12-databases-list.webp' | relative_url }}" width="1440" height="765" alt="Daftar Databases dengan satu baris: notes-on-redis-free, penggunaan memori 7.4 persen dari 30 MB, versi 8.6" loading="lazy" decoding="async"></p>

Kolom: status, nama database, subscription, endpoint (tombol Connect), penggunaan memori, capabilities, tags, versi, actions. Filter untuk status, subscription, plan, capabilities, versi, region, dan cloud. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/13-subscriptions.webp' | relative_url }}" width="1440" height="765" alt="Halaman Subscriptions dengan kartu subscription gratis dan daftar database-nya" loading="lazy" decoding="async"></p>

Subscription gratis di ap-northeast-2, dengan tombol Plan upgrade serta tab Databases dan Overview. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

### Menu produk

Tiga entri sidebar merupakan titik masuk ke produk, bukan pengaturan.

<p class="shot"><img src="{{ '/assets/img/cloud-console/14-redis-search.webp' | relative_url }}" width="1440" height="818" alt="Halaman Redis Search yang memperkenalkan vector search untuk agent, dengan pemilih database" loading="lazy" decoding="async"></p>

Redis Search adalah awal terpandu untuk membuat vector index pertama pada database yang sudah ada. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/15-data-integration.webp' | relative_url }}" width="1440" height="1489" alt="Halaman Data Integration: sinkronisasi hampir real-time ke Redis, $1.37 per jam, tiga langkah" loading="lazy" decoding="async"></p>

Data Integration adalah RDI terkelola: $1.37/jam, perkiraan sekitar $1,000/bulan, ditagih sejak pipeline dibuat. Langkah: hubungkan database sumber, transformasi, layani pembacaan dari Redis. Tidak dibuat di sini. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/16-iris.webp' | relative_url }}" width="1440" height="1276" alt="Halaman landing Iris AI Services dengan video demo dan daftar layanan" loading="lazy" decoding="async"></p>

Halaman landing Iris. Layanan yang tercantum: Agent Memory, Agent Playbooks, Intent Router, Context Gateway, Agent Mesh; Lens muncul di sidebar. Halaman Iris di situs ini menguraikan semuanya. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

### Laporan

<p class="shot"><img src="{{ '/assets/img/cloud-console/17-logs-system.webp' | relative_url }}" width="1440" height="765" alt="System log: subscription dibuat, database diaktifkan, persistence dinonaktifkan, source IP ditambahkan, RESP3 diaktifkan, API diaktifkan, API key ditetapkan" loading="lazy" decoding="async"></p>

System log mencantumkan setiap peristiwa konfigurasi beserta waktu, originator, dan nama API key; Export all mengunduhnya. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/18-logs-sessions.webp' | relative_url }}" width="1440" height="765" alt="Sessions log dengan dua login yang berhasil" loading="lazy" decoding="async"></p>

Sessions: setiap login konsol beserta user agent, IP, peran, dan jenis login. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/19-usage.webp' | relative_url }}" width="1440" height="765" alt="Laporan Usage, tab Memory Usage, grafik harian untuk November 2026" loading="lazy" decoding="async"></p>

Usage memiliki tab Memory Usage dan RBU Usage serta unduhan Cost report. Tepat setelah database dibuat, tertulis bahwa laporan akan muncul satu jam kemudian; pada tangkapan terakhir sudah menampilkan data. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

### Akun

<p class="shot"><img src="{{ '/assets/img/cloud-console/20-api-keys.webp' | relative_url }}" width="1440" height="765" alt="Tab API Keys dengan account key tersembunyi dan satu user key" loading="lazy" decoding="async"></p>

Enable API berfungsi di paket gratis. Panggilan membutuhkan account key dan user key; satu user key dibuat dan GET /v1/fixed/subscriptions mengembalikan 200. Subscription Free dan Essentials berada di bawah /v1/fixed, Pro di bawah /v1/subscriptions. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/21-team.webp' | relative_url }}" width="1440" height="765" alt="Tab Team dengan satu owner yang mendaftar melalui Google" loading="lazy" decoding="async"></p>

Team: pengguna konsol, peran, dan jenis pendaftaran mereka. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/22-single-sign-on.webp' | relative_url }}" width="1440" height="765" alt="Tab Single Sign-On: SSO tidak diaktifkan, tombol Set up SAML SSO" loading="lazy" decoding="async"></p>

SAML SSO dapat disiapkan atau digabungkan dari konfigurasi yang sudah ada; tab ini tersedia di paket gratis. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/23-data-access-users.webp' | relative_url }}" width="1440" height="765" alt="Data Access Control, tab Users, belum ada pengguna yang ditentukan" loading="lazy" decoding="async"></p>

Data Access adalah RBAC tingkat database: pengguna, peran, dan Redis ACLs. Sebuah peran harus ada sebelum pengguna dapat ditambahkan. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/24-data-access-roles.webp' | relative_url }}" width="1440" height="765" alt="Tab Roles, belum ada peran yang ditentukan" loading="lazy" decoding="async"></p>

Roles mengikat aturan ACL ke database. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/25-redis-acls.webp' | relative_url }}" width="1440" height="765" alt="Tab Redis ACLs dengan tiga aturan default" loading="lazy" decoding="async"></p>

Tiga aturan ACL default: Full-Access +@all ~*, Read-Write +@all -@dangerous ~*, Read-Only +@read ~*. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/26-billing-history.webp' | relative_url }}" width="1440" height="765" alt="Billing history: tidak ada riwayat penagihan" loading="lazy" decoding="async"></p>

Billing memiliki Billing History, Payment Methods, dan Credits, ditambah tombol Cost report. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/27-payment-methods.webp' | relative_url }}" width="1440" height="765" alt="Payment methods: tidak ada kartu, tombol Add credit card" loading="lazy" decoding="async"></p>

Tidak ada kartu tersimpan: paket gratis tidak memintanya. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/28-credits.webp' | relative_url }}" width="1440" height="765" alt="Tab Credits dengan kolom kode kupon, jumlah terpakai dan sisa keduanya $0" loading="lazy" decoding="async"></p>

Credits: kode kupon dan saldonya. Penawaran Pro "First $200 free" tidak muncul di sini sebelum ada subscription Pro. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/29-integrations.webp' | relative_url }}" width="1440" height="765" alt="Halaman Integrations: Datadog, Confluent, Grafana, dan Prometheus" loading="lazy" decoding="async"></p>

Integrations: Datadog dan Grafana/Prometheus untuk metrik, Confluent untuk data Kafka ke Redis. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/30-settings.webp' | relative_url }}" width="1440" height="1248" alt="Account settings: info akun, kontak, MFA enforcement nonaktif, unduhan certificate authority, zona waktu UTC" loading="lazy" decoding="async"></p>

Settings: info akun, kontak bisnis, MFA enforcement (nonaktif secara default), bundel CA Redis Cloud untuk klien TLS, zona waktu. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/31-account-menu.webp' | relative_url }}" width="1440" height="765" alt="Menu akun terbuka: pengalih akun, profil pengguna, logout" loading="lazy" decoding="async"></p>

Menu akun beralih antar akun dan membuka profil pengguna. <small>Diambil pada 2026-11-07, paket gratis Redis Cloud.</small>

### Lab: database gratis dan batasnya

**Diverifikasi pada Redis 8.6.2 (paket gratis Redis Cloud, AWS ap-northeast-2), 2026-11-07.** Klien: redis-py 6.1.1 dari host di Korea, round trip sekitar 2.6 ms, TCP biasa (paket gratis tidak memiliki TLS). Sumber dan keluaran lengkap: [`cloud/01-free-database`](https://github.com/litkhai/notes-on-redis/tree/main/cloud/01-free-database).

| Advertised limit | What the client saw |
|---|---|
| 30 connections | Koneksi ke-31 ditolak: `max number of clients reached` |
| 30 MB | Penulisan ditolak pada sekitar 28 MB nilai berukuran 10 kB: `OOM command not allowed when used memory > 'maxmemory'`; tidak ada key yang di-evict (volatile-lru, tidak ada key yang memiliki TTL) |
| 100 ops/s | Tidak diberlakukan pada percobaan ini: sekitar 104,000 INCR/s selama 60 detik pada 8 koneksi dengan pipeline 100, tanpa error; konsol menampilkan 61,806 / 100 dan sebuah peringatan |

Satu koneksi tanpa pipeline mencapai 249 ops/s, yang ditentukan oleh round trip, bukan oleh paket. Angka ops/s tampaknya merupakan panduan ukuran yang dilaporkan konsol, bukan pembatas laju; hal ini dapat berubah tanpa pemberitahuan, jadi jangan membangun sesuatu di atas kelebihan tersebut.

### Daftar periksa minggu pertama

- Atur **CIDR allow list**: database gratis dimulai dengan 0.0.0.0/0. **TLS** tidak dapat diaktifkan pada paket gratis (API menolaknya dengan `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`), jadi simpan hanya data uji, atau pindah ke paket berbayar dan aktifkan TLS di sana.
- Ganti default user dengan pengguna dan peran **Data Access**, atau setidaknya ganti kata sandinya.
- Tentukan **eviction policy**: volatile-lru menolak penulisan ketika tidak ada key yang memiliki TTL.
- Jaga **alerts** pada 80% atau lebih rendah; paket gratis tidak memiliki replikasi, persistence, atau backup sebagai cadangan.
- Aktifkan **MFA enforcement** di Settings setelah lebih banyak orang bergabung.
- Jika Anda mengaktifkan **API**, hapus user key yang tidak lagi digunakan; system log mencantumkan nama key pada setiap panggilan yang dibuatnya.

### Belum dibahas

Essentials di Seoul dengan replikasi, persistence, backup, dan RBAC, lab REST API, dan Pro Active-Active adalah lab terpisah dengan issue masing-masing di repositori.

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

**Redis Cloud, dari pendaftaran hingga setiap menu konsol.** Ditangkap pada 2026-11-07 di pelan percuma: satu pangkalan data percuma (Redis 8.6, AWS ap-northeast-2 Seoul), konsol dalam mod gelap, tiada bayaran. Borang Essentials dan Pro dibuka dan ditangkap tetapi tidak dihantar. Disamarkan dalam setiap tangkapan skrin: nama, e-mel, nombor akaun, ID subscription dan pangkalan data, endpoint, port, alamat IP, API key. Harga pada halaman ini dibaca dalam konsol pada 2026-11-07.

### Sekilas pandang

Bar sisi kiri, dari atas ke bawah: **Databases**, **Subscriptions**, **Redis Search**, **Data Integration**; di bawah *AI services* terdapat **Iris** dengan Agent Playbooks, Agent Memory, Context Gateway, Intent Router, Lens (beta), Agent Mesh (beta) dan Access & Identity; di bawah *Reports* terdapat **Logs** dan **Usage**; di bawah *Account* terdapat **API Keys & Team**, **Data Access**, **Billing**, **Integrations**, **Settings**. Bar atas mengandungi penukar aplikasi, ikon petua, penukar tema (cerah, gelap, sistem) dan menu akaun.

<p class="shot"><img src="{{ '/assets/img/cloud-console/01-databases-empty.webp' | relative_url }}" width="1440" height="765" alt="Halaman Databases kosong dengan butang New database" loading="lazy" decoding="async"></p>

Akaun baharu dibuka pada Databases tanpa sebarang kandungan. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

### Cipta pangkalan data

**New database** membuka satu halaman dengan dua kad pelan. **Essentials** ialah infrastruktur kongsi, bermula dari $0.007/jam ($5/bulan). **Pro** ialah infrastruktur khusus, bermula dari $0.014/jam dengan minimum $200/bulan dan lencana "First $200 free". Di bawah kad terdapat baris *Not ready? Try 30 MB for free*; pautan itu satu-satunya jalan ke pelan percuma.

<p class="shot"><img src="{{ '/assets/img/cloud-console/02-create-essentials-form.webp' | relative_url }}" width="1440" height="2118" alt="Borang penciptaan Essentials: cloud vendor dan region, nama, versi 8.6, peluncur saiz, pilihan high availability dan persistence, kaedah pembayaran" loading="lazy" decoding="async"></p>

Lalai Essentials: AWS us-east-1, Redis 8.6, jumlah 250 MB (dataset 125 MB ditambah replica 125 MB), 1,000 ops/s, replikasi single-zone dan AOF setiap saat, $8/bulan. Saiz dari 250 MB hingga 100 GB; RAM+SSD (Flex) ialah togol. Kaedah pembayaran diperlukan sebelum Confirm & pay. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/03-create-pro-form.webp' | relative_url }}" width="1440" height="2338" alt="Borang penciptaan Pro: Easy create atau Custom settings, jubin cloud vendor, region, stepper saiz dataset dan throughput, persistence, high availability, ringkasan harga" loading="lazy" decoding="async"></p>

Pro bermula dengan kaedah persediaan, Easy create atau Custom settings. Lalai Easy create: dataset 3 GB (jumlah memori 6 GB dengan replica), 3,000 ops/s, AOF setiap saat, high availability dihidupkan, $0.274/jam (kira-kira $200/bulan). <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/04-create-free-form.webp' | relative_url }}" width="1440" height="1259" alt="Borang penciptaan pelan percuma dengan region Asia Pacific (Seoul), nama notes-on-redis-free, dan had yang disertakan" loading="lazy" decoding="async"></p>

Borang percuma menyenaraikan apa yang disertakan: 1 pangkalan data, RAM 30 MB, 30 sambungan, 100 ops/sec, $0/bulan. Pilihan region adalah bebas (AWS, Google Cloud atau Azure; Seoul dipilih). Hanya tangkapan ini dalam mod cerah; borang tidak boleh dibuka semula sebaik sahaja akaun mempunyai pangkalan data percuma. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

### Skrin pangkalan data

Create database membawa anda ke halaman pangkalan data selepas beberapa saat. Halaman ini mempunyai empat tab: Configuration, Metrics, Alerts, Slowlog. Dialog lawatan pertama menawarkan persediaan berpandu; menutupnya tidak menggunakan sebarang perubahan.

<p class="shot"><img src="{{ '/assets/img/cloud-console/05-database-setup-dialog.webp' | relative_url }}" width="1440" height="765" alt="Dialog Set up your database di atas halaman pangkalan data baharu" loading="lazy" decoding="async"></p>

"No changes are applied until you confirm." Dialog ditutup tanpa disemak. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/06-database-configuration.webp' | relative_url }}" width="1440" height="1977" alt="Tab Configuration pangkalan data percuma: kad penggunaan, peluncur pelan, panel ketersediaan dan sandaran, akses, data, keselamatan dan maklumat pangkalan data" loading="lazy" decoding="async"></p>

Lalai pangkalan data percuma seperti yang dipaparkan: tiada replikasi, tiada persistence, remote backup dimatikan, eviction policy volatile-lru, default user dihidupkan, CIDR allow list dimatikan, TLS dimatikan (pelan percuma tidak boleh menghidupkannya), RESP3, Redis 8.6. Halaman Logs merekodkan allow list sebagai 0.0.0.0/0. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/07-connect-dialog.webp' | relative_url }}" width="1440" height="765" alt="Laci Connect dengan bahagian klien Redis CLI, Redis Insight dan Redis SDK" loading="lazy" decoding="async"></p>

Connect memberikan arahan redis-cli yang sedia digunakan melalui endpoint awam; kata laluan kekal tersembunyi sehingga ikon mata ditekan. Endpoint ialah nama hos yang dijana di bawah db.redis.io. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/08-database-metrics.webp' | relative_url }}" width="1440" height="1587" alt="Tab Metrics semasa ujian beban: ops sesaat meningkat kepada 82 ribu, graf kependaman, sambungan, key, memori dan rangkaian" loading="lazy" decoding="async"></p>

Julat dari 5 minit hingga 3 bulan. Graf: ops/sec, kependaman (juga dipecahkan kepada reads, writes, other), sambungan, objek dikeluarkan dan tamat tempoh/saat, jumlah key, reads/sec, writes/sec, other commands/sec, read hit ratio, memori digunakan, network egress dan ingress. Ditangkap semasa ujian throughput di bawah. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/09-database-throughput-over-limit.webp' | relative_url }}" width="1440" height="765" alt="Kad Throughput menunjukkan 61,806 daripada 100 ops sesaat dengan ikon amaran" loading="lazy" decoding="async"></p>

Kad throughput semasa ujian: 61,806 / 100 ops/sec. Konsol menandakan lebihan itu; pangkalan data terus berfungsi (lihat ukuran di bawah). <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/10-database-alerts.webp' | relative_url }}" width="1440" height="765" alt="Tab Alerts dengan alert saiz dataset dan sambungan, kedua-duanya pada 80 peratus had pelan" loading="lazy" decoding="async"></p>

Alert pelan percuma: saiz dataset dan bilangan sambungan, masing-masing sebagai peratusan had pelan, ditetapkan awal pada 80%. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/11-database-slowlog.webp' | relative_url }}" width="1440" height="765" alt="Tab Slowlog tanpa entri dan butang Clear slowlog" loading="lazy" decoding="async"></p>

Slowlog kekal kosong: ujian hanya menggunakan INCR dan SET. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

### Pangkalan data dan subscription

Setiap pangkalan data tergolong dalam sebuah subscription. Pelan percuma mencipta satu subscription yang mengandungi satu pangkalan data.

<p class="shot"><img src="{{ '/assets/img/cloud-console/12-databases-list.webp' | relative_url }}" width="1440" height="765" alt="Senarai Databases dengan satu baris: notes-on-redis-free, penggunaan memori 7.4 peratus daripada 30 MB, versi 8.6" loading="lazy" decoding="async"></p>

Lajur: status, nama pangkalan data, subscription, endpoint (butang Connect), penggunaan memori, capabilities, tags, versi, actions. Penapis untuk status, subscription, plan, capabilities, versi, region dan cloud. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/13-subscriptions.webp' | relative_url }}" width="1440" height="765" alt="Halaman Subscriptions dengan kad subscription percuma dan senarai pangkalan datanya" loading="lazy" decoding="async"></p>

Subscription percuma di ap-northeast-2, dengan butang Plan upgrade serta tab Databases dan Overview. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

### Menu produk

Tiga entri bar sisi ialah pintu masuk ke produk, bukan tetapan.

<p class="shot"><img src="{{ '/assets/img/cloud-console/14-redis-search.webp' | relative_url }}" width="1440" height="818" alt="Halaman Redis Search yang memperkenalkan vector search untuk agent, dengan pemilih pangkalan data" loading="lazy" decoding="async"></p>

Redis Search ialah permulaan berpandu untuk mencipta vector index pertama pada pangkalan data sedia ada. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/15-data-integration.webp' | relative_url }}" width="1440" height="1489" alt="Halaman Data Integration: penyegerakan hampir masa nyata ke Redis, $1.37 sejam, tiga langkah" loading="lazy" decoding="async"></p>

Data Integration ialah RDI terurus: $1.37/jam, anggaran kira-kira $1,000/bulan, dibilkan sejak pipeline dicipta. Langkah: sambung pangkalan data sumber, ubah, layani bacaan daripada Redis. Tidak dicipta di sini. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/16-iris.webp' | relative_url }}" width="1440" height="1276" alt="Halaman landing Iris AI Services dengan video demo dan senarai perkhidmatan" loading="lazy" decoding="async"></p>

Halaman landing Iris. Perkhidmatan yang disenaraikan: Agent Memory, Agent Playbooks, Intent Router, Context Gateway, Agent Mesh; Lens muncul dalam bar sisi. Halaman Iris di tapak ini menerangkan kesemuanya. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

### Laporan

<p class="shot"><img src="{{ '/assets/img/cloud-console/17-logs-system.webp' | relative_url }}" width="1440" height="765" alt="System log: subscription dicipta, pangkalan data diaktifkan, persistence dimatikan, source IP ditambah, RESP3 didayakan, API didayakan, API key ditetapkan" loading="lazy" decoding="async"></p>

System log menyenaraikan setiap peristiwa konfigurasi dengan masa, originator dan nama API key; Export all memuat turunnya. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/18-logs-sessions.webp' | relative_url }}" width="1440" height="765" alt="Sessions log dengan dua log masuk yang berjaya" loading="lazy" decoding="async"></p>

Sessions: setiap log masuk konsol dengan user agent, IP, peranan dan jenis log masuk. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/19-usage.webp' | relative_url }}" width="1440" height="765" alt="Laporan Usage, tab Memory Usage, graf harian untuk November 2026" loading="lazy" decoding="async"></p>

Usage mempunyai tab Memory Usage dan RBU Usage serta muat turun Cost report. Sejurus selepas pangkalan data dicipta, ia menyatakan laporan akan muncul sejam kemudian; pada tangkapan akhir ia telah menunjukkan data. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

### Akaun

<p class="shot"><img src="{{ '/assets/img/cloud-console/20-api-keys.webp' | relative_url }}" width="1440" height="765" alt="Tab API Keys dengan account key tersembunyi dan satu user key" loading="lazy" decoding="async"></p>

Enable API berfungsi pada pelan percuma. Panggilan memerlukan account key dan user key; satu user key dicipta dan GET /v1/fixed/subscriptions memulangkan 200. Subscription Free dan Essentials berada di bawah /v1/fixed, Pro di bawah /v1/subscriptions. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/21-team.webp' | relative_url }}" width="1440" height="765" alt="Tab Team dengan seorang owner yang mendaftar melalui Google" loading="lazy" decoding="async"></p>

Team: pengguna konsol, peranan dan jenis pendaftaran mereka. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/22-single-sign-on.webp' | relative_url }}" width="1440" height="765" alt="Tab Single Sign-On: SSO tidak didayakan, butang Set up SAML SSO" loading="lazy" decoding="async"></p>

SAML SSO boleh disediakan atau disertai daripada konfigurasi sedia ada; tab ini terdapat pada pelan percuma. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/23-data-access-users.webp' | relative_url }}" width="1440" height="765" alt="Data Access Control, tab Users, tiada pengguna ditakrifkan" loading="lazy" decoding="async"></p>

Data Access ialah RBAC peringkat pangkalan data: pengguna, peranan dan Redis ACLs. Satu peranan mesti wujud sebelum pengguna boleh ditambah. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/24-data-access-roles.webp' | relative_url }}" width="1440" height="765" alt="Tab Roles, tiada peranan ditakrifkan" loading="lazy" decoding="async"></p>

Roles mengikat peraturan ACL kepada pangkalan data. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/25-redis-acls.webp' | relative_url }}" width="1440" height="765" alt="Tab Redis ACLs dengan tiga peraturan lalai" loading="lazy" decoding="async"></p>

Tiga peraturan ACL lalai: Full-Access +@all ~*, Read-Write +@all -@dangerous ~*, Read-Only +@read ~*. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/26-billing-history.webp' | relative_url }}" width="1440" height="765" alt="Billing history: tiada sejarah pengebilan" loading="lazy" decoding="async"></p>

Billing mempunyai Billing History, Payment Methods dan Credits, serta butang Cost report. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/27-payment-methods.webp' | relative_url }}" width="1440" height="765" alt="Payment methods: tiada kad, butang Add credit card" loading="lazy" decoding="async"></p>

Tiada kad dalam fail: pelan percuma tidak memintanya. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/28-credits.webp' | relative_url }}" width="1440" height="765" alt="Tab Credits dengan medan kod kupon, jumlah digunakan dan baki kedua-duanya $0" loading="lazy" decoding="async"></p>

Credits: kod kupon dan bakinya. Tawaran Pro "First $200 free" tidak dipaparkan di sini sebelum subscription Pro wujud. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/29-integrations.webp' | relative_url }}" width="1440" height="765" alt="Halaman Integrations: Datadog, Confluent, Grafana dan Prometheus" loading="lazy" decoding="async"></p>

Integrations: Datadog dan Grafana/Prometheus untuk metrik, Confluent untuk data Kafka ke dalam Redis. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/30-settings.webp' | relative_url }}" width="1440" height="1248" alt="Account settings: maklumat akaun, kenalan, MFA enforcement dimatikan, muat turun certificate authority, zon waktu UTC" loading="lazy" decoding="async"></p>

Settings: maklumat akaun, kenalan perniagaan, MFA enforcement (dimatikan secara lalai), bundle CA Redis Cloud untuk klien TLS, zon waktu. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

<p class="shot"><img src="{{ '/assets/img/cloud-console/31-account-menu.webp' | relative_url }}" width="1440" height="765" alt="Menu akaun dibuka: penukar akaun, profil pengguna, logout" loading="lazy" decoding="async"></p>

Menu akaun bertukar antara akaun dan membuka profil pengguna. <small>Ditangkap pada 2026-11-07, pelan percuma Redis Cloud.</small>

### Makmal: pangkalan data percuma dan hadnya

**Disahkan pada Redis 8.6.2 (pelan percuma Redis Cloud, AWS ap-northeast-2), 2026-11-07.** Klien: redis-py 6.1.1 dari hos di Korea, round trip kira-kira 2.6 ms, TCP biasa (pelan percuma tidak mempunyai TLS). Sumber dan output penuh: [`cloud/01-free-database`](https://github.com/litkhai/notes-on-redis/tree/main/cloud/01-free-database).

| Advertised limit | What the client saw |
|---|---|
| 30 connections | Sambungan ke-31 ditolak: `max number of clients reached` |
| 30 MB | Penulisan ditolak pada kira-kira 28 MB nilai 10 kB: `OOM command not allowed when used memory > 'maxmemory'`; tiada key dikeluarkan (volatile-lru, tiada key yang mempunyai TTL) |
| 100 ops/s | Tidak dikuatkuasakan dalam larian ini: kira-kira 104,000 INCR/s selama 60 saat pada 8 sambungan dengan pipeline 100, tiada ralat; konsol menunjukkan 61,806 / 100 dan satu amaran |

Satu sambungan tanpa pipeline mencapai 249 ops/s, iaitu round trip, bukan pelan. Angka ops/s kelihatan seperti panduan saiz yang dilaporkan oleh konsol, bukan pendikit; ini mungkin berubah tanpa notis, jadi jangan membina sesuatu berdasarkan lebihan itu.

### Senarai semak minggu pertama

- Tetapkan **CIDR allow list**: pangkalan data percuma bermula dengan 0.0.0.0/0. **TLS** tidak boleh dihidupkan pada pelan percuma (API menolaknya dengan `FIXED_DATABASE_ENABLE_TLS_NOT_SUPPORTED_IN_REQUESTED_PLAN`), jadi simpan data ujian sahaja, atau beralih ke pelan berbayar dan hidupkan TLS di sana.
- Gantikan default user dengan pengguna dan peranan **Data Access**, atau sekurang-kurangnya tukar kata laluannya.
- Tentukan **eviction policy**: volatile-lru menolak penulisan apabila tiada key yang mempunyai TTL.
- Kekalkan **alerts** pada 80% atau lebih rendah; pelan percuma tidak mempunyai replikasi, persistence atau sandaran sebagai pilihan terakhir.
- Hidupkan **MFA enforcement** dalam Settings apabila lebih ramai orang menyertai.
- Jika anda mendayakan **API**, padam user key yang tidak lagi digunakan; system log menamakan key pada setiap panggilan yang dibuatnya.

### Belum diliputi

Essentials di Seoul dengan replikasi, persistence, sandaran dan RBAC, makmal REST API, dan Pro Active-Active ialah makmal berasingan dengan isu masing-masing dalam repositori.

</div>
