---
layout: default
title: Deep Dive
permalink: /deep-dive/
---

# Deep Dive

<div class="lang" data-lang="en" markdown="1">

## English

<div class="note" markdown="1">
**Status: design only.** Nothing on this page has been run yet. The plan is in [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md).
</div>

One page per mechanism, each with the mechanism in plain words, the official doc link, a script that produces a number or an observable, and the output as run: threading and the event loop (`io-threads`), persistence (RDB, AOF, `BACKUP` since 8.10), replication / Sentinel / Cluster (`PSYNC`, failover, 16384 slots, `CLUSTER MIGRATION`), eviction and memory (LRU / LFU / LRM, `HOTKEYS`), client-side caching (`CLIENT TRACKING`), Streams (consumer groups, `IDMP`, `XNACK`), Functions and ACL.

</div>

<div class="lang" data-lang="ko" markdown="1">

## 한국어

<div class="note" markdown="1">
**상태: 설계만.** 이 페이지의 내용은 아직 아무것도 실행하지 않았다. 계획은 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)에 있다.
</div>

메커니즘당 한 페이지 — 평이한 설명, 공식 문서 링크, 숫자나 관찰을 만드는 스크립트, 실행한 출력: 스레딩과 이벤트 루프(`io-threads`), 영속성(RDB, AOF, 8.10의 `BACKUP`), 복제 / Sentinel / Cluster(`PSYNC`, 페일오버, 16384 슬롯, `CLUSTER MIGRATION`), 축출과 메모리(LRU / LFU / LRM, `HOTKEYS`), 클라이언트 캐시(`CLIENT TRACKING`), Streams(컨슈머 그룹, `IDMP`, `XNACK`), Functions와 ACL.

</div>

<div class="lang" data-lang="zh" markdown="1">

## 简体中文

<div class="note" markdown="1">
**状态：仅有设计。** 本页内容尚未实际运行。计划见 [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md)。
</div>

每个机制一页 — 通俗说明、官方文档链接、产生数字或可观察结果的脚本、实际运行输出：线程与事件循环（`io-threads`）、持久化（RDB、AOF、8.10 的 `BACKUP`）、复制 / Sentinel / Cluster（`PSYNC`、故障转移、16384 个槽、`CLUSTER MIGRATION`）、淘汰与内存（LRU / LFU / LRM、`HOTKEYS`）、客户端缓存（`CLIENT TRACKING`）、Streams（消费者组、`IDMP`、`XNACK`）、Functions 与 ACL。

</div>

<div class="lang" data-lang="ja" markdown="1">

## 日本語

<div class="note" markdown="1">
**状態: 設計のみ。** このページの内容はまだ何も実行していない。計画は [`design/DESIGN.md`](https://github.com/litkhai/notes-on-redis/blob/main/design/DESIGN.md) にある。
</div>

仕組みごとに一ページ — 平易な説明、公式ドキュメントへのリンク、数値や観察結果を生むスクリプト、実行した出力: スレッドとイベントループ（`io-threads`）、永続化（RDB、AOF、8.10 の `BACKUP`）、レプリケーション / Sentinel / Cluster（`PSYNC`、フェイルオーバー、16384 スロット、`CLUSTER MIGRATION`）、エビクションとメモリ（LRU / LFU / LRM、`HOTKEYS`）、クライアントサイドキャッシュ（`CLIENT TRACKING`）、Streams（コンシューマーグループ、`IDMP`、`XNACK`）、Functions と ACL。

</div>
