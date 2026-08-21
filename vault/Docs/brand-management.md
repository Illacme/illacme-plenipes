---
title: 品牌版图 (Imprint) 多站点与工作区管理
layout: docs
slug: brand-management
route_prefix: docs
date: 2026-08-16
author: Illacme Editorial Team
description: 掌握如何构建多个相互物理隔离的独立出版版图，为不同写作领域定制专属主题、算力与分发矩阵。
tags: [Imprint, MultiSite, Workspace, Governance]
categories: [Documentation]
---

# 🏷️ 品牌版图 (Imprint) 多站点与工作区管理

在 **Illacme Plenipes** 中，每一个出版项目都是一个独立的**“品牌版图 (Imprint)”**。本指南将带您深入了解如何利用多品牌架构实现多站点、多文库与多渠道的绝对物理隔离管理。

---

## 🏛️ 1. 什么是“品牌版图 (Imprint)”？

当一位创作者同时经营多个领域的内容时（例如：个人技术博客、学术研究专栏、企业产品文档、生活旅行随笔），传统的发布工具往往需要部署多套独立程序或在同一数据库中混杂混乱。

**Illacme Plenipes 的多版图架构**：
- **物理隔离存储**：每个品牌拥有专属目录 `imprints/{brand}/`，独立存储配置（`config.imprint.yaml`）、历史账本（`usage_ledger.json`）与同步状态。
- **独立原稿文库**：品牌 A 可以绑定 `/Vaults/TechDocs`，品牌 B 可以绑定 `/Vaults/DailyLife`。
- **独立装帧主题**：技术站点可选用 `Docusaurus` 或 `Starlight`，个人博客选用 `Sovereign` 赛博风。
- **独立分发矩阵**：技术文章同步至 GitHub Pages 与 Dev.to，随笔文章同步至微信公众号与 Substack。

---

## 🚀 2. 如何新建与切换品牌

### 方式一：在治理中心中可视化操作
1. 打开浏览器进入治理中心：`http://127.0.0.1:43212/dashboard/`
2. 导航至【版图装帧与模式】&rarr;【版图管理 (imprints)】
3. 点击「➕ 新建出版版图」按钮，输入品牌代号（如 `tech_weekly`）与展示名称
4. 配置该品牌的文库路径、主题风格与分发凭据
5. 点击「激活并切换」，系统将毫秒级热切换当前工作空间！

### 方式二：命令行极速操作
```bash
# 1. 唤醒指挥中心
python3 plenipes.py

# 2. 在交互菜单中选择 [1] 切换出版版图，或使用参数指定启动：
python3 plenipes.py --imprint tech_weekly --sync
```

---

## 🛡️ 3. 默认品牌 (Default Imprint) 的特殊定位

- **开箱即用展示橱窗**：系统自带的 `imprints/default` 是官方提供的标准模板。
- **全功能体验特权**：当处于 `default` 品牌且激活 `Sovereign` 主题时，系统默认解锁全量高级专业版特性。
- **推荐实践**：建议您保留 `default` 作为系统功能试验场，并通过新建专属品牌来承载您的生产级实际文库。

---

## 🧭 4. 相关阅读

- 开始起草原稿：[[authoring-and-vault-guide|原稿文库组织与写作指引]]
- 装帧风格切换：[[themes-and-binding|装帧主题与视觉定制]]
- 全网分发配置：[[distribution-channels|发行矩阵与渠道配置]]
