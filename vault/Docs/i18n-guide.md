---
title: 多语言矩阵与内容治理实战
layout: docs
slug: i18n-guide
route_prefix: docs
date: 2026-08-16
author: Illacme Localization Team
description: 掌握多语种矩阵配置、块级规则保护、术语词库管理与段落重译校对工作流。
tags: [i18n, Localization, Glossary, BlockRules]
categories: [Documentation]
---

# 🌍 多语言矩阵与内容治理实战

**Illacme Plenipes** 提供了企业级的多语言内容治理管线，让您只需专注于用母语起草原稿，系统即可自动完成高保真跨语种编译与发布。

---

## 🧭 多语言核心架构

1. **源语言（Source Language）**：起草原稿时使用的母语（如中文 `zh` 或英文 `en`）。
2. **目标语种矩阵（Target Languages）**：需要自动翻译并分发的目标语言集合（如 `en`, `ja`, `fr`, `de`, `es`, `ko` 等）。
3. **块级规则（Block Rules）**：针对特定段落类型（代码块、公式、专有名词、版权声明）的保护策略，避免 AI 误翻译。
4. **术语词库（Glossary）**：跨文章强制统一的行业专有名词中英对照表。

---

## 🧱 块级规则（Block Rules）保护

系统内置多层 AST 语法树保护器：

- **代码块保护**：` ```python ... ``` ` 内部代码完全保持原样，仅根据需要翻译注释。
- **Obsidian 内部双链**：`[[quick-start|快速入门]]` 自动保留目标链接名，并根据目标语言智能调整别名。
- **Markdown 呼号**：`> [!NOTE]` 语法容器自动保留，仅翻译正文内容。

---

## 📖 术语词库（Glossary）配置

在治理中心【语言与内容治理】&rarr;【术语词库】中，您可以定义全站术语对：

```yaml
glossary:
  "主权出版": "Sovereign Publishing"
  "段落影子缓存": "Block Shadow Cache"
  "品牌版图": "Imprint"
  "装帧工厂": "SSG Bindery"
```

AI 在翻译过程中将自动遵循词库约束，确保跨文章专有名词的一致性与严谨度。

---

## 🔄 单段重译与校对工作台

如果您对某一段落的译文不满意，可在治理中心中使用**校对工作台（Review Workbench）**：
1. 实时对比原文与译文段落。
2. 针对单个段落触发单段 AI 重新翻译（无需重译整篇文章）。
3. 支持手动直接微调并写入段落缓存（Block Cache）。

---

## 🧭 相关阅读

- 了解算力节点配置：[[compute-and-ai|算力中心与 AI 翻译]]
- 探索治理中心界面：[[dashboard-guide|治理中心操作指南]]
