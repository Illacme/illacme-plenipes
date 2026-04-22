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

## VII. 测试驱动演化 (TDE Protocol)
- **演化必测 (Test-on-Evolution)**：任何针对核心逻辑（Pipeline/Adapter）的功能增强，必须在迭代文件夹中包含物理测试代码（如 `test_feature.py`）。未经测试的功能严禁归档。
- **哨兵监护 (Sentinel Guard)**：哨兵 Manager 拥有对全量代码执行 `ruff --fix` 的最高自愈授权。任何被检测到的低级代码坏味道必须被自动抹除。
- **云端共振**：本地哨兵规则必须与 GitHub Actions 哨兵流水线保持 100% 同步，任何本地无法通过的测试严禁推送至云端。
## VIII. 全自动演化矩阵 (Autonomy Matrix - AM)
- **模拟优先 (Simulation-First)**：凡涉及出站管线（Slug/Route/Assets）的自主重构，必须先在 `tests/autonomous_simulation.py` 中通过 100% 仿真校验，严禁盲目执行物理回写。
- **算力熔断 (Token/TCG)**：单次自主迭代的估算 Token 消耗不得超过 50k。一旦触线，哨兵将强制挂起任务并提交成本分析，等候人工注资许可。
- **意图溯源 (Traceable Intent)**：所有 AI 生成或修改的代码块必须包含 `[AEL-Iter-ID]` 标签。禁止产生任何无法溯源至历史归档（`.plenipes/history/`）的“孤儿代码”。
- **架构复健 (TDR)**：每 4 次业务特性迭代后，必须自动触发 1 次架构解耦迭代。

## IX. 规则元进化 (Meta-Evolution)
- **动态反哺 (Dynamic Feedback)**：在每次完整的迭代或 BUG 修复中，一旦智能体推导出了能避免未来报错的架构边界、Git 拦截钩子，或是确立了新的防御逻辑，智能体**拥有最高裁量权**自动更新和扩充本规则文件（`.plenipes/rules.md`）！严禁依靠模拟器事后惩罚报错来学习，必须通过“修宪法”来打通事前预防的认知循环。
- **自主迭代边界拓展**：把 `rules.md` 视作会呼吸的动态记忆器官，所有属于项目维度的共识必须第一时间沉淀入此处，避免 AI 本地沙盒脑暴清空后导致的“工程失忆”。这是实现 Agent 越开发越聪明的唯一合法路径。
- **进化记录双轨沉淀 (Dual Evolution Deposit)**：每次迭代结束时，智能体必须执行双轨写入：
    1. **项目层** `.plenipes/evolution_records.md`：沉淀本项目专属的技术踩坑、架构决策与配置边界。
    2. **全局层** 全局 KI `evolution_records.md`：沉淀跨项目通用的 AI 行为纪律与工具使用教训。
  未执行双轨沉淀的迭代视为"知识自杀"，其教训将随对话消亡。
