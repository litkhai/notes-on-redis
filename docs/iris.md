---
layout: default
title: Iris
permalink: /iris/
---

# Redis Iris

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: design only (2026-11-07).** Nothing on this page has been run yet. The plan is in [`design/DESIGN.md`](https://github.com/litkhai/redis-hols/blob/main/design/DESIGN.md).
</div>

Redis Iris is, in Redis's words, "a production-ready context engine for AI agents" — a suite of services, not a database; Redis is the database underneath. Launched 2026-05-18; on 2026-11-04 it became six services: Intent Router, Agent Playbooks, Agent Memory and Context Gateway (GA), Lens and Agent Mesh (beta). Managed on Redis Cloud; self-managed via a Helm chart that needs a licence. One lab per service, all on the free database and the 5,000 free messages, with the messages consumed per lab recorded. The naming trap — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — gets its own section. Read 2026-11-07 at [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 설계만 (2026-11-07).** 이 페이지의 내용은 아직 아무것도 실행하지 않았다. 계획은 [`design/DESIGN.md`](https://github.com/litkhai/redis-hols/blob/main/design/DESIGN.md)에 있다.
</div>

Redis Iris는 Redis의 표현으로 "AI 에이전트를 위한 프로덕션 준비 컨텍스트 엔진" — 서비스 묶음이지 데이터베이스가 아니고, 밑에 있는 데이터베이스가 Redis다. 2026-05-18 출시, 2026-11-04에 서비스 여섯이 됨: Intent Router, Agent Playbooks, Agent Memory, Context Gateway(GA), Lens, Agent Mesh(베타). Redis Cloud 관리형, 자체 운영은 라이선스가 필요한 Helm 차트. 서비스마다 랩 하나, 모두 무료 DB와 무료 5,000 메시지로, 랩마다 소비한 메시지 수를 기록. 이름 함정 — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — 은 별도 절. 2026-11-07 [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)에서 읽음.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：仅有设计（2026-11-07）。** 本页内容尚未实际运行。计划见 [`design/DESIGN.md`](https://github.com/litkhai/redis-hols/blob/main/design/DESIGN.md)。
</div>

Redis Iris 按 Redis 的说法是"面向 AI 代理的生产级上下文引擎" — 一组服务而非数据库，底层数据库是 Redis。2026-05-18 发布，2026-11-04 扩展为六项服务：Intent Router、Agent Playbooks、Agent Memory、Context Gateway（GA），Lens、Agent Mesh（beta）。Redis Cloud 托管；自管理需带许可证的 Helm chart。每项服务一个实验，全部使用免费数据库和 5,000 条免费消息，并记录每个实验消耗的消息数。命名陷阱 — Context Retriever → Context Gateway、LangCache 与 Agent Playbooks — 单独成节。2026-11-07 读取自 [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**状態: 設計のみ (2026-11-07)。** このページの内容はまだ何も実行していない。計画は [`design/DESIGN.md`](https://github.com/litkhai/redis-hols/blob/main/design/DESIGN.md) にある。
</div>

Redis Iris は Redis の言葉では「AI エージェント向けの本番対応コンテキストエンジン」 — サービス群でありデータベースではなく、その下にあるデータベースが Redis。2026-05-18 公開、2026-11-04 に六つのサービスに: Intent Router、Agent Playbooks、Agent Memory、Context Gateway（GA）、Lens、Agent Mesh（ベータ）。Redis Cloud のマネージド、セルフマネージドはライセンスが必要な Helm チャート。サービスごとにラボ一つ、すべて無料 DB と無料 5,000 メッセージで行い、ラボごとの消費メッセージ数を記録。名前の罠 — Context Retriever → Context Gateway、LangCache と Agent Playbooks — は別の節。2026-11-07 に [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/) で読んだ。

</div>
