# 🏛️ Illacme-plenipes: 全球私人出版社 (Global Private Press)

> **专为主权创作者打造的工业级数字出版发行工作台。**  
> 一套本土 Markdown 原稿 ➔ 多语言智能翻译 ➔ 商业级装帧排版 ➔ 全网静态托管与 30+ 社交媒体矩阵一键同步。

![品牌视觉 Banner](./docs/assets/hero_banner.png)

[![Version](https://img.shields.io/badge/version-v50.3--Industrial--Sovereignty-cyan.svg)](https://github.com/Illacme/illacme-plenipes)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm--Noncommercial--1.0.0-orange.svg)](https://polyformproject.org/licenses/noncommercial/1.0.0/)

[🇨🇳 简体中文](./README.zh-CN.md) | [🇬🇧 English](./README.md) | [📖 场景实战手册](./docs/cookbook/) | [📚 功能速查手册](./docs/manual/)

---

### 💡 为什么选择 Illacme Plenipes？

作为独立创作者、出海团队或技术博主，你是否面临以下痛点：
1. **多平台重复搬运**：每次写完文章，要在微信公众号、知乎、Dev.to、Medium 等平台挨个排版粘贴、调整图片防盗链；
2. **多语言维护割裂**：出海推广需要双语甚至多语种，但手动维护翻译文档容易发生语义漂移，且难以同步更新；
3. **技术栈繁杂门槛高**：想搭建属于自己的独立静态网站（如 Docusaurus、Starlight、VitePress），却要面对复杂的 Node.js 构建配置与云部署 CLI。

**Illacme Plenipes** 让创作彻底回归写作本身：
* 🌍 **本土创作，全球通达**：只维护一份本地 Markdown 笔记（完美兼容 Obsidian / Logseq 语法），AI 自动完成高质量分段翻译与段落级自愈校对。
* 🌐 **全网静态网站托管**：支持 10 大托管驱动（GitHub Pages、Vercel、Netlify、Cloudflare Pages、SFTP 等），一键构建多语言官方主站与备用镜像。
* 🛰️ **30+ 社媒矩阵全域同步**：微信公众号、知乎、掘金、Dev.to、Hashnode、Medium、Ghost、Substack 等一键直达，原生支持图床转存与防盗链治理。
* 📚 **出版级装帧与电子书导出**：自动排版生成带深层目录的双语对照版 **DOCX、印刷级 PDF、EPUB 电子书**，数学公式（OMML）与代码高亮原生渲染。
* 🛡️ **数据与凭据绝对自主**：遵循主权物理隔离架构，文库资产 100% 留存本地，账本独立，支持本地离线大模型（Ollama / LM Studio）。

---

### 🚀 极简快速点火 (Quick Start)

针对不同操作系统提供开箱即用的**双击启动器**（自动探测虚拟环境并在启动后自动唤起工作台）：

*   **🍎 macOS 用户**：在 Finder 中直接双击根目录 **`start.command`**（免敲终端，浏览器秒级自动弹出）。
*   **🪟 Windows 用户**：直接双击根目录 **`start.bat`**（或在 PowerShell 中运行 `.\start.ps1`）。
*   **🐧 Linux / 服务器用户**：终端运行：
    ```bash
    ./start.sh
    ```
*   **🐳 Docker 容器化部署**：
    ```bash
    docker compose up -d
    ```

> 💡 **启动后访问**：工作台控制台服务监听于 `http://127.0.0.1:43212`，开箱即用。

> ⌨️ **极客高频快捷键**：
> * `Cmd+K` / `Cmd+P`：唤起全功能命令面板（出版领航仪）；
> * `]`：唤起 / 收起 Sovereign Copilot 自主编排助手；
> * `[`：展开 / 收起左侧系统导航栏。

<details>
<summary><b>📝 点击展开：最简 Markdown 原稿规范示例（完美兼容 Obsidian）</b></summary>

```markdown
---
title: "我的第一篇主权出版物"
description: "本文介绍如何通过 Illacme Plenipes 实现全域多语言出版与同步分发。"
tags: ["Publishing", "Markdown", "OpenSource"]
categories: ["Tech"]
draft: false
cover: "assets/covers/hero.png" # 可留空，由设计中心自动生成
---

# 欢迎来到主权出版时代

你可以自由使用标准 Markdown、LaTeX 数学公式以及 Obsidian 双链语法：
* 双链引用：参见另一篇笔记 [[architecture-overview]]。
* 独立数学公式：
$$E = mc^2$$

系统在同步发布时会自动解析并清洗此类语法，并在目标平台原生渲染！
```
</details>

---

### 🎯 创作者 3 步核心旅程

```mermaid
graph LR
    A["1️⃣ 关联文库<br/>（指向本地 Markdown 目录）"] --> B["2️⃣ 装帧与翻译<br/>（选择主题、设定目标语种）"]
    B --> C["3️⃣ 一键分发<br/>（推送到官网与社交矩阵）"]
```

1. **第一步：关联原稿文库**  
   在治理中心填写您的本地 Markdown 文库物理路径（`vault_root`），系统自动解析目录树、关联图谱与草稿态。
2. **第二步：配置装帧主题与 AI 算力**  
   选择喜欢的母本主题（如 Docusaurus、Starlight、VitePress），填入 AI 密钥（支持 OpenAI、Gemini、DeepSeek、Claude 或本地 Ollama）。
3. **第三步：一键全域分发**  
   在文库抽屉中点击「网页托管发布」或「社交媒体分发」，实时监控部署流水与真实线上直达链接。

---

### 🧩 核心功能矩阵一览

| 模块中心 | 核心能力 | 实战指引 |
| :--- | :--- | :--- |
| **🌌 知识星谱 (Overview)** | 三维力导向知识网络拓扑、UnrealBloom 辉光、多维过滤器与交付物大盘 | [星谱导航指引](./docs/manual/01_overview_galaxy.md) |
| **📂 原稿文库 (Vault)** | Markdown / WYSIWYG 双模编辑、Frontmatter 元数据提纯、资产本地化 | [文库管理指南](./docs/manual/02_vault_management.md) |
| **📖 装帧书架 (Bindery)** | 双语对照排版、DOCX (OMML 公式)/PDF/EPUB 一键导出、动态二维码诊断 | [印刷装帧实战](./docs/manual/03_bindery_publishing.md) |
| **🚀 发布中心 (Dispatch)** | 全域发布任务大厅、SQLite 部署账本、单篇与整站物理推流、公网链接回填 | [全域发布实战](./docs/manual/04_dispatch_and_hosting.md) |
| **⚙️ 出版治理 (Governance)** | 物理品牌隔离 (Imprint)、6 大 SSG 母本热插拔、翻译规则块与校对工作台 | [治理与校对指南](./docs/manual/05_governance_and_review.md) |
| **🧠 算力底座 (Compute)** | 25+ AI 提供商接入、主备智能降级、Sovereign Copilot 自主协同与 HITL 审查 | [算力配置指南](./docs/manual/06_compute_and_copilot.md) |
| **🎨 设计中心 (Design)** | AI 生图引擎 (DALL-E/Imagen/Midjourney)、本地 OG 社交卡片、封面批量装帧 | [封面设计指引](./docs/manual/07_design_studio.md) |
| **🧩 插件生态 (Plugins)** | 10 大托管平台 + 20+ 社交渠道 + 14 大图床网络，中央凭据状态 SSOT 判决 | [插件生态矩阵](./docs/manual/08_plugins_ecosystem.md) |

---

### 💻 开发者命令行模式 (CLI)

```bash
# 1. 克隆与依赖安装
git clone https://github.com/Illacme/illacme-plenipes.git
cd illacme-plenipes
pip install -r requirements.txt

# 2. 唤醒交互式治理控制台
python3 plenipes.py 

# 3. 命令行执行全量同步与构建
python3 plenipes.py --sync --force

# 4. 开启文件变更毫秒级守护监控
python3 plenipes.py --watch
```

---

### 📜 治理协议与商业许可 (Licensing & Governance)

*   **开源非商业许可**：开源版本采用 [PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) 协议，供个人创作与学术研究等非商业用途免费使用。
*   **商业授权 (Commercial EULA)**：任何用于商业运营、团队协同分发或企业部署的场景，须取得版权所有者书面授权，详见 **[商业授权说明](./COMMERCIAL_LICENSE.md)** 与 **[商业最终用户许可协议 (EULA)](./docs/legal/EULA.md)**（商务联系：`wqbyc@msn.com`）。
*   **数据主权承诺**：恪守“本地为真源、文库不上传”承诺，详见 **[数据主权协议](./docs/legal/DATA_SOVEREIGNTY.md)**。
*   **免责与第三方致谢**：详见 **[第三方凭据免责声明](./docs/legal/THIRD_PARTY_DISCLAIMER.md)** 与 **[第三方开源致谢](./docs/legal/THIRD_PARTY_NOTICES.md)**。

---

*Powered by **Illacme Plenipes** | 让主权照耀创作，让品牌横跨全球。*