---
title: 治理中心 (Governance Dashboard) 操作指南
date: 2026-08-11
author: Illacme Editorial Team
description: 详尽拆解治理中心四大核心分类与二级子标签功能，涵盖基础配置、版图管理、多语言矩阵与路由映射。
tags: [Dashboard, Governance, Settings]
categories: [Documentation]
---

# 🎛️ 治理中心 (Governance Dashboard) 操作指南

治理中心是 **Illacme Plenipes** 的可视化控制塔。采用现代化高档毛玻璃设计体系，为创作者提供全方位的出版运维中枢。

---

## 🧭 四大核心分类导航

治理中心由四大顶级分类构成，每个分类均配备二级子标签（Sub-Tabs）：

```
治理中心 (Dashboard)
├── 1. 基础配置与运维 (General)
│   ├── 🏷️ 身份标识 (identity)
│   ├── 📖 出版合规 (compliance)
│   ├── 📂 存储适配 (storage)
│   └── ⚙️ 运行基座 (engine)
├── 2. 版图装帧与模式 (Layout)
│   ├── 🏷️ 版图管理 (imprints)
│   ├── 🎭 装帧主题 (themes)
│   └── 📋 出版模式 (modes)
├── 3. 语言翻译与治理 (Localization)
│   ├── 🌍 语种矩阵 (localization)
│   ├── 🧱 块级规则 (block_rules)
│   ├── 📖 术语词库 (glossary)
│   └── 🎭 翻译风格 (translation_style)
└── 4. 分发路由与网址 (Dissemination)
    ├── 📝 网址路径 (slug_settings)
    └── 🧭 频道映射 (route_matrix)
```

---

## 1. 基础配置与运维 (General Configuration)

- **🏷️ 身份标识 (Identity)**：配置品牌名称（`imprint_name`）、品牌描述、站点 Logo 路径与版权信息。
- **📖 出版合规 (Compliance)**：统一配置 Frontmatter 默认作者、许可证类型（如 CC BY-NC 4.0）及元数据清洗规则。
- **📂 存储适配 (Storage)**：文库物理路径（`vault_root`）、原稿换行模式（硬换行 / 软换行）、以及**段落缓存治理中枢（Block Cache Hub）**与算力缓存自动清理（Janitor GC / LRU）策略。
- **⚙️ 运行基座 (Engine)**：调节日志级别、全局代理、网络超时与遥测采集容量上限。

---

## 2. 版图装帧与模式 (Layout & Publishing Modes)

- **🏷️ 版图管理 (Imprints)**：一览所有独立出版品牌，支持一键切换当前激活的出版版图。
- **🎭 装帧主题 (Themes)**：自由切换站点装帧风格（Sovereign、Docusaurus、Starlight、VitePress、Nextra、Hugo）。
- **📋 出版模式 (Modes)**：
  - **基础模式 (Basic)**：纯物理拷贝分发，零 AI 算力开销。
  - **增强模式 (Enhanced)**：母语 AI 润色与智能 SEO 增强。
  - **全球模式 (Global)**：全量多语种矩阵翻译与全球全渠道分发。

---

## 3. 语言翻译与治理 (Localization & Content Governance)

- **🌍 语种矩阵 (Localization)**：勾选或添加目标翻译语种（英语、日语、德语、法语、西班牙语等 50+ 语种）。
- **🧱 块级规则 (Block Rules)**：针对代码块、表格、Callout、HTML 标签设定精细的“翻译 / 旁路 (Bypass) / 遮蔽 (Mask)”策略。
- **📖 术语词库 (Glossary)**：维护专业专有名词词汇表，确保专有名词在多语言翻译中 100% 准确一致。
- **🎭 翻译风格 (Translation Style)**：定制各频道特有的翻译语气（技术严谨、文学叙事、幽默风趣等）。

---

## 4. 分发路由与网址路径 (Dissemination & Routing)

- **📝 网址路径 (Slug Settings)**：配置 AI Slug 生成模式（平铺 Flat / 阶梯 Hierarchical），自动生成符合 SEO 规范的英文 URL。
- **🧭 频道映射 (Route Matrix)**：将本地子文件夹（如 `Blog`、`Docs`）映射到前端站点的对应 URL 前缀（如 `/blog/`、`/docs/`）。

---

> [!NOTE]
> 治理中心中所有的配置保存均为**毫秒级热更新**，修改后即刻在下一次同步中生效。
