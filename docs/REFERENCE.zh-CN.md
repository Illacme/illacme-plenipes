# 📖 Illacme-plenipes 技术参考手册 (REFERENCE)

本手册同步自 `core/config.py` 与 `cli_bootstrap.py` 的最新物理代码，涵盖所有命令行参数及配置项的全量定义。

## 1. 命令行参数 (CLI Arguments)

执行入口：`python3 plenipes.py [ARGS]`

| 参数 | 缩写 | 类型 | 描述 |
| :--- | :--- | :--- | :--- |
| `--config` | `key` | `string` | 目标 Frontmatter 中的键名 (如 `lastmod`) |
| `style` | `string` | `plain` (直接输出) 或 `object` (结构化对象) |
| `datetime_format` | `string` | **[GGP 新增]** strftime 风格格式化字符串 (如 `%Y-%m-%dT%H:%M:%S%z`) |
| `--watch` | - | `Flag` | 启动看门狗实时守护模式 |
| `--dry-run` | - | `Flag` | 演练模式：拦截 API 扣费与物理写盘 |
| `--force` | - | `Flag` | 强制模式：无视指纹，全量重刷所有文档 |
| `--path` | `-p` | `List` | **选择性同步**：仅同步指定的文件或目录路径 |
| `--no-ai` | - | `Flag` | **离线模式**：拦截所有 AI 任务，仅执行本地排版 |
| `--port` | - | `INT` | 物理覆盖 `singleton_port`，支持多实例运行 |
| `--log-level` | - | `Enum` | 日志级别：DEBUG, INFO, WARNING, ERROR |
| `--clean` | - | `Flag` | 重置引擎：物理清空指纹库与影子缓存 |

## 2. 配置文件详解 (Config Matrix - config.yaml)

### 2.1 系统层 (System)
*   **`max_workers`** (int): AI 处理的并发线程数。
*   **`auto_save_interval`** (int): 账本落盘间隔（秒）。
*   **`log_level`** (string): 全局日志详尽度。
*   **`singleton_port`** (int): 互斥锁端口，防止引擎多开冲突。

### 2.2 路径层 (Output Paths)
*   **`markdown_dir`** (path): SSG 框架存放 Markdown 的目标目录。
*   **`assets_dir`** (path): SSG 存放静态资源（图片/视频）的地址。
*   **`graph_json_dir`** (path/null): (可选) 导出全量图谱 JSON 的路径。

### 2.3 翻译与 AI (Translation/AI)
*   **`providers`** (dict): API Key 与 Base URL 的连接阵列。
*   **`max_chunk_size`** (int): 文档分片时的 Token 长度限制。
*   **`temperature`** (float): AI 生成的随机性（建议 0.1 以下）。
*   **`enable_semantic_slice`** (bool): 是否开启基于 AST 的语义切片。

### 2.4 SEO 与元数据 (SEO Settings)
*   **`generate_description`** (bool): 是否自动生成 150 字以内的摘要。
*   **`generate_keywords`** (bool): 是否自动生成 5-10 个关键词标签。
*   **`slug_mode`** (enum): `ai` (语义化美化) 或 `regex` (正则拼音化)。

### 2.5 审计时间轴 (Timeline)
*   **`enabled`** (bool): 记录“保存-同步”动作序列的开关。
*   **`max_entries`** (int): 历史记录回溯深度上限。

## 3. 环境变量 (Environments)

除配置文件外，引擎支持以下环境变量覆盖：

*   **`ILLACME_API_KEY`**: 强制覆盖所有翻译提供者的 API Key。
*   **`ILLACME_LOG_LEVEL`**: 终端输出的日志详尽度。
