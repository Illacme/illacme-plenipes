# 🌉 Illacme-plenipes (v34.5 Flagship Edition)

🇨🇳 简体中文 | [🇬🇧 English](./README.md)

![Version](https://img.shields.io/badge/version-v34.5--flagship-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Architecture](https://img.shields.io/badge/architecture-Industrial%20Grade%20/%20Anti--Pruning-success.svg)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

**Illacme-plenipes** 是一款工业级的 Markdown 知识同步引擎，专为对“代码完整性”和“创作可追溯性”有极致要求的开发者设计。它不仅能实现笔记到 SSG 矩阵的毫秒级同步，更通过内置的**审计时间轴 (Audit Timeline)** 和 **影子自愈引擎 (Shadow Recovery)** 确保每一行笔记的流转都有迹可循。

其命名灵感来源于地球上腿部数量最多的生物 *Illacme plenipes*。正如其名，本引擎搭载了 **OS 级防竞态锁**、**异步脏写状态机** 和 **Token 级 AI 切片引擎**，为您的数字花园提供重型动力。

---

## 🚀 旗舰版核心特性 (Flagship Features)

### 1. 📝 创作审计时间轴 (Industrial Audit Timeline)
这是 V34.5 引入的重量级特性。系统会实时监控本地文件系统的每一个“震动”，并将 `保存 -> 触发 -> 同步 -> 成功/失败` 的全链路过程记录在 `timeline.md` 中，让您的创作轨迹清晰可见。

### 2. 🛡️ 代码完整性防线 (Anti-Pruning Governance)
内置 `.antigravityrules` 规则固化引擎，严禁 AI 在自动化开发过程中擅自精简代码、删除注释或篡改防御性逻辑。保持“工业级繁荣”而非“极简主义”。

### 3. 🩹 影子资产自愈 (Shadow-Asset Recovery)
创新性引入 `.illacme-shadow` 缓存。在前端物理产物丢失的情况下，引擎能瞬间从影子资产中恢复，无需再次消耗 AI Token 执行推理，实现真正的零成本灾备。

### 4. 🧠 高精度 AI 切片调度 (Precision LLM Orchestration)
基于 `tiktoken` 与 AST (抽象语法树) 的语义切片算法。支持对长达万字的 MDX 文档进行智能拆分翻译，严格保护 Markdown 结构与代码块不被 AI 破坏。

---

## 📖 文档中心 (Documentation Hub)

为了提供更专业的开源体验，本项目建立了完整的文档矩阵：

*   **[技术规格书 (SPECIFICATION)](./docs/SPECIFICATION.zh-CN.md)**：深入了解 Pipeline 管线、适配器模式与底层存储架构。
*   **[用户参考手册 (REFERENCE)](./docs/REFERENCE.zh-CN.md)**：全量 `config.yaml` 参数字典及 CLI 命令行详解。
*   **[操作指南 (MANUAL)](./docs/MANUAL.zh-CN.md)**：分步式 How-to 教程，涵盖环境配置、监听模式及故障排除。
*   **[贡献指南 (CONTRIBUTING)](./CONTRIBUTING.zh-CN.md)**：如何为本项目提交代码或反馈 Bug。

---

## ⚙️ 安装与快速开始 (Quick Start)

```bash
# 1. 克隆并安装依赖
git clone https://github.com/Illacme/illacme-plenipes.git
pip install -r requirements.txt

# 2. 初始化配置
python3 plenipes.py  # 首次运行自动生成 config.yaml
# 请在 config.yaml 中填入您的 API Key 及同步路径

# 3. 启动全量同步
python3 plenipes.py --sync

# 4. 进入实时监听模式 (推荐)
python3 plenipes.py --watch
```

---

## 📜 开源协议 / License

本项目采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh) 协议。仅限个人及非商业性科研场景使用。如需商业授权，请通过 Issue 与作者联系。

---

## 🔌 NPM 终端集成 (NPM Integration)

建议将 **Illacme-plenipes** 的守护进程直接挂载到你的前端工程中。在前端项目 `package.json` 中注入以下脚本：

```JSON
"scripts": {
  "plenipes:sync": "cd ../.. && python plenipes.py --sync",
  "plenipes:watch": "cd ../.. && python plenipes.py --watch",
  "dev:i": "npm run plenipes:sync && concurrently -k -p \"[{name}]\" -n \"Illacme,Astro\" -c \"blue.bold,green.bold\" \"npm run plenipes:watch\" \"npm run dev\""
}
```

_注：需要提前安装并发执行器：`npm install -g concurrently`_

---

## 🛠 高阶配置指南 (Advanced Tuning)

| **参数项**              | **所属域**       | **场景调优建议**                                      |
| -------------------- | ------------- | ----------------------------------------------- |
| `max_workers`        | `system`      | 云端 API 建议 `20-50`；本地模型(无排队)必须设为 `1`；图片密集建议 `8`。 |
| `auto_save_interval` | `system`      | 默认 `2.0` 秒。极高频修改场景可上调至 `5.0`。                   |
| `temperature`        | `translation` | 翻译强绑定 `0.1`；发散任务可上调至 `0.6-0.8`。                 |
| `max_chunk_size`     | `translation` | 单位：Token。本地小模型建议 `2000`；顶级 API 可拉满至 `8000`。     |

---

### 🤫 算力节流阀：静默微调模式 (Silent Edit Valve)

Illacme-plenipes 底层搭载了基于 MD5 状态机的增量编译系统。默认情况下，任何微小的改动（哪怕是一个标点符号）都会触发全量的 AI 翻译与 SEO 提取。

为了在**“修正错别字”**或**“调整本地排版”**时避免对大模型算力（Tokens）的无意义消耗，引擎提供了文件级的“静默锁”：

在你的 Markdown 文件的 YAML 头部（Frontmatter）加上 `ai_sync: false`：

```yaml
---
title: 我的文章标题
ai_sync: false
---
```

## 📜 开源协议 / License

本项目代码与架构采用 [CC BY-NC 4.0 (知识共享-署名-非商业性使用 4.0 国际)](https://creativecommons.org/licenses/by-nc/4.0/deed.zh) 协议进行许可。

**你可以：**
- 自由地下载、克隆、修改本项目代码。
- 将本项目用于搭建个人博客、知识库、学术研究等非营利性场景。

**你不可：**
- 将本项目（包含引擎逻辑、主题架构）用于任何形式的**商业化盈利项目**（包括但不限于：作为付费 SaaS 服务售卖、接入带有强制商业广告的平台等）。

> 如需商业使用或定制开发授权，请通过 Issue 或邮件与作者取得联系。