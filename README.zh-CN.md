# 🌌 Illacme-plenipes: 全球私人出版社 (Global Private Press)

> **您的全球出版发行中心。让灵感在起草室点燃，在文库中沉淀，通过矩阵响彻全球。**

![品牌视觉 Banner](./illacme_imprinting_hero_1777097616124.png)

[![Version](https://img.shields.io/badge/version-v50.3--Industrial--Sovereignty-cyan.svg)](https://github.com/Illacme/illacme-plenipes)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm--Noncommercial--1.0.0-orange.svg)](https://polyformproject.org/licenses/noncommercial/1.0.0/)

[🇨🇳 简体中文](./README.zh-CN.md) | 🇬🇧 English

---

### 🚀 什么是 全球私人出版社 (Plenipes)？

**Illacme Plenipes** 是由 **Illacme** 出品的工业级 **Markdown 一站式内容出版流水线**。对外主产品名称为 **“全球私人出版社 (Global Private Press)”**。

它旨在帮助独立创作者、出海团队与数字出版机构，将本地的原稿文库（Markdown）全自动转化为全球化出版物：
* 🌍 **多语言翻译**：基于 AI 大模型上下文感知的高质量语义分片与段落级自愈翻译
* 🌐 **静态网站发布**：多主题（Docusaurus, VitePress, Starlight 等）一键装帧与全网托管
* 🛰️ **社媒矩阵分发**：30+ 社交渠道与技术博客矩阵（Dev.to, Hashnode, Medium, 微信公众号等）一键同步
* 📚 **电子书与多端导出**：面向商业出版的多格式（PDF / EPUB 等）排版导出

* 🌐 官网主站：[illacme.com](https://illacme.com)
* 📖 产品主页：[plenipes.illacme.com](https://plenipes.illacme.com)
* 💻 项目仓库：[illacme/illacme-plenipes](https://github.com/illacme/illacme-plenipes)

---

### ✨ 核心价值 (Core Values)

#### 1. 🛡️ 品牌主权 (Imprint Sovereignty)
每一个出版项目都是一个独立的 **出版品牌 (Imprint)**。拥有物理隔离的配置、主题与渠道。在您的出版矩阵中，您可以自由扩张，每一寸数字疆域都由您绝对主宰。

#### 2. 🌍 灵感即发布 (Ideation to Distribution)
内置 **创作中心 (Scriptorium)**。AI 不仅仅是翻译工具，更是您的创意学徒。从起草原稿到全球多语种同步发行，全链路自动化，让您的思想跨越语言与平台的疆界。

#### 3. ⚙️ 算力装帧 (Compute & Binding)
强大的 **算力中心 (Compute)** 负责将 **原稿文库 (Manuscript Vault)** 中的内容进行深度加工。配合多种 **装帧主题**，自动完成 SSG 渲染，确保每一本“数字出版物”都具备商业级的视觉品质。

#### 4. 🛰️ 发行矩阵 (The Matrix)
通过高度解耦的 **发行调度 (The Dispatch)**，您的内容将瞬间同步至全球各类 **发行渠道 (The Channels)**。无论是 GitHub、Netlify 还是社交媒体阵列，出版引擎确保全球共振。

---

### 🛠️ 快速启动指南 (Quick Start)

为不同操作系统提供开箱即用的**一键快速启动器**，自动探测并激活虚拟环境、检查依赖并在启动后自动唤醒治理中心控制台：

*   **🍎 macOS 用户**：在 Finder 中直接双击 **`start.command`**（免开终端，浏览器秒级自动弹出）。
*   **🪟 Windows 用户**：直接双击 **`start.bat`**（或在 PowerShell 中运行 `.\start.ps1`）。
*   **🐧 Linux / 服务器用户**：在终端直接运行：
    ```bash
    ./start.sh
    ```
*   **🐳 Docker 容器化一键部署**：
    ```bash
    docker compose up -d
    ```

---

#### 💻 高级开发者命令行模式 (CLI)
```bash
# 1. 准备底座
git clone https://github.com/Illacme/illacme-plenipes.git
pip install -r requirements.txt

# 2. 唤醒治理中心 (交互式控制台)
python3 plenipes.py 

# 3. 启动算力流水线 (全自动出版与发行)
python3 plenipes.py --sync --force

# 4. 实时全时守护 (毫秒级文件监控与即时同步)
python3 plenipes.py --watch
```

---

### 📂 探索架构 (Explore Architecture)

*   **[Manuscript Vault](./core/)**：支撑海量文稿的高性能调度内核。
*   **[The Matrix](./core/adapters/)**：支持 Cloudflare, DeepSeek, Webhook 等全渠道发行适配。
*   **[Governance Dashboard](./dashboard/)**：全息治理中心看板，掌控您的出版品牌。

---

### 📜 治理协议与商业许可 / License & Legal

- **开源非商业许可**：开源版本采用 [PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) 协议，供个人创作与学术研究等非商业用途免费使用。
- **商业授权 (Commercial EULA)**：任何用于商业运营、付费分发或企业部署的场景，须取得版权所有者书面授权，详见 **[商业授权说明](./COMMERCIAL_LICENSE.md)** 与 **[最终用户许可协议 (EULA)](./docs/legal/EULA.md)**（联系：wqbyc@msn.com）。
- **数据主权保障**：恪守“本地为真源、文库不上传”承诺，详见 **[数据主权协议](./docs/legal/DATA_SOVEREIGNTY.md)**。
- **免责声明与隐私政策**：详见 **[第三方凭据与 AI 内容免责声明](./docs/legal/THIRD_PARTY_DISCLAIMER.md)** 与 **[隐私与遥测声明](./docs/legal/PRIVACY_POLICY.md)**。

🛡️ *Illacme-plenipes - 让主权照耀创作，让品牌横跨全球。*