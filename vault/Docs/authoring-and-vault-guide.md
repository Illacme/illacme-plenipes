---
title: 原稿文库组织与写作指引 (Authoring & Vault Guide)
layout: docs
slug: authoring-and-vault-guide
route_prefix: docs
date: 2026-08-16
author: Illacme Editorial Team
description: 掌握如何无缝接入 Obsidian、Logseq、Typora 或纯文本文库，规范 Frontmatter 元数据、双向链接与媒体资源引用。
tags: [Vault, Authoring, Markdown, Obsidian, Frontmatter]
categories: [Documentation]
---

# ✍️ 原稿文库组织与写作指引

**Illacme Plenipes** 坚持“原稿即主权”的原则。系统将您的物理文件夹作为权威源（Single Source of Truth），您无需放弃原有的写作习惯或笔记软件，即可享受工业级的出版体验。

---

## 📂 1. 文库目录结构最佳实践

系统推荐的典型文库结构如下（以 `./vault` 为例）：

```
vault/
├── index.md                      # 站点首页（或欢迎页）
├── about.md                      # 品牌 / 个人关于页
├── Docs/                         # 技术文档 / 教程 / 知识库
│   ├── index.md                  # 文档中心索引
│   ├── quick-start.md            # 快速入门
│   └── ...
├── Blog/                         # 博客文章 / 随笔 / 动态
│   ├── my-first-post.md
│   └── ...
├── Showcase/                     # 成果展厅 / 作品集
│   └── index.md
└── assets/                       # 本地图片 / 附件资源
    └── cover.png
```

> [!TIP]
> **目录即频道**：通过治理中心中的【分发路由与网址路径】（`route_matrix`），您可以自由将任意本地文件夹映射到线上 URL 路径（例如将 `Docs/` 映射为 `/docs/`，将 `Blog/` 映射为 `/blog/`）。

---

## 🏷️ 2. Frontmatter 元数据规范

每篇 Markdown 笔记顶部均推荐附带标准 YAML Frontmatter，用于精细控制文章的标题、作者、日期、分类与 SEO 信息：

```yaml
---
title: 我的技术深度解析                 # [必填] 文章标题
date: 2026-08-16                    # [推荐] 发布日期 (YYYY-MM-DD)
author: 极客创作者                   # [可选] 作者署名（留空则继承全域默认作者）
description: 一句话概述本文核心内容   # [推荐] 供 SEO 与卡片预览使用的摘要
tags: [Architecture, AI, Python]    # [可选] 标签列表，自动生成聚合标签页
categories: [Tech]                  # [可选] 分类列表
slug: deep-dive-tech                # [可选] 自定义线上 URL 后缀（留空自动生成）
draft: false                        # [可选] 设为 true 则仅在本地保存，不执行线上分发
---
```

---

## 🔗 3. 链接与媒体资产引用

### 3.1 双向链接 (WikiLinks)
系统全面兼容 Obsidian 样式的双向链接：
- **标准链接**：`[[quick-start]]` &rarr; 自动解析并链接至 `quick-start.md` 对应的线上 HTML。
- **自定义别名**：`[[quick-start|⚡ 5 分钟上手]]` &rarr; 渲染为显示别名的超链接。

### 3.2 图片与附件资源
- **相对路径引用**：`![文章封面](./assets/cover.png)`
- **绝对/全域路径**：`![Logo](/static/logo.png)`
- **自动 Alt 文本与 WebP 压缩**：引擎内置图像处理管线，可自动将大图无损转换为现代 WebP 格式，并在缺少 Alt 时由 AI 自动根据上下文生成多语种无障碍描述。

---

## ⚙️ 4. 换行模式与方言适配 (Dialect Sensing)

在治理中心【基础配置与运维】&rarr;【存储适配】中，您可以根据您的写作软件习惯选择：

1. **📄 标准模式 (CommonMark)**：单个换行符保留为空格流，连续两个换行（空行）才会分段。适合习惯标准 Markdown 语法的专业技术人员。
2. **✍️ 直觉模式 (GFM 硬换行)**：按一次 Enter 键即直接换行（所见即所得）。适合日常笔记记录或习惯 Typora / 微信排版的用户。

---

## 🔄 5. 如何接入已有文库 (Obsidian / Logseq)

如果您已有成体系的 Obsidian 知识库：
1. 打开治理中心【版图装帧与模式】&rarr;【版图管理】；
2. 点击「➕ 新建出版版图」；
3. 将 **原稿文库路径 (`vault_root`)** 指向您的物理笔记目录绝对路径（如 `/Users/username/Documents/ObsidianVault`）；
4. 选择装帧主题与分发渠道，点击保存即可瞬间唤醒您的专属数字出版社！
