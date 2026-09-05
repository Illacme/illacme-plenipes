---
author: Illacme Core Team
categories:
- Documentation
date: '2026-08-30'
description: 段落级影子缓存 (Block Cache Hub) 的设计原理、物理路由机制、LRU 垃圾回收算法以及自动清理 (Janitor GC)
  策略。
layout: docs
route_prefix: docs
slug: block-cache-hub
tags:
- Engineering
- Cache
- Sovereign
- GC
title: 段落缓存治理中枢 (Block Cache Hub)
---
# 🧱 段落缓存治理中枢 (Block Cache Hub)

本指南详细介绍了 **Illacme Plenipes** 段落级影子缓存 (Block Cache Hub) 的设计原理、物理路由机制、LRU 垃圾回收算法以及自动清理 (Janitor GC) 策略。

---

## 🏗️ 1. 定义与物理路由 (Definition & Physical Routing)

### 什么是 Block Cache Hub？
在多语言出版与 AI 语义翻译管线中，段落级影子缓存 (Block Cache Hub) 负责维护原稿中每个物理段落 (Block) 的哈希值及其关联译文、元数据的映射。它能在原稿微调时，仅对发生变更的段落触发增量翻译，避免全量重新计算。

### 物理路由设计
段落影子缓存采用局部物理隔离存储：
- **配置文件路径**：`config.yaml` 或 `config.local.yaml` 中定义了缓存中枢策略。
- **物理持久化库**：对于当前品牌版图，其段落影子缓存持久化落盘在 `imprints/{brand}/cache/block_cache.db` 或 `.cache/` 目录下，与原稿文库完全物理隔离，确保文库纯净。

---

## ⚙️ 2. LRU 垃圾回收与缓存有效性验证算法 (LRU GC & Validation)

### LRU 垃圾回收机制
缓存中枢基于 **LRU (Least Recently Used)** 算法淘汰最旧的、无访问的缓存记录，维持物理存储在安全水线内。
- **访问更新**：每当有文档的某个段落命中缓存，其 LRU 时间戳更新为当前时间。
- **主动释放**：在超出阈值时，自动驱逐最久未使用的段落译文。

### 段落有效性验证算法 (Block Validation Algorithm)
每个缓存块由其源码段落的内容生成唯一的 SHA-256 哈希值 (Block Hash)。
验证流程如下：
1. 读取文档时，按空行或物理标记拆分成若干段落。
2. 逐段计算哈希 `sha256(content + block_context_salt)`。
3. 对比缓存库中的 `block_hash`：
   - **一致 (Hit)**：重用已有翻译与段落属性，无需重新调用 LLM。
   - **不一致 (Miss)**：标记为脏段落 (Dirty Block)，送入翻译待处理队列，并废弃原有该位置的缓存。

---

## 🔄 3. 缓存驱逐与段落校验契约 (Eviction & Verification Rules)

### 缓存驱逐工作流 (Eviction Flow)
```
[文档发生变更] ──> [计算新段落哈希列表] ──> [对比缓存映射]
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
         [哈希一致 (Hit)]                                               [哈希不一致 (Miss)]
    复用缓存，更新访问热度时间戳                                   物理驱逐失效缓存 ──> 触发 AI 翻译并写入新缓存
```

### 段落校验三铁律 (Verification Rules)
1. **结构不破坏**：被翻译段落的 Markdown 标记（加粗、链接、列表、代码块）在校验时，译文必须包含等价的标记符号，严禁丢失格式。
2. **上下文隔离**：哈希计算时，结合前导与后继段落的部分元数据（Block Context Salt），防止完全相同的内容在不同上下文中因歧义产生不匹配翻译。
3. **签名防篡改**：本地持久化数据库中所有缓存记录附带 Adler32 或 SHA-256 数据校验和，加载时若签名失效则判定物理损坏，自动初始化自愈。

---

## 🧹 4. 自动清理策略与容量阈值 (Janitor GC Policy)

### Janitor GC 自动清理器
系统驻留的 Janitor 守护协程定期执行缓存容量与物理占用率审计。

### 容量与阈值规则 (Threshold Rules)
- **物理存储水线**：单品牌 Block Cache 物理文件占用上限默认为 **128MB**，达到 80% (102.4MB) 时触发温和清理。
- **段落数量水线**：总段落记录数上限默认为 **100,000 条**。超过该阈值时，Janitor GC 启动并根据 LRU 热度对末尾 20% 的过期影子缓存块执行物理强制抹除 (Erase)，确保系统运行轻量与高响应度。
- **过期时间 (TTL)**：任何 90 天内未被读取或校验的段落记录均判定为冷数据 (Cold Cache)，在 GC 周期内被自动清空。