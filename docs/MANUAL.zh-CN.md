# 🚀 Illacme-plenipes 用户操作指南 (MANUAL)

本手册侧重于具体任务的落地，指导您如何将引擎部署到不同的生产环境并进行高效创作。

## 1. 快速上手 (Quick Start)

### 1.1 环境准备
*   确保安装了 Python 3.9+。
*   安装核心依赖：`pip install -r requirements.txt`。
*   (可选) 建议安装 `tiktoken` 以启用高精度 AI 语义切片。

### 1.2 首次启动
1.  运行 `python3 plenipes.py`。
2.  引擎会自动生成 `config.yaml` 模板。
3.  编辑 `config.yaml`：填入您的 `api_key` 并设置 `markdown_dir`。
4.  执行全量同步：`python3 plenipes.py --sync`。

## 2. 创作流实战指南

### 2.1 监听模式
启动后台守护进程：`python3 plenipes.py --watch`。引擎会监控源文件夹，按下 **Ctrl+S** 后自动触发增量同步。

### 2.2 影子资产自愈 (Shadow Recovery)
如果您手动删除了前端目录下的文件，只需再次运行同步任务。引擎会从影子缓存（`.illacme-shadow`）中自动恢复，**无需再次扣除 AI Token**。

## 3. 主权治理与自审指南 (Governance & Sovereignty)

### 3.1 运行自审引擎
在每次代码提交或重大配置变更前，建议手动执行：
```bash
python3 tests/governance_audit.py
```
系统会扫描“五大星系”（物理、系统、代码、仿真、历史）共 60 项指标。只有获得 **60/60 Pass** 才代表项目处于稳健的工业级状态。

### 3.2 维护历史归档 (AEL Protocol)
当您开始一个新的功能开发时，必须在 `.plenipes/history/` 下建立迭代目录，并包含：
1.  **`implementation_plan.md`**：设计方案。
2.  **`task.md`**：任务核销清单。
3.  **`walkthrough.md`**：验收复盘。
**注意**：归档文档的字数必须达标（计划 > 400 字符，验收 > 300 字符），否则审计引擎将拦截您的提交。

### 3.3 解读“冒烟测试”失败
如果审计报告提示 `仿真引擎点火失败`，意味着您的代码变更导致主程序无法启动。请检查最近的 `import` 路径或 `__init__.py` 文件是否完整。

## 4. 故障排除 (Troubleshooting)

*   **端口占用错误**：通常意味着有一个旧实例在后台运行。
*   **复杂度红线拦截**：如果代码超过 300 行被拦截，请按照 [Rule 11.1] 执行模块拆分。
