# Illacme-plenipes Project Governance Standards
# 🛡️ v5.4.1 (架构主权与治理加固版)

These project-specific rules extend the Global Integrity Protocols and must be strictly followed when working in this repository.

## I. Flagship Configuration Management
- **Master Schema Retention**: The `config.yaml` and `config.example.yaml` must maintain the V34.5+ structural complexity. Always preserve the `framework_adapters`, `theme_options`, and `ingress_settings` nodes.
- **Master Commentary**: Configuration files must be heavily documented in Chinese, explaining every industrial-grade parameter to the user.

## II. Core Architecture Protection
- **Dialect Fidelity**: The `InputAdapter` (Ingress) and `SSGAdapter` (Egress) logic must be protected. Do not "streamline" the dialect normalization regexes or masking logic.
- **Incremental Integrity**: Preserve the hash-based differential sync logic in `core/pipeline/steps.py`.

## III. Service Continuity
- **Audit Timeline (Required)**: The `TimelineManager` and its associated hooks in `daemon.py` and `engine.py` are mandatory. Never remove or simplify the chronological audit logging.
- **Asset Pipeline**: Maintain the strictly-typed WebP compression and ImageAlt generation pipeline.

## IV. Defensive Coding
- **NoneType Immunity**: All API responses and configuration lookups must use defensive `dict.get()` and type-casting (e.g., `int()`) to prevent `TypeError` or `AttributeError` crashes in industrial scenarios.
- **Concurrency Safety**: Always respect and enforce `max_workers` and `llm_concurrency` locks.

## V. 活化文档同步协议 (Living Documentation Mandate)
- **文档不掉队**：任何涉及核心逻辑的修改，必须同步更新 `docs/SPECIFICATION.zh-CN.md`。
- **版本透明化**：重大交付必须在 `CHANGELOG.md` 中留下演进记录。

## VI. 自动工程生命周期 (AEL Protocol)
- **基因沉淀 (Genetic Archiving)**：每一个重大功能增量，必须在 `.plenipes/history/` 下建立独立文件夹。同步存放 `plan.md`, `task.md`, `walkthrough.md`。

## VII. 自动演化矩阵 (Autonomy Matrix - AM)
- **模拟优先 (Simulation-First)**：凡涉及出站管线的自主重构，必须先在 `tests/autonomous_simulation.py` 中通过 100% 仿真校验。
- **意图溯源 (Traceable Intent)**：所有 AI 生成或修改的代码块必须包含 `[AEL-Iter-ID]` 标签。

## VIII. 治理与审计主权 (Governance Sovereignty)
- **[Rule 11.1] 复杂度红线硬约束 (300 Lines Policy)**：禁止任何逻辑文件（Python）超过 **300 行**。一旦触线，治理审计将强制拦截提交。
- **[Rule 12.8] 核心函数主权防护**：严禁在未迁移逻辑的前提下删除核心类方法（如 `translate`, `generate_slug`）。适配器必须通过协议完整性审计。
- **[Rule 12.9] 逻辑主权隔离协议**：严禁在子类适配器中重写受保护的业务层逻辑方法。适配器只能实现原子协议接口（如 `_ask_ai`）。
- **[Rule 12.10] 物理拓扑硬约束**：所有包含 Python 代码的目录必须包含 `__init__.py`，且静态导入链必须通过 100% 连通性扫描。
- **[Rule 12.11] 冒烟点火测试令**：任何代码提交前必须在子进程中成功执行主入口冒烟测试，确保系统具备 100% 可启动性。
- **[Rule 12.12] 五大星系治理阶梯**：治理审计必须遵循“物理 -> 系统 -> 代码 -> 动态 -> 历史”的阶梯式顺序执行，确保失败反馈的高效性。

## IX. 治理自审 (Governance Self-Audit)
- **每轮必审 (Mandatory Post-Iteration Audit)**：每次迭代结束后、`git commit` 前，必须执行 `python3 tests/governance_audit.py`。只有全部检查项通过（0 失败）才允许提交。
- **自愈授权**：审计引擎拥有对低级代码坏味道执行自动修复的最高授权。
