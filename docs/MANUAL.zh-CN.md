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
3.  编辑 `config.yaml`：
    *   填入您的 `api_key`。
    *   设置 `markdown_dir` (例如您的 Docusaurus `docs` 目录)。
4.  执行全量同步：`python3 plenipes.py --sync`。

## 2. 创作流实战指南

### 2.1 使用监听模式实现“保存即发布”
当您在 Obsidian 或 Logseq 中写作时，启动后台守护进程：
```bash
python3 plenipes.py --watch
```
引擎会以毫秒级频率监控源文件夹。每当您按下 **Ctrl+S**，系统会在 5 秒静默期后自动触发增量同步。

### 2.2 审计与溯源 (Timeline)
如果您想查看某篇文章的同步历史，请打开项目根目录下的 `timeline.md`。
*   它可以记录您的保存频率。
*   它可以显示某次同步失败的具体报错，助您快速修复 Markdown 语法问题。

### 2.3 “影子资产”管理 (Shadow Recovery)
如果您手动删除了前端目录下的文件导致“物理脱靶”，只需再次运行同步任务。引擎会检测到物理文件缺失，并从影子缓存（`.illacme-shadow`）中自动恢复，**无需再次扣除 AI Token**。

## 3. 高级配置场景

### 3.1 完美适配 Docusaurus
在 `config.yaml` 中将 `active_theme` 设为 `docusaurus`。引擎会自动转换：
*   Obsidian Callouts -> Docusaurus Admonitions (`:::tip` 等)。
*   内链双链 -> 标准 Markdown 引用。

### 3.2 离线开发与节流
如果您正在断网环境写作，或者想节省 API 支出：
```bash
python3 plenipes.py --sync --no-ai
```
在此模式下，所有 AI 任务会被挂起，系统仅执行格式清洗与路径分发。

## 4. 故障排除 (Troubleshooting)

*   **端口占用错误**：通常意味着有一个旧实例在后台运行。可通过 `fuser -k 43210/tcp` (Linux) 杀死或通过 `--port` 换个端口。
*   **JSON 解析失败**：意味着 AI 返回的内容不是标准 JSON。系统会自动重试，若持续失败请检查您的 Prompt 配置。
