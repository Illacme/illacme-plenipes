---
title: 创作者 5 分钟极速入门指南
date: 2026-08-03
author: Illacme Onboarding Group
description: 指引新创作者如何快速上手配置系统、管理出版版图并体验全全渠道同步功能。
tags: [Guide, Onboarding, Manual]
---

# 📖 创作者 5 分钟极速入门指南

欢迎使用 **Illacme Plenipes**！本指南将带您在 5 分钟内掌握治理中心使用技巧与发布流程。

---

## 🛠️ 步骤一：探索治理中心 (Governance Dashboard)

打开浏览器访问仪表盘 `http://127.0.0.1:43212/dashboard/`：

1. **基础配置与运维 (`general`)**：查看身份标识、合规元数据及算力缓存清理中枢。
2. **版图装帧与模式 (`layout`)**：管理品牌 Imprints、切换视觉主题（如 Starlight）及出版模式。
3. **语言翻译与治理 (`localization_gov`)**：配置多语种矩阵、块级规则与术语词库。

---

## ⚡ 步骤二：命令行极速同步

除了图形界面外，您也可以随时使用 CLI 命令执行增量预检与同步：

```bash
# 启动全量增量扫描与对齐
python3 plenipes.py --once

# 启动看门狗实时监听模式
python3 plenipes.py --watch
```

---

## 🎨 步骤三：本地预览与全域分发

运行发布流水线后，您可以随时启动本地预览服务端口 `43213` 实时查看优雅的静态渲染站点！
