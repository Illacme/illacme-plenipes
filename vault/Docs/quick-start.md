---
title: 创作者 5 分钟极速上手指南
layout: docs
slug: quick-start
route_prefix: docs
date: 2026-08-16
author: Illacme Onboarding Group
description: 5 步带您在几分钟内完成从本地环境唤醒、治理中心体验、原稿起草到全网发布的完整流程。
tags: [QuickStart, Tutorial, Onboarding]
categories: [Documentation]
---

# ⚡ 创作者 5 分钟极速上手指南

欢迎使用 **Illacme Plenipes**！跟随以下 5 个简单步骤，您将在几分钟内体验从创作到全网发布的全链路流程。

---

## 🛠️ 第一步：启动出版指挥中心

在终端运行以下命令唤醒系统：

```bash
# 启动出版指挥中心与治理面板
python3 plenipes.py
```

终端将打印典雅的 ASCII 出版徽章，并自动启动 Web API 控制网关（端口 `43212`）与治理中心。

---

## 🎛️ 第二步：进入治理中心 (Governance Dashboard)

打开浏览器访问：
👉 `http://127.0.0.1:43212/dashboard/`

在治理中心中，您可以直观体验：
1. **基础配置与运维**：查看品牌身份、存储适配与算力缓存清理中枢。
2. **版图装帧与模式**：切换品牌、配置主题与出版模式（基础 / 增强 / 全球）。
3. **语言翻译与治理**：配置多语种矩阵、块级过滤规则与术语词库。
4. **分发路由与网址路径**：配置文件夹与 URL 路径映射矩阵。

> [!TIP]
> 默认品牌（Illacme Press）已默认解锁全部高级专业版功能，您可以自由尝试所有配置项！

---

## ✍️ 第三步：在本地文库中起草原稿

您的原稿安全存放在 `./vault` 文件夹中。您可以使用喜欢的 Markdown 编辑器（如 Obsidian）：

- 在 `./vault/Blog/` 下创建新文件 `my-note.md`
- 填入标准的 Markdown 标题与正文

```markdown
---
title: 我的第一篇主权笔记
date: 2026-08-16
tags: [HelloWorld, Note]
---

# 🚀 记录我的最新思考

这是我在 Illacme Plenipes 中撰写的第一篇原稿！
```

---

## 🚀 第四步：一键全域发布与翻译

通过以下任一方式触发发布：
1. **图形界面**：在治理中心右上角点击 **🚀 全域发布** 按钮。
2. **命令行**：运行 `python3 plenipes.py --sync` 执行单次全量同步。

系统将自动执行：
- 增量段落切片与哈希计算（未修改部分零 Token 消耗）
- 算力中心多语言润色与翻译
- AI SEO 结构化元数据提取
- 静态站点 HTML 产物渲染

---

## 🌐 第五步：本地预览出版成果

同步完成后，访问本地预览服务：
👉 `http://127.0.0.1:43213/`

您将看到由 **Sovereign** 赛博主题装帧完毕的现代化站点，包含中英文双语切换、动态目录、即时搜索与响应式布局！

---

## 🧭 进阶探索推荐

- 学习文库管理与 Frontmatter 规范：[[authoring-and-vault-guide|✍️ 原稿文库组织与写作指引]]
- 建立您的独立出版品牌：[[brand-management|🏷️ 品牌版图多站点管理]]
- 探索治理中心全景：[[dashboard-guide|🎛️ 治理中心操作全解]]
- 配置您的专属算力：[[compute-and-ai|🧠 算力中心与 AI 翻译]]
- 定制全渠道分发：[[distribution-channels|🛰️ 发行矩阵配置]]

