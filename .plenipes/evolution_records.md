# 🧬 Illacme-plenipes 项目进化记录 (Project Evolution Records)

本文件记录 Illacme-plenipes 引擎开发过程中的专属技术踩坑与架构进化。通用 AI 行为纪律请查阅全局 KI 中的 `evolution_records.md`。

## 📅 2026-04-18/19 进化点

### 1. [逻辑防御] 状态机信号分层 (State Machine Signal Isolation)
- **背景**：系统中存在性能跳过（指纹一致）与安全拦截（空文/草稿）两种中止逻辑，原系统混用 `is_aborted` 信号导致统计数据全量误报为"拦截"。
- **进化结论**：
    - **强制分层**：必须通过 `is_skipped` (性能跳过) 与 `is_aborted` (规则拦截) 进行双轨上报。
    - **显示反馈**：在 Summary Dashboard 中必须精确区分 ✅、🔄、🛑 三种物理状态。
- **Action**: 处理管线跳过逻辑时，禁止直接 Abort，必须先显式标记 Skip。
- **Guard**: `check_core_architecture_fingerprint` — 通过指纹保护确保 Pipeline 类结构不被意外删除

### 2. [新特性] 创作实时审计 (Real-time Audit Capability)
- **需求驱动**：用户需要对"本地保存 -> 系统响应"的整个过程有物理追溯能力。
- **进化结论**：
    - **时空追溯**：实现了 `plenipes_timeline.json` 与 `timeline.md` 的异步持久化。
    - **状态闭环**：审计必须覆盖从 Watchdog 捕获动作到 Pipeline 输出结果的全生命周期。
- **Action**: 未来新增监听事件时，必须同步在 `on_*` 钩子中植入 `timeline` 记录点。
- **Guard**: `check_core_architecture_fingerprint` — TimelineManager 签名包含在 7 个神圣指纹中

### 3. [跨框架] 声明式 Egress 适配 (Declarative Egress GGP)
- **痛点回顾**：不同 SSG 的日期格式、短代码（Shortcode）各不相同，硬编码适配器导致工程臃肿。

---

## 📅 2026-04-26 进化点

### 1. [高并发] 嵌套池化死锁防御 (Nested Pool Deadlock Defense)
- **背景 (V11 危机)**：在 38 个文档全量并发同步时，系统发生“静默吊死”。经 `SIGUSR1` 物理堆栈追踪发现，调度线程（Global）与任务线程（AI）在同一个池子中发生了“ABBA 嵌套死锁”。
- **进化结论**：
    - **物理隔离原则 (Isolation)**：严禁在同一个线程池中提交任务并同步等待（`.result()`）该池子产生的子任务。
    - **层级化执行器**：
        - `global_executor`：仅处理非阻塞的管理调度（文件扫描、队列分发）。
        - `ai_executor`：处理重负载的 AI 逻辑。
    - **工位冗余化 (Management Overbooking)**：即便 `llm_concurrency` 为 1，`ai_executor` 也必须保持足够的冗余工位（16+），以防“管理流”被“计算流”反向阻塞。
    - **本地环境降级**：在本地模型环境下，文档内部的内容块翻译必须改为**顺序执行**，彻底杜绝池化嵌套需求。
- **Action**: 修改 `ai_scheduler.py` 逻辑，将块并行改为串行，并解除 `task_orchestrator.py` 的背压（Backpressure）限制。
- **Guard**: `SIGUSR1` 堆栈导出功能已固化在 `engine.py` 中，作为系统级的“黑匣子”导出接口。

### 2. [主权健壮性] 四层物理防线加固 (The Quad-Layer Hardening)
- **背景**：为了防止 AI 在迭代中破坏系统，建立了全自动的防御体系。
- **进化结论**：
    - **L1 压测层**：建立 `tests/stability` 体系，通过模拟极端并发探测架构缺陷。
    - **L2 内核层**：在 `OrchestratedExecutor` 注入线程名自察，实时拦截嵌套死锁。
    - **L3 契约层**：引入 `@SovereignCore` 装饰器锁定核心 API，配合 `sovereignty_guard.py` 进行 AST 语法审计。
    - **L4 数据层**：实现 `ShadowManager` 影子演练模式，防止同步过程中的数据坍塌。
- **Action**: 未来所有核心重构必须首先通过 `sovereignty_guard.py` 审计与 `concurrency_stress.py` 压测。
- **Guard**: `SIGUSR1` 堆栈导出功能已固化在 `engine.py` 中，作为系统级的“黑匣子”导出接口。
- **进化结论**：
    - **正则映射表**：引入 `shortcode_mappings` 与 `datetime_format`，将"逻辑适配"下沉至"配置定义"。
    - **栈式静态化**：在处理嵌套 Tabs 时，必须使用平衡栈（Stack）而非正则表达式，以确保 100% 结构保真。
- **Action**: 所有出站适配逻辑应优先查找 `shortcode_mappings` 全局配置。
- **Guard**: `check_core_architecture_fingerprint` — EgressDispatcher 签名包含在 7 个神圣指纹中

### 4. [自愈性] 哨兵监护与主动检测 (Guardian Sentinel)
- **需求驱动**：单纯的同步无法保证代码质量的长效稳定性。
- **进化结论**：
    - **主动纠偏**：通过 Sentinel + Ruff 实现静默期的代码自愈（Auto-Fix），消灭代码坏味道。
    - **测试驱动**：建立 AEL v2 协议，将"功能实现"与"单元测试"进行物理绑定（TDE）。
- **Action**: 哨兵审计报告必须作为 AEL 迭代归档的必要附件。
- **Guard**: `check_test_on_evolution` — 核心管线变更必须伴随测试文件

## 📅 2026-04-22 进化点

### 5. [Git 卫生] 本地状态泄露防线 (Git Hygiene)
- **故障回顾**：`ledger.json`、`plenipes_timeline.json` 等引擎运行时状态文件被 Git 追踪，导致仓库膨胀且存在隐私泄露风险。
- **进化结论**：
    - **精准切割**：`.plenipes/history/` 和 `rules.md` 必须提交（项目基因）；`ledger.json`、`timeline.*`、`sentinel_health.json` 和 `.illacme-shadow/` 必须屏蔽（本地状态）。
    - **追踪树清洗**：仅修改 `.gitignore` 不够，已被追踪的文件必须用 `git rm --cached` 物理摘除。
- **Action**: 新增运行时状态文件时，第一时间检查 `.gitignore` 是否已覆盖。
- **Guard**: `check_git_tracked_state_files` — 物理检测已知状态文件是否被 Git 追踪

### 6. [AEL 治理] 防爆钩子与文档耦合 (Simulation Hook Governance)
- **故障回顾**：历史归档目录出现空文件夹，文档更新长期滞后于代码变更。
- **进化结论**：
    - **Git 防爆钩子**：`autonomous_simulation.py` 中的 `verify_docs_sync_hook` 强制要求每次代码变更同步更新 `docs/` 或 `CHANGELOG.md`，且在 `.plenipes/history/` 下新增归档。
    - **规则元进化**：`rules.md` 第九章授权 AI 在实战中主动修改规则本身，通过"修宪"实现事前预防而非事后惩罚。
- **Action**: 每次提交前运行 `autonomous_simulation.py`，确保防爆钩子放行。
- **Guard**: `check_simulation_execution` — 物理运行仿真引擎验证防爆钩子

## 📅 2026-04-23 进化点

### 7. [流程缺陷] 部分暂存陷阱 (Partial Staging Trap)
- **故障回顾**：AI 执行 `git add file_a file_b` 手选文件提交时，遗漏了同时修改过的 `file_c`。该文件残留在工作区，而当时 22 项治理检查中无一能在**当次**提交时拦截此行为。仿真沙盒虽然在**下一次**提交时发现了残留，但已经造成了一次"通过了门禁却仍有未纳管代码"的事故。
- **进化结论**：
    - **当次拦截**：新增 `check_no_unstaged_leftovers`（第 22 项），在 pre-commit 阶段扫描 `git status --porcelain` 的第二字符位（worktree_char），一旦发现 `M`（已修改但未暂存）立即 `fail`。
    - **根因认知**：Git 的 staging area 设计允许"部分提交"，这对 AI 高频迭代场景是一个致命陷阱——AI 的注意力模型在长上下文中非常容易遗漏文件名。
- **Action**: 禁止依赖手动枚举的 `git add file1 file2`，优先使用 `harvest.py` 自动收割后再 `git add` 变更文件。
- **Guard**: `check_no_unstaged_leftovers` — 物理检测工作区未暂存修改

### 8. [技术缺陷] 正则贪婪陷阱与栈式静态化 (Parsing Evolution)
- **现象**：大规模嵌套 Callouts 在正则解析下发生“结构性坍塌”，内层标记被外层正则表达式贪婪吞噬。
- **教训**：对于 Markdown 等具备缩进递归特性的语法，正则表达式是不可持续的负债。必须采用“线性行扫描 + 缩进/语义栈”模式。
- **行动**：已将 Callout 解析逻辑全局迁移至 `StaticizerStep`，并引入 `_staticize_callouts` 递归栈解析器。
- **治理项**：`governance_audit.py` 已同步强化仿真测试中的嵌套深度校验。
- **Guard**: `check_callout_nesting` — 物理验证 StaticizerStep 是否包含栈式解析逻辑

### 9. [架构主权] Zero-Touch 架构包化重构 (Industrial Refactor / Reconstruction)
- **背景**：随着项目规模扩大，单体 `ai_provider.py` 和 `config.py` 变得臃肿，且不支持插件自发现。
- **重构结论**：
    - **包化迁移**：将单体逻辑拆分为 `core/adapters/ai/`, `core/adapters/ingress/` 等标准 Python 包结构。
    - **自发现机制**：引入 `plugin_loader.py` 实现“零触”加载，消灭硬编码注册。
    - **物理隔离**：所有的“净删除”和“注释丢失”均属于物理位置迁移，而非逻辑缺失。
- **Action**: 在重构期间，审计引擎需识别 "Refactor" 或 "Reconstruction" 信号并给予警告豁免。
- **Guard**: `check_topology_integrity` — 物理拓扑完整性审计确保迁移后的包结构合法。
### 10. [治理死锁] 原子化归档与同步陷阱 (Atomic Archiving Deadlock)
- **故障回顾**：在 v5.4 迭代中，AI 分两次执行了提交：第一次提交了历史归档（history/），第二次提交了规则与文档修订（rules.md）。由于 `autonomous_simulation.py` 的强约束逻辑要求“在看到变更的同时必须看到归档文件处于暂存区（Staged）”，导致第二次提交在 Pre-commit 阶段被仿真引擎熔断。
- **进化结论**：
    - **原子化提交**：功能代码、全局文档修订与 `.plenipes/history/` 归档必须在同一个 Git Transaction（暂存区信号）中出现。
    - **激活信号**：若不慎分步提交，可通过微调归档文件（如加空行）重新触发 Staged 信号以解锁审计引擎。
- **Action**: 开发结束后的收割阶段，必须执行 `git add .` 将所有变更（代码+文档+归档）一次性对齐，严禁分散暂存。
- **Guard**: `check_simulation_execution` — 仿真引擎现在已包含对“归档-变更同步性”的强校验。

### 11. [架构进化] 契约化主权与逻辑隔离 (Contractual Sovereignty)
- **现象**：在适配器（Adapter）扩展过程中，业务逻辑（如 Slug 生成、SEO 提取）极易在子类实现中发生“静默退化”或“被错误修剪”，导致引擎核心功能丢失。
- **重构结论**：
    - **逻辑下沉**：将所有“大脑级”逻辑从适配器子类移入 `BaseTranslator` 基类。
    - **原子协议**：子类仅允许实现 `_ask_ai` 等原子协议接口，严禁重写（Override）基类的业务流程方法。
- **Action**: 新增适配器时，必须继承基类模板并对齐 `_ask_ai` 契约，严禁在子类中编写 Prompt 组装逻辑。
- **Guard**: `check_logic_shadowing` — 通过 AST 静态扫描，物理拦截子类对基类主权方法的非法篡改。

## 📅 2026-04-24 进化点

### 12. [并发进化] 块级并行翻译与线程安全 (Parallel Block Synchronization)
- **背景 [AEL-Iter-v6.2.1]**：单文件长文同步耗时过长，原有的语种级并行无法解决单文件内的阻塞。
- **进化结论**：
    - **两层并行架构**：外层通过 `AIScheduler` 实现语种间并行，内层在 `process_target` 中引入 `ThreadPoolExecutor` 实现 Markdown 语义块（Blocks）间并行。
    - **资源隔离**：必须复用 `llm_concurrency` 信号量或按比例分配 `block_workers`，防止海量小块瞬时请求击穿本地 AI 节点（如 Ollama）。
- **Action**: 保持 `block_workers` 的动态计算逻辑，确保在多语种同步时总并发数受控。
- **Guard**: `check_parallel_concurrency_locks` — 物理验证调度器是否正确处理了并发限制。

### 13. [稳定性] 400 Bad Request 诊断防线 (AI Response Audit)
- **背景 [AEL-Iter-v6.2.1]**：本地模型在处理特定 Markdown 语法或长 Payload 时频繁返回 400 错误，且无详细日志导致排查困难。
- **进化结论**：
    - **深度响应审计**：在适配器层（OpenAI/Ollama）拦截非 200 响应，强制记录完整的 Response Body 到日志中。
    - **指数退避重试**：在 `BaseTranslator` 中集成统一的重试包装器，有效过滤网络瞬时抖动。
- **Action**: 所有 AI 适配器必须通过 `ask_ai_with_retry` 原子协议进行调用。
- **Guard**: `check_ai_retry_implementation` — AST 扫描确认 `_ask_ai` 调用是否被重试包装器覆盖。
