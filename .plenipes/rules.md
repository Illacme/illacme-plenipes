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

## X. 治理自审 (Governance Self-Audit)
- **每轮必审 (Mandatory Post-Iteration Audit)**：每次迭代结束后、`git commit` 前，智能体必须执行 `python3 tests/governance_audit.py`。只有全部检查项通过（0 失败）才允许提交。
- **自审进化 (Audit Evolution)**：智能体在实战中发现新的反模式时，必须主动向 `tests/governance_audit.py` 追加新的检查函数。自审清单本身也是一个会呼吸的活文档。
- **人类审计解放**：此机制的终极目标是让 AI 承担 100% 的治理巡检责任，将人类从"手动查阅发现问题"的低效循环中彻底解放。

## XI. 工程稳定性与原子化操作 (Engineering Stability)
- **[Rule 11.1] 复杂度红线与黄线**：
    - **硬性失败（红线）**：禁止任何逻辑文件（Python）超过 **500 行**。一旦触线，治理审计将强制拦截提交。Markdown/MDX 文件作为内容资产，豁免行数限制。
    - **健康警告（黄线）**：当 Python 逻辑文件超过 **300 行** 时，Agent 必须发出重构警告，并在下一个 TDR 迭代中优先拆分。
- **[Rule 11.2] 编辑原子化协议**：禁止单次 `replace_file_content` 超过 100 行或 2KB。大修必须拆分为多个微块执行。
- **[Rule 11.3] 影子自省校验**：超过 50 行的核心逻辑变更，AI 必须优先在 `.tmp` 副本中进行语法校验（ast.parse）或干跑（Dry-run），验证无误后方可覆盖原件。
- **[Rule 11.4] 死锁逃逸机制**：若单次编辑导致会话响应超过 60s 或出现逻辑死锁，下一任 Agent 必须强制回滚该文件至最近的审计通过点（Audit Checkpoint）。
- [Rule 11.5] 配置文件分片协议 (Config Fragmentation Protocol)：鼓励对超过 500 行的配置文件执行“分片拆分”。核心逻辑支持 `include: "sub_config.yaml"` 语法，将大体量配置（如主题适配器、AI 节点集）隔离到独立文件，降低单文件编辑时的 Context 负载与死锁风险。

## [Rule 12] 治理与审计主权 (Governance Sovereignty)
- **[Rule 12.8] 核心函数主权防护**：严禁在未迁移逻辑的前提下删除核心类方法（如 `translate`, `generate_slug`, `generate_seo_metadata`）。所有适配器类必须通过 AST 逻辑完整性审计。

## XII. 怠工防御与硬核强制协议 (Anti-Slacking & Hard Enforcement)
- **[Rule 12.1] 强制特征签名校验 (Mandatory Signature Audit)**：凡涉及类构造函数（`__init__`）、核心函数签名的修改，AI 必须**强制**执行全项目 grep 扫描所有调用点并同步更新。严禁在未确认调用链闭环的情况下宣告“完成”。
- **[Rule 12.2] 审计零红线准则 (Zero-Red Audit Policy)**：在宣布任务结束前，必须运行 `governance_audit.py`。任何 **RED (Failure)** 级别的问题必须当场修复。严禁带着 RED 状态交付。
- **[Rule 12.3] 三相文档物理落盘硬约束**：Plan、Task、Walkthrough 文档不仅要在会话中生成，必须**物理写入** `.plenipes/history/` 对应的归档目录。未见物理文件，视为“文档违约”。
- **[Rule 12.4] 配置模型联动校验**：任何针对 `config_models.py` 的修改，必须强制触发一轮 `tests/autonomous_simulation.py` 全量仿真。只有影子校验通过，才允许标记配置变更。
- **[Rule 12.5] 模块主权头强制令**：所有新建或重构的 Python 文件，必须以标准工业级 docstring 开头（包含模块职责、防护标签 `[AEL-Iter-ID]`）。缺失头部的代码视为“流浪代码”，治理审计将直接拦截。
- **[Rule 12.6] 清理产物物理销毁**：每次 TDR 迭代结束，必须物理执行 `find . -name "__pycache__" -exec rm -rf {} +`。严禁让编译产物污染物理目录。
- [Rule 12.7] 配置文件主权保护 (Config Integrity Guard)：严禁在未获得授权的情况下删除 `config.yaml` 或 `config.example.yaml` 中的任何注释块、示例节点或暂存占位符。精简必须通过“架构解耦（如模型化）”实现，而非“物理内容剪裁”。
