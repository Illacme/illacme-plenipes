#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Imprint Showcase Content (Part 2)
职责：提供 Astro Starlight、Nextra、VitePress 模板特性演示手稿文本。
"""


def get_starlight_doc(today_str: str) -> str:
    return f"""---
title: Astro Starlight 极星模板特性指南 (Starlight Theme Showcase)
date: {today_str}
tags: [theme, starlight, astro, fast]
summary: Astro Starlight 模板特性演示：基于 Astro 驱动的高性能文档引擎、0-JS 极速首屏与现代化卡片组件。
---

# 🌟 Astro Starlight 极星模板特性指南
# Astro Starlight Theme Showcase

Starlight 是由 Astro 官方打造的极致性能文档框架，以惊人的加载速度、精美现代的排版和卓越的无障碍体验著称。
Starlight is Astro's official documentation framework, celebrated for blazingly fast load times and modern aesthetic typography.

---

## ✨ 核心特性矩阵 (Core Features)

1. **极致轻量 0-JS 首屏 (Zero-JS by Default)**:
   - 极致削减客户端 JavaScript 载荷，核心文档内容毫秒级秒开，打造顶级 Web Vitals 评分。
2. **现代卡片式排版与徽标 (Card Grid & Badges)**:
   - 原生支持卡片阵列排版，适合构建模块导航、特性矩阵与产品指南。
3. **开箱即用的多语种架构 (Built-in i18n Architecture)**:
   - 与 Illacme Plenipes 的多语种主权分发管道深度契合，原生支持全站语种自动对齐。
4. **精细化的暗色调支持 (Curated Dark Mode)**:
   - 经由视觉设计师精心校准的对比度与配色，长时间阅读不刺眼、不疲劳。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-sovereign|官方旗舰模板]] · [[demo-universal|通用自适应模板]]
"""


def get_nextra_doc(today_str: str) -> str:
    return f"""---
title: Nextra 现代文档模板特性指南 (Nextra Theme Showcase)
date: {today_str}
tags: [theme, nextra, nextjs, react]
summary: Nextra 现代文档模板特性演示：基于 Next.js & React MDX，灵活组件混编与毫秒级折叠侧边栏。
---

# ⚡ Nextra 现代文档模板特性指南
# Nextra Theme Showcase

Nextra 是基于 Next.js 与 React MDX 驱动的现代知识库引擎，兼具极简外观与极高扩展性。
Nextra is a modern knowledge base engine powered by Next.js and MDX, combining minimalist aesthetics with infinite flexibility.

---

## ✨ 核心特性矩阵 (Core Features)

1. **React MDX 组件无缝混编 (MDX Component Power)**:
   - 可以在 Markdown 手稿中灵活嵌入丰富的交互式 UI 组件、演示 Demo 与图表。
2. **交互式可折叠详情 (Interactive Collapsible Details)**:
   - 原生支持 HTML5 `<details>` 与 `<summary>` 手风琴折叠面板，整洁收纳复杂内容。
3. **秒级全文检索与键盘导航 (Instant Full-Text Search)**:
   - 原生集成 FlexSearch 极速离线分词引擎，按下 `Cmd + K` 即可瞬间定位内容。
4. **自适应嵌套目录树 (Recursive Nested Sidebar)**:
   - 自动解析文件目录结构，生成可自由折叠与展开的多级导航侧边栏。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-docusaurus|Docusaurus 模板]] · [[demo-vitepress|VitePress 模板]]
"""


def get_vitepress_doc(today_str: str) -> str:
    return f"""---
title: VitePress 疾速轻量模板特性指南 (VitePress Theme Showcase)
date: {today_str}
tags: [theme, vitepress, vue, vite]
summary: VitePress 疾速轻量模板特性演示：基于 Vite & Vue 3 驱动的现代静态文档框架，展示代码高亮与行聚焦。
---

# 🚀 VitePress 疾速轻量模板特性指南
# VitePress Theme Showcase

VitePress 是由 Vue 作者尤雨溪打造的下一代静态站点生成器，基于 Vite 的极速构建体验与 Vue 3 的轻量运行时。
VitePress is the next-generation static site generator by Vue creator Evan You, powered by Vite and Vue 3.

---

## ✨ 代码高亮与行聚焦演示 (Code Highlighting & Focus)

VitePress 提供业界一流的代码块渲染能力，支持语言标识、代码行高亮与差异对比：

```javascript
// VitePress 核心启动配置演示
import {{ defineConfig }} from 'vitepress';

export default defineConfig({{
  title: "Illacme Plenipes",
  description: "主权数字出版平台", // [!code focus] 高亮重点行
  themeConfig: {{
    nav: [{{ text: "指南", link: "/docs/demo-vitepress" }}]
  }}
}});
```

---

## ✨ 核心特性矩阵 (Core Features)

1. **Vite 极速热更新与编译 (Blazing Fast HMR)**:
   - 无论是单篇修改还是整站发布，均能享受秒级冷启动与毫秒级热更新。
2. **轻量 SPA 架构 (Lightweight SPA Navigation)**:
   - 首屏加载完成后，后续页面跳转均为纯前端无感知切换，零网络往返延迟。
3. **原生 Markdown 扩展 (Markdown Extensions)**:
   - 深度支持自定义容器、代码行高亮与 GFM 任务列表。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-starlight|Astro 极星模板]] · [[demo-nextra|Nextra 现代模板]]
"""
