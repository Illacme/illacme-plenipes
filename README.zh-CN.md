# 🌉 Illacme-plenipes (v5.4.1 Sovereign Edition)

🇨🇳 简体中文 | [🇬🇧 English](./README.md)

![Version](https://img.shields.io/badge/version-v5.4.1--sovereign-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Governance](https://img.shields.io/badge/audit-60/60%20Pass-success.svg)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

**Illacme-plenipes** 是一款面向未来的工业级 Markdown 知识治理与 AI 翻译引擎。它不仅能实现海量笔记的跨框架同步，更通过首创的 **“五大星系审计 (5-Galaxy Audit)”** 和 **“逻辑主权隔离 (Logic Sovereignty)”** 架构，确保项目在高度自动化演化的同时，依然拥有固若金汤的物理稳定性与代码主权。

---

## 🚀 核心主权特性 (Sovereign Features)

### 1. 🛡️ 五大星系治理审计 (5-Galaxy Audit)
这是 v5.4 引入的终极治理方案。系统将审计逻辑划分为：
- **物理拓扑星系**：扫描包结构连通性与导入链。
- **环境星系**：监控 Git 卫生与全局知识纯净度。
- **代码质量星系**：强制执行 300 行复杂度红线与主权隔离校验。
- **动态仿真星系**：主入口点火冒烟测试与影子沙盒仿真。
- **历史归档星系**：三相文档 (Plan/Task/Walkthrough) 深度校验。

### 2. 🧩 逻辑主权隔离架构 (Logic Sovereignty)
采用“大脑与肢体”分离设计。核心业务逻辑（Slug生成、SEO提取、Prompt组装）被物理锁死在基类中，适配器（OpenAI/Gemini/DeepSeek）仅负责原子级的协议通信。严禁子类“越权篡改”核心逻辑。

### 3. 🩹 影子资产自愈 (Shadow-Asset Recovery)
创新性引入 `.illacme-shadow` 缓存。在前端物理产物丢失的情况下，引擎能瞬间从影子资产中恢复，无需再次消耗 AI Token。

### 4. 🧠 栈式组件静态化 (Stack-based Staticization)
针对复杂的嵌套组件（如 Tabs 套 Tabs），静态化引擎采用非正则的物理行扫描算法，通过栈（Stack）维护平衡匹配，确保复杂排版在降维过程中不丢失层级。

---

## 📖 文档中心 (Documentation Hub)

*   **[技术规格书 (SPECIFICATION)](./docs/SPECIFICATION.zh-CN.md)**：深入了解五大星系审计与主权隔离架构。
*   **[用户参考手册 (REFERENCE)](./docs/REFERENCE.zh-CN.md)**：全量 `config.yaml` 参数字典及治理红线配置。
*   **[操作指南 (MANUAL)](./docs/MANUAL.zh-CN.md)**：分步式教程，涵盖环境配置、历史归档及自审流程。

---

## ⚙️ 快速开始 (Quick Start)

```bash
# 1. 克隆并安装
git clone https://github.com/Illacme/illacme-plenipes.git
pip install -r requirements.txt

# 2. 初始化配置 (自动生成 config.yaml)
python3 plenipes.py 

# 3. 运行治理自审 (确保 60/60 通过)
python3 tests/governance_audit.py

# 4. 启动实时监听
python3 plenipes.py --watch
```

---

## 📜 开源协议 / License
本项目采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh) 协议。仅限个人及非商业性科研场景使用。
🛡️ *Illacme-plenipes - 物理主权固若金汤，治理光辉照耀迭代。*