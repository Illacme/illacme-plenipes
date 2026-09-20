#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Imprint Showcase Content
职责：提供演示文库注入所需的中英双语 6 大装帧模板特性指南与创世手稿文本。
"""

from .imprint_showcase_content_part2 import (
    get_starlight_doc,
    get_nextra_doc,
    get_vitepress_doc,
)

__all__ = [
    "get_welcome_content",
    "get_sovereign_doc",
    "get_universal_doc",
    "get_docusaurus_doc",
    "get_starlight_doc",
    "get_nextra_doc",
    "get_vitepress_doc",
    "get_about_doc",
]


def get_welcome_content(press_name: str, today_str: str) -> str:
    return f"""---
title: 欢迎探索 {press_name} 数字出版宇宙
date: {today_str}
tags: [welcome, guide, showcase, universe]
summary: 欢迎来到全新划定的出版品牌！本手稿由向导自动生成，串联了 6 大装帧模板特性指南，并构成 3D 知识星系的引力中心。
---

# 欢迎探索 {press_name} 数字出版宇宙
# Welcome to the {press_name} Publishing Universe

欢迎进入全新的出版品牌工作空间！这里是你的数字出版创世原点。
Welcome to your newly established sovereign imprint workspace! This is the origin of your digital publishing journey.

---

## 🌟 3D 知识星系与装帧模板特性概览
## 3D Knowledge Galaxy & Theme Showcases

为了帮助你全面了解系统支持的 6 种现代装帧模板，文库已自动为你生成了中英双语的模板特性演示手稿。通过下方双向链接（WikiLinks），它们在 3D 知识星系中与本创世手稿形成了引力互联拓扑：

* 👑 **Sovereign 官方旗舰装帧**：原生轻奢赛博毛玻璃视觉、免编译直出、实时中英双语无刷新切换。
  👉 详见特性手稿：[[demo-sovereign|Sovereign 官方旗舰模板特性指南]]

* 🌐 **Universal 通用自适应装帧**：现代极简单栏阅读流、移动端/桌面端全端自适应、暗黑明亮色盘智能适配。
  👉 详见特性手稿：[[demo-universal|Universal 通用自适应模板特性指南]]

* 🦖 **Docusaurus 知识库工程装帧**：Meta Facebook 经典技术文档套件、增强 Callouts 容器语法、多版本侧边栏。
  👉 详见特性手稿：[[demo-docusaurus|Docusaurus 知识库工程模板特性指南]]

* 🌟 **Astro Starlight 极星装帧**：基于 Astro 的极致轻量、0-JS 极速首屏、现代卡片式与徽标排版。
  👉 详见特性手稿：[[demo-starlight|Astro Starlight 极星模板特性指南]]

* ⚡ **Nextra 现代极简装帧**：Next.js 与 React MDX 深度混编、交互式手风琴折叠、秒级全文检索。
  👉 详见特性手稿：[[demo-nextra|Nextra 现代文档模板特性指南]]

* 🚀 **VitePress 疾速轻量装帧**：Vite 与 Vue 3 驱动、单页应用平滑跳转、代码行高亮与差异对比。
  👉 详见特性手稿：[[demo-vitepress|VitePress 疾速轻量模板特性指南]]

---

## 🚀 开启你的出版旅程
## Starting Your Publishing Journey

1. **直接编辑或增删文稿**：在你的原稿文库目录中新建 Markdown 手稿，系统将自动感知并同步更新 3D 知识星系。
2. **在治理中心切换模板**：前往控制台的【品牌装帧与模式】(Layout & Modes) 面板，可随时为当前出版品牌无缝切换上述任意装帧模板。
3. **一键分发同步**：在工作台点击“一键全量分发”，即可自动完成多语种翻译、资产打包并发布上线。
"""


def get_sovereign_doc(today_str: str) -> str:
    return f"""---
title: 官方旗舰装帧模板特性指南 (Sovereign Theme Showcase)
date: {today_str}
tags: [theme, sovereign, flagship, glassmorphism]
summary: 官方旗舰模板 (Sovereign) 特性演示：原生轻奢赛博毛玻璃、免编译直出架构与即时双语无刷新切换。
---

# 👑 官方旗舰装帧模板特性指南
# Sovereign Theme Showcase

Sovereign 是 Illacme Plenipes 的官方旗舰装帧主题，专为追求极致视觉品质与出版主权的创作者量身定制。
Sovereign is the official flagship theme of Illacme Plenipes, tailored for creators who seek ultimate visual sovereignty.

---

## ✨ 核心特性矩阵 (Core Features)

1. **免编译极速直出 (Zero-Build Instant Output)**:
   - 无需复杂的 Node.js 构建流水线，手稿与静态资源即改即看，出版毫秒级直达。
2. **赛博轻奢毛玻璃视觉 (Cyber Glassmorphism Aesthetics)**:
   - 深度采用高对比度暗色调、动态光晕与半透明磨砂质感，呈现专业高档的视觉工业品味。
3. **即时无刷新中英双语切换 (Instant Bilingual Locale Switcher)**:
   - 语言切换无需重新加载整页，段落级自动平滑对齐，双语阅读丝滑流畅。
4. **原生高维知识星系融合 (Native Galaxy Integration)**:
   - 与 3D 知识星系引擎底层原生互通，每一篇手稿都是宇宙中的一颗璀璨恒星。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-universal|通用自适应模板]] · [[demo-docusaurus|Docusaurus 工程模板]]
"""


def get_universal_doc(today_str: str) -> str:
    return f"""---
title: 通用自适应装帧模板特性指南 (Universal Theme Showcase)
date: {today_str}
tags: [theme, universal, responsive, minimal]
summary: 通用自适应模板 (Universal) 特性演示：现代极简单栏阅读流、全端自适应响应与暗黑模式深度支持。
---

# 🌐 通用自适应装帧模板特性指南
# Universal Theme Showcase

Universal 是一个极简、干净且优雅的通用现代装帧主题，专注于纯粹的文字阅读与全终端适配。
Universal is a clean and elegant universal theme focused on distraction-free reading and multi-device adaptability.

---

## ✨ 核心特性矩阵 (Core Features)

1. **全端自适应响应式布局 (Fully Responsive Across All Devices)**:
   - 完美适配手机、平板、超宽屏桌面端，提供无懈可击的排版栅格与阅读视距。
2. **沉浸式单栏阅读流 (Immersive Single-Column Reading Flow)**:
   - 剔除冗余干扰元素，让读者的注意力完全聚焦于创作者的思想与文字内容。
3. **明暗色盘智能适配 (Adaptive Light & Dark Modes)**:
   - 自动跟随操作系统或读者偏好无缝切换暗黑与浅色模式，有效保护视力。
4. **社交网络 OpenGraph 深度优化**:
   - 自动生成社交网络分享卡片、Twitter Card 与微信分享摘要。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-sovereign|官方旗舰模板]] · [[demo-starlight|Astro 极星模板]]
"""


def get_docusaurus_doc(today_str: str) -> str:
    return f"""---
title: Docusaurus 知识库工程模板特性指南 (Docusaurus Theme Showcase)
date: {today_str}
tags: [theme, docusaurus, engineering, callouts]
summary: Docusaurus 知识库工程模板特性演示：基于 Meta 经典开源技术文档标准，展示丰富的 Callouts/Admonitions 容器。
---

# 🦖 Docusaurus 知识库工程模板特性指南
# Docusaurus Theme Showcase

Docusaurus 基于 Meta (Facebook) 备受赞誉的开源文档框架标准，专为大型工程文档、知识库与技术规范打造。
Docusaurus is built upon Meta's acclaimed open-source documentation framework standard, designed for engineering knowledge bases.

---

## ✨ 提示块与容器语法演示 (Admonitions Showcase)

Docusaurus 具备强大的 Admonitions 提示块解析能力，能让你的技术文档结构分明、重点突出：

:::note 💡 核心说明 (Note)
这是一个标准 Note 说明块，适用于常规补充说明与背景知识展开。
This is a standard note callout for background context.
:::

:::tip 🎯 实用技巧 (Tip)
这是一个 Tip 提示块，适合分享最佳实践、快捷键或高阶操作技巧。
This is a tip callout for sharing best practices and shortcuts.
:::

:::warning ⚠️ 注意事项 (Warning)
这是一个 Warning 警示块，用于提示需要格外注意的配置陷阱或边界条件。
This is a warning callout for critical configuration caveats.
:::

:::danger 🛑 危险操作 (Danger)
这是一个 Danger 警示块，用于警告不可逆的物理删除或重大破坏性行为。
This is a danger callout warning against irreversible actions.
:::

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-nextra|Nextra 现代文档模板]] · [[demo-vitepress|VitePress 模板]]
"""


def get_about_doc(today_str: str) -> str:
    return f"""---
title: 关于本出版品牌 (About This Imprint)
date: {today_str}
tags: [about, imprint]
summary: 本出版品牌的独立主权说明与创作者介绍。
---

# 📖 关于本出版品牌
# About This Imprint

本出版品牌由 Illacme Plenipes 主权出版系统驱动，享有独立的品牌标识、多语种翻译治理策略与专属 3D 知识星系。
This imprint is powered by the Illacme Plenipes sovereign publishing system, with independent branding and a dedicated knowledge galaxy.

* 探索装帧模板特性指南：[[welcome-to-illacme|返回数字出版宇宙中心]]
"""
