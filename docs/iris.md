---
layout: default
title: Iris
permalink: /iris/
---

# Redis Iris

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: design only.** Nothing on this page has been run yet. The plan is in [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Iris is, in Redis's words, "a production-ready context engine for AI agents" — a suite of services, not a database; Redis is the database underneath. Launched 2026-05-18; on 2026-11-04 it became six services: Intent Router, Agent Playbooks, Agent Memory and Context Gateway (GA), Lens and Agent Mesh (beta). Managed on Redis Cloud; self-managed via a Helm chart that needs a licence. One lab per service, all on the free database and the 5,000 free messages, with the messages consumed per lab recorded. The naming trap — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — gets its own section. Read 2026-11-07 at [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 설계만.** 이 페이지의 내용은 아직 아무것도 실행하지 않았다. 계획은 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)에 있다.
</div>

Redis Iris는 Redis의 표현으로 "AI 에이전트를 위한 프로덕션 준비 컨텍스트 엔진" — 서비스 묶음이지 데이터베이스가 아니고, 밑에 있는 데이터베이스가 Redis다. 2026-05-18 출시, 2026-11-04에 서비스 여섯이 됨: Intent Router, Agent Playbooks, Agent Memory, Context Gateway(GA), Lens, Agent Mesh(베타). Redis Cloud 관리형, 자체 운영은 라이선스가 필요한 Helm 차트. 서비스마다 랩 하나, 모두 무료 DB와 무료 5,000 메시지로, 랩마다 소비한 메시지 수를 기록. 이름 함정 — Context Retriever → Context Gateway, LangCache vs Agent Playbooks — 은 별도 절. 2026-11-07 [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)에서 읽음.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：仅有设计。** 本页内容尚未实际运行。计划见 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)。
</div>

Redis Iris 按 Redis 的说法是"面向 AI 代理的生产级上下文引擎" — 一组服务而非数据库，底层数据库是 Redis。2026-05-18 发布，2026-11-04 扩展为六项服务：Intent Router、Agent Playbooks、Agent Memory、Context Gateway（GA），Lens、Agent Mesh（beta）。Redis Cloud 托管；自管理需带许可证的 Helm chart。每项服务一个实验，全部使用免费数据库和 5,000 条免费消息，并记录每个实验消耗的消息数。命名陷阱 — Context Retriever → Context Gateway、LangCache 与 Agent Playbooks — 单独成节。2026-11-07 读取自 [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**状態: 設計のみ。** このページの内容はまだ何も実行していない。計画は [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) にある。
</div>

Redis Iris は Redis の言葉では「AI エージェント向けの本番対応コンテキストエンジン」 — サービス群でありデータベースではなく、その下にあるデータベースが Redis。2026-05-18 公開、2026-11-04 に六つのサービスに: Intent Router、Agent Playbooks、Agent Memory、Context Gateway（GA）、Lens、Agent Mesh（ベータ）。Redis Cloud のマネージド、セルフマネージドはライセンスが必要な Helm チャート。サービスごとにラボ一つ、すべて無料 DB と無料 5,000 メッセージで行い、ラボごとの消費メッセージ数を記録。名前の罠 — Context Retriever → Context Gateway、LangCache と Agent Playbooks — は別の節。2026-11-07 に [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/) で読んだ。

</div>

<div class="lang" data-lang="th" markdown="1">

## ภาษาไทย

<div class="note" markdown="1">
**สถานะ: ออกแบบเท่านั้น** ยังไม่ได้รันสิ่งใดในหน้านี้ แผนอยู่ใน [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)
</div>

Redis Iris ตามคำของ Redis คือ "a production-ready context engine for AI agents" เป็นชุดบริการ ไม่ใช่ฐานข้อมูล โดยมี Redis เป็นฐานข้อมูลอยู่ข้างใต้ เปิดตัวเมื่อ 2026-05-18 และเมื่อ 2026-11-04 กลายเป็นหกบริการ ได้แก่ Intent Router, Agent Playbooks, Agent Memory และ Context Gateway (GA) รวมถึง Lens และ Agent Mesh (beta) ให้บริการแบบจัดการให้บน Redis Cloud ส่วนแบบดูแลเองใช้ Helm chart ซึ่งต้องมีใบอนุญาต มีหนึ่งแล็บต่อหนึ่งบริการ ทั้งหมดใช้ฐานข้อมูลฟรีและข้อความฟรี 5,000 ข้อความ โดยบันทึกจำนวนข้อความที่แต่ละแล็บใช้ไป กับดักเรื่องชื่อ คือ Context Retriever → Context Gateway และ LangCache เทียบกับ Agent Playbooks มีหัวข้อแยกต่างหาก อ่านเมื่อ 2026-11-07 ที่ [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/)

</div>

<div class="lang" data-lang="id" markdown="1">

## Bahasa Indonesia

<div class="note" markdown="1">
**Status: hanya desain.** Belum ada yang dijalankan di halaman ini. Rencananya ada di [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Iris, menurut Redis, adalah "a production-ready context engine for AI agents", yaitu kumpulan layanan, bukan basis data; Redis adalah basis data di bawahnya. Diluncurkan 2026-05-18; pada 2026-11-04 menjadi enam layanan: Intent Router, Agent Playbooks, Agent Memory dan Context Gateway (GA), Lens dan Agent Mesh (beta). Dikelola di Redis Cloud; untuk dikelola sendiri tersedia Helm chart yang memerlukan lisensi. Satu lab per layanan, semuanya memakai basis data gratis dan 5.000 pesan gratis, dengan jumlah pesan yang terpakai per lab dicatat. Jebakan penamaan, yaitu Context Retriever → Context Gateway serta LangCache vs Agent Playbooks, dibahas di bagian tersendiri. Dibaca 2026-11-07 di [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

</div>

<div class="lang" data-lang="ms" markdown="1">

## Bahasa Melayu

<div class="note" markdown="1">
**Status: reka bentuk sahaja.** Belum ada apa-apa di halaman ini yang telah dijalankan. Perancangannya ada dalam [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

Redis Iris, menurut Redis, ialah "a production-ready context engine for AI agents", iaitu suite perkhidmatan, bukan pangkalan data; Redis ialah pangkalan data di bawahnya. Dilancarkan 2026-05-18; pada 2026-11-04 ia menjadi enam perkhidmatan: Intent Router, Agent Playbooks, Agent Memory dan Context Gateway (GA), Lens dan Agent Mesh (beta). Diurus di Redis Cloud; untuk diurus sendiri tersedia Helm chart yang memerlukan lesen. Satu makmal bagi setiap perkhidmatan, kesemuanya menggunakan pangkalan data percuma dan 5,000 mesej percuma, dengan bilangan mesej yang digunakan setiap makmal direkodkan. Perangkap penamaan, iaitu Context Retriever → Context Gateway serta LangCache vs Agent Playbooks, diberi bahagian tersendiri. Dibaca 2026-11-07 di [redis.io/docs — context engine](https://redis.io/docs/latest/develop/ai/context-engine/).

</div>
