# Illacme-plenipes Project Governance Standards

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
- **文档不掉队**：任何涉及核心逻辑（Pipeline/Adapter）的修改，必须同步更新 `docs/SPECIFICATION.zh-CN.md`。
- **配置不失联**：任何新增配置项或 CLI 参数，必须同步更新 `docs/REFERENCE.zh-CN.md`。
- **操作不迷路**：任何用户端特性的变动，必须同步更新 `docs/MANUAL.zh-CN.md` 及 `README.zh-CN.md` 特性列表。
- **版本透明化**：重大交付必须在 `CHANGELOG.md` 中留下演进记录。

## VI. 自动工程生命周期 (AEL Protocol)
- **基因沉淀 (Genetic Archiving)**：每一个重大功能增量，必须在 `.plenipes/history/` 下建立独立文件夹。同步存放 `plan.md` (实施方案) 与 `task.md` (任务清单)。
- **里程碑追踪 (Milestone Tracking)**：必须实时维护根目录或 `.plenipes/` 下的 `ROADMAP.md`，使用 Mermaid 逻辑图表征当前工程的物理进度。
- **验收全透明**：每一轮迭代结束后，必须将最终的 `walkthrough.md` 归档至对应历史目录，确保项目的“思考-执行-验证”链路 100% 可追溯。