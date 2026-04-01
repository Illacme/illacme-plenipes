# 🌉 Illacme-plenipes (v13.0)

🇨🇳 简体中文 | [🇬🇧 English](./README.md)

![Version](https://img.shields.io/badge/version-v13.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Architecture](https://img.shields.io/badge/architecture-Cloud%20Native%20%2F%20High%20Concurrency-success.svg)
[![Framework Agnostic](https://img.shields.io/badge/SSG-Agnostic-success.svg)](#)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Illacme-plenipes** 是一款工业级的 Markdown 同步引擎。它不仅能将本地知识库以高并发形态秒级推送至主流前端框架 (SSG)，更内置了底层 AI 切片调度，实现从单语种笔记到 N 维多语言矩阵的全自动化蜕变。

其命名灵感来源于地球上腿部数量最多的生物 *Illacme plenipes*。正如其名，本引擎搭载了 **OS 级防竞态锁**、**异步脏写状态机** 和 **Token 级 AI 切片引擎**，像一台拥有 750 条腿的重型“V8 引擎”，旨在彻底榨干多核 CPU 与大模型上下文窗口的每一滴算力，实现海量笔记的毫秒级增量编译。

兼容生态：`Astro (Starlight)` | `VitePress` | `Docusaurus` | `Hugo` | `Hexo`

---

## 🚀 核心架构与技术特性 (Core Architecture)

### 1. 🛡️ 进程级单例防线 (OS-Level Singleton Mutex)
基于 `socket.bind()` 在操作系统底层抢占高位端口（默认 `43210`），物理免疫双开灾难。进程一旦意外死亡，内核瞬间释放端口，完美保护底层元数据不受并发污染。

### 2. ⚡️ 异步状态机与 Write-Behind Cache (原子级落盘)
- **O(1) 脏写标记**：核心管线只需标记 `self._dirty = True`，瞬间释放锁，吞吐量极高。
- **后台心跳守护**：独立的 Flusher 线程根据配置的心跳间隔将快照无感静默落盘。
- **防撕裂机制**：基于 `os.replace` 的事务级写入，即便写入瞬间遭遇物理断电，也能保证 MD5 指纹库 100% 完整。

### 3. 🧠 Token 级长文切片引擎 (High-Precision LLM Orchestration)
全面接入 OpenAI 工业级 `tiktoken` 库，精准压榨算力。
- **精准测算**：完美适配 DeepSeek、Qwen、OpenAI 以及 **OpenClaw (小龙虾)** 等模型。
- **防 OOM 截断**：长文自动根据 `max_chunk_size` (Token 级) 切分为并发子任务，彻底抹平耗时瓶颈。

### 4. 🧵 全域高并发线程池 (Thread Pool Dispatcher)
- **图片压缩管线**：挂载文件级细粒度并发锁，防止多线程处理同一张 8K 巨图击穿显存，支持 WebP 极速转码。
- **多语言矩阵**：目标语言阵列全部并发执行，翻译耗时由最慢的一个语种决定，而非线性叠加。

### 5. 🕷️ 动态 AST 降维与防死循环嵌套
- 动态深度受控（`max_depth`）的双链物理展开。
- 内置双重检查锁定（DCL）内存级缓存，阻断重复磁盘 I/O 踩踏。
- 零侵入将 Markdown 专有语法自适应降维至目标前端专属组件。

---

## ⚙️ 安装与快速开始 (Installation & Quick Start)

### 1. 安装核心级依赖

```bash
# 图像处理、YAML解析、网络层与看门狗
pip install Pillow PyYAML requests watchdog 

# [强烈推荐] 安装 Token 级高精度切片底座
pip install tiktoken
```

2. 配置总控总线
将项目根目录下的 config.yaml.example 复制为 config.yaml。
所有的底层魔法数字（并发数、推理温度、心跳间隔、SEO 排版权重）均已 100% 上浮至该配置文件，实现零代码侵入调度。

```YAML
# 核心路径配置示例
vault_root: "/Users/YourName/Documents/Obsidian-Vault" 
frontend_dir: "../my-astro-site"
```

(⚠️ 安全警告：请勿将包含真实 API Key 的 `config.yaml` 提交至公开仓库，务必加入 `.gitignore`！)

3. 驱动引擎 (CLI 调度)
Illacme-plenipes 提供了四种工业级运行模式：

```Bash
# 1. 单次增量同步 (Sync Mode) - 结合 MD5 校验，仅编译变动文件
python core/plenipes.py --sync

# 2. 守护进程模式 (Daemon Watch Mode) - 毫秒级热更监听
python core/plenipes.py --watch

# 3. 安全演练模式 (Dry-Run Mode) - 仅打印流转测绘日志，阻断物理写盘和 API 扣费
python core/plenipes.py --sync --dry-run

# 4. 强制重构模式 (Force Mode) - 撕碎 MD5 状态指纹，强拉全库执行覆盖重编
python core/plenipes.py --sync --force
```

---

## 🔌 NPM 终端集成 (NPM Integration)

建议将 **Illacme-plenipes** 的守护进程直接挂载到你的前端工程中。在前端项目 `package.json` 中注入以下脚本：

```JSON
"scripts": {
  "dev": "astro dev",
  "plenipes": "cd ../illacme-plenipes && python plenipes.py --sync --watch",
  "dev:i": "concurrently -k -p \"[{name}]\" -n \"Illacme,Astro\" -c \"blue.bold,green.bold\" \"npm run plenipes\" \"npm run dev\""
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

## 📜 许可证 (License)

基于 **MIT License** 开源。在保留署名的前提下，允许任何形式的商业化二次封装与分发。