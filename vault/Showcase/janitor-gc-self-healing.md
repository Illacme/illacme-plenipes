---
title: Janitor GC 物理清道夫与自愈账本
layout: page
slug: janitor-gc-self-healing
route_prefix: showcase
date: 2026-08-21
author: Illacme Sovereign Press
description: 了解 Illacme Plenipes 如何通过双向指纹账本自动清除失效幽灵 HTML 与孤岛资产，杜绝 404 死链并实现 LRU 缓存自愈。
tags: [Showcase, Janitor, GC, SelfHealing, Ledger, Performance]
---

# 🧹 Janitor GC 物理清道夫与自愈账本

> [!TIP]
> **拒绝臃肿与幽灵文件，保持磁盘绝对纯净**：传统静态站点生成器最常见的问题是：当创作者删除或重命名一篇笔记后，构建目录中依然残留着旧的 HTML 页面和切片图片。久而久之，站点充斥着死链与孤岛垃圾。Illacme Plenipes 内置了创新的 Janitor GC 物理清道夫与自愈账本。

---

## ⚡ 运维指标与自愈表现

<div class="stats-matrix" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin: 2rem 0;">
    <div class="stat-card" style="padding: 1.25rem 1.5rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">🧹 幽灵资产自动清除</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #00ff88;">0 幽灵 HTML · 0 孤岛图片</div>
    </div>
    <div class="stat-card" style="padding: 1.25rem 1.5rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">📜 SHA-256 账本对账</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #00f2fe;">毫秒级增量 · 仅重编变动块</div>
    </div>
    <div class="stat-card" style="padding: 1.25rem 1.5rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">♻️ LRU 缓存智能淘汰</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #ffb300;">按体积/时间窗自动降解</div>
    </div>
    <div class="stat-card" style="padding: 1.25rem 1.5rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">🛡️ 仓库合规审计</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--accent-color);">母本主题 100% 物理只读保护</div>
    </div>
</div>

---

## 🛠️ 核心机制与自愈架构

### 1. 📜 双向物理指纹账本 (Fingerprint Ledger)
系统在本地 SQLite 数据库与缓存目录中维护着创作者文库的全局指纹账本：
* 记录每个原稿文件（Markdown、图片、附件）的 SHA-256 哈希值与修改时间戳；
* 记录该文件所衍生出的所有目标产物（多语种 HTML、OpenGraph 社交卡片、图床引用 URL）。

### 2. 🧹 Janitor 物理清道夫 (Ghost Asset Scrubber)
在每次增量编译或同步触发时，Janitor 自动介入：
1. **反向比对**：遍历产物输出目录中的全部 HTML 和资源文件，检查是否存在“已没有对应源文档”的孤岛文件；
2. **安全回收**：毫秒级自动物理删除这些幽灵文件与过时路由映射，杜绝网站产生 404 死链；
3. **Sitemap 与索引同步修正**：自动从 `sitemap.xml` 和 `graph.json` 宇宙星系拓扑中剔除已删除节点。

### 3. ♻️ LRU 缓存治理与自动降解策略
* 在治理中心「存储适配」面板中，创作者可灵活设定算力缓存（Janitor GC）上限（如保留最近 30 天 / 500MB）；
* 当本地 AI 翻译段落缓存或生成式配图超过阈值时，引擎会优先淘汰最旧且未被锁定的低频段落，确保系统即便运行数年依然轻盈如初。
