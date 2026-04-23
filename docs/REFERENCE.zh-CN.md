# 📖 Illacme-plenipes 技术参考手册 (REFERENCE)

本手册同步自 `core/config.py` 与 `cli_bootstrap.py` 的最新物理代码，涵盖所有命令行参数及配置项的全量定义。

## 1. 命令行参数 (CLI Arguments)

执行入口：`python3 plenipes.py [ARGS]`

| 参数 | 缩写 | 类型 | 描述 |
| :--- | :--- | :--- | :--- |
| `--config` | - | `string` | 指定配置文件路径 (默认 config.yaml) |
| `--watch` | - | `Flag` | 启动看门狗实时守护模式 |
| `--dry-run` | - | `Flag` | 演练模式：拦截 API 扣费与物理写盘 |
| `--force` | - | `Flag` | 强制模式：无视指纹，全量重刷所有文档 |
| `--no-ai` | - | `Flag` | **离线模式**：拦截所有 AI 任务，仅执行本地排版 |

## 2. 配置文件详解 (Config Matrix - config.yaml)

### 2.1 系统层 (System)
*   **`max_workers`** (int): 处理并发线程数。
*   **`singleton_port`** (int): 互斥锁端口。
*   **`watchdog_settings`** (dict): [NEW] 包含 `heavy_task_delay` 和 `gc_delay` 调优。

### 2.2 翻译与 AI (Translation/AI)
*   **`custom_prompts`** (dict): [NEW] 外部化提示词覆盖 (slug/seo/translate)。
*   **`global_proxy`** (string): [NEW] 适配器全局 HTTP 代理。

### 2.3 治理与自审 (Governance)
*   **`governance.policy`** (enum): `strict` (审计失败阻止提交) 或 `loose`。
*   **`governance.complexity_hard_limit`** (int): [Rule 11.1] 逻辑文件行数红线 (300)。
*   **`governance.history_audit_depth`** (int): 迭代归档追溯深度 (3)。
*   **`governance.logic_sovereignty_protection`** (bool): [Rule 12.9] 逻辑主权隔离开关。

### 2.4 审计时间轴 (Timeline)
*   **`timeline.enabled`** (bool): 记录动作序列的开关。
*   **`timeline.max_entries`** (int): 历史记录回溯上限。

## 3. 环境变量 (Environments)
*   **`ILLACME_SKIP_DOC_CHECK`**: 设置为 `TRUE` 可临时跳过仿真引擎的文档强校验。
*   **`ILLACME_LOG_LEVEL`**: 终端日志详尽度。
