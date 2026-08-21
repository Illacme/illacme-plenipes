---
title: 物理隔离架构与技术原理
layout: docs
slug: architecture
route_prefix: docs
date: 2026-08-16
author: Illacme Core Architecture Team
description: 深度剖析 Illacme Plenipes 的物理主权隔离模型、双相分发管线与四端口微内核架构。
tags: [Architecture, Sovereign, Security, Core]
categories: [Documentation]
---

# 🏛️ 物理隔离架构与技术原理

**Illacme Plenipes** 遵循“主权绝对隔离（Sovereign Isolation Architecture）”哲学。本章将详细拆解系统的核心架构、物理数据流向与安全设计。

---

## 🏗️ 整体分层架构模型

```
┌─────────────────────────────────────────────────────────────┐
│                    创作者本地 Markdown 文库 (Vault)           │
│                   Obsidian / Logseq / Typora / CommonMark   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (只读探测与增量哈希)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Illacme 核心流转管线 (Pipeline)              │
│        读取净化 ──> 语义织网 ──> AI SEO 增强 ──> 遮罩路由     │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐┌─────────────────────────────┐
│   🧠 算力调度中心 (Compute)   ││   🎭 装帧编译工厂 (Bindery) │
│  本地 Ollama / LMStudio      ││  Sovereign / Docusaurus     │
│  云端 DeepSeek / OpenAI / xAI││  VitePress / Starlight      │
│  段落级影子缓存 (BlockCache) ││  全量静态 HTML / 源码包     │
└──────────────┬───────────────┘└─────────────┬───────────────┘
               │                              │
               └──────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 🛰️ 全球发行矩阵 (The Matrix)                 │
│      11 大托管平台 (GitHub / Vercel) + 12 大社交媒体渠道     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 四大物理隔离红线

### 1. 原稿文库只读红线 (Vault Read-Only Sentry)
系统对创作者的原稿目录（`vault/`）采用只读扫描与哈希索引，**绝不在原稿目录中写入任何临时构建文件或缓存数据库**。

### 2. 品牌版图物理隔离 (Imprint Territory Sovereignty)
每个品牌拥有独立的文件树（`imprints/{brand}/`），其配置文件、元数据账本（`ledger.db`）、装帧产物及日志均独立隔离，互不干扰。

### 3. 主题母本只读隔离 (Mother Theme Isolation)
系统自带的官方主题模板（`themes/`）作为纯净的只读母本（Mother Themes）。所有构建产物和用户静态输出均定向写入版图或全局 `dist/`，严禁污染母本目录。

### 4. 算力密钥本地加密隔离 (Credential Vault)
所有 API 密钥在落盘时均经过主权密文加密（`enc:...`），主配置文件中严禁存储明文 Key，杜绝代码提交导致的密钥泄露。

---

## 🔌 四端口微服务规划

| 服务端口 | 物理职责 | 说明 |
| :--- | :--- | :--- |
| **`43210`** | 🔒 单例进程锁 (Singleton Lock) | 进程唯一性占位锁，防止后台重复拉起导致 I/O 冲突。 |
| **`43212`** | 🔌 控制网关 (Web API Gateway) | FastAPI Web 控制服务，承载仪表盘交互与全量数据调度。 |
| **`43211`** | 🧙 可视化向导 (Wizard Port) | 引导安装与新用户初始化向导服务端口。 |
| **`43213`** | 🌐 本地静态预览 (Preview Server) | 本地快速浏览生成的多语言静态站点成品。 |

---

## 🚀 进一步阅读

- 深入算力与缓存中枢：[[compute-and-ai|算力中心与 AI 翻译]]
- 掌握主题装帧定制：[[themes-and-binding|装帧主题与视觉定制]]
- 配置多渠道全网推送：[[distribution-channels|发行矩阵配置]]
