---
title: 主权出版架构与零侵入 Markdown 节点治理
date: 2026-08-03
author: Illacme Architecture Team
description: 深入解析 Illacme Plenipes 的物理主权隔离、插件矩阵与自动降级防护机制。
tags: [Architecture, Sovereign, Security]
---

# 🛡️ 主权出版架构与零侵入 Markdown 节点治理

在数字出版与个人知识管理（PKM）领域，**内容物理主权**与**隐私安全**是创作者最重要的红线。Illacme Plenipes 采用了创新的“主权出版（Sovereign Publishing）”架构。

---

## 🏛️ 物理架构解耦

系统的设计遵循“零数据污染”与“无物理侵入”原则：

| 架构层级 | 物理组件 | 职责说明 |
|---|---|---|
| **原稿文库层** | `./vault/` | 创作者纯粹的 Markdown 笔记，系统**仅只读扫描**，绝对不破坏原稿结构 |
| **出版主权层** | `imprints/*/` | 多品牌物理隔离，存储专属主题、算力与配置模板 |
| **装帧渲染层** | `themes/*/` | 负责静态 SSG（Starlight / Docusaurus 等）前端模板渲染与产物输出 |
| **状态机账本** | `.plenipes/ledger.db` | SQLite/JSON 架构，记录切片指纹、Slug 映射与增量变更 |

---

## 🔒 物理防护与容错机制

> [!IMPORTANT]
> 系统的后台非交互式子进程均注入了强制非交互标志（如 `npx -y` 与 `--disable-pip-version-check`），确保任务永远自愈闭环退出，绝不卡死挂起。

### 自动化离线安全自愈
- **主权真空保护**：当检测到路径缺失或配置文件损坏时，系统启动零配置自愈探查机制。
- **单例进程占位锁**：通过绑定端口 `43210` 物理防范多进程竞态冲突。
